"""Tests for the YSC 2027 tool-discovery arena (proposal phases 0-2)."""

from __future__ import annotations

import json
from random import Random

import pytest

from simulation.tool_discovery import (
    ACTIONS,
    BARE,
    Arena,
    ArenaConfig,
    OutcomeLearner,
    RandomPolicy,
    candidate_mixes,
    config_dict,
    feature_key,
    perceived_properties,
    run_arena,
)
from simulation.tool_discovery_metrics import functional_objects, summarize_run
from world.environment import Environment

SHORT = dict(n_agents=6, ticks=150)


# -- information boundary (phase 0, Gate for "no oracle") ---------------------


def _run_with_utility_guard(monkeypatch, condition):
    arena = Arena(ArenaConfig(seed=3, condition=condition, **SHORT))
    deciding = {"on": False}
    real_score = Environment.score_object_for_action

    def guarded(self, *args, **kwargs):
        if deciding["on"]:
            raise AssertionError("policy read the world's utility score")
        return real_score(self, *args, **kwargs)

    monkeypatch.setattr(Environment, "score_object_for_action", guarded)
    for agent in arena.agents:
        for name in ("choose_use", "choose_mix", "choose_discard"):
            original = getattr(agent.policy, name)

            def wrapped(*args, _original=original, **kwargs):
                deciding["on"] = True
                try:
                    return _original(*args, **kwargs)
                finally:
                    deciding["on"] = False

            setattr(agent.policy, name, wrapped)
    arena.run()
    return arena


@pytest.mark.parametrize("condition", ["C0", "C1", "C2", "C4"])
def test_non_oracle_policies_never_read_utility(monkeypatch, condition):
    """While a non-oracle policy is deciding, any utility read is an error."""
    arena = _run_with_utility_guard(monkeypatch, condition)
    assert any(e["type"] == "use" and e["object_id"] is not None for e in arena.events)


def test_utility_guard_catches_the_oracle(monkeypatch):
    """Control: the guard must fire for C3, or the test above proves nothing."""
    with pytest.raises(AssertionError, match="utility score"):
        _run_with_utility_guard(monkeypatch, "C3")


@pytest.mark.parametrize("condition", ["C0", "C1", "C2", "C4"])
def test_non_oracle_policies_hold_no_world_reference(condition):
    arena = Arena(ArenaConfig(seed=1, condition=condition, **SHORT))
    for agent in arena.agents:
        for value in vars(agent.policy).values():
            assert not isinstance(value, Environment)
            assert type(value).__name__ not in {"World", "OracleView"}


def test_observation_contains_no_utility_fields():
    arena = Arena(ArenaConfig(seed=2, condition="C1", **SHORT))
    arena.run()
    agent = next(a for a in arena.agents if a.objects)
    obs = arena._observation(agent, "plant")
    allowed_object_fields = {"object_id", "properties", "feature_key", "uses"}
    for obs_object in obs["objects"]:
        assert set(obs_object) == allowed_object_fields
        assert set(obs_object["properties"]) == {
            "mass", "sharpness", "hardness", "length", "flexibility", "durability", "portability",
        }


def test_oracle_condition_does_read_utility(monkeypatch):
    calls = {"n": 0}
    real_score = Environment.score_object_for_action

    def counting(self, *args, **kwargs):
        calls["n"] += 1
        return real_score(self, *args, **kwargs)

    monkeypatch.setattr(Environment, "score_object_for_action", counting)
    run_arena(ArenaConfig(seed=1, condition="C3", **SHORT))
    assert calls["n"] > 0


# -- determinism and pairing ---------------------------------------------------


def test_same_seed_same_run_byte_identical():
    a = run_arena(ArenaConfig(seed=7, condition="C2", **SHORT))
    b = run_arena(ArenaConfig(seed=7, condition="C2", **SHORT))
    assert json.dumps(a.events, sort_keys=True) == json.dumps(b.events, sort_keys=True)
    assert a.ledger == b.ledger


