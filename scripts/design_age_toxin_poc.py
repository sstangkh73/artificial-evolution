# -*- coding: utf-8 -*-
"""Proof-of-concept figure for the age-dependent-toxicity EXPERIMENT DESIGN.

NOT full-sim results: a harness proof-of-concept that drives the REAL per-kind
EMA learner (_learn_food_value) with the REAL toxin formula, where a fruit is
toxic while fresh and safe once aged. It shows the predicted "strange" outcome:
a learner keyed on food KIND collapses the two hidden states (fresh/aged) into a
single blended value that matches NEITHER -> it cannot form the optimal
eat-aged/avoid-fresh policy. Output: reports/figures/design_age_toxin_poc.png
"""
import os
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
BLEND, FRESH, AGED, IDEAL, OLD = "#BA7517", "#A32D2D", "#0F6E56", "#185FA5", "#888780"


def _body():
    return BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)


def _net(age, T, acute=50.0):
    """Real net energy of a fruit of a given age (toxic while fresh, safe once aged)."""
    comp = metabolism.COMPOSITION["raw_fruit"]
    mass = metabolism.FOOD_MASS["raw_fruit"]
    body = _body()
    gross = metabolism.digestible_energy(comp, mass, body.enzyme_profile)
    detox = 0.0 if age >= T else 1.0            # step detox after T ticks (design default)
    load = metabolism.toxin_load(comp, mass) * detox
    excess = metabolism.toxin_penalty(load, body.toxin_tolerance)
    return gross - excess * acute, gross


def make_figure():
    T = 3                       # detox age (the "3 days")
    p_fresh = 0.5               # fraction of encountered fruit still fresh
    rng = Random(20260703)
    env = SimpleNamespace(food_value_learning_enabled=True, diet_learning_rate=0.2)
    a = Agent(agent_id=1, body=_body(), x=0, y=0)

    net_fresh, gross = _net(0, T)
    net_aged, _ = _net(T, T)
    traj = []
    for _ in range(60):
        age = 0 if rng.random() < p_fresh else T          # encounter a fresh or an aged fruit
        net, _ = _net(age, T)
        a._learn_food_value(env, "raw_fruit", net)         # REAL per-kind EMA
        traj.append(a.food_value_memory["raw_fruit"])
    blend = traj[-1]

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.0, 4.4))

    # LEFT: one blended value for two realities
    axL.plot(range(1, len(traj) + 1), traj, "-", color=BLEND, lw=2.4, label="learned value (keyed on KIND)")
    axL.axhline(net_aged, color=AGED, ls="--", lw=1.8, label=f"true value if AGED/safe ({net_aged:.0f})")
    axL.axhline(net_fresh, color=FRESH, ls="--", lw=1.8, label=f"true value if FRESH/toxic ({net_fresh:.0f})")
    axL.set_title("Per-kind learner blends two hidden states into one")
    axL.set_xlabel("feeding trial"); axL.set_ylabel("learned food value")
    axL.legend(fontsize=8.5, loc="center left", framealpha=0.92)
    axL.set_ylim(0, 11.5)
    axL.annotate(f"lands ≈{blend:.1f} —\nmatches NEITHER", xy=(len(traj), blend),
                 xytext=(len(traj) - 20, 1.2), fontsize=9.5, color=OLD, ha="left",
                 arrowprops=dict(arrowstyle="->", color=OLD))

    # RIGHT: policy vs food age -- no-cue (flat) vs ideal (step)
    ages = list(range(0, 7))
    plant = 5.0
    thr = 0.6 * plant
    eat_nocue = [1 if blend >= thr else 0 for _ in ages]       # one value -> same choice at every age
    eat_ideal = [0 if ag < T else 1 for ag in ages]            # eat only once detoxified
    axR.step(ages, eat_nocue, where="mid", color=BLEND, lw=2.6, label="no cue, keyed on kind (current)")
    axR.step(ages, eat_ideal, where="mid", color=IDEAL, lw=2.6, ls="--", label="ideal: cue + state-conditional")
    axR.axvspan(-0.5, T - 0.5, color=FRESH, alpha=0.08)
    axR.set_title("Resulting policy: does the agent track food age?")
    axR.set_xlabel("food age (ticks)"); axR.set_ylabel("P(choose to eat)")
    axR.set_yticks([0, 1]); axR.set_ylim(-0.15, 1.3); axR.set_xlim(-0.5, 6.5)
    axR.legend(fontsize=8.5, loc="center left", framealpha=0.92)
    axR.annotate("toxic while fresh", xy=(1, 1.16), fontsize=9, color=FRESH, ha="center")
    axR.annotate("eats the poison\nby mistake", xy=(1, 1.0), xytext=(4.0, 0.5), fontsize=9,
                 color=OLD, ha="center", arrowprops=dict(arrowstyle="->", color=OLD))

    fig.suptitle("PREDICTED (proof-of-concept in harness): age-dependent toxicity breaks per-kind diet learning",
                 fontsize=12)
    fig.savefig(OUT / "design_age_toxin_poc.png"); plt.close(fig)
    print("wrote", OUT / "design_age_toxin_poc.png", "| blend =", round(blend, 2))


if __name__ == "__main__":
    make_figure()
