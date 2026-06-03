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
import run_reproduction_chain_diagnostics as chain_diag


OUTPUT_ROOT = PROJECT_ROOT / "data" / "hypothesis_diagnostics" / "h20_h22_family_chain_2026-06-03"
REPORT_PATH = PROJECT_ROOT / "reports" / "h20_h22_family_chain_diagnostics_2026-06-03.md"


def block_reproduction(agent: Agent, reason: str) -> bool:
    debug = dict(agent.reproduction_debug)
    reasons = list(debug.get("reasons", []))
    if not reasons or reasons == ["ready"]:
        reasons = []
    reasons.append(reason)
    debug["eligible"] = False
    debug["reason"] = "|".join(reasons)
    debug["reasons"] = reasons
    agent.reproduction_debug = debug
    agent.reproduction_partner_id = None
    return False


def patch_h20_first_wave_throttling(registry: chain_diag.PatchRegistry) -> None:
    original_can = Agent.can_reproduce
    original_litter = Agent.decide_litter_size

    def throttled_can_reproduce(self: Agent) -> bool:
        ready = original_can(self)
        if not ready:
            return False
        env = getattr(self, "_last_env", None)
        if env is None or self.generation != 0:
            return ready

        # Stagger founder births so the first wave does not arrive as one synchronous shock.
        stagger_tick = 1 + ((self.agent_id // 2) % 8) * 6
        if env.tick_count < stagger_tick:
            return block_reproduction(self, "h20_stagger")

        owner_id = self._nest_owner_id()
        nest_food = env.get_nest_food_storage(owner_id) if owner_id is not None else 0
        local_child_load = int(self.reproduction_debug.get("local_child_load", 0) or 0)
        household_buffer = 16 + (local_child_load * 8)
        if env.tick_count < 120 and nest_food < household_buffer:
            return block_reproduction(self, "h20_household_buffer")

        # Avoid repeated founder births before the first child has become useful to the household.
        if self.children_count >= 1 and env.tick_count < 150:
            adult_child_nearby = any(
                member.parent_id == self.agent_id and member.current_stage == "adult"
                for member in self.local_group_members
            )
            if not adult_child_nearby:
                return block_reproduction(self, "h20_wait_for_adult_child")
        return True

    def throttled_litter_size(self: Agent, env: Environment, mate: Agent | None, rng: Random) -> int:
        litter_size = original_litter(self, env, mate, rng)
        if self.generation == 0 and env.tick_count < 160:
            return min(1, litter_size)
        return litter_size

    registry.set_attr(Agent, "can_reproduce", throttled_can_reproduce)
    registry.set_attr(Agent, "decide_litter_size", throttled_litter_size)


def patch_h21_nest_inheritance(registry: chain_diag.PatchRegistry) -> None:
    original_owner = Agent._nest_owner_id
    original_withdraw = Agent._withdraw_nest_food_if_needed

    def inherited_owner(self: Agent) -> int | None:
        env = getattr(self, "_last_env", None)
        if env is not None and self.generation >= 1:
            for owner_id in (self.shared_home_owner_id, self.parent_id, self.other_parent_id):
                if owner_id is None:
                    continue
                nest = env.find_nest(owner_id)
                if nest is None:
                    continue
                self.shared_home_owner_id = owner_id
                self.nest_position = (nest.x, nest.y)
                return owner_id
        return original_owner(self)

    def inherited_withdraw(self: Agent, env: Environment) -> None:
        original_withdraw(self, env)
        if (
            not self.alive
            or self.generation < 1
            or self.current_stage not in {"juvenile", "adult"}
            or not self.near_nest
            or self.energy >= 92
        ):
            return
        owner_id = self._nest_owner_id()
        if owner_id is None:
            return
        nest_food = env.get_nest_food_storage(owner_id)
        if nest_food <= agent_mod.BREEDER_NEST_FOOD_RESERVE:
            return
        amount = min(14, nest_food - agent_mod.BREEDER_NEST_FOOD_RESERVE, 100 - self.energy)
        if amount <= 0:
            return
        withdrawn = env.withdraw_food_from_nest(owner_id, amount)
        if withdrawn <= 0:
            return
        self.energy += withdrawn
        self.recent_events.append(
            f"gen1_inherited_withdraw -> agent={self.agent_id} nest={owner_id} amount={withdrawn}"
        )

    registry.set_attr(Agent, "_nest_owner_id", inherited_owner)
    registry.set_attr(Agent, "_withdraw_nest_food_if_needed", inherited_withdraw)


def patch_h22_mate_synchronization(registry: chain_diag.PatchRegistry) -> None:
    original_target = Agent._preferred_movement_target

    def gen1_rendezvous_target(self: Agent) -> tuple[int, int] | None:
        if self.generation >= 1 and self.current_stage == "adult" and self.nest_position is not None:
            mate = self._find_reproduction_partner() if self.sex == "female" else None
            if self.energy >= 58 and (self.sex == "male" or mate is None or not self.near_nest):
                return self.nest_position
        return original_target(self)

    registry.set_attr(Agent, "_preferred_movement_target", gen1_rendezvous_target)


def register_local_patches() -> None:
    local: dict[str, Callable[[chain_diag.PatchRegistry], None]] = {
        "h20_first_wave_throttling": patch_h20_first_wave_throttling,
        "h21_nest_inheritance": patch_h21_nest_inheritance,
        "h22_mate_synchronization": patch_h22_mate_synchronization,
    }
    chain_diag.PATCH_APPLIERS.update(local)


def family_conditions() -> list[h19.TraceCondition]:
    return [
        h19.TraceCondition("baseline", "baseline", "Current baseline", "No intervention."),
        h19.TraceCondition("h13_parent_child_overlap", "H13", "Parent-child overlap", "Reference H13.", ("h13_parent_child_overlap",)),
        h19.TraceCondition("i_h1_h11", "H1+H11", "Best prior second-wave signal", "Prior best H1+H11.", ("h1_breeder_tuned", "h11_extend_reproductive_life")),
        h19.TraceCondition("h17_lower_birth_cost", "H17", "Lower birth cost", "High first-wave birth warning.", ("h17_lower_birth_cost",)),
        h19.TraceCondition("h20_first_wave_throttling", "H20", "First-wave throttling", "Stagger and buffer founder births.", ("h20_first_wave_throttling",)),
        h19.TraceCondition("i_h20_h13", "Interaction", "H20 + H13", "Throttling plus parent-child overlap.", ("h20_first_wave_throttling", "h13_parent_child_overlap")),
        h19.TraceCondition("i_h20_h21", "Interaction", "H20 + H21", "Throttling plus nest inheritance.", ("h20_first_wave_throttling", "h21_nest_inheritance")),
        h19.TraceCondition("i_h20_h22", "Interaction", "H20 + H22", "Throttling plus Gen1 mate synchronization.", ("h20_first_wave_throttling", "h22_mate_synchronization")),
        h19.TraceCondition("i_h20_h13_h21", "Interaction", "H20 + H13 + H21", "Core family-chain candidate.", ("h20_first_wave_throttling", "h13_parent_child_overlap", "h21_nest_inheritance")),
        h19.TraceCondition("i_h20_h13_h22", "Interaction", "H20 + H13 + H22", "Overlap plus mate synchronization.", ("h20_first_wave_throttling", "h13_parent_child_overlap", "h22_mate_synchronization")),
        h19.TraceCondition("i_h20_h21_h22", "Interaction", "H20 + H21 + H22", "Inheritance plus mate synchronization.", ("h20_first_wave_throttling", "h21_nest_inheritance", "h22_mate_synchronization")),
        h19.TraceCondition("i_h20_h13_h21_h22", "Interaction", "H20 + H13 + H21 + H22", "Full family-chain stack.", ("h20_first_wave_throttling", "h13_parent_child_overlap", "h21_nest_inheritance", "h22_mate_synchronization")),
    ]


def render_family_report(summaries: list[dict[str, object]], args: argparse.Namespace) -> str:
    lines = [
        "# รายงานอัตโนมัติ H20-H22 Family Chain Diagnostic",
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
    parser = argparse.ArgumentParser(description="Run H20-H22 family-chain diagnostics.")
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
    h19.render_report = render_family_report

    args = parse_args()
    conditions = family_conditions()
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
