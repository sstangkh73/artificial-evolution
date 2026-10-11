# Before Fix Report: Ablation and Control Matrix

Date: 2026-06-26

## Objective

Fix journal-readiness item 4: make the publication package explicitly audit which control and ablation conditions exist and which are still missing.

## Research Risk

Experience-based learning claims require controls. Without them, reviewers can argue that observed behavior is explained by:

- food abundance or spatial hotspots,
- body morphology differences,
- scripted hunger rules,
- sensory access,
- social clustering,
- random seed luck,
- tuned ecology.

The current publication package exports conditions, but it does not classify their experimental role.

## Current State

`conditions.csv` records condition metadata such as:

- `condition_id`,
- label and question,
- body index,
- initial population,
- founder mode,
- spawn strategy,
- `env_kwargs`.

This is necessary, but not sufficient for review. A reader still has to infer whether a row is a baseline, treatment, robustness probe, sensory control, social control, or missing ablation.

## Hypothesis

The journal package becomes stronger if every condition is mapped to an interpretation role and the missing ablations are named in a machine-readable and human-readable artifact.

## Evidence Supporting

- `_publication_conditions()` includes baseline and treatment-like conditions.
- `_world_discovery_conditions()` includes a sensory control.
- Current exports do not state whether memory-disabled, value-blind, social-isolation, hunger-decoupled, or hotspot controls are present.
- Current exports do not state which claim each condition can or cannot support.

## Alternative Explanations

- A methods section could describe controls manually. That is weaker because condition-role classification should stay coupled to the generated package.
- Some controls may exist in separate scripts. They still need to be visible in the package used for submission.

## Required Fix

Add control and ablation artifacts:

1. `control_matrix.csv` with one row per condition and a classified role.
2. `ablation_control_plan.md` with required controls, current coverage, and interpretation limits.
3. Manifest entries and figure-source data for the condition role matrix.
4. Tests that verify known condition names are classified as baseline/control/treatment/stress where appropriate.

## Success Criteria

- Reviewers can see which conditions are controls without reading Python code.
- Missing ablations are explicitly marked as missing instead of hidden.
- The package states interpretation limits for each condition role.
- Tests cover the classifier and manifest entries.

## Failure Criteria

- Controls remain implicit in condition names only.
- Missing controls are not exported.
- The package overinterprets treatment conditions as causal proof without ablations.

## Confidence Before Fix

High. This is not primarily a simulation bug; it is an experimental-design packaging gap.
