# -*- coding: utf-8 -*-
"""Freeze compact, publication-facing statistics for the two lead papers.

This script does not run the full ecology again. It reads the completed paired
food-value runs and calls the existing toxin harnesses that drive the real toxin
mechanism. The outputs are small CSV/JSON source-data snapshots suitable for
manuscript tables, review, and later archival.
"""

from __future__ import annotations

import csv
import itertools
import json
import math
import runpy
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "publication_top2_2026-08-24" / "source_data"
FOOD_DATA = ROOT / "data" / "multiseed"
SEED_START = 20260610
SEED_STOP = 20260620
T95_DF9 = 2.262


def mean_ci95(values: list[float], t_critical: float | None = None) -> dict[str, float]:
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    critical = t_critical if t_critical is not None else 1.96
    half = critical * sd / math.sqrt(len(values)) if len(values) > 1 else 0.0
    return {"mean": mean, "sd": sd, "ci95_half_width": half}


def exact_sign_flip_paired_p(differences: list[float]) -> float:
    """Exact two-sided randomization p-value under exchangeable paired labels."""
    observed = abs(statistics.mean(differences))
    extreme = 0
    total = 0
    for signs in itertools.product((-1.0, 1.0), repeat=len(differences)):
        permuted = abs(statistics.mean([s * d for s, d in zip(signs, differences)]))
        extreme += int(permuted >= observed - 1e-12)
        total += 1
    return extreme / total


def load_food_pairs() -> list[dict[str, float | int]]:
    rows: list[dict[str, float | int]] = []
    for seed in range(SEED_START, SEED_STOP):
        a_path = FOOD_DATA / f"A_{seed}.json"
        b_path = FOOD_DATA / f"B_{seed}.json"
        if not a_path.exists() or not b_path.exists():
            raise FileNotFoundError(f"Missing paired food-value run for seed {seed}")
        a = json.loads(a_path.read_text(encoding="utf-8"))
        b = json.loads(b_path.read_text(encoding="utf-8"))
        a_meals = int(a["diet_by_kind"]["raw_seed"])
        b_meals = int(b["diet_by_kind"]["raw_seed"])
        rows.append(
            {
                "seed": seed,
                "no_learning_meals": a_meals,
                "value_learning_meals": b_meals,
                "paired_difference": a_meals - b_meals,
                "paired_ratio": a_meals / b_meals,
            }
        )
    return rows


def build_food_snapshot() -> tuple[dict, list[dict]]:
    rows = load_food_pairs()
    a = [float(row["no_learning_meals"]) for row in rows]
    b = [float(row["value_learning_meals"]) for row in rows]
    differences = [float(row["paired_difference"]) for row in rows]
    ratios = [float(row["paired_ratio"]) for row in rows]
    return (
        {
            "design": "paired-seed controlled simulation",
            "statistical_unit": "seed/run",
            "n_pairs": len(rows),
            "ticks_per_run": 3000,
            "no_learning": mean_ci95(a, T95_DF9),
            "value_learning": mean_ci95(b, T95_DF9),
            "paired_difference": {
                **mean_ci95(differences, T95_DF9),
                "median": statistics.median(differences),
                "exact_two_sided_sign_flip_p": exact_sign_flip_paired_p(differences),
                "all_pairs_favor_learning": all(d > 0 for d in differences),
            },
            "paired_ratio": {
                "mean": statistics.mean(ratios),
                "median": statistics.median(ratios),
            },
            "mechanism_control_from_report": {
                "memory_on_agents_skipping": "10/12",
                "memory_off_agents_skipping": "0/12",
                "scope": "single matched seed; mechanistic control, not the inferential unit",
            },
        },
        rows,
    )


def load_harness(path: str) -> dict:
    return runpy.run_path(str(ROOT / "scripts" / path), run_name=f"publication_{path}")


def build_toxin_snapshot() -> tuple[dict, list[dict], list[dict]]:
    multi = load_harness("run_toxin_multiseed.py")
    learners = load_harness("run_toxin_learner_comparison.py")
    fractions = [0.2, 0.3, 0.4, 0.5, 0.6]
    seeds = int(multi["SEEDS"])

    curve_rows: list[dict] = []
    for fraction in fractions:
        per_seed = [multi["result1_seed"](seed, fraction) for seed in range(seeds)]
        lured = mean_ci95([row[0] for row in per_seed])
        toxic_meals = mean_ci95([row[1] for row in per_seed])
        energy = mean_ci95([row[2] for row in per_seed])
        curve_rows.append(
            {
                "toxic_fraction": fraction,
                "lured_percent_mean": lured["mean"],
                "lured_percent_ci95_half_width": lured["ci95_half_width"],
                "toxic_meals_percent_mean": toxic_meals["mean"],
                "energy_per_meal_mean": energy["mean"],
            }
        )

    learner_rows: list[dict] = []
    for kind in learners["COL"]:
        for fraction in fractions:
            values = [learners["_run_learner"](kind, fraction, seed) for seed in range(seeds)]
            summary = mean_ci95(values)
            learner_rows.append(
                {
                    "learner": kind,
                    "toxic_fraction": fraction,
                    "lured_percent_mean": summary["mean"],
                    "lured_percent_ci95_half_width": summary["ci95_half_width"],
                }
            )

    r2 = [multi["result2_seed"](seed) for seed in range(seeds)]
    discrimination = mean_ci95([row[2] for row in r2])
    toxin_snapshot = {
        "design": "controlled two-state and safe-window mechanism experiments",
        "statistical_unit": "seed/run",
        "n_seeds": seeds,
        "agents_per_seed": int(multi["N"]),
        "trials_per_agent": int(multi["TRIALS"]),
        "fresh_net_energy": float(learners["NET_FRESH"]),
        "aged_net_energy": float(learners["NET_AGED"]),
        "safe_staple_energy": float(learners["STAPLE"]),
        "analytic_lure_boundary_toxic_fraction": (
            (learners["NET_AGED"] - learners["STAPLE"])
            / (learners["NET_AGED"] - learners["NET_FRESH"])
        ),
        "safe_window_discrimination_points": discrimination,
        "fitness_cost_demonstrated": False,
        "full_ecology_demonstrated": False,
        "claim_boundary": (
            "The representation-level discrimination failure is analytic; lure magnitude is "
            "learner- and protocol-specific. Survival or evolutionary cost is not established."
        ),
    }
    return toxin_snapshot, curve_rows, learner_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    food, food_rows = build_food_snapshot()
    toxin, toxin_curve, toxin_learners = build_toxin_snapshot()
    snapshot = {
        "generated_by": "scripts/prepare_top_two_publication_stats.py",
        "source_scope": "existing completed runs and existing real-mechanism toxin harnesses",
        "paper_01_food_value": food,
        "paper_02_toxin_lure": toxin,
    }
    (OUT / "results_snapshot.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_csv(OUT / "paper_01_food_value_paired_seeds.csv", food_rows)
    write_csv(OUT / "paper_02_toxin_lure_curve.csv", toxin_curve)
    write_csv(OUT / "paper_02_toxin_learner_comparison.csv", toxin_learners)
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
