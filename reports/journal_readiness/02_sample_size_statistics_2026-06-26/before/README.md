# Before Fix Report: Sample Size and Statistical Reporting

Date: 2026-06-26

## Objective

Fix journal-readiness item 2: move publication-oriented experiments from small/smoke sample sizes toward journal-grade replication and statistical reporting.

## Research Risk

The current evidence can support exploratory claims, but journal review will likely reject or heavily qualify results if:

- each condition has too few independent seed-level replicates,
- uncertainty is reported only qualitatively,
- continuous outcomes lack variance and confidence intervals,
- effect sizes are absent,
- agent-level rows are treated as independent when the true independent unit is seed/run.

## Current State

### Sample Size

`main.py` currently sets:

```python
parser.add_argument("--study-seeds", type=int, default=12)
```

This is better than a smoke test but below the intended journal-grade floor of 20-30 independent seed-level replicates per condition.

### Publication Package

`simulation/publication_artifacts.py` already writes:

- `replicate_index.csv`,
- `primary_outcomes.csv`,
- `secondary_outcomes.csv`,
- `condition_level_statistics.csv`,
- `statistical_analysis_plan.md`,
- figure source data.

This is a strong foundation. However, the current condition-level statistics mostly report means, medians, IQRs, and Wilson intervals for selected binary outcomes. Continuous metrics do not yet include:

- sample standard deviation,
- standard error,
- 95% confidence intervals,
- standardized effect sizes versus a reference condition,
- explicit sample-size audit status.

## Hypothesis

The publication path is structurally close to journal-ready, but underreports uncertainty and does not enforce or flag journal-grade seed counts.

## Evidence Supporting

- Default publication/study seed count is 12, below the planned minimum of 20.
- `condition_level_statistics.csv` reports `replicates`, binary Wilson intervals, means, medians, and IQRs, but not continuous 95% confidence intervals.
- No separate effect-size table exists in the publication manifest.
- No sample-size audit file exists to classify each condition as underpowered or journal-grade.

## Alternative Explanations

- Existing reports may include some manually computed statistics, but journal submission needs the package itself to produce them reproducibly from raw replicate rows.
- Some experiments are expensive, so defaulting all modes to 30 seeds may be slower. This is acceptable for journal-oriented batch modes, while developers can still pass a smaller `--study-seeds` value for pilot work.

## Required Fix

1. Raise the default study/batch seed count to a journal-oriented value.
2. Add sample-size status to exported condition statistics.
3. Add continuous SD/SE/95% CI fields.
4. Add effect-size output versus a reference condition.
5. Add a sample-size audit document to the publication package.
6. Add tests using synthetic replicate data so the statistics path is protected without running long simulations.

## Success Criteria

- Default study/batch seed count is at least 20.
- Publication artifacts include a sample-size audit.
- Condition statistics include SD, SE, and 95% CI for key continuous outcomes.
- Publication artifacts include effect sizes for key continuous metrics versus a reference condition.
- Tests verify journal-grade and underpowered sample-size classifications.

## Failure Criteria

- The package still defaults to fewer than 20 seeds for study/batch modes.
- Continuous metrics still lack confidence intervals.
- Effect-size output is missing.
- Sample-size status is implicit or undocumented.

## Confidence Before Fix

High that this is a genuine journal-readiness gap.

The current package is good exploratory infrastructure, but it needs stronger statistical output before it can carry a hard journal submission.
