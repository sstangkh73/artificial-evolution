# -*- coding: utf-8 -*-
"""Arm x seed runner for the G1-G6 experiment series (E1, E2, E3, E5).

Every experiment in PLAN_E1_E6 has the same shape: a small set of arms that differ
in a few flags, run over one shared seed set, analysed paired by seed. This script
is that shape. It does not decide anything scientific -- arms and parameters come
from a JSON spec that the preregistration freezes -- it only runs the grid,
records provenance, and flattens each run into one row per (arm, seed).

Spec format:

    {
      "experiment": "E1",
      "ticks": 800,
      "seeds": [20260910, ...],
      "base": ["--model", "v2", ...],
      "arms": {"A0": [...flags...], "A2": [...], "A3": [...]}
    }

The base flags are shared by every arm; anything an arm needs to differ on goes in
its own list. Arms are run in seed-major order so a partial run still covers every
arm at the seeds completed, which keeps the paired analysis valid if the batch is
interrupted.

Usage:
    python scripts/run_e_series.py --spec reports/prereg/E1_spec.json \
        --work-dir data/e1 --out-dir reports/e1 [--jobs 4] [--resume]
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_HERE))

from run_e0_pilot import diagnose, _params_from_flags  # noqa: E402

DRIVER = "scripts/food_value_study_driver.py"


def _git_revision() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=_HERE.parent,
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except Exception:
        return "unknown"


def _dirty_tree() -> bool:
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                             cwd=_HERE.parent, capture_output=True, text=True, check=True)
        return bool(out.stdout.strip())
    except Exception:
        return True


def _run_one(job: tuple) -> dict:
    spec, arm, flags, seed, work_dir, ticks, resume = job
    work = Path(work_dir)
    dump = work / f"{spec}_{arm}_s{seed}.json"
    if resume and dump.exists():
        summary = json.loads(dump.read_text(encoding="utf-8"))
        elapsed = 0.0
        reused = True
    else:
        command = [sys.executable, DRIVER, *flags, "--seed", str(seed), "--ticks", str(ticks),
                   "--output", str(work / f"{spec}_{arm}_s{seed}.out"), "--dump", str(dump)]
        started = time.monotonic()
        completed = subprocess.run(command, cwd=_HERE.parent, capture_output=True, text=True)
        elapsed = time.monotonic() - started
        if completed.returncode != 0:
            return {"arm": arm, "seed": seed, "error": completed.stderr[-3000:]}
        summary = json.loads(dump.read_text(encoding="utf-8"))
        reused = False
    row = {"experiment": spec, "arm": arm, "seed": seed, "reused": reused,
           "dump": str(dump), "flags": " ".join(flags)}
    row.update(diagnose(summary, _params_from_flags(flags), elapsed, ticks))
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--resume", action="store_true",
                        help="reuse dumps that already exist instead of rerunning")
    parser.add_argument("--allow-dirty", action="store_true",
                        help="run even though tracked files are modified (NOT for confirmatory runs)")
    args = parser.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    name = spec["experiment"]
    ticks = int(spec["ticks"])
    seeds = [int(s) for s in spec["seeds"]]
    base = list(spec.get("base") or [])
    arms = spec["arms"]

    if _dirty_tree() and not args.allow_dirty:
        print("REFUSING: tracked files are modified. A confirmatory run must be made from a "
              "clean tree so its commit hash means something. Commit, or pass --allow-dirty "
              "for an exploratory run.", file=sys.stderr)
        return 2

    work = Path(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs = [
        (name, arm, base + list(flags), seed, str(work), ticks, args.resume)
        for seed in seeds
        for arm, flags in arms.items()
    ]

    started = time.monotonic()
    rows: list[dict] = []
    if args.jobs > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            for row in pool.map(_run_one, jobs):
                rows.append(row)
                print(json.dumps({k: row.get(k) for k in ("arm", "seed", "final_tick",
                                                          "founder_mean_age", "error")},
                                 ensure_ascii=False), flush=True)
    else:
        for job in jobs:
            row = _run_one(job)
            rows.append(row)
            print(json.dumps({k: row.get(k) for k in ("arm", "seed", "final_tick",
                                                      "founder_mean_age", "error")},
                             ensure_ascii=False), flush=True)

    failures = [r for r in rows if r.get("error")]
    provenance = {
        "experiment": name,
        "spec": spec,
        "git_revision": _git_revision(),
        "git_tree_dirty": _dirty_tree(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "wall_seconds_total": round(time.monotonic() - started, 1),
        "runs": len(rows),
        "failures": len(failures),
    }
    results_path = out_dir / f"{name}_runs.json"
    results_path.write_text(json.dumps({"provenance": provenance, "rows": rows},
                                       indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {results_path}  ({len(rows)} runs, {len(failures)} failed, "
          f"{provenance['wall_seconds_total']}s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
