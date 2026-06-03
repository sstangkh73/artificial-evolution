# Paper Data Protocol

## Purpose

This protocol defines the minimum data collection standard for any run that may
be cited in a high-quality paper, thesis, preprint, or technical appendix.

The goal is to make every research run:

- reproducible
- auditable
- statistically analyzable
- suitable for both main-text figures and supplementary materials

## Core Principle

Do not treat a research run as only a final score.

For publication-quality analysis, each run should preserve:

1. configuration metadata
2. per-tick state summaries
3. structured event logs
4. lineage-level outcomes
5. agent-level terminal outcomes
6. replayable visual context

## Required Data Layers

### 1. Metadata

Must include:

- run name
- timestamp
- seed
- software/runtime information
- body design and body stats
- world dimensions
- day length
- season length
- food and animal caps
- initial population
- max population
- requested tick horizon
- final realized tick
- snapshot interval
- change note / experiment note

### 2. Tick-Level Panel

Each tick should preserve enough information to reconstruct temporal dynamics.

Required columns:

- `tick`
- `day`
- `population`
- `children`
- `juveniles`
- `adults`
- `old`
- `births`
- `deaths`
- `settlements`
- `stored_food`
- `food_cells`
- `large_animals`
- `mean_energy`
- `mean_durability`
- biome occupancy counts
- top lineages

### 3. Event Log

Store as structured JSONL, one event per line.

Required fields:

- `tick`
- `event_type`
- `raw_text`

Preferred optional fields:

- `day`
- `agent_ids`
- `parent_ids`
- `child_ids`
- `nest_ids`
- `tool_names`
- `position`
- `amount`

### 4. Lineage Table

Each lineage should record:

- founder id
- total births
- peak population
- alive count at run end
- extinction tick if extinct
- completed lifespans
- total agents observed
- mean final age

### 5. Agent Outcome Table

Each observed agent should record:

- lineage id
- parent id
- age at archive
- children count
- food eaten
- distance traveled
- stored-food contribution
- matured offspring count
- alive/dead status
- completed lifespan status
- death reason
- final coordinates
- meal/material/tool dictionaries

### 6. Replay / Visualization Bundle

Each paper-grade run should include:

- dashboard HTML
- dashboard telemetry JSON
- snapshots sufficient to inspect critical ticks

## Minimal Event Taxonomy

The following event families should be preserved whenever they exist:

- `birth`
- `matured_child`
- `build_nest`
- `craft_tool`
- `gather_materials`
- `store_food`
- `withdraw_food`
- `food_shared`
- `food_redistributed`
- `group_formed`
- `hunt_success`
- `hunt_failed`
- `failed_solo_hunt`
- `agent_died`

Alert-level subsets can then be derived from the raw event stream.

## Recommended Statistical Practice

One run is not enough for a paper claim.

Recommended:

- run multiple seeds per condition
- keep one artifact bundle per seed
- aggregate across seeds only after preserving per-run raw data
- separate exploratory runs from confirmatory runs

## Suggested Paper Workflow

1. Define one condition clearly.
2. Run `paper` mode for many seeds.
3. Keep all raw bundles.
4. Derive analysis tables and figures from the raw bundles.
5. Archive raw bundles or make them available as supplementary data.

## Current CLI Support

Run a paper-grade capture with:

```powershell
python main.py --mode paper --seed 7 --paper-body-index 8 --dashboard-ticks 2000 --snapshot-interval 10
```

This writes a research bundle into `data/research_runs/...`.

## Current Limitation

This protocol is already strong enough for serious reporting, but it is still
single-run centered. For publication-grade inference, the next step is a batch
runner that executes the same condition across many seeds and writes a combined
replicate index.
