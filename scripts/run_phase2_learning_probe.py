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


def _watch_args(args: argparse.Namespace, seed: int) -> SimpleNamespace:
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
        learning_revisit_radius=args.learning_revisit_radius,
        learning_revisit_min_delay_ticks=args.learning_revisit_min_delay_ticks,
        learning_revisit_max_age_ticks=args.learning_revisit_max_age_ticks,
        learning_reward_memory_limit=args.learning_reward_memory_limit,
    )


def _phase2_pass(result: dict[str, Any], args: argparse.Namespace) -> bool:
    events = result.get("event_counts", {})
    learning = result.get("learning_metrics", {})
    return_lift = learning.get("owner_return_lift")
    return (
        int(events.get("plant_matured", 0)) >= args.min_plant_matured
        and int(events.get("plant_fruited", 0)) >= args.min_plant_fruited
        and int(events.get("plant_lifecycle_food_consumed", 0)) >= args.min_plant_food_consumed
        and int(learning.get("owner_returned_reward_events", 0)) >= args.min_owner_returned_rewards
        and int(learning.get("owner_return_agents", 0)) >= args.min_owner_return_agents
        and return_lift is not None
        and float(return_lift) >= args.min_owner_return_lift
    )


def _summarize_run(result: dict[str, Any], seed: int, args: argparse.Namespace) -> dict[str, Any]:
    events = result.get("event_counts", {})
    learning = result.get("learning_metrics", {})
    return {
        "seed": seed,
        "phase2_pass": _phase2_pass(result, args),
        "elapsed_seconds": result.get("elapsed_seconds"),
        "tick": result.get("tick"),
        "population": result.get("population"),
        "plant_matured": int(events.get("plant_matured", 0)),
        "plant_fruited": int(events.get("plant_fruited", 0)),
        "plant_food_consumed": int(events.get("plant_lifecycle_food_consumed", 0)),
        "plant_food_decayed": int(events.get("plant_lifecycle_food_decayed", 0)),
        "parsed_reward_events": int(learning.get("parsed_reward_events", 0)),
        "rewarded_agents": int(learning.get("rewarded_agents", 0)),
        "owner_revisited_reward_events": int(learning.get("owner_revisited_reward_events", 0)),
        "owner_revisited_reward_fraction": float(learning.get("owner_revisited_reward_fraction", 0.0)),
        "owner_revisit_agents": int(learning.get("owner_revisit_agents", 0)),
        "owner_revisit_tick_hits": int(learning.get("owner_revisit_tick_hits", 0)),
        "owner_revisit_opportunities": int(learning.get("owner_revisit_opportunities", 0)),
        "random_expected_owner_hits": float(learning.get("random_expected_owner_hits", 0.0)),
        "owner_revisit_lift": learning.get("owner_revisit_lift"),
        "first_owner_revisit_tick": learning.get("first_owner_revisit_tick"),
        "owner_left_reward_events": int(learning.get("owner_left_reward_events", 0)),
        "owner_returned_reward_events": int(learning.get("owner_returned_reward_events", 0)),
        "owner_returned_reward_fraction": float(learning.get("owner_returned_reward_fraction", 0.0)),
        "owner_return_agents": int(learning.get("owner_return_agents", 0)),
        "owner_return_tick_hits": int(learning.get("owner_return_tick_hits", 0)),
        "owner_return_opportunities": int(learning.get("owner_return_opportunities", 0)),
        "random_expected_owner_return_hits": float(learning.get("random_expected_owner_return_hits", 0.0)),
        "owner_return_lift": learning.get("owner_return_lift"),
        "first_owner_return_tick": learning.get("first_owner_return_tick"),
    }


def _mean_numeric(rows: list[dict[str, Any]], field: str) -> float:
    values = [
        float(row[field])
        for row in rows
        if row.get(field) is not None and row.get(field) != ""
    ]
    if not values:
        return 0.0
    return round(statistics.fmean(values), 4)


