from __future__ import annotations

import argparse
import contextlib
import csv
import json
from collections import defaultdict
from pathlib import Path
import statistics
import sys
from types import SimpleNamespace
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_long_emergence_watch import run_watch


EVENT_FIELDS = [
    "harvest_seed_dropped",
    "seed_buried_by_disturbance",
    "seed_germinated",
    "plant_matured",
    "natural_seed_dropped",
    "plant_fruited",
    "plant_lifecycle_food_consumed",
    "plant_lifecycle_food_decayed",
    "plant_died",
    "seed_picked",
    "seed_dropped",
    "build_nest",
    "technology_emerged",
]


def _parse_int_list(text: str) -> list[int]:
    values = [int(part.strip()) for part in text.split(",") if part.strip()]
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def _parse_float_list(text: str) -> list[float]:
    values = [float(part.strip()) for part in text.split(",") if part.strip()]
    if not values:
        raise argparse.ArgumentTypeError("expected at least one number")
    return values


def _slug_number(value: int | float) -> str:
    return str(value).replace(".", "p")


def _run_status(event_counts: dict[str, int], plant_food: dict[str, int]) -> str:
    if plant_food.get("consumed", 0) > 0:
        return "agent_consumed_plant_food"
    if plant_food.get("decayed", 0) > 0:
        return "plant_food_fate_without_consumption"
    if event_counts.get("plant_fruited", 0) > 0:
        return "plant_fruited"
    if event_counts.get("plant_matured", 0) > 0:
        return "plant_matured"
    if event_counts.get("seed_germinated", 0) > 0:
        return "seed_germinated"
    if event_counts.get("harvest_seed_dropped", 0) > 0 or event_counts.get("natural_seed_dropped", 0) > 0:
        return "seed_available_only"
    return "no_ecology_signal"


def _ignition_score(event_counts: dict[str, int], plant_food: dict[str, int]) -> int:
    score = 0
    score += min(10, event_counts.get("harvest_seed_dropped", 0))
    score += min(20, event_counts.get("seed_buried_by_disturbance", 0)) * 2
    score += min(50, event_counts.get("seed_germinated", 0)) * 4
    score += min(30, event_counts.get("plant_matured", 0)) * 8
    score += min(30, event_counts.get("plant_fruited", 0)) * 12
    score += min(50, event_counts.get("natural_seed_dropped", 0)) * 6
    score += min(25, plant_food.get("consumed", 0)) * 20
    score += min(25, plant_food.get("decayed", 0)) * 8
    return score


def _safe_rate(numerator: int | float, denominator: int | float) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 4)


def _config_id(config: dict[str, Any], seed: int) -> str:
    return (
        f"w{config['width']}"
        f"_d{_slug_number(config['max_food_per_100_cells'])}"
        f"_b{config['base_food_spawn_per_tick']}"
        f"_fsm{_slug_number(config['food_spawn_multiplier'])}"
        f"_boot{config['bootstrap_food_spawn_ticks']}"
        f"_post{_slug_number(config['wild_food_spawn_after_bootstrap_multiplier'])}"
        f"_rain{config['natural_seed_rain_per_tick']}"
        f"_age{_slug_number(config['plant_seed_max_age_multiplier'])}"
        f"_grow{_slug_number(config['plant_growth_rate_multiplier'])}"
        f"_loss{_slug_number(config['sprout_biomass_loss_multiplier'])}"
        f"_gt{_slug_number(config['germination_good_ticks_multiplier'])}"
        f"_fruit{_slug_number(config['plant_fruiting_interval_multiplier'])}"
        f"_fthr{_slug_number(config['plant_fruiting_growth_threshold_multiplier'])}"
        f"_fch{_slug_number(config['plant_fruiting_chance_multiplier'])}"
        f"_ns{_slug_number(config['natural_seed_drop_chance_multiplier'])}"
        f"_pfd{_slug_number(config['plant_food_decay_chance'])}"
        f"_s{seed}"
    )


