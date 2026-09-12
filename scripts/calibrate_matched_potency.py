# -*- coding: utf-8 -*-
"""Solve the toxin_potency_scale that makes E1 arm A3 a fair control for A2.

Why this exists
---------------
PLAN_E1_E6 specifies A3 as "constant potency at p-bar, the MEAN POTENCY of the
detox arm". That is not a dose-matched control. `metabolism.toxin_penalty`
subtracts the body's `toxin_tolerance` from the load first:

    dose(p) = max(0, load * p - tolerance)

which is CONVEX in p. By Jensen's inequality a variable-potency arm whose mean
potency is p-bar ingests at least as much toxin as a constant-p-bar arm, and with
the shipped raw_fruit numbers (load 0.36, default tolerance 0.2) the gap is about
18x, not a rounding error: linear detox over ages 0-7 gives mean dose 0.0463 while
constant potency 0.5625 gives 0.0025.

An A3 built on mean potency would therefore be badly UNDER-dosed, and "A2 died
sooner than A3" would be explained by A2 simply eating more poison -- precisely the
confound A3 exists to remove (PLAN_G1_G6 S3.4). So A3 is matched on realised DOSE.

What is matched, exactly
------------------------
The target is the mean dose per *encounter*, weighted by the age-at-encounter
distribution measured in an A2 pilot run (P3 encounter telemetry), and averaged
over the founder `toxin_tolerance` distribution:

    target = SUM_bins  w(bin) * MEAN_bodies dose(potency(age_of_bin), tolerance)

Encounters are used rather than meals because the age-at-meal distribution is
filtered by the policy under test, which would make the control depend on the
result. Encounter ages are set by food spawn/decay and movement, so they are far
closer to an exogenous exposure distribution. Any residual dependence is a
limitation to state in the manuscript, not something this script can remove.

Usage
-----
    # from an A2 pilot dump written with --encounter-telemetry --agent-outcome-telemetry
    python scripts/calibrate_matched_potency.py --dump data/e0_pilot_A2/summary_dump.json \
        --detox-ticks 4

    # or from an explicit age distribution
    python scripts/calibrate_matched_potency.py --detox-ticks 8 --uniform-ages 0:8
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from world import metabolism  # noqa: E402


def dose(potency: float, tolerance: float, kind: str = "raw_fruit") -> float:
    """Realised toxin dose for one bite of `kind` at a given potency and tolerance."""
    load = metabolism.toxin_load(metabolism.COMPOSITION[kind], metabolism.FOOD_MASS[kind])
    return metabolism.toxin_penalty(load * potency, tolerance)


def mean_dose(potency: float, tolerances: list[float], kind: str = "raw_fruit") -> float:
    return sum(dose(potency, t, kind) for t in tolerances) / len(tolerances)


def solve_dose_matched_scale(
    target_dose: float,
    tolerances: list[float],
    kind: str = "raw_fruit",
    tolerance_eps: float = 1e-12,
    max_iterations: int = 200,
) -> float:
    """Smallest constant potency whose mean dose equals `target_dose`.

    mean_dose is non-decreasing in potency, so a bisection on [0, 1] is exact up to
    `tolerance_eps`. Raises if the target is unreachable at full potency -- which
    would mean the variable arm delivers more dose than a constant arm ever can,
    and the arm design has to be rethought rather than fudged.
    """
    if target_dose <= 0.0:
        return 0.0
    ceiling = mean_dose(1.0, tolerances, kind)
    if target_dose > ceiling + tolerance_eps:
        raise ValueError(
            f"target dose {target_dose:.6f} exceeds the maximum reachable dose "
            f"{ceiling:.6f} at potency 1.0 -- no constant-potency arm can match it"
        )
    low, high = 0.0, 1.0
    for _ in range(max_iterations):
        mid = (low + high) / 2.0
        if mean_dose(mid, tolerances, kind) < target_dose:
            low = mid
        else:
            high = mid
        if high - low < tolerance_eps:
            break
    return (low + high) / 2.0


def encounter_age_weights(summary: dict, kind: str = "raw_fruit") -> Counter:
    """Age-bin -> encounter count, read from the P3 telemetry in a run dump."""
    weights: Counter = Counter()
    for row in summary.get("agent_diet_summary") or []:
        for key, counts in (row.get("encounters_by_kind_age") or {}).items():
            row_kind, _, bin_text = key.partition("@")
            if row_kind != kind:
                continue
            weights[int(bin_text)] += int(counts.get("seen", 0))
    return weights


def founder_tolerances(summary: dict) -> list[float]:
    """toxin_tolerance of every observed founder (generation 0)."""
    values = [
        float(row["toxin_tolerance"])
        for row in summary.get("agent_diet_summary") or []
        if row.get("generation") == 0 and row.get("toxin_tolerance") is not None
    ]
    return values


def target_dose_from_weights(
    weights: Counter,
    tolerances: list[float],
    detox_ticks: int,
    window_start: int,
    window_end: int,
    age_bin: int,
    kind: str = "raw_fruit",
) -> float:
    total = sum(weights.values())
    if not total:
        raise ValueError("no encounters found -- run the pilot with --encounter-telemetry")
    accumulated = 0.0
    for bin_index, count in weights.items():
        # Mid-point of the bin: with the default bin size of 1 this is the exact age.
        age = bin_index * age_bin + (age_bin - 1) / 2.0
        potency = metabolism.toxin_age_potency(age, detox_ticks, window_start, window_end)
        accumulated += count * mean_dose(potency, tolerances, kind)
    return accumulated / total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dump", default=None, help="A2 pilot summary dump (JSON) with P3 telemetry")
    parser.add_argument("--detox-ticks", type=int, default=0, help="the A2 arm's --toxin-detox-ticks")
    parser.add_argument("--safe-window-start", type=int, default=0)
    parser.add_argument("--safe-window-end", type=int, default=0)
    parser.add_argument("--age-bin", type=int, default=1, help="the pilot's --encounter-age-bin")
    parser.add_argument("--kind", default="raw_fruit")
    parser.add_argument("--uniform-ages", default=None,
                        help="fallback when no dump is available: START:END, ages weighted equally")
    parser.add_argument("--tolerance", type=float, default=None,
                        help="single toxin_tolerance to assume when no dump is available")
    args = parser.parse_args()

    if args.dump:
        summary = json.loads(Path(args.dump).read_text(encoding="utf-8"))
        weights = encounter_age_weights(summary, args.kind)
        tolerances = founder_tolerances(summary)
        if not tolerances:
            if args.tolerance is None:
                raise SystemExit(
                    "the dump has no founder toxin_tolerance values: rerun the pilot with "
                    "--agent-outcome-telemetry, or pass --tolerance"
                )
            tolerances = [args.tolerance]
        source = f"dump {args.dump}"
    elif args.uniform_ages:
        start_text, _, end_text = args.uniform_ages.partition(":")
        weights = Counter({age: 1 for age in range(int(start_text), int(end_text))})
        tolerances = [args.tolerance if args.tolerance is not None else 0.2]
        source = f"uniform ages {args.uniform_ages}"
    else:
        raise SystemExit("pass --dump or --uniform-ages")

    target = target_dose_from_weights(
        weights, tolerances, args.detox_ticks, args.safe_window_start,
        args.safe_window_end, args.age_bin, args.kind,
    )
    scale = solve_dose_matched_scale(target, tolerances, args.kind)

    total_potency = sum(
        count * metabolism.toxin_age_potency(
            bin_index * args.age_bin + (args.age_bin - 1) / 2.0,
            args.detox_ticks, args.safe_window_start, args.safe_window_end,
        )
        for bin_index, count in weights.items()
    )
    mean_potency = total_potency / sum(weights.values())

    report = {
        "source": source,
        "kind": args.kind,
        "encounters": sum(weights.values()),
        "distinct_age_bins": len(weights),
        "bodies_in_tolerance_sample": len(tolerances),
        "mean_toxin_tolerance": round(sum(tolerances) / len(tolerances), 6),
        "mean_potency_naive": round(mean_potency, 6),
        "mean_dose_if_matched_on_potency": round(mean_dose(mean_potency, tolerances, args.kind), 8),
        "target_mean_dose_per_encounter": round(target, 8),
        "dose_matched_potency_scale": round(scale, 6),
    }
    naive = report["mean_dose_if_matched_on_potency"]
    report["under_dosing_factor_if_matched_on_potency"] = (
        round(target / naive, 3) if naive > 0 else None
    )
    print(json.dumps(report, indent=2))
    print(f"\n  use:  --toxin-potency-scale {scale:.6f}   (arm A3)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