def test_paired_seeds_share_paths_and_encounters():
    cfg = dict(seed=5, n_agents=6, ticks=30, start_energy=500.0)
    runs = {c: run_arena(ArenaConfig(condition=c, **cfg)) for c in ("C0", "C1", "C3")}
    positions = {c: [(a.x, a.y) for a in r.agents] for c, r in runs.items()}
    assert positions["C0"] == positions["C1"] == positions["C3"]
    contexts = {
        c: [(e["tick"], e["agent"], e["context"]) for e in r.events if e["type"] == "use"] for c, r in runs.items()
    }
    assert contexts["C0"] == contexts["C1"] == contexts["C3"]


def test_world_physics_identical_for_same_mix():
    arena = Arena(ArenaConfig(seed=0, **SHORT))
    mix = {"stone": 2, "wood": 1}
    one = arena.world.craft(mix, Random(9), 0)
    two = arena.world.craft(mix, Random(9), 0)
    assert perceived_properties(one) == perceived_properties(two)
    for action in ACTIONS:
        assert arena.world.expected_use(one, action, "prey") == arena.world.expected_use(two, action, "prey")


# -- learner behaviour ---------------------------------------------------------


def test_learner_moves_toward_good_and_away_from_bad_outcomes():
    learner = OutcomeLearner(ArenaConfig(alpha=0.5, q_init=0.0))
    good, bad = ("feat", (1,), "cut", "plant"), ("feat", (2,), "cut", "plant")
    learner.learn_use(good, 10.0)
    learner.learn_use(bad, -4.0)
    assert learner.value(good) == pytest.approx(5.0)
    assert learner.value(bad) == pytest.approx(-2.0)


def test_learner_empty_memory_returns_initial_value():
    learner = OutcomeLearner(ArenaConfig(q_init=1.5))
    assert learner.value((BARE, "soil")) == 1.5
    assert learner.choose_discard({"objects": []}, Random(0)) is None


def test_frozen_learner_does_not_update():
    learner = OutcomeLearner(ArenaConfig(alpha=0.5))
    learner.frozen = True
    learner.learn_use((BARE, "plant"), 10.0)
    learner.learn_mix("stone2", 10.0)
    assert learner.q_use == {} and learner.q_mix == {}


def test_learner_exploits_best_known_option():
    learner = OutcomeLearner(ArenaConfig(epsilon=0.0))
    obj = {"object_id": 1, "feature_key": (0, 3, 3, 1, 0, 1), "properties": {}, "uses": 3}
    learner.q_use[("feat", obj["feature_key"], "pierce", "prey")] = 9.0
    obs = {"context": "prey", "objects": [obj]}
    choice = learner.choose_use(obs, Random(0))
    assert (choice.handle, choice.action) == (0, "pierce")


def test_object_id_learner_does_not_generalise_to_new_object():
    learner = OutcomeLearner(ArenaConfig(epsilon=0.0, q_init=0.0), key_by="object_id")
    key = (0, 3, 3, 1, 0, 1)
    learner.learn_use(learner.use_key({"object_id": 1, "feature_key": key}, "cut", "plant"), 8.0)
    twin = {"object_id": 2, "feature_key": key}
    assert learner.value(learner.use_key(twin, "cut", "plant")) == 0.0
    by_features = OutcomeLearner(ArenaConfig(q_init=0.0))
    by_features.learn_use(by_features.use_key({"object_id": 1, "feature_key": key}, "cut", "plant"), 8.0)
    assert by_features.value(by_features.use_key(twin, "cut", "plant")) > 0.0


def test_shuffled_feedback_only_in_c2():
    c1 = run_arena(ArenaConfig(seed=4, condition="C1", **SHORT))
    assert all(e["signal"] == e["net"] for e in c1.events if e["type"] == "use")
    c2 = run_arena(ArenaConfig(seed=4, condition="C2", **SHORT))
    uses = [e for e in c2.events if e["type"] == "use"]
    assert any(e["signal"] != e["net"] for e in uses)


