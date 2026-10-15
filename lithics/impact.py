"""Hammer impact: kinetic energy of the hammerstone -> peak contact force.

Part (a) of step 4: the elastic (pre-fracture) collision only. Fracture under
this load and the energy budget it consumes are added on top of these results.

Analytic two-body impact: Johnson 1985, *Contact Mechanics*, sec. 11.4
(quasi-static Hertz impact of two elastic bodies, frictionless, no loss):

- contact law P = K delta^(3/2), K = (4/3) E* sqrt(R)  (sec. 4.2), where R is
  the effective radius 1/R = 1/R1 + 1/R2 (``effective_radius``); a flat
  target has R2 = inf so R is the hammer radius
- 1/m = 1/m1 + 1/m2 (reduced mass), closing speed v
- delta_max = (15 m v^2 / (16 E* sqrt(R)))^(2/5)   (eq. 11.22)
- P_max = K delta_max^(3/2), a_max = sqrt(R delta_max)
- duration t = 2 (delta_max / v) int_0^1 (1 - x^(5/2))^(-1/2) dx
           = (4/5) B(2/5, 1/2) delta_max / v = 2.943 delta_max / v  (eq. 11.24)

The quasi-static assumption needs the contact duration to be long compared
with the time elastic waves take to cross the bodies (Johnson sec. 11.4).

Supports (lumped masses along the strike line, solved as an ODE):

- ``hand_held``: the core is held by a linear spring to fixed ground. The
  spring stiffness is an ASSUMPTION (no cited value); the tests show the peak
  force hardly depends on it because the hand period is far longer than the
  contact.
- ``on_anvil``: the core rests on an anvil stone (passive hammer / bipolar).
  The core-anvil contact is a second Hertz contact with its own radius of
  curvature and materials; the anvil mass may be infinite (fixed ground).
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
from scipy.special import beta

from .contact import effective_modulus
from .materials import Material

# (4/5) B(2/5, 1/2): Johnson 1985 eq. 11.24 gives 2.94
DURATION_COEFF = 0.8 * float(beta(0.4, 0.5))


def effective_radius(r1_m: float, r2_m: float = math.inf) -> float:
    """1/R = 1/R1 + 1/R2 for two convex spherical surfaces (R2 = inf: flat)."""
    if not (r1_m > 0 and r2_m > 0):
        raise ValueError("radii must be positive")
    return r1_m if math.isinf(r2_m) else r1_m * r2_m / (r1_m + r2_m)


def hertz_stiffness(radius_m: float, e_star_pa: float) -> float:
    """K in P = K delta^(3/2) for a sphere of radius R on a flat (Johnson sec. 4.2)."""
    if not (radius_m > 0 and e_star_pa > 0):
        raise ValueError("radius and E* must be positive")
    return 4.0 / 3.0 * e_star_pa * math.sqrt(radius_m)


def contact_modulus(a: Material, b: Material) -> float:
    """E* of two materials in contact."""
    return effective_modulus(a.youngs_modulus_pa, a.poisson_ratio, b.youngs_modulus_pa, b.poisson_ratio)


def reduced_mass(m1_kg: float, m2_kg: float) -> float:
    if not (m1_kg > 0 and m2_kg > 0):
        raise ValueError("masses must be positive")
    if math.isinf(m2_kg):
        return m1_kg
    if math.isinf(m1_kg):
        return m2_kg
    return m1_kg * m2_kg / (m1_kg + m2_kg)


@dataclass(frozen=True)
class HertzImpact:
    max_force_n: float
    max_approach_m: float
    max_contact_radius_m: float
    max_pressure_pa: float  # p0 at the peak
    duration_s: float
    elastic_energy_j: float  # stored at the peak = kinetic energy of relative motion


def hertz_impact(mass_kg: float, speed_m_s: float, radius_m: float, e_star_pa: float) -> HertzImpact:
    """Johnson 1985 sec. 11.4 for reduced mass ``mass_kg`` and closing speed."""
    if not (mass_kg > 0 and speed_m_s > 0):
        raise ValueError("mass and speed must be positive")
    k = hertz_stiffness(radius_m, e_star_pa)
    d = (15.0 * mass_kg * speed_m_s ** 2 / (16.0 * e_star_pa * math.sqrt(radius_m))) ** 0.4
    p = k * d ** 1.5
    a = math.sqrt(radius_m * d)
    return HertzImpact(
        max_force_n=p,
        max_approach_m=d,
        max_contact_radius_m=a,
        max_pressure_pa=3.0 * p / (2.0 * math.pi * a * a),
        duration_s=DURATION_COEFF * d / speed_m_s,
        elastic_energy_j=0.4 * k * d ** 2.5,
    )


@dataclass(frozen=True)
class Support:
    """How the struck core is held. Build with ``hand_held`` or ``on_anvil``."""

    kind: str  # "hand" or "anvil"
    stiffness_n_m: float = 0.0  # hand spring
    anvil_mass_kg: float = math.inf
    anvil_material: Material | None = None
    anvil_radius_m: float = 0.0  # radius of curvature at the core-anvil contact

    def __post_init__(self) -> None:
        if self.kind == "hand":
            if not (self.stiffness_n_m >= 0 and math.isfinite(self.stiffness_n_m)):
                raise ValueError("hand stiffness must be finite and >= 0")
        elif self.kind == "anvil":
            if self.anvil_material is None or not self.anvil_radius_m > 0 or not self.anvil_mass_kg > 0:
                raise ValueError("anvil needs a material, a positive contact radius and mass")
        else:
            raise ValueError("support kind must be 'hand' or 'anvil'")


# ASSUMPTION: order of magnitude of a grip on a held stone; not from a cited
# measurement. Results are insensitive to it (see tests).
DEFAULT_HAND_STIFFNESS_N_M = 5.0e4


def hand_held(stiffness_n_m: float = DEFAULT_HAND_STIFFNESS_N_M) -> Support:
    return Support("hand", stiffness_n_m=stiffness_n_m)


def on_anvil(anvil_material: Material, contact_radius_m: float, anvil_mass_kg: float = math.inf) -> Support:
    return Support("anvil", anvil_material=anvil_material, anvil_radius_m=contact_radius_m,
                   anvil_mass_kg=anvil_mass_kg)


@dataclass(frozen=True)
class ImpactHistory:
    max_force_n: float  # hammer-core contact
    max_approach_m: float
    duration_s: float  # hammer-core contact time
    max_support_force_n: float  # core-anvil contact, or hand spring
    max_elastic_energy_j: float  # peak elastic energy stored in all contacts
    hammer_velocity_after_m_s: float
    core_velocity_after_m_s: float
    anvil_velocity_after_m_s: float  # 0 for a fixed anvil or a hand
    energy_error: float  # relative drift of total mechanical energy
    t_s: np.ndarray
    force_n: np.ndarray  # hammer-core force history
    contact_energy_j: np.ndarray | None = None  # hammer-core contact energy history
    support_energy_j: np.ndarray | None = None  # hand spring or core-anvil contact energy history


def lumped_impact(hammer_mass_kg: float, hammer_speed_m_s: float, hammer_radius_m: float,
                  e_star_hammer_pa: float, core_mass_kg: float, support: Support,
                  core_material: Material | None = None, rtol: float = 1e-10,
                  max_energy_error: float = 1e-6) -> ImpactHistory:
    """Integrate hammer -> core -> support along the strike line until the
    hammer leaves the core. Hertz contacts are elastic and lossless, so the
    total energy must stay constant; a drift above ``max_energy_error``
    raises. ``hammer_radius_m`` is the effective radius (``effective_radius``)."""
    if not (hammer_mass_kg > 0 and hammer_speed_m_s > 0 and core_mass_kg > 0):
        raise ValueError("masses and speed must be positive")
    k1 = hertz_stiffness(hammer_radius_m, e_star_hammer_pa)
    mh, mc, v0 = hammer_mass_kg, core_mass_kg, hammer_speed_m_s
    if support.kind == "anvil":
        if core_material is None:
            raise ValueError("core_material is needed for the core-anvil contact")
        k2 = hertz_stiffness(support.anvil_radius_m, contact_modulus(core_material, support.anvil_material))
        ma = support.anvil_mass_kg
    else:
        k2, ma = support.stiffness_n_m, math.inf
    fixed_anvil = math.isinf(ma)

    def support_force(xc, xa):
        if support.kind == "hand":
            return k2 * xc  # spring from rest position; pulls back if xc < 0
        d2 = xc - xa
        return k2 * d2 ** 1.5 if d2 > 0 else 0.0

    def support_energy(xc, xa):
        if support.kind == "hand":
            return 0.5 * k2 * xc * xc
        d2 = xc - xa
        return 0.4 * k2 * d2 ** 2.5 if d2 > 0 else 0.0

    def rhs(_t, y):
        xh, xc, xa, vh, vc, va = y
        d1 = xh - xc
        f1 = k1 * d1 ** 1.5 if d1 > 0 else 0.0
        f2 = support_force(xc, xa)
        aa = 0.0 if fixed_anvil else f2 / ma
        return [vh, vc, va, -f1 / mh, (f1 - f2) / mc, aa]

    def separated(_t, y):
        return y[0] - y[1]

    separated.terminal = True
    separated.direction = -1

    # hammer starts touching (d1 = 0) and moving in +x
    y0 = [0.0, 0.0, 0.0, v0, 0.0, 0.0]
    t_scale = hertz_impact(reduced_mass(mh, mc), v0, hammer_radius_m, e_star_hammer_pa).duration_s
    # upper bound: whole hammer mass against the softest contact path
    k_slow = k1 if support.kind == "hand" else (k1 ** (-2 / 3) + k2 ** (-2 / 3)) ** -1.5
    t_max = 50.0 * DURATION_COEFF * (15.0 * mh * v0 ** 2 / (8.0 * 1.5 * k_slow)) ** 0.4 / v0
    # first step must leave d1 = 0 before the separation event is armed
    # separate absolute tolerances for positions (m) and velocities (m/s)
    atol = np.array([1e-14 * v0 * t_scale] * 3 + [1e-14 * v0] * 3)
    sol = solve_ivp(rhs, (0.0, max(t_max, 50.0 * t_scale)), y0, method="DOP853", rtol=rtol,
                    atol=atol, events=separated, dense_output=True,
                    first_step=1e-4 * t_scale)
    if sol.t_events[0].size == 0:
        raise RuntimeError("hammer did not separate from the core within the time bound")
    t_end = float(sol.t_events[0][0])
    t = np.linspace(0.0, t_end, 4001)
    Y = sol.sol(t)
    d1 = np.clip(Y[0] - Y[1], 0.0, None)
    f1 = k1 * d1 ** 1.5
    f2 = np.array([support_force(xc, xa) for xc, xa in zip(Y[1], Y[2])])
    e_contact = 0.4 * k1 * d1 ** 2.5
    e_support = np.array([support_energy(xc, xa) for xc, xa in zip(Y[1], Y[2])])
    elastic = e_contact + e_support
    kin_a = 0.0 if fixed_anvil else 0.5 * ma * Y[5] ** 2
    total = 0.5 * mh * Y[3] ** 2 + 0.5 * mc * Y[4] ** 2 + kin_a + elastic
    e0 = 0.5 * mh * v0 ** 2
    energy_error = float(np.abs(total - e0).max() / e0)
    if energy_error > max_energy_error:
        raise RuntimeError(f"energy drift {energy_error:.2e} exceeds {max_energy_error:.0e}")
    # refine the peak of d1 on the dense solution (samples alone miss it)
    i = int(np.argmax(d1))
    lo, hi = t[max(i - 1, 0)], t[min(i + 1, t.size - 1)]
    pk = minimize_scalar(lambda s: -(sol.sol(s)[0] - sol.sol(s)[1]), bounds=(lo, hi), method="bounded",
                         options={"xatol": 1e-12 * t_end})
    d_peak = max(float(-pk.fun), float(d1[i]))
    return ImpactHistory(
        max_force_n=k1 * d_peak ** 1.5,
        max_approach_m=d_peak,
        duration_s=t_end,
        max_support_force_n=float(np.abs(f2).max()),
        max_elastic_energy_j=float(elastic.max()),
        hammer_velocity_after_m_s=float(Y[3, -1]),
        core_velocity_after_m_s=float(Y[4, -1]),
        anvil_velocity_after_m_s=float(Y[5, -1]),
        energy_error=energy_error,
        t_s=t,
        force_n=f1,
        contact_energy_j=e_contact,
        support_energy_j=e_support,
    )


# ASSUMPTION: hammerstone material when none is given (granite is in the spec
# material list and is a common hammerstone rock); pass hammer_material= to change it
DEFAULT_HAMMER_MATERIAL = "granite"


@dataclass(frozen=True)
class StrikeResult:
    pieces: list  # Stone per piece, heaviest first; masses sum to the struck stone
    fracture_energy_j: float  # phase-field crack energy of the section
    seconds: float  # wall time of the strike
    budget_j: float  # work allowed on the core (02 sec. 4.4-4.5)
    impact: ImpactHistory  # elastic hammer-core-support collision (part a)
    blow: object  # strike2d.BlowResult: mesh, force-approach history, u, d, cell damage
    contact_modulus_pa: float  # E* hammer-core
    rigid_radius_m: float  # equivalent rigid radius on the core
    quasi_static_ratio: float  # contact time / (largest stone extent / P-wave speed); should be >> 1
    converged: bool  # every staggered step converged
    work_j: float  # work done on the section (= budget unless released)
    released: bool  # force fell below strike2d.RELEASE_FRACTION of its peak before the budget was used


def strike(stone, contact_point_m, direction, hammer_mass_kg: float, hammer_speed_m_s: float,
           hammer_radius_m: float, support: Support, *, hammer_material: Material | None = None,
           n_steps: int = 10, max_iter: int = 300, tol: float = 1e-3, split: str = "rankine",
           progress=None) -> StrikeResult:
    """Strike a 2D stone section with a hammerstone (api.md).

    1. Elastic collision hammer -> core -> support (``lumped_impact``) with
       the stone mass, giving the peak elastic energy of the contacts.
    2. Budget: core share of that energy, max over time of
       s1 E_contact(t) + s2 E_support(t), s = E*/E'_core of each contact
       (``indentation.core_energy_share``; s2 = 0 for a hand).
    3. The equivalent rigid indenter does at most this work on the section
       (``strike2d.fracture_blow``); broken cells split the pieces.

    ``hammer_radius_m`` is the radius of curvature of the hammer at the
    contact; the stone surface is taken as flat (effective radius = hammer
    radius). ``direction`` is the hammer velocity direction in the section
    plane (x, y)."""
    import time

    from . import indentation as ind
    from . import strike2d
    from .materials import load_material

    if stone.dim != 2:
        raise ValueError("strike needs a 2D stone (3D is step 9)")
    start = time.perf_counter()
    core = load_material(stone.material_name)
    hammer = load_material(DEFAULT_HAMMER_MATERIAL) if hammer_material is None else hammer_material
    e_star = contact_modulus(hammer, core)
    history = lumped_impact(hammer_mass_kg, hammer_speed_m_s, hammer_radius_m, e_star, stone.mass_kg,
                            support, core_material=core)
    energy = ind.core_energy_share(e_star, core) * history.contact_energy_j
    anvil_radius = None
    if support.kind == "anvil":
        e_star_a = contact_modulus(core, support.anvil_material)
        energy = energy + ind.core_energy_share(e_star_a, core) * history.support_energy_j
        anvil_radius = ind.equivalent_rigid_radius(support.anvil_radius_m, e_star_a, core)
    budget = float(energy.max())
    radius = ind.equivalent_rigid_radius(hammer_radius_m, e_star, core)
    blow = strike2d.fracture_blow(stone, contact_point_m, direction, radius, budget,
                                  anvil_rigid_radius_m=anvil_radius, split=split, n_steps=n_steps,
                                  tol=tol, max_iter=max_iter, progress=progress)
    extent = float(np.max(np.array(stone.cells.shape) * stone.cell_size_m))
    # fastest wave: longitudinal (P) wave c_L = sqrt((lam + 2 mu) / rho)
    wave = max(math.sqrt(p.youngs_modulus_pa * (1 - p.poisson_ratio)
                         / ((1 + p.poisson_ratio) * (1 - 2 * p.poisson_ratio) * p.density_kg_m3))
               for p in stone.phases)
    return StrikeResult(
        pieces=blow.pieces,
        fracture_energy_j=blow.indent.fracture_energy_j,
        seconds=time.perf_counter() - start,
        budget_j=budget,
        impact=history,
        blow=blow,
        contact_modulus_pa=e_star,
        rigid_radius_m=radius,
        quasi_static_ratio=history.duration_s / (extent / wave),
        converged=blow.indent.converged,
        work_j=float(blow.indent.work_j[-1]),
        released=blow.indent.released,
    )
