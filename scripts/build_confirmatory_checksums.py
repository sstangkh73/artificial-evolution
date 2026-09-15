# -*- coding: utf-8 -*-
"""Build a stable SHA-256 inventory for confirmatory publication artifacts."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def collect_files(root: Path, includes: list[Path], output: Path) -> list[Path]:
    root = root.resolve()
    output = output.resolve()
    files: set[Path] = set()
    for include in includes:
        resolved = (root / include).resolve() if not include.is_absolute() else include.resolve()
        if not resolved.exists():
            raise FileNotFoundError(resolved)
        candidates = resolved.rglob("*") if resolved.is_dir() else (resolved,)
        for candidate in candidates:
            candidate = candidate.resolve()
            if candidate.is_file() and candidate != output:
                try:
                    candidate.relative_to(root)
                except ValueError as exc:
                    raise ValueError(f"included file is outside root: {candidate}") from exc
                files.add(candidate)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def build_manifest(root: Path, includes: list[Path], output: Path) -> int:
    files = collect_files(root, includes, output)
    lines = [
        f"{sha256_file(path)}  {path.relative_to(root.resolve()).as_posix()}"
        for path in files
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return len(files)


def refresh_manifest(root: Path, output: Path) -> int:
    """Rehash the existing path set without silently changing its scope."""
    root = root.resolve()
    output = output.resolve()
    if not output.is_file():
        raise FileNotFoundError(output)
    paths: list[Path] = []
    for line_number, line in enumerate(output.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            _, relative = line.split("  ", 1)
        except ValueError as exc:
            raise ValueError(f"malformed checksum line {line_number}: {line!r}") from exc
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"manifest path is outside root: {relative}") from exc
        if not candidate.is_file():
            raise FileNotFoundError(candidate)
        paths.append(candidate)
    if len(paths) != len(set(paths)):
        raise ValueError("manifest contains duplicate paths")
    lines = [
        f"{sha256_file(path)}  {path.relative_to(root).as_posix()}"
        for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix())
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return len(paths)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--include", action="append")
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--refresh-existing",
        action="store_true",
        help="rehash exactly the paths already listed in --out",
    )
    args = parser.parse_args()
    root = Path(args.root)
    output = Path(args.out)
    if not output.is_absolute():
        output = root / output
    if args.refresh_existing:
        if args.include:
            parser.error("--refresh-existing cannot be combined with --include")
        count = refresh_manifest(root, output)
    else:
        if not args.include:
            parser.error("at least one --include is required unless --refresh-existing is used")
        count = build_manifest(root, [Path(path) for path in args.include], output)
    print(f"wrote {count} SHA-256 entries to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
