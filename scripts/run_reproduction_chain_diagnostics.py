from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from contextlib import contextmanager
from dataclasses import dataclass, field
import json
from pathlib import Path
from random import Random
import statistics
import sys
from typing import Callable, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import agents.agent as agent_mod
import agents.body as body_mod
from agents.agent import Agent
from agents.body import BodyPlan, generate_candidate_body_plans
from simulation import runner as runner_mod
from world.environment import Environment
import world.environment as env_mod


OUTPUT_ROOT = PROJECT_ROOT / "data" / "hypothesis_diagnostics" / "h12_h18_2026-06-03"
REPORT_PATH = PROJECT_ROOT / "reports" / "reproduction_chain_diagnostics_h12_h18_2026-06-03.md"


@dataclass(frozen=True)
class DiagnosticCondition:
    condition_id: str
    hypothesis: str
    label: str
    description: str
    patches: tuple[str, ...] = ()
    env_kwargs: dict[str, object] = field(default_factory=dict)


@dataclass
class FemaleLifeStats:
    agent_id: int
    generation: int
    lineage_id: str | None
    first_adult_tick: int | None = None
    death_tick: int | None = None
    adult_alive_ticks: int = 0
    near_nest_ticks: int = 0
    mate_available_ticks: int = 0
    cooldown_blocked_ticks: int = 0
    full_ready_ticks: int = 0
    opportunity_ticks: int = 0
    opportunity_window_count: int = 0
    birth_count: int = 0
    matured_child_count: int = 0
    matured_female_child_count: int = 0
    _in_opportunity_window: bool = False
    _missed_opportunity_ticks: int = 0


class PatchRegistry:
    def __init__(self) -> None:
        self._restores: list[tuple[object, str, object]] = []

    def set_attr(self, target: object, name: str, value: object) -> None:
        self._restores.append((target, name, getattr(target, name)))
        setattr(target, name, value)

    def restore(self) -> None:
        for target, name, value in reversed(self._restores):
            setattr(target, name, value)
        self._restores.clear()


@contextmanager
def apply_patches(patch_names: Iterable[str]):
    registry = PatchRegistry()
    try:
        for patch_name in patch_names:
            PATCH_APPLIERS[patch_name](registry)
        yield
    finally:
        registry.restore()


def patch_h1_breeder_tuned(registry: PatchRegistry) -> None:
    registry.set_attr(agent_mod, "BREEDER_NEST_FOOD_RESERVE", 6)
    registry.set_attr(agent_mod, "GENERAL_NEST_FOOD_RESERVE", 24)
    registry.set_attr(agent_mod, "CRITICAL_ADULT_WITHDRAW_ENERGY", 34)
    registry.set_attr(agent_mod, "PERSONAL_ENERGY_STORAGE_MARGIN", 24)


def patch_h2_canonical_household(registry: PatchRegistry) -> None:
    original = Agent._nest_owner_id

    def canonical_owner(self: Agent) -> int | None:
        env = getattr(self, "_last_env", None)
        if env is not None:
            for owner_id in (self.shared_home_owner_id, self.parent_id, self.other_parent_id):
                if owner_id is None:
                    continue
                nest = env.find_nest(owner_id)
                if nest is None:
                    continue
                if self.nest_position is None or abs(nest.x - self.x) + abs(nest.y - self.y) <= nest.safe_radius + 8:
                    self.shared_home_owner_id = owner_id
                    self.nest_position = (nest.x, nest.y)
                    return owner_id
        return original(self)

    registry.set_attr(Agent, "_nest_owner_id", canonical_owner)


def patch_h3_pipeline_priority(registry: PatchRegistry) -> None:
    original = Agent._withdraw_nest_food_if_needed

    def pipeline_withdraw(self: Agent, env: Environment) -> None:
        original(self, env)
        if not self.alive or not self.near_nest or self.current_stage not in {"juvenile", "adult"}:
            return
        if not (45 <= self.age <= 82):
            return
        if self.energy >= 76:
            return
        owner_id = self._nest_owner_id()
        if owner_id is None:
            return
        nest_food = env.get_nest_food_storage(owner_id)
        if nest_food <= agent_mod.GENERAL_NEST_FOOD_RESERVE + 8:
            return
        amount = min(10, nest_food - agent_mod.GENERAL_NEST_FOOD_RESERVE, 82 - self.energy)
        if amount <= 0:
            return
        withdrawn = env.withdraw_food_from_nest(owner_id, amount)
        if withdrawn <= 0:
            return
        self.energy += withdrawn
        self.recent_events.append(
            f"pipeline_withdraw -> agent={self.agent_id} nest={owner_id} amount={withdrawn}"
        )

    registry.set_attr(Agent, "_withdraw_nest_food_if_needed", pipeline_withdraw)


def patch_h4_mate_rendezvous(registry: PatchRegistry) -> None:
    original = Agent._preferred_movement_target

    def rendezvous_target(self: Agent) -> tuple[int, int] | None:
        if self.current_stage == "adult" and self.nest_position is not None and self.energy >= 52:
            mate = self._find_reproduction_partner() if self.sex == "female" else None
            if self.sex == "male" or mate is None or not self.near_nest:
                return self.nest_position
        return original(self)

    registry.set_attr(Agent, "_preferred_movement_target", rendezvous_target)


def patch_h5_soft_cooldown(registry: PatchRegistry) -> None:
    original = Agent.prepare_reproduction

    def soft_prepare(self: Agent, env: Environment, mate: Agent | None, litter_size: int) -> None:
        original(self, env, mate, litter_size)
        self.reproduction_cooldown = max(5, int(round(self.reproduction_cooldown * 0.55)))
        if mate is not None:
            mate.reproduction_cooldown = max(4, int(round(mate.reproduction_cooldown * 0.65)))

    registry.set_attr(Agent, "prepare_reproduction", soft_prepare)


def patch_h6_earned_nest_support(registry: PatchRegistry) -> None:
    original_build = Environment.build_nest

    def build_with_lower_seed(self: Environment, owner_id: int, x: int, y: int, safe_radius: int = 4):
        nest = original_build(self, owner_id, x, y, safe_radius)
        if nest is not None:
            nest.food_storage = min(nest.food_storage, 6)
        return nest

    def active_only_support(self: Environment, rng: Random) -> None:
        for owner_id, nest in list(self.nests.items()):
            active = self.is_nest_active(owner_id)
            if not active:
                continue
            if self.is_safe_area(nest.x, nest.y) and rng.random() < 0.24:
                nest.food_storage += 1
            if rng.random() < 0.12:
                nest.material_storage[env_mod.MATERIAL_LEAF] = nest.material_storage.get(env_mod.MATERIAL_LEAF, 0) + 1
            if rng.random() < 0.07:
                nest.material_storage[env_mod.MATERIAL_WOOD] = nest.material_storage.get(env_mod.MATERIAL_WOOD, 0) + 1

    registry.set_attr(Environment, "build_nest", build_with_lower_seed)
    registry.set_attr(Environment, "_support_nests", active_only_support)


