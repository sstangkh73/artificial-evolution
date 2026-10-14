"""Freeze docs/ysc2027_tool_discovery/confirmatory_config.json (ysc-loop step 7).

config = base_config of data/tool_discovery_pilot_s2_selected/protocol.json
(the cell selected by the pilot rule) minus the per-run fields seed/condition.
Prints the sha256 that 05_confirmatory_protocol.md records.
"""
import dataclasses
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from simulation.tool_discovery import ArenaConfig  # noqa: E402

s2 = json.loads((ROOT / "data/tool_discovery_pilot_s2_selected/protocol.json").read_text(encoding="utf-8"))
base = dict(s2["base_config"])
base.pop("seed")
base.pop("condition")

cfg = ArenaConfig(**base)
cfg.validate()
s2_cfg = ArenaConfig(**s2["base_config"])
same = dataclasses.asdict(cfg) == dict(dataclasses.asdict(s2_cfg), seed=cfg.seed, condition=cfg.condition)
assert same, "confirmatory config differs from the S2 cell"
assert cfg.immortal and cfg.epsilon == 0.05 and cfg.q_init == 0 and cfg.ticks == 1600

spec = {
    "study": "YSC 2027 (29YCSS00443) phase 3 confirmatory run: tool discovery",
    "protocol": "docs/ysc2027_tool_discovery/05_confirmatory_protocol.md",
    "selected_cell": "pilot S1 rule (03 section 6): epsilon=0.05, q_init=0, ticks=1600",
    "conditions": ["C0", "C1", "C2", "C3", "C4"],
    "seeds": list(range(5000, 5050)),
    "config": base,
}
raw = (json.dumps(spec, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
out = ROOT / "docs/ysc2027_tool_discovery/confirmatory_config.json"
if out.exists() and out.read_bytes() != raw:
    sys.exit(f"{out.relative_to(ROOT)} is frozen and differs from the regenerated spec; not overwriting")
if not out.exists():
    out.write_bytes(raw)
print(out.relative_to(ROOT), len(spec["seeds"]), "seeds")
print("sha256", hashlib.sha256(raw).hexdigest())
