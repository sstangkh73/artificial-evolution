# -*- coding: utf-8 -*-
"""Render a REAL snapshot of the food-value Artificial Evolution world.

Builds the actual Environment (same config as the per-agent food-value study),
steps it with real Agent.tick for a few hundred ticks, then draws the live 2D
grid: agents at their positions and every food item coloured by its kind
(raw_seed / raw_plant / raw_fruit). Nothing is faked -- it is the program state.

Output: reports/figures/world_snapshot.png
"""
import sys
from pathlib import Path
from random import Random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_HERE))

import food_value_study_driver as D
import run_long_emergence_watch as R
from world.environment import Environment
from agents.agent import Agent

plt.rcParams.update({"font.family": "Tahoma", "axes.unicode_minus": False,
                     "figure.dpi": 150, "savefig.dpi": 150})

COLORS = {"raw_seed": "#B7791F", "raw_plant": "#1F8A5B", "raw_fruit": "#C0392B"}
THAI = {"raw_seed": "เมล็ด (ค่าต่ำ)", "raw_plant": "พืช (ค่าสูง)", "raw_fruit": "ผลไม้"}


def build_env(args):
    """Reproduce run_watch's Environment construction (kept in sync manually)."""
    g = lambda n, d=None: getattr(args, n, d)
    return Environment(
        width=args.width, height=args.height, max_food=args.max_food,
        base_food_spawn_per_tick=args.base_food_spawn_per_tick,
        food_spawn_multiplier=args.food_spawn_multiplier,
        bootstrap_food_spawn_ticks=args.bootstrap_food_spawn_ticks,
        wild_food_spawn_after_bootstrap_multiplier=args.wild_food_spawn_after_bootstrap_multiplier,
        natural_seed_rain_per_tick=args.natural_seed_rain_per_tick,
        max_plant_seeds=args.max_plant_seeds,
        large_animal_spawn_per_tick=args.large_animal_spawn_per_tick,
        max_large_animals=args.max_large_animals,
        nest_support_food_chance=args.nest_support_food_chance,
        nest_support_spawn_chance=args.nest_support_spawn_chance,
        frontier_band=args.frontier_band,
        global_food_decline_per_day=args.global_food_decline_per_day,
        minimum_global_food_multiplier=args.minimum_global_food_multiplier,
        ambient_food_decay_chance=args.ambient_food_decay_chance,
        plant_food_decay_chance=args.plant_food_decay_chance,
        plant_seed_max_age_multiplier=args.plant_seed_max_age_multiplier,
        plant_growth_rate_multiplier=args.plant_growth_rate_multiplier,
        sprout_biomass_loss_multiplier=args.sprout_biomass_loss_multiplier,
        germination_good_ticks_multiplier=args.germination_good_ticks_multiplier,
        plant_fruiting_interval_multiplier=args.plant_fruiting_interval_multiplier,
        plant_fruiting_growth_threshold_multiplier=args.plant_fruiting_growth_threshold_multiplier,
        plant_fruiting_chance_multiplier=args.plant_fruiting_chance_multiplier,
        natural_seed_drop_chance_multiplier=args.natural_seed_drop_chance_multiplier,
        food_signal_radius_cap=g("food_signal_radius_cap"),
        food_sensing_radius=g("food_sensing_radius", 0),
        food_detection_threshold=g("food_detection_threshold", 0.0),
        vision_horizon=g("vision_horizon", 0),
        memory_return_enabled=g("memory_return_enabled", True),
        metabolism_model=g("metabolism_model", "v1"),
        low_value_food_spawn_per_tick=g("low_value_food_spawn_per_tick", 0.0),
        food_energy_multiplier=g("food_energy_multiplier", 1.0),
        metabolic_drain_multiplier=g("metabolic_drain_multiplier", 1.0),
        food_value_learning_enabled=g("food_value_learning_enabled", False),
        diet_pickiness=g("diet_pickiness", 0.5),
        diet_starvation_energy=g("diet_starvation_energy", 6),
    )


def main():
    args = D.make_args(seed=20260610, model="v2", max_ticks=250, output="data/_snap_tmp",
                       low_value_food=6, value_learning=True, food_energy_mult=50,
                       drain_mult=0.1, population=12, world=40, max_population=40,
                       body_index=37)
    rng = Random(args.seed)
    body = R.generate_candidate_body_plans()[max(1, min(args.body_index, 999)) - 1]
    env = build_env(args)
    positions = R._spawn_initial_positions(env, rng, args.initial_population, body,
                                           strategy=args.spawn_strategy)
    agents = [Agent(agent_id=i, body=body, x=x, y=y, age=R.FOUNDER_START_AGE, immortal=True)
              for i, (x, y) in enumerate(positions)]
    for _ in range(args.max_ticks):
        env.step(rng)
        for a in agents:
            a.tick(env, rng)

    W = args.width
    fig, ax = plt.subplots(figsize=(6.6, 6.4))
    ax.set_facecolor("#FaFbFc")
    # food items by kind
    by_kind = {}
    for (x, y), res in env.food_positions.items():
        by_kind.setdefault(res.kind, []).append((x, y))
    for kind, pts in by_kind.items():
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        ax.scatter(xs, ys, s=42, color=COLORS.get(kind, "#9AA0A0"),
                   edgecolor="white", linewidth=0.4, zorder=2)
    # agents
    ax_ = [a.x for a in agents]; ay_ = [a.y for a in agents]
    ax.scatter(ax_, ay_, s=170, marker="^", color="#1F4E79", edgecolor="white",
               linewidth=0.8, zorder=4)
    for a in agents:
        ax.text(a.x, a.y - 1.1, "AI", ha="center", fontsize=7, color="#1F4E79", zorder=4)

    ax.set_xlim(-1, W); ax.set_ylim(-1, W); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(f"โลกจำลอง 2 มิติ ขนาด {W}×{W} — เอเจนต์ {len(agents)} ตัว หากินท่ามกลางอาหารหลายชนิด\n"
                 f"(ภาพสถานะจริงจากโปรแกรม Artificial Evolution ที่รอบเวลา {args.max_ticks})",
                 fontsize=11)
    handles = [Line2D([0], [0], marker="^", color="w", markerfacecolor="#1F4E79",
                      markersize=12, label="เอเจนต์ (AI)")]
    for kind in ("raw_seed", "raw_plant", "raw_fruit"):
        if kind in by_kind:
            handles.append(Line2D([0], [0], marker="o", color="w",
                                  markerfacecolor=COLORS[kind], markersize=11, label=THAI[kind]))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.02),
              ncol=len(handles), fontsize=9, frameon=False)
    fig.tight_layout()
    out = _HERE.parent / "reports" / "figures" / "world_snapshot.png"
    fig.savefig(out, bbox_inches="tight"); plt.close(fig)
    counts = {k: len(v) for k, v in by_kind.items()}
    print(f"wrote {out}  agents={len(agents)} food_by_kind={counts}")


if __name__ == "__main__":
    main()
