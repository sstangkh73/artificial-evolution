"""Empirical validation targets for the fracture world from the Dibble et al. glass experiments.

python prototypes/fracture_poc/dibble_targets.py [--out file.json]

Fits cbrt(flake mass) on platform depth (PD), exterior platform angle (EPA) and
angle of blow (AOB) for unbeveled semispherical glass cores struck with a steel
hammer (data: Li et al. 2023, JAMT 30:1284-1325, ESM 3). The simulated world
must reproduce the signs and rough ratios of these coefficients, not the exact
values (our stones, units and 2D geometry differ).
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[2] / "data" / "external" / "dibble_li2023" / "flakes.csv"


def load_glass_semispherical() -> dict[str, np.ndarray]:
    rows = []
    with DATA.open(encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            if (r["coretype"], r["bevel"], r["hmat"]) != ("SEMISPHERICAL", "NONE", "STEEL"):
                continue
            if r["coremat"] not in ("GLASS", ""):
                continue
            try:
                vals = [float(r[k]) for k in ("platthick", "epa", "aob", "fweight")]
            except ValueError:
                continue
            if vals[3] > 0:
                rows.append(vals)
    pd_mm, epa, aob, mass_g = (np.array(c) for c in zip(*rows))
    return {"pd_mm": pd_mm, "epa_deg": epa, "aob_deg": aob, "mass_g": mass_g}


def ols(y: np.ndarray, cols: list[np.ndarray]) -> tuple[np.ndarray, float]:
    x = np.column_stack([np.ones(len(y))] + cols)
    b, *_ = np.linalg.lstsq(x, y, rcond=None)
    r2 = 1 - ((y - x @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return b, float(r2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    d = load_glass_semispherical()
    y = np.cbrt(d["mass_g"])
    models = {
        "PD": [d["pd_mm"]],
        "PD+EPA": [d["pd_mm"], d["epa_deg"]],
        "PD+EPA+AOB": [d["pd_mm"], d["epa_deg"], d["aob_deg"]],
    }
    out = {"n": int(len(y)), "response": "cbrt(mass_g)", "models": {}}
    for name, cols in models.items():
        b, r2 = ols(y, cols)
        out["models"][name] = {"coef": [round(float(v), 4) for v in b], "r2": round(r2, 3)}
        print(f"{name:12s} R2={r2:.3f} coef(intercept, ...)={np.round(b, 4).tolist()}")
    if args.out:
        args.out.write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
