"""Material constants for the lithic fracture world.

All values are read from ``physics-loop/spec/materials.json`` (SI units); this
module adds nothing of its own. Each material is a set of physical constants
only. Granite also carries a mineral mosaic description (grain size and
per-mineral constants from Yu et al. 2018, Table 4).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
import math
from pathlib import Path

SPEC_PATH = Path(__file__).resolve().parent.parent / "physics-loop" / "spec" / "materials.json"

_FIELDS = (
    "youngs_modulus_pa",
    "poisson_ratio",
    "density_kg_m3",
    "fracture_toughness_pa_sqrt_m",
    "tensile_strength_pa",
    "microstructure_scale_m",
)


@dataclass(frozen=True)
class Mineral:
    name: str
    fraction: float
    youngs_modulus_pa: float
    poisson_ratio: float
    tensile_strength_pa: float


@dataclass(frozen=True)
class Mosaic:
    grain_size_m: float
    minerals: tuple[Mineral, ...]


@dataclass(frozen=True)
class Material:
    name: str
    youngs_modulus_pa: float
    poisson_ratio: float
    density_kg_m3: float
    fracture_toughness_pa_sqrt_m: float
    tensile_strength_pa: float
    microstructure_scale_m: float
    heterogeneity: str
    mosaic: Mosaic | None = None

    @property
    def plane_strain_modulus_pa(self) -> float:
        """E' = E / (1 - nu^2) (plane strain; Anderson 2017, Fracture Mechanics, ch. 2)."""
        return self.youngs_modulus_pa / (1.0 - self.poisson_ratio ** 2)

    @property
    def fracture_energy_j_m2(self) -> float:
        """G_c = K_IC^2 / E' (Irwin relation, plane strain; Anderson 2017, ch. 2)."""
        return self.fracture_toughness_pa_sqrt_m ** 2 / self.plane_strain_modulus_pa

    @property
    def shear_modulus_pa(self) -> float:
        return self.youngs_modulus_pa / (2.0 * (1.0 + self.poisson_ratio))

    @property
    def bulk_wave_speed_m_s(self) -> float:
        """Bar wave speed sqrt(E/rho); used only for time scales."""
        return math.sqrt(self.youngs_modulus_pa / self.density_kg_m3)


@lru_cache(maxsize=1)
def _spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))["materials"]


def _parse_mosaic(raw: dict | None) -> Mosaic | None:
    if not raw:
        return None
    minerals = tuple(
        Mineral(
            name=name,
            fraction=float(m["fraction"]),
            youngs_modulus_pa=float(m["youngs_modulus_pa"]),
            poisson_ratio=float(m["poisson_ratio"]),
            tensile_strength_pa=float(m["tensile_strength_pa"]),
        )
        for name, m in raw["minerals"].items()
    )
    return Mosaic(grain_size_m=float(raw["grain_size_m"]), minerals=minerals)


MATERIAL_NAMES: tuple[str, ...] = tuple(_spec().keys())


@lru_cache(maxsize=None)
def load_material(name: str) -> Material:
    spec = _spec()
    if name not in spec:
        raise KeyError(f"unknown material {name!r}; known: {', '.join(MATERIAL_NAMES)}")
    raw = spec[name]
    values = {f: float(raw[f]["value"]) for f in _FIELDS}
    return Material(
        name=name,
        heterogeneity=str(raw.get("heterogeneity", "homogeneous")),
        mosaic=_parse_mosaic(raw.get("mosaic")),
        **values,
    )
