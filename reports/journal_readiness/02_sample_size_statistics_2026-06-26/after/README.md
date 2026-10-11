# After Fix Report: Sample Size and Statistical Reporting

Date: 2026-06-26

## Summary

Journal-oriented study/batch runs now default to 30 seed-level replicates, and publication packages now export sample-size audits, continuous-outcome confidence intervals, and effect-size tables.

This addresses the sample-size/statistical-reporting infrastructure gap. It does not yet generate a new 30-seed scientific dataset; that requires running the configured batch experiments after this change.

## Files Changed

- `main.py`
  - Changed `--study-seeds` default from `12` to `30`.
  - Updated help text to state that 30 is the journal-oriented default.

- `simulation/publication_artifacts.py`
  - Added journal replicate thresholds:
    - minimum: `20`
    - recommended: `30`
  - Added sample-size status:
    - `underpowered`
    - `minimum_journal_grade`
    - `recommended_journal_grade`
  - Added SD, SE, and t-based 95% CI columns for key continuous metrics.
  - Added `condition_effect_sizes.csv` with Hedges g for continuous outcomes and rate differences for binary outcomes.
  - Added `sample_size_audit.md`.
  - Updated the statistical analysis plan to document the seed/run as the independent unit.

- `simulation/runner.py`
  - Added sample-size thresholds and sample-size status to runtime provenance.

- `tests/test_publication_statistics.py`
  - Added synthetic tests for journal-grade and underpowered packages.

- `reports/journal_readiness/02_sample_size_statistics_2026-06-26/before/README.md`
  - Added pre-fix audit report.

- `reports/journal_readiness/02_sample_size_statistics_2026-06-26/after/README.md`
  - Added this post-fix report.

## Validation

### Automated Tests

```text
python -m unittest tests.test_publication_statistics
Ran 2 tests in 0.069s
OK
```

```text
python -m unittest discover -s tests
Ran 29 tests in 0.119s
OK
```

### Compile Check

```text
python -m compileall main.py simulation tests
OK
```

### CLI Check

```text
python main.py --help
--study-seeds STUDY_SEEDS
  Number of seeds to run for study and batch modes; journal-oriented default is 30.
```

## Output Changes

Publication packages now include:

- `condition_level_statistics.csv`
  - replicate count,
  - minimum/recommended journal thresholds,
  - sample-size status,
  - continuous metric means,
  - SD,
  - SE,
  - 95% CI.

- `condition_effect_sizes.csv`
  - reference condition,
  - comparison condition,
  - metric,
  - mean difference,
  - Hedges g for continuous outcomes,
  - rate differences for binary outcomes.

- `sample_size_audit.md`
  - per-condition replicate count,
  - per-condition status,
  - verdict on whether the package is journal-grade for confirmatory inference.

## Success Criteria Check

- Default study/batch seed count is at least 20: passed (`30`).
- Publication artifacts include a sample-size audit: passed.
- Condition statistics include SD, SE, and 95% CI: passed.
- Publication artifacts include effect sizes: passed.
- Tests verify journal-grade and underpowered classifications: passed.

## Remaining Limitations

This is an infrastructure fix. It does not retroactively upgrade old results.

To claim the old paper is journal-ready, the core experiments must still be rerun after the seed-independence fix and this sample-size/statistics upgrade:

- 30 seeds per condition for the paper-core experiments,
- frozen condition/config registry,
- archived raw run manifests,
- exported publication package,
- final manuscript tables regenerated from the new package.

## Recommended Next Step

Run the fixed publication batch with:

```text
python main.py --mode publication-batch --seed 20260610 --study-seeds 30 --change-note "Journal replication batch after seed independence fix"
```

Use a smaller `--study-seeds` only for pilot/debug runs; such packages will be flagged as `underpowered`.

## Confidence After Fix

High confidence that the publication artifact path now supports journal-grade sample-size reporting.

Medium confidence that this is sufficient for reviewer-facing statistics, because full confirmatory reruns have not yet been executed under the new defaults.
