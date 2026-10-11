# Before Fix Report: Per-Agent Causal Trace

Date: 2026-06-26

## Objective

Fix journal-readiness item 5: export a per-agent causal trace that links individual experience, memory, food choice, social contact, and outcomes.

## Research Risk

Aggregate condition outcomes can show that something changed, but they cannot prove that a specific agent changed behavior after direct experience. For a learning paper, reviewers will ask:

- Did the same agent taste the relevant food before avoiding it?
- Did the same agent hold memory before acting on it?
- Were skipped foods tied to direct prior experience or only social proximity?
- Are effects nested inside a few lucky agents or distributed across runs?

Without an exported per-agent trace, the paper risks relying on aggregate inference.

## Current State

Research artifacts already write `agent_outcomes.csv` per run. Publication batches currently load those rows to compute aggregate proxies:

- mean memory sites,
- social contact rate,
- object experimentation rate,
- mean friend count.

However, `_run_publication_conditions_batch()` does not pass enriched agent rows into `write_publication_artifacts()`, so the final publication package lacks a cross-run per-agent trace table.

## Evidence Supporting

- `simulation/runner.py` loads `agent_rows = bundle["agent_outcomes"]`.
- The publication payload currently includes replicate rows, tick rows, lineage rows, and event rows.
- It does not include `agent_outcome_rows`.
- `agent_outcomes.csv` records meals by type and memory counts, but not skip/value-memory fields yet.
- Event logs can record `food_consumed`, `plant_lifecycle_food_consumed`, `food_skipped`, and `seed_dropped`, but the package does not summarize them per agent.

## Alternative Explanations

- Per-run manifests still contain agent rows. That helps reproducibility but forces reviewers to reconstruct the causal table themselves.
- Script-specific food-value summaries exist elsewhere, but they are not part of the general publication package.

## Required Fix

1. Carry enriched agent outcome rows into publication packages with condition, replicate, and seed identifiers.
2. Add current skip/value-memory fields to research agent outcomes when available.
3. Build `agent_causal_trace.csv` from agent rows plus event rows.
4. Include direct-experience flags such as food consumed, food skipped, memory sites, and social contact.
5. Add tests using synthetic agent and event rows.

## Success Criteria

- Publication packages include an agent-level trace across all runs.
- Each trace row keeps the independent seed/run identifiers visible.
- Food-consumption and food-skip events can be audited per agent.
- The package flags cases where skip behavior lacks recorded direct taste.
- Tests protect the artifact.

## Failure Criteria

- Agent evidence remains buried only in per-run manifests.
- Aggregate means are the only learning proxy.
- Skip behavior cannot be checked against prior direct food experience.

## Confidence Before Fix

High that this is a genuine causal-evidence gap for a learning-focused journal paper.
