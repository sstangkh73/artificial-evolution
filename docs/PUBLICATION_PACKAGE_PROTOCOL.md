# Publication Package Protocol

## Goal

This protocol defines the minimum artifact set for a publication-grade simulation
study in this project.

The package is designed to support:

- multi-seed replicate analysis
- condition-level comparisons
- figure-ready source data
- data availability statements
- supplement-grade methods reporting

## Required Layers

### 1. Condition Registry

Store one row per experimental condition with:

- condition id
- scientific question
- body design
- founder composition
- world overrides
- stopping rules

### 2. Replicate Index

Store one row per seed per condition with:

- seed
- condition id
- primary outcomes
- secondary outcomes
- links to raw manifests

### 3. Primary Outcomes

At minimum:

- extinction status
- extinction / final tick
- generation-3 success
- generation-3 tick
- first technology tick
- peak population
- total births
- matured children

### 4. Secondary Outcomes

Recommended:

- stored food
- average age
- final sex composition
- maximum generation observed
- reproduction-failure burden

### 5. Figure Source Data

Every main figure should have a dedicated source-data CSV.

Recommended figure families:

- condition matrix
- population trajectories
- survival curves
- reproduction funnel
- technology emergence
- failure reasons
- lineage outcomes
- aggregate condition statistics

### 6. Methods and Analysis Files

Include:

- full methods
- statistical analysis plan
- data availability statement
- negative results summary

## Current CLI

Run a publication-grade batch with:

```powershell
python main.py --mode publication-batch --seed 7 --study-seeds 6 --dashboard-ticks 1200 --snapshot-interval 10
```

This writes:

- raw replicate bundles under `data/research_runs/`
- publication package outputs under `data/publication_packages/`

Run a robustness sweep with:

```powershell
python main.py --mode robustness-batch --seed 7 --study-seeds 4 --dashboard-ticks 1600 --snapshot-interval 20
```

Render figures from a publication package with:

```powershell
python scripts/render_publication_figures.py data/publication_packages/experiment_047_publication_batch
```

## Review Standard

A publication package is not complete unless:

- all seeds are indexed
- all figures have source data
- all conditions are declared explicitly
- negative results are preserved
- raw run manifests remain linked from aggregate tables
