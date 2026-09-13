# -*- coding: utf-8 -*-
"""Guarded analysis for the preregistered T2 R-B replication."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_e_series import contrast

REQUIRED_ARMS = ("A2", "A3O", "A3R")
REQUIRED_PROVENANCE = (
    "git_revision_start",
    "git_revision_end",
    "git_revision_changed_during_run",
    "git_tree_dirty_start",
    "git_tree_dirty_end",
    "failures",
)
FROZEN_STATUS = "PREREGISTERED_CONFIRMATORY_FROZEN"


def analyze_payload(payload: dict, metric: str = "founder_mean_followup_ticks") -> dict:
    provenance = payload.get("provenance") or {}
    spec = provenance.get("spec") or {}
    frozen_confirmatory_spec = spec.get("status") == FROZEN_STATUS
    expected_seeds = {int(seed) for seed in spec.get("seeds", [])}
    by_arm: dict[str, dict[int, float]] = {arm: {} for arm in REQUIRED_ARMS}
    unusable_rows: list[dict] = []

    for row in payload.get("rows", []):
        arm = str(row.get("arm", ""))
        if arm not in by_arm:
            continue
        value = row.get(metric)
        if row.get("error") or value is None:
            unusable_rows.append({
                "arm": arm,
                "seed": row.get("seed"),
                "reason": "run failed" if row.get("error") else f"no {metric}",
            })
            continue
        by_arm[arm][int(row["seed"])] = float(value)

    observed_seeds = set().union(*(set(rows) for rows in by_arm.values()))
    missing_by_arm = {
        arm: sorted(expected_seeds - set(by_arm[arm]))
        for arm in REQUIRED_ARMS
        if expected_seeds - set(by_arm[arm])
    }
    unexpected_seeds = sorted(observed_seeds - expected_seeds)
    provenance_complete = all(key in provenance for key in REQUIRED_PROVENANCE)
    design_complete = bool(expected_seeds) and not (
        missing_by_arm or unexpected_seeds or unusable_rows
    )
    confirmatory_eligible = frozen_confirmatory_spec and provenance_complete and design_complete and not (
        provenance.get("git_tree_dirty")
        or provenance.get("git_tree_dirty_start")
        or provenance.get("git_tree_dirty_end")
        or provenance.get("git_revision_changed_during_run")
        or provenance.get("failures")
    )

    return {
        "analysis": "T2 R-B replication",
        "primary_metric": metric,
        "inferential_unit": "seed/run",
        "provenance": provenance,
        "provenance_complete": provenance_complete,
        "frozen_confirmatory_spec": frozen_confirmatory_spec,
        "design_complete": design_complete,
        "confirmatory_provenance_eligible": confirmatory_eligible,
        "expected_seed_count": len(expected_seeds),
        "missing_by_arm": missing_by_arm,
        "unexpected_seeds": unexpected_seeds,
        "unusable_rows": unusable_rows,
        "primary": contrast(by_arm, "A2", "A3R", metric),
        "direct_replication_secondary": contrast(by_arm, "A2", "A3O", metric),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", required=True)
    parser.add_argument("--metric", default="founder_mean_followup_ticks")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.runs).read_text(encoding="utf-8"))
    analysis = analyze_payload(payload, metric=args.metric)
    Path(args.out).write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    primary = analysis["primary"]["paired_difference"]
    print(
        f"A2-A3R: n={analysis['primary']['n_pairs']}, "
        f"mean={primary['mean']}, 95% CI "
        f"{primary['t_ci95']['low']} to {primary['t_ci95']['high']}, "
        f"{primary['method']} p={primary['p']}"
    )
    print(f"wrote {args.out}")
    return 0 if analysis["confirmatory_provenance_eligible"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
