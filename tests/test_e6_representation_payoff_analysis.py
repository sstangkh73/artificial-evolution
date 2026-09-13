import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from analyze_e6_representation_payoff import analyze_payload, ols_slope


def _clean_provenance():
    return {
        "git_revision_start": "abc",
        "git_revision_end": "abc",
        "git_revision_changed_during_run": False,
        "git_tree_dirty_start": False,
        "git_tree_dirty_end": False,
        "failures": 0,
    }


class TestE6RepresentationPayoffAnalysis(unittest.TestCase):
    def test_ols_slope_recovers_known_line(self):
        self.assertAlmostEqual(ols_slope([4, 5, 6, 8, 10], [9, 11, 13, 17, 21]), 2.0)

    def test_analysis_uses_one_slope_per_complete_seed(self):
        rows = []
        for seed, slope in ((11, 2.0), (12, 3.0)):
            for energy in (4, 5, 6, 8, 10):
                rows.extend([
                    {"arm": f"V{energy:02d}_B2", "seed": seed,
                     "founder_mean_age": 200 + slope * energy},
                    {"arm": f"V{energy:02d}_B3", "seed": seed,
                     "founder_mean_age": 200},
                ])
        result = analyze_payload(
            {"provenance": _clean_provenance(), "rows": rows},
            expected_seed_count=2,
        )
        self.assertEqual(result["primary"]["n_complete_seeds"], 2)
        self.assertEqual(result["primary"]["slope_summary"]["mean"], 2.5)
        self.assertEqual(result["primary"]["slopes_positive"], 2)
        self.assertTrue(result["confirmatory_provenance_eligible"])

    def test_analysis_excludes_a_seed_missing_one_matched_arm(self):
        rows = []
        for energy in (4, 5, 6, 8, 10):
            rows.append({"arm": f"V{energy:02d}_B2", "seed": 11,
                         "founder_mean_age": 200 + energy})
            if energy != 6:
                rows.append({"arm": f"V{energy:02d}_B3", "seed": 11,
                             "founder_mean_age": 200})
        result = analyze_payload({"provenance": _clean_provenance(), "rows": rows})
        self.assertEqual(result["primary"]["n_complete_seeds"], 0)
        self.assertEqual(result["excluded_seeds"][0]["missing"], ["V06_B3"])
        self.assertFalse(result["confirmatory_provenance_eligible"])

    def test_analysis_rejects_missing_provenance_or_wrong_seed_count(self):
        rows = []
        for energy in (4, 5, 6, 8, 10):
            rows.extend([
                {"arm": f"V{energy:02d}_B2", "seed": 11,
                 "founder_mean_age": 200 + energy},
                {"arm": f"V{energy:02d}_B3", "seed": 11,
                 "founder_mean_age": 200},
            ])

        missing_provenance = analyze_payload({"provenance": {"failures": 0}, "rows": rows})
        wrong_seed_count = analyze_payload(
            {"provenance": _clean_provenance(), "rows": rows},
            expected_seed_count=20,
        )
        self.assertFalse(missing_provenance["confirmatory_provenance_eligible"])
        self.assertFalse(wrong_seed_count["confirmatory_provenance_eligible"])


if __name__ == "__main__":
    unittest.main()
