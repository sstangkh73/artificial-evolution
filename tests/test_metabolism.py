"""First unit test in the repo — Metabolism Physics v2.0 scaffolding.

Run from anywhere:  python tests/test_metabolism.py
Protocol: reports/metabolism_physics_v2_0_protocol_2026-06-15.th.md
"""

import os
import sys
import types
import unittest

# Make the repo root importable regardless of cwd (repo has no test infra yet).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent import Agent
from agents.body import BodyPlan
from world.environment import FOOD_ENERGY, FOOD_RAW_MEAT, FOOD_RAW_PLANT
from world.metabolism import (
    COMPOSITION,
    FOOD_MASS,
    FOOD_SIZE,
    can_ingest,
    digestible_energy,
    toxin_load,
    toxin_penalty,
)


def _default_body() -> BodyPlan:
    return BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)


class TestMetabolismV20(unittest.TestCase):
    def test_composition_fractions_sum_to_one(self):
        for kind, comp in COMPOSITION.items():
            self.assertAlmostEqual(sum(comp.values()), 1.0, places=6, msg=f"{kind} fractions must sum to 1.0")

    def test_raw_plant_energy_matches_hand_calc(self):
        # 3.24 + 0.84 + 0.675 = 4.755
        energy = digestible_energy(COMPOSITION["raw_plant"], FOOD_MASS["raw_plant"], _default_body().enzyme_profile)
        self.assertAlmostEqual(energy, 4.755, places=3)

    def test_raw_meat_energy_matches_hand_calc(self):
        # 1.5 * (0.55 * 0.7 * 24) = 13.86
        energy = digestible_energy(COMPOSITION["raw_meat"], FOOD_MASS["raw_meat"], _default_body().enzyme_profile)
        self.assertAlmostEqual(energy, 13.86, places=3)

    def test_ingestion_gate(self):
        gape = _default_body().gape  # 5.0
        self.assertTrue(can_ingest(FOOD_SIZE["raw_meat"], gape))   # 5.0 <= 5.0
        self.assertTrue(can_ingest(FOOD_SIZE["raw_plant"], gape))  # 2.0 <= 5.0
        self.assertFalse(can_ingest(6.0, gape))                    # too big to fit

    def test_undigestible_nutrient_yields_zero(self):
        # A body with an empty enzyme profile extracts nothing.
        self.assertEqual(digestible_energy(COMPOSITION["raw_plant"], 1.0, {}), 0.0)

    def test_v1_food_energy_unchanged(self):
        # Guard: v2.0 must not alter the legacy energy table (runtime still v1).
        self.assertEqual(FOOD_ENERGY[FOOD_RAW_PLANT], 6)
        self.assertEqual(FOOD_ENERGY[FOOD_RAW_MEAT], 18)


class TestMetabolismV21Wiring(unittest.TestCase):
    """v2.1: Agent._metabolic_base_energy honors env.metabolism_model.

    Called unbound with a stub `self` (only needs `.body`) and stub env/resource,
    so we test the flag branch without standing up a full Agent or world.
    """

    def setUp(self):
        self.fake_self = types.SimpleNamespace(
            body=BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)
        )
        self.env_v1 = types.SimpleNamespace(metabolism_model="v1")
        self.env_v2 = types.SimpleNamespace(metabolism_model="v2")

    def _base(self, env, kind, energy):
        resource = types.SimpleNamespace(kind=kind, energy=energy)
        return Agent._metabolic_base_energy(self.fake_self, env, resource)

    def test_v1_passes_through_legacy_energy(self):
        self.assertEqual(self._base(self.env_v1, FOOD_RAW_PLANT, 6), 6)
        self.assertEqual(self._base(self.env_v1, FOOD_RAW_MEAT, 18), 18)

    def test_v2_uses_composition_energy(self):
        # round(4.755) = 5 (plant), round(13.86) = 14 (meat)
        self.assertEqual(self._base(self.env_v2, FOOD_RAW_PLANT, 6), 5)
        self.assertEqual(self._base(self.env_v2, FOOD_RAW_MEAT, 18), 14)

    def test_v2_unknown_kind_falls_back_to_legacy(self):
        self.assertEqual(self._base(self.env_v2, "mystery_food", 99), 99)


