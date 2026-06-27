# -*- coding: utf-8 -*-
"""Neuroevolution driver for the neural-brain agent controller.

Evolves a population of neural-network *genomes* (weights + biases) across
generations with explicit fitness-based selection -- the "Artificial Evolution"
the project is named for. Each generation:

  1. every genome is dropped into the world as an agent and lives ``ticks`` ticks
  2. fitness = total food energy the agent actually gathered (foraging skill)
  3. the fittest genomes are kept (elitism); the rest of the next generation is
     bred by tournament selection + crossover + Gaussian mutation

Generation 0 is a population of *random* networks, so the gen-0 mean is the
random-agent baseline and the rise from gen 0 -> gen G is the learning curve.

Everything is standard library only and fully seeded, so a given command is
reproducible. Fitness can be averaged over several evaluation worlds
(``--eval-seeds``) so the result is not a single-world fluke.

Example (smoke):
    python scripts/run_neuroevolution.py --generations 8 --pop 24 --ticks 150 \
        --world 30 --seed 1 --dump data/neuroevo_smoke.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from random import Random

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))  # repo root
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from agents import neural_brain
from agents.agent import ADULT_AGE, Agent
from agents.body import BodyPlan
from agents.neural_brain import NeuralBrainSpec
from world.environment import Environment


def build_body() -> BodyPlan:
    """A single fixed body shared by all agents: only the brain evolves, so the
    fitness difference between generations is attributable to the network."""
    return BodyPlan(sensor_units=2, muscle_units=2, armor_units=0, brain_units=2)


def _food_config(world: int, max_food: int, food_spawn: int) -> dict:
    return {
        "width": world,
        "height": world,
        "max_food": max_food,
        "base_food_spawn_per_tick": food_spawn,
        # keep the world stationary across generations so fitness reflects the
        # brain, not a drifting food economy
        "global_food_decline_per_day": 0.0,
        "bootstrap_food_spawn_ticks": 10_000_000,
        "metabolism_model": "v1",
    }


def evaluate(
    genomes: list[list[float]],
    spec: NeuralBrainSpec,
    *,
    world: int,
    ticks: int,
    eval_seed: int,
    max_food: int,
    food_spawn: int,
    temperature: float,
) -> list[float]:
    """Run one world and return each genome's fitness (total food energy gained).

    Agents are immortal so every genome gets the full horizon (no luck-of-death);
    foraging skill is what separates them.
    """
    env = Environment(**_food_config(world, max_food, food_spawn))
    env.neural_controller_enabled = True
    env.neural_brain_spec = spec
    env.neural_temperature = temperature

    rng = Random(eval_seed)
    agents: list[Agent] = []
    for i, genome in enumerate(genomes):
        x = rng.randrange(world)
        y = rng.randrange(world)
        agents.append(
            Agent(
                agent_id=i,
                body=build_body(),
                x=x,
                y=y,
                age=ADULT_AGE,
                immortal=True,
                neural_genome=genome,
            )
        )

    for _ in range(ticks):
        env.step(rng)
        for agent in agents:
            agent.tick(env, rng)

    return [float(agent.energy_gained_total) for agent in agents]


def evaluate_mean(
    genomes: list[list[float]],
    spec: NeuralBrainSpec,
    *,
    world: int,
    ticks: int,
    eval_seeds: list[int],
    max_food: int,
    food_spawn: int,
    temperature: float,
) -> list[float]:
    """Average fitness over several evaluation worlds to avoid single-world bias."""
    totals = [0.0] * len(genomes)
    for es in eval_seeds:
        fit = evaluate(
            genomes,
            spec,
            world=world,
            ticks=ticks,
            eval_seed=es,
            max_food=max_food,
            food_spawn=food_spawn,
            temperature=temperature,
        )
        for i, f in enumerate(fit):
            totals[i] += f
    n = len(eval_seeds)
    return [t / n for t in totals]


def _tournament(fitnesses: list[float], rng: Random, k: int) -> int:
    """Return the index of the tournament winner among k random contenders."""
    best = rng.randrange(len(fitnesses))
    for _ in range(k - 1):
        challenger = rng.randrange(len(fitnesses))
        if fitnesses[challenger] > fitnesses[best]:
            best = challenger
    return best


def next_generation(
    genomes: list[list[float]],
    fitnesses: list[float],
    rng: Random,
    *,
    elite_frac: float,
    tournament_k: int,
    mutation_rate: float,
    mutation_sigma: float,
) -> list[list[float]]:
    n = len(genomes)
    order = sorted(range(n), key=lambda i: fitnesses[i], reverse=True)
    elite_n = max(1, int(round(n * elite_frac)))
    # elitism: best genomes survive unchanged
    new_genomes = [list(genomes[i]) for i in order[:elite_n]]
    while len(new_genomes) < n:
        pa = genomes[_tournament(fitnesses, rng, tournament_k)]
        pb = genomes[_tournament(fitnesses, rng, tournament_k)]
        child = neural_brain.crossover(pa, pb, rng)
        child = neural_brain.mutate(child, rng, rate=mutation_rate, sigma=mutation_sigma)
        new_genomes.append(child)
    return new_genomes


def run(args: argparse.Namespace) -> dict:
    spec = NeuralBrainSpec()
    rng = Random(args.seed)
    eval_seeds = [args.eval_seed + i for i in range(args.eval_seeds)]

    genomes = [neural_brain.random_genome(spec, rng) for _ in range(args.pop)]

    history: list[dict] = []
    for gen in range(args.generations):
        fitnesses = evaluate_mean(
            genomes,
            spec,
            world=args.world,
            ticks=args.ticks,
            eval_seeds=eval_seeds,
            max_food=args.max_food,
            food_spawn=args.food_spawn,
            temperature=args.temperature,
        )
        best = max(fitnesses)
        mean = statistics.mean(fitnesses)
        median = statistics.median(fitnesses)
        row = {
            "generation": gen,
            "best_fitness": round(best, 3),
            "mean_fitness": round(mean, 3),
            "median_fitness": round(median, 3),
        }
        history.append(row)
        print(
            f"gen {gen:>3}  best={best:10.2f}  mean={mean:9.2f}  median={median:9.2f}",
            flush=True,
        )
        if gen < args.generations - 1:
            genomes = next_generation(
                genomes,
                fitnesses,
                rng,
                elite_frac=args.elite_frac,
                tournament_k=args.tournament_k,
                mutation_rate=args.mutation_rate,
                mutation_sigma=args.mutation_sigma,
            )

    # The final population's best genome (elitism guarantees it is the overall
    # best). Save it so the demo/visualiser can replay its behaviour.
    best_idx = max(range(len(genomes)), key=lambda i: fitnesses[i])
    if getattr(args, "save_best", None):
        Path(args.save_best).parent.mkdir(parents=True, exist_ok=True)
        Path(args.save_best).write_text(
            json.dumps(
                {
                    "spec": neural_brain.spec_to_dict(spec),
                    "genome": genomes[best_idx],
                    "fitness": fitnesses[best_idx],
                    "config": {
                        "world": args.world,
                        "ticks": args.ticks,
                        "max_food": args.max_food,
                        "food_spawn": args.food_spawn,
                        "eval_seeds": eval_seeds,
                        "seed": args.seed,
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        print(f"saved best genome -> {args.save_best}")

    baseline_mean = history[0]["mean_fitness"]
    final_mean = history[-1]["mean_fitness"]
    final_best = history[-1]["best_fitness"]
    improvement = (final_mean / baseline_mean) if baseline_mean > 0 else float("inf")
    summary = {
        "config": {
            "generations": args.generations,
            "pop": args.pop,
            "ticks": args.ticks,
            "world": args.world,
            "seed": args.seed,
            "eval_seeds": eval_seeds,
            "elite_frac": args.elite_frac,
            "tournament_k": args.tournament_k,
            "mutation_rate": args.mutation_rate,
            "mutation_sigma": args.mutation_sigma,
            "temperature": args.temperature,
            "genome_size": spec.genome_size(),
            "spec": neural_brain.spec_to_dict(spec),
        },
        "random_baseline_mean_fitness": baseline_mean,
        "final_mean_fitness": final_mean,
        "final_best_fitness": final_best,
        "mean_improvement_vs_random": round(improvement, 3),
        "history": history,
    }
    print(
        f"\nrandom baseline (gen0 mean) = {baseline_mean:.2f}  ->  "
        f"final mean = {final_mean:.2f}  "
        f"({summary['mean_improvement_vs_random']}x)  best = {final_best:.2f}"
    )
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--generations", type=int, default=12)
    p.add_argument("--pop", type=int, default=30)
    p.add_argument("--ticks", type=int, default=200, help="lifetime ticks per evaluation")
    p.add_argument("--world", type=int, default=30, help="world width=height")
    p.add_argument("--seed", type=int, default=1, help="evolution RNG seed (init/mutation/selection)")
    p.add_argument("--eval-seed", type=int, default=1000, help="first evaluation-world seed")
    p.add_argument("--eval-seeds", type=int, default=1, help="number of evaluation worlds to average over")
    p.add_argument("--max-food", type=int, default=400)
    p.add_argument("--food-spawn", type=int, default=8, help="base food spawned per tick")
    p.add_argument("--elite-frac", type=float, default=0.2)
    p.add_argument("--tournament-k", type=int, default=3)
    p.add_argument("--mutation-rate", type=float, default=0.15)
    p.add_argument("--mutation-sigma", type=float, default=0.2)
    p.add_argument("--temperature", type=float, default=0.0,
                   help="action-sampling temperature (0 = deterministic argmax)")
    p.add_argument("--dump", default=None, help="write the full summary+history JSON here")
    p.add_argument("--save-best", default=None, help="write the best evolved genome JSON here (for the demo/visualiser)")
    args = p.parse_args()

    summary = run(args)
    if args.dump:
        Path(args.dump).parent.mkdir(parents=True, exist_ok=True)
        Path(args.dump).write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"wrote {args.dump}")


if __name__ == "__main__":
    main()
