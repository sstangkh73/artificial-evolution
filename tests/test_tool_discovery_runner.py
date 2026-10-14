"""Phase 3 runner hygiene: dirty-code refusal, strict --resume, C4 in the default conditions."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from simulation.tool_discovery import CONDITIONS  # noqa: E402
import run_tool_discovery as runner  # noqa: E402

TREE = {"simulation": "aaa", "world": "bbb", "scripts": "ccc"}


@pytest.fixture
def fake_git(monkeypatch):
    state = {"dirty": False, "tree": dict(TREE)}
    monkeypatch.setattr(runner, "git_dirty", lambda: state["dirty"])
    monkeypatch.setattr(runner, "git_code_tree", lambda: dict(state["tree"]))
    monkeypatch.setattr(runner, "git_commit", lambda: "deadbeef")
    return state


def run(monkeypatch, out: Path, *extra: str) -> None:
    argv = ["run_tool_discovery.py", "--out", str(out), "--seeds", "1000", "--ticks", "30", "--agents", "3", *extra]
    monkeypatch.setattr(sys, "argv", argv)
    runner.main()


def test_default_conditions_include_c4(fake_git, monkeypatch, tmp_path):
    out = tmp_path / "run"
    run(monkeypatch, out)
    protocol = json.loads((out / "protocol.json").read_text(encoding="utf-8"))
    assert protocol["conditions"] == list(CONDITIONS) and "C4" in protocol["conditions"]
    assert protocol["code_tree"] == TREE and protocol["code_dirty"] is False
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["completed_runs"] == manifest["expected_runs"] == len(CONDITIONS)


def test_dirty_code_is_refused_unless_allowed(fake_git, monkeypatch, tmp_path):
    fake_git["dirty"] = True
    with pytest.raises(SystemExit, match="uncommitted"):
        run(monkeypatch, tmp_path / "refused", "--conditions", "C0")
    assert not (tmp_path / "refused").exists()
    run(monkeypatch, tmp_path / "allowed", "--conditions", "C0", "--allow-dirty")
    protocol = json.loads((tmp_path / "allowed" / "protocol.json").read_text(encoding="utf-8"))
    assert protocol["code_dirty"] is True


@pytest.mark.parametrize("extra, new_tree", [
    (["--conditions", "C0", "--set", "epsilon=0.3"], False),
    (["--conditions", "C0", "--seeds", "1000-1001"], False),  # argparse keeps the last --seeds
    (["--conditions", "C0", "C1"], False),
    (["--conditions", "C0"], True),
])
def test_resume_rejects_mismatch_with_protocol(fake_git, monkeypatch, tmp_path, extra, new_tree):
    out = tmp_path / "run"
    run(monkeypatch, out, "--conditions", "C0")
    if new_tree:
        fake_git["tree"]["simulation"] = "changed"
    with pytest.raises(SystemExit, match="does not match"):
        run(monkeypatch, out, "--resume", *extra)


def test_resume_fills_missing_runs_when_protocol_matches(fake_git, monkeypatch, tmp_path):
    out = tmp_path / "run"
    run(monkeypatch, out, "--conditions", "C0", "C1")
    (out / "runs" / "seed1000_C1.summary.json").unlink()
    run(monkeypatch, out, "--conditions", "C0", "C1", "--resume")
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["completed_runs"] == 2 and not manifest["missing"]


def test_resume_with_dirty_code_is_refused_both_ways(fake_git, monkeypatch, tmp_path):
    clean = tmp_path / "clean"
    run(monkeypatch, clean, "--conditions", "C0")
    fake_git["dirty"] = True
    with pytest.raises(SystemExit, match="committed code"):
        run(monkeypatch, clean, "--conditions", "C0", "--resume", "--allow-dirty")
    dirty = tmp_path / "dirty"
    run(monkeypatch, dirty, "--conditions", "C0", "--allow-dirty")
    fake_git["dirty"] = False
    with pytest.raises(SystemExit, match="code_dirty"):
        run(monkeypatch, dirty, "--conditions", "C0", "--resume")


def test_resume_without_protocol_is_refused(fake_git, monkeypatch, tmp_path):
    out = tmp_path / "run"
    (out / "runs").mkdir(parents=True)
    with pytest.raises(SystemExit, match="no protocol.json"):
        run(monkeypatch, out, "--conditions", "C0", "--resume")


def test_incomplete_run_is_redone_and_stray_runs_are_ignored(fake_git, monkeypatch, tmp_path):
    out = tmp_path / "run"
    run(monkeypatch, out, "--conditions", "C0")
    (out / "runs" / "seed1000_C0.ledger.csv.gz").unlink()
    (out / "runs" / "seed0042_C9.summary.json").write_text("{}", encoding="utf-8")
    run(monkeypatch, out, "--conditions", "C0", "--resume")
    assert (out / "runs" / "seed1000_C0.ledger.csv.gz").exists()
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["completed_runs"] == 1 and not manifest["missing"]
    assert all(name.startswith("runs/seed1000_C0.") for name in manifest["files"])
    assert "seed0042" not in (out / "summary.csv").read_text(encoding="utf-8")


def test_resume_refuses_existing_run_with_other_config(fake_git, monkeypatch, tmp_path):
    out = tmp_path / "run"
    run(monkeypatch, out, "--conditions", "C0")
    path = out / "runs" / "seed1000_C0.summary.json"
    summary = json.loads(path.read_text(encoding="utf-8"))
    summary["config"]["epsilon"] = 0.99
    path.write_text(json.dumps(summary), encoding="utf-8")
    with pytest.raises(SystemExit, match="different config"):
        run(monkeypatch, out, "--conditions", "C0", "--resume")


def test_confirmatory_seeds_are_refused(fake_git, monkeypatch, tmp_path):
    with pytest.raises(SystemExit, match="reserved"):
        run(monkeypatch, tmp_path / "run", "--conditions", "C0", "--seeds", "5000")
    assert not (tmp_path / "run").exists()


def test_missing_git_tree_fails_closed(monkeypatch):
    def broken(*args, **kwargs):
        raise runner.subprocess.CalledProcessError(128, "git")
    monkeypatch.setattr(runner.subprocess, "run", broken)
    with pytest.raises(SystemExit, match="provenance"):
        runner.git_code_tree()
