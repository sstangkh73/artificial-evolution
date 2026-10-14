"""Analytic checks, V11 part 2: Hertz contact pressure (axisymmetric) and the
single-edge-notch stress intensity factor from the J-integral."""
import math

import numpy as np
import pytest

from lithics import contact, fem2d
from lithics.materials import load_material
from lithics.stone import Stone, phases_of

GLASS = load_material("glass_soda_lime")
E, NU = GLASS.youngs_modulus_pa, GLASS.poisson_ratio
E_PLANE_STRAIN = E / (1 - NU ** 2)


# ---------- Hertz ----------

def test_hertz_formulas_are_consistent():
    """Johnson 1985 sec. 4.2: P = 4/3 E* R^1/2 delta^3/2 and p0 = 2 E* a / (pi R)."""
    es = contact.effective_modulus(E, NU)
    assert math.isclose(es, E / (1 - NU ** 2), rel_tol=1e-12)
    assert math.isclose(contact.effective_modulus(E, NU, E, NU), es / 2, rel_tol=1e-12)
    R, P = 0.01, 50.0
    h = contact.hertz_sphere_flat(P, R, es)
    assert math.isclose(h.approach_m, h.contact_radius_m ** 2 / R, rel_tol=1e-12)
    assert math.isclose(4 / 3 * es * math.sqrt(R) * h.approach_m ** 1.5, P, rel_tol=1e-12)
    assert math.isclose(h.max_pressure_pa, 2 * es * h.contact_radius_m / (math.pi * R), rel_tol=1e-12)
    with pytest.raises(ValueError):
        contact.hertz_sphere_flat(-1.0, R, es)


def _indent(n_fine, extent=30.0):
    """Rigid sphere R = 10 mm, approach giving a ~ 0.5 mm, on a glass cylinder
    of radius and height extent*a (bottom held). Uniform elements of size
    1.5a/n_fine up to 1.5a, then growing by 15 % per element."""
    R, a0 = 10e-3, 0.5e-3

    def grid():
        h = 1.5 * a0 / n_fine
        x, step = list(np.arange(0.0, 1.5 * a0 + h / 2, h)), h
        while x[-1] < extent * a0:
            step *= 1.15
            x.append(x[-1] + step)
        return np.array(x)

    g = grid()
    m = contact.tensor_mesh(g, -g[::-1], E, NU)
    res = contact.rigid_sphere_indent(m, 0.0, -g[-1], a0 * a0 / R, R)
    exact = contact.hertz_sphere_flat(res.force_n, R, contact.effective_modulus(E, NU))
    return res, exact, 1.5 * a0 / n_fine


R_SPHERE, A0 = 10e-3, 0.5e-3  # as in _indent
DELTA = A0 * A0 / R_SPHERE


def test_hertz_pmax_against_analytic():
    res, exact, h = _indent(60)
    err = abs(res.surface_pressure_pa[0] / exact.max_pressure_pa - 1)
    assert err <= 0.10  # V11 criterion
    assert err < 0.02  # observed 1.3 %
    assert abs(res.contact_radius_m - exact.contact_radius_m) <= h


def test_hertz_force_and_radius_from_approach():
    """Independent of the measured force: a = sqrt(R delta) and
    P = 4/3 E* R^1/2 delta^3/2. The finite body (bottom held) is a little
    stiffer than a half-space, so P/P_Hertz > 1 and falls as the body grows."""
    es = contact.effective_modulus(E, NU)
    p_hertz = 4 / 3 * es * math.sqrt(R_SPHERE) * DELTA ** 1.5
    ratios = []
    for extent in (30.0, 60.0):
        res, _, h = _indent(60, extent)
        assert abs(res.contact_radius_m - math.sqrt(R_SPHERE * DELTA)) <= h
        ratios.append(res.force_n / p_hertz)
    assert 1.0 < ratios[1] < ratios[0] < 1.03  # observed 1.023, 1.012
    assert ratios[1] < 1.015


def test_contact_complementarity():
    """Signorini conditions at the nodes: no overlap anywhere, only pushing
    forces, and force only where the gap is closed."""
    res, _, _ = _indent(30)
    scale = DELTA
    assert np.all(res.surface_gap_m >= -1e-9 * scale)
    assert np.all(np.abs(res.surface_gap_m[res.in_contact]) <= 1e-9 * scale)
    assert np.all(res.surface_force_n[res.in_contact] > 0)
    assert np.all(np.abs(res.surface_force_n[~res.in_contact]) <= 1e-9 * res.force_n)


def test_hertz_pressure_profile_and_free_surface():
    res, exact, _ = _indent(60)
    r, p, a = res.surface_r_m, res.surface_pressure_pa, exact.contact_radius_m
    inside = r < 0.8 * a
    assert inside.sum() >= 20
    assert np.abs(p[inside] / (exact.max_pressure_pa * np.sqrt(1 - (r[inside] / a) ** 2)) - 1).max() < 0.02
    assert np.abs(p[r > 1.1 * a]).max() < 1e-3 * exact.max_pressure_pa  # free surface outside
    assert np.all(res.surface_force_n > -1e-9 * res.force_n)  # the indenter never pulls
    assert math.isclose(res.surface_force_n.sum(), res.force_n, rel_tol=1e-12)


def test_hertz_pmax_converges_with_mesh():
    e = []
    for n in (15, 30, 60):
        res, exact, _ = _indent(n)
        e.append(abs(res.surface_pressure_pa[0] / exact.max_pressure_pa - 1))
    assert e[0] > e[1] > e[2]
    assert e[1] < 0.03 and e[2] < 0.02  # observed 2.5 %, 1.3 %


