# -*- coding: utf-8 -*-
"""Regenerate the Paper 2 source-data files from the included harnesses."""
from __future__ import annotations

import csv
import json
import math
import runpy
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "source_data"
OUT.mkdir(exist_ok=True)


def ci95(values):
    return {
        "mean": statistics.mean(values),
        "sd": statistics.stdev(values),
        "ci95_half_width": 1.96 * statistics.stdev(values) / math.sqrt(len(values)),
    }


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


multi = runpy.run_path(str(ROOT / "scripts" / "run_toxin_multiseed.py"), run_name="supp_multi")
learners = runpy.run_path(str(ROOT / "scripts" / "run_toxin_learner_comparison.py"), run_name="supp_learners")
fractions = [0.2, 0.3, 0.4, 0.5, 0.6]
seeds = int(multi["SEEDS"])

curve = []
for fraction in fractions:
    rows = [multi["result1_seed"](seed, fraction) for seed in range(seeds)]
    lure = ci95([row[0] for row in rows])
    toxic = ci95([row[1] for row in rows])
    energy = ci95([row[2] for row in rows])
    curve.append({
        "toxic_fraction": fraction,
        "lured_percent_mean": lure["mean"],
        "lured_percent_ci95_half_width": lure["ci95_half_width"],
        "toxic_meals_percent_mean": toxic["mean"],
        "energy_per_meal_mean": energy["mean"],
    })

comparison = []
for learner in learners["COL"]:
    for fraction in fractions:
        values = [learners["_run_learner"](learner, fraction, seed) for seed in range(seeds)]
        summary = ci95(values)
        comparison.append({
            "learner": learner,
            "toxic_fraction": fraction,
            "lured_percent_mean": summary["mean"],
            "lured_percent_ci95_half_width": summary["ci95_half_width"],
        })

discrimination = ci95([multi["result2_seed"](seed)[2] for seed in range(seeds)])
snapshot = {
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
}

write_csv(OUT / "paper_02_toxin_lure_curve.csv", curve)
write_csv(OUT / "paper_02_toxin_learner_comparison.csv", comparison)
(OUT / "paper_02_results_snapshot.json").write_text(
    json.dumps(snapshot, indent=2), encoding="utf-8"
)
print(json.dumps(snapshot, indent=2))