def patch_h7_managed_patch_productivity(registry: PatchRegistry) -> None:
    original = Environment.tend_food_patch

    def easier_patch(self: Environment, owner_id: int, rng: Random) -> dict[str, object]:
        outcome = original(self, owner_id, rng)
        if outcome.get("success"):
            return outcome
        nest = self.find_nest(owner_id)
        if nest is None:
            return outcome
        candidates: list[tuple[int, int]] = []
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                x = max(0, min(self.width - 1, nest.x + dx))
                y = max(0, min(self.height - 1, nest.y + dy))
                if self.is_safe_area(x, y):
                    candidates.append((x, y))
        if not candidates:
            return outcome
        candidates.sort(
            key=lambda item: (
                self.managed_food_map[item[1]][item[0]],
                abs(item[0] - nest.x) + abs(item[1] - nest.y),
            )
        )
        patch_x, patch_y = candidates[0]
        self.managed_food_map[patch_y][patch_x] = min(1.2, self.managed_food_map[patch_y][patch_x] + 0.26)
        self.physics_events.append(
            f"diagnostic_food_patch_tended -> nest={owner_id} x={patch_x} y={patch_y} boost={self.managed_food_map[patch_y][patch_x]:.2f}"
        )
        return {"success": True, "x": patch_x, "y": patch_y, "boost": round(self.managed_food_map[patch_y][patch_x], 3)}

    registry.set_attr(Environment, "tend_food_patch", easier_patch)


def patch_h8_adult_energy_saver(registry: PatchRegistry) -> None:
    original_base = Agent._base_energy_drain
    original_brain = Agent._brain_energy_drain

    def base_saver(self: Agent) -> int:
        drain = original_base(self)
        if self.current_stage == "adult" and self.near_nest:
            return max(0, drain - 1)
        return drain

    def brain_saver(self: Agent) -> int:
        drain = original_brain(self)
        if self.current_stage == "adult" and self.near_nest and self.current_role in {"caretaker", "planner", "gatherer"}:
            return max(0, drain - 1)
        return drain

    registry.set_attr(Agent, "_base_energy_drain", base_saver)
    registry.set_attr(Agent, "_brain_energy_drain", brain_saver)


def patch_h9_disable_mutation(registry: PatchRegistry) -> None:
    def inherit_without_mutation(parent_a: BodyPlan, parent_b: BodyPlan, rng: Random, **_: object) -> BodyPlan:
        return body_mod.inherit_body_plan(
            parent_a,
            parent_b,
            rng,
            trait_mutation_rate=0.0,
            major_trait_mutation_rate=0.0,
            morphology_mutation_rate=0.0,
        )

    registry.set_attr(agent_mod, "inherit_body_plan", inherit_without_mutation)


def patch_h10_delay_technology(registry: PatchRegistry) -> None:
    original_experiment = Agent._experiment_with_objects
    original_hearth = Agent._maintain_hearth

    def delayed_hearth(self: Agent, env: Environment) -> None:
        if env.tick_count < 120:
            return
        original_hearth(self, env)

    def delayed_experiment(self: Agent, env: Environment, rng: Random) -> None:
        if env.tick_count < 180:
            return
        owner_id = self._nest_owner_id()
        if owner_id is not None and env.get_nest_food_storage(owner_id) < 34:
            return
        original_experiment(self, env, rng)

    registry.set_attr(Agent, "_maintain_hearth", delayed_hearth)
    registry.set_attr(Agent, "_experiment_with_objects", delayed_experiment)


def patch_h11_extend_reproductive_life(registry: PatchRegistry) -> None:
    registry.set_attr(agent_mod, "CHILD_MAX_AGE", 20)
    registry.set_attr(agent_mod, "JUVENILE_MAX_AGE", 39)
    registry.set_attr(agent_mod, "ADULT_AGE", 40)
    registry.set_attr(agent_mod, "OLD_AGE", 190)
    registry.set_attr(agent_mod, "MAX_AGE", 240)


def patch_h12_second_wave_support(registry: PatchRegistry) -> None:
    original = Agent._withdraw_nest_food_if_needed

    def gen1_priority_withdraw(self: Agent, env: Environment) -> None:
        original(self, env)
        if (
            not self.alive
            or self.generation != 1
            or self.sex != "female"
            or self.current_stage != "adult"
            or not self.near_nest
            or self.energy >= 138
        ):
            return
        mate = self._find_reproduction_partner()
        if mate is None or self.durability < agent_mod.MINIMUM_REPRODUCTION_HEALTH:
            return
        owner_id = self._nest_owner_id()
        if owner_id is None:
            return
        nest_food = env.get_nest_food_storage(owner_id)
        if nest_food <= 0:
            return
        amount = min(24, nest_food, 142 - self.energy)
        if amount <= 0:
            return
        withdrawn = env.withdraw_food_from_nest(owner_id, amount)
        if withdrawn <= 0:
            return
        self.energy += withdrawn
        self.recent_events.append(
            f"gen1_priority_withdraw -> agent={self.agent_id} nest={owner_id} amount={withdrawn}"
        )

    registry.set_attr(Agent, "_withdraw_nest_food_if_needed", gen1_priority_withdraw)


def patch_h13_parent_child_overlap(registry: PatchRegistry) -> None:
    registry.set_attr(agent_mod, "CHILD_MAX_AGE", 16)
    registry.set_attr(agent_mod, "JUVENILE_MAX_AGE", 34)
    registry.set_attr(agent_mod, "ADULT_AGE", 35)
    registry.set_attr(agent_mod, "OLD_AGE", 175)
    registry.set_attr(agent_mod, "MAX_AGE", 220)


def patch_h14_food_liquidity(registry: PatchRegistry) -> None:
    original = Agent.can_reproduce

    def liquid_can_reproduce(self: Agent) -> bool:
        ready = original(self)
        if ready:
            return True
        if self.sex != "female" or self.current_stage != "adult":
            return False
        debug = self.reproduction_debug
        reasons = set(debug.get("reasons", []))
        if "nest_food_low" not in reasons:
            return False
        env = getattr(self, "_last_env", None)
        if env is None:
            return False
        owner_id = self._nest_owner_id()
        if owner_id is None or owner_id not in env.nests:
            return False
        local_food = int(debug.get("nest_food", 0) or 0)
        requirement = int(debug.get("nest_food_requirement", 0) or 0)
        need = max(0, requirement - local_food)
        if need <= 0:
            return False

        donors = sorted(
            (
                (donor_id, nest)
                for donor_id, nest in env.nests.items()
                if donor_id != owner_id and nest.food_storage > agent_mod.GENERAL_NEST_FOOD_RESERVE
            ),
            key=lambda item: item[1].food_storage,
            reverse=True,
        )
        moved_total = 0
        for donor_id, donor_nest in donors:
            movable = min(need - moved_total, donor_nest.food_storage - agent_mod.GENERAL_NEST_FOOD_RESERVE)
            if movable <= 0:
                continue
            donor_nest.food_storage -= movable
            env.nests[owner_id].food_storage += movable
            moved_total += movable
            self.recent_events.append(
                f"liquidity_transfer -> agent={self.agent_id} from={donor_id} to={owner_id} amount={movable}"
            )
            if moved_total >= need:
                break
        if moved_total <= 0:
            return False
        return original(self)

    registry.set_attr(Agent, "can_reproduce", liquid_can_reproduce)


def patch_h15_role_protection(registry: PatchRegistry) -> None:
    original_target = Agent._preferred_movement_target
    original_base = Agent._base_energy_drain

    def protected_target(self: Agent) -> tuple[int, int] | None:
        if self.sex == "female" and self.current_stage == "adult" and self.nest_position is not None:
            mate = self._find_reproduction_partner()
            has_child = any(member.current_stage == "child" for member in self.local_group_members)
            if mate is not None and (self.energy >= 92 or has_child):
                return self.nest_position
        if self.current_stage == "adult" and self.sex == "male" and self.nest_position is not None:
            local_females = [
                member
                for member in self.local_group_members
                if member.sex == "female" and member.current_stage == "adult"
            ]
            if local_females and self.energy >= 70:
                return self.nest_position
        return original_target(self)

    def protected_base_drain(self: Agent) -> int:
        drain = original_base(self)
        if self.current_stage == "adult" and self.current_role in {"caretaker", "protector"} and self.near_nest:
            return max(0, drain - 1)
        return drain

    registry.set_attr(Agent, "_preferred_movement_target", protected_target)
    registry.set_attr(Agent, "_base_energy_drain", protected_base_drain)


