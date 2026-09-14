# -*- coding: utf-8 -*-
"""Export source data and publication figures for the pre-confirmatory studies.

The script reads the frozen E1-E4 result tables and raw E4 summaries. It does
not select hypotheses or recompute the registered tests; plotted intervals are
descriptive 95% t intervals over independent seeds.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from analyze_e_series import mean_sd, t_ci95


E1_ARMS = ("A0", "A1", "A2", "A3")
E2_ARMS = ("B1", "B2", "B3", "B4")
PROFILES = ("M", "W")
E3_ARMS = ("A0", "A2", "A3")
E4_ARMS = ("A_no_learning", "B_value_learning")


def load_rows(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["rows"]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def require_cells(rows: list[dict], arms: tuple[str, ...], seeds: int, label: str) -> None:
    observed = {str(row["arm"]) for row in rows}
    if observed != set(arms):
        raise ValueError(f"{label}: arms {sorted(observed)} != {sorted(arms)}")
    counts = {arm: sum(str(row["arm"]) == arm for row in rows) for arm in arms}
    if any(count != seeds for count in counts.values()):
        raise ValueError(f"{label}: incomplete cells {counts}")


def export_e1(rows: list[dict]) -> list[dict]:
    require_cells(rows, E1_ARMS, 20, "E1")
    return [{
        "seed": int(row["seed"]),
        "arm": row["arm"],
        "founder_mean_attained_age": float(row["founder_mean_age"]),
        "fruit_p_eat_given_encounter": float(row["fruit_p_eat_given_encounter"]),
        "mean_learned_fruit_value": float(row["mean_learned_fruit_value"]),
        "mean_learned_staple_value": float(row["mean_learned_plant_value"]),
        "mean_toxin_damage": float(row["mean_toxin_damage"]),
    } for row in rows]


def export_e2(rows: list[dict]) -> list[dict]:
    expected = tuple(f"{arm}_{profile}" for profile in PROFILES for arm in E2_ARMS)
    require_cells(rows, expected, 20, "E2")
    output = []
    for row in rows:
        arm, profile = str(row["arm"]).split("_")
        output.append({
            "seed": int(row["seed"]),
            "profile": profile,
            "arm": arm,
            "founder_mean_attained_age": float(row["founder_mean_age"]),
            "discrimination_index": float(row["discrimination_index"]),
            "p_eat_given_safe": float(row["p_eat_given_safe"]),
            "p_eat_given_toxic": float(row["p_eat_given_toxic"]),
            "fruit_encounters": int(row["fruit_encounters_total"]),
        })
    return output


def export_e3(rows: list[dict]) -> list[dict]:
    require_cells(rows, E3_ARMS, 20, "E3")
    return [{
        "seed": int(row["seed"]),
        "arm": row["arm"],
        "selection_differential": float(row["selection_differential"]),
        "tolerance_age_slope": float(row["beta_tolerance_age"]),
        "cohort_tolerance_mean": float(row["cohort_tolerance_mean"]),
        "cohort_tolerance_sd": float(row["cohort_tolerance_sd"]),
        "births": int(row["births"]),
        "max_generation": int(row["max_generation"]),
    } for row in rows]


def export_e4(rows: list[dict], repo_root: Path) -> list[dict]:
    require_cells(rows, E4_ARMS, 10, "E4")
    output = []
    for row in rows:
        dump_path = repo_root / Path(str(row["dump"]))
        dump = json.loads(dump_path.read_text(encoding="utf-8"))
        metrics = dump["agent_diet_metrics"]
        meals = int(metrics["total_raw_seed_meals"])
        behavior_skips = int(metrics["total_raw_seed_skips"])
        encounter_seen = 0
        encounter_ate = 0
        encounter_skipped = 0
        for agent in dump["agent_diet_summary"]:
            for key, bucket in agent["encounters_by_kind_age"].items():
                if not key.startswith("raw_seed@"):
                    continue
                encounter_seen += int(bucket["seen"])
                encounter_ate += int(bucket["ate"])
                encounter_skipped += int(bucket["skipped"])
        if encounter_seen != encounter_ate + encounter_skipped:
            raise ValueError(f"E4 {row['arm']} seed {row['seed']}: seen != ate + skipped")
        if encounter_ate != meals:
            raise ValueError(f"E4 {row['arm']} seed {row['seed']}: telemetry ate != meals")
        output.append({
            "seed": int(row["seed"]),
            "arm": row["arm"],
            "raw_seed_meals": meals,
            "raw_seed_behavior_skip_calls": behavior_skips,
            "raw_seed_encounter_ate": encounter_ate,
            "raw_seed_encounter_skipped": encounter_skipped,
            "raw_seed_encounters": encounter_seen,
            "raw_seed_p_eat_given_encounter": encounter_ate / encounter_seen if encounter_seen else "",
        })
    return output


def values(rows: list[dict], field: str, **match: str) -> list[float]:
    return [float(row[field]) for row in rows if all(str(row[key]) == value for key, value in match.items())]


def draw_points(ax, x: float, vals: list[float], color: str, width: float = 0.16) -> None:
    offsets = [((index % 9) - 4) / 4 * width for index in range(len(vals))]
    ax.scatter([x + offset for offset in offsets], vals, s=14, color=color, alpha=0.42, edgecolors="none", zorder=2)
    mean = mean_sd(vals)["mean"]
    ci = t_ci95(vals)
    ax.errorbar(x, mean, yerr=[[mean - ci["low"]], [ci["high"] - mean]], marker="D", markersize=5,
                color="black", linewidth=1.5, capsize=4, zorder=4)


def make_figure_1(e1: list[dict], output_dir: Path) -> None:
    import matplotlib.pyplot as plt
    colors = ("#999999", "#D55E00", "#0072B2", "#009E73")
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.1), constrained_layout=True)
    for index, (arm, color) in enumerate(zip(E1_ARMS, colors)):
        draw_points(axes[0], index, values(e1, "founder_mean_attained_age", arm=arm), color)
        draw_points(axes[1], index, values(e1, "fruit_p_eat_given_encounter", arm=arm), color)
    for ax in axes:
        ax.set_xticks(range(4), E1_ARMS)
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("Mean founder attained age (ticks)")
    axes[0].set_title("A  Survival outcome")
    axes[1].set_ylabel("P(eat | fruit encounter)")
    axes[1].set_ylim(-0.04, 1.05)
    axes[1].set_title("B  Encounter-conditional acceptance")
    fig.savefig(output_dir / "figure_1_hidden_toxicity.png", dpi=300)
    fig.savefig(output_dir / "figure_1_hidden_toxicity.pdf")
    plt.close(fig)


def make_figure_2(e2: list[dict], output_dir: Path) -> None:
    import matplotlib.pyplot as plt
    colors = {"B1": "#999999", "B2": "#0072B2", "B3": "#D55E00", "B4": "#009E73"}
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2), constrained_layout=True)
    offsets = {"B1": -0.27, "B2": -0.09, "B3": 0.09, "B4": 0.27}
    for p_index, profile in enumerate(PROFILES):
        for arm in E2_ARMS:
            x = p_index + offsets[arm]
            draw_points(axes[0], x, values(e2, "discrimination_index", profile=profile, arm=arm), colors[arm], width=0.035)
    axes[0].set_xticks(range(2), ["Monotonic (M)", "Toxic-safe-toxic (W)"])
    axes[0].set_ylabel("Discrimination index")
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_title("A  State discrimination")
    axes[0].grid(axis="y", alpha=0.2)
    handles = [plt.Line2D([0], [0], marker="o", linestyle="", color=colors[arm], label=arm) for arm in E2_ARMS]
    axes[0].legend(handles=handles, frameon=False, ncol=4, loc="lower center")

    indexed = {(row["profile"], row["arm"], row["seed"]): row for row in e2}
    contrast_arms = ("B2", "B3", "B4")
    for p_index, profile in enumerate(PROFILES):
        seeds = sorted({row["seed"] for row in e2 if row["profile"] == profile})
        for a_index, arm in enumerate(contrast_arms):
            vals = [indexed[(profile, arm, seed)]["founder_mean_attained_age"] -
                    indexed[(profile, "B1", seed)]["founder_mean_attained_age"] for seed in seeds]
            x = p_index + (-0.2, 0.0, 0.2)[a_index]
            draw_points(axes[1], x, vals, colors[arm], width=0.04)
    axes[1].set_xticks(range(2), ["Monotonic (M)", "Toxic-safe-toxic (W)"])
    axes[1].set_ylabel("Paired attained-age difference vs B1 (ticks)")
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_title("B  Survival consequence")
    axes[1].grid(axis="y", alpha=0.2)
    handles = [plt.Line2D([0], [0], marker="o", linestyle="", color=colors[arm], label=f"{arm}-B1") for arm in contrast_arms]
    axes[1].legend(handles=handles, frameon=False, ncol=3, loc="lower center")
    fig.savefig(output_dir / "figure_2_information_rescue.png", dpi=300)
    fig.savefig(output_dir / "figure_2_information_rescue.pdf")
    plt.close(fig)


def make_figure_3(e3: list[dict], e4: list[dict], output_dir: Path) -> None:
    import matplotlib.pyplot as plt
    colors = {"A0": "#999999", "A2": "#0072B2", "A3": "#009E73",
              "A_no_learning": "#999999", "B_value_learning": "#CC79A7"}
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.2), constrained_layout=True)
    for index, arm in enumerate(E3_ARMS):
        draw_points(axes[0], index, values(e3, "selection_differential", arm=arm), colors[arm])
    axes[0].set_xticks(range(3), E3_ARMS)
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_ylabel("Within-founder selection differential")
    axes[0].set_title("A  Toxin-tolerance selection")
    axes[0].grid(axis="y", alpha=0.2)

    labels = ("No learning", "Value learning")
    for index, arm in enumerate(E4_ARMS):
        vals = values(e4, "raw_seed_p_eat_given_encounter", arm=arm)
        draw_points(axes[1], index, vals, colors[arm])
        mean_meals = mean_sd(values(e4, "raw_seed_meals", arm=arm))["mean"]
        mean_encounters = mean_sd(values(e4, "raw_seed_encounters", arm=arm))["mean"]
        axes[1].text(index, 0.56 if index == 0 else 0.23,
                     f"mean meals = {mean_meals:,.1f}\nmean encounters = {mean_encounters:,.1f}",
                     ha="center", va="center", fontsize=8)
    axes[1].set_xticks(range(2), labels)
    axes[1].set_ylim(-0.04, 1.05)
    axes[1].set_ylabel("P(eat | raw-seed encounter)")
    axes[1].set_title("B  Exposure denominator check")
    axes[1].grid(axis="y", alpha=0.2)
    fig.savefig(output_dir / "figure_3_selection_and_denominator.png", dpi=300)
    fig.savefig(output_dir / "figure_3_selection_and_denominator.pdf")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    source_dir = out_dir / "source_data"
    figure_dir = out_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    e1 = export_e1(load_rows(repo_root / "reports/e1_20260912/E1_runs.json"))
    e2 = export_e2(load_rows(repo_root / "reports/e2_20260913/E2_runs.json"))
    e3 = export_e3(load_rows(repo_root / "reports/e3_20260913/E3_selection_runs.json"))
    e4 = export_e4(load_rows(repo_root / "reports/e4_20260913/E4_runs.json"), repo_root)
    write_csv(source_dir / "e1_seed_outcomes.csv", e1)
    write_csv(source_dir / "e2_seed_outcomes.csv", e2)
    write_csv(source_dir / "e3_seed_selection.csv", e3)
    write_csv(source_dir / "e4_seed_behavior.csv", e4)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
        "axes.spines.right": False, "figure.dpi": 140,
    })
    make_figure_1(e1, figure_dir)
    make_figure_2(e2, figure_dir)
    make_figure_3(e3, e4, figure_dir)
    print(f"wrote 4 source-data tables and 3 figures under {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
