# -*- coding: utf-8 -*-
"""Freeze the pre-revision manuscript and confirmatory-data baseline.

The generated manifest is an audit artifact.  It never modifies the archived
confirmatory package or any raw dump.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


PUBLICATION = Path("reports/publication_value_of_information_2026-09-13")
RAW_ROOT = Path("data/confirmatory_resource_age_2026-09-14")
CHECKSUMS = PUBLICATION / "confirmatory/checksums.sha256"
BASELINE_TARGETS = (
    PUBLICATION / "manuscript_v0.en.md",
    PUBLICATION / "submission/manuscript_initial_submission_draft.pdf",
    PUBLICATION / "confirmatory/e6/E6_analysis.json",
    PUBLICATION / "confirmatory/e6/E6_secondary_and_mechanism.json",
    PUBLICATION / "confirmatory/t2rb/T2RB_analysis.json",
    PUBLICATION / "confirmatory/figures",
)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def parse_checksum_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as exc:
            raise ValueError(f"malformed checksum line {line_number}: {line!r}") from exc
        if relative in entries:
            raise ValueError(f"duplicate checksum path: {relative}")
        entries[relative] = digest
    return entries


def collect_targets(root: Path) -> list[Path]:
    files: set[Path] = set()
    for target in BASELINE_TARGETS:
        path = root / target
        if not path.exists():
            raise FileNotFoundError(path)
        if path.is_file():
            files.add(path)
        else:
            files.update(candidate for candidate in path.rglob("*") if candidate.is_file())
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def build_manifest(root: Path) -> dict:
    root = root.resolve()
    archived = parse_checksum_manifest(root / CHECKSUMS)
    raw_files = {
        "E6": sorted((root / RAW_ROOT / "e6").glob("*.json")),
        "T2RB": sorted((root / RAW_ROOT / "t2rb").glob("*.json")),
    }
    raw_verification: dict[str, dict] = {}
    all_raw_entries: list[dict] = []
    for experiment, files in raw_files.items():
        mismatches: list[dict] = []
        missing_from_archive: list[str] = []
        for path in files:
            relative = path.relative_to(root).as_posix()
            actual = sha256_file(path)
            expected = archived.get(relative)
            if expected is None:
                missing_from_archive.append(relative)
            elif actual != expected:
                mismatches.append({"path": relative, "expected": expected, "actual": actual})
            all_raw_entries.append({"experiment": experiment, "path": relative, "sha256": actual})
        raw_verification[experiment] = {
            "observed_files": len(files),
            "expected_files": 450 if experiment == "E6" else 150,
            "missing_from_archived_checksum_manifest": missing_from_archive,
            "checksum_mismatches": mismatches,
            "passes": (
                len(files) == (450 if experiment == "E6" else 150)
                and not missing_from_archive
                and not mismatches
            ),
        }

    baseline_files = []
    for path in collect_targets(root):
        baseline_files.append({
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })

    scoped_status = git(
        root,
        "status",
        "--short",
        "--",
        PUBLICATION.as_posix(),
        RAW_ROOT.as_posix(),
        "scripts",
        "tests",
    ).splitlines()
    return {
        "manifest": "red-team revision baseline v1",
        "revision_plan": (PUBLICATION / "REVISION_PLAN_FROM_REDTEAM_2026-09-15.th.md").as_posix(),
        "git": {
            "head": git(root, "rev-parse", "HEAD"),
            "describe": git(root, "describe", "--always", "--dirty"),
            "tags_at_head": git(root, "tag", "--points-at", "HEAD").splitlines(),
            "scoped_status": scoped_status,
        },
        "raw_data": raw_verification,
        "raw_files": all_raw_entries,
        "baseline_files": baseline_files,
        "gate_0_passes": all(item["passes"] for item in raw_verification.values()),
        "immutability_note": (
            "This manifest records pre-revision bytes. Derived revision artifacts are written "
            "separately; raw dumps and archived confirmatory outputs are not overwritten."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    output = Path(args.out)
    if not output.is_absolute():
        output = root / output
    result = build_manifest(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"wrote {output}; E6={result['raw_data']['E6']['observed_files']}, "
        f"T2RB={result['raw_data']['T2RB']['observed_files']}, "
        f"gate_0={'PASS' if result['gate_0_passes'] else 'FAIL'}"
    )
    return 0 if result["gate_0_passes"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
