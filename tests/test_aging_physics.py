"""Aging Physics v1 — unit + property + reproducibility tests.

Run:  python tests/test_aging_physics.py

Validates that the aging module reproduces the PROVEN results from the longevity
literature (papers/longevity/, and the audit reports/physics_realism_audit_aging_
2026-07-01.th.md):
  - death EMERGES from accumulated damage crossing a threshold (senescence),
    not from a hard age timer;
  - Disposable Soma trade-off (Kirkwood 1977): more somatic maintenance -> longer
    life (until the repair cap);
  - mortality is guaranteed (repair can never fully cancel damage -> ageing is
    inevitable; López-Otín);
  - allometric scaling (Speakman 2005): lifespan ~ mass^+aging_mass_exponent;
  - membrane/mito quality (Hulbert 2007, Kitazoe 2017): higher damage_resistance
    -> slower ageing, decoupled from metabolic rate;
  - caloric restriction (CALERIE): higher food intake -> faster ageing;
  - the aging genome is inherited byte-identically OFF (zero extra RNG) and is
    drawn within bounds ON.
"""

import math
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from random import Random

from agents.agent import Agent
from agents.body import AGING_TRAIT_FIELDS, TRAIT_BOUNDS, BodyPlan, inherit_body_plan


def _aging_env(**overrides):
    """Fake env exposing the aging knobs with the same defaults as WorldEnvironment."""
    base = dict(
        aging_physics_enabled=True,
        aging_damage_rate=0.4,
        aging_repair_gain=0.5,
        aging_maintenance_cost=2.0,
        aging_damage_threshold=100.0,
        aging_mass_exponent=0.25,
        aging_max_repair_fraction=0.95,
        aging_intake_damage_coeff=0.0,
    )
    base.update(overrides)
    return types.SimpleNamespace(**base)


def _body(**genes) -> BodyPlan:
    defaults = dict(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)
    defaults.update(genes)
    return BodyPlan(**defaults)


def _agent(body: BodyPlan) -> Agent:
    return Agent(agent_id=1, body=body, x=0, y=0)


def _damage_per_tick(body: BodyPlan, env) -> float:
    """Net damage a fresh agent accrues in one _apply_aging call (float, no rounding)."""
    agent = _agent(body)
    agent._aging_gained_mark = agent.energy_gained_total
    high = _aging_env(**{**env.__dict__, "aging_damage_threshold": 1e18})
    agent._apply_aging(high)
    return agent.damage


def _ticks_to_senescence(body: BodyPlan, env, cap: int = 2_000_000) -> int:
    agent = _agent(body)
    for tick in range(1, cap + 1):
        agent._aging_gained_mark = agent.energy_gained_total
        if agent._apply_aging(env):
            return tick
    return cap + 1  # sentinel: did not die (would be a bug)


class TestAgingCore(unittest.TestCase):
    def test_damage_accumulates_to_senescence(self):
        agent = _agent(_body())
        env = _aging_env()
        died = False
        for _ in range(100_000):
            agent._aging_gained_mark = agent.energy_gained_total
            if agent._apply_aging(env):
                died = True
                break
        self.assertTrue(died, "agent should eventually die of accumulated damage")
        self.assertEqual(agent.death_reason, "senescence")
        self.assertTrue(agent.completed_lifespan)
        self.assertFalse(agent.alive)
        self.assertGreaterEqual(agent.damage, env.aging_damage_threshold)

    def test_disposable_soma_more_maintenance_longer_life(self):
        # Kirkwood 1977: below the repair cap, more maintenance -> longer life.
        env = _aging_env()
        lifespans = [
            _ticks_to_senescence(_body(somatic_maintenance=m, repair_efficiency=1.0), env)
            for m in (0.0, 0.2, 0.4, 0.6)
        ]
        self.assertEqual(lifespans, sorted(lifespans))
        self.assertEqual(len(set(lifespans)), len(lifespans), f"should strictly increase: {lifespans}")

    def test_mortality_is_guaranteed_even_with_best_repair(self):
        # Even the best anti-ageing genome dies: repair caps below gross damage,
        # so net damage is always > 0 (López-Otín: accumulation is inevitable).
        best = _body(somatic_maintenance=1.0, repair_efficiency=1.0, damage_resistance=2.0)
        ticks = _ticks_to_senescence(best, _aging_env())
        self.assertLess(ticks, 1_000_000, "no genome may be immortal under aging physics")

    def test_higher_damage_resistance_slows_ageing(self):
        # Hulbert/Kitazoe: better membranes/mitochondria -> less damage per unit
        # metabolism, decoupled from metabolic rate.
        env = _aging_env()
        low = _damage_per_tick(_body(damage_resistance=0.5, somatic_maintenance=0.0), env)
        high = _damage_per_tick(_body(damage_resistance=2.0, somatic_maintenance=0.0), env)
        self.assertLess(high, low)
        self.assertAlmostEqual(low / high, 4.0, places=6)  # gross ∝ 1/resistance

    def test_caloric_restriction_intake_accelerates_ageing(self):
        # CALERIE: more energy absorbed this tick -> more damage. So restricting
        # intake extends life (with the CR lever on).
        env = _aging_env(aging_intake_damage_coeff=0.01)
        fasted = _agent(_body(somatic_maintenance=0.0))
        fasted._aging_gained_mark = 0.0
        fasted.energy_gained_total = 0.0
        fasted._apply_aging(env)

        fed = _agent(_body(somatic_maintenance=0.0))
        fed._aging_gained_mark = 0.0
        fed.energy_gained_total = 50.0  # absorbed 50 energy this tick
        fed._apply_aging(env)

        self.assertGreater(fed.damage, fasted.damage)
        self.assertAlmostEqual(fed.damage - fasted.damage, 0.01 * 50.0, places=6)


