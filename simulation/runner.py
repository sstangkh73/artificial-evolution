from __future__ import annotations

from collections import Counter, defaultdict
import csv
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from random import Random
import platform
import re
import subprocess
import sys

from agents.agent import ADULT_AGE, Agent, INITIAL_ENERGY, MAX_AGE
from agents.body import BodyPlan, create_trait_variant, generate_candidate_body_plans
from simulation.publication_artifacts import write_publication_artifacts
from simulation.research_artifacts import write_research_artifacts
from visualization.dashboard import build_dashboard_artifacts
from world.environment import Environment, ZONE_SAFE_HIGH_FOOD

TARGET_SURVIVORS = 50
TARGET_BODY_TYPES = 50
INITIAL_POPULATION = 12
MAX_POPULATION = 200
MAX_TICKS = 5000
MAX_BODY_CANDIDATES_TO_TEST = 250
FOUNDER_START_AGE = ADULT_AGE + 6
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
EXPERIMENTS_DIR = DATA_DIR / "experiments"
HISTORY_PATH = DATA_DIR / "experiment_history.json"
DASHBOARDS_DIR = DATA_DIR / "dashboards"
RESEARCH_RUNS_DIR = DATA_DIR / "research_runs"
PUBLICATION_PACKAGES_DIR = DATA_DIR / "publication_packages"


@dataclass
class ExperimentResult:
    body_name: str
    body_design: str
    body_stats: str
    target_survivors: int
    achieved_survivors: int
    peak_population: int
    total_births: int
    matured_children: int
    final_tick: int
    first_birth_tick: int | None
    first_birth_day: int | None
    first_matured_child_tick: int | None
    first_matured_child_day: int | None
    completed_lineages: int
    average_age: float
    average_food_eaten: float
    average_children: float
    food_type_totals: dict[str, int]
    stored_food_total: int
    gathered_material_totals: dict[str, int]
    emergent_technology_totals: dict[str, int]
    death_reasons: dict[str, int]
    reached_target: bool
    social_events: list[str]
    first_technology_tick: int | None = None
    first_technology_day: int | None = None
    first_technology_name: str | None = None
    population_extinct: bool = False
    target_generation_reached: bool = False
    target_generation_tick: int | None = None
    dashboard_path: str | None = None
    telemetry_path: str | None = None
    research_manifest_path: str | None = None


@dataclass
class ExperimentRun:
    experiment_number: int
    change_note: str
    started_at: str
    log_lines: list[str]


@dataclass
class DistinctSurvivorRecord:
    body_index: int
    body_name: str
    body_design: str
    body_stats: str
    first_found_seed: int
    achieved_survivors: int
    total_births: int
    matured_children: int
    first_birth_day: int | None
    first_matured_child_day: int | None


@dataclass
class LineageBodyRecord:
    body_index: int
    body_name: str
    body_design: str
    body_stats: str
    first_found_seed: int
    founder_population: int
    max_population: int
    max_ticks: int
    achieved_survivors: int
    total_births: int
    matured_children: int
    first_birth_day: int | None
    first_matured_child_day: int | None


@dataclass
class FirstToolEmergenceRecord:
    seed: int
    body_index: int
    body_name: str
    body_design: str
    first_technology_tick: int | None
    first_technology_day: int | None
    first_technology_name: str | None
    total_births: int
    matured_children: int
    peak_population: int
    stored_food_total: int
    reached_target: bool


@dataclass
class SexedSurvivalResult:
    seed: int
    body_index: int
    body_name: str
    body_design: str
    final_tick: int
    peak_population: int
    total_births: int
    matured_children: int
    population_extinct: bool
    target_generation_reached: bool
    target_generation_tick: int | None
    first_birth_tick: int | None
    dashboard_path: str | None


@dataclass
class SexedSearchRecord:
    body_index: int
    body_name: str
    body_design: str
    body_stats: str
    seed: int
    final_tick: int
    peak_population: int
    total_births: int
    matured_children: int
    population_extinct: bool
    target_generation_reached: bool
    target_generation_tick: int | None


@dataclass
class PublicationConditionSpec:
    condition_id: str
    label: str
    question: str
    body_index: int
    body_name: str
    body_design: str
    body_stats: str
    initial_population: int
    max_population: int
    max_ticks: int
    founder_mode: str
    founder_sexes: list[str] | None
    stop_on_generation_adult: int | None
    env_kwargs: dict[str, object] | None
    spawn_strategy: str


def run_prototype_experiment(seed: int = 7, change_note: str = "Manual test run") -> list[ExperimentResult]:
    rng = Random(seed)
    results: list[ExperimentResult] = []
    survivors: list[ExperimentResult] = []
    candidate_bodies = generate_candidate_body_plans()
    experiment = start_experiment_run(change_note)

    log(experiment, "Artificial Evolution Survivor Search")
    log(experiment, "=" * 40)
    log(
        experiment,
        f"Experiment #{experiment.experiment_number}",
    )
    log(
        experiment,
        f"Change note: {change_note}",
    )
    log(
        experiment,
        f"Started at: {experiment.started_at}",
    )
    log(
        experiment,
        f"MAX_AGE={MAX_AGE}, TARGET_SURVIVORS={TARGET_SURVIVORS}, "
        f"TARGET_BODY_TYPES={TARGET_BODY_TYPES}, INITIAL_ENERGY={INITIAL_ENERGY}"
    )

    for index, body in enumerate(candidate_bodies[:MAX_BODY_CANDIDATES_TO_TEST], start=1):
        result = run_single_body_trial(rng, body_index=index, body=body)
        results.append(result)

        log(experiment, f"Body {index} design: {body.short_description}")
        log(experiment, f"Body {index} stats: {body.stats_description}")
        log(
            experiment,
            f"Body {index}: achieved={result.achieved_survivors}/{result.target_survivors}, "
            f"peak_pop={result.peak_population}, births={result.total_births}, "
            f"matured_children={result.matured_children}, "
            f"first_birth_day={result.first_birth_day}, "
            f"first_matured_day={result.first_matured_child_day}, "
            f"avg_age={result.average_age:.1f}, avg_food={result.average_food_eaten:.1f}, "
            f"avg_children={result.average_children:.1f}, foods={result.food_type_totals}, "
            f"stored={result.stored_food_total}, materials={result.gathered_material_totals}, "
            f"technologies={result.emergent_technology_totals}, "
            f"deaths={result.death_reasons}"
        )
        for social_event in result.social_events[:10]:
            log(experiment, f"  social: {social_event}")

        if result.reached_target:
            survivors.append(result)
            log(experiment, f"Accepted survivor body {len(survivors)}/{TARGET_BODY_TYPES}")

        if len(survivors) >= TARGET_BODY_TYPES:
            break

    save_results(results, survivors, seed=seed, experiment=experiment)
    log(experiment, "-" * 40)
    log(experiment, f"Qualified body types: {len(survivors)}/{TARGET_BODY_TYPES}")
    if survivors:
        log(experiment, f"Top survivor body: {survivors[0].body_name}")
    finalize_experiment_run(experiment, results, survivors, seed)
    return survivors


def run_distinct_survivor_search(
    start_seed: int = 7,
    change_note: str = "Distinct survivor search",
    target_body_types: int = TARGET_BODY_TYPES,
    max_seed_rounds: int = 50,
    max_stagnation_rounds: int = 10,
) -> list[DistinctSurvivorRecord]:
    candidate_bodies = generate_candidate_body_plans()
    experiment = start_experiment_run(change_note)
    distinct_survivors: dict[int, DistinctSurvivorRecord] = {}
    seed_summaries: list[dict[str, int]] = []
    stagnation_rounds = 0

    log(experiment, "Artificial Evolution Distinct Survivor Search")
    log(experiment, "=" * 46)
    log(experiment, f"Experiment #{experiment.experiment_number}")
    log(experiment, f"Change note: {change_note}")
    log(experiment, f"Started at: {experiment.started_at}")
    log(
        experiment,
        f"Searching for {target_body_types} distinct survivor body types "
        f"across up to {max_seed_rounds} seeds",
    )

    all_results: list[ExperimentResult] = []

    for round_index in range(max_seed_rounds):
        seed = start_seed + round_index
        rng = Random(seed)
        before_count = len(distinct_survivors)
        qualifying_this_seed = 0

        log(experiment, "-" * 46)
        log(experiment, f"Seed {seed} scan started")

        for body_index, body in enumerate(candidate_bodies, start=1):
            result = run_single_body_trial(rng, body_index=body_index, body=body)
            all_results.append(result)

            if not result.reached_target:
                continue

            qualifying_this_seed += 1
            if body_index not in distinct_survivors:
                distinct_survivors[body_index] = DistinctSurvivorRecord(
                    body_index=body_index,
                    body_name=result.body_name,
                    body_design=result.body_design,
                    body_stats=result.body_stats,
                    first_found_seed=seed,
                    achieved_survivors=result.achieved_survivors,
                    total_births=result.total_births,
                    matured_children=result.matured_children,
                    first_birth_day=result.first_birth_day,
                    first_matured_child_day=result.first_matured_child_day,
                )
                log(
                    experiment,
                    f"New survivor body found: {result.body_name} | {result.body_design} | "
                    f"seed={seed} | births={result.total_births} | "
                    f"matured_children={result.matured_children} | "
                    f"first_birth_day={result.first_birth_day}",
                )

                if len(distinct_survivors) >= target_body_types:
                    break

        new_this_seed = len(distinct_survivors) - before_count
        if new_this_seed == 0:
            stagnation_rounds += 1
        else:
            stagnation_rounds = 0

        seed_summaries.append(
            {
                "seed": seed,
                "qualifying_bodies": qualifying_this_seed,
                "new_distinct_bodies": new_this_seed,
                "total_distinct_bodies": len(distinct_survivors),
            }
        )
        log(
            experiment,
            f"Seed {seed} complete: qualifying={qualifying_this_seed}, "
            f"new_distinct={new_this_seed}, total_distinct={len(distinct_survivors)}",
        )

        if len(distinct_survivors) >= target_body_types:
            log(experiment, f"Target reached: {len(distinct_survivors)}/{target_body_types}")
            break

        if stagnation_rounds >= max_stagnation_rounds:
            log(
                experiment,
                f"Stopped after {stagnation_rounds} stagnant seeds with no new survivor bodies",
            )
            break

    _save_distinct_survivor_search(
        experiment=experiment,
        start_seed=start_seed,
        target_body_types=target_body_types,
        max_seed_rounds=max_seed_rounds,
        max_stagnation_rounds=max_stagnation_rounds,
        records=list(distinct_survivors.values()),
        seed_summaries=seed_summaries,
    )
    finalize_experiment_run(
        experiment,
        all_results,
        [
            ExperimentResult(
                body_name=record.body_name,
                body_design=record.body_design,
                body_stats=record.body_stats,
                target_survivors=TARGET_SURVIVORS,
                achieved_survivors=record.achieved_survivors,
                peak_population=0,
                total_births=record.total_births,
                matured_children=record.matured_children,
                final_tick=0,
                first_birth_tick=None,
                first_birth_day=record.first_birth_day,
                first_matured_child_tick=None,
                first_matured_child_day=record.first_matured_child_day,
                completed_lineages=0,
                average_age=0.0,
                average_food_eaten=0.0,
                average_children=0.0,
                food_type_totals={},
                stored_food_total=0,
                gathered_material_totals={},
                emergent_technology_totals={},
                death_reasons={},
                reached_target=True,
                social_events=[],
            )
            for record in distinct_survivors.values()
        ],
        start_seed,
    )
    return list(distinct_survivors.values())


def run_massive_lineage_search(
    start_seed: int = 7,
    change_note: str = "Massive lineage search",
    target_body_types: int = TARGET_BODY_TYPES,
    founder_population_steps: tuple[int, ...] = (12, 24, 48, 96, 192),
    max_population_multiplier: int = 20,
    max_ticks: int = 15000,
    max_seed_rounds: int = 20,
) -> list[LineageBodyRecord]:
    candidate_bodies = generate_candidate_body_plans()
    experiment = start_experiment_run(change_note)
    lineage_bodies: dict[int, LineageBodyRecord] = {}
    all_results: list[ExperimentResult] = []

    log(experiment, "Artificial Evolution Massive Lineage Search")
    log(experiment, "=" * 46)
    log(experiment, f"Experiment #{experiment.experiment_number}")
    log(experiment, f"Change note: {change_note}")
    log(experiment, f"Started at: {experiment.started_at}")
    log(
        experiment,
        f"Searching for {target_body_types} body types that survive and produce mature offspring",
    )
    log(
        experiment,
        f"Founder steps={founder_population_steps}, max_population_multiplier={max_population_multiplier}, "
        f"max_ticks={max_ticks}, max_seed_rounds={max_seed_rounds}",
    )

    for body_index, body in enumerate(candidate_bodies, start=1):
        if len(lineage_bodies) >= target_body_types:
            break

        found_success = False
        for seed_offset in range(max_seed_rounds):
            seed = start_seed + seed_offset
            for founder_population in founder_population_steps:
                trial_rng = Random((seed * 100000) + (body_index * 100) + founder_population)
                result = run_single_body_trial(
                    trial_rng,
                    body_index=body_index,
                    body=body,
                    initial_population=founder_population,
                    max_population=max(founder_population * max_population_multiplier, 200),
                    max_ticks=max_ticks,
                )
                all_results.append(result)
                success = (
                    result.achieved_survivors >= 1
                    and result.total_births >= 1
                    and result.matured_children >= 1
                )
                if not success:
                    continue

                lineage_bodies[body_index] = LineageBodyRecord(
                    body_index=body_index,
                    body_name=result.body_name,
                    body_design=result.body_design,
                    body_stats=result.body_stats,
                    first_found_seed=seed,
                    founder_population=founder_population,
                    max_population=max(founder_population * max_population_multiplier, 200),
                    max_ticks=max_ticks,
                    achieved_survivors=result.achieved_survivors,
                    total_births=result.total_births,
                    matured_children=result.matured_children,
                    first_birth_day=result.first_birth_day,
                    first_matured_child_day=result.first_matured_child_day,
                )
                log(
                    experiment,
                    f"Lineage body {len(lineage_bodies)}/{target_body_types}: {result.body_name} | "
                    f"{result.body_design} | seed={seed} | founders={founder_population} | "
                    f"births={result.total_births} | matured_children={result.matured_children} | "
                    f"achieved={result.achieved_survivors}",
                )
                found_success = True
                break
            if found_success:
                break

        if not found_success and body_index % 25 == 0:
            log(
                experiment,
                f"Scanned {body_index} bodies, found {len(lineage_bodies)} lineage-capable body types so far",
            )

    if len(lineage_bodies) < target_body_types and lineage_bodies:
        log(
            experiment,
            f"Primary scan found only {len(lineage_bodies)} bodies. Exploring trait variants around successful niches.",
        )
        successful_templates = [
            candidate_bodies[record.body_index - 1]
            for record in lineage_bodies.values()
            if 0 < record.body_index <= len(candidate_bodies)
        ]
        variant_bodies = _generate_lineage_variants(successful_templates)
        next_body_index = len(candidate_bodies) + 1

        for variant in variant_bodies:
            if len(lineage_bodies) >= target_body_types:
                break
            found_success = False
            for seed_offset in range(max_seed_rounds):
                seed = start_seed + seed_offset
                for founder_population in founder_population_steps:
                    trial_rng = Random((seed * 100000) + (next_body_index * 100) + founder_population)
                    result = run_single_body_trial(
                        trial_rng,
                        body_index=next_body_index,
                        body=variant,
                        initial_population=founder_population,
                        max_population=max(founder_population * max_population_multiplier, 200),
                        max_ticks=max_ticks,
                    )
                    all_results.append(result)
                    success = (
                        result.achieved_survivors >= 1
                        and result.total_births >= 1
                        and result.matured_children >= 1
                    )
                    if not success:
                        continue

                    lineage_bodies[next_body_index] = LineageBodyRecord(
                        body_index=next_body_index,
                        body_name=result.body_name,
                        body_design=result.body_design,
                        body_stats=result.body_stats,
                        first_found_seed=seed,
                        founder_population=founder_population,
                        max_population=max(founder_population * max_population_multiplier, 200),
                        max_ticks=max_ticks,
                        achieved_survivors=result.achieved_survivors,
                        total_births=result.total_births,
                        matured_children=result.matured_children,
                        first_birth_day=result.first_birth_day,
                        first_matured_child_day=result.first_matured_child_day,
                    )
                    log(
                        experiment,
                        f"Variant lineage body {len(lineage_bodies)}/{target_body_types}: {result.body_name} | "
                        f"{result.body_design} | seed={seed} | founders={founder_population} | "
                        f"births={result.total_births} | matured_children={result.matured_children} | "
                        f"achieved={result.achieved_survivors}",
                    )
                    found_success = True
                    break
                if found_success:
                    break
            next_body_index += 1

    _save_massive_lineage_search(
        experiment=experiment,
        start_seed=start_seed,
        target_body_types=target_body_types,
        founder_population_steps=founder_population_steps,
        max_population_multiplier=max_population_multiplier,
        max_ticks=max_ticks,
        max_seed_rounds=max_seed_rounds,
        records=list(lineage_bodies.values()),
    )
    finalize_experiment_run(
        experiment,
        all_results,
        [
            ExperimentResult(
                body_name=record.body_name,
                body_design=record.body_design,
                body_stats=record.body_stats,
                target_survivors=TARGET_SURVIVORS,
                achieved_survivors=record.achieved_survivors,
                peak_population=record.max_population,
                total_births=record.total_births,
                matured_children=record.matured_children,
                final_tick=record.max_ticks,
                first_birth_tick=None,
                first_birth_day=record.first_birth_day,
                first_matured_child_tick=None,
                first_matured_child_day=record.first_matured_child_day,
                completed_lineages=record.achieved_survivors,
                average_age=0.0,
                average_food_eaten=0.0,
                average_children=0.0,
                food_type_totals={},
                stored_food_total=0,
                gathered_material_totals={},
                emergent_technology_totals={},
                death_reasons={},
                reached_target=True,
                social_events=[],
            )
            for record in lineage_bodies.values()
        ],
        start_seed,
    )
    return list(lineage_bodies.values())


