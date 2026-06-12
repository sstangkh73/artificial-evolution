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
    total_births = 0
    peak_population = len(agents)
    stop_reason = "max_ticks_reached"
    stop_signals: list[dict[str, object]] = []
    started = time.monotonic()
    next_progress_at = started

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

        for event in tick_events:
            kind = _event_type(event)
            event_counts[kind] += 1
            first_event_tick.setdefault(kind, current_tick)
            position = _event_position(event)
            if position is not None and kind in event_location_counts:
                event_location_counts[kind][position] += 1
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
        "event_location_hotspots": _top_event_locations(event_location_counts),
        "mean_photosynthetic_light": round(env.mean_photosynthetic_light(), 3),
        "mean_soil_nutrients": round(env.mean_soil_nutrients(), 3),
        "event_counts": dict(event_counts),
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = run_watch(args)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"type": "result", "output": str(args.output), **result}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
