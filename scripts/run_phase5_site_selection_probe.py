from __future__ import annotations

import argparse
import contextlib
import csv
import json
from pathlib import Path
import statistics
import sys
from types import SimpleNamespace
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_long_emergence_watch import run_watch


def _parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _mean(rows: list[dict[str, Any]], field: str) -> float:
    values = [
        float(row[field])
        for row in rows
        if row.get(field) not in {None, ""}
    ]
    if not values:
        return 0.0
    return round(statistics.fmean(values), 5)


def _conditions(args: argparse.Namespace) -> list[dict[str, Any]]:
    all_conditions = [
        {
            "condition_id": "baseline_100x100",
            "is_core_gate": True,
            "description": "Core Phase 5 tuned 100x100 ecology.",
            "seeds": args.core_seeds,
            "time_limit_seconds": args.core_time_limit_seconds,
            "width": 100,
            "height": 100,
            "max_food": 2000,
            "max_plant_seeds": 7600,
            "base_food_spawn_per_tick": 4,
            "frontier_band": 10,
            "food_signal_radius_cap": None,
            "plant_lifecycle_food_signal_weight": 1.35,
            "seed_hunger_drop_bonus": 0.06,
        },
        {
            "condition_id": "hunger_neutral_seed_drop_100x100",
            "is_core_gate": False,
            "description": "100x100 ablation: remove direct hunger bonus from primitive seed dropping.",
            "seeds": args.core_seeds,
            "time_limit_seconds": args.core_time_limit_seconds,
            "width": 100,
            "height": 100,
            "max_food": 2000,
            "max_plant_seeds": 7600,
            "base_food_spawn_per_tick": 4,
            "frontier_band": 10,
            "food_signal_radius_cap": None,
            "plant_lifecycle_food_signal_weight": 1.35,
            "seed_hunger_drop_bonus": 0.0,
        },
        {
            "condition_id": "no_hunger_seed_drop_bonus_100x100",
            "is_core_gate": False,
            "description": "Phase 5.5: remove direct hunger bonus from primitive seed dropping.",
            "seeds": args.core_seeds,
            "time_limit_seconds": args.core_time_limit_seconds,
            "width": 100,
            "height": 100,
            "max_food": 2000,
            "max_plant_seeds": 7600,
            "base_food_spawn_per_tick": 4,
            "frontier_band": 10,
            "food_signal_radius_cap": None,
            "plant_lifecycle_food_signal_weight": 1.35,
            "seed_hunger_drop_bonus": 0.0,
        },
        {
            "condition_id": "critical_hunger_drop_blocked_100x100",
            "is_core_gate": False,
            "description": "Phase 5.5: block seed drops only while critical hunger controls behavior.",
            "seeds": args.core_seeds,
            "time_limit_seconds": args.core_time_limit_seconds,
            "width": 100,
            "height": 100,
            "max_food": 2000,
            "max_plant_seeds": 7600,
            "base_food_spawn_per_tick": 4,
            "frontier_band": 10,
            "food_signal_radius_cap": None,
            "plant_lifecycle_food_signal_weight": 1.35,
            "seed_hunger_drop_bonus": 0.06,
            "seed_drop_block_critical_hunger": True,
        },
        {
            "condition_id": "safe_window_seed_drop_only_100x100",
            "is_core_gate": False,
            "description": "Phase 5.5: allow seed drops only when the carrier is balanced and safe.",
            "seeds": args.core_seeds,
            "time_limit_seconds": args.core_time_limit_seconds,
            "width": 100,
            "height": 100,
            "max_food": 2000,
            "max_plant_seeds": 7600,
            "base_food_spawn_per_tick": 4,
            "frontier_band": 10,
            "food_signal_radius_cap": None,
            "plant_lifecycle_food_signal_weight": 1.35,
            "seed_hunger_drop_bonus": 0.06,
            "seed_drop_safe_window_only": True,
            "seed_drop_safe_hunger_max": 1.0,
            "seed_drop_safe_fear_max": 1.0,
            "seed_drop_safe_cold_max": 1.0,
            "seed_drop_safe_safety_min": 0.0,
        },
        {
            "condition_id": "reward_memory_disabled_100x100",
            "is_core_gate": False,
            "description": "Phase 5.5: disable plant-food reward memory.",
            "seeds": args.core_seeds,
            "time_limit_seconds": args.core_time_limit_seconds,
            "width": 100,
            "height": 100,
            "max_food": 2000,
            "max_plant_seeds": 7600,
            "base_food_spawn_per_tick": 4,
            "frontier_band": 10,
            "food_signal_radius_cap": None,
            "plant_lifecycle_food_signal_weight": 1.35,
            "seed_hunger_drop_bonus": 0.06,
            "learning_reward_memory_limit": 0,
        },
        {
            "condition_id": "reward_memory_shuffled_100x100",
            "is_core_gate": False,
            "description": "Phase 5.5: keep reward memory volume but spatially shuffle reward locations.",
            "seeds": args.core_seeds,
            "time_limit_seconds": args.core_time_limit_seconds,
            "width": 100,
            "height": 100,
            "max_food": 2000,
            "max_plant_seeds": 7600,
            "base_food_spawn_per_tick": 4,
            "frontier_band": 10,
            "food_signal_radius_cap": None,
            "plant_lifecycle_food_signal_weight": 1.35,
            "seed_hunger_drop_bonus": 0.06,
            "reward_memory_shuffle_radius": 16,
        },
        {
            "condition_id": "low_food_signal_100x100",
            "is_core_gate": False,
            "description": "100x100 ablation: lower food signal radius and plant-lifecycle attraction weight.",
            "seeds": args.core_seeds,
            "time_limit_seconds": args.core_time_limit_seconds,
            "width": 100,
            "height": 100,
            "max_food": 2000,
            "max_plant_seeds": 7600,
            "base_food_spawn_per_tick": 4,
            "frontier_band": 10,
            "food_signal_radius_cap": 2,
            "plant_lifecycle_food_signal_weight": 1.0,
            "seed_hunger_drop_bonus": 0.06,
        },
        {
            "condition_id": "large_world_200x200_same_density_long_budget",
            "is_core_gate": False,
            "description": "200x200 stress: scale food and seed capacity with area; longer budget.",
            "seeds": args.stress_seeds,
            "time_limit_seconds": args.stress_time_limit_seconds,
            "width": 200,
            "height": 200,
            "max_food": 8000,
            "max_plant_seeds": 30400,
            "base_food_spawn_per_tick": 16,
            "frontier_band": 20,
            "food_signal_radius_cap": None,
            "plant_lifecycle_food_signal_weight": 1.35,
            "seed_hunger_drop_bonus": 0.06,
        },
        {
            "condition_id": "large_world_200x200_same_population_long_budget",
            "is_core_gate": False,
            "description": "200x200 stress: keep original food/seed counts with same 50-agent population; longer budget.",
            "seeds": args.stress_seeds,
            "time_limit_seconds": args.stress_time_limit_seconds,
            "width": 200,
            "height": 200,
            "max_food": 2000,
            "max_plant_seeds": 7600,
            "base_food_spawn_per_tick": 4,
            "frontier_band": 20,
            "food_signal_radius_cap": None,
            "plant_lifecycle_food_signal_weight": 1.35,
            "seed_hunger_drop_bonus": 0.06,
        },
    ]
    for condition in all_conditions:
        condition.setdefault("seed_drop_block_critical_hunger", False)
        condition.setdefault("seed_drop_safe_window_only", False)
        condition.setdefault("seed_drop_safe_hunger_max", 0.55)
        condition.setdefault("seed_drop_safe_fear_max", 0.45)
        condition.setdefault("seed_drop_safe_cold_max", 0.45)
        condition.setdefault("seed_drop_safe_safety_min", 0.45)
        condition.setdefault("learning_reward_memory_limit", 1200)
        condition.setdefault("reward_memory_shuffle_radius", 0)
    selected = set(args.conditions)
    if "all" in selected:
        return all_conditions
    return [condition for condition in all_conditions if condition["condition_id"] in selected]


