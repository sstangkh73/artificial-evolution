"""Validate the 2D fracture prototype and time one strike.

python prototypes/fracture_poc/bench.py [--sizes 32 48 64] [--out file.json]
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fracture2d as fx  # noqa: E402

# Placeholder constants for a fine-grained siliceous stone (chert/flint class).
# Order of magnitude only; every value must be replaced by a cited source
# before the real world uses it (see docs/physics_world/00_design.md).
CHERT = fx.Material("chert_placeholder", youngs_modulus_pa=70e9, poisson_ratio=0.2, density_kg_m3=2600,
                    toughness_pa_sqrt_m=1.5e6, flaw_size_m=1e-4)
# A coarse, tougher-but-weaker stone for contrast (sandstone-like placeholder).
COARSE = fx.Material("coarse_placeholder", youngs_modulus_pa=20e9, poisson_ratio=0.25, density_kg_m3=2300,
                     toughness_pa_sqrt_m=0.8e6, flaw_size_m=1e-3)


def validate_bar() -> dict:
    """Uniaxial tension: sigma_x must equal F / (height * thickness)."""
    ny, nx = 6, 30
    stone = fx.Stone(np.ones((ny, nx), np.int64), (CHERT,), 0.002)
    nodes, tris, mat, _ = fx.build_mesh(stone)
    left = [n for n, (x, y) in enumerate(nodes) if x < 1e-12]
    right = [n for n, (x, y) in enumerate(nodes) if abs(x - nx * stone.cell_size_m) < 1e-12]
    force = 1000.0
    # Consistent nodal loads on the right edge (end nodes get half).
    ys = sorted(right, key=lambda n: nodes[n][1])
    loads = {n: (force / (len(ys) - 1) * (0.5 if k in (0, len(ys) - 1) else 1.0), 0.0) for k, n in enumerate(ys)}
    # Fix x on the left edge and y at one node only (no Poisson restraint).
    alive = np.ones(len(tris), bool)
    # Re-solve with proper supports: emulate roller by fixing both dofs of
    # left-edge nodes (clamped). Check stress far from the clamp.
    s1 = fx.solve_stress(stone, nodes, tris, mat, alive, set(left), loads)
    expected = force / (ny * stone.cell_size_m * stone.thickness_m)
    centroid_x = nodes[tris].mean(axis=1)[:, 0]
    far = centroid_x > 0.6 * nx * stone.cell_size_m
    rel = float(np.max(np.abs(s1[far] - expected)) / expected)
    return {"expected_pa": expected, "max_relative_error_far_from_clamp": rel, "passed": rel < 0.02}


def strike_case(n: int, angle_deg: float, force_n: float, material=CHERT) -> dict:
    stone = fx.disc_stone(n, material)
    h = stone.cell_size_m
    ny, nx = stone.cells.shape
    # Strike near the right end of the pebble, from above-right; support under
    # the left half (stone resting on an anvil).
    rows = np.flatnonzero(stone.cells[:, nx - 4 if nx > 8 else nx - 1])
    target = ((nx - 4) * h, (rows.max() + 1) * h)
    support = (0.35 * nx * h, (np.flatnonzero(stone.cells[:, int(0.35 * nx)]).min()) * h)
    res = fx.strike(stone, target, angle_deg, force_n, support)
    flakes = [p for p in res.pieces[1:] if p["elements"] >= 6]
    return {
        "n": n, "angle_deg": angle_deg, "force_n": force_n, "material": material.name,
        "seconds": round(res.solve_seconds, 3), "iterations": res.iterations,
        "failed_elements": res.failed_elements, "pieces": len(res.pieces),
        "core_min_edge_angle_deg": res.pieces[0]["min_edge_angle_deg"] if res.pieces else None,
        "flake_min_edge_angle_deg": [round(p["min_edge_angle_deg"], 1) for p in flakes if p["min_edge_angle_deg"]],
        "flake_mass_g": [round(p["mass_kg"] * 1000, 1) for p in flakes],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[32, 48, 64])
    ap.add_argument("--angles", type=float, nargs="+", default=[-30, -60, -90, -120, -150])
    ap.add_argument("--forces", type=float, nargs="+", default=[2000, 5000, 10000])
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    report = {"scipy": fx.coo_matrix is not None, "validation": validate_bar(),
              "strength_mpa": {m.name: m.tensile_strength_pa / 1e6 for m in (CHERT, COARSE)}, "timing": [], "sweep": []}
    print(json.dumps(report["validation"]), report["strength_mpa"], "scipy:", report["scipy"], flush=True)
    for n in args.sizes:
        r = strike_case(n, -60, 5000)
        report["timing"].append(r)
        print("timing", r["n"], r["seconds"], "s", r["iterations"], "it", flush=True)
    n = args.sizes[0]
    for material in (CHERT, COARSE):
        for force in args.forces:
            for angle in args.angles:
                r = strike_case(n, angle, force, material)
                report["sweep"].append(r)
                print("sweep", material.name[:6], force, angle, r["pieces"], r["flake_min_edge_angle_deg"][:3],
                      r["flake_mass_g"][:3], r["seconds"], flush=True)
    if args.out:
        args.out.write_text(json.dumps(report, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
