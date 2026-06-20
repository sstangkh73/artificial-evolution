from __future__ import annotations

from dataclasses import dataclass, field
import math
from random import Random

MATERIAL_WOOD = "wood"
MATERIAL_STONE = "stone"
MATERIAL_FIBER = "fiber"
MATERIAL_LEAF = "leaf"
MATERIAL_WATER = "water"
MATERIAL_SOIL = "soil"
MATERIAL_CLAY = "clay"
MATERIAL_SAND = "sand"
MATERIAL_IRON = "iron"
MATERIAL_ASH = "ash"


ZONE_SAFE_LOW_FOOD = "safe_low_food"
ZONE_SAFE_HIGH_FOOD = "safe_high_food"
ZONE_DANGER_HIGH_FOOD = "danger_high_food"
ZONE_DANGER_LOW_FOOD = "danger_low_food"

FOOD_RAW_PLANT = "raw_plant"
FOOD_RAW_MEAT = "raw_meat"
FOOD_RAW_SEED = "raw_seed"  # edible low-value food for the food-value-learning study

SEASON_SPRING = "spring"
SEASON_SUMMER = "summer"
SEASON_AUTUMN = "autumn"
SEASON_WINTER = "winter"

SEASONS = [
    SEASON_SPRING,
    SEASON_SUMMER,
    SEASON_AUTUMN,
    SEASON_WINTER,
]

ZONE_PROFILES = {
    ZONE_SAFE_LOW_FOOD: {
        "food_density": 0.18,
        "food_energy": 30,
        "danger": 0.10,
    },
    ZONE_SAFE_HIGH_FOOD: {
        "food_density": 0.78,
        "food_energy": 42,
        "danger": 0.08,
    },
    ZONE_DANGER_HIGH_FOOD: {
        "food_density": 0.72,
        "food_energy": 50,
        "danger": 0.48,
    },
    ZONE_DANGER_LOW_FOOD: {
        "food_density": 0.08,
        "food_energy": 24,
        "danger": 0.62,
    },
}

SEASON_FOOD_MULTIPLIER = {
    SEASON_SPRING: 1.20,
    SEASON_SUMMER: 1.00,
    SEASON_AUTUMN: 0.85,
    SEASON_WINTER: 0.60,
}

FOOD_ENERGY = {
    FOOD_RAW_PLANT: 6,
    FOOD_RAW_MEAT: 18,
    FOOD_RAW_SEED: 1,  # v1 fallback only; the study runs under v2 composition energy
}

AMBIENT_TEMPERATURE_K = 293.15
IGNITION_OXYGEN_MIN = 0.12
WATER_HEAT_DAMPING = 0.18


@dataclass(frozen=True)
class MaterialSpec:
    name: str
    density_kg_m3: float
    specific_heat_j_kgk: float
    thermal_conductivity_w_mk: float
    moisture_capacity: float
    ignition_point_k: float | None
    pyrolysis_point_k: float | None
    softening_point_k: float | None
    melting_point_k: float | None
    yield_strength_mpa: float
    char_yield: float
    oxidation_rate: float
    porosity: float
    photosynthetic_transmittance: float = 0.0
    solar_reflectance: float = 0.18
    solar_absorptance: float = 0.72
    infrared_transmittance: float = 0.02
    compressive_strength_mpa: float = 1.0
    tensile_strength_mpa: float = 0.2
    bending_strength_mpa: float = 0.3
    cutting_resistance_n: float = 10.0
    friction_coefficient: float = 0.55


MATERIAL_SPECS = {
    MATERIAL_WOOD: MaterialSpec(
        name=MATERIAL_WOOD,
        density_kg_m3=650.0,
        specific_heat_j_kgk=1700.0,
        thermal_conductivity_w_mk=0.14,
        moisture_capacity=0.65,
        ignition_point_k=573.15,
        pyrolysis_point_k=473.15,
        softening_point_k=None,
        melting_point_k=None,
        yield_strength_mpa=45.0,
        char_yield=0.28,
        oxidation_rate=0.55,
        porosity=0.55,
        photosynthetic_transmittance=0.04,
        solar_reflectance=0.22,
        solar_absorptance=0.70,
        infrared_transmittance=0.03,
        compressive_strength_mpa=35.0,
        tensile_strength_mpa=75.0,
        bending_strength_mpa=65.0,
        cutting_resistance_n=55.0,
        friction_coefficient=0.62,
    ),
    MATERIAL_LEAF: MaterialSpec(
        name=MATERIAL_LEAF,
        density_kg_m3=140.0,
        specific_heat_j_kgk=1350.0,
        thermal_conductivity_w_mk=0.08,
        moisture_capacity=0.75,
        ignition_point_k=503.15,
        pyrolysis_point_k=433.15,
        softening_point_k=None,
        melting_point_k=None,
        yield_strength_mpa=8.0,
        char_yield=0.18,
        oxidation_rate=0.82,
        porosity=0.82,
        photosynthetic_transmittance=0.10,
        solar_reflectance=0.12,
        solar_absorptance=0.76,
        infrared_transmittance=0.08,
        compressive_strength_mpa=0.05,
        tensile_strength_mpa=1.2,
        bending_strength_mpa=0.08,
        cutting_resistance_n=2.0,
        friction_coefficient=0.45,
    ),
    MATERIAL_STONE: MaterialSpec(
        name=MATERIAL_STONE,
        density_kg_m3=2650.0,
        specific_heat_j_kgk=790.0,
        thermal_conductivity_w_mk=2.2,
        moisture_capacity=0.05,
        ignition_point_k=None,
        pyrolysis_point_k=None,
        softening_point_k=None,
        melting_point_k=1473.15,
        yield_strength_mpa=130.0,
        char_yield=0.0,
        oxidation_rate=0.01,
        porosity=0.04,
        photosynthetic_transmittance=0.0,
        solar_reflectance=0.24,
        solar_absorptance=0.70,
        infrared_transmittance=0.0,
        compressive_strength_mpa=120.0,
        tensile_strength_mpa=8.0,
        bending_strength_mpa=15.0,
        cutting_resistance_n=180.0,
        friction_coefficient=0.78,
    ),
    MATERIAL_SOIL: MaterialSpec(
        name=MATERIAL_SOIL,
        density_kg_m3=1400.0,
        specific_heat_j_kgk=1480.0,
        thermal_conductivity_w_mk=0.9,
        moisture_capacity=0.95,
        ignition_point_k=None,
        pyrolysis_point_k=None,
        softening_point_k=373.15,
        melting_point_k=None,
        yield_strength_mpa=18.0,
        char_yield=0.0,
        oxidation_rate=0.01,
        porosity=0.48,
        photosynthetic_transmittance=0.0,
        solar_reflectance=0.16,
        solar_absorptance=0.76,
        infrared_transmittance=0.0,
        compressive_strength_mpa=1.8,
        tensile_strength_mpa=0.08,
        bending_strength_mpa=0.12,
        cutting_resistance_n=8.0,
        friction_coefficient=0.68,
    ),
    MATERIAL_CLAY: MaterialSpec(
        name=MATERIAL_CLAY,
        density_kg_m3=1650.0,
        specific_heat_j_kgk=1100.0,
        thermal_conductivity_w_mk=0.95,
        moisture_capacity=1.05,
        ignition_point_k=None,
        pyrolysis_point_k=None,
        softening_point_k=393.15,
        melting_point_k=1673.15,
        yield_strength_mpa=22.0,
        char_yield=0.0,
        oxidation_rate=0.0,
        porosity=0.5,
        photosynthetic_transmittance=0.0,
        solar_reflectance=0.20,
        solar_absorptance=0.72,
        infrared_transmittance=0.0,
        compressive_strength_mpa=2.2,
        tensile_strength_mpa=0.12,
        bending_strength_mpa=0.18,
        cutting_resistance_n=12.0,
        friction_coefficient=0.72,
    ),
    MATERIAL_SAND: MaterialSpec(
        name=MATERIAL_SAND,
        density_kg_m3=1600.0,
        specific_heat_j_kgk=830.0,
        thermal_conductivity_w_mk=0.33,
        moisture_capacity=0.25,
        ignition_point_k=None,
        pyrolysis_point_k=None,
        softening_point_k=None,
        melting_point_k=1973.15,
        yield_strength_mpa=12.0,
        char_yield=0.0,
        oxidation_rate=0.0,
        porosity=0.42,
        photosynthetic_transmittance=0.0,
        solar_reflectance=0.34,
        solar_absorptance=0.58,
        infrared_transmittance=0.0,
        compressive_strength_mpa=0.9,
        tensile_strength_mpa=0.02,
        bending_strength_mpa=0.03,
        cutting_resistance_n=5.0,
        friction_coefficient=0.55,
    ),
    MATERIAL_WATER: MaterialSpec(
        name=MATERIAL_WATER,
        density_kg_m3=1000.0,
        specific_heat_j_kgk=4186.0,
        thermal_conductivity_w_mk=0.6,
        moisture_capacity=1.0,
        ignition_point_k=None,
        pyrolysis_point_k=None,
        softening_point_k=None,
        melting_point_k=273.15,
        yield_strength_mpa=0.0,
        char_yield=0.0,
        oxidation_rate=0.0,
        porosity=0.0,
        photosynthetic_transmittance=0.68,
        solar_reflectance=0.06,
        solar_absorptance=0.38,
        infrared_transmittance=0.35,
        compressive_strength_mpa=0.0,
        tensile_strength_mpa=0.0,
        bending_strength_mpa=0.0,
        cutting_resistance_n=0.0,
        friction_coefficient=0.0,
    ),
    MATERIAL_IRON: MaterialSpec(
        name=MATERIAL_IRON,
        density_kg_m3=7870.0,
        specific_heat_j_kgk=449.0,
        thermal_conductivity_w_mk=80.0,
        moisture_capacity=0.0,
        ignition_point_k=None,
        pyrolysis_point_k=None,
        softening_point_k=973.15,
        melting_point_k=1811.0,
        yield_strength_mpa=250.0,
        char_yield=0.0,
        oxidation_rate=0.05,
        porosity=0.0,
        photosynthetic_transmittance=0.0,
        solar_reflectance=0.55,
        solar_absorptance=0.40,
        infrared_transmittance=0.0,
        compressive_strength_mpa=250.0,
        tensile_strength_mpa=250.0,
        bending_strength_mpa=220.0,
        cutting_resistance_n=260.0,
        friction_coefficient=0.74,
    ),
    MATERIAL_FIBER: MaterialSpec(
        name=MATERIAL_FIBER,
        density_kg_m3=220.0,
        specific_heat_j_kgk=1500.0,
        thermal_conductivity_w_mk=0.1,
        moisture_capacity=0.7,
        ignition_point_k=523.15,
        pyrolysis_point_k=443.15,
        softening_point_k=None,
        melting_point_k=None,
        yield_strength_mpa=15.0,
        char_yield=0.22,
        oxidation_rate=0.68,
        porosity=0.7,
        photosynthetic_transmittance=0.16,
        solar_reflectance=0.18,
        solar_absorptance=0.66,
        infrared_transmittance=0.12,
        compressive_strength_mpa=0.12,
        tensile_strength_mpa=35.0,
        bending_strength_mpa=1.0,
        cutting_resistance_n=10.0,
        friction_coefficient=0.58,
    ),
    MATERIAL_ASH: MaterialSpec(
        name=MATERIAL_ASH,
        density_kg_m3=550.0,
        specific_heat_j_kgk=900.0,
        thermal_conductivity_w_mk=0.12,
        moisture_capacity=0.25,
        ignition_point_k=None,
        pyrolysis_point_k=None,
        softening_point_k=None,
        melting_point_k=1473.15,
        yield_strength_mpa=1.0,
        char_yield=0.0,
        oxidation_rate=0.0,
        porosity=0.88,
        photosynthetic_transmittance=0.0,
        solar_reflectance=0.32,
        solar_absorptance=0.60,
        infrared_transmittance=0.0,
        compressive_strength_mpa=0.04,
        tensile_strength_mpa=0.01,
        bending_strength_mpa=0.01,
        cutting_resistance_n=1.0,
        friction_coefficient=0.35,
    ),
}

CHILD_GROWTH = {
    FOOD_RAW_PLANT: 1,
    FOOD_RAW_MEAT: 3,
    "cooked_plant": 2,
    "cooked_meat": 4,
}


@dataclass(frozen=True)
class FoodResource:
    kind: str
    energy: int
    source: str = "ambient_spawn"
    plant_id: int | None = None
    created_tick: int = 0
    # Metabolism Physics v2: seed carried inside fruit (used by gut/excretion in
    # v2.2). Default None keeps v1 behavior. See metabolism_physics_v2 design doc.
    seed_payload: int | None = None


@dataclass(frozen=True)
class PlantSpeciesSpec:
    name: str
    germination_water_min: float
    germination_water_max: float
    germination_temp_min_k: float
    germination_temp_max_k: float
    germination_oxygen_min: float
    burial_depth_min_cm: float
    burial_depth_max_cm: float
    germination_good_ticks: int
    light_saturation: float
    nutrient_demand: float
    maturity_biomass: float
    fruiting_interval_ticks: int
    max_age_ticks: int
    natural_seed_interval_ticks: int
    natural_seed_drop_chance: float
    natural_seed_drop_radius: int
    natural_seed_drop_max_count: int
    # Metabolism v2 (endozoochory): resistance of the seed coat to gut acid.
    shell_hardness: float = 0.6


