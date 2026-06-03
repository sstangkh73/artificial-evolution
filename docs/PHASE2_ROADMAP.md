# Phase 2 Roadmap

## Goal

Phase 2 should shift the project from:

- curated search over body and trait space

to:

- genuine in-simulation adaptation across generations

The roadmap below is based on the current codebase and the main gaps between
documentation, implementation, and research goals.

## Phase 2 Priorities

### 1. Make Evolution Endogenous

Target outcome:
- offspring differ from parents through controlled inherited variation

Why first:
- this is the largest gap between the research framing and the actual implementation

Implementation targets:
- add heritable trait mutation during `spawn_child()`
- define mutation bounds and mutation rates
- decide which properties are inherited directly and which are derived
- persist lineage identifiers and parent-child ancestry more explicitly
- add experiment metrics for mutation spread and lineage branching

Suggested files:
- [agents/body.py](/C:/artificial-evolution/agents/body.py)
- [agents/agent.py](/C:/artificial-evolution/agents/agent.py)
- [simulation/runner.py](/C:/artificial-evolution/simulation/runner.py)

### 2. Separate Morphology Evolution From Trait Evolution

Target outcome:
- know whether success is coming from body structure, behavior traits, or both

Why next:
- current Phase 1 success is concentrated in a narrow morphology corridor

Implementation targets:
- support mutation toggles for morphology and traits independently
- record morphology drift and trait drift separately
- add metrics for morphology diversity over time
- compare runs with:
  - trait-only mutation
  - morphology-only mutation
  - combined mutation

### 3. Upgrade Experiment Telemetry

Target outcome:
- make lineage and settlement behavior auditable over time, not only in summary

Why next:
- current summaries are strong, but missing per-tick and spatial trace data needed for deeper analysis

Implementation targets:
- record per-tick population counts
- record births, deaths, and matured-child events as structured telemetry
- record settlement counts and storage totals over time
- optionally snapshot agent coordinates at intervals
- write a versioned schema for experiment artifacts

Suggested files:
- [simulation/runner.py](/C:/artificial-evolution/simulation/runner.py)
- [data/figures/README.md](/C:/artificial-evolution/data/figures/README.md)

### 4. Deepen The Settlement Economy

Target outcome:
- make settlement success depend on real medium-term planning, not only food buffering

Why next:
- the current world already rewards settlement logic, so this is the natural next layer

Implementation targets:
- add nest storage limits or upgrade paths
- add infrastructure tiers
- add resource conversion chains beyond direct food use
- add higher-tier tools or settlement modules
- add scarcity trade-offs between immediate consumption and infrastructure investment

Suggested files:
- [world/environment.py](/C:/artificial-evolution/world/environment.py)
- [agents/agent.py](/C:/artificial-evolution/agents/agent.py)
- [docs/TECH_TREE.md](/C:/artificial-evolution/docs/TECH_TREE.md)

### 5. Add Real Ecological Counterpressure

Target outcome:
- prevent one narrow safe-settlement strategy from dominating too easily

Why next:
- Phase 1 indicates the world strongly rewards one niche

Implementation targets:
- introduce more prey types with different risk/reward profiles
- introduce predators or raid-like threats
- vary safe-zone reliability over time
- make danger and food patterns less quadrant-static
- test whether successful lineages remain settlement-centered under changing ecology

### 6. Build Runtime Visualization From Telemetry

Target outcome:
- inspect emergent behavior directly rather than reconstructing it from logs

Why next:
- this improves research iteration speed and debugging quality

Implementation targets:
- population timeline plots
- settlement growth plots
- simple replay frames or heatmaps
- lineage branching diagrams from structured ancestry data

Suggested files:
- [visualization/__init__.py](/C:/artificial-evolution/visualization/__init__.py)
- future visualization modules under [visualization](/C:/artificial-evolution/visualization)

## Recommended Build Order

1. Add inherited mutation and lineage IDs.
2. Add structured telemetry and per-tick outputs.
3. Run controlled experiments separating morphology and trait mutation.
4. Add settlement economy depth.
5. Add ecological counterpressure.
6. Add visualization and analysis tooling.

## Suggested Research Questions For Phase 2

- When mutation is endogenous, does the same morphology corridor still dominate?
- Do settlement-centered strategies remain optimal once ecology is less stationary?
- Can morphology diversity emerge without external trait-variant generation?
- Which mutations correlate with lineage persistence across many generations?
- Does stronger ecology produce specialization, coexistence, or collapse into one niche?

## Concrete Near-Term Tasks

### Short Horizon

- create a `genome` or inheritance layer around `BodyPlan`
- mutate offspring traits inside reproduction
- add lineage metadata to saved experiment outputs
- save time-series population telemetry

### Medium Horizon

- add nest upgrades and storage limits
- add at least one additional prey niche
- add experiment comparison scripts for mutation regimes

### Longer Horizon

- add map variation beyond static quadrants
- add higher-order social behavior and inter-group competition
- add richer replayable visualization artifacts

## Documentation Cleanup Needed Alongside Phase 2

- update [README.md](/C:/artificial-evolution/README.md) to reflect the current system
- update [docs/SIMULATION_ARCHITECTURE.md](/C:/artificial-evolution/docs/SIMULATION_ARCHITECTURE.md) so implemented features are no longer listed as future work
- keep [docs/CURRENT_STATE.md](/C:/artificial-evolution/docs/CURRENT_STATE.md) as the living source of truth for status
