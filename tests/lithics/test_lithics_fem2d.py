"""Analytic checks of the 2D elastic solver (V11 part: bar, Kirsch; plus Lame
for the axisymmetric hoop term)."""
import math

import numpy as np
import pytest

from lithics import fem2d
from lithics.materials import load_material
from lithics.stone import Stone, phases_of

GLASS = load_material("glass_soda_lime")
E, NU = GLASS.youngs_modulus_pa, GLASS.poisson_ratio


def _block(nx, ny, h, origin=(0.0, 0.0), thickness=0.01):
    return Stone(cells=np.ones((ny, nx), dtype=np.int16), phases=phases_of(GLASS),
                 cell_size_m=h, material_name=GLASS.name, thickness_m=thickness,
                 origin_m=np.array(origin))


def _edges_on(mesh, axis, value):
    edges, _ = fem2d.boundary_edges(mesh)
    return edges[np.all(np.isclose(mesh.nodes[edges][:, :, axis], value), axis=1)]


def _nodes_on(mesh, axis, value):
    return np.nonzero(np.isclose(mesh.nodes[:, axis], value, atol=1e-12))[0]


def test_mesh_from_stone_counts_and_material():
    s = _block(5, 3, 1e-3)
    s.cells[0, 0] = 0
    m = fem2d.build_mesh(s)
    assert len(m.elements) == 14
    assert len(m.nodes) == 6 * 4 - 1  # corner node of the removed cell is unused
    assert np.allclose(m.youngs_pa, E) and np.allclose(m.poisson, NU)


def test_rejects_3d_and_bad_mode():
    s3 = Stone(cells=np.ones((2, 2, 2), dtype=np.int16), phases=phases_of(GLASS),
               cell_size_m=1e-3, material_name=GLASS.name)
    with pytest.raises(ValueError):
        fem2d.build_mesh(s3)
    with pytest.raises(ValueError):
        fem2d.assemble(fem2d.build_mesh(_block(2, 2, 1e-3)), "plane")


def test_stiffness_symmetric_and_has_rigid_modes():
    m = fem2d.build_mesh(_block(4, 3, 1e-3))
    K = fem2d.assemble(m, "plane_strain").toarray()
    assert np.allclose(K, K.T, rtol=0, atol=1e-6 * np.abs(K).max())
    x, y = m.nodes[:, 0], m.nodes[:, 1]
    for mode in (np.c_[np.ones_like(x), 0 * x], np.c_[0 * x, np.ones_like(x)], np.c_[-y, x]):
        assert np.abs(K @ mode.ravel()).max() < 1e-6 * np.abs(K).max() * 1e-3


@pytest.mark.parametrize("mode", ["plane_strain", "plane_stress"])
def test_bar_in_tension(mode):
    """Uniaxial tension: e_xx = sigma (1 - nu^2)/E (plane strain) or sigma/E."""
    h, nx, ny, sigma = 1e-3, 40, 8, 5e6
    m = fem2d.build_mesh(_block(nx, ny, h))
    L = nx * h
    f = fem2d.traction_forces(m, mode, _edges_on(m, 0, L), (sigma, 0.0))
    left = _nodes_on(m, 0, 0.0)
    corner = np.nonzero(np.isclose(m.nodes, 0.0).all(axis=1))[0]
    u = fem2d.solve(m, mode, np.r_[2 * left, 2 * corner + 1], 0.0, f)
    exact = sigma * L / E * ((1 - NU ** 2) if mode == "plane_strain" else 1.0)
    tip = u[2 * _nodes_on(m, 0, L)]
    assert np.abs(tip / exact - 1).max() <= 0.02
    assert np.abs(tip / exact - 1).max() < 1e-8  # a linear field is exact for Q4
    s = fem2d.element_stress(m, mode, u)
    assert np.allclose(s[:, 0], sigma, rtol=1e-8)
    assert np.allclose(s[:, 1], 0.0, atol=1e-8 * sigma)
    expect_zz = NU * sigma if mode == "plane_strain" else 0.0
    assert np.allclose(s[:, 2], expect_zz, rtol=1e-8, atol=1e-8 * sigma)


def test_force_total_equals_traction_times_area():
    m = fem2d.build_mesh(_block(10, 6, 1e-3, thickness=0.02))
    f = fem2d.traction_forces(m, "plane_strain", _edges_on(m, 1, 6e-3), (0.0, 2e6))
    assert math.isclose(f[1::2].sum(), 2e6 * 10e-3 * 0.02, rel_tol=1e-12)
    ma = fem2d.build_mesh(_block(10, 6, 1e-3, origin=(0.0, 0.0)))
    fa = fem2d.traction_forces(ma, "axisymmetric", _edges_on(ma, 1, 6e-3), (0.0, 2e6))
    assert math.isclose(fa[1::2].sum(), 2e6 * math.pi * (10e-3) ** 2, rel_tol=1e-12)


