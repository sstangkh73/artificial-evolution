"""Fracture under a hammer blow: quasi-static spherical indentation of an
axisymmetric body with phase-field damage, limited by an energy budget.

Step 4 part (b). The hammer-core contact is reduced to an equivalent rigid
sphere pressing the core (frictionless, small slope, as in ``contact``):

- Hertz contact of two elastic bodies gives the same contact radius a(P) and
  pressure p(r) on the core as a RIGID sphere of radius
  R' = R E'_core / E*, with E'_core = E_core / (1 - nu_core^2) and
  1/E* = (1 - nu1^2)/E1 + (1 - nu2^2)/E2 (Johnson 1985, *Contact Mechanics*,
  sec. 4.2: a^3 = 3 P R / (4 E*)). ``equivalent_rigid_radius`` returns R'.
- The mutual approach splits between the bodies in proportion to
  (1 - nu_i^2)/E_i (Johnson 1985 eq. 4.23 applied to each body), so the work
  done on the core is the fraction E* / E'_core of the work of the contact
  force (``core_energy_share``). The hammer's share stays elastic in the
  hammer.
- ASSUMPTION: the kinetic energy of the relative motion (peak elastic energy
  of the hammer-core contact, ``impact.hertz_impact`` or
  ``impact.lumped_impact``) times the core share is the budget of work the
  indenter may do on the core. The blow is treated as quasi-static
  (Johnson sec. 11.4): no wave or inertia effects, and energy released by
  unstable crack growth at fixed approach is not returned to the hammer.

The approach delta is increased step by step. Each step is a staggered
iteration of ``phasefield`` (displacement with the contact active set and
degraded stiffness, then damage with d >= d of the previous step). The work
W = int P d(delta) is summed by the trapezoid rule; the last step is cut
(bisection on delta) so that W ends within ``budget_rtol`` of the budget.
Elements below the contact keep d free: whether they break is decided by the
energy split (``phasefield.energy_split``).
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import scipy.sparse.linalg as spla

from . import contact, fem2d
from . import phasefield as pf
from .materials import Material

MODE = "axisymmetric"


def plane_modulus(material: Material) -> float:
    """E' = E / (1 - nu^2)."""
    return material.youngs_modulus_pa / (1.0 - material.poisson_ratio ** 2)


def equivalent_rigid_radius(radius_m: float, e_star_pa: float, core: Material) -> float:
    """R' = R E'_core / E*: rigid sphere giving the core the same a(P) and p(r)."""
    if not (radius_m > 0 and e_star_pa > 0):
        raise ValueError("radius and E* must be positive")
    return radius_m * plane_modulus(core) / e_star_pa


def core_energy_share(e_star_pa: float, core: Material) -> float:
    """Fraction of the contact work done on the core, E* / E'_core."""
    share = e_star_pa / plane_modulus(core)
    if not (0 < share <= 1 + 1e-12):
        raise ValueError("E* must not exceed E' of the core")
    return min(share, 1.0)


def graded_axis(fine_m: float, h_m: float, extent_m: float, growth: float = 1.15) -> np.ndarray:
    """0, h, 2h, ... up to the first multiple of h >= ``fine_m`` (capped at
    ``extent_m``), then sizes growing by ``growth`` up to ``extent_m`` (the
    last node is exactly ``extent_m``)."""
    if not (0 < h_m <= fine_m <= extent_m) or growth < 1:
        raise ValueError("need 0 < h <= fine <= extent and growth >= 1")
    n = int(math.ceil(fine_m / h_m - 1e-9))
    end = extent_m * (1 - 1e-12)
    x = [float(v) for v in np.arange(n + 1) * h_m if v < end]
    if n * h_m >= end:  # the fine grid reaches the far side
        x.append(extent_m)
    step = h_m
    while x[-1] < extent_m - 1e-12 * extent_m:
        step *= growth
        x.append(min(x[-1] + step, extent_m))
    if len(x) >= 3 and x[-1] - x[-2] < 0.5 * (x[-2] - x[-3]):  # merge a sliver last element
        x.pop(-2)
    return np.asarray(x)


def indentation_mesh(material: Material, h_m: float, fine_radius_m: float, fine_depth_m: float,
                     radius_m: float, depth_m: float, growth: float = 1.15) -> fem2d.Mesh2D:
    """Axisymmetric block 0 <= r <= radius, -depth <= z <= 0 (top surface
    z = 0), uniform elements of size h in r <= fine_radius, z >= -fine_depth,
    growing outside."""
    r = graded_axis(fine_radius_m, h_m, radius_m, growth)
    z = -graded_axis(fine_depth_m, h_m, depth_m, growth)[::-1]
    return contact.tensor_mesh(r, z, material.youngs_modulus_pa, material.poisson_ratio)


