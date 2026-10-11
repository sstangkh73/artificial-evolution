# After Fix Report: True Replication Seed Independence

Date: 2026-06-26

## Summary

The targeted-movement RNG bypass was fixed. `Agent._move_toward()` now uses the run-level RNG supplied by its caller instead of constructing a local `Random(self.agent_id + self.age)`.

This makes targeted movement reproducible for the same experiment seed and sensitive to different experiment seeds.

## Files Changed

- `agents/agent.py`
  - `_move_toward(env, target_x, target_y, rng)` now receives caller RNG.
  - home-anchor movement passes `rng`.
  - hunger-memory return movement passes `rng`.
  - local `Random(self.agent_id + self.age)` calls were removed from targeted movement.

- `tests/test_seed_independence.py`
  - Added regression tests for same-seed reproducibility and cross-seed movement sensitivity.

- `reports/journal_readiness/01_true_replication_seed_fix_2026-06-26/before/README.md`
  - Added pre-fix audit report.

- `reports/journal_readiness/01_true_replication_seed_fix_2026-06-26/after/README.md`
  - Added this post-fix validation report.

## Root Cause

The simulation had a run-level RNG, and many behavior paths already used it correctly. However, targeted movement bypassed it:

```python
Random(self.agent_id + self.age)
```

That made tie-breaking inside `_choose_best_step()` depend on agent identity and age, not on `args.seed`. Multi-seed runs could therefore share identical targeted movement decisions in paths where targeted movement dominated behavior.

## Fix

Before:

```python
best_step = self._choose_best_step(env, Random(self.agent_id + self.age), target=target)
...
self._wander(env, Random(self.agent_id + self.age))
```

After:

```python
best_step = self._choose_best_step(env, rng, target=target)
...
self._wander(env, rng)
```

Callers now pass the existing run-level `rng` into `_move_toward()`.

## Validation

### Source Search

Post-fix search found no remaining targeted-movement instances of:

```text
Random(self.agent_id + self.age)
```

### Probe Result

Same probe as the before report:

```text
Agent._move_toward(env, 13, 13, Random(seed)) from identical state:
20260610 -> (10, 12, 138, 2)
20260611 -> (12, 10, 138, 2)
20260612 -> (10, 12, 138, 2)
20260613 -> (10, 12, 138, 2)
20260614 -> (12, 10, 138, 2)
repeat 20260610 -> (10, 12, 138, 2), (10, 12, 138, 2)
```

Interpretation:

- Same seed is reproducible.
- Different seeds can produce different targeted movement choices.

### Automated Tests

```text
python -m unittest tests.test_seed_independence
Ran 2 tests in 0.011s
OK
```

```text
python -m unittest discover -s tests
Ran 27 tests in 0.015s
OK
```

## Success Criteria Check

- No remaining `Random(self.agent_id + self.age)` targeted-movement bypasses: passed.
- Same seed + same initial state remains reproducible: passed.
- Different seeds + same initial state can produce different targeted movement choices: passed.
- Unit tests cover reproducibility and seed sensitivity: passed.

## Remaining Limitations

This fix validates the mechanism but does not by itself revalidate prior scientific results.

The following older results should be treated as pre-fix evidence until rerun:

- Phase 1 ecology gate multi-seed claims,
- Phase 2 reward-place learning multi-seed claims,
- Phase 3 seed-causality multi-seed claims,
- Phase 4/5 falsification and site-selection claims,
- population sustainability sweeps that relied on multi-seed variance.

## Recommended Next Step

Create a frozen replication protocol and rerun the paper-core experiments under the fixed RNG:

- 20-30 seeds per main condition,
- per-run aggregate metrics,
- confidence intervals and effect sizes,
- nested analysis where agents are nested inside seed/run.

## Confidence After Fix

High confidence that the identified targeted-movement RNG bypass is fixed.

Medium confidence that overall multi-seed independence is now substantially improved. A full replication audit should still scan other deterministic helper paths before journal submission.