def _generate_lineage_variants(successful_templates: list[BodyPlan]) -> list[BodyPlan]:
    variants: list[BodyPlan] = []
    variant_specs = [
        ("stable_memory", dict(memory_delta=0.10, planning_delta=0.06, cooperation_delta=0.04)),
        ("settler_plus", dict(parenting_delta=0.10, cooperation_delta=0.08, metabolism_delta=-0.04)),
        ("agile_planner", dict(curiosity_delta=0.08, planning_delta=0.10, fear_delta=-0.06)),
        ("care_heavy", dict(parenting_delta=0.16, reproduction_investment_delta=0.12, fear_delta=0.04)),
        ("social_dense", dict(cooperation_delta=0.14, memory_delta=0.08, metabolism_delta=0.02)),
        ("herbivore_efficient", dict(plant_efficiency_delta=0.14, metabolism_delta=-0.06, fear_delta=0.04)),
        ("omnivore_balanced", dict(plant_efficiency_delta=0.06, meat_efficiency_delta=0.06, planning_delta=0.04)),
        ("risk_scout", dict(curiosity_delta=0.16, aggression_delta=0.06, fear_delta=-0.10)),
        ("patient_lineage", dict(reproduction_drive_delta=-0.06, reproduction_investment_delta=0.16, memory_delta=0.06)),
        ("dense_storage", dict(planning_delta=0.12, cooperation_delta=0.10, parenting_delta=0.06)),
        ("cool_metabolism", dict(metabolism_delta=-0.10, memory_delta=0.04, plant_efficiency_delta=0.08)),
        ("guarded_home", dict(fear_delta=0.10, parenting_delta=0.08, cooperation_delta=0.06)),
        ("broad_memory", dict(brain_capacity_delta=0.5, memory_delta=0.14, planning_delta=0.06)),
        ("tribal_core", dict(cooperation_delta=0.16, parenting_delta=0.10, aggression_delta=-0.04)),
        ("resource_saver", dict(metabolism_delta=-0.08, reproduction_drive_delta=-0.04, plant_efficiency_delta=0.10)),
        ("forager_chain", dict(memory_delta=0.12, plant_efficiency_delta=0.12, curiosity_delta=0.04)),
        ("expander", dict(curiosity_delta=0.12, cooperation_delta=0.06, reproduction_drive_delta=0.04)),
        ("child_guard", dict(parenting_delta=0.18, fear_delta=0.06, aggression_delta=-0.06)),
        ("camp_builder", dict(planning_delta=0.14, parenting_delta=0.06, metabolism_delta=-0.02)),
        ("slow_stable", dict(metabolism_delta=-0.12, fear_delta=0.08, reproduction_investment_delta=0.10)),
        ("adaptive_omnivore", dict(plant_efficiency_delta=0.08, meat_efficiency_delta=0.08, memory_delta=0.04)),
        ("home_network", dict(cooperation_delta=0.12, memory_delta=0.10, planning_delta=0.08)),
        ("secure_reproducer", dict(reproduction_drive_delta=0.02, reproduction_investment_delta=0.14, parenting_delta=0.08)),
        ("safe_explorer", dict(curiosity_delta=0.06, fear_delta=0.06, planning_delta=0.06)),
    ]
    for template in successful_templates:
        for variant_name, deltas in variant_specs:
            variants.append(create_trait_variant(template, variant_name, **deltas))
    return variants


def run_visual_dashboard_demo(
    seed: int = 7,
    change_note: str = "Visual dashboard demo",
    max_ticks: int = 800,
    snapshot_interval: int = 10,
) -> ExperimentResult:
    experiment = start_experiment_run(change_note)
    rng = Random(seed)
    body = BodyPlan.from_archetype(0, 0, 1, 3, "social_planner")

    log(experiment, "Artificial Evolution Visual Dashboard Demo")
    log(experiment, "=" * 44)
    log(experiment, f"Experiment #{experiment.experiment_number}")
    log(experiment, f"Change note: {change_note}")
    log(experiment, f"Started at: {experiment.started_at}")
    log(experiment, f"Seed: {seed} | max_ticks={max_ticks} | snapshot_interval={snapshot_interval}")
    log(experiment, f"Demo body: {body.short_description}")

    result = run_single_body_trial(
        rng,
        body_index=1,
        body=body,
        max_ticks=max_ticks,
        capture_dashboard=True,
        dashboard_group="dashboard_mode",
        dashboard_run_name=f"experiment_{experiment.experiment_number:03d}_dashboard",
        dashboard_seed=seed,
        dashboard_title="Visual Dashboard Demo",
        snapshot_interval=snapshot_interval,
    )

    if result.dashboard_path is not None:
        log(experiment, f"Dashboard: {result.dashboard_path}")
    if result.telemetry_path is not None:
        log(experiment, f"Telemetry: {result.telemetry_path}")

    finalize_experiment_run(experiment, [result], [result], seed)
    return result


def run_paper_data_capture(
    seed: int = 7,
    change_note: str = "Research-grade paper capture",
    body_index: int = 8,
    max_ticks: int = 2000,
    snapshot_interval: int = 10,
) -> ExperimentResult:
    experiment = start_experiment_run(change_note)
    candidate_bodies = generate_candidate_body_plans()
    resolved_body_index = max(1, min(body_index, len(candidate_bodies)))
    body = candidate_bodies[resolved_body_index - 1]
    rng = Random(seed)

    log(experiment, "Artificial Evolution Paper Data Capture")
    log(experiment, "=" * 43)
    log(experiment, f"Experiment #{experiment.experiment_number}")
    log(experiment, f"Change note: {change_note}")
    log(experiment, f"Started at: {experiment.started_at}")
    log(
        experiment,
        f"Seed: {seed} | body_index={resolved_body_index} | max_ticks={max_ticks} | "
        f"snapshot_interval={snapshot_interval}",
    )
    log(experiment, f"Body: {body.short_description}")

    result = run_single_body_trial(
        rng,
        body_index=resolved_body_index,
        body=body,
        max_ticks=max_ticks,
        capture_dashboard=True,
        dashboard_group="paper_mode",
        dashboard_run_name=f"experiment_{experiment.experiment_number:03d}_paper_dashboard",
        dashboard_seed=seed,
        dashboard_title="Paper Data Capture",
        snapshot_interval=snapshot_interval,
        capture_research_data=True,
        research_run_name=f"experiment_{experiment.experiment_number:03d}_paper_capture",
        research_seed=seed,
        research_change_note=change_note,
    )

    if result.research_manifest_path is not None:
        log(experiment, f"Research manifest: {result.research_manifest_path}")
    if result.dashboard_path is not None:
        log(experiment, f"Dashboard: {result.dashboard_path}")
    if result.telemetry_path is not None:
        log(experiment, f"Telemetry: {result.telemetry_path}")

    finalize_experiment_run(experiment, [result], [result], seed)
    return result


def run_publication_batch_capture(
    start_seed: int = 7,
    seed_count: int = 6,
    change_note: str = "Publication-grade batch capture",
    max_ticks: int = 1200,
    snapshot_interval: int = 10,
) -> str:
    candidate_bodies = generate_candidate_body_plans()
    conditions = _publication_conditions(candidate_bodies, max_ticks=max_ticks)
    return _run_publication_conditions_batch(
        conditions=conditions,
        start_seed=start_seed,
        seed_count=seed_count,
        change_note=change_note,
        snapshot_interval=snapshot_interval,
        batch_label="publication_batch",
        headline="Artificial Evolution Publication Batch Capture",
    )


def run_robustness_sweep_capture(
    start_seed: int = 7,
    seed_count: int = 4,
    change_note: str = "Robustness sweep for sexed survival and technology emergence",
    max_ticks: int = 1600,
    snapshot_interval: int = 20,
) -> str:
    candidate_bodies = generate_candidate_body_plans()
    conditions = _robustness_conditions(candidate_bodies, max_ticks=max_ticks)
    return _run_publication_conditions_batch(
        conditions=conditions,
        start_seed=start_seed,
        seed_count=seed_count,
        change_note=change_note,
        snapshot_interval=snapshot_interval,
        batch_label="robustness_sweep",
        headline="Artificial Evolution Robustness Sweep Capture",
    )


def run_world_discovery_phase_capture(
    start_seed: int = 7,
    seed_count: int = 4,
    change_note: str = "Phase-separated world discovery study",
    max_ticks: int = 1600,
    snapshot_interval: int = 20,
) -> str:
    candidate_bodies = generate_candidate_body_plans()
    conditions = _world_discovery_conditions(candidate_bodies, max_ticks=max_ticks)
    return _run_publication_conditions_batch(
        conditions=conditions,
        start_seed=start_seed,
        seed_count=seed_count,
        change_note=change_note,
        snapshot_interval=snapshot_interval,
        batch_label="world_discovery_phase",
        headline="Artificial Evolution World Discovery Phase Capture",
    )


def run_immortal_discovery_capture(
    seed: int = 7,
    change_note: str = "Immortal open-ended discovery run",
    body_index: int = 8,
    max_ticks: int = 8000,
    snapshot_interval: int = 25,
) -> ExperimentResult:
    experiment = start_experiment_run(change_note)
    candidate_bodies = generate_candidate_body_plans()
    resolved_body_index = max(1, min(body_index, len(candidate_bodies)))
    body = candidate_bodies[resolved_body_index - 1]
    founder_sexes = ["male"] * 25 + ["female"] * 25
    rng = Random(seed)

    log(experiment, "Artificial Evolution Immortal Discovery Run")
    log(experiment, "=" * 49)
    log(experiment, f"Experiment #{experiment.experiment_number}")
    log(experiment, f"Change note: {change_note}")
    log(experiment, f"Started at: {experiment.started_at}")
    log(
        experiment,
        f"Seed: {seed} | body_index={resolved_body_index} | founders=50 | "
        f"immortal=True | max_ticks={max_ticks} | snapshot_interval={snapshot_interval}",
    )
    log(experiment, f"Body: {body.short_description}")

    result = run_single_body_trial(
        rng,
        body_index=resolved_body_index,
        body=body,
        initial_population=50,
        max_population=250,
        max_ticks=max_ticks,
        capture_dashboard=True,
        dashboard_group="immortal_discovery",
        dashboard_run_name=f"experiment_{experiment.experiment_number:03d}_immortal_discovery",
        dashboard_seed=seed,
        dashboard_title="Immortal Discovery Run",
        snapshot_interval=snapshot_interval,
        capture_research_data=True,
        research_run_name=f"experiment_{experiment.experiment_number:03d}_immortal_discovery",
        research_seed=seed,
        research_change_note=change_note,
        research_condition_id="immortal_discovery_50_founders",
        research_condition_label="Immortal 50-founder open-ended discovery",
        research_question=(
            "What changes emerge when 50 immortal reproductive agents are left "
            "unsupervised in the world with no added teaching intervention?"
        ),
        founder_sexes=founder_sexes,
        stop_on_target_survivors=False,
        immortal_agents=True,
    )

    if result.research_manifest_path is not None:
        log(experiment, f"Research manifest: {result.research_manifest_path}")
    if result.dashboard_path is not None:
        log(experiment, f"Dashboard: {result.dashboard_path}")
    if result.telemetry_path is not None:
        log(experiment, f"Telemetry: {result.telemetry_path}")

    finalize_experiment_run(experiment, [result], [result], seed)
    return result