def _watch_args(args: argparse.Namespace, config: dict[str, Any], seed: int) -> SimpleNamespace:
    return SimpleNamespace(
        seed=seed,
        body_index=args.body_index,
        initial_population=args.initial_population,
        max_population=args.max_population,
        max_ticks=args.max_ticks,
        time_limit_seconds=args.time_limit_seconds,
        progress_every_seconds=args.progress_every_seconds,
        evaluate_every_ticks=args.evaluate_every_ticks,
        event_sample_limit=args.event_sample_limit,
        output=Path(),
        spawn_strategy=args.spawn_strategy,
        immortal=args.immortal,
        width=config["width"],
        height=config["height"],
        max_food=config["max_food"],
        base_food_spawn_per_tick=config["base_food_spawn_per_tick"],
        food_spawn_multiplier=config["food_spawn_multiplier"],
        bootstrap_food_spawn_ticks=config["bootstrap_food_spawn_ticks"],
        wild_food_spawn_after_bootstrap_multiplier=config["wild_food_spawn_after_bootstrap_multiplier"],
        natural_seed_rain_per_tick=config["natural_seed_rain_per_tick"],
        max_plant_seeds=config["max_plant_seeds"],
        large_animal_spawn_per_tick=args.large_animal_spawn_per_tick,
        max_large_animals=args.max_large_animals,
        nest_support_food_chance=args.nest_support_food_chance,
        nest_support_spawn_chance=args.nest_support_spawn_chance,
        frontier_band=args.frontier_band,
        global_food_decline_per_day=args.global_food_decline_per_day,
        minimum_global_food_multiplier=args.minimum_global_food_multiplier,
        ambient_food_decay_chance=args.ambient_food_decay_chance,
        plant_food_decay_chance=config["plant_food_decay_chance"],
        plant_seed_max_age_multiplier=config["plant_seed_max_age_multiplier"],
        plant_growth_rate_multiplier=config["plant_growth_rate_multiplier"],
        sprout_biomass_loss_multiplier=config["sprout_biomass_loss_multiplier"],
        germination_good_ticks_multiplier=config["germination_good_ticks_multiplier"],
        plant_fruiting_interval_multiplier=config["plant_fruiting_interval_multiplier"],
        plant_fruiting_growth_threshold_multiplier=config["plant_fruiting_growth_threshold_multiplier"],
        plant_fruiting_chance_multiplier=config["plant_fruiting_chance_multiplier"],
        natural_seed_drop_chance_multiplier=config["natural_seed_drop_chance_multiplier"],
        learning_revisit_radius=args.learning_revisit_radius,
        learning_revisit_min_delay_ticks=args.learning_revisit_min_delay_ticks,
        learning_revisit_max_age_ticks=args.learning_revisit_max_age_ticks,
        learning_reward_memory_limit=args.learning_reward_memory_limit,
    )


