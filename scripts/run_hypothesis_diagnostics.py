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


OUTPUT_ROOT = PROJECT_ROOT / "data" / "hypothesis_diagnostics" / "h1_h11_2026-06-03"
REPORT_PATH = PROJECT_ROOT / "reports" / "hypothesis_diagnostics_h1_h11_2026-06-03.md"


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
}


def diagnostic_conditions() -> list[DiagnosticCondition]:
    return [
        DiagnosticCondition("baseline", "baseline", "Current baseline", "No diagnostic intervention."),
        DiagnosticCondition("h1_breeder_tuned", "H1", "Breeder-priority tuning", "Lower breeder reserve, raise general reserve, and protect adult-female personal floor.", ("h1_breeder_tuned",)),
        DiagnosticCondition("h2_canonical_household", "H2", "Canonical household owner", "Prefer shared/parent household owner for store/withdraw/reproduction access.", ("h2_canonical_household",)),
        DiagnosticCondition("h3_pipeline_priority", "H3", "Juvenile/new-adult pipeline", "Give low-energy juveniles and newly adult agents limited household withdrawal.", ("h3_pipeline_priority",)),
        DiagnosticCondition("h4_mate_rendezvous", "H4", "Mate/nest rendezvous", "Bias adult males and mate-seeking females back to nest rendezvous.", ("h4_mate_rendezvous",)),
        DiagnosticCondition("h5_soft_cooldown", "H5", "Soft reproduction cooldown", "Shorten post-birth cooldown to test cohort/lifetime opportunity limits.", ("h5_soft_cooldown",)),
        DiagnosticCondition("h6_earned_nest_support", "H6", "Earned active nest support", "Lower initial nest seed food and only support active nests.", ("h6_earned_nest_support",)),
        DiagnosticCondition("h7_managed_patch_productivity", "H7", "Managed patch productivity", "Make tended food patches easier to create as active settlement productivity.", ("h7_managed_patch_productivity",)),
        DiagnosticCondition("h8_adult_energy_saver", "H8", "Adult near-nest energy saver", "Reduce adult near-nest drain for settlement roles.", ("h8_adult_energy_saver",)),
        DiagnosticCondition("h9_disable_mutation", "H9", "Mutation disabled probe", "Disable inherited mutation to see whether current mutation is helping or adding noise.", ("h9_disable_mutation",)),
        DiagnosticCondition("h10_delay_technology", "H10", "Delay hearth/technology", "Delay hearth and object experimentation until settlement buffers exist.", ("h10_delay_technology",)),
        DiagnosticCondition("h11_extend_reproductive_life", "H11", "Extend reproductive opportunity", "Shorten development and extend adult reproductive life to test lifetime opportunity bottleneck.", ("h11_extend_reproductive_life",)),
        DiagnosticCondition("i_h1_h11", "Interaction", "H1 + H11", "Breeder allocation tuning plus longer reproductive life.", ("h1_breeder_tuned", "h11_extend_reproductive_life")),
        DiagnosticCondition("i_h2_h4_h11", "Interaction", "H2 + H4 + H11", "Canonical household owner plus mate rendezvous plus longer reproductive life.", ("h2_canonical_household", "h4_mate_rendezvous", "h11_extend_reproductive_life")),
        DiagnosticCondition("i_h6_h7", "Interaction", "H6 + H7", "Earned support plus active patch productivity.", ("h6_earned_nest_support", "h7_managed_patch_productivity")),
        DiagnosticCondition(
            "i_reproduction_stack",
            "Interaction",
            "Reproduction stack",
            "H1+H2+H3+H4+H5+H8+H11 combined without adding global food.",
            (
                "h1_breeder_tuned",
                "h2_canonical_household",
                "h3_pipeline_priority",
                "h4_mate_rendezvous",
                "h5_soft_cooldown",
                "h8_adult_energy_saver",
                "h11_extend_reproductive_life",
            ),
        ),
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
    repro_block_reasons: Counter[str] = Counter()
    event_counts: Counter[str] = Counter()
    owner_mismatch_samples = 0
    owner_mismatch_count = 0
    active_nest_food_samples: list[int] = []
    abandoned_nest_food_samples: list[int] = []

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
                reason = str(agent.reproduction_debug.get("reason", "unknown"))
                if reason and reason != "ready":
                    for part in reason.split("|"):
                        repro_block_reasons[part] += 1
            if (
                agent.alive
                and agent.parent_id is not None
                and agent.age >= agent_mod.ADULT_AGE
                and agent.agent_id not in matured_children
            ):
                matured_children.add(agent.agent_id)
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
                for _child_index in range(litter_size):
                    child = agent.spawn_child(next_agent_id, rng, env, mate=mate)
                    child_parent[child.agent_id] = agent.agent_id
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
        "first_matured_child_tick": first_matured_child_tick,
        "first_technology_tick": first_technology_tick,
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


def safe_div(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def mean(values: Iterable[float]) -> float:
    data = list(values)
    return round(statistics.fmean(data), 6) if data else 0.0


def median(values: Iterable[float]) -> float:
    data = list(values)
    return round(statistics.median(data), 6) if data else 0.0


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
        "first_matured_child_tick",
        "first_technology_tick",
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
    best_opportunity = sorted(summaries, key=lambda row: float(row["mean_opportunity_windows"]), reverse=True)[:5]
    worst_extinct = sorted(summaries, key=lambda row: (float(row["extinction_rate"]), -float(row["mean_final_tick"])), reverse=True)[:5]

    lines: list[str] = [
        "# รายงานผลทดลอง H1-H11 Diagnostic Suite",
        "",
        "จัดทำอัตโนมัติจาก `scripts/run_hypothesis_diagnostics.py`",
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
        "การทดลองนี้เป็น diagnostic sweep เพื่อเทียบผลเชิงกลไก ไม่ใช่ final publication-grade confirmation. ใช้ seed set เดียวกันทุก condition เพื่อดูทิศทางของผลและ interaction ระหว่างสมมุติฐาน.",
        "",
        "## ตารางสรุป condition",
        "",
        "| Condition | H | Extinct | Final Tick | Final Pop | Births | Matured | Max Gen | Opp/Female | Birth/Female | Matured Female/Female | Stored | Owner Mismatch |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summaries:
        lines.append(
            f"| `{row['condition_id']}` | {row['hypothesis']} | {row['extinction_rate']:.2f} | "
            f"{row['mean_final_tick']:.1f} | {row['mean_final_population']:.1f} | "
            f"{row['mean_total_births']:.1f} | {row['mean_matured_children']:.1f} | "
            f"{row['mean_max_generation']:.1f} | {row['mean_opportunity_windows']:.2f} | "
            f"{row['mean_births_per_adult_female']:.3f} | {row['mean_matured_female_children_per_adult_female']:.3f} | "
            f"{row['mean_stored_food_total']:.1f} | {row['mean_owner_mismatch_rate']:.3f} |"
        )

    lines.extend(["", "## อ่านผลเร็ว", ""])
    if baseline:
        lines.extend(
            [
                f"- Baseline มี mean final tick `{baseline['mean_final_tick']:.1f}`, births `{baseline['mean_total_births']:.1f}`, matured `{baseline['mean_matured_children']:.1f}`, opportunity windows/female `{baseline['mean_opportunity_windows']:.2f}`.",
                f"- Share adult females below 2 opportunities ใน baseline = `{baseline['share_adult_females_below_2_opportunities']:.2f}`.",
            ]
        )
    lines.append("- เงื่อนไขที่ matured children สูงสุด:")
    for row in best_matured:
        lines.append(
            f"  - `{row['condition_id']}`: matured `{row['mean_matured_children']:.1f}`, births `{row['mean_total_births']:.1f}`, opp/female `{row['mean_opportunity_windows']:.2f}`"
        )
    lines.append("- เงื่อนไขที่เพิ่ม opportunity windows สูงสุด:")
    for row in best_opportunity:
        lines.append(
            f"  - `{row['condition_id']}`: opp/female `{row['mean_opportunity_windows']:.2f}`, matured `{row['mean_matured_children']:.1f}`"
        )
    lines.append("- เงื่อนไขที่ collapse/สูญพันธุ์เด่น:")
    for row in worst_extinct:
        lines.append(
            f"  - `{row['condition_id']}`: extinction `{row['extinction_rate']:.2f}`, final tick `{row['mean_final_tick']:.1f}`, matured `{row['mean_matured_children']:.1f}`"
        )

    lines.extend(
        [
            "",
            "## Reproduction Opportunity Bottleneck",
            "",
            "ตัวชี้วัดสำคัญใน suite นี้คือ `mean_opportunity_windows`: จำนวนหน้าต่างโอกาส reproduction ต่อ adult female lifetime โดยประมาณ. ถ้าค่านี้ต่ำกว่า 2 และ `matured_female_children_per_adult_female` ต่ำกว่า 1 แปลว่าระบบมี fertility ceiling แม้ stored food จะสูง.",
            "",
            "## Interaction Notes",
            "",
        ]
    )
    for condition_id in ("i_h1_h11", "i_h2_h4_h11", "i_h6_h7", "i_reproduction_stack"):
        row = next((item for item in summaries if item["condition_id"] == condition_id), None)
        if row is None:
            continue
        lines.append(
            f"- `{condition_id}`: delta matured vs baseline `{row.get('delta_matured_vs_baseline', 0):.1f}`, "
            f"delta opportunities `{row.get('delta_opportunity_windows_vs_baseline', 0):.2f}`, "
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
            "- sample seeds มีจำกัดเพื่อให้ทดลองครบ H1-H11 ได้ในเวลาสั้น.",
            "- interaction ที่ดีควรถูกนำไปรันซ้ำแบบ publication-grade batch ก่อนสรุปเป็นข้อค้นพบหลัก.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run H1-H11 diagnostic hypothesis experiments.")
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
