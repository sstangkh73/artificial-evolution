"""Step 5: analyst-side measurements (lithics.measure) on shapes with known answers."""
import math

import numpy as np
import pytest

from lithics import impact
from lithics import measure as ms
from lithics.materials import load_material
from lithics.stone import Stone, make_core, phases_of

GLASS = load_material("glass_soda_lime")


def _stone(mask, h):
    return Stone(cells=mask.astype(int), phases=phases_of(GLASS), cell_size_m=h,
                 material_name=GLASS.name, thickness_m=1e-3)


def _raster(inside, h, n):
    """Cells of an n x n grid (cell size h, origin 0) whose centre satisfies inside(x, y)."""
    c = (np.arange(n) + 0.5) * h
    X, Y = np.meshgrid(c, c)
    return _stone(inside(X, Y), h)


# ---------------------------------------------------------------- Dibble set

@pytest.mark.parametrize("aob", [-20.0, 0.0, 15.0, 50.0])
def test_angle_of_blow_round_trip_and_sign(aob):
    v = ms.blow_direction(aob)
    assert np.linalg.norm(v) == pytest.approx(1.0)
    assert ms.angle_of_blow_deg(v) == pytest.approx(aob, abs=1e-12)
    # positive AOB: the hammer leans toward the exterior edge (+x); always moves into the platform
    assert v[1] < 0
    assert np.sign(v[0]) == np.sign(aob)


def test_positive_aob_leans_toward_the_exterior_edge_of_a_core():
    # convention (02 sec. 5.1): positive = trajectory leans outward, toward the exterior face
    core = make_core(GLASS, height_m=4e-3, platform_m=6e-3, epa_deg=75.0, cell_size_m=0.1e-3)
    edge = np.array(core.meta["edge_m"])
    contact = edge - (1.5e-3, 0.0)
    for aob in (10.0, 30.0):
        v = ms.blow_direction(aob, platform_normal=core.meta["platform_normal"])
        assert v @ (edge - contact) > 0  # moves toward the edge
        assert v @ np.array(core.meta["platform_normal"]) < 0  # and into the platform
        assert ms.blow_direction(-aob) @ (edge - contact) < 0  # negative: toward the core interior


def test_angle_of_blow_rejects_bad_vectors():
    with pytest.raises(ValueError):
        ms.angle_of_blow_deg((0.0, 0.0))
    with pytest.raises(ValueError):
        ms.angle_of_blow_deg((0.0, 1.0))  # leaving the platform
    with pytest.raises(ValueError):
        ms.angle_of_blow_deg((0.0, -1.0), outward=(1.0, 1.0))


def test_angle_of_blow_of_perpendicular_blow_is_zero():
    assert ms.angle_of_blow_deg((0.0, -2.0)) == pytest.approx(0.0, abs=1e-12)
    assert ms.angle_of_blow_deg((1.0, -1.0)) == pytest.approx(45.0)


@pytest.mark.parametrize("epa", [60.0, 75.0, 80.0, 95.0, 110.0])
def test_exterior_platform_angle_measured_from_cells(epa):
    h = 0.05e-3
    core = make_core(GLASS, height_m=6e-3, platform_m=8e-3, epa_deg=epa, cell_size_m=h)
    assert ms.exterior_platform_angle_deg(core, window_m=3e-3) == pytest.approx(epa, abs=0.5)


