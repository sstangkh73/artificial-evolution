from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "reports" / "publication_top2_2026-08-24" / "source_data"
RUNS = ROOT / "data" / "multiseed"

FIG1_PNG = HERE / "figure_01_stationary_learning.png"
FIG1_PDF = HERE / "Injun_Figure_1_Stationary_Learning.pdf"
FIG2_PNG = HERE / "figure_02_temporal_lure.png"
FIG2_PDF = HERE / "Injun_Figure_2_Temporal_Lure.pdf"

COLORS = {
    "blind": "#6B7280",
    "memory": "#0072B2",
    "analytic": "#D55E00",
    "staple": "#009E73",
    "gate": "#6B7280",
    "eps": "#0072B2",
    "softmax": "#009E73",
    "greedy": "#D55E00",
}


def configure() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "legend.fontsize": 8.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.18,
            "savefig.bbox": "tight",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def window_counts(dump: dict, window: int = 1000) -> list[int]:
    cumulative: dict[int, int] = {}
    for row in dump["agent_diet_trajectory"]:
        tick = int(row["tick"])
        cumulative[tick] = cumulative.get(tick, 0) + int(row.get("raw_seed_meals") or 0)
    return [cumulative[window * (i + 1)] - cumulative[window * i] for i in range(3)]


def mean_ci_t(values: list[float], critical: float = 2.262) -> tuple[float, float]:
    return statistics.mean(values), critical * statistics.stdev(values) / math.sqrt(len(values))


def build_figure_1() -> None:
    with (SOURCE / "paper_01_food_value_paired_seeds.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    blind = [int(row["no_learning_meals"]) for row in rows]
    memory = [int(row["value_learning_meals"]) for row in rows]

    windows = {"A": [[], [], []], "B": [[], [], []]}
    for arm in windows:
        for path in sorted(RUNS.glob(f"{arm}_*.json")):
            counts = window_counts(json.loads(path.read_text(encoding="utf-8")))
            for index, value in enumerate(counts):
                windows[arm][index].append(value)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.15))

    for y0, y1 in zip(blind, memory):
        ax1.plot([0, 1], [y0, y1], color="#A8ADB4", lw=1.15, alpha=0.9, zorder=1)
    ax1.scatter([0] * len(blind), blind, color=COLORS["blind"], s=31, zorder=3, label="Value blind")
    ax1.scatter([1] * len(memory), memory, color=COLORS["memory"], s=31, zorder=3, label="Value memory")
    ax1.set_xticks([0, 1], ["Value blind", "Value memory"])
    ax1.set_xlim(-0.3, 1.3)
    ax1.set_ylabel("Low-value meals over 3,000 ticks")
    ax1.set_title("A  Paired seed/run totals", loc="left", fontweight="bold")
    ax1.text(
        0.03,
        0.95,
        "Mean paired reduction = 1,522.3\n95% interval: 1,340.7–1,703.9\nExact paired p = 0.001953",
        transform=ax1.transAxes,
        va="top",
        fontsize=8.4,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#D1D5DB"},
    )

    x = [1, 2, 3]
    for arm, label, color, marker in (
        ("A", "Value blind", COLORS["blind"], "o"),
        ("B", "Value memory", COLORS["memory"], "s"),
    ):
        summary = [mean_ci_t(values) for values in windows[arm]]
        means = [item[0] for item in summary]
        ci = [item[1] for item in summary]
        ax2.errorbar(x, means, yerr=ci, marker=marker, ms=6, lw=2.2, capsize=4, color=color, label=label)
    ax2.set_xticks(x, ["0–1,000", "1,000–2,000", "2,000–3,000"])
    ax2.set_xlabel("Tick window")
    ax2.set_ylabel("Low-value meals per window")
    ax2.set_ylim(bottom=0)
    ax2.set_title("B  Acquisition across time", loc="left", fontweight="bold")
    ax2.legend(frameon=False, loc="upper right")

    fig.suptitle("Experience-based value memory suppresses low-value consumption", fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG1_PNG, dpi=350)
    fig.savefig(FIG1_PDF)
    plt.close(fig)


def build_figure_2() -> None:
    with (SOURCE / "paper_02_toxin_learner_comparison.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["learner"], []).append(row)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.15))

    xs = [i / 100 for i in range(0, 101)]
    mixed = [10 - 8 * value for value in xs]
    ax1.plot([100 * value for value in xs], mixed, color=COLORS["analytic"], lw=2.5, label="Mixed-fruit expected value")
    ax1.axhline(5, color=COLORS["staple"], lw=2, ls="--", label="Safe staple value")
    ax1.axvline(62.5, color="#7C3AED", lw=1.6, ls=":")
    ax1.fill_between([0, 62.5], [5, 5], [10, 5], color=COLORS["analytic"], alpha=0.10)
    ax1.text(64, 8.9, "Analytic boundary\np* = 62.5%", color="#6D28D9", fontsize=8.5)
    ax1.set_xlim(0, 100)
    ax1.set_ylim(1.5, 10.5)
    ax1.set_xlabel("Toxic encounters (%)")
    ax1.set_ylabel("Stored / expected energy value")
    ax1.set_title("A  Mixture ranking", loc="left", fontweight="bold")
    ax1.legend(frameon=False, loc="lower left")

    style = {
        "L1 sim gate": ("Simulation gate", COLORS["gate"], "o", "--"),
        "L2 eps-greedy": ("Epsilon-greedy", COLORS["eps"], "s", "-"),
        "L3 softmax": ("Softmax", COLORS["softmax"], "^", "-"),
        "L4 sample-avg": ("Greedy sample average", COLORS["greedy"], "D", "-"),
    }
    for key, values in grouped.items():
        values = sorted(values, key=lambda item: float(item["toxic_fraction"]))
        label, color, marker, line = style[key]
        x = [100 * float(item["toxic_fraction"]) for item in values]
        y = [float(item["lured_percent_mean"]) for item in values]
        e = [float(item["lured_percent_ci95_half_width"]) for item in values]
        ax2.errorbar(x, y, yerr=e, label=label, color=color, marker=marker, ls=line, lw=2, ms=4.5, capsize=3)
    ax2.axvline(62.5, color="#7C3AED", lw=1.3, ls=":", alpha=0.85)
    ax2.set_xlim(18, 65)
    ax2.set_ylim(0, 104)
    ax2.set_xlabel("Toxic encounters (%)")
    ax2.set_ylabel("Agents ranking fruit above staple (%)")
    ax2.set_title("B  Finite-horizon lure", loc="left", fontweight="bold")
    ax2.legend(frameon=False, loc="lower left")

    fig.suptitle("Intermittent safety can invert type-level value learning", fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG2_PNG, dpi=350)
    fig.savefig(FIG2_PDF)
    plt.close(fig)


if __name__ == "__main__":
    configure()
    build_figure_1()
    build_figure_2()
    print(FIG1_PNG)
    print(FIG1_PDF)
    print(FIG2_PNG)
    print(FIG2_PDF)
