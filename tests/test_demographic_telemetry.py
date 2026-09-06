"""Unit tests for Option ข.0 demographic telemetry helpers.

These tests keep the diagnostic metrics stable without running a full
population simulation.

Run from anywhere:  python tests/test_demographic_telemetry.py
"""

import os
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.run_long_emergence_watch import (
    _age_structure_summary,
    _bucket_label,
    _coefficient_of_variation,
    _estimate_k_from_trajectory,
    _local_food_per_capita_summary,
    _summarize_r0_by_density,
)


class TestDemographicTelemetry(unittest.TestCase):
    def test_bucket_label_uses_closed_integer_ranges(self):
        self.assertEqual(_bucket_label(0, 10), "0-9")
        self.assertEqual(_bucket_label(9, 10), "0-9")
        self.assertEqual(_bucket_label(10, 10), "10-19")
        self.assertEqual(_bucket_label(-3, 10), "0-9")

    def test_coefficient_of_variation_handles_empty_and_zero_mean(self):
        self.assertIsNone(_coefficient_of_variation([]))
        self.assertIsNone(_coefficient_of_variation([0, 0]))
        self.assertEqual(_coefficient_of_variation([0, 2]), 1.0)

    def test_age_structure_summary_buckets_age_and_stage(self):
        agents = [
            SimpleNamespace(age=5, current_stage="child"),
            SimpleNamespace(age=24, current_stage="adult"),
            SimpleNamespace(age=25, current_stage="adult"),
        ]
        summary = _age_structure_summary(agents, bucket_size=20)
        self.assertEqual(summary["histogram"], {"0-19": 1, "20-39": 2})
        self.assertEqual(summary["stage_counts"], {"child": 1, "adult": 2})
        self.assertEqual(summary["mean_age"], 18.0)

    def test_local_food_per_capita_uses_local_agents_as_denominator(self):
        env = SimpleNamespace(food_positions={(0, 1): object(), (2, 1): object(), (5, 5): object()})
        agents = [
            SimpleNamespace(x=0, y=0, home_anchor=None),
            SimpleNamespace(x=2, y=0, home_anchor=None),
        ]
        summary = _local_food_per_capita_summary(env, agents, radius=2)
        self.assertEqual(summary["radius"], 2)
        self.assertEqual(summary["agents"], 2)
        self.assertEqual(summary["mean"], 0.5)
        self.assertEqual(summary["min"], 0.5)
        self.assertEqual(summary["max"], 0.5)
        self.assertEqual(summary["mean_local_agents"], 2.0)

    def test_r0_by_density_summary_reports_maturation_and_replacement_proxy(self):
        bins = {
            "10-19": {
                "births": 2,
                "matured_offspring": 1,
                "matured_female_offspring": 1,
                "population_at_birth": [10, 12],
                "food_per_capita_at_birth": [4.0, 6.0],
            }
        }
        summary = _summarize_r0_by_density(
            bins,
            {"10-19": {101}},
            {"10-19": {101}},
        )
        row = summary["10-19"]
        self.assertEqual(row["mothers"], 1)
        self.assertEqual(row["births"], 2)
        self.assertEqual(row["offspring_maturation_rate"], 0.5)
        self.assertEqual(row["matured_offspring_per_mother"], 1.0)
        self.assertEqual(row["female_replacement_proxy"], 1.0)
        self.assertEqual(row["mean_population_at_birth"], 11.0)
        self.assertEqual(row["mean_food_per_capita_at_birth"], 5.0)

    def test_k_estimator_uses_birth_death_balance_windows(self):
        estimate = _estimate_k_from_trajectory([
            {
                "tick": 200,
                "population": 30,
                "standing_food": 200,
                "food_per_capita": 6.67,
                "births_window": 3,
                "deaths_window": 1,
                "birth_death_balance_error": 2,
            },
            {
                "tick": 400,
                "population": 40,
                "standing_food": 160,
                "food_per_capita": 4.0,
                "births_window": 2,
                "deaths_window": 2,
                "birth_death_balance_error": 0,
            },
        ])
        self.assertEqual(estimate["candidate_windows"], 1)
        self.assertEqual(estimate["mean_population_at_balance"], 40.0)
        self.assertEqual(estimate["mean_food_per_capita_at_balance"], 4.0)
        self.assertEqual(estimate["nearest_balance_window"]["tick"], 400)


if __name__ == "__main__":
    unittest.main()
