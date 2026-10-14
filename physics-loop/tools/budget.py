"""Print each agent's remaining token budget and who should lead this round.

Usage:
    python physics-loop/tools/budget.py                 # report + LEAD=...
    python physics-loop/tools/budget.py add AGENT N     # log N tokens for claude|codex
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

LOOP = Path(__file__).resolve().parents[1]
USAGE = LOOP / ".loop" / "usage.csv"


def used() -> dict[str, int]:
    totals = {"claude": 0, "codex": 0}
    if USAGE.exists():
        with USAGE.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                totals[row["agent"]] = totals.get(row["agent"], 0) + int(row["tokens"])
    return totals


def add(agent: str, tokens: int) -> None:
    USAGE.parent.mkdir(parents=True, exist_ok=True)
    new = not USAGE.exists()
    with USAGE.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        if new:
            writer.writerow(["time", "agent", "tokens"])
        writer.writerow([time.strftime("%Y-%m-%dT%H:%M:%S"), agent, tokens])


def main() -> None:
    if len(sys.argv) == 4 and sys.argv[1] == "add":
        add(sys.argv[2], int(sys.argv[3]))
        return
    budget = json.loads((LOOP / "budget.json").read_text(encoding="utf-8"))
    totals = used()
    remaining = {}
    for agent in ("claude", "codex"):
        cap = budget[f"{agent}_tokens"]
        remaining[agent] = max(0.0, 1 - totals.get(agent, 0) / cap)
        print(f"{agent}: used {totals.get(agent, 0):,} / {cap:,} -> {remaining[agent]:.0%} left")
    # The agent with more budget left does the heavy work; ties go to Claude.
    lead = "codex" if remaining["codex"] > remaining["claude"] else "claude"
    if remaining[lead] == 0:
        lead = "none"
    print(f"LEAD={lead}")


if __name__ == "__main__":
    main()