@dataclass(frozen=True)
class IndentResult:
    approach_m: np.ndarray  # delta at the end of each accepted step (0 first)
    force_n: np.ndarray  # indenter force at each step
    work_j: np.ndarray  # cumulative work on the core
    fracture_energy_steps_j: np.ndarray  # crack energy after each step
    contact_radius_m: np.ndarray
    u: np.ndarray
    d: np.ndarray
    fracture_energy_j: float
    # 1/2 u.K(d).u at the final state (hybrid u-step energy). With d never
    # decreasing K(d) never stiffens, so W >= this up to the trapezoid error;
    # W - elastic is NOT guaranteed to equal fracture_energy_j (the hybrid
    # scheme is not variational, phasefield docstring)
    elastic_energy_j: float
    budget_j: float
    converged: bool  # every staggered step converged
    step_converged: np.ndarray  # per accepted step
    steps: int
    # True if the loop stopped because the force fell below
    # release_fraction * peak (crack through, budget not used up)
    released: bool = False


@dataclass(frozen=True)
class _Geometry:
    top: np.ndarray  # top surface node ids, increasing r
    r: np.ndarray  # their radii
    fixed_base: np.ndarray  # dofs always fixed: bottom u_z and axis u_r


def _geometry(mesh: fem2d.Mesh2D, top_z: float, bottom_z: float) -> _Geometry:
    tol = 1e-9 * mesh.h
    top = np.nonzero(np.abs(mesh.nodes[:, 1] - top_z) <= tol)[0]
    top = top[np.argsort(mesh.nodes[top, 0])]
    bottom = np.nonzero(np.abs(mesh.nodes[:, 1] - bottom_z) <= tol)[0]
    axis = np.nonzero(np.abs(mesh.nodes[:, 0]) <= tol)[0]
    return _Geometry(top, mesh.nodes[top, 0], np.r_[2 * bottom + 1, 2 * axis])


def _contact(K, geo: _Geometry, delta: float, radius: float, active: np.ndarray, max_iter: int = 100):
    """Frictionless unilateral contact with a rigid paraboloid (same active
    set rule as ``contact.rigid_sphere_indent``) for an assembled K.
    Returns (u, force, active)."""
    n = K.shape[0]
    target = -delta + geo.r ** 2 / (2.0 * radius)
    uz_dofs = 2 * geo.top + 1
    active = active.copy() if active.any() else target < 0
    for _ in range(max_iter):
        fixed = np.zeros(n, dtype=bool)
        fixed[geo.fixed_base] = True
        fixed[uz_dofs[active]] = True
        u = np.zeros(n)
        u[uz_dofs[active]] = target[active]
        free = ~fixed
        u[free] = spla.spsolve(K[free][:, free].tocsc(), -K[free][:, fixed] @ u[fixed])
        reaction = (K @ u)[uz_dofs]
        release = active & (reaction > 0)
        add = ~active & (u[uz_dofs] > target + 1e-12 * delta)
        if not release.any() and not add.any():
            return u, float(-reaction.sum()), active
        active = (active & ~release) | add
    raise RuntimeError("contact active set did not converge")


def _step(mesh, geo, radius, delta, d_prev, active, g_c, ell, split, tol, max_iter):
    """One staggered step at fixed approach: (u, force, active, d, converged)."""
    d = d_prev.copy()
    inner_ok, change = True, math.inf
    for _ in range(max_iter):
        K = fem2d.assemble(mesh, MODE, pf.degradation(pf.at_gauss_points(mesh, d)))
        u, force, active = _contact(K, geo, delta, radius, active)
        pos, _ = pf.energy_split(mesh, MODE, u, split)
        res = pf.solve_damage(mesh, MODE, pos, g_c, ell, d_prev, d)
        inner_ok = inner_ok and res.converged
        change = float(np.max(np.abs(res.d - d)))
        d = res.d
        if change < tol:
            break
    K = fem2d.assemble(mesh, MODE, pf.degradation(pf.at_gauss_points(mesh, d)))
    u, force, active = _contact(K, geo, delta, radius, active)
    return u, force, active, d, change < tol and inner_ok


