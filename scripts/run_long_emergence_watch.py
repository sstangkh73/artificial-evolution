from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from random import Random
import sys
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.agent import Agent
from agents.body import generate_candidate_body_plans
from simulation.runner import (
    FOUNDER_START_AGE,
    _detect_emergent_technology_events,
    _lineage_label,
    _occupied_nest_owner_ids,
    _spawn_initial_positions,
    _update_social_groups,
)
from world.environment import Environment

SAMPLED_EVENT_KINDS = {
    "build_nest",
    "tend_food_patch",
    "food_patch_tended",
    "plant_lifecycle_food_consumed",
    "plant_lifecycle_food_decayed",
    "natural_seed_dropped",
    "seed_germinated",
    "seed_buried_by_disturbance",
    "plant_matured",
    "plant_fruited",
    "plant_died",
    "harvest_seed_dropped",
    "seed_picked",
    "seed_dropped",
    "technology_emerged",
    "materialized_scaffold_nest",
}


def _event_type(event_text: str) -> str:
    return event_text.split(" ->", 1)[0].strip()


def _event_position(event_text: str) -> tuple[int, int] | None:
    x_value: int | None = None
    y_value: int | None = None
    for token in event_text.replace(",", " ").split():
        if token.startswith("x="):
            try:
                x_value = int(float(token.split("=", 1)[1]))
            except ValueError:
                continue
        elif token.startswith("y="):
            try:
                y_value = int(float(token.split("=", 1)[1]))
            except ValueError:
                continue
    if x_value is None or y_value is None:
        return None
    return (x_value, y_value)


def _event_field(event_text: str, field_name: str) -> str | None:
    prefix = f"{field_name}="
    for token in event_text.replace(",", " ").split():
        if token.startswith(prefix):
            return token.split("=", 1)[1]
    return None