def _watch_args(args: argparse.Namespace, condition: dict[str, Any], seed: int) -> SimpleNamespace:
    return SimpleNamespace(
        seed=seed,
        body_index=37,
        initial_population=50,
        max_population=250,
        max_ticks=10_000_000,
        time_limit_seconds=condition["time_limit_seconds"],
        progress_every_seconds=args.progress_every_seconds,
        evaluate_every_ticks=100_000_000,
        event_sample_limit=args.event_sample_limit,
        output=Path(),
        spawn_strategy="frontier_safe_high_food",
        immortal=True,
        width=condition["width"],
        height=condition["height"],
        max_food=condition["max_food"],
        base_food_spawn_per_tick=condition["base_food_spawn_per_tick"],
        food_spawn_multiplier=0.70,
        bootstrap_food_spawn_ticks=300,
        wild_food_spawn_after_bootstrap_multiplier=0.10,
        natural_seed_rain_per_tick=0,
        max_plant_seeds=condition["max_plant_seeds"],
        large_animal_spawn_per_tick=2,
        max_large_animals=28,
        nest_support_food_chance=0.05,
        nest_support_spawn_chance=0.03,
        frontier_band=condition["frontier_band"],
        global_food_decline_per_day=0.012,
        minimum_global_food_multiplier=0.24,
        ambient_food_decay_chance=0.006,
        plant_food_decay_chance=0.0015,
        plant_seed_max_age_multiplier=4.0,
        plant_growth_rate_multiplier=2.0,
        sprout_biomass_loss_multiplier=0.1,
        germination_good_ticks_multiplier=0.5,
        plant_fruiting_interval_multiplier=0.25,
        plant_fruiting_growth_threshold_multiplier=0.5,
        plant_fruiting_chance_multiplier=2.0,
        natural_seed_drop_chance_multiplier=2.0,
        learning_revisit_radius=4,
        learning_revisit_min_delay_ticks=20,
        learning_revisit_max_age_ticks=2000,
        learning_reward_memory_limit=condition["learning_reward_memory_limit"],
        phase3_min_seed_move_distance=1,
        phase4_patch_radius=4,
        phase4_min_patch_moved_seed_drops=3,
        phase4_patch_return_min_delay_ticks=20,
        phase4_patch_return_max_age_ticks=2000,
        phase4_min_matched_control_seeds=5,
        phase5_future_control_offsets=args.future_control_offsets,
        food_signal_radius_cap=condition["food_signal_radius_cap"],
        plant_lifecycle_food_signal_weight=condition["plant_lifecycle_food_signal_weight"],
        seed_hunger_drop_bonus=condition["seed_hunger_drop_bonus"],
        seed_drop_block_critical_hunger=condition["seed_drop_block_critical_hunger"],
        seed_drop_safe_window_only=condition["seed_drop_safe_window_only"],
        seed_drop_safe_hunger_max=condition["seed_drop_safe_hunger_max"],
        seed_drop_safe_fear_max=condition["seed_drop_safe_fear_max"],
        seed_drop_safe_cold_max=condition["seed_drop_safe_cold_max"],
        seed_drop_safe_safety_min=condition["seed_drop_safe_safety_min"],
        reward_memory_shuffle_radius=condition["reward_memory_shuffle_radius"],
    )