def _run_publication_conditions_batch(
    *,
    conditions: list[PublicationConditionSpec],
    start_seed: int,
    seed_count: int,
    change_note: str,
    snapshot_interval: int,
    batch_label: str,
    headline: str,
) -> str:
    experiment = start_experiment_run(change_note)
    candidate_bodies = generate_candidate_body_plans()
    all_results: list[ExperimentResult] = []
    replicate_rows: list[dict[str, object]] = []
    tick_metrics_long: list[dict[str, object]] = []
    failure_reason_rows: list[dict[str, object]] = []
    lineage_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []

    log(experiment, headline)
    log(experiment, "=" * max(49, len(headline)))
    log(experiment, f"Experiment #{experiment.experiment_number}")
    log(experiment, f"Change note: {change_note}")
    log(experiment, f"Started at: {experiment.started_at}")
    max_ticks = max(condition.max_ticks for condition in conditions)
    log(experiment, f"Conditions={len(conditions)} | seeds_per_condition={seed_count} | max_ticks={max_ticks}")

    for condition in conditions:
        log(experiment, "-" * 49)
        log(
            experiment,
            f"Condition {condition.condition_id} | body={condition.body_name} | "
            f"initial_population={condition.initial_population} | founder_mode={condition.founder_mode}",
        )
        for seed_offset in range(seed_count):
            seed = start_seed + seed_offset
            rng = Random(seed)
            run_name = (
                f"experiment_{experiment.experiment_number:03d}_"
                f"{condition.condition_id}_seed_{seed}"
            )
            result = run_single_body_trial(
                rng,
                body_index=condition.body_index,
                body=candidate_bodies[condition.body_index - 1],
                initial_population=condition.initial_population,
                max_population=condition.max_population,
                max_ticks=condition.max_ticks,
                capture_dashboard=True,
                dashboard_group="publication_batch",
                dashboard_run_name=run_name,
                dashboard_seed=seed,
                dashboard_title=f"Publication Batch {condition.condition_id}",
                snapshot_interval=snapshot_interval,
                capture_research_data=True,
                research_run_name=run_name,
                research_seed=seed,
                research_change_note=f"{change_note} | {condition.condition_id}",
                research_condition_id=condition.condition_id,
                research_condition_label=condition.label,
                research_question=condition.question,
                env_kwargs=condition.env_kwargs,
                spawn_strategy=condition.spawn_strategy,
                founder_sexes=condition.founder_sexes,
                stop_on_generation_adult=condition.stop_on_generation_adult,
            )
            all_results.append(result)
            log(
                experiment,
                f"  seed={seed} | final_tick={result.final_tick} | extinct={result.population_extinct} | "
                f"gen3={result.target_generation_reached} | tech={result.first_technology_tick}",
            )

            if result.research_manifest_path is None:
                continue
            bundle = _load_research_manifest_bundle(Path(result.research_manifest_path))
            metadata = bundle["metadata"]
            summary = bundle["summary"]
            tick_rows = bundle["tick_metrics"]
            agent_rows = bundle["agent_outcomes"]
            lineage_bundle_rows = bundle["lineages"]
            events = bundle["events"]

            final_snapshot = tick_rows[-1] if tick_rows else {}
            reproduce_fail_count = sum(1 for event in events if event.get("event_type") == "repro_fail")
            max_generation_observed = max((int(agent.get("generation", 0)) for agent in agent_rows), default=0)
            learning_proxy = _agent_learning_proxy_summary(agent_rows)
            replicate_id = f"{condition.condition_id}_seed_{seed}"
            replicate_rows.append(
                {
                    "condition_id": condition.condition_id,
                    "condition_label": condition.label,
                    "replicate_id": replicate_id,
                    "seed": seed,
                    "body_index": condition.body_index,
                    "body_name": condition.body_name,
                    "body_design": condition.body_design,
                    "initial_population": condition.initial_population,
                    "max_population": condition.max_population,
                    "max_ticks_requested": condition.max_ticks,
                    "final_tick": summary["final_tick"] if "final_tick" in summary else metadata["final_tick"],
                    "population_extinct": result.population_extinct,
                    "target_generation_reached": result.target_generation_reached,
                    "target_generation_tick": result.target_generation_tick,
                    "first_birth_tick": result.first_birth_tick,
                    "first_matured_child_tick": result.first_matured_child_tick,
                    "first_technology_tick": result.first_technology_tick,
                    "first_technology_name": result.first_technology_name,
                    "peak_population": result.peak_population,
                    "total_births": result.total_births,
                    "matured_children": result.matured_children,
                    "stored_food_total": result.stored_food_total,
                    "average_age": round(result.average_age, 3),
                    "average_food_eaten": round(result.average_food_eaten, 3),
                    "average_children": round(result.average_children, 3),
                    "completed_lineages": result.completed_lineages,
                    "final_population": final_snapshot.get("population", 0),
                    "final_female": final_snapshot.get("female", 0),
                    "final_male": final_snapshot.get("male", 0),
                    "max_generation_observed": max_generation_observed,
                    "reproduction_failure_events": reproduce_fail_count,
                    "mean_agent_memory_sites": learning_proxy["mean_agent_memory_sites"],
                    "max_agent_memory_sites": learning_proxy["max_agent_memory_sites"],
                    "social_contact_rate": learning_proxy["social_contact_rate"],
                    "object_experiment_agent_rate": learning_proxy["object_experiment_agent_rate"],
                    "mean_friend_count": learning_proxy["mean_friend_count"],
                    "manifest_path": result.research_manifest_path,
                    "dashboard_path": result.dashboard_path,
                    "telemetry_path": result.telemetry_path,
                }
            )

            for row in tick_rows:
                normalized = dict(row)
                normalized["condition_id"] = condition.condition_id
                normalized["condition_label"] = condition.label
                normalized["replicate_id"] = replicate_id
                normalized["seed"] = seed
                tick_metrics_long.append(normalized)

            for event in events:
                enriched_event = dict(event)
                enriched_event["condition_id"] = condition.condition_id
                enriched_event["replicate_id"] = replicate_id
                enriched_event["seed"] = seed
                event_rows.append(enriched_event)
                if event.get("event_type") == "repro_fail":
                    failure_reason_rows.append(
                        {
                            "condition_id": condition.condition_id,
                            "replicate_id": replicate_id,
                            "seed": seed,
                            "tick": event.get("tick"),
                            "day": event.get("day"),
                            "details": event.get("details"),
                            "raw_text": event.get("raw_text"),
                        }
                    )

            for lineage in lineage_bundle_rows:
                enriched_lineage = dict(lineage)
                enriched_lineage["condition_id"] = condition.condition_id
                enriched_lineage["replicate_id"] = replicate_id
                enriched_lineage["seed"] = seed
                lineage_rows.append(enriched_lineage)

    condition_rows = [
        {
            "condition_id": condition.condition_id,
            "label": condition.label,
            "question": condition.question,
            "body_index": condition.body_index,
            "body_name": condition.body_name,
            "body_design": condition.body_design,
            "body_stats": condition.body_stats,
            "initial_population": condition.initial_population,
            "max_population": condition.max_population,
            "max_ticks": condition.max_ticks,
            "founder_mode": condition.founder_mode,
            "stop_on_generation_adult": condition.stop_on_generation_adult,
            "spawn_strategy": condition.spawn_strategy,
            "env_kwargs": condition.env_kwargs or {},
        }
        for condition in conditions
    ]

    package_dir = PUBLICATION_PACKAGES_DIR / f"experiment_{experiment.experiment_number:03d}_{batch_label}"
    manifest = write_publication_artifacts(
        package_dir,
        {
            "conditions": condition_rows,
            "replicates": replicate_rows,
            "tick_metrics_long": tick_metrics_long,
            "failure_reasons": failure_reason_rows,
            "lineage_rows": lineage_rows,
            "event_rows": event_rows,
            "runtime_provenance": {
                "experiment_number": experiment.experiment_number,
                "started_at": experiment.started_at,
                "change_note": change_note,
                "platform": platform.platform(),
                "python_version": sys.version,
                "git_revision": _git_revision(),
                "seed_start": start_seed,
                "seed_count_per_condition": seed_count,
            },
        },
    )
    log(experiment, f"Publication manifest: {manifest['publication_manifest']}")
    finalize_experiment_run(
        experiment,
        all_results,
        [result for result in all_results if result.target_generation_reached or result.first_technology_tick is not None],
        start_seed,
    )
    return manifest["publication_manifest"]


def _publication_conditions(candidate_bodies: list[BodyPlan], max_ticks: int) -> list[PublicationConditionSpec]:
    sexed_founders = ["male"] * 25 + ["female"] * 25
    technology_pressure_env = {
        "max_food": 120,
        "base_food_spawn_per_tick": 5,
        "max_large_animals": 36,
        "large_animal_spawn_per_tick": 3,
        "food_spawn_multiplier": 0.9,
        "nest_support_food_chance": 0.10,
        "nest_support_spawn_chance": 0.08,
        "safe_area_stone_chance": 0.03,
        "frontier_stone_bonus": 0.18,
        "frontier_band": 6,
    }
    selected_indices = [8, 14]
    conditions: list[PublicationConditionSpec] = []
    for body_index in selected_indices:
        body = candidate_bodies[body_index - 1]
        conditions.append(
            PublicationConditionSpec(
                condition_id=f"baseline_body_{body_index}",
                label=f"Baseline lineage body {body_index}",
                question="How does the selected survivor body behave in the default world under replicate seeds?",
                body_index=body_index,
                body_name=f"body_{body_index}",
                body_design=body.short_description,
                body_stats=body.stats_description,
                initial_population=INITIAL_POPULATION,
                max_population=MAX_POPULATION,
                max_ticks=max_ticks,
                founder_mode="default_alternating",
                founder_sexes=None,
                stop_on_generation_adult=None,
                env_kwargs=None,
                spawn_strategy="default",
            )
        )
    body8 = candidate_bodies[7]
    conditions.append(
        PublicationConditionSpec(
            condition_id="technology_pressure_body_8",
            label="Technology pressure body 8",
            question="How quickly does emergent technology appear under food pressure and frontier exploration?",
            body_index=8,
            body_name="body_8",
            body_design=body8.short_description,
            body_stats=body8.stats_description,
            initial_population=INITIAL_POPULATION,
            max_population=MAX_POPULATION,
            max_ticks=min(max_ticks, 800),
            founder_mode="default_alternating",
            founder_sexes=None,
            stop_on_generation_adult=None,
            env_kwargs=technology_pressure_env,
            spawn_strategy="frontier_safe_high_food",
        )
    )
    for body_index in selected_indices:
        body = candidate_bodies[body_index - 1]
        conditions.append(
            PublicationConditionSpec(
                condition_id=f"sexed_gen3_body_{body_index}",
                label=f"Sexed gen3 body {body_index}",
                question="Can the selected body sustain sexed reproduction through generation-3 adulthood?",
                body_index=body_index,
                body_name=f"body_{body_index}",
                body_design=body.short_description,
                body_stats=body.stats_description,
                initial_population=50,
                max_population=MAX_POPULATION,
                max_ticks=max(max_ticks, 2000),
                founder_mode="25_male_25_female",
                founder_sexes=sexed_founders,
                stop_on_generation_adult=3,
                env_kwargs=None,
                spawn_strategy="default",
            )
        )
    return conditions


def _robustness_conditions(candidate_bodies: list[BodyPlan], max_ticks: int) -> list[PublicationConditionSpec]:
    sexed_founders = ["male"] * 25 + ["female"] * 25
    body8 = candidate_bodies[7]
    body14 = candidate_bodies[13]
    harsh_technology_envs = [
        (
            "harsh_tech_low_food",
            {
                "max_food": 90,
                "base_food_spawn_per_tick": 3,
                "max_large_animals": 18,
                "large_animal_spawn_per_tick": 1,
                "food_spawn_multiplier": 0.75,
                "nest_support_food_chance": 0.04,
                "nest_support_spawn_chance": 0.04,
                "safe_area_stone_chance": 0.01,
                "frontier_stone_bonus": 0.08,
                "frontier_band": 10,
            },
        ),
        (
            "harsh_tech_frontier_cost",
            {
                "max_food": 80,
                "base_food_spawn_per_tick": 2,
                "max_large_animals": 14,
                "large_animal_spawn_per_tick": 1,
                "food_spawn_multiplier": 0.65,
                "nest_support_food_chance": 0.02,
                "nest_support_spawn_chance": 0.03,
                "safe_area_stone_chance": 0.005,
                "frontier_stone_bonus": 0.05,
                "frontier_band": 12,
            },
        ),
    ]
    conditions: list[PublicationConditionSpec] = []
    for suffix, env_kwargs in harsh_technology_envs:
        conditions.append(
            PublicationConditionSpec(
                condition_id=f"{suffix}_body_8",
                label=f"{suffix} body 8",
                question="How much can stronger ecological pressure delay first emergent technology?",
                body_index=8,
                body_name="body_8",
                body_design=body8.short_description,
                body_stats=body8.stats_description,
                initial_population=12,
                max_population=MAX_POPULATION,
                max_ticks=min(max_ticks, 900),
                founder_mode="default_alternating",
                founder_sexes=None,
                stop_on_generation_adult=None,
                env_kwargs=env_kwargs,
                spawn_strategy="frontier_safe_high_food",
            )
        )
    for body_index, body in [(8, body8), (14, body14)]:
        conditions.append(
            PublicationConditionSpec(
                condition_id=f"sexed_default_body_{body_index}",
                label=f"sexed default body {body_index}",
                question="How robust is sexed multi-generation survival in the default world?",
                body_index=body_index,
                body_name=f"body_{body_index}",
                body_design=body.short_description,
                body_stats=body.stats_description,
                initial_population=50,
                max_population=MAX_POPULATION,
                max_ticks=max(max_ticks, 2000),
                founder_mode="25_male_25_female",
                founder_sexes=sexed_founders,
                stop_on_generation_adult=3,
                env_kwargs=None,
                spawn_strategy="default",
            )
        )
        conditions.append(
            PublicationConditionSpec(
                condition_id=f"sexed_low_food_body_{body_index}",
                label=f"sexed low food body {body_index}",
                question="How robust is sexed multi-generation survival under lower food regeneration?",
                body_index=body_index,
                body_name=f"body_{body_index}",
                body_design=body.short_description,
                body_stats=body.stats_description,
                initial_population=50,
                max_population=MAX_POPULATION,
                max_ticks=max(max_ticks, 2000),
                founder_mode="25_male_25_female",
                founder_sexes=sexed_founders,
                stop_on_generation_adult=3,
                env_kwargs={
                    "max_food": 140,
                    "base_food_spawn_per_tick": 4,
                    "max_large_animals": 24,
                    "large_animal_spawn_per_tick": 2,
                    "food_spawn_multiplier": 0.72,
                    "nest_support_food_chance": 0.05,
                    "nest_support_spawn_chance": 0.05,
                    "safe_area_stone_chance": 0.02,
                    "frontier_stone_bonus": 0.10,
                    "frontier_band": 8,
                },
                spawn_strategy="default",
            )
        )
    return conditions


def _world_discovery_conditions(candidate_bodies: list[BodyPlan], max_ticks: int) -> list[PublicationConditionSpec]:
    sexed_founders = ["male"] * 25 + ["female"] * 25
    body8 = candidate_bodies[7]
    body14 = candidate_bodies[13]
    control_body_index = 131 if len(candidate_bodies) >= 131 else len(candidate_bodies)
    sensory_control = candidate_bodies[control_body_index - 1]

    frontier_object_env = {
        "max_food": 115,
        "base_food_spawn_per_tick": 4,
        "max_large_animals": 34,
        "large_animal_spawn_per_tick": 3,
        "food_spawn_multiplier": 0.82,
        "nest_support_food_chance": 0.06,
        "nest_support_spawn_chance": 0.05,
        "safe_area_stone_chance": 0.02,
        "frontier_stone_bonus": 0.22,
        "frontier_band": 10,
        "global_food_decline_per_day": 0.014,
        "minimum_global_food_multiplier": 0.28,
    }
    novel_scarcity_env = {
        "max_food": 95,
        "base_food_spawn_per_tick": 3,
        "max_large_animals": 28,
        "large_animal_spawn_per_tick": 2,
        "food_spawn_multiplier": 0.72,
        "nest_support_food_chance": 0.03,
        "nest_support_spawn_chance": 0.03,
        "safe_area_stone_chance": 0.01,
        "frontier_stone_bonus": 0.08,
        "frontier_band": 12,
        "day_length": 16,
        "season_length": 60,
        "global_food_decline_per_day": 0.018,
        "minimum_global_food_multiplier": 0.22,
    }

    return [
        PublicationConditionSpec(
            condition_id="embodied_world_model_body_8",
            label="Embodied world-model body 8",
            question="Can high-cognition embodied agents accumulate usable Type-1 world knowledge from direct interaction in the default world?",
            body_index=8,
            body_name="body_8",
            body_design=body8.short_description,
            body_stats=body8.stats_description,
            initial_population=INITIAL_POPULATION,
            max_population=MAX_POPULATION,
            max_ticks=max_ticks,
            founder_mode="default_alternating",
            founder_sexes=None,
            stop_on_generation_adult=None,
            env_kwargs=None,
            spawn_strategy="default",
        ),
        PublicationConditionSpec(
            condition_id="frontier_object_discovery_body_8",
            label="Frontier object discovery body 8",
            question="Does scarcity plus frontier material access drive object experimentation and first technology emergence?",
            body_index=8,
            body_name="body_8",
            body_design=body8.short_description,
            body_stats=body8.stats_description,
            initial_population=INITIAL_POPULATION,
            max_population=MAX_POPULATION,
            max_ticks=min(max_ticks, 1000),
            founder_mode="default_alternating",
            founder_sexes=None,
            stop_on_generation_adult=None,
            env_kwargs=frontier_object_env,
            spawn_strategy="frontier_safe_high_food",
        ),
        PublicationConditionSpec(
            condition_id="collective_world_model_body_8",
            label="Collective world-model body 8",
            question="Does a larger sexed community turn individual memories into group-level persistence across generations?",
            body_index=8,
            body_name="body_8",
            body_design=body8.short_description,
            body_stats=body8.stats_description,
            initial_population=50,
            max_population=MAX_POPULATION,
            max_ticks=max(max_ticks, 2200),
            founder_mode="25_male_25_female",
            founder_sexes=sexed_founders,
            stop_on_generation_adult=3,
            env_kwargs=None,
            spawn_strategy="default",
        ),
        PublicationConditionSpec(
            condition_id="collective_world_model_body_14",
            label="Collective world-model body 14",
            question="Does the nurturing-settler lineage build a more stable collective world model than the social-planner lineage?",
            body_index=14,
            body_name="body_14",
            body_design=body14.short_description,
            body_stats=body14.stats_description,
            initial_population=50,
            max_population=MAX_POPULATION,
            max_ticks=max(max_ticks, 2200),
            founder_mode="25_male_25_female",
            founder_sexes=sexed_founders,
            stop_on_generation_adult=3,
            env_kwargs=None,
            spawn_strategy="default",
        ),
        PublicationConditionSpec(
            condition_id=f"sensory_control_body_{control_body_index}",
            label=f"Sensory control body {control_body_index}",
            question="Do high-sensor lower-brain agents survive without producing the same memory, social, and technology signatures?",
            body_index=control_body_index,
            body_name=f"body_{control_body_index}",
            body_design=sensory_control.short_description,
            body_stats=sensory_control.stats_description,
            initial_population=INITIAL_POPULATION,
            max_population=MAX_POPULATION,
            max_ticks=max_ticks,
            founder_mode="default_alternating",
            founder_sexes=None,
            stop_on_generation_adult=None,
            env_kwargs=None,
            spawn_strategy="default",
        ),
        PublicationConditionSpec(
            condition_id="novel_scarcity_transfer_body_8",
            label="Novel scarcity transfer body 8",
            question="Do direct-interaction strategies remain viable when the world is made less abundant and more temporally variable?",
            body_index=8,
            body_name="body_8",
            body_design=body8.short_description,
            body_stats=body8.stats_description,
            initial_population=INITIAL_POPULATION,
            max_population=MAX_POPULATION,
            max_ticks=max_ticks,
            founder_mode="default_alternating",
            founder_sexes=None,
            stop_on_generation_adult=None,
            env_kwargs=novel_scarcity_env,
            spawn_strategy="frontier_safe_high_food",
        ),
    ]