def patch_h16_energy_debt_relief(registry: PatchRegistry) -> None:
    original_base = Agent._base_energy_drain
    original_brain = Agent._brain_energy_drain

    def early_base_drain(self: Agent) -> int:
        drain = original_base(self)
        env = getattr(self, "_last_env", None)
        if env is not None and env.tick_count <= 140 and self.current_stage in {"adult", "juvenile"}:
            return max(0, drain - 1)
        return drain

    def early_brain_drain(self: Agent) -> int:
        drain = original_brain(self)
        env = getattr(self, "_last_env", None)
        if env is not None and env.tick_count <= 140:
            return max(0, drain - 1)
        return drain

    registry.set_attr(Agent, "_base_energy_drain", early_base_drain)
    registry.set_attr(Agent, "_brain_energy_drain", early_brain_drain)


def patch_h17_lower_birth_cost(registry: PatchRegistry) -> None:
    registry.set_attr(agent_mod, "REPRODUCTION_COST", 38)
    registry.set_attr(agent_mod, "BIRTH_NEST_FOOD_COST", 4)


def patch_h18_settlement_commute(registry: PatchRegistry) -> None:
    original = Agent._preferred_movement_target

    def commute_target(self: Agent) -> tuple[int, int] | None:
        if self.current_stage in {"adult", "juvenile"} and self.nest_position is not None:
            if self.care_target is not None:
                return self.care_target
            if self.energy < 108 and self.current_role not in {"protector", "caretaker"}:
                remembered_food = self._best_remembered_target(self.remembered_food_sources)
                if remembered_food is not None:
                    return remembered_food
                return None
        return original(self)

    registry.set_attr(Agent, "_preferred_movement_target", commute_target)


PATCH_APPLIERS: dict[str, Callable[[PatchRegistry], None]] = {
    "h1_breeder_tuned": patch_h1_breeder_tuned,
    "h2_canonical_household": patch_h2_canonical_household,
    "h3_pipeline_priority": patch_h3_pipeline_priority,
    "h4_mate_rendezvous": patch_h4_mate_rendezvous,
    "h5_soft_cooldown": patch_h5_soft_cooldown,
    "h6_earned_nest_support": patch_h6_earned_nest_support,
    "h7_managed_patch_productivity": patch_h7_managed_patch_productivity,
    "h8_adult_energy_saver": patch_h8_adult_energy_saver,
    "h9_disable_mutation": patch_h9_disable_mutation,
    "h10_delay_technology": patch_h10_delay_technology,
    "h11_extend_reproductive_life": patch_h11_extend_reproductive_life,
    "h12_second_wave_support": patch_h12_second_wave_support,
    "h13_parent_child_overlap": patch_h13_parent_child_overlap,
    "h14_food_liquidity": patch_h14_food_liquidity,
    "h15_role_protection": patch_h15_role_protection,
    "h16_energy_debt_relief": patch_h16_energy_debt_relief,
    "h17_lower_birth_cost": patch_h17_lower_birth_cost,
    "h18_settlement_commute": patch_h18_settlement_commute,
}


def diagnostic_conditions() -> list[DiagnosticCondition]:
    return [
        DiagnosticCondition("baseline", "baseline", "Current baseline", "No diagnostic intervention."),
        DiagnosticCondition("h11_extend_reproductive_life", "H11", "Extend reproductive opportunity", "Reference condition from H1-H11: shorten development and extend adult reproductive life.", ("h11_extend_reproductive_life",)),
        DiagnosticCondition("i_h1_h11", "H1+H11", "Best prior interaction", "Reference best prior interaction: breeder allocation tuning plus longer reproductive life.", ("h1_breeder_tuned", "h11_extend_reproductive_life")),
        DiagnosticCondition("h12_second_wave_support", "H12", "Second-wave support", "Give generation-1 adult females priority household withdrawal to test second-wave gate.", ("h12_second_wave_support",)),
        DiagnosticCondition("h13_parent_child_overlap", "H13", "Parent-child overlap", "Shorten development and extend adult window enough to test parent-child adult overlap.", ("h13_parent_child_overlap",)),
        DiagnosticCondition("h14_food_liquidity", "H14", "Food liquidity", "Move food from surplus nests to the reproducing female's nest when nest-food gate blocks reproduction.", ("h14_food_liquidity",)),
        DiagnosticCondition("h15_role_protection", "H15", "Reproductive role protection", "Keep likely breeders and mates near nest while reducing protected caretaker/protector drain.", ("h15_role_protection",)),
        DiagnosticCondition("h16_energy_debt_relief", "H16", "Early energy debt relief", "Reduce adult/juvenile and brain energy drain during early settlement.", ("h16_energy_debt_relief",)),
        DiagnosticCondition("h17_lower_birth_cost", "H17", "Lower birth cost", "Reduce mother and nest food cost of birth to test whether first-wave births bankrupt households.", ("h17_lower_birth_cost",)),
        DiagnosticCondition("h18_settlement_commute", "H18", "Settlement commute", "Prevent adults from defaulting back to the nest when food-seeking commute is likely needed.", ("h18_settlement_commute",)),
        DiagnosticCondition("i_h12_h13", "Interaction", "H12 + H13", "Second-wave support plus parent-child adult overlap.", ("h12_second_wave_support", "h13_parent_child_overlap")),
        DiagnosticCondition("i_h12_h14", "Interaction", "H12 + H14", "Second-wave support plus food liquidity.", ("h12_second_wave_support", "h14_food_liquidity")),
        DiagnosticCondition("i_h13_h17", "Interaction", "H13 + H17", "Parent-child overlap plus lower birth cost.", ("h13_parent_child_overlap", "h17_lower_birth_cost")),
        DiagnosticCondition("i_h14_h15", "Interaction", "H14 + H15", "Food liquidity plus reproductive role protection.", ("h14_food_liquidity", "h15_role_protection")),
        DiagnosticCondition("i_h16_h17", "Interaction", "H16 + H17", "Early energy debt relief plus lower birth cost.", ("h16_energy_debt_relief", "h17_lower_birth_cost")),
        DiagnosticCondition("i_h1_h11_h14_h17", "Interaction", "H1 + H11 + H14 + H17", "Best prior interaction plus food liquidity and lower birth cost.", ("h1_breeder_tuned", "h11_extend_reproductive_life", "h14_food_liquidity", "h17_lower_birth_cost")),
    ]


