"""Tool-discovery arena for YSC 2027 project 29YCSS00443.

Research question: can agents discover functional objects by combining
materials and learning from real outcomes, with no tool names, recipes, or
utility scores handed to them?

World truth comes from the existing ``world.environment.Environment``:
material foraging, object physics (``create_experimental_object``), and how
well an object performs an action (``score_object_for_action``). The world code
is reused unchanged.

Information boundary: policies never receive the environment. They receive
only observation dicts (context, perceived object properties, material
counts). The C3 oracle is the only policy handed a scoring function, and it
gets it explicitly through ``OracleView``.

Conditions (proposal section 3.3):
    C0  no-learning random
    C1  outcome learning over perceived property groups
    C2  C1's learner fed shuffled feedback (real energy, wrong learning signal)
    C3  oracle upper bound (reads the world's physics score)
    C4  C1's learner keyed by object identity instead of properties
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
from itertools import combinations_with_replacement
import hashlib
from random import Random
from typing import Callable

from world.environment import (
    MATERIAL_CLAY,
    MATERIAL_FIBER,
    MATERIAL_LEAF,
    MATERIAL_SAND,
    MATERIAL_SOIL,
    MATERIAL_STONE,
    MATERIAL_WOOD,
    Environment,
    PhysicalObject,
)

CONDITIONS = ("C0", "C1", "C2", "C3", "C4")
# Basic physical actions; none of them names a tool.
ACTIONS = ("cut", "pierce", "hit", "throw", "dig")
CONTEXTS = ("plant", "prey", "soil")
MATERIALS = (
    MATERIAL_WOOD,
    MATERIAL_STONE,
    MATERIAL_FIBER,
    MATERIAL_LEAF,
    MATERIAL_SOIL,
    MATERIAL_CLAY,
    MATERIAL_SAND,
)
PERCEIVED_PROPERTIES = ("mass", "sharpness", "hardness", "length", "flexibility", "durability")
BARE = "bare"


@dataclass
class ArenaConfig:
    seed: int = 0
    condition: str = "C1"
    n_agents: int = 20
    ticks: int = 800
    width: int = 40
    height: int = 40
    # Pre-pilot defaults (2026-10-14 smoke). Phase 3 pilot fixes the final
    # values on pilot seeds before any confirmatory run.
    start_energy: float = 100.0
    max_energy: float = 150.0
    drain_per_tick: float = 0.3
    gather_cost: float = 1.0
    craft_cost_per_material: float = 2.0
    craft_energy_reserve: float = 20.0
    use_effort_base: float = 0.5
    use_effort_per_mass: float = 0.25
    target_prob: float = 0.35
    bare_yield: dict[str, float] = field(default_factory=lambda: {"plant": 2.0, "prey": 0.5, "soil": 1.5})
    success_yield: dict[str, float] = field(default_factory=lambda: {"plant": 5.0, "prey": 9.0, "soil": 6.0})
    threshold: dict[str, float] = field(default_factory=lambda: {"plant": 12.0, "prey": 14.0, "soil": 10.0})
    max_materials: int = 6
    max_objects: int = 2
    min_mix_size: int = 2
    max_mix_size: int = 4
    alpha: float = 0.2
    epsilon: float = 0.1
    q_init: float = 0.0
    feature_bin_width: int = 3
    shuffle_window: int = 50
    c0_discard_prob: float = 0.5
    # Transfer test (proposal phase 5): from transfer_tick on, these
    # materials can no longer be gathered.
    transfer_tick: int | None = None
    blocked_materials_after_transfer: tuple[str, ...] = ()
    # Phase 5 falsification: from this tick on, learners stop updating and
    # stop exploring (memory frozen); None keeps learning on.
    freeze_memory_tick: int | None = None

    def validate(self) -> None:
        if self.condition not in CONDITIONS:
            raise ValueError(f"unknown condition {self.condition!r}")
        if self.min_mix_size < 1 or self.max_mix_size < self.min_mix_size:
            raise ValueError("bad mix size range")


def _stream_seed(*parts: object) -> int:
    """Stable integer seed from parts, independent of PYTHONHASHSEED."""
    digest = hashlib.sha256(":".join(str(p) for p in parts).encode()).digest()
    return int.from_bytes(digest[:8], "big")


def mix_key(mix: dict[str, int]) -> str:
    return "+".join(f"{m}{mix[m]}" for m in sorted(mix) if mix[m] > 0)


def perceived_properties(physical_object: PhysicalObject) -> dict[str, int]:
    """What an agent can see about an object: raw physical properties only."""
    props = {name: int(getattr(physical_object, name)) for name in PERCEIVED_PROPERTIES}
    props["portability"] = int(bool(physical_object.portability))
    return props


def feature_key(props: dict[str, int], bin_width: int) -> tuple[int, ...]:
    """Property group used for generalisation. Durability is left out on
    purpose: it falls with use, so including it would split one object's
    history across groups."""
    return (
        props["mass"] // bin_width,
        props["sharpness"] // bin_width,
        props["hardness"] // bin_width,
        props["length"] // bin_width,
        props["flexibility"] // bin_width,
        props["portability"],
    )


# --------------------------------------------------------------------------
# World truth (hidden from agents)
# --------------------------------------------------------------------------


class World:
    """Wraps the existing Environment. Only this class reads utility."""

    def __init__(self, config: ArenaConfig) -> None:
        self.config = config
        self.env = Environment(width=config.width, height=config.height)
        self._resolving = False

    def ground(self, x: int, y: int) -> str:
        return self.env.get_ground_material(x, y)

    def encounter_context(self, x: int, y: int, rng: Random) -> str:
        ground = self.ground(x, y)
        if self.env.is_safe_area(x, y):
            weights = {"plant": 0.6, "prey": 0.15, "soil": 0.25}
        else:
            weights = {"plant": 0.2, "prey": 0.6, "soil": 0.2}
        if ground in {MATERIAL_SOIL, MATERIAL_CLAY}:
            weights["soil"] += 0.2
        roll = rng.random() * sum(weights.values())
        for context in CONTEXTS:
            roll -= weights[context]
            if roll < 0:
                return context
        return CONTEXTS[-1]

    def gather(self, x: int, y: int, rng: Random, tick: int) -> dict[str, int]:
        gathered = self.env.forage_materials(x, y, rng, cognition_score=0.0)
        cfg = self.config
        if cfg.transfer_tick is not None and tick >= cfg.transfer_tick:
            for blocked in cfg.blocked_materials_after_transfer:
                gathered.pop(blocked, None)
        return {m: n for m, n in gathered.items() if m in MATERIALS and n > 0}

    def craft(self, mix: dict[str, int], rng: Random, agent_id: int) -> PhysicalObject:
        return self.env.create_experimental_object(dict(mix), rng, creator_agent_id=agent_id)

    def expected_use(self, physical_object: PhysicalObject | None, action: str | None, context: str) -> tuple[float, float]:
        """(food, effort) of a use, without side effects."""
        cfg = self.config
        bare = cfg.bare_yield[context]
        if physical_object is None:
            return bare, 0.0
        self._resolving = True
        try:
            score = self.env.score_object_for_action(physical_object, action, context)
        finally:
            self._resolving = False
        food = bare
        threshold = cfg.threshold[context]
        if score >= threshold:
            food += cfg.success_yield[context] + int((score - threshold) // 3)
        effort = cfg.use_effort_base + physical_object.mass * cfg.use_effort_per_mass
        return food, effort

    def resolve_use(
        self, physical_object: PhysicalObject | None, action: str | None, context: str, agent_id: int
    ) -> tuple[float, float]:
        food, effort = self.expected_use(physical_object, action, context)
        if physical_object is not None:
            self.env.record_object_use(
                physical_object.object_id, agent_id, outcome_score=food - effort, action=action, context=context
            )
        return food, effort


class OracleView:
    """The only route by which a policy may see utility (C3 only)."""

    def __init__(self, world: World, scratch_seed: int) -> None:
        self._world = world
        self._scratch = Environment(width=8, height=8)
        self._scratch_seed = scratch_seed

    def expected_net(self, physical_object: PhysicalObject | None, action: str | None, context: str) -> float:
        food, effort = self._world.expected_use(physical_object, action, context)
        return food - effort

    def mix_value(self, mix: dict[str, int]) -> float:
        """Mean over contexts of the best tool-over-bare gain for a mix."""
        probe = self._scratch.create_experimental_object(dict(mix), Random(self._scratch_seed))
        self._scratch.objects.clear()
        total = 0.0
        for context in CONTEXTS:
            bare = self.expected_net(None, None, context)
            best = max(self.expected_net(probe, action, context) for action in ACTIONS)
            total += best - bare
        return total / len(CONTEXTS)


# --------------------------------------------------------------------------
# Policies (see only observations)
# --------------------------------------------------------------------------


@dataclass
class UseOption:
    handle: int | None  # index into the agent's held objects; None = bare hands
    action: str | None


class Policy:
    learns = False

    def choose_use(self, obs: dict, rng: Random) -> UseOption:
        raise NotImplementedError

    def choose_mix(self, candidates: list[dict[str, int]], rng: Random) -> dict[str, int]:
        raise NotImplementedError

    def choose_discard(self, obs: dict, rng: Random) -> int | None:
        raise NotImplementedError

    def use_key(self, obs_object: dict | None, action: str | None, context: str) -> tuple | None:
        return None

    def value(self, key: tuple | None) -> float | None:
        return None

    def learn_use(self, key: tuple | None, signal: float) -> None:
        pass

    def learn_mix(self, key: str, signal: float) -> None:
        pass


def _all_options(obs: dict) -> list[UseOption]:
    options = [UseOption(None, None)]
    for handle in range(len(obs["objects"])):
        options.extend(UseOption(handle, action) for action in ACTIONS)
    return options


class RandomPolicy(Policy):
    """C0: picks uniformly, keeps no memory of outcomes."""

    def __init__(self, config: ArenaConfig) -> None:
        self.config = config

    def choose_use(self, obs: dict, rng: Random) -> UseOption:
        return rng.choice(_all_options(obs))

    def choose_mix(self, candidates: list[dict[str, int]], rng: Random) -> dict[str, int]:
        return rng.choice(candidates)

    def choose_discard(self, obs: dict, rng: Random) -> int | None:
        if obs["objects"] and rng.random() < self.config.c0_discard_prob:
            return rng.randrange(len(obs["objects"]))
        return None


class OutcomeLearner(Policy):
    """C1/C2 (by properties) and C4 (by object identity).

    Q_new = Q_old + alpha * (signal - Q_old), epsilon-greedy choice.
    """

    learns = True

    def __init__(self, config: ArenaConfig, key_by: str = "features") -> None:
        self.config = config
        self.key_by = key_by
        self.q_use: dict[tuple, float] = {}
        self.n_use: dict[tuple, int] = {}
        self.q_mix: dict[str, float] = {}
        self.frozen = False

    def use_key(self, obs_object: dict | None, action: str | None, context: str) -> tuple:
        if obs_object is None:
            return (BARE, context)
        if self.key_by == "object_id":
            return ("id", obs_object["object_id"], action, context)
        return ("feat", obs_object["feature_key"], action, context)

    def value(self, key: tuple | None) -> float:
        return self.q_use.get(key, self.config.q_init)

    def _greedy(self, items: list, values: list[float], rng: Random):
        if not self.frozen and rng.random() < self.config.epsilon:
            return rng.choice(items)
        best = max(values)
        return rng.choice([item for item, v in zip(items, values) if v == best])

    def choose_use(self, obs: dict, rng: Random) -> UseOption:
        options = _all_options(obs)
        values = [
            self.value(self.use_key(None if o.handle is None else obs["objects"][o.handle], o.action, obs["context"]))
            for o in options
        ]
        return self._greedy(options, values, rng)

    def choose_mix(self, candidates: list[dict[str, int]], rng: Random) -> dict[str, int]:
        values = [self.q_mix.get(mix_key(m), self.config.q_init) for m in candidates]
        return self._greedy(candidates, values, rng)

    def _object_best(self, obs_object: dict) -> float | None:
        known = [
            self.q_use[k]
            for action in ACTIONS
            for context in CONTEXTS
            if (k := self.use_key(obs_object, action, context)) in self.q_use
        ]
        return max(known) if known else None

    def choose_discard(self, obs: dict, rng: Random) -> int | None:
        bare_best = max(self.value((BARE, c)) for c in CONTEXTS)
        worst_handle, worst_value = None, None
        for handle, obs_object in enumerate(obs["objects"]):
            if obs_object["uses"] < 2:
                continue
            best = self._object_best(obs_object)
            if best is not None and best < bare_best and (worst_value is None or best < worst_value):
                worst_handle, worst_value = handle, best
        return worst_handle

    def learn_use(self, key: tuple | None, signal: float) -> None:
        if self.frozen or key is None:
            return
        old = self.value(key)
        self.q_use[key] = old + self.config.alpha * (signal - old)
        self.n_use[key] = self.n_use.get(key, 0) + 1

    def learn_mix(self, key: str, signal: float) -> None:
        if self.frozen:
            return
        old = self.q_mix.get(key, self.config.q_init)
        self.q_mix[key] = old + self.config.alpha * (signal - old)


class OraclePolicy(Policy):
    """C3: reads the world's physics score through OracleView."""

    def __init__(self, config: ArenaConfig, oracle: OracleView, held: Callable[[], list[PhysicalObject]]) -> None:
        self.config = config
        self.oracle = oracle
        self._held = held  # the oracle may see the true objects, not just observations

    def choose_use(self, obs: dict, rng: Random) -> UseOption:
        objects = self._held()
        options = _all_options(obs)
        values = [
            self.oracle.expected_net(None if o.handle is None else objects[o.handle], o.action, obs["context"])
            for o in options
        ]
        best = max(values)
        return rng.choice([o for o, v in zip(options, values) if v == best])

    def choose_mix(self, candidates: list[dict[str, int]], rng: Random) -> dict[str, int]:
        values = [self.oracle.mix_value(m) for m in candidates]
        best = max(values)
        return rng.choice([m for m, v in zip(candidates, values) if v == best])

    def choose_discard(self, obs: dict, rng: Random) -> int | None:
        for handle, physical_object in enumerate(self._held()):
            gain = max(
                self.oracle.expected_net(physical_object, a, c) - self.oracle.expected_net(None, None, c)
                for a in ACTIONS
                for c in CONTEXTS
            )
            if gain <= 0:
                return handle
        return None


