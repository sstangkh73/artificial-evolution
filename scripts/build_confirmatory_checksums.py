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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--include", action="append", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root = Path(args.root)
    output = Path(args.out)
    if not output.is_absolute():
        output = root / output
    count = build_manifest(root, [Path(path) for path in args.include], output)
    print(f"wrote {count} SHA-256 entries to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
