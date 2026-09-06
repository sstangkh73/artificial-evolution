"""Tests for journal-readiness artifacts beyond sample-size statistics."""

import csv
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.publication_artifacts import write_publication_artifacts


def _condition(
    condition_id: str,
    *,
    label: str | None = None,
    question: str = "synthetic condition",
    env_kwargs: dict[str, object] | None = None,
    founder_mode: str = "default_alternating",
    spawn_strategy: str = "default",
    body_index: int = 8,
    initial_population: int = 10,
    max_ticks: int = 200,
) -> dict[str, object]:
    return {
        "condition_id": condition_id,
        "label": label or condition_id.replace("_", " "),
        "question": question,
        "body_index": body_index,
        "body_name": f"body_{body_index}",
        "body_design": "synthetic",
        "body_stats": "synthetic",
        "initial_population": initial_population,
        "max_population": 50,
        "max_ticks": max_ticks,
        "founder_mode": founder_mode,
        "stop_on_generation_adult": None,
        "spawn_strategy": spawn_strategy,
        "env_kwargs": env_kwargs or {},
    }


def _replicate(condition_id: str, seed: int, social_contact_rate: float = 0.0) -> dict[str, object]:
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
        "final_tick": 120,
        "population_extinct": False,
        "target_generation_reached": False,
        "target_generation_tick": None,
        "first_birth_tick": 20,
        "first_matured_child_tick": 60,
        "first_technology_tick": None,
        "first_technology_name": None,
        "peak_population": 20,
        "total_births": 5,
        "matured_children": 2,
        "stored_food_total": 3,
        "average_age": 50.0,
        "average_food_eaten": 4.0,
        "average_children": 1.0,
        "completed_lineages": 1,
        "final_population": 10,
        "final_female": 5,
        "final_male": 5,
        "max_generation_observed": 1,
        "reproduction_failure_events": 0,
        "mean_agent_memory_sites": 1.0,
        "max_agent_memory_sites": 3,
        "social_contact_rate": social_contact_rate,
        "object_experiment_agent_rate": 0.0,
        "mean_friend_count": social_contact_rate,
        "manifest_path": "",
        "dashboard_path": "",
        "telemetry_path": "",
    }


