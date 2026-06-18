"""Metabolism Physics v2 — composition-based eating/digestion primitives.

Design + protocol:
- reports/metabolism_physics_v2_design_2026-06-15.th.md
- reports/metabolism_physics_v2_0_protocol_2026-06-15.th.md

v2.0 scope: pure data + pure functions only. This module does NOT change any
runtime behavior; `world.environment.consume_food` still uses the v1 FOOD_ENERGY
table until v2.1 wires this in. Keeping the logic here (not in environment.py)
makes it unit-testable in isolation, which matters because the repo had no test
suite before this stage.

Philosophy (see design doc): the world must not declare what is "edible". An
object is ingestible if it physically fits the mouth (`can_ingest`), and yields
energy only to the extent the body can chemically break down its composition
(`digestible_energy`). Edibility and seed dispersal are meant to EMERGE from
physics, not from hand-coded rules.
"""

from __future__ import annotations

from collections.abc import Mapping

# Macronutrient channels. `shell` = indigestible seed coat (energy only if the
# gut's acid cracks it, handled in v2.2 via acid_strength vs shell_hardness).
# `toxin` carries no energy here; its penalty is handled separately in v2.3.
NUTRIENTS: tuple[str, ...] = ("sugar", "protein", "fiber", "shell", "water", "toxin")

# Abstract energy per 1.0 unit of mass when a nutrient is digested at 100%.
# Units are internal and consistent, not real calories (see design doc Q11.1).
ENERGY_DENSITY: dict[str, float] = {
    "sugar": 18.0,
    "protein": 24.0,
    "fiber": 9.0,
    "shell": 0.0,
    "water": 0.0,
    "toxin": 0.0,
}

# Composition fractions per food kind. Each kind's fractions sum to 1.0.
# Keys must match world.environment food-kind constants (FOOD_RAW_PLANT, ...).
COMPOSITION: dict[str, dict[str, float]] = {
    "raw_plant": {"sugar": 0.20, "protein": 0.05, "fiber": 0.30, "shell": 0.10, "water": 0.35},
    "raw_meat": {"sugar": 0.00, "protein": 0.55, "fiber": 0.00, "shell": 0.00, "water": 0.45},
    # raw_seed: edible-but-low-value food for the food-value-learning study.
    # Mostly indigestible shell -> tiny net energy (~1 vs raw_plant ~5), and a
    # small size so it fits any mouth (the ingestion gate is size-only). It is a
    # genuine FOOD here (a deliberate diet choice), distinct from the plant_seeds
    # that ride through the gut as an endozoochory byproduct. Spawned only when
    # low_value_food_spawn_per_tick > 0, so default worlds are unchanged.
    "raw_seed": {"sugar": 0.10, "protein": 0.00, "fiber": 0.25, "shell": 0.60, "water": 0.05},
}

# Default mass and physical size per food kind (abstract units).
FOOD_MASS: dict[str, float] = {"raw_plant": 1.0, "raw_meat": 1.5, "raw_seed": 0.4}
FOOD_SIZE: dict[str, float] = {"raw_plant": 2.0, "raw_meat": 5.0, "raw_seed": 1.0}


def digestible_energy(
    composition: Mapping[str, float],
    mass: float,
    enzyme: Mapping[str, float],
) -> float:
    """Energy a body extracts from one object.

    energy = mass * Σ_n composition[n] * enzyme[n] * ENERGY_DENSITY[n]

    Nutrients absent from `enzyme` contribute zero (the body cannot break them
    down). Result is never negative; toxin penalties are handled elsewhere.
    """
    total = 0.0
    for nutrient, fraction in composition.items():
        efficiency = enzyme.get(nutrient, 0.0)
        density = ENERGY_DENSITY.get(nutrient, 0.0)
        total += fraction * efficiency * density
    return max(0.0, mass * total)


def can_ingest(object_size: float, gape: float) -> bool:
    """An object can enter the mouth iff it is no larger than the gape."""
    return object_size <= gape


def toxin_load(composition: Mapping[str, float], mass: float) -> float:
    """Total toxin ingested from one object (mass x its toxin fraction).

    v2.3 scaffold — not yet wired into the eating path. Real toxin selection
    pressure switches on with mortality in Phase 6 (see design doc layer 4)."""
    return max(0.0, mass * composition.get("toxin", 0.0))


def toxin_penalty(ingested_toxin: float, toxin_tolerance: float) -> float:
    """Health/energy penalty from toxin exceeding the body's tolerance.

    Zero while within tolerance; otherwise the excess. v2.3 scaffold."""
    return max(0.0, ingested_toxin - max(0.0, toxin_tolerance))
