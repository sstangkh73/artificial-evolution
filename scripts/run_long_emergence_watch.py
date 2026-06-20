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

from agents.agent import ADULT_AGE, MAX_AGE, Agent
from agents.body import generate_candidate_body_plans
from simulation.runner import (
    FOUNDER_START_AGE,
    _detect_emergent_technology_events,
    _lineage_label,
    _occupied_nest_owner_ids,
    _spawn_initial_positions,
    _update_social_groups,
)
from world.environment import Environment, PLANT_SPECIES

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
    # v2 endozoochory (Fix 2): without these, gut-dispersed seeds were left with
    # agent_moved=False and miscounted into the agent-independent control group.
    "gut_seed_ingested",
    "gut_seed_excreted",
    "gut_seed_killed",
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


def _int_list(value: object, default: list[int] | None = None) -> list[int]:
    if default is None:
        default = []
    if value is None:
        return default
    if isinstance(value, str):
        values: list[int] = []
        for item in value.split(","):
            item = item.strip()
            if not item:
                continue
            values.append(int(item))
        return values or default
    if isinstance(value, (list, tuple)):
        return [int(item) for item in value]
    return default


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


def _manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _seed_record_position(record: dict[str, object]) -> tuple[int, int] | None:
    x_value = record.get("last_drop_x")
    y_value = record.get("last_drop_y")
    if isinstance(x_value, int) and isinstance(y_value, int):
        return (x_value, y_value)
    x_value = record.get("origin_x")
    y_value = record.get("origin_y")
    if isinstance(x_value, int) and isinstance(y_value, int):
        return (x_value, y_value)
    return None


def _seed_completed_chain(record: dict[str, object]) -> bool:
    return (
        record.get("germinated_tick") is not None
        and record.get("matured_tick") is not None
        and record.get("first_fruited_tick") is not None
        and int(record.get("consumed_count", 0)) > 0
    )


def _diet_by_kind(agents) -> dict[str, int]:
    """Total meals eaten per food kind, summed across agents (food-value study)."""
    totals: Counter = Counter()
    for agent in agents:
        for kind, count in getattr(agent, "meals_by_type", {}).items():
            totals[kind] += int(count)
    return dict(totals)


def _energy_economy(agents, env) -> dict[str, object]:
    """Energy-economy diagnostics (is starvation real / supply vs metabolism)."""
    if not agents:
        return {}
    n = len(agents)
    ticks = max(1, env.tick_count)
    energies = [a.energy for a in agents]
    clamp = sum(getattr(a, "clamp_energy_injected_total", 0.0) for a in agents)
    gained = sum(getattr(a, "energy_gained_total", 0.0) for a in agents)
    d_base = sum(getattr(a, "drain_base_total", 0.0) for a in agents)
    d_brain = sum(getattr(a, "drain_brain_total", 0.0) for a in agents)
    d_move = sum(getattr(a, "drain_move_total", 0.0) for a in agents)
    standing = Counter(r.kind for r in env.food_positions.values())
    denom = n * ticks
    return {
        "mean_energy": round(sum(energies) / n, 2),
        "min_energy": round(min(energies), 2),
        "max_energy": round(max(energies), 2),
        # per-agent per-tick: deficit the immortal floor had to cover (true gap),
        # vs energy actually eaten. If injection >> 0, the economy can't sustain
        # the population; if injection ~ 0, starvation is an artifact.
        "deficit_per_agent_tick": round(clamp / denom, 4),
        "intake_per_agent_tick": round(gained / denom, 4),
        # drain decomposition (per agent per tick): where the energy goes.
        "drain_base_per_tick": round(d_base / denom, 4),
        "drain_brain_per_tick": round(d_brain / denom, 4),
        "drain_move_per_tick": round(d_move / denom, 4),
        "drain_total_per_tick": round((d_base + d_brain + d_move) / denom, 4),
        "standing_food_by_kind": dict(standing),
    }


def _learned_food_value(agents) -> dict[str, float]:
    """Mean learned per-kind food value across agents that have tasted it
    (food-value study B). Confirms whether agents learned seed < plant."""
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for agent in agents:
        for kind, value in getattr(agent, "food_value_memory", {}).items():
            sums[kind] = sums.get(kind, 0.0) + float(value)
            counts[kind] = counts.get(kind, 0) + 1
    return {kind: round(sums[kind] / counts[kind], 3) for kind in sums}


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _quality_lift(numerator: float, denominator: float) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 4)


def _site_quality_snapshot(env: Environment, x: int, y: int) -> dict[str, float | int]:
    spec = PLANT_SPECIES["wild_grain"]
    moisture = env.get_cell_moisture(x, y)
    light = env.get_cell_photosynthetic_light(x, y)
    nutrients = env.get_cell_soil_nutrients(x, y)
    temp_k = env.get_cell_temperature(x, y)
    danger = env.get_danger_level(x, y)
    moisture_midpoint = (spec.germination_water_min + spec.germination_water_max) / 2.0
    moisture_span = max(0.01, (spec.germination_water_max - spec.germination_water_min) / 2.0)
    temp_midpoint = (spec.germination_temp_min_k + spec.germination_temp_max_k) / 2.0
    temp_span = max(0.01, (spec.germination_temp_max_k - spec.germination_temp_min_k) / 2.0)
    moisture_fit = _clamp01(1.0 - (abs(moisture - moisture_midpoint) / moisture_span))
    temperature_fit = _clamp01(1.0 - (abs(temp_k - temp_midpoint) / temp_span))
    light_fit = _clamp01(light / max(0.01, spec.light_saturation))
    nutrient_score = _clamp01(nutrients / max(0.01, spec.nutrient_demand))
    danger_penalty = _clamp01(danger)
    temperature_penalty = round(1.0 - temperature_fit, 5)
    quality_total = max(
        0.0,
        (moisture_fit * 0.30)
        + (light_fit * 0.24)
        + (nutrient_score * 0.24)
        + (temperature_fit * 0.14)
        - (danger_penalty * 0.18),
    )
    return {
        "x": x,
        "y": y,
        "quality_score_total": round(quality_total, 5),
        "moisture_fit": round(moisture_fit, 5),
        "light_fit": round(light_fit, 5),
        "nutrient_score": round(nutrient_score, 5),
        "danger_penalty": round(danger_penalty, 5),
        "temperature_penalty": temperature_penalty,
        "raw_moisture": round(moisture, 5),
        "raw_light": round(light, 5),
        "raw_nutrients": round(nutrients, 5),
        "raw_temperature_k": round(temp_k, 3),
        "raw_danger": round(danger, 5),
    }


def _mean_quality_snapshots(snapshots: list[dict[str, float | int]]) -> dict[str, float | int] | None:
    if not snapshots:
        return None
    fields = [
        "quality_score_total",
        "moisture_fit",
        "light_fit",
        "nutrient_score",
        "danger_penalty",
        "temperature_penalty",
    ]
    return {
        field: round(
            sum(float(snapshot[field]) for snapshot in snapshots if field in snapshot) / len(snapshots),
            5,
        )
        for field in fields
    }


def _nearby_quality_control(env: Environment, x: int, y: int, radius: int = 3) -> dict[str, float | int] | None:
    snapshots: list[dict[str, float | int]] = []
    for scan_y in range(max(0, y - radius), min(env.height, y + radius + 1)):
        for scan_x in range(max(0, x - radius), min(env.width, x + radius + 1)):
            if scan_x == x and scan_y == y:
                continue
            if abs(scan_x - x) + abs(scan_y - y) > radius:
                continue
            if not env.is_walkable(scan_x, scan_y):
                continue
            snapshots.append(_site_quality_snapshot(env, scan_x, scan_y))
    return _mean_quality_snapshots(snapshots)


def _visible_quality_controls(
    env: Environment,
    x: int,
    y: int,
    radius: int,
) -> tuple[dict[str, float | int] | None, dict[str, float | int] | None]:
    snapshots: list[dict[str, float | int]] = []
    radius = max(1, radius)
    for scan_y in range(max(0, y - radius), min(env.height, y + radius + 1)):
        for scan_x in range(max(0, x - radius), min(env.width, x + radius + 1)):
            if scan_x == x and scan_y == y:
                continue
            if abs(scan_x - x) + abs(scan_y - y) > radius:
                continue
            if not env.is_walkable(scan_x, scan_y):
                continue
            snapshots.append(_site_quality_snapshot(env, scan_x, scan_y))
    if not snapshots:
        return None, None
    best = max(snapshots, key=lambda snapshot: float(snapshot["quality_score_total"]))
    return _mean_quality_snapshots(snapshots), best


