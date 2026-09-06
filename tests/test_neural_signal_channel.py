"""Tests for the opt-in neural signal channel.

Run from repo root:
    python -m unittest tests.test_neural_signal_channel
"""

import os
import sys
import unittest
from random import Random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import neural_brain as nb
from agents.agent import ADULT_AGE, Agent
from agents.body import BodyPlan
from agents.neural_brain import NeuralBrainSpec
from world.environment import Environment


def _empty_env() -> Environment:
    return Environment(
        width=20,
        height=20,
        max_food=0,
        base_food_spawn_per_tick=0,
        max_large_animals=0,
        large_animal_spawn_per_tick=0,
    )


def _probe_body() -> BodyPlan:
    return BodyPlan.from_archetype(2, 2, 0, 2, "social_planner")


class TestEnvironmentSignalBuffer(unittest.TestCase):
    def test_signal_is_previous_tick_visible(self):
        env = _empty_env()
        env.neural_signal_enabled = True

        env.emit_agent_signal(agent_id=1, x=5, y=5, value=1.0)
        self.assertEqual(env.agent_signal_at(5, 5, radius=0), 0.0)

        env.step(Random(1))
        self.assertEqual(env.agent_signal_at(5, 5, radius=0), 1.0)
        self.assertEqual(env.neural_signal_current, {})

    def test_receiver_blind_blocks_signal_input(self):
        env = _empty_env()
        env.neural_signal_enabled = True
        env.neural_signal_previous = {1: (5, 5, 1.0)}

        self.assertEqual(env.agent_signal_at(5, 5, radius=0), 1.0)
        env.neural_signal_receiver_blind = True
        self.assertEqual(env.agent_signal_at(5, 5, radius=0), 0.0)

    def test_shuffle_rotates_signal_values_across_emitters(self):
        env = _empty_env()
        env.neural_signal_enabled = True
        env.neural_signal_shuffle_enabled = True
        env.neural_signal_previous = {
            1: (4, 4, 1.0),
            2: (8, 8, -1.0),
        }

        self.assertEqual(env.agent_signal_at(4, 4, radius=0), -1.0)
        self.assertEqual(env.agent_signal_at(8, 8, radius=0), 1.0)


class TestAgentSignalObservation(unittest.TestCase):
    def test_new_spec_observation_includes_signal_channel(self):
        env = _empty_env()
        env.neural_signal_enabled = True
        env.neural_signal_previous = {99: (10, 10, 1.0)}
        spec = NeuralBrainSpec(vision_radius=1, vision_channels=4)
        env.neural_brain_spec = spec

        agent = Agent(agent_id=7, body=_probe_body(), x=10, y=10, age=ADULT_AGE)
        vision, scalars = agent._neural_observation(env)

        self.assertEqual(len(vision), spec.vision_size)
        self.assertEqual(len(scalars), spec.scalar_inputs)
        center_cell_index = 4
        center_signal_index = center_cell_index * spec.vision_channels + 3
        self.assertEqual(vision[center_signal_index], 1.0)

    def test_legacy_three_channel_spec_ignores_signal_channel(self):
        env = _empty_env()
        env.neural_signal_enabled = True
        env.neural_signal_previous = {99: (10, 10, 1.0)}
        spec = NeuralBrainSpec(vision_radius=1, vision_channels=3, signal_outputs=0)
        env.neural_brain_spec = spec

        agent = Agent(agent_id=7, body=_probe_body(), x=10, y=10, age=ADULT_AGE)
        vision, scalars = agent._neural_observation(env)

        self.assertEqual(len(vision), spec.vision_size)
        self.assertEqual(len(scalars), spec.scalar_inputs)

    def test_neural_decision_emits_signal_head_choice(self):
        env = _empty_env()
        env.neural_controller_enabled = True
        env.neural_signal_enabled = True
        spec = NeuralBrainSpec(vision_radius=1, vision_channels=4)
        env.neural_brain_spec = spec

        genome = [0.0] * spec.genome_size()
        signal_layer_offset = sum(
            out_dim * (in_dim + 1) for in_dim, out_dim in spec._layers[:-1]
        )
        positive_signal_bias = signal_layer_offset + (1 * (spec.shared_hidden + 1)) + spec.shared_hidden
        genome[positive_signal_bias] = 1.0

        agent = Agent(
            agent_id=7,
            body=_probe_body(),
            x=10,
            y=10,
            age=ADULT_AGE,
            neural_genome=genome,
        )
        agent._neural_decision(env, Random(1))

        self.assertEqual(agent.neural_signal_value, nb.SIGNAL_ACTIONS[1])
        self.assertEqual(env.neural_signal_current[7], (10, 10, 1.0))


if __name__ == "__main__":
    unittest.main()