def _iter_configs(args: argparse.Namespace) -> list[dict[str, Any]]:
    configs: list[dict[str, Any]] = []
    for size in args.map_sizes:
        for density in args.max_food_per_100_cells:
            for base_spawn in args.base_food_spawn_values:
                for food_spawn_multiplier in args.food_spawn_multiplier_values:
                    for bootstrap_ticks in args.bootstrap_food_spawn_ticks_values:
                        for post_multiplier in args.post_bootstrap_multiplier_values:
                            for seed_rain in args.natural_seed_rain_values:
                                for seed_age_multiplier in args.plant_seed_max_age_multiplier_values:
                                    for growth_multiplier in args.plant_growth_rate_multiplier_values:
                                        for loss_multiplier in args.sprout_biomass_loss_multiplier_values:
                                            for germination_multiplier in args.germination_good_ticks_multiplier_values:
                                                for fruit_interval_multiplier in args.plant_fruiting_interval_multiplier_values:
                                                    for fruit_threshold_multiplier in args.plant_fruiting_growth_threshold_multiplier_values:
                                                        for fruit_chance_multiplier in args.plant_fruiting_chance_multiplier_values:
                                                            for seed_drop_multiplier in args.natural_seed_drop_chance_multiplier_values:
                                                                for plant_food_decay_chance in args.plant_food_decay_chance_values:
                                                                    area = size * size
                                                                    max_food = max(
                                                                        args.minimum_max_food,
                                                                        int(round(area * density / 100.0)),
                                                                    )
                                                                    max_plant_seeds = max(
                                                                        args.minimum_max_plant_seeds,
                                                                        int(round(max_food * args.max_plant_seed_factor)),
                                                                    )
                                                                    configs.append(
                                                                        {
                                                                            "width": size,
                                                                            "height": size,
                                                                            "max_food_per_100_cells": density,
                                                                            "max_food": max_food,
                                                                            "base_food_spawn_per_tick": base_spawn,
                                                                            "food_spawn_multiplier": food_spawn_multiplier,
                                                                            "bootstrap_food_spawn_ticks": bootstrap_ticks,
                                                                            "wild_food_spawn_after_bootstrap_multiplier": post_multiplier,
                                                                            "natural_seed_rain_per_tick": seed_rain,
                                                                            "max_plant_seeds": max_plant_seeds,
                                                                            "plant_seed_max_age_multiplier": seed_age_multiplier,
                                                                            "plant_growth_rate_multiplier": growth_multiplier,
                                                                            "sprout_biomass_loss_multiplier": loss_multiplier,
                                                                            "germination_good_ticks_multiplier": germination_multiplier,
                                                                            "plant_fruiting_interval_multiplier": fruit_interval_multiplier,
                                                                            "plant_fruiting_growth_threshold_multiplier": fruit_threshold_multiplier,
                                                                            "plant_fruiting_chance_multiplier": fruit_chance_multiplier,
                                                                            "natural_seed_drop_chance_multiplier": seed_drop_multiplier,
                                                                            "plant_food_decay_chance": plant_food_decay_chance,
                                                                        }
                                                                    )
    return configs


