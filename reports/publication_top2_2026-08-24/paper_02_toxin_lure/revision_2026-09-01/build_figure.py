from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent / "source_data" / "paper_02_toxin_learner_comparison.csv"


def main() -> None:
    rows = list(csv.DictReader(SOURCE.open(encoding="utf-8")))
    learner_order = ["L1 sim gate", "L2 eps-greedy", "L3 softmax", "L4 sample-avg"]
    labels = {
        "L1 sim gate": "Simulation gate",
        "L2 eps-greedy": "Epsilon-greedy",
        "L3 softmax": "Softmax",
        "L4 sample-avg": "Greedy sample-average",
    }
    colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]
    markers = ["o", "s", "^", "D"]

    fig, axes = plt.subplots(1, 2, figsize=(7.25, 3.25), constrained_layout=True)

    p = np.linspace(0, 0.75, 301)
    axes[0].plot(p * 100, 10 - 8 * p, color="#0072B2", linewidth=2.2, label="Mixed fruit")
    axes[0].axhline(5, color="#222222", linewidth=1.5, linestyle="--", label="Safe staple")
    axes[0].axvline(62.5, color="#777777", linewidth=1.0, linestyle=":")
    axes[0].annotate("Boundary: 62.5%", xy=(62.5, 5), xytext=(39, 7.1),
                     arrowprops={"arrowstyle": "->", "color": "#555555"}, fontsize=8)
    axes[0].set(xlabel="Toxic encounters (%)", ylabel="Learned value", xlim=(0, 75), ylim=(3.5, 10.5))
    axes[0].set_title("A  Analytic mixture ranking", loc="left", fontweight="bold")
    axes[0].legend(frameon=False, fontsize=8, loc="upper right")

    for learner, color, marker in zip(learner_order, colors, markers):
        subset = [r for r in rows if r["learner"] == learner]
        x = np.array([float(r["toxic_fraction"]) * 100 for r in subset])
        y = np.array([float(r["lured_percent_mean"]) for r in subset])
        e = np.array([float(r["lured_percent_ci95_half_width"]) for r in subset])
        axes[1].errorbar(x, y, yerr=e, color=color, marker=marker, linewidth=1.7,
                         markersize=4.5, capsize=2.5, label=labels[learner])
    axes[1].axvline(62.5, color="#777777", linewidth=1.0, linestyle=":")
    axes[1].set(xlabel="Toxic encounters (%)", ylabel="Agents lured (%)", xlim=(17, 65), ylim=(0, 105))
    axes[1].set_title("B  Finite-horizon learners", loc="left", fontweight="bold")
    axes[1].legend(frameon=False, fontsize=7.2, loc="lower left")

    for ax in axes:
        ax.grid(axis="y", color="#D9D9D9", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=8.5)
        ax.xaxis.label.set_size(9)
        ax.yaxis.label.set_size(9)

    fig.savefig(HERE / "figure_01_temporal_toxicity_revised.png", dpi=600, facecolor="white")
    fig.savefig(HERE / "Injun_Figure_1_Temporal_Toxicity_Revised.pdf", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
