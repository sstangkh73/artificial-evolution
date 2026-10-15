"""Step 4 part b: fracture under a hammer blow (``lithics.indentation``).

A rigid sphere (radius R' = 50 mm, the equivalent rigid radius of a hammer
of about 25 mm on glass) is pushed into an axisymmetric glass block until
the work on the block reaches an energy budget. Checks: equivalence of the
elastic hammer and the rigid indenter (Johnson 1985 sec. 4.2), Hertz force in
the elastic regime, the energy budget and energy balance, and that a ring
crack starts outside the contact circle and runs down and outward (Hertzian
cone; Frank & Lawn 1967, Proc. R. Soc. A 299:291). The cone ANGLE is not
checked here (V1, step 7). The fracture run uses h = l/2 to keep the test
short; mesh convergence is step 6 (V6)."""
import math

import numpy as np
import pytest
from scipy.optimize import lsq_linear
from scipy.stats import spearmanr

from lithics import contact
from lithics import indentation as ind
from lithics import phasefield as pf
from lithics.impact import contact_modulus
from lithics.materials import load_material

GLASS = load_material("glass_soda_lime")
GRANITE = load_material("granite")
GC, ELL = pf.material_constants(GLASS, "axisymmetric")
E_PRIME = GLASS.youngs_modulus_pa / (1 - GLASS.poisson_ratio ** 2)
R_RIGID = 0.05
SIZE = 8e-3  # block radius and depth


def _mesh(h, fine):
    return ind.indentation_mesh(GLASS, h, fine, fine, SIZE, SIZE)


def test_equivalent_rigid_radius_gives_same_contact_radius():
    e_star = contact_modulus(GRANITE, GLASS)
    r_hammer = 0.03
    r_eq = ind.equivalent_rigid_radius(r_hammer, e_star, GLASS)
    for p in (10.0, 1e3, 3e4):
        two_body = contact.hertz_sphere_flat(p, r_hammer, e_star)
        rigid = contact.hertz_sphere_flat(p, r_eq, E_PRIME)
        assert rigid.contact_radius_m == pytest.approx(two_body.contact_radius_m, rel=1e-12)
        assert rigid.max_pressure_pa == pytest.approx(two_body.max_pressure_pa, rel=1e-12)
        # the approach of the core alone is the share E*/E' of the mutual approach
        share = ind.core_energy_share(e_star, GLASS)
        assert rigid.approach_m == pytest.approx(share * two_body.approach_m, rel=1e-12)


def test_core_energy_share_hand_values():
    # same material: E* = E'/2, half the work goes into each body
    assert ind.core_energy_share(E_PRIME / 2, GLASS) == pytest.approx(0.5, rel=1e-12)
    # rigid hammer: E* = E', all work into the core
    assert ind.core_energy_share(E_PRIME, GLASS) == pytest.approx(1.0, rel=1e-12)
    with pytest.raises(ValueError):
        ind.core_energy_share(1.5 * E_PRIME, GLASS)


def test_graded_axis():
    x = ind.graded_axis(1e-3, 1e-4, 1e-2, growth=1.2)
    assert x[0] == 0 and x[-1] == pytest.approx(1e-2, rel=1e-12)
    assert np.allclose(np.diff(x[x <= 1e-3 + 1e-12]), 1e-4)
    dx = np.diff(x)
    assert np.all(dx > 0)
    assert np.all(dx[1:-1] / dx[:-2] <= 1.2 + 1e-9)
    assert dx[-1] / dx[-2] <= 1.5 * 1.2  # last element may absorb a sliver
    # fine region covering the whole extent: uniform, ends exactly at extent
    assert np.allclose(ind.graded_axis(1e-3, 1e-3, 1e-3), [0.0, 1e-3])
    x = ind.graded_axis(1e-3, 3e-4, 1e-3)
    assert x[-1] == pytest.approx(1e-3, rel=1e-12) and x.max() <= 1e-3 and np.all(np.diff(x) > 0)


@pytest.fixture(scope="module")
def elastic_run():
    # budget below cracking: radial surface tension (1-2nu)p0/3 at the
    # contact edge stays under sigma_t
    m = _mesh(ELL / 4, 0.6e-3)
    return m, ind.indent_with_budget(m, 0.0, -SIZE, R_RIGID, 1e-6, GC, ELL, split="rankine", n_steps=4)