def indent_with_budget(mesh: fem2d.Mesh2D, top_z_m: float, bottom_z_m: float, rigid_radius_m: float,
                       budget_j: float, g_c, length_m, split: str = "spectral", n_steps: int = 20,
                       budget_rtol: float = 0.02, tol: float = 1e-3, max_iter: int = 100,
                       d0: np.ndarray | None = None, progress=None) -> IndentResult:
    """Increase the approach of a rigid sphere until the work on the body
    reaches ``budget_j`` (J, full revolution). The step size is
    delta_H / ``n_steps`` with delta_H the approach at which an uncracked
    elastic half-space would absorb the budget (Hertz:
    W = 8/15 E' sqrt(R') delta^(5/2)); the last step is bisected so that W
    ends in budget * (1 +- ``budget_rtol``). Bottom z = ``bottom_z_m`` is held
    with u_z = 0. ``progress(step, delta, force, work, converged)`` is called after each
    accepted step if given."""
    if budget_j <= 0 or n_steps < 1:
        raise ValueError("budget and n_steps must be positive")
    geo = _geometry(mesh, top_z_m, bottom_z_m)
    e_prime = float(np.max(mesh.youngs_pa / (1.0 - mesh.poisson ** 2)))
    delta_h = (15.0 * budget_j / (8.0 * e_prime * math.sqrt(rigid_radius_m))) ** 0.4

    def step(delta, d_prev, active):
        u, force, active, d, ok = _step(mesh, geo, rigid_radius_m, delta, d_prev, active,
                                        g_c, length_m, split, tol, max_iter)
        return u, force, active, d, ok, float(geo.r[active].max()) if active.any() else 0.0

    return budget_loop(mesh, MODE, step, np.zeros(len(geo.top), dtype=bool), delta_h / n_steps,
                       budget_j, g_c, length_m, n_steps, budget_rtol, d0, progress)


def budget_loop(mesh: fem2d.Mesh2D, mode: str, step, state0, step_m: float, budget_j: float,
                g_c, length_m, n_steps: int, budget_rtol: float = 0.02,
                d0: np.ndarray | None = None, progress=None,
                release_fraction: float | None = None) -> IndentResult:
    """Increase the approach by ``step_m`` per step until the work
    W = int P d(delta) (trapezoid rule) reaches ``budget_j``; the last step is
    bisected on delta so that W ends in budget * (1 +- ``budget_rtol``).

    ``step(delta, d_prev, state) -> (u, force, state, d, converged, contact_size)``
    solves one staggered step at approach ``delta``; ``state`` is the contact
    active set carried from the previous accepted step. Shared by the
    axisymmetric indentation and the planar strike (``strike2d``).

    ``release_fraction``: if given, also stop after a step whose force is
    below this fraction of the largest force so far (the loaded part has
    broken off and no longer resists the indenter)."""
    d = np.zeros(len(mesh.nodes)) if d0 is None else np.asarray(d0, dtype=float).copy()
    state = state0
    deltas, forces, works, radii, efrac = [0.0], [0.0], [0.0], [0.0], [0.0]
    oks = []
    released = False
    u = np.zeros(mesh.n_dof)
    lo_w, hi_w = budget_j * (1.0 - budget_rtol), budget_j * (1.0 + budget_rtol)
    while works[-1] < lo_w:
        if len(deltas) > 50 * n_steps:
            raise RuntimeError("budget not reached within the step limit")
        lo, hi = deltas[-1], deltas[-1] + step_m
        a_lo, a_hi = lo, None  # bisection bracket on delta for the last step
        for _ in range(40):
            res = step(hi, d, state)
            w = works[-1] + 0.5 * (forces[-1] + res[1]) * (hi - lo)
            if w <= hi_w and (w >= lo_w or a_hi is None):
                break
            if w > hi_w:
                a_hi = hi
            else:
                a_lo = hi
            hi = 0.5 * (a_lo + a_hi)
        else:
            raise RuntimeError("could not cut the last step onto the budget")
        u, force, state, d, ok, size = res
        oks.append(ok)
        deltas.append(hi)
        forces.append(force)
        works.append(w)
        radii.append(size)
        efrac.append(pf.fracture_energy(mesh, mode, d, g_c, length_m))
        if progress is not None:
            progress(len(deltas) - 1, hi, force, w, ok)
        if release_fraction is not None and force < release_fraction * max(forces):
            released = True
            break
    scale = pf.degradation(pf.at_gauss_points(mesh, d))
    return IndentResult(
        approach_m=np.asarray(deltas), force_n=np.asarray(forces), work_j=np.asarray(works),
        fracture_energy_steps_j=np.asarray(efrac),
        contact_radius_m=np.asarray(radii), u=u, d=d,
        fracture_energy_j=efrac[-1],
        elastic_energy_j=0.5 * float(u @ (fem2d.assemble(mesh, mode, scale) @ u)),
        budget_j=float(budget_j), converged=bool(all(oks)),
        step_converged=np.asarray(oks), steps=len(deltas) - 1, released=released)
