# Phase 1 Ecology Gate Report - 2026-06-12

## Verdict

Phase 1 ecology gate passed for the tuned 100x100 ecology configuration.

This does not prove agent learning yet. It proves the full-scale world can now produce a stable enough ecology signal for Phase 2 learning tests.

## Gate Criteria

The target gate was:

- `100x100` world
- `natural_seed_rain=0`
- `plant_matured > 0` in at least 70% of seeds
- `plant_fruited > 0` in at least 70% of seeds
- more than a one-off lucky plant
- fruit reaches an observed fate, ideally agent consumption

Final confirmation result:

- `matured_runs`: 5/5
- `fruited_runs`: 5/5
- `plant_food_consumed_runs`: 5/5

## Final Passing Configuration

```text
width=100
height=100
max_food_per_100_cells=20
max_food=2000
base_food_spawn_per_tick=4
food_spawn_multiplier=0.70
bootstrap_food_spawn_ticks=300
wild_food_spawn_after_bootstrap_multiplier=0.10
natural_seed_rain_per_tick=0
max_plant_seeds=7600
plant_seed_max_age_multiplier=4.0
plant_growth_rate_multiplier=2.0
sprout_biomass_loss_multiplier=0.1
germination_good_ticks_multiplier=0.5
plant_fruiting_interval_multiplier=0.25
plant_fruiting_growth_threshold_multiplier=0.5
plant_fruiting_chance_multiplier=2.0
natural_seed_drop_chance_multiplier=2.0
plant_food_decay_chance=0.0015
```

## Run Evidence

Final confirm output:

`data/phase1_5_confirm03_20260612/summary.json`

Seeds:

- 20260610
- 20260611
- 20260612
- 20260613
- 20260614

Aggregate:

- `mean_seed_germinated`: 139.0
- `mean_plant_matured`: 33.6
- `mean_plant_fruited`: 68.6
- `mean_plant_food_consumed`: 47.8
- `mean_seed_to_germinated_rate`: 0.5567
- `mean_germinated_to_matured_rate`: 0.2496
- `mean_matured_to_fruited_rate`: 1.9888
- `mean_ticks_per_second`: 37.39
- `mean_hunger_level`: 0.983

Per-seed fruit/consumption:

- seed 20260610: `plant_fruited=41`, `plant_lifecycle_food_consumed=33`
- seed 20260611: `plant_fruited=48`, `plant_lifecycle_food_consumed=33`
- seed 20260612: `plant_fruited=67`, `plant_lifecycle_food_consumed=52`
- seed 20260613: `plant_fruited=49`, `plant_lifecycle_food_consumed=44`
- seed 20260614: `plant_fruited=138`, `plant_lifecycle_food_consumed=77`

## Iteration Trail

Baseline 100x100 before tuning:

- germination happened
- no mature plants
- no fruit
- many seeds/sprouts died before ecology ignition

Sweep 01:

- added seed age, growth, reduced sprout biomass loss, faster germination
- result: maturity became reliable
- best single seed reached `plant_fruited=1` and `plant_food_consumed=1`

Confirm 01:

- `matured_runs=5/5`
- `fruited_runs=3/5`
- conclusion: sprout survival fixed, fruiting gate still unstable

Confirm 02:

- reduced fruiting interval
- `fruited_runs=3/5`
- conclusion: interval alone was not enough

Confirm 03:

- reduced fruiting growth threshold
- increased fruiting chance
- `fruited_runs=5/5`
- `plant_food_consumed_runs=5/5`
- conclusion: Phase 1 tuned ecology gate passed

## Interpretation

The blocker was not simply food density. It was a chain of biological timing gates:

1. Seeds needed longer viability in the larger world.
2. Sprouts needed lower biomass loss and faster growth to survive sparse/gappy growth windows.
3. Mature plants needed a more permissive fruiting threshold/chance to produce fruit within the full-scale run budget.

The final config still uses substrate rules: seeds, growth, fruit, and food fate are world processes. It does not instruct agents to farm, move seeds, or seek fruit.

## Remaining Risks

- `mean_hunger_level` remains 0.983, so Phase 2 must still address hunger lock or measure learning under heavy hunger pressure.
- The passing config is tuned. It should be treated as the Phase 2 ecology testbed, not as a final claim about realism.
- Only 5 seeds were used for the gate. This is enough for a working gate decision, but a later paper-quality claim should use at least 10-20 seeds.
- `matured_to_fruited_rate` can exceed 1 because one mature plant can fruit multiple times; it is an event rate, not a per-plant probability.

## Phase 2 Readiness

Ready to start Phase 2 under the passing ecology config.

Recommended Phase 2 metrics:

- revisit index after fruit reward
- agent-level food-route recurrence
- fruit hotspot revisits compared with random baseline
- seed contact or seed movement before later plant/fruit events
- individual specialization in foraging
- hunger lock windows: when, if ever, agents leave pure hunger mode

Phase 2 should not yet claim farming. Farming requires:

- `seed_picked > 0`
- `seed_dropped > 0`
- moved seed later germinates
- moved seed later fruits
- agent revisits or consumes fruit from that chain