def test_elastic_regime_matches_hertz_and_budget(elastic_run):
    m, r = elastic_run
    assert r.converged
    assert r.d.max() == 0.0
    assert r.fracture_energy_j == 0.0
    a = math.sqrt(R_RIGID * r.approach_m[-1])
    p0 = 2 * E_PRIME * a / (math.pi * R_RIGID)
    assert (1 - 2 * GLASS.poisson_ratio) * p0 / 3 < 0.75 * GLASS.tensile_strength_pa
    hertz = 4 / 3 * E_PRIME * math.sqrt(R_RIGID) * r.approach_m[1:] ** 1.5
    assert np.allclose(r.force_n[1:], hertz, rtol=0.05)
    assert abs(r.work_j[-1] / r.budget_j - 1) <= 0.02
    # no fracture: work of the indenter = stored elastic energy (trapezoid error)
    assert r.elastic_energy_j == pytest.approx(r.work_j[-1], rel=0.03)


@pytest.fixture(scope="module")
def cone_run():
    m = _mesh(ELL / 2, 1.6e-3)
    r = ind.indent_with_budget(m, 0.0, -SIZE, R_RIGID, 0.03, GC, ELL, split="rankine",
                               n_steps=10, max_iter=300)
    return m, r


def test_cone_crack_starts_outside_contact_and_runs_down_and_out(cone_run):
    m, r = cone_run
    assert r.converged
    centre = m.nodes[m.elements].mean(axis=1)
    broken = r.d[m.elements].mean(axis=1) > 0.9
    assert broken.sum() >= 10
    rb, zb = centre[broken, 0], centre[broken, 1]
    # nothing breaks under the contact centre (Rankine: compression does not drive damage)
    assert not np.any(broken & (centre[:, 0] < 0.5 * r.contact_radius_m[-1]))
    # the crack is open at the surface and reaches well below it
    assert zb.max() > -ELL and zb.min() < -4 * ELL
    # deeper parts lie at larger radius (cone opening downward)
    rho, p = spearmanr(-zb, rb)
    assert rho > 0.8 and p < 1e-6
    # the ring starts outside the circle that was in contact when damage first appeared
    surface_ring = rb[zb > -ELL].min()
    first_damage = int(np.argmax(r.fracture_energy_steps_j > 0))
    assert first_damage > 0
    assert surface_ring > r.contact_radius_m[first_damage]
    # regression bounds (+-20 %) around the values of the single run reported
    # in 02 sec. 4.4; they are not an independent reference
    assert 0.98e-3 < surface_ring < 1.46e-3
    assert 0.65e-3 < -zb.min() < 0.97e-3
    assert 2.3e3 < r.force_n[-1] < 3.45e3


def test_energy_budget_and_work_inequality(cone_run):
    _, r = cone_run
    assert abs(r.work_j[-1] / r.budget_j - 1) <= 0.02
    assert np.all(np.diff(r.work_j) > 0)
    assert r.fracture_energy_j > 0
    # d never decreases, so K(d) never stiffens and the work of the indenter
    # bounds the stored energy 1/2 u.K(d).u (up to the trapezoid error).
    # W - stored is NOT required to equal the phase-field fracture energy:
    # the hybrid scheme is not variational (02 sec. 4.4)
    assert 0 < r.elastic_energy_j <= r.work_j[-1] * 1.005


def _homogeneous(mode, e1, e2):
    """Block whose boundary nodes follow u_x = e1 x, u_y = e2 y (axisymmetric:
    u_r = e1 r, so e_r = e_theta = e1); the interior solves to the same
    homogeneous field. Returns mesh, fixed dofs and a scale -> values map."""
    h = ELL / 2
    x0 = 1e-3 if mode == "axisymmetric" else 0.0
    m = contact.tensor_mesh(x0 + np.arange(0, 2 * ELL + h / 2, h), np.arange(0, 2 * ELL + h / 2, h),
                            GLASS.youngs_modulus_pa, GLASS.poisson_ratio)
    X, Y = m.nodes[:, 0], m.nodes[:, 1]
    edge = np.nonzero((X < X.min() + 1e-15) | (X > X.max() - 1e-15) | (Y < 1e-15) | (Y > Y.max() - 1e-15))[0]
    fixed = np.concatenate([2 * edge, 2 * edge + 1])
    return m, fixed, lambda s: s * np.concatenate([e1 * X[edge], e2 * Y[edge]])


