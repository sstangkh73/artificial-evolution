# -*- coding: utf-8 -*-
"""Build and verify the publication release inventory.

The inventory is intentionally narrower than a repository snapshot. It contains
the files needed to inspect the reported analyses, reproduce the confirmatory
runs, and audit the manuscript's quantitative claims. Submission-administration
files and unrelated experiments are excluded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


PUBLICATION = Path("reports/publication_value_of_information_2026-09-13")
INVENTORY = PUBLICATION / "supplement/publication_release_inventory.json"
CHECKSUMS = PUBLICATION / "supplement/publication_release_checksums.sha256"
CORE_CHECKSUMS = PUBLICATION / "confirmatory/checksums.sha256"

FROZEN_COMMIT = "3f1af32f9e37655ed9bee5462526921eff226c8a"
FROZEN_TAG = "prereg-resource-age-2026-09-14"

MANUSCRIPT_FILES = (
    "LICENSE",
    "LICENSE-DATA.md",
    str(PUBLICATION / "README.th.md"),
    str(PUBLICATION / "AI_USE_LOG.md"),
    str(PUBLICATION / "manuscript_v0.en.md"),
    str(PUBLICATION / "ODD_MODEL_DESCRIPTION_DRAFT.en.md"),
    str(PUBLICATION / "references.bib"),
)

PREREGISTRATION_FILES = (
    "reports/prereg/E6_representation_payoff_spec.json",
    "reports/prereg/T2_RB_replication_spec.json",
    "reports/prereg/E6_representation_payoff_SMOKE_spec.json",
    "reports/prereg/T2_RB_replication_SMOKE_spec.json",
    "reports/prereg/preregistration_manifest_2026-09-14.json",
)

REPRODUCTION_SCRIPTS = (
    "scripts/analyze_e6_representation_payoff.py",
    "scripts/analyze_e_series.py",
    "scripts/analyze_selection_differential.py",
    "scripts/analyze_t2rb_replication.py",
    "scripts/build_confirmatory_checksums.py",
    "scripts/build_preregistration_manifest.py",
    "scripts/export_experiment_parameter_matrix.py",
    "scripts/food_value_study_driver.py",
    "scripts/plot_publication_core_studies.py",
    "scripts/plot_resource_age_confirmatory.py",
    "scripts/run_e_series.py",
    "scripts/run_long_emergence_watch.py",
    "scripts/summarize_resource_age_confirmatory.py",
    "scripts/validate_e_series_batch.py",
    "scripts/verify_reproduction_smoke.py",
    "scripts/build_publication_release_inventory.py",
)

REPRODUCTION_TESTS = (
    "tests/test_aging_physics.py",
    "tests/test_build_confirmatory_checksums.py",
    "tests/test_demographic_telemetry.py",
    "tests/test_e6_representation_payoff_analysis.py",
    "tests/test_metabolism.py",
    "tests/test_plot_resource_age_confirmatory.py",
    "tests/test_publication_journal_readiness_artifacts.py",
    "tests/test_publication_statistics.py",
    "tests/test_seed_independence.py",
    "tests/test_summarize_resource_age_confirmatory.py",
    "tests/test_t2rb_replication_analysis.py",
    "tests/test_toxin.py",
    "tests/test_validate_e_series_batch.py",
)

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def require_files(root: Path, paths: tuple[str, ...]) -> list[Path]:
    files = []
    for name in paths:
        path = root / name
        if not path.is_file():
            raise FileNotFoundError(path)
        files.append(path)
    return files


def files_under(root: Path, directory: str, suffixes: tuple[str, ...] | None = None) -> list[Path]:
    base = root / directory
    if not base.is_dir():
        raise FileNotFoundError(base)
    files = [path for path in base.rglob("*") if path.is_file()]
    if suffixes is not None:
        files = [path for path in files if path.suffix.lower() in suffixes]
    return sorted(files, key=lambda path: rel(path, root))


def collect_bundles(root: Path) -> list[dict[str, object]]:
    raw_e6 = files_under(
        root, "data/confirmatory_resource_age_2026-09-14/e6", (".json",)
    )
    raw_t2rb = files_under(
        root, "data/confirmatory_resource_age_2026-09-14/t2rb", (".json",)
    )
    if len(raw_e6) != 450 or len(raw_t2rb) != 150:
        raise ValueError(
            f"expected 450 E6 and 150 T2-RB raw dumps; found {len(raw_e6)} and {len(raw_t2rb)}"
        )

    confirmatory = files_under(root, str(PUBLICATION / "confirmatory"))
    supplements = [
        path
        for path in files_under(root, str(PUBLICATION / "supplement"))
        if path.resolve() not in {(root / INVENTORY).resolve(), (root / CHECKSUMS).resolve()}
    ]

    model_code = []
    for directory in ("agents", "world", "simulation"):
        model_code.extend(files_under(root, directory, (".py",)))
    model_code.extend(require_files(root, ("main.py", "requirements.txt")))
    model_code.extend(require_files(root, REPRODUCTION_SCRIPTS))
    model_code.extend(require_files(root, REPRODUCTION_TESTS))

    bundles = [
        {
            "id": "confirmatory_raw_data",
            "license": "CC-BY-4.0",
            "purpose": "One raw JSON dump per registered arm and seed for E6 and T2-RB.",
            "files": raw_e6 + raw_t2rb,
        },
        {
            "id": "derived_evidence",
            "license": "CC-BY-4.0",
            "purpose": "Validated summaries, analyses, source tables, figures, and the original 616-entry core checksum manifest.",
            "files": confirmatory,
        },
        {
            "id": "manuscript_and_methods",
            "license": "CC-BY-4.0",
            "purpose": "Manuscript, model description, references, disclosure log, parameter/state/version documentation, and reproduction records.",
            "files": require_files(root, MANUSCRIPT_FILES) + supplements,
        },
        {
            "id": "frozen_preregistration",
            "license": "CC-BY-4.0",
            "purpose": "Frozen confirmatory and smoke specifications plus the preregistration manifest.",
            "files": require_files(root, PREREGISTRATION_FILES),
        },
        {
            "id": "code_and_tests",
            "license": "MIT",
            "purpose": "Focal model, experiment, analysis, figure, inventory, and regression-test code needed for reproduction and audit.",
            "files": model_code,
        },
    ]

    seen: dict[str, str] = {}
    for bundle in bundles:
        unique: list[Path] = []
        for path in bundle["files"]:
            relative = rel(path, root)
            if relative in seen:
                raise ValueError(
                    f"duplicate release path {relative!r} in {seen[relative]!r} and {bundle['id']!r}"
                )
            seen[relative] = str(bundle["id"])
            unique.append(path)
        bundle["files"] = sorted(unique, key=lambda path: rel(path, root))
    return bundles


def parse_checksum_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as exc:
            raise ValueError(f"malformed checksum line {line_number}: {line!r}") from exc
        if not SHA256_RE.fullmatch(digest):
            raise ValueError(f"invalid SHA-256 on line {line_number}: {digest!r}")
        if relative in entries:
            raise ValueError(f"duplicate checksum path on line {line_number}: {relative!r}")
        entries[relative] = digest
    return entries


def verify_core_manifest(root: Path) -> dict[str, object]:
    manifest_path = root / CORE_CHECKSUMS
    entries = parse_checksum_manifest(manifest_path)
    raw_e6 = [path for path in entries if path.startswith("data/confirmatory_resource_age_2026-09-14/e6/")]
    raw_t2rb = [path for path in entries if path.startswith("data/confirmatory_resource_age_2026-09-14/t2rb/")]
    derived = [path for path in entries if path not in set(raw_e6 + raw_t2rb)]
    counts = {"raw_e6": len(raw_e6), "raw_t2rb": len(raw_t2rb), "derived": len(derived)}
    expected = {"raw_e6": 450, "raw_t2rb": 150, "derived": 16}
    if counts != expected:
        raise ValueError(f"core checksum category counts differ: expected {expected}, found {counts}")
    for relative, expected_digest in entries.items():
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        actual_digest = sha256_file(path)
        if actual_digest != expected_digest:
            raise ValueError(
                f"core checksum mismatch for {relative}: expected {expected_digest}, found {actual_digest}"
            )
    return {
        "manifest_path": CORE_CHECKSUMS.as_posix(),
        "entries": len(entries),
        "category_counts": counts,
        "all_entries_verified": True,
    }


def build_inventory(root: Path) -> dict[str, object]:
    core = verify_core_manifest(root)
    bundles = collect_bundles(root)
    serial_bundles = []
    total_bytes = 0
    total_files = 0
    for bundle in bundles:
        entries = []
        for path in bundle["files"]:
            size = path.stat().st_size
            entries.append({"path": rel(path, root), "bytes": size, "sha256": sha256_file(path)})
            total_bytes += size
            total_files += 1
        serial_bundles.append(
            {
                "id": bundle["id"],
                "license": bundle["license"],
                "purpose": bundle["purpose"],
                "file_count": len(entries),
                "total_bytes": sum(entry["bytes"] for entry in entries),
                "files": entries,
            }
        )
    return {
        "schema_version": 1,
        "inventory_date": "2026-09-14",
        "title": "Resource-age information publication release inventory",
        "path_convention": "POSIX-style paths relative to the repository root",
        "confirmatory_run_revision": FROZEN_COMMIT,
        "confirmatory_preregistration_tag": FROZEN_TAG,
        "public_archive": {
            "status": "PENDING_AUTHOR_DEPOSIT",
            "doi": None,
            "landing_page_url": None,
            "release_commit_or_tag": None,
        },
        "core_confirmatory_manifest_verification": core,
        "summary": {"bundle_count": len(serial_bundles), "file_count": total_files, "total_bytes": total_bytes},
        "bundles": serial_bundles,
    }


def checksum_lines(inventory: dict[str, object]) -> list[str]:
    entries = []
    for bundle in inventory["bundles"]:
        entries.extend(bundle["files"])
    return [f"{entry['sha256']}  {entry['path']}" for entry in sorted(entries, key=lambda item: item["path"])]


def write_inventory(root: Path) -> dict[str, object]:
    inventory = build_inventory(root)
    inventory_path = root / INVENTORY
    checksums_path = root / CHECKSUMS
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    checksums_path.write_text("\n".join(checksum_lines(inventory)) + "\n", encoding="utf-8", newline="\n")
    return inventory


def verify_inventory(root: Path) -> dict[str, int]:
    verify_core_manifest(root)
    inventory_path = root / INVENTORY
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    expected_paths = {
        rel(path, root)
        for bundle in collect_bundles(root)
        for path in bundle["files"]
    }
    recorded_entries = [entry for bundle in inventory["bundles"] for entry in bundle["files"]]
    recorded_paths = {entry["path"] for entry in recorded_entries}
    if len(recorded_paths) != len(recorded_entries):
        raise ValueError("release inventory contains duplicate paths")
    if recorded_paths != expected_paths:
        missing = sorted(expected_paths - recorded_paths)
        extra = sorted(recorded_paths - expected_paths)
        raise ValueError(f"release scope differs; missing={missing}, extra={extra}")
    for entry in recorded_entries:
        path = root / entry["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        size = path.stat().st_size
        digest = sha256_file(path)
        if size != entry["bytes"] or digest != entry["sha256"]:
            raise ValueError(
                f"release mismatch for {entry['path']}: expected {entry['bytes']} bytes/{entry['sha256']}, "
                f"found {size} bytes/{digest}"
            )
    expected_checksum_text = "\n".join(checksum_lines(inventory)) + "\n"
    actual_checksum_text = (root / CHECKSUMS).read_text(encoding="utf-8")
    if actual_checksum_text != expected_checksum_text:
        raise ValueError(f"{CHECKSUMS.as_posix()} does not match the JSON inventory")
    return {
        "bundles": len(inventory["bundles"]),
        "files": len(recorded_entries),
        "bytes": sum(entry["bytes"] for entry in recorded_entries),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if args.write:
        inventory = write_inventory(root)
        print(
            f"wrote {inventory['summary']['file_count']} entries in {inventory['summary']['bundle_count']} bundles "
            f"({inventory['summary']['total_bytes']} bytes)"
        )
    else:
        result = verify_inventory(root)
        print(f"PASS: verified {result['files']} entries in {result['bundles']} bundles ({result['bytes']} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
