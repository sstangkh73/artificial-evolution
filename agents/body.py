from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from random import Random


TOTAL_BODY_COST = 100
SENSOR_COST = 10
MUSCLE_COST = 15
ARMOR_COST = 20
BRAIN_COST = 25

TRAIT_ARCHETYPES = {
    "cautious_forager": {
        "brain_capacity": 2.6,
        "memory_retention": 0.72,
        "planning_focus": 0.60,
        "cooperation_drive": 0.42,
        "parenting_instinct": 0.52,
        "curiosity": 0.38,
        "fear": 0.74,
        "aggression": 0.20,
        "metabolism_rate": 0.90,
        "plant_efficiency": 1.18,
        "meat_efficiency": 0.92,
        "reproduction_drive": 0.44,
        "reproduction_investment": 0.66,
    },
    "social_planner": {
        "brain_capacity": 4.1,
        "memory_retention": 0.88,
        "planning_focus": 0.90,
        "cooperation_drive": 0.86,
        "parenting_instinct": 0.82,
        "curiosity": 0.56,
        "fear": 0.48,
        "aggression": 0.34,
        "metabolism_rate": 1.06,
        "plant_efficiency": 1.04,
        "meat_efficiency": 1.08,
        "reproduction_drive": 0.58,
        "reproduction_investment": 0.86,
    },
    "fierce_hunter": {
        "brain_capacity": 3.3,
        "memory_retention": 0.58,
        "planning_focus": 0.54,
        "cooperation_drive": 0.64,
        "parenting_instinct": 0.34,
        "curiosity": 0.78,
        "fear": 0.22,
        "aggression": 0.84,
        "metabolism_rate": 1.16,
        "plant_efficiency": 0.84,
        "meat_efficiency": 1.22,
        "reproduction_drive": 0.62,
        "reproduction_investment": 0.44,
    },
    "nurturing_settler": {
        "brain_capacity": 3.8,
        "memory_retention": 0.84,
        "planning_focus": 0.76,
        "cooperation_drive": 0.74,
        "parenting_instinct": 0.94,
        "curiosity": 0.42,
        "fear": 0.58,
        "aggression": 0.18,
        "metabolism_rate": 0.96,
        "plant_efficiency": 1.12,
        "meat_efficiency": 1.00,
        "reproduction_drive": 0.50,
        "reproduction_investment": 0.94,
    },
}

TRAIT_FIELDS = (
    "brain_capacity",
    "memory_retention",
    "planning_focus",
    "cooperation_drive",
    "parenting_instinct",
    "curiosity",
    "fear",
    "aggression",
    "metabolism_rate",
    "plant_efficiency",
    "meat_efficiency",
    "reproduction_drive",
    "reproduction_investment",
)

MORPHOLOGY_FIELDS = (
    "sensor_units",
    "muscle_units",
    "armor_units",
    "brain_units",
)

TRAIT_BOUNDS = {
    "brain_capacity": (0.0, 6.0),
    "memory_retention": (0.0, 1.5),
    "planning_focus": (0.0, 1.5),
    "cooperation_drive": (0.0, 1.5),
    "parenting_instinct": (0.0, 1.5),
    "curiosity": (0.0, 1.5),
    "fear": (0.0, 1.5),
    "aggression": (0.0, 1.5),
    "metabolism_rate": (0.6, 1.6),
    "plant_efficiency": (0.6, 1.6),
    "meat_efficiency": (0.6, 1.6),
    "reproduction_drive": (0.0, 1.5),
    "reproduction_investment": (0.0, 1.5),
}

TRAIT_MUTATION_STEPS = {
    "brain_capacity": 0.18,
    "memory_retention": 0.06,
    "planning_focus": 0.06,
    "cooperation_drive": 0.06,
    "parenting_instinct": 0.06,
    "curiosity": 0.06,
    "fear": 0.06,
    "aggression": 0.06,
    "metabolism_rate": 0.04,
    "plant_efficiency": 0.05,
    "meat_efficiency": 0.05,
    "reproduction_drive": 0.05,
    "reproduction_investment": 0.05,
}