def _load_research_manifest_bundle(manifest_path: Path) -> dict[str, object]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "manifest": manifest,
        "metadata": json.loads(Path(manifest["metadata"]).read_text(encoding="utf-8")),
        "summary": json.loads(Path(manifest["summary"]).read_text(encoding="utf-8")),
        "tick_metrics": _read_csv_rows(Path(manifest["tick_metrics_csv"])),
        "events": [json.loads(line) for line in Path(manifest["events_jsonl"]).read_text(encoding="utf-8").splitlines() if line.strip()],
        "lineages": _read_csv_rows(Path(manifest["lineages_csv"])),
        "agent_outcomes": _read_csv_rows(Path(manifest["agent_outcomes_csv"])),
    }


def _read_csv_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, object]] = []
        for row in reader:
            normalized: dict[str, object] = {}
            for key, value in row.items():
                normalized[key] = _coerce_csv_value(value)
            rows.append(normalized)
        return rows


def _coerce_csv_value(value: str | None) -> object:
    if value is None or value == "":
        return None
    if value.startswith("{") or value.startswith("["):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _agent_learning_proxy_summary(agent_rows: list[dict[str, object]]) -> dict[str, float | int]:
    if not agent_rows:
        return {
            "mean_agent_memory_sites": 0.0,
            "max_agent_memory_sites": 0,
            "social_contact_rate": 0.0,
            "object_experiment_agent_rate": 0.0,
            "mean_friend_count": 0.0,
        }

    memory_counts: list[int] = []
    friend_counts: list[int] = []
    object_experimenters = 0
    for row in agent_rows:
        memory_count = sum(
            int(row.get(key) or 0)
            for key in (
                "remembered_food_sources_count",
                "remembered_safe_zones_count",
                "remembered_danger_count",
                "remembered_nest_locations_count",
            )
        )
        friend_count = int(row.get("friend_count") or 0)
        memory_counts.append(memory_count)
        friend_counts.append(friend_count)

        constructions = row.get("technology_constructions_json")
        if isinstance(constructions, dict) and any(int(value) > 0 for value in constructions.values()):
            object_experimenters += 1

    row_count = len(agent_rows)
    social_agents = sum(1 for count in friend_counts if count > 0)
    return {
        "mean_agent_memory_sites": round(sum(memory_counts) / row_count, 3),
        "max_agent_memory_sites": max(memory_counts),
        "social_contact_rate": round(social_agents / row_count, 4),
        "object_experiment_agent_rate": round(object_experimenters / row_count, 4),
        "mean_friend_count": round(sum(friend_counts) / row_count, 3),
    }


def _git_revision() -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip() or None
    except Exception:
        return None


def run_first_tool_emergence_study(
    start_seed: int = 7,
    seed_count: int = 12,
    change_note: str = "Emergent technology study",
    body_index: int = 8,
    max_ticks: int = 2000,
) -> list[FirstToolEmergenceRecord]:
    experiment = start_experiment_run(change_note)
    candidate_bodies = generate_candidate_body_plans()
    resolved_body_index = max(1, min(body_index, len(candidate_bodies)))
    body = candidate_bodies[resolved_body_index - 1]
    records: list[FirstToolEmergenceRecord] = []
    results: list[ExperimentResult] = []

    technology_pressure_env = {
        "max_food": 120,
        "base_food_spawn_per_tick": 5,
        "max_large_animals": 36,
        "large_animal_spawn_per_tick": 3,
        "food_spawn_multiplier": 0.9,
        "nest_support_food_chance": 0.10,
        "nest_support_spawn_chance": 0.08,
        "safe_area_stone_chance": 0.03,
        "frontier_stone_bonus": 0.18,
        "frontier_band": 6,
    }

    log(experiment, "Artificial Evolution Emergent Technology Study")
    log(experiment, "=" * 48)
    log(experiment, f"Experiment #{experiment.experiment_number}")
    log(experiment, f"Change note: {change_note}")
    log(experiment, f"Started at: {experiment.started_at}")
    log(
        experiment,
        f"Body index={resolved_body_index} | seeds={seed_count} | max_ticks={max_ticks}"
    )
    log(experiment, f"Body: {body.short_description}")
    log(experiment, f"Pressure world: {technology_pressure_env}")

    for seed_offset in range(seed_count):
        seed = start_seed + seed_offset
        rng = Random(seed)
        result = run_single_body_trial(
            rng,
            body_index=resolved_body_index,
            body=body,
            max_ticks=max_ticks,
            capture_dashboard=True,
            dashboard_group="first_technology_mode",
            dashboard_run_name=(
                f"experiment_{experiment.experiment_number:03d}_"
                f"first_technology_seed_{seed}"
            ),
            dashboard_seed=seed,
            dashboard_title=f"Emergent Technology Study Seed {seed}",
            env_kwargs=technology_pressure_env,
            spawn_strategy="frontier_safe_high_food",
        )
        results.append(result)
        record = FirstToolEmergenceRecord(
            seed=seed,
            body_index=resolved_body_index,
            body_name=result.body_name,
            body_design=result.body_design,
            first_technology_tick=result.first_technology_tick,
            first_technology_day=result.first_technology_day,
            first_technology_name=result.first_technology_name,
            total_births=result.total_births,
            matured_children=result.matured_children,
            peak_population=result.peak_population,
            stored_food_total=result.stored_food_total,
            reached_target=result.reached_target,
        )
        records.append(record)
        log(
            experiment,
            f"Seed {seed}: first_technology={record.first_technology_name} @ tick={record.first_technology_tick} "
            f"day={record.first_technology_day} | births={record.total_births} | peak_pop={record.peak_population}"
        )
        if result.dashboard_path is not None:
            log(experiment, f"  dashboard={result.dashboard_path}")

    _save_first_tool_emergence_study(
        experiment=experiment,
        start_seed=start_seed,
        seed_count=seed_count,
        body_index=resolved_body_index,
        body=body,
        max_ticks=max_ticks,
        env_kwargs=technology_pressure_env,
        records=records,
    )
    finalize_experiment_run(experiment, results, [], start_seed)
    return records


def run_sexed_generation_test(
    seed: int = 7,
    change_note: str = "Sexed survival generation test",
    body_index: int = 8,
    male_founders: int = 25,
    female_founders: int = 25,
    max_ticks: int = MAX_TICKS,
) -> SexedSurvivalResult:
    experiment = start_experiment_run(change_note)
    candidate_bodies = generate_candidate_body_plans()
    resolved_body_index = max(1, min(body_index, len(candidate_bodies)))
    body = candidate_bodies[resolved_body_index - 1]
    initial_population = male_founders + female_founders
    founder_sexes = (["male"] * male_founders) + (["female"] * female_founders)

    log(experiment, "Artificial Evolution Sexed Generation Test")
    log(experiment, "=" * 42)
    log(experiment, f"Experiment #{experiment.experiment_number}")
    log(experiment, f"Change note: {change_note}")
    log(experiment, f"Started at: {experiment.started_at}")
    log(experiment, f"Body index={resolved_body_index} | founders={initial_population} | max_ticks={max_ticks}")
    log(experiment, f"Founders: male={male_founders}, female={female_founders}")
    log(experiment, f"Body: {body.short_description}")

    result = run_single_body_trial(
        Random(seed),
        body_index=resolved_body_index,
        body=body,
        initial_population=initial_population,
        max_population=max(MAX_POPULATION, initial_population * 6),
        max_ticks=max_ticks,
        capture_dashboard=True,
        dashboard_group="sexed_generation_mode",
        dashboard_run_name=f"experiment_{experiment.experiment_number:03d}_sexed_seed_{seed}",
        dashboard_seed=seed,
        dashboard_title=f"Sexed Generation Test Seed {seed}",
        founder_sexes=founder_sexes,
        stop_on_generation_adult=3,
    )

    summary = SexedSurvivalResult(
        seed=seed,
        body_index=resolved_body_index,
        body_name=result.body_name,
        body_design=result.body_design,
        final_tick=result.final_tick,
        peak_population=result.peak_population,
        total_births=result.total_births,
        matured_children=result.matured_children,
        population_extinct=result.population_extinct,
        target_generation_reached=result.target_generation_reached,
        target_generation_tick=result.target_generation_tick,
        first_birth_tick=result.first_birth_tick,
        dashboard_path=result.dashboard_path,
    )

    status_line = (
        f"Result: extinct={summary.population_extinct} | gen3_adult={summary.target_generation_reached} "
        f"| gen3_tick={summary.target_generation_tick} | births={summary.total_births} | peak_pop={summary.peak_population}"
    )
    log(experiment, status_line)
    if summary.dashboard_path is not None:
        log(experiment, f"dashboard={summary.dashboard_path}")
    _save_sexed_generation_test(experiment, seed, body, summary, male_founders, female_founders, max_ticks)
    finalize_experiment_run(experiment, [result], [], seed)
    return summary


def run_sexed_world_body_search(
    start_seed: int = 7,
    change_note: str = "Sexed world body search",
    male_founders: int = 25,
    female_founders: int = 25,
    max_ticks: int = MAX_TICKS,
    max_seed_rounds: int = 3,
    candidate_limit: int = MAX_BODY_CANDIDATES_TO_TEST,
) -> list[SexedSearchRecord]:
    experiment = start_experiment_run(change_note)
    candidate_bodies = generate_candidate_body_plans()[:candidate_limit]
    records: list[SexedSearchRecord] = []
    all_results: list[ExperimentResult] = []
    founder_sexes = (["male"] * male_founders) + (["female"] * female_founders)

    log(experiment, "Artificial Evolution Sexed World Body Search")
    log(experiment, "=" * 43)
    log(experiment, f"Experiment #{experiment.experiment_number}")
    log(experiment, f"Change note: {change_note}")
    log(experiment, f"Started at: {experiment.started_at}")
    log(
        experiment,
        f"Founders: male={male_founders}, female={female_founders} | max_ticks={max_ticks} | "
        f"max_seed_rounds={max_seed_rounds} | candidate_limit={candidate_limit}",
    )

    best_record: SexedSearchRecord | None = None
    best_result: ExperimentResult | None = None

    for body_index, body in enumerate(candidate_bodies, start=1):
        body_best_result: ExperimentResult | None = None
        body_best_seed = start_seed
        for seed_offset in range(max_seed_rounds):
            seed = start_seed + seed_offset
            result = run_single_body_trial(
                Random((seed * 100000) + body_index),
                body_index=body_index,
                body=body,
                initial_population=male_founders + female_founders,
                max_population=max(MAX_POPULATION, (male_founders + female_founders) * 6),
                max_ticks=max_ticks,
                founder_sexes=founder_sexes,
                stop_on_generation_adult=3,
            )
            all_results.append(result)
            if body_best_result is None or _sexed_search_score(result) > _sexed_search_score(body_best_result):
                body_best_result = result
                body_best_seed = seed
            if result.target_generation_reached:
                break

        if body_best_result is None:
            continue

        record = SexedSearchRecord(
            body_index=body_index,
            body_name=body_best_result.body_name,
            body_design=body_best_result.body_design,
            body_stats=body_best_result.body_stats,
            seed=body_best_seed,
            final_tick=body_best_result.final_tick,
            peak_population=body_best_result.peak_population,
            total_births=body_best_result.total_births,
            matured_children=body_best_result.matured_children,
            population_extinct=body_best_result.population_extinct,
            target_generation_reached=body_best_result.target_generation_reached,
            target_generation_tick=body_best_result.target_generation_tick,
        )
        records.append(record)

        if best_record is None or _sexed_record_score(record) > _sexed_record_score(best_record):
            best_record = record
            best_result = body_best_result
            log(
                experiment,
                f"New best body: idx={record.body_index} | seed={record.seed} | extinct={record.population_extinct} | "
                f"gen3={record.target_generation_reached} | final_tick={record.final_tick} | "
                f"births={record.total_births} | matured={record.matured_children} | {record.body_design}",
            )

        if body_index % 25 == 0:
            log(
                experiment,
                f"Scanned {body_index}/{len(candidate_bodies)} bodies | current best idx={best_record.body_index if best_record else 'none'}",
            )

    _save_sexed_world_body_search(
        experiment=experiment,
        start_seed=start_seed,
        male_founders=male_founders,
        female_founders=female_founders,
        max_ticks=max_ticks,
        max_seed_rounds=max_seed_rounds,
        candidate_limit=candidate_limit,
        records=records,
        best_record=best_record,
    )
    finalize_experiment_run(experiment, all_results, [best_result] if best_result is not None else [], start_seed)
    return sorted(records, key=_sexed_record_score, reverse=True)


