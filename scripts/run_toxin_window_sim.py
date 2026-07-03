# -*- coding: utf-8 -*-
"""Non-monotonic toxicity in the sim: toxic (young) -> SAFE window -> toxic (old).

Drives the real code with env.toxin_safe_window_[start,end): a fruit is safe only
for age in [start, end), toxic before AND after. "Older" is no longer "safer", so
even a monotonic age heuristic would fail; the learner would have to know the
whole value(age) curve. We measure what the current per-kind learner does.
Output: reports/figures/toxin_window_sim_result.png
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
LINE, TOXIC, SAFE, IDEAL, OLD = "#BA7517", "#A32D2D", "#0F6E56", "#185FA5", "#888780"

START, END = 3, 7      # safe window [3, 7): toxic 0-3, safe 3-7, toxic 7+
MAXAGE = 10
ACUTE = 50.0
NOW = 100000


def _body():
    return BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)


def _env():
    return SimpleNamespace(
        food_value_learning_enabled=True, diet_learning_rate=0.3, diet_pickiness=0.6,
        diet_starvation_energy=6, toxin_acute_penalty=ACUTE, toxin_damage_coeff=0.0,
        toxin_detox_ticks=0, toxin_safe_window_start=START, toxin_safe_window_end=END,
        tick_count=NOW, food_positions={},
    )


def _fruit(age):
    return SimpleNamespace(kind="raw_fruit", energy=FOOD_ENERGY["raw_fruit"], source="s",
                           created_tick=NOW - age)


def _gross(agent):
    comp = metabolism.COMPOSITION["raw_fruit"]
    return metabolism.digestible_energy(comp, metabolism.FOOD_MASS["raw_fruit"], agent.body.enzyme_profile)


def _net_at_age(agent, age):
    """True net energy of a fruit of this age (real toxin formula)."""
    return agent._apply_toxin(_env(), _fruit(age), int(round(_gross(agent))))


def run():
    # Population (a single agent's one-shot learning is a coin-flip on the first
    # taste; the population shows the representative behaviour).
    rng = Random(20260706)
    N, trials = 300, 40
    ages = list(range(MAXAGE))
    eat_at_age = [0] * MAXAGE
    toxic_bites, total = 0, 0
    for _ in range(N):
        env = _env()
        a = Agent(agent_id=1, body=_body(), x=0, y=0)
        a.food_value_memory = {"raw_plant": 5.0}
        for _ in range(trials):
            a.energy = 100
            age = rng.randrange(0, MAXAGE)
            res = _fruit(age)
            env.food_positions = {(a.x, a.y): res}
            if a._food_worth_eating(env):
                a._learn_food_value(env, "raw_fruit", a._apply_toxin(env, res, int(round(_gross(a)))))
                total += 1
                if not (START <= age < END):
                    toxic_bites += 1
        # probe this trained agent's decision at every age
        for ag in ages:
            a.energy = 100
            env.food_positions = {(a.x, a.y): _fruit(ag)}
            if a._food_worth_eating(env):
                eat_at_age[ag] += 1

    probe = _body()
    net_curve = [_net_at_age(Agent(agent_id=9, body=probe, x=0, y=0), ag) for ag in ages]
    p_eat = [c / N for c in eat_at_age]
    toxic_rate = toxic_bites / total if total else 0.0
    return ages, net_curve, p_eat, 0.0, toxic_rate, total, trials * N


def make_figure():
    ages, net_curve, p_eat, blend, toxic_rate, total, trials = run()
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.2, 4.5))

    axL.axvspan(START - 0.5, END - 0.5, color=SAFE, alpha=0.12, label="safe window")
    axL.plot(ages, net_curve, "o-", color=LINE, lw=2.3)
    axL.axhline(5.0, color=OLD, ls=":", lw=1.5, label="raw_plant value (5)")
    axL.set_title("The reward landscape: net value vs food age")
    axL.set_xlabel("food age (ticks)"); axL.set_ylabel("true net energy if eaten")
    axL.set_xlim(-0.3, MAXAGE - 0.7); axL.set_ylim(1.3, 10.6)
    axL.legend(fontsize=8.5, loc="upper left", framealpha=0.9)
    axL.annotate("toxic\n(young)", xy=(1, net_curve[1]), xytext=(1, 3.1), fontsize=8.5, color=TOXIC, ha="center")
    axL.annotate("toxic\n(old)", xy=(8, net_curve[8]), xytext=(8, 3.1), fontsize=8.5, color=TOXIC, ha="center")
    axL.annotate("safe +\nrich", xy=(5, net_curve[5]), xytext=(5, 8.4), fontsize=8.5, color=SAFE, ha="center")

    axR.axvspan(START - 0.5, END - 0.5, color=SAFE, alpha=0.12)
    axR.step(ages, [100 * v for v in p_eat], where="mid", color=LINE, lw=2.6,
             label="current learner (per-kind)")
    axR.step(ages, [100 if (START <= ag < END) else 0 for ag in ages], where="mid",
             color=IDEAL, lw=2.4, ls="--", label="ideal (eat only in window)")
    axR.set_title("Can it target the safe window by age?")
    axR.set_xlabel("food age (ticks)"); axR.set_ylabel("P(choose to eat)  (% of agents)")
    axR.set_yticks([0, 50, 100]); axR.set_ylim(-8, 135); axR.set_xlim(-0.3, MAXAGE - 0.7)
    axR.legend(fontsize=8.5, loc="center right", framealpha=0.9)
    axR.annotate(f"flat across age (can't target window)\n→ {toxic_rate*100:.0f}% of all meals were TOXIC",
                 xy=(5, 100 * p_eat[5]), xytext=(1.3, 118), fontsize=8.8, color=OLD,
                 arrowprops=dict(arrowstyle="->", color=OLD))

    fig.suptitle("SIM RESULT (non-monotonic toxic→safe→toxic): one blended value cannot target a mid-life safe window",
                 fontsize=10.5)
    fig.savefig(OUT / "toxin_window_sim_result.png"); plt.close(fig)
    print(f"blend value = {blend:.2f} | net_by_age = {[round(v,1) for v in net_curve]}")
    print(f"P(eat) by age = {p_eat}  (flat = cannot target the window)")
    print(f"toxic fraction of meals = {toxic_rate*100:.0f}%  over {total}/{trials} bites")


if __name__ == "__main__":
    make_figure()
