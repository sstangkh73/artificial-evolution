# -*- coding: utf-8 -*-
"""Create a deterministic hash manifest for frozen preregistration inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_value(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return completed.stdout.strip()


def build_manifest(paths: list[Path], tag_name: str) -> dict:
    specs = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in paths if path.name.endswith("_spec.json")
    ]
    return {
        "manifest_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_by_annotated_tag": tag_name,
        "source_revision_before_freeze_commit": git_value("rev-parse", "HEAD"),
        "tree_clean_when_manifest_built": not bool(
            git_value("status", "--porcelain", "--untracked-files=no")
        ),
        "python_version": sys.version,
        "platform": platform.platform(),
        "experiments": [
            {
                "experiment": spec.get("experiment"),
                "status": spec.get("status"),
                "primary_metric": spec.get("primary_metric"),
                "ticks": spec.get("ticks"),
                "seeds": spec.get("seeds"),
                "arms": list((spec.get("arms") or {}).keys()),
                "expected_runs": len(spec.get("seeds") or []) * len(spec.get("arms") or {}),
            }
            for spec in specs
        ],
        "files": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in sorted(paths)
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    paths = [(ROOT / item).resolve() for item in args.files]
    missing = [str(path) for path in paths if not path.is_file()]
    outside = [str(path) for path in paths if ROOT not in path.parents]
    if missing or outside:
        parser.error(f"invalid manifest inputs; missing={missing}, outside_repo={outside}")
    manifest = build_manifest(paths, args.tag)
    output = (ROOT / args.out).resolve()
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {output.relative_to(ROOT)} with {len(paths)} hashed files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
