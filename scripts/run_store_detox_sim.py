# -*- coding: utf-8 -*-
"""First sim run of age-dependent toxicity: what does the CURRENT (per-kind) diet
learner actually do when the same fruit is toxic while fresh and safe once aged?

Drives the REAL production code end-to-end: env.toxin_detox_ticks makes
_apply_toxin compute each fruit's age from resource.created_tick vs env.tick_count,
scale the toxin by potency, feed the net energy into the REAL _learn_food_value,
and gate eating with the REAL _food_worth_eating. Controlled (well-fed) so the
foraging-starvation floor does not mask the learning. Output figure:
reports/figures/store_detox_sim_result.png
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
LINE, FRESH, AGED, IDEAL, OLD = "#BA7517", "#A32D2D", "#0F6E56", "#185FA5", "#888780"

T = 4          # detox age (ticks): fresh = age < T (toxic), aged = age >= T (safe)
ACUTE = 50.0
NOW = 100000   # a fixed "current tick"; fruit age set via created_tick


def _body():
    return BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)


def _env():
    return SimpleNamespace(
        food_value_learning_enabled=True, diet_learning_rate=0.3, diet_pickiness=0.6,
        diet_starvation_energy=6, toxin_acute_penalty=ACUTE, toxin_damage_coeff=0.0,
        toxin_detox_ticks=T, tick_count=NOW, food_positions={},
    )


def _fruit(age):
    return SimpleNamespace(kind="raw_fruit", energy=FOOD_ENERGY["raw_fruit"],
                           source="s", created_tick=NOW - age)


def _gross(agent):
    comp = metabolism.COMPOSITION["raw_fruit"]
    return metabolism.digestible_energy(comp, metabolism.FOOD_MASS["raw_fruit"], agent.body.enzyme_profile)


def run():
    rng = Random(20260705)
    env = _env()
    a = Agent(agent_id=1, body=_body(), x=0, y=0)
    a.food_value_memory = {"raw_plant": 5.0}

    trials = 60
    val_traj, toxic_bites, total_bites = [], 0, 0
    for _ in range(trials):
        a.energy = 100                       # well-fed: isolate preference from starvation
        age = rng.randrange(0, 2 * T)        # ~50% fresh (toxic), ~50% aged (safe)
        res = _fruit(age)
        env.food_positions = {(a.x, a.y): res}
        if a._food_worth_eating(env):
            net = a._apply_toxin(env, res, int(round(_gross(a))))
            a._learn_food_value(env, "raw_fruit", net)
            total_bites += 1
            if age < T:
                toxic_bites += 1
        val_traj.append(a.food_value_memory["raw_fruit"])

    # after learning: probe the decision at each specific food age (does it discriminate?)
    ages = list(range(0, 2 * T))
    p_eat = []
    for age in ages:
        a.energy = 100
        env.food_positions = {(a.x, a.y): _fruit(age)}
        p_eat.append(1 if a._food_worth_eating(env) else 0)

    net_fresh = int(round(_gross(a))) - 0.16 * ACUTE
    net_aged = int(round(_gross(a)))
    toxic_rate = toxic_bites / total_bites if total_bites else 0.0
    return val_traj, ages, p_eat, net_fresh, net_aged, toxic_rate, total_bites, trials


def make_figure():
    val_traj, ages, p_eat, net_fresh, net_aged, toxic_rate, bites, trials = run()
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.0, 4.4))

    axL.plot(range(1, len(val_traj) + 1), val_traj, "-", color=LINE, lw=2.2, label="learned value (keyed on KIND)")
    axL.axhline(net_aged, color=AGED, ls="--", lw=1.7, label=f"true if AGED/safe ({net_aged:.0f})")
    axL.axhline(net_fresh, color=FRESH, ls="--", lw=1.7, label=f"true if FRESH/toxic ({net_fresh:.0f})")
    axL.axhline(5.0, color=OLD, ls=":", lw=1.5, label="raw_plant value (5)")
    axL.set_title("Real _apply_toxin: value blends fresh+aged")
    axL.set_xlabel("feeding trial"); axL.set_ylabel("learned food value")
    axL.set_ylim(0, 12); axL.legend(fontsize=8, loc="upper right", framealpha=0.92)

    axR.step(ages, p_eat, where="mid", color=LINE, lw=2.6, label="current learner (per-kind)")
    axR.step(ages, [0 if ag < T else 1 for ag in ages], where="mid", color=IDEAL, lw=2.4, ls="--",
             label="ideal (eat only aged)")
    axR.axvspan(-0.5, T - 0.5, color=FRESH, alpha=0.08)
    axR.set_title("Does it avoid the fresh (toxic) fruit by age?")
    axR.set_xlabel("food age (ticks)"); axR.set_ylabel("P(choose to eat)")
    axR.set_yticks([0, 1]); axR.set_ylim(-0.15, 1.35); axR.set_xlim(-0.5, 2 * T - 0.5)
    axR.legend(fontsize=8.5, loc="center right", framealpha=0.92)
    axR.annotate(f"eats ALL ages the same →\n{toxic_rate*100:.0f}% of its fruit meals were TOXIC (fresh)",
                 xy=(1, 1.0), xytext=(1.2, 0.42), fontsize=9, color=OLD,
                 arrowprops=dict(arrowstyle="->", color=OLD))
    axR.annotate("toxic (fresh)", xy=(1.2, 1.22), fontsize=9, color=FRESH, ha="center")

    fig.suptitle("SIM RESULT: age-dependent detox makes the toxic food look GOOD on average → per-kind learner walks into the poison",
                 fontsize=11)
    fig.savefig(OUT / "store_detox_sim_result.png"); plt.close(fig)
    print(f"blend value = {val_traj[-1]:.2f} | fresh net = {net_fresh:.1f} | aged net = {net_aged:.1f}")
    print(f"P(eat) by age (0..{2*T-1}) = {p_eat}  (flat = no discrimination)")
    print(f"toxic (fresh) fraction of fruit meals = {toxic_rate*100:.0f}%  over {bites}/{trials} bites")


if __name__ == "__main__":
    make_figure()