# --------------------------------------------------------------------------
# Agents and the run loop
# --------------------------------------------------------------------------


@dataclass
class ArenaAgent:
    agent_id: int
    x: int
    y: int
    energy: float
    policy: Policy
    materials: dict[str, int] = field(default_factory=dict)
    objects: list[PhysicalObject] = field(default_factory=list)
    object_mix: dict[int, str] = field(default_factory=dict)
    alive: bool = True
    death_tick: int | None = None

    def material_count(self) -> int:
        return sum(self.materials.values())


def candidate_mixes(materials: dict[str, int], min_size: int, max_size: int) -> list[dict[str, int]]:
    pool = sorted(m for m, n in materials.items() if n > 0)
    seen: list[dict[str, int]] = []
    for size in range(min_size, max_size + 1):
        for combo in combinations_with_replacement(pool, size):
            mix: dict[str, int] = {}
            for material in combo:
                mix[material] = mix.get(material, 0) + 1
            if all(materials.get(m, 0) >= n for m, n in mix.items()):
                seen.append(mix)
    return seen


class Arena:
    def __init__(self, config: ArenaConfig) -> None:
        config.validate()
        self.config = config
        self.world = World(config)
        self.events: list[dict] = []
        self.tick = 0
        self.ledger: list[dict] = []  # per-tick per-agent accounting rows (compact)
        self._shuffle_buffer: deque[float] = deque(maxlen=config.shuffle_window)
        self._shuffle_rng = Random(_stream_seed(config.seed, "shuffle"))
        self.agents: list[ArenaAgent] = []
        place_rng = Random(_stream_seed(config.seed, "placement"))
        for agent_id in range(config.n_agents):
            x = place_rng.randrange(1, config.width - 1)
            y = place_rng.randrange(1, config.height - 1)
            agent = ArenaAgent(agent_id, x, y, config.start_energy, policy=None)  # type: ignore[arg-type]
            agent.policy = self._make_policy(agent)
            self.agents.append(agent)
        self._move_rngs = [Random(_stream_seed(config.seed, "move", a.agent_id)) for a in self.agents]
        self._encounter_rngs = [Random(_stream_seed(config.seed, "encounter", a.agent_id)) for a in self.agents]
        self._policy_rngs = [Random(_stream_seed(config.seed, "policy", config.condition, a.agent_id)) for a in self.agents]

    def _make_policy(self, agent: ArenaAgent) -> Policy:
        cond = self.config.condition
        if cond == "C0":
            return RandomPolicy(self.config)
        if cond in {"C1", "C2"}:
            return OutcomeLearner(self.config, key_by="features")
        if cond == "C4":
            return OutcomeLearner(self.config, key_by="object_id")
        oracle = OracleView(self.world, scratch_seed=_stream_seed(self.config.seed, "oracle"))
        return OraclePolicy(self.config, oracle, held=lambda: agent.objects)

    # -- observations -------------------------------------------------------

    def _observe_object(self, agent: ArenaAgent, physical_object: PhysicalObject) -> dict:
        props = perceived_properties(physical_object)
        return {
            "object_id": physical_object.object_id,
            "properties": props,
            "feature_key": feature_key(props, self.config.feature_bin_width),
            "uses": physical_object.use_count,
        }

    def _observation(self, agent: ArenaAgent, context: str | None) -> dict:
        return {
            "context": context,
            "energy": agent.energy,
            "objects": [self._observe_object(agent, o) for o in agent.objects],
            "materials": dict(agent.materials),
        }

    # -- learning signal ----------------------------------------------------

    def _learning_signal(self, net: float) -> float:
        """C2 gets a recent outcome from someone/something else."""
        self._shuffle_buffer.append(net)
        if self.config.condition != "C2":
            return net
        return self._shuffle_rng.choice(self._shuffle_buffer)

    # -- per-tick actions ---------------------------------------------------

    def _move(self, agent: ArenaAgent, rng: Random) -> None:
        dx, dy = rng.choice(((0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)))
        agent.x = min(self.config.width - 2, max(1, agent.x + dx))
        agent.y = min(self.config.height - 2, max(1, agent.y + dy))

    def _use(self, agent: ArenaAgent, context: str, rng: Random) -> dict:
        obs = self._observation(agent, context)
        option = agent.policy.choose_use(obs, rng)
        obs_object = None if option.handle is None else obs["objects"][option.handle]
        physical_object = None if option.handle is None else agent.objects[option.handle]
        key = agent.policy.use_key(obs_object, option.action, context)
        q_before = agent.policy.value(key)
        food, effort = self.world.resolve_use(physical_object, option.action, context, agent.agent_id)
        net = food - effort
        agent.energy = min(self.config.max_energy, agent.energy + net)
        signal = self._learning_signal(net)
        agent.policy.learn_use(key, signal)
        if physical_object is not None and physical_object.creator_agent_id == agent.agent_id:
            mk = agent.object_mix.get(physical_object.object_id)
            if mk is not None:
                agent.policy.learn_mix(mk, signal)
        event = {
            "type": "use",
            "tick": self.tick,
            "agent": agent.agent_id,
            "context": context,
            "object_id": None if physical_object is None else physical_object.object_id,
            "properties": None if obs_object is None else obs_object["properties"],
            "action": option.action,
            "n_options": 1 + len(ACTIONS) * len(obs["objects"]),
            "held_ids": [o["object_id"] for o in obs["objects"]],
            "food": food,
            "effort": effort,
            "net": net,
            "signal": signal,
            "q_before": q_before,
            "q_after": agent.policy.value(key),
        }
        self.events.append(event)
        if physical_object is not None and physical_object.durability <= 0:
            agent.objects.remove(physical_object)
            self.events.append(
                {"type": "break", "tick": self.tick, "agent": agent.agent_id, "object_id": physical_object.object_id}
            )
        return {"food": food, "effort": effort}

    def _craft(self, agent: ArenaAgent, rng: Random) -> float:
        cfg = self.config
        candidates = candidate_mixes(agent.materials, cfg.min_mix_size, cfg.max_mix_size)
        if not candidates:
            return 0.0
        mix = agent.policy.choose_mix(candidates, rng)
        for material, amount in mix.items():
            agent.materials[material] -= amount
            if agent.materials[material] == 0:
                del agent.materials[material]
        craft_rng = Random(_stream_seed(cfg.seed, "craft", agent.agent_id, self.tick))
        physical_object = self.world.craft(mix, craft_rng, agent.agent_id)
        physical_object.emergence_tick = self.tick
        agent.objects.append(physical_object)
        agent.object_mix[physical_object.object_id] = mix_key(mix)
        cost = cfg.craft_cost_per_material * sum(mix.values())
        agent.energy -= cost
        props = perceived_properties(physical_object)
        self.events.append(
            {
                "type": "craft",
                "tick": self.tick,
                "agent": agent.agent_id,
                "object_id": physical_object.object_id,
                "mix": mix_key(mix),
                "properties": props,
                "n_candidates": len(candidates),
                "cost": cost,
            }
        )
        return cost

    def _idle_step(self, agent: ArenaAgent, rng: Random) -> dict:
        """No food target this tick: craft, gather, or rest (same rule for every condition)."""
        cfg = self.config
        costs = {"craft": 0.0, "gather": 0.0}
        can_craft = agent.material_count() >= cfg.min_mix_size and agent.energy > cfg.craft_energy_reserve
        if can_craft and len(agent.objects) >= cfg.max_objects and agent.material_count() >= cfg.max_materials:
            obs = self._observation(agent, None)
            handle = agent.policy.choose_discard(obs, rng)
            if handle is not None:
                dropped = agent.objects.pop(handle)
                self.events.append(
                    {"type": "discard", "tick": self.tick, "agent": agent.agent_id, "object_id": dropped.object_id}
                )
        if can_craft and len(agent.objects) < cfg.max_objects:
            costs["craft"] = self._craft(agent, rng)
        elif agent.material_count() < cfg.max_materials:
            gather_rng = Random(_stream_seed(cfg.seed, "gather", agent.agent_id, self.tick))
            gathered = self.world.gather(agent.x, agent.y, gather_rng, self.tick)
            room = cfg.max_materials - agent.material_count()
            for material in sorted(gathered):
                take = min(room, gathered[material])
                if take <= 0:
                    break
                agent.materials[material] = agent.materials.get(material, 0) + take
                room -= take
            agent.energy -= cfg.gather_cost
            costs["gather"] = cfg.gather_cost
        return costs

    def step(self) -> None:
        cfg = self.config
        if cfg.freeze_memory_tick is not None and self.tick == cfg.freeze_memory_tick:
            for agent in self.agents:
                if isinstance(agent.policy, OutcomeLearner):
                    agent.policy.frozen = True
        for agent in self.agents:
            move_rng = self._move_rngs[agent.agent_id]
            encounter_rng = self._encounter_rngs[agent.agent_id]
            if not agent.alive:
                continue
            # Movement and encounters use per-agent streams that are drawn every
            # tick whatever the agent decides, so a seed gives every condition
            # the same paths and the same food encounters (paired seeds) until
            # an agent dies.
            self._move(agent, move_rng)
            has_target = encounter_rng.random() < cfg.target_prob
            context = self.world.encounter_context(agent.x, agent.y, encounter_rng)
            row = {"tick": self.tick, "agent": agent.agent_id, "food": 0.0, "effort": 0.0, "craft": 0.0, "gather": 0.0}
            agent.energy -= cfg.drain_per_tick
            policy_rng = self._policy_rngs[agent.agent_id]
            if has_target:
                row.update(self._use(agent, context, policy_rng))
            else:
                row.update(self._idle_step(agent, policy_rng))
            self.ledger.append(row)
            if agent.energy <= 0:
                agent.alive = False
                agent.death_tick = self.tick
                self.events.append({"type": "death", "tick": self.tick, "agent": agent.agent_id})
        self.tick += 1

    def run(self) -> "Arena":
        while self.tick < self.config.ticks:
            self.step()
        return self


def run_arena(config: ArenaConfig) -> Arena:
    return Arena(config).run()


def config_dict(config: ArenaConfig) -> dict:
    data = asdict(config)
    data["blocked_materials_after_transfer"] = list(config.blocked_materials_after_transfer)
    return data
