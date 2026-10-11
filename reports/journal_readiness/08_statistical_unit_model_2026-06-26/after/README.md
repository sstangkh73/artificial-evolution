# After Fix Report: Statistical Unit and Model Specification

Date: 2026-06-26

## Objective

Complete journal-readiness item 8 by adding a statistical-unit audit and model specification that prevents pseudoreplication.

## What Changed

`simulation/publication_artifacts.py` now writes:

- `statistical_unit_audit.csv`
- `statistical_model_spec.md`
- manifest keys:
  - `statistical_unit_audit_csv`
  - `statistical_model_spec_md`
- figure source:
  - `figure_14_statistical_unit_audit.csv`

## Before

The analysis plan said seed/run is the independent unit, but the package did not quantify each data layer's inferential role.

## After

The package now marks:

- replicate outcomes as `seed_run` and valid for condition-level inference,
- agent causal traces as nested within seed/run,
- event logs as nested within seed/run and agent,
- tick panels as longitudinal observations nested within seed/run.

The model spec states planned families for:

- binary outcomes,
- continuous outcomes,
- time-to-event outcomes,
- agent-level mechanism traces,
- event counts.

## Evidence Added

New tests verify that:

- replicate outcomes use `seed_run` as the independent unit,
- agent rows are `not_independent`,
- agent rows are nested within `seed_run`,
- the model spec warns not to count agent rows as independent replicates.

## Validation

Commands run:

```text
python -m unittest tests.test_publication_journal_readiness_artifacts
python -m unittest discover -s tests
python -m compileall main.py simulation tests
```

Result:

```text
Ran 34 tests
OK
```

## Remaining Risk

The artifact specifies correct units and model families, but it does not replace a full confirmatory statistical analysis after new 30-seed batches are generated.

## Journal Verdict

Fixed. The package now carries an explicit pseudoreplication guard.