def _render_report(summary: dict[str, Any], rows: list[dict[str, Any]], args: argparse.Namespace) -> str:
    verdict = "PASS" if summary["phase2_pass"] else "FAIL"
    lines = [
        "# Phase 2 Learning Probe Report",
        "",
        f"- Verdict: {verdict}",
        f"- Runs: {summary['run_count']} seeds; passed {summary['passing_runs']}/{summary['run_count']}",
        f"- Gate: at least {args.min_passing_runs} passing runs",
        f"- Ecology gate per run: matured >= {args.min_plant_matured}, fruited >= {args.min_plant_fruited}, consumed >= {args.min_plant_food_consumed}",
        f"- Learning gate per run: owner returned rewards >= {args.min_owner_returned_rewards}, owner return agents >= {args.min_owner_return_agents}, return lift >= {args.min_owner_return_lift}",
        "",
        "## Aggregate Metrics",
        "",
        f"- Mean plant food consumed: {summary['mean_plant_food_consumed']}",
        f"- Mean owner returned rewards: {summary['mean_owner_returned_reward_events']}",
        f"- Mean owner return agents: {summary['mean_owner_return_agents']}",
        f"- Mean owner return lift: {summary['mean_owner_return_lift']}",
        "",
        "## Runs",
        "",
        "| seed | pass | consumed | returned_rewards | return_agents | return_lift | first_return_tick |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {seed} | {phase2_pass} | {plant_food_consumed} | {owner_returned_reward_events} | "
            "{owner_return_agents} | {owner_return_lift} | {first_owner_return_tick} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This probe does not claim farming or symbolic understanding. It tests a narrower Phase 2 claim: after receiving energy from plant-lifecycle food, the same agent leaves and later returns near that rewarded location more often than a uniform random-position baseline.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    run_dir = args.output_dir / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for seed in args.seeds:
        run_id = f"phase2_learning_seed{seed}"
        result_path = run_dir / f"{run_id}.json"
        log_path = run_dir / f"{run_id}.out.log"
        try:
            with log_path.open("w", encoding="utf-8") as log_file:
                with contextlib.redirect_stdout(log_file):
                    result = run_watch(_watch_args(args, seed))
            result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            row = _summarize_run(result, seed, args)
            rows.append(row)
            print(json.dumps({"type": "run_result", **row}, ensure_ascii=False), flush=True)
        except Exception as exc:  # pragma: no cover - batch runner keeps failures visible.
            failure = {"seed": seed, "error": repr(exc)}
            failures.append(failure)
            print(json.dumps({"type": "run_failed", **failure}, ensure_ascii=False), flush=True)

    passing_runs = sum(1 for row in rows if bool(row["phase2_pass"]))
    summary = {
        "objective": "Phase 2: test reward-place learning from plant-lifecycle food without adding semantic farming instructions.",
        "phase2_pass": passing_runs >= args.min_passing_runs and not failures,
        "run_count": len(rows),
        "passing_runs": passing_runs,
        "failure_count": len(failures),
        "seeds": args.seeds,
        "success_criteria": {
            "min_passing_runs": args.min_passing_runs,
            "min_plant_matured": args.min_plant_matured,
            "min_plant_fruited": args.min_plant_fruited,
            "min_plant_food_consumed": args.min_plant_food_consumed,
            "min_owner_returned_rewards": args.min_owner_returned_rewards,
            "min_owner_return_agents": args.min_owner_return_agents,
            "min_owner_return_lift": args.min_owner_return_lift,
        },
        "mean_plant_food_consumed": _mean_numeric(rows, "plant_food_consumed"),
        "mean_owner_revisited_reward_events": _mean_numeric(rows, "owner_revisited_reward_events"),
        "mean_owner_revisit_agents": _mean_numeric(rows, "owner_revisit_agents"),
        "mean_owner_revisit_lift": _mean_numeric(rows, "owner_revisit_lift"),
        "mean_owner_returned_reward_events": _mean_numeric(rows, "owner_returned_reward_events"),
        "mean_owner_return_agents": _mean_numeric(rows, "owner_return_agents"),
        "mean_owner_return_lift": _mean_numeric(rows, "owner_return_lift"),
        "failures": failures,
    }
    _write_csv(args.output_dir / "runs.csv", rows)
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    args.report_path.write_text(_render_report(summary, rows, args), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 2 reward-place learning probes.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/phase2_learning_probe_latest"))
    parser.add_argument("--report-path", type=Path, default=Path("reports/phase2_learning_probe_latest.md"))
    parser.add_argument("--seeds", type=_parse_int_list, default=[20260610, 20260611, 20260612])
    parser.add_argument("--min-passing-runs", type=int, default=3)
    parser.add_argument("--min-plant-matured", type=int, default=1)
    parser.add_argument("--min-plant-fruited", type=int, default=1)
    parser.add_argument("--min-plant-food-consumed", type=int, default=5)
    parser.add_argument("--min-owner-returned-rewards", type=int, default=5)
    parser.add_argument("--min-owner-return-agents", type=int, default=2)
    parser.add_argument("--min-owner-return-lift", type=float, default=2.0)
    parser.add_argument("--body-index", type=int, default=37)
    parser.add_argument("--initial-population", type=int, default=50)
    parser.add_argument("--max-population", type=int, default=250)
    parser.add_argument("--max-ticks", type=int, default=10_000_000)
    parser.add_argument("--time-limit-seconds", type=float, default=90.0)
    parser.add_argument("--progress-every-seconds", type=float, default=30.0)
    parser.add_argument("--evaluate-every-ticks", type=int, default=100_000_000)
    parser.add_argument("--event-sample-limit", type=int, default=1200)
    parser.add_argument("--spawn-strategy", default="frontier_safe_high_food")
    parser.add_argument("--immortal", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--width", type=int, default=100)
    parser.add_argument("--height", type=int, default=100)
    parser.add_argument("--max-food", type=int, default=2000)
    parser.add_argument("--base-food-spawn-per-tick", type=int, default=4)
    parser.add_argument("--food-spawn-multiplier", type=float, default=0.70)
    parser.add_argument("--bootstrap-food-spawn-ticks", type=int, default=300)
    parser.add_argument("--wild-food-spawn-after-bootstrap-multiplier", type=float, default=0.10)
    parser.add_argument("--natural-seed-rain-per-tick", type=int, default=0)
    parser.add_argument("--max-plant-seeds", type=int, default=7600)
    parser.add_argument("--large-animal-spawn-per-tick", type=int, default=2)
    parser.add_argument("--max-large-animals", type=int, default=28)
    parser.add_argument("--nest-support-food-chance", type=float, default=0.05)
    parser.add_argument("--nest-support-spawn-chance", type=float, default=0.03)
    parser.add_argument("--frontier-band", type=int, default=10)
    parser.add_argument("--global-food-decline-per-day", type=float, default=0.012)
    parser.add_argument("--minimum-global-food-multiplier", type=float, default=0.24)
    parser.add_argument("--ambient-food-decay-chance", type=float, default=0.006)
    parser.add_argument("--plant-food-decay-chance", type=float, default=0.0015)
    parser.add_argument("--plant-seed-max-age-multiplier", type=float, default=4.0)
    parser.add_argument("--plant-growth-rate-multiplier", type=float, default=2.0)
    parser.add_argument("--sprout-biomass-loss-multiplier", type=float, default=0.1)
    parser.add_argument("--germination-good-ticks-multiplier", type=float, default=0.5)
    parser.add_argument("--plant-fruiting-interval-multiplier", type=float, default=0.25)
    parser.add_argument("--plant-fruiting-growth-threshold-multiplier", type=float, default=0.5)
    parser.add_argument("--plant-fruiting-chance-multiplier", type=float, default=2.0)
    parser.add_argument("--natural-seed-drop-chance-multiplier", type=float, default=2.0)
    parser.add_argument("--learning-revisit-radius", type=int, default=4)
    parser.add_argument("--learning-revisit-min-delay-ticks", type=int, default=20)
    parser.add_argument("--learning-revisit-max-age-ticks", type=int, default=2000)
    parser.add_argument("--learning-reward-memory-limit", type=int, default=1200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_probe(args)
    print(json.dumps({"type": "summary", **summary}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