def _seed_pass(metrics: dict[str, Any], args: argparse.Namespace) -> bool:
    current_lift = metrics.get("drop_quality_vs_current_position_lift")
    nearby_lift = metrics.get("drop_quality_vs_nearby_control_lift")
    visible_lift = metrics.get("drop_quality_vs_visible_control_lift")
    future_lift = metrics.get("drop_quality_vs_future_path_control_lift")
    late_lift = metrics.get("late_vs_early_drop_quality_lift")
    return (
        current_lift is not None
        and float(current_lift) > args.min_current_position_lift
        and nearby_lift is not None
        and float(nearby_lift) > args.min_nearby_control_lift
        and visible_lift is not None
        and float(visible_lift) > args.min_visible_control_lift
        and future_lift is not None
        and float(future_lift) > args.min_future_path_control_lift
        and bool(metrics.get("high_quality_chain_rate_gt_low", False))
        and late_lift is not None
        and float(late_lift) >= args.min_late_vs_early_lift
    )


def _phase5_5_seed_pass(metrics: dict[str, Any], args: argparse.Namespace) -> bool:
    current_lift = metrics.get("drop_quality_vs_current_position_lift")
    visible_lift = metrics.get("drop_quality_vs_visible_control_lift")
    recovery_lift = metrics.get("drop_quality_vs_hunger_recovery_position_lift")
    safe_window_lift = metrics.get("drop_quality_vs_safe_window_position_lift")
    late_lift = metrics.get("late_vs_early_drop_quality_lift")
    state_control_ok = (
        recovery_lift is not None
        and float(recovery_lift) > args.min_hunger_recovery_lift
    ) or (
        safe_window_lift is not None
        and float(safe_window_lift) > args.min_safe_window_lift
    )
    return (
        current_lift is not None
        and float(current_lift) > args.min_current_position_lift
        and visible_lift is not None
        and float(visible_lift) > args.min_visible_control_lift
        and state_control_ok
        and bool(metrics.get("high_quality_chain_rate_gt_low", False))
        and late_lift is not None
        and float(late_lift) >= args.min_late_vs_early_lift
    )


def _direction_consistent(metrics: dict[str, Any]) -> bool:
    late_lift = metrics.get("late_vs_early_drop_quality_lift")
    return (
        bool(metrics.get("drop_quality_direction_vs_current", False))
        and bool(metrics.get("drop_quality_direction_vs_nearby", False))
        and bool(metrics.get("drop_quality_direction_vs_visible", False))
        and bool(metrics.get("drop_quality_direction_vs_future_path", False))
        and late_lift is not None
        and float(late_lift) > 1.0
    )


def _phase5_5_direction_consistent(metrics: dict[str, Any]) -> bool:
    late_lift = metrics.get("late_vs_early_drop_quality_lift")
    state_direction = bool(metrics.get("drop_quality_direction_vs_hunger_recovery", False)) or bool(
        metrics.get("drop_quality_direction_vs_safe_window", False)
    )
    return (
        bool(metrics.get("drop_quality_direction_vs_current", False))
        and bool(metrics.get("drop_quality_direction_vs_visible", False))
        and state_direction
        and late_lift is not None
        and float(late_lift) > 1.0
    )


def _component(metrics: dict[str, Any], group: str, field: str) -> float:
    components = metrics.get(group, {})
    if not isinstance(components, dict):
        return 0.0
    return float(components.get(field, 0.0))


def _context_metric(metrics: dict[str, Any], context: str, field: str) -> float:
    context_metrics = metrics.get("context_matched_site_selection_metrics", {})
    if not isinstance(context_metrics, dict):
        return 0.0
    values = context_metrics.get(context, {})
    if not isinstance(values, dict):
        return 0.0
    value = values.get(field)
    if value in {None, ""}:
        return 0.0
    return float(value)


def _context_fraction(metrics: dict[str, Any], context: str) -> float:
    fractions = metrics.get("seed_drop_context_fractions", {})
    if not isinstance(fractions, dict):
        return 0.0
    return float(fractions.get(context, 0.0) or 0.0)