def run_diagnostic_trial(
    *,
    condition: DiagnosticCondition,
    seed: int,
    body_index: int,
    initial_population: int,
    max_population: int,
    max_ticks: int,
    snapshot_interval: int,
) -> dict[str, object]:
    rng = Random(seed)
    bodies = generate_candidate_body_plans()
    body = bodies[body_index - 1]
    env = Environment(**condition.env_kwargs)
    spawn_positions = runner_mod._spawn_initial_positions(env, rng, initial_population, body, strategy="default")
    agents: list[Agent] = []
    for agent_id, (x, y) in enumerate(spawn_positions):
        agents.append(
            Agent(
                agent_id=agent_id,
                body=body,
                x=x,
                y=y,
                age=agent_mod.ADULT_AGE + 6,
                lineage_id=runner_mod._lineage_label(agent_id),
                sex="female" if agent_id % 2 == 0 else "male",
                generation=0,
            )
        )

    next_agent_id = len(agents)
    archived_agents: list[Agent] = []
    death_counts: Counter[str] = Counter()
    total_births = 0
    matured_children: set[int] = set()
    first_birth_tick: int | None = None
    first_matured_child_tick: int | None = None
    first_technology_tick: int | None = None
    peak_population = len(agents)
    tick_metrics: list[dict[str, object]] = []
    female_stats: dict[int, FemaleLifeStats] = {}
    child_parent: dict[int, int | None] = {}
    child_sex: dict[int, str] = {}
    child_birth_tick: dict[int, int] = {}
    child_mature_tick: dict[int, int] = {}
    mother_birth_ticks: dict[int, list[int]] = defaultdict(list)
    births_by_mother_generation: Counter[int] = Counter()
    matured_by_child_generation: Counter[int] = Counter()
    first_gen1_birth_tick: int | None = None
    repro_block_reasons: Counter[str] = Counter()
    event_counts: Counter[str] = Counter()
    owner_mismatch_samples = 0
    owner_mismatch_count = 0
    active_nest_food_samples: list[int] = []
    abandoned_nest_food_samples: list[int] = []
    food_liquidity_failure_ticks = 0
    nest_food_low_with_active_food = 0
    nest_food_low_with_abandoned_food = 0
    local_food_gap_samples: list[int] = []
    active_food_at_nest_food_low: list[int] = []
    abandoned_food_at_nest_food_low: list[int] = []
    local_food_at_nest_food_low: list[int] = []
    full_ready_to_birth_candidates = 0

    def ensure_female(agent: Agent) -> FemaleLifeStats:
        if agent.agent_id not in female_stats:
            female_stats[agent.agent_id] = FemaleLifeStats(
                agent_id=agent.agent_id,
                generation=agent.generation,
                lineage_id=agent.lineage_id,
            )
        return female_stats[agent.agent_id]

    for agent in agents:
        if agent.sex == "female":
            ensure_female(agent)

    for _ in range(max_ticks):
        if not agents:
            break

        env.set_active_nest_owners(runner_mod._occupied_nest_owner_ids(env, agents))
        env.step(rng)
        current_tick = env.tick_count
        current_day = current_tick // env.day_length
        births_this_tick = 0
        deaths_this_tick = 0
        runner_mod._update_social_groups(agents, [], set())
        for agent in agents:
            agent.set_survival_context(env, agents)

        update_female_opportunities(env, agents, female_stats, current_tick)
        owner_mismatch_count, owner_mismatch_samples = update_owner_mismatch(
            env,
            agents,
            owner_mismatch_count,
            owner_mismatch_samples,
        )

        active_food, abandoned_food = nest_food_split(env, agents)
        active_nest_food_samples.append(active_food)
        abandoned_nest_food_samples.append(abandoned_food)

        newborns: list[Agent] = []
        for agent in list(agents):
            wants_reproduction = agent.tick(env, rng)
            for event_text in agent.pop_recent_events():
                event_type = event_text.split(" ->", 1)[0]
                event_counts[event_type] += 1
                if event_text.startswith("technology_emerged ->") and first_technology_tick is None:
                    first_technology_tick = current_tick
            if agent.sex == "female" and agent.current_stage == "adult":
                debug = agent.reproduction_debug
                if debug.get("eligible") is True:
                    full_ready_to_birth_candidates += 1
                reason = str(debug.get("reason", "unknown"))
                if reason and reason != "ready":
                    for part in reason.split("|"):
                        repro_block_reasons[part] += 1
                    if "nest_food_low" in reason.split("|"):
                        local_food = int(debug.get("nest_food", 0) or 0)
                        requirement = int(debug.get("nest_food_requirement", 0) or 0)
                        active_food_at_nest_food_low.append(active_food)
                        abandoned_food_at_nest_food_low.append(abandoned_food)
                        local_food_at_nest_food_low.append(local_food)
                        local_food_gap_samples.append(max(0, requirement - local_food))
                        if active_food > requirement:
                            nest_food_low_with_active_food += 1
                        if abandoned_food > 0:
                            nest_food_low_with_abandoned_food += 1
                        if active_food + abandoned_food > requirement:
                            food_liquidity_failure_ticks += 1
            if (
                agent.alive
                and agent.parent_id is not None
                and agent.age >= agent_mod.ADULT_AGE
                and agent.agent_id not in matured_children
            ):
                matured_children.add(agent.agent_id)
                child_mature_tick[agent.agent_id] = current_tick
                matured_by_child_generation[agent.generation] += 1
                parent_id = agent.parent_id
                if parent_id in female_stats:
                    female_stats[parent_id].matured_child_count += 1
                    if agent.sex == "female":
                        female_stats[parent_id].matured_female_child_count += 1
                if first_matured_child_tick is None:
                    first_matured_child_tick = current_tick

            if wants_reproduction and len(agents) + len(newborns) < max_population:
                mate = next(
                    (
                        candidate
                        for candidate in agents
                        if candidate.agent_id == agent.reproduction_partner_id and candidate.alive
                    ),
                    None,
                )
                litter_size = min(
                    max_population - (len(agents) + len(newborns)),
                    agent.decide_litter_size(env, mate, rng),
                )
                agent.prepare_reproduction(env, mate, litter_size)
                if agent.agent_id in female_stats:
                    female_stats[agent.agent_id].birth_count += litter_size
                mother_birth_ticks[agent.agent_id].append(current_tick)
                births_by_mother_generation[agent.generation] += litter_size
                if agent.generation == 1 and first_gen1_birth_tick is None:
                    first_gen1_birth_tick = current_tick
                for _child_index in range(litter_size):
                    child = agent.spawn_child(next_agent_id, rng, env, mate=mate)
                    child_parent[child.agent_id] = agent.agent_id
                    child_birth_tick[child.agent_id] = current_tick
                    child_sex[child.agent_id] = child.sex
                    if child.sex == "female":
                        ensure_female(child)
                    newborns.append(child)
                    next_agent_id += 1
                if first_birth_tick is None:
                    first_birth_tick = current_tick
                total_births += litter_size
                births_this_tick += litter_size

            if not agent.alive:
                if agent.sex == "female" and agent.agent_id in female_stats:
                    female_stats[agent.agent_id].death_tick = current_tick
                    female_stats[agent.agent_id]._in_opportunity_window = False
                death_counts[agent.death_reason or "unknown"] += 1
                archived_agents.append(agent)
                deaths_this_tick += 1
                agents.remove(agent)

        agents.extend(newborns)
        peak_population = max(peak_population, len(agents))
        for event_text in env.pop_physics_events():
            event_type = event_text.split(" ->", 1)[0]
            event_counts[event_type] += 1
            if event_text.startswith("technology_emerged ->") and first_technology_tick is None:
                first_technology_tick = current_tick

        if current_tick % snapshot_interval == 0 or births_this_tick or deaths_this_tick:
            tick_metrics.append(
                runner_mod._make_tick_summary(
                    env,
                    agents,
                    tick=current_tick,
                    births=births_this_tick,
                    deaths=deaths_this_tick,
                )
            )

    for agent in agents:
        if agent.sex == "female" and agent.agent_id in female_stats:
            female_stats[agent.agent_id].death_tick = env.tick_count if not agent.alive else None
        archived_agents.append(agent)

    final_tick = env.tick_count
    adult_gen_counts = Counter(
        agent.generation
        for agent in archived_agents
        if agent.parent_id is not None and agent.age >= agent_mod.ADULT_AGE
    )
    all_gen_counts = Counter(agent.generation for agent in archived_agents)
    stored_food_total = sum(agent.stored_food_contributions for agent in archived_agents)
    nest_food_remaining = sum(nest.food_storage for nest in env.nests.values())
    final_population = sum(1 for agent in agents if agent.alive)
    max_generation_observed = max((agent.generation for agent in archived_agents), default=0)
    first_technology_tick = first_technology_tick or first_technology_from_objects(env)
    female_rows = [female_stat_to_row(item) for item in female_stats.values()]
    opportunity_values = [
        row["opportunity_window_count"]
        for row in female_rows
        if row["first_adult_tick"] is not None
    ]
    actual_birth_values = [
        row["birth_count"]
        for row in female_rows
        if row["first_adult_tick"] is not None
    ]
    matured_female_values = [
        row["matured_female_child_count"]
        for row in female_rows
        if row["first_adult_tick"] is not None
    ]
    total_full_ready_ticks = sum(
        int(row["full_ready_ticks"])
        for row in female_rows
        if row["first_adult_tick"] is not None
    )
    gen1_female_summary = summarize_female_lives_by_generation(female_rows, 1)
    gen2_female_summary = summarize_female_lives_by_generation(female_rows, 2)
    mother_death_ticks = {
        agent_id: (stats.death_tick if stats.death_tick is not None else final_tick)
        for agent_id, stats in female_stats.items()
    }
    mother_post_birth_survival_ticks = [
        max(0, mother_death_ticks.get(mother_id, final_tick) - birth_tick)
        for mother_id, birth_ticks in mother_birth_ticks.items()
        for birth_tick in birth_ticks
    ]
    mothers_with_births = len(mother_birth_ticks)
    mothers_with_second_birth = sum(1 for birth_ticks in mother_birth_ticks.values() if len(birth_ticks) >= 2)
    parent_child_adult_overlap_ticks = []
    for child_id, mature_tick in child_mature_tick.items():
        mother_id = child_parent.get(child_id)
        if mother_id is None:
            continue
        parent_child_adult_overlap_ticks.append(max(0, mother_death_ticks.get(mother_id, final_tick) - mature_tick))
    gen1_adult_females_seen = int(gen1_female_summary["adult_females_seen"])
    gen1_births = births_by_mother_generation.get(1, 0)

    return {
        "condition_id": condition.condition_id,
        "hypothesis": condition.hypothesis,
        "label": condition.label,
        "description": condition.description,
        "patches": list(condition.patches),
        "seed": seed,
        "body_index": body_index,
        "body_design": body.short_description,
        "initial_population": initial_population,
        "max_population": max_population,
        "max_ticks": max_ticks,
        "final_tick": final_tick,
        "final_population": final_population,
        "population_extinct": final_population == 0,
        "peak_population": peak_population,
        "total_births": total_births,
        "matured_children": len(matured_children),
        "matured_per_birth": safe_div(len(matured_children), total_births),
        "max_generation_observed": max_generation_observed,
        "adult_generation_counts": dict(sorted(adult_gen_counts.items())),
        "all_generation_counts": dict(sorted(all_gen_counts.items())),
        "death_reasons": dict(death_counts),
        "reproduction_block_reasons": dict(repro_block_reasons),
        "event_counts": dict(event_counts),
        "first_birth_tick": first_birth_tick,
        "first_gen1_birth_tick": first_gen1_birth_tick,
        "first_matured_child_tick": first_matured_child_tick,
        "first_technology_tick": first_technology_tick,
        "births_by_mother_generation": dict(sorted(births_by_mother_generation.items())),
        "matured_by_child_generation": dict(sorted(matured_by_child_generation.items())),
        "gen1_births": gen1_births,
        "gen2_births": births_by_mother_generation.get(2, 0),
        "second_wave_success": gen1_births > 0,
        "gen1_adult_females_seen": gen1_adult_females_seen,
        "gen1_full_ready_ticks": gen1_female_summary["mean_full_ready_ticks"],
        "gen1_opportunity_windows": gen1_female_summary["mean_opportunity_windows"],
        "gen1_births_per_adult_female": safe_div(gen1_births, gen1_adult_females_seen),
        "gen1_matured_female_children_per_adult_female": gen1_female_summary["mean_matured_female_children_per_adult_female"],
        "gen2_adult_females_seen": gen2_female_summary["adult_females_seen"],
        "mother_post_birth_survival_mean": mean(mother_post_birth_survival_ticks),
        "mother_post_birth_survival_median": median(mother_post_birth_survival_ticks),
        "second_birth_probability": safe_div(mothers_with_second_birth, mothers_with_births),
        "parent_child_adult_overlap_mean": mean(parent_child_adult_overlap_ticks),
        "parent_child_adult_overlap_median": median(parent_child_adult_overlap_ticks),
        "food_liquidity_failure_ticks": food_liquidity_failure_ticks,
        "nest_food_low_with_active_food": nest_food_low_with_active_food,
        "nest_food_low_with_abandoned_food": nest_food_low_with_abandoned_food,
        "mean_local_food_gap_at_nest_food_low": mean(local_food_gap_samples),
        "mean_active_food_at_nest_food_low": mean(active_food_at_nest_food_low),
        "mean_abandoned_food_at_nest_food_low": mean(abandoned_food_at_nest_food_low),
        "mean_local_food_at_nest_food_low": mean(local_food_at_nest_food_low),
        "full_ready_to_birth_conversion": safe_div(total_births, total_full_ready_ticks),
        "eligible_tick_to_birth_conversion": safe_div(total_births, full_ready_to_birth_candidates),
        "stored_food_total": stored_food_total,
        "nest_food_remaining": nest_food_remaining,
        "active_nest_food_mean": mean(active_nest_food_samples),
        "abandoned_nest_food_mean": mean(abandoned_nest_food_samples),
        "final_settlements": len(env.nests),
        "owner_mismatch_rate": safe_div(owner_mismatch_count, owner_mismatch_samples),
        "owner_mismatch_count": owner_mismatch_count,
        "owner_mismatch_samples": owner_mismatch_samples,
        "female_life_summary": summarize_female_lives(female_rows),
        "female_life_rows": female_rows,
        "opportunity_values": opportunity_values,
        "actual_birth_values": actual_birth_values,
        "matured_female_values": matured_female_values,
        "tick_metrics_sample": tick_metrics[-20:],
    }