def _save_sexed_generation_test(
    experiment: ExperimentRun,
    seed: int,
    body: BodyPlan,
    summary: SexedSurvivalResult,
    male_founders: int,
    female_founders: int,
    max_ticks: int,
) -> None:
    payload = {
        "experiment_number": experiment.experiment_number,
        "change_note": experiment.change_note,
        "started_at": experiment.started_at,
        "seed": seed,
        "body_index": summary.body_index,
        "body_design": body.short_description,
        "body_stats": body.stats_description,
        "male_founders": male_founders,
        "female_founders": female_founders,
        "max_ticks": max_ticks,
        "summary": asdict(summary),
    }
    (DATA_DIR / "sexed_generation_test.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Sexed Generation Test",
        "",
        f"Seed: {seed}",
        f"Body index: {summary.body_index}",
        f"Body: {body.short_description}",
        f"Founders: male={male_founders}, female={female_founders}",
        f"Final tick: {summary.final_tick}",
        f"Population extinct: {summary.population_extinct}",
        f"Generation 3 adult reached: {summary.target_generation_reached}",
        f"Generation 3 adult tick: {summary.target_generation_tick}",
        f"First birth tick: {summary.first_birth_tick}",
        f"Peak population: {summary.peak_population}",
        f"Total births: {summary.total_births}",
        f"Matured children: {summary.matured_children}",
    ]
    if summary.dashboard_path is not None:
        lines.append(f"Dashboard: {summary.dashboard_path}")
    (DATA_DIR / "sexed_generation_test.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def _sexed_search_score(result: ExperimentResult) -> tuple[int, int, int, int, int]:
    return (
        1 if result.target_generation_reached else 0,
        0 if result.population_extinct else 1,
        result.final_tick,
        result.matured_children,
        result.total_births,
    )


def _sexed_record_score(record: SexedSearchRecord) -> tuple[int, int, int, int, int]:
    return (
        1 if record.target_generation_reached else 0,
        0 if record.population_extinct else 1,
        record.final_tick,
        record.matured_children,
        record.total_births,
    )


def _save_sexed_world_body_search(
    experiment: ExperimentRun,
    start_seed: int,
    male_founders: int,
    female_founders: int,
    max_ticks: int,
    max_seed_rounds: int,
    candidate_limit: int,
    records: list[SexedSearchRecord],
    best_record: SexedSearchRecord | None,
) -> None:
    ranked_records = sorted(records, key=_sexed_record_score, reverse=True)
    payload = {
        "experiment_number": experiment.experiment_number,
        "change_note": experiment.change_note,
        "started_at": experiment.started_at,
        "start_seed": start_seed,
        "male_founders": male_founders,
        "female_founders": female_founders,
        "max_ticks": max_ticks,
        "max_seed_rounds": max_seed_rounds,
        "candidate_limit": candidate_limit,
        "best_record": asdict(best_record) if best_record is not None else None,
        "records": [asdict(record) for record in ranked_records],
    }
    (DATA_DIR / "sexed_world_body_search.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Sexed World Body Search",
        "",
        f"Seeds start at: {start_seed}",
        f"Founders: male={male_founders}, female={female_founders}",
        f"Max ticks: {max_ticks}",
        f"Max seed rounds: {max_seed_rounds}",
        f"Candidate limit: {candidate_limit}",
        "",
        "## Best Record",
        "",
    ]
    if best_record is None:
        lines.append("- No candidate records saved.")
    else:
        lines.extend(
            [
                f"- body_index={best_record.body_index}",
                f"- seed={best_record.seed}",
                f"- design={best_record.body_design}",
                f"- extinct={best_record.population_extinct}",
                f"- gen3_adult={best_record.target_generation_reached}",
                f"- gen3_tick={best_record.target_generation_tick}",
                f"- final_tick={best_record.final_tick}",
                f"- births={best_record.total_births}",
                f"- matured_children={best_record.matured_children}",
                f"- peak_population={best_record.peak_population}",
            ]
        )
    lines.extend(["", "## Top 10", ""])
    for record in ranked_records[:10]:
        lines.append(
            f"- idx={record.body_index} | seed={record.seed} | extinct={record.population_extinct} | "
            f"gen3={record.target_generation_reached} | final_tick={record.final_tick} | "
            f"births={record.total_births} | matured={record.matured_children} | {record.body_design}"
        )

    (DATA_DIR / "sexed_world_body_search.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def _lineage_label(founder_index: int) -> str:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    letter = alphabet[founder_index % len(alphabet)]
    suffix = founder_index // len(alphabet)
    return f"{letter}{suffix + 1:02d}"


def _empty_heatmap(width: int, height: int, bin_size: int) -> list[list[int]]:
    return [
        [0 for _ in range((width + bin_size - 1) // bin_size)]
        for _ in range((height + bin_size - 1) // bin_size)
    ]


def _increment_heatmap(
    heatmap: list[list[int]],
    x: int,
    y: int,
    *,
    bin_size: int,
) -> None:
    row = min(len(heatmap) - 1, max(0, y // bin_size))
    col = min(len(heatmap[0]) - 1, max(0, x // bin_size))
    heatmap[row][col] += 1


def _lineage_counts(agents: list[Agent]) -> Counter[str]:
    return Counter(agent.lineage_id or f"agent_{agent.agent_id}" for agent in agents if agent.alive)


def _occupied_nest_owner_ids(env: Environment, agents: list[Agent]) -> set[int]:
    occupied: set[int] = set()
    for agent in agents:
        if not agent.alive:
            continue
        owner_id = agent._nest_owner_id()
        if owner_id is None:
            continue
        nest = env.find_nest(owner_id)
        if nest is None:
            continue
        if abs(agent.x - nest.x) + abs(agent.y - nest.y) <= nest.safe_radius:
            occupied.add(owner_id)
    return occupied


def _try_transfer_abandoned_nest(env: Environment, deceased: Agent, agents: list[Agent]) -> str | None:
    nest = env.find_nest(deceased.agent_id)
    if nest is None:
        return None

    candidates: list[tuple[tuple[int, int, int, int], Agent]] = []
    for agent in agents:
        if not agent.alive or agent.agent_id == deceased.agent_id:
            continue
        distance = abs(agent.x - nest.x) + abs(agent.y - nest.y)
        in_radius = int(distance <= nest.safe_radius + 1)
        kin_link = int(
            deceased.agent_id in {
                agent.parent_id,
                agent.other_parent_id,
                agent.shared_home_owner_id,
            }
        )
        if kin_link == 0 and in_radius == 0:
            continue
        stage_priority = 2 if agent.current_stage == "adult" else (1 if agent.current_stage == "juvenile" else 0)
        score = (kin_link, stage_priority, in_radius, agent.energy)
        candidates.append((score, agent))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    heir = candidates[0][1]
    if not env.transfer_nest(deceased.agent_id, heir.agent_id):
        return None

    for agent in agents:
        if not agent.alive:
            continue
        if agent.shared_home_owner_id == deceased.agent_id:
            agent.shared_home_owner_id = heir.agent_id

    return (
        f"nest_inherited -> old_owner={deceased.agent_id} new_owner={heir.agent_id} "
        f"stage={heir.current_stage} energy={heir.energy}"
    )


def _top_lineages(agents: list[Agent], limit: int = 2) -> list[str]:
    counts = _lineage_counts(agents)
    return [
        lineage_id
        for lineage_id, _ in counts.most_common(limit)
    ]


def _make_tick_summary(
    env: Environment,
    agents: list[Agent],
    *,
    tick: int,
    births: int,
    deaths: int,
) -> dict[str, object]:
    stage_counts = Counter(agent.current_stage for agent in agents if agent.alive)
    sex_counts = Counter(agent.sex for agent in agents if agent.alive)
    stored_food = sum(nest.food_storage for nest in env.nests.values())
    alive_agents = [agent for agent in agents if agent.alive]
    gen1_adult_females = [
        agent
        for agent in alive_agents
        if agent.generation == 1 and agent.sex == "female" and agent.current_stage == "adult"
    ]
    gen1_adult_males = [
        agent
        for agent in alive_agents
        if agent.generation == 1 and agent.sex == "male" and agent.current_stage == "adult"
    ]
    gen1_female_near_nest = sum(
        1 for agent in gen1_adult_females if bool(agent.reproduction_debug.get("near_nest", agent.near_nest))
    )
    gen1_female_with_mate = sum(
        1 for agent in gen1_adult_females if bool(agent.reproduction_debug.get("mate", False))
    )
    gen1_avg_energy = (
        sum(agent.energy for agent in gen1_adult_females) / len(gen1_adult_females)
        if gen1_adult_females
        else 0.0
    )
    gen1_reproduction_block_reason = Counter(
        str(agent.reproduction_debug.get("reason", "unknown"))
        for agent in gen1_adult_females
    )
    mean_energy = (
        sum(agent.energy for agent in alive_agents) / len(alive_agents)
        if alive_agents
        else 0.0
    )
    mean_durability = (
        sum(agent.durability for agent in alive_agents) / len(alive_agents)
        if alive_agents
        else 0.0
    )
    mean_safety_feeling = (
        sum(agent.safety_feeling for agent in alive_agents) / len(alive_agents)
        if alive_agents
        else 0.0
    )
    mean_comfort_level = (
        sum(agent.comfort_level for agent in alive_agents) / len(alive_agents)
        if alive_agents
        else 0.0
    )
    mean_fear_level = (
        sum(agent.fear_level for agent in alive_agents) / len(alive_agents)
        if alive_agents
        else 0.0
    )
    mean_hunger_level = (
        sum(agent.hunger_level for agent in alive_agents) / len(alive_agents)
        if alive_agents
        else 0.0
    )
    mean_pair_bond_ticks = (
        sum(agent.pair_bond_ticks for agent in alive_agents) / len(alive_agents)
        if alive_agents
        else 0.0
    )
    affect_ready_adults = sum(
        1
        for agent in alive_agents
        if agent.current_stage == "adult"
        and agent.safety_feeling >= 0.66
        and agent.comfort_level >= 0.58
        and agent.hunger_level < 0.35
        and agent.fear_level < 0.42
        and agent.safety_streak_ticks >= 10
        and agent.pair_bond_ticks >= 14
    )
    biome_counts = Counter(env.get_biome(agent.x, agent.y) for agent in alive_agents)
    plant_counts = env.plant_state_counts()
    return {
        "tick": tick,
        "day": tick // env.day_length,
        "population": len(agents),
        "children": stage_counts.get("child", 0),
        "juveniles": stage_counts.get("juvenile", 0),
        "adults": stage_counts.get("adult", 0),
        "old": stage_counts.get("old", 0),
        "female": sex_counts.get("female", 0),
        "male": sex_counts.get("male", 0),
        "generation_0": sum(1 for agent in alive_agents if agent.generation == 0),
        "generation_1": sum(1 for agent in alive_agents if agent.generation == 1),
        "generation_2": sum(1 for agent in alive_agents if agent.generation == 2),
        "generation_3_plus": sum(1 for agent in alive_agents if agent.generation >= 3),
        "gen1_adult_female_count": len(gen1_adult_females),
        "gen1_adult_male_count": len(gen1_adult_males),
        "gen1_female_near_nest": gen1_female_near_nest,
        "gen1_female_with_mate": gen1_female_with_mate,
        "gen1_avg_energy": round(gen1_avg_energy, 3),
        "gen1_reproduction_block_reason": dict(gen1_reproduction_block_reason),
        "births": births,
        "deaths": deaths,
        "settlements": len(env.nests),
        "stored_food": stored_food,
        "food_cells": len(env.food_positions),
        "large_animals": len(env.large_animals),
        "mean_energy": round(mean_energy, 3),
        "mean_durability": round(mean_durability, 3),
        "mean_safety_feeling": round(mean_safety_feeling, 3),
        "mean_comfort_level": round(mean_comfort_level, 3),
        "mean_fear_level": round(mean_fear_level, 3),
        "mean_hunger_level": round(mean_hunger_level, 3),
        "mean_pair_bond_ticks": round(mean_pair_bond_ticks, 3),
        "affect_ready_adults": affect_ready_adults,
        "population_safe_low_food": biome_counts.get("safe_low_food", 0),
        "population_safe_high_food": biome_counts.get("safe_high_food", 0),
        "population_danger_high_food": biome_counts.get("danger_high_food", 0),
        "population_danger_low_food": biome_counts.get("danger_low_food", 0),
        "plants_total": len(env.plant_seeds),
        "plant_state_seed": plant_counts.get("seed", 0),
        "plant_state_carried_seed": plant_counts.get("carried_seed", 0),
        "plant_state_sprout": plant_counts.get("sprout", 0),
        "plant_state_mature": plant_counts.get("mature", 0),
        "mean_photosynthetic_light": round(env.mean_photosynthetic_light(), 3),
        "mean_soil_nutrients": round(env.mean_soil_nutrients(), 3),
        "top_lineages": _top_lineages(agents),
    }


def _make_snapshot(
    env: Environment,
    agents: list[Agent],
    *,
    tick: int,
    births: int,
    deaths: int,
    death_positions: list[tuple[int, int]],
) -> dict[str, object]:
    return {
        "tick": tick,
        "population": len(agents),
        "births": births,
        "deaths": deaths,
        "agents": [
            {
                "agent_id": agent.agent_id,
                "lineage_id": agent.lineage_id or f"agent_{agent.agent_id}",
                "x": agent.x,
                "y": agent.y,
                "stage": agent.current_stage,
                "sex": agent.sex,
                "generation": agent.generation,
                "energy": agent.energy,
                "role": agent.current_role,
            }
            for agent in agents
            if agent.alive
        ],
        "food_positions": [list(position) for position in env.food_positions.keys()],
        "nests": [
            {
                "owner_id": nest.owner_id,
                "x": nest.x,
                "y": nest.y,
                "safe_radius": nest.safe_radius,
                "food_storage": nest.food_storage,
            }
            for nest in env.nests.values()
        ],
        "death_positions": [list(position) for position in death_positions],
    }


def _append_alert(
    alerts: list[dict[str, object]],
    seen_alerts: set[tuple[str, int, str]],
    *,
    tick: int,
    alert_type: str,
    message: str,
) -> None:
    key = (alert_type, tick, message)
    if key in seen_alerts:
        return
    seen_alerts.add(key)
    alerts.append(
        {
            "tick": tick,
            "type": alert_type,
            "message": message,
        }
    )


def _normalize_event(event_text: str, tick: int) -> dict[str, object]:
    normalized: dict[str, object] = {
        "tick": tick,
        "event_type": "unclassified",
        "raw_text": event_text,
    }

    if " -> " not in event_text:
        normalized["event_type"] = "free_text"
        return normalized

    event_type, details = event_text.split(" -> ", 1)
    normalized["event_type"] = event_type.strip().replace(" ", "_")
    normalized["details"] = details

    normalized["agent_ids"] = [int(value) for value in re.findall(r"agent=(\d+)", details)]
    normalized["parent_ids"] = [int(value) for value in re.findall(r"parent=(\d+)", details)]
    normalized["child_ids"] = [int(value) for value in re.findall(r"child=(\d+)", details)]
    normalized["nest_ids"] = [int(value) for value in re.findall(r"nest=(\d+)", details)]
    normalized["object_ids"] = [int(value) for value in re.findall(r"object=(\d+)", details)]
    classification_match = re.search(r"classification=([a-z_]+)", details)
    if classification_match:
        normalized["classification"] = classification_match.group(1)

    position_match = re.search(r"position=\((\d+), (\d+)\)", details)
    if position_match:
        normalized["position"] = [int(position_match.group(1)), int(position_match.group(2))]

    amount_match = re.search(r"amount=(\d+)", details)
    if amount_match:
        normalized["amount"] = int(amount_match.group(1))

    tick_match = re.search(r"tick=(\d+)", details)
    if tick_match:
        normalized["tick"] = int(tick_match.group(1))

    day_match = re.search(r"day=(\d+)", details)
    if day_match:
        normalized["day"] = int(day_match.group(1))

    return normalized


def _gen1_reproduction_diagnostics(agents: list[Agent]) -> dict[str, object]:
    gen1_adult_females = [
        agent
        for agent in agents
        if agent.alive and agent.generation == 1 and agent.sex == "female" and agent.current_stage == "adult"
    ]
    gen1_adult_males = [
        agent
        for agent in agents
        if agent.alive and agent.generation == 1 and agent.sex == "male" and agent.current_stage == "adult"
    ]
    eligible_female = sum(
        1 for agent in gen1_adult_females if bool(agent.reproduction_debug.get("eligible", False))
    )
    block_counter: Counter[str] = Counter()
    for agent in gen1_adult_females:
        reasons = agent.reproduction_debug.get("reasons", [])
        if not reasons:
            continue
        for reason in reasons:
            block_counter[str(reason)] += 1
    return {
        "adult_male": len(gen1_adult_males),
        "adult_female": len(gen1_adult_females),
        "eligible_female": eligible_female,
        "blocks": dict(block_counter),
    }


def _parse_technology_name(event_text: str) -> str | None:
    match = re.search(r"classification=([a-z_]+)", event_text)
    if match is None:
        return None
    return match.group(1)


def _classify_emergent_technology(physical_object) -> str:
    if physical_object.state_label == "fired_hard" and physical_object.hardness >= 6:
        return "proto_ceramic_type_a"
    if physical_object.state_label == "thermal_fractured" and physical_object.sharpness >= 6:
        return "proto_flaked_stone_type_a"
    if physical_object.state_label == "charred":
        return "proto_charred_material_type_a"
    if physical_object.sharpness >= 7 and physical_object.portability:
        return "proto_blade_type_a"
    if physical_object.length >= 7 and physical_object.hardness >= 6:
        return "proto_piercer_type_a"
    if physical_object.mass >= 5 and physical_object.hardness >= 6:
        return "proto_hammer_type_a"
    return "proto_composite_type_a"


def _detect_emergent_technology_events(env: Environment, tick: int, day: int) -> list[str]:
    events: list[str] = []
    for physical_object in env.objects.values():
        if physical_object.classification is not None:
            continue
        if physical_object.use_count < 4:
            continue
        if physical_object.total_outcome_score < 18:
            continue
        if len(physical_object.user_ids) < 2:
            continue
        if len(physical_object.copied_by_agents) < 1:
            continue
        physical_object.classification = _classify_emergent_technology(physical_object)
        physical_object.emergence_tick = tick
        events.append(
            f"technology_emerged -> tick={tick} day={day} classification={physical_object.classification} "
            f"object={physical_object.object_id} use_count={physical_object.use_count} "
            f"users={len(physical_object.user_ids)} outcome={physical_object.total_outcome_score:.1f}"
        )
    return events


def run_single_body_trial(
    rng: Random,
    body_index: int,
    body: BodyPlan,
    initial_population: int = INITIAL_POPULATION,
    max_population: int = MAX_POPULATION,
    max_ticks: int = MAX_TICKS,
    capture_dashboard: bool = False,
    dashboard_group: str = "general",
    dashboard_run_name: str | None = None,
    dashboard_seed: int | None = None,
    dashboard_title: str = "Simulation Dashboard",
    snapshot_interval: int = 10,
    capture_research_data: bool = False,
    research_run_name: str | None = None,
    research_seed: int | None = None,
    research_change_note: str = "Research capture",
    env_kwargs: dict[str, object] | None = None,
    spawn_strategy: str = "default",
    founder_sexes: list[str] | None = None,
    stop_on_generation_adult: int | None = None,
    stop_on_target_survivors: bool = True,
    research_condition_id: str | None = None,
    research_condition_label: str | None = None,
    research_question: str | None = None,
    immortal_agents: bool = False,
) -> ExperimentResult:
    env = Environment(**(env_kwargs or {}))
    spawn_positions = _spawn_initial_positions(env, rng, initial_population, body, strategy=spawn_strategy)
    agents: list[Agent] = []
    for agent_id, (spawn_x, spawn_y) in enumerate(spawn_positions):
        sex = founder_sexes[agent_id] if founder_sexes is not None and agent_id < len(founder_sexes) else ("female" if agent_id % 2 == 0 else "male")
        agents.append(
            Agent(
                agent_id=agent_id,
                body=body,
                x=spawn_x,
                y=spawn_y,
                age=FOUNDER_START_AGE,
                lineage_id=_lineage_label(agent_id),
                sex=sex,
                generation=0,
                immortal=immortal_agents,
            )
        )

    completed_survivors = 0
    death_counts: Counter[str] = Counter()
    archived_agents: list[Agent] = []
    next_agent_id = len(agents)
    peak_population = len(agents)
    total_births = 0
    matured_children: set[int] = set()
    first_birth_tick: int | None = None
    first_birth_day: int | None = None
    first_matured_child_tick: int | None = None
    first_matured_child_day: int | None = None
    first_technology_tick: int | None = None
    first_technology_day: int | None = None
    first_technology_name: str | None = None
    target_generation_tick: int | None = None
    target_generation_reached = False
    social_events: list[str] = []
    seen_groups: set[frozenset[int]] = set()
    dashboard_path: str | None = None
    telemetry_path: str | None = None
    research_manifest_path: str | None = None

    heatmap_bin_size = 5
    population_heatmap = _empty_heatmap(env.width, env.height, heatmap_bin_size)
    death_heatmap = _empty_heatmap(env.width, env.height, heatmap_bin_size)
    food_heatmap = _empty_heatmap(env.width, env.height, heatmap_bin_size)
    tick_summaries: list[dict[str, object]] = []
    snapshots: list[dict[str, object]] = []
    alerts: list[dict[str, object]] = []
    seen_alerts: set[tuple[str, int, str]] = set()
    lineage_stats: dict[str, dict[str, object]] = {}
    known_lineages: set[str] = set()
    occupied_nests_previous: set[int] = set()
    boom_threshold = max(24, initial_population * 2)
    first_birth_alerted = False
    first_matured_alerted = False
    structured_events: list[dict[str, object]] = []
    capture_telemetry = capture_dashboard or capture_research_data

    for agent in agents:
        lineage_id = agent.lineage_id or f"agent_{agent.agent_id}"
        lineage_stats[lineage_id] = {
            "lineage_id": lineage_id,
            "founder_agent_id": agent.agent_id,
            "total_births": 0,
            "peak_population": 1,
            "alive_now": 1,
            "extinct_tick": None,
        }
        known_lineages.add(lineage_id)

    if capture_telemetry:
        tick_summaries.append(
            _make_tick_summary(
                env,
                agents,
                tick=0,
                births=0,
                deaths=0,
            )
        )
        snapshots.append(
            _make_snapshot(
                env,
                agents,
                tick=0,
                births=0,
                deaths=0,
                death_positions=[],
            )
        )

    for _ in range(max_ticks):
        if stop_on_target_survivors and completed_survivors >= TARGET_SURVIVORS:
            break
        if not agents:
            break

        env.set_active_nest_owners(_occupied_nest_owner_ids(env, agents))
        env.step(rng)
        current_tick = env.tick_count
        current_day = current_tick // env.day_length
        tick_events: list[str] = []
        births_this_tick = 0
        deaths_this_tick = 0
        death_positions: list[tuple[int, int]] = []
        _update_social_groups(agents, tick_events, seen_groups)
        for agent in agents:
            agent.set_survival_context(env, agents)
        newborns: list[Agent] = []
        current_agents = list(agents)

        for agent in current_agents:
            wants_reproduction = agent.tick(env, rng)
            tick_events.extend(agent.pop_recent_events())
            if (
                agent.alive
                and agent.generation == 1
                and agent.sex == "female"
                and agent.current_stage == "adult"
                and not bool(agent.reproduction_debug.get("eligible", False))
            ):
                tick_events.append(
                    f"repro_fail -> tick={current_tick} day={current_day} "
                    f"id={agent.agent_id} gen={agent.generation} sex={agent.sex} age={agent.age} "
                    f"energy={agent.energy} mate={'yes' if agent.reproduction_debug.get('mate', False) else 'no'} "
                    f"near_nest={'yes' if agent.reproduction_debug.get('near_nest', False) else 'no'} "
                    f"nest_food={agent.reproduction_debug.get('nest_food', 0)} "
                    f"threshold={agent.reproduction_debug.get('threshold', 'na')} "
                    f"reason={agent.reproduction_debug.get('reason', 'unknown')}"
                )
            if agent.parent_id is not None and agent.age >= ADULT_AGE:
                if agent.agent_id not in matured_children:
                    matured_children.add(agent.agent_id)
                    if first_matured_child_tick is None:
                        first_matured_child_tick = current_tick
                        first_matured_child_day = current_day
                        tick_events.append(
                            f"matured_child -> tick={current_tick} day={current_day} "
                            f"child={agent.agent_id} parent={agent.parent_id}"
                        )

            if wants_reproduction and len(agents) + len(newborns) < max_population:
                mate = next(
                    (candidate for candidate in agents if candidate.agent_id == agent.reproduction_partner_id and candidate.alive),
                    None,
                )
                litter_size = min(
                    max_population - (len(agents) + len(newborns)),
                    agent.decide_litter_size(env, mate, rng),
                )
                agent.prepare_reproduction(env, mate, litter_size)
                litter_children: list[Agent] = []
                for _ in range(litter_size):
                    child = agent.spawn_child(next_agent_id, rng, env, mate=mate)
                    litter_children.append(child)
                    newborns.append(child)
                    next_agent_id += 1
                child = litter_children[0]
                if first_birth_tick is None:
                    first_birth_tick = current_tick
                    first_birth_day = current_day
                tick_events.append(
                    f"birth -> tick={current_tick} day={current_day} "
                    f"parent={agent.agent_id} other_parent={mate.agent_id if mate is not None else -1} "
                    f"role={agent.current_role} child={child.agent_id} generation={child.generation} litter_size={litter_size}"
                )
                total_births += litter_size
                births_this_tick += litter_size
                for child in litter_children:
                    lineage_id = child.lineage_id or f"agent_{child.agent_id}"
                    if lineage_id not in lineage_stats:
                        lineage_stats[lineage_id] = {
                            "lineage_id": lineage_id,
                            "founder_agent_id": child.agent_id,
                            "total_births": 0,
                            "peak_population": 1,
                            "alive_now": 0,
                            "extinct_tick": None,
                        }
                    lineage_stats[lineage_id]["total_births"] = int(lineage_stats[lineage_id]["total_births"]) + 1

            if not agent.alive:
                if agent.friend_ids:
                    tick_events.append(
                        f"agent {agent.agent_id} role={agent.current_role} "
                        f"died because {agent.death_reason}; grouped_with={sorted(agent.friend_ids)}"
                    )
                if agent.completed_lifespan:
                    completed_survivors += 1
                death_counts[agent.death_reason or "unknown"] += 1
                archived_agents.append(agent)
                deaths_this_tick += 1
                death_positions.append((agent.x, agent.y))
                agents.remove(agent)

        agents.extend(newborns)
        tick_events.extend(env.pop_physics_events())
        peak_population = max(peak_population, len(agents))
        if current_tick % 20 == 0:
            diagnostics = _gen1_reproduction_diagnostics(agents)
            block_text = ", ".join(
                f"{reason}={count}" for reason, count in sorted(diagnostics["blocks"].items())
            ) or "none"
            tick_events.append(
                f"gen1_status -> tick={current_tick} day={current_day} "
                f"adult_male={diagnostics['adult_male']} adult_female={diagnostics['adult_female']} "
                f"eligible_female={diagnostics['eligible_female']} blocks={block_text}"
            )
        if stop_on_generation_adult is not None:
            matured_target = next(
                (
                    agent
                    for agent in agents
                    if agent.alive and agent.current_stage == "adult" and agent.generation >= stop_on_generation_adult
                ),
                None,
            )
            if matured_target is not None:
                target_generation_reached = True
                target_generation_tick = current_tick
                tick_events.append(
                    f"generation_target_reached -> tick={current_tick} day={current_day} "
                    f"agent={matured_target.agent_id} generation={matured_target.generation}"
                )
        tick_events.extend(_detect_emergent_technology_events(env, current_tick, current_day))
        social_events.extend(tick_events)
        structured_events.extend(_normalize_event(event_text, current_tick) for event_text in tick_events)

        if first_technology_tick is None:
            for event_text in tick_events:
                if not event_text.startswith("technology_emerged ->"):
                    continue
                first_technology_tick = current_tick
                first_technology_day = current_day
                first_technology_name = _parse_technology_name(event_text)
                break

        if capture_telemetry:
            live_lineage_counts = _lineage_counts(agents)
            occupied_nests_current = _occupied_nest_owner_ids(env, agents)

            for lineage_id in known_lineages | set(live_lineage_counts):
                count = live_lineage_counts.get(lineage_id, 0)
                if lineage_id not in lineage_stats:
                    lineage_stats[lineage_id] = {
                        "lineage_id": lineage_id,
                        "founder_agent_id": -1,
                        "total_births": 0,
                        "peak_population": count,
                        "alive_now": count,
                        "extinct_tick": None,
                    }
                lineage_stats[lineage_id]["alive_now"] = count
                lineage_stats[lineage_id]["peak_population"] = max(
                    int(lineage_stats[lineage_id]["peak_population"]),
                    count,
                )
                if count == 0 and lineage_stats[lineage_id]["extinct_tick"] is None:
                    lineage_stats[lineage_id]["extinct_tick"] = current_tick
                    _append_alert(
                        alerts,
                        seen_alerts,
                        tick=current_tick,
                        alert_type="lineage_extinct",
                        message=f"{lineage_id} disappeared from the world",
                    )

            for agent in agents:
                _increment_heatmap(
                    population_heatmap,
                    agent.x,
                    agent.y,
                    bin_size=heatmap_bin_size,
                )
            for position in death_positions:
                _increment_heatmap(
                    death_heatmap,
                    position[0],
                    position[1],
                    bin_size=heatmap_bin_size,
                )
            for position in env.food_positions:
                _increment_heatmap(
                    food_heatmap,
                    position[0],
                    position[1],
                    bin_size=heatmap_bin_size,
                )

            for event in tick_events:
                if event.startswith("birth ->"):
                    if first_birth_tick == current_tick and not first_birth_alerted:
                        _append_alert(
                            alerts,
                            seen_alerts,
                            tick=current_tick,
                            alert_type="first_birth",
                            message=event,
                        )
                        first_birth_alerted = True
                elif event.startswith("matured_child ->"):
                    if first_matured_child_tick == current_tick and not first_matured_alerted:
                        _append_alert(
                            alerts,
                            seen_alerts,
                            tick=current_tick,
                            alert_type="first_matured_child",
                            message=event,
                        )
                        first_matured_alerted = True
                elif event.startswith("build_nest ->"):
                    _append_alert(
                        alerts,
                        seen_alerts,
                        tick=current_tick,
                        alert_type="new_settlement",
                        message=event,
                    )
                elif event.startswith("technology_emerged ->"):
                    _append_alert(
                        alerts,
                        seen_alerts,
                        tick=current_tick,
                        alert_type="technology_emerged",
                        message=event,
                    )
                elif event.startswith("gen1_status ->"):
                    _append_alert(
                        alerts,
                        seen_alerts,
                        tick=current_tick,
                        alert_type="gen1_status",
                        message=event,
                    )
                elif event.startswith("repro_fail ->"):
                    _append_alert(
                        alerts,
                        seen_alerts,
                        tick=current_tick,
                        alert_type="repro_fail",
                        message=event,
                    )

            for owner_id in occupied_nests_previous - occupied_nests_current:
                _append_alert(
                    alerts,
                    seen_alerts,
                    tick=current_tick,
                    alert_type="settlement_collapse",
                    message=f"nest owner={owner_id} no longer has active occupancy",
                )
            occupied_nests_previous = occupied_nests_current

            if len(agents) >= boom_threshold:
                _append_alert(
                    alerts,
                    seen_alerts,
                    tick=current_tick,
                    alert_type="population_boom",
                    message=f"population reached {len(agents)}",
                )
                boom_threshold += max(12, initial_population)

            if deaths_this_tick >= max(6, max(1, peak_population // 8)):
                _append_alert(
                    alerts,
                    seen_alerts,
                    tick=current_tick,
                    alert_type="mass_death",
                    message=f"{deaths_this_tick} agents died on tick {current_tick}",
                )

            tick_summaries.append(
                _make_tick_summary(
                    env,
                    agents,
                    tick=current_tick,
                    births=births_this_tick,
                    deaths=deaths_this_tick,
                )
            )

            should_snapshot = (
                current_tick % max(1, snapshot_interval) == 0
                or deaths_this_tick > 0
                or births_this_tick > 0
                or any(alert["tick"] == current_tick for alert in alerts[-4:])
                or current_tick == max_ticks
            )
            if should_snapshot:
                snapshots.append(
                    _make_snapshot(
                        env,
                        agents,
                        tick=current_tick,
                        births=births_this_tick,
                        deaths=deaths_this_tick,
                        death_positions=death_positions,
                    )
                )

        if target_generation_reached:
            break

    archived_agents.extend(agents)
    for agent in agents:
        if agent.alive:
            death_counts["simulation_ended"] += 1
        if agent.parent_id is not None and agent.age >= ADULT_AGE and agent.agent_id not in matured_children:
            matured_children.add(agent.agent_id)
            if first_matured_child_tick is None:
                first_matured_child_tick = env.tick_count
                first_matured_child_day = env.tick_count // env.day_length

    food_type_totals: Counter[str] = Counter()
    stored_food_total = 0
    gathered_material_totals: Counter[str] = Counter()
    emergent_technology_totals: Counter[str] = Counter()
    for agent in archived_agents:
        food_type_totals.update(agent.meals_by_type)
        stored_food_total += agent.stored_food_contributions
        gathered_material_totals.update(agent.gathered_materials)
        emergent_technology_totals.update(agent.technology_constructions)

    if capture_telemetry:
        final_tick = env.tick_count
        if not snapshots or snapshots[-1]["tick"] != final_tick:
            snapshots.append(
                _make_snapshot(
                    env,
                    agents,
                    tick=final_tick,
                    births=0,
                    deaths=0,
                    death_positions=[],
                )
            )
        if not tick_summaries or tick_summaries[-1]["tick"] != final_tick:
            tick_summaries.append(
                _make_tick_summary(
                    env,
                    agents,
                    tick=final_tick,
                    births=0,
                    deaths=0,
                )
            )

        run_name = dashboard_run_name or f"body_{body_index}_dashboard"
        output_dir = DASHBOARDS_DIR / dashboard_group / run_name
        payload = {
            "meta": {
                "title": dashboard_title,
                "seed": dashboard_seed,
                "body_name": f"body_{body_index}",
                "body_design": body.short_description,
                "body_stats": body.stats_description,
                "peak_population": peak_population,
                "total_births": total_births,
                "final_tick": env.tick_count,
            },
            "world": {
                "width": env.width,
                "height": env.height,
                "biomes": [
                    {
                        "name": "safe_low_food",
                        "x": 0,
                        "y": 0,
                        "width": env.width // 2,
                        "height": env.height // 2,
                        "color": "#dce8cc",
                    },
                    {
                        "name": "safe_high_food",
                        "x": env.width // 2,
                        "y": 0,
                        "width": env.width - (env.width // 2),
                        "height": env.height // 2,
                        "color": "#a9d67f",
                    },
                    {
                        "name": "danger_high_food",
                        "x": 0,
                        "y": env.height // 2,
                        "width": env.width // 2,
                        "height": env.height - (env.height // 2),
                        "color": "#f6b26b",
                    },
                    {
                        "name": "danger_low_food",
                        "x": env.width // 2,
                        "y": env.height // 2,
                        "width": env.width - (env.width // 2),
                        "height": env.height - (env.height // 2),
                        "color": "#b85c38",
                    },
                ],
            },
            "tick_summaries": tick_summaries,
            "snapshots": snapshots,
            "alerts": [
                alert
                for alert in alerts
                if alert["type"] in {
                    "new_settlement",
                    "settlement_collapse",
                    "first_birth",
                    "first_matured_child",
                    "population_boom",
                    "mass_death",
                    "technology_emerged",
                    "lineage_extinct",
                    "gen1_status",
                    "repro_fail",
                }
            ],
            "lineage_stats": sorted(
                lineage_stats.values(),
                key=lambda item: (-(int(item["peak_population"])), str(item["lineage_id"])),
            ),
            "heatmaps": {
                "population": population_heatmap,
                "death": death_heatmap,
                "food": food_heatmap,
            },
        }
        dashboard_file, telemetry_file = build_dashboard_artifacts(output_dir, payload)
        dashboard_path = str(dashboard_file)
        telemetry_path = str(telemetry_file)

    if capture_research_data:
        run_name = research_run_name or f"body_{body_index}_research"
        research_output_dir = RESEARCH_RUNS_DIR / run_name
        lineage_rollup: dict[str, dict[str, object]] = {}
        lineage_trait_totals: defaultdict[str, float] = defaultdict(float)
        lineage_morph_totals: defaultdict[str, float] = defaultdict(float)
        for item in lineage_stats.values():
            lineage_rollup[str(item["lineage_id"])] = {
                "lineage_id": str(item["lineage_id"]),
                "founder_agent_id": item["founder_agent_id"],
                "total_births": item["total_births"],
                "peak_population": item["peak_population"],
                "alive_now": item["alive_now"],
                "extinct_tick": item["extinct_tick"],
                "completed_lifespans": 0,
                "total_agents_observed": 0,
                "mean_final_age": 0.0,
                "mean_brain_capacity": 0.0,
                "mean_memory_retention": 0.0,
                "mean_planning_focus": 0.0,
                "mean_cooperation_drive": 0.0,
                "mean_parenting_instinct": 0.0,
                "mean_curiosity": 0.0,
                "mean_fear": 0.0,
                "mean_aggression": 0.0,
                "mean_metabolism_rate": 0.0,
                "mean_plant_efficiency": 0.0,
                "mean_meat_efficiency": 0.0,
                "mean_reproduction_drive": 0.0,
                "mean_reproduction_investment": 0.0,
                "mean_sensor_units": 0.0,
                "mean_muscle_units": 0.0,
                "mean_armor_units": 0.0,
                "mean_brain_units": 0.0,
            }

        agent_outcomes: list[dict[str, object]] = []
        lineage_age_totals: defaultdict[str, float] = defaultdict(float)
        generation_trait_rollup: dict[int, dict[str, float]] = {}
        for agent in archived_agents:
            lineage_id = agent.lineage_id or f"agent_{agent.agent_id}"
            if lineage_id not in lineage_rollup:
                lineage_rollup[lineage_id] = {
                    "lineage_id": lineage_id,
                    "founder_agent_id": agent.agent_id if agent.parent_id is None else -1,
                    "total_births": 0,
                    "peak_population": 0,
                    "alive_now": 0,
                    "extinct_tick": None,
                    "completed_lifespans": 0,
                    "total_agents_observed": 0,
                    "mean_final_age": 0.0,
                    "mean_brain_capacity": 0.0,
                    "mean_memory_retention": 0.0,
                    "mean_planning_focus": 0.0,
                    "mean_cooperation_drive": 0.0,
                    "mean_parenting_instinct": 0.0,
                    "mean_curiosity": 0.0,
                    "mean_fear": 0.0,
                    "mean_aggression": 0.0,
                    "mean_metabolism_rate": 0.0,
                    "mean_plant_efficiency": 0.0,
                    "mean_meat_efficiency": 0.0,
                    "mean_reproduction_drive": 0.0,
                    "mean_reproduction_investment": 0.0,
                    "mean_sensor_units": 0.0,
                    "mean_muscle_units": 0.0,
                    "mean_armor_units": 0.0,
                    "mean_brain_units": 0.0,
                }
            lineage_rollup[lineage_id]["total_agents_observed"] = int(lineage_rollup[lineage_id]["total_agents_observed"]) + 1
            if agent.completed_lifespan:
                lineage_rollup[lineage_id]["completed_lifespans"] = int(lineage_rollup[lineage_id]["completed_lifespans"]) + 1
            lineage_age_totals[lineage_id] += agent.age
            for trait_name, value in agent.body.trait_values.items():
                lineage_trait_totals[f"{lineage_id}:{trait_name}"] += value
            for morph_name, value in agent.body.morphology_values.items():
                lineage_morph_totals[f"{lineage_id}:{morph_name}"] += value

            generation_bucket = generation_trait_rollup.setdefault(
                agent.generation,
                {
                    "generation": agent.generation,
                    "agent_count": 0.0,
                    "adult_count": 0.0,
                    "mean_sensor_units": 0.0,
                    "mean_muscle_units": 0.0,
                    "mean_armor_units": 0.0,
                    "mean_brain_units": 0.0,
                    "mean_brain_capacity": 0.0,
                    "mean_memory_retention": 0.0,
                    "mean_planning_focus": 0.0,
                    "mean_cooperation_drive": 0.0,
                    "mean_parenting_instinct": 0.0,
                    "mean_curiosity": 0.0,
                    "mean_fear": 0.0,
                    "mean_aggression": 0.0,
                    "mean_metabolism_rate": 0.0,
                    "mean_plant_efficiency": 0.0,
                    "mean_meat_efficiency": 0.0,
                    "mean_reproduction_drive": 0.0,
                    "mean_reproduction_investment": 0.0,
                    "mean_trait_mutation_count": 0.0,
                    "mean_morphology_mutation_count": 0.0,
                },
            )
            generation_bucket["agent_count"] += 1.0
            if agent.age >= ADULT_AGE:
                generation_bucket["adult_count"] += 1.0
            for morph_name, value in agent.body.morphology_values.items():
                generation_bucket[f"mean_{morph_name}"] += value
            for trait_name, value in agent.body.trait_values.items():
                generation_bucket[f"mean_{trait_name}"] += value
            generation_bucket["mean_trait_mutation_count"] += agent.body.trait_mutation_count
            generation_bucket["mean_morphology_mutation_count"] += agent.body.morphology_mutation_count

            agent_outcomes.append(
                {
                    "agent_id": agent.agent_id,
                    "lineage_id": lineage_id,
                    "parent_id": agent.parent_id,
                    "other_parent_id": agent.other_parent_id,
                    "sex": agent.sex,
                    "generation": agent.generation,
                    "immortal": agent.immortal,
                    "preferred_role": agent.preferred_role,
                    "final_role": agent.current_role,
                    "friend_count": len(agent.friend_ids),
                    "instinct_state": agent.instinct_state,
                    "hunger_stress_ticks": agent.hunger_stress_ticks,
                    "cold_stress_ticks": agent.cold_stress_ticks,
                    "fear_stress_ticks": agent.fear_stress_ticks,
                    "carried_seed_id": agent.carried_seed_id,
                    "safety_feeling": round(agent.safety_feeling, 3),
                    "comfort_level": round(agent.comfort_level, 3),
                    "attachment_level": round(agent.attachment_level, 3),
                    "hunger_level": round(agent.hunger_level, 3),
                    "fear_level": round(agent.fear_level, 3),
                    "cold_level": round(agent.cold_level, 3),
                    "wetness": round(agent.wetness, 3),
                    "body_temperature_k": round(agent.body_temperature_k, 3),
                    "safety_streak_ticks": agent.safety_streak_ticks,
                    "pair_bond_ticks": agent.pair_bond_ticks,
                    "body_profile": agent.body.trait_profile,
                    "body_inherited_from_profiles": agent.body.inherited_from_profiles,
                    "body_trait_mutation_count": agent.body.trait_mutation_count,
                    "body_morphology_mutation_count": agent.body.morphology_mutation_count,
                    "body_units_json": agent.body.morphology_values,
                    "body_traits_json": agent.body.trait_values,
                    "remembered_food_sources_count": len(agent.remembered_food_sources),
                    "remembered_safe_zones_count": len(agent.remembered_safe_zones),
                    "remembered_danger_count": len(agent.remembered_danger),
                    "remembered_nest_locations_count": len(agent.remembered_nest_locations),
                    "age": agent.age,
                    "children_count": agent.children_count,
                    "food_eaten": agent.food_eaten,
                    "distance_traveled": agent.distance_traveled,
                    "stored_food_contributions": agent.stored_food_contributions,
                    "matured_offspring_count": agent.matured_offspring_count,
                    "alive": agent.alive,
                    "completed_lifespan": agent.completed_lifespan,
                    "death_reason": agent.death_reason,
                    "final_x": agent.x,
                    "final_y": agent.y,
                    "meals_by_type_json": agent.meals_by_type,
                    "gathered_materials_json": agent.gathered_materials,
                    "technology_constructions_json": agent.technology_constructions,
                    "technology_uses_json": agent.technology_uses,
                }
            )

        for lineage_id, row in lineage_rollup.items():
            observed = int(row["total_agents_observed"])
            row["mean_final_age"] = round(lineage_age_totals[lineage_id] / observed, 3) if observed else 0.0
            if observed:
                for trait_name in (
                    "brain_capacity",
                    "memory_retention",
                    "planning_focus",
                    "cooperation_drive",
                    "parenting_instinct",
                    "curiosity",
                    "fear",
                    "aggression",
                    "metabolism_rate",
                    "plant_efficiency",
                    "meat_efficiency",
                    "reproduction_drive",
                    "reproduction_investment",
                ):
                    row[f"mean_{trait_name}"] = round(lineage_trait_totals[f"{lineage_id}:{trait_name}"] / observed, 4)
                for morph_name in ("sensor_units", "muscle_units", "armor_units", "brain_units"):
                    row[f"mean_{morph_name}"] = round(lineage_morph_totals[f"{lineage_id}:{morph_name}"] / observed, 4)

        generation_trait_rows: list[dict[str, object]] = []
        for generation in sorted(generation_trait_rollup):
            row = generation_trait_rollup[generation]
            count = row["agent_count"] or 1.0
            generation_trait_rows.append(
                {
                    key: (
                        round(value / count, 4)
                        if key.startswith("mean_")
                        else int(value)
                        if key in {"generation", "agent_count", "adult_count"}
                        else value
                    )
                    for key, value in row.items()
                }
            )

        research_payload = {
            "metadata": {
                "run_name": run_name,
                "change_note": research_change_note,
                "condition_id": research_condition_id,
                "condition_label": research_condition_label,
                "research_question": research_question,
                "seed": research_seed,
                "python_version": sys.version,
                "platform": platform.platform(),
                "git_revision": _git_revision(),
                "body_name": f"body_{body_index}",
                "body_design": body.short_description,
                "body_stats": body.stats_description,
                "world_width": env.width,
                "world_height": env.height,
                "day_length": env.day_length,
                "season_length": env.season_length,
                "max_food": env.max_food,
                "max_large_animals": env.max_large_animals,
                "initial_population": initial_population,
                "max_population": max_population,
                "max_ticks_requested": max_ticks,
                "final_tick": env.tick_count,
                "snapshot_interval": snapshot_interval,
                "spawn_strategy": spawn_strategy,
                "founder_mode": "explicit" if founder_sexes is not None else "default_alternating",
                "male_founders": sum(1 for value in founder_sexes if value == "male") if founder_sexes is not None else sum(1 for agent in archived_agents if agent.parent_id is None and agent.sex == "male"),
                "female_founders": sum(1 for value in founder_sexes if value == "female") if founder_sexes is not None else sum(1 for agent in archived_agents if agent.parent_id is None and agent.sex == "female"),
                "stop_on_generation_adult": stop_on_generation_adult,
                "immortal_agents": immortal_agents,
                "environment_overrides": env_kwargs or {},
                "world_physics_v2": True,
            },
            "summary": {
                "achieved_survivors": completed_survivors,
                "peak_population": peak_population,
                "total_births": total_births,
                "matured_children": len(matured_children),
                "completed_lineages": sum(1 for agent in archived_agents if agent.completed_lifespan),
                "average_age": sum(agent.age for agent in archived_agents) / len(archived_agents),
                "average_food_eaten": sum(agent.food_eaten for agent in archived_agents) / len(archived_agents),
                "average_children": sum(agent.children_count for agent in archived_agents) / len(archived_agents),
                "food_type_totals": dict(food_type_totals),
                "stored_food_total": stored_food_total,
                "gathered_material_totals": dict(gathered_material_totals),
                "emergent_technology_totals": dict(emergent_technology_totals),
                "death_reasons": dict(death_counts),
                "first_birth_tick": first_birth_tick,
                "first_birth_day": first_birth_day,
                "first_matured_child_tick": first_matured_child_tick,
                "first_matured_child_day": first_matured_child_day,
                "first_technology_tick": first_technology_tick,
                "first_technology_day": first_technology_day,
                "first_technology_name": first_technology_name,
                "final_tick": env.tick_count,
                "population_extinct": not any(agent.alive for agent in agents),
                "target_generation_reached": target_generation_reached,
                "target_generation_tick": target_generation_tick,
                "final_population": len(agents),
            },
            "tick_metrics": tick_summaries,
            "events": structured_events,
            "lineages": sorted(lineage_rollup.values(), key=lambda item: (-int(item["peak_population"]), str(item["lineage_id"]))),
            "agent_outcomes": agent_outcomes,
            "generation_traits": generation_trait_rows,
            "dashboard_payload": {
                "meta": {
                    "title": dashboard_title,
                    "seed": research_seed,
                    "body_name": f"body_{body_index}",
                    "body_design": body.short_description,
                    "body_stats": body.stats_description,
                    "peak_population": peak_population,
                    "total_births": total_births,
                    "final_tick": env.tick_count,
                },
                "world": {
                    "width": env.width,
                    "height": env.height,
                    "physics": {
                        "ambient_temperature_k": env.get_cell_temperature(0, 0),
                        "material_model": "field_and_object_thermal_physics_v2",
                    },
                    "biomes": [
                        {"name": "safe_low_food", "x": 0, "y": 0, "width": env.width // 2, "height": env.height // 2, "color": "#dce8cc"},
                        {"name": "safe_high_food", "x": env.width // 2, "y": 0, "width": env.width - (env.width // 2), "height": env.height // 2, "color": "#a9d67f"},
                        {"name": "danger_high_food", "x": 0, "y": env.height // 2, "width": env.width // 2, "height": env.height - (env.height // 2), "color": "#f6b26b"},
                        {"name": "danger_low_food", "x": env.width // 2, "y": env.height // 2, "width": env.width - (env.width // 2), "height": env.height - (env.height // 2), "color": "#b85c38"},
                    ],
                },
                "tick_summaries": tick_summaries,
                "snapshots": snapshots,
                "alerts": alerts,
                "lineage_stats": sorted(lineage_rollup.values(), key=lambda item: (-int(item["peak_population"]), str(item["lineage_id"]))),
                "heatmaps": {
                    "population": population_heatmap,
                    "death": death_heatmap,
                    "food": food_heatmap,
                },
            },
        }
        manifest = write_research_artifacts(research_output_dir, research_payload)
        research_manifest_path = manifest["manifest"]
        if not dashboard_path and manifest.get("dashboard_html"):
            dashboard_path = manifest["dashboard_html"]
        if not telemetry_path and manifest.get("dashboard_json"):
            telemetry_path = manifest["dashboard_json"]

    return ExperimentResult(
        body_name=f"body_{body_index}",
        body_design=body.short_description,
        body_stats=body.stats_description,
        target_survivors=TARGET_SURVIVORS,
        achieved_survivors=completed_survivors,
        peak_population=peak_population,
        total_births=total_births,
        matured_children=len(matured_children),
        final_tick=env.tick_count,
        first_birth_tick=first_birth_tick,
        first_birth_day=first_birth_day,
        first_matured_child_tick=first_matured_child_tick,
        first_matured_child_day=first_matured_child_day,
        completed_lineages=sum(1 for agent in archived_agents if agent.completed_lifespan),
        average_age=sum(agent.age for agent in archived_agents) / len(archived_agents),
        average_food_eaten=sum(agent.food_eaten for agent in archived_agents) / len(archived_agents),
        average_children=sum(agent.children_count for agent in archived_agents) / len(archived_agents),
        food_type_totals=dict(food_type_totals),
        stored_food_total=stored_food_total,
        gathered_material_totals=dict(gathered_material_totals),
        emergent_technology_totals=dict(emergent_technology_totals),
        death_reasons=dict(death_counts),
        reached_target=completed_survivors >= TARGET_SURVIVORS,
        social_events=social_events,
        first_technology_tick=first_technology_tick,
        first_technology_day=first_technology_day,
        first_technology_name=first_technology_name,
        population_extinct=not any(agent.alive for agent in agents),
        target_generation_reached=target_generation_reached,
        target_generation_tick=target_generation_tick,
        dashboard_path=dashboard_path,
        telemetry_path=telemetry_path,
        research_manifest_path=research_manifest_path,
    )


def _spawn_initial_positions(
    env: Environment,
    rng: Random,
    count: int,
    body: BodyPlan,
    strategy: str = "default",
) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    anchor_x = rng.randrange(env.width)
    anchor_y = rng.randrange(env.height)

    if strategy == "frontier_safe_high_food":
        for _ in range(400):
            candidate_x = rng.randrange(env.width // 2, env.width)
            candidate_y = rng.randrange(max(0, (env.height // 2) - env.frontier_band - 2), env.height // 2)
            if env.get_biome(candidate_x, candidate_y) == ZONE_SAFE_HIGH_FOOD and env.is_frontier_area(candidate_x, candidate_y):
                anchor_x = candidate_x
                anchor_y = candidate_y
                break
    elif body.cognition_score >= 4.2:
        for _ in range(200):
            candidate_x = rng.randrange(env.width)
            candidate_y = rng.randrange(env.height)
            if env.get_biome(candidate_x, candidate_y) == ZONE_SAFE_HIGH_FOOD:
                anchor_x = candidate_x
                anchor_y = candidate_y
                break
    else:
        for _ in range(100):
            candidate_x = rng.randrange(env.width)
            candidate_y = rng.randrange(env.height)
            if env.is_walkable(candidate_x, candidate_y):
                anchor_x = candidate_x
                anchor_y = candidate_y
                break

    while len(positions) < count:
        radius = 4 if body.social_score >= 1.2 else 6
        x = max(0, min(env.width - 1, anchor_x + rng.randrange(-radius, radius + 1)))
        y = max(0, min(env.height - 1, anchor_y + rng.randrange(-radius, radius + 1)))
        if env.is_walkable(x, y):
            positions.append((x, y))

    return positions


def _update_social_groups(
    agents: list[Agent],
    social_events: list[str],
    seen_groups: set[frozenset[int]],
) -> None:
    for agent in agents:
        agent.reset_social_state()

    cooperative_agents = [agent for agent in agents if agent.can_cooperate()]
    visited: set[int] = set()
    next_group_id = 1

    for agent in cooperative_agents:
        if agent.agent_id in visited:
            continue

        stack = [agent]
        members: list[Agent] = []

        while stack:
            current = stack.pop()
            if current.agent_id in visited:
                continue
            visited.add(current.agent_id)
            members.append(current)

            for other in cooperative_agents:
                if other.agent_id in visited:
                    continue
                if _are_neighbors(current, other):
                    stack.append(other)

        if len(members) < 2:
            continue

        members.sort(key=lambda item: item.agent_id)
        roles = _assign_roles(members)
        for member in members:
            member.join_group(next_group_id, roles[member.agent_id], members)

        group_signature = frozenset(member.agent_id for member in members)
        if group_signature not in seen_groups:
            seen_groups.add(group_signature)
            social_events.append(
                "group formed -> "
                f"members={sorted(group_signature)} "
                f"roles={', '.join(f'{member.agent_id}:{roles[member.agent_id]}' for member in members)}"
            )
        next_group_id += 1


def _assign_roles(members: list[Agent]) -> dict[int, str]:
    assignments: dict[int, str] = {}

    sorted_members = sorted(members, key=lambda item: item.agent_id)
    for member in sorted_members:
        assignments[member.agent_id] = member.preferred_role

    planners = [member for member in sorted_members if member.body.planning_focus >= 0.75]
    scouts = [member for member in sorted_members if member.body.sensor_units >= 3 or member.body.curiosity >= 0.7]

    if planners:
        assignments[planners[0].agent_id] = "planner"
    if scouts:
        scout = scouts[0]
        if assignments[scout.agent_id] == scout.preferred_role:
            assignments[scout.agent_id] = "scout"

    return assignments


def _are_neighbors(left: Agent, right: Agent) -> bool:
    return abs(left.x - right.x) + abs(left.y - right.y) <= 3


def save_results(
    results: list[ExperimentResult],
    survivors: list[ExperimentResult],
    seed: int,
    experiment: ExperimentRun,
) -> None:
    payload = {
        "experiment_number": experiment.experiment_number,
        "change_note": experiment.change_note,
        "started_at": experiment.started_at,
        "seed": seed,
        "max_age": MAX_AGE,
        "target_survivors": TARGET_SURVIVORS,
        "target_body_types": TARGET_BODY_TYPES,
        "initial_population": INITIAL_POPULATION,
        "max_population": MAX_POPULATION,
        "max_ticks": MAX_TICKS,
        "tested_body_candidates": len(results),
        "qualified_body_types": len(survivors),
        "survivors": [asdict(item) for item in survivors],
        "all_results": [asdict(item) for item in results],
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    (DATA_DIR / "survivor_body_search.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Survivor Body Types",
        "",
        f"Qualified body types: {len(survivors)}/{TARGET_BODY_TYPES}",
        "",
    ]
    for index, item in enumerate(survivors, start=1):
        lines.append(
            f"{index}. {item.body_name} | {item.body_design} | {item.body_stats} | "
            f"achieved={item.achieved_survivors}/{item.target_survivors}"
        )

    (DATA_DIR / "survivor_body_types.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def _save_distinct_survivor_search(
    experiment: ExperimentRun,
    start_seed: int,
    target_body_types: int,
    max_seed_rounds: int,
    max_stagnation_rounds: int,
    records: list[DistinctSurvivorRecord],
    seed_summaries: list[dict[str, int]],
) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "experiment_number": experiment.experiment_number,
        "change_note": experiment.change_note,
        "started_at": experiment.started_at,
        "start_seed": start_seed,
        "target_body_types": target_body_types,
        "max_seed_rounds": max_seed_rounds,
        "max_stagnation_rounds": max_stagnation_rounds,
        "found_distinct_body_types": len(records),
        "records": [asdict(record) for record in records],
        "seed_summaries": seed_summaries,
    }

    (DATA_DIR / "distinct_survivor_search.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Distinct Survivor Search",
        "",
        f"Found distinct body types: {len(records)}/{target_body_types}",
        f"Start seed: {start_seed}",
        f"Max seed rounds: {max_seed_rounds}",
        f"Max stagnation rounds: {max_stagnation_rounds}",
        "",
        "## Distinct Survivor Bodies",
        "",
    ]
    if records:
        for index, record in enumerate(records, start=1):
            lines.append(
                f"{index}. {record.body_name} | {record.body_design} | {record.body_stats} | "
                f"first_found_seed={record.first_found_seed} | births={record.total_births} | "
                f"matured_children={record.matured_children} | "
                f"first_birth_day={record.first_birth_day} | "
                f"first_matured_day={record.first_matured_child_day}"
            )
    else:
        lines.append("No distinct survivor bodies found.")

    lines.extend(["", "## Seed Summary", ""])
    for item in seed_summaries:
        lines.append(
            f"- seed={item['seed']} | qualifying={item['qualifying_bodies']} | "
            f"new_distinct={item['new_distinct_bodies']} | total_distinct={item['total_distinct_bodies']}"
        )

    (DATA_DIR / "distinct_survivor_search.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def _save_massive_lineage_search(
    experiment: ExperimentRun,
    start_seed: int,
    target_body_types: int,
    founder_population_steps: tuple[int, ...],
    max_population_multiplier: int,
    max_ticks: int,
    max_seed_rounds: int,
    records: list[LineageBodyRecord],
) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "experiment_number": experiment.experiment_number,
        "change_note": experiment.change_note,
        "started_at": experiment.started_at,
        "start_seed": start_seed,
        "target_body_types": target_body_types,
        "founder_population_steps": list(founder_population_steps),
        "max_population_multiplier": max_population_multiplier,
        "max_ticks": max_ticks,
        "max_seed_rounds": max_seed_rounds,
        "found_lineage_body_types": len(records),
        "records": [asdict(record) for record in records],
    }

    (DATA_DIR / "massive_lineage_search.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Massive Lineage Search",
        "",
        f"Found lineage-capable body types: {len(records)}/{target_body_types}",
        f"Start seed: {start_seed}",
        f"Founder steps: {founder_population_steps}",
        f"Max population multiplier: {max_population_multiplier}",
        f"Max ticks: {max_ticks}",
        f"Max seed rounds: {max_seed_rounds}",
        "",
        "## Successful Bodies",
        "",
    ]
    if records:
        for index, record in enumerate(records, start=1):
            lines.append(
                f"{index}. {record.body_name} | {record.body_design} | {record.body_stats} | "
                f"seed={record.first_found_seed} | founders={record.founder_population} | "
                f"max_pop={record.max_population} | births={record.total_births} | "
                f"matured_children={record.matured_children} | achieved={record.achieved_survivors} | "
                f"first_birth_day={record.first_birth_day} | "
                f"first_matured_day={record.first_matured_child_day}"
            )
    else:
        lines.append("No lineage-capable body types found.")

    (DATA_DIR / "massive_lineage_search.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def _save_first_tool_emergence_study(
    experiment: ExperimentRun,
    start_seed: int,
    seed_count: int,
    body_index: int,
    body: BodyPlan,
    max_ticks: int,
    env_kwargs: dict[str, object],
    records: list[FirstToolEmergenceRecord],
) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    successful = [record for record in records if record.first_technology_tick is not None]
    successful_ticks = [
        record.first_technology_tick for record in successful if record.first_technology_tick is not None
    ]
    mean_tick = round(sum(successful_ticks) / len(successful_ticks), 2) if successful_ticks else None
    min_tick = min(successful_ticks) if successful_ticks else None
    max_tick = max(successful_ticks) if successful_ticks else None

    payload = {
        "experiment_number": experiment.experiment_number,
        "change_note": experiment.change_note,
        "started_at": experiment.started_at,
        "start_seed": start_seed,
        "seed_count": seed_count,
        "body_index": body_index,
        "body_design": body.short_description,
        "body_stats": body.stats_description,
        "max_ticks": max_ticks,
        "environment": env_kwargs,
        "successful_technology_emergence_runs": len(successful),
        "mean_first_technology_tick": mean_tick,
        "min_first_technology_tick": min_tick,
        "max_first_technology_tick": max_tick,
        "records": [asdict(record) for record in records],
    }

    (DATA_DIR / "first_technology_emergence_study.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Emergent Technology Study",
        "",
        f"Body index: {body_index}",
        f"Body: {body.short_description}",
        f"Seeds: {seed_count} starting from {start_seed}",
        f"Max ticks: {max_ticks}",
        f"Successful runs: {len(successful)}/{len(records)}",
        f"Mean first-technology tick: {mean_tick}",
        f"Min first-technology tick: {min_tick}",
        f"Max first-technology tick: {max_tick}",
        "",
        "## Per-Seed Results",
        "",
    ]
    for record in records:
        lines.append(
            f"- seed={record.seed} | technology={record.first_technology_name} | tick={record.first_technology_tick} | "
            f"day={record.first_technology_day} | births={record.total_births} | peak_pop={record.peak_population}"
        )

    (DATA_DIR / "first_technology_emergence_study.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def start_experiment_run(change_note: str) -> ExperimentRun:
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)

    if HISTORY_PATH.exists():
        history = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    else:
        history = {"last_experiment_number": 0, "runs": []}

    experiment_number = int(history.get("last_experiment_number", 0)) + 1
    started_at = datetime.now().isoformat(timespec="seconds")

    return ExperimentRun(
        experiment_number=experiment_number,
        change_note=change_note,
        started_at=started_at,
        log_lines=[],
    )


def log(experiment: ExperimentRun, message: str) -> None:
    print(message)
    experiment.log_lines.append(message)


def finalize_experiment_run(
    experiment: ExperimentRun,
    results: list[ExperimentResult],
    survivors: list[ExperimentResult],
    seed: int,
) -> None:
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)

    if HISTORY_PATH.exists():
        history = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    else:
        history = {"last_experiment_number": 0, "runs": []}

    history["last_experiment_number"] = experiment.experiment_number
    history["runs"].append(
        {
            "experiment_number": experiment.experiment_number,
            "change_note": experiment.change_note,
            "started_at": experiment.started_at,
            "seed": seed,
            "qualified_body_types": len(survivors),
            "tested_body_candidates": len(results),
        }
    )
    HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")

    experiment_path = EXPERIMENTS_DIR / f"experiment_{experiment.experiment_number:03d}.md"
    lines = [
        f"# Experiment {experiment.experiment_number}",
        "",
        f"- Started at: {experiment.started_at}",
        f"- Change note: {experiment.change_note}",
        f"- Seed: {seed}",
        f"- Tested body candidates: {len(results)}",
        f"- Qualified body types: {len(survivors)}",
        "",
        "## Run Log",
        "",
    ]
    lines.extend(experiment.log_lines)
    experiment_path.write_text("\n".join(lines), encoding="utf-8")
