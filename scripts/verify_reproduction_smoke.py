# -*- coding: utf-8 -*-
"""Verify a fresh E6/T2-RB reproduction smoke against frozen signatures."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


EXCLUDED_ROW_FIELDS = {"dump", "wall_seconds"}
FOCAL_CODE_PATHS = (
    "agents/agent.py",
    "agents/body.py",
    "world/environment.py",
    "world/metabolism.py",
    "scripts/run_long_emergence_watch.py",
    "scripts/food_value_study_driver.py",
    "scripts/run_e_series.py",
)


def stable_rows(payload: dict) -> list[dict]:
    rows = [
        {key: value for key, value in row.items() if key not in EXCLUDED_ROW_FIELDS}
        for row in payload.get("rows", [])
    ]
    return sorted(rows, key=lambda row: (str(row.get("arm")), int(row.get("seed", -1))))


def rows_hash(rows: list[dict]) -> str:
    serialized = json.dumps(
        rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def focal_code_matches(repo_root: Path, frozen_revision: str, run_revision: str) -> bool:
    completed = subprocess.run(
        ["git", "diff", "--quiet", f"{frozen_revision}..{run_revision}", "--", *FOCAL_CODE_PATHS],
        cwd=repo_root,
    )
    return completed.returncode == 0


def verify_one(repo_root: Path, path: Path, expected: dict, frozen_revision: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    provenance = payload.get("provenance", {})
    rows = stable_rows(payload)
    failures: list[str] = []
    run_revision = str(provenance.get("git_revision_start") or provenance.get("git_revision") or "")
    if not run_revision or provenance.get("git_revision_end") != run_revision:
        failures.append("run revision missing or changed during batch")
    if provenance.get("git_tree_dirty_start") is not False or provenance.get("git_tree_dirty_end") is not False:
        failures.append("tracked tree was dirty")
    if not focal_code_matches(repo_root, frozen_revision, run_revision):
        failures.append("focal code differs from frozen revision")
    if len(rows) != int(expected["row_count"]):
        failures.append(f"row count {len(rows)} != {expected['row_count']}")
    if provenance.get("experiment") != expected["experiment"] or any(
        row.get("experiment") != expected["experiment"] for row in rows
    ):
        failures.append("experiment identifier differs")
    observed_arms = sorted(str(row.get("arm")) for row in rows)
    if observed_arms != sorted(expected["arms"]):
        failures.append("arm set differs")
    if sorted({int(row.get("seed", -1)) for row in rows}) != sorted(expected["seeds"]):
        failures.append("seed set differs")
    if any(int(row.get("requested_ticks", -1)) != int(expected["ticks"]) for row in rows):
        failures.append("requested horizon differs")
    if any(row.get("error") or row.get("reused") is not False for row in rows):
        failures.append("a row failed or reused an existing dump")
    observed_hash = rows_hash(rows)
    if observed_hash != expected["normalized_rows_sha256"]:
        failures.append("normalized outcome signature differs")
    return {
        "path": str(path),
        "run_revision": run_revision,
        "focal_code_matches_frozen": focal_code_matches(repo_root, frozen_revision, run_revision),
        "rows": len(rows),
        "normalized_rows_sha256": observed_hash,
        "expected_sha256": expected["normalized_rows_sha256"],
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--e6-runs", type=Path, required=True)
    parser.add_argument("--t2-runs", type=Path, required=True)
    parser.add_argument(
        "--expected",
        type=Path,
        default=Path("reports/publication_value_of_information_2026-09-13/supplement/reproduction_smoke_expected.json"),
    )
    parser.add_argument("--out", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    expected = json.loads(args.expected.read_text(encoding="utf-8"))
    frozen_revision = expected["frozen_revision"]
    report = {
        "schema_version": 1,
        "frozen_revision": frozen_revision,
        "excluded_row_fields": sorted(EXCLUDED_ROW_FIELDS),
        "checks": {
            "e6": verify_one(repo_root, args.e6_runs, expected["datasets"]["e6"], frozen_revision),
            "t2rb": verify_one(repo_root, args.t2_runs, expected["datasets"]["t2rb"], frozen_revision),
        },
    }
    report["status"] = (
        "PASS" if all(check["status"] == "PASS" for check in report["checks"].values()) else "FAIL"
    )
    output = json.dumps(report, indent=2, ensure_ascii=False)
    print(output)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output + "\n", encoding="utf-8", newline="\n")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