def test_platform_depth_planned_and_measured_on_a_piece():
    h = 0.1e-3
    core = make_core(GLASS, height_m=4e-3, platform_m=6e-3, epa_deg=90.0, cell_size_m=h)
    ex, ey = core.meta["edge_m"]
    assert ms.platform_depth_m(core, (ex - 1.3e-3, ey)) == pytest.approx(1.3e-3)
    # a piece holding the top-right block, 15 cells wide, 8 rows deep
    mask = np.zeros_like(core.cells, dtype=bool)
    mask[-8:, -15:] = True
    piece = core.extract(mask)
    assert ms.flake_platform_depth_m(piece, core) == pytest.approx(15 * h)
    # a piece not reaching the platform carries no platform
    low = np.zeros_like(mask)
    low[:5, -15:] = True
    assert ms.flake_platform_depth_m(core.extract(low), core) == 0.0
    # platform run broken by a gap: only the run from the edge counts
    gap = np.zeros_like(mask)
    gap[-8:, -15:] = True
    gap[-1, -10] = False
    assert ms.flake_platform_depth_m(core.extract(gap), core) == pytest.approx(9 * h)
    # platform cells that do not reach the edge: no platform depth
    inner = np.zeros_like(mask)
    inner[-8:, -15:-3] = True
    assert ms.flake_platform_depth_m(core.extract(inner), core) == 0.0


def test_section_area_counts_and_flakes():
    h = 0.2e-3
    st = _stone(np.ones((10, 7), dtype=bool), h)
    assert ms.section_area_m2(st) == pytest.approx(70 * h * h)
    small = st.extract(np.pad(np.ones((2, 2), bool), ((0, 8), (0, 5))))
    assert ms.flakes([st, small]) == [small]
    assert ms.count_pieces([st, small]) == 2
    assert ms.count_pieces([st, small], min_mass_kg=small.mass_kg) == 1


# --------------------------------------------------------------- cone angle

def _cone_field(half_deg, r0, depth, r_nodes, z_nodes, band):
    """Nodal damage of an axisymmetric cone crack from the ring r0 at the
    surface (z = 0, depth downward = -z): d = 1 within ``band`` of the line."""
    R, Z = np.meshgrid(r_nodes, z_nodes)
    t = -Z
    centre = r0 + t * math.tan(math.radians(half_deg))
    d = np.where((np.abs(R - centre) <= band) & (t <= depth), 1.0, 0.0)
    return np.column_stack([R.ravel(), Z.ravel()]), d.ravel()


@pytest.mark.parametrize("half", [55.0, 61.0, 75.0])
def test_cone_angle_of_a_known_cone_on_a_graded_mesh(half):
    # nodes graded in r and in depth (fine near the ring and the surface) must not bias the fit
    r = np.concatenate([np.linspace(0, 1e-3, 201), 1e-3 + np.cumsum(np.full(80, 1e-5) * 1.04 ** np.arange(80))])
    z = -np.concatenate([np.linspace(0, 0.3e-3, 61), 0.3e-3 + np.cumsum(np.full(60, 5e-6) * 1.05 ** np.arange(60))])
    pts, d = _cone_field(half, 0.4e-3, 1.5e-3, r, z, band=12e-6)
    fit = ms.cone_angle(pts, d, apex_m=(0.0, 0.0), axis=(0.0, -1.0))
    assert fit.included_angle_deg == pytest.approx(2 * half, abs=1.0)
    assert fit.n_bins >= 5  # coarse deep rows leave some bins empty


def test_cone_angle_skips_the_steep_ring_start():
    # 0.15 mm vertical ring crack, then a 62 deg cone: the fit (depth >= 25 % of the deepest) sees the cone
    r = np.linspace(0, 4e-3, 801)
    z = -np.linspace(0, 2e-3, 401)
    R, Z = np.meshgrid(r, z)
    t = -Z
    centre = np.where(t < 0.15e-3, 0.4e-3, 0.4e-3 + (t - 0.15e-3) * math.tan(math.radians(62)))
    d = (np.abs(R - centre) <= 12e-6) & (t <= 1.5e-3)
    fit = ms.cone_angle(np.column_stack([R.ravel(), Z.ravel()]), d.ravel().astype(float),
                        apex_m=(0.0, 0.0), axis=(0.0, -1.0))
    assert fit.included_angle_deg == pytest.approx(124.0, abs=1.0)


