# Affective Safety Gate: Before/After Report

Date: 2026-06-10

## Abstract

This run replaced scaffolded reproduction pressure with a substrate-first affective gate: hunger, fear, cold stress, wetness, safety, comfort, attachment, and repeated pair safety now determine whether reproduction can happen. The main result is that the old immediate-birth failure mode was removed. Under the scarce-food condition, all agents became hunger-dominated and reproduction stayed blocked. Under an abundant-food positive-control condition, no birth occurred either, but the simulation produced a low-to-medium confidence substrate farm hotspot without using `build_nest` or `tend_food_patch`.

## Research Question

Can reproduction be made to depend on emergent felt conditions instead of explicit nest/farm scaffolds?

Operational definition:

- Reproduction should require adult female + mate + enough energy + low hunger/fear/cold + safety + comfort + attachment + sustained safety window + sustained pair bond.
- Hunger should override other behavior without killing immortal agents.
- Seeds should appear from plant harvesting and must pass through physical lifecycle conditions before becoming useful plants.
- Scaffolded helper actions should stay disabled by default.

## Before State

Baseline file: `data/affective_reproduction_before.json`

Condition:

- Seed: `20260610`
- Body: `body_index=8`, `sensor=0, muscle=0, armor=1, brain=3, profile=social_planner`
- Initial population: 50 immortal agents
- Time limit: 6 seconds
- World: 40x40, max food 160, base food spawn 5, no natural seed rain

Observed result:

- Tick/day reached: 645 / day 32
- Population: 50, peak 50
- Births: 0
- Nests: 0
- `build_nest`: 0
- `tend_food_patch`: 0
- Harvest seed drops: 68
- Seed picked: 1
- Seed germinated: 26
- Plant matured/fruited: 0 / 0

Interpretation:

The scaffolded nest/farm actions were already disabled, and seed lifecycle was functioning. However, the system still lacked a clean emotional/safety explanation for reproduction. It could say "not near nest" or "not enough nest food" in older paths, which was not aligned with the current research goal.

## Intermediate Failure

File: `data/affective_reproduction_after.json`

After the first affective reproduction gate, the same 6-second condition produced:

- Tick/day reached: 300 / day 15
- Population: 73, peak 73
- Births: 23
- First birth tick: 5
- Nests: 0
- Mean hunger at end: 0.983
- Mean safety at end: 0.127
- Affect-ready adults at end: 0

Interpretation:

This was the important failure. The affective gate worked mechanically, but it was too permissive: agents reproduced almost immediately before hunger and safety pressure had time to matter. This created a birth burst, then the population fell into hunger stress. That is not a discovery process; it is still too much help from the rules.

## Changes Made

Affected code:

- `agents/agent.py`
- `simulation/runner.py`
- `simulation/research_artifacts.py`
- `scripts/run_long_emergence_watch.py`

Main behavioral changes:

- Added continuous affective state:
  - `hunger_level`
  - `fear_level`
  - `cold_level`
  - `wetness`
  - `body_temperature_k`
  - `safety_feeling`
  - `comfort_level`
  - `attachment_level`
  - `safety_streak_ticks`
  - `pair_bond_ticks`
- Hunger now becomes the dominant instinct and blocks reproduction.
- Starvation no longer kills immortal agents; it forces food-seeking priority and can degrade durability.
- Reproduction now requires:
  - adult female
  - mate nearby
  - enough energy/durability
  - low hunger/fear/cold
  - safety and comfort above threshold
  - attachment above threshold
  - sustained safety window
  - sustained pair bond
  - mate not stressed
  - cooldown clear
- Pair bond resets or decreases after reproduction.
- Telemetry now records affective readiness, mean pair-bond ticks, final instinct states, and adult-female reproduction block reasons.

## After State: Tuned Scarce-Food Condition

Diagnostic file: `data/affective_reproduction_after_tuned_diagnostic.json`

Same 6-second condition as baseline:

- Tick/day reached: 577 / day 28
- Population: 50, peak 50
- Births: 0
- Nests: 0
- Mean safety: 0.210
- Mean comfort: 0.000
- Mean fear: 0.095
- Mean hunger: 0.983
- Mean pair-bond ticks: 0.000
- Affect-ready adults: 0
- Instinct states: `hunger=50`
- Adult-female reproduction block reason: `low_energy=25`
- Max attachment: 1.000
- Max pair-bond ticks: 0
- Harvest seed drops: 65
- Seed germinated: 26

