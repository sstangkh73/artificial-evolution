import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from validate_e_series_batch import validate_payload


def _payload():
    spec = {
        "experiment": "E6TEST",
        "primary_metric": "founder_mean_followup_ticks",
        "seeds": [11, 12],
        "arms": {"V10_B2": [], "V10_B3": []},
        "realized_fruit_energy_by_prefix": {"V10": 10},
    }
    rows = [
        {
            "arm": arm,
            "seed": seed,
            "founder_mean_followup_ticks": 50.0,
            "realized_gross_fruit_energy": 10.0,
        }
        for seed in spec["seeds"] for arm in spec["arms"]
    ]
    return {
        "provenance": {
            "experiment": "E6TEST",
            "spec": spec,
            "git_revision_start": "abc",
            "git_revision_end": "abc",
            "git_revision_changed_during_run": False,
            "git_tree_dirty_start": False,
            "git_tree_dirty_end": False,
            "runs": 4,
            "failures": 0,
        },
        "rows": rows,
    }


class TestBatchValidation(unittest.TestCase):
    def test_accepts_complete_clean_cartesian_batch(self):
        result = validate_payload(_payload())
        self.assertTrue(result["valid"])
        self.assertEqual(result["expected_runs"], 4)

    def test_rejects_missing_duplicate_and_wrong_energy(self):
        payload = _payload()
        payload["rows"].pop()
        payload["rows"].append(dict(payload["rows"][0]))
        payload["rows"][0]["realized_gross_fruit_energy"] = 8.0
        result = validate_payload(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(result["errors"]["missing_cells"])
        self.assertTrue(result["errors"]["duplicate_cells"])
        self.assertTrue(result["errors"]["realized_energy_errors"])

    def test_rejects_dirty_provenance_and_missing_outcome(self):
        payload = _payload()
        payload["provenance"]["git_tree_dirty_start"] = True
        payload["rows"][0]["founder_mean_followup_ticks"] = None
        result = validate_payload(payload)
        self.assertFalse(result["valid"])
        self.assertIn("tree was dirty at batch start", result["errors"]["provenance_errors"])
        self.assertEqual(len(result["errors"]["missing_outcomes"]), 1)

    def test_rejects_a_draft_spec(self):
        payload = _payload()
        payload["provenance"]["spec"]["status"] = "DRAFT_DO_NOT_RUN_CONFIRMATORY"
        result = validate_payload(payload)
        self.assertFalse(result["valid"])
        self.assertEqual(
            result["errors"]["spec_status_errors"],
            ["embedded experiment spec is still marked DRAFT"],
        )


if __name__ == "__main__":
    unittest.main()
