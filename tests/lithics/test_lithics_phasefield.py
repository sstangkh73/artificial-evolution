"""Phase-field fracture (AT1), step 3 part a: length from material constants,
exact 1D crack profile and energy, elastic threshold, energy split, bounded
damage solver, and crack onset at K_IC on a single-edge-notch specimen."""
import math

import numpy as np
import pytest
from scipy.optimize import minimize

from lithics import contact, fem2d
from lithics import phasefield as pf
from lithics.materials import load_material

GLASS = load_material("glass_soda_lime")
E, NU = GLASS.youngs_modulus_pa, GLASS.poisson_ratio
GC, ELL = pf.material_constants(GLASS, "plane_strain")
SIGMA_C = GLASS.tensile_strength_pa


def test_length_from_material_constants():
    """Hand values for soda-lime glass (spec: E 71 GPa, nu 0.22, K_IC 0.75
    MPa m^0.5, sigma_t 41 MPa): G_c = K^2 (1 - nu^2) / E = 7.5391 J/m^2 and
    l = 3 G_c E / (8 sigma_t^2) = 0.11941 mm; plane stress G_c = K^2 / E =
    7.9225 J/m^2, l = 3 K^2 / (8 sigma_t^2) = 0.12548 mm."""
    assert math.isclose(GC, 7.5391, rel_tol=1e-4)
    assert math.isclose(ELL, 0.11941e-3, rel_tol=1e-4)
    assert math.isclose(GC, GLASS.fracture_energy_j_m2, rel_tol=1e-12)
    gc_ps, ell_ps = pf.material_constants(GLASS, "plane_stress")
    assert math.isclose(gc_ps, 7.9225, rel_tol=1e-4)
    assert math.isclose(ell_ps, 0.12548e-3, rel_tol=1e-4)
    assert pf.material_constants(GLASS, "axisymmetric") == (GC, ELL)
    with pytest.raises(ValueError):
        pf.regularization_length(GC, E, 0.0)


def test_gauss_point_scale_matches_element_scale():
    m = contact.tensor_mesh(np.linspace(0, 1e-3, 5), np.linspace(0, 1e-3, 4), E, NU)
    s = np.linspace(0.2, 1.0, len(m.elements))
    K1 = fem2d.assemble(m, "plane_strain", s)
    K4 = fem2d.assemble(m, "plane_strain", np.repeat(s[:, None], 4, axis=1))
    assert abs(K1 - K4).max() <= 1e-12 * abs(K1).max()
    with pytest.raises(ValueError):
        fem2d.assemble(m, "plane_strain", np.ones((len(m.elements), 3)))


@pytest.mark.parametrize("n_per_ell", [4, 8])
def test_at1_crack_profile_and_energy(n_per_ell):
    """With d = 1 on a line and no strain energy, AT1 gives d = (1 - |x|/2l)^2
    on |x| < 2l and dissipates exactly G_c per unit crack area."""
    h = ELL / n_per_ell
    x = np.arange(-6 * ELL, 6 * ELL + h / 2, h)
    m = contact.tensor_mesh(x, np.array([0.0, h]), E, NU)
    lower = np.where(np.abs(m.nodes[:, 0]) < h / 4, 1.0, 0.0)
    res = pf.solve_damage(m, "plane_strain", np.zeros((len(m.elements), 4)), GC, ELL, lower)
    assert res.converged
    exact = np.clip(1 - np.abs(m.nodes[:, 0]) / (2 * ELL), 0, None) ** 2
    assert np.abs(res.d - exact).max() < 1e-9
    energy_per_area = pf.fracture_energy(m, "plane_strain", res.d, GC, ELL) / (h * m.thickness_m)
    assert abs(energy_per_area / GC - 1) < 0.005


def test_bounded_solver_satisfies_kkt():
    rng = np.random.default_rng(3)
    n = 30
    Q = rng.normal(size=(n, n))
    A = Q @ Q.T + n * np.eye(n)
    b = rng.normal(size=n) * 20
    lo, hi = np.zeros(n), np.ones(n)
    lo[:5] = 0.5
    import scipy.sparse as sp
    res = pf.solve_bounded(sp.csr_matrix(A), b, lo, hi)
    assert res.converged
    x = res.d
    ref = minimize(lambda z: 0.5 * z @ A @ z - b @ z, np.full(n, 0.5), jac=lambda z: A @ z - b,
                   bounds=list(zip(lo, hi)), method="L-BFGS-B", options={"ftol": 1e-14, "gtol": 1e-12})
    assert np.abs(x - ref.x).max() < 1e-5
    g = A @ x - b
    tol = 1e-9 * np.abs(b).max()
    assert np.all(x >= lo) and np.all(x <= hi)
    free = (x > lo) & (x < hi)
    assert np.all(np.abs(g[free]) < tol)
    assert np.all(g[x == lo] >= -tol) and np.all(g[(x == hi) & (x > lo)] <= tol)


