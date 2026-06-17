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
        phase3_min_seed_move_distance=args.phase3_min_seed_move_distance,
        phase4_patch_radius=args.phase4_patch_radius,
        phase4_min_patch_moved_seed_drops=args.phase4_min_patch_moved_seed_drops,
        phase4_patch_return_min_delay_ticks=args.phase4_patch_return_min_delay_ticks,
        phase4_patch_return_max_age_ticks=args.phase4_patch_return_max_age_ticks,
        phase4_min_matched_control_seeds=args.phase4_min_matched_control_seeds,
        food_signal_radius_cap=args.food_signal_radius_cap,
        plant_lifecycle_food_signal_weight=args.plant_lifecycle_food_signal_weight,
    )


def _lift_ok(
    lift: Any,
    minimum: float,
    *,
    allow_unbounded: bool,
    unbounded: bool,
    completed_chains: int,
    min_completed_chains: int,
) -> bool:
    if lift is not None and float(lift) >= minimum:
        return True
    return allow_unbounded and unbounded and completed_chains >= min_completed_chains


def _phase4_pass(result: dict[str, Any], args: argparse.Namespace) -> bool:
    metrics = result.get("phase4_patch_metrics", {})
    best_patch = metrics.get("best_patch") or {}
    productivity_lift = metrics.get("best_patch_productivity_lift_vs_control")
    return_lift = metrics.get("best_patch_return_lift_vs_random_control")
    completed_chains = int(metrics.get("patch_completed_seed_chains", 0))
    return (
        int(metrics.get("repeated_drop_patch_count", 0)) >= args.min_repeated_drop_patch_count
        and completed_chains >= args.min_patch_completed_seed_chains
        and int(metrics.get("patch_food_consumed", 0)) >= args.min_patch_food_consumed
        and int(metrics.get("patch_return_agents", 0)) >= args.min_patch_return_agents
        and _lift_ok(
            productivity_lift,
            args.min_patch_productivity_lift_vs_control,
            allow_unbounded=args.allow_unbounded_productivity_lift,
            unbounded=bool(best_patch.get("productivity_lift_unbounded", False)),
            completed_chains=completed_chains,
            min_completed_chains=args.min_patch_completed_seed_chains,
        )
        and return_lift is not None
        and float(return_lift) >= args.min_patch_return_lift_vs_random_control
        and (
            not args.require_no_contamination
            or int(metrics.get("contamination_events", 0)) == 0
        )
    )


