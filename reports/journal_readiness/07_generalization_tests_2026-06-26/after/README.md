# After Fix Report: Generalization Tests

Date: 2026-06-26

## Objective

Complete journal-readiness item 7 by adding explicit generalization coverage artifacts to every publication package.

## What Changed

`simulation/publication_artifacts.py` now writes:

- `generalization_audit.csv`
- `generalization_audit.md`
- manifest keys:
  - `generalization_audit_csv`
  - `generalization_audit_md`
- figure source:
  - `figure_13_generalization_audit.csv`

## Before

Generalization coverage was implicit. Reviewers had to infer coverage from condition names, body indices, `env_kwargs`, founder modes, and spawn strategies.

## After

The package now audits these axes:

- seed replication,
- body plan,
- ecology/resource regime,
- social scale,
- spawn strategy,
- time horizon,
- control-role coverage.

Each axis reports:

- observed levels,
- required minimum,
- status,
- interpretation limit.

## Evidence Added

New tests verify that:

- the manifest exports the generalization audit,
- multiple body plans produce body-plan coverage,
- default plus modified ecology produces ecology coverage.

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

This fix audits generalization coverage. It does not itself create new generalization runs. Axes marked weak must still be treated as limitations until new batches are run.

## Journal Verdict

Fixed at the publication-package level. Broad claims now have an explicit coverage gate.
