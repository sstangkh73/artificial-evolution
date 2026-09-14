import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from plot_resource_age_confirmatory import e6_seed_rows, t2_seed_rows


class TestConfirmatorySourceRows(unittest.TestCase):
    def test_e6_rows_preserve_seed_pairing(self):
        rows = []
        for energy in (4, 5, 6, 8, 10):
            for condition, value in (("B1", 10), ("B2", 20 + energy), ("B3", 20)):
                rows.append({
                    "arm": f"V{energy:02d}_{condition}", "seed": 7,
                    "founder_mean_followup_ticks": value,
                    "discrimination_index": 0.5,
                    "p_eat_given_safe": 0.8,
                    "p_eat_given_toxic": 0.3,
                    "fruit_encounters_per_agent": 40,
                })
        result = e6_seed_rows({"rows": rows})
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["B2_minus_B3_followup_ticks"], 4)
        self.assertEqual(result[-1]["B2_minus_B1_followup_ticks"], 20)

    def test_t2_rows_preserve_both_controls(self):
        rows = [
            {"arm": arm, "seed": 9, "founder_mean_followup_ticks": value}
            for arm, value in (("A2", 80), ("A3O", 90), ("A3R", 92))
        ]
        result = t2_seed_rows({"rows": rows})
        self.assertEqual(result[0]["A2_minus_A3O_followup_ticks"], -10)
        self.assertEqual(result[0]["A2_minus_A3R_followup_ticks"], -12)


if __name__ == "__main__":
    unittest.main()
