"""Level B (proposal 3.5) for the tool-discovery arena: a between-condition test.

`level_b_run` in each run summary is only a per-run screen; it passes in C2
(shuffled feedback) too. Level B proper asks whether the selective-reuse and
rebuild signals are larger in C1 than in the controls on the *same seeds*.
This script pairs runs by seed inside one output directory (one grid cell) and
reports, per metric, the paired difference treatment - control.

The output is descriptive. Which metric and contrast is primary, and how
multiple comparisons are handled, is fixed in the pilot protocol, not here.
A run with no discovery has first_discovery_tick censored at `ticks` (not
dropped); other undefined values (e.g. reuse_delta without bad-outcome pairs)
are dropped and counted.

Example:
    python scripts/analyze_tool_discovery_level_b.py data/tool_discovery_pilot_x \
        --pairs C1:C0 C1:C2 C3:C0 --out data/tool_discovery_pilot_x/level_b.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
from statistics import mean, stdev

METRICS = (
    "reuse_delta",
    "level_b_run",
    "functional_rate",
    "functional_per_agent",
    "rebuild_rate",
    "first_discovery_tick",
    "final_tool_use_rate",
    "final_net_per_alive_tick",
)


def load_runs(run_dir: Path) -> dict[tuple[str, int], dict]:
    """(condition, seed) -> summary, read from runs/*.summary.json.

    Refuses directories that mix grid cells: apart from seed and condition,
    every run must share one config, and each (condition, seed) appears once.
    """
    runs = {}
    shared = None
    for path in sorted((run_dir / "runs").glob("*.summary.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        key = (row["condition"], int(row["seed"]))
        if key in runs:
            raise ValueError(f"duplicate run {key} in {run_dir}")
        if "config" in row:
            cell = {k: v for k, v in row["config"].items() if k not in ("seed", "condition")}
            if shared is None:
                shared = cell
            elif cell != shared:
                raise ValueError(f"{path.name} has a different config from other runs in {run_dir}")
        runs[key] = row
    return runs


def _value(row: dict, metric: str):
    v = row.get(metric)
    if v is None and metric == "first_discovery_tick" and "config" in row:
        return float(row["config"]["ticks"])  # censored: no discovery within the run
    if isinstance(v, bool):
        return float(v)
    return None if v is None else float(v)


def bootstrap_ci(diffs: list[float], n_boot: int = 10000, seed: int = 0, level: float = 0.95):
    """Percentile bootstrap CI of the mean paired difference (resampling seeds)."""
    if len(diffs) < 2:
        return None
    rng = random.Random(seed)
    n = len(diffs)
    means = sorted(mean(rng.choices(diffs, k=n)) for _ in range(n_boot))
    lo = means[int((1 - level) / 2 * n_boot)]
    hi = means[int((1 + level) / 2 * n_boot) - 1]
    return [lo, hi]


def paired_comparison(runs: dict, treatment: str, control: str, metric: str) -> dict:
    seeds = sorted({s for c, s in runs if c == treatment} & {s for c, s in runs if c == control})
    t_vals, c_vals, diffs, dropped = [], [], [], []
    for s in seeds:
        t, c = _value(runs[(treatment, s)], metric), _value(runs[(control, s)], metric)
        if t is None or c is None:
            dropped.append(s)
            continue
        t_vals.append(t)
        c_vals.append(c)
        diffs.append(t - c)
    sd = stdev(diffs) if len(diffs) >= 2 else None
    return {
        "metric": metric,
        "treatment": treatment,
        "control": control,
        "n_seeds_paired": len(seeds),
        "n_pairs": len(diffs),
        "n_dropped_missing": len(dropped),
        "mean_treatment": mean(t_vals) if t_vals else None,
        "mean_control": mean(c_vals) if c_vals else None,
        "mean_diff": mean(diffs) if diffs else None,
        "sd_diff": sd,
        "dz": mean(diffs) / sd if sd else None,
        "n_treatment_higher": sum(d > 0 for d in diffs),
        "n_ties": sum(d == 0 for d in diffs),
        "n_control_higher": sum(d < 0 for d in diffs),
        "ci95_mean_diff": bootstrap_ci(diffs),
    }


def analyze(run_dir: Path, pairs: list[tuple[str, str]], metrics=METRICS) -> list[dict]:
    runs = load_runs(run_dir)
    return [paired_comparison(runs, t, c, m) for t, c in pairs for m in metrics]


def _fmt(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, list):
        return "[" + ", ".join(_fmt(x) for x in v) + "]"
    return f"{v:.3f}" if isinstance(v, float) else str(v)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--pairs", nargs="+", default=["C1:C0", "C1:C2", "C3:C0"],
                        help="treatment:control pairs (default C1:C0 C1:C2 C3:C0)")
    parser.add_argument("--out", type=Path, help="write the full result as JSON")
    args = parser.parse_args()
    pairs = [tuple(p.split(":")) for p in args.pairs]
    rows = analyze(args.run_dir, pairs)
    print("pair       metric                     n  mean_diff  ci95                 t>c/tie/c>t")
    for r in rows:
        print(f"{r['treatment']}-{r['control']:<6} {r['metric']:<26} {r['n_pairs']:>2}  "
              f"{_fmt(r['mean_diff']):>9}  {_fmt(r['ci95_mean_diff']):<20} "
              f"{r['n_treatment_higher']}/{r['n_ties']}/{r['n_control_higher']}")
    if args.out:
        args.out.write_text(json.dumps({"run_dir": str(args.run_dir), "comparisons": rows}, indent=2),
                            encoding="utf-8")


if __name__ == "__main__":
    main()
