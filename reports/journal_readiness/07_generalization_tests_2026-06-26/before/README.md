# Before Fix Report: Generalization Tests

Date: 2026-06-26

## Objective

Fix journal-readiness item 7: make generalization coverage explicit in every publication package.

## Research Risk

Even if a learning effect is real in one condition, a journal reviewer will ask whether it generalizes across:

- random seeds,
- body plans,
- ecology/resource regimes,
- social scale,
- spawn strategies,
- time horizons.

Without an exported generalization audit, the paper can accidentally look like it is claiming a broad phenomenon from a narrow condition.

## Current State

The package exports condition metadata and controls, but does not summarize generalization axes. A reader has to infer coverage from:

- `conditions.csv`,
- `replicate_index.csv`,
- `control_matrix.csv`,
- condition names,
- `env_kwargs`.

## Hypothesis

The publication package becomes more journal-ready if it automatically reports which generalization axes are tested, weak, or missing.

## Evidence Supporting

- Conditions can include multiple bodies, low-food/scarcity environments, and social founder modes.
- The current package does not convert that into a reviewer-facing coverage table.
- Generalization claims remain easy to overstate without an audit.

## Required Fix

Add generated artifacts:

1. `generalization_audit.csv`
2. `generalization_audit.md`
3. manifest entries and figure-source data
4. tests that verify body/ecology/generalization coverage and missing axes are reported

## Success Criteria

- Generalization axes are explicit.
- Each axis has observed levels and a status.
- Weak or missing axes are listed in markdown.
- Manuscript authors can avoid broad claims when coverage is narrow.

## Confidence Before Fix

High that this is a real paper-readiness gap. The raw data may contain generalization evidence, but it is not packaged as such.