def _summarize_run(result: dict[str, Any], config: dict[str, Any], seed: int, run_id: str) -> dict[str, Any]:
    event_counts = {field: int(result.get("event_counts", {}).get(field, 0)) for field in EVENT_FIELDS}
    attribute_counts = result.get("event_attribute_counts", {})
    numeric_summaries = result.get("event_numeric_summaries", {})
    plant_died_reasons = attribute_counts.get("plant_died_reason", {})
    first_event_tick = result.get("first_event_tick", {})
    plant_food = result.get("plant_lifecycle_food", {})
    elapsed_seconds = float(result.get("elapsed_seconds") or 0.0)
    tick_count = int(result.get("tick") or 0)
    row: dict[str, Any] = {
        "run_id": run_id,
        "seed": seed,
        **config,
        "stop_reason": result.get("stop_reason"),
        "elapsed_seconds": elapsed_seconds,
        "tick": tick_count,
        "ticks_per_second": _safe_rate(tick_count, elapsed_seconds),
        "day": result.get("day"),
        "population": result.get("population"),
        "births": result.get("births"),
        "nests": result.get("nests"),
        "status": _run_status(event_counts, plant_food),
        "ignition_score": _ignition_score(event_counts, plant_food),
        "plant_food_remaining": int(plant_food.get("remaining", 0)),
        "plant_food_consumed": int(plant_food.get("consumed", 0)),
        "plant_food_decayed": int(plant_food.get("decayed", 0)),
        "plant_food_fruited": int(plant_food.get("fruited", 0)),
        "seed_to_germinated_rate": _safe_rate(
            event_counts["seed_germinated"],
            event_counts["harvest_seed_dropped"] + event_counts["natural_seed_dropped"],
        ),
        "germinated_to_matured_rate": _safe_rate(event_counts["plant_matured"], event_counts["seed_germinated"]),
        "matured_to_fruited_rate": _safe_rate(event_counts["plant_fruited"], event_counts["plant_matured"]),
        "fruit_to_consumed_rate": _safe_rate(plant_food.get("consumed", 0), event_counts["plant_fruited"]),
        "plant_died_no_biomass": int(plant_died_reasons.get("no_biomass", 0)),
        "plant_died_max_age": int(plant_died_reasons.get("max_age", 0)),
        "plant_died_low_viability": int(plant_died_reasons.get("low_viability", 0)),
        "plant_died_mean_age_ticks": numeric_summaries.get("plant_died_age_ticks", {}).get("mean"),
        "plant_died_mean_biomass": numeric_summaries.get("plant_died_biomass", {}).get("mean"),
        "plant_died_mean_water": numeric_summaries.get("plant_died_water", {}).get("mean"),
        "plant_died_mean_temp_k": numeric_summaries.get("plant_died_temp_k", {}).get("mean"),
        "plant_died_mean_light": numeric_summaries.get("plant_died_light", {}).get("mean"),
        "plant_died_mean_nutrients": numeric_summaries.get("plant_died_nutrients", {}).get("mean"),
        "plant_died_mean_growth": numeric_summaries.get("plant_died_growth", {}).get("mean"),
        "mean_safety_feeling": result.get("affect", {}).get("mean_safety_feeling"),
        "mean_comfort_level": result.get("affect", {}).get("mean_comfort_level"),
        "mean_fear_level": result.get("affect", {}).get("mean_fear_level"),
        "mean_hunger_level": result.get("affect", {}).get("mean_hunger_level"),
        "mean_pair_bond_ticks": result.get("affect", {}).get("mean_pair_bond_ticks"),
        "first_seed_germinated_tick": first_event_tick.get("seed_germinated"),
        "first_plant_matured_tick": first_event_tick.get("plant_matured"),
        "first_plant_fruited_tick": first_event_tick.get("plant_fruited"),
        "first_plant_food_consumed_tick": first_event_tick.get("plant_lifecycle_food_consumed"),
        "first_natural_seed_dropped_tick": first_event_tick.get("natural_seed_dropped"),
        "plant_origins": json.dumps(result.get("plant_origins", {}), ensure_ascii=False, sort_keys=True),
    }
    row.update(event_counts)
    return row


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _aggregate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    config_fields = [
        "width",
        "height",
        "max_food_per_100_cells",
        "max_food",
        "base_food_spawn_per_tick",
        "food_spawn_multiplier",
        "bootstrap_food_spawn_ticks",
        "wild_food_spawn_after_bootstrap_multiplier",
        "natural_seed_rain_per_tick",
        "max_plant_seeds",
        "plant_seed_max_age_multiplier",
        "plant_growth_rate_multiplier",
        "sprout_biomass_loss_multiplier",
        "germination_good_ticks_multiplier",
        "plant_fruiting_interval_multiplier",
        "plant_fruiting_growth_threshold_multiplier",
        "plant_fruiting_chance_multiplier",
        "natural_seed_drop_chance_multiplier",
        "plant_food_decay_chance",
    ]
    for row in rows:
        groups[tuple(row[field] for field in config_fields)].append(row)

    aggregates: list[dict[str, Any]] = []
    for key, group_rows in groups.items():
        aggregate = {field: value for field, value in zip(config_fields, key)}
        aggregate["runs"] = len(group_rows)
        aggregate["germinated_runs"] = sum(1 for row in group_rows if int(row["seed_germinated"]) > 0)
        aggregate["matured_runs"] = sum(1 for row in group_rows if int(row["plant_matured"]) > 0)
        aggregate["fruited_runs"] = sum(1 for row in group_rows if int(row["plant_fruited"]) > 0)
        aggregate["plant_food_consumed_runs"] = sum(1 for row in group_rows if int(row["plant_food_consumed"]) > 0)
        aggregate["mean_ignition_score"] = round(statistics.fmean(float(row["ignition_score"]) for row in group_rows), 2)
        aggregate["mean_seed_germinated"] = round(statistics.fmean(int(row["seed_germinated"]) for row in group_rows), 2)
        aggregate["mean_plant_matured"] = round(statistics.fmean(int(row["plant_matured"]) for row in group_rows), 2)
        aggregate["mean_plant_fruited"] = round(statistics.fmean(int(row["plant_fruited"]) for row in group_rows), 2)
        aggregate["mean_plant_food_consumed"] = round(statistics.fmean(int(row["plant_food_consumed"]) for row in group_rows), 2)
        aggregate["mean_plant_died_no_biomass"] = round(
            statistics.fmean(int(row["plant_died_no_biomass"]) for row in group_rows),
            2,
        )
        aggregate["mean_plant_died_max_age"] = round(
            statistics.fmean(int(row["plant_died_max_age"]) for row in group_rows),
            2,
        )
        aggregate["mean_plant_died_low_viability"] = round(
            statistics.fmean(int(row["plant_died_low_viability"]) for row in group_rows),
            2,
        )
        aggregate["mean_plant_died_mean_growth"] = round(
            statistics.fmean(float(row["plant_died_mean_growth"] or 0.0) for row in group_rows),
            4,
        )
        aggregate["mean_plant_died_mean_light"] = round(
            statistics.fmean(float(row["plant_died_mean_light"] or 0.0) for row in group_rows),
            4,
        )
        aggregate["mean_plant_died_mean_nutrients"] = round(
            statistics.fmean(float(row["plant_died_mean_nutrients"] or 0.0) for row in group_rows),
            4,
        )
        aggregate["mean_hunger_level"] = round(statistics.fmean(float(row["mean_hunger_level"]) for row in group_rows), 3)
        aggregate["mean_ticks_per_second"] = round(statistics.fmean(float(row["ticks_per_second"]) for row in group_rows), 2)
        aggregate["mean_seed_to_germinated_rate"] = round(
            statistics.fmean(float(row["seed_to_germinated_rate"]) for row in group_rows),
            4,
        )
        aggregate["mean_germinated_to_matured_rate"] = round(
            statistics.fmean(float(row["germinated_to_matured_rate"]) for row in group_rows),
            4,
        )
        aggregate["mean_matured_to_fruited_rate"] = round(
            statistics.fmean(float(row["matured_to_fruited_rate"]) for row in group_rows),
            4,
        )
        aggregate["best_status"] = max(group_rows, key=lambda row: int(row["ignition_score"]))["status"]
        aggregates.append(aggregate)
    return sorted(aggregates, key=lambda row: (-row["mean_ignition_score"], row["width"]))