def test_axisymmetric_cylinder_in_tension():
    """Solid cylinder, axial stress sigma: e_zz = sigma/E, u_r = -nu sigma r / E."""
    h, nr, nz, sigma = 1e-3, 10, 30, 3e6
    m = fem2d.build_mesh(_block(nr, nz, h))
    Lz, R = nz * h, nr * h
    f = fem2d.traction_forces(m, "axisymmetric", _edges_on(m, 1, Lz), (0.0, sigma))
    bottom = _nodes_on(m, 1, 0.0)
    u = fem2d.solve(m, "axisymmetric", 2 * bottom + 1, 0.0, f)
    top = _nodes_on(m, 1, Lz)
    assert np.allclose(u[2 * top + 1], sigma * Lz / E, rtol=1e-8)
    assert np.allclose(u[0::2], -NU * sigma * m.nodes[:, 0] / E, rtol=1e-8, atol=1e-12 * R)
    s = fem2d.element_stress(m, "axisymmetric", u)
    assert np.allclose(s[:, 1], sigma, rtol=1e-8)
    assert np.allclose(s[:, [0, 2, 3]], 0.0, atol=1e-8 * sigma)


def test_axisymmetric_lame_thick_cylinder():
    """Thick cylinder a..b, internal pressure p, plane strain ends (u_z = 0):
    u_r = p a^2 (1+nu) / (E (b^2-a^2)) * ((1-2nu) r + b^2/r)
    (Timoshenko & Goodier 1970, Theory of Elasticity, sec. 28)."""
    h, a, b, p = 2.5e-4, 5e-3, 15e-3, 10e6
    nr, nz = int(round((b - a) / h)), 4
    m = fem2d.build_mesh(_block(nr, nz, h, origin=(a, 0.0)))
    f = fem2d.traction_forces(m, "axisymmetric", _edges_on(m, 0, a), (p, 0.0))
    u = fem2d.solve(m, "axisymmetric", 2 * np.arange(len(m.nodes)) + 1, 0.0, f)
    r = m.nodes[:, 0]
    exact = p * a * a * (1 + NU) / (E * (b * b - a * a)) * ((1 - 2 * NU) * r + b * b / r)
    assert np.abs(u[0::2] / exact - 1).max() < 0.005
    s = fem2d.element_stress(m, "axisymmetric", u)
    rc = m.nodes[m.elements, 0].mean(axis=1)
    hoop = p * a * a / (b * b - a * a) * (1 + b * b / rc ** 2)
    assert np.abs(s[:, 2] / hoop - 1).max() < 0.02


def _kirsch_scf(n_r, n_t, mode="plane_strain"):
    """Quarter of an infinite plate (outer radius 25a) with a circular hole of
    radius a, remote uniaxial stress sigma along y on a body-fitted polar mesh.
    The outer radius only approximates 'infinite': the Kirsch r^-2 terms are
    (a/R)^2 = 0.16 % there."""
    a, R, sigma = 1e-3, 25e-3, 1e6
    r = a * (R / a) ** (np.arange(n_r + 1) / n_r)
    th = np.linspace(0.0, math.pi / 2, n_t + 1)
    RR, TT = np.meshgrid(r, th, indexing="ij")
    nodes = np.stack([(RR * np.cos(TT)).ravel(), (RR * np.sin(TT)).ravel()], axis=1)
    I, J = np.meshgrid(np.arange(n_r), np.arange(n_t), indexing="ij")
    n0 = (I * (n_t + 1) + J).ravel()
    m = fem2d.quad_mesh(nodes, np.stack([n0, n0 + n_t + 1, n0 + n_t + 2, n0 + 1], axis=1),
                        E, NU, 1e-3)
    edges, normal = fem2d.boundary_edges(m)
    outer = np.all(np.isclose(np.hypot(*m.nodes[edges].transpose(2, 0, 1)), R), axis=1)
    traction = np.stack([np.zeros(outer.sum()), sigma * normal[outer][:, 1]], axis=1)
    f = fem2d.traction_forces(m, mode, edges[outer], traction)
    u = fem2d.solve(m, mode, np.r_[2 * _nodes_on(m, 0, 0.0), 2 * _nodes_on(m, 1, 0.0) + 1], 0.0, f)
    s = fem2d.element_stress(m, mode, u)
    first_column = J.ravel() == 0  # elements next to theta = 0, where s_yy peaks
    rc = np.sqrt(r[:-1] * r[1:])
    coef = np.polyfit(rc[:3] - a, s[first_column, 1][:3], 2)  # extrapolate to the hole edge
    return coef[-1] / sigma, rc / a, s[first_column, 1] / sigma


@pytest.mark.parametrize("mode", ["plane_strain", "plane_stress"])
def test_kirsch_stress_concentration(mode):
    """Kirsch (1898): sigma_max = 3 sigma at the hole edge, independent of nu."""
    scf, _, _ = _kirsch_scf(60, 48, mode)
    assert abs(scf / 3.0 - 1) <= 0.05


