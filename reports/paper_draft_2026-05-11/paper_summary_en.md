# Artificial Evolution Paper Summary Draft (2026-05-11)

## Working Title

From Survival Search to Multi-Generational Continuity and Emergent Technology in an Artificial Life World

## One-Sentence Summary

This project began as a body-plan survival simulation, evolved through a Phase 1 search for lineage-capable settlement-centered agents, and has now reached a post-Phase-1 stage in which sexed reproduction can sometimes sustain generation-3 adulthood, while emergent technology appears reliably but still too early to count as strongly pressure-driven innovation.

## Project Arc From Zero

The project started from a minimal question: under a fixed body-cost budget, which artificial bodies survive longest in a spatial world with limited food and movement costs. The earliest system emphasized morphology, energy depletion, and simple foraging in a `100x100` world. At that stage, the central readout was still close to individual survival.

Over time, the simulation expanded in scope. The world gained ecological zones, day-night cycles, seasons, danger, herd prey, food processing, memory, nests, storage, cooperation, parent-child links, and social role persistence. This changed the scientific question from “which body survives” to “which body can establish a lineage under ecological and social constraints.”

## Phase 1 Outcome

Phase 1 established the first robust lineage-capable niche in the project. The main result was not broad morphological diversity, but a narrow successful corridor centered on settlement-oriented, care-investing bodies. In current working data, two canonical representatives dominate this corridor:

- `body_8`: `sensor=0, muscle=0, armor=1, brain=3, profile=social_planner`
- `body_14`: `sensor=0, muscle=0, armor=1, brain=3, profile=nurturing_settler`

The massive-lineage search confirms that both bodies can produce large birth counts and matured offspring under the older lineage-search regime. The larger scientific lesson from Phase 1 is that long-run success in this world is driven less by speed or aggressive scouting alone and more by a settlement-centered strategy combining durability, sociality, storage, and care.

## Post-Phase-1 Shift

After Phase 1, the project moved in two major directions.

First, the simulation was instrumented as a research system rather than only a prototype. It now exports run metadata, per-tick panels, structured event logs, lineage tables, agent tables, replay dashboards, publication packages, and figure-ready source data.

Second, the conceptual model of technology was changed. The old named crafting system was removed in favor of emergent technology detection. The simulation no longer asks whether agents “crafted a knife”; instead, it asks whether they created and repeatedly used objects whose physical properties improved outcomes and spread socially enough to count as technology.

## Current Experimental Results

### Publication Batch

The main publication package in [C:/artificial-evolution/data/publication_packages/experiment_047_publication_batch](C:/artificial-evolution/data/publication_packages/experiment_047_publication_batch) ran `5 conditions x 6 seeds = 30 replicates`.

The major outcomes are:

- `baseline_body_8`: generation-3 success rate `0/6`, extinction rate `6/6`
- `baseline_body_14`: generation-3 success rate `0/6`, extinction rate `6/6`
- `technology_pressure_body_8`: generation-3 success rate `0/6`, extinction rate `6/6`
- `sexed_gen3_body_8`: generation-3 success rate `2/6` (`33.3%`)
- `sexed_gen3_body_14`: generation-3 success rate `1/6` (`16.7%`)

These results show that the post-fix sexed world can sustain multi-generational continuity in some replicates, but not yet robustly.

### Robustness Sweep

The robustness package in [C:/artificial-evolution/data/publication_packages/experiment_048_robustness_sweep](C:/artificial-evolution/data/publication_packages/experiment_048_robustness_sweep) tested harsher technology-emergence conditions and lower-food sexed worlds.

The strongest current robustness findings are:

- `harsh_tech_low_food_body_8`: mean first-technology tick `21.0`
- `harsh_tech_frontier_cost_body_8`: mean first-technology tick `36.333`
- one replicate in `harsh_tech_frontier_cost_body_8` produced no technology emergence within the run
- `sexed_low_food_body_8`: generation-3 success rate `0/4`
- `sexed_low_food_body_14`: generation-3 success rate `1/4`

This means technology emergence can be delayed substantially by ecological pressure, but the current world still tends to generate useful object behavior relatively early. It also means that sexed multi-generation survival remains fragile under lower-food conditions.

## What Was Solved Recently

One of the most important recent findings is that earlier sexed-world collapse was not simply “the world being too hard.” Diagnostics showed that generation-1 agents had valid sex assignments and matured correctly, but the reproduction chain frequently broke because newly matured adults did not reliably resolve access to a usable family household and nest storage. After fixing family household continuity, generation-3 adulthood became achievable without reducing world difficulty.

This is scientifically important because it shifts the interpretation of failure. Some earlier extinctions were not evidence that the ecological hypothesis failed; they were evidence that household inheritance mechanics were incomplete.

## Current Problems

The current project is much stronger than the original prototype, but it still has major open problems before a front-rank paper claim would be fully justified.

### 1. Technology Emergence Is Still Too Early

Emergent technology now exists as a conceptually better system, but it remains too easy in many conditions. Even after pressure increases, technology often emerges within tens of ticks, not after prolonged exploratory pressure. This weakens any claim that the current world has already produced strongly pressure-driven innovation.

### 2. Multi-Generational Survival Is Not Yet Robust

`body_8` can reach generation 3 under sexed reproduction, but only in a subset of seeds. `body_14` performs worse overall. Lower-food conditions reduce success sharply. The present conclusion is therefore “possible but fragile,” not “stable and general.”

### 3. Endogenous Evolution Is Still Incomplete

The project has lineages and selection pressures, but it still does not run a full inherited mutation-and-selection loop internally across many generations. Much of the earlier search success came from external sweeps over candidate bodies and trait variants. That is good for discovery, but weaker for claims about autonomous open-ended evolution.

### 4. Morphological Diversity Remains Narrow

The project has produced rich differences in trait-space and life-history style, but success remains concentrated in a narrow morphology corridor. This is not a failure, but it does limit how broadly one can currently generalize about “many viable body plans.”

### 5. Paper-Grade Analysis Is Now Possible, But Not Finished

The repository now contains publication packages, source-data tables, and rendered figures. However, a final paper would still need:

- a tighter main claim
- a curated figure set
- a formal results narrative
- explicit limitations
- possibly one more round of targeted experiments on delayed technology emergence

## Conservative Scientific Claim Today

A defensible current claim would be:

“In this artificial life world, long-run success is concentrated in a narrow settlement-centered body niche. After fixing family household continuity, some sexed populations can sustain multi-generational survival to generation-3 adulthood under unchanged world difficulty. A physically grounded emergent-technology system also produces socially reused useful objects, but current technology emergence still occurs too early to support a strong claim of late-stage, pressure-driven invention.”

## Suggested Paper Structure

1. Introduction
   The problem of moving from survival optimization to lineage continuity and emergent technology.

2. Phase 1
   Search for lineage-capable body plans and discovery of the settlement-centered niche.

3. Post-Phase-1 Methods
   Sexed reproduction, household continuity, emergent technology, and publication-grade telemetry.

4. Results
   Pre-fix collapse, household continuity fix, publication batch, robustness sweep, delayed-yet-still-early technology emergence.

5. Discussion
   Why lineage continuity and technology emergence remain fragile; what prevents a stronger claim today.

6. Limitations
   No full endogenous mutation loop, narrow morphology corridor, and early technology emergence.

7. Future Work
   Stronger exploration pressure, endogenous heredity, and longer-term open-ended dynamics.
