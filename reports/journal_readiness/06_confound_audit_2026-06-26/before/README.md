# Before Fix Report: Confound Audit

Date: 2026-06-26

## Objective

Fix journal-readiness item 6: add an explicit confound audit for hunger, resource hotspots, social clustering, immortal/tuned ecology, and other alternative explanations.

## Research Risk

The current project has promising signals, but reviewers will ask whether the effect is really learning or whether it is driven by:

- hunger-triggered seed dropping,
- agents repeatedly encountering fixed food hotspots,
- social clustering rather than individual learning,
- immortal agents or unusually high founder support,
- ecology tuned to produce plant-food feedback,
- treatment conditions with easier survival budgets.

If these alternatives are not audited in the package, the manuscript will look under-controlled even when the raw logs contain useful evidence.

## Current State

The simulation logs rich events. For example:

- `seed_dropped` events include context and `critical_hunger`.
- food events include source, position, kind, and agent id.
- replicate rows include social-contact and memory proxy rates.
- condition rows include `env_kwargs`, founder mode, spawn strategy, and population settings.

However, the publication package does not yet convert this into a reviewer-facing confound table or verdict.

## Hypothesis

The package becomes journal-stronger if it automatically emits confound flags and interpretation limits, even when the verdict is "not yet controlled".

## Evidence Supporting

- Current `event_taxonomy.json` counts events, but not confound risk.
- Current condition statistics report social contact rate, but not whether social clustering threatens interpretation.
- Current condition metadata contains tuned ecology knobs, but no audit converts them into a warning.
- Immortal agents can exist in the project, but publication package outputs do not audit immortal fraction when agent rows are present.

## Alternative Explanations

- Some confounds may be addressed by separate phase scripts. That still needs to be visible in the package selected for journal submission.
- A limitations section could discuss confounds manually, but an exported audit is more reproducible and harder to accidentally omit.

## Required Fix

Add confound artifacts:

1. `confound_audit.csv` with per-condition risk flags.
2. `confound_audit.md` with reviewer-facing interpretation.
3. Automated checks for hunger-drop dominance, social clustering, immortal fraction, tuned ecology knobs, and missing hotspot/social controls.
4. Manifest entries and tests.

## Success Criteria

- The package flags major confounds directly.
- Missing controls are distinguished from cleared controls.
- Confound verdicts are tied to event rows, agent rows, replicate rows, and condition metadata.
- Tests cover at least hunger confounding and missing-control detection.

## Failure Criteria

- Confounds remain implicit.
- Hunger/social/ecology alternatives are discussed only in prose outside the package.
- The package implies causal certainty when controls are missing.

## Confidence Before Fix

High. This is a core peer-review concern and should be exported as part of every journal-oriented package.
