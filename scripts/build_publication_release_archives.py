# -*- coding: utf-8 -*-
"""Create and verify deterministic ZIP files for the publication deposit."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from build_publication_release_inventory import (
    CHECKSUMS,
    INVENTORY,
    sha256_file,
    verify_inventory,
)


DEFAULT_OUTPUT = Path("output/publication_release_2026-09-14")
PACKAGE_JSON = "package_artifacts.json"
PACKAGE_CHECKSUMS = "package_artifact_checksums.sha256"
DEPOSIT_README = "DEPOSIT_README.txt"
FIXED_ZIP_TIME = (2026, 9, 14, 0, 0, 0)


def zip_name(index: int, bundle_id: str) -> str:
    return f"{index:02d}_{bundle_id}.zip"


def write_bundle_zip(root: Path, destination: Path, entries: list[dict[str, object]]) -> None:
    with zipfile.ZipFile(
        destination,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        allowZip64=True,
    ) as archive:
        for entry in sorted(entries, key=lambda item: str(item["path"])):
            relative = str(entry["path"])
            info = zipfile.ZipInfo(relative, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            with (root / relative).open("rb") as source, archive.open(info, "w", force_zip64=True) as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)


def deposit_readme(inventory: dict[str, object]) -> str:
    rows = [
        "Resource-age information publication release",
        "",
        "STATUS: PENDING AUTHOR DEPOSIT. This directory is a locally verified upload package; it is not a public archive or DOI record.",
        "",
        f"Confirmatory run revision: {inventory['confirmatory_run_revision']}",
        f"Preregistration tag: {inventory['confirmatory_preregistration_tag']}",
        f"Release inventory: {inventory['summary']['file_count']} files in {inventory['summary']['bundle_count']} bundles",
        "",
        "Upload the five numbered ZIP files together with publication_release_inventory.json, publication_release_checksums.sha256, package_artifacts.json, package_artifact_checksums.sha256, and this README.",
        "",
        "Before citing a DOI, download every deposited artifact, run this package's verifier from the matching code release, and open every PDF plus representative JSON and CSV files.",
        "",
        "Licensing: source code is MIT; data, reports, and figures are CC BY 4.0. The licence files are included in the manuscript_and_methods ZIP.",
        "",
        "Do not describe the internal deterministic smoke check as independent reproduction. Add a second person's signed record only after that person completes the supplied protocol.",
    ]
    return "\n".join(rows) + "\n"


def package_files(output: Path, bundle_zip_names: list[str]) -> list[Path]:
    names = [
        *bundle_zip_names,
        INVENTORY.name,
        CHECKSUMS.name,
        DEPOSIT_README,
        PACKAGE_JSON,
    ]
    return [output / name for name in names]


def write_package(root: Path, output: Path) -> dict[str, object]:
    verify_inventory(root)
    inventory = json.loads((root / INVENTORY).read_text(encoding="utf-8"))
    output.mkdir(parents=True, exist_ok=True)
    bundle_records = []
    bundle_zip_names = []
    for index, bundle in enumerate(inventory["bundles"], 1):
        name = zip_name(index, bundle["id"])
        bundle_zip_names.append(name)
        destination = output / name
        write_bundle_zip(root, destination, bundle["files"])
        bundle_records.append(
            {
                "bundle_id": bundle["id"],
                "archive": name,
                "contained_file_count": bundle["file_count"],
                "contained_uncompressed_bytes": bundle["total_bytes"],
                "archive_bytes": destination.stat().st_size,
                "archive_sha256": sha256_file(destination),
            }
        )
    shutil.copyfile(root / INVENTORY, output / INVENTORY.name)
    shutil.copyfile(root / CHECKSUMS, output / CHECKSUMS.name)
    (output / DEPOSIT_README).write_text(deposit_readme(inventory), encoding="utf-8", newline="\n")
    package = {
        "schema_version": 1,
        "package_date": "2026-09-14",
        "status": "PENDING_AUTHOR_DEPOSIT",
        "source_inventory": INVENTORY.name,
        "source_release_file_count": inventory["summary"]["file_count"],
        "archives": bundle_records,
    }
    (output / PACKAGE_JSON).write_text(
        json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    artifacts = package_files(output, bundle_zip_names)
    lines = [f"{sha256_file(path)}  {path.name}" for path in sorted(artifacts, key=lambda path: path.name)]
    (output / PACKAGE_CHECKSUMS).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return package


def digest_stream(stream, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    while chunk := stream.read(chunk_size):
        digest.update(chunk)
    return digest.hexdigest()


def parse_flat_checksums(path: Path) -> dict[str, str]:
    entries = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            digest, name = line.split("  ", 1)
        except ValueError as exc:
            raise ValueError(f"malformed package checksum line {line_number}") from exc
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError(f"invalid SHA-256 on package checksum line {line_number}")
        if name in entries:
            raise ValueError(f"duplicate package artifact {name!r}")
        entries[name] = digest
    return entries


def verify_package(root: Path, output: Path) -> dict[str, int]:
    verify_inventory(root)
    inventory = json.loads((root / INVENTORY).read_text(encoding="utf-8"))
    package = json.loads((output / PACKAGE_JSON).read_text(encoding="utf-8"))
    bundles = {bundle["id"]: bundle for bundle in inventory["bundles"]}
    expected_zip_names = []
    archive_records = package.get("archives", [])
    if len(archive_records) != len(bundles):
        raise ValueError("package archive count differs from release inventory")
    verified_members = 0
    for record in archive_records:
        bundle = bundles.get(record["bundle_id"])
        if bundle is None:
            raise ValueError(f"unknown bundle in package: {record['bundle_id']!r}")
        archive_path = output / record["archive"]
        expected_zip_names.append(record["archive"])
        if sha256_file(archive_path) != record["archive_sha256"]:
            raise ValueError(f"archive SHA-256 mismatch: {archive_path.name}")
        expected_entries = {entry["path"]: entry for entry in bundle["files"]}
        with zipfile.ZipFile(archive_path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or set(names) != set(expected_entries):
                raise ValueError(f"archive member scope differs: {archive_path.name}")
            bad = archive.testzip()
            if bad is not None:
                raise ValueError(f"ZIP CRC failure in {archive_path.name}: {bad}")
            for name in names:
                info = archive.getinfo(name)
                expected = expected_entries[name]
                if info.file_size != expected["bytes"]:
                    raise ValueError(f"member size mismatch: {archive_path.name}:{name}")
                with archive.open(info) as stream:
                    if digest_stream(stream) != expected["sha256"]:
                        raise ValueError(f"member SHA-256 mismatch: {archive_path.name}:{name}")
                verified_members += 1
    artifacts = package_files(output, expected_zip_names)
    expected_artifacts = {path.name for path in artifacts}
    artifact_checksums = parse_flat_checksums(output / PACKAGE_CHECKSUMS)
    if set(artifact_checksums) != expected_artifacts:
        raise ValueError("package artifact checksum scope differs")
    for path in artifacts:
        if sha256_file(path) != artifact_checksums[path.name]:
            raise ValueError(f"package artifact SHA-256 mismatch: {path.name}")
    if (output / INVENTORY.name).read_bytes() != (root / INVENTORY).read_bytes():
        raise ValueError("packaged release inventory differs from repository copy")
    if (output / CHECKSUMS.name).read_bytes() != (root / CHECKSUMS).read_bytes():
        raise ValueError("packaged release checksums differ from repository copy")
    return {
        "archives": len(archive_records),
        "members": verified_members,
        "package_artifacts": len(artifact_checksums),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    if args.write:
        package = write_package(root, output)
        compressed = sum(record["archive_bytes"] for record in package["archives"])
        print(f"wrote {len(package['archives'])} archives ({compressed} compressed bytes) to {output}")
    result = verify_package(root, output)
    print(
        f"PASS: verified {result['archives']} archives, {result['members']} members, "
        f"and {result['package_artifacts']} package artifacts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
