# Before Fix Report: Claim Scope and Overclaim Guard

Date: 2026-06-26

## Objective

Fix journal-readiness item 3: narrow the paper claims so the exported publication package distinguishes supported findings from unproven interpretations.

## Research Risk

The project now has evidence for experience-sensitive agent behavior, but a journal reviewer will reject broad claims if the package does not explicitly separate:

- individual experience-based learning,
- aggregate ecological effects,
- social transmission,
- intentional farming,
- language-like communication,
- open-ended evolution.

The current system can accidentally sound stronger than the evidence because the publication package exports methods, outcomes, and negative results, but not a claim-scope contract.

## Current State

`simulation/publication_artifacts.py` writes:

- `statistical_analysis_plan.md`,
- `methods_full.md`,
- `negative_results.md`,
- figure source data,
- condition and replicate tables.

These are useful, but none of them explicitly state:

- what claims are allowed,
- what claims are prohibited,
- what evidence is required before upgrading a claim.

## Hypothesis

The paper is closer to publishable if the package itself contains a reviewer-facing claim-scope artifact that prevents accidental overclaiming.

## Evidence Supporting

- The current artifact manifest has no `claim_scope` entry.
- Existing outputs can show behavior and outcomes, but they do not state that social communication, intentional agriculture, and language remain unproven.
- Agent-level and condition-level signals can be mistaken for stronger cognitive claims unless the paper locks terminology.

## Alternative Explanations

- The manuscript text could narrow claims manually. That is weaker because tables and derived figures may circulate independently.
- A reviewer may infer caution from limitations text. That still leaves ambiguity in the exported data package.

## Required Fix

Add a publication artifact that states:

1. permitted claims,
2. prohibited claims,
3. evidence needed to upgrade each prohibited claim,
4. analysis boundaries for paper writing.

The artifact should be listed in `publication_manifest.json` and covered by tests so future changes cannot remove the guard silently.

## Success Criteria

- Publication packages include `claim_scope.md`.
- The manifest exposes the claim-scope artifact.
- The text explicitly permits only defensible claims.
- The text explicitly blocks intentional farming, social transmission, language, and open-ended evolution claims until stronger evidence exists.
- Tests assert that the guard remains present.

## Failure Criteria

- Claim limits exist only in prose outside the exported package.
- The package can be interpreted as claiming social learning or intentional agriculture without direct controls.
- Future edits can remove the claim guard without a failing test.

## Confidence Before Fix

High that this is a real journal-readiness gap. The science is stronger when the artifact package itself prevents overinterpretation.
