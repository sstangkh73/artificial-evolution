from __future__ import annotations

import argparse
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

from scripts.run_phase4_managed_patch_probe import run_probe


def _parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def _mean(rows: list[dict[str, Any]], field: str) -> float:
    values = [
        float(row[field])
        for row in rows
        if row.get(field) not in {None, ""}
    ]
    if not values:
        return 0.0
    return round(statistics.fmean(values), 4)


def _read_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _condition_args(args: argparse.Namespace, condition: dict[str, Any]) -> SimpleNamespace:
    condition_id = condition["condition_id"]
    return SimpleNamespace(
        output_dir=args.output_dir / condition_id,
        report_path=args.report_dir / f"phase4_1_{condition_id}_2026-06-13.th.md",
        seeds=args.seeds,
        min_passing_runs=args.min_passing_runs,
        min_repeated_drop_patch_count=1,
        min_patch_completed_seed_chains=3,
        min_patch_food_consumed=3,
        min_patch_return_agents=2,
        min_patch_productivity_lift_vs_control=1.25,
        min_patch_return_lift_vs_random_control=2.0,
        allow_unbounded_productivity_lift=True,
        require_no_contamination=True,
        body_index=37,
        initial_population=50,
        max_population=250,
        max_ticks=10_000_000,
        time_limit_seconds=args.time_limit_seconds,
        progress_every_seconds=args.progress_every_seconds,
        evaluate_every_ticks=100_000_000,
        event_sample_limit=args.event_sample_limit,
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
        learning_reward_memory_limit=1200,
        phase3_min_seed_move_distance=1,
        phase4_patch_radius=4,
        phase4_min_patch_moved_seed_drops=3,
        phase4_patch_return_min_delay_ticks=20,
        phase4_patch_return_max_age_ticks=2000,
        phase4_min_matched_control_seeds=5,
        food_signal_radius_cap=condition["food_signal_radius_cap"],
        plant_lifecycle_food_signal_weight=condition["plant_lifecycle_food_signal_weight"],
    )


def _conditions(args: argparse.Namespace) -> list[dict[str, Any]]:
    selected = set(args.conditions)
    all_conditions = [
        {
            "condition_id": "baseline_100x100",
            "description": "Phase 4 baseline world and food-signal settings.",
            "width": 100,
            "height": 100,
            "max_food": 2000,
            "max_plant_seeds": 7600,
            "base_food_spawn_per_tick": 4,
            "frontier_band": 10,
            "food_signal_radius_cap": None,
            "plant_lifecycle_food_signal_weight": 1.35,
        },
        {
            "condition_id": "low_food_signal_100x100",
            "description": "Reduce food-signal radius and remove extra plant-lifecycle attraction weight.",
            "width": 100,
            "height": 100,
            "max_food": 2000,
            "max_plant_seeds": 7600,
            "base_food_spawn_per_tick": 4,
            "frontier_band": 10,
            "food_signal_radius_cap": 2,
            "plant_lifecycle_food_signal_weight": 1.0,
        },
        {
            "condition_id": "large_world_200x200",
            "description": "Scale world area 4x while keeping food and seed capacity density roughly similar.",
            "width": 200,
            "height": 200,
            "max_food": 8000,
            "max_plant_seeds": 30400,
            "base_food_spawn_per_tick": 16,
            "frontier_band": 20,
            "food_signal_radius_cap": None,
            "plant_lifecycle_food_signal_weight": 1.35,
        },
    ]
    if "all" in selected:
        return all_conditions
    return [condition for condition in all_conditions if condition["condition_id"] in selected]


