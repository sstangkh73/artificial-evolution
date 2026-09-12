# -*- coding: utf-8 -*-
"""E0 pilot calibration for the G1-G6 toxin experiments.

E0 exists to find parameters that make E1-E5 MEANINGFUL, not parameters that make
the result look good. Nothing it produces may appear in the manuscript as a
result (PLAN_E1_E6 S3). It answers, per candidate configuration:

  * do the founders survive long enough for a lifespan difference to be visible?
  * does an agent meet fruit often enough (>= 30 encounters/life) to learn at all?
  * is the trap condition actually satisfied -- fresh fruit worth less than the
    staple, but the blended mean worth MORE, so a kind-keyed learner keeps eating?
  * is toxin a visible share of total somatic damage, or is it lost in the noise?
  * what constant potency would make arm A3 dose-matched to arm A2?
  * how long does a run take in wall-clock?

Configurations are declared in a JSON file (see --config-file) or taken from the
built-in stage lists. Each is run at every seed given, and the diagnostics are
written as JSON plus a Markdown table.

Usage:
    python scripts/run_e0_pilot.py --stage ecology --seeds 20260910 --ticks 3000 \
        --out-dir reports/e0 --work-dir data/e0_pilot
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_HERE))

from world import metabolism  # noqa: E402
from calibrate_matched_potency import (  # noqa: E402
    dose, mean_dose, solve_dose_matched_scale,
)

DRIVER = "scripts/food_value_study_driver.py"

# Shared across every pilot configuration. Telemetry is always on here: E0 is
# precisely the run whose exposure and gene channels we need to read.
BASE = [
    "--model", "v2", "--body", "37", "--population", "50",
    "--value-learning", "--pickiness", "0.6", "--starvation-energy", "6",
    "--mortal", "--starvation-death", "--aging", "--founder-age-spread", "1",
    "--encounter-telemetry", "--agent-outcome-telemetry",
]

# Stage 1: can founders live at all? No toxins yet -- mixing an ecology question
# with a toxin question would make neither answerable.
STAGE_ECOLOGY = {
    "eco_barren": ["--world", "100"],
    "eco_rain12": ["--world", "100", "--natural-seed-rain", "12"],
    "eco_rain12_smell": ["--world", "100", "--natural-seed-rain", "12", "--food-sensing-radius", "20"],
    "eco_rain12_smell_plants": [
        "--world", "100", "--natural-seed-rain", "12", "--food-sensing-radius", "20",
        "--initial-plants", "2500",
    ],
    "eco_rain12_vision_plants": [
        "--world", "100", "--natural-seed-rain", "12", "--initial-plants", "2500",
        "--food-detection-threshold", "0.01", "--vision-horizon", "200",
    ],
    "eco_rain12_vision_plants_drain05": [
        "--world", "100", "--natural-seed-rain", "12", "--initial-plants", "2500",
        "--food-detection-threshold", "0.01", "--vision-horizon", "200",
        "--drain-mult", "0.5",
    ],
    "eco_rain12_vision_plants_drain02": [
        "--world", "100", "--natural-seed-rain", "12", "--initial-plants", "2500",
        "--food-detection-threshold", "0.01", "--vision-horizon", "200",
        "--drain-mult", "0.2",
    ],
}

STAGES = {"ecology": STAGE_ECOLOGY}


# --------------------------------------------------------------- diagnostics


def _fruit_encounters(rows: list[dict], kind: str = "raw_fruit") -> Counter:
    weights: Counter = Counter()
    for row in rows:
        for key, counts in (row.get("encounters_by_kind_age") or {}).items():
            row_kind, _, bin_text = key.partition("@")
            if row_kind == kind:
                weights[int(bin_text)] += int(counts.get("seen", 0))
    return weights


def _encounter_outcomes(rows: list[dict], kind: str) -> dict[str, int]:
    total = {"seen": 0, "ate": 0, "skipped": 0}
    for row in rows:
        for key, counts in (row.get("encounters_by_kind_age") or {}).items():
            if key.partition("@")[0] != kind:
                continue
            for field in total:
                total[field] += int(counts.get(field, 0))
    return total


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def _trap_condition(gross_fruit: float, gross_staple: float, acute: float,
                    tolerance: float, detox_ticks: int, window: tuple[int, int]) -> dict:
    """The analytic trap test, in learned-value units.

    A kind-keyed learner converges on the MEAN net value of the kind. The trap
    needs two things at once: fresh fruit must be worth less than the staple (so
    eating it is a mistake), while the blend must be worth more (so the learner
    never stops). If the blend falls below the staple the learner correctly
    abandons fruit and there is no trap to measure.
    """
    fresh_potency = metabolism.toxin_age_potency(0, detox_ticks, window[0], window[1])
    safe_age = max(1, detox_ticks) if detox_ticks else (window[0] + window[1]) // 2
    safe_potency = metabolism.toxin_age_potency(safe_age, detox_ticks, window[0], window[1])
    value_fresh = gross_fruit - acute * dose(fresh_potency, tolerance)
    value_safe = gross_fruit - acute * dose(safe_potency, tolerance)
    value_mix = (value_fresh + value_safe) / 2.0
    return {
        "value_staple": round(gross_staple, 3),
        "value_fresh_fruit": round(value_fresh, 3),
        "value_safe_fruit": round(value_safe, 3),
        "value_mixed_fruit": round(value_mix, 3),
        "fresh_below_staple": value_fresh < gross_staple,
        "mixed_above_staple": value_mix > gross_staple,
        "trap_condition_met": value_fresh < gross_staple and value_mix > gross_staple,
    }


def diagnose(summary: dict, params: dict, wall_seconds: float, requested_ticks: int) -> dict:
    rows = summary.get("agent_diet_summary") or []
    founders = [r for r in rows if r.get("generation") == 0]
    alive_founders = [r for r in founders if r.get("alive")]
    tolerances = [float(r["toxin_tolerance"]) for r in founders if r.get("toxin_tolerance") is not None] or [0.2]

    weights = _fruit_encounters(rows)
    fruit = _encounter_outcomes(rows, "raw_fruit")
    plant = _encounter_outcomes(rows, "raw_plant")

    detox = int(params.get("toxin_detox_ticks", 0))
    window = (int(params.get("toxin_safe_window_start", 0)), int(params.get("toxin_safe_window_end", 0)))
    acute = float(params.get("toxin_acute_penalty", 0.0))

    diagnostics: dict = {
        "wall_seconds": round(wall_seconds, 2),
        "requested_ticks": requested_ticks,
        "final_tick": summary.get("tick"),
        "stopped_early": (summary.get("tick") or 0) < requested_ticks,
        "population_end": summary.get("population"),
        "peak_population": summary.get("peak_population"),
        "births": summary.get("births"),
        "death_reasons": summary.get("agent_death_reasons"),
        "observed_agents": len(rows),
        "founders": len(founders),
        "founders_alive_at_end": len(alive_founders),
        "founder_survival_at_end": round(len(alive_founders) / len(founders), 3) if founders else None,
        "founder_mean_age": _mean([float(r["age"]) for r in founders]),
        "founder_mean_age_at_death": _mean([float(r["age"]) for r in founders if not r.get("alive")]),
        "fruit_encounters_total": fruit["seen"],
        "fruit_encounters_per_agent": round(fruit["seen"] / len(rows), 2) if rows else None,
        "fruit_p_eat_given_encounter": round(fruit["ate"] / fruit["seen"], 4) if fruit["seen"] else None,
        "plant_encounters_total": plant["seen"],
        "plant_p_eat_given_encounter": round(plant["ate"] / plant["seen"], 4) if plant["seen"] else None,
        "mean_learned_fruit_value": _mean([
            float(r["food_value_memory"]["raw_fruit"]) for r in rows
            if "raw_fruit" in (r.get("food_value_memory") or {})
        ]),
        "mean_learned_plant_value": _mean([
            float(r["food_value_memory"]["raw_plant"]) for r in rows
            if "raw_plant" in (r.get("food_value_memory") or {})
        ]),
        "mean_damage": _mean([float(r["damage"]) for r in rows]),
        "mean_toxin_damage": _mean([float(r["toxin_damage_total"]) for r in rows]),
        "mean_toxin_ingested": _mean([float(r["toxin_ingested_total"]) for r in rows]),
        "mean_founder_toxin_tolerance": round(sum(tolerances) / len(tolerances), 4),
    }

    damage = diagnostics["mean_damage"] or 0.0
    diagnostics["toxin_share_of_damage"] = (
        round((diagnostics["mean_toxin_damage"] or 0.0) / damage, 4) if damage > 0 else None
    )

    if weights and (detox > 0 or window[1] > window[0]):
        age_bin = int(params.get("encounter_age_bin", 1))
        total = sum(weights.values())
        target = sum(
            count * mean_dose(
                metabolism.toxin_age_potency(
                    index * age_bin + (age_bin - 1) / 2.0, detox, window[0], window[1]),
                tolerances,
            )
            for index, count in weights.items()
        ) / total
        mean_potency = sum(
            count * metabolism.toxin_age_potency(
                index * age_bin + (age_bin - 1) / 2.0, detox, window[0], window[1])
            for index, count in weights.items()
        ) / total
        diagnostics["a2_mean_potency_at_encounter"] = round(mean_potency, 4)
        diagnostics["a2_mean_dose_at_encounter"] = round(target, 6)
        try:
            diagnostics["a3_dose_matched_potency_scale"] = round(
                solve_dose_matched_scale(target, tolerances), 6)
        except ValueError as error:
            diagnostics["a3_dose_matched_potency_scale"] = f"unreachable: {error}"
        naive = mean_dose(mean_potency, tolerances)
        diagnostics["a3_under_dosing_if_matched_on_potency"] = (
            round(target / naive, 2) if naive > 0 else None)

    if acute > 0:
        enzyme = None  # gross energy is body-dependent; use the shipped default body profile
        from agents.body import BodyPlan
        body = BodyPlan(sensor_units=2, muscle_units=2, armor_units=0, brain_units=2)
        enzyme = body.enzyme_profile
        gross_fruit = metabolism.digestible_energy(
            metabolism.COMPOSITION["raw_fruit"], metabolism.FOOD_MASS["raw_fruit"], enzyme)
        gross_staple = metabolism.digestible_energy(
            metabolism.COMPOSITION["raw_plant"], metabolism.FOOD_MASS["raw_plant"], enzyme)
        diagnostics["trap"] = _trap_condition(
            gross_fruit, gross_staple, acute,
            sum(tolerances) / len(tolerances), detox, window)

    return diagnostics


# --------------------------------------------------------------- run loop


def _params_from_flags(flags: list[str]) -> dict:
    params: dict = {}
    index = 0
    while index < len(flags):
        token = flags[index]
        if token.startswith("--"):
            name = token[2:].replace("-", "_")
            if index + 1 < len(flags) and not flags[index + 1].startswith("--"):
                params[name] = flags[index + 1]
                index += 2
                continue
            params[name] = True
        index += 1
    # normalise the names diagnose() looks for
    for key, default in (("toxin_detox_ticks", 0), ("toxin_safe_window_start", 0),
                         ("toxin_safe_window_end", 0), ("toxin_acute_penalty", 0.0),
                         ("encounter_age_bin", 1)):
        params.setdefault(key, default)
    if "toxic_food" in params:
        params["toxin_acute_penalty"] = float(params.get("toxin_acute_penalty", 0.0))
    return params


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", default="ecology", choices=sorted(STAGES))
    parser.add_argument("--config-file", default=None,
                        help="JSON {name: [flags]} overriding the built-in stage")
    parser.add_argument("--seeds", default="20260910", help="comma-separated")
    parser.add_argument("--ticks", type=int, default=3000)
    parser.add_argument("--work-dir", default="data/e0_pilot")
    parser.add_argument("--out-dir", default="reports/e0")
    parser.add_argument("--label", default=None)
    args = parser.parse_args()

    configs = (json.loads(Path(args.config_file).read_text(encoding="utf-8"))
               if args.config_file else STAGES[args.stage])
    seeds = [int(s) for s in args.seeds.split(",")]
    work = Path(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    label = args.label or args.stage

    results = []
    for name, flags in configs.items():
        for seed in seeds:
            dump = work / f"{label}_{name}_s{seed}.json"
            command = [sys.executable, DRIVER, *BASE, *flags,
                       "--seed", str(seed), "--ticks", str(args.ticks),
                       "--output", str(work / f"{label}_{name}_s{seed}.out"),
                       "--dump", str(dump)]
            started = time.monotonic()
            completed = subprocess.run(command, cwd=_HERE.parent, capture_output=True, text=True)
            elapsed = time.monotonic() - started
            if completed.returncode != 0:
                print(f"FAILED {name} seed {seed}:\n{completed.stderr[-2000:]}")
                return 1
            summary = json.loads(dump.read_text(encoding="utf-8"))
            row = {"config": name, "seed": seed, "flags": " ".join(flags)}
            row.update(diagnose(summary, _params_from_flags(flags), elapsed, args.ticks))
            results.append(row)
            print(json.dumps({k: row[k] for k in (
                "config", "seed", "final_tick", "population_end", "founder_survival_at_end",
                "fruit_encounters_per_agent", "wall_seconds")}, ensure_ascii=False), flush=True)

    payload_path = out_dir / f"E0_{label}_diagnostics.json"
    payload_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    columns = ["config", "seed", "final_tick", "stopped_early", "population_end", "births",
               "founder_survival_at_end", "founder_mean_age", "fruit_encounters_per_agent",
               "fruit_p_eat_given_encounter", "toxin_share_of_damage",
               "a3_dose_matched_potency_scale", "wall_seconds"]
    lines = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    for row in results:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    table_path = out_dir / f"E0_{label}_table.md"
    table_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nwrote {payload_path}\nwrote {table_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