Longer file: `data/affective_reproduction_after_tuned_long.json`

60-second scarce-food run:

- Tick/day reached: 6357 / day 317
- Population: 50, peak 50
- Births: 0
- Nests: 0
- Mean safety: 0.005
- Mean comfort: 0.000
- Mean hunger: 0.983
- Mean pair-bond ticks: 0.000
- Instinct states: `hunger=50`
- Harvest seed drops: 325
- Seed germinated: 305
- Plant matured/fruited: 3 / 3
- `build_nest`: 0
- `tend_food_patch`: 0

Interpretation:

The tuned gate removed the immediate birth burst. Agents did form proximity/attachment signals, but hunger dominated before safety and pair-bond duration could accumulate. In this world, "safe enough to reproduce" did not emerge. The agents are immortal, so the outcome is a long hunger-dominated search state rather than extinction.

## Positive Controls

File: `data/affective_reproduction_after_positive_control.json`

Abundant-food run with the original body:

- Body: `body_index=8`
- Max food: 600
- Base food spawn: 25
- Food decline: 0
- Stop reason: `interesting_signal:substrate_farm_hotspot_candidate`
- Tick/day reached: 800 / day 40
- Births: 0
- Mean hunger: 0.903
- Max safety: 0.725
- Max comfort: 0.839
- Max pair-bond ticks: 0
- Seed picked/dropped: 76 / 62
- Seed germinated: 563
- Plant matured/fruited: 35 / 67
- Hotspot: heavily visited cells overlapped mature plants and plant-lifecycle food

File: `data/affective_reproduction_after_positive_control_body37.json`

Abundant-food run with a more capable body:

- Body: `body_index=37`, `sensor=2, muscle=2, armor=0, brain=2, profile=social_planner`
- Tick/day reached: 1268 / day 63
- Births: 0
- Mean hunger: 0.980
- Max pair-bond ticks: 0
- Seed picked/dropped: 17 / 7
- Seed germinated: 519
- Plant matured/fruited: 6 / 10

Additional gate sanity check:

- Manually configured two adult agents with high safety, comfort, attachment, energy, low stress, and complete pair-bond duration.
- `can_reproduce()` returned `eligible=True`.

Interpretation:

The reproduction rule is not logically impossible. The world simply did not produce stable non-hungry, safe, paired states during these runs. The original body is especially weak because it starts with no sensor or muscle units, so even abundant food does not translate into sustained energy security.

## What Actually Happened

The most interesting event is not reproduction. It is the separation between plant ecology and agent understanding:

1. Seeds are now mostly generated by harvest events, not by global seed rain.
2. Seeds can settle, germinate, mature, and fruit from environmental conditions.
3. Agents can pick up and drop seeds.
4. In the abundant-food condition, repeated movement and seed drops created a plant/visit hotspot that looks farm-like at low-to-medium confidence.
5. The agents still do not appear to understand that seeds are delayed food or that plant clusters can become safety infrastructure.
6. Hunger dominates behavior before pair safety can accumulate.

This is a useful failure: the world now has enough substrate for "farming-like" discovery, but the agents do not yet have the cognitive bridge from observation to intentional cultivation.

## Limitations

- The current agent body used in the main run has `sensor=0` and `muscle=0`; it is a harsh founder morphology.
- Pair bond currently depends on already feeling safe, so no pair memory survives extended hunger stress.
- Food exists in the world but agents still fail to convert it into stable energy. This may be perception, movement, food distribution, or energy-cost tuning.
- The farm hotspot detector is intentionally conservative: it reports overlap of visits + mature plants + plant-lifecycle food, not proof of intentional farming.
- No 20-minute wall-clock run was performed in this patch cycle; the longest run here was 60 seconds, reaching simulation day 317.

## Next Work

1. Add a lightweight memory link: "food found here after plant matured" without telling agents that seeds cause plants.
2. Add observation telemetry for seed contact, seed drop location, later plant food, and revisits.
3. Test multiple body morphologies, because `sensor=0/muscle=0` may mask learning capacity.
4. Let pair bond decay more slowly than immediate safety so relationships can persist through short hunger periods.
5. Add a controlled energy-economy sweep to find whether hunger domination is caused by metabolism, food placement, vision, or movement cost.
