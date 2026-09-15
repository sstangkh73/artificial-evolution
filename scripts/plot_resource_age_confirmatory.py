# -*- coding: utf-8 -*-
"""Create confirmatory source-data tables and publication figures.

The primary estimates are read from the frozen analyzers.  Plotting and tabular
layout do not recompute or select the confirmatory hypothesis.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from analyze_e_series import mean_sd, t_ci95


ENERGIES = (4, 5, 6, 8, 10)


def e6_seed_rows(payload: dict) -> list[dict]:
    indexed = {(str(row["arm"]), int(row["seed"])): row for row in payload["rows"]}
    seeds = sorted({int(row["seed"]) for row in payload["rows"]})
    output = []
    for seed in seeds:
        for energy in ENERGIES:
            arms = {
                condition: indexed[(f"V{energy:02d}_{condition}", seed)]
                for condition in ("B1", "B2", "B3")
            }
            output.append({
                "seed": seed,
                "realized_fruit_energy": energy,
                "B1_followup_ticks": arms["B1"]["founder_mean_followup_ticks"],
                "B2_followup_ticks": arms["B2"]["founder_mean_followup_ticks"],
                "B3_followup_ticks": arms["B3"]["founder_mean_followup_ticks"],
                "B2_minus_B3_followup_ticks": (
                    arms["B2"]["founder_mean_followup_ticks"]
                    - arms["B3"]["founder_mean_followup_ticks"]
                ),
                "B2_minus_B1_followup_ticks": (
                    arms["B2"]["founder_mean_followup_ticks"]
                    - arms["B1"]["founder_mean_followup_ticks"]
                ),
                "B3_minus_B1_followup_ticks": (
                    arms["B3"]["founder_mean_followup_ticks"]
                    - arms["B1"]["founder_mean_followup_ticks"]
                ),
                "B1_discrimination_index": arms["B1"]["discrimination_index"],
                "B2_discrimination_index": arms["B2"]["discrimination_index"],
                "B3_discrimination_index": arms["B3"]["discrimination_index"],
                "B2_p_eat_given_safe": arms["B2"]["p_eat_given_safe"],
                "B2_p_eat_given_toxic": arms["B2"]["p_eat_given_toxic"],
                "B2_fruit_encounters_per_founder": arms["B2"]["fruit_encounters_per_agent"],
            })
    return output


def t2_seed_rows(payload: dict) -> list[dict]:
    indexed = {(str(row["arm"]), int(row["seed"])): row for row in payload["rows"]}
    seeds = sorted({int(row["seed"]) for row in payload["rows"]})
    output = []
    for seed in seeds:
        values = {
            arm: float(indexed[(arm, seed)]["founder_mean_followup_ticks"])
            for arm in ("A2", "A3O", "A3R")
        }
        output.append({
            "seed": seed,
            "A2_followup_ticks": values["A2"],
            "A3O_followup_ticks": values["A3O"],
            "A3R_followup_ticks": values["A3R"],
            "A2_minus_A3O_followup_ticks": values["A2"] - values["A3O"],
            "A2_minus_A3R_followup_ticks": values["A2"] - values["A3R"],
        })
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _summary_row(label: str, values: list[float]) -> dict:
    summary = mean_sd(values)
    ci = t_ci95(values)
    return {
        "contrast": label,
        **summary,
        "ci95_low": ci["low"],
        "ci95_high": ci["high"],
    }


def make_figures(e6_rows: list[dict], t2_rows: list[dict], output_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 140,
    })

    # Figure 4 is rendered at the manuscript's full 6.5-inch text width.  A
    # taller source aspect ratio and larger source fonts keep axes and legends
    # legible after the PDF page compositor scales the vector artwork.
    plt.rcParams.update({"font.size": 11, "axes.titlesize": 12})
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 5.2), constrained_layout=True)
    by_seed: dict[int, list[dict]] = {}
    for row in e6_rows:
        by_seed.setdefault(int(row["seed"]), []).append(row)
    for seed_rows in by_seed.values():
        ordered = sorted(seed_rows, key=lambda row: row["realized_fruit_energy"])
        axes[0].plot(
            [row["realized_fruit_energy"] for row in ordered],
            [row["B2_minus_B3_followup_ticks"] for row in ordered],
            color="#7f8c8d", alpha=0.18, linewidth=0.7,
        )
    for field, label, color, marker in (
        ("B2_minus_B3_followup_ticks", "B2-B3 (registered primary)", "#1f4e79", "o"),
        ("B2_minus_B1_followup_ticks", "B2-B1", "#009E73", "s"),
        ("B3_minus_B1_followup_ticks", "B3-B1 (descriptive)", "#D55E00", "^"),
    ):
        means, lows, highs = [], [], []
        for energy in ENERGIES:
            values = [
                float(row[field]) for row in e6_rows
                if row["realized_fruit_energy"] == energy
            ]
            means.append(mean_sd(values)["mean"])
            ci = t_ci95(values)
            lows.append(means[-1] - ci["low"])
            highs.append(ci["high"] - means[-1])
        axes[0].errorbar(
            ENERGIES, means, yerr=[lows, highs], color=color, marker=marker,
            linewidth=1.8, capsize=3, label=label,
        )
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_xlabel("Realized safe-fruit energy")
    axes[0].set_ylabel("Paired restricted mean follow-up difference (ticks)")
    axes[0].set_title("A  Survival effect by resource payoff")
    axes[0].legend(frameon=False, loc="best", fontsize=9.5)

    for field, label, color in (
        ("B1_discrimination_index", "Type-only key (B1)", "#333333"),
        ("B2_discrimination_index", "Resource-age key (B2)", "#0072B2"),
        ("B3_discrimination_index", "Capacity-matched sham (B3)", "#D55E00"),
    ):
        means, lows, highs = [], [], []
        for energy in ENERGIES:
            values = [
                float(row[field]) for row in e6_rows
                if row["realized_fruit_energy"] == energy
            ]
            mean = mean_sd(values)["mean"]
            ci = t_ci95(values)
            means.append(mean)
            lows.append(mean - ci["low"])
            highs.append(ci["high"] - mean)
        axes[1].errorbar(
            ENERGIES, means, yerr=[lows, highs], color=color, marker="o",
            linewidth=2, capsize=3, label=label,
        )
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_xlabel("Realized safe-fruit energy")
    axes[1].set_ylabel("Discrimination index")
    axes[1].set_title("B  Mechanism check")
    axes[1].legend(frameon=False, loc="best")
    fig.savefig(output_dir / "figure_e6_energy_gradient.png", dpi=300)
    fig.savefig(output_dir / "figure_e6_energy_gradient.pdf")
    plt.close(fig)

    plt.rcParams.update({"font.size": 9, "axes.titlesize": "large"})
    fig, ax = plt.subplots(figsize=(5.6, 4.2), constrained_layout=True)
    series = [
        [float(row["A2_minus_A3O_followup_ticks"]) for row in t2_rows],
        [float(row["A2_minus_A3R_followup_ticks"]) for row in t2_rows],
    ]
    for left, right in zip(*series):
        ax.plot([0, 1], [left, right], color="#a0a0a0", alpha=0.25, linewidth=0.6)
    for x, values, color in zip((0, 1), series, ("#6A3D9A", "#1B9E77")):
        jitter = [x + ((index % 7) - 3) * 0.012 for index in range(len(values))]
        ax.scatter(jitter, values, s=14, color=color, alpha=0.55, edgecolors="none")
        mean = mean_sd(values)["mean"]
        ci = t_ci95(values)
        ax.errorbar(
            x, mean, yerr=[[mean - ci["low"]], [ci["high"] - mean]],
            marker="D", color="black", capsize=5, markersize=6, linewidth=1.8,
        )
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axhline(-5, color="#555555", linestyle="--", linewidth=0.9, label="SESOI = -5 ticks")
    ax.set_xticks([0, 1], ["A2-A3O\noriginal control", "A2-A3R\nrecalibrated control"])
    ax.set_ylabel("Paired restricted mean follow-up difference (ticks)")
    ax.set_title("T2-RB replication across 50 matched seeds")
    ax.legend(frameon=False, loc="lower right")
    fig.savefig(output_dir / "figure_t2rb_replication.png", dpi=300)
    fig.savefig(output_dir / "figure_t2rb_replication.pdf")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--e6-runs", required=True)
    parser.add_argument("--t2-runs", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    e6_payload = json.loads(Path(args.e6_runs).read_text(encoding="utf-8"))
    t2_payload = json.loads(Path(args.t2_runs).read_text(encoding="utf-8"))
    output_dir = Path(args.out_dir)
    source_dir = output_dir / "source_data"
    e6_rows = e6_seed_rows(e6_payload)
    t2_rows = t2_seed_rows(t2_payload)
    write_csv(source_dir / "e6_seed_by_energy.csv", e6_rows)
    write_csv(source_dir / "t2rb_seed_contrasts.csv", t2_rows)

    e6_summary = []
    for energy in ENERGIES:
        for field, label in (
            ("B2_minus_B3_followup_ticks", "B2-B3"),
            ("B2_minus_B1_followup_ticks", "B2-B1"),
            ("B3_minus_B1_followup_ticks", "B3-B1 descriptive"),
        ):
            values = [
                float(row[field]) for row in e6_rows
                if row["realized_fruit_energy"] == energy
            ]
            e6_summary.append({
                "realized_fruit_energy": energy,
                **_summary_row(label, values),
            })
    write_csv(source_dir / "e6_energy_summary.csv", e6_summary)
    write_csv(source_dir / "t2rb_contrast_summary.csv", [
        _summary_row("A2-A3O", [float(row["A2_minus_A3O_followup_ticks"]) for row in t2_rows]),
        _summary_row("A2-A3R", [float(row["A2_minus_A3R_followup_ticks"]) for row in t2_rows]),
    ])
    make_figures(e6_rows, t2_rows, output_dir / "figures")
    print(f"wrote source-data tables and figures under {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
