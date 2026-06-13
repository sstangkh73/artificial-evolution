# Phase 2 Learning Probe Report

- Verdict: PASS
- Runs: 3 seeds; passed 3/3
- Gate: at least 3 passing runs
- Ecology gate per run: matured >= 1, fruited >= 1, consumed >= 5
- Learning gate per run: owner revisited rewards >= 5, owner revisit agents >= 2, lift >= 2.0

## Aggregate Metrics

- Mean plant food consumed: 291.3333
- Mean owner revisited rewards: 269.6667
- Mean owner revisit agents: 44.6667
- Mean owner revisit lift: 61.3747

## Runs

| seed | pass | consumed | revisited_rewards | revisit_agents | lift | first_revisit_tick |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 20260610 | True | 228 | 214 | 45 | 69.504 | 790 |
| 20260611 | True | 205 | 194 | 41 | 60.826 | 479 |
| 20260612 | True | 441 | 401 | 48 | 53.794 | 749 |

## Interpretation

This probe does not claim farming or symbolic understanding. It tests a narrower Phase 2 claim: after receiving energy from plant-lifecycle food, the same agent returns near that rewarded location more often than a uniform random-position baseline.
