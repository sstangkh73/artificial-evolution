# -*- coding: utf-8 -*-
"""Reproduce the E6/T2-RB red-team mechanism checks from raw founder records.

This is a post hoc descriptive analysis.  It does not replace or modify the
frozen confirmatory analyses.  The independent replicate is always the seed;
founder rows are aggregated within a run before any cross-arm contrast.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import shlex
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable

from analyze_e6_representation_payoff import EXPECTED_ENERGIES, ols_slope
from analyze_e_series import mean_sd, t_ci95
from run_e0_pilot import discrimination_index

E6_ARMS = ("B1", "B2", "B3")
T2_ARMS = ("A2", "A3O", "A3R")
DEATH_REASONS = ("starvation", "durability_depleted", "senescence")
MECHANISM_METRICS = (
    "founder_mean_followup_ticks",
    "fruit_meals_per_founder",
    "staple_meals_per_founder",
    "fruit_skips_per_founder_repeated_contact_count",
    "staple_skips_per_founder_repeated_contact_count",
    "fruit_acceptance_per_telemetry_encounter",
    "staple_acceptance_per_telemetry_encounter",
    "founders_ever_skipping_staple_fraction",
    "toxin_excess_per_founder",
    "toxin_excess_per_fruit_meal",
    "toxin_damage_per_founder",
    "death_fraction_starvation",
    "death_fraction_durability_depleted",
    "death_fraction_senescence",
)
OPTIONAL_CELL_METRICS = (
    "p_eat_given_safe",
    "p_eat_given_toxic",
    "discrimination_index",
    "potential_toxin_excess_per_fruit_encounter",
)
MONTE_CARLO_DRAWS = 200_000
MONTE_CARLO_SEED = 20260912


def _round(value: float | None) -> float | None:
    return round(value, 6) if value is not None else None


def _mean(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def _flag_value(flags: str, name: str, default: str | None = None) -> str | None:
    tokens = shlex.split(flags, posix=True)
    try:
        index = tokens.index(name)
    except ValueError:
        return default
    return tokens[index + 1] if index + 1 < len(tokens) else default


def _toxin_params(flags: str) -> dict:
    integer_flags = (
        "toxin-detox-ticks",
        "toxin-safe-window-start",
        "toxin-safe-window-end",
        "encounter-age-bin",
    )
    params = {}
    for name in integer_flags:
        value = _flag_value(flags, f"--{name}")
        if value is not None:
            params[name.replace("-", "_")] = int(value)
    return params


def _founder_initial_age(agent_id: int, population: int, spread: bool) -> int:
    # Frozen implementation constants at the generation commit.
    adult_age = 61
    max_age = 200
    founder_start_age = 67
    if not spread:
        return founder_start_age
    return adult_age + int(
        agent_id / max(1, population - 1) * (max_age - adult_age - 1)
    )


def validate_cells(payload: dict, expected_arms: set[str]) -> dict:
    spec = (payload.get("provenance") or {}).get("spec") or {}
    expected_seeds = {int(seed) for seed in spec.get("seeds", [])}
    observed = Counter((str(row.get("arm")), int(row.get("seed"))) for row in payload.get("rows", []))
    expected = {(arm, seed) for arm in expected_arms for seed in expected_seeds}
    duplicates = [
        {"arm": arm, "seed": seed, "count": count}
        for (arm, seed), count in sorted(observed.items()) if count > 1
    ]
    missing = [
        {"arm": arm, "seed": seed}
        for arm, seed in sorted(expected - set(observed))
    ]
    unexpected = [
        {"arm": arm, "seed": seed}
        for arm, seed in sorted(set(observed) - expected)
    ]
    return {
        "expected_cells": len(expected),
        "observed_rows": sum(observed.values()),
        "duplicates": duplicates,
        "missing": missing,
        "unexpected": unexpected,
        "passes": bool(expected_seeds) and not (duplicates or missing or unexpected),
    }


def _encounters(founders: list[dict], kind: str) -> dict[str, int]:
    result = {"seen": 0, "ate": 0, "skipped": 0}
    for founder in founders:
        for key, counts in (founder.get("encounters_by_kind_age") or {}).items():
            if key.partition("@")[0] != kind:
                continue
            for field in result:
                result[field] += int(counts.get(field, 0))
    return result


def _learned_rows(experiment: str, arm: str, seed: int, founders: list[dict]) -> list[dict]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for founder in founders:
        for key, value in (founder.get("food_value_memory") or {}).items():
            grouped[str(key)].append(float(value))
    rows = []
    for key, values in sorted(grouped.items()):
        rows.append({
            "experiment": experiment,
            "arm": arm,
            "seed": seed,
            "food_kind": key.partition("@")[0],
            "key": key,
            "n_founders_with_key": len(values),
            "mean_learned_value": _round(statistics.mean(values)),
            "sd_learned_value": _round(statistics.stdev(values)) if len(values) > 1 else 0.0,
        })
    return rows


def aggregate_founder_run(raw: dict, summary_row: dict, experiment: str) -> tuple[dict, list[dict]]:
    founders = [
        row for row in (raw.get("agent_diet_summary") or [])
        if int(row.get("generation", -1)) == 0
    ]
    if not founders:
        raise ValueError(f"no founder rows for {summary_row.get('arm')} seed {summary_row.get('seed')}")
    arm = str(summary_row["arm"])
    seed = int(summary_row["seed"])
    if int(raw.get("seed")) != seed:
        raise ValueError(f"raw seed {raw.get('seed')} does not match summary seed {seed}")
    population = int(_flag_value(str(summary_row.get("flags", "")), "--population", str(len(founders))))
    spread = int(_flag_value(str(summary_row.get("flags", "")), "--founder-age-spread", "0")) != 0
    followups = [
        float(founder["age"])
        - _founder_initial_age(int(founder["agent_id"]), population, spread)
        for founder in founders
    ]
    fruit_meals = [float((f.get("meals_by_type") or {}).get("raw_fruit", 0)) for f in founders]
    staple_meals = [float((f.get("meals_by_type") or {}).get("raw_plant", 0)) for f in founders]
    fruit_skips = [float((f.get("skipped_food_by_type") or {}).get("raw_fruit", 0)) for f in founders]
    staple_skips = [float((f.get("skipped_food_by_type") or {}).get("raw_plant", 0)) for f in founders]
    toxin = [float(f.get("toxin_ingested_total", 0.0)) for f in founders]
    toxin_damage = [float(f.get("toxin_damage_total", 0.0)) for f in founders]
    fruit_encounters = _encounters(founders, "raw_fruit")
    staple_encounters = _encounters(founders, "raw_plant")
    death_counts = Counter(str(f.get("death_reason")) for f in founders if not f.get("alive"))
    memories = [f.get("food_value_memory") or {} for f in founders]
    nonempty_memories = [memory for memory in memories if memory]
    best_known = [max(float(value) for value in memory.values()) for memory in nonempty_memories]
    pickiness = float(_flag_value(str(summary_row.get("flags", "")), "--pickiness", "0.6"))
    threshold_over_staple = [pickiness * value > 5.0 for value in best_known]
    fruit_key_below = []
    for memory in nonempty_memories:
        threshold = pickiness * max(float(value) for value in memory.values())
        fruit_values = [float(value) for key, value in memory.items() if str(key).partition("@")[0] == "raw_fruit"]
        if fruit_values:
            fruit_key_below.append(sum(value < threshold for value in fruit_values) / len(fruit_values))
    fruit_total = sum(fruit_meals)
    discrimination = discrimination_index(
        founders,
        _toxin_params(str(summary_row.get("flags", ""))),
        [float(f.get("toxin_tolerance", 0.2)) for f in founders],
    )
    record = {
        "experiment": experiment,
        "arm": arm,
        "seed": seed,
        "realized_fruit_energy": (
            int(arm[1:3]) if experiment == "E6" else float(summary_row.get("realized_gross_fruit_energy"))
        ),
        "founders": len(founders),
        "founders_censored": sum(bool(f.get("alive")) for f in founders),
        "founder_mean_followup_ticks": _round(statistics.mean(followups)),
        "fruit_meals_per_founder": _round(statistics.mean(fruit_meals)),
        "staple_meals_per_founder": _round(statistics.mean(staple_meals)),
        "fruit_skips_per_founder_repeated_contact_count": _round(statistics.mean(fruit_skips)),
        "staple_skips_per_founder_repeated_contact_count": _round(statistics.mean(staple_skips)),
        "fruit_encounters": fruit_encounters["seen"],
        "staple_encounters": staple_encounters["seen"],
        "fruit_acceptance_per_telemetry_encounter": _round(
            fruit_encounters["ate"] / fruit_encounters["seen"] if fruit_encounters["seen"] else None
        ),
        "staple_acceptance_per_telemetry_encounter": _round(
            staple_encounters["ate"] / staple_encounters["seen"] if staple_encounters["seen"] else None
        ),
        "founders_ever_skipping_staple_fraction": _round(
            sum(value > 0 for value in staple_skips) / len(founders)
        ),
        "founders_ever_skipping_fruit_fraction": _round(
            sum(value > 0 for value in fruit_skips) / len(founders)
        ),
        "toxin_excess_per_founder": _round(statistics.mean(toxin)),
        "toxin_excess_per_fruit_meal": _round(sum(toxin) / fruit_total if fruit_total else None),
        "toxin_damage_per_founder": _round(statistics.mean(toxin_damage)),
        "potential_toxin_excess_per_fruit_encounter": (
            float(summary_row["a2_mean_dose_at_encounter"])
            if summary_row.get("a2_mean_dose_at_encounter") is not None else None
        ),
        "p_eat_given_safe": discrimination.get("p_eat_given_safe"),
        "p_eat_given_toxic": discrimination.get("p_eat_given_toxic"),
        "discrimination_index": discrimination.get("discrimination_index"),
        "memory_empty_founders": len(memories) - len(nonempty_memories),
        "max_learned_value_nonempty_memory_mean": _round(_mean(best_known)),
        "fraction_nonempty_memory_with_relative_threshold_above_staple": _round(
            sum(threshold_over_staple) / len(threshold_over_staple) if threshold_over_staple else None
        ),
        "fruit_keys_below_relative_threshold_fraction": _round(_mean(fruit_key_below)),
        "summary_followup_delta": _round(
            statistics.mean(followups) - float(summary_row["founder_mean_followup_ticks"])
        ),
    }
    for reason in DEATH_REASONS:
        record[f"death_count_{reason}"] = int(death_counts.get(reason, 0))
        record[f"death_fraction_{reason}"] = _round(death_counts.get(reason, 0) / len(founders))
    if abs(float(record["summary_followup_delta"])) > 0.00011:
        raise ValueError(f"founder follow-up mismatch for {arm} seed {seed}: {record['summary_followup_delta']}")
    if sum(record[f"death_count_{reason}"] for reason in DEATH_REASONS) + record["founders_censored"] != len(founders):
        raise ValueError(f"unclassified founder outcome for {arm} seed {seed}")
    return record, _learned_rows(experiment, arm, seed, founders)


def paired_summary(records: list[dict], left: str, right: str, metric: str) -> dict:
    by_arm = {
        arm: {int(row["seed"]): float(row[metric]) for row in records if row["arm"] == arm}
        for arm in (left, right)
    }
    shared = sorted(set(by_arm[left]) & set(by_arm[right]))
    differences = [by_arm[left][seed] - by_arm[right][seed] for seed in shared]
    sd = statistics.stdev(differences) if len(differences) > 1 else 0.0
    superiority = (
        (sum(value > 0 for value in differences) + 0.5 * sum(value == 0 for value in differences))
        / len(differences) if differences else None
    )
    return {
        "contrast": f"{left}-{right}",
        "metric": metric,
        "n_pairs": len(shared),
        "paired_difference": mean_sd(differences),
        "paired_t_ci95": t_ci95(differences),
        "paired_standardized_mean_difference_dz": _round(
            statistics.mean(differences) / sd if sd else None
        ),
        "paired_probability_of_superiority": _round(superiority),
        "seeds_favouring_left": sum(value > 0 for value in differences),
        "seeds_favouring_right": sum(value < 0 for value in differences),
        "seeds_tied": sum(value == 0 for value in differences),
    }


def _cell_summaries(records: list[dict], group_fields: tuple[str, ...]) -> list[dict]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in records:
        grouped[tuple(row[field] for field in group_fields)].append(row)
    summaries = []
    for key, rows in sorted(grouped.items()):
        item = {field: value for field, value in zip(group_fields, key)}
        item["n_seeds"] = len(rows)
        item["metrics"] = {}
        for metric in MECHANISM_METRICS + OPTIONAL_CELL_METRICS:
            values = [float(row[metric]) for row in rows if row.get(metric) is not None]
            item["metrics"][metric] = {**mean_sd(values), "t_ci95": t_ci95(values)}
        summaries.append(item)
    return summaries


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    x_mean = statistics.mean(xs)
    y_mean = statistics.mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    denominator = math.sqrt(
        sum((x - x_mean) ** 2 for x in xs) * sum((y - y_mean) ** 2 for y in ys)
    )
    return numerator / denominator if denominator else None


def _within_cell_correlations(records: list[dict]) -> dict:
    def outcome_values(row: dict) -> dict[str, float]:
        followup = float(row["founder_mean_followup_ticks"])
        if followup <= 0:
            raise ValueError("rate-based mechanism descriptives require positive founder follow-up")
        return {
            "staple_meals_per_founder": float(row["staple_meals_per_founder"]),
            "fruit_meals_per_founder": float(row["fruit_meals_per_founder"]),
            "toxin_excess_per_founder": float(row["toxin_excess_per_founder"]),
            "toxin_damage_per_founder": float(row["toxin_damage_per_founder"]),
            "staple_meals_per_followup_tick": float(row["staple_meals_per_founder"]) / followup,
            "fruit_meals_per_followup_tick": float(row["fruit_meals_per_founder"]) / followup,
            "toxin_excess_per_followup_tick": float(row["toxin_excess_per_founder"]) / followup,
            "toxin_excess_per_fruit_meal": float(row["toxin_excess_per_fruit_meal"]),
        }

    outcomes = tuple(outcome_values(records[0]))
    cells: dict[tuple, list[dict]] = defaultdict(list)
    for row in records:
        cells[(row["arm"], row["realized_fruit_energy"])].append(row)
    residual_followup: list[float] = []
    residuals: dict[str, list[float]] = {metric: [] for metric in outcomes}
    for rows in cells.values():
        followup_mean = statistics.mean(float(row["founder_mean_followup_ticks"]) for row in rows)
        values = [outcome_values(row) for row in rows]
        metric_means = {metric: statistics.mean(value[metric] for value in values) for metric in outcomes}
        for row, value in zip(rows, values):
            residual_followup.append(float(row["founder_mean_followup_ticks"]) - followup_mean)
            for metric in outcomes:
                residuals[metric].append(value[metric] - metric_means[metric])
    return {
        metric: _round(_pearson(residuals[metric], residual_followup)) for metric in outcomes
    }


def _minimum_effect_test(slopes: list[float], sesoi: float = 1.0) -> dict:
    centered = [slope - sesoi for slope in slopes]
    observed = sum(centered)
    rng = random.Random(MONTE_CARLO_SEED)
    extreme = 0
    for _ in range(MONTE_CARLO_DRAWS):
        permuted = sum(value if rng.random() < 0.5 else -value for value in centered)
        extreme += int(permuted >= observed - 1e-12)
    return {
        "status": "post hoc minimum-effect sensitivity; not the frozen H6.1 decision rule",
        "null_sesoi_ticks_per_energy_unit": sesoi,
        "alternative": "mean slope greater than SESOI",
        "mean_slope": _round(statistics.mean(slopes)),
        "t_ci95": t_ci95(slopes),
        "effect_exceeds_sesoi_by_interval": t_ci95(slopes)["low"] > sesoi,
        "one_sided_monte_carlo_sign_flip_p": (extreme + 1) / (MONTE_CARLO_DRAWS + 1),
        "draws": MONTE_CARLO_DRAWS,
        "seed": MONTE_CARLO_SEED,
    }


def _slope_analysis(e6_records: list[dict]) -> dict:
    indexed = {(int(row["seed"]), int(row["realized_fruit_energy"]), row["arm"]): row for row in e6_records}
    seeds = sorted({int(row["seed"]) for row in e6_records})
    per_seed = []
    slopes = []
    for seed in seeds:
        differences = [
            float(indexed[(seed, energy, "B2")]["founder_mean_followup_ticks"])
            - float(indexed[(seed, energy, "B3")]["founder_mean_followup_ticks"])
            for energy in EXPECTED_ENERGIES
        ]
        slope = ols_slope([float(energy) for energy in EXPECTED_ENERGIES], differences)
        slopes.append(slope)
        per_seed.append({"seed": seed, "slope_ticks_per_energy_unit": _round(slope)})
    leave_one_out = []
    for excluded in EXPECTED_ENERGIES:
        included = [energy for energy in EXPECTED_ENERGIES if energy != excluded]
        values = []
        for seed in seeds:
            differences = [
                float(indexed[(seed, energy, "B2")]["founder_mean_followup_ticks"])
                - float(indexed[(seed, energy, "B3")]["founder_mean_followup_ticks"])
                for energy in included
            ]
            values.append(ols_slope([float(energy) for energy in included], differences))
        leave_one_out.append({
            "excluded_energy": excluded,
            "slope_summary": mean_sd(values),
            "t_ci95": t_ci95(values),
        })
    observed_sd = statistics.stdev(slopes)
    assumed_sd = 1.624
    approximate_power = None
    if observed_sd > 0:
        standardized = 1.0 * math.sqrt(len(slopes)) / observed_sd
        normal = statistics.NormalDist()
        approximate_power = (
            (1 - normal.cdf(1.959964 - standardized))
            + normal.cdf(-1.959964 - standardized)
        )
    return {
        "per_seed": per_seed,
        "summary": mean_sd(slopes),
        "t_ci95": t_ci95(slopes),
        "registered_directional_rule_met": statistics.mean(slopes) > 0 and t_ci95(slopes)["low"] > 0,
        "minimum_effect_sensitivity": _minimum_effect_test(slopes),
        "leave_one_energy_out": leave_one_out,
        "planning_sensitivity": {
            "status": "descriptive design sensitivity, not retrospective evidence for truth or nullity",
            "planned_slope_sd": assumed_sd,
            "observed_slope_sd": _round(observed_sd),
            "observed_to_planned_sd_ratio": _round(observed_sd / assumed_sd),
            "normal_approx_two_sided_power_for_slope_1_at_n30_using_observed_sd": _round(approximate_power),
        },
    }


def _load_records(
    payload: dict,
    experiment: str,
    root: Path,
    raw_loader: Callable[[str], dict] | None = None,
) -> tuple[list[dict], list[dict], list[str]]:
    records: list[dict] = []
    learned: list[dict] = []
    sources: list[str] = []
    for summary_row in sorted(payload["rows"], key=lambda row: (str(row["arm"]), int(row["seed"]))):
        source_name = str(summary_row["dump"])
        if raw_loader is not None:
            raw = raw_loader(source_name)
            source_label = source_name
        else:
            raw_path = Path(source_name)
            if not raw_path.is_file():
                # Preserve archive portability when the repository is moved.
                candidates = list((root / "data/confirmatory_resource_age_2026-09-14").rglob(raw_path.name))
                if len(candidates) != 1:
                    raise FileNotFoundError(raw_path)
                raw_path = candidates[0]
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
            source_label = raw_path.relative_to(root).as_posix()
        record, learned_rows = aggregate_founder_run(raw, summary_row, experiment)
        records.append(record)
        learned.extend(learned_rows)
        sources.append(source_label)
    return records, learned, sources


def analyze(
    e6_payload: dict,
    t2_payload: dict,
    root: Path,
    raw_loader: Callable[[str], dict] | None = None,
) -> tuple[dict, dict[str, list[dict]]]:
    e6_arms = {f"V{energy:02d}_{arm}" for energy in EXPECTED_ENERGIES for arm in E6_ARMS}
    e6_design = validate_cells(e6_payload, e6_arms)
    t2_design = validate_cells(t2_payload, set(T2_ARMS))
    if not e6_design["passes"] or not t2_design["passes"]:
        raise ValueError(f"incomplete design: E6={e6_design}, T2RB={t2_design}")
    e6_records, e6_learned, e6_sources = _load_records(e6_payload, "E6", root, raw_loader)
    t2_records, t2_learned, t2_sources = _load_records(t2_payload, "T2RB", root, raw_loader)

    # Normalize E6 arm names after preserving the full arm in the raw-source row.
    for record in e6_records:
        full_arm = record["arm"]
        record["full_arm"] = full_arm
        record["arm"] = full_arm.rsplit("_", 1)[1]
    for row in e6_learned:
        row["full_arm"] = row["arm"]
        row["arm"] = row["arm"].rsplit("_", 1)[1]

    e6_contrasts = []
    for energy in EXPECTED_ENERGIES:
        level = [row for row in e6_records if int(row["realized_fruit_energy"]) == energy]
        for left, right in (("B2", "B3"), ("B2", "B1"), ("B3", "B1")):
            for metric in MECHANISM_METRICS:
                item = paired_summary(level, left, right, metric)
                item["realized_fruit_energy"] = energy
                e6_contrasts.append(item)
    t2_contrasts = []
    for left, right in (("A2", "A3R"), ("A2", "A3O"), ("A3O", "A3R")):
        for metric in MECHANISM_METRICS:
            t2_contrasts.append(paired_summary(t2_records, left, right, metric))

    a3_values = [
        float(row["mean_learned_value"])
        for row in t2_learned
        if row["arm"] in {"A3O", "A3R"} and row["food_kind"] == "raw_fruit"
    ]
    b23_plant_keys = sorted({
        row["key"] for row in e6_learned
        if row["arm"] in {"B2", "B3"} and row["food_kind"] == "raw_plant"
    })
    t2_cell = _cell_summaries(t2_records, ("arm",))
    t2_by_arm = {row["arm"]: row for row in t2_cell}
    a3o_damage = t2_by_arm["A3O"]["metrics"]["toxin_damage_per_founder"]["mean"]
    a3r_damage = t2_by_arm["A3R"]["metrics"]["toxin_damage_per_founder"]["mean"]

    result = {
        "analysis": "E6 and T2-RB red-team mechanism reproduction v1",
        "status": "post hoc descriptive unless a field explicitly names a frozen analysis",
        "inferential_unit": "seed; founders are aggregated within run",
        "metadata": {
            "analysis_timing": "implemented after the 2026-09-15 red-team report and after primary-result reveal",
            "source_summary_files": [
                "reports/publication_value_of_information_2026-09-13/confirmatory/e6/E6_runs.json",
                "reports/publication_value_of_information_2026-09-13/confirmatory/t2rb/T2RB_runs.json",
            ],
            "raw_source_files": sorted(e6_sources + t2_sources),
            "raw_source_count": len(e6_sources) + len(t2_sources),
            "skip_count_warning": (
                "skipped_food_by_type and encounter telemetry can count repeated contact on consecutive ticks; "
                "skip counts are not independent food-item encounters"
            ),
            "starvation_override_identifiable": False,
            "starvation_override_limitation": (
                "the archived founder/event telemetry does not record agent energy at the food-decision moment, "
                "so meals taken specifically under the energy <= 6 override cannot be separated"
            ),
        },
        "design_validation": {"E6": e6_design, "T2RB": t2_design},
        "E6": {
            "seed_records": e6_records,
            "cell_summaries": _cell_summaries(e6_records, ("realized_fruit_energy", "arm")),
            "paired_contrasts": e6_contrasts,
            "slope": _slope_analysis(e6_records),
            "within_arm_energy_cell_correlations_with_followup": _within_cell_correlations(e6_records),
            "energy_10_regime": {
                "relative_threshold_at_safe_fruit_value": 0.6 * 10,
                "staple_value": 5,
                "threshold_exceeds_staple": 0.6 * 10 > 5,
                "cell_summaries": [
                    row for row in _cell_summaries(e6_records, ("realized_fruit_energy", "arm"))
                    if row["realized_fruit_energy"] == 10
                ],
                "paired_contrasts": [row for row in e6_contrasts if row["realized_fruit_energy"] == 10],
            },
            "representation_checks": {
                "B2_and_B3_split_raw_plant_keys": bool(b23_plant_keys) and all(key.startswith("raw_plant@") for key in b23_plant_keys),
                "observed_raw_plant_keys": b23_plant_keys,
            },
        },
        "T2RB": {
            "seed_records": t2_records,
            "cell_summaries": t2_cell,
            "paired_contrasts": t2_contrasts,
            "within_arm_correlations_with_followup": _within_cell_correlations(t2_records),
            "constant_control_checks": {
                "A3O_A3R_all_observed_learned_fruit_key_means_equal_6": bool(a3_values) and all(abs(value - 6.0) < 1e-9 for value in a3_values),
                "observed_learned_fruit_value_min": _round(min(a3_values)) if a3_values else None,
                "observed_learned_fruit_value_max": _round(max(a3_values)) if a3_values else None,
                "A3O_vs_A3R_toxin_damage_mean_relative_difference": _round((a3o_damage - a3r_damage) / a3r_damage),
            },
        },
    }
    tables = {
        "e6_seed_mechanisms.csv": e6_records,
        "t2rb_seed_mechanisms.csv": t2_records,
        "learned_values_by_key.csv": sorted(e6_learned + t2_learned, key=lambda row: (row["experiment"], row["arm"], row["seed"], row["key"])),
        "e6_paired_contrasts.csv": e6_contrasts,
        "t2rb_paired_contrasts.csv": t2_contrasts,
    }
    return result, tables


def _flatten(row: dict, prefix: str = "") -> dict:
    result: dict[str, object] = {}
    for key, value in row.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            result.update(_flatten(value, f"{name}."))
        elif isinstance(value, list):
            result[name] = json.dumps(value, ensure_ascii=False, sort_keys=True)
        else:
            result[name] = value
    return result


def _write_csv(path: Path, rows: list[dict]) -> None:
    flat = [_flatten(row) for row in rows]
    fields = sorted({key for row in flat for key in row})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(flat)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--e6-runs", required=True)
    parser.add_argument("--t2-runs", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    e6_payload = json.loads((root / args.e6_runs).read_text(encoding="utf-8"))
    t2_payload = json.loads((root / args.t2_runs).read_text(encoding="utf-8"))
    result, tables = analyze(e6_payload, t2_payload, root)
    output = root / args.out_dir
    output.mkdir(parents=True, exist_ok=True)
    (output / "mechanism_analysis.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for name, rows in tables.items():
        _write_csv(output / name, rows)
    print(
        f"wrote mechanism analysis for {len(result['E6']['seed_records'])} E6 and "
        f"{len(result['T2RB']['seed_records'])} T2-RB seed-runs to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
