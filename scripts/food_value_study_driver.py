# -*- coding: utf-8 -*-
"""Fixed-tick metabolism / energy-economy / food-value-learning study driver.

Reuses the canonical metabolism gate config (locks ticks instead of wall-clock)
and exposes the study knobs (energy multipliers, low-value food, value learning,
body index, mortality) on top of scripts/run_long_emergence_watch.py.
See reports/food_value_learning_paper_2026-06-19.th.md.
"""
import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

_HERE = Path(__file__).resolve().parent          # scripts/
sys.path.insert(0, str(_HERE.parent))            # repo root (for world/agents imports)
sys.path.insert(0, str(_HERE))                   # scripts/ (for run_long_emergence_watch)
sys.stdout.reconfigure(encoding="utf-8")

import run_long_emergence_watch as R


def make_args(seed: int, model: str, max_ticks: int, output: str,
              low_value_food: float = 0.0, value_learning: bool = False,
              pickiness: float = 0.5, starvation_energy: int = 6,
              immortal: bool = True, population: int = 50,
              food_energy_mult: float = 1.0, drain_mult: float = 1.0,
              body_index: int = 37, founder_age_spread: int = 0,
              repro_safety: float = 0.66, repro_comfort: float = 0.58,
              repro_safety_streak: int = 10, repro_pair_bond_streak: int = 14,
              repro_max_age: int = 200, repro_litter_min: int = 1,
              scaffolded_actions: bool = False,
              continuous_repro: bool = False, continuous_repro_rate: float = 0.05,
              continuous_repro_local_cap: float = 6.0, world: int = 100,
              home_fidelity: bool = False, home_radius: int = 3,
              stochastic_mortality: bool = False, mortality_hazard: float = 0.03) -> SimpleNamespace:
    return SimpleNamespace(
        home_fidelity_enabled=home_fidelity,
        home_radius=home_radius,
        stochastic_mortality_enabled=stochastic_mortality,
        mortality_hazard=mortality_hazard,
        scaffolded_agent_actions_enabled=scaffolded_actions,
        scaffolded_nest_support_enabled=scaffolded_actions,
        scaffolded_social_support_enabled=scaffolded_actions,
        legacy_scaffold_nest_enabled=scaffolded_actions,
        continuous_reproduction_enabled=continuous_repro,
        continuous_repro_base_rate=continuous_repro_rate,
        continuous_repro_local_cap=continuous_repro_local_cap,
        food_energy_multiplier=food_energy_mult,
        metabolic_drain_multiplier=drain_mult,
        founder_age_spread=founder_age_spread,
        repro_safety_threshold=repro_safety,
        repro_comfort_threshold=repro_comfort,
        repro_safety_streak=repro_safety_streak,
        repro_pair_bond_streak=repro_pair_bond_streak,
        repro_max_age=repro_max_age,
        repro_litter_min=repro_litter_min,
        low_value_food_spawn_per_tick=low_value_food,
        food_value_learning_enabled=value_learning,
        diet_pickiness=pickiness,
        diet_starvation_energy=starvation_energy,
        seed=seed, body_index=body_index, initial_population=population, max_population=250,
        max_ticks=max_ticks, time_limit_seconds=999999.0, progress_every_seconds=1e9,
        evaluate_every_ticks=100_000_000, event_sample_limit=80,
        output=Path(output),
        spawn_strategy="frontier_safe_high_food", immortal=immortal,
        width=world, height=world, max_food=2000, base_food_spawn_per_tick=4,
        food_spawn_multiplier=0.70, bootstrap_food_spawn_ticks=300,
        wild_food_spawn_after_bootstrap_multiplier=0.10, natural_seed_rain_per_tick=0,
        max_plant_seeds=7600, large_animal_spawn_per_tick=2, max_large_animals=28,
        nest_support_food_chance=0.05, nest_support_spawn_chance=0.03, frontier_band=10,
        global_food_decline_per_day=0.012, minimum_global_food_multiplier=0.24,
        ambient_food_decay_chance=0.006, plant_food_decay_chance=0.0015,
        plant_seed_max_age_multiplier=4.0, plant_growth_rate_multiplier=2.0,
        sprout_biomass_loss_multiplier=0.1, germination_good_ticks_multiplier=0.5,
        plant_fruiting_interval_multiplier=0.25, plant_fruiting_growth_threshold_multiplier=0.5,
        plant_fruiting_chance_multiplier=2.0, natural_seed_drop_chance_multiplier=2.0,
        learning_revisit_radius=4, learning_revisit_min_delay_ticks=20,
        learning_revisit_max_age_ticks=2000, learning_reward_memory_limit=1200,
        phase3_min_seed_move_distance=1, phase4_patch_radius=4,
        phase4_min_patch_moved_seed_drops=3, phase4_patch_return_min_delay_ticks=20,
        phase4_patch_return_max_age_ticks=2000, phase4_min_matched_control_seeds=5,
        phase5_future_control_offsets=[10, 25, 50],
        food_signal_radius_cap=None, plant_lifecycle_food_signal_weight=1.35,
        seed_hunger_drop_bonus=0.06, seed_drop_block_critical_hunger=False,
        seed_drop_safe_window_only=False, seed_drop_safe_hunger_max=0.55,
        seed_drop_safe_fear_max=0.45, seed_drop_safe_cold_max=0.45,
        seed_drop_safe_safety_min=0.45, reward_memory_shuffle_radius=0,
        metabolism_model=model,
    )


