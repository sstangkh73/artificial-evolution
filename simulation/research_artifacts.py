from __future__ import annotations

import csv
import json
from pathlib import Path

from visualization.dashboard import build_dashboard_artifacts


def write_research_artifacts(output_dir: Path, payload: dict[str, object]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = output_dir / "metadata.json"
    summary_path = output_dir / "summary.json"
    tick_metrics_path = output_dir / "tick_metrics.csv"
    events_path = output_dir / "events.jsonl"
    lineage_path = output_dir / "lineages.csv"
    agents_path = output_dir / "agent_outcomes.csv"
    generation_traits_path = output_dir / "generation_traits.csv"
    methods_path = output_dir / "methods.md"
    readable_log_path = output_dir / "readable_log.md"
    checkpoints_path = output_dir / "tick_checkpoints.md"
    event_summary_path = output_dir / "event_summary.json"
    manifest_path = output_dir / "manifest.json"

    metadata_path.write_text(
        json.dumps(payload["metadata"], indent=2),
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(payload["summary"], indent=2),
        encoding="utf-8",
    )

    _write_csv(
        tick_metrics_path,
        payload["tick_metrics"],
        [
            "tick",
            "day",
            "population",
            "children",
            "juveniles",
            "adults",
            "old",
            "female",
            "male",
            "generation_0",
            "generation_1",
            "generation_2",
            "generation_3_plus",
            "gen1_adult_female_count",
            "gen1_adult_male_count",
            "gen1_female_near_nest",
            "gen1_female_with_mate",
            "gen1_avg_energy",
            "gen1_reproduction_block_reason",
            "births",
            "deaths",
            "settlements",
            "stored_food",
            "food_cells",
            "large_animals",
            "mean_energy",
            "mean_durability",
            "population_safe_low_food",
            "population_safe_high_food",
            "population_danger_high_food",
            "population_danger_low_food",
            "top_lineages",
        ],
    )
    _write_jsonl(events_path, payload["events"])
    _write_csv(
        lineage_path,
        payload["lineages"],
        [
            "lineage_id",
            "founder_agent_id",
            "total_births",
            "peak_population",
            "alive_now",
            "extinct_tick",
            "completed_lifespans",
            "total_agents_observed",
            "mean_final_age",
            "mean_brain_capacity",
            "mean_memory_retention",
            "mean_planning_focus",
            "mean_cooperation_drive",
            "mean_parenting_instinct",
            "mean_curiosity",
            "mean_fear",
            "mean_aggression",
            "mean_metabolism_rate",
            "mean_plant_efficiency",
            "mean_meat_efficiency",
            "mean_reproduction_drive",
            "mean_reproduction_investment",
            "mean_sensor_units",
            "mean_muscle_units",
            "mean_armor_units",
            "mean_brain_units",
        ],
    )
    _write_csv(
        agents_path,
        payload["agent_outcomes"],
        [
            "agent_id",
            "lineage_id",
            "parent_id",
            "other_parent_id",
            "sex",
            "generation",
            "body_profile",
            "body_inherited_from_profiles",
            "body_trait_mutation_count",
            "body_morphology_mutation_count",
            "body_units_json",
            "body_traits_json",
            "age",
            "children_count",
            "food_eaten",
            "distance_traveled",
            "stored_food_contributions",
            "matured_offspring_count",
            "alive",
            "completed_lifespan",
            "death_reason",
            "final_x",
            "final_y",
            "meals_by_type_json",
            "gathered_materials_json",
            "technology_constructions_json",
            "technology_uses_json",
        ],
    )
    _write_csv(
        generation_traits_path,
        payload["generation_traits"],
        [
            "generation",
            "agent_count",
            "adult_count",
            "mean_sensor_units",
            "mean_muscle_units",
            "mean_armor_units",
            "mean_brain_units",
            "mean_brain_capacity",
            "mean_memory_retention",
            "mean_planning_focus",
            "mean_cooperation_drive",
            "mean_parenting_instinct",
            "mean_curiosity",
            "mean_fear",
            "mean_aggression",
            "mean_metabolism_rate",
            "mean_plant_efficiency",
            "mean_meat_efficiency",
            "mean_reproduction_drive",
            "mean_reproduction_investment",
            "mean_trait_mutation_count",
            "mean_morphology_mutation_count",
        ],
    )
    methods_path.write_text(_methods_markdown(), encoding="utf-8")
    readable_log_path.write_text(_readable_log_markdown(payload), encoding="utf-8")
    checkpoints_path.write_text(_tick_checkpoints_markdown(payload), encoding="utf-8")
    event_summary_path.write_text(
        json.dumps(_event_summary(payload["events"]), indent=2),
        encoding="utf-8",
    )

    dashboard_html_path = ""
    dashboard_json_path = ""
    dashboard_payload = payload.get("dashboard_payload")
    if dashboard_payload is not None:
        dashboard_dir = output_dir / "dashboard"
        html_path, json_path = build_dashboard_artifacts(dashboard_dir, dashboard_payload)
        dashboard_html_path = str(html_path)
        dashboard_json_path = str(json_path)

    manifest = {
        "metadata": str(metadata_path),
        "summary": str(summary_path),
        "tick_metrics_csv": str(tick_metrics_path),
        "events_jsonl": str(events_path),
        "lineages_csv": str(lineage_path),
        "agent_outcomes_csv": str(agents_path),
        "generation_traits_csv": str(generation_traits_path),
        "methods_md": str(methods_path),
        "readable_log_md": str(readable_log_path),
        "tick_checkpoints_md": str(checkpoints_path),
        "event_summary_json": str(event_summary_path),
        "dashboard_html": dashboard_html_path,
        "dashboard_json": dashboard_json_path,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    manifest["manifest"] = str(manifest_path)
    return manifest


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def _write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            normalized = {}
            for column in columns:
                value = row.get(column)
                if isinstance(value, list):
                    normalized[column] = json.dumps(value, ensure_ascii=False)
                elif isinstance(value, dict):
                    normalized[column] = json.dumps(value, ensure_ascii=False, sort_keys=True)
                else:
                    normalized[column] = value
            writer.writerow(normalized)


def _methods_markdown() -> str:
    return """# Research Data Collection Protocol

## Purpose

This artifact bundle is designed for high-quality research reporting.
It preserves enough information to support:

- descriptive plots
- survival and lineage analysis
- event chronology reconstruction
- reproducibility and auditability
- appendix-level methods disclosure

## Included Files

- `metadata.json`: run configuration, body specification, world parameters, and provenance
- `summary.json`: final aggregate outcomes for the run
- `tick_metrics.csv`: per-tick panel for time-series analysis
- `events.jsonl`: structured event log with one JSON object per event
- `lineages.csv`: lineage-level aggregate outcomes
- `agent_outcomes.csv`: one row per observed agent at archive time
- `generation_traits.csv`: aggregate trait and morphology drift by generation
- `dashboard/`: replayable visualization bundle

## Recommended Use In A Paper

### Main Text

Use:

- `summary.json`
- selected plots from `tick_metrics.csv`
- aggregate lineage outcomes from `lineages.csv`

### Methods Section

Report:

- world size
- seed
- tick horizon
- initial population
- body design
- ecological settings
- event logging protocol
- snapshot interval

### Appendix / Supplement

Include or archive:

- `events.jsonl`
- `agent_outcomes.csv`
- raw `tick_metrics.csv`
- dashboard replay bundle

## Variable Notes

- `top_lineages` is stored as a JSON list in CSV cells.
- `population_*` biome variables count alive agents by biome each tick.
- `mean_energy` and `mean_durability` are alive-agent means at that tick.
- `agent_outcomes.csv` stores complex per-agent dictionaries as JSON strings.

## Reproducibility Notes

- Keep `metadata.json`, `summary.json`, and the experiment log together.
- For statistical reporting, run multiple seeds and treat one bundle as one replicate.
"""


def _event_summary(events: list[dict[str, object]]) -> dict[str, object]:
    counts: dict[str, int] = {}
    first_occurrence: dict[str, int] = {}
    for event in events:
        event_type = str(event.get("event_type", "unclassified"))
        counts[event_type] = counts.get(event_type, 0) + 1
        first_occurrence.setdefault(event_type, int(event.get("tick", 0)))
    return {
        "counts": counts,
        "first_occurrence_tick": first_occurrence,
    }


def _readable_log_markdown(payload: dict[str, object]) -> str:
    metadata = payload["metadata"]
    summary = payload["summary"]
    tick_metrics = payload["tick_metrics"]
    events = payload["events"]
    lineages = payload["lineages"]
    final_tick = metadata["final_tick"]
    final_snapshot = tick_metrics[-1] if tick_metrics else {}

    milestone_events = [
        event for event in events
        if event.get("event_type") in {
            "birth",
            "matured_child",
            "build_nest",
            "technology_emerged",
            "experiment_object",
            "hunt_success",
            "hunt_failed",
        }
    ][:60]

    top_lineages = sorted(
        lineages,
        key=lambda item: (-int(item["peak_population"]), str(item["lineage_id"])),
    )[:10]

    lines = [
        "# Readable Log",
        "",
        "## Run",
        "",
        f"- Run name: {metadata['run_name']}",
        f"- Change note: {metadata['change_note']}",
        f"- Seed: {metadata['seed']}",
        f"- Final tick: {final_tick}",
        f"- Body: {metadata['body_name']} | {metadata['body_design']}",
        "",
        "## Final Snapshot",
        "",
        f"- Population: {final_snapshot.get('population', 0)}",
        f"- Children: {final_snapshot.get('children', 0)}",
        f"- Juveniles: {final_snapshot.get('juveniles', 0)}",
        f"- Adults: {final_snapshot.get('adults', 0)}",
        f"- Old: {final_snapshot.get('old', 0)}",
        f"- Settlements: {final_snapshot.get('settlements', 0)}",
        f"- Stored food: {final_snapshot.get('stored_food', 0)}",
        "",
        "## Aggregate Outcomes",
        "",
        f"- Peak population: {summary['peak_population']}",
        f"- Total births: {summary['total_births']}",
        f"- Matured children: {summary['matured_children']}",
        f"- First birth tick: {summary['first_birth_tick']}",
        f"- First matured-child tick: {summary['first_matured_child_tick']}",
        f"- Death reasons: {json.dumps(summary['death_reasons'], ensure_ascii=False, sort_keys=True)}",
        "",
        "## Top Lineages",
        "",
    ]

    for lineage in top_lineages:
        lines.append(
            f"- {lineage['lineage_id']} | peak={lineage['peak_population']} | "
            f"births={lineage['total_births']} | alive_now={lineage['alive_now']} | "
            f"extinct_tick={lineage['extinct_tick']}"
        )

    lines.extend(["", "## Milestones", ""])
    if milestone_events:
        for event in milestone_events:
            lines.append(
                f"- tick={event.get('tick')} | {event.get('event_type')} | {event.get('raw_text')}"
            )
    else:
        lines.append("- No milestone events recorded.")

    return "\n".join(lines)


def _tick_checkpoints_markdown(payload: dict[str, object]) -> str:
    tick_metrics = payload["tick_metrics"]
    if not tick_metrics:
        return "# Tick Checkpoints\n\n- No tick metrics recorded."

    checkpoint_stride = max(1, len(tick_metrics) // 20)
    checkpoints = [
        tick_metrics[index]
        for index in range(0, len(tick_metrics), checkpoint_stride)
    ]
    if checkpoints[-1]["tick"] != tick_metrics[-1]["tick"]:
        checkpoints.append(tick_metrics[-1])

    lines = [
        "# Tick Checkpoints",
        "",
        "Condensed timeline for quick human reading.",
        "",
    ]
    for row in checkpoints:
        lines.append(
            f"- tick={row['tick']} day={row['day']} | pop={row['population']} | "
            f"births={row['births']} | deaths={row['deaths']} | "
            f"settlements={row['settlements']} | stored_food={row['stored_food']} | "
            f"top_lineages={row['top_lineages']}"
        )
    return "\n".join(lines)