def _uniform_strain(m, mode, strain):
    """Nodal u of a homogeneous strain (e_xx, e_yy, g_xy) in the mesh plane."""
    X, Y = m.nodes[:, 0], m.nodes[:, 1]
    exx, eyy, gxy = strain
    u = np.zeros(m.n_dof)
    u[0::2] = exx * X + 0.5 * gxy * Y
    u[1::2] = eyy * Y + 0.5 * gxy * X
    return u


@pytest.mark.parametrize("mode", fem2d.MODES)
@pytest.mark.parametrize("split", pf.SPLITS)
def test_split_sums_to_total_energy(mode, split):
    m = contact.tensor_mesh(np.linspace(1e-4, 1e-3, 4), np.linspace(0, 1e-3, 4), E, NU)
    D = fem2d.constitutive(m.youngs_pa[:1], m.poisson[:1], mode)[0]
    rng = np.random.default_rng(0)
    for _ in range(5):
        u = _uniform_strain(m, mode, rng.normal(size=3) * 1e-4)
        pos, neg = pf.energy_split(m, mode, u, split)
        assert np.all(pos >= 0) and np.all(neg >= 0)
        for g, (xi, eta) in enumerate(fem2d.GAUSS_POINTS):
            B, _ = fem2d._b_matrices(m, mode, xi, eta)
            e = np.einsum("eki,ei->ek", B, u[fem2d._element_dofs(m)])
            total = 0.5 * np.einsum("ek,kl,el->e", e, D, e)
            assert np.allclose(pos[:, g] + neg[:, g], total, rtol=1e-10, atol=0)


@pytest.mark.parametrize("split", ["spectral", "voldev"])
def test_no_damage_drive_in_hydrostatic_compression(split):
    """Axisymmetric u = e*(r, z) gives e_r = e_z = e_theta = e: truly
    hydrostatic (in plane strain e_zz = 0, so equal in-plane compression is
    not hydrostatic and voldev rightly sees a deviatoric part)."""
    m = contact.tensor_mesh(np.linspace(0, 1e-3, 4), np.linspace(0, 1e-3, 4), E, NU)
    u = _uniform_strain(m, "axisymmetric", (-1e-3, -1e-3, 0))
    pos, neg = pf.energy_split(m, "axisymmetric", u, split)
    assert np.all(pos <= 1e-12 * neg.max())
    assert neg.min() > 0


def _bar(mode):
    """Bar 4l x 2l pulled along x by prescribed end displacement; uniaxial
    stress (plane stress or axisymmetric cylinder, lateral faces free)."""
    h = ELL / 2
    x = np.arange(0.0, 2 * ELL + h / 2, h)
    y = np.arange(0.0, 4 * ELL + h / 2, h)
    m = contact.tensor_mesh(x, y, E, NU)
    X, Y = m.nodes[:, 0], m.nodes[:, 1]
    bottom, top = np.nonzero(Y < 1e-15)[0], np.nonzero(Y > y[-1] - 1e-15)[0]
    corner = np.nonzero((Y < 1e-15) & (X < 1e-15))[0]
    fixed = np.concatenate([2 * bottom + 1, 2 * top + 1, 2 * corner])
    return m, fixed, bottom, top, y[-1]


@pytest.mark.parametrize("mode", ["plane_stress", "axisymmetric"])
def test_elastic_until_strength_then_softening(mode):
    """AT1 with no split under uniaxial stress: no damage at all below
    sigma_c = sigma_t (the stress is computed from the strain, independent of
    the damage coefficients); above it the homogeneous bar damages and the
    stress drops (Tanne et al. 2018)."""
    gc, ell = pf.material_constants(GLASS, mode)
    m, fixed, bottom, top, L = _bar(mode)
    vals = lambda eps: np.concatenate([0 * bottom, eps * L + 0 * top, [0.0]])
    d0 = np.zeros(len(m.nodes))
    below = pf.staggered_step(m, mode, d0, gc, ell, fixed, vals(0.99 * SIGMA_C / E), split="none")
    assert below.converged and below.d.max() == 0.0
    s = fem2d.element_stress(m, mode, below.u)
    assert np.allclose(s[:, 1], 0.99 * SIGMA_C, rtol=1e-6)
    above = pf.staggered_step(m, mode, d0, gc, ell, fixed, vals(1.02 * SIGMA_C / E), split="none")
    assert above.converged and above.d.min() > 0.01
    s = fem2d.element_stress(m, mode, above.u, pf.degradation(pf.at_gauss_points(m, above.d)))
    assert s[:, 1].max() < SIGMA_C


