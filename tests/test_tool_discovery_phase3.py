"""Phase 3 additions: rate-based Level A, reuse_delta and the paired Level B analysis."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from simulation.tool_discovery import ArenaConfig, config_dict, run_arena  # noqa: E402
from simulation.tool_discovery_metrics import summarize_run  # noqa: E402
import analyze_tool_discovery_level_b as level_b  # noqa: E402


def test_summary_reports_level_a_rates_and_reuse_delta():
    arena = run_arena(ArenaConfig(seed=2, condition="C3", n_agents=6, ticks=200))
    s = summarize_run(arena.events, arena.ledger, config_dict(arena.config))
    assert "level_b" not in s and isinstance(s["level_b_run"], bool)
    assert s["n_crafted"] > 0
    assert s["functional_rate"] == s["n_functional_objects"] / s["n_crafted"]
    assert s["functional_per_agent"] == s["n_functional_objects"] / 6
    if s["reuse_after_good"] is not None and s["reuse_after_bad"] is not None:
        assert s["reuse_delta"] == pytest.approx(s["reuse_after_good"] - s["reuse_after_bad"])
    else:
        assert s["reuse_delta"] is None


def test_no_crafts_gives_no_functional_rate():
    cfg = config_dict(ArenaConfig(seed=0, condition="C0", n_agents=2, ticks=4))
    s = summarize_run([], [], cfg)
    assert s["functional_rate"] is None
    assert s["functional_per_agent"] == 0
    assert s["reuse_delta"] is None


def _runs(rows):
    return {(r["condition"], r["seed"]): r for r in rows}


def test_paired_comparison_pairs_by_seed_and_drops_missing():
    runs = _runs([
        {"condition": "C1", "seed": 1000, "reuse_delta": 0.5, "level_b_run": True},
        {"condition": "C2", "seed": 1000, "reuse_delta": 0.1, "level_b_run": False},
        {"condition": "C1", "seed": 1001, "reuse_delta": 0.3, "level_b_run": True},
        {"condition": "C2", "seed": 1001, "reuse_delta": None, "level_b_run": True},
        {"condition": "C1", "seed": 1002, "reuse_delta": 0.0, "level_b_run": False},
        {"condition": "C2", "seed": 1002, "reuse_delta": 0.2, "level_b_run": False},
        {"condition": "C1", "seed": 1003, "reuse_delta": 0.9, "level_b_run": True},  # no C2 partner
    ])
    r = level_b.paired_comparison(runs, "C1", "C2", "reuse_delta")
    assert r["n_seeds_paired"] == 3 and r["n_pairs"] == 2 and r["n_dropped_missing"] == 1
    assert r["mean_diff"] == pytest.approx((0.4 + -0.2) / 2)
    assert (r["n_treatment_higher"], r["n_ties"], r["n_control_higher"]) == (1, 0, 1)
    lo, hi = r["ci95_mean_diff"]
    assert -0.2 <= lo <= r["mean_diff"] <= hi <= 0.4

    b = level_b.paired_comparison(runs, "C1", "C2", "level_b_run")
    assert b["n_pairs"] == 3
    assert b["mean_diff"] == pytest.approx(1 / 3)  # bools count as 0/1


def test_analyze_reads_runner_summaries(tmp_path):
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    for seed in (1000, 1001):
        for cond, net in (("C0", 0.25), ("C1", 0.5)):
            row = {"condition": cond, "seed": seed, "final_net_per_alive_tick": net + seed % 2}
            (runs_dir / f"seed{seed:04d}_{cond}.summary.json").write_text(json.dumps(row), encoding="utf-8")
    out = level_b.analyze(tmp_path, [("C1", "C0")], metrics=("final_net_per_alive_tick",))
    assert len(out) == 1
    assert out[0]["n_pairs"] == 2
    assert out[0]["mean_diff"] == 0.25
    assert out[0]["sd_diff"] == 0
    assert out[0]["dz"] is None


def _write(runs_dir, row):
    path = runs_dir / f"seed{row['seed']:04d}_{row['condition']}.summary.json"
    path.write_text(json.dumps(row), encoding="utf-8")


def test_no_discovery_is_censored_not_dropped(tmp_path):
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    cfg = {"ticks": 400, "epsilon": 0.1}
    _write(runs_dir, {"condition": "C1", "seed": 1000, "first_discovery_tick": 100, "config": cfg})
    _write(runs_dir, {"condition": "C2", "seed": 1000, "first_discovery_tick": None, "config": cfg})
    out = level_b.analyze(tmp_path, [("C1", "C2")], metrics=("first_discovery_tick",))[0]
    assert out["n_pairs"] == 1
    assert out["mean_diff"] == 100 - 400


def test_mixed_grid_cells_are_refused(tmp_path):
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    _write(runs_dir, {"condition": "C1", "seed": 1000, "config": {"ticks": 400, "epsilon": 0.1}})
    _write(runs_dir, {"condition": "C2", "seed": 1000, "config": {"ticks": 400, "epsilon": 0.2}})
    with pytest.raises(ValueError):
        level_b.load_runs(tmp_path)
