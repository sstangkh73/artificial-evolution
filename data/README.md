# Data Directory

This directory contains generated experiment artifacts. Keep source-like data and
large run outputs separated so future experiments remain searchable.

- `raw/`: imported or externally sourced datasets that should not be rewritten.
- `processed/`: cleaned or derived datasets used for analysis.
- `figures/`: generated plots and visual outputs.
- `checkpoints/`: resumable run state, model state, and long-run checkpoints.
- `experiments/`: curated experiment notes and stable experiment records.
- `research_runs/`: run bundles and larger generated result sets.
- `publication_packages/`: frozen artifacts prepared for reporting or papers.

Avoid dropping new long-run outputs directly in `data/` unless a script still
depends on that legacy location.
