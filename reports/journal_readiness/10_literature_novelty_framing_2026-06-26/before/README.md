# Before Fix Report: Literature and Novelty Framing

Date: 2026-06-26

## Objective

Fix journal-readiness item 10: export a novelty and literature-framing artifact that states the paper's contribution without overstating it.

## Research Risk

A journal paper needs a clear contribution relative to existing fields. Without a framing artifact, the manuscript may drift between:

- artificial life,
- embodied agents,
- reinforcement learning,
- ecological simulation,
- open-ended evolution,
- social learning.

That can make the novelty vague or invite overclaiming.

## Current State

The project has reports discussing AI papers and positioning, and `claim_scope.md` now limits overclaims. However, the publication package itself does not include a concise novelty frame, literature-gap map, or claim-to-evidence table.

## Hypothesis

The publication package becomes more journal-ready if it includes a stable novelty frame that tells authors and reviewers what the work is and is not claiming.

## Evidence Supporting

- `claim_scope.md` limits claims but does not map them to literature domains.
- `methods_full.md` describes the package but does not state novelty.
- External reports exist, but they are not bundled with each publication package.

## Required Fix

Add generated artifacts:

1. `novelty_framing.md`
2. `claim_evidence_map.csv`
3. manifest entries and figure-source data
4. tests that verify the contribution, boundaries, and evidence requirements are exported

## Success Criteria

- The paper's main contribution is explicit.
- Literature-adjacent domains are named without pretending full coverage.
- Each claim level maps to required evidence.
- Stronger claims remain classified as future work unless evidence is present.

## Confidence Before Fix

High. This is not just writing polish; it controls how the paper survives peer review.
