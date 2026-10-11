from __future__ import annotations

import csv
import itertools
import json
import math
import statistics
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_data"
RUNS = HERE / "study_1_raw_runs"


def exact_sign_flip_p(values: list[float]) -> float:
    observed = abs(statistics.mean(values))
    extreme = 0
    total = 0
    for signs in itertools.product((-1.0, 1.0), repeat=len(values)):
        permuted = abs(statistics.mean([sign * value for sign, value in zip(signs, values)]))
        extreme += int(permuted >= observed - 1e-12)
        total += 1
    return extreme / total


def close(actual: float, expected: float, tolerance: float = 1e-9) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance):
        raise AssertionError(f"expected {expected}, got {actual}")


def verify_study_1() -> None:
    with (SOURCE / "paper_01_food_value_paired_seeds.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 10:
        raise AssertionError(f"expected 10 paired rows, got {len(rows)}")

    blind = [int(row["no_learning_meals"]) for row in rows]
    memory = [int(row["value_learning_meals"]) for row in rows]
    differences = [a - b for a, b in zip(blind, memory)]
    close(statistics.mean(blind), 1945.3)
    close(statistics.mean(memory), 423.0)
    close(statistics.mean(differences), 1522.3)
    close(exact_sign_flip_p(differences), 0.001953125)
    if not all(value > 0 for value in differences):
        raise AssertionError("not all pairs favor value memory")

    treatment_agents = []
    blind_skippers = 0
    blind_skip_events = 0
    for path in sorted(RUNS.glob("B_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        treatment_agents.extend(data["agent_diet_summary"])
    for path in sorted(RUNS.glob("A_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        blind_skippers += int(data["agent_diet_metrics"]["agents_skipped_raw_seed"])
        blind_skip_events += int(data["agent_diet_metrics"]["total_raw_seed_skips"])

    if len(treatment_agents) != 500:
        raise AssertionError(f"expected 500 treatment agents, got {len(treatment_agents)}")
    both = [agent for agent in treatment_agents if agent["tasted_raw_seed"] and agent["tasted_raw_plant"]]
    later_skip = [agent for agent in both if agent["first_raw_seed_skip_tick"] is not None]
    premature = [
        agent
        for agent in treatment_agents
        if agent["first_raw_seed_skip_tick"] is not None and not agent["tasted_raw_plant"]
    ]
    if (len(both), len(later_skip), len(premature)) != (491, 491, 0):
        raise AssertionError((len(both), len(later_skip), len(premature)))
    if blind_skippers != 0 or blind_skip_events != 0:
        raise AssertionError((blind_skippers, blind_skip_events))


def verify_study_2() -> None:
    snapshot = json.loads((SOURCE / "results_snapshot.json").read_text(encoding="utf-8"))
    toxin = snapshot["paper_02_toxin_lure"]
    close(float(toxin["analytic_lure_boundary_toxic_fraction"]), 0.625)
    close(float(toxin["safe_window_discrimination_points"]["mean"]), 0.0)

    with (SOURCE / "paper_02_toxin_learner_comparison.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    headline = {row["learner"]: row for row in rows if float(row["toxic_fraction"]) == 0.3}
    expected = {
        "L1 sim gate": 63.266666666666666,
        "L2 eps-greedy": 92.73333333333333,
        "L3 softmax": 99.2,
        "L4 sample-avg": 62.13333333333333,
    }
    for learner, value in expected.items():
        close(float(headline[learner]["lured_percent_mean"]), value)


if __name__ == "__main__":
    verify_study_1()
    verify_study_2()
    print("Article data verification: PASS")

