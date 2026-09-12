# -*- coding: utf-8 -*-
"""E3: the selection differential on toxin_tolerance, per arm and seed.

Reads the per-agent rows a run already writes and emits a runs-style JSON that
analyze_e_series.py can consume, so the selection metrics go through exactly the
same paired seed-level machinery as every other dependent variable.

Metrics per run (founders only, generation 0):

  selection_differential  S = mean tolerance of the longest-lived half of the
                          cohort minus the mean of the whole cohort. Using the
                          top half rather than "survivors at tick T" avoids a
                          cutoff that would itself depend on how long each arm's
                          agents happen to live.
  cov_tolerance_age       covariance between tolerance and age at death, the
                          continuous form of the same quantity and the one that
                          does not throw away half the cohort.
  beta_tolerance_age      that covariance divided by the variance in tolerance:
                          ticks of life per unit of tolerance, which is readable.
  cohort_tolerance_sd     the standing variation there was to select on. Zero
                          here means the run cannot answer the question at all,
                          rather than answering it in the negative.

N2, the cross-generation response, is reported only as the number of generations
that actually existed. With no births there is nothing to regress, and saying so
is the finding.

Usage:
    python scripts/analyze_selection_differential.py --runs reports/e3/E3_runs.json \
        --out reports/e3/E3_selection_runs.json
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path


def selection_metrics(summary: dict) -> dict:
    rows = [r for r in (summary.get("agent_diet_summary") or []) if r.get("generation") == 0]
    tolerances = [float(r["toxin_tolerance"]) for r in rows if r.get("toxin_tolerance") is not None]
    ages = [float(r["age"]) for r in rows if r.get("toxin_tolerance") is not None]
    generations = Counter(r.get("generation") for r in (summary.get("agent_diet_summary") or []))

    metrics: dict = {
        "founders": len(tolerances),
        "generations_observed": len([g for g in generations if g is not None]),
        "max_generation": max((g for g in generations if g is not None), default=None),
        "births": summary.get("births"),
        "cohort_tolerance_mean": None,
        "cohort_tolerance_sd": None,
        "selection_differential": None,
        "cov_tolerance_age": None,
        "beta_tolerance_age": None,
    }
    if len(tolerances) < 4:
        return metrics

    mean_tolerance = statistics.mean(tolerances)
    sd_tolerance = statistics.stdev(tolerances)
    metrics["cohort_tolerance_mean"] = round(mean_tolerance, 6)
    metrics["cohort_tolerance_sd"] = round(sd_tolerance, 6)
    if sd_tolerance <= 0.0:
        # No variation: S is zero by construction and means nothing. Leave the
        # metrics null so the run is dropped from the analysis with a named
        # reason, instead of contributing a spurious zero.
        metrics["reason"] = "no standing variation in toxin_tolerance"
        return metrics

    pairs = sorted(zip(ages, tolerances), reverse=True)
    top_half = pairs[: max(1, len(pairs) // 2)]
    metrics["selection_differential"] = round(
        statistics.mean([t for _, t in top_half]) - mean_tolerance, 6)

    mean_age = statistics.mean(ages)
    covariance = sum((t - mean_tolerance) * (a - mean_age)
                     for a, t in zip(ages, tolerances)) / (len(ages) - 1)
    metrics["cov_tolerance_age"] = round(covariance, 6)
    metrics["beta_tolerance_age"] = round(covariance / (sd_tolerance ** 2), 4)
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", required=True, help="the *_runs.json written by run_e_series.py")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.runs).read_text(encoding="utf-8"))
    rows = []
    for row in payload["rows"]:
        if row.get("error"):
            rows.append(row)
            continue
        summary = json.loads(Path(row["dump"]).read_text(encoding="utf-8"))
        merged = {k: row[k] for k in ("experiment", "arm", "seed", "dump", "flags") if k in row}
        merged.update(selection_metrics(summary))
        rows.append(merged)

    Path(args.out).write_text(
        json.dumps({"provenance": payload.get("provenance"), "rows": rows}, indent=2,
                   ensure_ascii=False), encoding="utf-8")

    by_arm: dict[str, list[float]] = {}
    for row in rows:
        if row.get("selection_differential") is not None:
            by_arm.setdefault(row["arm"], []).append(row["selection_differential"])
    for arm in sorted(by_arm):
        values = by_arm[arm]
        print(f"{arm}: S = {statistics.mean(values):+.5f} "
              f"(SD {statistics.stdev(values):.5f}, n = {len(values)})")
    generations = {row.get("max_generation") for row in rows}
    print(f"generations present across runs: {sorted(g for g in generations if g is not None)}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
