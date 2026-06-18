from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from agents.body import BodyPlan, inherit_body_plan
from world.environment import (
    AMBIENT_TEMPERATURE_K,
    CHILD_GROWTH,
    FOOD_RAW_MEAT,
    FOOD_RAW_PLANT,
    MATERIAL_ASH,
    MATERIAL_CLAY,
    MATERIAL_FIBER,
    MATERIAL_LEAF,
    MATERIAL_SAND,
    MATERIAL_SOIL,
    MATERIAL_STONE,
    MATERIAL_WOOD,
)
from world import metabolism

MAX_AGE = 200
INITIAL_ENERGY = 140
REPRODUCTION_THRESHOLD = 150
REPRODUCTION_COST = 60
ADULT_AGE = 61
MINIMUM_REPRODUCTION_HEALTH = 18
CHILD_MAX_AGE = 30
JUVENILE_MAX_AGE = 60
OLD_AGE = 161
SAFE_RADIUS = 3
NEST_BUILD_THRESHOLD = 165
NEST_BUILD_COST = 35
NEST_RESOURCE_REQUIREMENT = 3
STORAGE_SURPLUS_THRESHOLD = 24
PERSONAL_ENERGY_STORAGE_MARGIN = 18
HOUSEHOLD_STORAGE_SHARE = 0.35
LOW_BUFFER_STORAGE_SHARE = 0.55
CHILD_NEST_WITHDRAWAL = 12
LINEAGE_REPRODUCTION_BONUS = 25
MIN_CARE_TEAM_FOR_BIRTH = 1
BREEDER_NEST_FOOD_RESERVE = 10
GENERAL_NEST_FOOD_RESERVE = 20
CRITICAL_ADULT_WITHDRAW_ENERGY = 28
BIRTH_NEST_FOOD_COST = 8
HUNGER_PRIORITY_ENERGY = 58
HUNGER_CRITICAL_ENERGY = 24
FEAR_INSTINCT_DANGER = 0.45
COLD_STRESS_TEMPERATURE_K = 286.15
WARM_TARGET_TEMPERATURE_K = 289.15
REPRODUCTION_SAFETY_THRESHOLD = 0.66
REPRODUCTION_COMFORT_THRESHOLD = 0.58
REPRODUCTION_ATTACHMENT_THRESHOLD = 0.28
REPRODUCTION_SAFETY_STREAK = 10
REPRODUCTION_PAIR_BOND_STREAK = 14


