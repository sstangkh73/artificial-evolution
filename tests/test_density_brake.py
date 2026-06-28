"""Unit tests for the proportional food-per-capita density brake on continuous
reproduction (continuous_repro_food_target).

Mechanism rationale: reports/r0_fecundity_analysis_2026-06-20.th.md — fecundity is
at replacement, so the extinction cause is dynamical (delayed-logistic boom-bust).
The brake throttles reproduction BEFORE overshoot to damp the oscillation.

Run from anywhere:  python tests/test_density_brake.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent import _continuous_repro_food_brake
from world.environment import Environment


class TestFoodDensityBrake(unittest.TestCase):
    def test_off_by_default_returns_one(self):
        # target <= 0 disables the brake -> exactly 1.0 so prob*brake is unchanged
        # (the byte-identical guarantee for every pre-existing run/config).
        self.assertEqual(_continuous_repro_food_brake(0.0, 0.0), 1.0)
        self.assertEqual(_continuous_repro_food_brake(123.4, 0.0), 1.0)
        self.assertEqual(_continuous_repro_food_brake(5.0, -2.0), 1.0)

    def test_abundant_food_no_throttle(self):
        # food-per-capita at/above target -> full reproduction (clamped to 1.0).
        self.assertEqual(_continuous_repro_food_brake(10.0, 10.0), 1.0)
        self.assertEqual(_continuous_repro_food_brake(40.0, 10.0), 1.0)

    def test_scarce_food_proportional_throttle(self):
        # below target the multiplier is linear: half the food per head -> half rate.
        self.assertAlmostEqual(_continuous_repro_food_brake(5.0, 10.0), 0.5, places=9)
        self.assertAlmostEqual(_continuous_repro_food_brake(2.0, 10.0), 0.2, places=9)

    def test_zero_food_stops_reproduction(self):
        self.assertEqual(_continuous_repro_food_brake(0.0, 10.0), 0.0)

    def test_negative_food_guarded_to_zero(self):
        # defensive: food_per_capita should never be < 0, but never return < 0.
        self.assertEqual(_continuous_repro_food_brake(-3.0, 10.0), 0.0)

    def test_monotonic_in_food(self):
        target = 8.0
        prev = -1.0
        for fpc in [0.0, 1.0, 2.0, 4.0, 8.0, 16.0]:
            cur = _continuous_repro_food_brake(fpc, target)
            self.assertGreaterEqual(cur, prev)
            self.assertGreaterEqual(cur, 0.0)
            self.assertLessEqual(cur, 1.0)
            prev = cur

    def test_env_default_is_off(self):
        # A fresh environment must default the brake off (and expose food_per_capita)
        # so existing experiments stay byte-identical until the knob is set.
        env = Environment(width=10, height=10)
        self.assertEqual(env.continuous_repro_food_target, 0.0)
        self.assertEqual(env.food_per_capita, 0.0)


if __name__ == "__main__":
    unittest.main()