class TestAllometry(unittest.TestCase):
    def test_lifespan_scales_as_mass_to_the_exponent(self):
        # Speakman 2005: lifespan ~ mass^0.15-0.3. With maintenance off, lifespan =
        # threshold / damage_per_tick, and damage_per_tick ∝ mass^-exponent, so the
        # log-log slope of lifespan vs mass must equal aging_mass_exponent.
        env = _aging_env(aging_mass_exponent=0.25)
        masses = [0.5, 1.0, 2.0, 4.0]
        lifespans = [
            env.aging_damage_threshold / _damage_per_tick(_body(body_mass=m, somatic_maintenance=0.0), env)
            for m in masses
        ]
        xs = [math.log(m) for m in masses]
        ys = [math.log(L) for L in lifespans]
        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / sum((x - mean_x) ** 2 for x in xs)
        self.assertAlmostEqual(slope, 0.25, places=6)
        self.assertGreaterEqual(slope, 0.15)  # inside Speakman's empirical band
        self.assertLessEqual(slope, 0.30)

    def test_exponent_knob_changes_slope(self):
        for exp in (0.15, 0.20, 0.30):
            env = _aging_env(aging_mass_exponent=exp)
            masses = [0.5, 1.0, 2.0, 4.0]
            lifespans = [
                env.aging_damage_threshold / _damage_per_tick(_body(body_mass=m, somatic_maintenance=0.0), env)
                for m in masses
            ]
            xs = [math.log(m) for m in masses]
            ys = [math.log(L) for L in lifespans]
            n = len(xs)
            mean_x = sum(xs) / n
            mean_y = sum(ys) / n
            slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / sum((x - mean_x) ** 2 for x in xs)
            self.assertAlmostEqual(slope, exp, places=6)


class TestAgingInheritance(unittest.TestCase):
    def _parent(self) -> BodyPlan:
        return _body(body_mass=1.5, somatic_maintenance=0.5, repair_efficiency=0.6, damage_resistance=1.2)

    def test_off_is_byte_identical_zero_extra_rng(self):
        # draw_aging_genes=False must consume ZERO extra RNG vs not passing it, so
        # v1/Phase 1-5 and metabolism-v2 streams stay byte-identical.
        p = self._parent()
        rng1 = Random(123)
        child1 = inherit_body_plan(p, p, rng1, draw_metabolism_genes=True, draw_aging_genes=False)
        tail1 = rng1.random()
        rng2 = Random(123)
        child2 = inherit_body_plan(p, p, rng2, draw_metabolism_genes=True)  # default False
        tail2 = rng2.random()
        self.assertEqual(tail1, tail2, "OFF path must not consume extra RNG")
        self.assertEqual(child1.trait_values, child2.trait_values)

    def test_off_leaves_aging_genes_at_defaults(self):
        p = self._parent()
        child = inherit_body_plan(p, p, Random(1), draw_aging_genes=False)
        self.assertEqual(child.body_mass, 1.0)
        self.assertEqual(child.somatic_maintenance, 0.3)
        self.assertEqual(child.repair_efficiency, 0.5)
        self.assertEqual(child.damage_resistance, 1.0)

    def test_on_draws_rng_and_inherits_within_bounds(self):
        p = self._parent()
        rngA = Random(7)
        inherit_body_plan(p, p, rngA, draw_metabolism_genes=True, draw_aging_genes=False)
        after_off = rngA.random()
        rngB = Random(7)
        child = inherit_body_plan(p, p, rngB, draw_metabolism_genes=True, draw_aging_genes=True)
        after_on = rngB.random()
        self.assertNotEqual(after_off, after_on, "ON path must consume aging RNG draws")
        for field in AGING_TRAIT_FIELDS:
            low, high = TRAIT_BOUNDS[field]
            self.assertGreaterEqual(getattr(child, field), low)
            self.assertLessEqual(getattr(child, field), high)


if __name__ == "__main__":
    unittest.main(verbosity=2)