def update_female_opportunities(
    env: Environment,
    agents: list[Agent],
    female_stats: dict[int, FemaleLifeStats],
    tick: int,
) -> None:
    for agent in agents:
        if not agent.alive or agent.sex != "female":
            continue
        stats = female_stats.setdefault(
            agent.agent_id,
            FemaleLifeStats(agent.agent_id, agent.generation, agent.lineage_id),
        )
        if agent.current_stage != "adult":
            continue
        if stats.first_adult_tick is None:
            stats.first_adult_tick = tick
        stats.adult_alive_ticks += 1
        if agent.near_nest:
            stats.near_nest_ticks += 1
        mate = agent._find_reproduction_partner()
        if mate is not None:
            stats.mate_available_ticks += 1
        if agent.reproduction_cooldown > 0:
            stats.cooldown_blocked_ticks += 1

        owner_id = agent._nest_owner_id()
        nest = env.find_nest(owner_id) if owner_id is not None else None
        nest_reachable = False
        if nest is not None:
            distance = abs(nest.x - agent.x) + abs(nest.y - agent.y)
            nest_reachable = distance <= max(4, nest.safe_radius + 8)
        opportunity = (
            agent.durability >= agent_mod.MINIMUM_REPRODUCTION_HEALTH
            and nest_reachable
            and mate is not None
            and agent.reproduction_cooldown <= 0
        )
        if opportunity:
            stats.opportunity_ticks += 1
            stats._missed_opportunity_ticks = 0
            if not stats._in_opportunity_window:
                stats.opportunity_window_count += 1
                stats._in_opportunity_window = True
        elif stats._in_opportunity_window:
            stats._missed_opportunity_ticks += 1
            if stats._missed_opportunity_ticks >= 4:
                stats._in_opportunity_window = False
                stats._missed_opportunity_ticks = 0

        debug = agent.reproduction_debug
        if debug.get("eligible") is True:
            stats.full_ready_ticks += 1