class TestMetabolismV22Endozoochory(unittest.TestCase):
    """v2.2: gut transit deposits seeds at a NEW position (endozoochory)."""

    def _env_with_seed(self, sx, sy):
        from world.environment import Environment

        env = Environment(width=20, height=20, metabolism_model="v2")
        seed = env._deposit_seed(
            species="wild_grain", x=sx, y=sy, burial_depth_cm=0.0, dispersal_mode="gut_transit"
        )
        seed.carried_by_agent_id = 1
        return env, seed

    def test_excrete_survives_when_acid_below_shell(self):
        env, seed = self._env_with_seed(5, 5)
        ok = env.excrete_gut_seed(seed.seed_id, agent_id=1, x=9, y=9, acid_strength=0.4)
        self.assertTrue(ok)
        self.assertEqual((seed.x, seed.y), (9, 9))
        self.assertIsNone(seed.carried_by_agent_id)
        self.assertEqual(seed.dispersal_mode, "gut_passed")
        self.assertGreater(seed.viability, 0.0)

    def test_excrete_kills_when_acid_exceeds_shell(self):
        env, seed = self._env_with_seed(5, 5)
        ok = env.excrete_gut_seed(seed.seed_id, agent_id=1, x=9, y=9, acid_strength=0.9)
        self.assertFalse(ok)
        self.assertEqual(seed.viability, 0.0)

    def test_process_gut_waits_for_transit_then_excretes(self):
        env, seed = self._env_with_seed(5, 5)
        body = BodyPlan(
            sensor_units=1, muscle_units=1, armor_units=0, brain_units=1,
            gut_transit_ticks=6, acid_strength=0.4,
        )
        fake = types.SimpleNamespace(gut_seeds=[(seed.seed_id, 0)], body=body, agent_id=1, x=9, y=9)
        # Before transit elapses: seed stays in the gut.
        env.tick_count = 3
        Agent._process_gut(fake, env)
        self.assertEqual(len(fake.gut_seeds), 1)
        self.assertEqual(seed.carried_by_agent_id, 1)
        # After transit elapses: excreted at the agent's current position.
        env.tick_count = 6
        Agent._process_gut(fake, env)
        self.assertEqual(len(fake.gut_seeds), 0)
        self.assertEqual((seed.x, seed.y), (9, 9))
        self.assertIsNone(seed.carried_by_agent_id)


class TestMetabolismV21GapeGate(unittest.TestCase):
    """v2.1 layer 1: Agent._fits_mouth gates ingestion by object size vs gape."""

    def _fits(self, model, kind, gape):
        env = types.SimpleNamespace(
            metabolism_model=model, food_positions={(0, 0): types.SimpleNamespace(kind=kind)}
        )
        body = BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1, gape=gape)
        me = types.SimpleNamespace(x=0, y=0, body=body)
        return Agent._fits_mouth(me, env)

    def test_v1_always_fits(self):
        self.assertTrue(self._fits("v1", "raw_meat", 1.0))

    def test_v2_blocks_object_bigger_than_gape(self):
        self.assertFalse(self._fits("v2", "raw_meat", 1.0))  # meat size 5 > gape 1

    def test_v2_allows_fitting_object(self):
        self.assertTrue(self._fits("v2", "raw_meat", 5.0))   # 5 <= 5
        self.assertTrue(self._fits("v2", "raw_plant", 5.0))

    def test_v2_empty_cell_fits(self):
        env = types.SimpleNamespace(metabolism_model="v2", food_positions={})
        body = BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)
        me = types.SimpleNamespace(x=0, y=0, body=body)
        self.assertTrue(Agent._fits_mouth(me, env))


class TestMetabolismV23Toxin(unittest.TestCase):
    """v2.3 scaffold: toxin load/penalty pure functions (not yet wired in)."""

    def test_toxin_load_zero_for_clean_food(self):
        self.assertEqual(toxin_load(COMPOSITION["raw_plant"], 1.0), 0.0)

    def test_toxin_load_scales_with_mass(self):
        self.assertAlmostEqual(toxin_load({"toxin": 0.5}, 2.0), 1.0)

    def test_toxin_penalty_zero_within_tolerance(self):
        self.assertEqual(toxin_penalty(0.1, 0.2), 0.0)

    def test_toxin_penalty_excess_above_tolerance(self):
        self.assertAlmostEqual(toxin_penalty(1.0, 0.2), 0.8)