def _event_float(event_text: str, field_name: str) -> float | None:
    value = _event_field(event_text, field_name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _event_int(event_text: str, field_name: str) -> int | None:
    value = _event_field(event_text, field_name)
    if value is None:
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def _numeric_summary(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {}
    return {
        "count": len(values),
        "mean": round(sum(values) / len(values), 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def _top_event_locations(
    event_location_counts: dict[str, Counter[tuple[int, int]]],
    limit: int = 8,
) -> dict[str, list[dict[str, int]]]:
    return {
        event_type: [
            {"x": position[0], "y": position[1], "count": count}
            for position, count in counter.most_common(limit)
        ]
        for event_type, counter in sorted(event_location_counts.items())
        if counter
    }


def _plant_lifecycle_food_summary(env: Environment, event_counts: Counter[str]) -> dict[str, int]:
    return {
        "remaining": sum(1 for resource in env.food_positions.values() if resource.source == "plant_lifecycle"),
        "consumed": event_counts["plant_lifecycle_food_consumed"],
        "decayed": event_counts["plant_lifecycle_food_decayed"],
        "fruited": event_counts["plant_fruited"],
    }


def _plant_origin_summary(env: Environment) -> dict[str, int]:
    summary: Counter[str] = Counter()
    for plant in env.plant_seeds.values():
        mode = plant.dispersal_mode or "unknown"
        summary[mode] += 1
        summary[f"{mode}_{plant.state}"] += 1
        if plant.carried_by_agent_id is not None:
            summary[f"{mode}_carried"] += 1
    return dict(summary)


def _count_plants_near(env: Environment, x: int, y: int, radius: int, state: str | None = None) -> int:
    return sum(
        1
        for plant in env.plant_seeds.values()
        if (state is None or plant.state == state)
        and abs(plant.x - x) + abs(plant.y - y) <= radius
    )


def _count_food_source_near(env: Environment, x: int, y: int, radius: int, source: str) -> int:
    return sum(
        1
        for (food_x, food_y), resource in env.food_positions.items()
        if resource.source == source and abs(food_x - x) + abs(food_y - y) <= radius
    )


def _managed_patch_count_near(env: Environment, x: int, y: int, radius: int) -> int:
    count = 0
    for patch_y in range(max(0, y - radius), min(env.height, y + radius + 1)):
        for patch_x in range(max(0, x - radius), min(env.width, x + radius + 1)):
            if abs(patch_x - x) + abs(patch_y - y) <= radius and env.managed_food_map[patch_y][patch_x] >= 0.14:
                count += 1
    return count


def _visit_count_near(
    visit_counter: Counter[tuple[int, int]],
    x: int,
    y: int,
    radius: int,
) -> int:
    total = 0
    for (visit_x, visit_y), visits in visit_counter.items():
        if abs(visit_x - x) + abs(visit_y - y) <= radius:
            total += visits
    return total


def _bounded_manhattan_area(width: int, height: int, x: int, y: int, radius: int) -> int:
    area = 0
    for area_y in range(max(0, y - radius), min(height, y + radius + 1)):
        for area_x in range(max(0, x - radius), min(width, x + radius + 1)):
            if abs(area_x - x) + abs(area_y - y) <= radius:
                area += 1
    return area


def _top_agent_counts(counter: Counter[int], limit: int = 8) -> list[dict[str, int]]:
    return [
        {"agent": agent_id, "count": count}
        for agent_id, count in counter.most_common(limit)
    ]


def _round_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 5)


def _round_lift(numerator_rate: float, denominator_rate: float) -> float | None:
    if denominator_rate <= 0:
        return None
    return round(numerator_rate / denominator_rate, 3)


def _evaluate_signals(
    env: Environment,
    visit_counter: Counter[tuple[int, int]],
    event_counts: Counter[str],
) -> list[dict[str, object]]:
    signals: list[dict[str, object]] = []

    if event_counts["build_nest"] > 0:
        signals.append(
            {
                "type": "scaffold_nest_detected",
                "confidence": "high",
                "stop_candidate": False,
                "reason": "Agent emitted the existing high-level build_nest action.",
                "count": event_counts["build_nest"],
            }
        )

    if event_counts["plant_matured"] > 0 and event_counts["plant_fruited"] > 0:
        signals.append(
            {
                "type": "plant_lifecycle_breakthrough",
                "confidence": "medium",
                "stop_candidate": False,
                "plant_matured": event_counts["plant_matured"],
                "plant_fruited": event_counts["plant_fruited"],
                "seed_buried_by_disturbance": event_counts["seed_buried_by_disturbance"],
                "seed_germinated": event_counts["seed_germinated"],
                "reason": "A seed produced through harvest and burial-by-disturbance reached mature/fruiting plant lifecycle without oracle or farm scaffolds.",
            }
        )

    if event_counts["plant_lifecycle_food_consumed"] > 0 or event_counts["plant_lifecycle_food_decayed"] > 0:
        signals.append(
            {
                "type": "plant_lifecycle_food_fate_observed",
                "confidence": "high",
                "stop_candidate": True,
                "plant_lifecycle_food_consumed": event_counts["plant_lifecycle_food_consumed"],
                "plant_lifecycle_food_decayed": event_counts["plant_lifecycle_food_decayed"],
                "plant_fruited": event_counts["plant_fruited"],
                "reason": "At least one plant-lifecycle food item reached an observed fate: consumed by an agent or decayed in the world.",
            }
        )

    for owner_id, nest in env.nests.items():
        mature_near = _count_plants_near(env, nest.x, nest.y, radius=5, state="mature")
        plant_food_near = _count_food_source_near(env, nest.x, nest.y, radius=5, source="plant_lifecycle")
        managed_patches = _managed_patch_count_near(env, nest.x, nest.y, radius=5)
        visits_near = _visit_count_near(visit_counter, nest.x, nest.y, radius=5)
        stored_materials = sum(nest.material_storage.values())

        if event_counts["tend_food_patch"] >= 3 and managed_patches >= 2:
            signals.append(
                {
                    "type": "scaffold_farm_detected",
                    "confidence": "high_for_scaffold_low_for_emergence",
                    "stop_candidate": False,
                    "owner_id": owner_id,
                    "x": nest.x,
                    "y": nest.y,
                    "tend_food_patch_events": event_counts["tend_food_patch"],
                    "managed_patches_near": managed_patches,
                    "mature_plants_near": mature_near,
                    "plant_lifecycle_food_near": plant_food_near,
                    "visits_near": visits_near,
                    "reason": "Repeated high-level tend_food_patch action made a managed food area near a nest; recorded but not used as substrate-first stopping evidence.",
                }
            )

        if mature_near >= 6 and plant_food_near >= 1 and visits_near >= 250:
            signals.append(
                {
                    "type": "substrate_farm_candidate",
                    "confidence": "medium",
                    "stop_candidate": True,
                    "owner_id": owner_id,
                    "x": nest.x,
                    "y": nest.y,
                    "mature_plants_near": mature_near,
                    "plant_lifecycle_food_near": plant_food_near,
                    "visits_near": visits_near,
                    "reason": "Plant lifecycle food and mature plants clustered near a repeatedly used agent area.",
                }
            )

        if stored_materials >= 18 and nest.object_storage:
            signals.append(
                {
                    "type": "materialized_scaffold_nest",
                    "confidence": "medium_for_scaffold_low_for_substrate",
                    "stop_candidate": True,
                    "owner_id": owner_id,
                    "x": nest.x,
                    "y": nest.y,
                    "stored_materials": stored_materials,
                    "stored_objects": len(nest.object_storage),
                    "reason": "A high-level nest accumulated raw materials and physical objects.",
                }
            )

    for (hot_x, hot_y), visits in visit_counter.most_common(20):
        if visits < 350:
            continue
        mature_near = _count_plants_near(env, hot_x, hot_y, radius=4, state="mature")
        plant_food_near = _count_food_source_near(env, hot_x, hot_y, radius=4, source="plant_lifecycle")
        if mature_near >= 8 and plant_food_near >= 1:
            signals.append(
                {
                    "type": "substrate_farm_hotspot_candidate",
                    "confidence": "low_to_medium",
                    "stop_candidate": True,
                    "x": hot_x,
                    "y": hot_y,
                    "visits": visits,
                    "mature_plants_near": mature_near,
                    "plant_lifecycle_food_near": plant_food_near,
                    "reason": "A heavily visited cell overlaps a cluster of mature plants and plant lifecycle food.",
                }
            )

    return signals


def _affect_summary(agents: list[Agent]) -> dict[str, float | int]:
    alive_agents = [agent for agent in agents if agent.alive]
    if not alive_agents:
        return {
            "mean_safety_feeling": 0.0,
            "mean_comfort_level": 0.0,
            "mean_fear_level": 0.0,
            "mean_hunger_level": 0.0,
            "mean_pair_bond_ticks": 0.0,
            "affect_ready_adults": 0,
        }
    ready_adults = sum(
        1
        for agent in alive_agents
        if agent.current_stage == "adult"
        and agent.safety_feeling >= 0.66
        and agent.comfort_level >= 0.58
        and agent.hunger_level < 0.35
        and agent.fear_level < 0.42
        and agent.safety_streak_ticks >= 10
        and agent.pair_bond_ticks >= 14
    )
    return {
        "mean_safety_feeling": round(sum(agent.safety_feeling for agent in alive_agents) / len(alive_agents), 3),
        "mean_comfort_level": round(sum(agent.comfort_level for agent in alive_agents) / len(alive_agents), 3),
        "mean_fear_level": round(sum(agent.fear_level for agent in alive_agents) / len(alive_agents), 3),
        "mean_hunger_level": round(sum(agent.hunger_level for agent in alive_agents) / len(alive_agents), 3),
        "mean_pair_bond_ticks": round(sum(agent.pair_bond_ticks for agent in alive_agents) / len(alive_agents), 3),
        "affect_ready_adults": ready_adults,
    }


def _agent_state_summary(agents: list[Agent]) -> dict[str, object]:
    alive_agents = [agent for agent in agents if agent.alive]
    adult_females = [
        agent
        for agent in alive_agents
        if agent.sex == "female" and agent.current_stage == "adult"
    ]
    reason_counter = Counter(
        str(agent.reproduction_debug.get("reason", "not_checked"))
        for agent in adult_females
    )
    return {
        "instinct_states": dict(Counter(agent.instinct_state for agent in alive_agents)),
        "adult_female_reproduction_reasons": dict(reason_counter.most_common(8)),
        "max_safety_feeling": round(max((agent.safety_feeling for agent in alive_agents), default=0.0), 3),
        "max_comfort_level": round(max((agent.comfort_level for agent in alive_agents), default=0.0), 3),
        "max_attachment_level": round(max((agent.attachment_level for agent in alive_agents), default=0.0), 3),
        "max_pair_bond_ticks": max((agent.pair_bond_ticks for agent in alive_agents), default=0),
        "max_safety_streak_ticks": max((agent.safety_streak_ticks for agent in alive_agents), default=0),
    }


def run_watch(args: argparse.Namespace) -> dict[str, object]:
    rng = Random(args.seed)
    bodies = generate_candidate_body_plans()
    body_index = max(1, min(args.body_index, len(bodies)))
    body = bodies[body_index - 1]
    env = Environment(
        width=args.width,
        height=args.height,
        max_food=args.max_food,
        base_food_spawn_per_tick=args.base_food_spawn_per_tick,
        food_spawn_multiplier=args.food_spawn_multiplier,
        bootstrap_food_spawn_ticks=args.bootstrap_food_spawn_ticks,
        wild_food_spawn_after_bootstrap_multiplier=args.wild_food_spawn_after_bootstrap_multiplier,
        natural_seed_rain_per_tick=args.natural_seed_rain_per_tick,
        max_plant_seeds=args.max_plant_seeds,
        large_animal_spawn_per_tick=args.large_animal_spawn_per_tick,
        max_large_animals=args.max_large_animals,
        nest_support_food_chance=args.nest_support_food_chance,
        nest_support_spawn_chance=args.nest_support_spawn_chance,
        frontier_band=args.frontier_band,
        global_food_decline_per_day=args.global_food_decline_per_day,
        minimum_global_food_multiplier=args.minimum_global_food_multiplier,
        ambient_food_decay_chance=args.ambient_food_decay_chance,
        plant_food_decay_chance=args.plant_food_decay_chance,
        plant_seed_max_age_multiplier=args.plant_seed_max_age_multiplier,
        plant_growth_rate_multiplier=args.plant_growth_rate_multiplier,
        sprout_biomass_loss_multiplier=args.sprout_biomass_loss_multiplier,
        germination_good_ticks_multiplier=args.germination_good_ticks_multiplier,
        plant_fruiting_interval_multiplier=args.plant_fruiting_interval_multiplier,
        plant_fruiting_growth_threshold_multiplier=args.plant_fruiting_growth_threshold_multiplier,
        plant_fruiting_chance_multiplier=args.plant_fruiting_chance_multiplier,
        natural_seed_drop_chance_multiplier=args.natural_seed_drop_chance_multiplier,
    )
    founder_sexes = ["male"] * (args.initial_population // 2) + ["female"] * (
        args.initial_population - (args.initial_population // 2)
    )
    spawn_positions = _spawn_initial_positions(
        env,
        rng,
        args.initial_population,
        body,
        strategy=args.spawn_strategy,
    )
    agents = [
        Agent(
            agent_id=agent_id,
            body=body,
            x=spawn_x,
            y=spawn_y,
            age=FOUNDER_START_AGE,
            lineage_id=_lineage_label(agent_id),
            sex=founder_sexes[agent_id],
            generation=0,
            immortal=args.immortal,
        )
        for agent_id, (spawn_x, spawn_y) in enumerate(spawn_positions)
    ]

    next_agent_id = len(agents)
    seen_groups: set[frozenset[int]] = set()
    event_counts: Counter[str] = Counter()
    event_location_counts: dict[str, Counter[tuple[int, int]]] = {
        "harvest_seed_dropped": Counter(),
        "natural_seed_dropped": Counter(),
        "seed_picked": Counter(),
        "seed_dropped": Counter(),
        "seed_buried_by_disturbance": Counter(),
        "seed_germinated": Counter(),
        "plant_matured": Counter(),
        "plant_fruited": Counter(),
        "plant_died": Counter(),
        "plant_lifecycle_food_consumed": Counter(),
        "plant_lifecycle_food_decayed": Counter(),
    }
    visit_counter: Counter[tuple[int, int]] = Counter()
    first_event_tick: dict[str, int] = {}
    event_samples: list[str] = []
    event_samples_by_kind: dict[str, list[str]] = {kind: [] for kind in SAMPLED_EVENT_KINDS}
    event_attribute_counts: dict[str, Counter[str]] = {
        "plant_died_reason": Counter(),
        "plant_died_mode": Counter(),
        "natural_seed_distance": Counter(),
    }
    event_numeric_values: dict[str, list[float]] = {
        "plant_died_age_ticks": [],
        "plant_died_biomass": [],
        "plant_died_water": [],
        "plant_died_temp_k": [],
        "plant_died_light": [],
        "plant_died_nutrients": [],
        "plant_died_growth": [],
    }
    reward_records: list[dict[str, int]] = []
    next_reward_record_id = 0
    reward_counts_by_agent: Counter[int] = Counter()
    owner_revisit_tick_hits = 0
    owner_revisit_opportunities = 0
    random_expected_owner_hits = 0.0
    owner_revisited_reward_ids: set[int] = set()
    owner_revisit_agents: set[int] = set()
    owner_revisit_ticks_by_agent: Counter[int] = Counter()
    owner_revisited_rewards_by_agent: Counter[int] = Counter()
    first_owner_revisit_tick: int | None = None
    owner_return_tick_hits = 0
    owner_return_opportunities = 0
    random_expected_owner_return_hits = 0.0
    owner_returned_reward_ids: set[int] = set()
    owner_return_agents: set[int] = set()
    owner_return_ticks_by_agent: Counter[int] = Counter()
    owner_returned_rewards_by_agent: Counter[int] = Counter()
    first_owner_return_tick: int | None = None
    seed_records: dict[int, dict[str, object]] = {}
    agent_moved_seed_ids: set[int] = set()
    moved_seed_agents: set[int] = set()
    same_agent_seed_food_chain_ids: set[int] = set()
    agent_moved_seed_chain_ids: set[int] = set()
    agent_moved_seed_chain_agents: set[int] = set()
    control_seed_chain_ids: set[int] = set()
    total_births = 0
    peak_population = len(agents)
    stop_reason = "max_ticks_reached"
    stop_signals: list[dict[str, object]] = []
    started = time.monotonic()
    next_progress_at = started
    phase3_min_seed_move_distance = getattr(args, "phase3_min_seed_move_distance", 1)

    def seed_record(seed_id: int) -> dict[str, object]:
        record = seed_records.get(seed_id)
        if record is None:
            record = {
                "seed_id": seed_id,
                "source_kind": "unknown",
                "origin_mode": "unknown",
                "parent_seed_id": None,
                "origin_x": None,
                "origin_y": None,
                "created_tick": None,
                "pick_count": 0,
                "first_picked_by_agent": None,
                "first_pick_tick": None,
                "first_pick_x": None,
                "first_pick_y": None,
                "last_picked_by_agent": None,
                "last_pick_tick": None,
                "last_pick_x": None,
                "last_pick_y": None,
                "drop_count": 0,
                "first_dropped_by_agent": None,
                "first_drop_tick": None,
                "first_drop_x": None,
                "first_drop_y": None,
                "last_dropped_by_agent": None,
                "last_drop_tick": None,
                "last_drop_x": None,
                "last_drop_y": None,
                "max_move_distance": 0,
                "agent_moved": False,
                "moved_by_agent": None,
                "buried_tick": None,
                "germinated_tick": None,
                "matured_tick": None,
                "first_fruited_tick": None,
                "fruit_count": 0,
                "first_consumed_tick": None,
                "consumed_count": 0,
                "consumed_by_agents": set(),
                "decayed_count": 0,
                "death_tick": None,
                "death_reason": None,
            }
            seed_records[seed_id] = record
        return record

    def learning_metrics_summary() -> dict[str, object]:
        parsed_reward_events = sum(reward_counts_by_agent.values())
        owner_revisited_reward_events = len(owner_revisited_reward_ids)
        owner_revisit_lift = None
        if random_expected_owner_hits > 0:
            owner_revisit_lift = round(owner_revisit_tick_hits / random_expected_owner_hits, 3)
        owner_returned_reward_events = len(owner_returned_reward_ids)
        owner_return_lift = None
        if random_expected_owner_return_hits > 0:
            owner_return_lift = round(owner_return_tick_hits / random_expected_owner_return_hits, 3)
        owner_revisit_tick_rate = 0.0
        random_expected_owner_hit_rate = 0.0
        if owner_revisit_opportunities > 0:
            owner_revisit_tick_rate = round(owner_revisit_tick_hits / owner_revisit_opportunities, 5)
            random_expected_owner_hit_rate = round(random_expected_owner_hits / owner_revisit_opportunities, 5)
        owner_return_tick_rate = 0.0
        random_expected_owner_return_hit_rate = 0.0
        if owner_return_opportunities > 0:
            owner_return_tick_rate = round(owner_return_tick_hits / owner_return_opportunities, 5)
            random_expected_owner_return_hit_rate = round(random_expected_owner_return_hits / owner_return_opportunities, 5)
        owner_revisited_reward_fraction = 0.0
        owner_returned_reward_fraction = 0.0
        if parsed_reward_events > 0:
            owner_revisited_reward_fraction = round(owner_revisited_reward_events / parsed_reward_events, 5)
            owner_returned_reward_fraction = round(owner_returned_reward_events / parsed_reward_events, 5)
        return {
            "revisit_radius": args.learning_revisit_radius,
            "revisit_min_delay_ticks": args.learning_revisit_min_delay_ticks,
            "revisit_max_age_ticks": args.learning_revisit_max_age_ticks,
            "reward_memory_limit": args.learning_reward_memory_limit,
            "plant_food_reward_events": event_counts["plant_lifecycle_food_consumed"],
            "parsed_reward_events": parsed_reward_events,
            "rewarded_agents": len(reward_counts_by_agent),
            "active_reward_records": len(reward_records),
            "owner_revisit_opportunities": owner_revisit_opportunities,
            "owner_revisit_tick_hits": owner_revisit_tick_hits,
            "random_expected_owner_hits": round(random_expected_owner_hits, 3),
            "owner_revisit_lift": owner_revisit_lift,
            "owner_revisit_tick_rate": owner_revisit_tick_rate,
            "random_expected_owner_hit_rate": random_expected_owner_hit_rate,
            "owner_revisited_reward_events": owner_revisited_reward_events,
            "owner_revisited_reward_fraction": owner_revisited_reward_fraction,
            "owner_revisit_agents": len(owner_revisit_agents),
            "first_owner_revisit_tick": first_owner_revisit_tick,
            "top_reward_agents": _top_agent_counts(reward_counts_by_agent),
            "top_owner_revisit_tick_agents": _top_agent_counts(owner_revisit_ticks_by_agent),
            "top_owner_revisited_reward_agents": _top_agent_counts(owner_revisited_rewards_by_agent),
            "owner_left_reward_events": sum(
                1 for reward_record in reward_records if reward_record.get("left_tick", -1) >= 0
            ),
            "owner_return_opportunities": owner_return_opportunities,
            "owner_return_tick_hits": owner_return_tick_hits,
            "random_expected_owner_return_hits": round(random_expected_owner_return_hits, 3),
            "owner_return_lift": owner_return_lift,
            "owner_return_tick_rate": owner_return_tick_rate,
            "random_expected_owner_return_hit_rate": random_expected_owner_return_hit_rate,
            "owner_returned_reward_events": owner_returned_reward_events,
            "owner_returned_reward_fraction": owner_returned_reward_fraction,
            "owner_return_agents": len(owner_return_agents),
            "first_owner_return_tick": first_owner_return_tick,
            "top_owner_return_tick_agents": _top_agent_counts(owner_return_ticks_by_agent),
            "top_owner_returned_reward_agents": _top_agent_counts(owner_returned_rewards_by_agent),
        }

    def seed_causality_metrics_summary() -> dict[str, object]:
        records = list(seed_records.values())
        agent_moved_records = [record for record in records if bool(record.get("agent_moved"))]
        control_records = [
            record
            for record in records
            if not bool(record.get("agent_moved"))
            and record.get("source_kind") in {"harvest_seed_dropped", "natural_seed_dropped"}
        ]
        untouched_harvest_records = [
            record
            for record in control_records
            if record.get("source_kind") == "harvest_seed_dropped" and int(record.get("pick_count", 0)) == 0
        ]
        natural_drop_records = [
            record for record in control_records if record.get("source_kind") == "natural_seed_dropped"
        ]

        def count_with(group: list[dict[str, object]], key: str) -> int:
            return sum(1 for record in group if record.get(key) is not None)

        def count_consumed(group: list[dict[str, object]]) -> int:
            return sum(1 for record in group if int(record.get("consumed_count", 0)) > 0)

        def completed_chain(group: list[dict[str, object]]) -> int:
            return sum(
                1
                for record in group
                if record.get("germinated_tick") is not None
                and record.get("matured_tick") is not None
                and record.get("first_fruited_tick") is not None
                and int(record.get("consumed_count", 0)) > 0
            )

        moved_count = len(agent_moved_records)
        control_count = len(control_records)
        moved_completed = completed_chain(agent_moved_records)
        control_completed = completed_chain(control_records)
        moved_consumed_rate = _round_rate(moved_completed, moved_count)
        control_consumed_rate = _round_rate(control_completed, control_count)
        same_agent_completed = sum(
            1
            for record in agent_moved_records
            if record.get("moved_by_agent") in record.get("consumed_by_agents", set())
            and record.get("germinated_tick") is not None
            and record.get("matured_tick") is not None
            and record.get("first_fruited_tick") is not None
        )
        top_moved_agents = Counter(
            int(record["moved_by_agent"])
            for record in agent_moved_records
            if record.get("moved_by_agent") is not None
        )
        top_completed_agents = Counter(
            int(record["moved_by_agent"])
            for record in agent_moved_records
            if record.get("moved_by_agent") is not None
            and record.get("seed_id") in agent_moved_seed_chain_ids
        )
        sample_chains = []
        for record in agent_moved_records:
            if record.get("seed_id") not in agent_moved_seed_chain_ids:
                continue
            sample_chains.append(
                {
                    "seed": record["seed_id"],
                    "agent": record.get("moved_by_agent"),
                    "move_distance": record.get("max_move_distance"),
                    "drop": [record.get("last_drop_x"), record.get("last_drop_y")],
                    "germinated_tick": record.get("germinated_tick"),
                    "matured_tick": record.get("matured_tick"),
                    "first_fruited_tick": record.get("first_fruited_tick"),
                    "first_consumed_tick": record.get("first_consumed_tick"),
                    "consumed_count": record.get("consumed_count"),
                }
            )
            if len(sample_chains) >= 8:
                break
        return {
            "min_seed_move_distance": phase3_min_seed_move_distance,
            "tracked_seed_records": len(records),
            "agent_moved_seed_count": moved_count,
            "agent_moved_seed_agents": len(moved_seed_agents),
            "agent_moved_seed_germinated": count_with(agent_moved_records, "germinated_tick"),
            "agent_moved_seed_matured": count_with(agent_moved_records, "matured_tick"),
            "agent_moved_seed_fruited": count_with(agent_moved_records, "first_fruited_tick"),
            "agent_moved_seed_completed_chains": moved_completed,
            "agent_moved_seed_food_events": sum(int(record.get("consumed_count", 0)) for record in agent_moved_records),
            "agent_moved_seed_chain_agents": len(agent_moved_seed_chain_agents),
            "same_agent_seed_food_chains": same_agent_completed,
            "control_seed_count": control_count,
            "control_seed_germinated": count_with(control_records, "germinated_tick"),
            "control_seed_matured": count_with(control_records, "matured_tick"),
            "control_seed_fruited": count_with(control_records, "first_fruited_tick"),
            "control_seed_completed_chains": control_completed,
            "untouched_harvest_seed_count": len(untouched_harvest_records),
            "untouched_harvest_completed_chains": completed_chain(untouched_harvest_records),
            "natural_drop_seed_count": len(natural_drop_records),
            "natural_drop_completed_chains": completed_chain(natural_drop_records),
            "agent_moved_completed_chain_rate": moved_consumed_rate,
            "control_completed_chain_rate": control_consumed_rate,
            "agent_moved_vs_control_completed_lift": _round_lift(moved_consumed_rate, control_consumed_rate),
            "top_moved_seed_agents": _top_agent_counts(top_moved_agents),
            "top_completed_chain_agents": _top_agent_counts(top_completed_agents),
            "sample_agent_moved_seed_chains": sample_chains,
        }

    print(
        json.dumps(
            {
                "type": "start",
                "seed": args.seed,
                "body_index": body_index,
                "body": body.short_description,
                "initial_population": len(agents),
                "immortal": args.immortal,
                "time_limit_seconds": args.time_limit_seconds,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    for _ in range(args.max_ticks):
        elapsed = time.monotonic() - started
        if elapsed >= args.time_limit_seconds:
            stop_reason = "time_limit_reached"
            break
        if not agents:
            stop_reason = "population_extinct"
            break

        env.set_active_nest_owners(_occupied_nest_owner_ids(env, agents))
        env.step(rng)
        current_tick = env.tick_count
        current_day = current_tick // env.day_length
        tick_events: list[str] = []
        _update_social_groups(agents, tick_events, seen_groups)
        for agent in agents:
            agent.set_survival_context(env, agents)

        newborns: list[Agent] = []
        for agent in list(agents):
            wants_reproduction = agent.tick(env, rng)
            tick_events.extend(agent.pop_recent_events())
            if wants_reproduction and len(agents) + len(newborns) < args.max_population:
                mate = next(
                    (
                        candidate
                        for candidate in agents
                        if candidate.agent_id == agent.reproduction_partner_id and candidate.alive
                    ),
                    None,
                )
                litter_size = min(
                    args.max_population - (len(agents) + len(newborns)),
                    agent.decide_litter_size(env, mate, rng),
                )
                agent.prepare_reproduction(env, mate, litter_size)
                for _ in range(litter_size):
                    child = agent.spawn_child(next_agent_id, rng, env, mate=mate)
                    newborns.append(child)
                    next_agent_id += 1
                total_births += litter_size
                first_event_tick.setdefault("birth", current_tick)
                tick_events.append(
                    f"birth -> tick={current_tick} day={current_day} parent={agent.agent_id} "
                    f"other_parent={mate.agent_id if mate is not None else -1} litter_size={litter_size}"
                )

            if not agent.alive:
                agents.remove(agent)

        agents.extend(newborns)
        peak_population = max(peak_population, len(agents))
        tick_events.extend(env.pop_physics_events())
        tick_events.extend(_detect_emergent_technology_events(env, current_tick, current_day))

        for agent in agents:
            if agent.alive:
                visit_counter[(agent.x, agent.y)] += 1

        alive_positions_by_agent = {
            agent.agent_id: (agent.x, agent.y)
            for agent in agents
            if agent.alive
        }
        active_reward_records: list[dict[str, int]] = []
        for reward_record in reward_records:
            reward_age = current_tick - reward_record["tick"]
            if reward_age > args.learning_revisit_max_age_ticks:
                continue
            owner_position = alive_positions_by_agent.get(reward_record["agent"])
            if owner_position is not None:
                owner_distance = (
                    abs(owner_position[0] - reward_record["x"])
                    + abs(owner_position[1] - reward_record["y"])
                )
                if (
                    reward_age > 0
                    and reward_record.get("left_tick", -1) < 0
                    and owner_distance > args.learning_revisit_radius
                ):
                    reward_record["left_tick"] = current_tick
                if reward_age >= args.learning_revisit_min_delay_ticks:
                    owner_revisit_opportunities += 1
                    random_expected_owner_hits += (
                        _bounded_manhattan_area(
                            env.width,
                            env.height,
                            reward_record["x"],
                            reward_record["y"],
                            args.learning_revisit_radius,
                        )
                        / max(1, env.width * env.height)
                    )
                    if owner_distance <= args.learning_revisit_radius:
                        owner_revisit_tick_hits += 1
                        owner_revisit_ticks_by_agent[reward_record["agent"]] += 1
                        reward_id = reward_record["id"]
                        if reward_id not in owner_revisited_reward_ids:
                            owner_revisited_reward_ids.add(reward_id)
                            owner_revisit_agents.add(reward_record["agent"])
                            owner_revisited_rewards_by_agent[reward_record["agent"]] += 1
                            if first_owner_revisit_tick is None:
                                first_owner_revisit_tick = current_tick
                left_tick = reward_record.get("left_tick", -1)
                if left_tick >= 0 and current_tick - left_tick >= args.learning_revisit_min_delay_ticks:
                    owner_return_opportunities += 1
                    random_expected_owner_return_hits += (
                        _bounded_manhattan_area(
                            env.width,
                            env.height,
                            reward_record["x"],
                            reward_record["y"],
                            args.learning_revisit_radius,
                        )
                        / max(1, env.width * env.height)
                    )
                    if owner_distance <= args.learning_revisit_radius:
                        owner_return_tick_hits += 1
                        owner_return_ticks_by_agent[reward_record["agent"]] += 1
                        reward_id = reward_record["id"]
                        if reward_id not in owner_returned_reward_ids:
                            owner_returned_reward_ids.add(reward_id)
                            owner_return_agents.add(reward_record["agent"])
                            owner_returned_rewards_by_agent[reward_record["agent"]] += 1
                            if first_owner_return_tick is None:
                                first_owner_return_tick = current_tick
            active_reward_records.append(reward_record)
        reward_records = active_reward_records

        for event in tick_events:
            kind = _event_type(event)
            event_counts[kind] += 1
            first_event_tick.setdefault(kind, current_tick)
            position = _event_position(event)
            if position is not None and kind in event_location_counts:
                event_location_counts[kind][position] += 1
            if kind == "plant_died":
                seed_id = _event_int(event, "seed")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    record["death_tick"] = current_tick
                    record["death_reason"] = _event_field(event, "reason") or "unknown"
                event_attribute_counts["plant_died_reason"][_event_field(event, "reason") or "unknown"] += 1
                event_attribute_counts["plant_died_mode"][_event_field(event, "mode") or "unknown"] += 1
                for field_name in ("age_ticks", "biomass", "water", "temp_k", "light", "nutrients", "growth"):
                    value = _event_float(event, field_name)
                    if value is not None:
                        event_numeric_values[f"plant_died_{field_name}"].append(value)
            elif kind == "harvest_seed_dropped":
                seed_id = _event_int(event, "seed")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    record["source_kind"] = kind
                    record["origin_mode"] = _event_field(event, "mode") or "harvest_drop"
                    record["parent_seed_id"] = _event_int(event, "parent")
                    record["created_tick"] = current_tick
                    if position is not None:
                        record["origin_x"] = position[0]
                        record["origin_y"] = position[1]
            elif kind == "natural_seed_dropped":
                seed_id = _event_int(event, "seed")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    record["source_kind"] = kind
                    record["origin_mode"] = _event_field(event, "mode") or "natural_drop"
                    record["parent_seed_id"] = _event_int(event, "parent")
                    record["created_tick"] = current_tick
                    if position is not None:
                        record["origin_x"] = position[0]
                        record["origin_y"] = position[1]
                event_attribute_counts["natural_seed_distance"][_event_field(event, "distance") or "unknown"] += 1
            elif kind == "seed_picked":
                seed_id = _event_int(event, "seed")
                agent_id = _event_int(event, "agent")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    record["pick_count"] = int(record.get("pick_count", 0)) + 1
                    if record.get("first_pick_tick") is None:
                        record["first_picked_by_agent"] = agent_id
                        record["first_pick_tick"] = current_tick
                        if position is not None:
                            record["first_pick_x"] = position[0]
                            record["first_pick_y"] = position[1]
                    record["last_picked_by_agent"] = agent_id
                    record["last_pick_tick"] = current_tick
                    if position is not None:
                        record["last_pick_x"] = position[0]
                        record["last_pick_y"] = position[1]
            elif kind == "seed_dropped":
                seed_id = _event_int(event, "seed")
                agent_id = _event_int(event, "agent")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    record["drop_count"] = int(record.get("drop_count", 0)) + 1
                    if record.get("first_drop_tick") is None:
                        record["first_dropped_by_agent"] = agent_id
                        record["first_drop_tick"] = current_tick
                        if position is not None:
                            record["first_drop_x"] = position[0]
                            record["first_drop_y"] = position[1]
                    record["last_dropped_by_agent"] = agent_id
                    record["last_drop_tick"] = current_tick
                    if position is not None:
                        record["last_drop_x"] = position[0]
                        record["last_drop_y"] = position[1]
                        pick_x = record.get("last_pick_x")
                        pick_y = record.get("last_pick_y")
                        if isinstance(pick_x, int) and isinstance(pick_y, int):
                            move_distance = abs(position[0] - pick_x) + abs(position[1] - pick_y)
                            record["max_move_distance"] = max(int(record.get("max_move_distance", 0)), move_distance)
                            if move_distance >= phase3_min_seed_move_distance:
                                record["agent_moved"] = True
                                record["moved_by_agent"] = agent_id
                                agent_moved_seed_ids.add(seed_id)
                                if agent_id is not None:
                                    moved_seed_agents.add(agent_id)
            elif kind == "seed_buried_by_disturbance":
                seed_id = _event_int(event, "seed")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    record["buried_tick"] = current_tick
            elif kind == "seed_germinated":
                seed_id = _event_int(event, "seed")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    record["germinated_tick"] = current_tick
            elif kind == "plant_matured":
                seed_id = _event_int(event, "seed")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    record["matured_tick"] = current_tick
            elif kind == "plant_fruited":
                seed_id = _event_int(event, "seed")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    if record.get("first_fruited_tick") is None:
                        record["first_fruited_tick"] = current_tick
                    record["fruit_count"] = int(record.get("fruit_count", 0)) + 1
            elif kind == "plant_lifecycle_food_consumed":
                agent_id = _event_int(event, "agent")
                plant_id = _event_int(event, "plant")
                if plant_id is not None:
                    record = seed_record(plant_id)
                    if record.get("first_consumed_tick") is None:
                        record["first_consumed_tick"] = current_tick
                    record["consumed_count"] = int(record.get("consumed_count", 0)) + 1
                    consumed_by_agents = record.get("consumed_by_agents")
                    if isinstance(consumed_by_agents, set) and agent_id is not None:
                        consumed_by_agents.add(agent_id)
                    if (
                        bool(record.get("agent_moved"))
                        and record.get("germinated_tick") is not None
                        and record.get("matured_tick") is not None
                        and record.get("first_fruited_tick") is not None
                    ):
                        agent_moved_seed_chain_ids.add(plant_id)
                        moved_by_agent = record.get("moved_by_agent")
                        if isinstance(moved_by_agent, int):
                            agent_moved_seed_chain_agents.add(moved_by_agent)
                        if moved_by_agent == agent_id:
                            same_agent_seed_food_chain_ids.add(plant_id)
                    elif (
                        record.get("source_kind") in {"harvest_seed_dropped", "natural_seed_dropped"}
                        and record.get("germinated_tick") is not None
                        and record.get("matured_tick") is not None
                        and record.get("first_fruited_tick") is not None
                    ):
                        control_seed_chain_ids.add(plant_id)
                if agent_id is not None and position is not None and args.learning_reward_memory_limit > 0:
                    reward_counts_by_agent[agent_id] += 1
                    reward_records.append(
                        {
                            "id": next_reward_record_id,
                            "agent": agent_id,
                            "x": position[0],
                            "y": position[1],
                            "tick": current_tick,
                            "left_tick": -1,
                        }
                    )
                    next_reward_record_id += 1
                    if len(reward_records) > args.learning_reward_memory_limit:
                        reward_records = reward_records[-args.learning_reward_memory_limit :]
            elif kind == "plant_lifecycle_food_decayed":
                plant_id = _event_int(event, "plant")
                if plant_id is not None:
                    record = seed_record(plant_id)
                    record["decayed_count"] = int(record.get("decayed_count", 0)) + 1
            if kind in SAMPLED_EVENT_KINDS:
                if len(event_samples) < args.event_sample_limit:
                    event_samples.append(event)
                kind_samples = event_samples_by_kind[kind]
                if len(kind_samples) < 6:
                    kind_samples.append(event)

        if current_tick % args.evaluate_every_ticks == 0:
            signals = _evaluate_signals(env, visit_counter, event_counts)
            stop_signals = [signal for signal in signals if bool(signal.get("stop_candidate"))]
            if stop_signals:
                stop_reason = f"interesting_signal:{stop_signals[0]['type']}"
                break

        now = time.monotonic()
        if now >= next_progress_at:
            next_progress_at = now + args.progress_every_seconds
            progress = {
                "type": "progress",
                "elapsed_seconds": round(now - started, 1),
                "tick": current_tick,
                "day": current_day,
                "population": len(agents),
                "births": total_births,
                "nests": len(env.nests),
                "plants": env.plant_state_counts(),
                "plant_origins": _plant_origin_summary(env),
                "affect": _affect_summary(agents),
                "food_sources": dict(Counter(resource.source for resource in env.food_positions.values())),
                "plant_lifecycle_food": _plant_lifecycle_food_summary(env, event_counts),
                "learning_metrics": learning_metrics_summary(),
                "seed_causality_metrics": seed_causality_metrics_summary(),
                "events": {
                    "build_nest": event_counts["build_nest"],
                    "tend_food_patch": event_counts["tend_food_patch"],
                    "plant_matured": event_counts["plant_matured"],
                    "plant_fruited": event_counts["plant_fruited"],
                    "plant_lifecycle_food_consumed": event_counts["plant_lifecycle_food_consumed"],
                    "plant_lifecycle_food_decayed": event_counts["plant_lifecycle_food_decayed"],
                    "harvest_seed_dropped": event_counts["harvest_seed_dropped"],
                    "natural_seed_dropped": event_counts["natural_seed_dropped"],
                    "seed_picked": event_counts["seed_picked"],
                    "seed_dropped": event_counts["seed_dropped"],
                    "seed_buried_by_disturbance": event_counts["seed_buried_by_disturbance"],
                    "plant_died": event_counts["plant_died"],
                    "technology_emerged": event_counts["technology_emerged"],
                },
            }
            print(json.dumps(progress, ensure_ascii=False), flush=True)

    final_signals = _evaluate_signals(env, visit_counter, event_counts)
    if not stop_signals:
        stop_signals = [signal for signal in final_signals if bool(signal.get("stop_candidate"))]
    result = {
        "seed": args.seed,
        "body_index": body_index,
        "body": body.short_description,
        "stop_reason": stop_reason,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "tick": env.tick_count,
        "day": env.tick_count // env.day_length,
        "population": len(agents),
        "peak_population": peak_population,
        "births": total_births,
        "nests": len(env.nests),
        "plant_counts": env.plant_state_counts(),
        "plant_origins": _plant_origin_summary(env),
        "affect": _affect_summary(agents),
        "agent_state": _agent_state_summary(agents),
        "food_sources": dict(Counter(resource.source for resource in env.food_positions.values())),
        "plant_lifecycle_food": _plant_lifecycle_food_summary(env, event_counts),
        "learning_metrics": learning_metrics_summary(),
        "seed_causality_metrics": seed_causality_metrics_summary(),
        "event_location_hotspots": _top_event_locations(event_location_counts),
        "mean_photosynthetic_light": round(env.mean_photosynthetic_light(), 3),
        "mean_soil_nutrients": round(env.mean_soil_nutrients(), 3),
        "event_counts": dict(event_counts),
        "event_attribute_counts": {
            key: dict(counter)
            for key, counter in sorted(event_attribute_counts.items())
            if counter
        },
        "event_numeric_summaries": {
            key: summary
            for key, values in sorted(event_numeric_values.items())
            if (summary := _numeric_summary(values))
        },
        "first_event_tick": first_event_tick,
        "signals": final_signals,
        "stop_signals": stop_signals,
        "event_samples": event_samples,
        "event_samples_by_kind": {kind: samples for kind, samples in sorted(event_samples_by_kind.items()) if samples},
        "sample_harvest_seed_dropped": event_samples_by_kind["harvest_seed_dropped"],
        "sample_build_nest": event_samples_by_kind["build_nest"],
        "sample_tend_food_patch": event_samples_by_kind["tend_food_patch"],
        "sample_plant_fruited": event_samples_by_kind["plant_fruited"],
        "sample_natural_seed_dropped": event_samples_by_kind["natural_seed_dropped"],
        "sample_plant_died": event_samples_by_kind["plant_died"],
        "sample_plant_lifecycle_food_consumed": event_samples_by_kind["plant_lifecycle_food_consumed"],
        "sample_plant_lifecycle_food_decayed": event_samples_by_kind["plant_lifecycle_food_decayed"],
    }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a timed emergence watcher for nest/farm-like behavior.")
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--body-index", type=int, default=8)
    parser.add_argument("--initial-population", type=int, default=50)
    parser.add_argument("--max-population", type=int, default=250)
    parser.add_argument("--max-ticks", type=int, default=10_000_000)
    parser.add_argument("--time-limit-seconds", type=float, default=1200.0)
    parser.add_argument("--progress-every-seconds", type=float, default=30.0)
    parser.add_argument("--evaluate-every-ticks", type=int, default=100)
    parser.add_argument("--event-sample-limit", type=int, default=80)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--spawn-strategy", default="frontier_safe_high_food")
    parser.add_argument("--immortal", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--width", type=int, default=100)
    parser.add_argument("--height", type=int, default=100)
    parser.add_argument("--max-food", type=int, default=220)
    parser.add_argument("--base-food-spawn-per-tick", type=int, default=2)
    parser.add_argument("--food-spawn-multiplier", type=float, default=0.45)
    parser.add_argument("--bootstrap-food-spawn-ticks", type=int, default=120)
    parser.add_argument("--wild-food-spawn-after-bootstrap-multiplier", type=float, default=0.08)
    parser.add_argument("--natural-seed-rain-per-tick", type=int, default=0)
    parser.add_argument("--max-plant-seeds", type=int, default=1200)
    parser.add_argument("--large-animal-spawn-per-tick", type=int, default=2)
    parser.add_argument("--max-large-animals", type=int, default=28)
    parser.add_argument("--nest-support-food-chance", type=float, default=0.05)
    parser.add_argument("--nest-support-spawn-chance", type=float, default=0.03)
    parser.add_argument("--frontier-band", type=int, default=10)
    parser.add_argument("--global-food-decline-per-day", type=float, default=0.012)
    parser.add_argument("--minimum-global-food-multiplier", type=float, default=0.24)
    parser.add_argument("--ambient-food-decay-chance", type=float, default=0.006)
    parser.add_argument("--plant-food-decay-chance", type=float, default=0.003)
    parser.add_argument("--plant-seed-max-age-multiplier", type=float, default=1.0)
    parser.add_argument("--plant-growth-rate-multiplier", type=float, default=1.0)
    parser.add_argument("--sprout-biomass-loss-multiplier", type=float, default=1.0)
    parser.add_argument("--germination-good-ticks-multiplier", type=float, default=1.0)
    parser.add_argument("--plant-fruiting-interval-multiplier", type=float, default=1.0)
    parser.add_argument("--plant-fruiting-growth-threshold-multiplier", type=float, default=1.0)
    parser.add_argument("--plant-fruiting-chance-multiplier", type=float, default=1.0)
    parser.add_argument("--natural-seed-drop-chance-multiplier", type=float, default=1.0)
    parser.add_argument("--learning-revisit-radius", type=int, default=4)
    parser.add_argument("--learning-revisit-min-delay-ticks", type=int, default=20)
    parser.add_argument("--learning-revisit-max-age-ticks", type=int, default=2000)
    parser.add_argument("--learning-reward-memory-limit", type=int, default=1200)
    parser.add_argument("--phase3-min-seed-move-distance", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = run_watch(args)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"type": "result", "output": str(args.output), **result}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
