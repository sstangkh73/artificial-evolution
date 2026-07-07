# -*- coding: utf-8 -*-
"""Multi-seed replication with 95% CIs for the age-dependent-toxicity results
(fixes red-team item A: no more deterministic n=1). Drives the REAL code
(_apply_toxin with real food age, real _food_worth_eating gate, real EMA learning)
across S seeds x N agents, and reports mean +/- 95% CI for every headline number
used in the ALIFE abstract. Output: reports/figures/toxin_multiseed_ci.png
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
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "figure.autolayout": True,
})
LINE, TOXIC, SAFE, IDEAL, OLD = "#BA7517", "#A32D2D", "#0F6E56", "#185FA5", "#888780"

SEEDS, N, TRIALS = 30, 100, 40
ACUTE, STAPLE, NOW = 50.0, 5.0, 100000
COMP = metabolism.COMPOSITION["raw_fruit"]
MASS = metabolism.FOOD_MASS["raw_fruit"]


def _body():
    return BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)


def _gross(agent):
    return metabolism.digestible_energy(COMP, MASS, agent.body.enzyme_profile)


def _fruit(age):
    return SimpleNamespace(kind="raw_fruit", energy=FOOD_ENERGY["raw_fruit"], source="s",
                           created_tick=NOW - age)


def _env(**ov):
    base = dict(food_value_learning_enabled=True, diet_learning_rate=0.3, diet_pickiness=0.6,
                diet_starvation_energy=6, toxin_acute_penalty=ACUTE, toxin_damage_coeff=0.0,
                toxin_detox_ticks=0, toxin_safe_window_start=0, toxin_safe_window_end=0,
                tick_count=NOW, food_positions={})
    base.update(ov)
    return SimpleNamespace(**base)


def _ci95(xs):
    m = statistics.mean(xs)
    if len(xs) < 2:
        return m, 0.0
    sem = statistics.stdev(xs) / math.sqrt(len(xs))
    return m, 1.96 * sem


def result1_seed(seed, T=4):
    """Monotonic detox: toxic (age<T) -> safe (age>=T). ages ~ U(0,2T): 50% fresh."""
    rng = Random(seed)
    blends, lured, toxic_bites, total = [], 0, 0, 0
    for _ in range(N):
        env = _env(toxin_detox_ticks=T)
        a = Agent(agent_id=1, body=_body(), x=0, y=0)
        a.food_value_memory = {"raw_plant": STAPLE}
        for _ in range(TRIALS):
            a.energy = 100
            age = rng.randrange(0, 2 * T)
            res = _fruit(age)
            env.food_positions = {(a.x, a.y): res}
            if a._food_worth_eating(env):
                a._learn_food_value(env, "raw_fruit", a._apply_toxin(env, res, int(round(_gross(a)))))
                total += 1
                if age < T:
                    toxic_bites += 1
        v = a.food_value_memory["raw_fruit"]
        blends.append(v)
        if v > STAPLE:
            lured += 1
    return statistics.mean(blends), 100 * lured / N, 100 * toxic_bites / max(1, total)


def result2_seed(seed, start=3, end=7, maxage=10):
    """Non-monotonic window [start,end): toxic -> safe -> toxic. ages ~ U(0,maxage)."""
    rng = Random(seed)
    eat_in, eat_out, seen_in, seen_out = 0, 0, 0, 0
    toxic_bites, total = 0, 0
    for _ in range(N):
        env = _env(toxin_safe_window_start=start, toxin_safe_window_end=end)
        a = Agent(agent_id=1, body=_body(), x=0, y=0)
        a.food_value_memory = {"raw_plant": STAPLE}
        for _ in range(TRIALS):
            a.energy = 100
            age = rng.randrange(0, maxage)
            res = _fruit(age)
            env.food_positions = {(a.x, a.y): res}
            if a._food_worth_eating(env):
                a._learn_food_value(env, "raw_fruit", a._apply_toxin(env, res, int(round(_gross(a)))))
                total += 1
                if not (start <= age < end):
                    toxic_bites += 1
        for age in range(maxage):
            a.energy = 100
            env.food_positions = {(a.x, a.y): _fruit(age)}
            eat = a._food_worth_eating(env)
            if start <= age < end:
                seen_in += 1; eat_in += 1 if eat else 0
            else:
                seen_out += 1; eat_out += 1 if eat else 0
    p_in = 100 * eat_in / max(1, seen_in)
    p_out = 100 * eat_out / max(1, seen_out)
    return p_in, p_out, (p_in - p_out), 100 * toxic_bites / max(1, total)


def main():
    r1 = [result1_seed(s) for s in range(SEEDS)]
    blend = _ci95([x[0] for x in r1]); lured = _ci95([x[1] for x in r1]); tox1 = _ci95([x[2] for x in r1])
    r2 = [result2_seed(s) for s in range(SEEDS)]
    pin = _ci95([x[0] for x in r2]); pout = _ci95([x[1] for x in r2])
    disc = _ci95([x[2] for x in r2]); tox2 = _ci95([x[3] for x in r2])

    print(f"=== {SEEDS} seeds x {N} agents x {TRIALS} trials (mean +/- 95% CI) ===")
    print("RESULT 1 (monotonic detox, fresh toxic net~2 / aged safe net~10, staple 5):")
    print(f"  blended learned value  = {blend[0]:.2f} +/- {blend[1]:.2f}   (> staple 5 => 'lure')")
    print(f"  % agents lured (v>5)   = {lured[0]:.0f}% +/- {lured[1]:.0f}%")
    print(f"  % of fruit meals toxic = {tox1[0]:.0f}% +/- {tox1[1]:.0f}%")
    print("RESULT 2 (non-monotonic window [3,7]):")
    print(f"  P(eat | in window)     = {pin[0]:.0f}% +/- {pin[1]:.0f}%")
    print(f"  P(eat | out of window) = {pout[0]:.0f}% +/- {pout[1]:.0f}%")
    print(f"  discrimination (in-out)= {disc[0]:.1f}pts +/- {disc[1]:.1f}   (~0 => cannot target window)")
    print(f"  % of meals toxic       = {tox2[0]:.0f}% +/- {tox2[1]:.0f}%")

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.0, 4.4))
    # Left: Result 1 headline bars with CI
    labels = ["blended\nvalue", "% agents\nlured", "% fruit\nmeals toxic"]
    vals = [blend[0], lured[0], tox1[0]]; errs = [blend[1], lured[1], tox1[1]]
    cols = [LINE, TOXIC, TOXIC]
    bars = axL.bar(labels, vals, yerr=errs, capsize=5, color=cols, alpha=0.85)
    axL.axhline(STAPLE, color=OLD, ls=":", lw=1.5)
    axL.text(0.02, STAPLE + 0.3, "staple value 5", color=OLD, fontsize=8.5, transform=axL.get_yaxis_transform())
    axL.set_title(f"Result 1: monotonic detox ({SEEDS} seeds, 95% CI)")
    axL.set_ylabel("value  /  % of agents or meals")
    axL.bar_label(bars, fmt="%.1f", padding=3, fontsize=9)
    axL.set_ylim(0, max(vals) + max(errs) + 12)
    # Right: Result 2 discrimination with CI (in vs out of window)
    b2 = axR.bar(["P(eat|in\nwindow)", "P(eat|out of\nwindow)"], [pin[0], pout[0]],
                 yerr=[pin[1], pout[1]], capsize=5, color=[SAFE, TOXIC], alpha=0.85)
    axR.bar_label(b2, fmt="%.0f%%", padding=3, fontsize=10)
    axR.set_title(f"Result 2: safe window (discrimination = {disc[0]:.1f} pts, 95% CI)")
    axR.set_ylabel("P(choose to eat)  (%)")
    axR.set_ylim(0, max(pin[0], pout[0]) + max(pin[1], pout[1]) + 10)
    axR.annotate(f"ideal gap = 100 pts;\nlearner gap = {disc[0]:.1f} pts → age-blind",
                 xy=(0.5, max(pin[0], pout[0])), xytext=(0.15, max(pin[0], pout[0]) + 4),
                 fontsize=9, color=OLD)
    fig.suptitle(f"Multi-seed replication ({SEEDS} seeds x {N} agents x {TRIALS} trials): the failures are robust, not a single-seed artifact",
                 fontsize=10.5)
    fig.savefig(OUT / "toxin_multiseed_ci.png"); plt.close(fig)
    print("wrote", OUT / "toxin_multiseed_ci.png")


if __name__ == "__main__":
    main()
