# -*- coding: utf-8 -*-
"""Validate an E-series batch before confirmatory analysis.

The runner records one row for every arm x seed cell and embeds the exact spec
and git provenance.  This script checks that the recorded batch is the complete
Cartesian design, has one usable primary outcome per cell, and came from one
clean, unchanged revision.  E6 additionally checks the realized fruit-energy
mapping frozen in its spec.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


REQUIRED_PROVENANCE = (
    "git_revision_start",
    "git_revision_end",
    "git_revision_changed_during_run",
    "git_tree_dirty_start",
    "git_tree_dirty_end",
    "failures",
)
FROZEN_STATUS = "PREREGISTERED_CONFIRMATORY_FROZEN"


def validate_payload(payload: dict) -> dict:
    provenance = payload.get("provenance") or {}
    spec = provenance.get("spec") or {}
    experiment = str(spec.get("experiment", ""))
    primary_metric = str(spec.get("primary_metric", ""))
    arms = set((spec.get("arms") or {}).keys())
    seeds = {int(seed) for seed in spec.get("seeds", [])}
    expected = {(arm, seed) for arm in arms for seed in seeds}

    rows = payload.get("rows") or []
    observed_cells: list[tuple[str, int]] = []
    malformed_rows: list[dict] = []
    failed_rows: list[dict] = []
    missing_outcomes: list[dict] = []
    for index, row in enumerate(rows):
        try:
            cell = (str(row["arm"]), int(row["seed"]))
        except (KeyError, TypeError, ValueError):
            malformed_rows.append({"row_index": index, "reason": "invalid arm or seed"})
            continue
        observed_cells.append(cell)
        if row.get("error"):
            failed_rows.append({"arm": cell[0], "seed": cell[1], "error": row["error"]})
        if primary_metric and row.get(primary_metric) is None:
            missing_outcomes.append({"arm": cell[0], "seed": cell[1], "metric": primary_metric})

    counts = Counter(observed_cells)
    observed = set(observed_cells)
    duplicate_cells = [
        {"arm": arm, "seed": seed, "count": count}
        for (arm, seed), count in sorted(counts.items()) if count > 1
    ]
    missing_cells = [
        {"arm": arm, "seed": seed} for arm, seed in sorted(expected - observed)
    ]
    unexpected_cells = [
        {"arm": arm, "seed": seed} for arm, seed in sorted(observed - expected)
    ]

    provenance_missing = [key for key in REQUIRED_PROVENANCE if key not in provenance]
    provenance_errors: list[str] = []
    if provenance.get("git_revision_start") != provenance.get("git_revision_end"):
        provenance_errors.append("start/end revisions differ")
    if provenance.get("git_revision_changed_during_run"):
        provenance_errors.append("revision changed during run")
    if provenance.get("git_tree_dirty_start"):
        provenance_errors.append("tree was dirty at batch start")
    if provenance.get("git_tree_dirty_end"):
        provenance_errors.append("tree was dirty at batch end")
    if provenance.get("failures"):
        provenance_errors.append("runner recorded failures")
    if provenance.get("runs") != len(rows):
        provenance_errors.append("provenance run count does not match rows")
    if provenance.get("experiment") != experiment:
        provenance_errors.append("provenance experiment does not match embedded spec")

    realized_energy_errors: list[dict] = []
    mapping = spec.get("realized_fruit_energy_by_prefix") or {}
    for row in rows:
        arm = str(row.get("arm", ""))
        prefix = arm.split("_", 1)[0]
        if prefix not in mapping:
            continue
        observed_energy = row.get("realized_gross_fruit_energy")
        expected_energy = float(mapping[prefix])
        if observed_energy is None or float(observed_energy) != expected_energy:
            realized_energy_errors.append({
                "arm": arm,
                "seed": row.get("seed"),
                "expected": expected_energy,
                "observed": observed_energy,
            })

    errors = {
        "missing_spec_fields": [
            field for field, value in (
                ("experiment", experiment),
                ("primary_metric", primary_metric),
                ("arms", arms),
                ("seeds", seeds),
            ) if not value
        ],
        "spec_status_errors": (
            ["embedded experiment spec is still marked DRAFT"]
            if "DRAFT" in str(spec.get("status", "")).upper() else []
        ),
        "provenance_missing": provenance_missing,
        "provenance_errors": provenance_errors,
        "malformed_rows": malformed_rows,
        "failed_rows": failed_rows,
        "missing_outcomes": missing_outcomes,
        "duplicate_cells": duplicate_cells,
        "missing_cells": missing_cells,
        "unexpected_cells": unexpected_cells,
        "realized_energy_errors": realized_energy_errors,
    }
    valid = not any(errors.values()) and len(rows) == len(expected)
    confirmatory_eligible = valid and spec.get("status") == FROZEN_STATUS
    return {
        "validator": "E-series batch integrity v1",
        "experiment": experiment,
        "primary_metric": primary_metric,
        "expected_runs": len(expected),
        "observed_rows": len(rows),
        "valid": valid,
        "frozen_confirmatory_spec": spec.get("status") == FROZEN_STATUS,
        "confirmatory_eligible": confirmatory_eligible,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    payload = json.loads(Path(args.runs).read_text(encoding="utf-8"))
    report = validate_payload(payload)
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"{report['experiment']}: {'VALID' if report['valid'] else 'INVALID'} "
        f"({report['observed_rows']}/{report['expected_runs']} rows); wrote {args.out}"
    )
    return 0 if report["valid"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
