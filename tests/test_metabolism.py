"""First unit test in the repo — Metabolism Physics v2.0 scaffolding.

Run from anywhere:  python tests/test_metabolism.py
Protocol: reports/metabolism_physics_v2_0_protocol_2026-06-15.th.md
"""

import os
import sys
import unittest

# Make the repo root importable regardless of cwd (repo has no test infra yet).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.body import BodyPlan
from world.environment import FOOD_ENERGY, FOOD_RAW_MEAT, FOOD_RAW_PLANT
from world.metabolism import (
    COMPOSITION,
    FOOD_MASS,
    FOOD_SIZE,
    can_ingest,
    digestible_energy,
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


if __name__ == "__main__":
    unittest.main()
