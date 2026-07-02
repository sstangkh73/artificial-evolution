# -*- coding: utf-8 -*-
"""Figures for the 'store-to-detoxify / deferred consumption' experiment design.

fig1 (REAL, harness): the learning ONSET -- a population starts eating the fresh
toxic fruit, learns its net value is bad, and stops eating it now. Drives the real
gate + EMA + toxin formula.

fig2 (PREDICTED, hypothesis toy): the deferral SIGNATURE we would test for -- once
an agent has learned "fresh = toxic" it does not just avoid, it SEES the fruit and
DEFERS (stores it); the stored fruit detoxifies after T and is eaten safely later.
The onset per agent is taken from the real fig1 learning; the defer/store + delayed
safe-meal payoff is the hypothesised behaviour (NOT in the sim yet).
Output: reports/figures/design_store_defer_fig1_onset.png / _fig2_deferral.png
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
EAT, DEFER, SAFE, OLD = "#A32D2D", "#185FA5", "#0F6E56", "#888780"


def _body():
    return BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)


def _onsets(N, trials, acute=50.0, seed=20260704):
    """Per-agent trial at which it stops eating the fresh toxic fruit (real learning)."""
    rng = Random(seed)
    comp = metabolism.COMPOSITION["raw_fruit"]
    base_mass = metabolism.FOOD_MASS["raw_fruit"]
    onset, eat_frac = [], [0] * trials
    for _ in range(N):
        env = SimpleNamespace(food_value_learning_enabled=True, diet_learning_rate=0.4,
                              diet_pickiness=0.6, diet_starvation_energy=6, food_positions={})
        a = Agent(agent_id=1, body=_body(), x=0, y=0)
        a.food_value_memory = {"raw_plant": 5.0}
        res = SimpleNamespace(kind="raw_fruit", energy=FOOD_ENERGY["raw_fruit"], source="s")
        env.food_positions = {(a.x, a.y): res}
        quit_at = trials
        for t in range(trials):
            a.energy = 100
            if a._food_worth_eating(env):
                eat_frac[t] += 1
                mass = base_mass * rng.uniform(0.6, 1.5)
                gross = metabolism.digestible_energy(comp, mass, a.body.enzyme_profile)
                excess = metabolism.toxin_penalty(metabolism.toxin_load(comp, mass), a.body.toxin_tolerance)
                a._learn_food_value(env, "raw_fruit", gross - excess * acute)
            else:
                quit_at = min(quit_at, t)
        onset.append(quit_at)
    return onset, [c / N for c in eat_frac]


def fig1_onset():
    trials, N = 20, 400
    _, eat_frac = _onsets(N, trials)
    x = list(range(1, trials + 1))
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.plot(x, [100 * v for v in eat_frac], "o-", color=EAT, ms=3, lw=2.2)
    ax.set_title("Starts eating the fresh toxic fruit, then learns to stop")
    ax.set_xlabel("feeding trial"); ax.set_ylabel("P(eat the fresh fruit now)  (% of agents)")
    ax.set_xlim(1, trials); ax.set_ylim(-4, 108)
    ax.annotate("① starts eating\n(must taste to learn)", xy=(1, 100), xytext=(2.2, 74),
                fontsize=9.5, color=OLD, arrowprops=dict(arrowstyle="->", color=OLD))
    ax.annotate("② learning: net value\nfound to be bad", xy=(3, 100 * eat_frac[2]),
                xytext=(5.5, 55), fontsize=9.5, color=OLD, arrowprops=dict(arrowstyle="->", color=OLD))
    ax.annotate("③ stops eating it now", xy=(11, 2), xytext=(11, 20),
                fontsize=9.5, color=OLD, ha="center", arrowprops=dict(arrowstyle="->", color=OLD))
    fig.savefig(OUT / "design_store_defer_fig1_onset.png"); plt.close(fig)


def fig2_deferral():
    trials, N, T = 22, 400, 3
    onset, _ = _onsets(N, trials)
    eat_now = [sum(1 for o in onset if t < o) / N for t in range(trials)]         # not learned yet
    defer = [sum(1 for o in onset if t >= o) / N for t in range(trials)]          # learned -> sees & defers/stores
    safe = [sum(1 for o in onset if t >= o + T) / N for t in range(trials)]       # stored long enough -> safe meal
    x = list(range(1, trials + 1))
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.fill_between(x, 0, [100 * v for v in eat_now], color=EAT, alpha=0.85,
                    label="eats it NOW (fresh, toxic)")
    ax.fill_between(x, [100 * v for v in eat_now], [100 * (eat_now[i] + defer[i]) for i in range(trials)],
                    color=DEFER, alpha=0.8, label="SEES it but defers → stores")
    ax.plot(x, [100 * v for v in safe], "--", color=SAFE, lw=2.6,
            label=f"later eats it SAFELY from storage (age ≥ {T})")
    ax.set_title("PREDICTED signature: 'sees it, but not now' → store, wait, eat safely")
    ax.set_xlabel("feeding trial"); ax.set_ylabel("share of agents seeing the fruit (%)")
    ax.set_xlim(1, trials); ax.set_ylim(0, 108)
    ax.legend(fontsize=8.8, loc="center right", framealpha=0.92)
    ax.annotate("detox lag T", xy=(4.5, 8), xytext=(7.5, 24), fontsize=9, color=SAFE,
                arrowprops=dict(arrowstyle="->", color=SAFE))
    fig.suptitle("PREDICTED (hypothesis toy — deferral/storage NOT yet in the sim)", fontsize=11, color=OLD)
    fig.savefig(OUT / "design_store_defer_fig2_deferral.png"); plt.close(fig)


if __name__ == "__main__":
    fig1_onset()
    fig2_deferral()
    print("wrote design_store_defer_fig1_onset.png and _fig2_deferral.png")