def test_cone_angle_in_a_2d_section_on_either_side():
    # 2D: crack from the contact at (0, 0) running down at 30 deg from the blow axis to -x
    x = np.linspace(-2e-3, 2e-3, 401)
    y = -np.linspace(0, 2e-3, 201)
    X, Y = np.meshgrid(x, y)
    centre = -0.1e-3 - (-Y) * math.tan(math.radians(30))
    d = ((np.abs(X - centre) <= 12e-6) & (Y > -1.5e-3)).astype(float).ravel()
    pts = np.column_stack([X.ravel(), Y.ravel()])
    # axis (0, -1): perp = (1, 0), so the -x side is side = -1
    fit = ms.cone_angle(pts, d, (0.0, 0.0), (0.0, -1.0), side=-1.0)
    assert fit.half_angle_deg == pytest.approx(30.0, abs=0.5)
    with pytest.raises(ValueError):
        ms.cone_angle(pts, d, (0.0, 0.0), (0.0, -1.0), side=1.0)


def test_cone_angle_needs_a_crack():
    with pytest.raises(ValueError):
        ms.cone_angle(np.zeros((3, 2)), np.zeros(3), (0.0, 0.0), (0.0, -1.0))


# ------------------------------------------------------ edge angle, tip radius

@pytest.mark.parametrize("angle", [30.0, 45.0, 60.0, 75.0])
def test_edge_angle_of_a_rasterised_wedge(angle):
    # circular sector, radius 2 mm, apex (1 mm, 2.5 mm), opening to +x: the
    # other two corners are 90 deg, so the apex is the sharpest
    h, n = 0.02e-3, 250
    tx, ty = 1e-3, 2.5e-3
    tan_half = math.tan(math.radians(angle / 2))
    st = _raster(lambda X, Y: (X >= tx) & ((X - tx) ** 2 + (Y - ty) ** 2 <= 4e-6)
                 & (np.abs(Y - ty) <= (X - tx) * tan_half), h, n)
    fit = ms.sharpest_edge(st, face_window_m=(10 * h, 40 * h), tip_window_m=4 * h)
    assert fit.angle_deg == pytest.approx(angle, abs=1.5)
    assert np.linalg.norm(fit.tip_m - (tx, ty)) < 3 * h
    assert fit.grid_limited  # an ideal tip is below what the grid shows


@pytest.mark.parametrize("bisector", [17.0, 38.0])
def test_edge_angle_of_a_wedge_not_aligned_with_the_grid(bisector):
    h, n, angle = 0.02e-3, 250, 40.0
    tx, ty = 1.2e-3, 1.3e-3
    b = math.radians(bisector)
    tan_half = math.tan(math.radians(angle / 2))

    def inside(X, Y):
        along = (X - tx) * math.cos(b) + (Y - ty) * math.sin(b)
        across = -(X - tx) * math.sin(b) + (Y - ty) * math.cos(b)
        return (along >= 0) & (along <= 2.5e-3) & (np.abs(across) <= along * tan_half)

    fit = ms.sharpest_edge(_raster(inside, h, n), face_window_m=(10 * h, 40 * h), tip_window_m=4 * h)
    assert fit.angle_deg == pytest.approx(angle, abs=1.5)
    assert np.linalg.norm(fit.tip_m - (tx, ty)) < 3 * h
    assert fit.grid_limited


def test_tip_radius_of_a_rounded_edge_is_resolved():
    # 40 deg wedge whose tip is a circle of radius 15 h (tangent to both faces)
    h, n, rho = 0.02e-3, 250, 15 * 0.02e-3
    half = math.radians(20.0)
    cx, cy = 1.5e-3, 2.5e-3  # circle centre
    tx = cx - rho / math.sin(half)  # sharp apex the faces would meet at
    st = _raster(lambda X, Y: ((X >= cx) & (X <= 4.5e-3) & (np.abs(Y - cy) <= (X - tx) * math.tan(half)))
                 | ((X - cx) ** 2 + (Y - cy) ** 2 <= rho ** 2), h, n)
    fit = ms.sharpest_edge(st, face_window_m=(30 * h, 80 * h), tip_window_m=0.6 * rho)
    assert fit.angle_deg == pytest.approx(40.0, abs=1.5)
    assert fit.tip_radius_m == pytest.approx(rho, rel=0.15)
    assert fit.tip_fit_rms_m < 0.5 * h
    assert fit.grid_radius_m < rho / 2
    assert not fit.grid_limited