def summarize(s: dict) -> dict:
    ec = s.get("event_counts", {})
    keys = [
        "seed_germinated", "plant_matured", "plant_fruited", "plant_lifecycle_food_consumed",
        "harvest_seed_dropped", "seed_picked", "seed_dropped",
        "gut_seed_ingested", "gut_seed_excreted", "gut_seed_killed",
    ]
    out = {k: ec.get(k, 0) for k in keys}
    out["tick"] = s.get("tick")
    out["births"] = s.get("births")
    out["population"] = s.get("population")
    out["metabolism_model"] = s.get("metabolism_model")
    scm = s.get("seed_causality_metrics", {})
    out["agent_moved_seed_count"] = scm.get("agent_moved_seed_count")
    out["agent_moved_seed_completed_chains"] = scm.get("agent_moved_seed_completed_chains")
    out["agent_moved_seed_fruited"] = scm.get("agent_moved_seed_fruited")
    out["diet_by_kind"] = s.get("diet_by_kind")
    out["agent_death_reasons"] = s.get("agent_death_reasons")
    out["energy_economy"] = s.get("energy_economy")
    out["learned_food_value"] = s.get("learned_food_value")
    out["food_spawned_by_kind"] = s.get("food_spawned_by_kind")
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=20260610)
    p.add_argument("--model", choices=["v1", "v2"], default="v1")
    p.add_argument("--ticks", type=int, default=3000)
    p.add_argument("--output", default="data/_gate_tmp")
    p.add_argument("--low-value-food", type=float, default=0.0,
                   help="raw_seed (low-value food) spawned per tick; 0 = off")
    p.add_argument("--value-learning", action="store_true", help="enable study-B food-value learning")
    p.add_argument("--pickiness", type=float, default=0.5, help="study-B diet pickiness threshold")
    p.add_argument("--starvation-energy", type=int, default=6, help="study-B eat-anything energy floor")
    p.add_argument("--mortal", action="store_true", help="immortal OFF (agents can die) for the mortality test")
    p.add_argument("--population", type=int, default=50)
    p.add_argument("--food-energy-mult", type=float, default=1.0, help="scale all food energy (energy study)")
    p.add_argument("--drain-mult", type=float, default=1.0, help="scale metabolic drain (energy study)")
    p.add_argument("--body", type=int, default=37, help="body index (37=armor0/dur10; 38=armor2/dur26)")
    p.add_argument("--founder-age-spread", type=int, default=0,
                   help="1 = spread founder ages across [ADULT_AGE, MAX_AGE) to avoid synchronized lifespan death")
    p.add_argument("--repro-safety", type=float, default=0.66, help="reproduction safety_feeling threshold (default 0.66)")
    p.add_argument("--repro-comfort", type=float, default=0.58, help="reproduction comfort threshold (default 0.58)")
    p.add_argument("--repro-safety-streak", type=int, default=10, help="ticks of safety needed (default 10)")
    p.add_argument("--repro-pair-bond-streak", type=int, default=14, help="ticks of pair-bond needed (default 14)")
    p.add_argument("--repro-max-age", type=int, default=200, help="lifespan / max age (default 200)")
    p.add_argument("--repro-litter-min", type=int, default=1, help="minimum litter size (default 1)")
    p.add_argument("--scaffolded", action="store_true",
                   help="enable the settlement/social layer (nest building, nest support, food sharing)")
    p.add_argument("--continuous-repro", action="store_true",
                   help="use logistic density-dependent stochastic reproduction instead of the gate")
    p.add_argument("--continuous-repro-rate", type=float, default=0.05, help="per-tick base reproduction rate")
    p.add_argument("--continuous-repro-cap", type=float, default=6.0, help="local crowding cap (allies)")
    p.add_argument("--world", type=int, default=100, help="world width=height (smaller = denser = more clustered)")
    p.add_argument("--home-fidelity", action="store_true", help="balanced agents return to/stay at the home anchor (clustering)")
    p.add_argument("--home-radius", type=int, default=3, help="how far from the anchor agents stay")
    p.add_argument("--stochastic-mortality", action="store_true", help="age-rising hazard death (spreads deaths) instead of hard max-age")
    p.add_argument("--mortality-hazard", type=float, default=0.03, help="base per-tick death hazard")
    p.add_argument("--dump", default=None, help="write full result JSON here for regression diff")
    a = p.parse_args()
    summary = R.run_watch(make_args(a.seed, a.model, a.ticks, a.output,
                                    low_value_food=a.low_value_food,
                                    value_learning=a.value_learning, pickiness=a.pickiness,
                                    starvation_energy=a.starvation_energy,
                                    immortal=not a.mortal, population=a.population,
                                    food_energy_mult=a.food_energy_mult, drain_mult=a.drain_mult,
                                    body_index=a.body, founder_age_spread=a.founder_age_spread,
                                    repro_safety=a.repro_safety, repro_comfort=a.repro_comfort,
                                    repro_safety_streak=a.repro_safety_streak,
                                    repro_pair_bond_streak=a.repro_pair_bond_streak,
                                    repro_max_age=a.repro_max_age, repro_litter_min=a.repro_litter_min,
                                    scaffolded_actions=a.scaffolded,
                                    continuous_repro=a.continuous_repro,
                                    continuous_repro_rate=a.continuous_repro_rate,
                                    continuous_repro_local_cap=a.continuous_repro_cap, world=a.world,
                                    home_fidelity=a.home_fidelity, home_radius=a.home_radius,
                                    stochastic_mortality=a.stochastic_mortality, mortality_hazard=a.mortality_hazard))
    if a.dump:
        Path(a.dump).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summarize(summary), ensure_ascii=False))
