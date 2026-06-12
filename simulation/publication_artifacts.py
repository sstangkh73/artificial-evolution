from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path


def write_publication_artifacts(output_dir: Path, payload: dict[str, object]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir = output_dir / "figure_source_data"
    figure_dir.mkdir(parents=True, exist_ok=True)

    conditions = payload["conditions"]
    replicates = payload["replicates"]
    tick_metrics_long = payload["tick_metrics_long"]
    failure_rows = payload["failure_reasons"]
    lineage_rows = payload["lineage_rows"]
    event_rows = payload["event_rows"]

    condition_path = output_dir / "conditions.csv"
    replicate_path = output_dir / "replicate_index.csv"
    primary_path = output_dir / "primary_outcomes.csv"
    secondary_path = output_dir / "secondary_outcomes.csv"
    condition_stats_path = output_dir / "condition_level_statistics.csv"
    runtime_path = output_dir / "runtime_provenance.json"
    event_taxonomy_path = output_dir / "event_taxonomy.json"
    analysis_plan_path = output_dir / "statistical_analysis_plan.md"
    methods_path = output_dir / "methods_full.md"
    data_availability_path = output_dir / "data_availability_statement.md"
    negative_results_path = output_dir / "negative_results.md"
    figure_manifest_path = output_dir / "figure_manifest.json"
    manifest_path = output_dir / "publication_manifest.json"

    primary_rows = _primary_outcomes_rows(replicates)
    secondary_rows = _secondary_outcomes_rows(replicates)
    condition_stats = _condition_level_statistics(replicates)
    event_taxonomy = _event_taxonomy(event_rows)

    _write_csv(condition_path, conditions)
    _write_csv(replicate_path, replicates)
    _write_csv(primary_path, primary_rows)
    _write_csv(secondary_path, secondary_rows)
    _write_csv(condition_stats_path, condition_stats)
    runtime_path.write_text(json.dumps(payload["runtime_provenance"], indent=2), encoding="utf-8")
    event_taxonomy_path.write_text(json.dumps(event_taxonomy, indent=2), encoding="utf-8")
    analysis_plan_path.write_text(_analysis_plan_markdown(), encoding="utf-8")
    methods_path.write_text(_methods_full_markdown(conditions), encoding="utf-8")
    data_availability_path.write_text(_data_availability_markdown(output_dir), encoding="utf-8")
    negative_results_path.write_text(_negative_results_markdown(replicates), encoding="utf-8")

    figure_manifest = {
        "figure_1_condition_matrix": str(_write_csv(figure_dir / "figure_1_condition_matrix.csv", conditions)),
        "figure_2_population_trajectories": str(_write_csv(figure_dir / "figure_2_population_trajectories.csv", tick_metrics_long)),
        "figure_3_survival_curves": str(_write_csv(figure_dir / "figure_3_survival_curves.csv", _survival_curve_rows(replicates))),
        "figure_4_reproduction_funnel": str(_write_csv(figure_dir / "figure_4_reproduction_funnel.csv", _reproduction_funnel_rows(replicates))),
        "figure_5_technology_emergence": str(_write_csv(figure_dir / "figure_5_technology_emergence.csv", _technology_rows(replicates))),
        "figure_6_failure_reasons": str(_write_csv(figure_dir / "figure_6_failure_reasons.csv", failure_rows)),
        "figure_7_lineage_outcomes": str(_write_csv(figure_dir / "figure_7_lineage_outcomes.csv", lineage_rows)),
        "figure_8_condition_statistics": str(_write_csv(figure_dir / "figure_8_condition_statistics.csv", condition_stats)),
    }
    figure_manifest_path.write_text(json.dumps(figure_manifest, indent=2), encoding="utf-8")

    manifest = {
        "conditions_csv": str(condition_path),
        "replicate_index_csv": str(replicate_path),
        "primary_outcomes_csv": str(primary_path),
        "secondary_outcomes_csv": str(secondary_path),
        "condition_level_statistics_csv": str(condition_stats_path),
        "runtime_provenance_json": str(runtime_path),
        "event_taxonomy_json": str(event_taxonomy_path),
        "statistical_analysis_plan_md": str(analysis_plan_path),
        "methods_full_md": str(methods_path),
        "data_availability_statement_md": str(data_availability_path),
        "negative_results_md": str(negative_results_path),
        "figure_manifest_json": str(figure_manifest_path),
        "figure_source_data_dir": str(figure_dir),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    manifest["publication_manifest"] = str(manifest_path)
    return manifest


def _write_csv(path: Path, rows: list[dict[str, object]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            normalized = {}
            for field in fieldnames:
                value = row.get(field)
                if isinstance(value, (list, dict)):
                    normalized[field] = json.dumps(value, ensure_ascii=False, sort_keys=True)
                else:
                    normalized[field] = value
            writer.writerow(normalized)
    return path


def _primary_outcomes_rows(replicates: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in replicates:
        rows.append(
            {
                "condition_id": row["condition_id"],
                "replicate_id": row["replicate_id"],
                "seed": row["seed"],
                "population_extinct": row["population_extinct"],
                "final_tick": row["final_tick"],
                "gen3_success": row["target_generation_reached"],
                "gen3_tick": row["target_generation_tick"],
                "first_technology_tick": row["first_technology_tick"],
                "first_technology_name": row["first_technology_name"],
                "peak_population": row["peak_population"],
                "total_births": row["total_births"],
                "matured_children": row["matured_children"],
            }
        )
    return rows


def _secondary_outcomes_rows(replicates: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in replicates:
        rows.append(
            {
                "condition_id": row["condition_id"],
                "replicate_id": row["replicate_id"],
                "seed": row["seed"],
                "first_birth_tick": row["first_birth_tick"],
                "first_matured_child_tick": row["first_matured_child_tick"],
                "stored_food_total": row["stored_food_total"],
                "average_age": row["average_age"],
                "average_food_eaten": row["average_food_eaten"],
                "average_children": row["average_children"],
                "completed_lineages": row["completed_lineages"],
                "final_population": row["final_population"],
                "final_female": row["final_female"],
                "final_male": row["final_male"],
                "max_generation_observed": row["max_generation_observed"],
                "reproduction_failure_events": row["reproduction_failure_events"],
                "mean_agent_memory_sites": row.get("mean_agent_memory_sites", 0),
                "max_agent_memory_sites": row.get("max_agent_memory_sites", 0),
                "social_contact_rate": row.get("social_contact_rate", 0),
                "object_experiment_agent_rate": row.get("object_experiment_agent_rate", 0),
                "mean_friend_count": row.get("mean_friend_count", 0),
            }
        )
    return rows


def _condition_level_statistics(replicates: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in replicates:
        grouped.setdefault(str(row["condition_id"]), []).append(row)

    stats_rows: list[dict[str, object]] = []
    for condition_id, rows in grouped.items():
        peak_values = [float(item["peak_population"]) for item in rows]
        births = [float(item["total_births"]) for item in rows]
        matured = [float(item["matured_children"]) for item in rows]
        final_ticks = [float(item["final_tick"]) for item in rows]
        tech_ticks = [float(item["first_technology_tick"]) for item in rows if item["first_technology_tick"] not in (None, "")]
        memory_means = [float(item.get("mean_agent_memory_sites", 0) or 0) for item in rows]
        social_rates = [float(item.get("social_contact_rate", 0) or 0) for item in rows]
        object_experiment_rates = [float(item.get("object_experiment_agent_rate", 0) or 0) for item in rows]
        gen3_successes = sum(1 for item in rows if bool(item["target_generation_reached"]))
        extinctions = sum(1 for item in rows if bool(item["population_extinct"]))
        tech_successes = sum(1 for item in rows if item["first_technology_tick"] not in (None, ""))
        stats_rows.append(
            {
                "condition_id": condition_id,
                "replicates": len(rows),
                "gen3_success_rate": round(gen3_successes / len(rows), 4),
                "gen3_success_wilson_low": round(_wilson_interval(gen3_successes, len(rows))[0], 4),
                "gen3_success_wilson_high": round(_wilson_interval(gen3_successes, len(rows))[1], 4),
                "extinction_rate": round(extinctions / len(rows), 4),
                "technology_emergence_rate": round(tech_successes / len(rows), 4),
                "peak_population_mean": round(statistics.fmean(peak_values), 3),
                "peak_population_median": round(statistics.median(peak_values), 3),
                "total_births_mean": round(statistics.fmean(births), 3),
                "matured_children_mean": round(statistics.fmean(matured), 3),
                "final_tick_mean": round(statistics.fmean(final_ticks), 3),
                "first_technology_tick_mean": round(statistics.fmean(tech_ticks), 3) if tech_ticks else None,
                "mean_agent_memory_sites_mean": round(statistics.fmean(memory_means), 3),
                "social_contact_rate_mean": round(statistics.fmean(social_rates), 4),
                "object_experiment_agent_rate_mean": round(statistics.fmean(object_experiment_rates), 4),
                "peak_population_iqr": round(_iqr(peak_values), 3),
                "total_births_iqr": round(_iqr(births), 3),
                "matured_children_iqr": round(_iqr(matured), 3),
            }
        )
    return stats_rows


def _wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return (0.0, 0.0)
    p_hat = successes / total
    denominator = 1 + (z * z) / total
    center = (p_hat + (z * z) / (2 * total)) / denominator
    margin = (z / denominator) * math.sqrt((p_hat * (1 - p_hat) / total) + ((z * z) / (4 * total * total)))
    return (max(0.0, center - margin), min(1.0, center + margin))


def _iqr(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return 0.0
    midpoint = len(ordered) // 2
    if len(ordered) % 2 == 0:
        lower = ordered[:midpoint]
        upper = ordered[midpoint:]
    else:
        lower = ordered[:midpoint]
        upper = ordered[midpoint + 1:]
    if not lower or not upper:
        return 0.0
    return statistics.median(upper) - statistics.median(lower)


def _survival_curve_rows(replicates: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in replicates:
        grouped.setdefault(str(row["condition_id"]), []).append(row)
    rows: list[dict[str, object]] = []
    for condition_id, items in grouped.items():
        max_tick = max(int(item["final_tick"]) for item in items)
        for tick in range(0, max_tick + 1):
            alive = sum(1 for item in items if int(item["final_tick"]) >= tick)
            unresolved_gen3 = sum(
                1
                for item in items
                if item["target_generation_tick"] in (None, "") or int(item["target_generation_tick"]) >= tick
            )
            rows.append(
                {
                    "condition_id": condition_id,
                    "tick": tick,
                    "population_survival_fraction": round(alive / len(items), 4),
                    "gen3_not_yet_reached_fraction": round(unresolved_gen3 / len(items), 4),
                }
            )
    return rows


def _reproduction_funnel_rows(replicates: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in replicates:
        rows.extend(
            [
                {"condition_id": item["condition_id"], "replicate_id": item["replicate_id"], "stage": "founders", "count": item["initial_population"]},
                {"condition_id": item["condition_id"], "replicate_id": item["replicate_id"], "stage": "births", "count": item["total_births"]},
                {"condition_id": item["condition_id"], "replicate_id": item["replicate_id"], "stage": "matured_children", "count": item["matured_children"]},
                {"condition_id": item["condition_id"], "replicate_id": item["replicate_id"], "stage": "gen3_success", "count": 1 if item["target_generation_reached"] else 0},
            ]
        )
    return rows


def _technology_rows(replicates: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "condition_id": item["condition_id"],
            "replicate_id": item["replicate_id"],
            "seed": item["seed"],
            "first_technology_tick": item["first_technology_tick"],
            "first_technology_name": item["first_technology_name"],
            "technology_emerged": item["first_technology_tick"] is not None,
        }
        for item in replicates
    ]


def _event_taxonomy(event_rows: list[dict[str, object]]) -> dict[str, object]:
    counts: dict[str, int] = {}
    by_condition: dict[str, dict[str, int]] = {}
    for event in event_rows:
        event_type = str(event.get("event_type", "unclassified"))
        condition_id = str(event.get("condition_id", "unknown"))
        counts[event_type] = counts.get(event_type, 0) + 1
        bucket = by_condition.setdefault(condition_id, {})
        bucket[event_type] = bucket.get(event_type, 0) + 1
    return {
        "global_counts": counts,
        "by_condition": by_condition,
    }


def _analysis_plan_markdown() -> str:
    return """# Statistical Analysis Plan

## Primary Outcomes

- Probability of reaching generation-3 adulthood
- Time to generation-3 adulthood
- Time to first emergent technology
- Population extinction status and extinction time

## Secondary Outcomes

- Peak population
- Total births
- Matured children
- Stored food accumulation
- Reproduction failure burden

## Planned Comparisons

- Compare conditions on binary outcomes using proportions with Wilson confidence intervals.
- Compare continuous outcomes using medians, IQR, means, and full replicate distributions.
- Use survival-style curves for extinction and generation-3 attainment.
- Treat each seed as one replicate and avoid collapsing to single-run claims.

## Reporting Practice

- Report per-condition sample size explicitly.
- Show representative trajectories only alongside aggregate replicate summaries.
- Keep source data for every figure panel in `figure_source_data/`.
"""


def _methods_full_markdown(conditions: list[dict[str, object]]) -> str:
    lines = [
        "# Full Methods",
        "",
        "## Simulation Design",
        "",
        "This package records a publication-grade batch of agent-based simulation replicates.",
        "Each condition is defined explicitly and each seed is treated as an independent replicate.",
        "",
        "## Condition Registry",
        "",
    ]
    for row in conditions:
        lines.append(
            f"- {row['condition_id']}: body_index={row['body_index']} | initial_population={row['initial_population']} | "
            f"max_ticks={row['max_ticks']} | founder_mode={row['founder_mode']} | stop_on_generation_adult={row['stop_on_generation_adult']}"
        )
    lines.extend(
        [
            "",
            "## Recorded Layers",
            "",
            "- Per-run metadata",
            "- Per-tick state panel",
            "- Structured event logs",
            "- Lineage-level outcomes",
            "- Agent-level outcomes",
            "- Figure-ready aggregate tables",
            "",
            "## Reproducibility Notes",
            "",
            "- The replicate index maps every condition and seed to a raw manifest path.",
            "- Figure source data are exported separately to avoid hidden plotting transforms.",
            "- Conditions, statistics, and negative results are preserved together in one package.",
        ]
    )
    return "\n".join(lines)


def _data_availability_markdown(output_dir: Path) -> str:
    return f"""# Data Availability Statement

All data needed to interpret, verify, and extend the analyses in this project are stored in the publication package rooted at:

- `{output_dir}`

The package contains:

- condition definitions
- replicate index
- primary and secondary outcomes
- condition-level statistics
- event taxonomy
- figure source data
- links to underlying raw run manifests
"""


def _negative_results_markdown(replicates: list[dict[str, object]]) -> str:
    failures = [
        row
        for row in replicates
        if not row["target_generation_reached"] or row["population_extinct"]
    ]
    lines = [
        "# Negative and Boundary Results",
        "",
        f"- Total replicates with unresolved failure or extinction signals: {len(failures)}",
        "",
    ]
    for row in failures[:50]:
        lines.append(
            f"- {row['condition_id']} | replicate={row['replicate_id']} | seed={row['seed']} | "
            f"extinct={row['population_extinct']} | gen3={row['target_generation_reached']} | "
            f"final_tick={row['final_tick']} | first_technology_tick={row['first_technology_tick']}"
        )
    return "\n".join(lines)