class TestMetabolismV2Heritability(unittest.TestCase):
    """Fix 3: digestion genes are heritable ONLY under v2 (draw_metabolism_genes),
    and the v1 path consumes zero extra RNG draws (byte-identity guarantee)."""

    from random import Random as _Random

    class _CountingRandom(_Random):
        """random.Random that counts random() calls (uniform() routes through it)."""

        def __init__(self, seed):
            super().__init__(seed)
            self.draws = 0

        def random(self):
            self.draws += 1
            return super().random()

    @staticmethod
    def _parents():
        # Two parents with distinct, non-default metabolism genes so inheritance
        # is observable (defaults are gape=5, gut_capacity=8, acid=0.4, ...).
        from agents.body import BodyPlan
        pa = BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1,
                      gape=4.0, gut_capacity=6.0, gut_transit_ticks=4,
                      acid_strength=0.3, cellulose_efficiency=0.2, toxin_tolerance=0.1)
        pb = BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1,
                      gape=8.0, gut_capacity=14.0, gut_transit_ticks=12,
                      acid_strength=0.8, cellulose_efficiency=0.6, toxin_tolerance=0.5)
        return pa, pb

    def test_v1_genes_stay_default(self):
        from agents.body import inherit_body_plan
        pa, pb = self._parents()
        child = inherit_body_plan(pa, pb, self._Random(7), draw_metabolism_genes=False)
        # v1: not inherited -> BodyPlan dataclass defaults.
        self.assertEqual(child.gape, 5.0)
        self.assertEqual(child.gut_capacity, 8.0)
        self.assertEqual(child.gut_transit_ticks, 6)
        self.assertEqual(child.acid_strength, 0.4)

    def test_v1_consumes_no_metabolism_rng_draws(self):
        from agents.body import inherit_body_plan
        pa, pb = self._parents()
        r_false = self._CountingRandom(7)
        inherit_body_plan(pa, pb, r_false, draw_metabolism_genes=False)
        r_true = self._CountingRandom(7)
        inherit_body_plan(pa, pb, r_true, draw_metabolism_genes=True)
        # v2 must consume strictly more draws; the extra draws are the metabolism
        # block at the tail, so the v1 prefix is untouched.
        self.assertGreater(r_true.draws, r_false.draws)

    def test_v2_genes_inherited_and_bounded(self):
        from agents.body import TRAIT_BOUNDS, inherit_body_plan
        pa, pb = self._parents()
        seen = set()
        for seed in range(40):
            child = inherit_body_plan(pa, pb, self._Random(seed), draw_metabolism_genes=True)
            for field in ("gape", "gut_capacity", "acid_strength", "cellulose_efficiency", "toxin_tolerance"):
                low, high = TRAIT_BOUNDS[field]
                value = getattr(child, field)
                self.assertGreaterEqual(value, low)
                self.assertLessEqual(value, high)
            self.assertIsInstance(child.gut_transit_ticks, int)
            seen.add(round(child.acid_strength, 4))
        # Inheritance + mutation must produce variation across offspring, and the
        # values must not collapse to the dataclass default (0.4).
        self.assertGreater(len(seen), 1)
        self.assertTrue(any(v != 0.4 for v in seen))


class TestLowValueSeedFood(unittest.TestCase):
    """Food-value study: raw_seed is edible (fits any mouth) but low-value."""

    def test_raw_seed_is_low_value_but_positive(self):
        body = _default_body()
        seed_e = digestible_energy(COMPOSITION["raw_seed"], FOOD_MASS["raw_seed"], body.enzyme_profile)
        plant_e = digestible_energy(COMPOSITION["raw_plant"], FOOD_MASS["raw_plant"], body.enzyme_profile)
        self.assertGreater(seed_e, 0.0)          # edible: yields some energy
        self.assertLess(seed_e, 0.3 * plant_e)   # but "not worth it" vs fruit

    def test_raw_seed_fits_any_mouth(self):
        # size-only ingestion gate: small seed fits the default gape (5.0)
        self.assertTrue(can_ingest(FOOD_SIZE["raw_seed"], 5.0))
        self.assertTrue(can_ingest(FOOD_SIZE["raw_seed"], 2.0))


if __name__ == "__main__":
    unittest.main()
