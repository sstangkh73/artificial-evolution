"""Regression tests for experiment-seed-sensitive movement.

Run from repo root:
    python -m unittest tests.test_seed_independence
"""

import os
import sys
import unittest
from random import Random

# Make the repo root importable regardless of cwd.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent import Agent
from agents.body import BodyPlan
from world.environment import Environment


def _probe_body() -> BodyPlan:
    return BodyPlan.from_archetype(2, 2, 0, 2, "social_planner")


def _empty_env() -> Environment:
    return Environment(
        width=20,
        height=20,
        max_food=0,
        base_food_spawn_per_tick=0,
        max_large_animals=0,
        large_animal_spawn_per_tick=0,
    )


def _targeted_move_outcome(seed: int) -> tuple[int, int, float, int]:
    agent = Agent(agent_id=7, body=_probe_body(), x=10, y=10, age=42)
    agent._move_toward(_empty_env(), 13, 13, Random(seed))
    return (agent.x, agent.y, round(agent.energy, 3), agent.distance_traveled)


class TestSeedIndependentMovement(unittest.TestCase):
    def test_targeted_movement_is_reproducible_for_same_seed(self):
        first = _targeted_move_outcome(20260610)
        second = _targeted_move_outcome(20260610)

        self.assertEqual(first, second)

    def test_targeted_movement_can_vary_across_experiment_seeds(self):
        outcomes = {
            _targeted_move_outcome(seed)
            for seed in [20260610, 20260611, 20260612, 20260613, 20260614]
        }

        self.assertGreater(
            len(outcomes),
            1,
            "targeted movement should not be locked to agent_id + age across experiment seeds",
        )


if __name__ == "__main__":
    unittest.main()