@dataclass
class Agent:
    agent_id: int
    body: BodyPlan
    x: int
    y: int
    energy: int = INITIAL_ENERGY
    age: int = 0
    durability: int = field(init=False)
    alive: bool = True
    food_eaten: int = 0
    children_count: int = 0
    distance_traveled: int = 0
    death_reason: str | None = None
    completed_lifespan: bool = False
    remembered_danger: list[tuple[int, int]] = field(default_factory=list)
    remembered_food: list[tuple[int, int]] = field(default_factory=list)
    remembered_food_sources: list[tuple[int, int]] = field(default_factory=list)
    remembered_safe_zones: list[tuple[int, int]] = field(default_factory=list)
    remembered_nest_locations: list[tuple[int, int]] = field(default_factory=list)
    friend_ids: set[int] = field(default_factory=set)
    preferred_role: str = "wanderer"
    current_role: str = "solo"
    group_id: int | None = None
    group_target: tuple[int, int] | None = None
    group_center: tuple[float, float] | None = None
    shared_home_owner_id: int | None = None
    protect_target_id: int | None = None
    protect_target_kind: str | None = None
    sex: str = "female"
    generation: int = 0
    parent_id: int | None = None
    other_parent_id: int | None = None
    lineage_id: str | None = None
    children_ids: list[int] = field(default_factory=list)
    bond_strength: dict[int, float] = field(default_factory=dict)
    last_known_family_positions: dict[int, tuple[int, int]] = field(default_factory=dict)
    nearby_support: bool = False
    near_parent: bool = False
    near_nest: bool = False
    nest_position: tuple[int, int] | None = None
    is_safe_area: bool = False
    care_target: tuple[int, int] | None = None
    settlement_target: tuple[int, int] | None = None
    local_group_members: list["Agent"] = field(default_factory=list, repr=False)
    recent_events: list[str] = field(default_factory=list, repr=False)
    growth_progress: int = 0
    child_stress: int = 0
    meals_by_type: dict[str, int] = field(default_factory=dict)
    # Food-value learning study B: learned net energy per food kind (EMA over the
    # energy actually gained when eating it). Drives an optimal-diet eat decision
    # when env.food_value_learning_enabled. Empty by default = no effect.
    food_value_memory: dict[str, float] = field(default_factory=dict)
    stored_food_contributions: int = 0
    equipped_object_id: int | None = None
    gathered_materials: dict[str, int] = field(default_factory=dict)
    technology_constructions: dict[str, int] = field(default_factory=dict)
    technology_uses: dict[str, int] = field(default_factory=dict)
    matured_offspring_count: int = 0
    reproduction_partner_id: int | None = None
    reproduction_cooldown: int = 0
    reproduction_debug: dict[str, object] = field(default_factory=dict, repr=False)
    immortal: bool = False
    instinct_state: str = "balanced"
    hunger_stress_ticks: int = 0
    cold_stress_ticks: int = 0
    fear_stress_ticks: int = 0
    carried_seed_id: int | None = None
    # Metabolism v2 endozoochory: seeds swallowed with fruit, as (seed_id, entry_tick).
    gut_seeds: list[tuple[int, int]] = field(default_factory=list)
    body_temperature_k: float = AMBIENT_TEMPERATURE_K
    wetness: float = 0.0
    hunger_level: float = 0.0
    fear_level: float = 0.0
    cold_level: float = 0.0
    safety_feeling: float = 0.5
    comfort_level: float = 0.5
    attachment_level: float = 0.0
    safety_streak_ticks: int = 0
    pair_bond_ticks: int = 0

    def __post_init__(self) -> None:
        self.durability = self.body.durability
        self.preferred_role = self._infer_preferred_role()

    def tick(self, env, rng: Random) -> bool:
        if not self.alive or self.completed_lifespan:
            return False

        self._last_env = env
        self.age += 1
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        self.energy -= self._base_energy_drain()
        self.energy -= self._brain_energy_drain()
        self._withdraw_nest_food_if_needed(env)

        if not self._resolve_life_state():
            return False

        self._update_affective_state(env)
        instinct = self._dominant_instinct(env)
        self._apply_instinct_pressure(env, instinct)

        if instinct != "balanced":
            self._act_on_instinct(env, rng, instinct)
        else:
            if getattr(env, "scaffolded_agent_actions_enabled", False):
                self._try_build_nest(env)
                self._gather_materials_for_nest(env, rng)
                self._tend_food_patch(env, rng)
                self._maintain_hearth(env)
                self._experiment_with_objects(env, rng)

            hunted = self._try_hunt_large_animal(env, rng)
            if not hunted and not self._move_toward_food_signal(env, rng):
                self._wander(env, rng)
            self._handle_seed_primitive(env, rng)

        consumed_food = self._consume_current_food(env)
        if consumed_food or self.carried_seed_id is not None:
            self._handle_seed_primitive(env, rng, food_contact=consumed_food)

        self._process_gut(env)

        self._apply_environmental_danger(env, rng)

        if not self._resolve_life_state():
            return False

        if self.age >= MAX_AGE and not self.immortal:
            self.completed_lifespan = True
            self.alive = False
            self.death_reason = "lifespan_completed"
            return False

        if instinct != "balanced":
            return False
        return self.can_reproduce()

    def can_reproduce(self) -> bool:
        if self.sex != "female":
            self.reproduction_partner_id = None
            self.reproduction_debug = {
                "eligible": False,
                "reason": "not_female",
                "near_nest": self.near_nest,
                "mate": False,
                "nest_food": 0,
                "energy": self.energy,
                "threshold": None,
            }
            return False
        support_count = sum(
            1
            for member in self.local_group_members
            if abs(member.x - self.x) + abs(member.y - self.y) <= SAFE_RADIUS
            and member.current_stage in {"adult", "juvenile"}
        )
        local_child_load = sum(
            1
            for member in self.local_group_members
            if member.current_stage == "child"
            and abs(member.x - self.x) + abs(member.y - self.y) <= SAFE_RADIUS + 1
        )
        mate = self._find_reproduction_partner()
        self.reproduction_partner_id = mate.agent_id if mate is not None else None
        reproduction_threshold = (
            REPRODUCTION_THRESHOLD
            - int(self.body.reproduction_drive * 20)
            - int(self.safety_feeling * 14)
            - int(self.comfort_level * 18)
            - min(14, support_count * 4)
        )
        reproduction_threshold += local_child_load * 8
        reproduction_threshold = max(92, reproduction_threshold)
        mate_safe_enough = (
            mate is not None
            and mate.fear_level < 0.45
            and mate.hunger_level < 0.45
            and mate.cold_level < 0.55
        )
        conditions = {
            "adult_age": self.age >= ADULT_AGE,
            "adult_stage": self.current_stage == "adult",
            "energy_ok": self.energy >= reproduction_threshold,
            "durability_ok": self.durability >= MINIMUM_REPRODUCTION_HEALTH,
            "safety_ok": self.safety_feeling >= REPRODUCTION_SAFETY_THRESHOLD,
            "comfort_ok": self.comfort_level >= REPRODUCTION_COMFORT_THRESHOLD,
            "attachment_ok": self.attachment_level >= REPRODUCTION_ATTACHMENT_THRESHOLD,
            "safe_duration_ok": self.safety_streak_ticks >= REPRODUCTION_SAFETY_STREAK,
            "pair_bond_ok": self.pair_bond_ticks >= REPRODUCTION_PAIR_BOND_STREAK,
            "hunger_ok": self.hunger_level < 0.35,
            "fear_ok": self.fear_level < 0.50,
            "cold_ok": self.cold_level < 0.60,
            "mate_ok": mate is not None,
            "mate_safe_ok": mate_safe_enough,
            "cooldown_ok": self.reproduction_cooldown <= 0,
        }
        if all(conditions.values()):
            reason = "ready"
            reason_list = ["ready"]
            eligible = True
        else:
            reason_list: list[str] = []
            if not conditions["adult_age"] or not conditions["adult_stage"]:
                reason_list.append("not_adult")
            if not conditions["energy_ok"]:
                reason_list.append("low_energy")
            if not conditions["safety_ok"]:
                reason_list.append("low_safety")
            if not conditions["comfort_ok"]:
                reason_list.append("low_comfort")
            if not conditions["attachment_ok"]:
                reason_list.append("low_attachment")
            if not conditions["safe_duration_ok"]:
                reason_list.append("short_safety_window")
            if not conditions["pair_bond_ok"]:
                reason_list.append("short_pair_bond")
            if not conditions["hunger_ok"]:
                reason_list.append("hungry")
            if not conditions["fear_ok"]:
                reason_list.append("fearful")
            if not conditions["cold_ok"]:
                reason_list.append("cold")
            if not conditions["mate_ok"]:
                reason_list.append("no_mate")
            if not conditions["mate_safe_ok"]:
                reason_list.append("mate_stressed")
            if not conditions["durability_ok"]:
                reason_list.append("low_durability")
            if not conditions["cooldown_ok"]:
                reason_list.append("cooldown")
            reason = "|".join(reason_list) if reason_list else "blocked_other"
            eligible = False

        self.reproduction_debug = {
            "eligible": eligible,
            "reason": reason,
            "reasons": reason_list,
            "near_nest": self.near_nest,
            "mate": mate is not None,
            "safety_feeling": round(self.safety_feeling, 3),
            "comfort_level": round(self.comfort_level, 3),
            "attachment_level": round(self.attachment_level, 3),
            "hunger_level": round(self.hunger_level, 3),
            "fear_level": round(self.fear_level, 3),
            "cold_level": round(self.cold_level, 3),
            "safety_streak_ticks": self.safety_streak_ticks,
            "pair_bond_ticks": self.pair_bond_ticks,
            "energy": self.energy,
            "threshold": reproduction_threshold,
            "support_count": support_count,
            "local_child_load": local_child_load,
            "cooldown": self.reproduction_cooldown,
        }
        return eligible

    @property
    def current_stage(self) -> str:
        if self.age <= CHILD_MAX_AGE:
            return "child"
        if self.age <= JUVENILE_MAX_AGE:
            return "juvenile"
        if self.immortal:
            return "adult"
        if self.age < OLD_AGE:
            return "adult"
        return "old"

    def can_cooperate(self) -> bool:
        return self.body.cognition_score >= 2.2 and self.body.cooperation_drive >= 0.35

    def reset_social_state(self) -> None:
        self.group_id = None
        self.group_target = None
        self.group_center = None
        self.shared_home_owner_id = None
        self.protect_target_id = None
        self.protect_target_kind = None
        self.reproduction_partner_id = None
        self.nearby_support = False
        self.near_parent = False
        self.near_nest = False
        self.nest_position = None
        self.is_safe_area = False
        self.care_target = None
        self.settlement_target = None
        self.local_group_members = []
        if self.can_cooperate():
            self.current_role = self.preferred_role
        else:
            self.current_role = "solo"

    def join_group(
        self,
        group_id: int,
        role: str,
        members: list["Agent"],
    ) -> None:
        self.group_id = group_id
        self.current_role = role
        self.local_group_members = [member for member in members if member.agent_id != self.agent_id]
        self.friend_ids.update(member.agent_id for member in members if member.agent_id != self.agent_id)
        self.group_center = (
            sum(member.x for member in members) / len(members),
            sum(member.y for member in members) / len(members),
        )
        self.shared_home_owner_id = None
        self.group_target = (
            int(round(self.group_center[0])),
            int(round(self.group_center[1])),
        )

    def _collect_shared_memory(
        self,
        members: list["Agent"],
        attribute_name: str,
    ) -> list[tuple[int, int]]:
        seen: list[tuple[int, int]] = []
        for member in members:
            for position in getattr(member, attribute_name):
                if position not in seen:
                    seen.append(position)
        return seen

    def _resolve_shared_home_owner(self, members: list["Agent"]) -> int | None:
        home_votes: list[int] = []
        for member in members:
            if member.parent_id is not None and member.current_stage == "child":
                home_votes.append(member.parent_id)
            elif member.nest_position is not None:
                home_votes.append(member.agent_id)
            elif member.parent_id is not None:
                home_votes.append(member.parent_id)
        if not home_votes:
            return None
        counts: dict[int, int] = {}
        for owner_id in home_votes:
            counts[owner_id] = counts.get(owner_id, 0) + 1
        return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]

    def _find_reproduction_partner(self) -> "Agent" | None:
        candidates = [
            member
            for member in self.local_group_members
            if member.sex == "male"
            and member.current_stage == "adult"
            and member.energy >= max(40, REPRODUCTION_COST // 2)
            and member.durability >= MINIMUM_REPRODUCTION_HEALTH
            and abs(member.x - self.x) + abs(member.y - self.y) <= SAFE_RADIUS
        ]
        if not candidates:
            return None
        candidates.sort(
            key=lambda member: (
                abs(member.x - self.x) + abs(member.y - self.y),
                -member.energy,
                member.agent_id,
            )
        )
        return candidates[0]

    def spawn_child(self, child_id: int, rng: Random, env, mate: "Agent" | None = None) -> Agent:
        # v2 (Fix 3): metabolism genes are heritable only under the v2 model. In v1
        # the flag stays False so inherit_body_plan consumes zero extra RNG draws
        # and the Phase 1-5 stream is byte-identical.
        draw_metabolism_genes = getattr(env, "metabolism_model", "v1") == "v2"
        child_body = inherit_body_plan(
            self.body,
            mate.body if mate is not None else self.body,
            rng,
            draw_metabolism_genes=draw_metabolism_genes,
        )
        self.children_count += 1
        self.children_ids.append(child_id)
        self.current_role = "caretaker"
        self.bond_strength[child_id] = max(self.bond_strength.get(child_id, 0.0), 8.0)
        if mate is not None:
            mate.bond_strength[child_id] = max(mate.bond_strength.get(child_id, 0.0), 6.0)
        child_x, child_y = self._find_spawn_position(env, rng)
        home_owner_id = self._nest_owner_id()
        child_sex = self._choose_child_sex(rng, mate)
        remembered_nests: list[tuple[int, int]] = []
        if self.nest_position is not None:
            remembered_nests.append(self.nest_position)
        return Agent(
            agent_id=child_id,
            body=child_body,
            x=child_x,
            y=child_y,
            energy=INITIAL_ENERGY,
            sex=child_sex,
            generation=self.generation + 1,
            parent_id=self.agent_id,
            other_parent_id=mate.agent_id if mate is not None else None,
            lineage_id=self.lineage_id,
            shared_home_owner_id=home_owner_id,
            remembered_nest_locations=remembered_nests,
            bond_strength={
                self.agent_id: 8.0,
                **({mate.agent_id: 6.0} if mate is not None else {}),
            },
            immortal=self.immortal,
        )

    def prepare_reproduction(self, env, mate: "Agent" | None, litter_size: int) -> None:
        total_cost = REPRODUCTION_COST + max(0, litter_size - 1) * 18
        self.energy -= total_cost
        self.current_role = "caretaker"
        self.reproduction_cooldown = max(10, 20 + (litter_size * 6) - int(self.body.parenting_instinct * 8))
        self.pair_bond_ticks = 0
        owner_id = self._nest_owner_id()
        if owner_id is not None:
            env.withdraw_food_from_nest(owner_id, BIRTH_NEST_FOOD_COST * litter_size)
        if mate is not None:
            mate.energy -= max(12, (REPRODUCTION_COST // 2) + max(0, litter_size - 1) * 8)
            mate.current_role = "protector" if mate.current_role == "solo" else mate.current_role
            mate.reproduction_cooldown = max(mate.reproduction_cooldown, 10 + (litter_size * 4))
            mate.pair_bond_ticks = max(0, mate.pair_bond_ticks - (REPRODUCTION_PAIR_BOND_STREAK // 2))

    def decide_litter_size(self, env, mate: "Agent" | None, rng: Random) -> int:
        litter_size = 1
        owner_id = self._nest_owner_id()
        nest_food_storage = env.get_nest_food_storage(owner_id) if owner_id is not None else 0
        support_count = sum(
            1
            for member in self.local_group_members
            if member.current_stage in {"adult", "juvenile"}
            and abs(member.x - self.x) + abs(member.y - self.y) <= SAFE_RADIUS
        )
        if (
            self.body.reproduction_investment >= 0.82
            and nest_food_storage >= 18
            and support_count >= 2
            and self.energy >= REPRODUCTION_THRESHOLD + 22
        ):
            litter_size += 1
        if (
            self.body.reproduction_drive >= 0.66
            and nest_food_storage >= 28
            and mate is not None
            and self.energy >= REPRODUCTION_THRESHOLD + 34
            and rng.random() < 0.45
        ):
            litter_size += 1
        return min(3, litter_size)

    def _choose_child_sex(self, rng: Random, mate: "Agent" | None) -> str:
        female_count = 0
        male_count = 0
        sampled_agents = [self, *self.local_group_members]
        if mate is not None and mate not in sampled_agents:
            sampled_agents.append(mate)
        for agent in sampled_agents:
            if agent.current_stage not in {"adult", "juvenile"}:
                continue
            if agent.sex == "female":
                female_count += 1
            else:
                male_count += 1
        if female_count <= max(1, male_count - 1):
            return "female"
        if male_count < max(1, female_count - 1):
            return "male"
        return "female" if rng.random() < 0.5 else "male"

    def _find_spawn_position(self, env, rng: Random) -> tuple[int, int]:
        offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        rng.shuffle(offsets)

        for dx, dy in offsets:
            spawn_x = max(0, min(env.width - 1, self.x + dx))
            spawn_y = max(0, min(env.height - 1, self.y + dy))
            if env.is_walkable(spawn_x, spawn_y):
                return spawn_x, spawn_y

        return self.x, self.y

    def _effective_vision(self, is_night: bool) -> int:
        stage_adjusted_vision = self._stage_adjusted_vision()
        if not is_night:
            return stage_adjusted_vision
        return max(1, stage_adjusted_vision // 2)

    def _clamp01(self, value: float) -> float:
        return max(0.0, min(1.0, value))

    def _update_affective_state(self, env) -> None:
        local_temp = env.get_cell_temperature(self.x, self.y)
        local_moisture = env.get_cell_moisture(self.x, self.y)
        local_danger = env.get_danger_level(self.x, self.y)
        nearby_allies = sum(
            1
            for member in self.local_group_members
            if abs(member.x - self.x) + abs(member.y - self.y) <= SAFE_RADIUS
        )
        nearby_food = env.nearby_food_count(self.x, self.y, radius=3)
        partner_near = self._nearby_reproductive_partner_present()

        wetness_target = self._clamp01((local_moisture - 0.38) / 0.55)
        if local_temp >= AMBIENT_TEMPERATURE_K + 3.0:
            wetness_target *= 0.75
        self.wetness += (wetness_target - self.wetness) * 0.16

        ally_warmth = min(1.2, nearby_allies * 0.18)
        hearth_warmth = min(2.5, self._hearth_support_level() * 2.5)
        target_body_temp = local_temp + ally_warmth + hearth_warmth - (self.wetness * 3.2)
        self.body_temperature_k += (target_body_temp - self.body_temperature_k) * 0.12

        max_durability = max(1, self.body.durability)
        injury_pressure = self._clamp01((max_durability - self.durability) / max_durability)
        remembered_danger_here = 0.18 if (self.x, self.y) in self.remembered_danger else 0.0
        social_buffer = min(0.24, nearby_allies * 0.045)
        food_buffer = min(0.14, nearby_food * 0.035)
        safe_area_buffer = max(0.0, 0.35 - local_danger) * 0.34

        self.hunger_level = self._clamp01((HUNGER_PRIORITY_ENERGY - self.energy) / HUNGER_PRIORITY_ENERGY)
        self.cold_level = self._clamp01((COLD_STRESS_TEMPERATURE_K - self.body_temperature_k) / 9.0)
        raw_fear = (
            local_danger
            + injury_pressure * 0.38
            + remembered_danger_here
            + (0.08 if env.is_night else 0.0)
            - social_buffer
            - safe_area_buffer
        )
        self.fear_level = self._clamp01(raw_fear)

        self.attachment_level = self._clamp01(
            (nearby_allies * 0.055)
            + (self.body.cooperation_drive * 0.18)
            + (self.body.parenting_instinct * 0.14)
            + (0.10 if partner_near else 0.0)
        )
        safety_target = self._clamp01(
            0.50
            + safe_area_buffer
            + social_buffer
            + food_buffer
            - (self.fear_level * 0.55)
            - (self.hunger_level * 0.34)
            - (self.cold_level * 0.42)
            - (self.wetness * 0.18)
        )
        self.safety_feeling += (safety_target - self.safety_feeling) * 0.22
        self.comfort_level = self._clamp01(
            self.safety_feeling
            + food_buffer
            + (social_buffer * 0.5)
            - (self.hunger_level * 0.30)
            - (self.cold_level * 0.34)
            - (self.wetness * 0.16)
        )
        if self.safety_feeling >= REPRODUCTION_SAFETY_THRESHOLD and self.comfort_level >= REPRODUCTION_COMFORT_THRESHOLD:
            self.safety_streak_ticks += 1
        else:
            self.safety_streak_ticks = max(0, self.safety_streak_ticks - 1)

        if (
            partner_near
            and self.safety_feeling >= REPRODUCTION_SAFETY_THRESHOLD
            and self.comfort_level >= REPRODUCTION_COMFORT_THRESHOLD
            and self.hunger_level < 0.35
            and self.fear_level < 0.42
        ):
            self.pair_bond_ticks += 1
        else:
            self.pair_bond_ticks = max(0, self.pair_bond_ticks - 1)

    def _dominant_instinct(self, env) -> str:
        if self.energy <= HUNGER_PRIORITY_ENERGY or self.hunger_level >= 0.35:
            return "hunger"
        if self.fear_level >= FEAR_INSTINCT_DANGER or (self.x, self.y) in self.remembered_danger:
            return "fear"
        if self.cold_level >= 0.35:
            return "cold"
        return "balanced"

    def _nearby_reproductive_partner_present(self) -> bool:
        if self.current_stage != "adult":
            return False
        target_sex = "male" if self.sex == "female" else "female"
        return any(
            member.sex == target_sex
            and member.current_stage == "adult"
            and member.durability >= MINIMUM_REPRODUCTION_HEALTH
            and member.energy >= max(36, REPRODUCTION_COST // 2)
            and abs(member.x - self.x) + abs(member.y - self.y) <= SAFE_RADIUS
            for member in self.local_group_members
        )

    def _apply_instinct_pressure(self, env, instinct: str) -> None:
        if instinct == "hunger":
            self.hunger_stress_ticks += 1
            self.instinct_state = "hunger"
            if self.energy <= HUNGER_CRITICAL_ENERGY and self.hunger_stress_ticks % 8 == 0:
                self.durability = max(1, self.durability - 1)
        else:
            self.hunger_stress_ticks = max(0, self.hunger_stress_ticks - 1)

        if instinct == "cold":
            self.cold_stress_ticks += 1
            self.instinct_state = "cold"
            if self.cold_stress_ticks % 10 == 0:
                self.energy -= 1
        else:
            self.cold_stress_ticks = max(0, self.cold_stress_ticks - 1)

        if instinct == "fear":
            self.fear_stress_ticks += 1
            self.instinct_state = "fear"
            self._remember_danger(self.x, self.y)
        else:
            self.fear_stress_ticks = max(0, self.fear_stress_ticks - 1)

        if instinct == "balanced":
            self.instinct_state = "balanced"

    def _act_on_instinct(self, env, rng: Random, instinct: str) -> None:
        if instinct == "hunger":
            self._act_on_hunger_instinct(env, rng)
        elif instinct == "cold":
            self._act_on_cold_instinct(env, rng)
        elif instinct == "fear":
            self._act_on_fear_instinct(env, rng)
        if instinct != "hunger":
            self._handle_seed_primitive(env, rng)

    def _act_on_hunger_instinct(self, env, rng: Random) -> None:
        if self._consume_current_food(env):
            return
        if self._move_toward_food_signal(env, rng, urgency=1.3):
            return
        remembered_food = self._best_remembered_target(self.remembered_food_sources)
        if remembered_food is not None:
            self._move_toward(env, remembered_food[0], remembered_food[1])
            return
        self._move_by_instinct_score(
            env,
            rng,
            lambda next_x, next_y: (
                env.animal_signal_at(next_x, next_y, radius=max(1, self._effective_vision(env.is_night) // 2)) * 0.015
                - (env.get_danger_level(next_x, next_y) * 0.7)
                + (self.body.gather_drive * 0.1)
            ),
        )

    def _act_on_cold_instinct(self, env, rng: Random) -> None:
        self._move_by_instinct_score(
            env,
            rng,
            lambda next_x, next_y: (
                (env.get_cell_temperature(next_x, next_y) - env.get_cell_temperature(self.x, self.y)) * 0.35
                - (env.get_danger_level(next_x, next_y) * 1.2)
                + max(0.0, 0.32 - env.get_danger_level(next_x, next_y))
            ),
        )

    def _act_on_fear_instinct(self, env, rng: Random) -> None:
        self._move_by_instinct_score(
            env,
            rng,
            lambda next_x, next_y: (
                -env.get_danger_level(next_x, next_y) * (2.2 + self.body.danger_avoidance)
                + max(0.0, 0.38 - env.get_danger_level(next_x, next_y)) * 2.0
            ),
        )

    def _move_toward_food_signal(self, env, rng: Random, urgency: float = 1.0) -> bool:
        radius = max(1, min(5, self._effective_vision(env.is_night)))
        current_signal = env.food_signal_at(self.x, self.y, radius=radius)
        moved = self._move_by_instinct_score(
            env,
            rng,
            lambda next_x, next_y: (
                env.food_signal_at(next_x, next_y, radius=radius) * urgency
                - env.get_danger_level(next_x, next_y) * (0.7 + self.body.danger_avoidance)
                + (self.body.gather_drive * 0.05)
            ),
            minimum_improvement=current_signal * 0.02,
        )
        return moved

    def _move_by_instinct_score(
        self,
        env,
        rng: Random,
        score_cell,
        minimum_improvement: float = 0.0,
    ) -> bool:
        candidates = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        rng.shuffle(candidates)
        scored_steps: list[tuple[float, tuple[int, int]]] = []
        current_score = float(score_cell(self.x, self.y))
        move_distance = self._movement_speed()
        for dx, dy in candidates:
            next_x = max(0, min(env.width - 1, self.x + (dx * move_distance)))
            next_y = max(0, min(env.height - 1, self.y + (dy * move_distance)))
            if not env.is_walkable(next_x, next_y):
                continue
            scored_steps.append((float(score_cell(next_x, next_y)) + (rng.random() * 0.05), (dx, dy)))
        if not scored_steps:
            return False
        scored_steps.sort(key=lambda item: item[0], reverse=True)
        if scored_steps[0][0] <= current_score + minimum_improvement:
            return False
        return self._move(env, scored_steps[0][1][0], scored_steps[0][1][1])

    def _consume_current_food(self, env) -> bool:
        if not self._fits_mouth(env):
            return False
        if getattr(env, "food_value_learning_enabled", False) and not self._food_worth_eating(env):
            return False
        resource = env.consume_food(self.x, self.y, eater=self)
        if resource is None:
            return False
        restored_energy = self._process_food_resource(env, resource)
        self._learn_food_value(env, resource.kind, restored_energy)
        self.energy += restored_energy
        self.food_eaten += 1
        self._remember_food(self.x, self.y)
        if resource.source == "plant_lifecycle":
            self.recent_events.append(
                f"plant_lifecycle_food_consumed -> agent={self.agent_id} "
                f"plant={resource.plant_id if resource.plant_id is not None else -1} "
                f"x={self.x} y={self.y} energy={resource.energy} kind={resource.kind}"
            )
        else:
            self.recent_events.append(
                f"food_consumed -> agent={self.agent_id} source={resource.source} "
                f"x={self.x} y={self.y} energy={resource.energy} kind={resource.kind}"
            )
        self.hunger_stress_ticks = 0
        self.instinct_state = "balanced"
        return True

    def _food_worth_eating(self, env) -> bool:
        """Study B optimal-diet decision: should I eat the food under me?

        Always eat an unfamiliar kind once (you must taste it to learn its
        value), and always eat at true starvation. Otherwise skip a kind whose
        LEARNED value is below `diet_pickiness` x the best value learned so far —
        i.e. don't waste a bite on low-value food when a better food is known.
        The value is learned from experienced energy, not hand-coded, so any
        avoidance is emergent. Deliberately NOT gated on the saturated hunger
        flag (mean hunger ~0.98 here would force-eat everything and mask
        learning); a true-starvation floor keeps it from being absurd."""
        pending = env.food_positions.get((self.x, self.y))
        if pending is None:
            return True
        kind = pending.kind
        if kind not in self.food_value_memory:
            return True
        if self.energy <= getattr(env, "diet_starvation_energy", 6):
            return True
        known_values = [v for v in self.food_value_memory.values()]
        best_known = max(known_values) if known_values else 0.0
        if best_known <= 0.0:
            return True
        pickiness = getattr(env, "diet_pickiness", 0.5)
        return self.food_value_memory[kind] >= pickiness * best_known

    def _learn_food_value(self, env, kind: str, gained_energy: float) -> None:
        """EMA update of the learned per-kind food value (study B)."""
        if not getattr(env, "food_value_learning_enabled", False):
            return
        alpha = getattr(env, "diet_learning_rate", 0.3)
        prev = self.food_value_memory.get(kind)
        if prev is None:
            self.food_value_memory[kind] = float(gained_energy)
        else:
            self.food_value_memory[kind] = prev + alpha * (float(gained_energy) - prev)

    def _process_gut(self, env) -> None:
        """v2 endozoochory: advance the gut and excrete seeds whose transit time
        has elapsed, at the agent's current (post-movement) position. Dispersal
        distance > 0 emerges from the agent having moved during transit — it is
        NOT scripted (contrast with the removed seed_hunger_drop_bonus)."""
        if getattr(env, "metabolism_model", "v1") != "v2" or not self.gut_seeds:
            return
        transit = max(1, self.body.gut_transit_ticks)
        remaining: list[tuple[int, int]] = []
        for seed_id, entry_tick in self.gut_seeds:
            if env.tick_count - entry_tick >= transit:
                env.excrete_gut_seed(seed_id, self.agent_id, self.x, self.y, self.body.acid_strength)
            else:
                remaining.append((seed_id, entry_tick))
        self.gut_seeds = remaining

    def _fits_mouth(self, env) -> bool:
        """v2 ingestion gate: an object can be eaten only if it fits the mouth
        (object size <= gape). v1 always allows it. Unknown food kinds (size 0)
        fit by default."""
        if getattr(env, "metabolism_model", "v1") != "v2":
            return True
        pending = env.food_positions.get((self.x, self.y))
        if pending is None:
            return True
        return metabolism.can_ingest(metabolism.FOOD_SIZE.get(pending.kind, 0.0), self.body.gape)

    def _handle_seed_primitive(self, env, rng: Random, food_contact: bool = False) -> None:
        if self.energy <= HUNGER_CRITICAL_ENERGY and not food_contact and self.carried_seed_id is None:
            return
        if self.carried_seed_id is not None and self.carried_seed_id not in env.plant_seeds:
            self.carried_seed_id = None
        if self.carried_seed_id is not None:
            critical_hunger = self.instinct_state == "hunger" and self.energy <= HUNGER_CRITICAL_ENERGY
            drop_safe_window = (
                self.instinct_state == "balanced"
                and self.hunger_level <= getattr(env, "seed_drop_safe_hunger_max", 0.55)
                and self.fear_level <= getattr(env, "seed_drop_safe_fear_max", 0.45)
                and self.cold_level <= getattr(env, "seed_drop_safe_cold_max", 0.45)
                and self.safety_feeling >= getattr(env, "seed_drop_safe_safety_min", 0.45)
            )
            if getattr(env, "seed_drop_block_critical_hunger", False) and critical_hunger:
                return
            if getattr(env, "seed_drop_safe_window_only", False) and not drop_safe_window:
                return
            drop_chance = 0.08 + (self.body.curiosity * 0.04)
            if self.instinct_state in {"fear", "cold"}:
                drop_chance += 0.12
            # v1 only: legacy hand-coded hunger bias. v2 removes it — seed
            # dispersal is meant to emerge from gut transit (endozoochory), not
            # from a scripted hunger rule.
            if self.instinct_state == "hunger" and getattr(env, "metabolism_model", "v1") != "v2":
                drop_chance += getattr(env, "seed_hunger_drop_bonus", 0.06)
            if rng.random() > drop_chance:
                return
            burial_depth = 0.0
            if env.drop_seed(self.carried_seed_id, self.x, self.y, burial_depth_cm=burial_depth):
                if hasattr(env, "disturb_surface"):
                    env.disturb_surface(self.x, self.y, force=0.08 + (self.body.curiosity * 0.04), agent_id=self.agent_id)
                if food_contact:
                    drop_context = "food_contact"
                elif self.instinct_state in {"hunger", "fear", "cold"}:
                    drop_context = self.instinct_state
                else:
                    drop_context = "balanced_random"
                self.recent_events.append(
                    f"seed_dropped -> agent={self.agent_id} seed={self.carried_seed_id} "
                    f"x={self.x} y={self.y} depth_cm={burial_depth:.2f} "
                    f"context={drop_context} instinct={self.instinct_state} "
                    f"food_contact={int(food_contact)} drop_chance={drop_chance:.3f} "
                    f"safe_window={int(drop_safe_window)} critical_hunger={int(critical_hunger)} "
                    f"energy={self.energy:.2f} hunger={self.hunger_level:.3f} "
                    f"fear={self.fear_level:.3f} cold={self.cold_level:.3f} "
                    f"comfort={self.comfort_level:.3f} safety={self.safety_feeling:.3f}"
                )
                self.carried_seed_id = None
            return

        loose_seed = env.find_loose_seed_at(self.x, self.y)
        if loose_seed is None:
            return
        pickup_chance = 0.015 + (self.body.curiosity * 0.05) + (self.body.gather_drive * 0.015)
        if food_contact:
            pickup_chance += 0.18 + (self.body.curiosity * 0.08) + (self.body.gather_drive * 0.025)
        if rng.random() > pickup_chance:
            return
        if env.pick_seed(loose_seed.seed_id, self.agent_id):
            self.carried_seed_id = loose_seed.seed_id
            self.recent_events.append(
                f"seed_picked -> agent={self.agent_id} seed={loose_seed.seed_id} "
                f"x={self.x} y={self.y} food_contact={int(food_contact)} "
                f"instinct={self.instinct_state} energy={self.energy:.2f} "
                f"hunger={self.hunger_level:.3f} fear={self.fear_level:.3f} "
                f"cold={self.cold_level:.3f} comfort={self.comfort_level:.3f}"
            )

    def _wander(self, env, rng: Random) -> None:
        if self.body.cognition_score < 1.2:
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            rng.shuffle(directions)
            for dx, dy in directions:
                if self._move(env, dx, dy):
                    return
            return

        preferred_target = self._preferred_movement_target()
        best_step = self._choose_best_step(env, rng, target=preferred_target)
        if best_step is not None and self._move(env, best_step[0], best_step[1]):
            return

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        rng.shuffle(directions)
        for dx, dy in directions:
            if self._move(env, dx, dy):
                return

    def _move_toward(self, env, target_x: int, target_y: int) -> None:
        target = (target_x, target_y)

        if self.body.cognition_score >= 1.4:
            best_step = self._choose_best_step(env, Random(self.agent_id + self.age), target=target)
            if best_step is not None and self._move(env, best_step[0], best_step[1]):
                return

        steps: list[tuple[int, int]] = []
        dx = 0
        dy = 0

        if target_x > self.x:
            dx = 1
        elif target_x < self.x:
            dx = -1

        if target_y > self.y:
            dy = 1
        elif target_y < self.y:
            dy = -1

        if self.body.decision_quality >= 3 and abs(target_x - self.x) >= abs(target_y - self.y):
            steps = [(dx, 0), (0, dy)]
        elif self.body.decision_quality >= 3:
            steps = [(0, dy), (dx, 0)]
        else:
            steps = [(dx, dy), (dx, 0), (0, dy)]

        for step_dx, step_dy in steps:
            if self._move(env, step_dx, step_dy):
                return

        self._wander(env, Random(self.agent_id + self.age))

    def _choose_best_step(
        self,
        env,
        rng: Random,
        target: tuple[int, int] | None,
    ) -> tuple[int, int] | None:
        candidates = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        scored_steps: list[tuple[float, tuple[int, int]]] = []

        for dx, dy in candidates:
            move_distance = self._movement_speed()
            proposed_x = max(0, min(env.width - 1, self.x + (dx * move_distance)))
            proposed_y = max(0, min(env.height - 1, self.y + (dy * move_distance)))
            if not env.is_walkable(proposed_x, proposed_y):
                continue

            score = 0.0
            danger_level = env.get_danger_level(proposed_x, proposed_y)
            score -= danger_level * (1.8 + (self.body.danger_avoidance * 2.6))

            if (proposed_x, proposed_y) in self.remembered_danger:
                score -= 2.0 + self.body.cognition_score

            if (proposed_x, proposed_y) in self.remembered_food:
                score += 1.2 + self.body.gather_drive

            if (proposed_x, proposed_y) in self.remembered_food_sources:
                score += 1.8 + self.body.gather_drive

            if (proposed_x, proposed_y) in self.remembered_safe_zones:
                score += 1.0 + self.body.danger_avoidance

            if (proposed_x, proposed_y) in self.remembered_nest_locations:
                score += 1.2 + self.body.social_score

            if target is not None:
                current_distance = abs(target[0] - self.x) + abs(target[1] - self.y)
                new_distance = abs(target[0] - proposed_x) + abs(target[1] - proposed_y)
                score += (current_distance - new_distance) * (1.0 + (self.body.planning_focus * 1.4))
                if self.body.memory_score >= 0.7:
                    score += 0.35

            if self.energy < 60:
                score -= danger_level * 1.5
                score += max(0.0, 0.35 - danger_level) * (1.2 + self.body.danger_avoidance)

            if self.nest_position is not None:
                current_nest_distance = abs(self.nest_position[0] - self.x) + abs(self.nest_position[1] - self.y)
                new_nest_distance = abs(self.nest_position[0] - proposed_x) + abs(self.nest_position[1] - proposed_y)
                score += (current_nest_distance - new_nest_distance) * 0.4

            if self.group_center is not None and self.current_role in {"follower", "guardian"}:
                current_group_distance = abs(self.group_center[0] - self.x) + abs(self.group_center[1] - self.y)
                new_group_distance = abs(self.group_center[0] - proposed_x) + abs(self.group_center[1] - proposed_y)
                score += (current_group_distance - new_group_distance) * 0.8

            if self.current_role == "planner":
                score -= danger_level * 1.4
            elif self.current_role == "scout":
                if target is not None:
                    score += 0.8
            elif self.current_role == "guardian":
                score -= danger_level * 1.0
            elif self.current_role == "forager":
                if target is not None:
                    score += 1.2
            elif self.current_role == "gatherer":
                if (proposed_x, proposed_y) in self.remembered_food_sources:
                    score += 1.6
            elif self.current_role == "hunter":
                if self.group_target is not None:
                    score += 1.0
            elif self.current_role == "protector":
                if self.near_nest or danger_level <= 0.35:
                    score += 1.1
            elif self.current_role == "experimenter":
                if self.nest_position is not None:
                    score += 1.0

            if self.current_stage == "child":
                if self.nearby_support:
                    score += 0.8
                elif self.parent_id is not None:
                    score -= 0.6
                score -= self.child_stress * 0.15
                score += max(0.0, 0.35 - danger_level)
            if self._best_object_score(env, "cut", "plant") >= 8.0 and (proposed_x, proposed_y) in self.remembered_food_sources:
                score += 1.6
            if self._best_object_score(env, "pierce", "prey") >= 9.0 and self.group_target is not None:
                score += 1.0
            if self._best_object_score(env, "hit", "defense") >= 7.0 and self.current_role in {"parent", "caretaker", "protector"}:
                score += 0.6
            if self.care_target is not None and target == self.care_target:
                score += 2.0
            if target is not None and self.current_role in {"parent", "caretaker", "protector"}:
                score += 1.4
            if self.current_role in {"caretaker", "protector"} and self.nest_position is not None:
                home_distance = abs(self.nest_position[0] - proposed_x) + abs(self.nest_position[1] - proposed_y)
                if home_distance <= SAFE_RADIUS + 1:
                    score += 1.0
            if self.current_role == "protector" and self.protect_target_kind == "child" and target == self.care_target:
                score += 2.2
            if self.current_role == "protector" and self.protect_target_kind == "nest" and self.nest_position is not None:
                home_distance = abs(self.nest_position[0] - proposed_x) + abs(self.nest_position[1] - proposed_y)
                if home_distance <= 2:
                    score += 1.4
            if self.body.planning_focus >= 0.7 and target is not None:
                score += 0.4
            if self.body.memory_score >= 0.7 and self._is_memory_guided_target(target):
                score += 0.8

            score += rng.random() * max(0.1, 1.0 - (self.body.planning_focus * 0.7))
            score += self.body.exploration_drive * 0.35
            scored_steps.append((score, (dx, dy)))

        if not scored_steps:
            return None

        scored_steps.sort(key=lambda item: item[0], reverse=True)
        return scored_steps[0][1]

    def _move(self, env, dx: int, dy: int) -> bool:
        if dx == 0 and dy == 0:
            return False

        move_distance = self._movement_speed()
        proposed_x = max(0, min(env.width - 1, self.x + (dx * move_distance)))
        proposed_y = max(0, min(env.height - 1, self.y + (dy * move_distance)))

        if not env.is_walkable(proposed_x, proposed_y):
            return False

        traveled = abs(proposed_x - self.x) + abs(proposed_y - self.y)
        self.x = proposed_x
        self.y = proposed_y
        self.distance_traveled += traveled
        movement_penalty = max(1, traveled)
        if self.current_stage == "child" and not self.nearby_support:
            movement_penalty += 1
        self.energy -= movement_penalty
        if hasattr(env, "disturb_surface"):
            env.disturb_surface(self.x, self.y, force=min(0.22, 0.04 * max(1, traveled)), agent_id=self.agent_id)
        return True

    def _try_hunt_large_animal(self, env, rng: Random) -> bool:
        if (
            getattr(env, "scaffolded_agent_actions_enabled", False)
            and self.body.cognition_score >= 4.2
            and self.nest_position is None
            and self.is_safe_area
        ):
            return False
        pierce_score = self._best_object_score(env, "pierce", "prey")
        engage_range = max(1, self.body.speed + (1 if pierce_score >= 9.0 else 0))
        animal = env.find_nearest_large_animal(self.x, self.y, engage_range)
        if animal is None:
            return False

        if self.group_id is None or len(self.local_group_members) < 1:
            if abs(animal.x - self.x) + abs(animal.y - self.y) <= max(1, self.body.speed):
                hunt_bonus = self.get_hunt_power_bonus(env)
                self.energy -= max(1, 2 - hunt_bonus)
                injury_risk = 0.38 - (self.body.aggression * 0.08) - min(0.14, pierce_score * 0.012)
                if rng.random() < max(0.05, injury_risk):
                    self.durability -= 1
                    self._remember_danger(self.x, self.y)
                self.recent_events.append(
                    f"failed solo hunt -> agent={self.agent_id} animal={animal.animal_id} "
                    f"reason=alone"
                )
            return False

        hunt_team = [self]
        for member in self.local_group_members:
            if abs(member.x - animal.x) + abs(member.y - animal.y) <= max(3, engage_range + 1):
                hunt_team.append(member)
        if len(hunt_team) < 2:
            if self.group_center is not None:
                self.group_target = (round(self.group_center[0]), round(self.group_center[1]))
            elif self.local_group_members:
                nearest_teammate = min(
                    self.local_group_members,
                    key=lambda member: abs(member.x - self.x) + abs(member.y - self.y),
                )
                self.group_target = (nearest_teammate.x, nearest_teammate.y)
            else:
                self.group_target = None
            return False

        if abs(animal.x - self.x) + abs(animal.y - self.y) > engage_range:
            return False

        outcome = env.attempt_hunt(animal.animal_id, hunt_team, rng)
        if not outcome["success"]:
            penalty = 2 if outcome["reason"] == "group_power_too_low" else 1
            for member in hunt_team:
                member_bonus = member.get_hunt_power_bonus(env)
                member.energy -= max(1, penalty - member_bonus)
                member_pierce = member._best_object_score(env, "pierce", "prey")
                injury_risk = 0.25 - min(0.10, member_pierce * 0.01)
                if outcome["reason"] != "group_power_too_low" and rng.random() < max(0.05, injury_risk):
                    member.durability -= 1
            self.recent_events.append(
                f"hunt failed -> leader={self.agent_id} team={[member.agent_id for member in hunt_team]} "
                f"animal={animal.animal_id} reason={outcome['reason']}"
            )
            return True

        harvested_energy = int(outcome["raw_meat_energy"]) + sum(
            member._apply_object_action(env, "cut", "prey", base_outcome=4.0)
            for member in hunt_team
        )
        share_per_member = max(1, harvested_energy // len(hunt_team))
        for member in hunt_team:
            restored_energy = member._consume_processed_food(
                env,
                FOOD_RAW_MEAT,
                share_per_member,
            )
            member.energy += restored_energy
            member.food_eaten += 1
            member.successful_hunt()
            member._apply_object_action(env, "pierce", "prey", base_outcome=2.0)
            if (
                getattr(env, "scaffolded_agent_actions_enabled", False)
                and member.body.cognition_score >= 4.2
                and member.is_safe_area
            ):
                member.settlement_target = (member.x, member.y)
                member._try_build_nest(env)
        self.recent_events.append(
            f"hunt success -> leader={self.agent_id} team={[member.agent_id for member in hunt_team]} "
            f"animal={animal.animal_id} herd={outcome['herd_id']} guards={outcome['guard_count']} "
            f"calves={outcome['calf_count']} power={outcome['group_power']} defense={outcome['animal_defense']}"
        )
        return True

    def _apply_environmental_danger(self, env, rng: Random) -> None:
        danger_level = env.get_danger_level(self.x, self.y)
        if self.near_nest:
            danger_level = max(0.0, danger_level - 0.18)
        if self._best_object_score(env, "pierce", "defense") >= 8.0 and self.near_nest:
            danger_level = max(0.0, danger_level - 0.08)
        if danger_level <= 0:
            return

        avoidance_bonus = (
            (self.body.decision_quality - 1) * 0.06
            + (self.body.speed - 1) * 0.12
            + (self.body.danger_avoidance * 0.22)
        )
        if rng.random() > max(0.0, danger_level - avoidance_bonus):
            return

        raw_damage = 1
        if danger_level >= 0.45:
            raw_damage = 2

        mitigated_damage = max(0, raw_damage - self.body.armor_units)
        if self._best_object_score(env, "hit", "defense") >= 7.0 and self.current_role in {"parent", "caretaker"}:
            mitigated_damage = max(0, mitigated_damage - 1)
        if mitigated_damage == 0 and danger_level >= 0.45:
            mitigated_damage = 1 if rng.random() < 0.25 else 0

        self.durability -= mitigated_damage
        if mitigated_damage > 0:
            self._remember_danger(self.x, self.y)

    def _remember_danger(self, x: int, y: int) -> None:
        memory_limit = self._memory_capacity()
        if memory_limit <= 0:
            return
        position = (x, y)
        if position in self.remembered_danger:
            self.remembered_danger.remove(position)
        self.remembered_danger.append(position)
        if len(self.remembered_danger) > memory_limit:
            self.remembered_danger.pop(0)

    def _remember_food(self, x: int, y: int) -> None:
        memory_limit = max(1, self._memory_capacity() // 2)
        position = (x, y)
        if position in self.remembered_food:
            self.remembered_food.remove(position)
        self.remembered_food.append(position)
        if len(self.remembered_food) > memory_limit:
            self.remembered_food.pop(0)
        self._remember_food_source(x, y)

    def _remember_food_source(self, x: int, y: int) -> None:
        self._remember_position(
            self.remembered_food_sources,
            (x, y),
            self._strategic_memory_capacity(),
        )

    def _remember_safe_zone(self, x: int, y: int) -> None:
        self._remember_position(
            self.remembered_safe_zones,
            (x, y),
            self._strategic_memory_capacity(),
        )

    def _remember_nest(self, x: int, y: int) -> None:
        self._remember_position(
            self.remembered_nest_locations,
            (x, y),
            self._strategic_memory_capacity(),
        )

    def _remember_position(
        self,
        memory: list[tuple[int, int]],
        position: tuple[int, int],
        limit: int,
    ) -> None:
        if limit <= 0:
            return
        if position in memory:
            memory.remove(position)
        memory.append(position)
        if len(memory) > limit:
            memory.pop(0)

    def _memory_capacity(self) -> int:
        return max(1, int(round((self.body.brain_units * 2) + (self.body.memory_score * 6))))

    def _strategic_memory_capacity(self) -> int:
        return max(1, int(round((self.body.brain_units * 2) + (self.body.memory_retention * 5))))

    def _process_food_resource(self, env, resource) -> int:
        base_energy = self._metabolic_base_energy(env, resource)
        return self._consume_processed_food(env, resource.kind, base_energy)

    def _metabolic_base_energy(self, env, resource) -> int:
        """Base food energy before cooking/tool bonuses.

        v1 (default): legacy fixed FOOD_ENERGY carried on the resource.
        v2: composition x THIS body's enzyme_profile, so a body that cannot
        chemically break down a nutrient gains nothing from it
        (see world/metabolism.py). Gated by env.metabolism_model so v1 behavior
        is unchanged. Note: v2 uses a fixed per-kind mass, so fruit-biomass
        variation is not yet reflected (a later v2.x refinement).
        """
        if getattr(env, "metabolism_model", "v1") != "v2":
            return resource.energy
        composition = metabolism.COMPOSITION.get(resource.kind)
        if composition is None:
            return resource.energy
        mass = metabolism.FOOD_MASS.get(resource.kind, 1.0)
        return int(round(metabolism.digestible_energy(composition, mass, self.body.enzyme_profile)))

    def _consume_processed_food(self, env, food_kind: str, base_energy: int) -> int:
        cooked_kind = food_kind
        restored_energy = base_energy
        if self._has_external_cooking_heat(env) and self.body.cooking_skill >= 0.5:
            if food_kind == FOOD_RAW_PLANT:
                cooked_kind = "cooked_plant"
                restored_energy = self._cooked_energy(food_kind, base_energy)
                self.recent_events.append(
                    f"cooking -> agent={self.agent_id} kind=plant skill={self.body.cooking_skill:.2f} energy={restored_energy}"
                )
            elif food_kind == FOOD_RAW_MEAT:
                cooked_kind = "cooked_meat"
                restored_energy = self._cooked_energy(food_kind, base_energy)
                self.recent_events.append(
                    f"cooking -> agent={self.agent_id} kind=meat skill={self.body.cooking_skill:.2f} energy={restored_energy}"
                )

        if food_kind == FOOD_RAW_PLANT:
            restored_energy += self._apply_object_action(env, "cut", "plant", base_outcome=4.0)

        if food_kind == FOOD_RAW_MEAT:
            restored_energy += self._apply_object_action(env, "cut", "prey", base_outcome=4.0)

        if self._hearth_support_level() >= 0.35:
            restored_energy += 2

        self.meals_by_type[cooked_kind] = self.meals_by_type.get(cooked_kind, 0) + 1
        self.growth_progress += CHILD_GROWTH.get(cooked_kind, 1)
        if self._hearth_support_level() >= 0.35:
            self.growth_progress += 1

        if getattr(env, "scaffolded_social_support_enabled", False) and self.body.social_score >= 1.7:
            self._share_food_support(env, restored_energy)
        self._store_surplus_food(env, restored_energy)
        return restored_energy

    def _has_external_cooking_heat(self, env) -> bool:
        if self._hearth_support_level() >= 0.35:
            return True
        return env.get_cell_temperature(self.x, self.y) >= 373.15

    def _cooked_energy(self, food_kind: str, raw_energy: int) -> int:
        hearth_bonus = 1.0 + (self._hearth_support_level() * 0.2)
        if food_kind == FOOD_RAW_PLANT:
            base_energy = max(10, int(round(14 * self.body.plant_efficiency)))
            base_energy += int(round(self.body.cooking_skill * 2))
            return int(round(base_energy * hearth_bonus))

        if food_kind == FOOD_RAW_MEAT:
            base_energy = max(18, int(round(24 * self.body.meat_efficiency)))
            base_energy += int(round(self.body.cooking_skill * 4))
            return int(round(base_energy * hearth_bonus))

        bonus = 1.2 + (self.body.cooking_skill * 0.25)
        return int(round(raw_energy * bonus * hearth_bonus))

    def _share_food_support(self, env, restored_energy: int) -> None:
        if not getattr(env, "scaffolded_social_support_enabled", False):
            return
        if not self.local_group_members:
            return

        receivers = [
            member
            for member in self.local_group_members
            if abs(member.x - self.x) + abs(member.y - self.y) <= 2
            and (
                member.agent_id in self.children_ids
                or member.current_stage == "child"
                or member.energy < restored_energy
            )
        ]
        if not receivers:
            return

        receivers.sort(
            key=lambda member: (
                member.agent_id not in self.children_ids,
                member.current_stage != "child",
                abs(member.x - self.x) + abs(member.y - self.y),
            )
        )

        share_energy = max(4, restored_energy // 5)
        for member in receivers[:2]:
            bonded_share = share_energy
            if member.agent_id in self.children_ids:
                bonded_share = max(bonded_share, restored_energy // 3)
            if self.energy <= bonded_share + 8:
                break
            self.energy -= bonded_share
            member.energy += bonded_share
            member.growth_progress += 1 if member.current_stage != "child" else 2
            self._increase_bond(member.agent_id, 1.4)
            member._increase_bond(self.agent_id, 1.0)
            self.recent_events.append(
                f"food shared -> giver={self.agent_id} receiver={member.agent_id} amount={bonded_share}"
            )
        if self.current_role in {"hunter", "gatherer"} and self.near_nest and self.energy > 120:
            self._redistribute_food_to_group()

    def successful_hunt(self) -> None:
        self.meals_by_type["hunt_share"] = self.meals_by_type.get("hunt_share", 0) + 1
        self.current_role = "hunter"

    def _redistribute_food_to_group(self) -> None:
        if not self.local_group_members:
            return
        receivers = [
            member
            for member in self.local_group_members
            if abs(member.x - self.x) + abs(member.y - self.y) <= 3
            and member.energy < self.energy
        ]
        receivers.sort(key=lambda member: (member.current_stage != "child", member.energy))
        for member in receivers[:3]:
            transfer = min(8, max(0, self.energy - member.energy))
            if transfer < 4:
                continue
            self.energy -= transfer
            member.energy += transfer
            self.recent_events.append(
                f"food redistributed -> giver={self.agent_id} receiver={member.agent_id} amount={transfer} role={self.current_role}"
            )

    def get_hunt_power_bonus(self, env) -> int:
        pierce_score = self._best_object_score(env, "pierce", "prey")
        hit_score = self._best_object_score(env, "hit", "prey")
        return int((max(pierce_score, hit_score * 0.7)) // 6)

    def _best_available_object(self, env, action: str, context: str):
        candidates = []
        if self.equipped_object_id is not None:
            equipped = env.get_object(self.equipped_object_id)
            if equipped is not None and equipped.durability > 0:
                candidates.append(equipped)
        owner_id = self._nest_owner_id()
        if owner_id is not None and self.near_nest:
            candidates.extend(env.get_nest_objects(owner_id))
        if not candidates:
            return None
        return max(
            candidates,
            key=lambda physical_object: env.score_object_for_action(physical_object, action, context),
        )

    def _best_object_score(self, env, action: str, context: str) -> float:
        physical_object = self._best_available_object(env, action, context)
        if physical_object is None:
            return 0.0
        if self.near_nest:
            self.equipped_object_id = physical_object.object_id
        return env.score_object_for_action(physical_object, action, context)

    def _apply_object_action(
        self,
        env,
        action: str,
        context: str,
        base_outcome: float,
    ) -> int:
        physical_object = self._best_available_object(env, action, context)
        if physical_object is None:
            return 0
        score = env.score_object_for_action(physical_object, action, context)
        if score <= 0:
            return 0
        if self.near_nest:
            self.equipped_object_id = physical_object.object_id
        bonus = int(score // 3)
        outcome_score = base_outcome + bonus
        env.record_object_use(
            physical_object.object_id,
            self.agent_id,
            outcome_score=outcome_score,
            action=action,
            context=context,
        )
        self.technology_uses[physical_object.classification or "unclassified_object"] = (
            self.technology_uses.get(physical_object.classification or "unclassified_object", 0) + 1
        )
        self.recent_events.append(
            f"object_used -> agent={self.agent_id} object={physical_object.object_id} "
            f"action={action} context={context} outcome={outcome_score:.1f}"
        )
        return max(0, bonus)

    def _base_energy_drain(self) -> int:
        drain = max(1, int(round(self.body.metabolism_rate)))
        if self.near_nest:
            drain = max(0, drain - 1)
        if self.near_nest and self._hearth_support_level() >= 0.35:
            drain = max(0, drain - 1)
        if self.current_stage == "child":
            if self.near_nest:
                drain = max(0, drain - 1)
            if self._hearth_support_level() >= 0.35:
                drain = max(0, drain - 1)
            if self.growth_progress >= 8:
                drain = max(0, drain - 1)
            if self.near_parent:
                drain = max(0, drain - 1)
            if self.nearby_support:
                return drain
            return drain + 1
        if self.current_stage == "juvenile":
            if self.growth_progress >= 12:
                drain = max(1, drain)
            return drain + 1
        if self.current_stage == "old":
            return drain + 1
        return drain

    def _brain_energy_drain(self) -> int:
        drain = self.body.passive_energy_drain
        if self.near_nest:
            drain = max(0, drain - 1)
        if self.near_nest and self._hearth_support_level() >= 0.35:
            drain = max(0, drain - 1)
        if self.current_stage == "child":
            if self.near_nest:
                drain = max(0, drain - 1)
            if self.near_parent:
                return max(0, drain // 2)
            if self.nearby_support:
                return max(0, drain - 1)
        if self.current_stage == "old":
            return drain + 1
        return drain

    def _movement_speed(self) -> int:
        speed = self.body.speed
        if self.current_stage == "child":
            speed = max(1, speed - 1)
            if not self.nearby_support:
                speed = 1
        elif self.current_stage == "juvenile":
            speed = max(1, speed)
        elif self.current_stage == "old":
            speed = max(1, speed - 1)
        return speed

    def _stage_adjusted_vision(self) -> int:
        vision = self.body.effective_vision
        if self.current_stage == "child":
            if self.growth_progress >= 6:
                return max(1, vision)
            return max(1, vision - 1)
        if self.current_stage == "old":
            return max(1, vision - 1)
        return vision

    def set_survival_context(self, env, agents: list["Agent"]) -> None:
        agent_lookup = {agent.agent_id: agent for agent in agents}
        self.is_safe_area = env.is_safe_area(self.x, self.y)
        if self.is_safe_area and self.body.memory_score >= 0.7:
            self._remember_safe_zone(self.x, self.y)
        self.nest_position = self._resolve_nest_position(env, agent_lookup)
        if self.nest_position is not None and self.body.memory_score >= 0.7:
            self._remember_nest(self.nest_position[0], self.nest_position[1])
        self.near_nest = (
            self.nest_position is not None
            and abs(self.nest_position[0] - self.x) + abs(self.nest_position[1] - self.y) <= 4
        )
        if self.near_nest and self.preferred_role == "wanderer":
            self.current_role = "gatherer" if self.body.gather_drive >= 1.6 else self.current_role
        self.care_target = None
        self.settlement_target = None
        if self.current_stage != "child":
            self.nearby_support = False
            self.near_parent = False
            if (
                getattr(env, "scaffolded_agent_actions_enabled", False)
                and self.body.cognition_score >= 4.2
                and self.nest_position is None
            ):
                if self.is_safe_area and env.nearby_food_count(self.x, self.y, radius=3) >= 2:
                    self.settlement_target = (self.x, self.y)
                else:
                    self.settlement_target = env.find_nearest_safe_area(self.x, self.y, vision_range=12)
            self._assign_care_target(agents, agent_lookup)
            return

        parent = agent_lookup.get(self.parent_id) if self.parent_id is not None else None
        self.near_parent = bool(
            parent is not None
            and abs(parent.x - self.x) + abs(parent.y - self.y) <= SAFE_RADIUS
        )
        support_candidates = [
            other
            for other in agents
            if other.agent_id != self.agent_id
            and abs(other.x - self.x) + abs(other.y - self.y) <= SAFE_RADIUS
            and (
                other.agent_id == self.parent_id
                or other.group_id == self.group_id
                or other.agent_id in self.friend_ids
            )
        ]
        self.nearby_support = bool(support_candidates)
        if self.near_parent:
            self.child_stress = max(0, self.child_stress - 2)
            self._increase_bond(self.parent_id, 0.4)
            if parent is not None:
                parent._increase_bond(self.agent_id, 0.4)
                parent.last_known_family_positions[self.agent_id] = (self.x, self.y)
                if parent.current_role not in {"hunter", "planner"}:
                    parent.current_role = "caretaker"
        else:
            self.child_stress += 1
        if self.near_nest:
            self.child_stress = max(0, self.child_stress - 1)
            self.nearby_support = True
            if self.parent_id is not None:
                owner_id = self.parent_id
                env.register_protected_child(owner_id, self.agent_id)
        if support_candidates:
            support_candidates.sort(
                key=lambda other: abs(other.x - self.x) + abs(other.y - self.y)
            )
            nearest = support_candidates[0]
            self.group_target = (nearest.x, nearest.y)
        elif self.parent_id is not None:
            if parent is not None:
                self.group_target = (parent.x, parent.y)
            elif self.parent_id in self.last_known_family_positions:
                self.group_target = self.last_known_family_positions[self.parent_id]

    def _assign_care_target(self, agents: list["Agent"], agent_lookup: dict[int, "Agent"]) -> None:
        if self.current_stage not in {"adult", "juvenile"}:
            return

        vulnerable_children = [
            other
            for other in agents
            if other.current_stage == "child"
            and other.agent_id != self.agent_id
            and (
                other.parent_id == self.agent_id
                or other.parent_id in self.friend_ids
                or (self.group_id is not None and other.group_id == self.group_id)
            )
        ]
        for child in vulnerable_children:
            self.last_known_family_positions[child.agent_id] = (child.x, child.y)
            self._increase_bond(child.agent_id, 0.2)

        if vulnerable_children:
            vulnerable_children.sort(
                key=lambda child: (
                    child.parent_id != self.agent_id,
                    child.nearby_support,
                    child.durability > 6,
                    abs(child.x - self.x) + abs(child.y - self.y),
                )
            )
            target_child = vulnerable_children[0]
            self.care_target = (target_child.x, target_child.y)
            if target_child.parent_id == self.agent_id:
                self.current_role = "caretaker"
                self.protect_target_id = target_child.agent_id
                self.protect_target_kind = "child"
                if not target_child.nearby_support:
                    self.recent_events.append(
                        f"search_for_child -> parent={self.agent_id} child={target_child.agent_id}"
                    )
                if target_child.durability <= 6:
                    self.current_role = "protector"
                    self.recent_events.append(
                        f"protect_child -> parent={self.agent_id} child={target_child.agent_id}"
                    )
            elif self.current_role in {"guardian", "follower", "independent"}:
                self.current_role = "caretaker"
            return

        missing_children = [
            child_id
            for child_id in self.children_ids
            if child_id not in agent_lookup and child_id in self.last_known_family_positions
        ]
        if missing_children:
            child_id = missing_children[0]
            self.care_target = self.last_known_family_positions[child_id]
            self.current_role = "caretaker"
            self.protect_target_id = child_id
            self.protect_target_kind = "missing_child"
            self._decrease_bond(child_id, 0.4)
            self.recent_events.append(
                f"search_for_child -> parent={self.agent_id} child={child_id} last_known={self.care_target}"
            )
            return

        if self.nest_position is not None and self.current_role == "protector":
            self.protect_target_kind = "nest"
            self.care_target = self.nest_position

    def _preferred_movement_target(self) -> tuple[int, int] | None:
        if self.current_stage == "child" and self.group_target is not None:
            return self.group_target
        if self.care_target is not None:
            return self.care_target
        if self.settlement_target is not None and self.nest_position is None:
            return self.settlement_target
        if self.current_role in {"experimenter", "protector"} and self.nest_position is not None:
            return self.nest_position
        if self._best_object_score(self._last_env, "pierce", "prey") >= 9.0 and self.group_target is not None:
            return self.group_target
        if self.energy < 45:
            remembered_food = self._best_remembered_target(self.remembered_food_sources)
            if remembered_food is not None:
                return remembered_food
        if self.current_stage == "child" and self.parent_id is not None:
            return (
                self.group_target
                or self.nest_position
                or self._best_remembered_target(self.remembered_safe_zones)
            )
        if self.child_stress >= 2:
            return self.nest_position or self._best_remembered_target(self.remembered_safe_zones)
        if self.group_target is not None:
            return self.group_target
        if self._best_object_score(self._last_env, "cut", "plant") >= 8.0:
            remembered_food = self._best_remembered_target(self.remembered_food_sources)
            if remembered_food is not None:
                return remembered_food
        if self.current_stage in {"adult", "juvenile"} and self.body.memory_score >= 0.9 and not self.near_nest:
            remembered_nest = self._best_remembered_target(self.remembered_nest_locations)
            if remembered_nest is not None:
                return remembered_nest
        remembered_food = self._best_remembered_target(self.remembered_food_sources)
        if remembered_food is not None:
            return remembered_food
        remembered_safe = self._best_remembered_target(self.remembered_safe_zones)
        if remembered_safe is not None and (self.energy < 70 or self.current_stage == "old"):
            return remembered_safe
        return self.nest_position

    def _best_remembered_target(
        self,
        memories: list[tuple[int, int]],
    ) -> tuple[int, int] | None:
        if not memories:
            return None
        ranked = sorted(
            memories,
            key=lambda position: abs(position[0] - self.x) + abs(position[1] - self.y),
        )
        return ranked[0]

    def _is_memory_guided_target(self, target: tuple[int, int] | None) -> bool:
        if target is None:
            return False
        return (
            target in self.remembered_food_sources
            or target in self.remembered_safe_zones
            or target in self.remembered_nest_locations
        )

    def _infer_preferred_role(self) -> str:
        if self.body.crafting_skill >= 1.6 and self.body.parenting_instinct >= 0.7:
            return "experimenter"
        if self.body.hunt_drive >= 1.2 and self.body.aggression >= 0.6:
            return "hunter"
        if self.body.parenting_instinct >= 0.8 or self.body.reproduction_investment >= 0.8:
            return "caretaker"
        if self.body.cooperation_drive >= 0.7 and self.body.armor_units >= 1:
            return "protector"
        if self.body.gather_drive >= 1.6:
            return "gatherer"
        if self.body.brain_units >= 3 and self.body.sensor_units >= 2:
            return "experimenter"
        if self.body.armor_units >= 2:
            return "protector"
        if self.body.muscle_units >= 2:
            return "hunter"
        if self.body.sensor_units >= 2 or self.body.brain_units >= 2:
            return "gatherer"
        return "wanderer"

    def pop_recent_events(self) -> list[str]:
        events = list(self.recent_events)
        self.recent_events.clear()
        return events

    def _increase_bond(self, other_id: int | None, amount: float) -> None:
        if other_id is None:
            return
        self.bond_strength[other_id] = min(10.0, self.bond_strength.get(other_id, 0.0) + amount)

    def _decrease_bond(self, other_id: int | None, amount: float) -> None:
        if other_id is None:
            return
        self.bond_strength[other_id] = max(0.0, self.bond_strength.get(other_id, 0.0) - amount)

    def _candidate_household_owners(self) -> list[int]:
        owners: list[int] = []
        for owner_id in (
            self.shared_home_owner_id,
            self.parent_id,
            self.other_parent_id,
            self.agent_id,
        ):
            if owner_id is None or owner_id in owners:
                continue
            owners.append(owner_id)
        return owners

    def _resolve_family_home_owner(self, env) -> int | None:
        best_owner_id: int | None = None
        best_score: tuple[int, int] | None = None
        for owner_id in self._candidate_household_owners():
            nest = env.find_nest(owner_id)
            if nest is None:
                continue
            distance = abs(nest.x - self.x) + abs(nest.y - self.y)
            within_radius = 1 if distance <= nest.safe_radius + 1 else 0
            score = (within_radius, nest.food_storage)
            if best_score is None or score > best_score:
                best_owner_id = owner_id
                best_score = score
        return best_owner_id

    def _resolve_nest_position(self, env, agent_lookup: dict[int, "Agent"]) -> tuple[int, int] | None:
        nest = env.find_nest(self.agent_id)
        if nest is not None:
            return (nest.x, nest.y)

        family_owner_id = self._resolve_family_home_owner(env)
        if family_owner_id is not None:
            family_nest = env.find_nest(family_owner_id)
            if family_nest is not None:
                self.shared_home_owner_id = family_owner_id
                return (family_nest.x, family_nest.y)

        if self.shared_home_owner_id is not None:
            shared_nest = env.find_nest(self.shared_home_owner_id)
            if shared_nest is not None:
                return (shared_nest.x, shared_nest.y)

        if self.parent_id is not None:
            parent_nest = env.find_nest(self.parent_id)
            if parent_nest is not None:
                return (parent_nest.x, parent_nest.y)
            parent = agent_lookup.get(self.parent_id)
            if parent is not None and parent.nest_position is not None:
                return parent.nest_position

        return None

    def _nest_owner_id(self) -> int | None:
        if self.nest_position is None:
            return None
        if hasattr(self, "_last_env"):
            family_owner_id = self._resolve_family_home_owner(self._last_env)
            if family_owner_id is not None:
                family_nest = self._last_env.find_nest(family_owner_id)
                if family_nest is not None and (family_nest.x, family_nest.y) == self.nest_position:
                    self.shared_home_owner_id = family_owner_id
                    return family_owner_id
        if self.current_stage == "child" and self.parent_id is not None:
            return self.parent_id
        if self.shared_home_owner_id is not None:
            return self.shared_home_owner_id
        if self.parent_id is not None and self.nest_position in self.remembered_nest_locations:
            return self.parent_id
        if self.other_parent_id is not None and self.nest_position in self.remembered_nest_locations:
            return self.other_parent_id
        if self.nest_position is not None:
            return self.agent_id
        return self.parent_id

    def _join_existing_nest(self, env) -> bool:
        preferred_owner_ids: set[int] = set()
        if self.shared_home_owner_id is not None:
            preferred_owner_ids.add(self.shared_home_owner_id)
        if self.parent_id is not None:
            preferred_owner_ids.add(self.parent_id)
        if self.other_parent_id is not None:
            preferred_owner_ids.add(self.other_parent_id)
        preferred_owner_ids.update(member.agent_id for member in self.local_group_members if member.nest_position is not None)
        nearby_owner_id = env.find_nearby_active_nest_owner(
            self.x,
            self.y,
            radius=6,
            preferred_owner_ids=preferred_owner_ids,
        )
        if nearby_owner_id is None:
            return False
        nest = env.find_nest(nearby_owner_id)
        if nest is None:
            return False
        self.shared_home_owner_id = nearby_owner_id
        self.nest_position = (nest.x, nest.y)
        self.near_nest = abs(nest.x - self.x) + abs(nest.y - self.y) <= nest.safe_radius
        self._remember_nest(nest.x, nest.y)
        return True

    def _try_build_nest(self, env) -> None:
        if not getattr(env, "scaffolded_agent_actions_enabled", False):
            return
        if self.body.cognition_score < 4.2 or self.body.parenting_instinct < 0.55:
            return
        if self.current_stage != "adult":
            return
        if env.find_nest(self.agent_id) is not None:
            return
        if self._join_existing_nest(env):
            return
        if not self.is_safe_area:
            return
        support_builders = sum(
            1
            for member in self.local_group_members
            if member.current_stage == "adult"
            and member.body.cooperation_drive >= 0.45
            and abs(member.x - self.x) + abs(member.y - self.y) <= SAFE_RADIUS
        )
        settlement_bonus = 0
        if self.settlement_target is not None and self.settlement_target == (self.x, self.y):
            settlement_bonus += 12
        if self.is_safe_area:
            settlement_bonus += 10
        if env.nearby_food_count(self.x, self.y, radius=3) >= 3:
            settlement_bonus += 8
        effective_threshold = max(126, NEST_BUILD_THRESHOLD - settlement_bonus - (support_builders * 16))
        effective_cost = max(16, NEST_BUILD_COST - (support_builders * 5) - (settlement_bonus // 6))
        resource_requirement = max(1, NEST_RESOURCE_REQUIREMENT - min(1, support_builders))
        planned_site = (
            self.settlement_target is not None
            and self.settlement_target == (self.x, self.y)
            and self.is_safe_area
        )
        if planned_site:
            resource_requirement = 0
        if self.energy <= effective_threshold:
            return
        if resource_requirement > 0 and env.nearby_food_count(self.x, self.y, radius=2) < resource_requirement:
            return

        consumed = 0
        if resource_requirement > 0:
            consumed = env.consume_building_resources(
                self.x,
                self.y,
                radius=2,
                required=resource_requirement,
            )
            if consumed < resource_requirement:
                return

        nest = env.build_nest(self.agent_id, self.x, self.y)
        if nest is None:
            return

        self.energy -= effective_cost
        self.nest_position = (nest.x, nest.y)
        self.near_nest = True
        self.recent_events.append(
            f"build_nest -> agent={self.agent_id} position={self.nest_position} "
            f"resources={consumed} supporters={support_builders} threshold={effective_threshold}"
        )

    def _gather_materials_for_nest(self, env, rng: Random) -> None:
        if not getattr(env, "scaffolded_agent_actions_enabled", False):
            return
        if self.body.crafting_skill < 1.3:
            return
        if self.current_stage not in {"adult", "juvenile"}:
            return
        if not self.near_nest:
            return
        if self.energy < 50:
            return

        owner_id = self._nest_owner_id()
        if owner_id is None:
            return

        gathered = env.forage_materials(self.x, self.y, rng, self.body.cognition_score)
        if not gathered:
            return
        stored = env.store_materials_in_nest(owner_id, gathered)
        if not stored:
            return

        self.energy -= 1
        for material, amount in stored.items():
            self.gathered_materials[material] = self.gathered_materials.get(material, 0) + amount
        material_text = ", ".join(f"{key}={value}" for key, value in sorted(stored.items()))
        self.recent_events.append(
            f"collect_raw_objects -> agent={self.agent_id} nest={owner_id} {material_text}"
        )

    def _maintain_hearth(self, env) -> None:
        if not getattr(env, "scaffolded_agent_actions_enabled", False):
            return
        if self.current_stage != "adult":
            return
        if not self.near_nest:
            return
        if self.energy < 65:
            return
        if self.body.cognition_score < 3.0:
            return

        owner_id = self._nest_owner_id()
        if owner_id is None:
            return
        outcome = env.maintain_nest_hearth(owner_id, self.body.cognition_score)
        if not outcome.get("success"):
            return
        self.energy -= 2
        self.recent_events.append(
            f"tend_hearth -> agent={self.agent_id} nest={owner_id} "
            f"wood={int(outcome.get('wood_used', 0))} leaf={int(outcome.get('leaf_used', 0))} "
            f"intensity={outcome.get('intensity', 0):.2f}"
        )

    def _tend_food_patch(self, env, rng: Random) -> None:
        if not getattr(env, "scaffolded_agent_actions_enabled", False):
            return
        if self.current_stage != "adult":
            return
        if not self.near_nest:
            return
        if self.energy < 85:
            return
        if self.body.cognition_score < 3.0 or self.body.plant_efficiency < 1.0:
            return
        if self.current_role not in {"planner", "gatherer", "caretaker"}:
            return

        owner_id = self._nest_owner_id()
        if owner_id is None:
            return
        nest_food_storage = env.get_nest_food_storage(owner_id)
        if nest_food_storage > 42 and rng.random() < 0.6:
            return
        outcome = env.tend_food_patch(owner_id, rng)
        if not outcome.get("success"):
            return
        self.energy -= 2
        self.recent_events.append(
            f"tend_food_patch -> agent={self.agent_id} nest={owner_id} "
            f"x={outcome.get('x')} y={outcome.get('y')} boost={outcome.get('boost')}"
        )

    def _experiment_with_objects(self, env, rng: Random) -> None:
        if not getattr(env, "scaffolded_agent_actions_enabled", False):
            return
        if self.body.crafting_skill < 1.4:
            return
        if self.current_stage != "adult":
            return
        if not self.near_nest:
            return
        if self.energy < 110:
            return
        if self.current_role not in {"planner", "experimenter"}:
            return

        owner_id = self._nest_owner_id()
        if owner_id is None:
            return
        nest_food_storage = env.get_nest_food_storage(owner_id)
        if nest_food_storage < 26:
            return
        if env.get_nest_hearth_intensity(owner_id) < 0.25:
            return

        available_materials = env.get_nest_materials(owner_id)
        experiment_mix = self._choose_experiment_mix(available_materials)
        if not experiment_mix:
            return
        if not env.consume_nest_materials(owner_id, experiment_mix):
            return

        physical_object = env.create_experimental_object(
            experiment_mix,
            rng,
            creator_agent_id=self.agent_id,
            creator_lineage_id=self.lineage_id,
        )
        stored_ids = env.store_objects_in_nest(owner_id, [physical_object.object_id])
        if not stored_ids:
            return

        self.equipped_object_id = physical_object.object_id
        self.energy -= max(8, sum(experiment_mix.values()) * 4)
        signature = self._classify_object_shape(physical_object)
        self.technology_constructions[signature] = self.technology_constructions.get(signature, 0) + 1
        material_text = ", ".join(f"{material}={amount}" for material, amount in sorted(experiment_mix.items()))
        self.recent_events.append(
            f"experiment_object -> agent={self.agent_id} nest={owner_id} object={physical_object.object_id} "
            f"signature={signature} materials={material_text} "
            f"props=mass:{physical_object.mass},sharp:{physical_object.sharpness},hard:{physical_object.hardness},"
            f"length:{physical_object.length},flex:{physical_object.flexibility}"
        )

    def _choose_experiment_mix(self, available_materials: dict[str, int]) -> dict[str, int]:
        mix: dict[str, int] = {}
        if available_materials.get(MATERIAL_STONE, 0) > 0:
            mix[MATERIAL_STONE] = 1
        if available_materials.get(MATERIAL_CLAY, 0) > 0 and self.body.crafting_skill >= 1.45:
            mix[MATERIAL_CLAY] = 1
        elif available_materials.get(MATERIAL_SOIL, 0) > 0 and self.body.crafting_skill >= 1.35 and len(mix) < 2:
            mix[MATERIAL_SOIL] = 1
        if available_materials.get(MATERIAL_SAND, 0) > 0 and self.body.crafting_skill >= 1.35 and len(mix) < 2:
            mix[MATERIAL_SAND] = 1
        if available_materials.get(MATERIAL_WOOD, 0) > 0 and (self.body.hunt_drive >= self.body.gather_drive or not mix):
            mix[MATERIAL_WOOD] = min(2, available_materials[MATERIAL_WOOD])
        if available_materials.get(MATERIAL_LEAF, 0) > 0 and self.body.crafting_skill >= 1.5:
            mix[MATERIAL_LEAF] = 1
        if available_materials.get(MATERIAL_ASH, 0) > 0 and self.body.memory_score >= 0.9 and len(mix) < 3:
            mix[MATERIAL_ASH] = 1
        if available_materials.get(MATERIAL_FIBER, 0) > 0 and (self.body.parenting_instinct >= 0.6 or len(mix) < 2):
            mix[MATERIAL_FIBER] = 1
        if not mix:
            return {}
        if sum(mix.values()) < 2:
            for material in (
                MATERIAL_WOOD,
                MATERIAL_STONE,
                MATERIAL_CLAY,
                MATERIAL_SOIL,
                MATERIAL_SAND,
                MATERIAL_LEAF,
                MATERIAL_ASH,
                MATERIAL_FIBER,
            ):
                if available_materials.get(material, 0) > mix.get(material, 0):
                    mix[material] = mix.get(material, 0) + 1
                    break
        return mix if sum(mix.values()) >= 2 else {}

    def _classify_object_shape(self, physical_object) -> str:
        if physical_object.state_label == "fired_hard":
            return "fired_compact_form"
        if physical_object.state_label == "thermal_fractured":
            return "fractured_stone_form"
        if physical_object.state_label == "charred":
            return "charred_composite_form"
        if physical_object.sharpness >= 7 and physical_object.portability:
            return "sharp_portable_form"
        if physical_object.length >= 6 and physical_object.hardness >= 5:
            return "long_rigid_form"
        if physical_object.mass >= 5 and physical_object.hardness >= 5:
            return "heavy_impact_form"
        return "mixed_form"

    def _store_surplus_food(self, env, restored_energy: int) -> None:
        if env is None or not self.near_nest:
            return
        if self.body.cognition_score < 4.2:
            return
        owner_id = self._nest_owner_id()
        if owner_id is None:
            return
        nest_food_storage = env.get_nest_food_storage(owner_id)
        threshold = REPRODUCTION_THRESHOLD + STORAGE_SURPLUS_THRESHOLD
        if self.current_role in {"gatherer", "hunter", "caretaker"}:
            threshold = REPRODUCTION_THRESHOLD - 10
        projected_energy = self.energy + restored_energy
        personal_floor = threshold + PERSONAL_ENERGY_STORAGE_MARGIN
        if self.sex == "female" and self.current_stage == "adult":
            personal_floor += 10
        if projected_energy <= personal_floor:
            return

        surplus = projected_energy - personal_floor
        storage_share = HOUSEHOLD_STORAGE_SHARE
        if nest_food_storage < 10:
            storage_share = LOW_BUFFER_STORAGE_SHARE
        elif nest_food_storage < 20:
            storage_share = max(storage_share, 0.45)

        storage_amount = min(12, max(0, int(round(surplus * storage_share))))
        if self._hearth_support_level() >= 0.35:
            storage_amount += 2
        if storage_amount <= 0:
            return
        stored = env.store_food_in_nest(owner_id, storage_amount)
        if stored <= 0:
            return

        self.energy -= stored
        self.stored_food_contributions += stored
        self.recent_events.append(
            f"store_food -> agent={self.agent_id} nest={owner_id} amount={stored}"
        )

    def _withdraw_nest_food_if_needed(self, env) -> None:
        if not self.near_nest or self.nest_position is None:
            return

        owner_id = self.parent_id if self.current_stage == "child" and self.parent_id is not None else self._nest_owner_id()
        if owner_id is None:
            return
        nest_food_storage = env.get_nest_food_storage(owner_id)
        if nest_food_storage <= 0:
            return
        needed = 0
        if self.current_stage == "child" and self.energy < 60:
            needed = CHILD_NEST_WITHDRAWAL
        elif self.current_stage != "child":
            mate = self._find_reproduction_partner() if self.current_stage == "adult" else None
            support_count = sum(
                1
                for member in self.local_group_members
                if abs(member.x - self.x) + abs(member.y - self.y) <= SAFE_RADIUS
                and member.current_stage in {"adult", "juvenile"}
            )
            reproduction_threshold = REPRODUCTION_THRESHOLD - int(self.body.reproduction_drive * 20)
            if self.near_nest and support_count >= MIN_CARE_TEAM_FOR_BIRTH:
                reproduction_threshold = max(
                    100,
                    reproduction_threshold - LINEAGE_REPRODUCTION_BONUS - int(self.body.parenting_instinct * 8),
                )

            breeder_priority = (
                self.current_stage == "adult"
                and self.sex == "female"
                and mate is not None
                and self.durability >= MINIMUM_REPRODUCTION_HEALTH
            )

            reserve = GENERAL_NEST_FOOD_RESERVE
            if breeder_priority:
                reserve = BREEDER_NEST_FOOD_RESERVE

            if breeder_priority and self.energy < reproduction_threshold:
                needed = min(18, max(8, reproduction_threshold - self.energy))
            elif self.energy < CRITICAL_ADULT_WITHDRAW_ENERGY and nest_food_storage > reserve:
                needed = 10

            if needed > 0 and self.energy >= CRITICAL_ADULT_WITHDRAW_ENERGY and nest_food_storage <= reserve:
                needed = 0
        if needed <= 0:
            return

        available_to_withdraw = nest_food_storage
        if self.current_stage != "child":
            reserve = BREEDER_NEST_FOOD_RESERVE if (
                self.current_stage == "adult"
                and self.sex == "female"
                and self.durability >= MINIMUM_REPRODUCTION_HEALTH
                and self._find_reproduction_partner() is not None
            ) else GENERAL_NEST_FOOD_RESERVE
            if self.energy >= CRITICAL_ADULT_WITHDRAW_ENERGY:
                available_to_withdraw = max(0, nest_food_storage - reserve)
        withdrawn = env.withdraw_food_from_nest(owner_id, min(needed, available_to_withdraw))
        if withdrawn <= 0:
            return

        self.energy += withdrawn
        self.recent_events.append(
            f"withdraw_food -> agent={self.agent_id} nest={owner_id} amount={withdrawn}"
        )

    def _resolve_life_state(self) -> bool:
        if self.immortal:
            self.energy = max(1, self.energy)
            self.durability = max(1, self.durability)
            return True
        if self.energy <= 0:
            self.energy = 1
            self.hunger_stress_ticks += 1
            self.instinct_state = "hunger"
            return True
        if self.durability <= 0:
            self.alive = False
            self.death_reason = "durability_depleted"
            return False
        if self.current_stage == "child" and not self.nearby_support and not self.near_nest and self.energy <= 8:
            self.alive = False
            self.death_reason = "child_isolation"
            return False
        return True

    def _hearth_support_level(self) -> float:
        if not self.near_nest or not hasattr(self, "_last_env"):
            return 0.0
        owner_id = self._nest_owner_id()
        if owner_id is None:
            return 0.0
        return self._last_env.get_nest_hearth_intensity(owner_id)
