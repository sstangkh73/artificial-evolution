# -*- coding: utf-8 -*-
"""Render competition visuals for the neuroevolution result.

Produces two figures:

  1. neuroevolution_learning_curve.png
     best / mean / median fitness vs generation, from a run's history JSON.
     Shows the population learning to forage across generations.

  2. neuroevolution_behavior_random_vs_evolved.png
     side-by-side foraging paths of an untrained (gen-0 random) network and the
     evolved best network in the SAME seeded world. Makes the abstract result
     tangible: random = aimless wandering, evolved = directed foraging.

Figure text is English (ISEF-style, font-safe); add Thai captions in the report.

Usage:
    python scripts/render_neuroevolution_demo.py \
        --history data/neuroevolution_smoke_2026-06-27.json \
        --best data/neuroevolution_best_2026-06-27.json \
        --outdir reports/figures
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from random import Random

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from agents import neural_brain
from agents.agent import ADULT_AGE, Agent
from agents.neural_brain import NeuralBrainSpec
from world.environment import Environment

# import the exact same body + world config the evolution used
from scripts.run_neuroevolution import build_body, _food_config


def render_learning_curve(history_path: Path, out_path: Path) -> None:
    data = json.loads(history_path.read_text(encoding="utf-8"))
    hist = data["history"]
    gens = [r["generation"] for r in hist]
    best = [r["best_fitness"] for r in hist]
    mean = [r["mean_fitness"] for r in hist]
    median = [r["median_fitness"] for r in hist]

    baseline = data["random_baseline_mean_fitness"]
    final = data["final_mean_fitness"]
    factor = data["mean_improvement_vs_random"]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(gens, best, "-o", color="#1b9e77", label="best in population", linewidth=2)
    ax.plot(gens, mean, "-o", color="#d95f02", label="population mean", linewidth=2)
    ax.plot(gens, median, "--", color="#7570b3", label="population median", linewidth=1.5)

    ax.axhline(baseline, color="#999999", linestyle=":", linewidth=1)
    ax.annotate(
        f"random baseline (gen 0) = {baseline:.1f}",
        xy=(0, baseline),
        xytext=(len(gens) * 0.30, baseline + (max(best) * 0.06)),
        fontsize=9,
        color="#555555",
    )
    ax.annotate(
        f"evolved mean = {final:.1f}  ({factor}x)",
        xy=(gens[-1], final),
        xytext=(len(gens) * 0.35, final + (max(best) * 0.10)),
        fontsize=10,
        color="#d95f02",
        arrowprops=dict(arrowstyle="->", color="#d95f02"),
    )

    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness  (food energy gathered per lifetime)")
    ax.set_title("Neuroevolution: agents learn to forage across generations")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.margins(x=0.02)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"wrote {out_path}")


def capture_single_agent(genome, spec, *, world, ticks, eval_seed, max_food, food_spawn):
    """Run one agent in a seeded world; record its path, eat events, food field."""
    env = Environment(**_food_config(world, max_food, food_spawn))
    env.neural_controller_enabled = True
    env.neural_brain_spec = spec
    env.neural_temperature = 0.0
    rng = Random(eval_seed)
    agent = Agent(
        agent_id=0,
        body=build_body(),
        x=world // 2,
        y=world // 2,
        age=ADULT_AGE,
        immortal=True,
        neural_genome=list(genome),
    )
    path = [(agent.x, agent.y)]
    eats: list[tuple[int, int]] = []
    prev_eaten = 0
    for _ in range(ticks):
        env.step(rng)
        agent.tick(env, rng)
        path.append((agent.x, agent.y))
        if agent.food_eaten > prev_eaten:
            eats.append((agent.x, agent.y))
            prev_eaten = agent.food_eaten
    food = list(env.food_positions.keys())
    return {"path": path, "eats": eats, "food": food, "eaten": agent.food_eaten}


def _draw_path(ax, cap, world, title):
    fx = [p[0] for p in cap["food"]]
    fy = [p[1] for p in cap["food"]]
    ax.scatter(fx, fy, s=8, color="#bdbd9b", alpha=0.5, label="food", zorder=1)

    pts = cap["path"]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    # colour the path by time (start -> end) so direction/purpose is visible
    segs = [[(xs[i], ys[i]), (xs[i + 1], ys[i + 1])] for i in range(len(xs) - 1)]
    lc = LineCollection(segs, cmap="viridis", linewidth=1.6, zorder=2)
    lc.set_array(range(len(segs)))
    ax.add_collection(lc)

    ax.scatter([xs[0]], [ys[0]], s=70, marker="o", color="black", zorder=4, label="start")
    if cap["eats"]:
        ex = [p[0] for p in cap["eats"]]
        ey = [p[1] for p in cap["eats"]]
        ax.scatter(ex, ey, s=60, marker="*", color="#e41a1c", zorder=3,
                   label=f"ate food (x{cap['eaten']})")

    ax.set_xlim(-1, world)
    ax.set_ylim(-1, world)
    ax.set_aspect("equal")
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8)
    ax.set_xticks([])
    ax.set_yticks([])


def render_behavior(best_path: Path, out_path: Path, eval_seed: int, ticks: int) -> None:
    saved = json.loads(best_path.read_text(encoding="utf-8"))
    spec = neural_brain.spec_from_dict(saved["spec"])
    evolved = saved["genome"]
    cfg = saved["config"]
    world = cfg["world"]
    max_food = cfg["max_food"]
    food_spawn = cfg["food_spawn"]

    random_genome = neural_brain.random_genome(spec, Random(0))

    cap_rand = capture_single_agent(
        random_genome, spec, world=world, ticks=ticks,
        eval_seed=eval_seed, max_food=max_food, food_spawn=food_spawn,
    )
    cap_evo = capture_single_agent(
        evolved, spec, world=world, ticks=ticks,
        eval_seed=eval_seed, max_food=max_food, food_spawn=food_spawn,
    )

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(11, 5.5))
    _draw_path(axl, cap_rand, world, f"Untrained network (gen 0)\nfood eaten: {cap_rand['eaten']}")
    _draw_path(axr, cap_evo, world, f"Evolved network\nfood eaten: {cap_evo['eaten']}")
    fig.suptitle(
        "Same world, same body — only the neural brain differs. "
        "Evolution turns aimless wandering into directed foraging.",
        fontsize=12,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"wrote {out_path}  (random ate {cap_rand['eaten']}, evolved ate {cap_evo['eaten']})")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--history", default="data/neuroevolution_smoke_2026-06-27.json")
    p.add_argument("--best", default="data/neuroevolution_best_2026-06-27.json")
    p.add_argument("--outdir", default="reports/figures")
    p.add_argument("--behavior-seed", type=int, default=1000, help="world seed for the behaviour demo")
    p.add_argument("--behavior-ticks", type=int, default=250)
    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    render_learning_curve(Path(args.history), outdir / "neuroevolution_learning_curve.png")
    render_behavior(
        Path(args.best),
        outdir / "neuroevolution_behavior_random_vs_evolved.png",
        args.behavior_seed,
        args.behavior_ticks,
    )


if __name__ == "__main__":
    main()
