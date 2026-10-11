# Before Fix Report: Statistical Unit and Model Specification

Date: 2026-06-26

## Objective

Fix journal-readiness item 8: export a statistical-unit audit and model specification that prevents pseudoreplication.

## Research Risk

Agent-based simulations produce many rows per seed. If a paper treats agent rows, event rows, or ticks as independent replicates, reviewers can reject the inference as pseudoreplication.

The correct independent unit for condition-level inference is the seed/run, while agent rows are nested within runs.

## Current State

The statistical analysis plan already says each seed is one replicate and agent rows are nested. However, there is no separate audit table that quantifies:

- seed-level replicate count,
- agent rows per seed,
- event rows per seed,
- which layer is inferential versus descriptive,
- which model family applies to each outcome.

## Hypothesis

The package becomes stronger if it includes a reviewer-facing unit/model artifact instead of relying only on prose.

## Evidence Supporting

- `condition_level_statistics.csv` is seed-level.
- `agent_causal_trace.csv` is agent-level and nested.
- `event_taxonomy.json` is event-level and nested.
- The current manifest does not include a statistical-unit audit.

## Required Fix

Add generated artifacts:

1. `statistical_unit_audit.csv`
2. `statistical_model_spec.md`
3. manifest entries
4. tests that verify the audit marks seed/run as the inferential unit and agent rows as nested

## Success Criteria

- The package explicitly marks seed/run as independent.
- Agent/event/tick layers are marked as nested/descriptive unless modeled hierarchically.
- The model spec states planned models for binary, continuous, time-to-event, and agent-level analyses.
- Tests protect the artifact.

## Confidence Before Fix

High. This is a classic reviewer concern for simulation papers.
