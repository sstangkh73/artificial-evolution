"""Pure-Python neural brain for artificial-evolution agents.

This module implements the agent controller described in the project proposal:
a multi-input / multi-output feed-forward neural network ("โครงข่ายประสาทเทียม
แบบ Multi-Input / Multi-Output") trained by *neuroevolution* rather than gradient
descent. It is written with the Python standard library only (``math`` +
``random``) so the project keeps its "standard library only" identity and stays
byte-for-byte reproducible from a seeded RNG.

Architecture (two input streams, two output heads):

    stream 1  vision grid      (2r+1)x(2r+1) cells x C raw channels
              -> dense -> tanh -> vision features
    stream 2  scalar state     energy / hunger / affect / environment ...
              -> concatenated with the vision features
              -> dense -> tanh -> shared hidden representation
                                 |-> move head    (logits over 5 directions)
                                 `-> action head  (logits over object actions)

The network carries *no* labels about what each input means: the vision channels
are raw physical measurements of the world and the meaning of every weight is
discovered by selection, not authored by hand. A genome is just the flat list of
all weights and biases; evolution mutates and recombines these lists.

The module is self-contained and has no dependency on the rest of the codebase,
so it can be unit-tested in isolation (see ``tests/test_neural_brain.py``).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from random import Random

# Decoded action labels for the two output heads. Order is part of the genome
# contract: index i in the head logits maps to entry i here. Do not reorder
# without re-evolving, or saved genomes will mean something different.
MOVE_ACTIONS: tuple[tuple[int, int], ...] = (
    (0, 0),   # stay
    (1, 0),   # +x (east)
    (-1, 0),  # -x (west)
    (0, 1),   # +y (south)
    (0, -1),  # -y (north)
)

OBJECT_ACTIONS: tuple[str, ...] = (
    "none",       # do nothing with objects this tick
    "eat",        # consume food under the agent (if any)
    "pick_seed",  # pick up a seed under the agent
    "drop_seed",  # drop a carried seed here
)


@dataclass(frozen=True)
class NeuralBrainSpec:
    """Fixed network architecture shared by every agent in a run.

    All agents in one evolutionary run share the same architecture (so genomes
    are comparable and recombinable); only the *weights* differ. The spec knows
    how to compute the flat genome length and how to slice it into layers.
    """

    vision_radius: int = 2
    vision_channels: int = 3
    scalar_inputs: int = 12
    vision_hidden: int = 10
    shared_hidden: int = 16
    move_outputs: int = len(MOVE_ACTIONS)
    action_outputs: int = len(OBJECT_ACTIONS)

    @property
    def vision_cells(self) -> int:
        side = 2 * self.vision_radius + 1
        return side * side

    @property
    def vision_size(self) -> int:
        return self.vision_cells * self.vision_channels

    @property
    def _layers(self) -> tuple[tuple[int, int], ...]:
        """(in_dim, out_dim) for each dense layer, in forward order."""
        return (
            (self.vision_size, self.vision_hidden),                 # vision encoder
            (self.vision_hidden + self.scalar_inputs, self.shared_hidden),  # fusion
            (self.shared_hidden, self.move_outputs),                # move head
            (self.shared_hidden, self.action_outputs),             # action head
        )

    def genome_size(self) -> int:
        """Number of floats in a genome for this architecture.

        Each dense layer of (in, out) contributes out*(in+1) parameters
        (weights + one bias per output unit).
        """
        return sum(out * (in_dim + 1) for in_dim, out in self._layers)


def random_genome(spec: NeuralBrainSpec, rng: Random) -> list[float]:
    """Create a fresh random genome with small weights.

    Weights use a Xavier-style scale (1/sqrt(fan_in)) so early networks produce
    bounded activations instead of saturating tanh immediately. Biases start at
    zero. Fully determined by ``rng``.
    """
    genome: list[float] = []
    for in_dim, out in spec._layers:
        scale = 1.0 / math.sqrt(in_dim) if in_dim > 0 else 1.0
        for _ in range(out):
            for _ in range(in_dim):
                genome.append(rng.gauss(0.0, scale))
            genome.append(0.0)  # bias
    return genome


def _dense(
    genome: list[float],
    offset: int,
    inputs: list[float],
    in_dim: int,
    out_dim: int,
    activation: str,
) -> tuple[list[float], int]:
    """Apply one dense layer read from ``genome`` starting at ``offset``.

    Returns the output vector and the new offset just past this layer's
    parameters. ``activation`` is "tanh" for hidden layers or "linear" for
    output heads (raw logits).
    """
    out: list[float] = []
    pos = offset
    for _ in range(out_dim):
        acc = 0.0
        for i in range(in_dim):
            acc += genome[pos + i] * inputs[i]
        pos += in_dim
        acc += genome[pos]  # bias
        pos += 1
        if activation == "tanh":
            acc = math.tanh(acc)
        out.append(acc)
    return out, pos


def forward(
    spec: NeuralBrainSpec,
    genome: list[float],
    vision: list[float],
    scalars: list[float],
) -> tuple[list[float], list[float]]:
    """Run a forward pass. Returns ``(move_logits, action_logits)``.

    ``vision`` must have length ``spec.vision_size`` and ``scalars`` length
    ``spec.scalar_inputs``. Raises ValueError on a mismatch so wiring bugs fail
    loudly instead of silently corrupting decisions.
    """
    if len(vision) != spec.vision_size:
        raise ValueError(f"vision length {len(vision)} != spec {spec.vision_size}")
    if len(scalars) != spec.scalar_inputs:
        raise ValueError(f"scalar length {len(scalars)} != spec {spec.scalar_inputs}")
    if len(genome) != spec.genome_size():
        raise ValueError(f"genome length {len(genome)} != spec {spec.genome_size()}")

    offset = 0
    vis_feat, offset = _dense(
        genome, offset, vision, spec.vision_size, spec.vision_hidden, "tanh"
    )
    fused_in = vis_feat + scalars
    shared, offset = _dense(
        genome,
        offset,
        fused_in,
        spec.vision_hidden + spec.scalar_inputs,
        spec.shared_hidden,
        "tanh",
    )
    move_logits, offset = _dense(
        genome, offset, shared, spec.shared_hidden, spec.move_outputs, "linear"
    )
    action_logits, offset = _dense(
        genome, offset, shared, spec.shared_hidden, spec.action_outputs, "linear"
    )
    return move_logits, action_logits


def _argmax(values: list[float]) -> int:
    best_i = 0
    best_v = values[0]
    for i in range(1, len(values)):
        if values[i] > best_v:
            best_v = values[i]
            best_i = i
    return best_i


def _sample(values: list[float], rng: Random, temperature: float) -> int:
    """Temperature softmax sampling over logits (exploration)."""
    if temperature <= 0.0:
        return _argmax(values)
    m = max(values)
    weights = [math.exp((v - m) / temperature) for v in values]
    total = sum(weights)
    if total <= 0.0:
        return _argmax(values)
    r = rng.random() * total
    upto = 0.0
    for i, w in enumerate(weights):
        upto += w
        if upto >= r:
            return i
    return len(values) - 1


def decide(
    spec: NeuralBrainSpec,
    genome: list[float],
    vision: list[float],
    scalars: list[float],
    rng: Random | None = None,
    temperature: float = 0.0,
) -> tuple[int, int]:
    """Forward pass + decode to ``(move_index, action_index)``.

    With ``temperature == 0`` the choice is deterministic argmax (reproducible).
    With ``temperature > 0`` and an ``rng`` the heads are sampled, giving
    exploration during evolution.
    """
    move_logits, action_logits = forward(spec, genome, vision, scalars)
    if temperature > 0.0 and rng is not None:
        return _sample(move_logits, rng, temperature), _sample(
            action_logits, rng, temperature
        )
    return _argmax(move_logits), _argmax(action_logits)


def mutate(
    genome: list[float], rng: Random, rate: float = 0.1, sigma: float = 0.2
) -> list[float]:
    """Return a mutated *copy* of ``genome``.

    Each gene is perturbed by Gaussian noise with probability ``rate``. The
    original list is left untouched so callers can keep the parent genome.
    """
    child = list(genome)
    for i in range(len(child)):
        if rng.random() < rate:
            child[i] += rng.gauss(0.0, sigma)
    return child


def crossover(
    genome_a: list[float], genome_b: list[float], rng: Random
) -> list[float]:
    """Uniform per-gene crossover of two equal-length genomes."""
    if len(genome_a) != len(genome_b):
        raise ValueError("crossover requires equal-length genomes")
    return [genome_a[i] if rng.random() < 0.5 else genome_b[i] for i in range(len(genome_a))]


def spec_to_dict(spec: NeuralBrainSpec) -> dict:
    """JSON-serialisable description of the architecture (for saved genomes)."""
    return {
        "vision_radius": spec.vision_radius,
        "vision_channels": spec.vision_channels,
        "scalar_inputs": spec.scalar_inputs,
        "vision_hidden": spec.vision_hidden,
        "shared_hidden": spec.shared_hidden,
        "move_outputs": spec.move_outputs,
        "action_outputs": spec.action_outputs,
    }


def spec_from_dict(data: dict) -> NeuralBrainSpec:
    return NeuralBrainSpec(
        vision_radius=int(data["vision_radius"]),
        vision_channels=int(data["vision_channels"]),
        scalar_inputs=int(data["scalar_inputs"]),
        vision_hidden=int(data["vision_hidden"]),
        shared_hidden=int(data["shared_hidden"]),
        move_outputs=int(data["move_outputs"]),
        action_outputs=int(data["action_outputs"]),
    )
