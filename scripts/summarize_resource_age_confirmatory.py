# -*- coding: utf-8 -*-
"""Report preregistered E6 secondary results and mechanism gates.

This script was implemented after the primary confirmatory result was revealed.
It only operationalizes secondary summaries explicitly listed in the frozen
preregistration; it cannot change the H6.1 decision produced by
analyze_e6_representation_payoff.py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_e_series import bootstrap_ci95, contrast, holm, mean_sd, sign_flip_p, t_ci95
from analyze_e6_representation_payoff import EXPECTED_ENERGIES, analyze_payload, ols_slope


CONDITIONS = ("B1", "B2", "B3")


def _mean_present(rows: list[dict], field: str) -> float | None:
    values = [float(row[field]) for row in rows if row.get(field) is not None]
    return round(sum(values) / len(values), 6) if values else None


def _learned_bin_mean(row: dict, indices: tuple[int, ...]) -> float | None:
    learned = row.get("learned_fruit_values_by_key") or {}
    values = [
        float(learned[f"raw_fruit@{index}"]["mean"])
        for index in indices if learned.get(f"raw_fruit@{index}", {}).get("mean") is not None
    ]
    return sum(values) / len(values) if values else None


def summarize_e6(payload: dict, metric: str = "founder_mean_followup_ticks") -> dict:
    primary = analyze_payload(payload, metric=metric)
    if not primary["confirmatory_provenance_eligible"]:
        raise ValueError("E6 batch is not eligible for confirmatory analysis")

    rows = payload["rows"]
    by_cell = {(str(row["arm"]), int(row["seed"])): row for row in rows}
    level_results: list[dict] = []
    raw_p: dict[str, float] = {}

    expected_keys = {f"raw_fruit@{index}" for index in range(9)}
    safe_bins = (2, 3)
    toxic_bins = (0, 1, 4, 5, 6, 7, 8)

    for energy in EXPECTED_ENERGIES:
        arm_names = {condition: f"V{energy:02d}_{condition}" for condition in CONDITIONS}
        rows_by_arm = {
            condition: {
                seed: float(row[metric])
                for (arm, seed), row in by_cell.items() if arm == arm_names[condition]
            }
            for condition in CONDITIONS
        }
        b2_b3 = contrast(rows_by_arm, "B2", "B3", metric)
        b2_b1 = contrast(rows_by_arm, "B2", "B1", metric)
        b3_b1 = contrast(rows_by_arm, "B3", "B1", metric)
        raw_p[str(energy)] = float(b2_b3["paired_difference"]["p"])

        condition_summaries = {}
        for condition, arm in arm_names.items():
            arm_rows = [row for row in rows if row["arm"] == arm]
            death_total = sum(sum((row.get("death_reasons") or {}).values()) for row in arm_rows)
            deaths = {
                reason: sum((row.get("death_reasons") or {}).get(reason, 0) for row in arm_rows)
                for reason in ("starvation", "durability_depleted", "senescence")
            }
            condition_summaries[condition] = {
                "n_runs": len(arm_rows),
                metric: mean_sd([float(row[metric]) for row in arm_rows]),
                "discrimination_index_mean": _mean_present(arm_rows, "discrimination_index"),
                "p_eat_given_safe_mean": _mean_present(arm_rows, "p_eat_given_safe"),
                "p_eat_given_toxic_mean": _mean_present(arm_rows, "p_eat_given_toxic"),
                "fruit_encounters_per_founder_mean": _mean_present(arm_rows, "fruit_encounters_per_agent"),
                "fruit_encounters_per_founder_min": min(
                    float(row["fruit_encounters_per_agent"]) for row in arm_rows
                ),
                "founders_censored_total": sum(int(row["founders_censored"]) for row in arm_rows),
                "death_reason_counts": deaths,
                "death_reason_proportions": {
                    reason: round(count / death_total, 6) if death_total else None
                    for reason, count in deaths.items()
                },
            }

        b2_rows = [row for row in rows if row["arm"] == arm_names["B2"]]
        signal_rows = 0
        coverage_rows = 0
        for row in b2_rows:
            learned = row.get("learned_fruit_values_by_key") or {}
            coverage_rows += set(learned) == expected_keys
            safe_value = _learned_bin_mean(row, safe_bins)
            toxic_value = _learned_bin_mean(row, toxic_bins)
            signal_rows += (
                safe_value is not None and toxic_value is not None and safe_value > toxic_value
            )
        mean_encounters = condition_summaries["B2"]["fruit_encounters_per_founder_mean"]
        minimum_encounters = condition_summaries["B2"]["fruit_encounters_per_founder_min"]
        mechanism = {
            "expected_resource_age_keys": sorted(expected_keys),
            "b2_rows_with_complete_key_coverage": coverage_rows,
            "b2_rows_with_safe_bin_value_above_toxic_bins": signal_rows,
            "b2_mean_fruit_encounters_per_founder": mean_encounters,
            "b2_minimum_fruit_encounters_per_founder": minimum_encounters,
            "passes_preregistered_gate": (
                coverage_rows == len(b2_rows)
                and signal_rows == len(b2_rows)
                and mean_encounters >= 30
            ),
            "stricter_all_runs_encounter_sensitivity_passes": minimum_encounters >= 30,
            "encounter_gate_interpretation": (
                "The frozen text states 30 encounters per founder at each energy level. "
                "The preregistered gate therefore uses the level mean; the minimum-run "
                "criterion is reported as a stricter post hoc sensitivity."
            ),
        }
        level_results.append({
            "realized_fruit_energy": energy,
            "B2_minus_B3": b2_b3,
            "B2_minus_B1": b2_b1,
            "B3_minus_B1_descriptive": b3_b1,
            "conditions": condition_summaries,
            "mechanism_gate": mechanism,
        })

    adjusted = holm(raw_p)
    for result in level_results:
        energy = str(result["realized_fruit_energy"])
        result["B2_minus_B3"]["paired_difference"]["holm_adjusted_p"] = adjusted[energy]

    seeds = sorted({int(row["seed"]) for row in rows})
    leave_one_energy_out = []
    for excluded_energy in EXPECTED_ENERGIES:
        included = [energy for energy in EXPECTED_ENERGIES if energy != excluded_energy]
        slopes = []
        for seed in seeds:
            differences = [
                float(by_cell[(f"V{energy:02d}_B2", seed)][metric])
                - float(by_cell[(f"V{energy:02d}_B3", seed)][metric])
                for energy in included
            ]
            slopes.append(ols_slope([float(energy) for energy in included], differences))
        leave_one_energy_out.append({
            "excluded_energy": excluded_energy,
            "included_energies": included,
            "slope_summary": mean_sd(slopes),
            "t_ci95": t_ci95(slopes),
            "bootstrap_ci95": bootstrap_ci95(slopes),
            **sign_flip_p(slopes),
        })

    return {
        "analysis_timing": (
            "post-prereg implementation after primary-result reveal; restricted to "
            "secondary summaries named in the frozen preregistration"
        ),
        "primary_decision_source": "analyze_e6_representation_payoff.py",
        "primary": primary["primary"],
        "all_mechanism_gates_pass": all(
            result["mechanism_gate"]["passes_preregistered_gate"]
            for result in level_results
        ),
        "holm_family": "B2-B3 across five realized-energy levels",
        "by_realized_fruit_energy": level_results,
        "post_hoc_sensitivity": {
            "status": "not preregistered; cannot change the H6.1 decision",
            "purpose": "diagnose whether the linear slope depends on one energy level",
            "leave_one_energy_out": leave_one_energy_out,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--e6-runs", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    payload = json.loads(Path(args.e6_runs).read_text(encoding="utf-8"))
    summary = summarize_e6(payload)
    Path(args.out).write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"wrote {args.out}; mechanism gates "
        f"{'PASS' if summary['all_mechanism_gates_pass'] else 'FAIL'}"
    )
    return 0 if summary["all_mechanism_gates_pass"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
