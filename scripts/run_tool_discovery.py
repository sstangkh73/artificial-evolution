"""Batch runner for the YSC 2027 tool-discovery arena.

Runs every condition on the same seeds (paired), writes raw events (JSONL.gz),
the per-tick ledger (CSV.gz), one summary row per run, and a manifest with
SHA-256 checksums. An existing output directory is never overwritten; use
--resume to fill in runs that are missing.

Example:
    python scripts/run_tool_discovery.py --out data/tool_discovery_smoke_20261014 \
        --conditions C0 C1 C2 C3 --seeds 0-4 --ticks 400
    python scripts/run_tool_discovery.py --out ... --set epsilon=0.2 --set q_init=5
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulation.tool_discovery import CONDITIONS, ArenaConfig, config_dict, run_arena  # noqa: E402
from simulation.tool_discovery_metrics import summarize_run  # noqa: E402

LEDGER_FIELDS = ("tick", "agent", "food", "effort", "craft", "gather")


def parse_seeds(text: str) -> list[int]:
    seeds: list[int] = []
    for part in text.split(","):
        if "-" in part:
            lo, hi = part.split("-")
            seeds.extend(range(int(lo), int(hi) + 1))
        else:
            seeds.append(int(part))
    return seeds


def parse_overrides(pairs: list[str]) -> dict:
    out = {}
    for pair in pairs:
        key, value = pair.split("=", 1)
        out[key] = json.loads(value)
    return out


def git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def git_dirty() -> bool:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain", "--", "simulation", "world", "scripts/run_tool_discovery.py"],
            capture_output=True, text=True, check=True,
        ).stdout
        return bool(out.strip())
    except (OSError, subprocess.CalledProcessError):
        return True


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--conditions", nargs="+", default=["C0", "C1", "C2", "C3"], choices=CONDITIONS)
    parser.add_argument("--seeds", default="0-4")
    parser.add_argument("--ticks", type=int)
    parser.add_argument("--agents", type=int)
    parser.add_argument("--set", action="append", default=[], help="override a config field, JSON value")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    overrides = parse_overrides(args.set)
    if args.ticks is not None:
        overrides["ticks"] = args.ticks
    if args.agents is not None:
        overrides["n_agents"] = args.agents
    seeds = parse_seeds(args.seeds)

    if args.out.exists() and not args.resume:
        raise SystemExit(f"{args.out} exists; refusing to overwrite (use --resume to add missing runs)")
    runs_dir = args.out / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    protocol = {
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "git_commit": git_commit(),
        "code_dirty": git_dirty(),
        "python": platform.python_version(),
        "conditions": args.conditions,
        "seeds": seeds,
        "overrides": overrides,
        "base_config": config_dict(ArenaConfig(**overrides)),
    }
    protocol_path = args.out / "protocol.json"
    if not protocol_path.exists():
        protocol_path.write_text(json.dumps(protocol, indent=2, ensure_ascii=False), encoding="utf-8")

    # Interleave conditions within each seed so machine drift is spread evenly.
    for seed in seeds:
        for condition in args.conditions:
            stem = runs_dir / f"seed{seed:04d}_{condition}"
            summary_path = stem.with_suffix(".summary.json")
            if summary_path.exists():
                continue
            config = ArenaConfig(seed=seed, condition=condition, **overrides)
            started = time.perf_counter()
            arena = run_arena(config)
            elapsed = time.perf_counter() - started
            cfg = config_dict(config)
            with gzip.open(stem.with_suffix(".events.jsonl.gz"), "wt", encoding="utf-8") as fh:
                for event in arena.events:
                    fh.write(json.dumps(event, sort_keys=True) + "\n")
            with gzip.open(stem.with_suffix(".ledger.csv.gz"), "wt", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=LEDGER_FIELDS)
                writer.writeheader()
                writer.writerows(arena.ledger)
            summary = summarize_run(arena.events, arena.ledger, cfg)
            summary["runtime_s"] = round(elapsed, 3)
            summary["config"] = cfg
            summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
            print(f"seed={seed} {condition} survivors={summary['survivors']} "
                  f"final_net={summary['final_net_per_alive_tick']} ({elapsed:.2f}s)", flush=True)

    rows = []
    for path in sorted(runs_dir.glob("*.summary.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        row.pop("config", None)
        rows.append(row)
    if rows:
        with (args.out / "summary.csv").open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    expected = {f"seed{s:04d}_{c}" for s in seeds for c in args.conditions}
    present = {p.name.split(".")[0] for p in runs_dir.glob("*.summary.json")}
    manifest = {
        "expected_runs": len(expected),
        "completed_runs": len(expected & present),
        "missing": sorted(expected - present),
        "files": {str(p.relative_to(args.out)).replace("\\", "/"): sha256(p) for p in sorted(runs_dir.iterdir())},
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"completed {manifest['completed_runs']}/{manifest['expected_runs']} -> {args.out}")


if __name__ == "__main__":
    main()
