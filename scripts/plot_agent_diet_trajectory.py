# -*- coding: utf-8 -*-
"""Plot per-agent food-value learning traces from a run_watch JSON dump.

Example:
  python scripts/plot_agent_diet_trajectory.py data/run.json
  python scripts/plot_agent_diet_trajectory.py data/run.json --event-output reports/figures/agent_learning_events.png
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_rows(payload: dict) -> list[dict]:
    rows = payload.get("agent_diet_trajectory") or []
    if not rows:
        raise SystemExit(
            "No agent_diet_trajectory rows found. Re-run food_value_study_driver "
            "with --dump after this telemetry change."
        )
    return rows


def _select_agent_ids(rows: list[dict], max_agents: int) -> list[int]:
    activity_by_agent: dict[int, int] = defaultdict(int)
    for row in rows:
        agent_id = int(row["agent_id"])
        activity = (
            int(row.get("raw_seed_meals", 0) or 0)
            + int(row.get("plant_meals", 0) or 0)
            + int(row.get("raw_seed_skips", 0) or 0)
        )
        activity_by_agent[agent_id] = max(activity_by_agent[agent_id], activity)
    ranked = sorted(activity_by_agent, key=lambda agent_id: (-activity_by_agent[agent_id], agent_id))
    return ranked[:max_agents]


def _series_by_agent(rows: list[dict], agent_ids: list[int], field: str) -> dict[int, tuple[list[int], list[int]]]:
    selected = set(agent_ids)
    series: dict[int, tuple[list[int], list[int]]] = {
        agent_id: ([], [])
        for agent_id in agent_ids
    }
    for row in sorted(rows, key=lambda item: (int(item.get("tick", 0)), int(item["agent_id"]))):
        agent_id = int(row["agent_id"])
        if agent_id not in selected:
            continue
        ticks, values = series[agent_id]
        ticks.append(int(row.get("tick", 0)))
        values.append(int(row.get(field, 0) or 0))
    return series


def plot_agent_diet_trajectory(input_path: Path, output_path: Path, max_agents: int) -> None:
    payload = _load_payload(input_path)
    rows = _load_rows(payload)
    agent_ids = _select_agent_ids(rows, max_agents)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        ("plant_meals", "plant meals"),
        ("raw_seed_meals", "raw seed meals"),
        ("raw_seed_skips", "raw seed skips"),
    ]
    fig, axes = plt.subplots(len(fields), 1, figsize=(9.0, 8.0), sharex=True)
    if len(fields) == 1:
        axes = [axes]

    for ax, (field, label) in zip(axes, fields):
        series = _series_by_agent(rows, agent_ids, field)
        for agent_id in agent_ids:
            ticks, values = series[agent_id]
            if not ticks:
                continue
            ax.plot(ticks, values, linewidth=1.6, label=f"A{agent_id}")
        ax.set_ylabel(label)
        ax.grid(alpha=0.25)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[-1].set_xlabel("tick")
    axes[0].set_title("Per-agent food-value learning trace")
    axes[0].legend(ncol=min(4, max(1, len(agent_ids))), fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_agent_learning_events(input_path: Path, output_path: Path, max_agents: int) -> None:
    payload = _load_payload(input_path)
    rows = list(payload.get("agent_diet_summary") or [])
    rows = [
        row
        for row in rows
        if row.get("first_raw_seed_tick") is not None
        or row.get("first_raw_plant_tick") is not None
        or row.get("first_raw_seed_skip_tick") is not None
    ]
    if not rows:
        raise SystemExit("No event-level first tick fields found in agent_diet_summary.")

    rows.sort(
        key=lambda row: (
            row.get("first_raw_plant_tick") is None,
            int(row.get("first_raw_plant_tick") or 10**9),
            row.get("first_raw_seed_skip_tick") is None,
            int(row.get("first_raw_seed_skip_tick") or 10**9),
            int(row.get("agent_id", 0)),
        )
    )
    rows = rows[:max_agents]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9.5, max(4.0, 0.38 * len(rows) + 1.8)))
    y_positions = list(range(len(rows)))
    labels = [f"A{int(row['agent_id'])}" for row in rows]
    event_fields = [
        ("first_raw_seed_tick", "first seed", "#B7791F", "o"),
        ("first_raw_plant_tick", "first plant", "#1F8A5B", "s"),
        ("first_raw_seed_skip_tick", "first seed skip", "#0E7C7B", "^"),
    ]

    for y, row in zip(y_positions, rows):
        ticks = [
            int(row[field])
            for field, _, _, _ in event_fields
            if row.get(field) is not None
        ]
        if ticks:
            ax.hlines(y, min(ticks), max(ticks), color="#B0BEC5", linewidth=1.1, alpha=0.8)
        for field, label, color, marker in event_fields:
            if row.get(field) is None:
                continue
            tick = int(row[field])
            ax.scatter(tick, y, s=58, color=color, marker=marker, label=label if y == 0 else None, zorder=3)
        delta = row.get("delta_learning_ticks")
        if delta is not None and row.get("first_raw_seed_skip_tick") is not None:
            ax.text(
                int(row["first_raw_seed_skip_tick"]) + 5,
                y,
                f"Δ={int(delta)}",
                va="center",
                fontsize=8,
                color="#455A64",
            )

    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("tick")
    ax.set_title("Event-level learning speed by agent")
    ax.grid(axis="x", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot tagged per-agent diet traces from a JSON dump.")
    parser.add_argument("input", type=Path, help="Path to a food_value_study_driver --dump JSON file.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/figures/agent_diet_trajectory.png"),
    )
    parser.add_argument(
        "--event-output",
        type=Path,
        default=None,
        help="Optional event-level timeline plot using first seed/plant/skip ticks.",
    )
    parser.add_argument("--max-agents", type=int, default=12)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plot_agent_diet_trajectory(args.input, args.output, max(1, args.max_agents))
    print(f"wrote: {args.output}")
    if args.event_output is not None:
        plot_agent_learning_events(args.input, args.event_output, max(1, args.max_agents))
        print(f"wrote: {args.event_output}")


if __name__ == "__main__":
    main()
