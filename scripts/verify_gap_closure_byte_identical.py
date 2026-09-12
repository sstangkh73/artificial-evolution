# -*- coding: utf-8 -*-
"""Byte-identical gate for the G1-G6 gap-closure patches (P0-P3).

Every mechanism and telemetry channel added for experiments E1-E5 is opt-in. This
script is the evidence for the project rule that says so: with the new flags left
at their defaults, a run must reproduce the pre-patch trajectory exactly, and
switching the *observation-only* channels on must not perturb the trajectory
either (they draw no RNG and reorder nothing).

Two checks:

  A. DEFAULTS vs PRE-PATCH. Needs a checkout of the reference commit; pass it with
     --reference-tree. Compares the full run dump, ignoring only `elapsed_seconds`
     (wall-clock).
  B. TELEMETRY ON vs TELEMETRY OFF, both at the current tree. Compares the full
     dump after removing the keys the telemetry itself adds. Any other difference
     means the telemetry changed the simulation and is not read-only.

Usage:
    python scripts/verify_gap_closure_byte_identical.py --work-dir <tmp> \
        [--reference-tree <path to pre-patch checkout>]

Exit code 0 = all requested checks passed.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent

# A toxin-study-shaped run: value learning on, toxic fruit with age-dependent
# detox, mortality + aging on, v2 genes. Short enough to be a gate, rich enough
# that every patched code path is exercised.
RUN_ARGS = [
    "--seed", "20260910", "--ticks", "400", "--population", "20", "--world", "60",
    "--value-learning", "--low-value-food", "1.5",
    "--toxic-food", "3", "--toxin-acute-penalty", "50", "--toxin-damage-coeff", "0.5",
    "--toxin-detox-ticks", "4",
    "--mortal", "--starvation-death", "--aging", "--model", "v2",
]

# Keys the opt-in telemetry adds to each agent_diet_summary row (check B ignores
# them; their presence is what is being switched on).
TELEMETRY_ROW_KEYS = {
    "death_reason", "completed_lifespan", "children_count", "distance_traveled",
    "damage", "toxin_ingested_total", "toxin_damage_total", "maintenance_energy_total",
    "body_mass", "somatic_maintenance", "repair_efficiency", "damage_resistance",
    "toxin_tolerance", "encounters_by_kind_age",
}


def _run(tree: Path, dump: Path, extra: list[str]) -> dict:
    cmd = [sys.executable, "scripts/food_value_study_driver.py", *RUN_ARGS, *extra,
           "--output", str(dump.with_suffix(".out")), "--dump", str(dump)]
    subprocess.run(cmd, cwd=tree, check=True, capture_output=True)
    return json.loads(dump.read_text(encoding="utf-8"))


def _normalise(summary: dict, strip_telemetry: bool) -> str:
    summary = dict(summary)
    summary.pop("elapsed_seconds", None)  # wall clock, not a simulation output
    if strip_telemetry:
        summary["agent_diet_summary"] = [
            {k: v for k, v in row.items() if k not in TELEMETRY_ROW_KEYS}
            for row in summary.get("agent_diet_summary") or []
        ]
    return json.dumps(summary, indent=1, sort_keys=True, ensure_ascii=False)


def _report(name: str, left: str, right: str) -> bool:
    if left == right:
        print(f"PASS  {name}")
        return True
    print(f"FAIL  {name}")
    left_lines, right_lines = left.splitlines(), right.splitlines()
    shown = 0
    for index, (a, b) in enumerate(zip(left_lines, right_lines)):
        if a != b and shown < 10:
            print(f"      line {index + 1}: {a.strip()!r} != {b.strip()!r}")
            shown += 1
    if len(left_lines) != len(right_lines):
        print(f"      line count {len(left_lines)} != {len(right_lines)}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", required=True, help="scratch directory for run dumps")
    parser.add_argument("--reference-tree", default=None,
                        help="checkout of the pre-patch commit; enables check A")
    args = parser.parse_args()

    work = Path(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)
    ok = True

    default_now = _run(_ROOT, work / "now_default.json", [])

    if args.reference_tree:
        reference = _run(Path(args.reference_tree), work / "reference.json", [])
        ok &= _report(
            "A. defaults reproduce the pre-patch run exactly",
            _normalise(reference, strip_telemetry=False),
            _normalise(default_now, strip_telemetry=False),
        )
    else:
        print("SKIP  A. defaults vs pre-patch (no --reference-tree given)")

    telemetry_on = _run(
        _ROOT, work / "now_telemetry.json",
        ["--encounter-telemetry", "--agent-outcome-telemetry"],
    )
    ok &= _report(
        "B. observation-only telemetry does not perturb the simulation",
        _normalise(default_now, strip_telemetry=True),
        _normalise(telemetry_on, strip_telemetry=True),
    )

    encounters = sum(
        counts.get("seen", 0)
        for row in telemetry_on.get("agent_diet_summary") or []
        for counts in (row.get("encounters_by_kind_age") or {}).values()
    )
    print(f"INFO  telemetry run recorded {encounters} food encounters "
          f"across {len(telemetry_on.get('agent_diet_summary') or [])} observed agents")
    if encounters <= 0:
        print("FAIL  telemetry run recorded no encounters -- the check proves nothing")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
