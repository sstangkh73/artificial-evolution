"""Toxicity study — does an agent LEARN to avoid a toxic-but-energy-rich food?

Run:  python scripts/run_toxin_diet_study.py

CONTROLLED experiment. In the full sim, agents are chronically near-starvation
(the documented foraging-access bottleneck), so the "eat anything when starving"
floor overrides diet choice and masks avoidance. This harness removes that
confound: a WELL-FED agent (energy reset high each trial) is offered a free
choice between raw_plant (modest energy, safe) and raw_fruit (high energy, toxic)
each trial, and decides with the REAL production gate (_food_worth_eating) +
toxin physics (_apply_toxin) + learning (_learn_food_value). No oracle: the agent
is never told the fruit is toxic; it only experiences the net (post-sickness)
energy.

Contrast:
  toxin OFF -> fruit is pure high-energy food -> agent should EAT it.
  toxin ON  -> after tasting, learned value falls below plant -> agent SKIPS it.
"""

from __future__ import annotations

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent import Agent
from agents.body import BodyPlan
from world.environment import FOOD_ENERGY


def _env(acute: float) -> SimpleNamespace:
    return SimpleNamespace(
        metabolism_model="v2", food_energy_multiplier=1.0,
        food_value_learning_enabled=True, diet_learning_rate=0.4,
        diet_pickiness=0.6, diet_starvation_energy=6,
        toxin_acute_penalty=acute, toxin_damage_coeff=0.0,
        food_positions={},
    )


def _resource(kind: str):
    return SimpleNamespace(kind=kind, energy=FOOD_ENERGY[kind], source="study")


def run(acute: float, trials: int = 60):
    env = _env(acute)
    body = BodyPlan(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1)  # toxin_tolerance 0.2
    agent = Agent(agent_id=1, body=body, x=0, y=0)
    eaten = {"raw_plant": 0, "raw_fruit": 0}
    skipped = {"raw_plant": 0, "raw_fruit": 0}
    fruit_choice_by_half = [0, 0]  # fruit eaten in first / second half
    for t in range(trials):
        agent.energy = 100  # well-fed: isolate PREFERENCE from starvation
        for kind in ("raw_plant", "raw_fruit"):
            res = _resource(kind)
            env.food_positions = {(agent.x, agent.y): res}
            if agent._food_worth_eating(env):
                gross = agent._metabolic_base_energy(env, res)
                net = agent._apply_toxin(env, res, gross)
                agent._learn_food_value(env, kind, net)
                eaten[kind] += 1
                if kind == "raw_fruit":
                    fruit_choice_by_half[0 if t < trials // 2 else 1] += 1
            else:
                skipped[kind] += 1
    total_fruit = eaten["raw_fruit"] + skipped["raw_fruit"]
    return {
        "learned": {k: round(v, 1) for k, v in agent.food_value_memory.items()},
        "fruit_eaten": eaten["raw_fruit"], "fruit_skipped": skipped["raw_fruit"],
        "fruit_eat_rate": round(eaten["raw_fruit"] / total_fruit, 2),
        "fruit_eaten_first_half": fruit_choice_by_half[0],
        "fruit_eaten_second_half": fruit_choice_by_half[1],
        "plant_eaten": eaten["raw_plant"],
    }


def main() -> int:
    print("=" * 74)
    print("TOXICITY DIET STUDY - does the agent learn to avoid the toxic fruit?")
    print("well-fed agent, free choice plant vs fruit each trial (real gate + physics)")
    print("=" * 74)
    off = run(acute=0.0)
    on = run(acute=50.0)
    print("\n[control] toxin OFF - fruit is pure high-energy food")
    print(f"   learned values : {off['learned']}")
    print(f"   fruit eaten     : {off['fruit_eaten']}/{off['fruit_eaten']+off['fruit_skipped']}  (rate {off['fruit_eat_rate']})")
    print(f"   fruit 1st half {off['fruit_eaten_first_half']}  ->  2nd half {off['fruit_eaten_second_half']}")
    print("\n[toxin ON] acute penalty 50 - fruit net energy drops below plant")
    print(f"   learned values : {on['learned']}")
    print(f"   fruit eaten     : {on['fruit_eaten']}/{on['fruit_eaten']+on['fruit_skipped']}  (rate {on['fruit_eat_rate']})")
    print(f"   fruit 1st half {on['fruit_eaten_first_half']}  ->  2nd half {on['fruit_eaten_second_half']}")
    avoids = on["fruit_eat_rate"] < 0.2 and off["fruit_eat_rate"] > 0.8
    print("\n" + "=" * 74)
    print("RESULT: agent LEARNS to avoid the toxic fruit (eats it OFF, skips it ON)"
          if avoids else "RESULT: no clean avoidance separation")
    print("        note: in the FULL sim this avoidance is masked while agents are")
    print("        starving (foraging bottleneck) -> the same binding constraint.")
    print("=" * 74)
    return 0 if avoids else 1


if __name__ == "__main__":
    raise SystemExit(main())
