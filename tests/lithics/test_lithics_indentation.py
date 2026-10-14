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


def test_energy_budget_and_balance(cone_run):
    _, r = cone_run
    assert abs(r.work_j[-1] / r.budget_j - 1) <= 0.02
    assert np.all(np.diff(r.work_j) > 0)
    assert r.fracture_energy_j > 0
    # quasi-static: work in >= stored + dissipated in the crack; the rest is
    # released by unstable growth and the trapezoid error
    stored = r.elastic_energy_j + r.fracture_energy_j
    assert stored <= r.work_j[-1] * 1.005
    assert stored >= 0.95 * r.work_j[-1]


def test_rankine_threshold_any_mode():
    """Damage driving force reaches the AT1 threshold 3 G_c / (16 l) exactly
    when the largest principal stress equals sigma_t, in every mode, and
    vanishes in compression."""
    m = contact.tensor_mesh(np.linspace(1e-3, 2e-3, 3), np.linspace(0, 1e-3, 3), GLASS.youngs_modulus_pa,
                            GLASS.poisson_ratio)
    for mode in ("plane_strain", "plane_stress", "axisymmetric"):
        gc, ell = pf.material_constants(GLASS, mode)
        u = np.zeros(m.n_dof)
        u[1::2] = 1e-4 * m.nodes[:, 1]
        pos, _ = pf.energy_split(m, mode, u, "rankine")
        s = pf.fem2d.element_stress(m, mode, u)
        s1 = s[:, 1]  # sigma_zz along y is the largest principal stress here
        assert np.allclose(pos, (s1 ** 2 / (2 * GLASS.youngs_modulus_pa))[:, None], rtol=1e-12)
        sigma_at_threshold = math.sqrt(2 * GLASS.youngs_modulus_pa * 3 * gc / (16 * ell))
        assert sigma_at_threshold == pytest.approx(GLASS.tensile_strength_pa, rel=1e-12)
        neg_pos, _ = pf.energy_split(m, mode, -u, "rankine")
        assert neg_pos.max() == 0.0


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