def test_indent_rejects_bad_input():
    m = contact.tensor_mesh(np.linspace(0, 1e-3, 4), np.linspace(-1e-3, 0, 4), E, NU)
    with pytest.raises(ValueError):
        contact.rigid_sphere_indent(m, 0.0, -1e-3, -1e-6, 1e-2)
    with pytest.raises(ValueError):
        contact.tensor_mesh(np.array([0.0, 1.0, 0.5]), np.linspace(0, 1, 3), E, NU)


# ---------- SEN K_I ----------

def _tada_sen(aw):
    """Single edge notch, uniform remote tension, bending not restrained:
    K = sigma sqrt(pi a) F(a/W), F from Tada, Paris & Irwin 2000, *The Stress
    Analysis of Cracks Handbook*, 3rd ed., single edge notch entry
    (Tada's 1973 fit, stated accuracy 0.5 % for any a/W)."""
    b = math.pi * aw / 2
    return math.sqrt(math.tan(b) / b) * (0.752 + 2.02 * aw + 0.37 * (1 - math.sin(b)) ** 3) / math.cos(b)


def _sen(n, aw=0.3, domains=((0.1, 0.3),), height_over_w=2.0):
    """Upper half of a plate W x 2H (H = 2W) on the cell grid of a Stone, crack
    of length a on the symmetry line y = 0 (crack faces free, ligament u_y = 0),
    H = height_over_w * W,
    plane strain. Returns K_J / K_Tada - 1 for each J domain (radii in units of a)."""
    W, sigma = 10e-3, 1e6
    h, a, H = W / n, aw * W, height_over_w * W
    ny = int(round(H / h))
    s = Stone(cells=np.ones((ny, n), dtype=np.int16), phases=phases_of(GLASS), cell_size_m=h,
              material_name=GLASS.name, thickness_m=1e-3, origin_m=np.zeros(2))
    m = fem2d.build_mesh(s)
    edges, _ = fem2d.boundary_edges(m)
    top = edges[np.all(np.isclose(m.nodes[edges][:, :, 1], H), axis=1)]
    f = fem2d.traction_forces(m, "plane_strain", top, (0.0, sigma))
    x, y = m.nodes[:, 0], m.nodes[:, 1]
    ligament = np.nonzero(np.isclose(y, 0.0) & (x >= a - 1e-9 * h))[0]
    tip = np.nonzero(np.isclose(y, 0.0) & np.isclose(x, a))[0]
    assert len(tip) == 1
    u = fem2d.solve(m, "plane_strain", np.r_[2 * ligament + 1, 2 * tip], 0.0, f)
    K_exact = sigma * math.sqrt(math.pi * a) * _tada_sen(aw)
    out = []
    for ri, ro in domains:
        J = 2.0 * fem2d.j_integral(m, "plane_strain", u, (a, 0.0), ri * a, ro * a)  # two halves
        assert J > 0
        out.append(math.sqrt(J * E_PLANE_STRAIN) / K_exact - 1)  # Irwin: J = K^2 / E'
    return out


def test_sen_k_from_j_integral():
    err = _sen(100)[0]
    assert abs(err) <= 0.05  # V11 criterion
    assert abs(err) < 0.01  # observed -0.6 %


def test_sen_j_is_domain_independent():
    errs = _sen(100, domains=((0.05, 0.15), (0.1, 0.3), (0.2, 0.5)))
    assert max(errs) - min(errs) < 0.005
    assert max(abs(e) for e in errs) < 0.01


def test_sen_insensitive_to_plate_height():
    """Tada's formula is for a long strip; the half-height 2W used here must
    already be long: going to 3W changes K by less than 0.3 %."""
    k2, k3 = _sen(100)[0], _sen(100, height_over_w=3.0)[0]
    assert abs((1 + k3) / (1 + k2) - 1) < 0.003


def test_sen_converges_with_mesh():
    e50, e100 = abs(_sen(50)[0]), abs(_sen(100)[0])
    assert e50 > e100
    assert e50 < 0.025 and e100 < 0.01  # observed 1.6 %, 0.6 %


def test_sen_other_crack_length():
    assert abs(_sen(100, aw=0.5)[0]) < 0.02


def test_j_is_zero_without_a_crack():
    """Uniform tension, no defect: the domain integral must vanish."""
    h, n = 1e-3, 20
    s = Stone(cells=np.ones((n, n), dtype=np.int16), phases=phases_of(GLASS), cell_size_m=h,
              material_name=GLASS.name, thickness_m=1e-3)
    m = fem2d.build_mesh(s)
    edges, _ = fem2d.boundary_edges(m)
    top = edges[np.all(np.isclose(m.nodes[edges][:, :, 1], n * h), axis=1)]
    f = fem2d.traction_forces(m, "plane_strain", top, (0.0, 1e6))
    bottom = np.nonzero(np.isclose(m.nodes[:, 1], 0.0))[0]
    u = fem2d.solve(m, "plane_strain", np.r_[2 * bottom + 1, 2 * bottom[:1]], 0.0, f)
    J = fem2d.j_integral(m, "plane_strain", u, (10 * h, 10 * h), 2 * h, 6 * h)
    W = (1e6) ** 2 / (2 * E_PLANE_STRAIN)  # strain energy density scale
    assert abs(J) < 1e-9 * W * h


def test_j_integral_rejects_bad_input():
    m = fem2d.build_mesh(Stone(cells=np.ones((4, 4), dtype=np.int16), phases=phases_of(GLASS),
                               cell_size_m=1e-3, material_name=GLASS.name))
    u = np.zeros(m.n_dof)
    with pytest.raises(ValueError):
        fem2d.j_integral(m, "axisymmetric", u, (0.0, 0.0), 1e-3, 2e-3)
    with pytest.raises(ValueError):
        fem2d.j_integral(m, "plane_strain", u, (0.0, 0.0), 2e-3, 1e-3)
