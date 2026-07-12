# -*- coding: utf-8 -*-
"""Tier-A A4 multi-seed batch runner: A (no learning) vs B (value learning).

Runs the population-level food-value-learning experiment across many seeds,
identical config in both arms except the --value-learning switch, so the only
difference is the learning mechanism. Each run is dumped to
data/multiseed/{A,B}_<seed>.json. Already-present dumps are skipped, so the
batch is resumable and can be extended (more seeds / longer ticks) by re-running.

Aggregate the dumps with scripts/aggregate_food_value_multiseed.py.

Example (n=10 seeds, 3000 ticks):
  python scripts/run_multiseed_food_value.py --seed-start 20260610 --n-seeds 10 --ticks 3000
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUTDIR = ROOT / "data" / "multiseed"
DRIVER = HERE / "food_value_study_driver.py"

# Shared config for both arms (only --value-learning differs).
BASE_FLAGS = [
    "--model", "v2", "--body", "37",
    "--drain-mult", "0.05", "--food-energy-mult", "50",
    "--low-value-food", "6",
]


def log(msg: str, logfile: Path) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with logfile.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def run_one(seed: int, ticks: int, learning: bool, logfile: Path) -> bool:
    arm = "B" if learning else "A"
    dump = OUTDIR / f"{arm}_{seed}.json"
    if dump.exists() and dump.stat().st_size > 0:
        log(f"skip {arm} seed={seed} (dump exists)", logfile)
        return True
    cmd = [sys.executable, str(DRIVER), *BASE_FLAGS,
           "--ticks", str(ticks), "--seed", str(seed),
           "--dump", str(dump)]
    if learning:
        cmd.append("--value-learning")
    t0 = time.time()
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    el = time.time() - t0
    if proc.returncode != 0 or not dump.exists():
        log(f"FAIL {arm} seed={seed} rc={proc.returncode} "
            f"err={proc.stderr.decode('utf-8','replace')[:200]}", logfile)
        return False
    log(f"done {arm} seed={seed} in {el:.0f}s -> {dump.name}", logfile)
    return True


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--seed-start", type=int, default=20260610)
    p.add_argument("--n-seeds", type=int, default=10)
    p.add_argument("--ticks", type=int, default=3000)
    a = p.parse_args()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    logfile = OUTDIR / "_batch_progress.log"
    seeds = list(range(a.seed_start, a.seed_start + a.n_seeds))
    log(f"=== batch start: {len(seeds)} seeds x 2 arms, ticks={a.ticks} ===", logfile)
    t_all = time.time()
    ok = 0
    total = len(seeds) * 2
    for seed in seeds:
        for learning in (False, True):  # A then B
            if run_one(seed, a.ticks, learning, logfile):
                ok += 1
    log(f"=== batch end: {ok}/{total} runs ok in {(time.time()-t_all)/60:.1f} min ===", logfile)
