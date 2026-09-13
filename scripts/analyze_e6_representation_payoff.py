# -*- coding: utf-8 -*-
"""Primary E6 analysis: seed-level slope of B2-B3 across realized fruit energy.

The capacity-matched sham (B3) is the causal control for the age-informed key
(B2). For each complete seed, this script computes B2-B3 at each preregistered
energy and fits one ordinary-least-squares slope. Those seed-level slopes are the
inferential observations used by the exact sign-flip test.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

from analyze_e_series import bootstrap_ci95, mean_sd, sign_flip_p, t_ci95

ARM_PATTERN = re.compile(r"^V(?P<energy>\d+)_B(?P<condition>[123])$")
EXPECTED_ENERGIES = (4, 5, 6, 8, 10)


def ols_slope(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("slope requires at least two paired x/y observations")
    x_bar = statistics.mean(xs)
    y_bar = statistics.mean(ys)
    denominator = sum((x - x_bar) ** 2 for x in xs)
    if denominator == 0:
        raise ValueError("slope predictor has zero variance")
    return sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys)) / denominator


def analyze_payload(
    payload: dict,
    metric: str = "founder_mean_followup_ticks",
    expected_seed_count: int | None = None,
    expected_seeds: set[int] | None = None,
) -> dict:
    values: dict[int, dict[int, dict[str, float]]] = {}
    unusable_rows: list[dict] = []
    for row in payload.get("rows", []):
        match = ARM_PATTERN.fullmatch(str(row.get("arm", "")))
        if not match:
            continue
        value = row.get(metric)
        if row.get("error") or value is None:
            unusable_rows.append({
                "arm": row.get("arm"),
                "seed": row.get("seed"),
                "reason": "run failed" if row.get("error") else f"no {metric}",
            })
            continue
        seed = int(row["seed"])
        energy = int(match.group("energy"))
        condition = f"B{match.group('condition')}"
        values.setdefault(seed, {}).setdefault(energy, {})[condition] = float(value)

    complete_seeds: list[int] = []
    excluded_seeds: list[dict] = []
    design_missing: list[dict] = []
    per_seed: list[dict] = []
    raw_slopes: list[float] = []
    seeds_to_check = sorted(expected_seeds if expected_seeds is not None else values)
    for seed in seeds_to_check:
        missing_design_arms = [
            f"V{energy:02d}_{condition}"
            for energy in EXPECTED_ENERGIES
            for condition in ("B1", "B2", "B3")
            if condition not in values.get(seed, {}).get(energy, {})
        ]
        if missing_design_arms:
            design_missing.append({"seed": seed, "missing": missing_design_arms})
        missing = [
            f"V{energy:02d}_{condition}"
            for energy in EXPECTED_ENERGIES
            for condition in ("B2", "B3")
            if condition not in values.get(seed, {}).get(energy, {})
        ]
        if missing:
            excluded_seeds.append({"seed": seed, "missing": missing})
            continue
        differences = {
            str(energy): values[seed][energy]["B2"] - values[seed][energy]["B3"]
            for energy in EXPECTED_ENERGIES
        }
        slope = ols_slope(
            [float(energy) for energy in EXPECTED_ENERGIES],
            [differences[str(energy)] for energy in EXPECTED_ENERGIES],
        )
        complete_seeds.append(seed)
        raw_slopes.append(slope)
        per_seed.append({
            "seed": seed,
            "b2_minus_b3_by_realized_energy": {
                energy: round(value, 6) for energy, value in differences.items()
            },
            "slope_ticks_per_energy_unit": round(slope, 6),
        })

    slopes = raw_slopes
    primary = {
        "contrast": "B2-B3",
        "metric": metric,
        "predictor": "realized fruit energy",
        "energies": list(EXPECTED_ENERGIES),
        "n_complete_seeds": len(slopes),
        "slope_summary": mean_sd(slopes),
        "t_ci95": t_ci95(slopes),
        "bootstrap_ci95": bootstrap_ci95(slopes),
        "slopes_positive": sum(s > 0 for s in slopes),
        "slopes_negative": sum(s < 0 for s in slopes),
        "slopes_zero": sum(s == 0 for s in slopes),
    }
    if slopes:
        primary.update(sign_flip_p(slopes))

    provenance = payload.get("provenance") or {}
    required_provenance = (
        "git_revision_start",
        "git_revision_end",
        "git_revision_changed_during_run",
        "git_tree_dirty_start",
        "git_tree_dirty_end",
        "failures",
    )
    provenance_complete = all(key in provenance for key in required_provenance)
    unexpected_seeds = sorted(set(values) - expected_seeds) if expected_seeds is not None else []
    expected_seed_count = (
        len(expected_seeds) if expected_seeds is not None else expected_seed_count
    )
    design_complete = (
        (expected_seeds is None or bool(expected_seeds))
        and not excluded_seeds
        and not design_missing
        and not unexpected_seeds
        and not unusable_rows
        and (expected_seed_count is None or len(slopes) == expected_seed_count)
    )
    confirmatory_eligible = provenance_complete and design_complete and not (
        provenance.get("git_tree_dirty")
        or provenance.get("git_tree_dirty_start")
        or provenance.get("git_tree_dirty_end")
        or provenance.get("git_revision_changed_during_run")
        or provenance.get("failures")
    )
    return {
        "analysis": "E6 representation-payoff slope",
        "inferential_unit": "seed-level slope",
        "provenance": provenance,
        "provenance_complete": provenance_complete,
        "design_complete": design_complete,
        "confirmatory_provenance_eligible": confirmatory_eligible,
        "complete_seeds": complete_seeds,
        "excluded_seeds": excluded_seeds,
        "design_missing": design_missing,
        "unexpected_seeds": unexpected_seeds,
        "unusable_rows": unusable_rows,
        "per_seed": per_seed,
        "primary": primary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", required=True)
    parser.add_argument("--metric", default="founder_mean_followup_ticks")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.runs).read_text(encoding="utf-8"))
    expected_seeds = ((payload.get("provenance") or {}).get("spec") or {}).get("seeds")
    expected_seed_set = (
        {int(seed) for seed in expected_seeds} if isinstance(expected_seeds, list) else set()
    )
    analysis = analyze_payload(
        payload,
        metric=args.metric,
        expected_seeds=expected_seed_set,
    )
    Path(args.out).write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")

    primary = analysis["primary"]
    summary = primary["slope_summary"]
    print(f"B2-B3 slope: n={primary['n_complete_seeds']} complete seeds, "
          f"mean={summary['mean']} ticks/energy unit, "
          f"95% CI {primary['t_ci95']['low']} to {primary['t_ci95']['high']}, "
          f"p={primary.get('p')}")
    print(f"wrote {args.out}")
    return 0 if analysis["confirmatory_provenance_eligible"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
