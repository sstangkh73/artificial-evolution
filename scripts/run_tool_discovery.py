"""Batch runner for the YSC 2027 tool-discovery arena.

Runs every condition on the same seeds (paired), writes raw events (JSONL.gz),
the per-tick ledger (CSV.gz), one summary row per run, and a manifest with
SHA-256 checksums. An existing output directory is never overwritten; use
--resume to fill in runs that are missing. Resuming requires the same
conditions, seeds, overrides and code tree as recorded in protocol.json.
Runs from uncommitted code (simulation/, world/, scripts/) are refused unless
--allow-dirty is given, are then recorded as code_dirty, and cannot be resumed.
Seeds 5000+ are reserved for the confirmatory run (--allow-confirmatory-seeds).

Example:
    python scripts/run_tool_discovery.py --out data/tool_discovery_smoke_20261014 \
        --conditions C0 C1 C2 C3 C4 --seeds 0-4 --ticks 400
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
CODE_PATHS = ("simulation", "world", "scripts")
RESUME_KEYS = ("conditions", "seeds", "overrides", "code_tree", "code_dirty")
RUN_SUFFIXES = (".events.jsonl.gz", ".ledger.csv.gz", ".summary.json")
CONFIRM_MIN_SEED = 5000


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
            ["git", "status", "--porcelain", "--", *CODE_PATHS],
            capture_output=True, text=True, check=True,
        ).stdout
        return bool(out.strip())
    except (OSError, subprocess.CalledProcessError):
        return True


def git_code_tree() -> dict:
    """Git tree hash of each code path at HEAD; unchanged by commits that touch only docs."""
    trees = {}
    for path in CODE_PATHS:
        try:
            trees[path] = subprocess.run(
                ["git", "rev-parse", f"HEAD:{path}"], capture_output=True, text=True, check=True
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise SystemExit(f"cannot read the git tree of {path}/; refusing to run without provenance") from exc
    return trees


def resume_mismatches(recorded: dict, current: dict) -> list[str]:
    """Keys whose value in an existing protocol.json differs from this invocation."""
    return [key for key in RESUME_KEYS if recorded.get(key) != current.get(key)]


def run_complete(stem: Path) -> bool:
    return all(stem.with_suffix(s).exists() for s in RUN_SUFFIXES)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--conditions", nargs="+", default=list(CONDITIONS), choices=CONDITIONS)
    parser.add_argument("--seeds", default="0-4")
    parser.add_argument("--ticks", type=int)
    parser.add_argument("--agents", type=int)
    parser.add_argument("--set", action="append", default=[], help="override a config field, JSON value")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--allow-dirty", action="store_true",
                        help="run even if simulation/, world/ or scripts/ has uncommitted changes (no --resume)")
    parser.add_argument("--allow-confirmatory-seeds", action="store_true",
                        help=f"permit seeds >= {CONFIRM_MIN_SEED} (reserved for the frozen confirmatory run)")
    args = parser.parse_args()

    overrides = parse_overrides(args.set)
    if args.ticks is not None:
        overrides["ticks"] = args.ticks
    if args.agents is not None:
        overrides["n_agents"] = args.agents
    seeds = parse_seeds(args.seeds)
    if any(s >= CONFIRM_MIN_SEED for s in seeds) and not args.allow_confirmatory_seeds:
        raise SystemExit(f"seeds >= {CONFIRM_MIN_SEED} are reserved for the confirmatory run")

    dirty = git_dirty()
    if dirty and not args.allow_dirty:
        raise SystemExit("uncommitted changes in simulation/, world/ or scripts/; commit first (or --allow-dirty)")
    if dirty and args.resume:
        raise SystemExit("--resume needs committed code so every run in the folder shares one code tree")
    if args.out.exists() and not args.resume:
        raise SystemExit(f"{args.out} exists; refusing to overwrite (use --resume to add missing runs)")
    if args.resume and args.out.exists() and not (args.out / "protocol.json").exists():
        raise SystemExit(f"{args.out} has no protocol.json; cannot check that existing runs match")

    protocol = {
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "git_commit": git_commit(),
        "code_tree": git_code_tree(),
        "code_dirty": dirty,
        "python": platform.python_version(),
        "conditions": args.conditions,
        "seeds": seeds,
        "overrides": overrides,
        "base_config": config_dict(ArenaConfig(**overrides)),
    }
    protocol_path = args.out / "protocol.json"
    if protocol_path.exists():
        recorded = json.loads(protocol_path.read_text(encoding="utf-8"))
        mismatched = resume_mismatches(recorded, protocol)
        if mismatched:
            raise SystemExit(f"--resume does not match {protocol_path}: {', '.join(mismatched)} differ")
    else:
        args.out.mkdir(parents=True, exist_ok=True)
        protocol_path.write_text(json.dumps(protocol, indent=2, ensure_ascii=False), encoding="utf-8")
    runs_dir = args.out / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    # Interleave conditions within each seed so machine drift is spread evenly.
    for seed in seeds:
        for condition in args.conditions:
            stem = runs_dir / f"seed{seed:04d}_{condition}"
            summary_path = stem.with_suffix(".summary.json")
            config = ArenaConfig(seed=seed, condition=condition, **overrides)
            if run_complete(stem):
                recorded_cfg = json.loads(summary_path.read_text(encoding="utf-8")).get("config")
                if recorded_cfg != config_dict(config):
                    raise SystemExit(f"{summary_path} was run with a different config; refusing to mix")
                continue
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

    # Only runs named by this protocol count; stray files in runs/ are ignored.
    expected = sorted(f"seed{s:04d}_{c}" for s in seeds for c in args.conditions)
    complete = [name for name in expected if run_complete(runs_dir / name)]
    rows = []
    for name in complete:
        row = json.loads((runs_dir / f"{name}.summary.json").read_text(encoding="utf-8"))
        row.pop("config", None)
        rows.append(row)
    if rows:
        with (args.out / "summary.csv").open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    files = [runs_dir / f"{name}{suffix}" for name in complete for suffix in RUN_SUFFIXES]
    manifest = {
        "expected_runs": len(expected),
        "completed_runs": len(complete),
        "missing": sorted(set(expected) - set(complete)),
        "files": {str(p.relative_to(args.out)).replace("\\", "/"): sha256(p) for p in files},
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"completed {manifest['completed_runs']}/{manifest['expected_runs']} -> {args.out}")


if __name__ == "__main__":
    main()
