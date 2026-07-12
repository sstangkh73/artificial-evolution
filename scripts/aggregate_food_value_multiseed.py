# -*- coding: utf-8 -*-
"""Tier-A A4 aggregator: multi-seed statistics + CI figure for A vs B.

Reads data/multiseed/A_<seed>.json (no learning) and B_<seed>.json (value
learning) produced by scripts/run_multiseed_food_value.py, then:

  * extracts low-value-food (raw_seed) consumption per 1000-tick window from each
    run's cumulative agent_diet_trajectory;
  * computes per-window mean +/- 95% CI (t-based) for each arm;
  * runs a Mann-Whitney U test (A vs B) on total raw_seed meals over the run,
    with tie + continuity correction (normal approximation, no scipy needed);
  * reports the effect size as Cliff's delta (= rank-biserial correlation);
  * renders reports/figures/fig_multiseed_seed_consumption_CI.png (mean lines
    with shaded 95% CI bands) and prints a Markdown stats table.

Usage:
  python scripts/aggregate_food_value_multiseed.py --window 1000
"""
import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
INDIR = ROOT / "data" / "multiseed"
OUT = ROOT / "reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 11,
    "font.family": "Tahoma", "axes.unicode_minus": False,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "figure.autolayout": True,
})
C = {"a": "#9A6BB0", "b": "#0E7C7B"}

# two-sided t critical values, alpha=0.05, by degrees of freedom
_T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
        8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160,
        14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
        20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
        26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042}


def t_crit_95(df: int) -> float:
    if df <= 0:
        return float("nan")
    if df in _T95:
        return _T95[df]
    if df > 30:
        return 1.96 if df > 200 else 2.0  # close enough for these n
    return _T95[30]


def mean_sd(xs: list[float]) -> tuple[float, float]:
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan")
    m = sum(xs) / n
    if n == 1:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var)


def ci95(xs: list[float]) -> tuple[float, float, float]:
    """Return (mean, half_width, sd) for a 95% CI of the mean."""
    n = len(xs)
    m, sd = mean_sd(xs)
    if n <= 1:
        return m, 0.0, sd
    half = t_crit_95(n - 1) * sd / math.sqrt(n)
    return m, half, sd