def _deterministic_world_control(env: Environment, seed_id: int, tick: int) -> dict[str, float | int]:
    value = ((seed_id + 1) * 1103515245 + (tick + 17) * 12345) & 0x7FFFFFFF
    for attempt in range(max(1, env.width * env.height)):
        x = (value + (attempt * 37)) % env.width
        y = ((value // max(1, env.width)) + (attempt * 53)) % env.height
        if env.is_walkable(x, y):
            return _site_quality_snapshot(env, x, y)
    return _site_quality_snapshot(env, 0, 0)


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
        food_signal_radius_cap=getattr(args, "food_signal_radius_cap", None),
        plant_lifecycle_food_signal_weight=getattr(args, "plant_lifecycle_food_signal_weight", 1.35),
        seed_hunger_drop_bonus=getattr(args, "seed_hunger_drop_bonus", 0.06),
        seed_drop_block_critical_hunger=getattr(args, "seed_drop_block_critical_hunger", False),
        seed_drop_safe_window_only=getattr(args, "seed_drop_safe_window_only", False),
        seed_drop_safe_hunger_max=getattr(args, "seed_drop_safe_hunger_max", 0.55),
        seed_drop_safe_fear_max=getattr(args, "seed_drop_safe_fear_max", 0.45),
        seed_drop_safe_cold_max=getattr(args, "seed_drop_safe_cold_max", 0.45),
        seed_drop_safe_safety_min=getattr(args, "seed_drop_safe_safety_min", 0.45),
        metabolism_model=getattr(args, "metabolism_model", "v1"),
        low_value_food_spawn_per_tick=getattr(args, "low_value_food_spawn_per_tick", 0.0),
        food_energy_multiplier=getattr(args, "food_energy_multiplier", 1.0),
        metabolic_drain_multiplier=getattr(args, "metabolic_drain_multiplier", 1.0),
        food_value_learning_enabled=getattr(args, "food_value_learning_enabled", False),
        diet_pickiness=getattr(args, "diet_pickiness", 0.5),
        diet_starvation_energy=getattr(args, "diet_starvation_energy", 6),
        repro_safety_threshold=getattr(args, "repro_safety_threshold", 0.66),
        repro_comfort_threshold=getattr(args, "repro_comfort_threshold", 0.58),
        repro_safety_streak=getattr(args, "repro_safety_streak", 10),
        repro_pair_bond_streak=getattr(args, "repro_pair_bond_streak", 14),
        repro_max_age=getattr(args, "repro_max_age", 200),
        repro_litter_min=getattr(args, "repro_litter_min", 1),
        repro_litter_max=getattr(args, "repro_litter_max", 3),
        scaffolded_agent_actions_enabled=getattr(args, "scaffolded_agent_actions_enabled", False),
        scaffolded_nest_support_enabled=getattr(args, "scaffolded_nest_support_enabled", False),
        scaffolded_social_support_enabled=getattr(args, "scaffolded_social_support_enabled", False),
        legacy_scaffold_nest_enabled=getattr(args, "legacy_scaffold_nest_enabled", False),
        continuous_reproduction_enabled=getattr(args, "continuous_reproduction_enabled", False),
        continuous_repro_base_rate=getattr(args, "continuous_repro_base_rate", 0.05),
        continuous_repro_local_cap=getattr(args, "continuous_repro_local_cap", 6.0),
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
    # Founder ages: all FOUNDER_START_AGE by default (byte-identical). With
    # founder_age_spread > 0, spread deterministically across [ADULT_AGE, MAX_AGE)
    # so the cohort does not all hit the lifespan cap on the same tick (avoids the
    # synchronized mass die-off that confounds sustained-reproduction studies).
    _spread = getattr(args, "founder_age_spread", 0)
    _npop = max(1, args.initial_population)

    def _founder_age(idx: int) -> int:
        if not _spread:
            return FOUNDER_START_AGE
        return ADULT_AGE + int(idx / max(1, _npop - 1) * (MAX_AGE - ADULT_AGE - 1))

    agents = [
        Agent(
            agent_id=agent_id,
            body=body,
            x=spawn_x,
            y=spawn_y,
            age=_founder_age(agent_id),
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
        "seed_pick_instinct": Counter(),
        "seed_pick_food_contact": Counter(),
        "seed_drop_context": Counter(),
        "seed_drop_instinct": Counter(),
        "seed_drop_food_contact": Counter(),
        "seed_drop_safe_window": Counter(),
        "seed_drop_critical_hunger": Counter(),
    }
    event_numeric_values: dict[str, list[float]] = {
        "plant_died_age_ticks": [],
        "plant_died_biomass": [],
        "plant_died_water": [],
        "plant_died_temp_k": [],
        "plant_died_light": [],
        "plant_died_nutrients": [],
        "plant_died_growth": [],
        "seed_pick_energy": [],
        "seed_pick_hunger": [],
        "seed_pick_fear": [],
        "seed_pick_cold": [],
        "seed_pick_comfort": [],
        "seed_drop_energy": [],
        "seed_drop_hunger": [],
        "seed_drop_fear": [],
        "seed_drop_cold": [],
        "seed_drop_comfort": [],
        "seed_drop_safety": [],
        "seed_drop_chance": [],
    }
    reward_records: list[dict[str, int]] = []
    next_reward_record_id = 0
    agent_death_reasons: Counter[str] = Counter()
    repro_funnel: Counter[str] = Counter()
    repro_funnel_checks = [0]
    population_trajectory: list[dict[str, object]] = []
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
    phase4_patch_radius = getattr(args, "phase4_patch_radius", 4)
    phase4_min_patch_moved_seed_drops = getattr(args, "phase4_min_patch_moved_seed_drops", 3)
    phase4_patch_return_min_delay_ticks = getattr(
        args,
        "phase4_patch_return_min_delay_ticks",
        getattr(args, "learning_revisit_min_delay_ticks", 20),
    )
    phase4_patch_return_max_age_ticks = getattr(
        args,
        "phase4_patch_return_max_age_ticks",
        getattr(args, "learning_revisit_max_age_ticks", 2000),
    )
    phase4_min_matched_control_seeds = getattr(args, "phase4_min_matched_control_seeds", 5)
    phase5_future_control_offsets = sorted(
        offset
        for offset in _int_list(getattr(args, "phase5_future_control_offsets", [10, 25, 50]), [10, 25, 50])
        if offset > 0
    )
    phase4_drop_watchers: list[dict[str, object]] = []
    phase5_future_path_watchers: list[dict[str, object]] = []
    carried_seed_position_controls: dict[tuple[int, int], dict[str, object]] = {}
    carried_seed_state_windows: dict[tuple[int, int], dict[str, object]] = {}

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
                "drop_site_quality": None,
                "current_position_control_quality": None,
                "nearby_control_quality": None,
                "visible_control_quality": None,
                "visible_best_control_quality": None,
                "random_world_control_quality": None,
                "future_path_control_qualities": {},
                "drop_vs_current_position_lift": None,
                "drop_vs_nearby_control_lift": None,
                "drop_vs_visible_control_lift": None,
                "drop_vs_visible_best_control_lift": None,
                "drop_vs_random_world_lift": None,
                "drop_vs_future_path_control_lift": None,
                "hunger_recovery_control_quality": None,
                "safe_window_control_quality": None,
                "drop_vs_hunger_recovery_position_lift": None,
                "drop_vs_safe_window_position_lift": None,
                "had_hunger_while_carried": False,
                "carry_ticks_observed": 0,
                "first_hunger_tick_while_carried": None,
                "first_hunger_recovery_tick": None,
                "first_safe_window_tick": None,
                "last_pick_instinct": None,
                "last_pick_food_contact": None,
                "last_drop_context": None,
                "last_drop_instinct": None,
                "last_drop_food_contact": None,
                "last_drop_safe_window": None,
                "last_drop_critical_hunger": None,
                "last_drop_energy": None,
                "last_drop_hunger": None,
                "last_drop_fear": None,
                "last_drop_cold": None,
                "last_drop_comfort": None,
                "last_drop_safety": None,
                "last_drop_chance": None,
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

    def phase4_patch_metrics_summary() -> dict[str, object]:
        records = list(seed_records.values())
        agent_moved_records = [
            record
            for record in records
            if bool(record.get("agent_moved")) and _seed_record_position(record) is not None
        ]
        control_records = [
            record
            for record in records
            if not bool(record.get("agent_moved"))
            and record.get("source_kind") in {"harvest_seed_dropped", "natural_seed_dropped"}
            and _seed_record_position(record) is not None
        ]

        def site_signature(position: tuple[int, int]) -> tuple[float, float, float, float]:
            x, y = position
            return (
                env.get_cell_moisture(x, y),
                env.get_cell_photosynthetic_light(x, y),
                env.get_cell_soil_nutrients(x, y),
                env.get_danger_level(x, y),
            )

        def matched_controls(position: tuple[int, int]) -> tuple[list[dict[str, object]], str]:
            moisture, light, nutrients, danger = site_signature(position)
            matched: list[dict[str, object]] = []
            for record in control_records:
                control_position = _seed_record_position(record)
                if control_position is None:
                    continue
                control_moisture, control_light, control_nutrients, control_danger = site_signature(control_position)
                if (
                    abs(control_moisture - moisture) <= 0.15
                    and abs(control_light - light) <= 0.20
                    and abs(control_nutrients - nutrients) <= 0.25
                    and abs(control_danger - danger) <= 0.25
                ):
                    matched.append(record)
            if len(matched) >= phase4_min_matched_control_seeds:
                return matched, "matched_micro_site"
            return control_records, "broad_fallback"

        def summarize_center(center: tuple[int, int]) -> dict[str, object]:
            members = [
                record
                for record in agent_moved_records
                if (position := _seed_record_position(record)) is not None
                and _manhattan(position, center) <= phase4_patch_radius
            ]
            member_seed_ids = {
                int(record["seed_id"])
                for record in members
                if isinstance(record.get("seed_id"), int)
            }
            completed_members = [record for record in members if _seed_completed_chain(record)]
            control_group, control_mode = matched_controls(center)
            completed_controls = [record for record in control_group if _seed_completed_chain(record)]
            moved_rate = _round_rate(len(completed_members), len(members))
            control_rate = _round_rate(len(completed_controls), len(control_group))
            patch_watchers = [
                watcher
                for watcher in phase4_drop_watchers
                if watcher.get("seed_id") in member_seed_ids
                and isinstance(watcher.get("x"), int)
                and isinstance(watcher.get("y"), int)
                and _manhattan((int(watcher["x"]), int(watcher["y"])), center) <= phase4_patch_radius
            ]
            return_agents: set[int] = set()
            first_return_tick: int | None = None
            return_tick_hits = 0
            return_opportunities = 0
            random_expected_return_hits = 0.0
            dropper_returned_after_left = 0
            dropper_left_watchers = 0
            dropper_return_tick_hits = 0
            dropper_return_opportunities = 0
            dropper_random_expected_hits = 0.0
            non_dropper_return_tick_hits = 0
            non_dropper_return_opportunities = 0
            non_dropper_random_expected_hits = 0.0
            non_dropper_return_agents: set[int] = set()
            pre_fruit_return_agents: set[int] = set()
            post_fruit_return_agents: set[int] = set()
            pre_drop_visit_counts: list[int] = []
            first_drop_tick: int | None = None
            for watcher in patch_watchers:
                return_tick_hits += int(watcher.get("return_tick_hits", 0))
                return_opportunities += int(watcher.get("return_opportunities", 0))
                random_expected_return_hits += float(watcher.get("random_expected_return_hits", 0.0))
                dropper_return_tick_hits += int(watcher.get("dropper_return_tick_hits_after_left", 0))
                dropper_return_opportunities += int(watcher.get("dropper_return_opportunities_after_left", 0))
                dropper_random_expected_hits += float(watcher.get("dropper_random_expected_return_hits", 0.0))
                non_dropper_return_tick_hits += int(watcher.get("non_dropper_return_tick_hits", 0))
                non_dropper_return_opportunities += int(watcher.get("non_dropper_return_opportunities", 0))
                non_dropper_random_expected_hits += float(watcher.get("non_dropper_random_expected_return_hits", 0.0))
                if watcher.get("dropper_left_tick") is not None:
                    dropper_left_watchers += 1
                if bool(watcher.get("dropper_returned_after_left")):
                    dropper_returned_after_left += 1
                pre_drop_visit_count = watcher.get("pre_drop_visit_count_near")
                if isinstance(pre_drop_visit_count, int):
                    pre_drop_visit_counts.append(pre_drop_visit_count)
                watcher_drop_tick = watcher.get("drop_tick")
                if isinstance(watcher_drop_tick, int) and (
                    first_drop_tick is None or watcher_drop_tick < first_drop_tick
                ):
                    first_drop_tick = watcher_drop_tick
                watcher_returned_agents = watcher.get("returned_agents", set())
                if isinstance(watcher_returned_agents, set):
                    return_agents.update(int(agent_id) for agent_id in watcher_returned_agents)
                watcher_non_dropper_agents = watcher.get("non_dropper_returned_agents", set())
                if isinstance(watcher_non_dropper_agents, set):
                    non_dropper_return_agents.update(int(agent_id) for agent_id in watcher_non_dropper_agents)
                watcher_pre_fruit_agents = watcher.get("pre_fruit_returned_agents", set())
                if isinstance(watcher_pre_fruit_agents, set):
                    pre_fruit_return_agents.update(int(agent_id) for agent_id in watcher_pre_fruit_agents)
                watcher_post_fruit_agents = watcher.get("post_fruit_returned_agents", set())
                if isinstance(watcher_post_fruit_agents, set):
                    post_fruit_return_agents.update(int(agent_id) for agent_id in watcher_post_fruit_agents)
                watcher_first_tick = watcher.get("first_return_tick")
                if isinstance(watcher_first_tick, int) and (
                    first_return_tick is None or watcher_first_tick < first_return_tick
                ):
                    first_return_tick = watcher_first_tick
            same_agent_chains = sum(
                1
                for record in completed_members
                if record.get("moved_by_agent") in record.get("consumed_by_agents", set())
            )
            return_lift = None
            if random_expected_return_hits > 0:
                return_lift = round(return_tick_hits / random_expected_return_hits, 3)
            dropper_return_lift = None
            if dropper_random_expected_hits > 0:
                dropper_return_lift = round(dropper_return_tick_hits / dropper_random_expected_hits, 3)
            non_dropper_return_lift = None
            if non_dropper_random_expected_hits > 0:
                non_dropper_return_lift = round(non_dropper_return_tick_hits / non_dropper_random_expected_hits, 3)
            productivity_lift = _round_lift(moved_rate, control_rate)
            final_visit_count = _visit_count_near(visit_counter, center[0], center[1], phase4_patch_radius)
            pre_drop_visit_count_at_first_drop = min(pre_drop_visit_counts) if pre_drop_visit_counts else 0
            pre_fruit_agent_count = len(pre_fruit_return_agents)
            post_fruit_agent_count = len(post_fruit_return_agents)
            return {
                "center": [center[0], center[1]],
                "radius": phase4_patch_radius,
                "moved_seed_drops": len(members),
                "moved_seed_agents": len(
                    {
                        int(record["moved_by_agent"])
                        for record in members
                        if isinstance(record.get("moved_by_agent"), int)
                    }
                ),
                "completed_seed_chains": len(completed_members),
                "food_consumed": sum(int(record.get("consumed_count", 0)) for record in members),
                "same_agent_patch_food_chains": same_agent_chains,
                "return_tick_hits_after_drop": return_tick_hits,
                "return_opportunities_after_drop": return_opportunities,
                "random_expected_return_hits": round(random_expected_return_hits, 3),
                "return_lift_vs_random_control": return_lift,
                "return_agents": len(return_agents),
                "first_return_tick": first_return_tick,
                "first_drop_tick": first_drop_tick,
                "pre_drop_visit_count_at_first_drop": pre_drop_visit_count_at_first_drop,
                "final_visit_count_near": final_visit_count,
                "visit_delta_after_first_drop": max(0, final_visit_count - pre_drop_visit_count_at_first_drop),
                "dropper_left_watchers": dropper_left_watchers,
                "dropper_returned_after_left_count": dropper_returned_after_left,
                "dropper_return_rate_after_left": _round_rate(dropper_returned_after_left, max(1, dropper_left_watchers)),
                "dropper_return_tick_hits_after_left": dropper_return_tick_hits,
                "dropper_return_opportunities_after_left": dropper_return_opportunities,
                "dropper_random_expected_return_hits": round(dropper_random_expected_hits, 3),
                "dropper_return_lift_vs_random_control": dropper_return_lift,
                "non_dropper_return_tick_hits": non_dropper_return_tick_hits,
                "non_dropper_return_opportunities": non_dropper_return_opportunities,
                "non_dropper_random_expected_return_hits": round(non_dropper_random_expected_hits, 3),
                "non_dropper_return_lift_vs_random_control": non_dropper_return_lift,
                "non_dropper_return_agents": len(non_dropper_return_agents),
                "pre_fruit_return_agents": pre_fruit_agent_count,
                "post_fruit_return_agents": post_fruit_agent_count,
                "post_to_pre_fruit_return_agent_ratio": (
                    round(post_fruit_agent_count / pre_fruit_agent_count, 3)
                    if pre_fruit_agent_count > 0
                    else None
                ),
                "control_mode": control_mode,
                "control_seed_count": len(control_group),
                "control_completed_seed_chains": len(completed_controls),
                "patch_completed_chain_rate": moved_rate,
                "control_completed_chain_rate": control_rate,
                "productivity_lift_vs_control": productivity_lift,
                "productivity_lift_unbounded": productivity_lift is None and moved_rate > 0 and control_rate == 0,
                "seed_ids": sorted(member_seed_ids)[:16],
            }

        candidates: list[dict[str, object]] = []
        seen_centers: set[tuple[int, int]] = set()
        for record in agent_moved_records:
            position = _seed_record_position(record)
            if position is None or position in seen_centers:
                continue
            seen_centers.add(position)
            candidate = summarize_center(position)
            if int(candidate["moved_seed_drops"]) >= phase4_min_patch_moved_seed_drops:
                candidates.append(candidate)
        candidates.sort(
            key=lambda candidate: (
                int(candidate["completed_seed_chains"]),
                int(candidate["moved_seed_drops"]),
                int(candidate["return_agents"]),
                int(candidate["food_consumed"]),
            ),
            reverse=True,
        )
        selected_patches: list[dict[str, object]] = []
        for candidate in candidates:
            center_values = candidate["center"]
            if not isinstance(center_values, list) or len(center_values) != 2:
                continue
            center = (int(center_values[0]), int(center_values[1]))
            if any(
                _manhattan(center, (int(existing["center"][0]), int(existing["center"][1]))) <= phase4_patch_radius
                for existing in selected_patches
                if isinstance(existing.get("center"), list)
            ):
                continue
            selected_patches.append(candidate)

        repeated_patches = [
            patch
            for patch in selected_patches
            if int(patch["moved_seed_drops"]) >= phase4_min_patch_moved_seed_drops
        ]
        best_patch = repeated_patches[0] if repeated_patches else None
        best_productivity_lift = max(
            (
                float(patch["productivity_lift_vs_control"])
                for patch in repeated_patches
                if patch.get("productivity_lift_vs_control") is not None
            ),
            default=None,
        )
        best_return_lift = max(
            (
                float(patch["return_lift_vs_random_control"])
                for patch in repeated_patches
                if patch.get("return_lift_vs_random_control") is not None
            ),
            default=None,
        )
        best_dropper_return_lift = max(
            (
                float(patch["dropper_return_lift_vs_random_control"])
                for patch in repeated_patches
                if patch.get("dropper_return_lift_vs_random_control") is not None
            ),
            default=None,
        )
        best_non_dropper_return_lift = max(
            (
                float(patch["non_dropper_return_lift_vs_random_control"])
                for patch in repeated_patches
                if patch.get("non_dropper_return_lift_vs_random_control") is not None
            ),
            default=None,
        )
        dropper_left_watchers = sum(int(patch["dropper_left_watchers"]) for patch in repeated_patches)
        dropper_returned_after_left = sum(
            int(patch["dropper_returned_after_left_count"]) for patch in repeated_patches
        )
        patch_return_agents: set[int] = set()
        for patch in repeated_patches:
            patch_seed_ids = set(int(seed_id) for seed_id in patch.get("seed_ids", []))
            for watcher in phase4_drop_watchers:
                if watcher.get("seed_id") not in patch_seed_ids:
                    continue
                watcher_returned_agents = watcher.get("returned_agents", set())
                if isinstance(watcher_returned_agents, set):
                    patch_return_agents.update(int(agent_id) for agent_id in watcher_returned_agents)
        contamination_events = event_counts["tend_food_patch"] + event_counts["food_patch_tended"]
        return {
            "patch_radius": phase4_patch_radius,
            "min_patch_moved_seed_drops": phase4_min_patch_moved_seed_drops,
            "drop_watchers": len(phase4_drop_watchers),
            "agent_moved_seed_drop_records": len(agent_moved_records),
            "control_seed_records": len(control_records),
            "repeated_drop_patch_count": len(repeated_patches),
            "patch_completed_seed_chains": sum(int(patch["completed_seed_chains"]) for patch in repeated_patches),
            "patch_food_consumed": sum(int(patch["food_consumed"]) for patch in repeated_patches),
            "patch_return_agents": len(patch_return_agents),
            "max_patch_moved_seed_drops": max((int(patch["moved_seed_drops"]) for patch in repeated_patches), default=0),
            "max_patch_completed_chains": max((int(patch["completed_seed_chains"]) for patch in repeated_patches), default=0),
            "max_patch_food_consumed": max((int(patch["food_consumed"]) for patch in repeated_patches), default=0),
            "best_patch_productivity_lift_vs_control": best_productivity_lift,
            "best_patch_return_lift_vs_random_control": best_return_lift,
            "patch_dropper_left_watchers": dropper_left_watchers,
            "patch_dropper_returned_after_left_count": dropper_returned_after_left,
            "patch_dropper_return_rate_after_left": _round_rate(dropper_returned_after_left, dropper_left_watchers),
            "best_patch_dropper_return_lift_vs_random_control": best_dropper_return_lift,
            "best_patch_non_dropper_return_lift_vs_random_control": best_non_dropper_return_lift,
            "best_patch_dropper_return_rate_after_left": (
                max(
                    (float(patch["dropper_return_rate_after_left"]) for patch in repeated_patches),
                    default=0.0,
                )
            ),
            "best_patch_non_dropper_return_agents": (
                max((int(patch["non_dropper_return_agents"]) for patch in repeated_patches), default=0)
            ),
            "best_patch_pre_drop_visit_count_at_first_drop": (
                int(best_patch["pre_drop_visit_count_at_first_drop"]) if best_patch is not None else 0
            ),
            "best_patch_visit_delta_after_first_drop": (
                int(best_patch["visit_delta_after_first_drop"]) if best_patch is not None else 0
            ),
            "best_patch_pre_fruit_return_agents": (
                int(best_patch["pre_fruit_return_agents"]) if best_patch is not None else 0
            ),
            "best_patch_post_fruit_return_agents": (
                int(best_patch["post_fruit_return_agents"]) if best_patch is not None else 0
            ),
            "best_patch_post_to_pre_fruit_return_agent_ratio": (
                best_patch["post_to_pre_fruit_return_agent_ratio"] if best_patch is not None else None
            ),
            "contamination_events": contamination_events,
            "contamination_event_counts": {
                "tend_food_patch": event_counts["tend_food_patch"],
                "food_patch_tended": event_counts["food_patch_tended"],
            },
            "best_patch": best_patch,
            "top_patch_candidates": repeated_patches[:8],
        }

    def phase5_site_selection_metrics_summary() -> dict[str, object]:
        records = [
            record
            for record in seed_records.values()
            if bool(record.get("agent_moved"))
            and isinstance(record.get("drop_site_quality"), dict)
            and isinstance(record.get("current_position_control_quality"), dict)
            and isinstance(record.get("nearby_control_quality"), dict)
        ]

        def quality(record: dict[str, object], key: str, field: str = "quality_score_total") -> float | None:
            snapshot = record.get(key)
            if not isinstance(snapshot, dict) or snapshot.get(field) is None:
                return None
            return float(snapshot[field])

        def mean_field(group: list[dict[str, object]], key: str, field: str = "quality_score_total") -> float:
            values = [value for record in group if (value := quality(record, key, field)) is not None]
            if not values:
                return 0.0
            return round(sum(values) / len(values), 5)

        def component_means(group: list[dict[str, object]], key: str) -> dict[str, float]:
            return {
                field: mean_field(group, key, field)
                for field in (
                    "quality_score_total",
                    "moisture_fit",
                    "light_fit",
                    "nutrient_score",
                    "danger_penalty",
                    "temperature_penalty",
                )
            }

        def future_snapshots(record: dict[str, object]) -> list[dict[str, float | int]]:
            raw = record.get("future_path_control_qualities")
            if not isinstance(raw, dict):
                return []
            return [snapshot for snapshot in raw.values() if isinstance(snapshot, dict)]

        def future_quality(record: dict[str, object]) -> float | None:
            snapshots = future_snapshots(record)
            if not snapshots:
                return None
            return round(sum(float(snapshot["quality_score_total"]) for snapshot in snapshots) / len(snapshots), 5)

        def mean_future_quality(group: list[dict[str, object]]) -> float:
            values = [value for record in group if (value := future_quality(record)) is not None]
            if not values:
                return 0.0
            return round(sum(values) / len(values), 5)

        def component_means_from_snapshots(snapshots: list[dict[str, float | int]]) -> dict[str, float]:
            if not snapshots:
                return {
                    "quality_score_total": 0.0,
                    "moisture_fit": 0.0,
                    "light_fit": 0.0,
                    "nutrient_score": 0.0,
                    "danger_penalty": 0.0,
                    "temperature_penalty": 0.0,
                }
            return {
                field: round(sum(float(snapshot[field]) for snapshot in snapshots) / len(snapshots), 5)
                for field in (
                    "quality_score_total",
                    "moisture_fit",
                    "light_fit",
                    "nutrient_score",
                    "danger_penalty",
                    "temperature_penalty",
                )
            }

        def top_record_positions(
            group: list[dict[str, object]],
            x_key: str,
            y_key: str,
            limit: int = 8,
        ) -> list[dict[str, int]]:
            counter: Counter[tuple[int, int]] = Counter()
            for record in group:
                x_value = record.get(x_key)
                y_value = record.get(y_key)
                if isinstance(x_value, int) and isinstance(y_value, int):
                    counter[(x_value, y_value)] += 1
            return [
                {"x": position[0], "y": position[1], "count": count}
                for position, count in counter.most_common(limit)
            ]

        def record_value_counts(field: str) -> dict[str, int]:
            counter: Counter[str] = Counter()
            for record in records:
                value = record.get(field)
                counter[str(value) if value is not None else "unknown"] += 1
            return dict(counter)

        def record_fraction(field: str, *values: str) -> float:
            accepted = set(values)
            return _round_rate(
                sum(1 for record in records if str(record.get(field)) in accepted),
                len(records),
            )

        def context_metrics(context: str) -> dict[str, object]:
            context_records = [
                record
                for record in records
                if record.get("last_drop_context") == context
            ]
            context_drop_quality = mean_field(context_records, "drop_site_quality")
            context_current_quality = mean_field(context_records, "current_position_control_quality")
            context_nearby_quality = mean_field(context_records, "nearby_control_quality")
            context_visible_quality = mean_field(context_records, "visible_control_quality")
            context_visible_best_quality = mean_field(context_records, "visible_best_control_quality")
            context_future_records = [record for record in context_records if future_quality(record) is not None]
            context_future_quality = mean_future_quality(context_future_records)
            context_drop_for_future_quality = mean_field(context_future_records, "drop_site_quality")
            return {
                "count": len(context_records),
                "fraction": _round_rate(len(context_records), len(records)),
                "drop_quality": context_drop_quality,
                "current_quality": context_current_quality,
                "nearby_quality": context_nearby_quality,
                "visible_quality": context_visible_quality,
                "visible_best_quality": context_visible_best_quality,
                "future_path_quality": context_future_quality,
                "drop_vs_current_lift": _quality_lift(context_drop_quality, context_current_quality),
                "drop_vs_nearby_lift": _quality_lift(context_drop_quality, context_nearby_quality),
                "drop_vs_visible_lift": _quality_lift(context_drop_quality, context_visible_quality),
                "drop_vs_visible_best_lift": _quality_lift(context_drop_quality, context_visible_best_quality),
                "drop_vs_future_path_lift": _quality_lift(
                    context_drop_for_future_quality,
                    context_future_quality,
                ),
                "completed_chain_rate": completed_rate(context_records),
                "high_quality_chain_rate": completed_rate(
                    sorted(
                        context_records,
                        key=lambda record: quality(record, "drop_site_quality") or 0.0,
                    )[-max(1, int(len(context_records) * 0.30)) :]
                    if context_records
                    else []
                ),
                "low_quality_chain_rate": completed_rate(
                    sorted(
                        context_records,
                        key=lambda record: quality(record, "drop_site_quality") or 0.0,
                    )[: max(1, int(len(context_records) * 0.30))]
                    if context_records
                    else []
                ),
            }

        def completed_rate(group: list[dict[str, object]]) -> float:
            return _round_rate(sum(1 for record in group if _seed_completed_chain(record)), len(group))

        sorted_by_quality = sorted(
            records,
            key=lambda record: quality(record, "drop_site_quality") or 0.0,
        )
        band_count = max(1, int(len(sorted_by_quality) * 0.30)) if sorted_by_quality else 0
        low_quality_records = sorted_by_quality[:band_count]
        high_quality_records = sorted_by_quality[-band_count:] if band_count else []

        sorted_by_drop_tick = sorted(
            records,
            key=lambda record: int(record.get("last_drop_tick", 0) or 0),
        )
        temporal_band_count = max(1, int(len(sorted_by_drop_tick) * 0.30)) if sorted_by_drop_tick else 0
        early_records = sorted_by_drop_tick[:temporal_band_count]
        late_records = sorted_by_drop_tick[-temporal_band_count:] if temporal_band_count else []

        mean_drop_quality = mean_field(records, "drop_site_quality")
        mean_current_quality = mean_field(records, "current_position_control_quality")
        mean_nearby_quality = mean_field(records, "nearby_control_quality")
        mean_random_quality = mean_field(records, "random_world_control_quality")
        mean_visible_quality = mean_field(records, "visible_control_quality")
        mean_visible_best_quality = mean_field(records, "visible_best_control_quality")
        future_records = [record for record in records if future_quality(record) is not None]
        mean_future_path_quality = mean_future_quality(future_records)
        mean_drop_quality_for_future = mean_field(future_records, "drop_site_quality")
        recovery_records = [
            record
            for record in records
            if isinstance(record.get("hunger_recovery_control_quality"), dict)
        ]
        safe_window_control_records = [
            record
            for record in records
            if isinstance(record.get("safe_window_control_quality"), dict)
        ]
        mean_hunger_recovery_quality = mean_field(recovery_records, "hunger_recovery_control_quality")
        mean_drop_quality_for_recovery = mean_field(recovery_records, "drop_site_quality")
        mean_safe_window_quality = mean_field(safe_window_control_records, "safe_window_control_quality")
        mean_drop_quality_for_safe_window = mean_field(safe_window_control_records, "drop_site_quality")
        early_quality = mean_field(early_records, "drop_site_quality")
        late_quality = mean_field(late_records, "drop_site_quality")
        high_rate = completed_rate(high_quality_records)
        low_rate = completed_rate(low_quality_records)
        all_future_snapshots = [
            snapshot
            for record in future_records
            for snapshot in future_snapshots(record)
        ]
        future_by_offset: dict[str, dict[str, float | int | None]] = {}
        for offset in phase5_future_control_offsets:
            offset_records = [
                record
                for record in records
                if isinstance(record.get("future_path_control_qualities"), dict)
                and isinstance(record["future_path_control_qualities"].get(str(offset)), dict)
            ]
            offset_future_values = [
                float(record["future_path_control_qualities"][str(offset)]["quality_score_total"])
                for record in offset_records
            ]
            offset_future_quality = round(sum(offset_future_values) / len(offset_future_values), 5) if offset_future_values else 0.0
            offset_drop_quality = mean_field(offset_records, "drop_site_quality")
            future_by_offset[str(offset)] = {
                "count": len(offset_records),
                "mean_drop_quality": offset_drop_quality,
                "mean_future_path_quality": offset_future_quality,
                "drop_vs_future_path_lift": _quality_lift(offset_drop_quality, offset_future_quality),
            }
        return {
            "agent_moved_drop_count": len(records),
            "current_position_control_count": sum(
                1 for record in records if isinstance(record.get("current_position_control_quality"), dict)
            ),
            "nearby_control_count": sum(
                1 for record in records if isinstance(record.get("nearby_control_quality"), dict)
            ),
            "visible_control_count": sum(
                1 for record in records if isinstance(record.get("visible_control_quality"), dict)
            ),
            "visible_best_control_count": sum(
                1 for record in records if isinstance(record.get("visible_best_control_quality"), dict)
            ),
            "future_path_control_count": len(future_records),
            "future_path_control_offsets": phase5_future_control_offsets,
            "hunger_recovery_control_count": len(recovery_records),
            "safe_window_control_count": len(safe_window_control_records),
            "drop_quality_components": component_means(records, "drop_site_quality"),
            "current_position_quality_components": component_means(records, "current_position_control_quality"),
            "nearby_control_quality_components": component_means(records, "nearby_control_quality"),
            "visible_control_quality_components": component_means(records, "visible_control_quality"),
            "visible_best_control_quality_components": component_means(records, "visible_best_control_quality"),
            "random_world_quality_components": component_means(records, "random_world_control_quality"),
            "future_path_quality_components": component_means_from_snapshots(all_future_snapshots),
            "hunger_recovery_quality_components": component_means(
                recovery_records,
                "hunger_recovery_control_quality",
            ),
            "safe_window_quality_components": component_means(
                safe_window_control_records,
                "safe_window_control_quality",
            ),
            "mean_drop_quality": mean_drop_quality,
            "mean_current_position_quality": mean_current_quality,
            "mean_nearby_control_quality": mean_nearby_quality,
            "mean_visible_control_quality": mean_visible_quality,
            "mean_visible_best_control_quality": mean_visible_best_quality,
            "mean_random_world_quality": mean_random_quality,
            "mean_future_path_control_quality": mean_future_path_quality,
            "mean_drop_quality_for_future_path_records": mean_drop_quality_for_future,
            "mean_hunger_recovery_position_quality": mean_hunger_recovery_quality,
            "mean_drop_quality_for_hunger_recovery_records": mean_drop_quality_for_recovery,
            "mean_safe_window_position_quality": mean_safe_window_quality,
            "mean_drop_quality_for_safe_window_records": mean_drop_quality_for_safe_window,
            "drop_quality_vs_current_position_lift": _quality_lift(mean_drop_quality, mean_current_quality),
            "drop_quality_vs_nearby_control_lift": _quality_lift(mean_drop_quality, mean_nearby_quality),
            "drop_quality_vs_visible_control_lift": _quality_lift(mean_drop_quality, mean_visible_quality),
            "drop_quality_vs_visible_best_control_lift": _quality_lift(mean_drop_quality, mean_visible_best_quality),
            "drop_quality_vs_random_world_lift": _quality_lift(mean_drop_quality, mean_random_quality),
            "drop_quality_vs_hunger_recovery_position_lift": _quality_lift(
                mean_drop_quality_for_recovery,
                mean_hunger_recovery_quality,
            ),
            "drop_quality_vs_safe_window_position_lift": _quality_lift(
                mean_drop_quality_for_safe_window,
                mean_safe_window_quality,
            ),
            "drop_quality_vs_future_path_control_lift": _quality_lift(
                mean_drop_quality_for_future,
                mean_future_path_quality,
            ),
            "future_path_control_by_offset": future_by_offset,
            "high_quality_drop_count": len(high_quality_records),
            "low_quality_drop_count": len(low_quality_records),
            "high_quality_completed_chain_rate": high_rate,
            "low_quality_completed_chain_rate": low_rate,
            "high_quality_chain_rate_gt_low": high_rate > low_rate,
            "early_drop_count": len(early_records),
            "late_drop_count": len(late_records),
            "early_drop_quality": early_quality,
            "late_drop_quality": late_quality,
            "late_vs_early_drop_quality_lift": _quality_lift(late_quality, early_quality),
            "late_drop_quality_gt_early_by_5pct": late_quality >= early_quality * 1.05 if early_quality > 0 else False,
            "drop_quality_direction_vs_current": mean_drop_quality > mean_current_quality,
            "drop_quality_direction_vs_nearby": mean_drop_quality > mean_nearby_quality,
            "drop_quality_direction_vs_visible": mean_drop_quality > mean_visible_quality,
            "drop_quality_direction_vs_visible_best": mean_drop_quality > mean_visible_best_quality,
            "drop_quality_direction_vs_future_path": mean_drop_quality_for_future > mean_future_path_quality,
            "drop_quality_direction_vs_hunger_recovery": (
                mean_drop_quality_for_recovery > mean_hunger_recovery_quality
            ),
            "drop_quality_direction_vs_safe_window": (
                mean_drop_quality_for_safe_window > mean_safe_window_quality
            ),
            "seed_drop_context_counts": record_value_counts("last_drop_context"),
            "seed_drop_context_fractions": {
                context: _round_rate(count, len(records))
                for context, count in record_value_counts("last_drop_context").items()
            },
            "seed_drop_instinct_counts": record_value_counts("last_drop_instinct"),
            "seed_drop_food_contact_counts": record_value_counts("last_drop_food_contact"),
            "seed_drop_safe_window_counts": record_value_counts("last_drop_safe_window"),
            "seed_drop_critical_hunger_counts": record_value_counts("last_drop_critical_hunger"),
            "safe_window_drop_fraction": record_fraction("last_drop_safe_window", "1"),
            "critical_hunger_drop_fraction": record_fraction("last_drop_critical_hunger", "1"),
            "balanced_drop_fraction": record_fraction("last_drop_instinct", "balanced"),
            "safe_or_balanced_drop_fraction": _round_rate(
                sum(
                    1
                    for record in records
                    if str(record.get("last_drop_safe_window")) == "1"
                    or str(record.get("last_drop_instinct")) == "balanced"
                ),
                len(records),
            ),
            "had_hunger_while_carried_fraction": _round_rate(
                sum(1 for record in records if bool(record.get("had_hunger_while_carried"))),
                len(records),
            ),
            "seed_pick_instinct_counts": record_value_counts("last_pick_instinct"),
            "seed_pick_food_contact_counts": record_value_counts("last_pick_food_contact"),
            "context_matched_site_selection_metrics": {
                context: context_metrics(context)
                for context in ("hunger", "food_contact", "balanced_random")
            },
            "phase5_pathway_hotspots": {
                "pickup_positions": top_record_positions(records, "last_pick_x", "last_pick_y"),
                "drop_positions": top_record_positions(records, "last_drop_x", "last_drop_y"),
                "completed_chain_drop_positions": top_record_positions(
                    [record for record in records if _seed_completed_chain(record)],
                    "last_drop_x",
                    "last_drop_y",
                ),
                "completed_chain_pickup_positions": top_record_positions(
                    [record for record in records if _seed_completed_chain(record)],
                    "last_pick_x",
                    "last_pick_y",
                ),
            },
            "sample_site_selection_records": [
                {
                    "seed": record.get("seed_id"),
                    "agent": record.get("moved_by_agent"),
                    "drop_tick": record.get("last_drop_tick"),
                    "drop_context": record.get("last_drop_context"),
                    "drop_instinct": record.get("last_drop_instinct"),
                    "drop": record.get("drop_site_quality"),
                    "current_control": record.get("current_position_control_quality"),
                    "nearby_control": record.get("nearby_control_quality"),
                    "visible_control": record.get("visible_control_quality"),
                    "visible_best_control": record.get("visible_best_control_quality"),
                    "future_path_control_qualities": record.get("future_path_control_qualities"),
                    "completed_chain": _seed_completed_chain(record),
                }
                for record in records[:8]
            ],
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
            if agent.alive and agent.carried_seed_id is not None:
                effective_vision = agent.body.effective_vision
                if hasattr(agent, "_effective_vision"):
                    effective_vision = agent._effective_vision(env.is_night)
                carried_key = (agent.agent_id, agent.carried_seed_id)
                carried_snapshot = {
                    "tick": current_tick,
                    "x": agent.x,
                    "y": agent.y,
                    "vision_radius": max(1, min(5, int(effective_vision))),
                    "instinct": agent.instinct_state,
                    "energy": round(agent.energy, 3),
                    "hunger": round(agent.hunger_level, 3),
                    "fear": round(agent.fear_level, 3),
                    "cold": round(agent.cold_level, 3),
                    "comfort": round(agent.comfort_level, 3),
                    "safety": round(agent.safety_feeling, 3),
                    "quality": _site_quality_snapshot(env, agent.x, agent.y),
                }
                carried_seed_position_controls[carried_key] = carried_snapshot
                state_window = carried_seed_state_windows.setdefault(
                    carried_key,
                    {
                        "had_hunger": False,
                        "first_hunger_tick": None,
                        "hunger_recovery_control": None,
                        "first_hunger_recovery_tick": None,
                        "safe_window_control": None,
                        "first_safe_window_tick": None,
                        "carry_ticks": 0,
                    },
                )
                state_window["carry_ticks"] = int(state_window.get("carry_ticks", 0)) + 1
                is_hunger_window = agent.instinct_state == "hunger"
                if is_hunger_window:
                    state_window["had_hunger"] = True
                    if state_window.get("first_hunger_tick") is None:
                        state_window["first_hunger_tick"] = current_tick
                elif bool(state_window.get("had_hunger")) and state_window.get("hunger_recovery_control") is None:
                    state_window["hunger_recovery_control"] = carried_snapshot
                    state_window["first_hunger_recovery_tick"] = current_tick
                is_safe_window = (
                    agent.instinct_state == "balanced"
                    and agent.hunger_level <= getattr(args, "seed_drop_safe_hunger_max", 0.55)
                    and agent.fear_level <= getattr(args, "seed_drop_safe_fear_max", 0.45)
                    and agent.cold_level <= getattr(args, "seed_drop_safe_cold_max", 0.45)
                    and agent.safety_feeling >= getattr(args, "seed_drop_safe_safety_min", 0.45)
                )
                if is_safe_window and state_window.get("safe_window_control") is None:
                    state_window["safe_window_control"] = carried_snapshot
                    state_window["first_safe_window_tick"] = current_tick

        newborns: list[Agent] = []
        for agent in list(agents):
            wants_reproduction = agent.tick(env, rng)
            # Reproduction funnel: tally which gate(s) block each adult female that
            # reached the reproduction check this tick (sex == female, balanced).
            if agent.alive and agent.sex == "female" and agent.current_stage == "adult":
                _dbg = getattr(agent, "reproduction_debug", {})
                _reasons = _dbg.get("reasons")
                if _reasons is not None:
                    repro_funnel_checks[0] += 1
                    for _r in _reasons:
                        repro_funnel[_r] += 1
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
                agent_death_reasons[getattr(agent, "death_reason", None) or "unknown"] += 1
                agents.remove(agent)

        agents.extend(newborns)
        peak_population = max(peak_population, len(agents))
        if current_tick % 200 == 0:
            diet_snap: Counter[str] = Counter()
            gen_snap: Counter[int] = Counter()
            for _a in agents:
                for _k, _c in getattr(_a, "meals_by_type", {}).items():
                    diet_snap[_k] += int(_c)
                gen_snap[int(getattr(_a, "generation", 0))] += 1
            population_trajectory.append({
                "tick": current_tick,
                "population": len(agents),
                "births": total_births,
                "deaths": sum(agent_death_reasons.values()),
                "mean_energy": round(sum(a.energy for a in agents) / len(agents), 1) if agents else 0,
                "raw_seed_meals": diet_snap.get("raw_seed", 0),
                "raw_plant_meals": diet_snap.get("raw_plant", 0),
                "max_generation": max(gen_snap) if gen_snap else 0,
                "generation_counts": dict(sorted(gen_snap.items())),
            })
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
        active_phase5_future_watchers: list[dict[str, object]] = []
        for watcher in phase5_future_path_watchers:
            drop_tick = int(watcher.get("drop_tick", current_tick))
            agent_id = watcher.get("agent")
            seed_id_for_watcher = watcher.get("seed_id")
            sampled_offsets = watcher.get("sampled_offsets")
            if not isinstance(sampled_offsets, set):
                sampled_offsets = set()
                watcher["sampled_offsets"] = sampled_offsets
            if not isinstance(agent_id, int) or not isinstance(seed_id_for_watcher, int):
                continue
            record = seed_records.get(seed_id_for_watcher)
            if record is None:
                continue
            future_qualities = record.get("future_path_control_qualities")
            if not isinstance(future_qualities, dict):
                future_qualities = {}
                record["future_path_control_qualities"] = future_qualities
            for offset in phase5_future_control_offsets:
                if offset in sampled_offsets or current_tick < drop_tick + offset:
                    continue
                sampled_offsets.add(offset)
                agent_position = alive_positions_by_agent.get(agent_id)
                if agent_position is None:
                    future_qualities[str(offset)] = None
                    continue
                future_qualities[str(offset)] = _site_quality_snapshot(env, agent_position[0], agent_position[1])
            if len(sampled_offsets) < len(phase5_future_control_offsets):
                active_phase5_future_watchers.append(watcher)
        phase5_future_path_watchers = active_phase5_future_watchers

        world_area = max(1, env.width * env.height)
        for watcher in phase4_drop_watchers:
            drop_tick = int(watcher.get("drop_tick", current_tick))
            watcher_age = current_tick - drop_tick
            if watcher_age < phase4_patch_return_min_delay_ticks:
                continue
            if watcher_age > phase4_patch_return_max_age_ticks:
                continue
            watcher_x = watcher.get("x")
            watcher_y = watcher.get("y")
            if not isinstance(watcher_x, int) or not isinstance(watcher_y, int):
                continue
            expected_hit_rate = (
                _bounded_manhattan_area(env.width, env.height, watcher_x, watcher_y, phase4_patch_radius)
                / world_area
            )
            for agent_id, agent_position in alive_positions_by_agent.items():
                distance_to_drop = _manhattan(agent_position, (watcher_x, watcher_y))
                seed_id_for_watcher = watcher.get("seed_id")
                seed_for_watcher = seed_records.get(seed_id_for_watcher) if isinstance(seed_id_for_watcher, int) else None
                fruit_tick = None
                if seed_for_watcher is not None and isinstance(seed_for_watcher.get("first_fruited_tick"), int):
                    fruit_tick = int(seed_for_watcher["first_fruited_tick"])
                return_phase = "post_fruit" if fruit_tick is not None and current_tick >= fruit_tick else "pre_fruit"
                watcher["return_opportunities"] = int(watcher.get("return_opportunities", 0)) + 1
                watcher["random_expected_return_hits"] = (
                    float(watcher.get("random_expected_return_hits", 0.0)) + expected_hit_rate
                )
                if agent_id == watcher.get("agent"):
                    if watcher.get("dropper_left_tick") is None and watcher_age > 0 and distance_to_drop > phase4_patch_radius:
                        watcher["dropper_left_tick"] = current_tick
                    left_tick = watcher.get("dropper_left_tick")
                    if isinstance(left_tick, int) and current_tick - left_tick >= phase4_patch_return_min_delay_ticks:
                        watcher["dropper_return_opportunities_after_left"] = int(
                            watcher.get("dropper_return_opportunities_after_left", 0)
                        ) + 1
                        watcher["dropper_random_expected_return_hits"] = (
                            float(watcher.get("dropper_random_expected_return_hits", 0.0)) + expected_hit_rate
                        )
                        if distance_to_drop <= phase4_patch_radius:
                            watcher["dropper_return_tick_hits_after_left"] = int(
                                watcher.get("dropper_return_tick_hits_after_left", 0)
                            ) + 1
                            watcher["dropper_returned_after_left"] = True
                            if watcher.get("dropper_first_return_tick_after_left") is None:
                                watcher["dropper_first_return_tick_after_left"] = current_tick
                            if return_phase == "post_fruit":
                                watcher["dropper_post_fruit_returned"] = True
                            else:
                                watcher["dropper_pre_fruit_returned"] = True
                    if distance_to_drop <= phase4_patch_radius:
                        watcher["return_tick_hits"] = int(watcher.get("return_tick_hits", 0)) + 1
                        returned_agents = watcher.get("returned_agents")
                        if isinstance(returned_agents, set):
                            returned_agents.add(agent_id)
                        if watcher.get("first_return_tick") is None:
                            watcher["first_return_tick"] = current_tick
                    continue

                watcher["non_dropper_return_opportunities"] = int(
                    watcher.get("non_dropper_return_opportunities", 0)
                ) + 1
                watcher["non_dropper_random_expected_return_hits"] = (
                    float(watcher.get("non_dropper_random_expected_return_hits", 0.0)) + expected_hit_rate
                )
                if distance_to_drop <= phase4_patch_radius:
                    watcher["non_dropper_return_tick_hits"] = int(watcher.get("non_dropper_return_tick_hits", 0)) + 1
                    non_dropper_agents = watcher.get("non_dropper_returned_agents")
                    if isinstance(non_dropper_agents, set):
                        non_dropper_agents.add(agent_id)
                    if return_phase == "post_fruit":
                        post_fruit_agents = watcher.get("post_fruit_returned_agents")
                        if isinstance(post_fruit_agents, set):
                            post_fruit_agents.add(agent_id)
                    else:
                        pre_fruit_agents = watcher.get("pre_fruit_returned_agents")
                        if isinstance(pre_fruit_agents, set):
                            pre_fruit_agents.add(agent_id)

                if distance_to_drop <= phase4_patch_radius:
                    watcher["return_tick_hits"] = int(watcher.get("return_tick_hits", 0)) + 1
                    returned_agents = watcher.get("returned_agents")
                    if isinstance(returned_agents, set):
                        returned_agents.add(agent_id)
                    if watcher.get("first_return_tick") is None:
                        watcher["first_return_tick"] = current_tick
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
            elif kind == "gut_seed_ingested":
                # v2 endozoochory: a harvested seed entered the eater's gut. From
                # this point the seed is agent-handled, so retag it out of the
                # agent-independent control group (it was tagged harvest_seed_dropped
                # at the eating spot just before being routed to the gut).
                seed_id = _event_int(event, "seed")
                agent_id = _event_int(event, "agent")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    record["source_kind"] = "gut_transit"
                    record["gut_ingested_tick"] = current_tick
                    record["gut_ingested_by_agent"] = agent_id
                    if position is not None:
                        record["gut_ingest_x"] = position[0]
                        record["gut_ingest_y"] = position[1]
                        if record.get("origin_x") is None:
                            record["origin_x"] = position[0]
                            record["origin_y"] = position[1]
            elif kind == "gut_seed_excreted":
                # v2 endozoochory: the seed survived transit and was deposited at
                # the agent's later position. This is real agent dispersal, so mark
                # it agent_moved with the EXCRETION coords as the drop site.
                seed_id = _event_int(event, "seed")
                agent_id = _event_int(event, "agent")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    record["source_kind"] = "gut_transit"
                    record["gut_excreted_tick"] = current_tick
                    record["gut_excreted_by_agent"] = agent_id
                    record["agent_moved"] = True
                    record["moved_by_agent"] = agent_id
                    agent_moved_seed_ids.add(seed_id)
                    if agent_id is not None:
                        moved_seed_agents.add(agent_id)
                    if position is not None:
                        record["last_drop_x"] = position[0]
                        record["last_drop_y"] = position[1]
                        record["last_dropped_by_agent"] = agent_id
                        record["last_drop_tick"] = current_tick
                        ingest_x = record.get("gut_ingest_x")
                        ingest_y = record.get("gut_ingest_y")
                        if isinstance(ingest_x, int) and isinstance(ingest_y, int):
                            move_distance = abs(position[0] - ingest_x) + abs(position[1] - ingest_y)
                            record["max_move_distance"] = max(int(record.get("max_move_distance", 0)), move_distance)
            elif kind == "gut_seed_killed":
                # v2 seed predation: gut acid cracked the coat. The seed is
                # agent-handled (so excluded from control) but destroyed, so it can
                # never complete a chain. This is the seed-predator outcome.
                seed_id = _event_int(event, "seed")
                agent_id = _event_int(event, "agent")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    record["source_kind"] = "gut_transit"
                    record["agent_moved"] = True
                    record["moved_by_agent"] = agent_id
                    agent_moved_seed_ids.add(seed_id)
                    if agent_id is not None:
                        moved_seed_agents.add(agent_id)
                    record["gut_killed_tick"] = current_tick
                    record["death_tick"] = current_tick
                    record["death_reason"] = "gut_acid"
                    if position is not None:
                        record["last_drop_x"] = position[0]
                        record["last_drop_y"] = position[1]
            elif kind == "seed_picked":
                seed_id = _event_int(event, "seed")
                agent_id = _event_int(event, "agent")
                if seed_id is not None:
                    record = seed_record(seed_id)
                    pick_instinct = _event_field(event, "instinct") or "unknown"
                    pick_food_contact = _event_field(event, "food_contact") or "unknown"
                    event_attribute_counts["seed_pick_instinct"][pick_instinct] += 1
                    event_attribute_counts["seed_pick_food_contact"][pick_food_contact] += 1
                    record["last_pick_instinct"] = pick_instinct
                    record["last_pick_food_contact"] = pick_food_contact
                    for field_name in ("energy", "hunger", "fear", "cold", "comfort"):
                        value = _event_float(event, field_name)
                        if value is not None:
                            record[f"last_pick_{field_name}"] = value
                            event_numeric_values[f"seed_pick_{field_name}"].append(value)
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
                    drop_context = _event_field(event, "context") or "unknown"
                    drop_instinct = _event_field(event, "instinct") or "unknown"
                    drop_food_contact = _event_field(event, "food_contact") or "unknown"
                    drop_safe_window = _event_field(event, "safe_window") or "unknown"
                    drop_critical_hunger = _event_field(event, "critical_hunger") or "unknown"
                    event_attribute_counts["seed_drop_context"][drop_context] += 1
                    event_attribute_counts["seed_drop_instinct"][drop_instinct] += 1
                    event_attribute_counts["seed_drop_food_contact"][drop_food_contact] += 1
                    event_attribute_counts["seed_drop_safe_window"][drop_safe_window] += 1
                    event_attribute_counts["seed_drop_critical_hunger"][drop_critical_hunger] += 1
                    record["last_drop_context"] = drop_context
                    record["last_drop_instinct"] = drop_instinct
                    record["last_drop_food_contact"] = drop_food_contact
                    record["last_drop_safe_window"] = drop_safe_window
                    record["last_drop_critical_hunger"] = drop_critical_hunger
                    for field_name in ("energy", "hunger", "fear", "cold", "comfort", "safety", "drop_chance"):
                        value = _event_float(event, field_name)
                        if value is not None:
                            record_key = "last_drop_chance" if field_name == "drop_chance" else f"last_drop_{field_name}"
                            numeric_key = "seed_drop_chance" if field_name == "drop_chance" else f"seed_drop_{field_name}"
                            record[record_key] = value
                            event_numeric_values[numeric_key].append(value)
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
                        drop_quality = _site_quality_snapshot(env, position[0], position[1])
                        record["drop_site_quality"] = drop_quality
                        current_control = None
                        if agent_id is not None:
                            carried_control = carried_seed_position_controls.get((agent_id, seed_id))
                            if isinstance(carried_control, dict) and isinstance(carried_control.get("quality"), dict):
                                current_control = carried_control["quality"]
                            state_window = carried_seed_state_windows.get((agent_id, seed_id))
                            if isinstance(state_window, dict):
                                recovery_control = state_window.get("hunger_recovery_control")
                                safe_window_control = state_window.get("safe_window_control")
                                if isinstance(recovery_control, dict) and isinstance(recovery_control.get("quality"), dict):
                                    record["hunger_recovery_control_quality"] = recovery_control["quality"]
                                if isinstance(safe_window_control, dict) and isinstance(safe_window_control.get("quality"), dict):
                                    record["safe_window_control_quality"] = safe_window_control["quality"]
                                record["had_hunger_while_carried"] = bool(state_window.get("had_hunger", False))
                                record["carry_ticks_observed"] = int(state_window.get("carry_ticks", 0) or 0)
                                record["first_hunger_tick_while_carried"] = state_window.get("first_hunger_tick")
                                record["first_hunger_recovery_tick"] = state_window.get("first_hunger_recovery_tick")
                                record["first_safe_window_tick"] = state_window.get("first_safe_window_tick")
                        if current_control is None:
                            pick_x = record.get("last_pick_x")
                            pick_y = record.get("last_pick_y")
                            if isinstance(pick_x, int) and isinstance(pick_y, int):
                                current_control = _site_quality_snapshot(env, pick_x, pick_y)
                        nearby_control = _nearby_quality_control(env, position[0], position[1], radius=3)
                        visible_radius = 3
                        if agent_id is not None:
                            carried_control = carried_seed_position_controls.get((agent_id, seed_id))
                            if isinstance(carried_control, dict) and isinstance(carried_control.get("vision_radius"), int):
                                visible_radius = int(carried_control["vision_radius"])
                        visible_control, visible_best_control = _visible_quality_controls(
                            env,
                            position[0],
                            position[1],
                            radius=visible_radius,
                        )
                        random_control = _deterministic_world_control(env, seed_id, current_tick)
                        record["current_position_control_quality"] = current_control
                        record["nearby_control_quality"] = nearby_control
                        record["visible_control_quality"] = visible_control
                        record["visible_best_control_quality"] = visible_best_control
                        record["random_world_control_quality"] = random_control
                        if isinstance(current_control, dict):
                            record["drop_vs_current_position_lift"] = _quality_lift(
                                float(drop_quality["quality_score_total"]),
                                float(current_control["quality_score_total"]),
                            )
                        if isinstance(nearby_control, dict):
                            record["drop_vs_nearby_control_lift"] = _quality_lift(
                                float(drop_quality["quality_score_total"]),
                                float(nearby_control["quality_score_total"]),
                            )
                        if isinstance(visible_control, dict):
                            record["drop_vs_visible_control_lift"] = _quality_lift(
                                float(drop_quality["quality_score_total"]),
                                float(visible_control["quality_score_total"]),
                            )
                        if isinstance(visible_best_control, dict):
                            record["drop_vs_visible_best_control_lift"] = _quality_lift(
                                float(drop_quality["quality_score_total"]),
                                float(visible_best_control["quality_score_total"]),
                            )
                        recovery_quality = record.get("hunger_recovery_control_quality")
                        if isinstance(recovery_quality, dict):
                            record["drop_vs_hunger_recovery_position_lift"] = _quality_lift(
                                float(drop_quality["quality_score_total"]),
                                float(recovery_quality["quality_score_total"]),
                            )
                        safe_window_quality = record.get("safe_window_control_quality")
                        if isinstance(safe_window_quality, dict):
                            record["drop_vs_safe_window_position_lift"] = _quality_lift(
                                float(drop_quality["quality_score_total"]),
                                float(safe_window_quality["quality_score_total"]),
                            )
                        record["drop_vs_random_world_lift"] = _quality_lift(
                            float(drop_quality["quality_score_total"]),
                            float(random_control["quality_score_total"]),
                        )
                        if agent_id is not None:
                            carried_seed_position_controls.pop((agent_id, seed_id), None)
                            carried_seed_state_windows.pop((agent_id, seed_id), None)
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
                                phase4_drop_watchers.append(
                                    {
                                        "seed_id": seed_id,
                                        "agent": agent_id,
                                        "x": position[0],
                                        "y": position[1],
                                        "drop_tick": current_tick,
                                        "pre_drop_visit_count_near": _visit_count_near(
                                            visit_counter,
                                            position[0],
                                            position[1],
                                            phase4_patch_radius,
                                        ),
                                        "return_tick_hits": 0,
                                        "return_opportunities": 0,
                                        "random_expected_return_hits": 0.0,
                                        "returned_agents": set(),
                                        "first_return_tick": None,
                                        "dropper_left_tick": None,
                                        "dropper_returned_after_left": False,
                                        "dropper_return_tick_hits_after_left": 0,
                                        "dropper_return_opportunities_after_left": 0,
                                        "dropper_random_expected_return_hits": 0.0,
                                        "dropper_first_return_tick_after_left": None,
                                        "dropper_pre_fruit_returned": False,
                                        "dropper_post_fruit_returned": False,
                                        "non_dropper_return_tick_hits": 0,
                                        "non_dropper_return_opportunities": 0,
                                        "non_dropper_random_expected_return_hits": 0.0,
                                        "non_dropper_returned_agents": set(),
                                        "pre_fruit_returned_agents": set(),
                                        "post_fruit_returned_agents": set(),
                                    }
                                )
                                phase5_future_path_watchers.append(
                                    {
                                        "seed_id": seed_id,
                                        "agent": agent_id,
                                        "x": position[0],
                                        "y": position[1],
                                        "drop_tick": current_tick,
                                        "sampled_offsets": set(),
                                    }
                                )
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
                    reward_x, reward_y = position
                    shuffle_radius = max(0, int(getattr(args, "reward_memory_shuffle_radius", 0) or 0))
                    if shuffle_radius > 0:
                        for _ in range(max(8, shuffle_radius * shuffle_radius * 2)):
                            dx = rng.randint(-shuffle_radius, shuffle_radius)
                            dy = rng.randint(-shuffle_radius, shuffle_radius)
                            if abs(dx) + abs(dy) > shuffle_radius:
                                continue
                            candidate_x = max(0, min(env.width - 1, position[0] + dx))
                            candidate_y = max(0, min(env.height - 1, position[1] + dy))
                            if env.is_walkable(candidate_x, candidate_y):
                                reward_x, reward_y = candidate_x, candidate_y
                                break
                    reward_counts_by_agent[agent_id] += 1
                    reward_records.append(
                        {
                            "id": next_reward_record_id,
                            "agent": agent_id,
                            "x": reward_x,
                            "y": reward_y,
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
                "phase4_patch_metrics": phase4_patch_metrics_summary(),
                "phase5_site_selection_metrics": phase5_site_selection_metrics_summary(),
                "events": {
                    "build_nest": event_counts["build_nest"],
                    "tend_food_patch": event_counts["tend_food_patch"],
                    "food_patch_tended": event_counts["food_patch_tended"],
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
        "metabolism_model": getattr(args, "metabolism_model", "v1"),
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
        "diet_by_kind": _diet_by_kind(agents),
        "agent_death_reasons": dict(agent_death_reasons),
        "reproduction_funnel": {
            "adult_female_checks": repro_funnel_checks[0],
            "block_rate_by_gate": {
                gate: round(cnt / repro_funnel_checks[0], 3)
                for gate, cnt in repro_funnel.most_common()
            } if repro_funnel_checks[0] else {},
        },
        "population_trajectory": population_trajectory,
        "energy_economy": _energy_economy(agents, env),
        "learned_food_value": _learned_food_value(agents),
        "food_spawned_by_kind": dict(env.food_spawned_by_kind),
        "plant_origins": _plant_origin_summary(env),
        "affect": _affect_summary(agents),
        "agent_state": _agent_state_summary(agents),
        "food_sources": dict(Counter(resource.source for resource in env.food_positions.values())),
        "plant_lifecycle_food": _plant_lifecycle_food_summary(env, event_counts),
        "learning_metrics": learning_metrics_summary(),
        "seed_causality_metrics": seed_causality_metrics_summary(),
        "phase4_patch_metrics": phase4_patch_metrics_summary(),
        "phase5_site_selection_metrics": phase5_site_selection_metrics_summary(),
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
        "sample_gut_seed_ingested": event_samples_by_kind.get("gut_seed_ingested", []),
        "sample_gut_seed_excreted": event_samples_by_kind.get("gut_seed_excreted", []),
        "sample_gut_seed_killed": event_samples_by_kind.get("gut_seed_killed", []),
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
    parser.add_argument("--phase4-patch-radius", type=int, default=4)
    parser.add_argument("--phase4-min-patch-moved-seed-drops", type=int, default=3)
    parser.add_argument("--phase4-patch-return-min-delay-ticks", type=int, default=20)
    parser.add_argument("--phase4-patch-return-max-age-ticks", type=int, default=2000)
    parser.add_argument("--phase4-min-matched-control-seeds", type=int, default=5)
    parser.add_argument("--phase5-future-control-offsets", type=_int_list, default=[10, 25, 50])
    parser.add_argument("--food-signal-radius-cap", type=int, default=None)
    parser.add_argument("--plant-lifecycle-food-signal-weight", type=float, default=1.35)
    parser.add_argument("--seed-hunger-drop-bonus", type=float, default=0.06)
    parser.add_argument("--metabolism-model", choices=["v1", "v2"], default="v1")
    parser.add_argument("--seed-drop-block-critical-hunger", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--seed-drop-safe-window-only", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--seed-drop-safe-hunger-max", type=float, default=0.55)
    parser.add_argument("--seed-drop-safe-fear-max", type=float, default=0.45)
    parser.add_argument("--seed-drop-safe-cold-max", type=float, default=0.45)
    parser.add_argument("--seed-drop-safe-safety-min", type=float, default=0.45)
    parser.add_argument("--reward-memory-shuffle-radius", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = run_watch(args)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"type": "result", "output": str(args.output), **result}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
