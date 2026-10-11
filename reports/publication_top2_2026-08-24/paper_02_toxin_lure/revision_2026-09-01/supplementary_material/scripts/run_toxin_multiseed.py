# -*- coding: utf-8 -*-
"""Multi-seed replication with 95% CIs + optimal-gap, using a clean TWO-STATE model
(fixes red-team A, I, and the model-consistency issue the lure sweep exposed).

Two unambiguous hidden states: a fruit is FRESH (age 0 -> toxic, net ~2) with
probability p, or AGED (age >= detox -> safe, net ~10). This avoids the linear-
detox tolerance fuzz that mislabelled partially-aged fruit as toxic. Drives the
real _apply_toxin + gate + EMA. Reports, with 95% CIs over seeds:
  R1  lured% (learned fruit value > safe staple) vs fraction-toxic, plus the
      gap to an age-aware optimal agent;
  R2  discrimination inside vs outside a non-monotonic safe window.
Output: reports/figures/toxin_multiseed_ci.png
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
    "font.family": "Tahoma", "axes.unicode_minus": False,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "figure.autolayout": True,
})
LINE, TOXIC, SAFE, IDEAL, OLD = "#BA7517", "#A32D2D", "#0F6E56", "#185FA5", "#888780"

SEEDS, N, TRIALS = 30, 100, 40
ACUTE, STAPLE, NOW, T = 50.0, 5.0, 100000, 4
COMP = metabolism.COMPOSITION["raw_fruit"]
MASS = metabolism.FOOD_MASS["raw_fruit"]


def _body():
    return BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)


def _gross(body):
    return metabolism.digestible_energy(COMP, MASS, body.enzyme_profile)


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
    return m, 1.96 * statistics.stdev(xs) / math.sqrt(len(xs))


def result1_seed(seed, p_toxic):
    """Two states: FRESH (age 0, toxic) w.p. p_toxic, else AGED (age T, safe)."""
    rng = Random(seed)
    lured, toxic_bites, total, energy = 0, 0, 0, 0.0
    for _ in range(N):
        env = _env(toxin_detox_ticks=T)
        a = Agent(agent_id=1, body=_body(), x=0, y=0)
        a.food_value_memory = {"raw_plant": STAPLE}
        for _ in range(TRIALS):
            a.energy = 100
            fresh = rng.random() < p_toxic
            res = _fruit(0 if fresh else T)
            env.food_positions = {(a.x, a.y): res}
            if a._food_worth_eating(env):
                net = a._apply_toxin(env, res, int(round(_gross(a.body))))
                a._learn_food_value(env, "raw_fruit", net)
                total += 1; energy += net
                if fresh:
                    toxic_bites += 1
        if a.food_value_memory["raw_fruit"] > STAPLE:
            lured += 1
    pct_lured = 100 * lured / N
    pct_toxic = 100 * toxic_bites / max(1, total)
    energy_per = energy / max(1, total)
    return pct_lured, pct_toxic, energy_per


def result2_seed(seed, start=3, end=7, maxage=10):
    rng = Random(seed)
    eat_in, eat_out, seen_in, seen_out, toxic, total = 0, 0, 0, 0, 0, 0
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
                a._learn_food_value(env, "raw_fruit", a._apply_toxin(env, res, int(round(_gross(a.body)))))
                total += 1
                if not (start <= age < end):
                    toxic += 1
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
    return p_in, p_out, p_in - p_out, 100 * toxic / max(1, total)


def main():
    fracs = [0.2, 0.3, 0.4, 0.5, 0.6]
    lured_curve = {f: _ci95([result1_seed(s, f)[0] for s in range(SEEDS)]) for f in fracs}

    # headline point + optimal gap at a balanced-but-clear config (p=0.3 toxic)
    P0 = 0.3
    r1 = [result1_seed(s, P0) for s in range(SEEDS)]
    lured0 = _ci95([x[0] for x in r1]); toxic0 = _ci95([x[1] for x in r1]); en0 = _ci95([x[2] for x in r1])
    net_fresh = int(round(_gross(_body()))) - 0.16 * ACUTE
    net_aged = int(round(_gross(_body())))
    opt_energy = net_aged                 # age-aware optimal eats only aged/safe
    opt_toxic = 0.0

    r2 = [result2_seed(s) for s in range(SEEDS)]
    pin = _ci95([x[0] for x in r2]); pout = _ci95([x[1] for x in r2])
    disc = _ci95([x[2] for x in r2]); tox2 = _ci95([x[3] for x in r2])

    print(f"=== {SEEDS} seeds x {N} agents x {TRIALS} trials (mean +/- 95% CI) ===")
    print(f"Two-state model: fresh net {net_fresh:.1f} (toxic) / aged net {net_aged:.1f} (safe), staple {STAPLE}")
    print("R1 lured% vs fraction-toxic (acute 50):")
    for f in fracs:
        m, c = lured_curve[f]
        print(f"   {int(f*100)}% toxic -> lured {m:.0f}% +/- {c:.0f}%")
    print(f"R1 headline @ {int(P0*100)}% toxic: lured {lured0[0]:.0f}% +/- {lured0[1]:.0f}%, "
          f"toxic meals {toxic0[0]:.0f}% +/- {toxic0[1]:.0f}%")
    print(f"R1 gap vs optimal: learner {en0[0]:.1f} energy/meal @ {toxic0[0]:.0f}% toxic  |  "
          f"optimal {opt_energy:.0f} @ 0% toxic  -> learner poisons itself {toxic0[0]:.0f}% "
          f"to capture {100*en0[0]/opt_energy:.0f}% of optimal energy")
    print("R2 non-monotonic window [3,7]:")
    print(f"   P(eat|in) {pin[0]:.0f}% vs P(eat|out) {pout[0]:.0f}% -> discrimination {disc[0]:.1f} "
          f"+/- {disc[1]:.1f} pts (ideal 100); {tox2[0]:.0f}% +/- {tox2[1]:.0f}% toxic")

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(11.2, 4.5))
    xs = [int(f * 100) for f in fracs]
    ys = [lured_curve[f][0] for f in fracs]; es = [lured_curve[f][1] for f in fracs]
    axL.errorbar(xs, ys, yerr=es, marker="o", color=LINE, lw=2.2, capsize=4)
    axL.set_title("ผลที่ 1: การถูกล่อ (lure) เทียบกับความถี่ที่ผลไม้เป็นพิษ")
    axL.set_xlabel("% ครั้งที่เจอผลไม้เป็นพิษ (สด)")
    axL.set_ylabel("% เอเจนต์ที่ถูกล่อ (จัดผลไม้ > อาหารปลอดภัย)")
    axL.set_ylim(-5, 108)
    axL.annotate(f"แม้ {int(P0*100)}% ของครั้งเป็นพิษจริง\n(net {net_fresh:.0f} < staple 5)"
                 f" ก็ยัง {lured0[0]:.0f}% ที่มุ่งกิน",
                 xy=(int(P0*100), lured0[0]), xytext=(38, 70), fontsize=8.6, color=OLD,
                 arrowprops=dict(arrowstyle="->", color=OLD))
    b2 = axR.bar(["P(กิน|ในหน้าต่าง)", "P(กิน|นอกหน้าต่าง)"], [pin[0], pout[0]],
                 yerr=[pin[1], pout[1]], capsize=5, color=[SAFE, TOXIC], alpha=0.85)
    axR.bar_label(b2, fmt="%.0f%%", padding=3, fontsize=10)
    axR.set_title(f"ผลที่ 2: การแยกช่วงปลอดภัย = {disc[0]:.1f} pts")
    axR.set_ylabel("P(เลือกกิน)  (%)")
    axR.set_ylim(0, max(pin[0], pout[0]) + max(pin[1], pout[1]) + 8)
    axR.annotate(f"ค่าอุดมคติ 100 pts;\nเอเจนต์ {disc[0]:.1f} pts → มองไม่เห็นอายุ",
                 xy=(0.5, max(pin[0], pout[0])), xytext=(0.02, max(pin[0], pout[0]) + 2.5),
                 fontsize=9, color=OLD)
    fig.suptitle(f"หลายซีด ({SEEDS} ซีด × {N} เอเจนต์, 95% CI): ผลคงทนตลอดช่วงความถี่พิษ",
                 fontsize=10.5)
    fig.savefig(OUT / "toxin_multiseed_ci.png"); plt.close(fig)
    print("wrote", OUT / "toxin_multiseed_ci.png")


if __name__ == "__main__":
    main()
