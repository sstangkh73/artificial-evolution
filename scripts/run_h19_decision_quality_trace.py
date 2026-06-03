from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
import json
from pathlib import Path
from random import Random
import statistics
import sys
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for path in (PROJECT_ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import agents.agent as agent_mod
from agents.agent import Agent
from agents.body import generate_candidate_body_plans
from simulation import runner as runner_mod
from world.environment import Environment

import run_reproduction_chain_diagnostics as chain_diag


OUTPUT_ROOT = PROJECT_ROOT / "data" / "hypothesis_diagnostics" / "h19_decision_quality_2026-06-03"
REPORT_PATH = PROJECT_ROOT / "reports" / "h19_decision_quality_trace_2026-06-03.md"


@dataclass(frozen=True)
class TraceCondition:
    condition_id: str
    hypothesis: str
    label: str
    description: str
    patches: tuple[str, ...] = ()


@dataclass
class FemaleDecisionStats:
    agent_id: int
    generation: int
    lineage_id: str | None
    first_adult_tick: int | None = None
    adult_ticks: int = 0
    exact_ready_ticks: int = 0
    wants_reproduction_ticks: int = 0
    spawn_events: int = 0
    spawned_children: int = 0
    ready_no_want_ticks: int = 0
    want_no_spawn_ticks: int = 0
    first_ready_tick: int | None = None
    first_spawn_tick: int | None = None
    gate_samples: int = 0
    gate_ok_counts: Counter[str] | None = None
    block_reasons: Counter[str] | None = None

    def __post_init__(self) -> None:
        if self.gate_ok_counts is None:
            self.gate_ok_counts = Counter()
        if self.block_reasons is None:
            self.block_reasons = Counter()


def trace_conditions() -> list[TraceCondition]:
    return [
        TraceCondition("baseline", "baseline", "Current baseline", "No intervention."),
        TraceCondition("h11_extend_reproductive_life", "H11", "Lifetime opportunity reference", "H11 from previous suite.", ("h11_extend_reproductive_life",)),
        TraceCondition("h13_parent_child_overlap", "H13", "Parent-child overlap", "Shorten development and extend adult overlap.", ("h13_parent_child_overlap",)),
        TraceCondition("h16_energy_debt_relief", "H16", "Energy debt relief", "Reduce early energy drain.", ("h16_energy_debt_relief",)),
        TraceCondition("h17_lower_birth_cost", "H17", "Lower birth cost", "Reduce birth energy and nest food cost.", ("h17_lower_birth_cost",)),
        TraceCondition("i_h13_h17", "Interaction", "H13 + H17", "Parent-child overlap plus lower birth cost.", ("h13_parent_child_overlap", "h17_lower_birth_cost")),
        TraceCondition("i_h16_h17", "Interaction", "H16 + H17", "Energy debt relief plus lower birth cost.", ("h16_energy_debt_relief", "h17_lower_birth_cost")),
        TraceCondition("i_h1_h11", "H1+H11", "Best prior second-wave signal", "Prior best condition with gen1 births in seed 7.", ("h1_breeder_tuned", "h11_extend_reproductive_life")),
        TraceCondition("i_h1_h11_h14_h17", "Interaction", "H1 + H11 + H14 + H17", "High first-wave births/matured but no gen1 births.", ("h1_breeder_tuned", "h11_extend_reproductive_life", "h14_food_liquidity", "h17_lower_birth_cost")),
    ]


def run_trace_trial(
    *,
    condition: TraceCondition,
    seed: int,
    body_index: int,
    initial_population: int,
    max_population: int,
    max_ticks: int,
) -> dict[str, object]:
    rng = Random(seed)
    body = generate_candidate_body_plans()[body_index - 1]
    env = Environment()
    spawn_positions = runner_mod._spawn_initial_positions(env, rng, initial_population, body, strategy="default")
    agents: list[Agent] = [
        Agent(
            agent_id=agent_id,
            body=body,
            x=x,
            y=y,
            age=agent_mod.ADULT_AGE + 6,
            lineage_id=runner_mod._lineage_label(agent_id),
            sex="female" if agent_id % 2 == 0 else "male",
            generation=0,
        )
        for agent_id, (x, y) in enumerate(spawn_positions)
    ]

    next_agent_id = len(agents)
    archived_agents: list[Agent] = []
    death_counts: Counter[str] = Counter()
    event_counts: Counter[str] = Counter()
    total_births = 0
    matured_children: set[int] = set()
    child_parent: dict[int, int | None] = {}
    births_by_mother_generation: Counter[int] = Counter()
    matured_by_child_generation: Counter[int] = Counter()
    first_birth_tick: int | None = None
    first_gen1_ready_tick: int | None = None
    first_gen1_spawn_tick: int | None = None
    first_matured_child_tick: int | None = None
    peak_population = len(agents)

    female_stats: dict[int, FemaleDecisionStats] = {}
    decision_trace_rows: list[dict[str, object]] = []
    generation_gate_samples: Counter[int] = Counter()
    generation_gate_ok_counts: dict[int, Counter[str]] = defaultdict(Counter)
    generation_block_reasons: dict[int, Counter[str]] = defaultdict(Counter)
    spawn_block_reasons: Counter[str] = Counter()

    def ensure_female(agent: Agent) -> FemaleDecisionStats:
        if agent.agent_id not in female_stats:
            female_stats[agent.agent_id] = FemaleDecisionStats(
                agent_id=agent.agent_id,
                generation=agent.generation,
                lineage_id=agent.lineage_id,
            )
        return female_stats[agent.agent_id]

    for agent in agents:
        if agent.sex == "female":
            ensure_female(agent)

    for _ in range(max_ticks):
        if not agents:
            break

        env.set_active_nest_owners(runner_mod._occupied_nest_owner_ids(env, agents))
        env.step(rng)
        current_tick = env.tick_count
        runner_mod._update_social_groups(agents, [], set())
        for agent in agents:
            agent.set_survival_context(env, agents)

        active_food, abandoned_food = chain_diag.nest_food_split(env, agents)
        newborns: list[Agent] = []

        for agent in list(agents):
            wants_reproduction = agent.tick(env, rng)
            for event_text in agent.pop_recent_events():
                event_counts[event_text.split(" ->", 1)[0]] += 1

            if (
                agent.alive
                and agent.parent_id is not None
                and agent.age >= agent_mod.ADULT_AGE
                and agent.agent_id not in matured_children
            ):
                matured_children.add(agent.agent_id)
                matured_by_child_generation[agent.generation] += 1
                if first_matured_child_tick is None:
                    first_matured_child_tick = current_tick

            debug = dict(agent.reproduction_debug)
            exact_ready = bool(debug.get("eligible", False))
            spawned = False
            spawn_block_reason: str | None = None
            litter_size = 0
            mate = None

            if wants_reproduction:
                capacity = max_population - (len(agents) + len(newborns))
                if capacity <= 0:
                    spawn_block_reason = "population_cap"
                    spawn_block_reasons[spawn_block_reason] += 1
                else:
                    mate = next(
                        (
                            candidate
                            for candidate in agents
                            if candidate.agent_id == agent.reproduction_partner_id and candidate.alive
                        ),
                        None,
                    )
                    litter_size = min(capacity, agent.decide_litter_size(env, mate, rng))
                    if litter_size <= 0:
                        spawn_block_reason = "zero_litter"
                        spawn_block_reasons[spawn_block_reason] += 1
                    else:
                        agent.prepare_reproduction(env, mate, litter_size)
                        births_by_mother_generation[agent.generation] += litter_size
                        for _child_index in range(litter_size):
                            child = agent.spawn_child(next_agent_id, rng, env, mate=mate)
                            child_parent[child.agent_id] = agent.agent_id
                            if child.sex == "female":
                                ensure_female(child)
                            newborns.append(child)
                            next_agent_id += 1
                        spawned = True
                        if first_birth_tick is None:
                            first_birth_tick = current_tick
                        if agent.generation == 1 and first_gen1_spawn_tick is None:
                            first_gen1_spawn_tick = current_tick
                        total_births += litter_size

            if agent.alive and agent.sex == "female" and agent.current_stage == "adult":
                stats = ensure_female(agent)
                if stats.first_adult_tick is None:
                    stats.first_adult_tick = current_tick
                stats.adult_ticks += 1

                gates = gate_state(agent, debug)
                stats.gate_samples += 1
                generation_gate_samples[agent.generation] += 1
                for gate_name, ok in gates.items():
                    if ok:
                        stats.gate_ok_counts[gate_name] += 1
                        generation_gate_ok_counts[agent.generation][gate_name] += 1

                reasons = reason_list(debug)
                if reasons and reasons != ["ready"]:
                    for reason in reasons:
                        stats.block_reasons[reason] += 1
                        generation_block_reasons[agent.generation][reason] += 1

                if exact_ready:
                    stats.exact_ready_ticks += 1
                    if stats.first_ready_tick is None:
                        stats.first_ready_tick = current_tick
                    if agent.generation == 1 and first_gen1_ready_tick is None:
                        first_gen1_ready_tick = current_tick
                if wants_reproduction:
                    stats.wants_reproduction_ticks += 1
                if exact_ready and not wants_reproduction:
                    stats.ready_no_want_ticks += 1
                if wants_reproduction and not spawned:
                    stats.want_no_spawn_ticks += 1
                if spawned:
                    stats.spawn_events += 1
                    stats.spawned_children += litter_size
                    if stats.first_spawn_tick is None:
                        stats.first_spawn_tick = current_tick

                if exact_ready or wants_reproduction or spawned or agent.generation == 1:
                    owner_id = agent._nest_owner_id()
                    nest_food = env.get_nest_food_storage(owner_id) if owner_id is not None else 0
                    decision_trace_rows.append(
                        {
                            "tick": current_tick,
                            "condition_id": condition.condition_id,
                            "seed": seed,
                            "agent_id": agent.agent_id,
                            "generation": agent.generation,
                            "lineage_id": agent.lineage_id,
                            "age": agent.age,
                            "stage": agent.current_stage,
                            "energy": agent.energy,
                            "threshold": debug.get("threshold"),
                            "durability": agent.durability,
                            "near_nest": debug.get("near_nest", agent.near_nest),
                            "mate_ok": debug.get("mate", False),
                            "mate_id": agent.reproduction_partner_id,
                            "mate_alive": mate.alive if mate is not None else False,
                            "owner_id": owner_id,
                            "nest_food": nest_food,
                            "nest_food_debug": debug.get("nest_food"),
                            "nest_food_requirement": debug.get("nest_food_requirement"),
                            "cooldown": debug.get("cooldown"),
                            "exact_ready": exact_ready,
                            "wants_reproduction": wants_reproduction,
                            "spawned": spawned,
                            "litter_size": litter_size,
                            "spawn_block_reason": spawn_block_reason,
                            "reason": debug.get("reason"),
                            "active_food": active_food,
                            "abandoned_food": abandoned_food,
                            **{f"gate_{name}": ok for name, ok in gates.items()},
                        }
                    )

            if not agent.alive:
                death_counts[agent.death_reason or "unknown"] += 1
                archived_agents.append(agent)
                agents.remove(agent)

        agents.extend(newborns)
        peak_population = max(peak_population, len(agents))
        for event_text in env.pop_physics_events():
            event_counts[event_text.split(" ->", 1)[0]] += 1

    archived_agents.extend(agents)
    final_tick = env.tick_count
    final_population = sum(1 for agent in agents if agent.alive)
    adult_gen_counts = Counter(
        agent.generation
        for agent in archived_agents
        if agent.parent_id is not None and agent.age >= agent_mod.ADULT_AGE
    )
    all_gen_counts = Counter(agent.generation for agent in archived_agents)
    max_generation = max((agent.generation for agent in archived_agents), default=0)
    nest_food_remaining = sum(nest.food_storage for nest in env.nests.values())
    female_rows = [female_stat_to_row(item) for item in female_stats.values()]

    run_summary = {
        "condition_id": condition.condition_id,
        "hypothesis": condition.hypothesis,
        "label": condition.label,
        "description": condition.description,
        "patches": list(condition.patches),
        "seed": seed,
        "body_index": body_index,
        "body_design": body.short_description,
        "initial_population": initial_population,
        "max_population": max_population,
        "max_ticks": max_ticks,
        "final_tick": final_tick,
        "final_population": final_population,
        "population_extinct": final_population == 0,
        "peak_population": peak_population,
        "total_births": total_births,
        "matured_children": len(matured_children),
        "gen1_births": births_by_mother_generation.get(1, 0),
        "gen2_births": births_by_mother_generation.get(2, 0),
        "second_wave_success": births_by_mother_generation.get(1, 0) > 0,
        "first_birth_tick": first_birth_tick,
        "first_gen1_ready_tick": first_gen1_ready_tick,
        "first_gen1_spawn_tick": first_gen1_spawn_tick,
        "first_matured_child_tick": first_matured_child_tick,
        "max_generation_observed": max_generation,
        "adult_generation_counts": dict(sorted(adult_gen_counts.items())),
        "all_generation_counts": dict(sorted(all_gen_counts.items())),
        "births_by_mother_generation": dict(sorted(births_by_mother_generation.items())),
        "matured_by_child_generation": dict(sorted(matured_by_child_generation.items())),
        "death_reasons": dict(death_counts),
        "event_counts": dict(event_counts),
        "spawn_block_reasons": dict(spawn_block_reasons),
        "nest_food_remaining": nest_food_remaining,
        "decision_summary": summarize_female_decisions(female_rows),
        "generation_gate_summary": summarize_generation_gates(generation_gate_samples, generation_gate_ok_counts, generation_block_reasons),
        "female_decision_rows": female_rows,
    }
    return {"summary": run_summary, "trace_rows": decision_trace_rows}


def gate_state(agent: Agent, debug: dict[str, object]) -> dict[str, bool]:
    threshold = debug.get("threshold")
    energy = debug.get("energy", agent.energy)
    nest_food = debug.get("nest_food", 0) or 0
    nest_requirement = debug.get("nest_food_requirement", 0) or 0
    cooldown = debug.get("cooldown", agent.reproduction_cooldown)
    return {
        "energy_ok": bool(threshold is not None and float(energy) >= float(threshold)),
        "durability_ok": agent.durability >= agent_mod.MINIMUM_REPRODUCTION_HEALTH,
        "near_nest": bool(debug.get("near_nest", agent.near_nest)),
        "nest_food_ok": float(nest_food) >= float(nest_requirement),
        "mate_ok": bool(debug.get("mate", False)),
        "cooldown_ok": float(cooldown or 0) <= 0,
    }


def reason_list(debug: dict[str, object]) -> list[str]:
    reasons = debug.get("reasons")
    if isinstance(reasons, list):
        return [str(reason) for reason in reasons]
    reason = str(debug.get("reason", "unknown"))
    return reason.split("|") if reason else ["unknown"]


def female_stat_to_row(stats: FemaleDecisionStats) -> dict[str, object]:
    gates = stats.gate_ok_counts or Counter()
    blocks = stats.block_reasons or Counter()
    return {
        "agent_id": stats.agent_id,
        "generation": stats.generation,
        "lineage_id": stats.lineage_id,
        "first_adult_tick": stats.first_adult_tick,
        "adult_ticks": stats.adult_ticks,
        "exact_ready_ticks": stats.exact_ready_ticks,
        "wants_reproduction_ticks": stats.wants_reproduction_ticks,
        "spawn_events": stats.spawn_events,
        "spawned_children": stats.spawned_children,
        "ready_no_want_ticks": stats.ready_no_want_ticks,
        "want_no_spawn_ticks": stats.want_no_spawn_ticks,
        "first_ready_tick": stats.first_ready_tick,
        "first_spawn_tick": stats.first_spawn_tick,
        "gate_samples": stats.gate_samples,
        "energy_ok_rate": safe_div(gates["energy_ok"], stats.gate_samples),
        "durability_ok_rate": safe_div(gates["durability_ok"], stats.gate_samples),
        "near_nest_rate": safe_div(gates["near_nest"], stats.gate_samples),
        "nest_food_ok_rate": safe_div(gates["nest_food_ok"], stats.gate_samples),
        "mate_ok_rate": safe_div(gates["mate_ok"], stats.gate_samples),
        "cooldown_ok_rate": safe_div(gates["cooldown_ok"], stats.gate_samples),
        "top_block_reasons": ";".join(f"{name}:{count}" for name, count in blocks.most_common(6)),
    }


def summarize_female_decisions(rows: list[dict[str, object]]) -> dict[str, object]:
    adult_rows = [row for row in rows if int(row["adult_ticks"]) > 0]
    gen1_rows = [row for row in adult_rows if int(row["generation"]) == 1]
    return {
        "adult_females_seen": len(adult_rows),
        "gen1_adult_females_seen": len(gen1_rows),
        "exact_ready_ticks": sum(int(row["exact_ready_ticks"]) for row in adult_rows),
        "wants_reproduction_ticks": sum(int(row["wants_reproduction_ticks"]) for row in adult_rows),
        "spawn_events": sum(int(row["spawn_events"]) for row in adult_rows),
        "spawned_children": sum(int(row["spawned_children"]) for row in adult_rows),
        "ready_no_want_ticks": sum(int(row["ready_no_want_ticks"]) for row in adult_rows),
        "want_no_spawn_ticks": sum(int(row["want_no_spawn_ticks"]) for row in adult_rows),
        "gen1_exact_ready_ticks": sum(int(row["exact_ready_ticks"]) for row in gen1_rows),
        "gen1_wants_reproduction_ticks": sum(int(row["wants_reproduction_ticks"]) for row in gen1_rows),
        "gen1_spawn_events": sum(int(row["spawn_events"]) for row in gen1_rows),
        "gen1_spawned_children": sum(int(row["spawned_children"]) for row in gen1_rows),
        "gen1_ready_no_want_ticks": sum(int(row["ready_no_want_ticks"]) for row in gen1_rows),
        "gen1_want_no_spawn_ticks": sum(int(row["want_no_spawn_ticks"]) for row in gen1_rows),
        "ready_to_spawn_conversion": safe_div(
            sum(int(row["spawn_events"]) for row in adult_rows),
            sum(int(row["exact_ready_ticks"]) for row in adult_rows),
        ),
        "gen1_ready_to_spawn_conversion": safe_div(
            sum(int(row["spawn_events"]) for row in gen1_rows),
            sum(int(row["exact_ready_ticks"]) for row in gen1_rows),
        ),
    }


def summarize_generation_gates(
    generation_gate_samples: Counter[int],
    generation_gate_ok_counts: dict[int, Counter[str]],
    generation_block_reasons: dict[int, Counter[str]],
) -> dict[str, object]:
    summary: dict[str, object] = {}
    for generation in sorted(generation_gate_samples):
        samples = generation_gate_samples[generation]
        gate_counts = generation_gate_ok_counts[generation]
        blocks = generation_block_reasons[generation]
        summary[str(generation)] = {
            "samples": samples,
            "energy_ok_rate": safe_div(gate_counts["energy_ok"], samples),
            "durability_ok_rate": safe_div(gate_counts["durability_ok"], samples),
            "near_nest_rate": safe_div(gate_counts["near_nest"], samples),
            "nest_food_ok_rate": safe_div(gate_counts["nest_food_ok"], samples),
            "mate_ok_rate": safe_div(gate_counts["mate_ok"], samples),
            "cooldown_ok_rate": safe_div(gate_counts["cooldown_ok"], samples),
            "top_block_reasons": blocks.most_common(8),
        }
    return summary


def summarize_conditions(runs: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for run in runs:
        grouped[str(run["condition_id"])].append(run)

    rows: list[dict[str, object]] = []
    for condition_id, items in grouped.items():
        decision = [item["decision_summary"] for item in items]
        rows.append(
            {
                "condition_id": condition_id,
                "hypothesis": items[0]["hypothesis"],
                "label": items[0]["label"],
                "replicates": len(items),
                "extinction_rate": safe_div(sum(1 for item in items if item["population_extinct"]), len(items)),
                "mean_final_tick": mean(float(item["final_tick"]) for item in items),
                "mean_total_births": mean(float(item["total_births"]) for item in items),
                "mean_matured_children": mean(float(item["matured_children"]) for item in items),
                "mean_gen1_births": mean(float(item["gen1_births"]) for item in items),
                "second_wave_success_rate": safe_div(sum(1 for item in items if item["second_wave_success"]), len(items)),
                "mean_max_generation": mean(float(item["max_generation_observed"]) for item in items),
                "mean_adult_females_seen": mean(float(summary["adult_females_seen"]) for summary in decision),
                "mean_gen1_adult_females_seen": mean(float(summary["gen1_adult_females_seen"]) for summary in decision),
                "mean_exact_ready_ticks": mean(float(summary["exact_ready_ticks"]) for summary in decision),
                "mean_wants_reproduction_ticks": mean(float(summary["wants_reproduction_ticks"]) for summary in decision),
                "mean_spawn_events": mean(float(summary["spawn_events"]) for summary in decision),
                "mean_ready_no_want_ticks": mean(float(summary["ready_no_want_ticks"]) for summary in decision),
                "mean_want_no_spawn_ticks": mean(float(summary["want_no_spawn_ticks"]) for summary in decision),
                "mean_gen1_exact_ready_ticks": mean(float(summary["gen1_exact_ready_ticks"]) for summary in decision),
                "mean_gen1_wants_reproduction_ticks": mean(float(summary["gen1_wants_reproduction_ticks"]) for summary in decision),
                "mean_gen1_spawn_events": mean(float(summary["gen1_spawn_events"]) for summary in decision),
                "mean_gen1_ready_no_want_ticks": mean(float(summary["gen1_ready_no_want_ticks"]) for summary in decision),
                "mean_gen1_want_no_spawn_ticks": mean(float(summary["gen1_want_no_spawn_ticks"]) for summary in decision),
                "mean_ready_to_spawn_conversion": mean(float(summary["ready_to_spawn_conversion"]) for summary in decision),
                "mean_gen1_ready_to_spawn_conversion": mean(float(summary["gen1_ready_to_spawn_conversion"]) for summary in decision),
            }
        )
    rows.sort(key=lambda row: (str(row["condition_id"]) != "baseline", str(row["condition_id"])))
    return rows


def safe_div(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def mean(values: Iterable[float]) -> float:
    data = list(values)
    return round(statistics.fmean(data), 6) if data else 0.0


def write_outputs(
    runs: list[dict[str, object]],
    summaries: list[dict[str, object]],
    trace_rows: list[dict[str, object]],
    args: argparse.Namespace,
) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "runs.json").write_text(
        json.dumps({"args": vars(args), "runs": runs, "summaries": summaries}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    run_fields = [
        "condition_id",
        "hypothesis",
        "seed",
        "final_tick",
        "final_population",
        "population_extinct",
        "peak_population",
        "total_births",
        "matured_children",
        "gen1_births",
        "gen2_births",
        "second_wave_success",
        "first_birth_tick",
        "first_gen1_ready_tick",
        "first_gen1_spawn_tick",
        "first_matured_child_tick",
        "max_generation_observed",
        "nest_food_remaining",
    ]
    write_csv(OUTPUT_ROOT / "runs.csv", run_fields, runs)

    summary_fields = [
        "condition_id",
        "hypothesis",
        "label",
        "replicates",
        "extinction_rate",
        "mean_final_tick",
        "mean_total_births",
        "mean_matured_children",
        "mean_gen1_births",
        "second_wave_success_rate",
        "mean_max_generation",
        "mean_adult_females_seen",
        "mean_gen1_adult_females_seen",
        "mean_exact_ready_ticks",
        "mean_wants_reproduction_ticks",
        "mean_spawn_events",
        "mean_ready_no_want_ticks",
        "mean_want_no_spawn_ticks",
        "mean_gen1_exact_ready_ticks",
        "mean_gen1_wants_reproduction_ticks",
        "mean_gen1_spawn_events",
        "mean_gen1_ready_no_want_ticks",
        "mean_gen1_want_no_spawn_ticks",
        "mean_ready_to_spawn_conversion",
        "mean_gen1_ready_to_spawn_conversion",
    ]
    write_csv(OUTPUT_ROOT / "condition_summary.csv", summary_fields, summaries)

    female_fields = [
        "condition_id",
        "seed",
        "agent_id",
        "generation",
        "lineage_id",
        "first_adult_tick",
        "adult_ticks",
        "exact_ready_ticks",
        "wants_reproduction_ticks",
        "spawn_events",
        "spawned_children",
        "ready_no_want_ticks",
        "want_no_spawn_ticks",
        "first_ready_tick",
        "first_spawn_tick",
        "gate_samples",
        "energy_ok_rate",
        "durability_ok_rate",
        "near_nest_rate",
        "nest_food_ok_rate",
        "mate_ok_rate",
        "cooldown_ok_rate",
        "top_block_reasons",
    ]
    female_rows: list[dict[str, object]] = []
    for run in runs:
        for row in run["female_decision_rows"]:
            female_rows.append({"condition_id": run["condition_id"], "seed": run["seed"], **row})
    write_csv(OUTPUT_ROOT / "female_decisions.csv", female_fields, female_rows)

    trace_fields = [
        "condition_id",
        "seed",
        "tick",
        "agent_id",
        "generation",
        "lineage_id",
        "age",
        "stage",
        "energy",
        "threshold",
        "durability",
        "near_nest",
        "mate_ok",
        "mate_id",
        "mate_alive",
        "owner_id",
        "nest_food",
        "nest_food_debug",
        "nest_food_requirement",
        "cooldown",
        "exact_ready",
        "wants_reproduction",
        "spawned",
        "litter_size",
        "spawn_block_reason",
        "reason",
        "active_food",
        "abandoned_food",
        "gate_energy_ok",
        "gate_durability_ok",
        "gate_near_nest",
        "gate_nest_food_ok",
        "gate_mate_ok",
        "gate_cooldown_ok",
    ]
    write_csv(OUTPUT_ROOT / "decision_trace.csv", trace_fields, trace_rows)

    REPORT_PATH.write_text(render_report(summaries, args), encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def render_report(summaries: list[dict[str, object]], args: argparse.Namespace) -> str:
    lines = [
        "# รายงานอัตโนมัติ H19 Decision Quality Trace",
        "",
        f"- body_index: `{args.body_index}`",
        f"- initial_population: `{args.initial_population}`",
        f"- max_population: `{args.max_population}`",
        f"- max_ticks: `{args.max_ticks}`",
        f"- seeds: `{', '.join(str(seed) for seed in args.seeds)}`",
        f"- output: `{OUTPUT_ROOT}`",
        "",
        "| Condition | Extinct | Final Tick | Births | Matured | Gen1 Births | Exact Ready | Spawn Events | Ready No Want | Want No Spawn | Gen1 Ready | Gen1 Spawn |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| `{row['condition_id']}` | {row['extinction_rate']:.2f} | {row['mean_final_tick']:.1f} | "
            f"{row['mean_total_births']:.1f} | {row['mean_matured_children']:.1f} | {row['mean_gen1_births']:.1f} | "
            f"{row['mean_exact_ready_ticks']:.1f} | {row['mean_spawn_events']:.1f} | "
            f"{row['mean_ready_no_want_ticks']:.1f} | {row['mean_want_no_spawn_ticks']:.1f} | "
            f"{row['mean_gen1_exact_ready_ticks']:.1f} | {row['mean_gen1_spawn_events']:.1f} |"
        )
    lines.extend(
        [
            "",
            "## ไฟล์ข้อมูล",
            "",
            f"- `runs.json`: `{OUTPUT_ROOT / 'runs.json'}`",
            f"- `runs.csv`: `{OUTPUT_ROOT / 'runs.csv'}`",
            f"- `condition_summary.csv`: `{OUTPUT_ROOT / 'condition_summary.csv'}`",
            f"- `female_decisions.csv`: `{OUTPUT_ROOT / 'female_decisions.csv'}`",
            f"- `decision_trace.csv`: `{OUTPUT_ROOT / 'decision_trace.csv'}`",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run H19 reproduction decision-quality trace.")
    parser.add_argument("--body-index", type=int, default=14)
    parser.add_argument("--initial-population", type=int, default=250)
    parser.add_argument("--max-population", type=int, default=375)
    parser.add_argument("--max-ticks", type=int, default=800)
    parser.add_argument("--seeds", type=int, nargs="+", default=[7, 8, 11, 13])
    parser.add_argument("--conditions", nargs="*", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    conditions = trace_conditions()
    if args.conditions:
        allowed = set(args.conditions)
        conditions = [condition for condition in conditions if condition.condition_id in allowed]

    runs: list[dict[str, object]] = []
    trace_rows: list[dict[str, object]] = []
    total = len(conditions) * len(args.seeds)
    index = 0
    for condition in conditions:
        for seed in args.seeds:
            index += 1
            print(f"[{index}/{total}] {condition.condition_id} seed={seed}", flush=True)
            with chain_diag.apply_patches(condition.patches):
                result = run_trace_trial(
                    condition=condition,
                    seed=seed,
                    body_index=args.body_index,
                    initial_population=args.initial_population,
                    max_population=args.max_population,
                    max_ticks=args.max_ticks,
                )
            runs.append(result["summary"])
            trace_rows.extend(result["trace_rows"])

    summaries = summarize_conditions(runs)
    write_outputs(runs, summaries, trace_rows, args)
    print(f"Wrote {OUTPUT_ROOT}", flush=True)
    print(f"Wrote {REPORT_PATH}", flush=True)


if __name__ == "__main__":
    main()
