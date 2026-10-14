"""Pilot analysis for the tool-discovery arena (03_pilot_protocol.md, sections 5-7).

Two steps, each a subcommand:

  s1     Read every S1 grid cell (data/tool_discovery_pilot_s1_*), check Gate A
         and Gate B per cell, and apply the selection rule of section 6
         (best mean C1 `final_net_per_alive_tick` among cells passing both gates,
         one-SE ties broken by fewer ticks -> smaller epsilon -> q_init 0).
         Also reports C1 - C2 per cell for the section 9 stop check.
  power  Read the S2 directory of the selected cell, re-check the gates (report
         only) and compute the confirmatory seed count from the paired C1 - C2
         difference: safeguard dz (20th percentile of bootstrap dz), Guenther's
         approximation rounded up to a multiple of 10 (minimum 50), then checked
         by simulating paired t-tests, adding 10 seeds until power >= 0.90.

Only directories whose manifest says every run completed are analysed.
Nothing here chooses a metric or a rule; those are fixed in the protocol.

Example:
    python scripts/analyze_tool_discovery_pilot.py s1 --out docs/ysc2027_tool_discovery/pilot_s1_analysis.json
    python scripts/analyze_tool_discovery_pilot.py power data/tool_discovery_pilot_s2_selected \
        --out docs/ysc2027_tool_discovery/pilot_s2_power.json
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import sys
from statistics import NormalDist, mean, stdev

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_tool_discovery_level_b import bootstrap_ci, load_runs, paired_comparison  # noqa: E402

PRIMARY = "final_net_per_alive_tick"
GATE_B1_MIN_FRACTION = 0.20
POWER = 0.90
ALPHA = 0.05
MIN_SEEDS = 50
MAX_SEEDS = 2000
CONDITIONS = ("C0", "C1", "C2", "C3", "C4")
S1_SEEDS = tuple(range(1000, 1050))
S2_SEEDS = tuple(range(1050, 1100))
S1_CELLS = 16


def add_components(runs: dict) -> dict:
    """Per agent-tick components of the primary metric (late window)."""
    for row in runs.values():
        ticks = row.get("final_agent_ticks") or 0
        if ticks:
            row["food_minus_effort_per_tick"] = row["final_food_per_alive_tick"] - row["final_effort"] / ticks
            row["craft_cost_per_tick"] = row["final_craft_cost"] / ticks
            row["gather_cost_per_tick"] = row["final_gather_cost"] / ticks
    return runs


def load_complete(run_dir: Path, seeds: tuple[int, ...]) -> dict:
    """Runs of one folder; refuses anything but the full C0-C4 x `seeds` design."""
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("completed_runs") != manifest.get("expected_runs") or manifest.get("missing"):
        raise ValueError(f"{run_dir} is incomplete; the protocol analyses complete folders only")
    runs = load_runs(run_dir)
    expected = {(c, s) for c in CONDITIONS for s in seeds}
    if set(runs) != expected:
        raise ValueError(f"{run_dir}: runs do not match conditions {CONDITIONS} x seeds "
                         f"{seeds[0]}-{seeds[-1]} ({len(set(runs) ^ expected)} differ)")
    return add_components(runs)


def _paired_full(runs: dict, treatment: str, control: str, metric: str) -> dict:
    """paired_comparison that must use every seed (gate, selection and power metrics)."""
    cmp = paired_comparison(runs, treatment, control, metric)
    if cmp["n_pairs"] != cmp["n_seeds_paired"]:
        raise ValueError(f"{treatment}-{control} {metric}: {cmp['n_dropped_missing']} seeds lack a value")
    return cmp


def cell_params(runs: dict) -> dict:
    cfg = next(iter(runs.values()))["config"]
    return {"epsilon": float(cfg["epsilon"]), "q_init": float(cfg["q_init"]), "ticks": int(cfg["ticks"])}


def _ci_lo_positive(cmp: dict) -> bool:
    ci = cmp["ci95_mean_diff"]
    return ci is not None and ci[0] > 0


def gates(runs: dict) -> dict:
    """Gate A and Gate B of section 5, with the components reported beside Gate A."""
    a = _paired_full(runs, "C3", "C0", PRIMARY)
    a_parts = {m: _paired_full(runs, "C3", "C0", m)
               for m in ("food_minus_effort_per_tick", "craft_cost_per_tick", "gather_cost_per_tick")}
    c0 = [row for (c, _), row in runs.items() if c == "C0"]
    b1_fraction = sum((row.get("n_functional_objects") or 0) >= 1 for row in c0) / len(c0) if c0 else 0.0
    b2 = _paired_full(runs, "C3", "C0", "functional_rate")
    gate_a = _ci_lo_positive(a)
    gate_b1 = b1_fraction >= GATE_B1_MIN_FRACTION
    gate_b2 = _ci_lo_positive(b2)
    return {
        "gate_a": gate_a, "gate_a_cmp": a, "gate_a_components": a_parts,
        "gate_b1": gate_b1, "gate_b1_c0_fraction_functional": b1_fraction,
        "gate_b2": gate_b2, "gate_b2_cmp": b2,
        "pass": gate_a and gate_b1 and gate_b2,
    }


def describe_cell(run_dir: Path, seeds: tuple[int, ...] = S1_SEEDS) -> dict:
    runs = load_complete(run_dir, seeds)
    c1 = [row[PRIMARY] for (c, _), row in runs.items() if c == "C1"]
    c1_c2 = _paired_full(runs, "C1", "C2", PRIMARY)
    ci = c1_c2["ci95_mean_diff"]
    return {
        "dir": run_dir.name,
        **cell_params(runs),
        "c1_n": len(c1),
        "c1_mean": mean(c1),
        "c1_sd": stdev(c1),
        "c1_se": stdev(c1) / math.sqrt(len(c1)),
        "c1_minus_c2": c1_c2,
        "c1_minus_c2_food_minus_effort": _paired_full(runs, "C1", "C2", "food_minus_effort_per_tick"),
        "c1_c2_ci_excludes_zero": ci is not None and (ci[0] > 0 or ci[1] < 0),
        **gates(runs),
    }


def select_cell(cells: list[dict]) -> dict:
    """Section 6: gate filter, best C1 mean, one-SE tie, then ticks -> epsilon -> q_init."""
    passing = [c for c in cells if c["pass"]]
    if not passing:
        return {"selected": None, "reason": "no S1 cell passes both Gate A and Gate B"}
    best = max(passing, key=lambda c: c["c1_mean"])
    tied = [c for c in passing if best["c1_mean"] - c["c1_mean"] < best["c1_se"]]
    chosen = min(tied, key=lambda c: (c["ticks"], c["epsilon"], c["q_init"]))
    return {
        "selected": chosen["dir"],
        "params": {k: chosen[k] for k in ("epsilon", "q_init", "ticks")},
        "best_by_c1_mean": best["dir"],
        "best_c1_mean": best["c1_mean"],
        "best_c1_se": best["c1_se"],
        "tied_within_1se": sorted(c["dir"] for c in tied),
        "n_passing": len(passing),
    }


def run_s1(data_dir: Path, seeds: tuple[int, ...] = S1_SEEDS, n_cells: int = S1_CELLS) -> dict:
    dirs = sorted(p for p in data_dir.glob("tool_discovery_pilot_s1_*") if p.is_dir())
    if len(dirs) != n_cells:
        raise ValueError(f"expected {n_cells} S1 cells, found {len(dirs)}")
    cells = [describe_cell(d, seeds) for d in dirs]
    if len({(c["epsilon"], c["q_init"], c["ticks"]) for c in cells}) != n_cells:
        raise ValueError("S1 folders do not cover distinct grid cells")
    selection = select_cell(cells)
    stop = []
    if selection["selected"] is None:
        stop.append(selection["reason"])
    if cells and not any(c["c1_c2_ci_excludes_zero"] for c in cells):
        stop.append("every S1 cell has a C1 - C2 95% CI that spans 0")
    return {"n_cells": len(cells), "cells": cells, "selection": selection, "stop_reasons": stop}


# --- power (section 7) -----------------------------------------------------------

def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the regularized incomplete beta (Numerical Recipes)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(1.0 + aa / c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c if abs(1.0 + aa / c) > 1e-300 else 1e-300
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return h


def _betainc(a: float, b: float, x: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_cdf(t: float, df: int) -> float:
    tail = 0.5 * _betainc(df / 2, 0.5, df / (df + t * t))
    return 1.0 - tail if t > 0 else tail


def t_crit(p: float, df: int) -> float:
    lo, hi = 0.0, 50.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def guenther_n(dz: float, alpha: float = ALPHA, power: float = POWER) -> int:
    z = NormalDist()
    za, zb = z.inv_cdf(1 - alpha / 2), z.inv_cdf(power)
    return math.ceil(((za + zb) / dz) ** 2 + za * za / 2)


def simulated_power(n: int, dz: float, reps: int = 10000, seed: int = 0, alpha: float = ALPHA) -> float:
    rng = random.Random(seed)
    crit = t_crit(1 - alpha / 2, n - 1)
    hits = 0
    for _ in range(reps):
        x = [rng.gauss(dz, 1.0) for _ in range(n)]
        sd = stdev(x)
        if sd > 0 and abs(mean(x) / (sd / math.sqrt(n))) > crit:
            hits += 1
    return hits / reps


def bootstrap_dz(diffs: list[float], n_boot: int = 10000, seed: int = 0) -> list[float]:
    rng = random.Random(seed)
    out = []
    for _ in range(n_boot):
        s = rng.choices(diffs, k=len(diffs))
        sd = stdev(s)
        out.append(mean(s) / sd if sd > 0 else (math.inf if mean(s) > 0 else -math.inf if mean(s) < 0 else 0.0))
    return sorted(out)


def _round_up_10(n: int) -> int:
    return max(MIN_SEEDS, int(math.ceil(n / 10.0)) * 10)


def seed_count(diffs: list[float], sim_reps: int = 10000) -> dict:
    """Section 7 rule, including the SD = 0 and stop cases."""
    m = mean(diffs)
    sd = stdev(diffs)
    if sd == 0:
        if m > 0:
            return {"mean_diff": m, "sd_diff": 0.0, "dz": None, "dz_safe": None, "n": MIN_SEEDS,
                    "stop": None, "note": "SD of differences is 0 and the mean is positive: minimum seeds"}
        return {"mean_diff": m, "sd_diff": 0.0, "dz": None, "dz_safe": None, "n": None,
                "stop": "SD of differences is 0 and the mean is not positive"}
    dz = m / sd
    boot = bootstrap_dz(diffs)
    dz_safe = boot[int(0.20 * len(boot))]
    out = {"mean_diff": m, "sd_diff": sd, "dz": dz, "dz_safe": dz_safe,
           "dz_boot_ci95": [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]]}
    if dz <= 0 or dz_safe <= 0:
        return {**out, "n": None, "stop": "dz or dz_safe is not positive"}
    n_formula = guenther_n(dz_safe)
    n = _round_up_10(n_formula)
    checks = []
    while n <= MAX_SEEDS:
        p = simulated_power(n, dz_safe, reps=sim_reps)
        checks.append({"n": n, "power": p})
        if p >= POWER:
            break
        n += 10
    if n > MAX_SEEDS:
        return {**out, "n_guenther": n_formula, "power_checks": checks, "n": None,
                "stop": f"required seeds exceed {MAX_SEEDS}"}
    return {**out, "n_guenther": n_formula, "power_checks": checks, "n": n, "stop": None}


def run_power(run_dir: Path, seeds: tuple[int, ...] = S2_SEEDS) -> dict:
    runs = load_complete(run_dir, seeds)
    cmp = _paired_full(runs, "C1", "C2", PRIMARY)
    seeds = sorted({s for c, s in runs if c == "C1"} & {s for c, s in runs if c == "C2"})
    diffs = [runs[("C1", s)][PRIMARY] - runs[("C2", s)][PRIMARY] for s in seeds]
    return {
        "dir": run_dir.name,
        **cell_params(runs),
        "seeds": [min(seeds), max(seeds)] if seeds else None,
        "gates_s2": gates(runs),
        "c1_minus_c2": cmp,
        "c1_minus_c2_food_minus_effort": _paired_full(runs, "C1", "C2", "food_minus_effort_per_tick"),
        "power": seed_count(diffs),
    }


def _f(v, nd=3):
    if v is None:
        return "-"
    if isinstance(v, list):
        return "[" + ", ".join(_f(x, nd) for x in v) + "]"
    return f"{v:.{nd}f}" if isinstance(v, float) else str(v)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("s1")
    p1.add_argument("--data", type=Path, default=Path("data"))
    p1.add_argument("--out", type=Path)
    p2 = sub.add_parser("power")
    p2.add_argument("run_dir", type=Path)
    p2.add_argument("--out", type=Path)
    args = parser.parse_args()

    if args.cmd == "s1":
        res = run_s1(args.data)
        print("cell                                  A  B1    B2  C1mean   C1se   C1-C2   ci95")
        for c in res["cells"]:
            print(f"{c['dir']:<37} {'Y' if c['gate_a'] else 'n'}  {c['gate_b1_c0_fraction_functional']:.2f}  "
                  f"{'Y' if c['gate_b2'] else 'n'}  {c['c1_mean']:>6.3f}  {c['c1_se']:.3f}  "
                  f"{_f(c['c1_minus_c2']['mean_diff']):>6}  {_f(c['c1_minus_c2']['ci95_mean_diff'])}")
        print("selection:", json.dumps(res["selection"]))
        print("stop:", res["stop_reasons"] or "none")
    else:
        res = run_power(args.run_dir)
        print(json.dumps({k: res[k] for k in ("dir", "epsilon", "q_init", "ticks", "seeds")}))
        g = res["gates_s2"]
        print(f"S2 gates: A={g['gate_a']} B1={g['gate_b1_c0_fraction_functional']:.2f} B2={g['gate_b2']}")
        pw = res["power"]
        print(f"C1-C2 mean={_f(pw['mean_diff'])} sd={_f(pw.get('sd_diff'))} dz={_f(pw['dz'])} "
              f"dz_safe={_f(pw['dz_safe'])} n={pw['n']} stop={pw['stop']}")
    if args.out:
        args.out.write_text(json.dumps(res, indent=2, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