def update_owner_mismatch(
    env: Environment,
    agents: list[Agent],
    mismatch_count: int,
    sample_count: int,
) -> tuple[int, int]:
    for agent in agents:
        if not agent.alive or agent.current_stage not in {"adult", "juvenile"}:
            continue
        if agent.nest_position is None:
            continue
        owner_id = agent._nest_owner_id()
        if owner_id is None:
            continue
        sample_count += 1
        nest = env.find_nest(owner_id)
        if nest is None or (nest.x, nest.y) != agent.nest_position:
            mismatch_count += 1
    return mismatch_count, sample_count


def nest_food_split(env: Environment, agents: list[Agent]) -> tuple[int, int]:
    active_owners = runner_mod._occupied_nest_owner_ids(env, agents)
    active_food = 0
    abandoned_food = 0
    for owner_id, nest in env.nests.items():
        if owner_id in active_owners:
            active_food += nest.food_storage
        else:
            abandoned_food += nest.food_storage
    return active_food, abandoned_food


def first_technology_from_objects(env: Environment) -> int | None:
    ticks = [
        obj.emergence_tick
        for obj in env.objects.values()
        if obj.emergence_tick is not None
    ]
    return min(ticks) if ticks else None


def female_stat_to_row(stats: FemaleLifeStats) -> dict[str, object]:
    return {
        "agent_id": stats.agent_id,
        "generation": stats.generation,
        "lineage_id": stats.lineage_id,
        "first_adult_tick": stats.first_adult_tick,
        "death_tick": stats.death_tick,
        "adult_alive_ticks": stats.adult_alive_ticks,
        "near_nest_ticks": stats.near_nest_ticks,
        "mate_available_ticks": stats.mate_available_ticks,
        "cooldown_blocked_ticks": stats.cooldown_blocked_ticks,
        "full_ready_ticks": stats.full_ready_ticks,
        "opportunity_ticks": stats.opportunity_ticks,
        "opportunity_window_count": stats.opportunity_window_count,
        "birth_count": stats.birth_count,
        "matured_child_count": stats.matured_child_count,
        "matured_female_child_count": stats.matured_female_child_count,
    }


def summarize_female_lives(rows: list[dict[str, object]]) -> dict[str, object]:
    adult_rows = [row for row in rows if row["first_adult_tick"] is not None]
    return {
        "female_agents_seen": len(rows),
        "adult_females_seen": len(adult_rows),
        "mean_adult_alive_ticks": mean([int(row["adult_alive_ticks"]) for row in adult_rows]),
        "mean_near_nest_ticks": mean([int(row["near_nest_ticks"]) for row in adult_rows]),
        "mean_mate_available_ticks": mean([int(row["mate_available_ticks"]) for row in adult_rows]),
        "mean_cooldown_blocked_ticks": mean([int(row["cooldown_blocked_ticks"]) for row in adult_rows]),
        "mean_full_ready_ticks": mean([int(row["full_ready_ticks"]) for row in adult_rows]),
        "mean_opportunity_ticks": mean([int(row["opportunity_ticks"]) for row in adult_rows]),
        "mean_opportunity_windows": mean([int(row["opportunity_window_count"]) for row in adult_rows]),
        "median_opportunity_windows": median([int(row["opportunity_window_count"]) for row in adult_rows]),
        "mean_births_per_adult_female": mean([int(row["birth_count"]) for row in adult_rows]),
        "mean_matured_children_per_adult_female": mean([int(row["matured_child_count"]) for row in adult_rows]),
        "mean_matured_female_children_per_adult_female": mean([int(row["matured_female_child_count"]) for row in adult_rows]),
        "female_lifetime_replacement_ratio": mean([int(row["matured_female_child_count"]) for row in adult_rows]),
        "share_adult_females_below_2_opportunities": safe_div(
            sum(1 for row in adult_rows if int(row["opportunity_window_count"]) < 2),
            len(adult_rows),
        ),
    }


def summarize_female_lives_by_generation(rows: list[dict[str, object]], generation: int) -> dict[str, object]:
    return summarize_female_lives(
        [row for row in rows if int(row["generation"]) == generation]
    )


