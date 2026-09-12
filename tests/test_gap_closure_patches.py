# -*- coding: utf-8 -*-
"""Tests for the G1-G6 gap-closure patches P0-P3.

Plans under test:
  reports/PLAN_G1_G6_gap_closure_2026-09-12.th.md   (why each gap blocks the paper)
  reports/PLAN_E1_E6_experiments_2026-09-12.th.md   (P0-P3 and the E1-E5 arms)

P0  env.toxin_potency_scale   -- the matched-potency control arm A3
P1  env.food_value_key_mode   -- the rescue arm B2 and its sham control B3
P2  BodyPlan.metabolism_values + gene/outcome columns -- selection must be measurable
P3  env.encounter_telemetry_enabled -- the exposure denominator P(eat | encounter)

Run:  python -m unittest tests.test_gap_closure_patches
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from random import Random
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from agents.agent import Agent
from agents.body import BodyPlan, METABOLISM_TRAIT_FIELDS
from simulation.research_artifacts import write_research_artifacts
from world import metabolism
from world.environment import Environment, FoodResource

FRUIT_LOAD = metabolism.FOOD_MASS["raw_fruit"] * metabolism.COMPOSITION["raw_fruit"]["toxin"]
DEFAULT_TOLERANCE = 0.2
NOW = 10_000


def _body(**genes) -> BodyPlan:
    spec = dict(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)
    spec.update(genes)
    return BodyPlan(**spec)


def _agent(**genes) -> Agent:
    return Agent(agent_id=1, body=_body(**genes), x=0, y=0)


def _fruit(age: int = 0) -> SimpleNamespace:
    return SimpleNamespace(kind="raw_fruit", energy=10, source="test", created_tick=NOW - age)


def _env(**overrides) -> SimpleNamespace:
    base = dict(
        food_value_learning_enabled=True,
        diet_learning_rate=0.3,
        diet_pickiness=0.6,
        diet_starvation_energy=6,
        toxin_acute_penalty=50.0,
        toxin_damage_coeff=0.0,
        toxin_detox_ticks=0,
        toxin_safe_window_start=0,
        toxin_safe_window_end=0,
        toxin_potency_scale=1.0,
        food_value_key_mode="type",
        food_value_age_bin=1,
        food_value_age_max_bin=8,
        tick_count=NOW,
        food_positions={},
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _excess(potency: float, tolerance: float = DEFAULT_TOLERANCE) -> float:
    """Realised toxin dose for one raw_fruit bite at a given potency."""
    return metabolism.toxin_penalty(FRUIT_LOAD * potency, tolerance)


# ---------------------------------------------------------------- P0


class TestPotencyScale(unittest.TestCase):
    def test_potency_scale_default_is_one(self):
        """An env without the knob and an env with 1.0 must behave identically."""
        legacy = SimpleNamespace(toxin_acute_penalty=50.0, toxin_damage_coeff=1.0)
        scaled = SimpleNamespace(toxin_acute_penalty=50.0, toxin_damage_coeff=1.0,
                                 toxin_potency_scale=1.0)
        a, b = _agent(), _agent()
        self.assertEqual(a._apply_toxin(legacy, _fruit(), 10), b._apply_toxin(scaled, _fruit(), 10))
        self.assertEqual(a.toxin_ingested_total, b.toxin_ingested_total)
        self.assertEqual(a.damage, b.damage)

    def test_potency_scale_scales_realised_potency(self):
        """The knob must act on potency, before the tolerance subtraction."""
        agent = _agent()
        agent._apply_toxin(_env(toxin_potency_scale=0.5, toxin_damage_coeff=1.0), _fruit(), 10)
        self.assertAlmostEqual(agent.toxin_ingested_total, _excess(0.5), places=9)

    def test_potency_scale_below_tolerance_is_harmless(self):
        agent = _agent()
        out = agent._apply_toxin(_env(toxin_potency_scale=0.4, toxin_damage_coeff=1.0), _fruit(), 10)
        self.assertEqual(out, 10)
        self.assertEqual(agent.toxin_ingested_total, 0.0)

    def test_matched_mean_potency_does_not_match_mean_dose(self):
        """Matching MEAN POTENCY is not enough to build the A3 control arm.

        toxin_penalty subtracts tolerance from the load, so realised dose is a
        CONVEX function of potency: a variable-potency arm whose mean potency is p
        ingests strictly MORE toxin than a constant-potency-p arm. An A3 built by
        setting toxin_potency_scale to the mean potency of A2 would be under-dosed,
        and any A2 deficit could then be explained by dose rather than by hidden
        state -- exactly the confound A3 exists to remove. A3 must be matched on
        realised DOSE instead.
        """
        detox_ticks = 8
        potencies = [metabolism.toxin_age_potency(age, detox_ticks, 0, 0) for age in range(detox_ticks)]
        mean_potency = sum(potencies) / len(potencies)

        variable_dose = sum(_excess(p) for p in potencies) / len(potencies)
        matched_potency_dose = _excess(mean_potency)

        self.assertGreater(variable_dose, matched_potency_dose)
        self.assertGreater(variable_dose, 5 * matched_potency_dose,
                           "convexity gap should be large enough to matter, not a rounding effect")

    def test_dose_matched_scale_reproduces_the_variable_arms_mean_dose(self):
        """The scale that makes A3 a fair control is solved on dose, not potency."""
        from calibrate_matched_potency import solve_dose_matched_scale

        detox_ticks = 8
        potencies = [metabolism.toxin_age_potency(age, detox_ticks, 0, 0) for age in range(detox_ticks)]
        target_dose = sum(_excess(p) for p in potencies) / len(potencies)

        scale = solve_dose_matched_scale(target_dose, [DEFAULT_TOLERANCE], kind="raw_fruit")
        self.assertAlmostEqual(_excess(scale), target_dose, places=6)

        agent = _agent()
        agent._apply_toxin(_env(toxin_potency_scale=scale, toxin_damage_coeff=1.0), _fruit(), 10)
        self.assertAlmostEqual(agent.toxin_ingested_total, target_dose, places=6)


# ---------------------------------------------------------------- P1


def _taste(agent, env, resource, gross=10):
    """One encounter: decide, and on a bite apply toxin then learn (as production does)."""
    env.food_positions = {(agent.x, agent.y): resource}
    if not agent._food_worth_eating(env):
        return False
    net = agent._apply_toxin(env, resource, gross)
    agent._learn_food_value(env, resource.kind, net, resource=resource)
    return True


def _fruit_at(tick, age):
    return SimpleNamespace(kind="raw_fruit", energy=10, source="test", created_tick=tick - age)


def _train(env, ages, seed=20260912, trials=400, gross=10):
    """Well-fed learner meets fruit of random age; returns it after training.

    The clock ADVANCES between encounters. That matters for the sham arm: its bin
    is a scramble of the food's creation tick, so holding env.tick_count frozen
    would make age -> bin a fixed mapping and hand the sham arm the very
    information it is supposed to lack. A frozen clock is a harness artefact; the
    real loop always advances.
    """
    rng = Random(seed)
    agent = _agent()
    agent.food_value_memory = {"raw_plant": 5.0}
    for step in range(trials):
        env.tick_count = NOW + step
        agent.energy = 100  # isolate preference from hunger
        _taste(agent, env, _fruit_at(env.tick_count, rng.choice(ages)), gross=gross)
    env.tick_count = NOW + trials
    return agent


def _p_eat_by_age(agent, env, ages, probes=40):
    """Mean eat-rate per food age, averaged over several ticks.

    Averaging matters for the same reason: a single probe tick would sample one
    arbitrary sham mapping rather than the arm's behaviour.
    """
    out = {}
    base = int(env.tick_count)
    for age in ages:
        eaten = 0
        for step in range(probes):
            env.tick_count = base + step
            agent.energy = 100
            env.food_positions = {(agent.x, agent.y): _fruit_at(env.tick_count, age)}
            eaten += 1 if agent._food_worth_eating(env) else 0
        out[age] = eaten / probes
    env.tick_count = base
    return out


class TestFoodValueKey(unittest.TestCase):
    def test_key_mode_type_is_byte_identical(self):
        """Default mode must key on kind alone and leave the legacy call form working."""
        env = _env()
        agent = _agent()
        resource = _fruit(37)
        self.assertEqual(agent._food_value_key(env, resource), "raw_fruit")

        legacy, keyed = _agent(), _agent()
        legacy._learn_food_value(env, "raw_fruit", 7.0)           # frozen-script form
        keyed._learn_food_value(env, "raw_fruit", 7.0, resource=resource)
        self.assertEqual(legacy.food_value_memory, keyed.food_value_memory)

    def test_type_age_key_separates_fresh_and_aged(self):
        env = _env(food_value_key_mode="type_age", food_value_age_bin=1, food_value_age_max_bin=8)
        agent = _agent()
        self.assertEqual(agent._food_value_key(env, _fruit(0)), "raw_fruit@0")
        self.assertEqual(agent._food_value_key(env, _fruit(5)), "raw_fruit@5")
        self.assertEqual(agent._food_value_key(env, _fruit(99)), "raw_fruit@8",
                         "ages above the cap share the top bin")

        env.food_value_age_bin = 4
        self.assertEqual(agent._food_value_key(env, _fruit(3)), "raw_fruit@0")
        self.assertEqual(agent._food_value_key(env, _fruit(4)), "raw_fruit@1")

    def test_type_age_key_recovers_safe_window(self):
        """Profile W (toxic -> safe -> toxic) is the case a monotonic rule cannot solve.

        With the age cue the learner must end up eating inside the safe window and
        refusing outside it; keyed on kind alone it cannot represent the difference
        at all, so its decision is the same at every age.
        """
        ages = list(range(0, 10))
        window = dict(toxin_safe_window_start=3, toxin_safe_window_end=7)

        aged_env = _env(food_value_key_mode="type_age", food_value_age_max_bin=9, **window)
        aged = _train(aged_env, ages)
        aged_p = _p_eat_by_age(aged, aged_env, ages)
        self.assertTrue(all(aged_p[a] == 1.0 for a in (3, 4, 5, 6)), f"safe window refused: {aged_p}")
        self.assertTrue(all(aged_p[a] == 0.0 for a in (0, 1, 2, 7, 8, 9)), f"toxic ages eaten: {aged_p}")

        typed_env = _env(food_value_key_mode="type", **window)
        typed = _train(typed_env, ages)
        typed_p = _p_eat_by_age(typed, typed_env, ages)
        self.assertEqual(len(set(typed_p.values())), 1,
                         f"type-only keying cannot vary its decision with age: {typed_p}")

    def test_sham_key_count_matches_type_age(self):
        """B3 must have the same key cardinality as B2 -- that is the whole control."""
        ages = list(range(0, 10))
        window = dict(toxin_safe_window_start=3, toxin_safe_window_end=7)
        max_bin = 9

        aged = _train(_env(food_value_key_mode="type_age", food_value_age_max_bin=max_bin, **window), ages)
        sham = _train(_env(food_value_key_mode="type_sham", food_value_age_max_bin=max_bin, **window), ages)

        aged_keys = {k for k in aged.food_value_memory if k.startswith("raw_fruit@")}
        sham_keys = {k for k in sham.food_value_memory if k.startswith("raw_fruit@")}
        self.assertEqual(len(aged_keys), len(sham_keys),
                         f"key counts differ: {sorted(aged_keys)} vs {sorted(sham_keys)}")

    def test_sham_key_does_not_recover_window(self):
        """Same number of keys, no information -> no recovery of the safe window."""
        ages = list(range(0, 10))
        window = dict(toxin_safe_window_start=3, toxin_safe_window_end=7)
        env = _env(food_value_key_mode="type_sham", food_value_age_max_bin=9, **window)

        sham = _train(env, ages)
        p_eat = _p_eat_by_age(sham, env, ages)
        safe_rate = sum(p_eat[a] for a in (3, 4, 5, 6)) / 4
        toxic_rate = sum(p_eat[a] for a in (0, 1, 2, 7, 8, 9)) / 6
        self.assertLess(safe_rate - toxic_rate, 0.5,
                        f"sham key must not discriminate safe from toxic ages: {p_eat}")

    def test_sham_key_is_deterministic(self):
        """Reproducible: the bin is a pure function of the food, not an RNG draw."""
        env = _env(food_value_key_mode="type_sham", food_value_age_max_bin=7)
        agent = _agent()
        resource = _fruit(4)
        self.assertEqual(agent._food_value_key(env, resource), agent._food_value_key(env, resource))

        bins = [int(agent._food_value_key(env, _fruit(age)).split("@")[1]) for age in range(200)]
        self.assertGreater(len(set(bins)), 1, "sham bins must actually spread")
        self.assertLessEqual(max(bins), 7)
        self.assertNotEqual(bins, sorted(bins), "a monotonic assignment would carry age")

    def test_sham_age_to_bin_mapping_is_not_stable_across_ticks(self):
        """The property that makes the sham key information-free.

        The bin scrambles the food's CREATION tick, so at any single tick it is a
        function of age -- but the mapping is reshuffled on the next tick, so no
        stable age -> value association can be learned. Anything that held the
        clock still would break this and silently turn B3 into a second B2.
        """
        agent = _agent()
        env = _env(food_value_key_mode="type_sham", food_value_age_max_bin=7)
        ages = list(range(10))
        mappings = set()
        for tick in range(NOW, NOW + 12):
            env.tick_count = tick
            mappings.add(tuple(
                agent._food_value_key(env, _fruit_at(tick, age)) for age in ages
            ))
        self.assertGreater(len(mappings), 1, "sham mapping must change as the clock advances")


# ---------------------------------------------------------------- P3


def _world(**overrides) -> Environment:
    """A real Environment with all spawning off, so only placed food exists.

    Deliberately not a stub: the encounter counters sit in the production eating
    path, which reaches into cooking heat, fertility and seed handling. A stub that
    only fakes consume_food would test a path that does not exist.
    """
    settings = dict(
        width=20, height=20, max_food=0, base_food_spawn_per_tick=0,
        max_large_animals=0, large_animal_spawn_per_tick=0,
        food_value_learning_enabled=True, diet_pickiness=0.6, diet_starvation_energy=6,
        encounter_telemetry_enabled=True, encounter_age_bin=1, encounter_age_max_bin=32,
    )
    settings.update(overrides)
    env = Environment(**settings)
    env.tick_count = NOW
    return env


def _place(env, agent, kind: str, age: int, energy: int = 10) -> None:
    env.food_positions[(agent.x, agent.y)] = FoodResource(
        kind=kind, energy=energy, source="test", created_tick=env.tick_count - age
    )


class TestEncounterTelemetry(unittest.TestCase):
    def test_encounter_counts_sum_to_ate_plus_skipped(self):
        env = _world()
        agent = _agent()
        agent.energy = 100
        agent.food_value_memory = {"raw_plant": 40.0, "raw_fruit": 1.0}  # fruit below pickiness
        for tick in range(6):
            env.tick_count = NOW + tick
            _place(env, agent, "raw_fruit", 0)
            agent._consume_current_food(env)
            env.tick_count = NOW + 100 + tick
            _place(env, agent, "raw_plant", 0, energy=5)
            agent._consume_current_food(env)

        self.assertTrue(agent.encounters_by_kind_age)
        for key, counts in agent.encounters_by_kind_age.items():
            self.assertEqual(counts["seen"], counts["ate"] + counts["skipped"], key)
        fruit_skips = sum(c["skipped"] for k, c in agent.encounters_by_kind_age.items()
                          if k.startswith("raw_fruit@"))
        plant_meals = sum(c["ate"] for k, c in agent.encounters_by_kind_age.items()
                          if k.startswith("raw_plant@"))
        self.assertEqual(fruit_skips, 6, "every low-value fruit encounter should be a recorded skip")
        self.assertEqual(plant_meals, 6, "every high-value plant encounter should be a recorded meal")

    def test_encounter_telemetry_off_records_nothing(self):
        env = _world(encounter_telemetry_enabled=False)
        agent = _agent()
        agent.energy = 100
        _place(env, agent, "raw_fruit", 0)
        self.assertTrue(agent._consume_current_food(env))
        self.assertEqual(agent.encounters_by_kind_age, {})

    def test_encounter_is_deduplicated_within_a_tick(self):
        """_consume_current_food runs twice in a hunger tick; one cell = one encounter.

        Without this the legacy skip counter double-counts refusals but never
        double-counts meals, which would bias P(eat | encounter) downward.
        """
        env = _world()
        agent = _agent()
        agent.energy = 100
        agent.food_value_memory = {"raw_plant": 40.0, "raw_fruit": 1.0}
        _place(env, agent, "raw_fruit", 0)
        agent._consume_current_food(env)
        agent._consume_current_food(env)   # same tick, same cell, food still there

        counts = agent.encounters_by_kind_age["raw_fruit@0"]
        self.assertEqual(counts["seen"], 1)
        self.assertEqual(counts["skipped"], 1)
        self.assertEqual(agent.skipped_food_by_type["raw_fruit"], 2,
                         "legacy counter is left as-is on purpose (byte-identical)")

    def test_encounter_age_bins_track_real_food_age(self):
        env = _world(encounter_age_bin=2, encounter_age_max_bin=3)
        agent = _agent()
        agent.energy = 100
        for index, age in enumerate((0, 3, 5, 40)):
            env.tick_count = NOW + index
            _place(env, agent, "raw_fruit", age)
            agent._consume_current_food(env)
        self.assertEqual(sorted(agent.encounters_by_kind_age),
                         ["raw_fruit@0", "raw_fruit@1", "raw_fruit@2", "raw_fruit@3"])


# ---------------------------------------------------------------- P2


class TestGeneAndOutcomeTelemetry(unittest.TestCase):
    def test_metabolism_values_includes_toxin_tolerance(self):
        values = _body().metabolism_values
        self.assertEqual(set(values), set(METABOLISM_TRAIT_FIELDS))
        self.assertIn("toxin_tolerance", values)
        self.assertNotIn("toxin_tolerance", _body().trait_values,
                         "metabolism genes must stay out of TRAIT_FIELDS (inheritance RNG prefix)")

    def _write(self, tmp, agent_row, generation_row):
        payload = {
            "metadata": {
                "run_name": "gap_closure_test", "change_note": "-", "seed": 1,
                "final_tick": 0, "body_name": "body_37", "body_design": "-",
            },
            "summary": {
                "peak_population": 0, "total_births": 0, "matured_children": 0,
                "first_birth_tick": None, "first_matured_child_tick": None,
                "death_reasons": {},
            },
            "tick_metrics": [],
            "events": [],
            "lineages": [],
            "agent_outcomes": [agent_row],
            "generation_traits": [generation_row],
        }
        write_research_artifacts(Path(tmp), payload)
        return Path(tmp)

    def test_agent_outcomes_csv_includes_genes_and_toxin_columns(self):
        row = {
            "agent_id": 1, "age": 55, "death_reason": "senescence",
            "damage": 101.5, "toxin_ingested_total": 2.5, "toxin_damage_total": 1.25,
            "maintenance_energy_total": 30.0, "body_mass": 1.0,
            "toxin_tolerance": 0.31, "gape": 5.0, "gut_capacity": 8.0,
            "gut_transit_ticks": 6, "acid_strength": 0.4, "cellulose_efficiency": 0.25,
            "encounters_by_kind_age_json": {"raw_fruit@0": {"seen": 3, "ate": 1, "skipped": 2}},
        }
        with tempfile.TemporaryDirectory() as tmp:
            out = self._write(tmp, row, {"generation": 0, "agent_count": 1})
            text = (out / "agent_outcomes.csv").read_text(encoding="utf-8").splitlines()
            header = text[0].split(",")
            for column in ("damage", "toxin_ingested_total", "toxin_damage_total",
                           "toxin_tolerance", "encounters_by_kind_age_json"):
                self.assertIn(column, header)
            self.assertIn("0.31", text[1])

    def test_generation_traits_include_toxin_tolerance(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self._write(tmp, {"agent_id": 1},
                              {"generation": 0, "agent_count": 2, "mean_toxin_tolerance": 0.27})
            lines = (out / "generation_traits.csv").read_text(encoding="utf-8").splitlines()
            self.assertIn("mean_toxin_tolerance", lines[0].split(","))
            self.assertIn("0.27", lines[1])


if __name__ == "__main__":
    unittest.main()
