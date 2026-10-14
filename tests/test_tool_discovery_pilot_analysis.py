import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import analyze_tool_discovery_pilot as ap  # noqa: E402


def _cell(name, c1_mean, c1_se, ticks, eps, q, ok=True):
    return {"dir": name, "c1_mean": c1_mean, "c1_se": c1_se, "ticks": ticks,
            "epsilon": eps, "q_init": q, "pass": ok}


def test_select_best_c1_among_gate_passing_cells():
    cells = [_cell("a", 0.5, 0.01, 800, 0.1, 0, ok=False),  # best but fails a gate
             _cell("b", 0.3, 0.01, 800, 0.1, 0),
             _cell("c", 0.4, 0.01, 1600, 0.2, 0)]
    assert ap.select_cell(cells)["selected"] == "c"


def test_one_se_tie_prefers_fewer_ticks_then_smaller_epsilon_then_q0():
    cells = [_cell("best", 0.40, 0.02, 1600, 0.05, 0),
             _cell("tie_t800_e02", 0.39, 0.05, 800, 0.2, 0),
             _cell("tie_t800_e01_q10", 0.385, 0.05, 800, 0.1, 10),
             _cell("tie_t800_e01_q0", 0.385, 0.05, 800, 0.1, 0),
             _cell("outside", 0.37, 0.05, 800, 0.05, 0)]  # 0.03 > 1 SE of best (0.02)
    sel = ap.select_cell(cells)
    assert sel["selected"] == "tie_t800_e01_q0"
    assert "outside" not in sel["tied_within_1se"]


def test_no_passing_cell_reports_stop_reason():
    sel = ap.select_cell([_cell("a", 0.5, 0.01, 800, 0.1, 0, ok=False)])
    assert sel["selected"] is None


def test_t_cdf_matches_known_values():
    assert ap.t_cdf(0.0, 5) == pytest.approx(0.5)
    assert ap.t_cdf(1.0, 1) == pytest.approx(0.75, abs=1e-9)  # Cauchy
    assert ap.t_cdf(-2.0096, 49) == pytest.approx(0.025, abs=1e-4)


def test_power_n_is_a_checked_multiple_of_ten(monkeypatch):
    # Guenther n = 44 for dz 0.5 -> start at 50; power below 0.90 at 50 forces 60.
    monkeypatch.setattr(ap, "bootstrap_dz", lambda diffs: [0.5] * 10000)
    calls = []

    def fake_power(n, dz, reps=10000):
        calls.append(n)
        return 0.85 if n < 60 else 0.95
    monkeypatch.setattr(ap, "simulated_power", fake_power)
    res = ap.seed_count([0.5, 1.5, 1.0, 0.0, 2.0] * 10)
    assert res["n_guenther"] == 44 and calls == [50, 60] and res["n"] == 60


def test_power_stops_above_max_seeds(monkeypatch):
    monkeypatch.setattr(ap, "bootstrap_dz", lambda diffs: [0.05] * 10000)
    monkeypatch.setattr(ap, "simulated_power", lambda n, dz, reps=10000: 0.5)
    res = ap.seed_count([0.5, 1.5, 1.0, 0.0, 2.0] * 10)
    assert res["n"] is None and "2000" in res["stop"]


def test_t_critical_and_guenther():
    assert ap.t_crit(0.975, 49) == pytest.approx(2.0096, abs=1e-3)
    assert ap.t_crit(0.975, 9) == pytest.approx(2.2622, abs=1e-3)
    assert ap.guenther_n(0.5) == 44  # (3.242/0.5)^2 + 1.92 = 43.96 -> 44


def test_seed_count_rules():
    zero_pos = ap.seed_count([0.2] * 50)
    assert zero_pos["n"] == 50 and zero_pos["stop"] is None
    assert ap.seed_count([0.0] * 50)["stop"] is not None
    neg = ap.seed_count([-1.0, -0.5, -0.8, -1.2, 0.1] * 10)
    assert neg["n"] is None and neg["stop"] is not None
    big = ap.seed_count([1.0, 1.2, 0.8, 1.1, 0.9] * 10, sim_reps=500)
    assert big["n"] == 50 and big["dz_safe"] > 0  # huge effect -> minimum seeds