@pytest.mark.parametrize("mode", fem2d.MODES)
@pytest.mark.parametrize("split", ["spectral", "voldev"])
def test_split_threshold_in_uniaxial_tension(mode, split):
    """With a split, psi+ < psi in uniaxial tension, so damage starts above
    sigma_t; the start must be the stress where max psi+ = 3 G_c / (16 l)
    (derivative of the AT1 energy at d = 0), and below it d stays 0."""
    gc, ell = pf.material_constants(GLASS, mode)
    m, fixed, bottom, top, L = _bar(mode)
    vals = lambda eps: np.concatenate([0 * bottom, eps * L + 0 * top, [0.0]])
    d0 = np.zeros(len(m.nodes))
    unit = fem2d.solve(m, mode, fixed, vals(1.0))
    pos, _ = pf.energy_split(m, mode, unit, split)
    eps_c = math.sqrt(3 * gc / (16 * ell) / pos.max())
    assert 0.9 < eps_c * E / SIGMA_C < 1.2
    below = pf.staggered_step(m, mode, d0, gc, ell, fixed, vals(0.99 * eps_c), split=split)
    assert below.converged and below.d.max() == 0.0
    above = pf.staggered_step(m, mode, d0, gc, ell, fixed, vals(1.02 * eps_c), split=split)
    assert above.converged and above.d.min() > 0.005


def test_irreversibility_and_bounds():
    m, fixed, bottom, top, L = _bar("plane_strain")
    vals = lambda eps: np.concatenate([0 * bottom, eps * L + 0 * top, [0.0]])
    d = pf.staggered_step(m, "plane_strain", np.zeros(len(m.nodes)), GC, ELL, fixed,
                          vals(1.2 * SIGMA_C / E)).d
    assert d.min() > 0
    unloaded = pf.staggered_step(m, "plane_strain", d, GC, ELL, fixed, vals(0.0))
    assert np.array_equal(unloaded.d, d)  # no healing
    assert np.all(unloaded.d <= 1.0)
    with pytest.raises(ValueError):
        pf.staggered_step(m, "plane_strain", d + 1.0, GC, ELL, fixed, vals(0.0))
    with pytest.raises(ValueError):
        pf.energy_split(m, "plane_strain", np.zeros(m.n_dof), "other")


def _graded(lo, hi, h0, start, end):
    xs, step = list(np.arange(lo, hi + h0 / 2, h0)), h0
    while xs[-1] < end - 1e-15:
        step *= 1.15
        xs.append(min(xs[-1] + step, end))
    left, step = [xs[0]], h0
    while left[-1] > start + 1e-15:
        step *= 1.15
        left.append(max(left[-1] - step, start))
    return np.array(left[::-1][:-1] + xs)


def test_sen_crack_starts_near_k_ic():
    """Half SEN specimen (a = 20 l, a/W = 0.3, half height 2W), top edge
    displaced, the nodes on the crack faces start at d = 1. K for the
    applied displacement comes from the J-integral of the undamaged elastic
    solution (linear in the displacement). The crack must stay put at
    0.95 K_IC and run at 1.10 K_IC. One-off runs outside the test (see 02
    sec. 3.3) bracketed the onset more tightly."""
    a = 20 * ELL
    W, h = a / 0.3, ELL / 4
    x = _graded(a - 4 * ELL, a + 12 * ELL, h, 0.0, W)
    y = _graded(0.0, 6 * ELL, h, 0.0, 2 * W)
    m = contact.tensor_mesh(x, y, E, NU)
    X, Y = m.nodes[:, 0], m.nodes[:, 1]
    lig = np.nonzero((Y < 1e-15) & (X >= a - 1e-12))[0]
    top = np.nonzero(Y > 2 * W - 1e-12)[0]
    pin = np.nonzero((Y > 2 * W - 1e-12) & (X < 1e-12))[0]
    fixed = np.concatenate([2 * lig + 1, 2 * top + 1, 2 * pin])
    vals = lambda delta: np.concatenate([0 * lig, delta + 0 * top, [0.0]])
    u1 = fem2d.solve(m, "plane_strain", fixed, vals(1.0))
    j1 = 2 * fem2d.j_integral(m, "plane_strain", u1, (a, 0.0), 0.1 * a, 0.3 * a)
    k_per_m = math.sqrt(j1 * E / (1 - NU ** 2))
    kic = GLASS.fracture_toughness_pa_sqrt_m
    d0 = np.zeros(len(m.nodes))
    d0[(Y < 1e-15) & (X <= a + 1e-12)] = 1.0

    def tip(d):
        broken = X[(d > 0.95) & (Y < 1e-15)]
        return broken.max() - a

    hold = pf.staggered_step(m, "plane_strain", d0, GC, ELL, fixed, vals(0.95 * kic / k_per_m))
    assert hold.converged and tip(hold.d) < 0.5 * h
    run = pf.staggered_step(m, "plane_strain", hold.d, GC, ELL, fixed, vals(1.10 * kic / k_per_m),
                            max_iter=60)
    assert tip(run.d) > 2 * ELL
    off_line = (Y > 4 * ELL) & (X > a)
    assert run.d[off_line].max() < 0.5  # damage stays on the crack plane
