"""Hertz contact of a sphere on a flat (analytic) and a frictionless rigid
sphere pressed into an axisymmetric elastic body (finite elements).

Analytic formulas: Johnson 1985, *Contact Mechanics*, sec. 4.2 (sphere on a
flat, non-conforming, frictionless, small strain):

- 1/E* = (1 - nu1^2)/E1 + (1 - nu2^2)/E2
- a = (3 P R / (4 E*))^(1/3),  delta = a^2 / R,  p0 = 3 P / (2 pi a^2)
- p(r) = p0 sqrt(1 - r^2/a^2)

The finite element version uses the axisymmetric mode of ``fem2d`` and an
active-set iteration on the top surface nodes (unilateral, frictionless,
paraboloid indenter z = -delta + r^2/(2R), the same small-slope geometry as
Hertz). It is used to check the solver against the analytic p0 (V11).
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from . import fem2d


def effective_modulus(e1_pa: float, nu1: float, e2_pa: float = math.inf, nu2: float = 0.0) -> float:
    """E* of two elastic bodies; default second body is rigid."""
    inv = (1.0 - nu1 ** 2) / e1_pa + (0.0 if math.isinf(e2_pa) else (1.0 - nu2 ** 2) / e2_pa)
    return 1.0 / inv


@dataclass(frozen=True)
class HertzSolution:
    force_n: float
    contact_radius_m: float
    approach_m: float  # delta, mutual approach of distant points
    max_pressure_pa: float  # p0


def hertz_sphere_flat(force_n: float, radius_m: float, e_star_pa: float) -> HertzSolution:
    if force_n <= 0 or radius_m <= 0 or e_star_pa <= 0:
        raise ValueError("force, radius and E* must be positive")
    a = (3.0 * force_n * radius_m / (4.0 * e_star_pa)) ** (1.0 / 3.0)
    return HertzSolution(force_n, a, a * a / radius_m, 3.0 * force_n / (2.0 * math.pi * a * a))


def tensor_mesh(x: np.ndarray, y: np.ndarray, youngs_pa, poisson, thickness_m: float = 1.0) -> fem2d.Mesh2D:
    """Structured quad mesh on the grid x (increasing) by y (increasing)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if np.any(np.diff(x) <= 0) or np.any(np.diff(y) <= 0):
        raise ValueError("grid coordinates must be strictly increasing")
    X, Y = np.meshgrid(x, y, indexing="ij")
    nodes = np.stack([X.ravel(), Y.ravel()], axis=1)
    ny = len(y)
    I, J = np.meshgrid(np.arange(len(x) - 1), np.arange(ny - 1), indexing="ij")
    n0 = (I * ny + J).ravel()
    return fem2d.quad_mesh(nodes, np.stack([n0, n0 + ny, n0 + ny + 1, n0 + 1], axis=1),
                           youngs_pa, poisson, thickness_m)


@dataclass(frozen=True)
class ContactResult:
    force_n: float  # total indenter force (compressive positive)
    contact_radius_m: float  # radius of the outermost node in contact
    surface_r_m: np.ndarray  # radii of the top-surface nodes, increasing
    surface_pressure_pa: np.ndarray  # pressure at those nodes (compressive positive)
    surface_force_n: np.ndarray  # nodal ring forces from the indenter (compressive positive)
    surface_gap_m: np.ndarray  # indenter surface minus u_z (>= 0 means no overlap)
    in_contact: np.ndarray  # final active set (bool)
    iterations: int


def rigid_sphere_indent(mesh: fem2d.Mesh2D, top_z_m: float, bottom_z_m: float,
                        approach_m: float, radius_m: float, max_iter: int = 100) -> ContactResult:
    """Push a rigid frictionless sphere (radius R) by ``approach_m`` into the
    top surface z = top_z of an axisymmetric body whose bottom z = bottom_z is
    held with u_z = 0. The indenter is the small-slope paraboloid of Hertz
    theory: the gap is measured along z at the undeformed radius and only z
    forces are exchanged (frictionless). Nodal pressures are the consistent
    (L2) projection of the nodal reactions (F = M p on the top surface), so
    they ring slightly next to the contact edge where p(r) has infinite slope."""
    if approach_m <= 0 or radius_m <= 0:
        raise ValueError("approach and radius must be positive")
    tol = 1e-9 * mesh.h
    top = np.nonzero(np.abs(mesh.nodes[:, 1] - top_z_m) <= tol)[0]
    top = top[np.argsort(mesh.nodes[top, 0])]
    bottom = np.nonzero(np.abs(mesh.nodes[:, 1] - bottom_z_m) <= tol)[0]
    r = mesh.nodes[top, 0]
    target = -approach_m + r * r / (2.0 * radius_m)  # indenter surface (u_z limit)
    K = fem2d.assemble(mesh, "axisymmetric")
    active = target < 0  # first guess: the geometric overlap
    for it in range(1, max_iter + 1):
        idx = top[active]
        u = fem2d.solve(mesh, "axisymmetric", np.r_[2 * bottom + 1, 2 * idx + 1],
                        np.r_[np.zeros(len(bottom)), target[active]])
        reaction = (K @ u)[2 * top + 1]  # force the indenter puts on each node
        uz = u[2 * top + 1]
        release = active & (reaction > 0)  # indenter would have to pull
        add = ~active & (uz > target + 1e-12 * approach_m)  # surface passes through indenter
        if not release.any() and not add.any():
            break
        active = (active & ~release) | add
    else:
        raise RuntimeError("contact active set did not converge")
    # consistent edge matrix with 2*pi*r weight (2-point Gauss) on the top surface
    n = len(top)
    M = sp.lil_matrix((n, n))
    g = 1.0 / math.sqrt(3.0)
    for k in range(n - 1):
        ra, rb = r[k], r[k + 1]
        for s in (0.5 - 0.5 * g, 0.5 + 0.5 * g):
            N = np.array([1 - s, s])
            w = 0.5 * (rb - ra) * 2.0 * math.pi * ((1 - s) * ra + s * rb)
            M[k:k + 2, k:k + 2] += w * np.outer(N, N)
    pressure = -spla.spsolve(M.tocsc(), reaction)
    force = -reaction.sum()
    a = float(r[active].max()) if active.any() else 0.0
    return ContactResult(float(force), a, r, pressure, -reaction, target - uz, active, it)