PLANT_SPECIES = {
    "wild_grain": PlantSpeciesSpec(
        name="wild_grain",
        germination_water_min=0.24,
        germination_water_max=0.78,
        germination_temp_min_k=281.0,
        germination_temp_max_k=309.0,
        germination_oxygen_min=0.14,
        burial_depth_min_cm=0.3,
        burial_depth_max_cm=4.5,
        germination_good_ticks=28,
        light_saturation=0.64,
        nutrient_demand=0.32,
        maturity_biomass=1.0,
        fruiting_interval_ticks=85,
        max_age_ticks=900,
        natural_seed_interval_ticks=120,
        natural_seed_drop_chance=0.38,
        natural_seed_drop_radius=3,
        natural_seed_drop_max_count=3,
        shell_hardness=0.6,
    )
}


@dataclass
class PlantSeed:
    seed_id: int
    species: str
    x: int
    y: int
    burial_depth_cm: float
    viability: float = 1.0
    age_ticks: int = 0
    accumulated_good_ticks: int = 0
    biomass: float = 0.0
    state: str = "seed"
    last_food_tick: int = -10_000
    last_natural_seed_tick: int = -10_000
    carried_by_agent_id: int | None = None
    parent_plant_id: int | None = None
    dispersal_mode: str = "unknown"
    dropped_by_agent_id: int | None = None
    created_tick: int = 0


@dataclass
class LargeAnimal:
    animal_id: int
    herd_id: int
    x: int
    y: int
    defense: float
    energy: int
    speed: int
    awareness: int
    stage: str
    role: str


@dataclass
class PhysicalObject:
    object_id: int
    creator_agent_id: int | None
    creator_lineage_id: str | None
    component_mix: dict[str, int]
    mass: int
    sharpness: int
    hardness: int
    length: int
    flexibility: int
    durability: int
    portability: bool
    use_count: int = 0
    total_outcome_score: float = 0.0
    contexts: dict[str, int] = field(default_factory=dict)
    user_ids: set[int] = field(default_factory=set)
    copied_by_agents: set[int] = field(default_factory=set)
    classification: str | None = None
    emergence_tick: int | None = None
    dominant_material: str = MATERIAL_WOOD
    temperature_k: float = AMBIENT_TEMPERATURE_K
    moisture_ratio: float = 0.08
    oxygen_exposure: float = 0.21
    volatile_fraction: float = 0.0
    carbon_fraction: float = 0.0
    ash_fraction: float = 0.0
    thermal_dose: float = 0.0
    blackness: float = 0.0
    softened: bool = False
    state_label: str = "raw"
    last_reported_state: str | None = None


@dataclass
class Nest:
    owner_id: int
    x: int
    y: int
    safe_radius: int
    food_storage: int = 0
    material_storage: dict[str, int] = field(default_factory=dict)
    object_storage: list[int] = field(default_factory=list)
    protected_children: set[int] = field(default_factory=set)
    last_active_tick: int = 0
    hearth_intensity: float = 0.0
    hearth_temperature_k: float = AMBIENT_TEMPERATURE_K
    hearth_fuel: float = 0.0
    hearth_oxygen: float = 0.21
    hearth_smoke: float = 0.0