def safe_div(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def mean(values: Iterable[float]) -> float:
    data = list(values)
    return round(statistics.fmean(data), 6) if data else 0.0


def median(values: Iterable[float]) -> float:
    data = list(values)
    return round(statistics.median(data), 6) if data else 0.0


def mean_present(values: Iterable[object]) -> float:
    data = [float(value) for value in values if value is not None]
    return mean(data)


def summarize_conditions(runs: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for run in runs:
        grouped[str(run["condition_id"])].append(run)

    rows: list[dict[str, object]] = []
    for condition_id, items in grouped.items():
        female_summaries = [item["female_life_summary"] for item in items]
        rows.append(
            {
                "condition_id": condition_id,
                "hypothesis": items[0]["hypothesis"],
                "label": items[0]["label"],
                "replicates": len(items),
                "extinction_rate": safe_div(sum(1 for item in items if item["population_extinct"]), len(items)),
                "mean_final_tick": mean(float(item["final_tick"]) for item in items),
                "mean_final_population": mean(float(item["final_population"]) for item in items),
                "mean_peak_population": mean(float(item["peak_population"]) for item in items),
                "mean_total_births": mean(float(item["total_births"]) for item in items),
                "mean_matured_children": mean(float(item["matured_children"]) for item in items),
                "mean_matured_per_birth": mean(float(item["matured_per_birth"]) for item in items),
                "mean_gen1_births": mean(float(item["gen1_births"]) for item in items),
                "mean_gen2_births": mean(float(item["gen2_births"]) for item in items),
                "second_wave_success_rate": safe_div(sum(1 for item in items if item["second_wave_success"]), len(items)),
                "mean_first_gen1_birth_tick": mean_present(item["first_gen1_birth_tick"] for item in items),
                "mean_gen1_adult_females_seen": mean(float(item["gen1_adult_females_seen"]) for item in items),
                "mean_gen1_full_ready_ticks": mean(float(item["gen1_full_ready_ticks"]) for item in items),
                "mean_gen1_opportunity_windows": mean(float(item["gen1_opportunity_windows"]) for item in items),
                "mean_gen1_births_per_adult_female": mean(float(item["gen1_births_per_adult_female"]) for item in items),
                "mean_mother_post_birth_survival": mean(float(item["mother_post_birth_survival_mean"]) for item in items),
                "mean_parent_child_adult_overlap": mean(float(item["parent_child_adult_overlap_mean"]) for item in items),
                "mean_second_birth_probability": mean(float(item["second_birth_probability"]) for item in items),
                "mean_food_liquidity_failure_ticks": mean(float(item["food_liquidity_failure_ticks"]) for item in items),
                "mean_local_food_gap_at_nest_food_low": mean(float(item["mean_local_food_gap_at_nest_food_low"]) for item in items),
                "mean_active_food_at_nest_food_low": mean(float(item["mean_active_food_at_nest_food_low"]) for item in items),
                "mean_abandoned_food_at_nest_food_low": mean(float(item["mean_abandoned_food_at_nest_food_low"]) for item in items),
                "mean_full_ready_to_birth_conversion": mean(float(item["full_ready_to_birth_conversion"]) for item in items),
                "mean_max_generation": mean(float(item["max_generation_observed"]) for item in items),
                "mean_stored_food_total": mean(float(item["stored_food_total"]) for item in items),
                "mean_nest_food_remaining": mean(float(item["nest_food_remaining"]) for item in items),
                "mean_active_nest_food": mean(float(item["active_nest_food_mean"]) for item in items),
                "mean_abandoned_nest_food": mean(float(item["abandoned_nest_food_mean"]) for item in items),
                "mean_owner_mismatch_rate": mean(float(item["owner_mismatch_rate"]) for item in items),
                "mean_opportunity_windows": mean(float(summary["mean_opportunity_windows"]) for summary in female_summaries),
                "mean_full_ready_ticks": mean(float(summary["mean_full_ready_ticks"]) for summary in female_summaries),
                "mean_births_per_adult_female": mean(float(summary["mean_births_per_adult_female"]) for summary in female_summaries),
                "mean_matured_female_children_per_adult_female": mean(float(summary["mean_matured_female_children_per_adult_female"]) for summary in female_summaries),
                "share_adult_females_below_2_opportunities": mean(float(summary["share_adult_females_below_2_opportunities"]) for summary in female_summaries),
                "top_death_reasons": merge_counter(items, "death_reasons").most_common(4),
                "top_repro_blocks": merge_counter(items, "reproduction_block_reasons").most_common(6),
            }
        )
    baseline = next((row for row in rows if row["condition_id"] == "baseline"), None)
    if baseline is not None:
        for row in rows:
            row["delta_final_tick_vs_baseline"] = round(float(row["mean_final_tick"]) - float(baseline["mean_final_tick"]), 6)
            row["delta_births_vs_baseline"] = round(float(row["mean_total_births"]) - float(baseline["mean_total_births"]), 6)
            row["delta_matured_vs_baseline"] = round(float(row["mean_matured_children"]) - float(baseline["mean_matured_children"]), 6)
            row["delta_opportunity_windows_vs_baseline"] = round(float(row["mean_opportunity_windows"]) - float(baseline["mean_opportunity_windows"]), 6)
            row["delta_gen1_births_vs_baseline"] = round(float(row["mean_gen1_births"]) - float(baseline["mean_gen1_births"]), 6)
            row["delta_second_wave_success_vs_baseline"] = round(float(row["second_wave_success_rate"]) - float(baseline["second_wave_success_rate"]), 6)
    rows.sort(key=lambda row: (str(row["condition_id"]) != "baseline", str(row["condition_id"])))
    return rows


def merge_counter(items: list[dict[str, object]], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for item in items:
        counter.update({str(k): int(v) for k, v in dict(item.get(key, {})).items()})
    return counter


def write_outputs(runs: list[dict[str, object]], summaries: list[dict[str, object]], args: argparse.Namespace) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "runs.json").write_text(
        json.dumps({"args": vars(args), "runs": runs, "summaries": summaries}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    run_fieldnames = [
        "condition_id",
        "hypothesis",
        "seed",
        "final_tick",
        "final_population",
        "population_extinct",
        "peak_population",
        "total_births",
        "matured_children",
        "matured_per_birth",
        "max_generation_observed",
        "stored_food_total",
        "nest_food_remaining",
        "active_nest_food_mean",
        "abandoned_nest_food_mean",
        "owner_mismatch_rate",
        "first_birth_tick",
        "first_gen1_birth_tick",
        "first_matured_child_tick",
        "first_technology_tick",
        "gen1_births",
        "gen2_births",
        "second_wave_success",
        "gen1_adult_females_seen",
        "gen1_full_ready_ticks",
        "gen1_opportunity_windows",
        "gen1_births_per_adult_female",
        "mother_post_birth_survival_mean",
        "second_birth_probability",
        "parent_child_adult_overlap_mean",
        "food_liquidity_failure_ticks",
        "nest_food_low_with_active_food",
        "nest_food_low_with_abandoned_food",
        "mean_local_food_gap_at_nest_food_low",
        "mean_active_food_at_nest_food_low",
        "mean_abandoned_food_at_nest_food_low",
        "full_ready_to_birth_conversion",
    ]
    with (OUTPUT_ROOT / "runs.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=run_fieldnames)
        writer.writeheader()
        for run in runs:
            writer.writerow({field: run.get(field) for field in run_fieldnames})

    summary_fieldnames = [
        "condition_id",
        "hypothesis",
        "label",
        "replicates",
        "extinction_rate",
        "mean_final_tick",
        "mean_final_population",
        "mean_peak_population",
        "mean_total_births",
        "mean_matured_children",
        "mean_matured_per_birth",
        "mean_gen1_births",
        "mean_gen2_births",
        "second_wave_success_rate",
        "mean_first_gen1_birth_tick",
        "mean_gen1_adult_females_seen",
        "mean_gen1_full_ready_ticks",
        "mean_gen1_opportunity_windows",
        "mean_gen1_births_per_adult_female",
        "mean_mother_post_birth_survival",
        "mean_parent_child_adult_overlap",
        "mean_second_birth_probability",
        "mean_food_liquidity_failure_ticks",
        "mean_local_food_gap_at_nest_food_low",
        "mean_active_food_at_nest_food_low",
        "mean_abandoned_food_at_nest_food_low",
        "mean_full_ready_to_birth_conversion",
        "mean_max_generation",
        "mean_stored_food_total",
        "mean_nest_food_remaining",
        "mean_active_nest_food",
        "mean_abandoned_nest_food",
        "mean_owner_mismatch_rate",
        "mean_opportunity_windows",
        "mean_full_ready_ticks",
        "mean_births_per_adult_female",
        "mean_matured_female_children_per_adult_female",
        "share_adult_females_below_2_opportunities",
        "delta_final_tick_vs_baseline",
        "delta_births_vs_baseline",
        "delta_matured_vs_baseline",
        "delta_opportunity_windows_vs_baseline",
        "delta_gen1_births_vs_baseline",
        "delta_second_wave_success_vs_baseline",
    ]
    with (OUTPUT_ROOT / "condition_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary_fieldnames)
        writer.writeheader()
        for summary in summaries:
            writer.writerow({field: summary.get(field) for field in summary_fieldnames})

    female_fieldnames = [
        "condition_id",
        "seed",
        "agent_id",
        "generation",
        "lineage_id",
        "first_adult_tick",
        "death_tick",
        "adult_alive_ticks",
        "near_nest_ticks",
        "mate_available_ticks",
        "cooldown_blocked_ticks",
        "full_ready_ticks",
        "opportunity_ticks",
        "opportunity_window_count",
        "birth_count",
        "matured_child_count",
        "matured_female_child_count",
    ]
    with (OUTPUT_ROOT / "female_lifetimes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=female_fieldnames)
        writer.writeheader()
        for run in runs:
            for row in run["female_life_rows"]:
                payload = {"condition_id": run["condition_id"], "seed": run["seed"], **row}
                writer.writerow({field: payload.get(field) for field in female_fieldnames})

    REPORT_PATH.write_text(render_report(summaries, runs, args), encoding="utf-8")


def render_report(summaries: list[dict[str, object]], runs: list[dict[str, object]], args: argparse.Namespace) -> str:
    baseline = next((row for row in summaries if row["condition_id"] == "baseline"), None)
    best_matured = sorted(summaries, key=lambda row: float(row["mean_matured_children"]), reverse=True)[:5]
    best_second_wave = sorted(summaries, key=lambda row: (float(row["mean_gen1_births"]), float(row["second_wave_success_rate"])), reverse=True)[:5]
    best_overlap = sorted(summaries, key=lambda row: float(row["mean_parent_child_adult_overlap"]), reverse=True)[:5]
    worst_extinct = sorted(summaries, key=lambda row: (float(row["extinction_rate"]), -float(row["mean_final_tick"])), reverse=True)[:5]

    lines: list[str] = [
        "# รายงานผลทดลอง H12-H18 Reproduction Chain Diagnostic Suite",
        "",
        "จัดทำอัตโนมัติจาก `scripts/run_reproduction_chain_diagnostics.py`",
        "",
        "## ขอบเขตการทดลอง",
        "",
        f"- body_index: `{args.body_index}`",
        f"- initial_population: `{args.initial_population}`",
        f"- max_population: `{args.max_population}`",
        f"- max_ticks: `{args.max_ticks}`",
        f"- seeds: `{', '.join(str(seed) for seed in args.seeds)}`",
        f"- output: `{OUTPUT_ROOT}`",
        "",
        "การทดลองนี้เป็น diagnostic sweep เพื่อดู second-wave reproduction, parent-child overlap, food liquidity, energy debt, birth cost, and settlement-trap interactions. ใช้ seed set เดียวกันทุก condition เพื่อดูทิศทางของผล.",
        "",
        "## ตารางสรุป condition",
        "",
        "| Condition | H | Extinct | Final Tick | Births | Matured | Gen1 Births | 2nd Wave | Max Gen | Gen1 Ready | Parent-Child Overlap | Liquidity Fail | Food Gap | Nest Left |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summaries:
        lines.append(
            f"| `{row['condition_id']}` | {row['hypothesis']} | {row['extinction_rate']:.2f} | "
            f"{row['mean_final_tick']:.1f} | {row['mean_total_births']:.1f} | "
            f"{row['mean_matured_children']:.1f} | {row['mean_gen1_births']:.1f} | "
            f"{row['second_wave_success_rate']:.2f} | {row['mean_max_generation']:.1f} | "
            f"{row['mean_gen1_full_ready_ticks']:.2f} | {row['mean_parent_child_adult_overlap']:.1f} | "
            f"{row['mean_food_liquidity_failure_ticks']:.1f} | {row['mean_local_food_gap_at_nest_food_low']:.1f} | "
            f"{row['mean_nest_food_remaining']:.1f} |"
        )

    lines.extend(["", "## อ่านผลเร็ว", ""])
    if baseline:
        lines.extend(
            [
                f"- Baseline มี mean final tick `{baseline['mean_final_tick']:.1f}`, births `{baseline['mean_total_births']:.1f}`, matured `{baseline['mean_matured_children']:.1f}`, opportunity windows/female `{baseline['mean_opportunity_windows']:.2f}`.",
                f"- Baseline gen1 births `{baseline['mean_gen1_births']:.1f}`, second-wave success rate `{baseline['second_wave_success_rate']:.2f}`, parent-child adult overlap `{baseline['mean_parent_child_adult_overlap']:.1f}`.",
            ]
        )
    lines.append("- เงื่อนไขที่ matured children สูงสุด:")
    for row in best_matured:
        lines.append(
            f"  - `{row['condition_id']}`: matured `{row['mean_matured_children']:.1f}`, births `{row['mean_total_births']:.1f}`, gen1 births `{row['mean_gen1_births']:.1f}`"
        )
    lines.append("- เงื่อนไขที่ second wave ดีสุด:")
    for row in best_second_wave:
        lines.append(
            f"  - `{row['condition_id']}`: gen1 births `{row['mean_gen1_births']:.1f}`, success rate `{row['second_wave_success_rate']:.2f}`, max gen `{row['mean_max_generation']:.1f}`"
        )
    lines.append("- เงื่อนไขที่ parent-child adult overlap สูงสุด:")
    for row in best_overlap:
        lines.append(
            f"  - `{row['condition_id']}`: overlap `{row['mean_parent_child_adult_overlap']:.1f}`, gen1 births `{row['mean_gen1_births']:.1f}`, matured `{row['mean_matured_children']:.1f}`"
        )
    lines.append("- เงื่อนไขที่ collapse/สูญพันธุ์เด่น:")
    for row in worst_extinct:
        lines.append(
            f"  - `{row['condition_id']}`: extinction `{row['extinction_rate']:.2f}`, final tick `{row['mean_final_tick']:.1f}`, matured `{row['mean_matured_children']:.1f}`"
        )

    lines.extend(
        [
            "",
            "## Second-Wave Diagnostic Notes",
            "",
            "ตัวชี้วัดสำคัญใน suite นี้คือ `mean_gen1_births` และ `second_wave_success_rate`. ถ้า H ใดเพิ่ม final tick หรือ stored food แต่ไม่เพิ่ม gen-1 births แปลว่ายังเป็น wealth/survival effect ไม่ใช่ reproduction-chain fix.",
            "",
            "## Interaction Notes",
            "",
        ]
    )
    for condition_id in ("i_h12_h13", "i_h12_h14", "i_h13_h17", "i_h14_h15", "i_h16_h17", "i_h1_h11_h14_h17"):
        row = next((item for item in summaries if item["condition_id"] == condition_id), None)
        if row is None:
            continue
        lines.append(
            f"- `{condition_id}`: delta gen1 births vs baseline `{row.get('delta_gen1_births_vs_baseline', 0):.1f}`, "
            f"delta matured `{row.get('delta_matured_vs_baseline', 0):.1f}`, "
            f"extinction `{row['extinction_rate']:.2f}`."
        )

    lines.extend(
        [
            "",
            "## ไฟล์ข้อมูลดิบ",
            "",
            f"- `runs.json`: `{OUTPUT_ROOT / 'runs.json'}`",
            f"- `runs.csv`: `{OUTPUT_ROOT / 'runs.csv'}`",
            f"- `condition_summary.csv`: `{OUTPUT_ROOT / 'condition_summary.csv'}`",
            f"- `female_lifetimes.csv`: `{OUTPUT_ROOT / 'female_lifetimes.csv'}`",
            "",
            "## ข้อจำกัด",
            "",
            "- เป็น diagnostic intervention ผ่าน monkeypatch ในสคริปต์ ไม่ใช่ patch ถาวรของ simulation core.",
            "- sample seeds มีจำกัดเพื่อให้ทดลองครบ H12-H18 ได้ในเวลาสั้น.",
            "- interaction ที่ดีควรถูกนำไปรันซ้ำแบบ publication-grade batch ก่อนสรุปเป็นข้อค้นพบหลัก.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run H12-H18 reproduction-chain diagnostic hypothesis experiments.")
    parser.add_argument("--body-index", type=int, default=14)
    parser.add_argument("--initial-population", type=int, default=250)
    parser.add_argument("--max-population", type=int, default=375)
    parser.add_argument("--max-ticks", type=int, default=1200)
    parser.add_argument("--snapshot-interval", type=int, default=20)
    parser.add_argument("--seeds", type=int, nargs="+", default=[7, 8, 11, 13])
    parser.add_argument("--conditions", nargs="*", default=None, help="Optional condition ids to run.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    conditions = diagnostic_conditions()
    if args.conditions:
        allowed = set(args.conditions)
        conditions = [condition for condition in conditions if condition.condition_id in allowed]
    runs: list[dict[str, object]] = []
    total = len(conditions) * len(args.seeds)
    index = 0
    for condition in conditions:
        for seed in args.seeds:
            index += 1
            print(f"[{index}/{total}] {condition.condition_id} seed={seed}", flush=True)
            with apply_patches(condition.patches):
                run = run_diagnostic_trial(
                    condition=condition,
                    seed=seed,
                    body_index=args.body_index,
                    initial_population=args.initial_population,
                    max_population=args.max_population,
                    max_ticks=args.max_ticks,
                    snapshot_interval=args.snapshot_interval,
                )
            runs.append(run)
    summaries = summarize_conditions(runs)
    write_outputs(runs, summaries, args)
    print(f"Wrote {OUTPUT_ROOT}", flush=True)
    print(f"Wrote {REPORT_PATH}", flush=True)


if __name__ == "__main__":
    main()