@dataclass(frozen=True)
class BodyPlan:
    sensor_units: int
    muscle_units: int
    armor_units: int
    brain_units: int
    trait_profile: str = "baseline"
    brain_capacity: float = 0.0
    memory_retention: float = 0.0
    planning_focus: float = 0.0
    cooperation_drive: float = 0.0
    parenting_instinct: float = 0.0
    curiosity: float = 0.0
    fear: float = 0.0
    aggression: float = 0.0
    metabolism_rate: float = 1.0
    plant_efficiency: float = 1.0
    meat_efficiency: float = 1.0
    reproduction_drive: float = 0.5
    reproduction_investment: float = 0.5
    inherited_from_profiles: str = "generated"
    trait_mutation_count: int = 0
    morphology_mutation_count: int = 0
    # Metabolism Physics v2 genes (heritable; defaults keep v1 behavior intact).
    # See reports/metabolism_physics_v2_0_protocol_2026-06-15.th.md
    gape: float = 5.0
    gut_capacity: float = 8.0
    gut_transit_ticks: int = 6
    acid_strength: float = 0.4
    cellulose_efficiency: float = 0.25
    toxin_tolerance: float = 0.2

    @classmethod
    def from_archetype(
        cls,
        sensor_units: int,
        muscle_units: int,
        armor_units: int,
        brain_units: int,
        trait_profile: str,
    ) -> "BodyPlan":
        archetype = TRAIT_ARCHETYPES[trait_profile]
        return cls(
            sensor_units=sensor_units,
            muscle_units=muscle_units,
            armor_units=armor_units,
            brain_units=brain_units,
            trait_profile=trait_profile,
            **archetype,
        )

    @property
    def total_cost(self) -> int:
        return (
            self.sensor_units * SENSOR_COST
            + self.muscle_units * MUSCLE_COST
            + self.armor_units * ARMOR_COST
            + self.brain_units * BRAIN_COST
        )

    @property
    def enzyme_profile(self) -> dict[str, float]:
        """Digestive efficiency per nutrient, derived from heritable genes.

        See reports/metabolism_physics_v2_0_protocol_2026-06-15.th.md. `shell`
        is 0.0 here: seed coats are cracked by gut acid (acid_strength vs a
        seed's shell_hardness, v2.2), not by enzymes.
        """
        return {
            "sugar": 0.9,
            "protein": 0.7 * self.meat_efficiency,
            "fiber": self.cellulose_efficiency * self.plant_efficiency,
            "shell": 0.0,
            "water": 0.0,
        }

    @property
    def sensor_vision(self) -> int:
        return 2 + self.sensor_units

    @property
    def brain_processing_limit(self) -> int:
        return int(2 * (self.brain_units + 1) + (self.brain_capacity // 2))

    @property
    def effective_vision(self) -> int:
        return min(self.sensor_vision, self.brain_processing_limit)

    @property
    def speed(self) -> int:
        base_speed = 1 + self.muscle_units // 2
        armor_penalty = self.armor_units // 2
        return max(1, base_speed - armor_penalty)

    @property
    def durability(self) -> int:
        return 10 + (self.armor_units * 8)

    @property
    def passive_energy_drain(self) -> int:
        brain_load = (self.brain_units * 0.7) + (self.brain_capacity * 0.18)
        metabolism_load = max(0.0, self.metabolism_rate - 1.0) * 2.4
        return max(0, int(round(brain_load + metabolism_load)))

    @property
    def decision_quality(self) -> int:
        return max(1, int(round(1 + self.brain_units + (self.planning_focus * 2.0))))

    @property
    def cognition_score(self) -> float:
        return self.brain_units + (self.brain_capacity / 2.5)

    @property
    def social_score(self) -> float:
        return self.cooperation_drive + self.parenting_instinct + (self.brain_units * 0.15)

    @property
    def danger_avoidance(self) -> float:
        return max(0.0, min(1.5, self.fear + (self.planning_focus * 0.35)))

    @property
    def exploration_drive(self) -> float:
        return max(0.0, min(1.5, self.curiosity - (self.fear * 0.25)))

    @property
    def memory_score(self) -> float:
        return max(0.0, self.memory_retention + (self.brain_capacity * 0.05))

    @property
    def cooking_skill(self) -> float:
        return max(0.0, (self.brain_units - 1) * 0.35 + self.planning_focus * 0.8)

    @property
    def crafting_skill(self) -> float:
        return max(0.0, (self.brain_units - 2) * 0.4 + self.planning_focus + (self.memory_retention * 0.5))

    @property
    def hunt_drive(self) -> float:
        return self.aggression + (self.meat_efficiency - 1.0) + (self.muscle_units * 0.08)

    @property
    def gather_drive(self) -> float:
        return self.plant_efficiency + self.memory_retention + (self.sensor_units * 0.05)

    @property
    def life_history_label(self) -> str:
        if self.reproduction_drive >= 0.6 and self.reproduction_investment <= 0.55:
            return "fast_breeder"
        if self.reproduction_investment >= 0.8:
            return "care_investor"
        return "balanced_lineage"

    @property
    def diet_label(self) -> str:
        if self.meat_efficiency - self.plant_efficiency >= 0.15:
            return "carnivore_bias"
        if self.plant_efficiency - self.meat_efficiency >= 0.15:
            return "herbivore_bias"
        return "omnivore_bias"

    def is_valid(self) -> bool:
        return self.total_cost <= TOTAL_BODY_COST

    @property
    def short_description(self) -> str:
        return (
            f"sensor={self.sensor_units}, "
            f"muscle={self.muscle_units}, "
            f"armor={self.armor_units}, "
            f"brain={self.brain_units}, "
            f"profile={self.trait_profile}"
        )

    @property
    def stats_description(self) -> str:
        return (
            f"cost={self.total_cost}, "
            f"sensor_vision={self.sensor_vision}, "
            f"brain_limit={self.brain_processing_limit}, "
            f"effective_vision={self.effective_vision}, "
            f"speed={self.speed}, "
            f"durability={self.durability}, "
            f"brain_drain={self.passive_energy_drain}, "
            f"metabolism={self.metabolism_rate:.2f}, "
            f"memory={self.memory_score:.2f}, "
            f"social={self.social_score:.2f}, "
            f"diet={self.diet_label}, "
            f"life_history={self.life_history_label}, "
            f"trait_mutations={self.trait_mutation_count}, "
            f"morph_mutations={self.morphology_mutation_count}"
        )

    @property
    def trait_values(self) -> dict[str, float]:
        return {field: getattr(self, field) for field in TRAIT_FIELDS}

    @property
    def morphology_values(self) -> dict[str, int]:
        return {field: getattr(self, field) for field in MORPHOLOGY_FIELDS}


BODY_LIBRARY = [
    BodyPlan.from_archetype(2, 2, 1, 1, "fierce_hunter"),
    BodyPlan.from_archetype(1, 4, 0, 1, "fierce_hunter"),
    BodyPlan.from_archetype(3, 1, 1, 1, "cautious_forager"),
    BodyPlan.from_archetype(1, 1, 2, 1, "nurturing_settler"),
    BodyPlan.from_archetype(4, 0, 0, 2, "social_planner"),
]


def validate_body_library() -> None:
    invalid = [body for body in BODY_LIBRARY if not body.is_valid()]
    if invalid:
        raise ValueError(f"Invalid body plans found: {invalid}")


def generate_candidate_body_plans() -> list[BodyPlan]:
    candidates: list[BodyPlan] = []

    for sensor_units, muscle_units, armor_units, brain_units in product(
        range(0, 9),
        range(0, 7),
        range(0, 5),
        range(0, 5),
    ):
        for trait_profile in TRAIT_ARCHETYPES:
            body = BodyPlan.from_archetype(
                sensor_units=sensor_units,
                muscle_units=muscle_units,
                armor_units=armor_units,
                brain_units=brain_units,
                trait_profile=trait_profile,
            )
            if not body.is_valid():
                continue
            candidates.append(body)

    candidates.sort(
        key=lambda body: (
            -body.cognition_score,
            -body.social_score,
            -body.effective_vision,
            body.passive_energy_drain,
            -body.durability,
            body.speed,
            body.total_cost,
            body.trait_profile,
        )
    )
    return candidates


def create_trait_variant(
    base: BodyPlan,
    variant_name: str,
    *,
    brain_capacity_delta: float = 0.0,
    memory_delta: float = 0.0,
    planning_delta: float = 0.0,
    cooperation_delta: float = 0.0,
    parenting_delta: float = 0.0,
    curiosity_delta: float = 0.0,
    fear_delta: float = 0.0,
    aggression_delta: float = 0.0,
    metabolism_delta: float = 0.0,
    plant_efficiency_delta: float = 0.0,
    meat_efficiency_delta: float = 0.0,
    reproduction_drive_delta: float = 0.0,
    reproduction_investment_delta: float = 0.0,
) -> BodyPlan:
    return BodyPlan(
        sensor_units=base.sensor_units,
        muscle_units=base.muscle_units,
        armor_units=base.armor_units,
        brain_units=base.brain_units,
        trait_profile=f"{base.trait_profile}:{variant_name}",
        brain_capacity=max(0.0, base.brain_capacity + brain_capacity_delta),
        memory_retention=max(0.0, min(1.5, base.memory_retention + memory_delta)),
        planning_focus=max(0.0, min(1.5, base.planning_focus + planning_delta)),
        cooperation_drive=max(0.0, min(1.5, base.cooperation_drive + cooperation_delta)),
        parenting_instinct=max(0.0, min(1.5, base.parenting_instinct + parenting_delta)),
        curiosity=max(0.0, min(1.5, base.curiosity + curiosity_delta)),
        fear=max(0.0, min(1.5, base.fear + fear_delta)),
        aggression=max(0.0, min(1.5, base.aggression + aggression_delta)),
        metabolism_rate=max(0.6, min(1.6, base.metabolism_rate + metabolism_delta)),
        plant_efficiency=max(0.6, min(1.6, base.plant_efficiency + plant_efficiency_delta)),
        meat_efficiency=max(0.6, min(1.6, base.meat_efficiency + meat_efficiency_delta)),
        reproduction_drive=max(0.0, min(1.5, base.reproduction_drive + reproduction_drive_delta)),
        reproduction_investment=max(0.0, min(1.5, base.reproduction_investment + reproduction_investment_delta)),
        inherited_from_profiles=base.trait_profile,
    )


def inherit_body_plan(
    parent_a: BodyPlan,
    parent_b: BodyPlan,
    rng: Random,
    *,
    trait_mutation_rate: float = 0.35,
    major_trait_mutation_rate: float = 0.06,
    morphology_mutation_rate: float = 0.10,
) -> BodyPlan:
    morphology = _inherit_morphology(parent_a, parent_b, rng)
    morphology_mutations = 0
    if rng.random() < morphology_mutation_rate:
        morphology_mutations = _mutate_morphology(morphology, rng)
    morphology = _normalize_morphology_budget(morphology)

    traits: dict[str, float] = {}
    trait_mutations = 0
    for field in TRAIT_FIELDS:
        base_value = _inherit_trait_value(getattr(parent_a, field), getattr(parent_b, field), rng)
        mutated_value = base_value
        if rng.random() < trait_mutation_rate:
            step = TRAIT_MUTATION_STEPS[field]
            mutated_value += rng.uniform(-step, step)
            trait_mutations += 1
        if rng.random() < major_trait_mutation_rate:
            step = TRAIT_MUTATION_STEPS[field] * 1.8
            mutated_value += rng.uniform(-step, step)
            trait_mutations += 1
        low, high = TRAIT_BOUNDS[field]
        traits[field] = _clamp(mutated_value, low, high)

    parent_profile = parent_a.trait_profile if parent_a.trait_profile == parent_b.trait_profile else "hybrid"
    return BodyPlan(
        sensor_units=morphology["sensor_units"],
        muscle_units=morphology["muscle_units"],
        armor_units=morphology["armor_units"],
        brain_units=morphology["brain_units"],
        trait_profile=parent_profile,
        inherited_from_profiles=f"{parent_a.trait_profile}|{parent_b.trait_profile}",
        trait_mutation_count=trait_mutations,
        morphology_mutation_count=morphology_mutations,
        **traits,
    )


def _inherit_morphology(parent_a: BodyPlan, parent_b: BodyPlan, rng: Random) -> dict[str, int]:
    morphology: dict[str, int] = {}
    for field in MORPHOLOGY_FIELDS:
        value_a = getattr(parent_a, field)
        value_b = getattr(parent_b, field)
        if rng.random() < 0.5:
            morphology[field] = value_a
        else:
            morphology[field] = value_b
        if rng.random() < 0.5:
            morphology[field] = int(round((value_a + value_b) / 2))
    return morphology


def _mutate_morphology(morphology: dict[str, int], rng: Random) -> int:
    field = MORPHOLOGY_FIELDS[rng.randrange(len(MORPHOLOGY_FIELDS))]
    delta = -1 if rng.random() < 0.5 else 1
    current = morphology[field]
    upper_bounds = {
        "sensor_units": 8,
        "muscle_units": 6,
        "armor_units": 4,
        "brain_units": 4,
    }
    morphology[field] = max(0, min(upper_bounds[field], current + delta))
    return 1 if morphology[field] != current else 0


def _normalize_morphology_budget(morphology: dict[str, int]) -> dict[str, int]:
    while (
        morphology["sensor_units"] * SENSOR_COST
        + morphology["muscle_units"] * MUSCLE_COST
        + morphology["armor_units"] * ARMOR_COST
        + morphology["brain_units"] * BRAIN_COST
    ) > TOTAL_BODY_COST:
        if morphology["muscle_units"] > 0:
            morphology["muscle_units"] -= 1
            continue
        if morphology["sensor_units"] > 0:
            morphology["sensor_units"] -= 1
            continue
        if morphology["armor_units"] > 0:
            morphology["armor_units"] -= 1
            continue
        if morphology["brain_units"] > 0:
            morphology["brain_units"] -= 1
            continue
        break
    return morphology


def _inherit_trait_value(value_a: float, value_b: float, rng: Random) -> float:
    midpoint = (value_a + value_b) / 2.0
    blend = rng.uniform(0.35, 0.65)
    return (value_a * blend) + (value_b * (1.0 - blend)) if rng.random() < 0.5 else midpoint


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