@dataclass
class Environment:
    width: int = 100
    height: int = 100
    max_food: int = 220
    day_length: int = 20
    season_length: int = 80
    base_food_spawn_per_tick: int = 5
    max_large_animals: int = 24
    large_animal_spawn_per_tick: int = 2
    food_spawn_multiplier: float = 1.0
    nest_support_food_chance: float = 0.35
    nest_support_spawn_chance: float = 0.22
    nest_active_grace_ticks: int = 20
    safe_area_stone_chance: float = 0.0
    frontier_stone_bonus: float = 0.0
    frontier_band: int = 6
    fertility_recovery_rate: float = 0.0015
    fertility_spawn_cost: float = 0.14
    fertility_harvest_cost: float = 0.08
    minimum_fertility: float = 0.05
    global_food_decline_per_day: float = 0.025
    minimum_global_food_multiplier: float = 0.02
    bootstrap_food_spawn_ticks: int = 120
    wild_food_spawn_after_bootstrap_multiplier: float = 0.08
    natural_seed_rain_per_tick: int = 0
    max_plant_seeds: int = 450
    plant_lifecycle_enabled: bool = True
    plant_seed_max_age_multiplier: float = 1.0
    plant_growth_rate_multiplier: float = 1.0
    sprout_biomass_loss_multiplier: float = 1.0
    germination_good_ticks_multiplier: float = 1.0
    plant_fruiting_interval_multiplier: float = 1.0
    plant_fruiting_growth_threshold_multiplier: float = 1.0
    plant_fruiting_chance_multiplier: float = 1.0
    natural_seed_drop_chance_multiplier: float = 1.0
    scaffolded_agent_actions_enabled: bool = False
    scaffolded_nest_support_enabled: bool = False
    scaffolded_social_support_enabled: bool = False
    legacy_scaffold_nest_enabled: bool = False
    legacy_oracle_perception_enabled: bool = False
    food_signal_radius_cap: int | None = None
    plant_lifecycle_food_signal_weight: float = 1.35
    seed_hunger_drop_bonus: float = 0.06
    seed_drop_block_critical_hunger: bool = False
    seed_drop_safe_window_only: bool = False
    seed_drop_safe_hunger_max: float = 0.55
    seed_drop_safe_fear_max: float = 0.45
    seed_drop_safe_cold_max: float = 0.45
    seed_drop_safe_safety_min: float = 0.45
    # Metabolism Physics v2 selector: "v1" = legacy FOOD_ENERGY (default, no
    # behavior change); "v2" reserved for composition-based digestion (v2.1+).
    metabolism_model: str = "v1"
    # Food-value-learning study: spawn this many low-value raw_seed items per tick
    # (0 = off, default -> world unchanged). The agent must walk over and choose to
    # eat them; we then measure whether it learns they are not worth eating.
    low_value_food_spawn_per_tick: float = 0.0
    # Energy-economy study (default 1.0 = byte-identical): scale all food energy
    # up and/or all metabolic drain (base + brain + movement) down to find a
    # viable regime where intake can exceed drain.
    food_energy_multiplier: float = 1.0
    metabolic_drain_multiplier: float = 1.0
    # Food-value-learning study B (default off = no behavior change): agents learn
    # net energy per food kind and skip low-value food via an optimal-diet rule.
    food_value_learning_enabled: bool = False
    diet_pickiness: float = 0.5          # skip kind whose value < pickiness x best known
    diet_learning_rate: float = 0.3      # EMA alpha for learned food value
    diet_starvation_energy: int = 6      # below this, eat anything (true-starvation floor)
    # Reproduction-rate study (defaults = the agent.py constants -> byte-identical):
    # loosen these to test whether a self-sustaining multi-generation population
    # is reachable.
    repro_safety_threshold: float = 0.66
    repro_comfort_threshold: float = 0.58
    repro_safety_streak: int = 10
    repro_pair_bond_streak: int = 14
    repro_max_age: int = 200
    repro_litter_min: int = 1
    repro_litter_max: int = 3
    # Structural alternative (opt-in, default off): continuous density-dependent
    # stochastic reproduction (logistic) instead of the synchronized gate pulse.
    continuous_reproduction_enabled: bool = False
    continuous_repro_base_rate: float = 0.05
    continuous_repro_local_cap: float = 6.0
    # Home/breeding-site fidelity (opt-in): balanced agents return to home_anchor
    # and stay within home_radius instead of dispersing -> stable breeding clusters.
    home_fidelity_enabled: bool = False
    home_radius: int = 3
    ambient_food_decay_chance: float = 0.006
    plant_food_decay_chance: float = 0.003
    tick_count: int = 0
    food_positions: dict[tuple[int, int], FoodResource] = field(default_factory=dict)
    food_spawned_by_kind: dict[str, int] = field(default_factory=dict)
    large_animals: dict[int, LargeAnimal] = field(default_factory=dict)
    nests: dict[int, Nest] = field(default_factory=dict)
    objects: dict[int, PhysicalObject] = field(default_factory=dict)
    plant_seeds: dict[int, PlantSeed] = field(default_factory=dict)
    next_animal_id: int = 0
    next_herd_id: int = 0
    next_object_id: int = 0
    next_seed_id: int = 0
    active_nest_owner_ids: set[int] = field(default_factory=set)
    nest_owner_aliases: dict[int, int] = field(default_factory=dict)
    physics_events: list[str] = field(default_factory=list)
    zone_map: list[list[str]] = field(init=False)
    fertility_map: list[list[float]] = field(init=False)
    ground_material_map: list[list[str]] = field(init=False)
    moisture_map: list[list[float]] = field(init=False)
    temperature_map: list[list[float]] = field(init=False)
    oxygen_map: list[list[float]] = field(init=False)
    photosynthetic_light_map: list[list[float]] = field(init=False)
    soil_disturbance_map: list[list[float]] = field(init=False)
    soil_nitrogen_map: list[list[float]] = field(init=False)
    soil_phosphorus_map: list[list[float]] = field(init=False)
    soil_potassium_map: list[list[float]] = field(init=False)
    surface_fuel_map: list[list[float]] = field(init=False)
    managed_food_map: list[list[float]] = field(init=False)

    def __post_init__(self) -> None:
        self.zone_map = self._generate_zone_map()
        self.fertility_map = self._generate_fertility_map()
        self.ground_material_map = self._generate_ground_material_map()
        self.moisture_map = self._generate_moisture_map()
        self.temperature_map = self._generate_temperature_map()
        self.oxygen_map = self._generate_oxygen_map()
        self.photosynthetic_light_map = self._generate_photosynthetic_light_map()
        self.soil_disturbance_map = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        self.soil_nitrogen_map = self._generate_soil_nutrient_map("nitrogen")
        self.soil_phosphorus_map = self._generate_soil_nutrient_map("phosphorus")
        self.soil_potassium_map = self._generate_soil_nutrient_map("potassium")
        self.surface_fuel_map = self._generate_surface_fuel_map()
        self.managed_food_map = [[0.0 for _ in range(self.width)] for _ in range(self.height)]

    @property
    def is_night(self) -> bool:
        cycle = (self.tick_count // self.day_length) % 2
        return cycle == 1

    @property
    def season(self) -> str:
        season_index = (self.tick_count // self.season_length) % len(SEASONS)
        return SEASONS[season_index]

    def step(self, rng: Random) -> None:
        self.tick_count += 1
        self.physics_events.clear()
        self._recover_fertility()
        self._decay_managed_food()
        self._decay_soil_disturbance()
        self._decay_food_resources(rng)
        self._update_world_physics(rng)
        self._update_radiation_fields()
        self._natural_seed_rain(rng)
        self._update_plant_lifecycle(rng)
        self._spawn_food(rng)
        self._spawn_low_value_food(rng)
        self._spawn_large_animals(rng)
        self._move_large_animals(rng)
        if self.scaffolded_nest_support_enabled:
            self._support_nests(rng)
        self._update_nest_hearths(rng)
        self._update_object_physics()

    def get_biome(self, x: int, y: int) -> str:
        return self.zone_map[y][x]

    def get_zone_profile(self, x: int, y: int) -> dict[str, float]:
        return ZONE_PROFILES[self.get_biome(x, y)]

    def get_danger_level(self, x: int, y: int) -> float:
        return self.get_zone_profile(x, y)["danger"]

    def get_ground_material(self, x: int, y: int) -> str:
        return self.ground_material_map[y][x]

    def get_cell_temperature(self, x: int, y: int) -> float:
        return self.temperature_map[y][x]

    def get_cell_oxygen(self, x: int, y: int) -> float:
        return self.oxygen_map[y][x]

    def get_cell_moisture(self, x: int, y: int) -> float:
        return self.moisture_map[y][x]

    def get_cell_photosynthetic_light(self, x: int, y: int) -> float:
        return self.photosynthetic_light_map[y][x]

    def get_cell_soil_nutrients(self, x: int, y: int) -> float:
        return (
            self.soil_nitrogen_map[y][x]
            + self.soil_phosphorus_map[y][x]
            + self.soil_potassium_map[y][x]
        ) / 3.0

    def plant_state_counts(self) -> dict[str, int]:
        counts = {
            "seed": 0,
            "carried_seed": 0,
            "sprout": 0,
            "mature": 0,
            "dead": 0,
            "natural_drop_seed": 0,
            "harvest_drop_seed": 0,
            "agent_carried_seed": 0,
            "agent_disturbed_seed": 0,
            "natural_seed_rain_seed": 0,
        }
        for plant in self.plant_seeds.values():
            if plant.carried_by_agent_id is not None:
                counts["carried_seed"] += 1
                counts["agent_carried_seed"] += 1
            else:
                counts[plant.state] = counts.get(plant.state, 0) + 1
            if plant.dispersal_mode in {"natural_drop", "harvest_drop", "agent_carried", "agent_disturbed", "natural_seed_rain"}:
                key = f"{plant.dispersal_mode}_seed"
                counts[key] = counts.get(key, 0) + 1
        return counts

    def mean_photosynthetic_light(self) -> float:
        total = 0.0
        for row in self.photosynthetic_light_map:
            total += sum(row)
        return total / max(1, self.width * self.height)

    def mean_soil_nutrients(self) -> float:
        total = 0.0
        for y in range(self.height):
            for x in range(self.width):
                total += self.get_cell_soil_nutrients(x, y)
        return total / max(1, self.width * self.height)

    def pop_physics_events(self) -> list[str]:
        events = list(self.physics_events)
        self.physics_events.clear()
        return events

    def is_safe_area(self, x: int, y: int) -> bool:
        biome = self.get_biome(x, y)
        return biome in {ZONE_SAFE_LOW_FOOD, ZONE_SAFE_HIGH_FOOD}

    def is_frontier_area(self, x: int, y: int) -> bool:
        horizontal_boundary = (self.height // 2) - 1
        vertical_boundary = (self.width // 2) - 1
        return (
            abs(y - horizontal_boundary) <= self.frontier_band
            or abs(x - vertical_boundary) <= self.frontier_band
        )

    def consume_food(self, x: int, y: int, eater=None) -> FoodResource | None:
        resource = self.food_positions.pop((x, y), None)
        if resource is not None:
            self._deplete_fertility(x, y, self.fertility_harvest_cost)
            if resource.plant_id is not None:
                self._harvest_plant(resource.plant_id)
            if resource.kind == FOOD_RAW_PLANT:
                seed = self._drop_harvest_seed(x, y, resource)
                # v2 endozoochory: the harvested seed travels in the eater's gut
                # instead of being dropped at the eating spot.
                if seed is not None and eater is not None and self.metabolism_model == "v2":
                    self._route_seed_to_gut(seed, eater)
        return resource

    def food_signal_at(self, x: int, y: int, radius: int) -> float:
        signal = 0.0
        radius = max(0, radius)
        if self.food_signal_radius_cap is not None:
            radius = min(radius, max(0, self.food_signal_radius_cap))
        for (food_x, food_y), resource in self.food_positions.items():
            distance = abs(food_x - x) + abs(food_y - y)
            if distance > radius:
                continue
            source_weight = self.plant_lifecycle_food_signal_weight if resource.source == "plant_lifecycle" else 1.0
            signal += (resource.energy * source_weight) / ((distance + 1) ** 2)
        return signal

    def animal_signal_at(self, x: int, y: int, radius: int) -> float:
        signal = 0.0
        radius = max(0, radius)
        for animal in self.large_animals.values():
            distance = abs(animal.x - x) + abs(animal.y - y)
            if distance > radius:
                continue
            signal += animal.energy / ((distance + 1) ** 2)
        return signal

    def disturb_surface(self, x: int, y: int, force: float, agent_id: int | None = None) -> None:
        if not self.is_walkable(x, y) or force <= 0.0:
            return
        if self.ground_material_map[y][x] not in {MATERIAL_SOIL, MATERIAL_SAND, MATERIAL_CLAY}:
            return
        previous = self.soil_disturbance_map[y][x]
        self.soil_disturbance_map[y][x] = min(1.0, previous + force)
        if previous < 0.10 <= self.soil_disturbance_map[y][x]:
            actor = f" agent={agent_id}" if agent_id is not None else ""
            self.physics_events.append(
                f"surface_disturbed -> x={x} y={y}{actor} force={self.soil_disturbance_map[y][x]:.2f}"
            )

    def is_walkable(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def find_nearest_food(
        self,
        x: int,
        y: int,
        vision_range: int,
    ) -> tuple[int, int] | None:
        if not self.legacy_oracle_perception_enabled:
            return None
        nearest = None
        nearest_distance = None
        for food_x, food_y in self.food_positions:
            distance = abs(food_x - x) + abs(food_y - y)
            if distance > vision_range:
                continue
            if nearest_distance is None or distance < nearest_distance:
                nearest = (food_x, food_y)
                nearest_distance = distance
        return nearest

    def find_nearest_warm_cell(
        self,
        x: int,
        y: int,
        vision_range: int,
        minimum_temperature_k: float,
    ) -> tuple[int, int] | None:
        if not self.legacy_oracle_perception_enabled:
            return None
        nearest = None
        nearest_score = None
        min_x = max(0, x - vision_range)
        max_x = min(self.width - 1, x + vision_range)
        min_y = max(0, y - vision_range)
        max_y = min(self.height - 1, y + vision_range)
        for scan_y in range(min_y, max_y + 1):
            for scan_x in range(min_x, max_x + 1):
                temperature_k = self.temperature_map[scan_y][scan_x]
                if temperature_k < minimum_temperature_k:
                    continue
                distance = abs(scan_x - x) + abs(scan_y - y)
                danger = self.get_danger_level(scan_x, scan_y)
                score = (distance, danger, -temperature_k)
                if nearest_score is None or score < nearest_score:
                    nearest = (scan_x, scan_y)
                    nearest_score = score
        return nearest

    def find_loose_seed_at(self, x: int, y: int) -> PlantSeed | None:
        for plant in self.plant_seeds.values():
            if (
                plant.state == "seed"
                and plant.carried_by_agent_id is None
                and plant.x == x
                and plant.y == y
            ):
                return plant
        return None

    def pick_seed(self, seed_id: int, agent_id: int) -> bool:
        plant = self.plant_seeds.get(seed_id)
        if plant is None or plant.state != "seed" or plant.carried_by_agent_id is not None:
            return False
        plant.carried_by_agent_id = agent_id
        plant.dispersal_mode = "agent_carried"
        plant.dropped_by_agent_id = agent_id
        plant.x = -1
        plant.y = -1
        return True

    def drop_seed(self, seed_id: int, x: int, y: int, burial_depth_cm: float = 0.0) -> bool:
        plant = self.plant_seeds.get(seed_id)
        if plant is None or plant.state != "seed":
            return False
        if not self.is_walkable(x, y):
            return False
        plant.carried_by_agent_id = None
        plant.x = x
        plant.y = y
        if plant.dropped_by_agent_id is not None:
            plant.dispersal_mode = "agent_carried"
        plant.burial_depth_cm = max(0.0, burial_depth_cm)
        plant.accumulated_good_ticks = 0
        return True

    def find_nearest_large_animal(
        self,
        x: int,
        y: int,
        vision_range: int,
    ) -> LargeAnimal | None:
        nearest: LargeAnimal | None = None
        nearest_distance = None
        for animal in self.large_animals.values():
            distance = abs(animal.x - x) + abs(animal.y - y)
            if distance > vision_range:
                continue
            if nearest_distance is None or distance < nearest_distance:
                nearest = animal
                nearest_distance = distance
        return nearest

    def find_nearest_safe_area(
        self,
        x: int,
        y: int,
        vision_range: int,
    ) -> tuple[int, int] | None:
        if not self.legacy_oracle_perception_enabled:
            return None
        nearest = None
        nearest_distance = None
        min_x = max(0, x - vision_range)
        max_x = min(self.width - 1, x + vision_range)
        min_y = max(0, y - vision_range)
        max_y = min(self.height - 1, y + vision_range)
        for scan_y in range(min_y, max_y + 1):
            for scan_x in range(min_x, max_x + 1):
                if not self.is_safe_area(scan_x, scan_y):
                    continue
                distance = abs(scan_x - x) + abs(scan_y - y)
                if nearest_distance is None or distance < nearest_distance:
                    nearest = (scan_x, scan_y)
                    nearest_distance = distance
        return nearest

    def find_nest(self, owner_id: int) -> Nest | None:
        resolved_owner_id = self.resolve_nest_owner(owner_id)
        return self.nests.get(resolved_owner_id)

    def resolve_nest_owner(self, owner_id: int | None) -> int | None:
        if owner_id is None:
            return None
        resolved = owner_id
        visited: set[int] = set()
        while resolved in self.nest_owner_aliases and resolved not in visited:
            visited.add(resolved)
            resolved = self.nest_owner_aliases[resolved]
        return resolved

    def is_in_nest_radius(self, owner_id: int | None, x: int, y: int) -> bool:
        if owner_id is None:
            return False
        nest = self.find_nest(owner_id)
        if nest is None:
            return False
        return abs(nest.x - x) + abs(nest.y - y) <= nest.safe_radius

    def nearby_food_count(self, x: int, y: int, radius: int) -> int:
        return sum(
            1
            for food_x, food_y in self.food_positions
            if abs(food_x - x) + abs(food_y - y) <= radius
        )

    def find_nearby_active_nest_owner(
        self,
        x: int,
        y: int,
        radius: int,
        preferred_owner_ids: set[int] | None = None,
    ) -> int | None:
        nearest_owner_id: int | None = None
        nearest_distance: int | None = None
        preferred_owner_ids = preferred_owner_ids or set()
        for owner_id, nest in self.nests.items():
            if not self.is_nest_active(owner_id):
                continue
            distance = abs(nest.x - x) + abs(nest.y - y)
            if distance > radius:
                continue
            if nearest_distance is None or distance < nearest_distance:
                nearest_owner_id = owner_id
                nearest_distance = distance
                continue
            if (
                distance == nearest_distance
                and nearest_owner_id is not None
                and owner_id in preferred_owner_ids
                and nearest_owner_id not in preferred_owner_ids
            ):
                nearest_owner_id = owner_id
        return nearest_owner_id

    def consume_building_resources(self, x: int, y: int, radius: int, required: int) -> int:
        if not self.scaffolded_agent_actions_enabled or not self.legacy_scaffold_nest_enabled:
            return 0
        consumed = 0
        targets = [
            position
            for position, resource in self.food_positions.items()
            if resource.kind == FOOD_RAW_PLANT
            and abs(position[0] - x) + abs(position[1] - y) <= radius
        ]
        targets.sort(key=lambda position: abs(position[0] - x) + abs(position[1] - y))
        for position in targets[:required]:
            resource = self.food_positions.pop(position, None)
            if resource is None:
                continue
            if resource.plant_id is not None:
                self._harvest_plant(resource.plant_id)
            if resource.kind == FOOD_RAW_PLANT:
                self._drop_harvest_seed(position[0], position[1], resource)
            consumed += 1
        return consumed

    def build_nest(self, owner_id: int, x: int, y: int, safe_radius: int = 4) -> Nest | None:
        if not self.scaffolded_agent_actions_enabled or not self.legacy_scaffold_nest_enabled:
            return None
        if owner_id in self.nests:
            return None
        starter_leaf = 1 if self.surface_fuel_map[y][x] >= 0.04 else 0
        starter_wood = 1 if self.get_ground_material(x, y) in {MATERIAL_SOIL, MATERIAL_STONE} else 0
        nest = Nest(
            owner_id=owner_id,
            x=x,
            y=y,
            safe_radius=safe_radius,
            food_storage=18,
            material_storage={
                MATERIAL_LEAF: starter_leaf,
                MATERIAL_WOOD: starter_wood,
            },
            last_active_tick=self.tick_count,
        )
        self.nests[owner_id] = nest
        return nest

    def set_active_nest_owners(self, owner_ids: set[int]) -> None:
        self.active_nest_owner_ids = set(owner_ids)
        for owner_id in owner_ids:
            nest = self.nests.get(owner_id)
            if nest is not None:
                nest.last_active_tick = self.tick_count

    def is_nest_active(self, owner_id: int) -> bool:
        nest = self.nests.get(owner_id)
        if nest is None:
            return False
        if owner_id in self.active_nest_owner_ids:
            return True
        return (self.tick_count - nest.last_active_tick) <= self.nest_active_grace_ticks

    def transfer_nest(self, old_owner_id: int, new_owner_id: int) -> bool:
        resolved_old_owner_id = self.resolve_nest_owner(old_owner_id)
        resolved_new_owner_id = self.resolve_nest_owner(new_owner_id)
        if resolved_old_owner_id is None or resolved_new_owner_id is None:
            return False
        if resolved_old_owner_id == resolved_new_owner_id:
            self.nest_owner_aliases[old_owner_id] = resolved_new_owner_id
            return True

        old_nest = self.nests.get(resolved_old_owner_id)
        if old_nest is None:
            return False

        new_nest = self.nests.get(resolved_new_owner_id)
        if new_nest is not None:
            new_nest.food_storage += old_nest.food_storage
            new_nest.safe_radius = max(new_nest.safe_radius, old_nest.safe_radius)
            new_nest.last_active_tick = max(new_nest.last_active_tick, old_nest.last_active_tick)
            for material, amount in old_nest.material_storage.items():
                new_nest.material_storage[material] = new_nest.material_storage.get(material, 0) + amount
            new_nest.object_storage.extend(old_nest.object_storage)
            new_nest.protected_children.update(old_nest.protected_children)
            self.nests.pop(resolved_old_owner_id, None)
        else:
            self.nests.pop(resolved_old_owner_id, None)
            old_nest.owner_id = new_owner_id
            self.nests[new_owner_id] = old_nest

        self.nest_owner_aliases[old_owner_id] = new_owner_id
        self.nest_owner_aliases[resolved_old_owner_id] = new_owner_id
        return True

    def store_food_in_nest(self, owner_id: int, amount: int) -> int:
        nest = self.find_nest(owner_id)
        if nest is None or amount <= 0:
            return 0
        nest.food_storage += amount
        return amount

    def withdraw_food_from_nest(self, owner_id: int, amount: int) -> int:
        nest = self.find_nest(owner_id)
        if nest is None or amount <= 0 or nest.food_storage <= 0:
            return 0
        withdrawn = min(amount, nest.food_storage)
        nest.food_storage -= withdrawn
        return withdrawn

    def get_nest_food_storage(self, owner_id: int) -> int:
        nest = self.find_nest(owner_id)
        if nest is None:
            return 0
        return nest.food_storage

    def get_nest_hearth_intensity(self, owner_id: int) -> float:
        nest = self.find_nest(owner_id)
        if nest is None:
            return 0.0
        return nest.hearth_intensity

    def tend_food_patch(self, owner_id: int, rng: Random) -> dict[str, object]:
        if not self.scaffolded_agent_actions_enabled or not self.legacy_scaffold_nest_enabled:
            return {"success": False, "reason": "scaffold_disabled"}
        nest = self.find_nest(owner_id)
        if nest is None:
            return {"success": False, "reason": "missing_nest"}
        if nest.material_storage.get(MATERIAL_SOIL, 0) + nest.material_storage.get(MATERIAL_ASH, 0) <= 0:
            return {"success": False, "reason": "missing_soil_or_ash"}

        candidates: list[tuple[int, int]] = []
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                x = max(0, min(self.width - 1, nest.x + dx))
                y = max(0, min(self.height - 1, nest.y + dy))
                if not self.is_safe_area(x, y):
                    continue
                if self.get_ground_material(x, y) not in {MATERIAL_SOIL, MATERIAL_SAND}:
                    continue
                candidates.append((x, y))
        if not candidates:
            return {"success": False, "reason": "no_patch_site"}

        candidates.sort(
            key=lambda item: (
                self.managed_food_map[item[1]][item[0]],
                -self.get_fertility(item[0], item[1]),
                abs(item[0] - nest.x) + abs(item[1] - nest.y),
            )
        )
        patch_x, patch_y = candidates[0]
        if nest.material_storage.get(MATERIAL_ASH, 0) > 0:
            nest.material_storage[MATERIAL_ASH] -= 1
        else:
            nest.material_storage[MATERIAL_SOIL] -= 1
        self.managed_food_map[patch_y][patch_x] = min(0.8, self.managed_food_map[patch_y][patch_x] + 0.14)
        self.physics_events.append(
            f"food_patch_tended -> nest={owner_id} x={patch_x} y={patch_y} boost={self.managed_food_map[patch_y][patch_x]:.2f}"
        )
        return {"success": True, "x": patch_x, "y": patch_y, "boost": round(self.managed_food_map[patch_y][patch_x], 3)}

    def register_protected_child(self, owner_id: int, child_id: int) -> None:
        nest = self.find_nest(owner_id)
        if nest is None:
            return
        nest.protected_children.add(child_id)

    def store_materials_in_nest(self, owner_id: int, materials: dict[str, int]) -> dict[str, int]:
        nest = self.find_nest(owner_id)
        if nest is None:
            return {}

        stored: dict[str, int] = {}
        for material, amount in materials.items():
            if amount <= 0:
                continue
            nest.material_storage[material] = nest.material_storage.get(material, 0) + amount
            stored[material] = amount
        return stored

    def get_nest_materials(self, owner_id: int) -> dict[str, int]:
        nest = self.find_nest(owner_id)
        if nest is None:
            return {}
        return dict(nest.material_storage)

    def maintain_nest_hearth(self, owner_id: int, cognition_score: float) -> dict[str, float | bool]:
        nest = self.find_nest(owner_id)
        if nest is None:
            return {"success": False, "reason": "missing_nest"}

        available_wood = nest.material_storage.get(MATERIAL_WOOD, 0)
        available_leaf = nest.material_storage.get(MATERIAL_LEAF, 0) + nest.material_storage.get(MATERIAL_FIBER, 0)
        local_oxygen = self.get_cell_oxygen(nest.x, nest.y)
        local_moisture = self.get_cell_moisture(nest.x, nest.y)
        if local_oxygen < IGNITION_OXYGEN_MIN:
            return {"success": False, "reason": "oxygen_too_low"}
        if available_wood <= 0 and available_leaf <= 0:
            return {"success": False, "reason": "missing_fuel"}

        ignition_readiness = cognition_score * max(0.2, 1.0 - (local_moisture * 0.65))
        if nest.hearth_intensity <= 0.05 and ignition_readiness < 2.8:
            return {"success": False, "reason": "low_ignition_skill"}

        consumed_leaf = 0
        consumed_wood = 0
        if nest.hearth_intensity <= 0.05:
            if available_leaf > 0:
                consumed_leaf = 1
                if nest.material_storage.get(MATERIAL_LEAF, 0) > 0:
                    nest.material_storage[MATERIAL_LEAF] -= 1
                else:
                    nest.material_storage[MATERIAL_FIBER] -= 1
            if available_wood > 0:
                consumed_wood = 1
                nest.material_storage[MATERIAL_WOOD] -= 1
            nest.hearth_intensity = min(1.0, 0.42 + (cognition_score * 0.04))
        else:
            if available_wood > 0 and nest.hearth_fuel < 1.4:
                consumed_wood = 1
                nest.material_storage[MATERIAL_WOOD] -= 1
                nest.hearth_intensity = min(1.0, nest.hearth_intensity + 0.18)
            elif available_leaf > 0 and nest.hearth_fuel < 1.1:
                consumed_leaf = 1
                if nest.material_storage.get(MATERIAL_LEAF, 0) > 0:
                    nest.material_storage[MATERIAL_LEAF] -= 1
                else:
                    nest.material_storage[MATERIAL_FIBER] -= 1
                nest.hearth_intensity = min(1.0, nest.hearth_intensity + 0.09)
            else:
                return {"success": False, "reason": "hearth_already_stable"}

        nest.hearth_fuel += (consumed_wood * 1.0) + (consumed_leaf * 0.45)
        self.physics_events.append(
            f"hearth_maintained -> nest={owner_id} x={nest.x} y={nest.y} "
            f"wood={consumed_wood} leaf={consumed_leaf} intensity={nest.hearth_intensity:.2f}"
        )
        return {
            "success": True,
            "wood_used": float(consumed_wood),
            "leaf_used": float(consumed_leaf),
            "intensity": round(nest.hearth_intensity, 3),
        }

    def get_nest_objects(self, owner_id: int) -> list[PhysicalObject]:
        nest = self.find_nest(owner_id)
        if nest is None:
            return []
        return [
            self.objects[object_id]
            for object_id in nest.object_storage
            if object_id in self.objects and self.objects[object_id].durability > 0
        ]

    def store_objects_in_nest(self, owner_id: int, object_ids: list[int]) -> list[int]:
        nest = self.find_nest(owner_id)
        if nest is None:
            return []
        stored: list[int] = []
        for object_id in object_ids:
            if object_id not in self.objects:
                continue
            if object_id not in nest.object_storage:
                nest.object_storage.append(object_id)
            stored.append(object_id)
        return stored

    def consume_nest_materials(self, owner_id: int, requirements: dict[str, int]) -> bool:
        nest = self.find_nest(owner_id)
        if nest is None:
            return False

        for material, amount in requirements.items():
            if nest.material_storage.get(material, 0) < amount:
                return False

        for material, amount in requirements.items():
            nest.material_storage[material] -= amount
        return True

    def create_experimental_object(
        self,
        materials: dict[str, int],
        rng: Random,
        creator_agent_id: int | None = None,
        creator_lineage_id: str | None = None,
    ) -> PhysicalObject:
        wood = materials.get(MATERIAL_WOOD, 0)
        stone = materials.get(MATERIAL_STONE, 0)
        fiber = materials.get(MATERIAL_FIBER, 0)
        leaf = materials.get(MATERIAL_LEAF, 0)
        soil = materials.get(MATERIAL_SOIL, 0)
        clay = materials.get(MATERIAL_CLAY, 0)
        sand = materials.get(MATERIAL_SAND, 0)
        ash = materials.get(MATERIAL_ASH, 0)
        iron = materials.get(MATERIAL_IRON, 0)
        mass = max(1, wood + (stone * 2) + fiber + leaf + soil + clay + sand + ash + (iron * 3))
        sharpness = max(0, (stone * 3) + sand + rng.randint(0, 2) - max(0, fiber - 1))
        hardness = max(1, (stone * 3) + wood + clay + (iron * 4) + rng.randint(0, 1))
        length = max(1, (wood * 2) + fiber + leaf + rng.randint(0, 1))
        flexibility = max(0, (fiber * 3) + leaf + wood + rng.randint(0, 1) - stone - iron - clay)
        durability = max(1, hardness + fiber + clay + max(0, wood - 1))
        portability = mass <= 7 and length <= 8
        dominant_material = max(
            materials.items(),
            key=lambda item: (item[1], item[0]),
        )[0]
        dominant_spec = MATERIAL_SPECS.get(dominant_material, MATERIAL_SPECS[MATERIAL_WOOD])
        initial_moisture = min(
            dominant_spec.moisture_capacity,
            (
                (wood * 0.12)
                + (leaf * 0.18)
                + (fiber * 0.15)
                + (soil * 0.25)
                + (clay * 0.35)
                + (sand * 0.05)
                + (ash * 0.04)
                + (stone * 0.03)
            )
            / max(1, mass),
        )
        volatile_fraction = min(1.0, ((wood + leaf + fiber) * 0.18) / max(1, mass))
        carbon_fraction = min(1.0, ((wood * 0.10) + (leaf * 0.06)) / max(1, mass))

        physical_object = PhysicalObject(
            object_id=self.next_object_id,
            creator_agent_id=creator_agent_id,
            creator_lineage_id=creator_lineage_id,
            component_mix=dict(materials),
            mass=mass,
            sharpness=sharpness,
            hardness=hardness,
            length=length,
            flexibility=flexibility,
            durability=durability,
            portability=portability,
            dominant_material=dominant_material,
            moisture_ratio=initial_moisture,
            volatile_fraction=volatile_fraction,
            carbon_fraction=carbon_fraction,
        )
        self.objects[self.next_object_id] = physical_object
        self.next_object_id += 1
        return physical_object

    def get_object(self, object_id: int) -> PhysicalObject | None:
        return self.objects.get(object_id)

    def score_object_for_action(
        self,
        physical_object: PhysicalObject,
        action: str,
        context: str,
    ) -> float:
        if physical_object.durability <= 0:
            return 0.0

        base_score = 0.0
        if action == "cut":
            base_score = (
                (physical_object.sharpness * 1.4)
                + (physical_object.hardness * 0.4)
                + (1.5 if physical_object.portability else 0.0)
            )
        elif action == "pierce":
            base_score = (
                (physical_object.sharpness * 1.1)
                + (physical_object.length * 0.9)
                + (physical_object.hardness * 0.7)
            )
        elif action == "hit":
            base_score = (
                (physical_object.mass * 0.8)
                + (physical_object.hardness * 0.8)
                + (physical_object.length * 0.3)
            )
        elif action == "throw":
            base_score = (
                (physical_object.length * 0.5)
                + (physical_object.hardness * 0.4)
                + (2.0 if physical_object.portability else -1.5)
                - (physical_object.mass * 0.2)
            )
        elif action == "dig":
            base_score = (
                (physical_object.hardness * 0.8)
                + (physical_object.mass * 0.6)
                + (physical_object.sharpness * 0.3)
            )

        context_modifier = 1.0
        if context == "plant":
            context_modifier = 1.1 if action in {"cut", "hit"} else 0.7
        elif context == "prey":
            context_modifier = 1.2 if action in {"pierce", "throw", "hit"} else 0.8
        elif context == "defense":
            context_modifier = 1.0 if action in {"pierce", "hit"} else 0.75
        elif context == "soil":
            context_modifier = 1.0 if action == "dig" else 0.6

        return round(max(0.0, base_score * context_modifier), 3)

    def best_object_for_action(
        self,
        owner_id: int,
        action: str,
        context: str,
    ) -> PhysicalObject | None:
        best_object: PhysicalObject | None = None
        best_score = 0.0
        for physical_object in self.get_nest_objects(owner_id):
            score = self.score_object_for_action(physical_object, action, context)
            if score > best_score:
                best_object = physical_object
                best_score = score
        return best_object

    def record_object_use(
        self,
        object_id: int,
        agent_id: int,
        outcome_score: float,
        action: str,
        context: str,
    ) -> PhysicalObject | None:
        physical_object = self.objects.get(object_id)
        if physical_object is None:
            return None
        physical_object.use_count += 1
        physical_object.total_outcome_score += outcome_score
        key = f"{action}:{context}"
        physical_object.contexts[key] = physical_object.contexts.get(key, 0) + 1
        if agent_id != physical_object.creator_agent_id:
            physical_object.copied_by_agents.add(agent_id)
        physical_object.user_ids.add(agent_id)
        physical_object.durability = max(0, physical_object.durability - 1)
        return physical_object

    def forage_materials(self, x: int, y: int, rng: Random, cognition_score: float) -> dict[str, int]:
        profile = self.get_zone_profile(x, y)
        bonus = cognition_score * 0.025
        gathered: dict[str, int] = {}
        ground_material = self.get_ground_material(x, y)

        if self.is_safe_area(x, y):
            if rng.random() < 0.32 + bonus:
                gathered[MATERIAL_FIBER] = gathered.get(MATERIAL_FIBER, 0) + 1
            if rng.random() < 0.26 + bonus:
                gathered[MATERIAL_LEAF] = gathered.get(MATERIAL_LEAF, 0) + 1
            if rng.random() < 0.22 + bonus:
                gathered[MATERIAL_WOOD] = gathered.get(MATERIAL_WOOD, 0) + 1
            stone_chance = self.safe_area_stone_chance
            if self.is_frontier_area(x, y):
                stone_chance += self.frontier_stone_bonus
            if rng.random() < max(0.0, stone_chance + (bonus * 0.35)):
                gathered[MATERIAL_STONE] = gathered.get(MATERIAL_STONE, 0) + 1
        else:
            if rng.random() < 0.30 + bonus:
                gathered[MATERIAL_STONE] = gathered.get(MATERIAL_STONE, 0) + 1
            if rng.random() < 0.18 + bonus:
                gathered[MATERIAL_WOOD] = gathered.get(MATERIAL_WOOD, 0) + 1
            if rng.random() < 0.14 + bonus:
                gathered[MATERIAL_LEAF] = gathered.get(MATERIAL_LEAF, 0) + 1
            if profile["food_density"] >= 0.6 and rng.random() < 0.20 + bonus:
                gathered[MATERIAL_FIBER] = gathered.get(MATERIAL_FIBER, 0) + 1
        if ground_material == MATERIAL_SAND and rng.random() < 0.20 + (bonus * 0.3):
            gathered[MATERIAL_SAND] = gathered.get(MATERIAL_SAND, 0) + 1
        elif ground_material == MATERIAL_SOIL and rng.random() < 0.22 + (bonus * 0.3):
            gathered[MATERIAL_SOIL] = gathered.get(MATERIAL_SOIL, 0) + 1
            if self.get_cell_moisture(x, y) >= 0.42 and rng.random() < 0.18 + (bonus * 0.25):
                gathered[MATERIAL_CLAY] = gathered.get(MATERIAL_CLAY, 0) + 1

        return gathered

    def attempt_hunt(self, animal_id: int, hunters: list[object], rng: Random) -> dict[str, object]:
        animal = self.large_animals.get(animal_id)
        if animal is None:
            return {"success": False, "reason": "animal_missing"}

        herd_members = self._get_herd_members(animal.herd_id)
        guard_count = sum(1 for member in herd_members if member.role == "guard")
        calf_count = sum(1 for member in herd_members if member.stage == "calf")
        group_power = sum(
            getattr(member.body, "speed")
            + (member.durability / 10)
            + member.body.cognition_score
            + (member.body.cooperation_drive * 1.5)
            + (member.body.aggression * 0.8)
            + getattr(member, "get_hunt_power_bonus", lambda _env: 0)(self)
            for member in hunters
        )
        effective_defense = animal.defense + (guard_count * 1.8) + (calf_count * 0.6)
        if group_power < effective_defense:
            self._scatter_herd(animal.herd_id, hunters, rng)
            return {
                "success": False,
                "reason": "group_power_too_low",
                "group_power": round(group_power, 2),
                "animal_defense": round(effective_defense, 2),
                "herd_id": animal.herd_id,
            }

        coordination_bonus = sum(member.body.cognition_score for member in hunters) * 0.06
        social_bonus = sum(member.body.cooperation_drive for member in hunters) * 0.07
        pursuit_bonus = sum(member.body.speed for member in hunters) * 0.04
        armor_bonus = sum(member.body.armor_units for member in hunters) * 0.03
        target_distance = min(
            abs(member.x - animal.x) + abs(member.y - animal.y)
            for member in hunters
        )
        herd_awareness = animal.awareness + (0.25 * len(herd_members))
        success_rate = min(
            0.95,
            0.30
            + coordination_bonus
            + social_bonus
            + pursuit_bonus
            + armor_bonus
            + max(0, 0.12 - (target_distance * 0.03))
            - (herd_awareness * 0.03),
        )
        if rng.random() > success_rate:
            self._scatter_herd(animal.herd_id, hunters, rng)
            return {
                "success": False,
                "reason": "hunt_failed",
                "group_power": round(group_power, 2),
                "animal_defense": round(effective_defense, 2),
                "herd_id": animal.herd_id,
            }

        self.large_animals.pop(animal_id, None)
        self._scatter_herd(animal.herd_id, hunters, rng)
        return {
            "success": True,
            "reason": "hunt_success",
            "group_power": round(group_power, 2),
            "animal_defense": round(effective_defense, 2),
            "raw_meat_energy": animal.energy,
            "animal_id": animal.animal_id,
            "position": (animal.x, animal.y),
            "herd_id": animal.herd_id,
            "guard_count": guard_count,
            "calf_count": calf_count,
        }

    def _update_world_physics(self, rng: Random) -> None:
        seasonal_delta = {
            SEASON_SPRING: 4.0,
            SEASON_SUMMER: 10.0,
            SEASON_AUTUMN: 1.5,
            SEASON_WINTER: -7.0,
        }[self.season]
        diurnal_delta = -3.5 if self.is_night else 2.0

        for y in range(self.height):
            for x in range(self.width):
                biome = self.get_biome(x, y)
                ground = self.ground_material_map[y][x]
                base_k = AMBIENT_TEMPERATURE_K + seasonal_delta + diurnal_delta
                if biome == ZONE_DANGER_HIGH_FOOD:
                    base_k += 3.0
                elif biome == ZONE_DANGER_LOW_FOOD:
                    base_k += 1.0
                target_k = base_k - (self.moisture_map[y][x] * 7.0)
                self.temperature_map[y][x] += (target_k - self.temperature_map[y][x]) * 0.14

                oxygen_target = 0.205 if self.is_night else 0.21
                if ground == MATERIAL_WATER:
                    oxygen_target -= 0.03
                self.oxygen_map[y][x] += (oxygen_target - self.oxygen_map[y][x]) * 0.09
                self.oxygen_map[y][x] = min(0.21, max(0.05, self.oxygen_map[y][x]))

                moisture_target = self._target_cell_moisture(x, y, biome, ground)
                self.moisture_map[y][x] += (moisture_target - self.moisture_map[y][x]) * 0.05
                self.moisture_map[y][x] = min(1.0, max(0.02, self.moisture_map[y][x]))

                if self.surface_fuel_map[y][x] > 0 and rng.random() < 0.015:
                    self.surface_fuel_map[y][x] = max(0.0, self.surface_fuel_map[y][x] - 0.02)

    def _update_nest_hearths(self, rng: Random) -> None:
        for nest in self.nests.values():
            local_temp = self.temperature_map[nest.y][nest.x]
            local_oxygen = self.oxygen_map[nest.y][nest.x]
            local_moisture = self.moisture_map[nest.y][nest.x]
            if nest.hearth_fuel <= 0.01 or nest.hearth_intensity <= 0.01:
                nest.hearth_intensity = 0.0
                nest.hearth_fuel = max(0.0, nest.hearth_fuel - 0.02)
                nest.hearth_temperature_k = local_temp
                continue

            oxygen_factor = max(0.0, min(1.0, (local_oxygen - 0.08) / 0.13))
            moisture_penalty = max(0.15, 1.0 - (local_moisture * WATER_HEAT_DAMPING))
            burn_rate = 0.03 * nest.hearth_intensity * oxygen_factor * moisture_penalty
            nest.hearth_fuel = max(0.0, nest.hearth_fuel - burn_rate)
            ash_generated = burn_rate * (0.15 + (nest.hearth_smoke * 0.1))
            if ash_generated > 0.002:
                nest.material_storage[MATERIAL_ASH] = nest.material_storage.get(MATERIAL_ASH, 0) + max(1, int(ash_generated * 10))
            if nest.hearth_fuel <= 0.02:
                nest.hearth_intensity *= 0.55
            else:
                nest.hearth_intensity = max(0.0, min(1.0, nest.hearth_intensity * (0.97 + (oxygen_factor * 0.03))))

            local_heat_gain = 220.0 * nest.hearth_intensity * oxygen_factor
            nest.hearth_temperature_k = max(local_temp, 420.0 + local_heat_gain)
            self.temperature_map[nest.y][nest.x] = max(self.temperature_map[nest.y][nest.x], nest.hearth_temperature_k)
            self.oxygen_map[nest.y][nest.x] = max(0.05, self.oxygen_map[nest.y][nest.x] - (0.015 * nest.hearth_intensity))
            nest.hearth_smoke = max(0.0, min(1.0, (1.0 - oxygen_factor) + (local_moisture * 0.4)))

            if nest.hearth_intensity > 0.08 and rng.random() < 0.04:
                self.physics_events.append(
                    f"hearth_state -> nest={nest.owner_id} temp_k={nest.hearth_temperature_k:.1f} "
                    f"fuel={nest.hearth_fuel:.2f} oxygen={self.oxygen_map[nest.y][nest.x]:.2f} smoke={nest.hearth_smoke:.2f}"
                )

    def _update_object_physics(self) -> None:
        emitted_events: set[tuple[int, str]] = set()
        for nest in self.nests.values():
            if not nest.object_storage:
                continue
            local_temp = max(self.temperature_map[nest.y][nest.x], nest.hearth_temperature_k)
            local_oxygen = min(0.21, self.oxygen_map[nest.y][nest.x] + 0.01)
            local_moisture = self.moisture_map[nest.y][nest.x]
            for object_id in list(nest.object_storage):
                physical_object = self.objects.get(object_id)
                if physical_object is None:
                    continue
                self._apply_object_thermal_physics(
                    physical_object,
                    local_temp,
                    local_oxygen,
                    local_moisture,
                    emitted_events,
                )

    def _apply_object_thermal_physics(
        self,
        physical_object: PhysicalObject,
        local_temp_k: float,
        local_oxygen: float,
        local_moisture: float,
        emitted_events: set[tuple[int, str]],
    ) -> None:
        dominant_spec = MATERIAL_SPECS.get(physical_object.dominant_material, MATERIAL_SPECS[MATERIAL_WOOD])
        previous_temperature = physical_object.temperature_k
        thermal_response = min(0.28, 0.08 + (dominant_spec.thermal_conductivity_w_mk / 20.0))
        physical_object.temperature_k += (local_temp_k - physical_object.temperature_k) * thermal_response
        physical_object.oxygen_exposure = max(0.05, min(0.21, (physical_object.oxygen_exposure * 0.6) + (local_oxygen * 0.4)))
        thermal_delta = abs(physical_object.temperature_k - previous_temperature)

        if local_moisture > physical_object.moisture_ratio and physical_object.temperature_k < 340.0:
            uptake = min(
                dominant_spec.moisture_capacity - physical_object.moisture_ratio,
                0.01 * max(0.0, local_moisture - physical_object.moisture_ratio),
            )
            physical_object.moisture_ratio = min(dominant_spec.moisture_capacity, physical_object.moisture_ratio + uptake)
            if physical_object.moisture_ratio >= 0.45 and physical_object.state_label == "raw":
                physical_object.state_label = "waterlogged"

        if physical_object.moisture_ratio > 0 and physical_object.temperature_k > 373.15:
            evaporation = 0.01 * ((physical_object.temperature_k - 373.15) / 120.0) * max(0.2, 1.0 - local_moisture)
            physical_object.moisture_ratio = max(0.0, physical_object.moisture_ratio - evaporation)
            if physical_object.moisture_ratio <= 0.08 and physical_object.state_label in {"raw", "waterlogged"}:
                if physical_object.dominant_material in {MATERIAL_WOOD, MATERIAL_LEAF, MATERIAL_FIBER}:
                    physical_object.state_label = "dried"
                elif physical_object.dominant_material in {MATERIAL_SOIL, MATERIAL_CLAY}:
                    physical_object.state_label = "sun_dried"
        physical_object.thermal_dose += max(0.0, physical_object.temperature_k - AMBIENT_TEMPERATURE_K)

        pyrolysis_point = dominant_spec.pyrolysis_point_k
        ignition_point = dominant_spec.ignition_point_k
        if pyrolysis_point is not None and physical_object.temperature_k >= pyrolysis_point:
            pyrolysis_factor = max(0.0, min(1.0, (physical_object.temperature_k - pyrolysis_point) / 240.0))
            low_oxygen_factor = max(0.0, min(1.0, (0.18 - physical_object.oxygen_exposure) / 0.10))
            char_gain = dominant_spec.char_yield * 0.05 * (0.35 + pyrolysis_factor + low_oxygen_factor)
            physical_object.carbon_fraction = min(1.0, physical_object.carbon_fraction + char_gain)
            physical_object.blackness = min(1.0, physical_object.blackness + (0.04 + (char_gain * 0.8)))
            if physical_object.blackness >= 0.22:
                physical_object.state_label = "blackened"
            if physical_object.blackness >= 0.5:
                physical_object.state_label = "charred"
                physical_object.hardness = min(12, physical_object.hardness + 1)
                physical_object.flexibility = max(0, physical_object.flexibility - 1)

        if ignition_point is not None and physical_object.temperature_k >= ignition_point and physical_object.oxygen_exposure >= IGNITION_OXYGEN_MIN:
            volatile_burn = min(
                physical_object.volatile_fraction,
                0.04 * max(0.2, (physical_object.temperature_k - ignition_point) / 160.0) * (physical_object.oxygen_exposure / 0.21),
            )
            if volatile_burn > 0:
                physical_object.volatile_fraction = max(0.0, physical_object.volatile_fraction - volatile_burn)
                physical_object.ash_fraction = min(1.0, physical_object.ash_fraction + (volatile_burn * 0.7))
                physical_object.durability = max(0, physical_object.durability - max(1, int(math.ceil(volatile_burn * 6))))
                if physical_object.ash_fraction >= 0.25:
                    physical_object.state_label = "ashy"
                if physical_object.durability == 0:
                    physical_object.state_label = "burned_out"

        if dominant_spec.softening_point_k is not None:
            physical_object.softened = physical_object.temperature_k >= dominant_spec.softening_point_k

        if physical_object.dominant_material in {MATERIAL_SOIL, MATERIAL_CLAY}:
            if (
                physical_object.temperature_k >= 620.0
                and physical_object.moisture_ratio <= 0.06
                and physical_object.thermal_dose >= 700.0
            ):
                physical_object.state_label = "fired_hard"
                physical_object.hardness = min(12, physical_object.hardness + 2)
                physical_object.durability = min(20, physical_object.durability + 2)
                physical_object.flexibility = max(0, physical_object.flexibility - 2)
            elif (
                physical_object.temperature_k >= 450.0
                and physical_object.moisture_ratio <= 0.12
                and physical_object.state_label in {"raw", "sun_dried", "waterlogged"}
            ):
                physical_object.state_label = "sun_dried"

        if physical_object.dominant_material == MATERIAL_STONE:
            if previous_temperature >= 430.0 and local_moisture >= 0.48 and thermal_delta >= 16.0:
                physical_object.state_label = "thermal_fractured"
                physical_object.sharpness = min(12, physical_object.sharpness + 2)
                physical_object.durability = max(0, physical_object.durability - 1)

        if physical_object.dominant_material == MATERIAL_SAND:
            if physical_object.moisture_ratio >= 0.10 and physical_object.temperature_k < 340.0:
                physical_object.state_label = "packed_grit"

        if physical_object.dominant_material == MATERIAL_ASH and physical_object.moisture_ratio >= 0.10:
            physical_object.state_label = "alkaline_slurry"

        state_key = (physical_object.object_id, physical_object.state_label)
        if (
            physical_object.state_label in {
                "waterlogged",
                "dried",
                "sun_dried",
                "blackened",
                "charred",
                "ashy",
                "burned_out",
                "fired_hard",
                "thermal_fractured",
                "packed_grit",
                "alkaline_slurry",
            }
            and physical_object.last_reported_state != physical_object.state_label
            and state_key not in emitted_events
        ):
            emitted_events.add(state_key)
            physical_object.last_reported_state = physical_object.state_label
            self.physics_events.append(
                f"material_shift -> object={physical_object.object_id} state={physical_object.state_label} "
                f"temp_k={physical_object.temperature_k:.1f} blackness={physical_object.blackness:.2f} "
                f"carbon={physical_object.carbon_fraction:.2f} ash={physical_object.ash_fraction:.2f}"
            )

    def _target_cell_moisture(self, x: int, y: int, biome: str, ground: str) -> float:
        target = 0.30 + (self.get_fertility(x, y) * 0.35)
        if biome == ZONE_SAFE_HIGH_FOOD:
            target += 0.12
        elif biome == ZONE_DANGER_LOW_FOOD:
            target -= 0.10
        if ground == MATERIAL_WATER:
            target = 1.0
        elif ground == MATERIAL_SAND:
            target *= 0.55
        elif ground == MATERIAL_STONE:
            target *= 0.65
        if self.season == SEASON_SUMMER:
            target -= 0.08
        elif self.season == SEASON_WINTER:
            target += 0.06
        return min(1.0, max(0.02, target))

    def _generate_zone_map(self) -> list[list[str]]:
        zone_map: list[list[str]] = []
        for y in range(self.height):
            row: list[str] = []
            for x in range(self.width):
                row.append(self._zone_for_position(x, y))
            zone_map.append(row)
        return zone_map

    def _generate_fertility_map(self) -> list[list[float]]:
        return [
            [1.0 for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _generate_ground_material_map(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for y in range(self.height):
            row: list[str] = []
            for x in range(self.width):
                biome = self._zone_for_position(x, y)
                if biome == ZONE_SAFE_HIGH_FOOD:
                    material = MATERIAL_SOIL
                elif biome == ZONE_SAFE_LOW_FOOD:
                    material = MATERIAL_SOIL if (x + y) % 5 else MATERIAL_SAND
                elif biome == ZONE_DANGER_HIGH_FOOD:
                    material = MATERIAL_STONE if (x + y) % 4 == 0 else MATERIAL_SOIL
                else:
                    material = MATERIAL_SAND if (x + y) % 3 else MATERIAL_STONE
                if x in {0, self.width - 1} or y in {0, self.height - 1}:
                    material = MATERIAL_WATER
                row.append(material)
            rows.append(row)
        return rows

    def _generate_moisture_map(self) -> list[list[float]]:
        rows: list[list[float]] = []
        for y in range(self.height):
            row: list[float] = []
            for x in range(self.width):
                ground = self.ground_material_map[y][x]
                biome = self._zone_for_position(x, y)
                row.append(self._target_cell_moisture(x, y, biome, ground))
            rows.append(row)
        return rows

    def _generate_temperature_map(self) -> list[list[float]]:
        return [
            [AMBIENT_TEMPERATURE_K for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _generate_oxygen_map(self) -> list[list[float]]:
        rows: list[list[float]] = []
        for y in range(self.height):
            row: list[float] = []
            for x in range(self.width):
                row.append(0.18 if self.ground_material_map[y][x] == MATERIAL_WATER else 0.21)
            rows.append(row)
        return rows

    def _generate_photosynthetic_light_map(self) -> list[list[float]]:
        rows: list[list[float]] = []
        for y in range(self.height):
            row: list[float] = []
            for x in range(self.width):
                ground_spec = MATERIAL_SPECS[self.ground_material_map[y][x]]
                row.append(max(0.0, min(1.0, 1.0 - ground_spec.solar_absorptance)))
            rows.append(row)
        return rows

    def _generate_soil_nutrient_map(self, nutrient: str) -> list[list[float]]:
        offsets = {
            "nitrogen": 0.08,
            "phosphorus": -0.02,
            "potassium": 0.03,
        }
        offset = offsets.get(nutrient, 0.0)
        rows: list[list[float]] = []
        for y in range(self.height):
            row: list[float] = []
            for x in range(self.width):
                ground = self.ground_material_map[y][x]
                biome = self._zone_for_position(x, y)
                if ground == MATERIAL_WATER:
                    base = 0.02
                elif ground == MATERIAL_SOIL:
                    base = 0.56
                elif ground == MATERIAL_CLAY:
                    base = 0.48
                elif ground == MATERIAL_SAND:
                    base = 0.18
                else:
                    base = 0.08
                if biome in {ZONE_SAFE_HIGH_FOOD, ZONE_DANGER_HIGH_FOOD}:
                    base += 0.22
                if biome == ZONE_DANGER_LOW_FOOD:
                    base -= 0.08
                row.append(max(0.0, min(1.0, base + offset)))
            rows.append(row)
        return rows

    def _generate_surface_fuel_map(self) -> list[list[float]]:
        rows: list[list[float]] = []
        for y in range(self.height):
            row: list[float] = []
            for x in range(self.width):
                biome = self._zone_for_position(x, y)
                base = 0.12 if biome in {ZONE_SAFE_HIGH_FOOD, ZONE_DANGER_HIGH_FOOD} else 0.05
                if self.ground_material_map[y][x] == MATERIAL_WATER:
                    base = 0.0
                row.append(base)
            rows.append(row)
        return rows

    @property
    def food_pressure_multiplier(self) -> float:
        elapsed_days = self.tick_count / max(1, self.day_length)
        return max(
            self.minimum_global_food_multiplier,
            1.0 - (elapsed_days * self.global_food_decline_per_day),
        )

    def get_fertility(self, x: int, y: int) -> float:
        return self.fertility_map[y][x]

    def _recover_fertility(self) -> None:
        if self.fertility_recovery_rate <= 0:
            return
        for row_index, row in enumerate(self.fertility_map):
            for col_index, value in enumerate(row):
                if value >= 1.0:
                    continue
                row[col_index] = min(1.0, value + self.fertility_recovery_rate)

    def _decay_managed_food(self) -> None:
        for y, row in enumerate(self.managed_food_map):
            for x, value in enumerate(row):
                if value <= 0.0:
                    continue
                decay = 0.004 if self.is_safe_area(x, y) else 0.006
                row[x] = max(0.0, value - decay)

    def _decay_soil_disturbance(self) -> None:
        for y, row in enumerate(self.soil_disturbance_map):
            for x, value in enumerate(row):
                if value <= 0.0:
                    continue
                row[x] = max(0.0, value - 0.035)

    def _decay_food_resources(self, rng: Random) -> None:
        if not self.food_positions:
            return
        for (x, y), resource in list(self.food_positions.items()):
            age_ticks = max(0, self.tick_count - resource.created_tick)
            if resource.source in {"ambient_spawn", "wild_plant"}:
                base_decay = self.ambient_food_decay_chance
            else:
                base_decay = self.plant_food_decay_chance
            age_decay = min(0.018, age_ticks / max(1, self.day_length * 900))
            if rng.random() > base_decay + age_decay:
                continue
            self.food_positions.pop((x, y), None)
            if resource.source == "plant_lifecycle":
                self.physics_events.append(
                    f"plant_lifecycle_food_decayed -> plant={resource.plant_id if resource.plant_id is not None else -1} "
                    f"x={x} y={y} energy={resource.energy} age_ticks={age_ticks}"
                )
            else:
                self.physics_events.append(
                    f"food_decayed -> source={resource.source} x={x} y={y} energy={resource.energy} age_ticks={age_ticks}"
                )
            self.surface_fuel_map[y][x] = min(1.0, self.surface_fuel_map[y][x] + 0.01)
            self.fertility_map[y][x] = min(1.0, self.fertility_map[y][x] + 0.004)

    def _deplete_fertility(self, x: int, y: int, amount: float) -> None:
        current = self.fertility_map[y][x]
        self.fertility_map[y][x] = max(self.minimum_fertility, current - amount)

    def _solar_input(self) -> float:
        if self.is_night:
            return 0.0
        seasonal_multiplier = {
            SEASON_SPRING: 0.86,
            SEASON_SUMMER: 1.00,
            SEASON_AUTUMN: 0.72,
            SEASON_WINTER: 0.46,
        }[self.season]
        return seasonal_multiplier

    def _update_radiation_fields(self) -> None:
        solar_energy = self._solar_input()
        biomass_by_cell: dict[tuple[int, int], float] = {}
        for plant in self.plant_seeds.values():
            if plant.state in {"sprout", "mature"} and plant.biomass > 0.0:
                biomass_by_cell[(plant.x, plant.y)] = biomass_by_cell.get((plant.x, plant.y), 0.0) + plant.biomass

        leaf_spec = MATERIAL_SPECS[MATERIAL_LEAF]
        for y in range(self.height):
            for x in range(self.width):
                ground_spec = MATERIAL_SPECS[self.ground_material_map[y][x]]
                surface_organic_cover = min(1.0, self.surface_fuel_map[y][x] * 2.5)
                surface_transmittance = (
                    (1.0 - surface_organic_cover)
                    + (surface_organic_cover * leaf_spec.photosynthetic_transmittance)
                )
                plant_biomass = biomass_by_cell.get((x, y), 0.0)
                plant_surface_area = min(1.0, plant_biomass * 0.55)
                plant_transmittance = (
                    (1.0 - plant_surface_area)
                    + (plant_surface_area * leaf_spec.photosynthetic_transmittance)
                )
                reflected = ground_spec.solar_reflectance * 0.18
                absorbed_by_ground_surface = ground_spec.solar_absorptance * 0.10
                photosynthetic_band = solar_energy * surface_transmittance * plant_transmittance
                self.photosynthetic_light_map[y][x] = max(
                    0.0,
                    min(1.0, photosynthetic_band * (1.0 - reflected - absorbed_by_ground_surface)),
                )

    def _natural_seed_rain(self, rng: Random) -> None:
        if not self.plant_lifecycle_enabled or self.natural_seed_rain_per_tick <= 0:
            return
        if len(self.plant_seeds) >= self.max_plant_seeds:
            return

        for _ in range(self.natural_seed_rain_per_tick):
            if len(self.plant_seeds) >= self.max_plant_seeds:
                return
            x = rng.randrange(self.width)
            y = rng.randrange(self.height)
            if self.ground_material_map[y][x] == MATERIAL_WATER:
                continue
            local_nutrients = self.get_cell_soil_nutrients(x, y)
            profile = self.get_zone_profile(x, y)
            establishment_chance = profile["food_density"] * self.get_fertility(x, y) * local_nutrients
            if rng.random() > establishment_chance:
                continue
            self._deposit_seed(
                species="wild_grain",
                x=x,
                y=y,
                burial_depth_cm=rng.uniform(0.1, 5.2),
                dispersal_mode="natural_seed_rain",
            )

    def _deposit_seed(
        self,
        *,
        species: str,
        x: int,
        y: int,
        burial_depth_cm: float,
        dispersal_mode: str,
        parent_plant_id: int | None = None,
        dropped_by_agent_id: int | None = None,
    ) -> PlantSeed:
        plant = PlantSeed(
            seed_id=self.next_seed_id,
            species=species,
            x=x,
            y=y,
            burial_depth_cm=burial_depth_cm,
            parent_plant_id=parent_plant_id,
            dispersal_mode=dispersal_mode,
            dropped_by_agent_id=dropped_by_agent_id,
            created_tick=self.tick_count,
        )
        self.plant_seeds[plant.seed_id] = plant
        self.next_seed_id += 1
        return plant

    def _drop_harvest_seed(self, x: int, y: int, resource: FoodResource) -> PlantSeed | None:
        if not self.plant_lifecycle_enabled:
            return None
        if len(self.plant_seeds) >= self.max_plant_seeds:
            return None
        if self.ground_material_map[y][x] == MATERIAL_WATER:
            return None
        seed = self._deposit_seed(
            species="wild_grain",
            x=x,
            y=y,
            burial_depth_cm=0.0,
            dispersal_mode="harvest_drop",
            parent_plant_id=resource.plant_id,
        )
        self.physics_events.append(
            f"harvest_seed_dropped -> seed={seed.seed_id} x={x} y={y} source={resource.source} "
            f"parent={resource.plant_id if resource.plant_id is not None else -1} mode={seed.dispersal_mode}"
        )
        return seed

    def _route_seed_to_gut(self, seed: PlantSeed, eater) -> None:
        """v2 endozoochory: move a just-harvested seed into the eater's gut.

        The seed leaves the open world (carried_by_agent_id set, so the plant
        lifecycle skips germination) and travels with the agent until excreted
        at a later position by Agent._process_gut.

        v2 (Fix 3): the gut holds at most gut_capacity seeds. When full the seed
        is NOT ingested; it stays on the ground as a normal harvest_drop (already
        deposited by _drop_harvest_seed before routing), so a full gut becomes a
        surface drop rather than vanishing.
        """
        if len(eater.gut_seeds) >= int(eater.body.gut_capacity):
            return
        seed.carried_by_agent_id = eater.agent_id
        seed.dropped_by_agent_id = eater.agent_id
        seed.dispersal_mode = "gut_transit"
        eater.gut_seeds.append((seed.seed_id, self.tick_count))
        self.physics_events.append(
            f"gut_seed_ingested -> agent={eater.agent_id} seed={seed.seed_id} "
            f"x={seed.x} y={seed.y} tick={self.tick_count}"
        )

    def excrete_gut_seed(self, seed_id: int, agent_id: int, x: int, y: int, acid_strength: float) -> bool:
        """v2 endozoochory: deposit a gut-carried seed at the agent's current
        position. Returns True if a live (dispersed) seed was deposited.

        If the body's acid cracks the seed coat (acid_strength >= the species'
        shell_hardness) the seed is killed (viability 0); otherwise it survives,
        with a small scarification boost to germination speed.
        """
        plant = self.plant_seeds.get(seed_id)
        if plant is None:
            return False
        if not self.is_walkable(x, y):
            return False
        spec = PLANT_SPECIES[plant.species]
        shell = spec.shell_hardness
        plant.carried_by_agent_id = None
        plant.x = x
        plant.y = y
        plant.burial_depth_cm = 0.0
        plant.dispersal_mode = "gut_passed"
        if acid_strength >= shell:
            plant.viability = 0.0
            self.physics_events.append(
                f"gut_seed_killed -> agent={agent_id} seed={seed_id} x={x} y={y} "
                f"acid={acid_strength:.2f} shell={shell:.2f}"
            )
            return False
        good_ticks = max(1, int(round(spec.germination_good_ticks * self.germination_good_ticks_multiplier)))
        plant.accumulated_good_ticks += int(round(acid_strength * good_ticks * 0.5))
        self.physics_events.append(
            f"gut_seed_excreted -> agent={agent_id} seed={seed_id} x={x} y={y} "
            f"acid={acid_strength:.2f} shell={shell:.2f} scarified=1"
        )
        return True

    def _update_plant_lifecycle(self, rng: Random) -> None:
        if not self.plant_lifecycle_enabled:
            return

        dead_plant_ids: list[int] = []
        for plant in list(self.plant_seeds.values()):
            spec = PLANT_SPECIES[plant.species]
            max_age_ticks = max(1, int(round(spec.max_age_ticks * self.plant_seed_max_age_multiplier)))
            germination_good_ticks = max(
                1,
                int(round(spec.germination_good_ticks * self.germination_good_ticks_multiplier)),
            )
            plant.age_ticks += 1
            if plant.carried_by_agent_id is not None:
                plant.viability -= 0.0002
                if plant.viability <= 0.0 or plant.age_ticks > max_age_ticks:
                    dead_plant_ids.append(plant.seed_id)
                continue
            water = self.moisture_map[plant.y][plant.x]
            temperature_k = self.temperature_map[plant.y][plant.x]
            oxygen = self.oxygen_map[plant.y][plant.x]
            light = self.photosynthetic_light_map[plant.y][plant.x]
            nutrients = self.get_cell_soil_nutrients(plant.x, plant.y)
            growth_factor = 0.0

            if plant.state == "seed":
                self._settle_surface_seed(plant, spec, rng)
                if self._seed_germination_conditions_met(plant, spec, water, temperature_k, oxygen):
                    plant.accumulated_good_ticks += 1
                else:
                    plant.accumulated_good_ticks = max(0, plant.accumulated_good_ticks - 1)
                    plant.viability -= 0.0007

                if plant.accumulated_good_ticks >= germination_good_ticks:
                    plant.state = "sprout"
                    plant.biomass = 0.08
                    self._consume_soil_nutrients(plant.x, plant.y, 0.01)
                    self.physics_events.append(
                        f"seed_germinated -> seed={plant.seed_id} species={plant.species} x={plant.x} y={plant.y} "
                        f"water={water:.2f} temp_k={temperature_k:.1f} oxygen={oxygen:.2f} light={light:.2f} "
                        f"nutrients={nutrients:.2f} depth_cm={plant.burial_depth_cm:.1f}"
                    )
            elif plant.state in {"sprout", "mature"}:
                growth_factor = self._plant_growth_factor(spec, water, temperature_k, oxygen, light, nutrients)
                if growth_factor > 0.0:
                    growth = growth_factor * 0.035 * self.plant_growth_rate_multiplier
                    plant.biomass = min(spec.maturity_biomass * 2.8, plant.biomass + growth)
                    self._consume_soil_nutrients(plant.x, plant.y, growth * spec.nutrient_demand * 0.05)
                    self.surface_fuel_map[plant.y][plant.x] = min(
                        1.0,
                        self.surface_fuel_map[plant.y][plant.x] + (growth * 0.02),
                    )
                else:
                    plant.biomass = max(0.0, plant.biomass - (0.006 * self.sprout_biomass_loss_multiplier))
                    plant.viability -= 0.0015

                if plant.state == "sprout" and plant.biomass >= spec.maturity_biomass:
                    plant.state = "mature"
                    self.physics_events.append(
                        f"plant_matured -> seed={plant.seed_id} species={plant.species} x={plant.x} y={plant.y} "
                        f"biomass={plant.biomass:.2f} light={light:.2f} nutrients={nutrients:.2f}"
                    )

                if plant.state == "mature":
                    self._maybe_emit_plant_food(plant, spec, growth_factor, rng)
                    self._maybe_drop_natural_offspring_seeds(plant, spec, growth_factor, rng)

            death_reason = None
            if plant.viability <= 0.0:
                death_reason = "low_viability"
            elif plant.age_ticks > max_age_ticks:
                death_reason = "max_age"
            elif plant.state in {"sprout", "mature"} and plant.biomass <= 0.0:
                death_reason = "no_biomass"
            if death_reason is not None:
                self.physics_events.append(
                    f"plant_died -> seed={plant.seed_id} species={plant.species} x={plant.x} y={plant.y} "
                    f"state={plant.state} age_ticks={plant.age_ticks} reason={death_reason} biomass={plant.biomass:.3f} "
                    f"water={water:.2f} temp_k={temperature_k:.1f} light={light:.2f} nutrients={nutrients:.2f} "
                    f"growth={growth_factor:.3f} "
                    f"mode={plant.dispersal_mode} parent={plant.parent_plant_id if plant.parent_plant_id is not None else -1}"
                )
                dead_plant_ids.append(plant.seed_id)

        for plant_id in dead_plant_ids:
            plant = self.plant_seeds.pop(plant_id, None)
            if plant is None:
                continue
            if plant.x >= 0 and plant.y >= 0:
                self.surface_fuel_map[plant.y][plant.x] = min(
                    1.0,
                    self.surface_fuel_map[plant.y][plant.x] + (plant.biomass * 0.08),
                )

    def _settle_surface_seed(self, plant: PlantSeed, spec: PlantSpeciesSpec, rng: Random) -> None:
        if plant.burial_depth_cm >= spec.burial_depth_max_cm:
            return
        ground = self.ground_material_map[plant.y][plant.x]
        if ground not in {MATERIAL_SOIL, MATERIAL_SAND, MATERIAL_CLAY}:
            return
        disturbance = self.soil_disturbance_map[plant.y][plant.x]
        if disturbance < 0.05:
            return
        previous_depth = plant.burial_depth_cm
        moisture = self.moisture_map[plant.y][plant.x]
        material_multiplier = {
            MATERIAL_SAND: 1.25,
            MATERIAL_SOIL: 1.0,
            MATERIAL_CLAY: 0.55,
        }.get(ground, 0.0)
        plant.burial_depth_cm = min(
            spec.burial_depth_max_cm,
            plant.burial_depth_cm + (disturbance * material_multiplier * (0.10 + moisture * 0.12)),
        )
        if previous_depth < spec.burial_depth_min_cm <= plant.burial_depth_cm:
            self.physics_events.append(
                f"seed_buried_by_disturbance -> seed={plant.seed_id} x={plant.x} y={plant.y} "
                f"depth_cm={plant.burial_depth_cm:.2f} disturbance={disturbance:.2f}"
            )

    def _seed_germination_conditions_met(
        self,
        plant: PlantSeed,
        spec: PlantSpeciesSpec,
        water: float,
        temperature_k: float,
        oxygen: float,
    ) -> bool:
        return (
            plant.viability > 0.0
            and spec.germination_water_min <= water <= spec.germination_water_max
            and spec.germination_temp_min_k <= temperature_k <= spec.germination_temp_max_k
            and oxygen >= spec.germination_oxygen_min
            and spec.burial_depth_min_cm <= plant.burial_depth_cm <= spec.burial_depth_max_cm
        )

    def _plant_growth_factor(
        self,
        spec: PlantSpeciesSpec,
        water: float,
        temperature_k: float,
        oxygen: float,
        light: float,
        nutrients: float,
    ) -> float:
        water_midpoint = (spec.germination_water_min + spec.germination_water_max) / 2.0
        water_span = max(0.01, (spec.germination_water_max - spec.germination_water_min) / 2.0)
        water_factor = max(0.0, 1.0 - (abs(water - water_midpoint) / water_span))
        temperature_midpoint = (spec.germination_temp_min_k + spec.germination_temp_max_k) / 2.0
        temperature_span = max(0.01, (spec.germination_temp_max_k - spec.germination_temp_min_k) / 2.0)
        temperature_factor = max(0.0, 1.0 - (abs(temperature_k - temperature_midpoint) / temperature_span))
        oxygen_factor = max(0.0, min(1.0, (oxygen - 0.08) / 0.13))
        light_factor = max(0.0, min(1.0, light / max(0.01, spec.light_saturation)))
        nutrient_factor = max(0.0, min(1.0, nutrients / max(0.01, spec.nutrient_demand)))
        return water_factor * temperature_factor * oxygen_factor * light_factor * nutrient_factor

    def _consume_soil_nutrients(self, x: int, y: int, amount: float) -> None:
        if amount <= 0.0:
            return
        self.soil_nitrogen_map[y][x] = max(0.0, self.soil_nitrogen_map[y][x] - amount)
        self.soil_phosphorus_map[y][x] = max(0.0, self.soil_phosphorus_map[y][x] - (amount * 0.55))
        self.soil_potassium_map[y][x] = max(0.0, self.soil_potassium_map[y][x] - (amount * 0.75))

    def _maybe_emit_plant_food(
        self,
        plant: PlantSeed,
        spec: PlantSpeciesSpec,
        growth_factor: float,
        rng: Random,
    ) -> None:
        if len(self.food_positions) >= self.max_food:
            return
        if (plant.x, plant.y) in self.food_positions:
            return
        fruiting_interval_ticks = max(
            1,
            int(round(spec.fruiting_interval_ticks * self.plant_fruiting_interval_multiplier)),
        )
        if self.tick_count - plant.last_food_tick < fruiting_interval_ticks:
            return
        if growth_factor < (0.18 * self.plant_fruiting_growth_threshold_multiplier):
            return
        seasonal_bonus = 1.25 if self.season in {SEASON_SPRING, SEASON_SUMMER} else 0.75
        fruiting_chance = min(0.90, growth_factor * seasonal_bonus * self.plant_fruiting_chance_multiplier)
        if rng.random() > fruiting_chance:
            return

        energy = FOOD_ENERGY[FOOD_RAW_PLANT] + int(min(8.0, plant.biomass * 3.0))
        self.food_positions[(plant.x, plant.y)] = FoodResource(
            kind=FOOD_RAW_PLANT,
            energy=energy,
            source="plant_lifecycle",
            plant_id=plant.seed_id,
            created_tick=self.tick_count,
        )
        self.food_spawned_by_kind[FOOD_RAW_PLANT] = self.food_spawned_by_kind.get(FOOD_RAW_PLANT, 0) + 1
        plant.last_food_tick = self.tick_count
        plant.biomass = max(spec.maturity_biomass * 0.72, plant.biomass - 0.18)
        self.physics_events.append(
            f"plant_fruited -> seed={plant.seed_id} species={plant.species} x={plant.x} y={plant.y} "
            f"energy={energy} biomass={plant.biomass:.2f} light={self.photosynthetic_light_map[plant.y][plant.x]:.2f}"
        )

    def _maybe_drop_natural_offspring_seeds(
        self,
        plant: PlantSeed,
        spec: PlantSpeciesSpec,
        growth_factor: float,
        rng: Random,
    ) -> None:
        if len(self.plant_seeds) >= self.max_plant_seeds:
            return
        if self.tick_count - plant.last_natural_seed_tick < spec.natural_seed_interval_ticks:
            return
        if growth_factor < 0.14:
            return
        natural_seed_drop_chance = spec.natural_seed_drop_chance * self.natural_seed_drop_chance_multiplier
        if rng.random() > min(0.95, natural_seed_drop_chance * (0.7 + growth_factor)):
            return

        dropped = 0
        attempts = max(4, spec.natural_seed_drop_max_count * 5)
        for _ in range(attempts):
            if dropped >= spec.natural_seed_drop_max_count or len(self.plant_seeds) >= self.max_plant_seeds:
                break
            dx = rng.randint(-spec.natural_seed_drop_radius, spec.natural_seed_drop_radius)
            dy = rng.randint(-spec.natural_seed_drop_radius, spec.natural_seed_drop_radius)
            if abs(dx) + abs(dy) > spec.natural_seed_drop_radius:
                continue
            seed_x = max(0, min(self.width - 1, plant.x + dx))
            seed_y = max(0, min(self.height - 1, plant.y + dy))
            if self.ground_material_map[seed_y][seed_x] == MATERIAL_WATER:
                continue
            if rng.random() > max(0.08, self.get_fertility(seed_x, seed_y) * self.get_cell_soil_nutrients(seed_x, seed_y)):
                continue
            burial_depth = rng.uniform(0.0, 0.8)
            seed = self._deposit_seed(
                species=plant.species,
                x=seed_x,
                y=seed_y,
                burial_depth_cm=burial_depth,
                dispersal_mode="natural_drop",
                parent_plant_id=plant.seed_id,
            )
            self.physics_events.append(
                f"natural_seed_dropped -> seed={seed.seed_id} parent={plant.seed_id} x={seed_x} y={seed_y} "
                f"mode=natural_drop depth_cm={burial_depth:.2f} distance={abs(dx) + abs(dy)}"
            )
            dropped += 1

        if dropped > 0:
            plant.last_natural_seed_tick = self.tick_count

    def _harvest_plant(self, plant_id: int) -> None:
        plant = self.plant_seeds.get(plant_id)
        if plant is None:
            return
        spec = PLANT_SPECIES[plant.species]
        plant.biomass = max(0.0, plant.biomass - 0.12)
        self.surface_fuel_map[plant.y][plant.x] = min(1.0, self.surface_fuel_map[plant.y][plant.x] + 0.01)
        if plant.biomass < spec.maturity_biomass * 0.35:
            plant.state = "sprout"

    def _zone_for_position(self, x: int, y: int) -> str:
        left_side = x < self.width // 2
        top_side = y < self.height // 2
        if left_side and top_side:
            return ZONE_SAFE_LOW_FOOD
        if not left_side and top_side:
            return ZONE_SAFE_HIGH_FOOD
        if left_side and not top_side:
            return ZONE_DANGER_HIGH_FOOD
        return ZONE_DANGER_LOW_FOOD

    def _spawn_food(self, rng: Random) -> None:
        if self.base_food_spawn_per_tick <= 0:
            return
        bootstrap_multiplier = (
            1.0
            if self.tick_count <= self.bootstrap_food_spawn_ticks
            else self.wild_food_spawn_after_bootstrap_multiplier
        )
        seasonal_rate = int(round(
            self.base_food_spawn_per_tick
            * SEASON_FOOD_MULTIPLIER[self.season]
            * self.food_spawn_multiplier
            * self.food_pressure_multiplier
            * bootstrap_multiplier
        ))
        spawn_attempts = max(0, seasonal_rate)
        for _ in range(spawn_attempts):
            if len(self.food_positions) >= self.max_food:
                return
            x = rng.randrange(self.width)
            y = rng.randrange(self.height)
            profile = self.get_zone_profile(x, y)
            if (x, y) in self.food_positions:
                continue
            spawn_chance = profile["food_density"] * self.get_fertility(x, y) * (1.0 + self.managed_food_map[y][x])
            if rng.random() <= spawn_chance:
                self.food_positions[(x, y)] = FoodResource(
                    kind=FOOD_RAW_PLANT,
                    energy=FOOD_ENERGY[FOOD_RAW_PLANT],
                    source="wild_plant",
                    created_tick=self.tick_count,
                )
                self.food_spawned_by_kind[FOOD_RAW_PLANT] = self.food_spawned_by_kind.get(FOOD_RAW_PLANT, 0) + 1
                self._deplete_fertility(x, y, self.fertility_spawn_cost)

    def _spawn_low_value_food(self, rng: Random) -> None:
        """Food-value-learning study: scatter edible low-value raw_seed food.

        Off by default (rate 0 returns before drawing any RNG, so existing worlds
        and v1 reproducibility are untouched). When on, agents must walk over the
        seed-food and decide whether to eat it; ingestion is size-only so they
        physically can. Decay (_decay_food_resources) bounds accumulation."""
        rate = self.low_value_food_spawn_per_tick
        if rate <= 0.0:
            return
        count = int(rate)
        if rng.random() < (rate - count):
            count += 1
        hard_cap = self.max_food * 3
        for _ in range(count):
            if len(self.food_positions) >= hard_cap:
                return
            x = rng.randrange(self.width)
            y = rng.randrange(self.height)
            if (x, y) in self.food_positions:
                continue
            if not self.is_walkable(x, y):
                continue
            self.food_positions[(x, y)] = FoodResource(
                kind=FOOD_RAW_SEED,
                energy=FOOD_ENERGY[FOOD_RAW_SEED],
                source="low_value_study",
                created_tick=self.tick_count,
            )
            self.food_spawned_by_kind[FOOD_RAW_SEED] = self.food_spawned_by_kind.get(FOOD_RAW_SEED, 0) + 1

    def _spawn_large_animals(self, rng: Random) -> None:
        for _ in range(self.large_animal_spawn_per_tick):
            if len(self.large_animals) >= self.max_large_animals:
                return
            x = rng.randrange(self.width)
            y = rng.randrange(self.height)
            if not self.is_walkable(x, y):
                continue
            profile = self.get_zone_profile(x, y)
            if profile["food_density"] < 0.6 or profile["danger"] < 0.4:
                continue

            herd_size = min(4, self.max_large_animals - len(self.large_animals))
            if herd_size < 2:
                return
            herd_id = self.next_herd_id
            self.next_herd_id += 1
            self._spawn_herd(herd_id, x, y, profile, herd_size, rng)

    def _spawn_herd(
        self,
        herd_id: int,
        center_x: int,
        center_y: int,
        profile: dict[str, float],
        herd_size: int,
        rng: Random,
    ) -> None:
        offsets = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        rng.shuffle(offsets)
        for index in range(herd_size):
            offset_x, offset_y = offsets[index]
            x = max(0, min(self.width - 1, center_x + offset_x))
            y = max(0, min(self.height - 1, center_y + offset_y))
            if not self.is_walkable(x, y):
                continue

            stage = "adult"
            role = "grazer"
            defense = 7 + (profile["danger"] * 6)
            energy = FOOD_ENERGY[FOOD_RAW_MEAT]
            speed = 2
            awareness = 3
            if index == 0:
                role = "guard"
                defense += 4
                energy = 24
            elif index == herd_size - 1:
                stage = "calf"
                role = "calf"
                defense -= 2
                energy = 12
                speed = 1
                awareness = 2

            self.large_animals[self.next_animal_id] = LargeAnimal(
                animal_id=self.next_animal_id,
                herd_id=herd_id,
                x=x,
                y=y,
                defense=defense,
                energy=energy,
                speed=speed,
                awareness=awareness,
                stage=stage,
                role=role,
            )
            self.next_animal_id += 1

    def _move_large_animals(self, rng: Random) -> None:
        if not self.large_animals:
            return

        herds: dict[int, list[LargeAnimal]] = {}
        for animal in self.large_animals.values():
            herds.setdefault(animal.herd_id, []).append(animal)

        for members in herds.values():
            center_x = round(sum(member.x for member in members) / len(members))
            center_y = round(sum(member.y for member in members) / len(members))
            for animal in members:
                predator_bias = self.get_danger_level(animal.x, animal.y)
                if predator_bias >= 0.45:
                    step = self._escape_step(animal, center_x, center_y, rng)
                elif animal.stage == "calf":
                    step = self._step_toward(animal, center_x, center_y, rng)
                elif animal.role == "guard":
                    step = self._guard_step(animal, center_x, center_y, rng)
                else:
                    step = self._graze_step(animal, center_x, center_y, rng)

                if step is None:
                    continue
                next_x = max(0, min(self.width - 1, animal.x + step[0]))
                next_y = max(0, min(self.height - 1, animal.y + step[1]))
                if self.is_walkable(next_x, next_y):
                    animal.x = next_x
                    animal.y = next_y

    def _escape_step(
        self,
        animal: LargeAnimal,
        center_x: int,
        center_y: int,
        rng: Random,
    ) -> tuple[int, int] | None:
        options = [
            (animal.x - center_x, animal.y - center_y),
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
        ]
        rng.shuffle(options)
        for dx, dy in options:
            step_x = 0 if dx == 0 else int(dx / abs(dx))
            step_y = 0 if dy == 0 else int(dy / abs(dy))
            if step_x == 0 and step_y == 0:
                continue
            return (step_x, step_y)
        return None

    def _step_toward(
        self,
        animal: LargeAnimal,
        target_x: int,
        target_y: int,
        rng: Random,
    ) -> tuple[int, int] | None:
        directions = [
            (1 if target_x > animal.x else -1 if target_x < animal.x else 0, 0),
            (0, 1 if target_y > animal.y else -1 if target_y < animal.y else 0),
        ]
        rng.shuffle(directions)
        for direction in directions:
            if direction != (0, 0):
                return direction
        return None

    def _guard_step(
        self,
        animal: LargeAnimal,
        center_x: int,
        center_y: int,
        rng: Random,
    ) -> tuple[int, int] | None:
        if abs(animal.x - center_x) + abs(animal.y - center_y) > 2:
            return self._step_toward(animal, center_x, center_y, rng)
        return self._graze_step(animal, center_x, center_y, rng)

    def _graze_step(
        self,
        animal: LargeAnimal,
        center_x: int,
        center_y: int,
        rng: Random,
    ) -> tuple[int, int] | None:
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
        rng.shuffle(directions)
        for dx, dy in directions:
            next_x = max(0, min(self.width - 1, animal.x + dx))
            next_y = max(0, min(self.height - 1, animal.y + dy))
            if abs(next_x - center_x) + abs(next_y - center_y) <= 3:
                return (dx, dy)
        return None

    def _scatter_herd(self, herd_id: int, hunters: list[object], rng: Random) -> None:
        members = self._get_herd_members(herd_id)
        if not members:
            return
        hunter_center_x = sum(member.x for member in hunters) / len(hunters)
        hunter_center_y = sum(member.y for member in hunters) / len(hunters)
        for animal in members:
            dx = animal.x - hunter_center_x
            dy = animal.y - hunter_center_y
            step_x = 0 if dx == 0 else int(dx / abs(dx))
            step_y = 0 if dy == 0 else int(dy / abs(dy))
            if step_x == 0 and step_y == 0:
                step_x, step_y = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            animal.x = max(0, min(self.width - 1, animal.x + step_x))
            animal.y = max(0, min(self.height - 1, animal.y + step_y))

    def _get_herd_members(self, herd_id: int) -> list[LargeAnimal]:
        return [
            animal
            for animal in self.large_animals.values()
            if animal.herd_id == herd_id
        ]

    def _support_nests(self, rng: Random) -> None:
        for nest in self.nests.values():
            if self.is_safe_area(nest.x, nest.y) and rng.random() < self.nest_support_food_chance:
                nest.food_storage += 1
            if rng.random() < 0.18:
                nest.material_storage[MATERIAL_LEAF] = nest.material_storage.get(MATERIAL_LEAF, 0) + 1
            if rng.random() < 0.10:
                nest.material_storage[MATERIAL_WOOD] = nest.material_storage.get(MATERIAL_WOOD, 0) + 1

            for _ in range(2):
                dx = rng.randrange(-2, 3)
                dy = rng.randrange(-2, 3)
                spawn_x = max(0, min(self.width - 1, nest.x + dx))
                spawn_y = max(0, min(self.height - 1, nest.y + dy))
                if (spawn_x, spawn_y) in self.food_positions:
                    continue
                if not self.is_safe_area(spawn_x, spawn_y):
                    continue
                if rng.random() < (self.nest_support_spawn_chance * self.get_fertility(spawn_x, spawn_y)):
                    self.food_positions[(spawn_x, spawn_y)] = FoodResource(
                        kind=FOOD_RAW_PLANT,
                        energy=FOOD_ENERGY[FOOD_RAW_PLANT],
                        source="nest_support",
                        created_tick=self.tick_count,
                    )
                    self._deplete_fertility(spawn_x, spawn_y, self.fertility_spawn_cost / 2)
