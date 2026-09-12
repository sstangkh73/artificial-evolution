# -*- coding: utf-8 -*-
"""Paired seed-level analysis for the G1-G6 experiment series.

The inferential unit is the seed/run, never the agent and never the tick (agents
and ticks are nested inside a run and are descriptive only). Every arm is run on
the SAME seed set, so every contrast is paired and analysed on the within-seed
differences.

Reported per contrast:
  * mean and SD of each arm
  * mean paired difference with a 95% CI (Student t, plus a bootstrap CI)
  * an exact two-sided sign-flip randomization p-value while the seed count allows
    it (2^n enumerations), otherwise a seeded Monte Carlo approximation, labelled
    as such
  * Cliff's delta as a non-parametric effect size
  * the number of seeds favouring each direction

Multiplicity: a spec names ONE primary contrast. Everything else is reported as
context and marked secondary; Holm-adjusted p-values are added across the
secondary contrasts so that the adjustment is visible rather than implied.

Usage:
    python scripts/analyze_e_series.py --runs reports/e1/E1_runs.json \
        --metric founder_mean_age --primary A2:A3 --out reports/e1/E1_analysis.json
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from pathlib import Path

EXACT_LIMIT = 20          # 2^20 = 1,048,576 sign vectors: the largest exact enumeration
MONTE_CARLO_DRAWS = 200_000
MONTE_CARLO_SEED = 20260912


def mean_sd(values: list[float]) -> dict:
    return {
        "n": len(values),
        "mean": round(statistics.mean(values), 6) if values else None,
        "sd": round(statistics.stdev(values), 6) if len(values) > 1 else 0.0,
        "median": round(statistics.median(values), 6) if values else None,
    }


def t_critical_95(df: int) -> float:
    """Two-sided 95% Student t critical values for the sample sizes used here."""
    table = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
             8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145,
             15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
             24: 2.064, 29: 2.045, 39: 2.023, 59: 2.001}
    if df in table:
        return table[df]
    keys = sorted(table)
    if df > keys[-1]:
        return 1.960
    return table[min(k for k in keys if k >= df)]


def t_ci95(values: list[float]) -> dict:
    if len(values) < 2:
        return {"half_width": None, "low": None, "high": None}
    mean = statistics.mean(values)
    half = t_critical_95(len(values) - 1) * statistics.stdev(values) / math.sqrt(len(values))
    return {"half_width": round(half, 6), "low": round(mean - half, 6), "high": round(mean + half, 6)}


def bootstrap_ci95(values: list[float], draws: int = 20_000, seed: int = MONTE_CARLO_SEED) -> dict:
    if len(values) < 2:
        return {"low": None, "high": None}
    rng = random.Random(seed)
    n = len(values)
    means = sorted(statistics.mean([values[rng.randrange(n)] for _ in range(n)]) for _ in range(draws))
    return {"low": round(means[int(0.025 * draws)], 6), "high": round(means[int(0.975 * draws) - 1], 6)}


def sign_flip_p(differences: list[float]) -> dict:
    """Two-sided randomization p under exchangeable paired labels.

    Exact by enumeration while 2^n is tractable; otherwise a seeded Monte Carlo
    estimate, reported with its own method label so a reader is never left to
    assume an exact test was run.
    """
    n = len(differences)
    observed = abs(sum(differences))          # comparing sums == comparing means
    if n <= EXACT_LIMIT:
        # Gray-code enumeration: consecutive sign vectors differ in exactly one
        # position, so each of the 2^n states costs one add instead of a full
        # re-sum. At n = 20 that is the difference between a minute and a second.
        total = 1 << n
        running = sum(differences)
        extreme = 1 if abs(running) >= observed - 1e-12 else 0
        signs = [1.0] * n
        for index in range(1, total):
            bit = (index & -index).bit_length() - 1
            running -= 2.0 * signs[bit] * differences[bit]
            signs[bit] = -signs[bit]
            if abs(running) >= observed - 1e-12:
                extreme += 1
        return {"method": "exact_sign_flip", "p": extreme / total,
                "enumerations": total, "floor": 2 / total}
    rng = random.Random(MONTE_CARLO_SEED)
    extreme = 0
    for _ in range(MONTE_CARLO_DRAWS):
        permuted = abs(sum(d if rng.random() < 0.5 else -d for d in differences))
        extreme += int(permuted >= observed - 1e-12)
    # +1 correction: a Monte Carlo p is never reported as exactly zero.
    return {"method": "monte_carlo_sign_flip", "p": (extreme + 1) / (MONTE_CARLO_DRAWS + 1),
            "draws": MONTE_CARLO_DRAWS, "floor": 1 / (MONTE_CARLO_DRAWS + 1)}


def cliffs_delta(a: list[float], b: list[float]) -> dict:
    greater = sum(1 for x in a for y in b if x > y)
    lesser = sum(1 for x in a for y in b if x < y)
    delta = (greater - lesser) / (len(a) * len(b)) if a and b else 0.0
    size = ("negligible" if abs(delta) < 0.147 else
            "small" if abs(delta) < 0.33 else
            "medium" if abs(delta) < 0.474 else "large")
    return {"delta": round(delta, 6), "magnitude": size}


def holm(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    count = len(ordered)
    adjusted: dict[str, float] = {}
    running = 0.0
    for index, (name, value) in enumerate(ordered):
        running = max(running, min(1.0, (count - index) * value))
        adjusted[name] = round(running, 8)
    return adjusted


def contrast(rows_by_arm: dict[str, dict[int, float]], left: str, right: str, metric: str) -> dict:
    """left - right, paired on seed. Seeds missing from either arm are dropped and named."""
    shared = sorted(set(rows_by_arm[left]) & set(rows_by_arm[right]))
    dropped = sorted((set(rows_by_arm[left]) | set(rows_by_arm[right])) - set(shared))
    left_values = [rows_by_arm[left][s] for s in shared]
    right_values = [rows_by_arm[right][s] for s in shared]
    differences = [a - b for a, b in zip(left_values, right_values)]
    return {
        "contrast": f"{left}-{right}",
        "metric": metric,
        "n_pairs": len(shared),
        "seeds_dropped_for_missing_arm": dropped,
        left: mean_sd(left_values),
        right: mean_sd(right_values),
        "paired_difference": {
            **mean_sd(differences),
            "t_ci95": t_ci95(differences),
            "bootstrap_ci95": bootstrap_ci95(differences),
            **sign_flip_p(differences),
            "seeds_favouring_left": sum(1 for d in differences if d > 0),
            "seeds_favouring_right": sum(1 for d in differences if d < 0),
            "seeds_tied": sum(1 for d in differences if d == 0),
        },
        "cliffs_delta": cliffs_delta(left_values, right_values),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", required=True, help="the *_runs.json written by run_e_series.py")
    parser.add_argument("--metric", required=True, help="the primary dependent variable field")
    parser.add_argument("--primary", required=True, help="the primary contrast, as LEFT:RIGHT")
    parser.add_argument("--secondary", default="",
                        help="comma-separated further contrasts, e.g. A2:A0,A1:A0")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.runs).read_text(encoding="utf-8"))
    rows = payload["rows"]

    by_arm: dict[str, dict[int, float]] = {}
    missing: list[dict] = []
    for row in rows:
        value = row.get(args.metric)
        if row.get("error") or value is None:
            missing.append({"arm": row.get("arm"), "seed": row.get("seed"),
                            "reason": "run failed" if row.get("error") else f"no {args.metric}"})
            continue
        by_arm.setdefault(row["arm"], {})[int(row["seed"])] = float(value)

    left, _, right = args.primary.partition(":")
    analysis = {
        "source_runs": str(args.runs),
        "provenance": payload.get("provenance"),
        "primary_metric": args.metric,
        "inferential_unit": "seed/run",
        "runs_excluded": missing,
        "primary": contrast(by_arm, left, right, args.metric),
        "secondary": [],
    }

    secondary_names = [c for c in args.secondary.split(",") if c]
    for spec in secondary_names:
        a, _, b = spec.partition(":")
        if a in by_arm and b in by_arm:
            analysis["secondary"].append(contrast(by_arm, a, b, args.metric))
    if len(analysis["secondary"]) > 1:
        raw = {c["contrast"]: c["paired_difference"]["p"] for c in analysis["secondary"]}
        adjusted = holm(raw)
        for entry in analysis["secondary"]:
            entry["paired_difference"]["holm_adjusted_p"] = adjusted[entry["contrast"]]
        analysis["multiplicity"] = {
            "method": "Holm across secondary contrasts only",
            "note": "the primary contrast is a single pre-specified test and is not adjusted",
        }

    Path(args.out).write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
    primary = analysis["primary"]
    difference = primary["paired_difference"]
    print(f"{primary['contrast']} on {args.metric}: n={primary['n_pairs']} pairs, "
          f"mean difference {difference['mean']} "
          f"(95% CI {difference['t_ci95']['low']} to {difference['t_ci95']['high']}), "
          f"{difference['method']} p={difference['p']:.6g}, "
          f"Cliff's delta {primary['cliffs_delta']['delta']} ({primary['cliffs_delta']['magnitude']})")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