def _event(
    event_type: str,
    details: str,
    *,
    tick: int,
    condition_id: str = "baseline",
    seed: int = 100,
) -> dict[str, object]:
    return {
        "condition_id": condition_id,
        "replicate_id": f"{condition_id}_seed_{seed}",
        "seed": seed,
        "tick": tick,
        "event_type": event_type,
        "details": details,
        "raw_text": f"{event_type} -> {details}",
        "agent_ids": [int(value) for value in re.findall(r"agent=(\d+)", details)],
    }


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class TestPublicationJournalReadinessArtifacts(unittest.TestCase):
    def test_exports_claim_scope_and_control_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "package"
            manifest = write_publication_artifacts(
                output_dir,
                {
                    "conditions": [
                        _condition("baseline_body_8"),
                        _condition(
                            "sensory_control_body_99",
                            question="Do high-sensor lower-brain agents survive without the same memory signature?",
                        ),
                        _condition(
                            "novel_scarcity_transfer_body_8",
                            env_kwargs={"max_food": 95, "food_spawn_multiplier": 0.72},
                            spawn_strategy="frontier_safe_high_food",
                        ),
                    ],
                    "replicates": [
                        _replicate("baseline_body_8", 100),
                        _replicate("sensory_control_body_99", 100),
                        _replicate("novel_scarcity_transfer_body_8", 100),
                    ],
                    "tick_metrics_long": [],
                    "failure_reasons": [],
                    "lineage_rows": [],
                    "event_rows": [],
                    "agent_outcome_rows": [],
                    "runtime_provenance": {"test": True},
                },
            )

            self.assertIn("claim_scope_md", manifest)
            self.assertIn("control_matrix_csv", manifest)
            self.assertIn("ablation_control_plan_md", manifest)

            claim_scope = Path(manifest["claim_scope_md"]).read_text(encoding="utf-8")
            self.assertIn("Do not claim intentional farming", claim_scope)
            self.assertIn("Do not claim social transmission", claim_scope)
            self.assertIn("Do not claim language", claim_scope)
            self.assertIn("Do not claim open-ended evolution", claim_scope)

            control_rows = _read_csv(Path(manifest["control_matrix_csv"]))
            baseline = next(row for row in control_rows if row["condition_id"] == "baseline_body_8")
            sensory = next(row for row in control_rows if row["condition_id"] == "sensory_control_body_99")
            self.assertEqual(baseline["learning_control_role"], "reference_baseline")
            self.assertEqual(sensory["learning_control_role"], "sensory_access_control")

            ablation_plan = Path(manifest["ablation_control_plan_md"]).read_text(encoding="utf-8")
            self.assertIn("memory-disabled or memory-shuffled ablation | missing", ablation_plan)

    def test_agent_causal_trace_links_experience_to_skip(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "package"
            manifest = write_publication_artifacts(
                output_dir,
                {
                    "conditions": [_condition("baseline")],
                    "replicates": [_replicate("baseline", 100)],
                    "tick_metrics_long": [],
                    "failure_reasons": [],
                    "lineage_rows": [],
                    "event_rows": [
                        _event("food_consumed", "agent=1 source=spawn x=1 y=1 kind=raw_seed energy=1", tick=10),
                        _event("plant_lifecycle_food_consumed", "agent=1 plant=7 x=1 y=1 energy=5 kind=raw_plant", tick=20),
                        _event("food_skipped", "agent=1 source=spawn x=1 y=1 kind=raw_seed energy=1 reason=low_value", tick=30),
                        _event("food_skipped", "agent=2 source=spawn x=1 y=1 kind=raw_seed energy=1 reason=low_value", tick=40),
                    ],
                    "agent_outcome_rows": [
                        {
                            "condition_id": "baseline",
                            "replicate_id": "baseline_seed_100",
                            "seed": 100,
                            "agent_id": 1,
                            "generation": 0,
                            "alive": True,
                            "immortal": False,
                            "friend_count": 0,
                            "remembered_food_sources_count": 1,
                            "remembered_safe_zones_count": 0,
                            "remembered_danger_count": 0,
                            "remembered_nest_locations_count": 0,
                            "food_eaten": 2,
                            "meals_by_type_json": {"raw_seed": 1, "raw_plant": 1},
                            "skipped_food_by_type_json": {"raw_seed": 1},
                            "food_value_memory_json": {"raw_seed": 1.0, "raw_plant": 5.0},
                        }
                    ],
                    "runtime_provenance": {"test": True},
                },
            )

            trace_rows = _read_csv(Path(manifest["agent_causal_trace_csv"]))
            agent_1 = next(row for row in trace_rows if row["agent_id"] == "1")
            agent_2 = next(row for row in trace_rows if row["agent_id"] == "2")
            self.assertEqual(agent_1["learning_evidence_class"], "direct_experience_before_skip")
            self.assertEqual(agent_1["experienced_seed_and_plant_before_seed_skip"], "True")
            self.assertEqual(agent_1["seed_skip_without_recorded_taste"], "False")
            self.assertEqual(agent_2["learning_evidence_class"], "skip_without_recorded_seed_taste")
            self.assertEqual(agent_2["seed_skip_without_recorded_taste"], "True")

    def test_confound_audit_flags_hunger_social_and_immortal_risk(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "package"
            manifest = write_publication_artifacts(
                output_dir,
                {
                    "conditions": [_condition("baseline")],
                    "replicates": [_replicate("baseline", 100, social_contact_rate=0.5)],
                    "tick_metrics_long": [],
                    "failure_reasons": [],
                    "lineage_rows": [],
                    "event_rows": [
                        _event(
                            "seed_dropped",
                            "agent=1 seed=9 x=1 y=1 context=hunger instinct=hunger critical_hunger=1",
                            tick=10,
                        ),
                        _event(
                            "seed_dropped",
                            "agent=1 seed=10 x=1 y=2 context=hunger instinct=hunger critical_hunger=1",
                            tick=20,
                        ),
                    ],
                    "agent_outcome_rows": [
                        {
                            "condition_id": "baseline",
                            "replicate_id": "baseline_seed_100",
                            "seed": 100,
                            "agent_id": 1,
                            "generation": 0,
                            "alive": True,
                            "immortal": True,
                            "friend_count": 2,
                            "remembered_food_sources_count": 0,
                            "remembered_safe_zones_count": 0,
                            "remembered_danger_count": 0,
                            "remembered_nest_locations_count": 0,
                            "food_eaten": 0,
                            "meals_by_type_json": {},
                            "skipped_food_by_type_json": {},
                            "food_value_memory_json": {},
                        }
                    ],
                    "runtime_provenance": {"test": True},
                },
            )

            confound_rows = _read_csv(Path(manifest["confound_audit_csv"]))
            baseline = confound_rows[0]
            self.assertEqual(baseline["hunger_confound_status"], "high_risk_hunger_dominant_missing_control")
            self.assertEqual(baseline["social_confound_status"], "possible_social_clustering_missing_control")
            self.assertEqual(baseline["immortal_confound_status"], "high_risk_immortal_agents_present")
            self.assertEqual(baseline["overall_confound_verdict"], "high_risk")

    def test_generalization_audit_protocol_and_statistical_unit_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "package"
            conditions = [
                _condition("baseline_body_8", body_index=8),
                _condition("baseline_body_14", body_index=14),
                _condition(
                    "novel_scarcity_transfer_body_8",
                    env_kwargs={"max_food": 90, "food_spawn_multiplier": 0.7},
                    spawn_strategy="frontier_safe_high_food",
                    max_ticks=400,
                ),
                _condition(
                    "collective_world_model_body_8",
                    founder_mode="25_male_25_female",
                    initial_population=50,
                    max_ticks=2200,
                ),
            ]
            replicates = [_replicate(str(condition["condition_id"]), 100) for condition in conditions]
            manifest = write_publication_artifacts(
                output_dir,
                {
                    "conditions": conditions,
                    "replicates": replicates,
                    "tick_metrics_long": [
                        {
                            "condition_id": "baseline_body_8",
                            "replicate_id": "baseline_body_8_seed_100",
                            "seed": 100,
                            "tick": 0,
                            "population": 10,
                        }
                    ],
                    "failure_reasons": [],
                    "lineage_rows": [],
                    "event_rows": [
                        _event(
                            "food_consumed",
                            "agent=1 source=spawn x=1 y=1 kind=raw_seed energy=1",
                            tick=10,
                            condition_id="baseline_body_8",
                        )
                    ],
                    "agent_outcome_rows": [
                        {
                            "condition_id": "baseline_body_8",
                            "replicate_id": "baseline_body_8_seed_100",
                            "seed": 100,
                            "agent_id": 1,
                            "generation": 0,
                            "alive": True,
                            "immortal": False,
                            "friend_count": 0,
                            "remembered_food_sources_count": 1,
                            "remembered_safe_zones_count": 0,
                            "remembered_danger_count": 0,
                            "remembered_nest_locations_count": 0,
                            "food_eaten": 1,
                            "meals_by_type_json": {"raw_seed": 1},
                            "skipped_food_by_type_json": {},
                            "food_value_memory_json": {"raw_seed": 1.0},
                        }
                    ],
                    "runtime_provenance": {
                        "test": True,
                        "seed_start": 100,
                        "seed_count_per_condition": 1,
                        "snapshot_interval": 10,
                    },
                },
            )

            self.assertIn("generalization_audit_csv", manifest)
            self.assertIn("statistical_unit_audit_csv", manifest)
            self.assertIn("statistical_model_spec_md", manifest)
            self.assertIn("frozen_protocol_json", manifest)
            self.assertIn("reproducibility_checklist_md", manifest)

            generalization_rows = _read_csv(Path(manifest["generalization_audit_csv"]))
            body_axis = next(row for row in generalization_rows if row["axis"] == "body_plan")
            ecology_axis = next(row for row in generalization_rows if row["axis"] == "ecology_regime")
            self.assertEqual(body_axis["status"], "minimum_coverage")
            self.assertEqual(ecology_axis["status"], "minimum_coverage")

            unit_rows = _read_csv(Path(manifest["statistical_unit_audit_csv"]))
            replicate_layer = next(row for row in unit_rows if row["data_layer"] == "replicate_outcomes")
            agent_layer = next(row for row in unit_rows if row["data_layer"] == "agent_causal_trace")
            self.assertEqual(replicate_layer["independent_unit"], "seed_run")
            self.assertEqual(agent_layer["independent_unit"], "not_independent")
            self.assertEqual(agent_layer["nested_within"], "seed_run")

            model_spec = Path(manifest["statistical_model_spec_md"]).read_text(encoding="utf-8")
            self.assertIn("Do not count agent rows", model_spec)

            protocol = __import__("json").loads(Path(manifest["frozen_protocol_json"]).read_text(encoding="utf-8"))
            self.assertEqual(protocol["protocol_version"], "journal-readiness-2026-06-26-v1")
            self.assertEqual(protocol["independent_unit"], "seed_run")
            self.assertIn("generalization_audit.csv", protocol["required_artifacts"])
            self.assertIn("--study-seeds 1", protocol["rerun_command_templates"][0])

            checklist = Path(manifest["reproducibility_checklist_md"]).read_text(encoding="utf-8")
            self.assertIn("Rerun Template", checklist)

    def test_novelty_framing_and_claim_evidence_map_bound_strong_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "package"
            manifest = write_publication_artifacts(
                output_dir,
                {
                    "conditions": [_condition("baseline")],
                    "replicates": [_replicate("baseline", 100)],
                    "tick_metrics_long": [],
                    "failure_reasons": [],
                    "lineage_rows": [],
                    "event_rows": [
                        _event("food_consumed", "agent=1 source=spawn x=1 y=1 kind=raw_seed energy=1", tick=10),
                        _event("plant_lifecycle_food_consumed", "agent=1 plant=7 x=1 y=1 energy=5 kind=raw_plant", tick=20),
                        _event("food_skipped", "agent=1 source=spawn x=1 y=1 kind=raw_seed energy=1 reason=low_value", tick=30),
                    ],
                    "agent_outcome_rows": [
                        {
                            "condition_id": "baseline",
                            "replicate_id": "baseline_seed_100",
                            "seed": 100,
                            "agent_id": 1,
                            "generation": 0,
                            "alive": True,
                            "immortal": False,
                            "friend_count": 0,
                            "remembered_food_sources_count": 1,
                            "remembered_safe_zones_count": 0,
                            "remembered_danger_count": 0,
                            "remembered_nest_locations_count": 0,
                            "food_eaten": 2,
                            "meals_by_type_json": {"raw_seed": 1, "raw_plant": 1},
                            "skipped_food_by_type_json": {"raw_seed": 1},
                            "food_value_memory_json": {"raw_seed": 1.0, "raw_plant": 5.0},
                        }
                    ],
                    "runtime_provenance": {"test": True},
                },
            )

            self.assertIn("novelty_framing_md", manifest)
            self.assertIn("claim_evidence_map_csv", manifest)

            novelty = Path(manifest["novelty_framing_md"]).read_text(encoding="utf-8")
            self.assertIn("experience-sensitive behavior", novelty)
            self.assertIn("not proof of open-ended evolution", novelty)

            claim_rows = _read_csv(Path(manifest["claim_evidence_map_csv"]))
            learning_claim = next(
                row for row in claim_rows if row["claim_id"] == "C1_individual_experience_sensitive_learning"
            )
            strong_claim = next(
                row for row in claim_rows if row["claim_id"] == "C6_intentional_farming_or_open_ended_evolution"
            )
            self.assertEqual(learning_claim["current_status"], "supported_in_package")
            self.assertEqual(strong_claim["current_status"], "prohibited_by_claim_scope")


if __name__ == "__main__":
    unittest.main()