@pytest.mark.parametrize("mode,e1,e2", [
    ("plane_strain", 1.0, 0.5),    # biaxial tension, sigma_zz = lam tr e > 0 too
    ("plane_stress", 1.0, -1.0),   # tension + compression
    ("axisymmetric", 1.0, -2.0),   # equal radial and hoop tension, axial compression
])
def test_rankine_damage_starts_at_tensile_strength_in_multiaxial_states(mode, e1, e2):
    """Rankine + AT1 on a homogeneous multiaxial state: no damage at
    sigma_1 = 0.99 sigma_t, damage everywhere at 1.02 sigma_t. sigma_1 is
    computed here by hand from Hooke's law, independent of the code."""
    E, nu = GLASS.youngs_modulus_pa, GLASS.poisson_ratio
    lam, mu = E * nu / ((1 + nu) * (1 - 2 * nu)), E / (2 * (1 + nu))
    if mode == "plane_strain":
        s = [lam * (e1 + e2) + 2 * mu * e1, lam * (e1 + e2) + 2 * mu * e2, lam * (e1 + e2)]
    elif mode == "plane_stress":
        s = [E / (1 - nu ** 2) * (e1 + nu * e2), E / (1 - nu ** 2) * (e2 + nu * e1), 0.0]
    else:
        tr = 2 * e1 + e2
        s = [lam * tr + 2 * mu * e1, lam * tr + 2 * mu * e2, lam * tr + 2 * mu * e1]
    s1_unit = max(s)
    gc, ell = pf.material_constants(GLASS, mode)
    m, fixed, vals = _homogeneous(mode, e1, e2)
    d0 = np.zeros(len(m.nodes))
    scale_t = GLASS.tensile_strength_pa / s1_unit
    below = pf.staggered_step(m, mode, d0, gc, ell, fixed, vals(0.99 * scale_t), split="rankine")
    assert below.converged and below.d.max() == 0.0
    st = pf.fem2d.element_stress(m, mode, below.u)
    assert st[:, 0].max() == pytest.approx(0.99 * scale_t * s[0], rel=1e-6)
    above = pf.staggered_step(m, mode, d0, gc, ell, fixed, vals(1.02 * scale_t), split="rankine")
    assert above.converged and above.d.min() > 0.005
    if min(e1, e2) >= 0:  # reversed: every principal stress compressive, never driven
        pos, _ = pf.energy_split(m, mode, -below.u, "rankine")
        assert pos.max() == 0.0


def test_solve_bounded_fallback_matches_active_set():
    """The fallback chain (max_iter=1 forces it) returns the same minimiser
    as the converged active set method."""
    rng = np.random.default_rng(0)
    n = 60
    M = rng.normal(size=(n, n))
    A = pf.sp.csr_matrix(M @ M.T + n * np.eye(n))
    b = rng.normal(size=n) * n
    lo, up = np.zeros(n), np.ones(n)
    ref = pf.solve_bounded(A, b, lo, up)
    assert ref.converged
    assert pf.kkt_residual(A, b, ref.d, lo, up) < 1e-10
    fb = pf.solve_bounded(A, b, lo, up, max_iter=1)
    assert fb.converged
    assert np.allclose(fb.d, ref.d, atol=1e-5)
    # independent reference: min 1/2 d.A.d - b.d = min |L^T d - L^-1 b|^2 / 2
    # (A = L L^T) with bounds, solved by bounded-variable least squares
    L = np.linalg.cholesky(A.toarray())
    ind_ref = lsq_linear(L.T, np.linalg.solve(L, b), bounds=(lo, up), method="bvls", tol=1e-14).x
    assert np.allclose(ref.d, ind_ref, atol=1e-8)
    assert np.allclose(fb.d, ind_ref, atol=1e-5)
