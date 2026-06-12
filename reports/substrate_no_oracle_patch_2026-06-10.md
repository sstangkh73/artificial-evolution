# Substrate-First No-Oracle Patch Report

Date: 2026-06-10

## Abstract

This patch removes the remaining high-level helpers that made the world interpret itself for agents. Hunger immortality was intentionally preserved. The simulation now favors local sensory gradients, physical seed burial through soil disturbance, heat-required cooking, disabled automatic food sharing, disabled shared group memory, and bootstrap-only wild food. Short validation runs confirm that legacy birth/nest/farm/cooking/share scaffolds did not fire, while seed burial and germination can still occur through substrate events.

## Changes

### Perception

- Agents no longer call nearest-food, nearest-warm-cell, or nearest-safe-area oracle search in normal behavior.
- Movement toward food now uses `food_signal_at(...)`, a local attenuated signal rather than a target coordinate.
- Cold and fear instincts choose among neighboring cells by local temperature and danger gradients.
- Legacy nearest food/warm/safe APIs now return `None` unless `legacy_oracle_perception_enabled=True`.
- Hunting no longer chases distant prey by oracle target; it only engages nearby animals.

### Cooking

- `body.cooking_skill` no longer cooks food by itself.
- Cooking now requires an external heat condition:
  - hearth support, or
  - cell temperature at least 373.15 K.
- Without heat, raw food stays raw.

### Social Help

- Group joining no longer merges food/danger/safe/nest memories across members.
- Automatic food sharing and redistribution are disabled unless `scaffolded_social_support_enabled=True`.
- Agents can still form proximity groups and social/pair affect from local contact.

### Seeds And Plants

- Surface seeds no longer gradually bury themselves just from moisture/cover.
- Soil has a disturbance field.
- Agent movement and seed dropping can disturb the surface.
- Seeds can become buried only through disturbance on soil/sand/clay.
- The event changed from `seed_settled` to `seed_buried_by_disturbance`.

### Food Ecology

- Wild plant food is now an early bootstrap source.
- After `bootstrap_food_spawn_ticks`, wild food spawn is multiplied by `wild_food_spawn_after_bootstrap_multiplier`.
- Watch-run defaults now use lower wild food pressure:
  - `max_food=220`
  - `base_food_spawn_per_tick=2`
  - `food_spawn_multiplier=0.45`
  - `bootstrap_food_spawn_ticks=120`
  - `wild_food_spawn_after_bootstrap_multiplier=0.08`
- Plant lifecycle food is now the intended long-run source.

### Structure/Nest Scaffold

- Existing high-level `build_nest`, `consume_building_resources`, and `tend_food_patch` require both:
  - `scaffolded_agent_actions_enabled=True`
  - `legacy_scaffold_nest_enabled=True`
- Default substrate-first runs keep both disabled, so no symbolic nest/farm action can accidentally create infrastructure.

## Validation Runs

### Final Smoke

File: `data/substrate_no_oracle_final_smoke.json`

- Body: `body_index=37`, `sensor=2, muscle=2, armor=0, brain=2`
- Tick/day: 948 / day 47
- Population: 50
- Births: 0
- Nests: 0
- Cooking events: 0
- Food shared events: 0
- `build_nest`: 0
- `tend_food_patch`: 0
- `surface_disturbed`: 2984
- `harvest_seed_dropped`: 27
- `seed_buried_by_disturbance`: 9
- `seed_germinated`: 9
- `plant_matured`: 0
- `plant_fruited`: 0
- Mean hunger: 0.983

### Body 37 Probe

File: `data/substrate_no_oracle_body37_probe.json`

- Tick/day: 3224 / day 161
- Population: 50
- Births: 0
- Nests: 0
- Cooking events: 0
- Food shared events: 0
- `build_nest`: 0
- `tend_food_patch`: 0
- `surface_disturbed`: 7125
- `harvest_seed_dropped`: 96
- `seed_buried_by_disturbance`: 31
- `seed_germinated`: 31
- `plant_matured`: 0
- `plant_fruited`: 0
- Mean hunger: 0.983

## Interpretation

The patch succeeded at removing the major helpers:

- no oracle target search for food/warmth/safety in normal behavior
- no trait-only cooking
- no automatic food sharing
- no group memory merge
- no auto seed burial
- no accidental symbolic nest/farm construction

The world is now more honest, but also much harsher. Agents quickly enter hunger instinct and do not sustain safety or pair-bond windows. Seeds can still be physically buried and germinate, but in these short validation runs plants did not reach mature/fruiting states before the food economy collapsed.

## Remaining Physics Gaps

- Large-animal ecology is still simplified.
- Agent sensing is still abstract scalar signal, not vision/olfaction/raycast perception.
- There is no full material assembly model for shelters yet; legacy nest construction is locked off rather than replaced by complete load-bearing construction.
- Fire/heat can gate cooking, but agents still do not have a full discoverable fire-making pathway.
- Plant maturity may now be too slow relative to food bootstrap decay.
- Group formation is still proximity-based and role assignment is still symbolic, though shared memory and automatic food transfer are disabled.

## Next Verification

Run a parameter sweep over:

- bootstrap food duration
- plant maturity rate
- seed burial disturbance strength
- sensory signal radius
- body morphologies with nonzero sensor/muscle

Success criteria for the next phase:

- at least one run reaches `plant_matured` and `plant_fruited` after oracle removal
- no `cooking`, `food shared`, `build_nest`, or `tend_food_patch` events in substrate-first mode
- agents revisit plant-lifecycle food cells more often than random walk expectation
