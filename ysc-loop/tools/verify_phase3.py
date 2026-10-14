"""Judge for the YSC phase 3 loop: exit 0 only when phase 3 is really done.

It checks evidence, not ticks: tests pass, the default config still
reproduces the committed smoke run, pilot data is complete and came from
committed code on pilot seeds only, the pilot protocol was committed before
any pilot run, and the confirmatory protocol is frozen with a matching hash.
The AI may not edit this file (run-loop.ps1 stops the loop if it changes).
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

DOCS = ROOT / "docs" / "ysc2027_tool_discovery"
PLAN = ROOT / "worklog" / "2026-10-14-ysc-phase3-loop" / "plan.md"
REPORT = PLAN.with_name("report.md")
PILOT_PROTOCOL = DOCS / "03_pilot_protocol.md"
PILOT_RESULTS = DOCS / "04_ผล_pilot.md"
CONFIRM_PROTOCOL = DOCS / "05_confirmatory_protocol.md"
CONFIRM_CONFIG = DOCS / "confirmatory_config.json"
SMOKE = ROOT / "data" / "tool_discovery_smoke_20261014" / "summary.csv"
PILOT_SEEDS = range(1000, 1100)
CONFIRM_MIN_SEED = 5000
CONDITIONS = {"C0", "C1", "C2", "C3", "C4"}

failures: list[str] = []


def check(ok: bool, message: str) -> bool:
    print(("PASS " if ok else "FAIL ") + message)
    if not ok:
        failures.append(message)
    return ok


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")


def main() -> int:
    # 1. Tests.
    tests = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q"], cwd=ROOT, capture_output=True, text=True)
    check(tests.returncode == 0, "pytest tests: " + (tests.stdout.strip().splitlines() or ["no output"])[-1])

    # 2. Default config still reproduces the committed smoke run.
    from simulation.tool_discovery import ArenaConfig, config_dict, run_arena
    from simulation.tool_discovery_metrics import summarize_run

    with SMOKE.open(encoding="utf-8") as fh:
        smoke = {(r["seed"], r["condition"]): r for r in csv.DictReader(fh)}
    for seed, cond in ((0, "C1"), (1, "C3")):
        arena = run_arena(ArenaConfig(seed=seed, condition=cond))
        got = summarize_run(arena.events, arena.ledger, config_dict(arena.config))["final_net_per_alive_tick"]
        want = float(smoke[(str(seed), cond)]["final_net_per_alive_tick"])
        check(abs(got - want) < 1e-12, f"default config reproduces smoke seed {seed} {cond}")

    # 3. Plan fully ticked and report written.
    plan = PLAN.read_text(encoding="utf-8")
    open_steps = re.findall(r"^- \[ \] .*", plan, re.M)
    check(not open_steps, f"plan.md has no open steps ({len(open_steps)} open)")
    check(REPORT.exists() and len(REPORT.read_text(encoding="utf-8")) > 800, "report.md written")

    # 4. Documents exist and are substantive.
    for path, words in (
        (PILOT_PROTOCOL, ("C2", "Gate", "power", "1000")),
        (PILOT_RESULTS, ("C2", "Gate", "power")),
        (CONFIRM_PROTOCOL, ("sha256", "5000")),
    ):
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        check(len(text) > 1500 and all(w.lower() in text.lower() for w in words),
              f"{path.name} exists, >1500 chars, mentions {', '.join(words)}")

    # 5. Pilot protocol was committed before any pilot run (pre-registration).
    added = git("log", "--diff-filter=A", "--format=%H", "--", str(PILOT_PROTOCOL.relative_to(ROOT))).stdout.split()
    prereg = added[-1] if added else None
    check(prereg is not None, "03_pilot_protocol.md is committed")

    # 6. Pilot data: complete, committed code, pilot seeds only, immortal.
    pilot_dirs = sorted(p for p in (ROOT / "data").glob("tool_discovery_pilot_*") if p.is_dir())
    check(bool(pilot_dirs), f"pilot data directories found ({len(pilot_dirs)})")
    for d in pilot_dirs:
        name = d.name
        try:
            protocol = json.loads((d / "protocol.json").read_text(encoding="utf-8"))
            manifest = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            check(False, f"{name}: protocol.json/manifest.json readable ({exc})")
            continue
        check(manifest["completed_runs"] == manifest["expected_runs"] > 0 and not manifest["missing"],
              f"{name}: all runs complete")
        check(protocol.get("code_dirty") is False, f"{name}: run from committed code")
        check(all(s in PILOT_SEEDS for s in protocol["seeds"]), f"{name}: pilot seeds 1000-1099 only")
        check(protocol["base_config"].get("immortal") is True, f"{name}: immortal agents")
        if prereg:
            ok = git("merge-base", "--is-ancestor", prereg, protocol["git_commit"]).returncode == 0
            check(ok, f"{name}: run after the pilot protocol was committed")

    # 7. No data directory anywhere has used confirmatory seeds yet.
    for protocol_path in (ROOT / "data").glob("tool_discovery_*/protocol.json"):
        seeds = json.loads(protocol_path.read_text(encoding="utf-8")).get("seeds", [])
        check(all(s < CONFIRM_MIN_SEED for s in seeds), f"{protocol_path.parent.name}: no confirmatory seeds used")

    # 8. Confirmatory config frozen, valid, and its hash recorded.
    if check(CONFIRM_CONFIG.exists(), "confirmatory_config.json exists"):
        raw = CONFIRM_CONFIG.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        spec = json.loads(raw.decode("utf-8"))
        seeds = spec.get("seeds", [])
        check(bool(seeds) and all(s >= CONFIRM_MIN_SEED for s in seeds), "confirmatory seeds are 5000+")
        check(CONDITIONS <= set(spec.get("conditions", [])), "confirmatory conditions include C0-C4")
        try:
            cfg = ArenaConfig(**spec["config"])
            cfg.validate()
            check(cfg.immortal is True, "confirmatory config is immortal")
        except (KeyError, TypeError, ValueError) as exc:
            check(False, f"confirmatory config loads into ArenaConfig ({exc})")
        protocol_text = CONFIRM_PROTOCOL.read_text(encoding="utf-8") if CONFIRM_PROTOCOL.exists() else ""
        check(digest in protocol_text, "05_confirmatory_protocol.md records the config sha256")
        committed = git("log", "--format=%H", "-1", "--", str(CONFIRM_CONFIG.relative_to(ROOT))).stdout.strip()
        check(bool(committed) and not git("status", "--porcelain", "--", str(CONFIRM_CONFIG.relative_to(ROOT))).stdout.strip(),
              "confirmatory_config.json committed and unchanged")

    print(f"\n{len(failures)} check(s) failed" if failures else "\nALL CHECKS PASSED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
