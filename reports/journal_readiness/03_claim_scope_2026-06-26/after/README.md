# After Fix Report: Claim Scope and Overclaim Guard

Date: 2026-06-26

## Objective

Complete journal-readiness item 3 by adding a generated claim-scope guard to every publication package.

## What Changed

`simulation/publication_artifacts.py` now writes:

- `claim_scope.md`
- manifest key: `claim_scope_md`

The generated claim-scope artifact defines:

- permitted claims,
- prohibited claims,
- evidence required to upgrade each stronger claim,
- writing boundaries for manuscript language.

The statistical analysis plan also now instructs authors to keep claim language within `claim_scope.md`.

## Before

The publication package contained methods, statistics, figures, and negative results, but no explicit claim boundary. A reader could overinterpret aggregate evidence as:

- intentional farming,
- social transmission,
- language-like communication,
- planning,
- open-ended evolution.

Those interpretations were not automatically blocked by the artifact package.

## After

The package now explicitly permits only defensible claims such as:

- experience-sensitive behavior when same-agent traces exist,
- seed-level condition differences when sample size is adequate,
- ecological feedback when event logs support the chain.

It explicitly blocks stronger claims without additional evidence:

- intentional farming,
- social transmission,
- language or symbolic communication,
- open-ended evolution,
- planning or goal understanding from aggregate outcomes alone.

## Evidence Added

New test coverage in `tests/test_publication_journal_readiness_artifacts.py` verifies that:

- `claim_scope_md` is exported in the manifest,
- the claim-scope text blocks intentional farming,
- the text blocks social transmission,
- the text blocks language claims,
- the text blocks open-ended evolution claims.

## Validation

Commands run:

```text
python -m unittest tests.test_publication_journal_readiness_artifacts
python -m unittest discover -s tests
python -m compileall main.py simulation tests
```

Result:

```text
Ran 32 tests
OK
```

## Remaining Risk

This fix prevents overclaiming in generated packages. It does not prove the stronger claims. To upgrade the paper's language, future experiments still need the evidence listed in `claim_scope.md`.

## Journal Verdict

This item is fixed at the artifact and reporting level. The project is now safer to frame as a cautious journal paper because the package itself constrains the manuscript's claims.