def test_kirsch_stress_profile_away_from_hole():
    """Independent of the extrapolation: s_yy(r, theta~0) along the ligament
    against Kirsch, 1 + a^2/(2 r^2) + 3 a^4/(2 r^4), for r in [1.1a, 3a]."""
    _, rho, syy = _kirsch_scf(60, 48)
    sel = (rho >= 1.1) & (rho <= 3.0)
    assert sel.sum() >= 10
    exact = 1 + 0.5 / rho[sel] ** 2 + 1.5 / rho[sel] ** 4
    assert np.abs(syy[sel] / exact - 1).max() < 0.03


def test_kirsch_converges_monotonically():
    errs = [abs(_kirsch_scf(n, int(0.8 * n))[0] - 3.0) for n in (20, 40, 80)]
    assert errs[0] > errs[1] > errs[2]


def test_patch_test_on_distorted_quads():
    """Affine displacement on an irregular convex quad mesh must give exactly
    the constant stress (patch test; Zienkiewicz & Taylor 2000, ch. 10)."""
    g = np.linspace(0.0, 1e-2, 4)
    X, Y = np.meshgrid(g, g, indexing="ij")
    rng = np.random.default_rng(0)
    inner = (X > 0) & (X < 1e-2) & (Y > 0) & (Y < 1e-2)
    X = X + inner * rng.uniform(-8e-4, 8e-4, X.shape)
    Y = Y + inner * rng.uniform(-8e-4, 8e-4, Y.shape)
    nodes = np.stack([X.ravel(), Y.ravel()], axis=1)
    I, J = np.meshgrid(np.arange(3), np.arange(3), indexing="ij")
    n0 = (I * 4 + J).ravel()
    m = fem2d.quad_mesh(nodes, np.stack([n0, n0 + 4, n0 + 5, n0 + 1], axis=1), E, NU, 0.01)
    exx, eyy, gxy = 1e-4, -3e-5, 5e-5
    boundary = np.nonzero(~inner.ravel())[0]
    x, y = m.nodes[:, 0], m.nodes[:, 1]
    ux, uy = exx * x + 0.5 * gxy * y, eyy * y + 0.5 * gxy * x
    u = fem2d.solve(m, "plane_strain", np.r_[2 * boundary, 2 * boundary + 1],
                    np.r_[ux[boundary], uy[boundary]])
    assert np.allclose(u[0::2], ux, rtol=0, atol=1e-12) and np.allclose(u[1::2], uy, rtol=0, atol=1e-12)
    expect = fem2d.constitutive([E], [NU], "plane_strain")[0] @ np.array([exx, eyy, gxy])
    s = fem2d.element_stress(m, "plane_strain", u)
    assert np.allclose(s[:, [0, 1, 3]], expect, rtol=1e-8)


def test_two_phase_bar_in_series():
    """Two materials in series along x under plane stress tension: each part
    strains sigma/E_k (uses per-element E from the stone phases)."""
    granite = load_material("granite")
    ph = phases_of(granite)[:2]
    h, nx, ny, sigma = 1e-3, 20, 4, 1e6
    cells = np.ones((ny, nx), dtype=np.int16)
    cells[:, nx // 2:] = 2
    s = Stone(cells=cells, phases=ph, cell_size_m=h, material_name=granite.name,
              thickness_m=0.01, grain=np.zeros((ny, nx), dtype=np.int32))
    m = fem2d.build_mesh(s)
    f = fem2d.traction_forces(m, "plane_stress", _edges_on(m, 0, nx * h), (sigma, 0.0))
    corner = np.nonzero(np.isclose(m.nodes, 0.0).all(axis=1))[0]
    u = fem2d.solve(m, "plane_stress", np.r_[2 * _nodes_on(m, 0, 0.0), 2 * corner + 1], 0.0, f)
    half = nx // 2 * h
    E1, E2 = ph[0].youngs_modulus_pa, ph[1].youngs_modulus_pa
    assert E1 != E2
    assert np.allclose(u[2 * _nodes_on(m, 0, half)], sigma * half / E1, rtol=1e-8)
    assert np.allclose(u[2 * _nodes_on(m, 0, nx * h)], sigma * half / E1 + sigma * half / E2, rtol=1e-8)


def test_axisymmetric_rejects_negative_radius_and_nonzero_axis_value():
    m = fem2d.build_mesh(_block(4, 4, 1e-3, origin=(-1e-3, 0.0)))
    with pytest.raises(ValueError):
        fem2d.assemble(m, "axisymmetric")
    m0 = fem2d.build_mesh(_block(4, 4, 1e-3))
    axis = _nodes_on(m0, 0, 0.0)
    with pytest.raises(ValueError):
        fem2d.solve(m0, "axisymmetric", np.r_[2 * axis, 2 * axis + 1], 1e-6)
