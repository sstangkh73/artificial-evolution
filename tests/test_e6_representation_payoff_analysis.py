import os
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
                    {"arm": f"V{energy:02d}_B1", "seed": seed,
                     "founder_mean_age": 201},
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

    def test_analysis_rejects_wrong_seed_identity_and_missing_secondary_arm(self):
        rows = []
        for energy in (4, 5, 6, 8, 10):
            rows.extend([
                {"arm": f"V{energy:02d}_B1", "seed": 12,
                 "founder_mean_age": 201},
                {"arm": f"V{energy:02d}_B2", "seed": 12,
                 "founder_mean_age": 200 + energy},
                {"arm": f"V{energy:02d}_B3", "seed": 12,
                 "founder_mean_age": 200},
            ])
        wrong_seed = analyze_payload(
            {"provenance": _clean_provenance(), "rows": rows},
            expected_seeds={11},
        )
        self.assertEqual(wrong_seed["unexpected_seeds"], [12])
        self.assertFalse(wrong_seed["confirmatory_provenance_eligible"])

        missing_b1_rows = [row for row in rows if row["arm"] != "V06_B1"]
        missing_b1 = analyze_payload(
            {"provenance": _clean_provenance(), "rows": missing_b1_rows},
            expected_seeds={12},
        )
        self.assertEqual(missing_b1["design_missing"][0]["missing"], ["V06_B1"])
        self.assertFalse(missing_b1["confirmatory_provenance_eligible"])

    def test_cli_takes_expected_seed_count_from_frozen_spec(self):
        rows = []
        for energy in (4, 5, 6, 8, 10):
            rows.extend([
                {"arm": f"V{energy:02d}_B1", "seed": 11,
                 "founder_mean_age": 201},
                {"arm": f"V{energy:02d}_B2", "seed": 11,
                 "founder_mean_age": 200 + energy},
                {"arm": f"V{energy:02d}_B3", "seed": 11,
                 "founder_mean_age": 200},
            ])
        provenance = _clean_provenance()
        provenance["spec"] = {"seeds": [11]}
        payload = {"provenance": provenance, "rows": rows}

        with tempfile.TemporaryDirectory(dir=os.getcwd()) as tmp:
            runs = Path(tmp) / "runs.json"
            out = Path(tmp) / "analysis.json"
            runs.write_text(json.dumps(payload), encoding="utf-8")
            completed = subprocess.run([
                sys.executable,
                os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             "scripts", "analyze_e6_representation_payoff.py"),
                "--runs", str(runs), "--out", str(out),
            ], check=False, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(json.loads(out.read_text())["design_complete"])


if __name__ == "__main__":
    unittest.main()
