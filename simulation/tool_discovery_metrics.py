"""Run-level metrics for the tool-discovery arena (proposal sections 3.4-3.5).

All metrics are computed from the logged events and the per-tick ledger, so
the same function can re-analyse saved runs with a different property-bin
width (robustness check in proposal 3.9.4).
"""

from __future__ import annotations

from statistics import mean

from simulation.tool_discovery import CONTEXTS, feature_key


def _window_totals(ledger: list[dict], start: int, stop: int) -> dict:
    rows = [r for r in ledger if start <= r["tick"] < stop]
    totals = {k: sum(r[k] for r in rows) for k in ("food", "effort", "craft", "gather")}
    totals["agent_ticks"] = len(rows)
    net = totals["food"] - totals["effort"] - totals["craft"] - totals["gather"]
    totals["net"] = net
    totals["net_per_alive_tick"] = net / len(rows) if rows else None
    totals["food_per_alive_tick"] = totals["food"] / len(rows) if rows else None
    return totals


def bare_baselines(events: list[dict], config: dict) -> dict[str, float]:
    """Mean net of bare-handed attempts per context in this run."""
    out = {}
    for context in CONTEXTS:
        nets = [e["net"] for e in events if e["type"] == "use" and e["object_id"] is None and e["context"] == context]
        out[context] = mean(nets) if nets else float(config["bare_yield"][context])
    return out


def functional_objects(events: list[dict], baselines: dict[str, float], min_uses: int) -> dict[int, int]:
    """Level A (proposal 3.5): object_id -> tick it first met the criteria.

    Criteria: crafted (all arena objects are), used >= min_uses times, mean net
    above the bare baseline of the contexts it was used in, and at least two
    individual uses above baseline (not a single lucky event).
    """
    history: dict[int, list[dict]] = {}
    for e in events:
        if e["type"] == "use" and e["object_id"] is not None:
            history.setdefault(e["object_id"], []).append(e)
    found: dict[int, int] = {}
    for object_id, uses in history.items():
        for i in range(min_uses, len(uses) + 1):
            prefix = uses[:i]
            gains = [u["net"] - baselines[u["context"]] for u in prefix]
            if mean(gains) > 0 and sum(g > 0 for g in gains) >= 2:
                found[object_id] = prefix[-1]["tick"]
                break
    return found


def summarize_run(events: list[dict], ledger: list[dict], config: dict, bin_width: int | None = None,
                  min_uses: int = 3, window_fraction: float = 0.25) -> dict:
    bin_width = bin_width or config["feature_bin_width"]
    ticks = config["ticks"]
    window = max(1, int(ticks * window_fraction))
    early = _window_totals(ledger, 0, window)
    final = _window_totals(ledger, ticks - window, ticks)

    baselines = bare_baselines(events, config)
    functional = functional_objects(events, baselines, min_uses)
    first_discovery = min(functional.values()) if functional else None

    crafts = [e for e in events if e["type"] == "craft"]
    uses = [e for e in events if e["type"] == "use"]
    craft_key = {e["object_id"]: feature_key(e["properties"], bin_width) for e in crafts}

    final_uses = [u for u in uses if u["tick"] >= ticks - window]
    tool_use_rate = (sum(u["object_id"] is not None for u in final_uses) / len(final_uses)) if final_uses else None

    # H3 part 1: after a good vs bad outcome with property group F, does the
    # agent pick F again at its next opportunity where F is still in hand?
    by_agent: dict[int, list[dict]] = {}
    for u in uses:
        by_agent.setdefault(u["agent"], []).append(u)
    reuse = {"good": [0, 0], "bad": [0, 0]}
    for agent_uses in by_agent.values():
        for prev, nxt in zip(agent_uses, agent_uses[1:]):
            if prev["object_id"] is None:
                continue
            key = craft_key[prev["object_id"]]
            if key not in {craft_key[i] for i in nxt["held_ids"]}:
                continue
            outcome = "good" if prev["net"] > baselines[prev["context"]] else "bad"
            reuse[outcome][1] += 1
            if nxt["object_id"] is not None and craft_key[nxt["object_id"]] == key:
                reuse[outcome][0] += 1
    reuse_after_good = reuse["good"][0] / reuse["good"][1] if reuse["good"][1] else None
    reuse_after_bad = reuse["bad"][0] / reuse["bad"][1] if reuse["bad"][1] else None

    # H3 part 2: rebuilds of a property group the agent has already used
    # successfully (a functional object it used itself).
    functional_keys_used: dict[int, dict[tuple, int]] = {}
    for u in uses:
        if u["object_id"] in functional and u["tick"] >= functional[u["object_id"]]:
            functional_keys_used.setdefault(u["agent"], {}).setdefault(craft_key[u["object_id"]], u["tick"])
    rebuilds = 0
    crafts_after_success = 0
    for c in crafts:
        known = functional_keys_used.get(c["agent"], {})
        eligible = {k for k, t in known.items() if t < c["tick"]}
        if not eligible:
            continue
        crafts_after_success += 1
        if craft_key[c["object_id"]] in eligible:
            rebuilds += 1

    level_a = bool(functional)
    reuse_up = (
        reuse_after_good is not None and reuse_after_bad is not None and reuse_after_good > reuse_after_bad
    ) or (reuse_after_good is not None and reuse_after_bad is None and reuse_after_good > 0)
    level_b = level_a and reuse_up and rebuilds >= 1

    deaths = [e for e in events if e["type"] == "death"]
    return {
        "seed": config["seed"],
        "condition": config["condition"],
        "bin_width": bin_width,
        "final_net_per_alive_tick": final["net_per_alive_tick"],
        "final_food_per_alive_tick": final["food_per_alive_tick"],
        "final_effort": final["effort"],
        "final_craft_cost": final["craft"],
        "final_gather_cost": final["gather"],
        "final_agent_ticks": final["agent_ticks"],
        "early_net_per_alive_tick": early["net_per_alive_tick"],
        "learning_gain": (
            final["net_per_alive_tick"] - early["net_per_alive_tick"]
            if final["net_per_alive_tick"] is not None and early["net_per_alive_tick"] is not None
            else None
        ),
        "survivors": config["n_agents"] - len(deaths),
        "level_a": level_a,
        "level_b": level_b,
        "first_discovery_tick": first_discovery,
        "n_functional_objects": len(functional),
        "n_crafted": len(crafts),
        "n_feature_groups": len(set(craft_key.values())),
        "final_tool_use_rate": tool_use_rate,
        "reuse_after_good": reuse_after_good,
        "reuse_after_bad": reuse_after_bad,
        "reuse_pairs_good": reuse["good"][1],
        "reuse_pairs_bad": reuse["bad"][1],
        "rebuilds_of_functional_group": rebuilds,
        "crafts_after_success": crafts_after_success,
        "rebuild_rate": rebuilds / crafts_after_success if crafts_after_success else None,
        **{f"bare_baseline_{c}": baselines[c] for c in CONTEXTS},
    }
