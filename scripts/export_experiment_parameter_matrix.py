# -*- coding: utf-8 -*-
"""Export reproducible parameter tables for publication experiments E1-E6/T2-RB.

The archived E1-E5 result summaries contain the exact launch specification in
``provenance.spec``. E6 and T2-RB use their frozen preregistration specs. This
script combines those explicit flags with defaults parsed from
``food_value_study_driver.py`` and records the origin of every value.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import subprocess
from collections import OrderedDict
from pathlib import Path
from typing import Any


SPEC_PATHS = OrderedDict([
    ("E1", Path("reports/e1_20260912/E1_runs.json")),
    ("E2", Path("reports/e2_20260913/E2_runs.json")),
    ("E3", Path("reports/e3_20260913/E3_runs.json")),
    ("E4", Path("reports/e4_20260913/E4_runs.json")),
    ("E5", Path("reports/e5_20260913/E5_runs.json")),
    ("E6", Path("reports/prereg/E6_representation_payoff_spec.json")),
    ("T2-RB", Path("reports/prereg/T2_RB_replication_spec.json")),
])

RUN_SUMMARY_PATHS = {
    "E1": Path("reports/e1_20260912/E1_runs.json"),
    "E2": Path("reports/e2_20260913/E2_runs.json"),
    "E3": Path("reports/e3_20260913/E3_runs.json"),
    "E4": Path("reports/e4_20260913/E4_runs.json"),
    "E5": Path("reports/e5_20260913/E5_runs.json"),
    "E6": Path("reports/publication_value_of_information_2026-09-13/confirmatory/e6/E6_runs.json"),
    "T2-RB": Path("reports/publication_value_of_information_2026-09-13/confirmatory/t2rb/T2RB_runs.json"),
}

OPERATIONAL_PARAMETERS = {"dump", "output", "seed", "ticks"}
FOCAL_FIXED_SETTINGS = {
    "spawn_strategy", "max_food", "base_food_spawn_per_tick", "food_spawn_multiplier",
    "bootstrap_food_spawn_ticks", "wild_food_spawn_after_bootstrap_multiplier",
    "max_plant_seeds", "large_animal_spawn_per_tick", "max_large_animals", "frontier_band",
    "global_food_decline_per_day", "minimum_global_food_multiplier",
    "ambient_food_decay_chance", "plant_food_decay_chance",
    "plant_seed_max_age_multiplier", "plant_growth_rate_multiplier",
    "sprout_biomass_loss_multiplier", "germination_good_ticks_multiplier",
    "plant_fruiting_interval_multiplier", "plant_fruiting_growth_threshold_multiplier",
    "plant_fruiting_chance_multiplier", "natural_seed_drop_chance_multiplier",
    "plant_lifecycle_food_signal_weight", "food_signal_radius_cap",
}


def literal(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        return None


def driver_defaults(source: str, filename: str) -> tuple[OrderedDict[str, Any], dict[str, str]]:
    tree = ast.parse(source, filename=filename)
    defaults: dict[str, Any] = {}
    actions: dict[str, str] = {}
    positions: dict[str, tuple[int, int]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "add_argument" or not node.args:
            continue
        flag = literal(node.args[0])
        if not isinstance(flag, str) or not flag.startswith("--"):
            continue
        name = flag[2:].replace("-", "_")
        keywords = {kw.arg: kw.value for kw in node.keywords if kw.arg}
        action = literal(keywords["action"]) if "action" in keywords else "value"
        if action == "store_true":
            default = False
        elif action == "store_false":
            default = True
        else:
            default = literal(keywords["default"]) if "default" in keywords else None
        defaults[name] = default
        actions[name] = str(action)
        positions[name] = (node.lineno, node.col_offset)
    ordered_names = sorted(defaults, key=lambda name: positions[name])
    return OrderedDict((name, defaults[name]) for name in ordered_names), actions


def fixed_runtime_settings(source: str, filename: str) -> OrderedDict[str, Any]:
    tree = ast.parse(source, filename=filename)
    function = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "make_args"
    )
    return_call = next(
        node.value
        for node in ast.walk(function)
        if isinstance(node, ast.Return)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "SimpleNamespace"
    )
    settings: OrderedDict[str, Any] = OrderedDict()
    for keyword in return_call.keywords:
        if not keyword.arg:
            continue
        try:
            settings[keyword.arg] = ast.literal_eval(keyword.value)
        except (ValueError, TypeError):
            continue
    return settings


def parse_flags(tokens: list[str], actions: dict[str, str]) -> OrderedDict[str, Any]:
    parsed: OrderedDict[str, Any] = OrderedDict()
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if not token.startswith("--"):
            raise ValueError(f"expected flag at token {index}: {token!r}")
        name = token[2:].replace("-", "_")
        if name not in actions:
            raise ValueError(f"unknown driver flag: {token}")
        if name in parsed:
            raise ValueError(f"duplicate driver flag: {token}")
        if actions[name] == "store_true":
            parsed[name] = True
            index += 1
        elif actions[name] == "store_false":
            parsed[name] = False
            index += 1
        else:
            if index + 1 >= len(tokens) or tokens[index + 1].startswith("--"):
                raise ValueError(f"missing value for {token}")
            parsed[name] = tokens[index + 1]
            index += 2
    return parsed


def load_spec(repo_root: Path, relative_path: Path) -> tuple[dict, str]:
    payload = json.loads((repo_root / relative_path).read_text(encoding="utf-8"))
    nested = payload.get("provenance", {}).get("spec")
    return (nested, "archived_result_provenance") if nested else (payload, "frozen_spec")


def verify_run_summary(repo_root: Path, label: str, spec: dict) -> tuple[str, int, dict]:
    relative_path = RUN_SUMMARY_PATHS[label]
    payload = json.loads((repo_root / relative_path).read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    seeds = set(spec["seeds"])
    arms = spec["arms"]
    expected_cells = {(str(arm), int(seed)) for arm in arms for seed in seeds}
    observed_cells = {(str(row["arm"]), int(row["seed"])) for row in rows}
    if observed_cells != expected_cells or len(rows) != len(expected_cells):
        raise ValueError(f"{label}: archived run cells do not match the specification")
    for row in rows:
        expected_flags = list(spec.get("base", [])) + list(arms[str(row["arm"])])
        if str(row.get("flags", "")).split() != expected_flags:
            raise ValueError(f"{label} {row['arm']} seed {row['seed']}: launch flags differ from spec")
        if int(row.get("requested_ticks", spec["ticks"])) != int(spec["ticks"]):
            raise ValueError(f"{label} {row['arm']} seed {row['seed']}: horizon differs from spec")
    provenance = payload.get("provenance", {})
    revision = provenance.get("git_revision") or provenance.get("git_revision_start")
    if not revision or provenance.get("git_tree_dirty") is True:
        raise ValueError(f"{label}: missing clean run revision")
    return relative_path.as_posix(), len(rows), provenance


def encode(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def cli_text(tokens: list[str]) -> str:
    return " ".join(tokens) if tokens else "(no arm-specific flags)"


def build_tables(repo_root: Path) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict]]:
    designs: list[dict] = []
    wide_rows: list[dict] = []
    long_rows: list[dict] = []
    arm_rows: list[dict] = []
    fixed_rows: list[dict] = []

    for label, path in SPEC_PATHS.items():
        spec, spec_origin = load_spec(repo_root, path)
        seeds = list(spec.get("seeds", []))
        arms = spec.get("arms", {})
        if not seeds or len(seeds) != len(set(seeds)):
            raise ValueError(f"{label}: missing or duplicate seeds")
        if not arms or int(spec.get("ticks", 0)) <= 0:
            raise ValueError(f"{label}: incomplete design")
        base_tokens = list(spec.get("base", []))
        run_summary_source, verified_run_rows, provenance = verify_run_summary(repo_root, label, spec)
        revision = str(provenance["git_revision"])
        driver_source = subprocess.run(
            ["git", "show", f"{revision}:scripts/food_value_study_driver.py"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
        defaults, actions = driver_defaults(driver_source, f"{revision}:scripts/food_value_study_driver.py")
        for setting, value in fixed_runtime_settings(
            driver_source, f"{revision}:scripts/food_value_study_driver.py"
        ).items():
            fixed_rows.append({
                "experiment": label,
                "setting": setting,
                "value": encode(value),
                "run_git_revision": revision,
                "origin": "make_args_literal",
            })
        scientific_defaults = OrderedDict(
            (name, value) for name, value in defaults.items() if name not in OPERATIONAL_PARAMETERS
        )
        base_values = parse_flags(base_tokens, actions)
        designs.append({
            "experiment": label,
            "ticks": int(spec["ticks"]),
            "seed_count": len(seeds),
            "first_seed": min(seeds),
            "last_seed": max(seeds),
            "arm_count": len(arms),
            "planned_runs": len(seeds) * len(arms),
            "spec_source": path.as_posix(),
            "spec_origin": spec_origin,
            "run_summary_source": run_summary_source,
            "verified_run_rows": verified_run_rows,
            "run_git_revision": revision,
            "run_tree_dirty": encode(provenance.get("git_tree_dirty")),
            "python_version": provenance.get("python_version", ""),
            "platform": provenance.get("platform", ""),
            "preregistration": spec.get("preregistration", ""),
            "preregistration_commit_or_tag": spec.get("preregistration_commit", spec.get("frozen_tag", "")),
            "explicit_base_cli": cli_text(base_tokens),
        })

        for arm, arm_tokens_raw in arms.items():
            arm_tokens = list(arm_tokens_raw)
            arm_values = parse_flags(arm_tokens, actions)
            effective = OrderedDict(scientific_defaults)
            origin = {name: "driver_default" for name in effective}
            for name, value in base_values.items():
                if name not in OPERATIONAL_PARAMETERS:
                    effective[name] = value
                    origin[name] = "base_spec"
            for name, value in arm_values.items():
                if name not in OPERATIONAL_PARAMETERS:
                    effective[name] = value
                    origin[name] = "arm_spec"

            row = OrderedDict([
                ("experiment", label),
                ("arm", arm),
                ("ticks", int(spec["ticks"])),
                ("seed_count", len(seeds)),
                ("first_seed", min(seeds)),
                ("last_seed", max(seeds)),
            ])
            row.update((name, encode(value)) for name, value in effective.items())
            wide_rows.append(row)

            for name, value in effective.items():
                long_rows.append({
                    "experiment": label,
                    "arm": arm,
                    "parameter": name,
                    "value": encode(value),
                    "origin": origin[name],
                })
            for name, value in arm_values.items():
                if name not in OPERATIONAL_PARAMETERS:
                    arm_rows.append({
                        "experiment": label,
                        "arm": arm,
                        "parameter": name,
                        "value": encode(value),
                    })
            if not arm_values:
                arm_rows.append({
                    "experiment": label,
                    "arm": arm,
                    "parameter": "(none)",
                    "value": "inherits base",
                })

    if len(wide_rows) != 38:
        raise ValueError(f"expected 38 experiment arms, found {len(wide_rows)}")
    return designs, wide_rows, long_rows, arm_rows, fixed_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    for row in rows[1:]:
        fieldnames.extend(name for name in row if name not in fieldnames)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def markdown(designs: list[dict], arm_rows: list[dict], fixed_rows: list[dict]) -> str:
    lines = [
        "# Experiment Parameter Tables — E1–E6 and T2-RB",
        "",
        "**Generated file.** Run `python scripts/export_experiment_parameter_matrix.py` from the repository root.",
        "",
        "These tables report the planned launch configuration preserved in each archived or frozen specification. The companion CSV files combine those explicit settings with defaults parsed from `scripts/food_value_study_driver.py` at the clean Git revision recorded by each run batch. Operational output paths are excluded. Per-run JSON dumps remain the authority for values realized during execution.",
        "",
        "## Design and provenance",
        "",
        "| Experiment | Ticks | Seeds | Arms | Planned runs | Verified rows | Run revision | Specification | Preregistration commit/tag |",
        "|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for row in designs:
        source = f"`{row['spec_source']}`"
        freeze = row["preregistration_commit_or_tag"] or "not recorded in spec"
        lines.append(
            f"| {row['experiment']} | {row['ticks']} | {row['seed_count']} "
            f"({row['first_seed']}–{row['last_seed']}) | {row['arm_count']} | "
            f"{row['planned_runs']} | {row['verified_run_rows']} | `{row['run_git_revision']}` | {source} | `{freeze}` |"
        )

    lines.extend(["", "## Explicit shared settings", ""])
    for row in designs:
        lines.extend([
            f"### {row['experiment']}",
            "",
            f"`{row['explicit_base_cli']}`",
            "",
        ])

    lines.extend([
        "## Arm-specific changes from each experiment base",
        "",
        "| Experiment | Arm | Parameter | Value |",
        "|---|---|---|---|",
    ])
    for row in arm_rows:
        lines.append(f"| {row['experiment']} | `{row['arm']}` | `{row['parameter']}` | `{row['value']}` |")

    fixed_lookup: OrderedDict[str, dict[str, str]] = OrderedDict()
    for row in fixed_rows:
        if row["setting"] in FOCAL_FIXED_SETTINGS:
            fixed_lookup.setdefault(row["setting"], {})[row["experiment"]] = row["value"]
    lines.extend([
        "",
        "## Code-fixed ecology and access settings",
        "",
        "These values are literal assignments in `make_args` rather than command-line flags. Only settings that directly describe initialization, food renewal, food persistence, or food sensing are shown here; the machine-readable file includes every literal assignment.",
        "",
        "| Runtime setting | E1 | E2 | E3 | E4 | E5 | E6 | T2-RB |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    labels = list(SPEC_PATHS)
    for setting, values in fixed_lookup.items():
        lines.append("| `" + setting + "` | " + " | ".join(f"`{values.get(label, '')}`" for label in labels) + " |")

    lines.extend([
        "",
        "## Machine-readable tables",
        "",
        "- `experiment_parameter_matrix.csv`: one row per arm, including design fields and every effective scientific driver parameter.",
        "- `experiment_parameter_origins.csv`: one row per arm and parameter, with origin marked as `driver_default`, `base_spec`, or `arm_spec`.",
        "- `experiment_code_fixed_settings.csv`: literal runtime settings assigned inside `make_args` at each recorded run revision.",
        "- `experiment_design_provenance.csv`: seed ranges, horizons, run counts, specification locations, and freeze identifiers.",
        "",
        "The exporter also verifies every archived result row against the expected arm, seed, horizon, and ordered launch-flag sequence. The seed range notation is a compact description of the archived seed list; the exporter checks uniqueness but does not assume contiguity. Boolean driver flags are written as `true` or `false`, `null` denotes an argparse default of `None`, and a blank wide-matrix cell means that the parameter was absent from that run revision's driver.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/publication_value_of_information_2026-09-13/supplement"),
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = repo_root / output_dir

    designs, wide_rows, long_rows, arm_rows, fixed_rows = build_tables(repo_root)
    write_csv(output_dir / "experiment_design_provenance.csv", designs)
    write_csv(output_dir / "experiment_parameter_matrix.csv", wide_rows)
    write_csv(output_dir / "experiment_parameter_origins.csv", long_rows)
    write_csv(output_dir / "experiment_code_fixed_settings.csv", fixed_rows)
    (output_dir / "PARAMETER_TABLES.en.md").write_text(
        markdown(designs, arm_rows, fixed_rows), encoding="utf-8", newline="\n"
    )
    print(
        f"wrote {len(designs)} experiment designs, {len(wide_rows)} arms, "
        f"{len(long_rows)} parameter-origin rows, and {len(fixed_rows)} code-fixed rows"
    )


if __name__ == "__main__":
    main()
