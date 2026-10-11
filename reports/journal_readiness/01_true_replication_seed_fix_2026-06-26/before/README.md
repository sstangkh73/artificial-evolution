# Before Fix Report: True Replication Seed Independence

Date: 2026-06-26

## Objective

Fix journal-readiness item 1: make multi-seed runs valid independent replications by ensuring movement randomness is controlled by the experiment seed.

## Research Risk

The current paper claims depend on comparing outcomes across seeds. If the dominant movement path ignores `args.seed`, then apparent multi-seed evidence can collapse into deterministic repetition. That weakens:

- reward-place learning replication,
- seed-causality replication,
- site-selection controls,
- population-dynamics sweeps,
- any reported mean/variance across seeds.

## Hypothesis

`args.seed` does not fully control agent movement because part of the movement stack creates a local RNG from `agent_id + age` instead of using the run-level RNG.

## Evidence Supporting

Source inspection found two deterministic local RNG calls in `agents/agent.py`:

- `Agent._move_toward()` calls `_choose_best_step(env, Random(self.agent_id + self.age), target=target)`.
- `Agent._move_toward()` falls back to `_wander(env, Random(self.agent_id + self.age))`.

These calls ignore the run-level `rng` passed into `Agent.tick(env, rng)`.

## Probe Result

Pre-fix probe:

```text
for seeds [20260610, 20260611, 20260612, 20260613, 20260614]
Agent._move_toward(env, 13, 13) from identical state:
20260610 -> (10, 12, 138, 2)
20260611 -> (10, 12, 138, 2)
20260612 -> (10, 12, 138, 2)
20260613 -> (10, 12, 138, 2)
20260614 -> (10, 12, 138, 2)
```

Control probe on the lower-level chooser:

```text
Agent._choose_best_step(env, Random(seed), target=(13, 13)):
20260610 -> (0, 1)
20260611 -> (1, 0)
20260612 -> (0, 1)
20260613 -> (0, 1)
20260614 -> (1, 0)
```

Interpretation: the movement chooser can vary by seed when it receives a seed-specific RNG, but `_move_toward()` masks that variation by constructing its own deterministic RNG.

## Pattern

The defect is not global randomness failure. The run-level RNG exists and is passed through most behavior paths. The bug is a localized bypass in targeted movement.

## Possible Causes

- The local `Random(agent_id + age)` was likely introduced to make target movement deterministic per agent/tick.
- It accidentally severed target movement from experiment-level seed control.

## Alternative Causes Considered

- Spawn randomness: not the root cause of this probe because the probe fixes initial agent state.
- Environment randomness: not the root cause of this probe because the probe uses an empty deterministic environment.
- `_choose_best_step()` itself: not the root cause because it varies when given `Random(seed)`.

## Required Fix

Thread the run-level `rng` into `_move_toward()` and use it for:

- `_choose_best_step(...)`,
- `_wander(...)` fallback.

Update all `_move_toward()` call sites so targeted movement remains deterministic under the run seed and diverges across different run seeds.

## Success Criteria

- No remaining `Random(self.agent_id + self.age)` movement bypasses.
- Same seed + same initial state remains reproducible.
- Different seeds + same initial state can produce different targeted movement choices.
- Unit tests cover both reproducibility and seed sensitivity.

## Failure Criteria

- `_move_toward()` still produces identical paths across different seeds when RNG-sensitive tie-breaking is available.
- Run-level reproducibility breaks for identical seeds.
- Any behavior path still constructs movement RNG from only `agent_id + age`.

## Confidence Before Fix

High that this is a real replication defect for targeted movement paths.

Generalization impact is medium-to-high because targeted movement is used by hunger memory return and home-anchor movement, both relevant to learning and population experiments.
