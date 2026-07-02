"""Toxicity study (G11) — toxin -> acute energy penalty + chronic damage, and the
link to food-value learning (does the agent LEARN to avoid a toxic-but-rich food?).

Run:  python tests/test_toxin.py

Design under test (agents/agent.py `_apply_toxin`, world/metabolism.py `raw_fruit`):
  raw_fruit = HIGH energy (~10.3 vs raw_plant ~4.8) but HIGH toxin. Toxin load
  beyond a body's heritable toxin_tolerance causes (a) an ACUTE net-energy hit
  that flows into food_value_memory -> learnable avoidance, and (b) CHRONIC
  somatic `damage` (aging channel). No oracle: the world never labels food toxic.
"""

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent import Agent
from agents.body import BodyPlan
from world import metabolism


def _body(**genes) -> BodyPlan:
    d = dict(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)
    d.update(genes)
    return BodyPlan(**d)


def _agent(body: BodyPlan) -> Agent:
    return Agent(agent_id=1, body=body, x=0, y=0)


def _fruit():
    return types.SimpleNamespace(kind="raw_fruit")


def _tox_env(acute=0.0, chronic=0.0):
    return types.SimpleNamespace(toxin_acute_penalty=acute, toxin_damage_coeff=chronic)


# raw_fruit: toxin_load = mass 1.2 x toxin 0.30 = 0.36; excess @ tol 0.2 = 0.16.
EXCESS_AT_DEFAULT_TOL = 0.16


class TestToxinCore(unittest.TestCase):
    def test_off_is_byte_identical(self):
        a = _agent(_body())
        out = a._apply_toxin(_tox_env(0.0, 0.0), _fruit(), 10)
        self.assertEqual(out, 10)
        self.assertEqual(a.damage, 0.0)
        self.assertEqual(a.toxin_ingested_total, 0.0)
        self.assertEqual(a.toxin_damage_total, 0.0)

    def test_below_tolerance_no_effect(self):
        # tolerance 0.4 > toxin_load 0.36 -> zero excess -> no penalty even when on.
        a = _agent(_body(toxin_tolerance=0.4))
        out = a._apply_toxin(_tox_env(acute=50.0, chronic=10.0), _fruit(), 10)
        self.assertEqual(out, 10)
        self.assertEqual(a.damage, 0.0)
        self.assertEqual(a.toxin_ingested_total, 0.0)

    def test_acute_penalty_reduces_net_energy(self):
        a = _agent(_body(toxin_tolerance=0.2))
        out = a._apply_toxin(_tox_env(acute=20.0), _fruit(), 10)
        self.assertEqual(out, round(10 - EXCESS_AT_DEFAULT_TOL * 20.0))  # 10 - 3.2 -> 7
        self.assertAlmostEqual(a.toxin_ingested_total, EXCESS_AT_DEFAULT_TOL, places=6)
        self.assertEqual(a.damage, 0.0)  # acute only, no chronic

    def test_strong_poison_can_net_negative(self):
        a = _agent(_body(toxin_tolerance=0.0))  # excess = full 0.36
        out = a._apply_toxin(_tox_env(acute=50.0), _fruit(), 10)
        self.assertLess(out, 0)  # 10 - 0.36*50 = -8

    def test_chronic_damage_added(self):
        a = _agent(_body(toxin_tolerance=0.2))
        a._apply_toxin(_tox_env(chronic=10.0), _fruit(), 10)
        self.assertAlmostEqual(a.damage, EXCESS_AT_DEFAULT_TOL * 10.0, places=6)  # 1.6
        self.assertAlmostEqual(a.toxin_damage_total, EXCESS_AT_DEFAULT_TOL * 10.0, places=6)

    def test_tolerance_gene_mitigates_monotonically(self):
        env = _tox_env(acute=20.0, chronic=10.0)
        dmg = []
        for tol in (0.0, 0.1, 0.2, 0.3):
            a = _agent(_body(toxin_tolerance=tol))
            a._apply_toxin(env, _fruit(), 10)
            dmg.append(a.damage)
        self.assertEqual(dmg, sorted(dmg, reverse=True))  # higher tolerance -> less damage
        self.assertGreater(dmg[0], dmg[-1])

    def test_non_toxic_food_unaffected(self):
        a = _agent(_body(toxin_tolerance=0.0))
        out = a._apply_toxin(_tox_env(acute=50.0, chronic=10.0), types.SimpleNamespace(kind="raw_plant"), 5)
        self.assertEqual(out, 5)
        self.assertEqual(a.damage, 0.0)


class TestToxinLearningLink(unittest.TestCase):
    def _learn_env(self):
        return types.SimpleNamespace(
            food_value_learning_enabled=True, diet_learning_rate=0.4, diet_pickiness=0.5,
            diet_starvation_energy=6, toxin_acute_penalty=50.0, toxin_damage_coeff=0.0,
            food_positions={},
        )

    def test_learned_value_reflects_toxin(self):
        # Repeated toxic bites: the learned raw_fruit value converges to its NET
        # (post-sickness) energy, which is far below its gross ~10 -> avoidance is
        # learnable without any oracle.
        env = self._learn_env()
        a = _agent(_body(toxin_tolerance=0.2))
        for _ in range(30):
            net = a._apply_toxin(env, _fruit(), 10)  # gross 10 -> net 10-8 = 2
            a._learn_food_value(env, "raw_fruit", net)
        self.assertLess(a.food_value_memory["raw_fruit"], 5.0)
        self.assertAlmostEqual(a.food_value_memory["raw_fruit"], 2.0, delta=0.5)

    def test_agent_skips_toxic_food_once_a_better_food_is_known(self):
        # With a good food known (raw_plant) and toxic fruit learned low, the
        # real optimal-diet gate skips the fruit under the agent.
        env = self._learn_env()
        a = _agent(_body())
        a.energy = 100  # not starving
        a.food_value_memory = {"raw_plant": 4.75, "raw_fruit": 2.0}
        env.food_positions = {(a.x, a.y): _fruit()}
        self.assertFalse(a._food_worth_eating(env))  # 2.0 < 0.5 * 4.75 -> skip
        # ...but eats it if it were the only/valuable option
        a.food_value_memory = {"raw_fruit": 6.0}
        self.assertTrue(a._food_worth_eating(env))


if __name__ == "__main__":
    unittest.main(verbosity=2)