def _render_report(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# รายงาน Phase 4.1: Return-Signal Falsification",
        "",
        "วันที่รัน: 2026-06-13",
        f"ชุดข้อมูล: `{summary['output_dir']}`",
        "",
        "## Objective",
        "",
        "ทดสอบข้อสงสัยว่า Phase 4 ผ่านเพราะ agent กลับ patch เฉพาะตัวจริง หรือเพราะทุก agent ถูก food attraction / world density ดึงเข้าพื้นที่อาหารเหมือนกันหมด",
        "",
        "## Conditions",
        "",
    ]
    for condition in summary["conditions"]:
        lines.append(
            f"- `{condition['condition_id']}`: {condition['description']} "
            f"(world={condition['width']}x{condition['height']}, "
            f"food_signal_radius_cap={condition['food_signal_radius_cap']}, "
            f"plant_weight={condition['plant_lifecycle_food_signal_weight']})"
        )
    lines.extend(
        [
            "",
            "## Aggregate Results",
            "",
            "| condition | runs | pass | patches | patch food | return agents | dropper return rate | dropper lift | non-dropper lift | prod lift |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for condition in summary["condition_summaries"]:
        lines.append(
            "| {condition_id} | {run_count} | {passing_runs} | {mean_repeated_drop_patch_count} | "
            "{mean_patch_food_consumed} | {mean_patch_return_agents} | "
            "{mean_patch_dropper_return_rate_after_left} | "
            "{mean_best_patch_dropper_return_lift_vs_random_control} | "
            "{mean_best_patch_non_dropper_return_lift_vs_random_control} | "
            "{mean_best_patch_productivity_lift_vs_control} |".format(**condition)
        )
    lines.extend(
        [
            "",
            "## Per-Run Results",
            "",
            "| condition | seed | pass | patches | patch chains | patch food | return agents | dropper return rate | dropper lift | non-dropper lift | pre-drop visits | visit delta |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            "| {condition_id} | {seed} | {phase4_pass} | {repeated_drop_patch_count} | "
            "{patch_completed_seed_chains} | {patch_food_consumed} | {patch_return_agents} | "
            "{patch_dropper_return_rate_after_left} | {best_patch_dropper_return_lift_vs_random_control} | "
            "{best_patch_non_dropper_return_lift_vs_random_control} | "
            "{best_patch_pre_drop_visit_count_at_first_drop} | {best_patch_visit_delta_after_first_drop} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Interpretation Rules",
            "",
            "- ถ้า dropper return rate/lift ต่ำ แต่ non-dropper lift สูง แปลว่า signal หลักน่าจะเป็น food hotspot หรือ social/foraging attraction",
            "- ถ้า low-food-signal แล้วยังมี patch productivity แต่ return ลดลงมาก แปลว่า Phase 4 productivity ยังอยู่ แต่ return metric เดิม inflated",
            "- ถ้า world ใหญ่ขึ้นแล้ว return agents ลดลงมาก แปลว่าโลก 100x100 อาจเล็ก/หนาแน่นเกินสำหรับ claim เรื่อง patch-specific behavior",
            "",
            "## Limitations",
            "",
            "- นี่เป็น falsification gate ขนาดเล็ก ไม่ใช่ replication ระดับ paper",
            "- ยังไม่ได้ปิด memory หรือ shuffled reward labels",
            "- ยังไม่ได้บังคับ same-agent ownership เป็น success gate",
        ]
    )
    return "\n".join(lines) + "\n"


def run_suite(args: argparse.Namespace) -> dict[str, Any]:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    conditions = _conditions(args)
    all_rows: list[dict[str, Any]] = []
    condition_summaries: list[dict[str, Any]] = []
    for condition in conditions:
        condition_args = _condition_args(args, condition)
        print(json.dumps({"type": "condition_start", **condition}, ensure_ascii=False), flush=True)
        condition_summary = run_probe(condition_args)
        condition_rows = _read_csv(condition_args.output_dir / "runs.csv")
        for row in condition_rows:
            row["condition_id"] = condition["condition_id"]
            all_rows.append(row)
        enriched_summary = {
            "condition_id": condition["condition_id"],
            "description": condition["description"],
            **condition_summary,
        }
        condition_summaries.append(enriched_summary)
        print(json.dumps({"type": "condition_summary", **enriched_summary}, ensure_ascii=False), flush=True)

    summary = {
        "objective": "Phase 4.1 falsification of broad return-agent signal.",
        "output_dir": str(args.output_dir),
        "seeds": args.seeds,
        "time_limit_seconds": args.time_limit_seconds,
        "conditions": conditions,
        "condition_summaries": condition_summaries,
        "row_count": len(all_rows),
        "mean_dropper_return_rate_after_left": _mean(all_rows, "patch_dropper_return_rate_after_left"),
        "mean_non_dropper_return_lift": _mean(all_rows, "best_patch_non_dropper_return_lift_vs_random_control"),
        "mean_dropper_return_lift": _mean(all_rows, "best_patch_dropper_return_lift_vs_random_control"),
    }
    _write_csv(args.output_dir / "runs.csv", all_rows)
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    args.report_path.write_text(_render_report(summary, all_rows), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 4.1 return-signal falsification suite.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/phase4_1_falsification_latest"))
    parser.add_argument("--report-dir", type=Path, default=Path("reports"))
    parser.add_argument("--report-path", type=Path, default=Path("reports/phase4_1_falsification_latest.th.md"))
    parser.add_argument("--seeds", type=_parse_int_list, default=[20260610, 20260611, 20260612])
    parser.add_argument("--conditions", nargs="+", default=["all"])
    parser.add_argument("--min-passing-runs", type=int, default=1)
    parser.add_argument("--time-limit-seconds", type=float, default=60.0)
    parser.add_argument("--progress-every-seconds", type=float, default=30.0)
    parser.add_argument("--event-sample-limit", type=int, default=1600)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_suite(args)
    print(json.dumps({"type": "summary", **summary}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
