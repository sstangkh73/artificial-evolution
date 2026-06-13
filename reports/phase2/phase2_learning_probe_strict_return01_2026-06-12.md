# Phase 2 Learning Probe Report

- Verdict: PASS
- Runs: 3 seeds; passed 3/3
- Gate: at least 3 passing runs
- Ecology gate per run: matured >= 1, fruited >= 1, consumed >= 5
- Learning gate per run: owner returned rewards >= 5, owner return agents >= 2, return lift >= 2.0

## Aggregate Metrics

- Mean plant food consumed: 106.6667
- Mean owner returned rewards: 80.0
- Mean owner return agents: 30.6667
- Mean owner return lift: 41.7027

## Runs

| seed | pass | consumed | returned_rewards | return_agents | return_lift | first_return_tick |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 20260610 | True | 105 | 82 | 31 | 52.715 | 806 |
| 20260611 | True | 84 | 65 | 24 | 38.694 | 485 |
| 20260612 | True | 131 | 93 | 37 | 33.699 | 754 |

## Interpretation

This probe does not claim farming or symbolic understanding. It tests a narrower Phase 2 claim: after receiving energy from plant-lifecycle food, the same agent leaves and later returns near that rewarded location more often than a uniform random-position baseline.
