import json
import math
from pathlib import Path

import numpy as np
import pytest

from lithics.materials import MATERIAL_NAMES, load_material
from lithics.stone import Stone, make_core, phases_of

FIELDS = (
    "youngs_modulus_pa",
    "poisson_ratio",
    "density_kg_m3",
    "fracture_toughness_pa_sqrt_m",
    "tensile_strength_pa",
    "microstructure_scale_m",
)
SPEC_FILE = Path(__file__).resolve().parents[2] / "physics-loop" / "spec" / "materials.json"
SPEC = json.loads(SPEC_FILE.read_text(encoding="utf-8"))["materials"]


def test_material_names_match_spec():
    assert isinstance(MATERIAL_NAMES, tuple)
    assert sorted(MATERIAL_NAMES) == sorted(SPEC)


@pytest.mark.parametrize("name", sorted(SPEC))
def test_material_values_equal_spec(name):
    m = load_material(name)
    for f in FIELDS:
        assert getattr(m, f) == float(SPEC[name][f]["value"]), f


def test_fracture_energy_glass():
    m = load_material("glass_soda_lime")
    e_prime = 71e9 / (1 - 0.22 ** 2)
    assert m.fracture_energy_j_m2 == pytest.approx(0.75e6 ** 2 / e_prime, rel=1e-12)
    # soda-lime G_c is a few J/m^2
    assert 3.0 < m.fracture_energy_j_m2 < 10.0


def test_granite_mosaic_from_spec():
    g = load_material("granite")
    raw = SPEC["granite"]["mosaic"]
    assert g.mosaic.grain_size_m == raw["grain_size_m"]
    assert {m.name for m in g.mosaic.minerals} == set(raw["minerals"])
    for m in g.mosaic.minerals:
        r = raw["minerals"][m.name]
        for f in ("fraction", "youngs_modulus_pa", "poisson_ratio", "tensile_strength_pa"):
            assert getattr(m, f) == r[f], (m.name, f)
    phases = phases_of(g)
    assert len(phases) == 3
    for p, m in zip(phases, g.mosaic.minerals):
        assert p.youngs_modulus_pa == m.youngs_modulus_pa
        assert p.tensile_strength_pa == m.tensile_strength_pa
        # no per-mineral density/toughness in the spec: bulk values (assumption)
        assert p.density_kg_m3 == g.density_kg_m3
        assert p.fracture_toughness_pa_sqrt_m == g.fracture_toughness_pa_sqrt_m
    assert load_material("obsidian").mosaic is None


def test_unknown_material():
    with pytest.raises(KeyError):
        load_material("unobtainium")


def test_core_area_matches_polygon():
    m = load_material("glass_soda_lime")
    H, P, epa, h = 0.04, 0.05, 70.0, 2.5e-4
    s = make_core(m, height_m=H, platform_m=P, epa_deg=epa, cell_size_m=h, depth_m=0.03)
    area = P * H - 0.5 * H * H / math.tan(math.radians(epa))
    assert s.dim == 2
    assert s.n_cells * h * h == pytest.approx(area, rel=0.02)
    assert s.mass_kg == pytest.approx(area * 0.03 * 2500, rel=0.02)


def test_core_face_angle_follows_epa():
    m = load_material("glass_soda_lime")
    h = 2.5e-4
    for epa in (60.0, 75.0, 90.0, 110.0):
        s = make_core(m, height_m=0.03, platform_m=0.05, epa_deg=epa, cell_size_m=h)
        # rightmost filled cell per row traces the exterior face
        rows = np.arange(s.cells.shape[0])
        right = np.array([np.flatnonzero(s.cells[j]).max() for j in rows])
        slope = np.polyfit((rows + 0.5) * h, (right + 0.5) * h, 1)[0]  # dx/dy
        got = math.degrees(math.atan2(1.0, slope))
        assert got == pytest.approx(epa, abs=1.0)


def test_core_3d_extrusion_mass():
    m = load_material("obsidian")
    s2 = make_core(m, cell_size_m=2e-3, depth_m=0.02)
    s3 = make_core(m, cell_size_m=2e-3, depth_m=0.02, dim=3)
    assert s3.dim == 3 and s3.cells.shape[0] == 10
    assert s3.mass_kg == pytest.approx(s2.mass_kg, rel=1e-12)
    assert len(s3.meta["platform_normal"]) == 3
    with pytest.raises(ValueError):
        make_core(m, cell_size_m=2e-3, depth_m=0.021, dim=3)


def test_mosaic_needs_seed_and_is_deterministic():
    g = load_material("granite")
    with pytest.raises(ValueError):
        make_core(g, cell_size_m=5e-4)
    a = make_core(g, cell_size_m=5e-4, seed=3)
    b = make_core(g, cell_size_m=5e-4, seed=3)
    c = make_core(g, cell_size_m=5e-4, seed=4)
    assert np.array_equal(a.cells, b.cells) and np.array_equal(a.grain, b.grain)
    assert not np.array_equal(a.cells, c.cells)
    # cell volume fractions near the spec fractions (many grains)
    filled = a.cells[a.cells > 0]
    frac = np.bincount(filled, minlength=4)[1:] / filled.size
    want = [mm.fraction for mm in g.mosaic.minerals]
    assert np.allclose(frac, want, atol=0.08)
    # grains are about grain_size wide: number of grains ~ area / d^2
    n_grains = np.unique(a.grain[a.grain >= 0]).size
    area = a.n_cells * 5e-4 ** 2
    assert 0.5 < n_grains / (area / g.mosaic.grain_size_m ** 2) < 1.5


def test_extract_conserves_cells_and_position():
    m = load_material("glass_soda_lime")
    s = make_core(m, cell_size_m=1e-3)
    mask = np.zeros_like(s.cells, dtype=bool)
    mask[30:, 20:] = True
    a = s.extract(mask)
    b = s.extract(~mask)
    assert a.n_cells + b.n_cells == s.n_cells
    assert a.mass_kg + b.mass_kg == pytest.approx(s.mass_kg, rel=1e-12)

    def rows_sorted(p):
        q = np.round(p / 0.5e-3).astype(np.int64)  # half-cell units
        return q[np.lexsort(q.T[::-1])]

    got = rows_sorted(np.concatenate([a.cell_centers_m(), b.cell_centers_m()]))
    assert np.array_equal(got, rows_sorted(s.cell_centers_m()))


def test_stone_rejects_bad_dim():
    m = load_material("glass_soda_lime")
    with pytest.raises(ValueError):
        Stone(cells=np.ones(4, dtype=int), phases=phases_of(m), cell_size_m=1e-3, material_name=m.name)
    for bad in (-1, 2):
        with pytest.raises(ValueError):
            Stone(cells=np.full((3, 3), bad), phases=phases_of(m), cell_size_m=1e-3, material_name=m.name)
    with pytest.raises(ValueError):
        Stone(cells=np.ones((3, 3), dtype=int), phases=phases_of(m), cell_size_m=0.0, material_name=m.name)
    with pytest.raises(ValueError):
        make_core(m, height_m=-0.01)
    with pytest.raises(ValueError):  # base width would be negative
        make_core(m, height_m=0.05, platform_m=0.01, epa_deg=45.0)
