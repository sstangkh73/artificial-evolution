"""Unit tests for the pure-Python neural brain (neuroevolution controller).

Run from anywhere:  python tests/test_neural_brain.py
"""

import os
import sys
import unittest
from random import Random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import neural_brain as nb
from agents.neural_brain import NeuralBrainSpec


def _obs(spec: NeuralBrainSpec, rng: Random):
    vision = [rng.random() for _ in range(spec.vision_size)]
    scalars = [rng.random() for _ in range(spec.scalar_inputs)]
    return vision, scalars


class TestGenomeShape(unittest.TestCase):
    def test_genome_size_matches_hand_calc(self):
        spec = NeuralBrainSpec(
            vision_radius=1,
            vision_channels=2,
            scalar_inputs=3,
            vision_hidden=4,
            shared_hidden=5,
        )
        # vision_size = (2*1+1)^2 * 2 = 9*2 = 18
        self.assertEqual(spec.vision_size, 18)
        # L1: 4*(18+1)=76 ; L2: 5*((4+3)+1)=40 ; move: 5*(5+1)=30 ; action: 4*(5+1)=24
        self.assertEqual(spec.genome_size(), 76 + 40 + 30 + 24)

    def test_random_genome_length(self):
        spec = NeuralBrainSpec()
        genome = nb.random_genome(spec, Random(1))
        self.assertEqual(len(genome), spec.genome_size())


class TestForward(unittest.TestCase):
    def test_forward_output_shapes(self):
        spec = NeuralBrainSpec()
        rng = Random(7)
        genome = nb.random_genome(spec, rng)
        vision, scalars = _obs(spec, rng)
        move, action = nb.forward(spec, genome, vision, scalars)
        self.assertEqual(len(move), spec.move_outputs)
        self.assertEqual(len(action), spec.action_outputs)

    def test_forward_is_deterministic(self):
        spec = NeuralBrainSpec()
        genome = nb.random_genome(spec, Random(3))
        vision, scalars = _obs(spec, Random(99))
        out_a = nb.forward(spec, genome, vision, scalars)
        out_b = nb.forward(spec, genome, vision, scalars)
        self.assertEqual(out_a, out_b)

    def test_forward_rejects_wrong_input_size(self):
        spec = NeuralBrainSpec()
        genome = nb.random_genome(spec, Random(3))
        with self.assertRaises(ValueError):
            nb.forward(spec, genome, [0.0], [0.0] * spec.scalar_inputs)
        with self.assertRaises(ValueError):
            nb.forward(spec, genome, [0.0] * spec.vision_size, [0.0])

    def test_finite_outputs(self):
        spec = NeuralBrainSpec()
        rng = Random(5)
        genome = nb.random_genome(spec, rng)
        vision, scalars = _obs(spec, rng)
        move, action = nb.forward(spec, genome, vision, scalars)
        for v in move + action:
            self.assertEqual(v, v)  # not NaN
            self.assertTrue(abs(v) < 1e9)


class TestDecide(unittest.TestCase):
    def test_decide_indices_in_range(self):
        spec = NeuralBrainSpec()
        rng = Random(11)
        genome = nb.random_genome(spec, rng)
        vision, scalars = _obs(spec, rng)
        m, a = nb.decide(spec, genome, vision, scalars)
        self.assertTrue(0 <= m < spec.move_outputs)
        self.assertTrue(0 <= a < spec.action_outputs)

    def test_argmax_is_deterministic(self):
        spec = NeuralBrainSpec()
        genome = nb.random_genome(spec, Random(2))
        vision, scalars = _obs(spec, Random(42))
        self.assertEqual(
            nb.decide(spec, genome, vision, scalars),
            nb.decide(spec, genome, vision, scalars),
        )


class TestEvolutionOps(unittest.TestCase):
    def test_mutate_preserves_length_and_copies(self):
        spec = NeuralBrainSpec()
        genome = nb.random_genome(spec, Random(1))
        child = nb.mutate(genome, Random(1), rate=1.0, sigma=0.5)
        self.assertEqual(len(child), len(genome))
        self.assertNotEqual(child, genome)  # rate=1.0 -> all genes move
        # parent untouched
        self.assertEqual(genome, nb.random_genome(spec, Random(1)))

    def test_mutate_zero_rate_is_identity(self):
        spec = NeuralBrainSpec()
        genome = nb.random_genome(spec, Random(1))
        child = nb.mutate(genome, Random(8), rate=0.0, sigma=0.5)
        self.assertEqual(child, genome)

    def test_crossover_length_and_provenance(self):
        spec = NeuralBrainSpec()
        a = nb.random_genome(spec, Random(1))
        b = nb.random_genome(spec, Random(2))
        child = nb.crossover(a, b, Random(3))
        self.assertEqual(len(child), len(a))
        for i, gene in enumerate(child):
            self.assertIn(gene, (a[i], b[i]))

    def test_crossover_unequal_raises(self):
        with self.assertRaises(ValueError):
            nb.crossover([0.0, 1.0], [0.0], Random(1))


class TestSerialization(unittest.TestCase):
    def test_spec_round_trip(self):
        spec = NeuralBrainSpec(vision_radius=3, scalar_inputs=9, shared_hidden=20)
        restored = nb.spec_from_dict(nb.spec_to_dict(spec))
        self.assertEqual(spec, restored)
        self.assertEqual(spec.genome_size(), restored.genome_size())


if __name__ == "__main__":
    unittest.main(verbosity=2)
