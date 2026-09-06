"""Tests for publication-grade sample-size and statistics artifacts."""

import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Make the repo root importable regardless of cwd.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.publication_artifacts import write_publication_artifacts


def _condition(condition_id: str) -> dict[str, object]:
    return {
        "condition_id": condition_id,
        "label": condition_id.replace("_", " "),
        "question": "synthetic test condition",
        "body_index": 8,
        "body_name": "body_8",
        "body_design": "synthetic",
        "body_stats": "synthetic",
        "initial_population": 10,
        "max_population": 50,
        "max_ticks": 200,
        "founder_mode": "synthetic",
        "stop_on_generation_adult": None,
        "spawn_strategy": "synthetic",
        "env_kwargs": {},
    }


def _replicate(condition_id: str, seed: int, offset: int, lift: int = 0) -> dict[str, object]:
    return {
        "condition_id": condition_id,
        "condition_label": condition_id,
        "replicate_id": f"{condition_id}_seed_{seed}",
        "seed": seed,
        "body_index": 8,
        "body_name": "body_8",
        "body_design": "synthetic",
        "initial_population": 10,
        "max_population": 50,
        "max_ticks_requested": 200,
        "final_tick": 120 + offset,
        "population_extinct": False,
        "target_generation_reached": lift > 0 and offset % 2 == 0,
        "target_generation_tick": 80 + offset if lift > 0 and offset % 2 == 0 else None,
        "first_birth_tick": 20 + offset,
        "first_matured_child_tick": 60 + offset,
        "first_technology_tick": 40 + offset if lift > 0 else None,
        "first_technology_name": "synthetic_tool" if lift > 0 else None,
        "peak_population": 20 + offset + lift,
        "total_births": 5 + offset + lift,
        "matured_children": 2 + offset + lift,
        "stored_food_total": 3 + offset,
        "average_age": 50.0 + offset,
        "average_food_eaten": 4.0 + offset,
        "average_children": 1.0 + (offset / 10.0),
        "completed_lineages": 1 + (offset % 3),
        "final_population": 10 + offset,
        "final_female": 5,
        "final_male": 5,
        "max_generation_observed": 1 + (1 if lift > 0 else 0),
        "reproduction_failure_events": offset,
        "mean_agent_memory_sites": 1.0 + (offset / 10.0) + (lift / 10.0),
        "max_agent_memory_sites": 3 + offset,
        "social_contact_rate": 0.1 + (offset / 100.0),
        "object_experiment_agent_rate": 0.05 + (lift / 100.0),
        "mean_friend_count": 0.2 + (offset / 100.0),
        "manifest_path": "",
        "dashboard_path": "",
        "telemetry_path": "",
    }


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class TestPublicationStatistics(unittest.TestCase):
    def test_journal_grade_package_exports_ci_effect_sizes_and_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "package"
            replicates = []
            for index in range(30):
                replicates.append(_replicate("baseline", 1000 + index, index))
                replicates.append(_replicate("treatment", 2000 + index, index, lift=10))

            manifest = write_publication_artifacts(
                output_dir,
                {
                    "conditions": [_condition("baseline"), _condition("treatment")],
                    "replicates": replicates,
                    "tick_metrics_long": [],
                    "failure_reasons": [],
                    "lineage_rows": [],
                    "event_rows": [],
                    "runtime_provenance": {"test": True},
                },
            )

            stats_rows = _read_csv(Path(manifest["condition_level_statistics_csv"]))
            baseline_stats = next(row for row in stats_rows if row["condition_id"] == "baseline")
            self.assertEqual(baseline_stats["replicates"], "30")
            self.assertEqual(baseline_stats["sample_size_status"], "recommended_journal_grade")
            self.assertNotEqual(baseline_stats["peak_population_sd"], "")
            self.assertNotEqual(baseline_stats["peak_population_ci95_low"], "")
            self.assertNotEqual(baseline_stats["peak_population_ci95_high"], "")

            effect_rows = _read_csv(Path(manifest["condition_effect_sizes_csv"]))
            peak_effect = next(row for row in effect_rows if row["condition_id"] == "treatment" and row["metric"] == "peak_population")
            self.assertNotEqual(peak_effect["hedges_g"], "")
            self.assertGreater(float(peak_effect["hedges_g"]), 0.0)

            audit = Path(manifest["sample_size_audit_md"]).read_text(encoding="utf-8")
            self.assertIn("All conditions meet the minimum journal-grade replicate threshold.", audit)

    def test_underpowered_package_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "package"
            replicates = [_replicate("baseline", 1000 + index, index) for index in range(3)]
            manifest = write_publication_artifacts(
                output_dir,
                {
                    "conditions": [_condition("baseline")],
                    "replicates": replicates,
                    "tick_metrics_long": [],
                    "failure_reasons": [],
                    "lineage_rows": [],
                    "event_rows": [],
                    "runtime_provenance": {"test": True},
                },
            )

            stats_rows = _read_csv(Path(manifest["condition_level_statistics_csv"]))
            self.assertEqual(stats_rows[0]["sample_size_status"], "underpowered")

            audit = Path(manifest["sample_size_audit_md"]).read_text(encoding="utf-8")
            self.assertIn("This package is not journal-grade for confirmatory inference yet.", audit)


if __name__ == "__main__":
    unittest.main()
