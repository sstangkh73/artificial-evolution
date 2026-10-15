"""Judge for physics-loop round 1. Exit 0 = done, 1 = not done, 3 = technical checks pass but red team missing/failed.

python physics-loop/tools/verify_physics.py [--quick]

Writes physics-loop/.loop/verify_status.json with the red-team key of the current tree.
The AI must not edit this file (run-loop.ps1 stops if it changes).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOOP = ROOT / "physics-loop"
SPEC = LOOP / "spec"
PLAN = ROOT / "worklog" / "2026-10-15-physics-loop-r1" / "plan.md"
RESULTS = ROOT / "data" / "lithics_validation" / "results.json"
DOCS = [ROOT / "docs" / "physics_world" / "02_physics_spec.md", ROOT / "docs" / "physics_world" / "03_validation_report.md"]
KEY_PATHS = ["lithics", "tests/lithics", "data/lithics_validation", "docs/physics_world"]
FORBIDDEN_WORDS = re.compile(r"sharp|quality|knappab|recipe|tool_type", re.I)
ANALYST_MODULES = re.compile(r"^(measure|validate|bench)")

failures: list[str] = []


def check(ok: bool, msg: str) -> bool:
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        failures.append(msg)
    return ok


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def redteam_key() -> str:
    parts = [git("rev-parse", f"HEAD:{p}") for p in KEY_PATHS]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:12]


def run(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout,
                          encoding="utf-8", errors="replace")


def check_static() -> None:
    check((ROOT / "lithics" / "__init__.py").exists(), "package lithics/ exists")
    if PLAN.exists():
        open_steps = [l for l in PLAN.read_text(encoding="utf-8").splitlines() if re.match(r"\s*- \[ \]", l)]
        check(not open_steps, f"plan.md has no open steps ({len(open_steps)} open)")
    else:
        check(False, "plan.md exists")
    for d in DOCS:
        check(d.exists() and len(d.read_text(encoding="utf-8")) > 1500, f"doc {d.relative_to(ROOT)} written")
    bad = []
    for f in sorted((ROOT / "lithics").rglob("*.py")) if (ROOT / "lithics").exists() else []:
        if ANALYST_MODULES.match(f.name):
            continue
        text = f.read_text(encoding="utf-8")
        if FORBIDDEN_WORDS.search(text):
            bad.append(f"{f.name}: forbidden word")
        if re.search(r"^\s*(from\s+lithics\.measure|from\s+\.\s*measure|from\s+\.measure|import\s+lithics\.measure)", text, re.M):
            bad.append(f"{f.name}: imports measure")
    check(not bad, "physics modules free of outcome words / measure imports " + "; ".join(bad[:5]))


def check_materials() -> None:
    spec = json.loads((SPEC / "materials.json").read_text(encoding="utf-8"))["materials"]
    code = ("import json,sys; from lithics.materials import load_material, MATERIAL_NAMES as N; "
            "fs=['youngs_modulus_pa','poisson_ratio','density_kg_m3','fracture_toughness_pa_sqrt_m','tensile_strength_pa','microstructure_scale_m']; "
            "print(json.dumps({'names':list(N),'v':{n:{f:getattr(load_material(n),f) for f in fs} for n in N}}))")
    p = run([sys.executable, "-c", code], 120)
    if not check(p.returncode == 0, "lithics.materials importable"):
        print(p.stderr[-800:])
        return
    got = json.loads(p.stdout.strip().splitlines()[-1])
    check(sorted(got["names"]) == sorted(spec), "MATERIAL_NAMES matches spec")
    mism = [f"{n}.{f}" for n, fields in got["v"].items() for f, v in fields.items()
            if n in spec and abs(float(v) - float(spec[n][f]["value"])) > 1e-9 * max(1.0, abs(float(spec[n][f]["value"])))]
    check(not mism, "material constants equal spec values " + ", ".join(mism[:6]))


def _num(m: dict, k: str):
    v = m.get(k)
    return v


def judge(criteria: dict, results_minutes: float | None) -> None:
    def m(cid: str) -> dict:
        c = criteria.get(cid)
        if not check(isinstance(c, dict) and isinstance(c.get("metrics"), dict), f"{cid} present in results"):
            return {}
        return c["metrics"]

    try:
        x = m("V1")
        if x:
            a = [float(v) for v in x["cone_included_angle_deg"]]
            check(len(a) >= 4 and all(121 <= v <= 151 for v in a) and max(a) - min(a) <= 10, f"V1 cone angle {a}")
        x = m("V2")
        if x:
            check(x["n"] >= 60 and x["ci_pd"][0] > 0 and x["ci_epa"][0] > 0 and x["ci_aob"][1] < 0 and bool(x.get("aob_convention_source")),
                  f"V2 EPA-PD-AOB n={x['n']} ci_pd={x['ci_pd']} ci_epa={x['ci_epa']} ci_aob={x['ci_aob']}")
        x = m("V3")
        if x:
            check(x["n"] >= 8 and x["spearman_rho"] > 0 and x["p_value"] < 0.05, f"V3 min energy vs flake size rho={x['spearman_rho']} p={x['p_value']}")
        x = m("V4")
        if x:
            check(x["cv_ratio_ci"][0] > 1 and x["single_flake_frac_obsidian"] > x["single_flake_frac_granite"],
                  f"V4 predictability ci={x['cv_ratio_ci']} single {x['single_flake_frac_obsidian']} vs {x['single_flake_frac_granite']}")
        x = m("V5")
        if x:
            r = x["ratio_to_glass"]
            check(set(r) >= {"obsidian", "chert_flint", "basalt"} and all(0.75 <= float(v) <= 1.33 for v in r.values()), f"V5 ratio to glass {r}")
        x = m("V6")
        if x:
            a, c = x["rel_dev_area"], x["cone_angle_dev_deg"]
            check(len(a) >= 2 and len(c) >= 2 and all(float(v) <= 0.10 for v in a.values()) and all(float(v) <= 5 for v in c.values()),
                  f"V6 mesh convergence area={a} cone={c}")
        x = m("V7")
        if x:
            check(x["frac_monotone_pd"] >= 0.8 and x["frac_monotone_epa"] >= 0.8 and x["bar_rel_error_3d"] <= 0.02
                  and x["n_pairs_pd"] >= 2 and x["n_pairs_epa"] >= 1, f"V7 3D agreement {x}")
        x = m("V8")
        if x:
            check(x["spearman_force_vs_tip_radius"] > 0 and x["p_value"] < 0.05 and x["n"] >= 10
                  and x["force_ratio_obsidian_to_granite"] < 1 and bool(x["target_material_sources"]), "V8 cutting physics")
        x = m("V9")
        if x:
            check(x["median_strike_seconds_2d"] <= 60.0 and (results_minutes or 1e9) <= 240, f"V9 speed {x['median_strike_seconds_2d']} s, suite {results_minutes} min")
        x = m("V10")
        if x:
            check(x["identical_rerun"] is True and x["max_mass_conservation_rel_error"] <= 1e-9 and x["elements_in_multiple_pieces"] == 0, "V10 determinism/conservation")
        x = m("V11")
        if x:
            check(x["bar_rel_error"] <= 0.02 and x["kirsch_scf_rel_error"] <= 0.05 and x["hertz_pmax_rel_error"] <= 0.10 and x["sen_k_rel_error"] <= 0.05,
                  f"V11 analytic {x}")
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        check(False, f"results.json metrics malformed: {exc!r}")


def check_results(quick: bool) -> None:
    if not check(RESULTS.exists(), "data/lithics_validation/results.json exists"):
        return
    res = json.loads(RESULTS.read_text(encoding="utf-8"))
    check(res.get("lithics_tree") == git("rev-parse", "HEAD:lithics"), "results produced from current committed lithics/ tree")
    check(res.get("code_dirty") is False, "results produced from clean code")
    judge(res.get("criteria", {}), res.get("suite_minutes"))
    if quick or failures:
        return
    with tempfile.TemporaryDirectory() as tmp:
        p = run([sys.executable, "-m", "lithics.validate", "--only", "V10,V11", "--out", tmp], 1800)
        if not check(p.returncode == 0, "re-run of V10,V11 succeeds"):
            print(p.stderr[-1500:])
            return
        again = json.loads((Path(tmp) / "results.json").read_text(encoding="utf-8"))["criteria"]
        for cid in ("V10", "V11"):
            old, new = res["criteria"][cid]["metrics"], again[cid]["metrics"]
            same = all(
                (abs(float(old[k]) - float(new[k])) <= 1e-9 * max(1.0, abs(float(old[k]))) if isinstance(old[k], (int, float)) and not isinstance(old[k], bool) else old[k] == new[k])
                for k in old if k in new)
            check(same, f"{cid} reproduces on re-run")


def check_redteam(key: str) -> bool:
    ok = True
    for who in ("claude", "codex"):
        f = LOOP / "redteam" / f"{key}-{who}.md"
        if not f.exists():
            print(f"WAIT  red team {who} missing for key {key}")
            ok = False
            continue
        lines = [l.strip() for l in f.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
        verdict = next((l for l in reversed(lines) if l.startswith("VERDICT:")), "")
        if verdict != "VERDICT: PASS":
            print(f"FAIL  red team {who}: {verdict or 'no verdict'} ({f.relative_to(ROOT)})")
            ok = False
        else:
            print(f"PASS  red team {who}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="skip the slow re-run")
    args = ap.parse_args()
    check_static()
    p = run([sys.executable, "-m", "pytest", "-q", "-x", "--no-header", "-p", "no:cacheprovider", "tests"], 3600)
    tail = (p.stdout or "").strip().splitlines()[-1:] or [""]
    check(p.returncode == 0, f"pytest passes ({tail[0]})")
    if (ROOT / "lithics").exists():
        check_materials()
    check_results(args.quick)
    dirty = git("status", "--porcelain", "--", *KEY_PATHS)
    check(not dirty, "lithics work committed (no uncommitted changes in key paths)")
    key = redteam_key()
    technical = not failures
    rt = check_redteam(key) if technical else False
    status = {"technical_pass": technical, "redteam_key": key, "redteam_pass": rt, "failures": failures}
    (LOOP / ".loop").mkdir(exist_ok=True)
    (LOOP / ".loop" / "verify_status.json").write_text(json.dumps(status, indent=1), encoding="utf-8")
    print(f"\nredteam_key={key} technical_pass={technical} redteam_pass={rt}")
    if not technical:
        print(f"{len(failures)} check(s) failed")
        return 1
    return 0 if rt else 3


if __name__ == "__main__":
    sys.exit(main())
