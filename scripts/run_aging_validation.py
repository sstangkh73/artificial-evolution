"""Aging Physics v1 — controlled validation against the proven literature.

Run:  python scripts/run_aging_validation.py

This is a CONTROLLED experiment (experiment-design skill): it drives the REAL
production aging code (Agent._apply_aging) one variable at a time, holding all
else fixed, and checks that each proven result from papers/longevity/ EMERGES
from the model rather than being hand-set. It deliberately isolates the aging
dynamics from foraging/reproduction confounds (the viable-population work is a
separate thread — see reports/lifespan_masks_starvation_2026-06-27.th.md), which
is exactly what a mechanism-validation should do.

Arms:
  1. Allometry (Speakman 2005)      : lifespan ~ mass^0.15-0.3
  2. Disposable Soma (Kirkwood 1977): more somatic maintenance -> longer life
  3. Membrane/mito (Hulbert 2007)   : higher damage_resistance -> longer life
  4. Caloric restriction (CALERIE)  : lower food intake -> longer life
"""

from __future__ import annotations

import math
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent import Agent
from agents.body import BodyPlan


def _env(**overrides) -> SimpleNamespace:
    base = dict(
        aging_physics_enabled=True,
        aging_damage_rate=0.4,
        aging_repair_gain=0.5,
        aging_maintenance_cost=2.0,
        aging_damage_threshold=100.0,
        aging_mass_exponent=0.25,
        aging_max_repair_fraction=0.95,
        aging_intake_damage_coeff=0.0,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _body(**genes) -> BodyPlan:
    defaults = dict(sensor_units=1, muscle_units=1, armor_units=0, brain_units=1, metabolism_rate=1.0)
    defaults.update(genes)
    return BodyPlan(**defaults)


def _lifespan(body: BodyPlan, env, intake_per_tick: float = 0.0, cap: int = 5_000_000) -> int:
    """Emergent age at senescence, driving the real Agent._apply_aging each tick."""
    agent = Agent(agent_id=1, body=body, x=0, y=0)
    for tick in range(1, cap + 1):
        agent._aging_gained_mark = agent.energy_gained_total
        if intake_per_tick:
            agent.energy_gained_total += intake_per_tick
        if agent._apply_aging(env):
            return tick
    return cap + 1


def _fit_loglog_slope(xs: list[float], ys: list[float]) -> float:
    lx = [math.log(x) for x in xs]
    ly = [math.log(y) for y in ys]
    n = len(lx)
    mx = sum(lx) / n
    my = sum(ly) / n
    return sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)


def _verdict(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def arm_allometry() -> bool:
    print("\n[1] ALLOMETRY  (Speakman 2005: lifespan ~ mass^0.15-0.3)")
    env = _env()
    masses = [0.5, 0.7, 1.0, 1.4, 2.0, 2.8, 4.0]
    lifespans = [_lifespan(_body(body_mass=m, somatic_maintenance=0.0), env) for m in masses]
    for m, L in zip(masses, lifespans):
        print(f"     mass={m:>4}  ->  lifespan={L:>6} ticks")
    slope = _fit_loglog_slope(masses, lifespans)
    ok = 0.15 <= slope <= 0.30
    print(f"     fitted exponent (log-log slope) = {slope:.3f}   [{_verdict(ok)}]  target set 0.25, band 0.15-0.30")
    return ok


def arm_disposable_soma() -> bool:
    print("\n[2] DISPOSABLE SOMA  (Kirkwood 1977: more maintenance -> longer life)")
    env = _env()
    maints = [0.0, 0.25, 0.5, 0.75, 1.0]
    lifespans = [_lifespan(_body(somatic_maintenance=m, repair_efficiency=1.0), env) for m in maints]
    for m, L in zip(maints, lifespans):
        print(f"     somatic_maintenance={m:>4}  ->  lifespan={L:>6} ticks")
    ok = all(b >= a for a, b in zip(lifespans, lifespans[1:])) and lifespans[-1] > lifespans[0]
    print(f"     monotonic non-decreasing & net gain = {lifespans[-1] - lifespans[0]:+} ticks   [{_verdict(ok)}]")
    return ok


def arm_membrane() -> bool:
    print("\n[3] MEMBRANE / MITOCHONDRIA  (Hulbert 2007 / Kitazoe 2017: higher damage_resistance -> longer life)")
    env = _env()
    res = [0.5, 1.0, 1.5, 2.0]
    lifespans = [_lifespan(_body(damage_resistance=r, somatic_maintenance=0.0), env) for r in res]
    for r, L in zip(res, lifespans):
        print(f"     damage_resistance={r:>4}  ->  lifespan={L:>6} ticks")
    ok = all(b > a for a, b in zip(lifespans, lifespans[1:]))
    print(f"     strictly increasing = {_verdict(ok)}  (decoupled from metabolic rate, the 'bird' lesson)")
    return ok


def arm_caloric_restriction() -> bool:
    print("\n[4] CALORIC RESTRICTION  (CALERIE / Ravussin 2015, Waziry 2023: less intake -> longer life)")
    env = _env(aging_intake_damage_coeff=0.02)
    intakes = [0.0, 10.0, 20.0, 40.0]
    lifespans = [_lifespan(_body(somatic_maintenance=0.0), env, intake_per_tick=i) for i in intakes]
    for i, L in zip(intakes, lifespans):
        print(f"     intake/tick={i:>5}  ->  lifespan={L:>6} ticks")
    ok = all(b < a for a, b in zip(lifespans, lifespans[1:]))
    print(f"     lifespan falls as intake rises = {_verdict(ok)}   (restriction extends life)")
    print("     caveat: in humans CR is proven to slow ageing MARKERS, not yet lifespan itself (Waziry 2023).")
    return ok


def main() -> int:
    print("=" * 78)
    print("AGING PHYSICS v1 - controlled validation vs proven longevity literature")
    print("driving the real Agent._apply_aging; one variable per arm, all else fixed")
    print("=" * 78)
    results = {
        "allometry (Speakman)": arm_allometry(),
        "disposable soma (Kirkwood)": arm_disposable_soma(),
        "membrane/mito (Hulbert/Kitazoe)": arm_membrane(),
        "caloric restriction (CALERIE)": arm_caloric_restriction(),
    }
    print("\n" + "=" * 78)
    print("SUMMARY")
    for name, ok in results.items():
        print(f"   [{_verdict(ok)}]  {name}")
    all_ok = all(results.values())
    print("=" * 78)
    print("ALL ARMS PASS" if all_ok else "SOME ARMS FAILED")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