def run_calibration(args: argparse.Namespace) -> dict[str, Any]:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_dir = args.output_dir / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    configs = _iter_configs(args)
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for config in configs:
        for seed in args.seeds:
            run_id = _config_id(config, seed)
            log_path = run_dir / f"{run_id}.out.log"
            result_path = run_dir / f"{run_id}.json"
            try:
                with log_path.open("w", encoding="utf-8") as log_file:
                    with contextlib.redirect_stdout(log_file):
                        result = run_watch(_watch_args(args, config, seed))
                result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
                row = _summarize_run(result, config, seed, run_id)
                rows.append(row)
                print(
                    json.dumps(
                        {
                            "type": "run_result",
                            "run_id": run_id,
                            "status": row["status"],
                            "score": row["ignition_score"],
                            "seed_germinated": row["seed_germinated"],
                            "plant_matured": row["plant_matured"],
                            "plant_fruited": row["plant_fruited"],
                            "plant_food_consumed": row["plant_food_consumed"],
                            "mean_hunger_level": row["mean_hunger_level"],
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
            except Exception as exc:  # pragma: no cover - kept visible in JSON for batch runs.
                failure = {"run_id": run_id, "seed": seed, **config, "error": repr(exc)}
                failures.append(failure)
                print(json.dumps({"type": "run_failed", **failure}, ensure_ascii=False), flush=True)

    aggregate_rows = _aggregate_rows(rows)
    _write_csv(args.output_dir / "runs.csv", rows)
    _write_csv(args.output_dir / "aggregate.csv", aggregate_rows)
    summary = {
        "objective": "Calibrate ecology density before judging agent learning.",
        "run_count": len(rows),
        "failure_count": len(failures),
        "configs": len(configs),
        "seeds": args.seeds,
        "success_criteria": {
            "ecology_ignition": "plant_fruited > 0",
            "agent_food_link": "plant_lifecycle_food_consumed > 0",
            "strong_candidate": "fruited in >=70% of seeds for a config before learning claims",
        },
        "best_configs": aggregate_rows[: min(10, len(aggregate_rows))],
        "failures": failures,
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sweep ecology parameters before long learning runs.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/ecology_calibration_latest"))
    parser.add_argument("--seeds", type=_parse_int_list, default=[20260610])
    parser.add_argument("--map-sizes", type=_parse_int_list, default=[40, 100])
    parser.add_argument("--max-food-per-100-cells", type=_parse_float_list, default=[2.2, 20.0])
    parser.add_argument("--base-food-spawn-values", type=_parse_int_list, default=[2, 4])
    parser.add_argument("--food-spawn-multiplier-values", type=_parse_float_list, default=[0.45, 0.70])
    parser.add_argument("--bootstrap-food-spawn-ticks-values", type=_parse_int_list, default=[120, 300])
    parser.add_argument("--post-bootstrap-multiplier-values", type=_parse_float_list, default=[0.08, 0.12])
    parser.add_argument("--natural-seed-rain-values", type=_parse_int_list, default=[0])
    parser.add_argument("--plant-seed-max-age-multiplier-values", type=_parse_float_list, default=[1.0])
    parser.add_argument("--plant-growth-rate-multiplier-values", type=_parse_float_list, default=[1.0])
    parser.add_argument("--sprout-biomass-loss-multiplier-values", type=_parse_float_list, default=[1.0])
    parser.add_argument("--germination-good-ticks-multiplier-values", type=_parse_float_list, default=[1.0])
    parser.add_argument("--plant-fruiting-interval-multiplier-values", type=_parse_float_list, default=[1.0])
    parser.add_argument("--plant-fruiting-growth-threshold-multiplier-values", type=_parse_float_list, default=[1.0])
    parser.add_argument("--plant-fruiting-chance-multiplier-values", type=_parse_float_list, default=[1.0])
    parser.add_argument("--natural-seed-drop-chance-multiplier-values", type=_parse_float_list, default=[1.0])
    parser.add_argument("--plant-food-decay-chance-values", type=_parse_float_list, default=[0.003])
    parser.add_argument("--minimum-max-food", type=int, default=60)
    parser.add_argument("--minimum-max-plant-seeds", type=int, default=450)
    parser.add_argument("--max-plant-seed-factor", type=float, default=3.8)
    parser.add_argument("--body-index", type=int, default=37)
    parser.add_argument("--initial-population", type=int, default=50)
    parser.add_argument("--max-population", type=int, default=250)
    parser.add_argument("--max-ticks", type=int, default=10_000_000)
    parser.add_argument("--time-limit-seconds", type=float, default=20.0)
    parser.add_argument("--progress-every-seconds", type=float, default=30.0)
    parser.add_argument("--evaluate-every-ticks", type=int, default=100_000_000)
    parser.add_argument("--event-sample-limit", type=int, default=400)
    parser.add_argument("--spawn-strategy", default="frontier_safe_high_food")
    parser.add_argument("--immortal", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--large-animal-spawn-per-tick", type=int, default=2)
    parser.add_argument("--max-large-animals", type=int, default=28)
    parser.add_argument("--nest-support-food-chance", type=float, default=0.05)
    parser.add_argument("--nest-support-spawn-chance", type=float, default=0.03)
    parser.add_argument("--frontier-band", type=int, default=10)
    parser.add_argument("--global-food-decline-per-day", type=float, default=0.012)
    parser.add_argument("--minimum-global-food-multiplier", type=float, default=0.24)
    parser.add_argument("--ambient-food-decay-chance", type=float, default=0.006)
    parser.add_argument("--learning-revisit-radius", type=int, default=4)
    parser.add_argument("--learning-revisit-min-delay-ticks", type=int, default=20)
    parser.add_argument("--learning-revisit-max-age-ticks", type=int, default=2000)
    parser.add_argument("--learning-reward-memory-limit", type=int, default=1200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_calibration(args)
    print(json.dumps({"type": "summary", **summary}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
