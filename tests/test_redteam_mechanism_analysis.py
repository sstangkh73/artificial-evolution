import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import analyze_redteam_mechanisms as mechanism
from analyze_redteam_mechanisms import aggregate_founder_run, analyze, paired_summary, validate_cells


def _agent(agent_id, followup, *, generation=0, fruit_meals=2, staple_meals=3,
           fruit_skips=2, staple_skips=1, toxin=1.0, memory=None,
           death_reason="starvation"):
    return {
        "agent_id": agent_id,
        "generation": generation,
        "alive": False,
        "age": 67 + followup,
        "meals_by_type": {"raw_fruit": fruit_meals, "raw_plant": staple_meals},
        "skipped_food_by_type": {"raw_fruit": fruit_skips, "raw_plant": staple_skips},
        "toxin_ingested_total": toxin,
        "toxin_damage_total": toxin * 5,
        "death_reason": death_reason,
        "food_value_memory": memory or {"raw_fruit": 4.0, "raw_plant": 5.0},
        "encounters_by_kind_age": {
            "raw_fruit@0": {"seen": fruit_meals + fruit_skips, "ate": fruit_meals, "skipped": fruit_skips},
            "raw_plant@0": {"seen": staple_meals + staple_skips, "ate": staple_meals, "skipped": staple_skips},
        },
    }


def _raw(seed, followup, memory, *, include_child=True):
    rows = [
        _agent(0, followup, memory=memory, death_reason="starvation"),
        _agent(1, followup, memory=memory, death_reason="senescence"),
    ]
    if include_child:
        rows.append(_agent(99, 999, generation=1, fruit_meals=100, staple_meals=100))
    return {"seed": seed, "agent_diet_summary": rows}


def _provenance(seeds):
    return {
        "spec": {"status": "PREREGISTERED_CONFIRMATORY_FROZEN", "seeds": seeds},
        "git_revision_start": "abc",
        "git_revision_end": "abc",
        "git_revision_changed_during_run": False,
        "git_tree_dirty_start": False,
        "git_tree_dirty_end": False,
        "failures": 0,
    }


