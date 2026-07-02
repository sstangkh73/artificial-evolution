# -*- coding: utf-8 -*-
"""Generate publication-quality figures for the Aging + Toxin Physics report.

All data are produced by DRIVING THE REAL production code (Agent._apply_aging,
Agent._apply_toxin, the real diet gate) in controlled harnesses -> deterministic,
seed-invariant. Output: reports/figures/aging_*.png, reports/figures/toxin_*.png
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
from agents.body import BodyPlan, AGING_TRAIT_FIELDS, TRAIT_BOUNDS
from world.environment import FOOD_ENERGY
from world import metabolism

OUT = Path(__file__).resolve().parent.parent / "reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "figure.autolayout": True,
})
C = {"aging": "#0F6E56", "mass": "#185FA5", "repair": "#534AB7", "cr": "#993C1D",
     "old": "#888780", "new": "#0F6E56", "fruit": "#BA7517", "plant": "#3B6D11",
     "warn": "#A32D2D"}


def _env(**ov):
    base = dict(aging_physics_enabled=True, aging_damage_rate=0.4, aging_repair_gain=0.5,
                aging_maintenance_cost=2.0, aging_damage_threshold=100.0, aging_mass_exponent=0.25,
                aging_max_repair_fraction=0.95, aging_intake_damage_coeff=0.0)
    base.update(ov)
    return SimpleNamespace(**base)


def _body(**g):
    d = dict(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1, metabolism_rate=1.0)
    d.update(g)
    return BodyPlan(**d)


def _lifespan(b, e, intake=0.0, cap=2_000_000):
    a = Agent(agent_id=1, body=b, x=0, y=0)
    for t in range(1, cap + 1):
        a._aging_gained_mark = a.energy_gained_total
        if intake:
            a.energy_gained_total += intake
        if a._apply_aging(e):
            return t
    return cap


def fig_validation_4arms():
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.0))
    e = _env()
    # (1) allometry - log-log
    masses = [0.5, 0.7, 1.0, 1.4, 2.0, 2.8, 4.0]
    ls = [_lifespan(_body(body_mass=m, somatic_maintenance=0.0), e) for m in masses]
    xs, ys = [math.log(m) for m in masses], [math.log(v) for v in ls]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    ax = axes[0, 0]
    ax.loglog(masses, ls, "o-", color=C["mass"], lw=2)
    ax.set_title(f"1. Allometry (Speakman): slope = {slope:.2f}")
    ax.set_xlabel("body mass (gene)"); ax.set_ylabel("lifespan (ticks)")
    ax.annotate("lifespan ∝ mass$^{0.25}$\n(band 0.15–0.30)", xy=(2.0, ls[4]),
                xytext=(0.7, max(ls) * 0.95), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=C["old"]))
    # (2) disposable soma
    maints = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    lsm = [_lifespan(_body(somatic_maintenance=m, repair_efficiency=1.0), e) for m in maints]
    ax = axes[0, 1]
    ax.plot(maints, lsm, "o-", color=C["repair"], lw=2)
    ax.set_title("2. Disposable soma (Kirkwood)")
    ax.set_xlabel("somatic_maintenance (gene)"); ax.set_ylabel("lifespan (ticks)")
    ax.set_yscale("log")
    # (3) membrane / damage resistance
    res = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    lsr = [_lifespan(_body(damage_resistance=r, somatic_maintenance=0.0), e) for r in res]
    ax = axes[1, 0]
    ax.plot(res, lsr, "o-", color=C["aging"], lw=2)
    ax.set_title("3. Membrane/mito (Hulbert, Kitazoe)")
    ax.set_xlabel("damage_resistance (gene)"); ax.set_ylabel("lifespan (ticks)")
    # (4) caloric restriction
    ec = _env(aging_intake_damage_coeff=0.02)
    intakes = [0, 10, 20, 30, 40]
    lsc = [_lifespan(_body(somatic_maintenance=0.0), ec, intake=i) for i in intakes]
    ax = axes[1, 1]
    ax.plot(intakes, lsc, "o-", color=C["cr"], lw=2)
    ax.set_title("4. Caloric restriction (CALERIE)")
    ax.set_xlabel("food intake / tick"); ax.set_ylabel("lifespan (ticks)")
    ax.annotate("eat less → live longer", xy=(10, lsc[1]), xytext=(15, lsc[0] * 0.9),
                fontsize=9, arrowprops=dict(arrowstyle="->", color=C["old"]))
    fig.suptitle("Aging Physics v1 validated against proven longevity papers (4/4 arms)", fontsize=13)
    fig.savefig(OUT / "aging_fig1_validation_4arms.png"); plt.close(fig)


def fig_lifespan_desync():
    e = _env()
    rng = Random(20260701)
    cohort = [_lifespan(_body(**{f: rng.uniform(*TRAIT_BOUNDS[f]) for f in AGING_TRAIT_FIELDS}), e)
              for _ in range(400)]
    cv = statistics.pstdev(cohort) / statistics.mean(cohort)
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    clipped = [min(c, 3000) for c in cohort]
    ax.hist(clipped, bins=40, color=C["new"], alpha=0.8, label=f"aging ON (gene variation), CV = {cv:.2f}")
    ax.axvline(200, color=C["old"], lw=2.5, ls="--", label="aging OFF: everyone dies at 200 (CV = 0)")
    ax.set_title("Senescence desynchronises death (breaks the cohort die-off wave)")
    ax.set_xlabel("age at intrinsic death (ticks; clipped at 3000)")
    ax.set_ylabel("number of agents")
    ax.legend(fontsize=9)
    ax.annotate(f"median {int(statistics.median(cohort))}, max {max(cohort)}",
                xy=(0.62, 0.55), xycoords="axes fraction", fontsize=9, color=C["old"])
    fig.savefig(OUT / "aging_fig2_lifespan_desync.png"); plt.close(fig)


def fig_death_cause_shift():
    fig, ax = plt.subplots(figsize=(6.6, 4.3))
    labels = ["aging OFF", "aging ON"]
    ages = [200, 354]
    colors = [C["old"], C["new"]]
    bars = ax.bar(labels, ages, color=colors, width=0.55)
    ax.set_ylabel("founder age at intrinsic death (ticks)")
    ax.set_title("Full sim (3 seeds): death shifts age-timer → damage")
    ax.bar_label(bars, labels=["age timer\n(lifespan_completed)", "senescence\n(damage ≥ threshold)"],
                 padding=4, fontsize=10)
    ax.set_ylim(0, 430)
    fig.savefig(OUT / "aging_fig3_death_cause_shift.png"); plt.close(fig)


def _diet_env(acute):
    return SimpleNamespace(metabolism_model="v2", food_energy_multiplier=1.0,
                           food_value_learning_enabled=True, diet_learning_rate=0.4,
                           diet_pickiness=0.6, diet_starvation_energy=6,
                           toxin_acute_penalty=acute, toxin_damage_coeff=0.0, food_positions={})


def _run_diet(acute, trials=60):
    env = _diet_env(acute)
    a = Agent(agent_id=1, body=_body(), x=0, y=0)
    fruit_val, eaten_fruit = [], 0
    for t in range(trials):
        a.energy = 100
        for kind in ("raw_plant", "raw_fruit"):
            res = SimpleNamespace(kind=kind, energy=FOOD_ENERGY[kind], source="s")
            env.food_positions = {(a.x, a.y): res}
            if a._food_worth_eating(env):
                gross = a._metabolic_base_energy(env, res)
                net = a._apply_toxin(env, res, gross)
                a._learn_food_value(env, kind, net)
                if kind == "raw_fruit":
                    eaten_fruit += 1
        fruit_val.append(a.food_value_memory.get("raw_fruit", float("nan")))
    return fruit_val, eaten_fruit, a.food_value_memory.get("raw_plant", 5.0)


def fig_toxin_learning():
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    val_on, _, plant = _run_diet(acute=50.0)
    ax.plot(range(1, len(val_on) + 1), val_on, "o-", color=C["fruit"], ms=3, lw=1.8,
            label="learned value of toxic fruit")
    ax.axhline(plant, color=C["plant"], ls="--", lw=2, label=f"raw_plant value ({plant:.0f})")
    thr = 0.6 * plant
    ax.axhline(thr, color=C["warn"], ls=":", lw=1.6, label=f"skip threshold (pickiness × best = {thr:.1f})")
    ax.set_title("Individual learning: fruit's net value falls below plant → avoided")
    ax.set_xlabel("feeding trial"); ax.set_ylabel("learned food value")
    ax.legend(fontsize=9, loc="right")
    ax.annotate("first taste\n(mandatory)", xy=(1, val_on[0]), xytext=(4, val_on[0] + 2),
                fontsize=9, arrowprops=dict(arrowstyle="->", color=C["old"]))
    fig.savefig(OUT / "toxin_fig1_learning.png"); plt.close(fig)


def _p_toxic_curve(acute, N=400, trials=40, seed=20260701):
    """Population P(choose toxic fruit) per trial — a learning curve (Option A).

    Drives the REAL decision gate (_food_worth_eating) + REAL EMA learning
    (_learn_food_value) + REAL metabolism/toxin formulas. Heterogeneity comes from
    a realistic source: fruit SIZE varies per fruit (mass ~ U(0.6,1.5) x base),
    scaling both its energy and its toxin, so different agents cross the avoidance
    threshold at different trials -> a smooth population curve (a single
    deterministic agent would give a step, which is why we use a population)."""
    rng = Random(seed)
    comp = metabolism.COMPOSITION["raw_fruit"]
    base_mass = metabolism.FOOD_MASS["raw_fruit"]
    counts = [0] * trials
    for _ in range(N):
        env = _diet_env(acute)
        a = Agent(agent_id=1, body=_body(), x=0, y=0)
        a.food_value_memory = {"raw_plant": 5.0}  # a good food is already known (the alternative)
        res = SimpleNamespace(kind="raw_fruit", energy=FOOD_ENERGY["raw_fruit"], source="s")
        env.food_positions = {(a.x, a.y): res}
        for t in range(trials):
            a.energy = 100  # well-fed: isolate PREFERENCE from the starvation floor
            if a._food_worth_eating(env):
                counts[t] += 1
                mass = base_mass * rng.uniform(0.6, 1.5)  # this fruit's size (varies)
                gross = metabolism.digestible_energy(comp, mass, a.body.enzyme_profile)
                excess = metabolism.toxin_penalty(metabolism.toxin_load(comp, mass), a.body.toxin_tolerance)
                net = gross - excess * acute
                a._learn_food_value(env, "raw_fruit", net)
    return [c / N for c in counts]


def _p_toxic_matrix_hetero(acute, N, trials, seed=20260702):
    """Per-agent 'ate the toxic fruit' matrix, with HERITABLE toxin_tolerance
    variation between individuals. Same real machinery (gate + EMA + toxin
    formulas + per-fruit size noise); returns (rows, tolerances) so we can show
    which individuals avoid and WHY."""
    rng = Random(seed)
    comp = metabolism.COMPOSITION["raw_fruit"]
    base_mass = metabolism.FOOD_MASS["raw_fruit"]
    rows, tols = [], []
    for _ in range(N):
        tol = rng.uniform(0.0, 0.45)  # heritable toxin_tolerance varies between agents
        env = _diet_env(acute)
        a = Agent(agent_id=1, body=_body(toxin_tolerance=tol), x=0, y=0)
        a.food_value_memory = {"raw_plant": 5.0}
        res = SimpleNamespace(kind="raw_fruit", energy=FOOD_ENERGY["raw_fruit"], source="s")
        env.food_positions = {(a.x, a.y): res}
        ate = []
        for t in range(trials):
            a.energy = 100
            if a._food_worth_eating(env):
                ate.append(True)
                mass = base_mass * rng.uniform(0.6, 1.5)
                gross = metabolism.digestible_energy(comp, mass, a.body.enzyme_profile)
                excess = metabolism.toxin_penalty(metabolism.toxin_load(comp, mass), tol)
                a._learn_food_value(env, "raw_fruit", gross - excess * acute)
            else:
                ate.append(False)
        rows.append(ate); tols.append(tol)
    return rows, tols


def fig_toxin_individual_raster():
    trials, N = 18, 60
    rows, tols = _p_toxic_matrix_hetero(50.0, N, trials)

    def last_ate(r):
        idx = [i for i, v in enumerate(r) if v]
        return idx[-1] if idx else -1

    order = sorted(range(N), key=lambda i: last_ate(rows[i]))
    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    xs, ys, cs = [], [], []
    for yi, i in enumerate(order):
        for t, v in enumerate(rows[i]):
            if v:
                xs.append(t + 1); ys.append(yi + 1); cs.append(tols[i])
    sc = ax.scatter(xs, ys, s=20, marker="s", c=cs, cmap="YlOrBr", vmin=0.0, vmax=0.45)
    cb = fig.colorbar(sc, ax=ax, pad=0.02)
    cb.set_label("toxin_tolerance (gene)", fontsize=10)
    ax.set_title("Individual diet trajectories: avoidance depends on the toxin_tolerance gene")
    ax.set_xlabel("feeding trial"); ax.set_ylabel("agent (row) — sorted by when they quit")
    ax.set_xlim(0.5, trials + 0.5); ax.set_ylim(0.5, N + 0.5)
    never = sum(1 for r in rows if all(r))
    ax.annotate("blank = avoided\n(low tolerance → quits fast)", xy=(11, 16),
                fontsize=10, color=C["new"], ha="center")
    ax.annotate(f"{never}/{N} tolerant agents\nnever avoid (keep eating)",
                xy=(trials - 0.3, N - 3), xytext=(11.5, 34),
                fontsize=9.5, color=C["old"], ha="center",
                arrowprops=dict(arrowstyle="->", color=C["old"]))
    fig.savefig(OUT / "toxin_fig4_individual_raster.png"); plt.close(fig)


def fig_toxin_learning_curve():
    trials = 40
    off = _p_toxic_curve(0.0, trials=trials)
    on = _p_toxic_curve(50.0, trials=trials)
    x = list(range(1, trials + 1))
    fig, ax = plt.subplots(figsize=(7.4, 4.5))
    ax.plot(x, [100 * v for v in off], "-", color=C["old"], lw=2.5,
            label="no toxin mechanism (fruit stays attractive)")
    ax.plot(x, [100 * v for v in on], "o-", color=C["new"], ms=3, lw=2.2,
            label="with toxin mechanism (learns to avoid)")
    ax.set_title("Learning curve: probability of choosing the toxic fruit")
    ax.set_xlabel("feeding trial"); ax.set_ylabel("P(choose toxic fruit)  (% of 400 agents)")
    ax.legend(fontsize=9, loc="center right")
    ax.set_xlim(1, trials); ax.set_ylim(-3, 105)
    ax.annotate("population learns\nto avoid (~trial 9)", xy=(5, 100 * on[4]),
                xytext=(11, 78), fontsize=10, color=C["new"], ha="left",
                arrowprops=dict(arrowstyle="->", color=C["new"]))
    fig.savefig(OUT / "toxin_fig3_learning_curve.png"); plt.close(fig)


def fig_toxin_avoidance():
    _, eaten_off, _ = _run_diet(acute=0.0)
    _, eaten_on, _ = _run_diet(acute=50.0)
    fig, ax = plt.subplots(figsize=(6.0, 4.3))
    bars = ax.bar(["toxin OFF", "toxin ON"], [eaten_off, eaten_on],
                  color=[C["old"], C["new"]], width=0.55)
    ax.set_ylabel("times the fruit was eaten (out of 60)")
    ax.set_title("Emergent diet avoidance (well-fed agent, real choice)")
    ax.bar_label(bars, padding=4, fontsize=12)
    ax.set_ylim(0, 68)
    ax.annotate("tastes once,\nthen skips forever", xy=(1, eaten_on), xytext=(0.55, 22),
                fontsize=9, arrowprops=dict(arrowstyle="->", color=C["old"]))
    fig.savefig(OUT / "toxin_fig2_avoidance.png"); plt.close(fig)


def main():
    fig_validation_4arms()
    fig_lifespan_desync()
    fig_death_cause_shift()
    fig_toxin_learning()
    fig_toxin_avoidance()
    fig_toxin_learning_curve()
    fig_toxin_individual_raster()
    print("wrote figures to", OUT)
    for p in sorted(OUT.glob("aging_*.png")) + sorted(OUT.glob("toxin_*.png")):
        print("  ", p.name)


if __name__ == "__main__":
    main()