def _phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _rankdata(values: list[float]) -> list[float]:
    """Average ranks (1-based), handling ties."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + 1 + j + 1) / 2.0  # average of 1-based ranks i+1..j+1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def mann_whitney_u(a: list[float], b: list[float]) -> dict:
    """Two-sided Mann-Whitney U with tie + continuity correction (normal approx)."""
    n1, n2 = len(a), len(b)
    combined = a + b
    ranks = _rankdata(combined)
    r1 = sum(ranks[:n1])
    u1 = r1 - n1 * (n1 + 1) / 2.0
    u2 = n1 * n2 - u1
    u = min(u1, u2)
    mu = n1 * n2 / 2.0
    # tie correction
    n = n1 + n2
    counts: dict[float, int] = {}
    for v in combined:
        counts[v] = counts.get(v, 0) + 1
    tie_sum = sum(t ** 3 - t for t in counts.values())
    sigma2 = (n1 * n2 / 12.0) * ((n ** 3 - n - tie_sum) / (n * (n - 1)))
    sigma = math.sqrt(sigma2) if sigma2 > 0 else float("nan")
    if not sigma or math.isnan(sigma):
        z, p = float("nan"), float("nan")
    else:
        z = (abs(u - mu) - 0.5) / sigma  # continuity correction
        p = 2.0 * (1.0 - _phi(z))
        p = min(1.0, max(0.0, p))
    return {"U1_A": u1, "U2_B": u2, "U": u, "z": z, "p_two_sided": p,
            "n_A": n1, "n_B": n2}


def cliffs_delta(a: list[float], b: list[float]) -> dict:
    """delta = P(a>b) - P(a<b); positive => A tends to be larger than B."""
    gt = lt = 0
    for x in a:
        for y in b:
            if x > y:
                gt += 1
            elif x < y:
                lt += 1
    n = len(a) * len(b)
    d = (gt - lt) / n if n else float("nan")
    ad = abs(d)
    mag = ("negligible" if ad < 0.147 else "small" if ad < 0.33
           else "medium" if ad < 0.474 else "large")
    return {"delta": d, "magnitude": mag}


def cum_seed_by_tick(dump: dict) -> dict[int, int]:
    traj = dump.get("agent_diet_trajectory") or []
    out: dict[int, int] = {}
    for row in traj:
        t = int(row.get("tick", 0))
        out[t] = out.get(t, 0) + int(row.get("raw_seed_meals", 0) or 0)
    return out


def windowed_seed(dump: dict, window: int) -> list[int]:
    cum = cum_seed_by_tick(dump)
    final_tick = max(cum) if cum else 0
    n_windows = final_tick // window
    vals = []
    for k in range(n_windows):
        lo, hi = k * window, (k + 1) * window
        if lo not in cum or hi not in cum:
            break
        vals.append(cum[hi] - cum[lo])
    return vals


def load_arm(prefix: str) -> dict[int, dict]:
    out = {}
    for f in sorted(INDIR.glob(f"{prefix}_*.json")):
        try:
            seed = int(f.stem.split("_")[1])
        except (IndexError, ValueError):
            continue
        out[seed] = json.loads(f.read_text(encoding="utf-8"))
    return out


def fmt(x: float, nd: int = 1) -> str:
    if isinstance(x, float) and math.isnan(x):
        return "nan"
    return f"{x:.{nd}f}"


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--window", type=int, default=1000)
    a = p.parse_args()

    A = load_arm("A")
    B = load_arm("B")
    if not A or not B:
        raise SystemExit(f"need both arms; found A={len(A)} B={len(B)} in {INDIR}")

    # totals per run (authoritative: diet_by_kind.raw_seed)
    totals_A = [d["diet_by_kind"]["raw_seed"] for d in A.values()]
    totals_B = [d["diet_by_kind"]["raw_seed"] for d in B.values()]

    # per-window matrices
    win_A = [windowed_seed(d, a.window) for d in A.values()]
    win_B = [windowed_seed(d, a.window) for d in B.values()]
    n_win = min(min((len(w) for w in win_A), default=0),
                min((len(w) for w in win_B), default=0))
    win_A = [w[:n_win] for w in win_A]
    win_B = [w[:n_win] for w in win_B]

    perwin = []
    for k in range(n_win):
        ak = [w[k] for w in win_A]
        bk = [w[k] for w in win_B]
        mA, hA, sA = ci95(ak)
        mB, hB, sB = ci95(bk)
        perwin.append({"window": f"{k*a.window//1000}-{(k+1)*a.window//1000}k",
                       "A_mean": mA, "A_ci": hA, "A_sd": sA,
                       "B_mean": mB, "B_ci": hB, "B_sd": sB})

    mwu = mann_whitney_u(totals_A, totals_B)
    eff = cliffs_delta(totals_A, totals_B)
    tA = ci95(totals_A)
    tB = ci95(totals_B)

    # ---- figure: mean lines + 95% CI bands ----
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    xs = list(range(n_win))
    labels = [w["window"] for w in perwin]
    aM = [w["A_mean"] for w in perwin]; aC = [w["A_ci"] for w in perwin]
    bM = [w["B_mean"] for w in perwin]; bC = [w["B_ci"] for w in perwin]
    ax.plot(xs, aM, "o-", color=C["a"], lw=2.4, ms=7, label=f"A: ไม่เรียนรู้ (n={mwu['n_A']})")
    ax.fill_between(xs, [m - c for m, c in zip(aM, aC)], [m + c for m, c in zip(aM, aC)],
                    color=C["a"], alpha=0.18)
    ax.plot(xs, bM, "s--", color=C["b"], lw=2.4, ms=7, label=f"B: เรียนรู้คุณค่า (n={mwu['n_B']})")
    ax.fill_between(xs, [m - c for m, c in zip(bM, bC)], [m + c for m, c in zip(bM, bC)],
                    color=C["b"], alpha=0.18)
    ax.set_xticks(xs); ax.set_xticklabels(labels)
    ax.set_xlabel("ช่วงเวลา (ticks)")
    ax.set_ylabel(f"อาหารค่าต่ำ (raw_seed) ที่กินต่อ {a.window} ticks")
    ax.set_ylim(bottom=0)
    ax.set_title("หลายซีดยืนยัน: การเรียนรู้คุณค่าลดการกินอาหารค่าต่ำ\n"
                 f"(เฉลี่ย ± 95% CI; Mann-Whitney p={fmt(mwu['p_two_sided'],4)}, "
                 f"Cliff's d={fmt(eff['delta'],2)})", fontsize=10.5)
    ax.legend(fontsize=9.5)
    fig.savefig(OUT / "fig_multiseed_seed_consumption_CI.png")
    plt.close(fig)

    # ---- text report ----
    print("## Multi-seed A vs B (total raw_seed meals over the run)\n")
    print(f"- n_A = {mwu['n_A']} seeds, n_B = {mwu['n_B']} seeds, window = {a.window} ticks, "
          f"windows = {n_win}")
    print(f"- A (no learning): mean {fmt(tA[0])} +/- {fmt(tA[1])} (95% CI), SD {fmt(tA[2])}")
    print(f"- B (value learning): mean {fmt(tB[0])} +/- {fmt(tB[1])} (95% CI), SD {fmt(tB[2])}")
    if tB[0] > 0:
        print(f"- reduction: A/B = {fmt(tA[0]/tB[0],1)}x fewer low-value meals with learning")
    print(f"- Mann-Whitney U = {fmt(mwu['U'],1)}, z = {fmt(mwu['z'],2)}, "
          f"p (two-sided) = {fmt(mwu['p_two_sided'],4)}")
    print(f"- Cliff's delta = {fmt(eff['delta'],3)} ({eff['magnitude']})")
    print()
    print("| window | A mean | A 95% CI | B mean | B 95% CI |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for w in perwin:
        print(f"| {w['window']} | {fmt(w['A_mean'])} | +/-{fmt(w['A_ci'])} | "
              f"{fmt(w['B_mean'])} | +/-{fmt(w['B_ci'])} |")
    print()
    print("raw totals A:", sorted(totals_A))
    print("raw totals B:", sorted(totals_B))

    # machine-readable dump for the report
    (INDIR / "_aggregate_result.json").write_text(json.dumps({
        "n_A": mwu["n_A"], "n_B": mwu["n_B"], "window": a.window, "n_windows": n_win,
        "total_A": {"mean": tA[0], "ci95": tA[1], "sd": tA[2], "values": sorted(totals_A)},
        "total_B": {"mean": tB[0], "ci95": tB[1], "sd": tB[2], "values": sorted(totals_B)},
        "mann_whitney": mwu, "cliffs_delta": eff, "per_window": perwin,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote:", (OUT / 'fig_multiseed_seed_consumption_CI.png').name,
          "and", (INDIR / '_aggregate_result.json').name)
