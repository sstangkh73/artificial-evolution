from __future__ import annotations

import csv
import json
import math
import re
import statistics
from pathlib import Path

MIN_JOURNAL_REPLICATES = 20
RECOMMENDED_JOURNAL_REPLICATES = 30

CONTINUOUS_OUTCOME_METRICS = (
    "peak_population",
    "total_births",
    "matured_children",
    "final_tick",
    "mean_agent_memory_sites",
    "social_contact_rate",
    "object_experiment_agent_rate",
)

T_CRITICAL_95 = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
    11: 2.201,
    12: 2.179,
    13: 2.16,
    14: 2.145,
    15: 2.131,
    16: 2.12,
    17: 2.11,
    18: 2.101,
    19: 2.093,
    20: 2.086,
    21: 2.08,
    22: 2.074,
    23: 2.069,
    24: 2.064,
    25: 2.06,
    26: 2.056,
    27: 2.052,
    28: 2.048,
    29: 2.045,
    30: 2.042,
}


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
    agent_outcome_rows = payload.get("agent_outcome_rows", [])

    condition_path = output_dir / "conditions.csv"
    replicate_path = output_dir / "replicate_index.csv"
    primary_path = output_dir / "primary_outcomes.csv"
    secondary_path = output_dir / "secondary_outcomes.csv"
    condition_stats_path = output_dir / "condition_level_statistics.csv"
    effect_sizes_path = output_dir / "condition_effect_sizes.csv"
    sample_size_audit_path = output_dir / "sample_size_audit.md"
    claim_scope_path = output_dir / "claim_scope.md"
    control_matrix_path = output_dir / "control_matrix.csv"
    ablation_control_plan_path = output_dir / "ablation_control_plan.md"
    agent_causal_trace_path = output_dir / "agent_causal_trace.csv"
    confound_audit_csv_path = output_dir / "confound_audit.csv"
    confound_audit_path = output_dir / "confound_audit.md"
    generalization_audit_csv_path = output_dir / "generalization_audit.csv"
    generalization_audit_path = output_dir / "generalization_audit.md"
    statistical_unit_audit_path = output_dir / "statistical_unit_audit.csv"
    statistical_model_spec_path = output_dir / "statistical_model_spec.md"
    frozen_protocol_path = output_dir / "frozen_protocol.json"
    reproducibility_checklist_path = output_dir / "reproducibility_checklist.md"
    novelty_framing_path = output_dir / "novelty_framing.md"
    claim_evidence_map_path = output_dir / "claim_evidence_map.csv"
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
    reference_condition_id = str(conditions[0]["condition_id"]) if conditions else None
    effect_sizes = _condition_effect_sizes(replicates, reference_condition_id)
    control_matrix = _control_matrix(conditions)
    agent_causal_trace = _agent_causal_trace(agent_outcome_rows, event_rows)
    confound_rows = _confound_audit_rows(
        conditions,
        replicates,
        event_rows,
        agent_causal_trace,
        control_matrix,
    )
    generalization_rows = _generalization_audit_rows(conditions, replicates, control_matrix)
    statistical_unit_rows = _statistical_unit_audit_rows(
        replicates,
        tick_metrics_long,
        event_rows,
        agent_causal_trace,
    )
    frozen_protocol = _frozen_protocol_json(conditions, payload["runtime_provenance"])
    claim_evidence_rows = _claim_evidence_map_rows(
        replicates,
        agent_causal_trace,
        generalization_rows,
        confound_rows,
        control_matrix,
    )
    event_taxonomy = _event_taxonomy(event_rows)

    _write_csv(condition_path, conditions)
    _write_csv(replicate_path, replicates)
    _write_csv(primary_path, primary_rows)
    _write_csv(secondary_path, secondary_rows)
    _write_csv(condition_stats_path, condition_stats)
    _write_csv(effect_sizes_path, effect_sizes)
    sample_size_audit_path.write_text(_sample_size_audit_markdown(replicates), encoding="utf-8")
    claim_scope_path.write_text(_claim_scope_markdown(), encoding="utf-8")
    _write_csv(control_matrix_path, control_matrix)
    ablation_control_plan_path.write_text(_ablation_control_plan_markdown(control_matrix), encoding="utf-8")
    _write_csv(agent_causal_trace_path, agent_causal_trace)
    _write_csv(confound_audit_csv_path, confound_rows)
    confound_audit_path.write_text(_confound_audit_markdown(confound_rows), encoding="utf-8")
    _write_csv(generalization_audit_csv_path, generalization_rows)
    generalization_audit_path.write_text(_generalization_audit_markdown(generalization_rows), encoding="utf-8")
    _write_csv(statistical_unit_audit_path, statistical_unit_rows)
    statistical_model_spec_path.write_text(_statistical_model_spec_markdown(statistical_unit_rows), encoding="utf-8")
    frozen_protocol_path.write_text(json.dumps(frozen_protocol, indent=2, sort_keys=True), encoding="utf-8")
    reproducibility_checklist_path.write_text(_reproducibility_checklist_markdown(frozen_protocol), encoding="utf-8")
    novelty_framing_path.write_text(_novelty_framing_markdown(), encoding="utf-8")
    _write_csv(claim_evidence_map_path, claim_evidence_rows)
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
        "figure_9_condition_effect_sizes": str(_write_csv(figure_dir / "figure_9_condition_effect_sizes.csv", effect_sizes)),
        "figure_10_control_matrix": str(_write_csv(figure_dir / "figure_10_control_matrix.csv", control_matrix)),
        "figure_11_agent_causal_trace": str(_write_csv(figure_dir / "figure_11_agent_causal_trace.csv", agent_causal_trace)),
        "figure_12_confound_audit": str(_write_csv(figure_dir / "figure_12_confound_audit.csv", confound_rows)),
        "figure_13_generalization_audit": str(_write_csv(figure_dir / "figure_13_generalization_audit.csv", generalization_rows)),
        "figure_14_statistical_unit_audit": str(_write_csv(figure_dir / "figure_14_statistical_unit_audit.csv", statistical_unit_rows)),
        "figure_15_claim_evidence_map": str(_write_csv(figure_dir / "figure_15_claim_evidence_map.csv", claim_evidence_rows)),
    }
    figure_manifest_path.write_text(json.dumps(figure_manifest, indent=2), encoding="utf-8")

    manifest = {
        "conditions_csv": str(condition_path),
        "replicate_index_csv": str(replicate_path),
        "primary_outcomes_csv": str(primary_path),
        "secondary_outcomes_csv": str(secondary_path),
        "condition_level_statistics_csv": str(condition_stats_path),
        "condition_effect_sizes_csv": str(effect_sizes_path),
        "sample_size_audit_md": str(sample_size_audit_path),
        "claim_scope_md": str(claim_scope_path),
        "control_matrix_csv": str(control_matrix_path),
        "ablation_control_plan_md": str(ablation_control_plan_path),
        "agent_causal_trace_csv": str(agent_causal_trace_path),
        "confound_audit_csv": str(confound_audit_csv_path),
        "confound_audit_md": str(confound_audit_path),
        "generalization_audit_csv": str(generalization_audit_csv_path),
        "generalization_audit_md": str(generalization_audit_path),
        "statistical_unit_audit_csv": str(statistical_unit_audit_path),
        "statistical_model_spec_md": str(statistical_model_spec_path),
        "frozen_protocol_json": str(frozen_protocol_path),
        "reproducibility_checklist_md": str(reproducibility_checklist_path),
        "novelty_framing_md": str(novelty_framing_path),
        "claim_evidence_map_csv": str(claim_evidence_map_path),
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
        row = {
            "condition_id": condition_id,
            "replicates": len(rows),
            "min_journal_replicates": MIN_JOURNAL_REPLICATES,
            "recommended_journal_replicates": RECOMMENDED_JOURNAL_REPLICATES,
            "sample_size_status": _sample_size_status(len(rows)),
            "gen3_success_rate": round(gen3_successes / len(rows), 4),
            "gen3_success_wilson_low": round(_wilson_interval(gen3_successes, len(rows))[0], 4),
            "gen3_success_wilson_high": round(_wilson_interval(gen3_successes, len(rows))[1], 4),
            "extinction_rate": round(extinctions / len(rows), 4),
            "technology_emergence_rate": round(tech_successes / len(rows), 4),
            "first_technology_tick_mean": round(statistics.fmean(tech_ticks), 3) if tech_ticks else None,
            "peak_population_median": round(statistics.median(peak_values), 3),
            "peak_population_iqr": round(_iqr(peak_values), 3),
            "total_births_iqr": round(_iqr(births), 3),
            "matured_children_iqr": round(_iqr(matured), 3),
        }
        metric_values = {
            "peak_population": peak_values,
            "total_births": births,
            "matured_children": matured,
            "final_tick": final_ticks,
            "mean_agent_memory_sites": memory_means,
            "social_contact_rate": social_rates,
            "object_experiment_agent_rate": object_experiment_rates,
        }
        for metric_name, values in metric_values.items():
            row.update(_continuous_summary_columns(metric_name, values))
        stats_rows.append(row)
    return stats_rows


def _condition_effect_sizes(
    replicates: list[dict[str, object]],
    reference_condition_id: str | None,
) -> list[dict[str, object]]:
    if reference_condition_id is None:
        return []

    grouped: dict[str, list[dict[str, object]]] = {}
    for row in replicates:
        grouped.setdefault(str(row["condition_id"]), []).append(row)

    reference_rows = grouped.get(reference_condition_id, [])
    if not reference_rows:
        return []

    effect_rows: list[dict[str, object]] = []
    for condition_id, rows in grouped.items():
        if condition_id == reference_condition_id:
            continue
        for metric_name in CONTINUOUS_OUTCOME_METRICS:
            reference_values = _continuous_values(reference_rows, metric_name)
            condition_values = _continuous_values(rows, metric_name)
            effect_rows.append(
                {
                    "reference_condition_id": reference_condition_id,
                    "condition_id": condition_id,
                    "metric": metric_name,
                    "reference_n": len(reference_values),
                    "condition_n": len(condition_values),
                    "reference_mean": _rounded_mean(reference_values),
                    "condition_mean": _rounded_mean(condition_values),
                    "mean_difference": _rounded_difference(condition_values, reference_values),
                    "hedges_g": _hedges_g(condition_values, reference_values),
                    "sample_size_status": _sample_size_status(min(len(reference_values), len(condition_values))),
                }
            )

        for outcome_name in ("target_generation_reached", "population_extinct", "technology_emerged"):
            reference_rate = _binary_rate(reference_rows, outcome_name)
            condition_rate = _binary_rate(rows, outcome_name)
            effect_rows.append(
                {
                    "reference_condition_id": reference_condition_id,
                    "condition_id": condition_id,
                    "metric": outcome_name,
                    "reference_n": len(reference_rows),
                    "condition_n": len(rows),
                    "reference_mean": reference_rate,
                    "condition_mean": condition_rate,
                    "mean_difference": round(condition_rate - reference_rate, 4),
                    "hedges_g": None,
                    "sample_size_status": _sample_size_status(min(len(reference_rows), len(rows))),
                }
            )
    return effect_rows


def _continuous_values(rows: list[dict[str, object]], metric_name: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = row.get(metric_name)
        if value in (None, ""):
            continue
        values.append(float(value))
    return values


def _continuous_summary_columns(metric_name: str, values: list[float]) -> dict[str, object]:
    n = len(values)
    if n == 0:
        return {
            f"{metric_name}_n": 0,
            f"{metric_name}_mean": None,
            f"{metric_name}_sd": None,
            f"{metric_name}_se": None,
            f"{metric_name}_ci95_low": None,
            f"{metric_name}_ci95_high": None,
        }

    mean_value = statistics.fmean(values)
    if n == 1:
        return {
            f"{metric_name}_n": n,
            f"{metric_name}_mean": round(mean_value, 3),
            f"{metric_name}_sd": None,
            f"{metric_name}_se": None,
            f"{metric_name}_ci95_low": None,
            f"{metric_name}_ci95_high": None,
        }

    sd = statistics.stdev(values)
    se = sd / math.sqrt(n)
    margin = _t_critical_95(n - 1) * se
    return {
        f"{metric_name}_n": n,
        f"{metric_name}_mean": round(mean_value, 3),
        f"{metric_name}_sd": round(sd, 3),
        f"{metric_name}_se": round(se, 3),
        f"{metric_name}_ci95_low": round(mean_value - margin, 3),
        f"{metric_name}_ci95_high": round(mean_value + margin, 3),
    }


def _t_critical_95(degrees_of_freedom: int) -> float:
    if degrees_of_freedom <= 0:
        return 0.0
    if degrees_of_freedom in T_CRITICAL_95:
        return T_CRITICAL_95[degrees_of_freedom]
    return 1.96


def _hedges_g(values: list[float], reference_values: list[float]) -> float | None:
    n_values = len(values)
    n_reference = len(reference_values)
    if n_values < 2 or n_reference < 2:
        return None

    sd_values = statistics.stdev(values)
    sd_reference = statistics.stdev(reference_values)
    pooled_df = n_values + n_reference - 2
    if pooled_df <= 0:
        return None
    pooled_variance = (
        ((n_values - 1) * sd_values * sd_values)
        + ((n_reference - 1) * sd_reference * sd_reference)
    ) / pooled_df
    if pooled_variance <= 0:
        return None

    cohen_d = (statistics.fmean(values) - statistics.fmean(reference_values)) / math.sqrt(pooled_variance)
    correction = 1.0 - (3.0 / ((4.0 * (n_values + n_reference)) - 9.0))
    return round(cohen_d * correction, 4)


def _rounded_mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(statistics.fmean(values), 4)


def _rounded_difference(values: list[float], reference_values: list[float]) -> float | None:
    if not values or not reference_values:
        return None
    return round(statistics.fmean(values) - statistics.fmean(reference_values), 4)


def _binary_rate(rows: list[dict[str, object]], outcome_name: str) -> float:
    if not rows:
        return 0.0
    if outcome_name == "technology_emerged":
        successes = sum(1 for row in rows if row.get("first_technology_tick") not in (None, ""))
    else:
        successes = sum(1 for row in rows if bool(row.get(outcome_name)))
    return round(successes / len(rows), 4)


def _sample_size_status(replicates: int) -> str:
    if replicates >= RECOMMENDED_JOURNAL_REPLICATES:
        return "recommended_journal_grade"
    if replicates >= MIN_JOURNAL_REPLICATES:
        return "minimum_journal_grade"
    return "underpowered"


def _sample_size_audit_markdown(replicates: list[dict[str, object]]) -> str:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in replicates:
        grouped.setdefault(str(row["condition_id"]), []).append(row)

    lines = [
        "# Sample Size Audit",
        "",
        f"- Minimum journal-grade replicates per condition: {MIN_JOURNAL_REPLICATES}",
        f"- Recommended journal-grade replicates per condition: {RECOMMENDED_JOURNAL_REPLICATES}",
        "- Independent unit: seed/run, not agent row.",
        "",
        "| condition_id | replicates | status |",
        "| --- | ---: | --- |",
    ]
    for condition_id, rows in grouped.items():
        lines.append(f"| {condition_id} | {len(rows)} | {_sample_size_status(len(rows))} |")

    underpowered = [condition_id for condition_id, rows in grouped.items() if len(rows) < MIN_JOURNAL_REPLICATES]
    lines.extend(["", "## Verdict", ""])
    if underpowered:
        lines.append("This package is not journal-grade for confirmatory inference yet.")
        lines.append("")
        lines.append("Underpowered conditions:")
        for condition_id in underpowered:
            lines.append(f"- `{condition_id}`")
    else:
        lines.append("All conditions meet the minimum journal-grade replicate threshold.")

    return "\n".join(lines)


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


def _claim_scope_markdown() -> str:
    return """# Claim Scope

## Permitted Claims

- Agents can show experience-sensitive behavior when direct interaction, memory, and later behavior are present in the same agent-level trace.
- Seed-level replicate batches can support condition-level differences when the sample-size audit marks the condition as journal-grade.
- Ecological feedback can be discussed as an observed simulation outcome when event logs connect actions, resources, and later population dynamics.
- Social context can be reported as a measured covariate when friend/contact fields are present.

## Prohibited Claims Without Additional Evidence

- Do not claim intentional farming or agriculture unless agents repeatedly create, protect, revisit, and benefit from planted sites under hotspot and hunger controls.
- Do not claim social transmission unless isolated, exposed, and naive-agent controls show transfer beyond individual experience.
- Do not claim language, symbolic communication, or teaching unless explicit signal production, reception, and counterfactual controls are added.
- Do not claim open-ended evolution unless long-run novelty, heritable variation, and non-saturating adaptive dynamics are shown across independent seeds.
- Do not claim planning or goal understanding from aggregate survival, reproduction, or technology outcomes alone.

## Evidence Needed To Upgrade Claims

| Candidate claim | Minimum upgrade evidence |
| --- | --- |
| Individual food-value learning | Same-agent taste, learned value, later skip/choice, and no skip-without-taste failures. |
| Site-selection learning | Same-agent site experience followed by return or improved placement under shuffled/hotspot controls. |
| Social transmission | Naive agents change behavior after exposure to experienced agents while isolated controls do not. |
| Intentional farming | Repeated seed placement, maintenance or return, delayed food benefit, and hunger/hotspot controls. |
| Open-ended evolution | Independent long runs with heritable novelty, persistent selection gradients, and no fixed ceiling in outcome diversity. |

## Writing Boundary

Manuscript language should prefer "experience-sensitive behavior", "direct-interaction learning proxy", and "ecological feedback" until the required controls above are present. Stronger cognitive language must cite the exact artifact that satisfies the upgrade evidence.
"""


def _control_matrix(conditions: list[dict[str, object]]) -> list[dict[str, object]]:
    return [_control_matrix_row(condition) for condition in conditions]


def _control_matrix_row(condition: dict[str, object]) -> dict[str, object]:
    condition_id = str(condition.get("condition_id", "unknown"))
    text = _condition_search_text(condition)
    env_kwargs = _as_dict(condition.get("env_kwargs"))
    family = _control_family(text)
    role = _learning_control_role(text, family)
    return {
        "condition_id": condition_id,
        "label": condition.get("label", ""),
        "control_family": family,
        "learning_control_role": role,
        "tests_against": _control_tests_against(role),
        "interpretation_limit": _control_interpretation_limit(role, family),
        "founder_mode": condition.get("founder_mode", ""),
        "spawn_strategy": condition.get("spawn_strategy", ""),
        "initial_population": condition.get("initial_population", ""),
        "max_ticks": condition.get("max_ticks", ""),
        "env_knob_count": len(env_kwargs),
        "env_knobs_json": env_kwargs,
    }


def _condition_search_text(condition: dict[str, object]) -> str:
    env_kwargs = _as_dict(condition.get("env_kwargs"))
    parts = [
        str(condition.get("condition_id", "")),
        str(condition.get("label", "")),
        str(condition.get("question", "")),
        str(condition.get("founder_mode", "")),
        str(condition.get("spawn_strategy", "")),
        " ".join(str(key) for key in env_kwargs.keys()),
        " ".join(str(value) for value in env_kwargs.values()),
    ]
    return " ".join(parts).lower()


def _control_family(text: str) -> str:
    if "baseline" in text or "default world" in text:
        return "baseline"
    if "control" in text:
        return "control"
    if any(token in text for token in ("harsh", "low_food", "low food", "scarcity", "transfer", "frontier_cost")):
        return "stress_or_generalization"
    if any(token in text for token in ("pressure", "discovery", "world_model", "sexed_gen3", "collective")):
        return "candidate_treatment"
    return "unclassified"


def _learning_control_role(text: str, family: str) -> str:
    if family == "baseline":
        return "reference_baseline"
    if "sensory" in text:
        return "sensory_access_control"
    if any(token in text for token in ("memory_disabled", "no_memory", "memory_shuffle", "shuffled_memory")):
        return "memory_ablation"
    if any(token in text for token in ("value_blind", "no_learning", "diet_learning_disabled")):
        return "value_learning_ablation"
    if any(token in text for token in ("random_policy", "random_movement")):
        return "random_policy_control"
    if any(token in text for token in ("social_isolation", "no_social", "isolated")):
        return "social_isolation_control"
    if any(token in text for token in ("critical_hunger_drop_blocked", "hunger_decoupled", "seed_drop_block_critical_hunger")):
        return "hunger_decoupling_control"
    if any(token in text for token in ("hotspot", "shuffled_food", "food_signal_radius_cap", "spatial_control")):
        return "spatial_hotspot_control"
    if family == "stress_or_generalization":
        return "ecology_robustness_control"
    if "sexed" in text or "collective" in text:
        return "social_population_treatment"
    if "technology" in text or "frontier" in text or "object" in text:
        return "object_discovery_treatment"
    return "candidate_behavior_condition"


def _control_tests_against(role: str) -> str:
    return {
        "reference_baseline": "default survival, reproduction, memory, and event rates",
        "sensory_access_control": "pure sensory access without comparable cognitive/memory profile",
        "memory_ablation": "whether memory is required for the observed behavior",
        "value_learning_ablation": "whether learned food value is required for diet choice",
        "random_policy_control": "whether behavior exceeds random movement/action baselines",
        "social_isolation_control": "whether social proximity explains behavior transfer",
        "hunger_decoupling_control": "whether hunger state drives seed or food behavior",
        "spatial_hotspot_control": "whether fixed resource hotspots explain returns or feeding",
        "ecology_robustness_control": "whether the result survives altered resource pressure",
        "social_population_treatment": "whether larger sexed groups change persistence or social exposure",
        "object_discovery_treatment": "whether material access and scarcity alter object experimentation",
        "candidate_behavior_condition": "candidate effect; requires paired controls for causal interpretation",
    }.get(role, "unclassified role")


def _control_interpretation_limit(role: str, family: str) -> str:
    if role.endswith("_ablation") or role.endswith("_control") or family == "baseline":
        return "Can constrain a specific alternative explanation when sample size is adequate."
    if role.endswith("_treatment") or role == "candidate_behavior_condition":
        return "Can show an association, but causal learning claims require paired ablations and confound audit clearance."
    if family == "stress_or_generalization":
        return "Can test robustness, but not the mechanism by itself."
    return "Use for descriptive evidence only until paired controls are present."


def _ablation_control_plan_markdown(control_matrix: list[dict[str, object]]) -> str:
    catalog = _required_control_catalog()
    lines = [
        "# Ablation and Control Plan",
        "",
        "This audit classifies current package conditions and lists controls required before stronger causal claims.",
        "",
        "## Current Condition Roles",
        "",
        "| condition_id | family | role | interpretation limit |",
        "| --- | --- | --- | --- |",
    ]
    for row in control_matrix:
        lines.append(
            f"| {row['condition_id']} | {row['control_family']} | {row['learning_control_role']} | "
            f"{row['interpretation_limit']} |"
        )

    lines.extend(
        [
            "",
            "## Required Journal Controls",
            "",
            "| control | status | detects |",
            "| --- | --- | --- |",
        ]
    )
    for item in catalog:
        status = "present" if _has_control_coverage(control_matrix, item["keywords"]) else "missing"
        lines.append(f"| {item['name']} | {status} | {item['detects']} |")

    missing = [item["name"] for item in catalog if not _has_control_coverage(control_matrix, item["keywords"])]
    lines.extend(["", "## Verdict", ""])
    if missing:
        lines.append("The package is not yet a full causal ablation suite. Missing controls:")
        for name in missing:
            lines.append(f"- {name}")
    else:
        lines.append("All required control families are represented in this package.")
    return "\n".join(lines)


def _required_control_catalog() -> list[dict[str, object]]:
    return [
        {
            "name": "baseline/default-world reference",
            "keywords": ("baseline", "reference_baseline"),
            "detects": "default outcome rates and seed-level variation",
        },
        {
            "name": "sensory access control",
            "keywords": ("sensory", "sensory_access_control"),
            "detects": "high sensor access without the same cognitive/memory profile",
        },
        {
            "name": "ecology robustness or transfer control",
            "keywords": ("low_food", "low food", "harsh", "scarcity", "transfer", "ecology_robustness_control"),
            "detects": "resource-regime tuning and generalization limits",
        },
        {
            "name": "memory-disabled or memory-shuffled ablation",
            "keywords": ("memory_disabled", "no_memory", "memory_shuffle", "shuffled_memory", "memory_ablation"),
            "detects": "whether remembered locations are necessary",
        },
        {
            "name": "value-blind or no-learning diet ablation",
            "keywords": ("value_blind", "no_learning", "diet_learning_disabled", "value_learning_ablation"),
            "detects": "whether learned value, not fixed food contact, explains diet choice",
        },
        {
            "name": "random movement/action baseline",
            "keywords": ("random_policy", "random_movement", "random_policy_control"),
            "detects": "whether observed returns/actions exceed random behavior",
        },
        {
            "name": "social isolation/exposure control",
            "keywords": ("social_isolation", "no_social", "isolated", "social_isolation_control"),
            "detects": "whether social proximity or transfer explains behavior",
        },
        {
            "name": "hunger-decoupled seed-drop control",
            "keywords": ("critical_hunger_drop_blocked", "hunger_decoupled", "seed_drop_block_critical_hunger", "hunger_decoupling_control"),
            "detects": "whether hunger rules drive seed placement",
        },
        {
            "name": "spatial hotspot or shuffled-food control",
            "keywords": ("hotspot", "shuffled_food", "food_signal_radius_cap", "spatial_control", "spatial_hotspot_control"),
            "detects": "whether fixed resource hotspots explain return behavior",
        },
    ]


def _has_control_coverage(control_matrix: list[dict[str, object]], keywords: tuple[str, ...]) -> bool:
    lowered_keywords = tuple(keyword.lower() for keyword in keywords)
    for row in control_matrix:
        row_text = " ".join(str(value).lower() for value in row.values())
        if any(keyword in row_text for keyword in lowered_keywords):
            return True
    return False


def _agent_causal_trace(
    agent_outcome_rows: list[dict[str, object]],
    event_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    event_rollup = _agent_event_rollup(event_rows)
    agent_rows_by_key: dict[tuple[str, str, str, str], dict[str, object]] = {}

    for row in agent_outcome_rows:
        agent_id = row.get("agent_id")
        if agent_id in (None, ""):
            continue
        key = _agent_key(
            row.get("condition_id"),
            row.get("replicate_id"),
            row.get("seed"),
            agent_id,
        )
        agent_rows_by_key[key] = row

    for key in event_rollup:
        agent_rows_by_key.setdefault(
            key,
            {
                "condition_id": key[0],
                "replicate_id": key[1],
                "seed": key[2],
                "agent_id": key[3],
            },
        )

    rows: list[dict[str, object]] = []
    for key in sorted(agent_rows_by_key):
        condition_id, replicate_id, seed, agent_id = key
        agent = agent_rows_by_key[key]
        events = event_rollup.get(key, _empty_agent_event_summary())
        meals = _as_dict(agent.get("meals_by_type_json"))
        skipped = _as_dict(agent.get("skipped_food_by_type_json"))
        food_values = _as_dict(agent.get("food_value_memory_json"))

        raw_seed_meals = max(_dict_int(meals, "raw_seed"), int(events["raw_seed_meal_events"]))
        raw_plant_meals = max(
            _dict_int(meals, "raw_plant") + _dict_int(meals, "cooked_plant"),
            int(events["raw_plant_meal_events"]),
        )
        raw_seed_skips = max(_dict_int(skipped, "raw_seed"), int(events["raw_seed_skip_events"]))
        first_seed_tick = events["first_raw_seed_tick"]
        first_plant_tick = events["first_raw_plant_tick"]
        first_skip_tick = events["first_raw_seed_skip_tick"]
        experienced_before_skip = (
            first_skip_tick is not None
            and first_seed_tick is not None
            and first_plant_tick is not None
            and int(first_seed_tick) <= int(first_skip_tick)
            and int(first_plant_tick) <= int(first_skip_tick)
        )
        memory_total = sum(
            _as_int(agent.get(key_name))
            for key_name in (
                "remembered_food_sources_count",
                "remembered_safe_zones_count",
                "remembered_danger_count",
                "remembered_nest_locations_count",
            )
        )
        direct_taste = raw_seed_meals > 0 or raw_plant_meals > 0 or int(events["food_consumed_events"]) > 0
        skip_without_taste = raw_seed_skips > 0 and raw_seed_meals == 0
        friend_count = _as_int(agent.get("friend_count"))
        rows.append(
            {
                "condition_id": condition_id,
                "replicate_id": replicate_id,
                "seed": seed,
                "agent_id": agent_id,
                "agent_row_present": "generation" in agent or "alive" in agent,
                "generation": agent.get("generation"),
                "alive": agent.get("alive"),
                "immortal": agent.get("immortal"),
                "friend_count": friend_count,
                "social_contact_observed": friend_count > 0,
                "memory_site_total": memory_total,
                "remembered_food_sources_count": _as_int(agent.get("remembered_food_sources_count")),
                "food_eaten": _as_int(agent.get("food_eaten")),
                "raw_seed_meals": raw_seed_meals,
                "raw_plant_meals": raw_plant_meals,
                "raw_seed_skips": raw_seed_skips,
                "learned_raw_seed_value": _dict_float_or_none(food_values, "raw_seed"),
                "learned_raw_plant_value": _dict_float_or_none(food_values, "raw_plant"),
                "food_consumed_events": events["food_consumed_events"],
                "plant_lifecycle_food_consumed_events": events["plant_lifecycle_food_consumed_events"],
                "food_skipped_events": events["food_skipped_events"],
                "seed_picked_events": events["seed_picked_events"],
                "seed_dropped_events": events["seed_dropped_events"],
                "first_raw_seed_tick": first_seed_tick,
                "first_raw_plant_tick": first_plant_tick,
                "first_raw_seed_skip_tick": first_skip_tick,
                "has_direct_food_taste_trace": direct_taste,
                "seed_skip_without_recorded_taste": skip_without_taste,
                "experienced_seed_and_plant_before_seed_skip": experienced_before_skip,
                "learning_evidence_class": _learning_evidence_class(
                    direct_taste=direct_taste,
                    memory_total=memory_total,
                    raw_seed_skips=raw_seed_skips,
                    skip_without_taste=skip_without_taste,
                    experienced_before_skip=experienced_before_skip,
                ),
            }
        )
    return rows


def _agent_event_rollup(event_rows: list[dict[str, object]]) -> dict[tuple[str, str, str, str], dict[str, object]]:
    rollup: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for event in event_rows:
        agent_ids = _event_agent_ids(event)
        if not agent_ids:
            continue
        event_type = str(event.get("event_type", "unclassified"))
        tick = _as_int(event.get("tick"))
        kind = _event_field(event, "kind")
        for agent_id in agent_ids:
            key = _agent_key(
                event.get("condition_id"),
                event.get("replicate_id"),
                event.get("seed"),
                agent_id,
            )
            summary = rollup.setdefault(key, _empty_agent_event_summary())
            if event_type == "food_consumed":
                summary["food_consumed_events"] = int(summary["food_consumed_events"]) + 1
            elif event_type == "plant_lifecycle_food_consumed":
                summary["plant_lifecycle_food_consumed_events"] = int(summary["plant_lifecycle_food_consumed_events"]) + 1
            elif event_type == "food_skipped":
                summary["food_skipped_events"] = int(summary["food_skipped_events"]) + 1
            elif event_type == "seed_picked":
                summary["seed_picked_events"] = int(summary["seed_picked_events"]) + 1
            elif event_type == "seed_dropped":
                summary["seed_dropped_events"] = int(summary["seed_dropped_events"]) + 1

            if event_type in {"food_consumed", "plant_lifecycle_food_consumed"}:
                if kind == "raw_seed":
                    summary["raw_seed_meal_events"] = int(summary["raw_seed_meal_events"]) + 1
                    summary["first_raw_seed_tick"] = _min_optional_tick(summary["first_raw_seed_tick"], tick)
                elif kind in {"raw_plant", "cooked_plant"}:
                    summary["raw_plant_meal_events"] = int(summary["raw_plant_meal_events"]) + 1
                    summary["first_raw_plant_tick"] = _min_optional_tick(summary["first_raw_plant_tick"], tick)
            elif event_type == "food_skipped" and kind == "raw_seed":
                summary["raw_seed_skip_events"] = int(summary["raw_seed_skip_events"]) + 1
                summary["first_raw_seed_skip_tick"] = _min_optional_tick(summary["first_raw_seed_skip_tick"], tick)
    return rollup


def _empty_agent_event_summary() -> dict[str, object]:
    return {
        "food_consumed_events": 0,
        "plant_lifecycle_food_consumed_events": 0,
        "food_skipped_events": 0,
        "seed_picked_events": 0,
        "seed_dropped_events": 0,
        "raw_seed_meal_events": 0,
        "raw_plant_meal_events": 0,
        "raw_seed_skip_events": 0,
        "first_raw_seed_tick": None,
        "first_raw_plant_tick": None,
        "first_raw_seed_skip_tick": None,
    }


def _agent_key(
    condition_id: object,
    replicate_id: object,
    seed: object,
    agent_id: object,
) -> tuple[str, str, str, str]:
    return (
        "unknown" if condition_id in (None, "") else str(condition_id),
        "unknown" if replicate_id in (None, "") else str(replicate_id),
        "unknown" if seed in (None, "") else str(seed),
        "unknown" if agent_id in (None, "") else str(agent_id),
    )


def _event_agent_ids(event: dict[str, object]) -> list[str]:
    raw_agent_ids = event.get("agent_ids")
    if isinstance(raw_agent_ids, list):
        return [str(value) for value in raw_agent_ids]
    if isinstance(raw_agent_ids, str):
        try:
            decoded = json.loads(raw_agent_ids)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, list):
            return [str(value) for value in decoded]
    details = " ".join(str(event.get(field, "")) for field in ("details", "raw_text"))
    return [match.group(1) for match in re.finditer(r"agent=(\d+)", details)]


def _event_field(event: dict[str, object], name: str) -> str | None:
    for field in ("details", "raw_text"):
        text = str(event.get(field, ""))
        match = re.search(rf"(?:^|\s){re.escape(name)}=([^\s]+)", text)
        if match:
            return match.group(1)
    return None


def _min_optional_tick(current: object, candidate: int) -> int | None:
    if candidate <= 0 and current is None:
        return candidate
    if current in (None, ""):
        return candidate
    return min(int(current), candidate)


def _learning_evidence_class(
    *,
    direct_taste: bool,
    memory_total: int,
    raw_seed_skips: int,
    skip_without_taste: bool,
    experienced_before_skip: bool,
) -> str:
    if skip_without_taste:
        return "skip_without_recorded_seed_taste"
    if experienced_before_skip:
        return "direct_experience_before_skip"
    if direct_taste and raw_seed_skips > 0:
        return "direct_taste_and_later_skip_unordered"
    if direct_taste and memory_total > 0:
        return "direct_taste_with_memory"
    if direct_taste:
        return "direct_taste_only"
    if memory_total > 0:
        return "memory_without_food_trace"
    return "no_direct_learning_trace"


def _confound_audit_rows(
    conditions: list[dict[str, object]],
    replicates: list[dict[str, object]],
    event_rows: list[dict[str, object]],
    agent_trace_rows: list[dict[str, object]],
    control_matrix: list[dict[str, object]],
) -> list[dict[str, object]]:
    replicates_by_condition = _group_by_condition(replicates)
    events_by_condition = _group_by_condition(event_rows)
    agents_by_condition = _group_by_condition(agent_trace_rows)
    has_social_control = _has_control_coverage(control_matrix, ("social_isolation", "no_social", "isolated", "social_isolation_control"))
    has_hotspot_control = _has_control_coverage(control_matrix, ("hotspot", "shuffled_food", "food_signal_radius_cap", "spatial_control", "spatial_hotspot_control"))
    has_hunger_control = _has_control_coverage(control_matrix, ("critical_hunger_drop_blocked", "hunger_decoupled", "seed_drop_block_critical_hunger", "hunger_decoupling_control"))
    has_ecology_control = _has_control_coverage(control_matrix, ("low_food", "harsh", "scarcity", "transfer", "ecology_robustness_control"))

    rows: list[dict[str, object]] = []
    for condition in conditions:
        condition_id = str(condition.get("condition_id", "unknown"))
        condition_events = events_by_condition.get(condition_id, [])
        condition_replicates = replicates_by_condition.get(condition_id, [])
        condition_agents = agents_by_condition.get(condition_id, [])
        seed_drop_events = [event for event in condition_events if event.get("event_type") == "seed_dropped"]
        critical_hunger_drops = [event for event in seed_drop_events if _is_critical_hunger_seed_drop(event)]
        critical_hunger_fraction = (
            round(len(critical_hunger_drops) / len(seed_drop_events), 4)
            if seed_drop_events
            else None
        )
        social_contact_mean = _mean_numeric(condition_replicates, "social_contact_rate")
        immortal_fraction = _agent_boolean_fraction(condition_agents, "immortal")
        env_kwargs = _as_dict(condition.get("env_kwargs"))
        tuned_ecology_keys = sorted(str(key) for key in env_kwargs.keys())
        possible_hotspot_bias = _possible_hotspot_bias(condition, env_kwargs)

        hunger_status = _hunger_confound_status(
            seed_drop_count=len(seed_drop_events),
            critical_hunger_fraction=critical_hunger_fraction,
            has_hunger_control=has_hunger_control,
        )
        social_status = _social_confound_status(social_contact_mean, has_social_control)
        immortal_status = _immortal_confound_status(immortal_fraction)
        ecology_status = _ecology_confound_status(tuned_ecology_keys, has_ecology_control)
        hotspot_status = _hotspot_confound_status(possible_hotspot_bias, has_hotspot_control)
        overall = _overall_confound_verdict(
            hunger_status,
            social_status,
            immortal_status,
            ecology_status,
            hotspot_status,
        )
        rows.append(
            {
                "condition_id": condition_id,
                "replicates": len(condition_replicates),
                "seed_drop_events": len(seed_drop_events),
                "critical_hunger_seed_drops": len(critical_hunger_drops),
                "critical_hunger_seed_drop_fraction": critical_hunger_fraction,
                "hunger_confound_status": hunger_status,
                "social_contact_rate_mean": social_contact_mean,
                "social_confound_status": social_status,
                "agent_trace_rows": len(condition_agents),
                "immortal_agent_fraction": immortal_fraction,
                "immortal_confound_status": immortal_status,
                "tuned_ecology_key_count": len(tuned_ecology_keys),
                "tuned_ecology_keys_json": tuned_ecology_keys,
                "ecology_confound_status": ecology_status,
                "possible_hotspot_bias": possible_hotspot_bias,
                "hotspot_confound_status": hotspot_status,
                "has_hunger_control_in_package": has_hunger_control,
                "has_social_control_in_package": has_social_control,
                "has_hotspot_control_in_package": has_hotspot_control,
                "has_ecology_control_in_package": has_ecology_control,
                "overall_confound_verdict": overall,
                "interpretation_limit": _confound_interpretation_limit(overall),
            }
        )
    return rows


def _group_by_condition(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("condition_id", "unknown")), []).append(row)
    return grouped


def _is_critical_hunger_seed_drop(event: dict[str, object]) -> bool:
    critical_hunger = _event_field(event, "critical_hunger")
    context = _event_field(event, "context")
    instinct = _event_field(event, "instinct")
    return critical_hunger == "1" or context == "hunger" or instinct == "hunger"


def _mean_numeric(rows: list[dict[str, object]], field_name: str) -> float | None:
    values = [float(row[field_name]) for row in rows if row.get(field_name) not in (None, "")]
    if not values:
        return None
    return round(statistics.fmean(values), 4)


def _agent_boolean_fraction(rows: list[dict[str, object]], field_name: str) -> float | None:
    values = [row.get(field_name) for row in rows if row.get(field_name) not in (None, "")]
    if not values:
        return None
    positives = sum(1 for value in values if _as_bool(value))
    return round(positives / len(values), 4)


def _possible_hotspot_bias(condition: dict[str, object], env_kwargs: dict[str, object]) -> bool:
    text = _condition_search_text(condition)
    hotspot_knobs = {
        "food_signal_radius_cap",
        "plant_lifecycle_food_signal_weight",
        "max_food",
        "base_food_spawn_per_tick",
        "food_spawn_multiplier",
        "nest_support_food_chance",
        "nest_support_spawn_chance",
    }
    return "frontier_safe_high_food" in text or any(key in env_kwargs for key in hotspot_knobs)


def _hunger_confound_status(
    *,
    seed_drop_count: int,
    critical_hunger_fraction: float | None,
    has_hunger_control: bool,
) -> str:
    if seed_drop_count == 0:
        return "not_observed"
    if critical_hunger_fraction is not None and critical_hunger_fraction >= 0.5 and not has_hunger_control:
        return "high_risk_hunger_dominant_missing_control"
    if critical_hunger_fraction is not None and critical_hunger_fraction > 0:
        return "possible_hunger_contribution"
    if not has_hunger_control:
        return "not_detected_but_hunger_control_missing"
    return "not_detected_control_present"


def _social_confound_status(social_contact_mean: float | None, has_social_control: bool) -> str:
    if social_contact_mean is None:
        return "not_measured"
    if social_contact_mean > 0 and not has_social_control:
        return "possible_social_clustering_missing_control"
    if social_contact_mean > 0:
        return "social_contact_observed_control_present"
    if not has_social_control:
        return "not_detected_but_social_control_missing"
    return "not_detected_control_present"


def _immortal_confound_status(immortal_fraction: float | None) -> str:
    if immortal_fraction is None:
        return "not_measured"
    if immortal_fraction > 0:
        return "high_risk_immortal_agents_present"
    return "not_detected"


def _ecology_confound_status(tuned_ecology_keys: list[str], has_ecology_control: bool) -> str:
    if tuned_ecology_keys and not has_ecology_control:
        return "possible_tuned_ecology_missing_generalization_control"
    if tuned_ecology_keys:
        return "tuned_ecology_with_generalization_control"
    if not has_ecology_control:
        return "default_ecology_but_generalization_control_missing"
    return "default_ecology_with_generalization_control"


def _hotspot_confound_status(possible_hotspot_bias: bool, has_hotspot_control: bool) -> str:
    if possible_hotspot_bias and not has_hotspot_control:
        return "possible_hotspot_bias_missing_control"
    if possible_hotspot_bias:
        return "possible_hotspot_bias_control_present"
    if not has_hotspot_control:
        return "not_detected_but_hotspot_control_missing"
    return "not_detected_control_present"


def _overall_confound_verdict(*statuses: str) -> str:
    if any(status.startswith("high_risk") for status in statuses):
        return "high_risk"
    if any("missing" in status for status in statuses):
        return "requires_additional_controls"
    if any(status.startswith("possible") for status in statuses):
        return "possible_confound"
    return "low_current_signal"


def _confound_interpretation_limit(overall: str) -> str:
    return {
        "high_risk": "Do not make causal learning claims from this condition until the flagged confound is controlled.",
        "requires_additional_controls": "Use as descriptive or exploratory evidence; causal interpretation needs the missing controls.",
        "possible_confound": "Report with caution and pair with targeted controls.",
        "low_current_signal": "No major audited confound signal was detected in available package fields.",
    }[overall]


def _confound_audit_markdown(confound_rows: list[dict[str, object]]) -> str:
    lines = [
        "# Confound Audit",
        "",
        "This audit converts package metadata, event logs, replicate summaries, and agent traces into reviewer-facing confound flags.",
        "",
        "| condition_id | hunger | social | immortal | ecology | hotspot | overall |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in confound_rows:
        lines.append(
            f"| {row['condition_id']} | {row['hunger_confound_status']} | "
            f"{row['social_confound_status']} | {row['immortal_confound_status']} | "
            f"{row['ecology_confound_status']} | {row['hotspot_confound_status']} | "
            f"{row['overall_confound_verdict']} |"
        )

    high_risk = [row for row in confound_rows if row["overall_confound_verdict"] == "high_risk"]
    needs_controls = [row for row in confound_rows if row["overall_confound_verdict"] == "requires_additional_controls"]
    lines.extend(["", "## Verdict", ""])
    if high_risk:
        lines.append("At least one condition has a high-risk confound. Treat those findings as exploratory.")
    elif needs_controls:
        lines.append("No high-risk confound was detected, but additional controls are still required before strong causal claims.")
    else:
        lines.append("No major audited confound signal was detected in the available package fields.")

    lines.extend(
        [
            "",
            "## Interpretation Rule",
            "",
            "A condition can support a strong causal learning claim only when its sample size is adequate, its paired controls are present, and this audit does not flag high-risk or missing-control confounds.",
        ]
    )
    return "\n".join(lines)


def _as_dict(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value:
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return {}
        if isinstance(decoded, dict):
            return decoded
    return {}


def _dict_int(mapping: dict[str, object], key: str) -> int:
    return _as_int(mapping.get(key))


def _dict_float_or_none(mapping: dict[str, object], key: str) -> float | None:
    value = mapping.get(key)
    if value in (None, ""):
        return None
    return round(float(value), 4)


def _as_int(value: object) -> int:
    if value in (None, ""):
        return 0
    return int(float(value))


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes"}
    return bool(value)


def _generalization_audit_rows(
    conditions: list[dict[str, object]],
    replicates: list[dict[str, object]],
    control_matrix: list[dict[str, object]],
) -> list[dict[str, object]]:
    condition_seed_counts: dict[str, int] = {}
    for row in replicates:
        condition_seed_counts[str(row.get("condition_id", "unknown"))] = (
            condition_seed_counts.get(str(row.get("condition_id", "unknown")), 0) + 1
        )
    min_seed_count = min(condition_seed_counts.values(), default=0)

    body_levels = sorted({str(condition.get("body_index", "unknown")) for condition in conditions})
    ecology_levels = sorted({_ecology_level(condition) for condition in conditions})
    founder_levels = sorted({str(condition.get("founder_mode", "unknown")) for condition in conditions})
    population_levels = sorted({str(condition.get("initial_population", "unknown")) for condition in conditions})
    spawn_levels = sorted({str(condition.get("spawn_strategy", "unknown")) for condition in conditions})
    tick_levels = sorted({str(condition.get("max_ticks", "unknown")) for condition in conditions})
    control_roles = sorted({str(row.get("learning_control_role", "unknown")) for row in control_matrix})

    return [
        _generalization_axis_row(
            axis="seed_replication",
            unit="seed/run",
            observed_levels=[f"{condition_id}:{count}" for condition_id, count in sorted(condition_seed_counts.items())],
            level_count=min_seed_count,
            required_minimum=MIN_JOURNAL_REPLICATES,
            status=_sample_size_status(min_seed_count),
            interpretation="Condition-level inference generalizes across random seeds only at the seed/run unit.",
        ),
        _generalization_axis_row(
            axis="body_plan",
            unit="body_index",
            observed_levels=body_levels,
            level_count=len(body_levels),
            required_minimum=2,
            status=_axis_status(len(body_levels), 2),
            interpretation="Single-body results should be framed as body-specific; multiple bodies support broader morphology claims.",
        ),
        _generalization_axis_row(
            axis="ecology_regime",
            unit="env_kwargs profile",
            observed_levels=ecology_levels,
            level_count=len(ecology_levels),
            required_minimum=2,
            status=_axis_status(len(ecology_levels), 2),
            interpretation="Default-only results should not be claimed as ecology-general; altered resource regimes test transfer.",
        ),
        _generalization_axis_row(
            axis="social_scale",
            unit="founder_mode and initial_population",
            observed_levels=sorted({f"{mode}|n={population}" for mode in founder_levels for population in population_levels}),
            level_count=max(len(founder_levels), len(population_levels)),
            required_minimum=2,
            status=_axis_status(max(len(founder_levels), len(population_levels)), 2),
            interpretation="Social or collective claims need more than one founder scale or social regime.",
        ),
        _generalization_axis_row(
            axis="spawn_strategy",
            unit="spawn strategy",
            observed_levels=spawn_levels,
            level_count=len(spawn_levels),
            required_minimum=2,
            status=_axis_status(len(spawn_levels), 2),
            interpretation="Strategy-specific resource placement can create narrow results if only one spawn strategy is tested.",
        ),
        _generalization_axis_row(
            axis="time_horizon",
            unit="max_ticks",
            observed_levels=tick_levels,
            level_count=len(tick_levels),
            required_minimum=2,
            status=_axis_status(len(tick_levels), 2),
            interpretation="Short-run discoveries need longer-horizon checks before claims about persistence.",
        ),
        _generalization_axis_row(
            axis="control_role_coverage",
            unit="condition role",
            observed_levels=control_roles,
            level_count=len(control_roles),
            required_minimum=3,
            status=_axis_status(len(control_roles), 3),
            interpretation="Generalization is stronger when baseline, candidate, control, and robustness roles coexist.",
        ),
    ]


def _ecology_level(condition: dict[str, object]) -> str:
    env_kwargs = _as_dict(condition.get("env_kwargs"))
    if not env_kwargs:
        return "default_ecology"
    keys = ",".join(sorted(str(key) for key in env_kwargs.keys()))
    return f"modified_ecology:{keys}"


def _generalization_axis_row(
    *,
    axis: str,
    unit: str,
    observed_levels: list[str],
    level_count: int,
    required_minimum: int,
    status: str,
    interpretation: str,
) -> dict[str, object]:
    return {
        "axis": axis,
        "unit": unit,
        "observed_level_count": level_count,
        "required_minimum": required_minimum,
        "status": status,
        "observed_levels_json": observed_levels,
        "interpretation": interpretation,
    }


def _axis_status(level_count: int, required_minimum: int) -> str:
    if level_count >= required_minimum + 1:
        return "broad_coverage"
    if level_count >= required_minimum:
        return "minimum_coverage"
    if level_count > 0:
        return "single_or_weak_coverage"
    return "missing"


def _generalization_audit_markdown(generalization_rows: list[dict[str, object]]) -> str:
    lines = [
        "# Generalization Audit",
        "",
        "This audit reports which axes can support broad claims and which remain condition-specific.",
        "",
        "| axis | levels | required | status |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in generalization_rows:
        lines.append(
            f"| {row['axis']} | {row['observed_level_count']} | {row['required_minimum']} | {row['status']} |"
        )

    weak_rows = [
        row
        for row in generalization_rows
        if row["status"] in {"underpowered", "single_or_weak_coverage", "missing"}
    ]
    lines.extend(["", "## Verdict", ""])
    if weak_rows:
        lines.append("Generalization remains limited on these axes:")
        for row in weak_rows:
            lines.append(f"- {row['axis']}: {row['interpretation']}")
    else:
        lines.append("The package has at least minimum coverage on all audited generalization axes.")
    lines.extend(
        [
            "",
            "## Interpretation Rule",
            "",
            "Manuscript claims should name the axes that passed this audit. Axes with weak coverage should be described as limitations or future work.",
        ]
    )
    return "\n".join(lines)


def _statistical_unit_audit_rows(
    replicates: list[dict[str, object]],
    tick_metrics_long: list[dict[str, object]],
    event_rows: list[dict[str, object]],
    agent_causal_trace: list[dict[str, object]],
) -> list[dict[str, object]]:
    condition_count = len({str(row.get("condition_id", "unknown")) for row in replicates})
    seed_count = len({str(row.get("replicate_id", "unknown")) for row in replicates})
    agent_replicate_count = len({str(row.get("replicate_id", "unknown")) for row in agent_causal_trace})
    event_replicate_count = len({str(row.get("replicate_id", "unknown")) for row in event_rows})
    tick_replicate_count = len({str(row.get("replicate_id", "unknown")) for row in tick_metrics_long})
    return [
        {
            "data_layer": "replicate_outcomes",
            "row_count": len(replicates),
            "condition_count": condition_count,
            "replicate_count": seed_count,
            "independent_unit": "seed_run",
            "nested_within": "",
            "inferential_role": "primary condition-level inference",
            "recommended_model": "binomial/logistic for binary outcomes; robust linear or rank-based summaries for continuous outcomes; survival-style models for time-to-event outcomes",
            "pseudoreplication_risk": "low if each seed/run is counted once",
        },
        {
            "data_layer": "agent_causal_trace",
            "row_count": len(agent_causal_trace),
            "condition_count": condition_count,
            "replicate_count": agent_replicate_count,
            "independent_unit": "not_independent",
            "nested_within": "seed_run",
            "inferential_role": "mechanism trace or hierarchical secondary analysis",
            "recommended_model": "mixed-effects or hierarchical model with replicate_id as grouping factor; descriptive trace otherwise",
            "pseudoreplication_risk": "high if agent rows are treated as independent replicates",
        },
        {
            "data_layer": "event_log",
            "row_count": len(event_rows),
            "condition_count": condition_count,
            "replicate_count": event_replicate_count,
            "independent_unit": "not_independent",
            "nested_within": "seed_run and agent",
            "inferential_role": "mechanism and confound evidence",
            "recommended_model": "aggregate to seed/run first, or use hierarchical count/time-to-event models",
            "pseudoreplication_risk": "high if events are counted as independent replicates",
        },
        {
            "data_layer": "tick_panel",
            "row_count": len(tick_metrics_long),
            "condition_count": condition_count,
            "replicate_count": tick_replicate_count,
            "independent_unit": "not_independent",
            "nested_within": "seed_run over time",
            "inferential_role": "trajectory visualization and longitudinal secondary analysis",
            "recommended_model": "summarize trajectories per seed/run or use longitudinal mixed models",
            "pseudoreplication_risk": "high if ticks are treated as independent replicates",
        },
    ]


def _statistical_model_spec_markdown(unit_rows: list[dict[str, object]]) -> str:
    lines = [
        "# Statistical Unit and Model Specification",
        "",
        "## Independent Unit",
        "",
        "The independent unit for condition-level inference is the seed/run. Agent rows, event rows, and tick rows are nested observations.",
        "",
        "## Layer Audit",
        "",
        "| data_layer | independent_unit | nested_within | inferential_role |",
        "| --- | --- | --- | --- |",
    ]
    for row in unit_rows:
        lines.append(
            f"| {row['data_layer']} | {row['independent_unit']} | {row['nested_within']} | {row['inferential_role']} |"
        )

    lines.extend(
        [
            "",
            "## Planned Model Families",
            "",
            "- Binary outcomes: report seed-level proportions with Wilson intervals; use logistic/binomial models when confirmatory modeling is needed.",
            "- Continuous seed-level outcomes: report means, SD, SE, t-based 95% CI, medians, IQR, and Hedges g versus the reference condition.",
            "- Time-to-event outcomes: treat missing event ticks as censored; use survival-style curves and models when sufficient events exist.",
            "- Agent-level mechanism traces: treat agents as nested within seed/run; use hierarchical models or descriptive causal traces.",
            "- Event counts: aggregate to seed/run before condition comparisons unless using a hierarchical count model.",
            "",
            "## Pseudoreplication Guard",
            "",
            "Do not count agent rows, events, or ticks as independent replicates in condition-level tests.",
        ]
    )
    return "\n".join(lines)


def _frozen_protocol_json(
    conditions: list[dict[str, object]],
    runtime_provenance: dict[str, object],
) -> dict[str, object]:
    seed_start = runtime_provenance.get("seed_start", "<seed_start>")
    seed_count = runtime_provenance.get("seed_count_per_condition", "<seed_count>")
    snapshot_interval = runtime_provenance.get("snapshot_interval", "<snapshot_interval>")
    max_ticks = max((_as_int(condition.get("max_ticks")) for condition in conditions), default=0)
    return {
        "protocol_version": "journal-readiness-2026-06-26-v1",
        "freeze_status": "frozen_at_publication_package_generation",
        "independent_unit": "seed_run",
        "seed_policy": {
            "seed_start": seed_start,
            "seed_count_per_condition": seed_count,
            "minimum_journal_replicates_per_condition": MIN_JOURNAL_REPLICATES,
            "recommended_journal_replicates_per_condition": RECOMMENDED_JOURNAL_REPLICATES,
        },
        "condition_registry": [
            {
                "condition_id": condition.get("condition_id"),
                "body_index": condition.get("body_index"),
                "initial_population": condition.get("initial_population"),
                "max_population": condition.get("max_population"),
                "max_ticks": condition.get("max_ticks"),
                "founder_mode": condition.get("founder_mode"),
                "spawn_strategy": condition.get("spawn_strategy"),
                "env_kwargs": _as_dict(condition.get("env_kwargs")),
            }
            for condition in conditions
        ],
        "primary_outcomes": [
            "target_generation_reached",
            "target_generation_tick",
            "population_extinct",
            "final_tick",
            "first_technology_tick",
        ],
        "secondary_outcomes": [
            "peak_population",
            "total_births",
            "matured_children",
            "mean_agent_memory_sites",
            "social_contact_rate",
            "object_experiment_agent_rate",
        ],
        "required_artifacts": [
            "conditions.csv",
            "replicate_index.csv",
            "primary_outcomes.csv",
            "secondary_outcomes.csv",
            "condition_level_statistics.csv",
            "condition_effect_sizes.csv",
            "sample_size_audit.md",
            "claim_scope.md",
            "control_matrix.csv",
            "ablation_control_plan.md",
            "agent_causal_trace.csv",
            "confound_audit.csv",
            "generalization_audit.csv",
            "statistical_unit_audit.csv",
            "statistical_model_spec.md",
            "novelty_framing.md",
            "claim_evidence_map.csv",
        ],
        "rerun_command_templates": [
            (
                "python main.py --mode publication-batch "
                f"--seed {seed_start} --study-seeds {seed_count} "
                f"--dashboard-ticks {max_ticks} --snapshot-interval {snapshot_interval}"
            )
        ],
        "runtime_provenance": runtime_provenance,
    }


def _reproducibility_checklist_markdown(protocol: dict[str, object]) -> str:
    seed_policy = protocol["seed_policy"]
    command = protocol["rerun_command_templates"][0]
    return f"""# Reproducibility Checklist

## Freeze Status

- Protocol version: `{protocol['protocol_version']}`
- Freeze status: `{protocol['freeze_status']}`
- Independent unit: `{protocol['independent_unit']}`

## Seed Policy

- Seed start: `{seed_policy['seed_start']}`
- Seeds per condition: `{seed_policy['seed_count_per_condition']}`
- Minimum journal-grade replicates: `{seed_policy['minimum_journal_replicates_per_condition']}`
- Recommended journal-grade replicates: `{seed_policy['recommended_journal_replicates_per_condition']}`

## Required Before Submission

- Confirm every condition in `frozen_protocol.json` appears in `conditions.csv`.
- Confirm every condition has the intended seed count in `sample_size_audit.md`.
- Confirm claim language follows `claim_scope.md`.
- Confirm missing controls in `ablation_control_plan.md` are described as limitations.
- Confirm high-risk rows in `confound_audit.csv` are not used for strong causal claims.
- Confirm generalization limits in `generalization_audit.md` are represented in the Discussion.
- Confirm agent/event/tick rows are not counted as independent replicates.

## Rerun Template

```text
{command}
```
"""


def _claim_evidence_map_rows(
    replicates: list[dict[str, object]],
    agent_causal_trace: list[dict[str, object]],
    generalization_rows: list[dict[str, object]],
    confound_rows: list[dict[str, object]],
    control_matrix: list[dict[str, object]],
) -> list[dict[str, object]]:
    condition_counts: dict[str, int] = {}
    for row in replicates:
        condition_counts[str(row.get("condition_id", "unknown"))] = (
            condition_counts.get(str(row.get("condition_id", "unknown")), 0) + 1
        )
    min_replicates = min(condition_counts.values(), default=0)
    has_direct_agent_learning = any(
        row.get("learning_evidence_class") == "direct_experience_before_skip"
        for row in agent_causal_trace
    )
    high_risk_confound = any(row.get("overall_confound_verdict") == "high_risk" for row in confound_rows)
    generalization_weak = any(
        row.get("status") in {"underpowered", "single_or_weak_coverage", "missing"}
        for row in generalization_rows
    )
    has_full_control_suite = all(
        _has_control_coverage(control_matrix, item["keywords"])
        for item in _required_control_catalog()
    )
    sample_size_status = _sample_size_status(min_replicates)
    return [
        {
            "claim_id": "C1_individual_experience_sensitive_learning",
            "manuscript_role": "core claim when same-agent traces exist",
            "current_status": "supported_in_package" if has_direct_agent_learning else "requires_agent_trace_evidence",
            "evidence_artifacts": "agent_causal_trace.csv; claim_scope.md",
            "required_evidence": "same-agent direct experience before later changed behavior",
            "reviewer_risk": "medium if trace is sparse; high if inferred only from aggregate condition means",
        },
        {
            "claim_id": "C2_seed_level_condition_differences",
            "manuscript_role": "statistical result claim",
            "current_status": sample_size_status,
            "evidence_artifacts": "condition_level_statistics.csv; condition_effect_sizes.csv; sample_size_audit.md",
            "required_evidence": "seed/run-level replication with uncertainty and effect sizes",
            "reviewer_risk": "high when underpowered",
        },
        {
            "claim_id": "C3_generalization_beyond_single_setting",
            "manuscript_role": "bounded generalization claim",
            "current_status": "partial_or_limited" if generalization_weak else "minimum_generalization_coverage",
            "evidence_artifacts": "generalization_audit.csv; control_matrix.csv",
            "required_evidence": "coverage across seeds, bodies, ecology, social scale, and time horizon",
            "reviewer_risk": "high if weak axes are omitted from limitations",
        },
        {
            "claim_id": "C4_causal_learning_mechanism",
            "manuscript_role": "conditional mechanism claim",
            "current_status": "blocked_by_high_risk_confound" if high_risk_confound else "requires_paired_controls",
            "evidence_artifacts": "confound_audit.csv; ablation_control_plan.md; agent_causal_trace.csv",
            "required_evidence": "no high-risk confounds plus paired ablations",
            "reviewer_risk": "high without controls",
        },
        {
            "claim_id": "C5_social_transmission",
            "manuscript_role": "future work only",
            "current_status": "blocked_until_social_controls_exist" if not has_full_control_suite else "requires_direct_transfer_test",
            "evidence_artifacts": "claim_scope.md; ablation_control_plan.md",
            "required_evidence": "naive-agent exposure/isolation controls showing transfer beyond individual experience",
            "reviewer_risk": "very high if claimed now",
        },
        {
            "claim_id": "C6_intentional_farming_or_open_ended_evolution",
            "manuscript_role": "future work only",
            "current_status": "prohibited_by_claim_scope",
            "evidence_artifacts": "claim_scope.md; novelty_framing.md",
            "required_evidence": "repeated site creation/maintenance/benefit for farming; heritable novelty and non-saturating dynamics for open-ended evolution",
            "reviewer_risk": "very high if claimed now",
        },
    ]


def _novelty_framing_markdown() -> str:
    return """# Literature and Novelty Framing

## Core Contribution

This project should be framed as an artificial-life simulation study of experience-sensitive behavior in embodied, resource-constrained agents. The contribution is not a new reinforcement-learning algorithm and not proof of open-ended evolution. The contribution is a reproducible substrate, telemetry stack, and evidence package for testing whether agents can acquire useful behavior from direct interaction with a changing world.

## Literature-Adjacent Domains

- Artificial life and agent-based modeling: population, ecology, reproduction, and emergent behavior under explicit world rules.
- Embodied cognition: behavior is constrained by bodies, sensors, energy, memory, and local interaction.
- Reinforcement learning and adaptive behavior: the study asks whether behavior changes after experience, but without claiming standard RL training or policy optimization.
- Ecological simulation: resource feedback, plant lifecycle, hunger, and spatial structure are part of the causal substrate.
- Open-ended evolution: relevant as future work, but not a current claim unless heritable novelty and persistent selection are demonstrated.

## Novelty Boundary

The safest manuscript thesis is:

> Direct-interaction traces in a resource-constrained artificial-life world can reveal experience-sensitive behavior, while generated audits expose when broader learning, social transmission, farming, or open-ended-evolution claims remain unsupported.

## What Not To Claim

- Do not claim intentional agriculture from seed movement alone.
- Do not claim social learning without naive/exposed/isolated controls.
- Do not claim language or symbolic communication without explicit signal tests.
- Do not claim open-ended evolution without self-sustaining heritable novelty across long independent runs.

## How To Use This Artifact

Use `claim_evidence_map.csv` as the manuscript guardrail. Claims marked as future work should stay in Discussion/Future Work, not Abstract or Results.
"""


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
    return f"""# Statistical Analysis Plan

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
- Compare continuous outcomes using medians, IQR, means, standard deviations, standard errors, and t-based 95% confidence intervals.
- Report standardized mean differences using Hedges g for key continuous metrics relative to the package reference condition.
- Use survival-style curves for extinction and generation-3 attainment.
- Treat each seed as one replicate and avoid collapsing to single-run claims.

## Sample Size Rule

- Minimum journal-grade threshold: {MIN_JOURNAL_REPLICATES} independent seed-level replicates per condition.
- Recommended journal-grade target: {RECOMMENDED_JOURNAL_REPLICATES} independent seed-level replicates per condition.
- Agent-level rows are nested inside seed/run and must not be counted as independent replicates for inferential statistics.

## Reporting Practice

- Report per-condition sample size explicitly.
- Report sample-size status using `sample_size_audit.md`.
- Show representative trajectories only alongside aggregate replicate summaries.
- Keep source data for every figure panel in `figure_source_data/`.
- Keep claim language within `claim_scope.md`.
- Use `control_matrix.csv` and `ablation_control_plan.md` before upgrading an association to a causal claim.
- Use `agent_causal_trace.csv` for per-agent learning evidence; do not infer individual learning from aggregate condition means alone.
- Use `confound_audit.csv` and `confound_audit.md` to flag hunger, social, hotspot, immortal, and tuned-ecology alternatives.
- Use `generalization_audit.csv` and `generalization_audit.md` before making broad claims beyond the tested bodies, ecologies, and time horizons.
- Use `statistical_unit_audit.csv` and `statistical_model_spec.md` to prevent pseudoreplication.
- Freeze submission-facing runs with `frozen_protocol.json` and `reproducibility_checklist.md`.
- Use `novelty_framing.md` and `claim_evidence_map.csv` to align Results, Discussion, and Future Work claims.
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
            "- Claim-scope limits",
            "- Control and ablation coverage",
            "- Per-agent causal trace",
            "- Confound audit",
            "- Generalization audit",
            "- Statistical-unit audit and model specification",
            "- Frozen protocol and reproducibility checklist",
            "- Novelty framing and claim-evidence map",
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
- claim-scope limits
- control and ablation audit
- per-agent causal trace
- confound audit
- generalization audit
- statistical-unit audit and model specification
- frozen protocol and reproducibility checklist
- novelty framing and claim-evidence map
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
