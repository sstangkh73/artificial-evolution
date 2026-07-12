# -*- coding: utf-8 -*-
"""Does the 'lure' survive a STANDARD learner? (fixes red-team R2-1 strong option)

The discrimination=0 failure is analytic and rule-INDEPENDENT: any value keyed on
food type holds one number per type, so P(eat) cannot depend on a hidden age. What
IS rule-dependent is the LURE magnitude. So we re-run the two-state fruit
(fresh=toxic net~2 / aged=safe net~10, from the REAL _apply_toxin) with four
value-learning rules and ask: does fruit end up ranked above the safe staple (=>
the agent is lured into the poison)?

  L1 sim gate    -- one-shot taste, then EMA, hard pickiness gate (freezes on a bad
                    first taste -> can UNDER-count the lure)
  L2 eps-greedy  -- optimistic init, sample-average, keeps exploring (eps=0.1)
  L3 softmax     -- optimistic init, sample-average, Boltzmann choice (tau=2)
  L4 sample-avg  -- optimistic init, sample-average, greedy

Prediction: L2-L4 keep sampling -> value converges to the true mean (blend), so
they are lured MORE than the freezing gate -> the lure is not a freezing artifact.
Output: reports/figures/toxin_learner_comparison.png
"""
import math
import os
import statistics
import sys
from pathlib import Path
from random import Random
from types import SimpleNamespace

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agents.agent import Agent
from agents.body import BodyPlan
from world.environment import FOOD_ENERGY
from world import metabolism

OUT = Path(__file__).resolve().parent.parent / "reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 11,
                     "font.family": "Tahoma", "axes.unicode_minus": False,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.25, "figure.autolayout": True})

STAPLE, NOW, T, ACUTE = 5.0, 100000, 4, 50.0
SEEDS, N, TRIALS = 30, 100, 40
FRACS = [0.2, 0.3, 0.4, 0.5, 0.6]
COL = {"L1 sim gate": "#888780", "L2 eps-greedy": "#185FA5",
       "L3 softmax": "#0F6E56", "L4 sample-avg": "#BA7517"}


def _real_nets():
    """Net energy of a fresh vs aged fruit, straight from the real _apply_toxin."""
    body = BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)
    gross = int(round(metabolism.digestible_energy(
        metabolism.COMPOSITION["raw_fruit"], metabolism.FOOD_MASS["raw_fruit"], body.enzyme_profile)))
    env = SimpleNamespace(toxin_acute_penalty=ACUTE, toxin_damage_coeff=0.0,
                          toxin_detox_ticks=T, toxin_safe_window_start=0, toxin_safe_window_end=0,
                          tick_count=NOW)
    fresh = Agent(1, body, 0, 0)._apply_toxin(env, SimpleNamespace(kind="raw_fruit", created_tick=NOW), gross)
    aged = Agent(1, body, 0, 0)._apply_toxin(env, SimpleNamespace(kind="raw_fruit", created_tick=NOW - T), gross)
    return float(fresh), float(aged)


NET_FRESH, NET_AGED = _real_nets()


def _run_learner(kind, p_toxic, seed):
    rng = Random(seed)
    lured = 0
    for _ in range(N):
        if kind == "L1 sim gate":
            value = None
        else:
            value = float(NET_AGED)   # optimistic init so it samples the fruit
        n = 0
        for _ in range(TRIALS):
            fresh = rng.random() < p_toxic
            net = NET_FRESH if fresh else NET_AGED
            if kind == "L1 sim gate":
                eat = (value is None) or value >= 0.6 * max(value, STAPLE)
                if eat:
                    value = net if value is None else value + 0.3 * (net - value)
            elif kind == "L2 eps-greedy":
                eat = rng.random() < 0.1 or value > STAPLE
                if eat:
                    n += 1; value += (net - value) / n
            elif kind == "L3 softmax":
                a, b = math.exp(value / 2.0), math.exp(STAPLE / 2.0)
                eat = rng.random() < a / (a + b)
                if eat:
                    n += 1; value += (net - value) / n
            else:  # L4 sample-avg greedy
                eat = value > STAPLE
                if eat:
                    n += 1; value += (net - value) / n
        v = value if value is not None else NET_FRESH
        if v > STAPLE:
            lured += 1
    return 100.0 * lured / N


def _ci(xs):
    m = statistics.mean(xs)
    return m, (1.96 * statistics.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else 0.0)


def main():
    print(f"two-state nets from real _apply_toxin: fresh {NET_FRESH:.0f} (toxic) / aged {NET_AGED:.0f} (safe), staple {STAPLE}")
    print("analytic blend (converged value) = p*fresh + (1-p)*aged; lured when > staple:")
    for p in FRACS:
        print(f"   {int(p*100)}% toxic -> blend {p*NET_FRESH+(1-p)*NET_AGED:.1f}")
    print("\n% agents LURED (fruit value > staple), 30 seeds, 95% CI:")
    results = {}
    for kind in COL:
        results[kind] = {p: _ci([_run_learner(kind, p, s) for s in range(SEEDS)]) for p in FRACS}
        row = "  ".join(f"{int(p*100)}%:{results[kind][p][0]:3.0f}" for p in FRACS)
        print(f"  {kind:15s} {row}")

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    xs = [int(p * 100) for p in FRACS]
    for kind, c in COL.items():
        ys = [results[kind][p][0] for p in FRACS]
        es = [results[kind][p][1] for p in FRACS]
        ls = "--" if kind == "L1 sim gate" else "-"
        ax.errorbar(xs, ys, yerr=es, marker="o", ms=4, lw=2, ls=ls, color=c, label=kind, capsize=3)
    # analytic boundary: blend > staple  <=>  p < (aged-staple)/(aged-fresh)
    p_star = 100 * (NET_AGED - STAPLE) / (NET_AGED - NET_FRESH)
    ax.axvline(p_star, color="#A32D2D", ls=":", lw=1.6)
    ax.text(p_star + 0.6, 8, f"ขอบเขตเชิงวิเคราะห์\n(ค่าเฉลี่ย=อาหารปลอดภัย, p*={p_star:.0f}%)",
            fontsize=8.5, color="#A32D2D")
    ax.set_title("การถูกล่อไม่ใช่ของเฉพาะกฎเรา: กฎมาตรฐานยิ่งถูกล่อมากกว่า")
    ax.set_xlabel("% ครั้งที่เจอผลไม้เป็นพิษ (สด)")
    ax.set_ylabel("% เอเจนต์ที่ถูกล่อ (จัดผลไม้ > อาหารปลอดภัย)")
    ax.set_ylim(-5, 108); ax.legend(fontsize=9, loc="lower left")
    fig.savefig(OUT / "toxin_learner_comparison.png"); plt.close(fig)
    print("\nnote: discrimination = 0 holds for ALL of these by construction (value is keyed on"
          " food TYPE, one number per type -> decision identical at every age).")
    print("wrote", OUT / "toxin_learner_comparison.png")


if __name__ == "__main__":
    main()