def _write_cell(root: Path, name: str, rows: list[dict], complete=True):
    d = root / name
    (d / "runs").mkdir(parents=True)
    for r in rows:
        (d / "runs" / f"seed{r['seed']}_{r['condition']}.summary.json").write_text(json.dumps(r))
    n = len(rows)
    (d / "manifest.json").write_text(json.dumps(
        {"expected_runs": n, "completed_runs": n if complete else n - 1, "missing": []}))
    return d


def _row(seed, cond, net, functional=1, frate=0.1):
    return {"seed": seed, "condition": cond, "final_net_per_alive_tick": net,
            "final_food_per_alive_tick": net + 0.5, "final_effort": 100.0, "final_craft_cost": 50.0,
            "final_gather_cost": 50.0, "final_agent_ticks": 200, "n_functional_objects": functional,
            "functional_rate": frate,
            "config": {"epsilon": 0.1, "q_init": 0, "ticks": 800}}


def test_run_s1_gates_and_incomplete_folder(tmp_path):
    rows = []
    for s in range(1000, 1010):
        j = (s % 3) * 0.01
        rows += [_row(s, "C0", -1.0 + j, functional=1 if s % 2 else 0, frate=0.05 + j),
                 _row(s, "C1", 0.3 + j), _row(s, "C2", 0.1 + j / 2),
                 _row(s, "C3", 0.6 + j, frate=0.5 + j), _row(s, "C4", 0.2 + j)]
    _write_cell(tmp_path, "tool_discovery_pilot_s1_e010_q0_t800", rows)
    seeds = tuple(range(1000, 1010))
    res = ap.run_s1(tmp_path, seeds=seeds, n_cells=1)
    cell = res["cells"][0]
    assert cell["gate_a"] and cell["gate_b2"] and cell["pass"]
    assert cell["gate_b1_c0_fraction_functional"] == pytest.approx(0.5)
    assert cell["c1_minus_c2"]["n_pairs"] == 10
    assert cell["gate_a_components"]["craft_cost_per_tick"]["mean_diff"] == pytest.approx(0.0)
    assert res["selection"]["selected"] == "tool_discovery_pilot_s1_e010_q0_t800"

    with pytest.raises(ValueError, match="expected 16"):
        ap.run_s1(tmp_path, seeds=seeds)  # only 1 of 16 cells present
    with pytest.raises(ValueError, match="do not match"):
        ap.run_s1(tmp_path, seeds=tuple(range(1000, 1011)), n_cells=1)  # a seed is missing

    _write_cell(tmp_path, "tool_discovery_pilot_s1_e020_q0_t800", rows, complete=False)
    with pytest.raises(ValueError, match="incomplete"):
        ap.run_s1(tmp_path, seeds=seeds, n_cells=2)


def test_missing_condition_is_refused(tmp_path):
    rows = [_row(s, c, 0.1 * i) for s in range(1000, 1005) for i, c in enumerate(("C0", "C1", "C2", "C3"))]
    _write_cell(tmp_path, "tool_discovery_pilot_s1_e010_q0_t800", rows)
    with pytest.raises(ValueError, match="do not match"):
        ap.run_s1(tmp_path, seeds=tuple(range(1000, 1005)), n_cells=1)


def test_missing_primary_value_is_refused(tmp_path):
    rows = [_row(s, c, 0.1 * i + 0.01 * s) for s in range(1000, 1005)
            for i, c in enumerate(("C0", "C1", "C2", "C3", "C4"))]
    rows[0]["final_net_per_alive_tick"] = None
    _write_cell(tmp_path, "tool_discovery_pilot_s1_e010_q0_t800", rows)
    with pytest.raises(ValueError, match="lack a value"):
        ap.run_s1(tmp_path, seeds=tuple(range(1000, 1005)), n_cells=1)