class TestRedteamMechanismAnalysis(unittest.TestCase):
    def test_founder_aggregation_excludes_later_generations_and_computes_acceptance(self):
        summary = {
            "arm": "V04_B1",
            "seed": 11,
            "flags": "--population 2 --founder-age-spread 0 --pickiness 0.6",
            "founder_mean_followup_ticks": 100,
            "realized_gross_fruit_energy": 4,
        }
        record, _ = aggregate_founder_run(
            _raw(11, 100, {"raw_fruit": 4.0, "raw_plant": 5.0}), summary, "E6"
        )
        self.assertEqual(record["founders"], 2)
        self.assertEqual(record["fruit_meals_per_founder"], 2.0)
        self.assertEqual(record["fruit_acceptance_per_telemetry_encounter"], 0.5)
        self.assertEqual(record["staple_acceptance_per_telemetry_encounter"], 0.75)
        self.assertEqual(record["toxin_excess_per_fruit_meal"], 0.5)
        self.assertEqual(record["death_fraction_starvation"], 0.5)
        self.assertEqual(record["death_fraction_senescence"], 0.5)

    def test_design_validation_detects_missing_and_duplicate_cells(self):
        payload = {
            "provenance": _provenance([11]),
            "rows": [{"arm": "A2", "seed": 11}, {"arm": "A2", "seed": 11}, {"arm": "A3O", "seed": 11}],
        }
        result = validate_cells(payload, {"A2", "A3O", "A3R"})
        self.assertFalse(result["passes"])
        self.assertEqual(result["duplicates"], [{"arm": "A2", "seed": 11, "count": 2}])
        self.assertEqual(result["missing"], [{"arm": "A3R", "seed": 11}])

    def test_paired_contrast_uses_seed_differences_and_paired_effect_size(self):
        rows = [
            {"arm": "B2", "seed": 1, "x": 5.0},
            {"arm": "B3", "seed": 1, "x": 1.0},
            {"arm": "B2", "seed": 2, "x": 8.0},
            {"arm": "B3", "seed": 2, "x": 2.0},
        ]
        result = paired_summary(rows, "B2", "B3", "x")
        self.assertEqual(result["paired_difference"]["mean"], 5.0)
        self.assertAlmostEqual(result["paired_standardized_mean_difference_dz"], 3.535534)
        self.assertEqual(result["paired_probability_of_superiority"], 1.0)

    def test_within_cell_correlations_export_rate_based_descriptives(self):
        rows = []
        for seed, followup, staple, fruit, toxin in (
            (1, 10.0, 10.0, 5.0, 2.0),
            (2, 20.0, 40.0, 4.0, 1.0),
            (3, 30.0, 90.0, 3.0, 0.5),
        ):
            rows.append({
                "arm": "B1",
                "realized_fruit_energy": 4,
                "seed": seed,
                "founder_mean_followup_ticks": followup,
                "staple_meals_per_founder": staple,
                "fruit_meals_per_founder": fruit,
                "toxin_excess_per_founder": toxin,
                "toxin_damage_per_founder": toxin * 5,
                "toxin_excess_per_fruit_meal": toxin / fruit,
            })
        result = mechanism._within_cell_correlations(rows)
        self.assertIn("staple_meals_per_followup_tick", result)
        self.assertIn("fruit_meals_per_followup_tick", result)
        self.assertIn("toxin_excess_per_followup_tick", result)
        self.assertIn("toxin_excess_per_fruit_meal", result)
        self.assertAlmostEqual(result["staple_meals_per_followup_tick"], 1.0)

    def test_full_analysis_is_deterministic_and_checks_constant_controls(self):
        old_draws = mechanism.MONTE_CARLO_DRAWS
        mechanism.MONTE_CARLO_DRAWS = 2_000
        try:
            root = Path(os.getcwd())
            seeds = [11, 12]
            raw_by_name = {}
            e6_rows = []
            for energy in mechanism.EXPECTED_ENERGIES:
                for arm in mechanism.E6_ARMS:
                    for seed in seeds:
                        followup = 90 + energy + {"B1": 0, "B2": energy, "B3": 1}[arm]
                        full_arm = f"V{energy:02d}_{arm}"
                        memory = (
                            {"raw_fruit@0": float(energy), "raw_plant@0": 5.0}
                            if arm in {"B2", "B3"}
                            else {"raw_fruit": float(energy), "raw_plant": 5.0}
                        )
                        source = f"memory://E6/{full_arm}/{seed}"
                        raw_by_name[source] = _raw(seed, followup, memory)
                        e6_rows.append({
                            "arm": full_arm,
                            "seed": seed,
                            "dump": source,
                            "flags": "--population 2 --founder-age-spread 0 --pickiness 0.6",
                            "founder_mean_followup_ticks": followup,
                            "realized_gross_fruit_energy": energy,
                        })
            t2_rows = []
            for arm in mechanism.T2_ARMS:
                for seed in seeds:
                    followup = {"A2": 90, "A3O": 100, "A3R": 101}[arm]
                    memory = {"raw_fruit": 6.0 if arm in {"A3O", "A3R"} else 5.0, "raw_plant": 5.0}
                    source = f"memory://T2/{arm}/{seed}"
                    raw_by_name[source] = _raw(seed, followup, memory)
                    t2_rows.append({
                        "arm": arm,
                        "seed": seed,
                        "dump": source,
                        "flags": "--population 2 --founder-age-spread 0 --pickiness 0.6",
                        "founder_mean_followup_ticks": followup,
                        "realized_gross_fruit_energy": 10,
                    })
            e6 = {"provenance": _provenance(seeds), "rows": e6_rows}
            t2 = {"provenance": _provenance(seeds), "rows": t2_rows}
            loader = raw_by_name.__getitem__
            first_result, first_tables = analyze(e6, t2, root, raw_loader=loader)
            second_result, second_tables = analyze(e6, t2, root, raw_loader=loader)
            self.assertEqual(first_result, second_result)
            self.assertEqual(first_tables, second_tables)
            self.assertEqual(first_result["metadata"]["raw_source_count"], 36)
            self.assertTrue(
                first_result["T2RB"]["constant_control_checks"]
                ["A3O_A3R_all_observed_learned_fruit_key_means_equal_6"]
            )
            self.assertTrue(
                first_result["E6"]["representation_checks"]["B2_and_B3_split_raw_plant_keys"]
            )
        finally:
            mechanism.MONTE_CARLO_DRAWS = old_draws


if __name__ == "__main__":
    unittest.main()
