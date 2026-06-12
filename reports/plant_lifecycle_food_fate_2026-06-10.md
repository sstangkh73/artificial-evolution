# Plant Lifecycle Food Fate Report

Date: 2026-06-10

## Objective

Measure the first priority metric proposed by the user:

`plant_lifecycle food consumed count`

The key question is whether fruit produced by the plant lifecycle is eaten by agents, decays, or remains in the world.

## Instrumentation Added

New event types:

- `plant_lifecycle_food_consumed`
- `plant_lifecycle_food_decayed`
- `food_consumed`
- `food_decayed`

New result fields:

- `plant_lifecycle_food.remaining`
- `plant_lifecycle_food.consumed`
- `plant_lifecycle_food.decayed`
- `plant_lifecycle_food.fruited`
- `event_location_hotspots`

Tracked location hotspots:

- `harvest_seed_dropped`
- `seed_picked`
- `seed_dropped`
- `seed_buried_by_disturbance`
- `seed_germinated`
- `plant_matured`
- `plant_fruited`
- `plant_lifecycle_food_consumed`
- `plant_lifecycle_food_decayed`

## Run

Output:

- `data/long_no_oracle_15min_20260610_body37_fate_tracking.json`
- `data/long_no_oracle_15min_20260610_body37_fate_tracking.out.log`

Stop condition:

- `interesting_signal:plant_lifecycle_food_fate_observed`

The run now does not stop immediately at first fruiting. It waits until at least one plant-lifecycle food item is consumed or decays.

## Results

- Tick/day: 1000 / day 50
- Population: 50
- Births: 0
- Nests: 0
- `plant_fruited`: 2
- `plant_lifecycle_food.consumed`: 0
- `plant_lifecycle_food.decayed`: 1
- `plant_lifecycle_food.remaining`: 1
- `plant_lifecycle_food_decayed` first tick: 930
- Mean hunger: 0.983
- Instinct states: `hunger=50`

Observed fruit fate:

```text
plant_fruited -> seed=103 species=wild_grain x=9 y=24 energy=9 biomass=0.83 light=0.32
plant_lifecycle_food_decayed -> plant=103 x=9 y=24 energy=9 age_ticks=118
plant_fruited -> seed=103 species=wild_grain x=9 y=24 energy=8 biomass=0.72 light=0.50
```

## Location Hotspots

Plant lifecycle:

- `plant_matured`: x=9, y=24, count=1
- `plant_fruited`: x=9, y=24, count=2
- `plant_lifecycle_food_decayed`: x=9, y=24, count=1
- `plant_lifecycle_food_consumed`: none

Seed burial/germination hotspots:

- x=35, y=15, count=2
- x=31, y=7, count=2
- x=37, y=18, count=2
- x=35, y=13, count=2

Seed pickup/drop:

- `seed_picked`: 0
- `seed_dropped`: 0

## Interpretation

The seed -> plant -> fruit chain is now confirmed. The fruit -> agent link is not confirmed.

In this run, fruit appeared but agents did not consume it before one fruit decayed. One plant-lifecycle food item remained at the stop point. This means the current bottleneck is not plant production alone; it is agent detection, movement, memory, or hunger-loop behavior after fruiting.

The absence of `seed_picked` and `seed_dropped` also matters. Seeds mostly entered the plant lifecycle from harvest drops and disturbance, not from deliberate transport by agents.

## Recommended Next Test

Add a detector for agent response after fruiting:

- distance from nearest agent to fruit at fruiting tick
- time until first agent enters fruit cell
- whether local food signal pulls agents toward x=9, y=24
- whether agents revisit fruiting cells more than nearby control cells

If `plant_lifecycle_food_consumed` becomes greater than 0, the chain becomes:

```text
seed -> plant -> fruit -> agent
```

That would be a much stronger discovery signal than plant fruiting alone.
