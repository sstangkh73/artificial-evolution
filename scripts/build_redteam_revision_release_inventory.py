"""Build and verify the Red Team revision artifact inventory.

The archived 616-entry confirmatory manifest remains an immutable historical
record.  This inventory verifies the 600 raw dumps against the revision
baseline, then hashes only the derived, manuscript, figure, and code artifacts
created or changed during the Red Team revision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLICATION = ROOT / "reports/publication_value_of_information_2026-09-13"
REVISION = PUBLICATION / "revision_2026-09-15"
BASELINE = REVISION / "baseline_manifest.json"
INVENTORY = REVISION / "revision_release_inventory.json"
CHECKSUMS = REVISION / "revision_release_checksums.sha256"

EXPLICIT_FILES = (
    PUBLICATION / "manuscript_v0.en.md",
    PUBLICATION / "references.bib",
    PUBLICATION / "AI_USE_LOG.md",
    PUBLICATION / "LITERATURE_EVIDENCE_MATRIX_2026-09-14.md",
    PUBLICATION / "ODD_MODEL_DESCRIPTION_DRAFT.en.md",
    PUBLICATION / "README.th.md",
    PUBLICATION / "cover_letter_draft.en.md",
    PUBLICATION / "SUBMISSION_CHECKLIST_2026-09-14.th.md",
    PUBLICATION / "supplement/PUBLIC_ARCHIVE_MANIFEST.en.md",
    PUBLICATION / "supplement/MECHANISM_TABLES.en.md",
    PUBLICATION / "submission/manuscript_initial_submission_draft.pdf",
    PUBLICATION / "submission/manuscript_submission_audit.json",
    ROOT / "scripts/analyze_redteam_mechanisms.py",
    ROOT / "scripts/audit_submission_manuscript.py",
    ROOT / "scripts/build_redteam_revision_baseline.py",
    ROOT / "scripts/build_redteam_revision_release_inventory.py",
    ROOT / "scripts/build_submission_manuscript.py",
    ROOT / "scripts/plot_publication_core_studies.py",
    ROOT / "scripts/plot_resource_age_confirmatory.py",
    ROOT / "scripts/render_redteam_revision_report.py",
    ROOT / "tests/test_audit_submission_manuscript.py",
    ROOT / "tests/test_plot_resource_age_confirmatory.py",
    ROOT / "tests/test_redteam_mechanism_analysis.py",
    ROOT / "tests/test_redteam_revision_release_inventory.py",
)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def verify_raw_baseline() -> dict[str, object]:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    rows = baseline["raw_files"]
    if len(rows) != 600:
        raise ValueError(f"expected 600 baseline raw files, found {len(rows)}")
    counts = {"E6": 0, "T2RB": 0}
    for row in rows:
        path = ROOT / row["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        observed = sha256_file(path)
        if observed != row["sha256"]:
            raise ValueError(
                f"raw baseline mismatch for {row['path']}: expected {row['sha256']}, found {observed}"
            )
        counts[row["experiment"]] += 1
    if counts != {"E6": 450, "T2RB": 150}:
        raise ValueError(f"raw baseline counts differ: {counts}")
    return {"status": "PASS", "file_count": len(rows), "counts": counts}


def collect_artifacts() -> list[Path]:
    excluded = {INVENTORY.resolve(), CHECKSUMS.resolve(), BASELINE.resolve()}
    paths = set(EXPLICIT_FILES)
    paths.update(path for path in REVISION.rglob("*") if path.is_file())
    paths.update(path for path in (PUBLICATION / "confirmatory/figures").glob("*") if path.is_file())
    paths.update(path for path in (PUBLICATION / "confirmatory/source_data").glob("*") if path.is_file())
    selected = sorted(
        (path.resolve() for path in paths if path.resolve() not in excluded),
        key=relative,
    )
    missing = [path for path in selected if not path.is_file()]
    if missing:
        raise FileNotFoundError(missing[0])
    return selected


def build_inventory() -> dict[str, object]:
    raw = verify_raw_baseline()
    files = [
        {"path": relative(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in collect_artifacts()
    ]
    return {
        "schema_version": 1,
        "inventory_date": "2026-09-16",
        "scope": "Red Team revision derived, manuscript, figure, audit, and code artifacts",
        "historical_confirmatory_manifest_modified": False,
        "raw_baseline_verification": raw,
        "status": "DRAFT_PENDING_AUTHOR_DECLARATIONS_AND_PUBLIC_DEPOSIT",
        "file_count": len(files),
        "total_bytes": sum(row["bytes"] for row in files),
        "files": files,
    }


def checksum_text(inventory: dict[str, object]) -> str:
    return "".join(f"{row['sha256']}  {row['path']}\n" for row in inventory["files"])


def write() -> dict[str, object]:
    inventory = build_inventory()
    INVENTORY.write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    CHECKSUMS.write_text(checksum_text(inventory), encoding="utf-8", newline="\n")
    return inventory


def verify() -> dict[str, object]:
    raw = verify_raw_baseline()
    recorded = json.loads(INVENTORY.read_text(encoding="utf-8"))
    expected_paths = {relative(path) for path in collect_artifacts()}
    rows = recorded["files"]
    recorded_paths = {row["path"] for row in rows}
    if len(recorded_paths) != len(rows):
        raise ValueError("revision inventory contains duplicate paths")
    if recorded_paths != expected_paths:
        raise ValueError(
            f"revision scope differs; missing={sorted(expected_paths - recorded_paths)}, "
            f"extra={sorted(recorded_paths - expected_paths)}"
        )
    for row in rows:
        path = ROOT / row["path"]
        observed_hash = sha256_file(path)
        if path.stat().st_size != row["bytes"] or observed_hash != row["sha256"]:
            raise ValueError(f"revision artifact mismatch for {row['path']}")
    if CHECKSUMS.read_text(encoding="utf-8") != checksum_text(recorded):
        raise ValueError("flat revision checksum file differs from JSON inventory")
    return {"raw": raw, "file_count": len(rows), "total_bytes": sum(row["bytes"] for row in rows)}


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.write:
        result = write()
        print(
            f"wrote {result['file_count']} revision artifacts ({result['total_bytes']} bytes); "
            f"raw baseline {result['raw_baseline_verification']['status']}"
        )
    else:
        result = verify()
        print(
            f"PASS: verified {result['file_count']} revision artifacts ({result['total_bytes']} bytes); "
            f"raw baseline {result['raw']['file_count']} files"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
