import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from summarize_resource_age_confirmatory import summarize_e6


class TestConfirmatorySecondarySummary(unittest.TestCase):
    def _payload(self):
        seeds = [11, 12]
        arms = {
            f"V{energy:02d}_{condition}": []
            for energy in (4, 5, 6, 8, 10)
            for condition in ("B1", "B2", "B3")
        }
        rows = []
        learned = {
            f"raw_fruit@{index}": {
                "n_agents": 50,
                "mean": 5.0 if index in (2, 3) else -2.0,
            }
            for index in range(9)
        }
        for seed in seeds:
            for energy in (4, 5, 6, 8, 10):
                for condition, value in (
                    ("B1", 100.0),
                    ("B2", 100.0 + energy),
                    ("B3", 100.0),
                ):
                    rows.append({
                        "arm": f"V{energy:02d}_{condition}",
                        "seed": seed,
                        "founder_mean_followup_ticks": value,
                        "learned_fruit_values_by_key": learned if condition == "B2" else {},
                        "fruit_encounters_per_agent": 40.0,
                        "founders_censored": 0,
                        "death_reasons": {"starvation": 50},
                        "discrimination_index": 0.7 if condition == "B2" else 0.0,
                        "p_eat_given_safe": 1.0,
                        "p_eat_given_toxic": 0.3,
                    })
        return {
            "provenance": {
                "experiment": "E6",
                "spec": {
                    "experiment": "E6",
                    "status": "PREREGISTERED_CONFIRMATORY_FROZEN",
                    "seeds": seeds,
                    "arms": arms,
                },
                "git_revision_start": "abc",
                "git_revision_end": "abc",
                "git_revision_changed_during_run": False,
                "git_tree_dirty_start": False,
                "git_tree_dirty_end": False,
                "failures": 0,
            },
            "rows": rows,
        }

    def test_reports_prespecified_levels_holm_and_mechanism_gate(self):
        result = summarize_e6(self._payload())
        self.assertEqual(len(result["by_realized_fruit_energy"]), 5)
        self.assertEqual(
            len(result["post_hoc_sensitivity"]["leave_one_energy_out"]), 5
        )
        self.assertTrue(result["all_mechanism_gates_pass"])
        for level in result["by_realized_fruit_energy"]:
            self.assertEqual(
                level["B2_minus_B3"]["paired_difference"]["mean"],
                level["realized_fruit_energy"],
            )
            self.assertIn("holm_adjusted_p", level["B2_minus_B3"]["paired_difference"])
            self.assertIn("holm_adjusted_p", level["B2_minus_B1"]["paired_difference"])
            self.assertEqual(
                level["B3_minus_B1_descriptive"]["paired_difference"]["mean"],
                0.0,
            )

    def test_gate_fails_when_encounters_are_below_threshold(self):
        payload = self._payload()
        for row in payload["rows"]:
            if row["arm"] == "V04_B2":
                row["fruit_encounters_per_agent"] = 29.9
        result = summarize_e6(payload)
        self.assertFalse(result["all_mechanism_gates_pass"])

    def test_single_low_run_is_reported_as_stricter_sensitivity(self):
        payload = self._payload()
        for row in payload["rows"]:
            if row["arm"] == "V04_B2" and row["seed"] == 11:
                row["fruit_encounters_per_agent"] = 29.9
        result = summarize_e6(payload)
        level = result["by_realized_fruit_energy"][0]
        self.assertTrue(level["mechanism_gate"]["passes_preregistered_gate"])
        self.assertFalse(
            level["mechanism_gate"]["stricter_all_runs_encounter_sensitivity_passes"]
        )


if __name__ == "__main__":
    unittest.main()
