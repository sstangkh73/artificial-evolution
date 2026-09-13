import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from analyze_t2rb_replication import analyze_payload


def _payload(missing: tuple[str, int] | None = None):
    seeds = [11, 12]
    rows = []
    for seed in seeds:
        for arm, value in (("A2", 190), ("A3O", 198), ("A3R", 200)):
            if missing == (arm, seed):
                continue
            rows.append({
                "arm": arm,
                "seed": seed,
                "founder_mean_followup_ticks": value + seed,
            })
    return {
        "provenance": {
            "spec": {"seeds": seeds},
            "git_revision_start": "abc",
            "git_revision_end": "abc",
            "git_revision_changed_during_run": False,
            "git_tree_dirty_start": False,
            "git_tree_dirty_end": False,
            "failures": 0,
        },
        "rows": rows,
    }


class TestT2RBReplicationAnalysis(unittest.TestCase):
    def test_primary_is_recalibrated_control_and_complete_batch_is_eligible(self):
        result = analyze_payload(_payload())
        self.assertEqual(result["primary"]["contrast"], "A2-A3R")
        self.assertEqual(result["primary"]["paired_difference"]["mean"], -10)
        self.assertEqual(result["direct_replication_secondary"]["contrast"], "A2-A3O")
        self.assertTrue(result["confirmatory_provenance_eligible"])

    def test_missing_arm_seed_makes_batch_ineligible(self):
        result = analyze_payload(_payload(missing=("A3R", 12)))
        self.assertEqual(result["missing_by_arm"], {"A3R": [12]})
        self.assertFalse(result["confirmatory_provenance_eligible"])

    def test_dirty_or_changed_revision_makes_batch_ineligible(self):
        payload = _payload()
        payload["provenance"]["git_revision_changed_during_run"] = True
        self.assertFalse(analyze_payload(payload)["confirmatory_provenance_eligible"])


if __name__ == "__main__":
    unittest.main()