def _summarize_run(result: dict[str, Any], condition: dict[str, Any], seed: int, args: argparse.Namespace) -> dict[str, Any]:
    metrics = result.get("phase5_site_selection_metrics", {})
    seed_metrics = result.get("seed_causality_metrics", {})
    events = result.get("event_counts", {})
    return {
        "condition_id": condition["condition_id"],
        "seed": seed,
        "phase5_seed_pass": _seed_pass(metrics, args),
        "phase5_5_seed_pass": _phase5_5_seed_pass(metrics, args),
        "direction_consistent": _direction_consistent(metrics),
        "phase5_5_direction_consistent": _phase5_5_direction_consistent(metrics),
        "elapsed_seconds": result.get("elapsed_seconds"),
        "tick": result.get("tick"),
        "plant_food_consumed": int(events.get("plant_lifecycle_food_consumed", 0)),
        "agent_moved_seed_count": int(seed_metrics.get("agent_moved_seed_count", 0)),
        "agent_moved_seed_completed_chains": int(seed_metrics.get("agent_moved_seed_completed_chains", 0)),
        "agent_moved_drop_count": int(metrics.get("agent_moved_drop_count", 0)),
        "drop_quality_vs_current_position_lift": metrics.get("drop_quality_vs_current_position_lift"),
        "drop_quality_vs_nearby_control_lift": metrics.get("drop_quality_vs_nearby_control_lift"),
        "drop_quality_vs_visible_control_lift": metrics.get("drop_quality_vs_visible_control_lift"),
        "drop_quality_vs_visible_best_control_lift": metrics.get("drop_quality_vs_visible_best_control_lift"),
        "drop_quality_vs_random_world_lift": metrics.get("drop_quality_vs_random_world_lift"),
        "drop_quality_vs_hunger_recovery_position_lift": metrics.get("drop_quality_vs_hunger_recovery_position_lift"),
        "drop_quality_vs_safe_window_position_lift": metrics.get("drop_quality_vs_safe_window_position_lift"),
        "drop_quality_vs_future_path_control_lift": metrics.get("drop_quality_vs_future_path_control_lift"),
        "mean_drop_quality": metrics.get("mean_drop_quality"),
        "mean_current_position_quality": metrics.get("mean_current_position_quality"),
        "mean_nearby_control_quality": metrics.get("mean_nearby_control_quality"),
        "mean_visible_control_quality": metrics.get("mean_visible_control_quality"),
        "mean_visible_best_control_quality": metrics.get("mean_visible_best_control_quality"),
        "mean_future_path_control_quality": metrics.get("mean_future_path_control_quality"),
        "future_path_control_count": int(metrics.get("future_path_control_count", 0)),
        "hunger_recovery_control_count": int(metrics.get("hunger_recovery_control_count", 0)),
        "safe_window_control_count": int(metrics.get("safe_window_control_count", 0)),
        "high_quality_completed_chain_rate": metrics.get("high_quality_completed_chain_rate"),
        "low_quality_completed_chain_rate": metrics.get("low_quality_completed_chain_rate"),
        "high_quality_chain_rate_gt_low": bool(metrics.get("high_quality_chain_rate_gt_low", False)),
        "early_drop_quality": metrics.get("early_drop_quality"),
        "late_drop_quality": metrics.get("late_drop_quality"),
        "late_vs_early_drop_quality_lift": metrics.get("late_vs_early_drop_quality_lift"),
        "late_drop_quality_gt_early_by_5pct": bool(metrics.get("late_drop_quality_gt_early_by_5pct", False)),
        "drop_context_counts": json.dumps(metrics.get("seed_drop_context_counts", {}), ensure_ascii=False, sort_keys=True),
        "drop_instinct_counts": json.dumps(metrics.get("seed_drop_instinct_counts", {}), ensure_ascii=False, sort_keys=True),
        "drop_food_contact_counts": json.dumps(metrics.get("seed_drop_food_contact_counts", {}), ensure_ascii=False, sort_keys=True),
        "drop_safe_window_counts": json.dumps(metrics.get("seed_drop_safe_window_counts", {}), ensure_ascii=False, sort_keys=True),
        "drop_critical_hunger_counts": json.dumps(metrics.get("seed_drop_critical_hunger_counts", {}), ensure_ascii=False, sort_keys=True),
        "drop_context_fraction_hunger": _context_fraction(metrics, "hunger"),
        "drop_context_fraction_food_contact": _context_fraction(metrics, "food_contact"),
        "drop_context_fraction_balanced_random": _context_fraction(metrics, "balanced_random"),
        "safe_window_drop_fraction": float(metrics.get("safe_window_drop_fraction", 0.0) or 0.0),
        "critical_hunger_drop_fraction": float(metrics.get("critical_hunger_drop_fraction", 0.0) or 0.0),
        "balanced_drop_fraction": float(metrics.get("balanced_drop_fraction", 0.0) or 0.0),
        "safe_or_balanced_drop_fraction": float(metrics.get("safe_or_balanced_drop_fraction", 0.0) or 0.0),
        "had_hunger_while_carried_fraction": float(metrics.get("had_hunger_while_carried_fraction", 0.0) or 0.0),
        "hunger_context_drop_count": int(_context_metric(metrics, "hunger", "count")),
        "hunger_context_current_lift": _context_metric(metrics, "hunger", "drop_vs_current_lift"),
        "hunger_context_visible_lift": _context_metric(metrics, "hunger", "drop_vs_visible_lift"),
        "hunger_context_future_lift": _context_metric(metrics, "hunger", "drop_vs_future_path_lift"),
        "hunger_context_chain_rate": _context_metric(metrics, "hunger", "completed_chain_rate"),
        "food_contact_context_drop_count": int(_context_metric(metrics, "food_contact", "count")),
        "food_contact_context_current_lift": _context_metric(metrics, "food_contact", "drop_vs_current_lift"),
        "food_contact_context_visible_lift": _context_metric(metrics, "food_contact", "drop_vs_visible_lift"),
        "food_contact_context_chain_rate": _context_metric(metrics, "food_contact", "completed_chain_rate"),
        "drop_moisture_fit": _component(metrics, "drop_quality_components", "moisture_fit"),
        "drop_light_fit": _component(metrics, "drop_quality_components", "light_fit"),
        "drop_nutrient_score": _component(metrics, "drop_quality_components", "nutrient_score"),
        "drop_danger_penalty": _component(metrics, "drop_quality_components", "danger_penalty"),
        "drop_temperature_penalty": _component(metrics, "drop_quality_components", "temperature_penalty"),
    }


