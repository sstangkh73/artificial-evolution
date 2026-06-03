from __future__ import annotations

import argparse
from pathlib import Path
from random import Random
import sys
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for path in (PROJECT_ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import agents.agent as agent_mod
from agents.agent import Agent
from world.environment import Environment

import run_h19_decision_quality_trace as h19
import run_h20_h22_family_chain_diagnostics as family_chain
import run_reproduction_chain_diagnostics as chain_diag


OUTPUT_ROOT = PROJECT_ROOT / "data" / "hypothesis_diagnostics" / "h20_soft_sweep_h23_2026-06-03"
REPORT_PATH = PROJECT_ROOT / "reports" / "h20_soft_sweep_h23_diagnostics_2026-06-03.md"


def _debug_number(agent: Agent, key: str, default: int = 0) -> int:
    value = agent.reproduction_debug.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _threshold(agent: Agent) -> int:
    return _debug_number(agent, "threshold", agent_mod.REPRODUCTION_THRESHOLD)


def _nest_food(agent: Agent, env: Environment) -> int:
    owner_id = agent._nest_owner_id()
    return env.get_nest_food_storage(owner_id) if owner_id is not None else 0


def _has_useful_child_nearby(agent: Agent) -> bool:
    return any(
        member.parent_id == agent.agent_id
        and member.current_stage in {"juvenile", "adult"}
        and abs(member.x - agent.x) + abs(member.y - agent.y) <= agent_mod.SAFE_RADIUS + 4
        for member in agent.local_group_members
    )


def patch_h20a_litter_cap_only(registry: chain_diag.PatchRegistry) -> None:
    original_litter = Agent.decide_litter_size

    def capped_litter(self: Agent, env: Environment, mate: Agent | None, rng: Random) -> int:
        litter_size = original_litter(self, env, mate, rng)
        if self.generation == 0 and env.tick_count < 170:
            return min(1, litter_size)
        return litter_size

    registry.set_attr(Agent, "decide_litter_size", capped_litter)


def patch_h20b_soft_birth_spacing(registry: chain_diag.PatchRegistry) -> None:
    original_prepare = Agent.prepare_reproduction

    def spaced_prepare(self: Agent, env: Environment, mate: Agent | None, litter_size: int) -> None:
        original_prepare(self, env, mate, litter_size)
        if self.generation == 0:
            self.reproduction_cooldown = max(self.reproduction_cooldown, 48)
            if mate is not None:
                mate.reproduction_cooldown = max(mate.reproduction_cooldown, 34)

    registry.set_attr(Agent, "prepare_reproduction", spaced_prepare)


def patch_h20c_household_buffer_only(registry: chain_diag.PatchRegistry) -> None:
    original_can = Agent.can_reproduce

    def buffered_can_reproduce(self: Agent) -> bool:
        ready = original_can(self)
        if not ready or self.generation != 0:
            return ready
        env = getattr(self, "_last_env", None)
        if env is None or env.tick_count >= 150:
            return ready
        requirement = _debug_number(self, "nest_food_requirement", agent_mod.BREEDER_NEST_FOOD_RESERVE)
        local_child_load = _debug_number(self, "local_child_load", 0)
        buffer_food = requirement + 6 + (local_child_load * 4)
        buffer_energy = _threshold(self) + 6
        if _nest_food(self, env) < buffer_food or self.energy < buffer_energy:
            return family_chain.block_reproduction(self, "h20c_soft_buffer")
        return True

    registry.set_attr(Agent, "can_reproduce", buffered_can_reproduce)


def patch_h20d_first_birth_free_repeat_gated(registry: chain_diag.PatchRegistry) -> None:
    original_can = Agent.can_reproduce

    def repeat_gated_can_reproduce(self: Agent) -> bool:
        ready = original_can(self)
        if not ready or self.generation != 0:
            return ready
        env = getattr(self, "_last_env", None)
        if env is None or self.children_count == 0 or env.tick_count >= 180:
            return ready
        requirement = _debug_number(self, "nest_food_requirement", agent_mod.BREEDER_NEST_FOOD_RESERVE)
        repeat_buffer_ok = _nest_food(self, env) >= requirement + 18 and self.energy >= _threshold(self) + 14
        if not (_has_useful_child_nearby(self) or repeat_buffer_ok):
            return family_chain.block_reproduction(self, "h20d_repeat_gate")
        return True

    registry.set_attr(Agent, "can_reproduce", repeat_gated_can_reproduce)


def patch_h20e_temporal_window_matching(registry: chain_diag.PatchRegistry) -> None:
    original_can = Agent.can_reproduce
    original_litter = Agent.decide_litter_size

    def temporal_can_reproduce(self: Agent) -> bool:
        ready = original_can(self)
        if not ready or self.generation != 0:
            return ready
        env = getattr(self, "_last_env", None)
        if env is None:
            return ready
        # First birth remains possible. Later births need either a usable child bridge or mild surplus.
        if self.children_count >= 1 and env.tick_count < 150:
            requirement = _debug_number(self, "nest_food_requirement", agent_mod.BREEDER_NEST_FOOD_RESERVE)
            surplus_ok = _nest_food(self, env) >= requirement + 12 and self.energy >= _threshold(self) + 10
            if not (_has_useful_child_nearby(self) or surplus_ok):
                return family_chain.block_reproduction(self, "h20e_temporal_gate")
        if env.tick_count > 115 and self.energy < _threshold(self) + 6:
            return family_chain.block_reproduction(self, "h20e_late_low_energy")
        return True

    def temporal_litter(self: Agent, env: Environment, mate: Agent | None, rng: Random) -> int:
        litter_size = original_litter(self, env, mate, rng)
        if self.generation == 0 and env.tick_count < 150:
            return min(1, litter_size)
        return litter_size

    registry.set_attr(Agent, "can_reproduce", temporal_can_reproduce)
    registry.set_attr(Agent, "decide_litter_size", temporal_litter)


def register_local_patches() -> None:
    local: dict[str, Callable[[chain_diag.PatchRegistry], None]] = {
        "h20a_litter_cap_only": patch_h20a_litter_cap_only,
        "h20b_soft_birth_spacing": patch_h20b_soft_birth_spacing,
        "h20c_household_buffer_only": patch_h20c_household_buffer_only,
        "h20d_first_birth_free_repeat_gated": patch_h20d_first_birth_free_repeat_gated,
        "h20e_temporal_window_matching": patch_h20e_temporal_window_matching,
        "h21_nest_inheritance": family_chain.patch_h21_nest_inheritance,
        "h22_mate_synchronization": family_chain.patch_h22_mate_synchronization,
    }
    chain_diag.PATCH_APPLIERS.update(local)


def soft_sweep_conditions() -> list[h19.TraceCondition]:
    return [
        h19.TraceCondition("baseline", "baseline", "Current baseline", "No intervention."),
        h19.TraceCondition("h13_parent_child_overlap", "H13", "Parent-child overlap", "Possible necessary condition.", ("h13_parent_child_overlap",)),
        h19.TraceCondition("i_h1_h11", "H1+H11", "Best prior second-wave signal", "Prior best condition.", ("h1_breeder_tuned", "h11_extend_reproductive_life")),
        h19.TraceCondition("h17_lower_birth_cost", "H17", "Lower birth cost", "First-wave overproduction warning.", ("h17_lower_birth_cost",)),
        h19.TraceCondition("h20a_litter_cap_only", "H20a", "Litter cap only", "Cap early Gen0 litter size without blocking birth.", ("h20a_litter_cap_only",)),
        h19.TraceCondition("h20b_soft_birth_spacing", "H20b", "Soft birth spacing", "Increase post-birth spacing per Gen0 mother.", ("h20b_soft_birth_spacing",)),
        h19.TraceCondition("h20c_household_buffer_only", "H20c", "Household buffer only", "Require mild local household buffer before early Gen0 birth.", ("h20c_household_buffer_only",)),
        h19.TraceCondition("h20d_first_birth_free_repeat_gated", "H20d", "First birth free, repeat gated", "Allow first birth, gate repeat births until child bridge or surplus exists.", ("h20d_first_birth_free_repeat_gated",)),
        h19.TraceCondition("h20e_temporal_window_matching", "H20e", "Temporal window matching", "Mild repeat-birth timing and early litter cap.", ("h20e_temporal_window_matching",)),
        h19.TraceCondition("i_h20a_h13", "Interaction", "H20a + H13", "Litter cap under parent-child overlap.", ("h20a_litter_cap_only", "h13_parent_child_overlap")),
        h19.TraceCondition("i_h20b_h13", "Interaction", "H20b + H13", "Soft spacing under parent-child overlap.", ("h20b_soft_birth_spacing", "h13_parent_child_overlap")),
        h19.TraceCondition("i_h20c_h13", "Interaction", "H20c + H13", "Household buffer under parent-child overlap.", ("h20c_household_buffer_only", "h13_parent_child_overlap")),
        h19.TraceCondition("i_h20d_h13", "Interaction", "H20d + H13", "Repeat-gated births under parent-child overlap.", ("h20d_first_birth_free_repeat_gated", "h13_parent_child_overlap")),
        h19.TraceCondition("i_h20e_h13", "Interaction", "H20e + H13", "Temporal window matching under parent-child overlap.", ("h20e_temporal_window_matching", "h13_parent_child_overlap")),
        h19.TraceCondition("i_h20d_h13_h21", "Interaction", "H20d + H13 + H21", "Repeat gate plus overlap plus inheritance.", ("h20d_first_birth_free_repeat_gated", "h13_parent_child_overlap", "h21_nest_inheritance")),
        h19.TraceCondition("i_h20d_h13_h22", "Interaction", "H20d + H13 + H22", "Repeat gate plus overlap plus mate sync.", ("h20d_first_birth_free_repeat_gated", "h13_parent_child_overlap", "h22_mate_synchronization")),
    ]


def render_soft_sweep_report(summaries: list[dict[str, object]], args: argparse.Namespace) -> str:
    lines = [
        "# รายงานอัตโนมัติ H20 Soft Sweep / H23 Temporal Synchronization",
        "",
        f"- body_index: `{args.body_index}`",
        f"- initial_population: `{args.initial_population}`",
        f"- max_population: `{args.max_population}`",
        f"- max_ticks: `{args.max_ticks}`",
        f"- seeds: `{', '.join(str(seed) for seed in args.seeds)}`",
        f"- output: `{OUTPUT_ROOT}`",
        "",
        "| Condition | Births | Matured | Gen1 Births | 2nd Wave | Exact Ready | Gen1 Ready | Gen1 Spawn | Final Tick |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| `{row['condition_id']}` | {row['mean_total_births']:.1f} | {row['mean_matured_children']:.1f} | "
            f"{row['mean_gen1_births']:.1f} | {row['second_wave_success_rate']:.2f} | "
            f"{row['mean_exact_ready_ticks']:.1f} | {row['mean_gen1_exact_ready_ticks']:.1f} | "
            f"{row['mean_gen1_spawn_events']:.1f} | {row['mean_final_tick']:.1f} |"
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
    parser = argparse.ArgumentParser(description="Run H20 soft sweep / H23 temporal synchronization diagnostics.")
    parser.add_argument("--body-index", type=int, default=14)
    parser.add_argument("--initial-population", type=int, default=250)
    parser.add_argument("--max-population", type=int, default=375)
    parser.add_argument("--max-ticks", type=int, default=800)
    parser.add_argument("--seeds", type=int, nargs="+", default=[7, 8, 11, 13])
    parser.add_argument("--conditions", nargs="*", default=None)
    return parser.parse_args()


def main() -> None:
    register_local_patches()
    h19.OUTPUT_ROOT = OUTPUT_ROOT
    h19.REPORT_PATH = REPORT_PATH
    h19.render_report = render_soft_sweep_report

    args = parse_args()
    conditions = soft_sweep_conditions()
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
                result = h19.run_trace_trial(
                    condition=condition,
                    seed=seed,
                    body_index=args.body_index,
                    initial_population=args.initial_population,
                    max_population=args.max_population,
                    max_ticks=args.max_ticks,
                )
            runs.append(result["summary"])
            trace_rows.extend(result["trace_rows"])

    summaries = h19.summarize_conditions(runs)
    h19.write_outputs(runs, summaries, trace_rows, args)
    print(f"Wrote {OUTPUT_ROOT}", flush=True)
    print(f"Wrote {REPORT_PATH}", flush=True)


if __name__ == "__main__":
    main()