def _summarize_run(result: dict[str, Any], seed: int, args: argparse.Namespace) -> dict[str, Any]:
    events = result.get("event_counts", {})
    seed_metrics = result.get("seed_causality_metrics", {})
    patch_metrics = result.get("phase4_patch_metrics", {})
    best_patch = patch_metrics.get("best_patch") or {}
    return {
        "seed": seed,
        "phase4_pass": _phase4_pass(result, args),
        "elapsed_seconds": result.get("elapsed_seconds"),
        "tick": result.get("tick"),
        "population": result.get("population"),
        "plant_food_consumed": int(events.get("plant_lifecycle_food_consumed", 0)),
        "seed_picked": int(events.get("seed_picked", 0)),
        "seed_dropped": int(events.get("seed_dropped", 0)),
        "agent_moved_seed_count": int(seed_metrics.get("agent_moved_seed_count", 0)),
        "agent_moved_seed_completed_chains": int(seed_metrics.get("agent_moved_seed_completed_chains", 0)),
        "repeated_drop_patch_count": int(patch_metrics.get("repeated_drop_patch_count", 0)),
        "patch_completed_seed_chains": int(patch_metrics.get("patch_completed_seed_chains", 0)),
        "patch_food_consumed": int(patch_metrics.get("patch_food_consumed", 0)),
        "patch_return_agents": int(patch_metrics.get("patch_return_agents", 0)),
        "max_patch_moved_seed_drops": int(patch_metrics.get("max_patch_moved_seed_drops", 0)),
        "max_patch_completed_chains": int(patch_metrics.get("max_patch_completed_chains", 0)),
        "best_patch_productivity_lift_vs_control": patch_metrics.get("best_patch_productivity_lift_vs_control"),
        "best_patch_return_lift_vs_random_control": patch_metrics.get("best_patch_return_lift_vs_random_control"),
        "patch_dropper_left_watchers": int(patch_metrics.get("patch_dropper_left_watchers", 0)),
        "patch_dropper_returned_after_left_count": int(
            patch_metrics.get("patch_dropper_returned_after_left_count", 0)
        ),
        "patch_dropper_return_rate_after_left": float(
            patch_metrics.get("patch_dropper_return_rate_after_left", 0.0)
        ),
        "best_patch_dropper_return_lift_vs_random_control": patch_metrics.get(
            "best_patch_dropper_return_lift_vs_random_control"
        ),
        "best_patch_non_dropper_return_lift_vs_random_control": patch_metrics.get(
            "best_patch_non_dropper_return_lift_vs_random_control"
        ),
        "best_patch_dropper_return_rate_after_left": float(
            patch_metrics.get("best_patch_dropper_return_rate_after_left", 0.0)
        ),
        "best_patch_non_dropper_return_agents": int(patch_metrics.get("best_patch_non_dropper_return_agents", 0)),
        "best_patch_pre_drop_visit_count_at_first_drop": int(
            patch_metrics.get("best_patch_pre_drop_visit_count_at_first_drop", 0)
        ),
        "best_patch_visit_delta_after_first_drop": int(patch_metrics.get("best_patch_visit_delta_after_first_drop", 0)),
        "best_patch_pre_fruit_return_agents": int(patch_metrics.get("best_patch_pre_fruit_return_agents", 0)),
        "best_patch_post_fruit_return_agents": int(patch_metrics.get("best_patch_post_fruit_return_agents", 0)),
        "best_patch_post_to_pre_fruit_return_agent_ratio": patch_metrics.get(
            "best_patch_post_to_pre_fruit_return_agent_ratio"
        ),
        "best_patch_control_mode": best_patch.get("control_mode"),
        "best_patch_control_seed_count": int(best_patch.get("control_seed_count", 0)),
        "best_patch_productivity_lift_unbounded": bool(best_patch.get("productivity_lift_unbounded", False)),
        "contamination_events": int(patch_metrics.get("contamination_events", 0)),
        "best_patch_center": best_patch.get("center"),
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
    verdict = "ผ่าน" if summary["phase4_pass"] else "ยังไม่ผ่าน"
    lines = [
        "# รายงาน Phase 4: Managed Patch / Proto-Farm Probe",
        "",
        "วันที่รัน: 2026-06-13",
        f"ชุดข้อมูล: `{args.output_dir}`",
        "",
        "## คำตัดสิน",
        "",
        f"Phase 4: {verdict}",
        "",
        f"- รันทั้งหมด: {summary['run_count']} seeds",
        f"- ผ่าน: {summary['passing_runs']}/{summary['run_count']}",
        f"- เกณฑ์ชุด: อย่างน้อย {args.min_passing_runs} runs ต้องผ่าน",
        "",
        "## เกณฑ์ต่อ Run",
        "",
        f"- repeated-drop patches >= {args.min_repeated_drop_patch_count}",
        f"- completed seed chains ใน patch >= {args.min_patch_completed_seed_chains}",
        f"- consumed food จาก patch >= {args.min_patch_food_consumed}",
        f"- return agents หลัง drop >= {args.min_patch_return_agents}",
        f"- productivity lift vs control >= {args.min_patch_productivity_lift_vs_control}",
        f"- return lift vs random >= {args.min_patch_return_lift_vs_random_control}",
        f"- contamination events ต้องเป็น 0: {args.require_no_contamination}",
        "",
        "## Aggregate Metrics",
        "",
        f"- mean repeated-drop patch count: {summary['mean_repeated_drop_patch_count']}",
        f"- mean patch completed chains: {summary['mean_patch_completed_seed_chains']}",
        f"- mean patch food consumed: {summary['mean_patch_food_consumed']}",
        f"- mean patch return agents: {summary['mean_patch_return_agents']}",
        f"- mean max patch moved-seed drops: {summary['mean_max_patch_moved_seed_drops']}",
        f"- mean max patch completed chains: {summary['mean_max_patch_completed_chains']}",
        f"- mean productivity lift: {summary['mean_best_patch_productivity_lift_vs_control']}",
        f"- mean return lift: {summary['mean_best_patch_return_lift_vs_random_control']}",
        f"- mean dropper return rate after leaving: {summary['mean_patch_dropper_return_rate_after_left']}",
        f"- mean best dropper return lift: {summary['mean_best_patch_dropper_return_lift_vs_random_control']}",
        f"- mean best non-dropper return lift: {summary['mean_best_patch_non_dropper_return_lift_vs_random_control']}",
        f"- total contamination events: {summary['total_contamination_events']}",
        "",
        "## Runs",
        "",
        "| seed | pass | moved seeds | patches | patch chains | patch food | return agents | dropper return rate | dropper lift | non-dropper lift | prod lift | return lift | contam |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {seed} | {phase4_pass} | {agent_moved_seed_count} | {repeated_drop_patch_count} | "
            "{patch_completed_seed_chains} | {patch_food_consumed} | {patch_return_agents} | "
            "{patch_dropper_return_rate_after_left} | {best_patch_dropper_return_lift_vs_random_control} | "
            "{best_patch_non_dropper_return_lift_vs_random_control} | {best_patch_productivity_lift_vs_control} | "
            "{best_patch_return_lift_vs_random_control} | {contamination_events} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Phase 4 วัดว่า agent-moved seeds รวมตัวเป็น repeated-drop patch ที่มีผลผลิตและมีการกลับมาใช้พื้นที่ซ้ำหรือไม่ โดยไม่ใช้ `tend_food_patch` หรือ `managed_food_map` เป็นหลักฐานผ่าน",
            "",
            "ถ้าผ่าน จึงควรเรียกอย่างระมัดระวังว่า managed patch / proto-farm evidence ไม่ใช่หลักฐานว่า agent เข้าใจการทำฟาร์มเชิงสัญลักษณ์",
            "",
            "## Limitations",
            "",
            "- control แบบ matched micro-site ใช้ข้อมูลคุณภาพ cell ณ เวลา summary จึงยังไม่เทียบเท่า causal counterfactual เต็มรูปแบบ",
            "- agent ยัง immortal เพื่อคงเงื่อนไขทดลองเดิมของ Phase 1-4",
            "- sample size ในรอบนี้ยังเป็น gate-level ไม่ใช่ paper-quality replication",
            "- return lift อาจรวม food attraction และ social clustering จึงยังต้องมี ablation ในเฟสถัดไป",
        ]
    )
    if summary["failures"]:
        lines.extend(["", "## Failures", ""])
        for failure in summary["failures"]:
            lines.append(f"- seed {failure['seed']}: `{failure['error']}`")
    return "\n".join(lines) + "\n"


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    run_dir = args.output_dir / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for seed in args.seeds:
        run_id = f"phase4_managed_patch_seed{seed}"
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
        except Exception as exc:  # pragma: no cover - visible batch failure record.
            failure = {"seed": seed, "error": repr(exc)}
            failures.append(failure)
            print(json.dumps({"type": "run_failed", **failure}, ensure_ascii=False), flush=True)

    passing_runs = sum(1 for row in rows if bool(row["phase4_pass"]))
    summary = {
        "objective": "Phase 4: test whether agent-moved seeds form repeated productive patches that agents revisit.",
        "phase4_pass": passing_runs >= args.min_passing_runs and not failures,
        "run_count": len(rows),
        "passing_runs": passing_runs,
        "failure_count": len(failures),
        "seeds": args.seeds,
        "success_criteria": {
            "min_passing_runs": args.min_passing_runs,
            "min_repeated_drop_patch_count": args.min_repeated_drop_patch_count,
            "min_patch_completed_seed_chains": args.min_patch_completed_seed_chains,
            "min_patch_food_consumed": args.min_patch_food_consumed,
            "min_patch_return_agents": args.min_patch_return_agents,
            "min_patch_productivity_lift_vs_control": args.min_patch_productivity_lift_vs_control,
            "min_patch_return_lift_vs_random_control": args.min_patch_return_lift_vs_random_control,
            "require_no_contamination": args.require_no_contamination,
        },
        "mean_repeated_drop_patch_count": _mean_numeric(rows, "repeated_drop_patch_count"),
        "mean_patch_completed_seed_chains": _mean_numeric(rows, "patch_completed_seed_chains"),
        "mean_patch_food_consumed": _mean_numeric(rows, "patch_food_consumed"),
        "mean_patch_return_agents": _mean_numeric(rows, "patch_return_agents"),
        "mean_max_patch_moved_seed_drops": _mean_numeric(rows, "max_patch_moved_seed_drops"),
        "mean_max_patch_completed_chains": _mean_numeric(rows, "max_patch_completed_chains"),
        "mean_best_patch_productivity_lift_vs_control": _mean_numeric(rows, "best_patch_productivity_lift_vs_control"),
        "mean_best_patch_return_lift_vs_random_control": _mean_numeric(rows, "best_patch_return_lift_vs_random_control"),
        "mean_patch_dropper_return_rate_after_left": _mean_numeric(rows, "patch_dropper_return_rate_after_left"),
        "mean_best_patch_dropper_return_lift_vs_random_control": _mean_numeric(
            rows,
            "best_patch_dropper_return_lift_vs_random_control",
        ),
        "mean_best_patch_non_dropper_return_lift_vs_random_control": _mean_numeric(
            rows,
            "best_patch_non_dropper_return_lift_vs_random_control",
        ),
        "mean_best_patch_pre_drop_visit_count_at_first_drop": _mean_numeric(
            rows,
            "best_patch_pre_drop_visit_count_at_first_drop",
        ),
        "mean_best_patch_visit_delta_after_first_drop": _mean_numeric(
            rows,
            "best_patch_visit_delta_after_first_drop",
        ),
        "total_contamination_events": sum(int(row.get("contamination_events", 0)) for row in rows),
        "failures": failures,
    }
    _write_csv(args.output_dir / "runs.csv", rows)
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    args.report_path.write_text(_render_report(summary, rows, args), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 4 managed-patch/proto-farm probes.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/phase4_managed_patch_latest"))
    parser.add_argument("--report-path", type=Path, default=Path("reports/phase4_managed_patch_latest.th.md"))
    parser.add_argument("--seeds", type=_parse_int_list, default=[20260610, 20260611, 20260612, 20260613, 20260614])
    parser.add_argument("--min-passing-runs", type=int, default=3)
    parser.add_argument("--min-repeated-drop-patch-count", type=int, default=1)
    parser.add_argument("--min-patch-completed-seed-chains", type=int, default=3)
    parser.add_argument("--min-patch-food-consumed", type=int, default=3)
    parser.add_argument("--min-patch-return-agents", type=int, default=2)
    parser.add_argument("--min-patch-productivity-lift-vs-control", type=float, default=1.25)
    parser.add_argument("--min-patch-return-lift-vs-random-control", type=float, default=2.0)
    parser.add_argument("--allow-unbounded-productivity-lift", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--require-no-contamination", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--body-index", type=int, default=37)
    parser.add_argument("--initial-population", type=int, default=50)
    parser.add_argument("--max-population", type=int, default=250)
    parser.add_argument("--max-ticks", type=int, default=10_000_000)
    parser.add_argument("--time-limit-seconds", type=float, default=150.0)
    parser.add_argument("--progress-every-seconds", type=float, default=30.0)
    parser.add_argument("--evaluate-every-ticks", type=int, default=100_000_000)
    parser.add_argument("--event-sample-limit", type=int, default=1800)
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
    parser.add_argument("--phase3-min-seed-move-distance", type=int, default=1)
    parser.add_argument("--phase4-patch-radius", type=int, default=4)
    parser.add_argument("--phase4-min-patch-moved-seed-drops", type=int, default=3)
    parser.add_argument("--phase4-patch-return-min-delay-ticks", type=int, default=20)
    parser.add_argument("--phase4-patch-return-max-age-ticks", type=int, default=2000)
    parser.add_argument("--phase4-min-matched-control-seeds", type=int, default=5)
    parser.add_argument("--food-signal-radius-cap", type=int, default=None)
    parser.add_argument("--plant-lifecycle-food-signal-weight", type=float, default=1.35)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_probe(args)
    print(json.dumps({"type": "summary", **summary}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