def test_random_policy_keeps_no_memory():
    policy = RandomPolicy(ArenaConfig())
    policy.learn_use((BARE, "plant"), 100.0)
    assert policy.value((BARE, "plant")) is None


# -- world mechanics: costs, breakage, empty input, transfer ---------------------


def test_object_breaks_and_leaves_inventory():
    arena = Arena(ArenaConfig(seed=0, condition="C1", n_agents=1, ticks=1))
    agent = arena.agents[0]
    obj = arena.world.craft({"stone": 2, "wood": 1}, Random(0), agent.agent_id)
    obj.durability = 1
    agent.objects.append(obj)
    agent.policy.config.epsilon = 0.0
    agent.policy.q_use[agent.policy.use_key(arena._observe_object(agent, obj), "pierce", "prey")] = 50.0
    arena._use(agent, "prey", Random(0))
    assert obj not in agent.objects
    assert any(e["type"] == "break" and e["object_id"] == obj.object_id for e in arena.events)


def test_tool_effort_scales_with_mass_and_bare_hands_cost_nothing():
    arena = Arena(ArenaConfig(seed=0, n_agents=1, ticks=1))
    light = arena.world.craft({"wood": 1, "fiber": 1}, Random(0), 0)
    heavy = arena.world.craft({"stone": 4}, Random(0), 0)
    assert arena.world.expected_use(None, None, "plant") == (2.0, 0.0)
    assert arena.world.expected_use(heavy, "hit", "plant")[1] > arena.world.expected_use(light, "hit", "plant")[1]


def test_candidate_mixes_respect_inventory_and_empty_input():
    assert candidate_mixes({}, 2, 4) == []
    assert candidate_mixes({"stone": 1}, 2, 4) == []
    mixes = candidate_mixes({"stone": 1, "wood": 2}, 2, 4)
    assert {"stone": 1, "wood": 1} in mixes and {"wood": 2} in mixes
    assert {"stone": 2} not in mixes
    assert all(sum(m.values()) <= 3 for m in mixes)


def test_transfer_blocks_materials():
    arena = Arena(ArenaConfig(seed=0, n_agents=1, ticks=1, transfer_tick=10, blocked_materials_after_transfer=("stone",)))
    seen_before, seen_after = set(), set()
    for i in range(400):
        x, y = 2 + i % 30, 2 + (i * 7) % 30
        seen_before |= set(arena.world.gather(x, y, Random(i), tick=0))
        seen_after |= set(arena.world.gather(x, y, Random(i), tick=10))
    assert "stone" in seen_before and "stone" not in seen_after


# -- metrics ---------------------------------------------------------------------


def _use(tick, object_id, net, context="plant", agent=0):
    return {"type": "use", "tick": tick, "agent": agent, "object_id": object_id, "net": net, "context": context}


def test_functional_object_needs_repeat_success_not_one_lucky_use():
    baselines = {"plant": 1.0, "prey": 0.0, "soil": 0.0}
    lucky = [_use(1, 10, 30.0), _use(2, 10, -1.0), _use(3, 10, -1.0)]
    steady = [_use(1, 11, 4.0), _use(5, 11, 3.0), _use(9, 11, 0.5)]
    found = functional_objects(lucky + steady, baselines, min_uses=3)
    assert 10 not in found
    assert found == {11: 9}


def test_summary_runs_and_rebins():
    arena = run_arena(ArenaConfig(seed=2, condition="C3", n_agents=6, ticks=200))
    cfg = config_dict(arena.config)
    narrow = summarize_run(arena.events, arena.ledger, cfg, bin_width=2)
    wide = summarize_run(arena.events, arena.ledger, cfg, bin_width=5)
    assert narrow["n_feature_groups"] >= wide["n_feature_groups"]
    assert narrow["final_net_per_alive_tick"] == wide["final_net_per_alive_tick"]


def test_feature_key_ignores_durability():
    props = {"mass": 4, "sharpness": 6, "hardness": 7, "length": 2, "flexibility": 0, "durability": 9, "portability": 1}
    worn = dict(props, durability=1)
    assert feature_key(props, 3) == feature_key(worn, 3)
