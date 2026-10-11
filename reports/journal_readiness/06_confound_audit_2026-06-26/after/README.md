# After Fix Report: Confound Audit

Date: 2026-06-26

## Objective

Complete journal-readiness item 6 by exporting an automatic confound audit for each publication package.

## What Changed

`simulation/publication_artifacts.py` now writes:

- `confound_audit.csv`
- `confound_audit.md`
- manifest keys:
  - `confound_audit_csv`
  - `confound_audit_md`
- figure source:
  - `figure_12_confound_audit.csv`

The audit uses:

- condition metadata,
- replicate-level summaries,
- structured event logs,
- per-agent causal traces,
- control-matrix coverage.

## Before

The package exported event counts and condition statistics, but did not convert them into explicit alternative-explanation flags. A reviewer still had to manually ask whether results could be explained by:

- hunger-triggered seed dropping,
- social clustering,
- immortal agents,
- tuned ecology,
- resource hotspots,
- missing paired controls.

## After

The package now emits per-condition confound fields including:

- `seed_drop_events`,
- `critical_hunger_seed_drops`,
- `critical_hunger_seed_drop_fraction`,
- `hunger_confound_status`,
- `social_contact_rate_mean`,
- `social_confound_status`,
- `immortal_agent_fraction`,
- `immortal_confound_status`,
- `tuned_ecology_keys_json`,
- `ecology_confound_status`,
- `possible_hotspot_bias`,
- `hotspot_confound_status`,
- package-level control coverage flags,
- `overall_confound_verdict`,
- `interpretation_limit`.

## Evidence Added

New tests verify that synthetic high-risk evidence is flagged correctly:

- critical-hunger seed drops become `high_risk_hunger_dominant_missing_control`,
- nonzero social contact without a social control becomes `possible_social_clustering_missing_control`,
- immortal agents become `high_risk_immortal_agents_present`,
- the overall condition verdict becomes `high_risk`.

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

This audit flags confounds from available fields. It cannot clear a confound unless the relevant control condition and event evidence exist. In particular, hotspot and social-transmission claims still need targeted controls before the manuscript can make strong causal claims.

## Journal Verdict

This item is fixed as a reviewer-facing audit. The package is now much more honest and defensible because confounds are surfaced automatically rather than hidden in raw logs.
