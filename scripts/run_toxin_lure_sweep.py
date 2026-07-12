# -*- coding: utf-8 -*-
"""Parameter sweep for the 'lure' effect (fixes red-team item E: is the lure a
single cherry-picked point, or a broad phenomenon?).

For a grid of (toxin acute-penalty x fraction-of-fruit-that-is-fresh), run the
REAL per-type learner (real _apply_toxin + EMA) and measure the fraction of agents
LURED -- i.e. whose learned fruit value ends up ABOVE the safe staple (5), so they
rank the partly-toxic fruit as their best food. A large lured region => the lure
is a general consequence of averaging over a hidden state, not a tuned artifact.
Output: reports/figures/toxin_lure_sweep.png
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
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 11,
                     "font.family": "Tahoma", "axes.unicode_minus": False, "figure.autolayout": True})

STAPLE, NOW, T = 5.0, 100000, 4
N, TRIALS = 60, 30
COMP = metabolism.COMPOSITION["raw_fruit"]
MASS = metabolism.FOOD_MASS["raw_fruit"]
ACUTES = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
FRESH_FRACS = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def _body():
    return BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)


def _gross(a):
    return metabolism.digestible_energy(COMP, MASS, a.body.enzyme_profile)


def _cell(acute, p_fresh, seed):
    rng = Random(seed)
    env = SimpleNamespace(food_value_learning_enabled=True, diet_learning_rate=0.3,
                          diet_pickiness=0.6, diet_starvation_energy=6, toxin_acute_penalty=float(acute),
                          toxin_damage_coeff=0.0, toxin_detox_ticks=T, toxin_safe_window_start=0,
                          toxin_safe_window_end=0, tick_count=NOW, food_positions={})
    lured = 0
    for _ in range(N):
        a = Agent(agent_id=1, body=_body(), x=0, y=0)
        a.food_value_memory = {"raw_plant": STAPLE}
        for _ in range(TRIALS):
            a.energy = 100
            age = 0 if rng.random() < p_fresh else T          # fresh(toxic) vs aged(safe)
            res = SimpleNamespace(kind="raw_fruit", energy=FOOD_ENERGY["raw_fruit"],
                                  source="s", created_tick=NOW - age)
            env.food_positions = {(a.x, a.y): res}
            if a._food_worth_eating(env):
                a._learn_food_value(env, "raw_fruit", a._apply_toxin(env, res, int(round(_gross(a)))))
        if a.food_value_memory["raw_fruit"] > STAPLE:
            lured += 1
    return 100.0 * lured / N


def main():
    grid = [[_cell(ac, pf, seed=1000 + i * 100 + j) for j, ac in enumerate(ACUTES)]
            for i, pf in enumerate(FRESH_FRACS)]

    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    im = ax.imshow(grid, origin="lower", aspect="auto", cmap="YlOrRd_r", vmin=0, vmax=100,
                   extent=[ACUTES[0] - 5, ACUTES[-1] + 5, FRESH_FRACS[0] - 0.05, FRESH_FRACS[-1] + 0.05])
    cb = fig.colorbar(im, ax=ax, pad=0.02); cb.set_label("% เอเจนต์ที่ถูกล่อ (จัดผลไม้ > อาหารปลอดภัย)")
    # contour marking the 50%-lured boundary (majority-lured region is to its left)
    cs = ax.contour(ACUTES, FRESH_FRACS, grid, levels=[50], colors="#0C447C", linewidths=2.2, linestyles="--")
    ax.clabel(cs, fmt="ถูกล่อ 50%%", fontsize=8)
    ax.set_xlabel("โทษพิษเฉียบพลัน (ความรุนแรงต่อคำ)")
    ax.set_ylabel("สัดส่วนผลไม้ที่สด (เป็นพิษ)")
    ax.set_title("การถูกล่อเป็นบริเวณกว้าง ไม่ใช่จุดที่เลือกมาเฉพาะ")
    ax.text(0.03, 0.90, "เอเจนต์ส่วนใหญ่ถูกล่อ\n(มุ่งกินผลไม้ที่มีพิษบางส่วน)",
            transform=ax.transAxes, fontsize=9, color="#7A1010")
    ax.text(0.62, 0.12, "ไม่ถูกล่อ\n(พิษรุนแรง + ถี่)",
            transform=ax.transAxes, fontsize=9, color="#0C447C")
    fig.savefig(OUT / "toxin_lure_sweep.png"); plt.close(fig)

    frac_lured_cells = sum(1 for row in grid for v in row if v >= 50) / (len(ACUTES) * len(FRESH_FRACS))
    print(f"grid {len(FRESH_FRACS)}x{len(ACUTES)} (fresh-frac x acute), {N} agents/cell")
    print(f"cells with >=50% agents lured: {100*frac_lured_cells:.0f}% of the grid")
    print(f"paper point (acute 50, 50% fresh) lured = {grid[FRESH_FRACS.index(0.5)][ACUTES.index(50)]:.0f}%")
    print("wrote", OUT / "toxin_lure_sweep.png")


if __name__ == "__main__":
    main()