def test_sharpest_edge_of_a_core_is_the_platform_edge():
    h = 0.05e-3
    core = make_core(GLASS, height_m=4e-3, platform_m=6e-3, epa_deg=70.0, cell_size_m=h)
    fit = ms.sharpest_edge(core, face_window_m=(10 * h, 30 * h), tip_window_m=3 * h)
    assert np.linalg.norm(fit.tip_m - np.array(core.meta["edge_m"])) < 3 * h
    assert fit.angle_deg == pytest.approx(70.0, abs=1.5)


def test_outline_is_counter_clockwise_and_closed_around_the_stone():
    h = 0.1e-3
    st = _stone(np.ones((6, 9), dtype=bool), h)
    line = ms.outline(st)
    x, y = line[:, 0], line[:, 1]
    area = 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)
    # marching squares through edge midpoints at cell centres +- h/2: the 9 x 6 cell box
    # with its four corners cut by h^2/8 each
    assert area == pytest.approx(54 * h * h - 4 * h * h / 8, rel=1e-9)


def test_outline_refuses_several_pieces():
    mask = np.zeros((6, 9), dtype=bool)
    mask[:2, :2] = True
    mask[4:, 5:] = True
    with pytest.raises(ValueError):
        ms.outline(_stone(mask, 0.1e-3))


# ------------------------------------------------------- on a real strike

def test_measures_on_pieces_of_a_real_strike():
    h = 60e-6  # the split case of test_lithics_strike
    core = make_core(GLASS, height_m=33 * h, platform_m=42 * h, epa_deg=80.0, cell_size_m=h, depth_m=2e-3)
    ex, ey = core.meta["edge_m"]
    r = impact.strike(core, (ex - 0.5e-3, ey), ms.blow_direction(0.0), 0.05, 10.0, 5e-3, impact.hand_held())
    assert ms.count_pieces(r.pieces) >= 2
    total = sum(ms.section_area_m2(p) for p in r.pieces)
    assert total == pytest.approx(ms.section_area_m2(core), rel=1e-12)
    assert sum(p.mass_kg for p in r.pieces) == pytest.approx(core.mass_kg, rel=1e-12)
    for f in ms.flakes(r.pieces):
        assert 0.0 <= ms.flake_platform_depth_m(f, core) <= 42 * h + 1e-12
    assert ms.exterior_platform_angle_deg(core, window_m=1e-3) == pytest.approx(80.0, abs=2.0)
    for p in r.pieces:  # edge measures run on real fracture outlines and give finite values
        e = ms.sharpest_edge(p, face_window_m=(3 * h, 8 * h), tip_window_m=2 * h)
        assert 0.0 < e.angle_deg < 180.0
        assert e.tip_radius_m > 0 and math.isfinite(e.grid_radius_m)
    # the crack of the blow: nodal damage of the section, measured from the contact along the blow
    blow = r.blow
    fit = ms.cone_angle(blow.mesh.nodes, blow.indent.d, (ex - 0.5e-3, ey), (0.0, -1.0),
                        side=1.0 if np.any((blow.indent.d >= 0.95) & (blow.mesh.nodes[:, 0] > ex - 0.5e-3)) else -1.0)
    assert math.isfinite(fit.included_angle_deg) and fit.n_bins >= 2
    assert ms.platform_depth_m(core, (ex - 0.5e-3, ey)) == pytest.approx(0.5e-3)
