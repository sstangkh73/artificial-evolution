# -*- coding: utf-8 -*-
"""Generate publication-quality figures for the food-value-learning report.
Data are deterministic (seed-invariant), taken from the 2026-06-18/19 runs.
Output: reports/figures/*.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "figure.autolayout": True,
})
C = {"drain": "#C0392B", "intake": "#1F8A5B", "a": "#9A6BB0", "b": "#0E7C7B",
     "neutral": "#7F8C8D", "accent": "#B7791F"}


def fig1_energy_budget():
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    # stacked drain vs intake (log y to show the ~450x gap)
    ax.bar(["drain"], [1.0], color="#E8A2A2", label="base (1.0)")
    ax.bar(["drain"], [2.0], bottom=[1.0], color="#D46A6A", label="brain/passive (2.0)")
    ax.bar(["drain"], [1.99], bottom=[3.0], color="#C0392B", label="movement (2.0)")
    ax.bar(["intake"], [0.011], color=C["intake"], label="intake (0.011)")
    ax.set_yscale("log")
    ax.set_ylabel("energy per agent per tick (log scale)")
    ax.set_title("Energy budget: drain 4.99 vs intake 0.011  (≈453:1)")
    ax.legend(fontsize=9, loc="upper right")
    ax.annotate("1 meal ≈ 1 tick of life\n(eats ~1 meal / 455 ticks)",
                xy=(1, 0.011), xytext=(0.55, 0.08), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=C["neutral"]))
    fig.savefig(OUT / "fig1_energy_budget.png"); plt.close(fig)


def fig2_not_food_limited():
    food = ["0", "6", "30"]
    deficit = [4.93, 4.91, 4.84]
    standing = [36, 757, 2654]
    fig, ax1 = plt.subplots(figsize=(6.2, 4.0))
    x = range(len(food))
    ax1.bar([i - 0.18 for i in x], deficit, width=0.36, color=C["drain"], label="energy deficit /tick")
    ax1.set_ylabel("energy deficit per agent per tick", color=C["drain"])
    ax1.set_ylim(0, 6)
    ax1.set_xticks(list(x)); ax1.set_xticklabels(food)
    ax1.set_xlabel("low-value food spawned per tick")
    ax2 = ax1.twinx(); ax2.spines["top"].set_visible(False)
    ax2.bar([i + 0.18 for i in x], standing, width=0.36, color=C["neutral"], alpha=0.6, label="standing food (uneaten)")
    ax2.set_ylabel("standing food items", color=C["neutral"])
    ax2.grid(False)
    ax1.set_title("Flooding food does NOT close the deficit\n(deficit ~4.9 flat; food sits uneaten → not supply-limited)")
    fig.savefig(OUT / "fig2_not_food_limited.png"); plt.close(fig)


def fig3_capstone_births():
    bodies = ["body 37\n(durability 10)", "body 38\n(durability 26)"]
    births = [0, 50]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    bars = ax.bar(bodies, births, color=[C["neutral"], C["b"]])
    ax.set_ylabel("births in 3000 ticks (surplus-energy regime)")
    ax.set_title("Reproduction unlock: armor (durability ≥ 18) is required\nsame energy regime, only the body differs")
    ax.set_ylim(0, 60)
    for bar, v, note in zip(bars, births, ["0 births\n(durability 10 < 18\n→ structurally impossible)", "50 births\npop 50 → 100"]):
        ax.text(bar.get_x() + bar.get_width()/2, v + 1.5, note, ha="center", va="bottom", fontsize=9)
    fig.savefig(OUT / "fig3_capstone_births.png"); plt.close(fig)


def fig4_learning_curve():
    win = ["0–1k", "1–2k", "2–3k", "3–4k", "4–5k", "5–6k"]
    a = [591, 613, 370, 336, 392, 334]
    b = [236, 105, 15, 5, 5, 5]
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    ax.plot(win, a, "o-", color=C["a"], lw=2.4, ms=7, label="A: no learning (value-blind)")
    ax.plot(win, b, "s--", color=C["b"], lw=2.4, ms=7, label="B: experience-driven value learning")
    ax.set_ylabel("low-value food eaten per 1000 ticks")
    ax.set_xlabel("time window (ticks)")
    ax.set_title("Food-value learning in a healthy (well-fed) regime\nhunger ≈ 0, normal starvation floor — no artificial override")
    ax.set_ylim(0, 680)
    ax.legend(fontsize=9.5)
    ax.annotate("learns: seed=50 ≪ plant=250\n→ stops eating low-value food",
                xy=(4, 5), xytext=(2.3, 230), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=C["b"]))
    fig.savefig(OUT / "fig4_learning_curve.png"); plt.close(fig)


def fig5_regime_ladder():
    cond = ["baseline", "drain÷5", "drain÷5\n+density", "drain÷5\n+density\n+food×10", "drain÷10\n+density\n+food×20"]
    energy = [1.12, 1.84, 1.05, 62.8, 3185]
    hunger = [0.983, 0.983, 0.983, 0.62, 0.0]
    fig, ax1 = plt.subplots(figsize=(7.0, 4.2))
    x = range(len(cond))
    ax1.bar(x, energy, color=C["accent"], alpha=0.85, label="mean energy")
    ax1.set_yscale("log"); ax1.set_ylabel("mean energy (log)", color=C["accent"])
    ax1.set_xticks(list(x)); ax1.set_xticklabels(cond, fontsize=8.5)
    ax1.axhline(92, color=C["drain"], ls=":", lw=1.5)
    ax1.text(0.05, 110, "reproduction energy threshold (92)", color=C["drain"], fontsize=8)
    ax2 = ax1.twinx(); ax2.spines["top"].set_visible(False); ax2.grid(False)
    ax2.plot(x, hunger, "o-", color=C["b"], lw=2, label="mean hunger")
    ax2.set_ylabel("mean hunger (0–1)", color=C["b"]); ax2.set_ylim(0, 1.05)
    ax1.set_title("The energy economy is fixable: combined levers reach surplus\n(energy → 1000s, hunger → 0)")
    fig.savefig(OUT / "fig5_regime_ladder.png"); plt.close(fig)


def fig6_carrying_capacity():
    ticks = [1, 2, 3, 4, 5, 6]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(ticks, [100]*6, "o-", color=C["b"], lw=2, label="food ×50 → 100")
    ax.plot(ticks, [96]*6, "s--", color=C["accent"], lw=2, label="food ×100 → 96")
    ax.plot(ticks, [96]*6, "^:", color=C["neutral"], lw=2, label="food ×200 → 96")
    ax.axhline(50, color=C["neutral"], ls=":", lw=1, alpha=0.6)
    ax.text(1, 52, "founders (50)", fontsize=8, color=C["neutral"])
    ax.set_ylim(0, 130); ax.set_xlabel("time (1000 ticks)"); ax.set_ylabel("population")
    ax.set_title("Carrying capacity self-caps at ~2× founders\nmore food energy does NOT raise it (item-count limited, safety collapses)")
    ax.legend(fontsize=9)
    fig.savefig(OUT / "fig6_carrying_capacity.png"); plt.close(fig)


for f in [fig1_energy_budget, fig2_not_food_limited, fig3_capstone_births,
          fig4_learning_curve, fig5_regime_ladder, fig6_carrying_capacity]:
    f()
print("wrote:", sorted(p.name for p in OUT.glob("*.png")))