def _condition_summary(condition: dict[str, Any], rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    passing = sum(1 for row in rows if bool(row["phase5_seed_pass"]))
    phase5_5_passing = sum(1 for row in rows if bool(row["phase5_5_seed_pass"]))
    direction_count = sum(1 for row in rows if bool(row["direction_consistent"]))
    phase5_5_direction_count = sum(1 for row in rows if bool(row["phase5_5_direction_consistent"]))
    required_passing = min(args.min_passing_runs, len(rows))
    required_direction = min(args.min_directional_consistency, len(rows))
    return {
        "condition_id": condition["condition_id"],
        "description": condition["description"],
        "is_core_gate": condition["is_core_gate"],
        "seed_hunger_drop_bonus": condition["seed_hunger_drop_bonus"],
        "seed_drop_block_critical_hunger": condition["seed_drop_block_critical_hunger"],
        "seed_drop_safe_window_only": condition["seed_drop_safe_window_only"],
        "learning_reward_memory_limit": condition["learning_reward_memory_limit"],
        "reward_memory_shuffle_radius": condition["reward_memory_shuffle_radius"],
        "run_count": len(rows),
        "passing_runs": passing,
        "phase5_5_passing_runs": phase5_5_passing,
        "direction_consistent_runs": direction_count,
        "phase5_5_direction_consistent_runs": phase5_5_direction_count,
        "condition_pass": bool(rows) and passing >= required_passing and direction_count >= required_direction,
        "phase5_5_condition_pass": (
            bool(rows)
            and phase5_5_passing >= required_passing
            and phase5_5_direction_count >= required_direction
        ),
        "mean_agent_moved_drop_count": _mean(rows, "agent_moved_drop_count"),
        "mean_drop_context_fraction_hunger": _mean(rows, "drop_context_fraction_hunger"),
        "mean_drop_context_fraction_food_contact": _mean(rows, "drop_context_fraction_food_contact"),
        "mean_drop_context_fraction_balanced_random": _mean(rows, "drop_context_fraction_balanced_random"),
        "mean_safe_window_drop_fraction": _mean(rows, "safe_window_drop_fraction"),
        "mean_critical_hunger_drop_fraction": _mean(rows, "critical_hunger_drop_fraction"),
        "mean_balanced_drop_fraction": _mean(rows, "balanced_drop_fraction"),
        "mean_safe_or_balanced_drop_fraction": _mean(rows, "safe_or_balanced_drop_fraction"),
        "mean_had_hunger_while_carried_fraction": _mean(rows, "had_hunger_while_carried_fraction"),
        "mean_current_lift": _mean(rows, "drop_quality_vs_current_position_lift"),
        "mean_nearby_lift": _mean(rows, "drop_quality_vs_nearby_control_lift"),
        "mean_visible_lift": _mean(rows, "drop_quality_vs_visible_control_lift"),
        "mean_visible_best_lift": _mean(rows, "drop_quality_vs_visible_best_control_lift"),
        "mean_hunger_recovery_lift": _mean(rows, "drop_quality_vs_hunger_recovery_position_lift"),
        "mean_safe_window_lift": _mean(rows, "drop_quality_vs_safe_window_position_lift"),
        "mean_future_path_lift": _mean(rows, "drop_quality_vs_future_path_control_lift"),
        "mean_random_lift": _mean(rows, "drop_quality_vs_random_world_lift"),
        "mean_future_path_control_count": _mean(rows, "future_path_control_count"),
        "mean_hunger_recovery_control_count": _mean(rows, "hunger_recovery_control_count"),
        "mean_safe_window_control_count": _mean(rows, "safe_window_control_count"),
        "mean_high_quality_chain_rate": _mean(rows, "high_quality_completed_chain_rate"),
        "mean_low_quality_chain_rate": _mean(rows, "low_quality_completed_chain_rate"),
        "mean_late_vs_early_lift": _mean(rows, "late_vs_early_drop_quality_lift"),
        "mean_drop_moisture_fit": _mean(rows, "drop_moisture_fit"),
        "mean_drop_light_fit": _mean(rows, "drop_light_fit"),
        "mean_drop_nutrient_score": _mean(rows, "drop_nutrient_score"),
        "mean_drop_danger_penalty": _mean(rows, "drop_danger_penalty"),
        "mean_drop_temperature_penalty": _mean(rows, "drop_temperature_penalty"),
        "mean_hunger_context_drop_count": _mean(rows, "hunger_context_drop_count"),
        "mean_hunger_context_current_lift": _mean(rows, "hunger_context_current_lift"),
        "mean_hunger_context_visible_lift": _mean(rows, "hunger_context_visible_lift"),
        "mean_hunger_context_future_lift": _mean(rows, "hunger_context_future_lift"),
        "mean_hunger_context_chain_rate": _mean(rows, "hunger_context_chain_rate"),
        "mean_food_contact_context_drop_count": _mean(rows, "food_contact_context_drop_count"),
        "mean_food_contact_context_current_lift": _mean(rows, "food_contact_context_current_lift"),
        "mean_food_contact_context_visible_lift": _mean(rows, "food_contact_context_visible_lift"),
        "mean_food_contact_context_chain_rate": _mean(rows, "food_contact_context_chain_rate"),
    }


def _condition_summary_by_id(condition_summaries: list[dict[str, Any]], condition_id: str) -> dict[str, Any] | None:
    for condition in condition_summaries:
        if condition["condition_id"] == condition_id:
            return condition
    return None


def _phase5_4_hunger_decoupling_summary(
    condition_summaries: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    baseline = _condition_summary_by_id(condition_summaries, "baseline_100x100")
    hunger_neutral = _condition_summary_by_id(condition_summaries, "hunger_neutral_seed_drop_100x100")
    if baseline is None or hunger_neutral is None:
        return {
            "available": False,
            "pass": False,
            "reason": "baseline_100x100 and hunger_neutral_seed_drop_100x100 are both required.",
        }

    baseline_hunger_fraction = float(baseline["mean_drop_context_fraction_hunger"])
    neutral_hunger_fraction = float(hunger_neutral["mean_drop_context_fraction_hunger"])
    activity_ok = float(hunger_neutral["mean_agent_moved_drop_count"]) >= 50.0
    hunger_reduced = neutral_hunger_fraction < baseline_hunger_fraction
    enough_passing_runs = int(hunger_neutral["passing_runs"]) >= min(
        args.min_passing_runs,
        int(hunger_neutral["run_count"]),
    )
    enough_direction_consistency = int(hunger_neutral["direction_consistent_runs"]) >= min(
        args.min_directional_consistency,
        int(hunger_neutral["run_count"]),
    )
    return {
        "available": True,
        "pass": (
            activity_ok
            and hunger_reduced
            and enough_passing_runs
            and enough_direction_consistency
        ),
        "baseline_mean_hunger_fraction": baseline_hunger_fraction,
        "hunger_neutral_mean_hunger_fraction": neutral_hunger_fraction,
        "hunger_fraction_delta": round(neutral_hunger_fraction - baseline_hunger_fraction, 5),
        "hunger_neutral_mean_agent_moved_drop_count": hunger_neutral["mean_agent_moved_drop_count"],
        "hunger_neutral_passing_runs": hunger_neutral["passing_runs"],
        "hunger_neutral_direction_consistent_runs": hunger_neutral["direction_consistent_runs"],
        "activity_ok": activity_ok,
        "hunger_reduced": hunger_reduced,
        "enough_passing_runs": enough_passing_runs,
        "enough_direction_consistency": enough_direction_consistency,
    }


def _phase5_5_state_decoupling_summary(
    condition_summaries: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    baseline = _condition_summary_by_id(condition_summaries, "baseline_100x100")
    if baseline is None:
        return {
            "available": False,
            "pass": False,
            "reason": "baseline_100x100 is required.",
        }

    baseline_safe_fraction = float(baseline["mean_safe_or_balanced_drop_fraction"])
    candidate_ids = (
        "no_hunger_seed_drop_bonus_100x100",
        "critical_hunger_drop_blocked_100x100",
        "safe_window_seed_drop_only_100x100",
    )
    candidates: list[dict[str, Any]] = []
    for condition_id in candidate_ids:
        condition = _condition_summary_by_id(condition_summaries, condition_id)
        if condition is None:
            continue
        safe_fraction = float(condition["mean_safe_or_balanced_drop_fraction"])
        safe_fraction_lift = round(safe_fraction - baseline_safe_fraction, 5)
        activity_ok = float(condition["mean_agent_moved_drop_count"]) >= 50.0
        safe_fraction_ok = safe_fraction_lift >= args.min_safe_or_balanced_fraction_delta
        passing_ok = int(condition["phase5_5_passing_runs"]) >= min(
            args.min_passing_runs,
            int(condition["run_count"]),
        )
        direction_ok = int(condition["phase5_5_direction_consistent_runs"]) >= min(
            args.min_directional_consistency,
            int(condition["run_count"]),
        )
        condition_pass = activity_ok and safe_fraction_ok and passing_ok and direction_ok
        candidates.append(
            {
                "condition_id": condition_id,
                "pass": condition_pass,
                "activity_ok": activity_ok,
                "safe_fraction_ok": safe_fraction_ok,
                "passing_ok": passing_ok,
                "direction_ok": direction_ok,
                "safe_or_balanced_fraction": safe_fraction,
                "safe_or_balanced_fraction_delta": safe_fraction_lift,
                "phase5_5_passing_runs": condition["phase5_5_passing_runs"],
                "phase5_5_direction_consistent_runs": condition["phase5_5_direction_consistent_runs"],
                "mean_agent_moved_drop_count": condition["mean_agent_moved_drop_count"],
                "mean_current_lift": condition["mean_current_lift"],
                "mean_hunger_recovery_lift": condition["mean_hunger_recovery_lift"],
                "mean_safe_window_lift": condition["mean_safe_window_lift"],
                "mean_visible_lift": condition["mean_visible_lift"],
                "mean_high_quality_chain_rate": condition["mean_high_quality_chain_rate"],
                "mean_low_quality_chain_rate": condition["mean_low_quality_chain_rate"],
            }
        )
    return {
        "available": bool(candidates),
        "pass": any(bool(candidate["pass"]) for candidate in candidates),
        "baseline_safe_or_balanced_fraction": baseline_safe_fraction,
        "candidates": candidates,
    }


def _render_report(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    phase5_4 = summary.get("phase5_4_hunger_decoupling", {})
    phase5_5 = summary.get("phase5_5_state_decoupling", {})
    lines = [
        "# รายงาน Phase 5: Site Selection / Seed Placement Quality",
        "",
        "วันที่รัน: 2026-06-13",
        f"ชุดข้อมูล: `{summary['output_dir']}`",
        "",
        "## Verdict",
        "",
        f"Phase 5 core pass: `{summary['phase5_core_pass']}`",
        f"Phase 5.4 hunger-decoupled pass: `{phase5_4.get('pass', False)}`",
        f"Phase 5.5 state-decoupled pass: `{phase5_5.get('pass', False)}`",
        "",
        "## Condition Summary",
        "",
        "| condition | core | hunger bonus | block critical | safe only | runs | p5.5 pass | p5.5 dir | moved drops | hunger frac | safe/balanced frac | critical frac | current | recovery | safe-window | visible | future | high chain | low chain | late/early |",
        "| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition in summary["condition_summaries"]:
        lines.append(
            "| {condition_id} | {is_core_gate} | {seed_hunger_drop_bonus} | {seed_drop_block_critical_hunger} | "
            "{seed_drop_safe_window_only} | {run_count} | {phase5_5_passing_runs} | "
            "{phase5_5_direction_consistent_runs} | {mean_agent_moved_drop_count} | "
            "{mean_drop_context_fraction_hunger} | {mean_safe_or_balanced_drop_fraction} | "
            "{mean_critical_hunger_drop_fraction} | {mean_current_lift} | {mean_hunger_recovery_lift} | "
            "{mean_safe_window_lift} | {mean_visible_lift} | {mean_future_path_lift} | "
            "{mean_high_quality_chain_rate} | {mean_low_quality_chain_rate} | {mean_late_vs_early_lift} |".format(**condition)
        )
    lines.extend(
        [
            "",
            "## Context-Matched Summary",
            "",
            "| condition | hunger count | hunger current | hunger visible | hunger future | hunger chain | food-contact count | food-contact current | food-contact visible | food-contact chain |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for condition in summary["condition_summaries"]:
        lines.append(
            "| {condition_id} | {mean_hunger_context_drop_count} | {mean_hunger_context_current_lift} | "
            "{mean_hunger_context_visible_lift} | {mean_hunger_context_future_lift} | "
            "{mean_hunger_context_chain_rate} | {mean_food_contact_context_drop_count} | "
            "{mean_food_contact_context_current_lift} | {mean_food_contact_context_visible_lift} | "
            "{mean_food_contact_context_chain_rate} |".format(**condition)
        )
    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| condition | seed | p5.5 pass | p5.5 dir | moved drops | hunger frac | safe/balanced frac | critical frac | current | recovery | safe-window | visible | future | high chain | low chain | late/early | moisture | light | nutrient | danger | temp penalty |",
            "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            "| {condition_id} | {seed} | {phase5_5_seed_pass} | {phase5_5_direction_consistent} | "
            "{agent_moved_drop_count} | {drop_context_fraction_hunger} | {safe_or_balanced_drop_fraction} | "
            "{critical_hunger_drop_fraction} | {drop_quality_vs_current_position_lift} | "
            "{drop_quality_vs_hunger_recovery_position_lift} | {drop_quality_vs_safe_window_position_lift} | "
            "{drop_quality_vs_visible_control_lift} | {drop_quality_vs_future_path_control_lift} | "
            "{high_quality_completed_chain_rate} | {low_quality_completed_chain_rate} | "
            "{late_vs_early_drop_quality_lift} | {drop_moisture_fit} | {drop_light_fit} | "
            "{drop_nutrient_score} | {drop_danger_penalty} | {drop_temperature_penalty} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `current_position_control` เป็น control หลักของ Phase 5",
            "- `visible_control` จำกัด control ให้อยู่ในระยะเห็นของ agent ตอน drop",
            "- `recovery` คือ control ที่ตำแหน่งแรกหลังถือ seed แล้วพ้นจาก hunger state",
            "- `safe-window` คือ control ที่ตำแหน่งแรกขณะถือ seed และอยู่ใน balanced/safe state",
            "- `future_path_control` ถามว่าจุด drop ดีกว่าจุดที่ agent เดินต่อไปหลังจากนั้นหรือไม่",
            "- `Context-Matched Summary` แยกถามว่า lift เกิดใน hunger/food-contact context หรือถูก context หนึ่งลากค่าเฉลี่ย",
            "- 200x200 conditions เป็น stress/blocker diagnosis ไม่ใช่ hard gate ในรอบนี้",
            "- ถ้า total quality ผ่านแต่ component เดียว dominate ต้องตีความอย่างระวัง",
            "",
            "## Limits",
            "",
            "- reward-memory ablations เป็น diagnostic ไม่ใช่ hard gate ถ้า state-decoupled conditions ยังไม่ผ่าน",
            "- quality score ยังเป็น observer score แต่ control ถูกจำกัดตามระยะเห็นของ agent",
            "- large-world failure ต้องแยกต่อว่าเป็น time budget, density, หรือ exploration limitation",
        ]
    )
    return "\n".join(lines) + "\n"


def run_suite(args: argparse.Namespace) -> dict[str, Any]:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, Any]] = []
    condition_summaries: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for condition in _conditions(args):
        condition_dir = args.output_dir / condition["condition_id"]
        run_dir = condition_dir / "runs"
        run_dir.mkdir(parents=True, exist_ok=True)
        condition_rows: list[dict[str, Any]] = []
        print(json.dumps({"type": "condition_start", **condition}, ensure_ascii=False), flush=True)
        for seed in condition["seeds"]:
            run_id = f"phase5_site_selection_{condition['condition_id']}_seed{seed}"
            result_path = run_dir / f"{run_id}.json"
            log_path = run_dir / f"{run_id}.out.log"
            try:
                with log_path.open("w", encoding="utf-8") as log_file:
                    with contextlib.redirect_stdout(log_file):
                        result = run_watch(_watch_args(args, condition, seed))
                result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
                row = _summarize_run(result, condition, seed, args)
                condition_rows.append(row)
                all_rows.append(row)
                print(json.dumps({"type": "run_result", **row}, ensure_ascii=False), flush=True)
            except Exception as exc:  # pragma: no cover - visible batch failure record.
                failure = {"condition_id": condition["condition_id"], "seed": seed, "error": repr(exc)}
                failures.append(failure)
                print(json.dumps({"type": "run_failed", **failure}, ensure_ascii=False), flush=True)
        _write_csv(condition_dir / "runs.csv", condition_rows)
        condition_summary = _condition_summary(condition, condition_rows, args)
        condition_summaries.append(condition_summary)
        (condition_dir / "summary.json").write_text(
            json.dumps(condition_summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(json.dumps({"type": "condition_summary", **condition_summary}, ensure_ascii=False), flush=True)

    core_conditions = [condition for condition in condition_summaries if bool(condition["is_core_gate"])]
    phase5_core_pass = bool(core_conditions) and all(bool(condition["condition_pass"]) for condition in core_conditions)
    phase5_4_hunger_decoupling = _phase5_4_hunger_decoupling_summary(condition_summaries, args)
    phase5_5_state_decoupling = _phase5_5_state_decoupling_summary(condition_summaries, args)
    summary = {
        "objective": "Phase 5: test seed placement site-selection against current-position and nearby controls.",
        "phase5_core_pass": phase5_core_pass,
        "phase5_4_hunger_decoupling": phase5_4_hunger_decoupling,
        "phase5_5_state_decoupling": phase5_5_state_decoupling,
        "output_dir": str(args.output_dir),
        "success_criteria": {
            "min_current_position_lift": args.min_current_position_lift,
            "min_nearby_control_lift": args.min_nearby_control_lift,
            "min_visible_control_lift": args.min_visible_control_lift,
            "min_future_path_control_lift": args.min_future_path_control_lift,
            "min_late_vs_early_lift": args.min_late_vs_early_lift,
            "min_hunger_recovery_lift": args.min_hunger_recovery_lift,
            "min_safe_window_lift": args.min_safe_window_lift,
            "min_safe_or_balanced_fraction_delta": args.min_safe_or_balanced_fraction_delta,
            "min_passing_runs": args.min_passing_runs,
            "min_directional_consistency": args.min_directional_consistency,
            "future_control_offsets": args.future_control_offsets,
        },
        "condition_summaries": condition_summaries,
        "row_count": len(all_rows),
        "failures": failures,
    }
    _write_csv(args.output_dir / "runs.csv", all_rows)
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    args.report_path.write_text(_render_report(summary, all_rows), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 5 site-selection probes.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/phase5_site_selection_latest"))
    parser.add_argument("--report-path", type=Path, default=Path("reports/phase5_site_selection_latest.th.md"))
    parser.add_argument("--conditions", nargs="+", default=["all"])
    parser.add_argument("--core-seeds", type=_parse_int_list, default=[20260610, 20260611, 20260612, 20260613, 20260614])
    parser.add_argument("--stress-seeds", type=_parse_int_list, default=[20260610, 20260611, 20260612])
    parser.add_argument("--core-time-limit-seconds", type=float, default=90.0)
    parser.add_argument("--stress-time-limit-seconds", type=float, default=180.0)
    parser.add_argument("--progress-every-seconds", type=float, default=30.0)
    parser.add_argument("--event-sample-limit", type=int, default=1800)
    parser.add_argument("--min-current-position-lift", type=float, default=1.10)
    parser.add_argument("--min-nearby-control-lift", type=float, default=1.05)
    parser.add_argument("--min-visible-control-lift", type=float, default=1.00)
    parser.add_argument("--min-future-path-control-lift", type=float, default=1.00)
    parser.add_argument("--min-late-vs-early-lift", type=float, default=1.05)
    parser.add_argument("--min-hunger-recovery-lift", type=float, default=1.05)
    parser.add_argument("--min-safe-window-lift", type=float, default=1.05)
    parser.add_argument("--min-safe-or-balanced-fraction-delta", type=float, default=0.05)
    parser.add_argument("--min-passing-runs", type=int, default=3)
    parser.add_argument("--min-directional-consistency", type=int, default=4)
    parser.add_argument("--future-control-offsets", type=_parse_int_list, default=[10, 25, 50])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_suite(args)
    print(json.dumps({"type": "summary", **summary}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
