"""A stone is a 2D or 3D grid of material cells.

``Stone.cells`` holds 0 for empty space and ``k`` for ``phases[k-1]``. A
homogeneous material has one phase. A mineral mosaic (granite) has one phase
per mineral and a ``grain`` array with the grain id of every cell, so later
modules can treat grain boundaries separately.

Coordinates: index order is (y, x) in 2D and (z, y, x) in 3D; cell (0, 0)
has its lower corner at ``origin_m``. The y axis points up, so the platform of
a core made by ``make_core`` is the top face.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
import math

import numpy as np

from .materials import Material


@dataclass(frozen=True)
class Phase:
    """Constants of one constituent of a stone (the whole material or one mineral)."""

    name: str
    youngs_modulus_pa: float
    poisson_ratio: float
    density_kg_m3: float
    fracture_toughness_pa_sqrt_m: float
    tensile_strength_pa: float


def phases_of(material: Material) -> tuple[Phase, ...]:
    """Phases of a material.

    For a mosaic, each mineral keeps its own E, nu and tensile strength
    (spec ``mosaic.minerals``). The spec gives no per-mineral density or
    toughness, so minerals take the bulk values (ASSUMPTION, recorded in
    docs/physics_world/02_physics_spec.md).
    """
    if material.mosaic is None:
        return (
            Phase(
                name=material.name,
                youngs_modulus_pa=material.youngs_modulus_pa,
                poisson_ratio=material.poisson_ratio,
                density_kg_m3=material.density_kg_m3,
                fracture_toughness_pa_sqrt_m=material.fracture_toughness_pa_sqrt_m,
                tensile_strength_pa=material.tensile_strength_pa,
            ),
        )
    return tuple(
        Phase(
            name=f"{material.name}:{m.name}",
            youngs_modulus_pa=m.youngs_modulus_pa,
            poisson_ratio=m.poisson_ratio,
            density_kg_m3=material.density_kg_m3,
            fracture_toughness_pa_sqrt_m=material.fracture_toughness_pa_sqrt_m,
            tensile_strength_pa=m.tensile_strength_pa,
        )
        for m in material.mosaic.minerals
    )


@dataclass
class Stone:
    cells: np.ndarray
    phases: tuple[Phase, ...]
    cell_size_m: float
    material_name: str
    thickness_m: float = 0.03  # out-of-plane depth, 2D only
    grain: np.ndarray | None = None  # grain id per cell (-1 = empty), mosaics only
    origin_m: np.ndarray = field(default_factory=lambda: np.zeros(3))
    meta: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        raw = np.asarray(self.cells)
        if not np.issubdtype(raw.dtype, np.integer) and not np.issubdtype(raw.dtype, np.bool_):
            raise ValueError("cells must be an integer array")
        if raw.ndim not in (2, 3):
            raise ValueError("Stone supports dim=2 or dim=3 only")
        if raw.size and (int(raw.min()) < 0 or int(raw.max()) > len(self.phases)):
            raise ValueError("cell phase index must be in [0, len(phases)]")
        self.cells = raw.astype(np.int16)
        if not (math.isfinite(self.cell_size_m) and self.cell_size_m > 0):
            raise ValueError("cell_size_m must be positive")
        if not (math.isfinite(self.thickness_m) and self.thickness_m > 0):
            raise ValueError("thickness_m must be positive")
        if self.grain is not None and self.grain.shape != self.cells.shape:
            raise ValueError("grain array must match cells shape")
        o = np.zeros(3)
        given = np.asarray(self.origin_m, dtype=float).ravel()
        o[: given.size] = given
        self.origin_m = o

    @property
    def dim(self) -> int:
        return self.cells.ndim

    @property
    def n_cells(self) -> int:
        return int(np.count_nonzero(self.cells))

    @property
    def cell_volume_m3(self) -> float:
        h = self.cell_size_m
        return h ** 3 if self.dim == 3 else h * h * self.thickness_m

    @property
    def volume_m3(self) -> float:
        return self.n_cells * self.cell_volume_m3

    @property
    def mass_kg(self) -> float:
        rho = np.array([0.0] + [p.density_kg_m3 for p in self.phases])
        return float(rho[self.cells].sum() * self.cell_volume_m3)

    def cell_centers_m(self) -> np.ndarray:
        """Centres of filled cells, shape (n, dim), in (x, y[, z]) order."""
        idx = np.argwhere(self.cells > 0)[:, ::-1].astype(float)
        return (idx + 0.5) * self.cell_size_m + self.origin_m[: self.dim]

    def extract(self, mask: np.ndarray) -> "Stone":
        """New stone holding exactly the filled cells where ``mask`` is True,
        cropped to their bounding box (origin moved so positions are kept)."""
        mask = np.asarray(mask, dtype=bool) & (self.cells > 0)
        if not mask.any():
            raise ValueError("mask selects no filled cells")
        lo = np.argwhere(mask).min(axis=0)
        hi = np.argwhere(mask).max(axis=0) + 1
        sl = tuple(slice(a, b) for a, b in zip(lo, hi))
        cells = np.where(mask, self.cells, 0)[sl]
        grain = None if self.grain is None else np.where(mask, self.grain, -1)[sl]
        shift = np.zeros(3)
        shift[: self.dim] = lo[::-1] * self.cell_size_m
        return replace(
            self,
            cells=cells.copy(),
            grain=None if grain is None else grain.copy(),
            origin_m=self.origin_m + shift,
            meta={},
        )


def _core_mask_2d(height_m: float, platform_m: float, epa_deg: float, h: float):
    """Cells whose centre lies in the core section.

    The platform is the top face (y = height) from x = 0 to the edge at
    x = platform_m. The exterior face leaves the edge downward and makes the
    angle ``epa_deg`` with the platform, measured through the stone:
    x_face(y) = platform_m - (height - y) * cot(EPA).
    """
    cot = 1.0 / math.tan(math.radians(epa_deg))
    bottom_width = platform_m - height_m * cot
    if bottom_width <= 0.0:
        raise ValueError("core too tall for this EPA and platform length (base width <= 0)")
    width = max(platform_m, bottom_width)
    nx = int(math.ceil(width / h))
    ny = int(math.ceil(height_m / h))
    x = (np.arange(nx) + 0.5) * h
    y = (np.arange(ny) + 0.5) * h
    X, Y = np.meshgrid(x, y)
    inside = (Y <= height_m) & (X <= platform_m - (height_m - Y) * cot)
    if not inside.any(axis=1).all():
        raise ValueError("cell_size_m too coarse: some rows of the core contain no cell centre")
    return inside


def _mosaic_phase_ids(material: Material, shape: tuple[int, ...], h: float, seed: int):
    """Voronoi mineral mosaic: grain seeds uniform in the bounding box, one
    seed per grain_size^dim of box volume, minerals drawn by volume fraction."""
    from scipy.spatial import cKDTree

    mosaic = material.mosaic
    rng = np.random.default_rng(seed)
    dim = len(shape)
    extent = np.array(shape[::-1], dtype=float) * h  # (x, y[, z])
    n_grains = max(1, int(round(float(np.prod(extent)) / mosaic.grain_size_m ** dim)))
    points = rng.random((n_grains, dim)) * extent
    fractions = np.array([m.fraction for m in mosaic.minerals])
    mineral_of_grain = rng.choice(len(fractions), size=n_grains, p=fractions / fractions.sum())
    centers = (np.argwhere(np.ones(shape, dtype=bool))[:, ::-1] + 0.5) * h
    _, grain = cKDTree(points).query(centers)
    grain = grain.reshape(shape)
    return mineral_of_grain[grain] + 1, grain


def make_core(
    material: Material,
    *,
    height_m: float = 0.04,
    platform_m: float = 0.05,
    epa_deg: float = 80.0,
    cell_size_m: float = 1e-3,
    dim: int = 2,
    depth_m: float = 0.03,
    seed: int | None = None,
) -> Stone:
    """Core with a flat platform (top face) and an exterior face meeting it at
    the edge with exterior platform angle ``epa_deg``.

    In 2D ``depth_m`` is the out-of-plane thickness; in 3D the section is
    extruded over ``depth_m`` along z (must be a whole number of cells). A mosaic material needs an explicit
    ``seed`` (all randomness comes from stated seeds).
    """
    if dim not in (2, 3):
        raise ValueError("dim must be 2 or 3")
    if not 0.0 < epa_deg < 180.0:
        raise ValueError("epa_deg must be in (0, 180)")
    for label, v in (("height_m", height_m), ("platform_m", platform_m),
                     ("cell_size_m", cell_size_m), ("depth_m", depth_m)):
        if not (math.isfinite(v) and v > 0):
            raise ValueError(f"{label} must be positive and finite")
    h = float(cell_size_m)
    inside = _core_mask_2d(height_m, platform_m, epa_deg, h)
    if dim == 3:
        nz = int(round(depth_m / h))
        if nz < 1 or abs(nz * h - depth_m) > 1e-9 * depth_m:
            raise ValueError("in 3D depth_m must be a whole number of cells")
        inside = np.broadcast_to(inside, (nz,) + inside.shape).copy()
    phases = phases_of(material)
    grain = None
    if material.mosaic is None:
        cells = inside.astype(np.int16)
    else:
        if seed is None:
            raise ValueError(f"{material.name} is a mosaic; pass seed=")
        ids, grain = _mosaic_phase_ids(material, inside.shape, h, seed)
        cells = np.where(inside, ids, 0).astype(np.int16)
        grain = np.where(inside, grain, -1).astype(np.int32)
    meta = {
        "edge_m": (platform_m, height_m),
        "epa_deg": float(epa_deg),
        "platform_normal": (0.0, 1.0) if dim == 2 else (0.0, 1.0, 0.0),
        "seed": seed,
    }
    return Stone(
        cells=cells,
        phases=phases,
        cell_size_m=h,
        material_name=material.name,
        thickness_m=float(depth_m),
        grain=grain,
        meta=meta,
    )
