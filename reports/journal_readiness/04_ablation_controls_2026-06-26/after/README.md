# After Fix Report: Ablation and Control Matrix

Date: 2026-06-26

## Objective

Complete journal-readiness item 4 by exporting explicit control and ablation coverage for each publication package.

## What Changed

`simulation/publication_artifacts.py` now writes:

- `control_matrix.csv`
- `ablation_control_plan.md`
- manifest keys:
  - `control_matrix_csv`
  - `ablation_control_plan_md`
- figure source:
  - `figure_10_control_matrix.csv`

Each condition is classified into:

- `control_family`,
- `learning_control_role`,
- `tests_against`,
- `interpretation_limit`.

## Before

Conditions were listed in `conditions.csv`, but their experimental role had to be inferred from names and source code. The package did not explicitly state whether a condition was:

- a baseline,
- sensory control,
- stress/generalization control,
- treatment condition,
- missing ablation.

Missing controls were also not listed.

## After

The package now classifies current conditions and generates a required-control checklist. The checklist includes:

- baseline/default-world reference,
- sensory access control,
- ecology robustness or transfer control,
- memory-disabled or memory-shuffled ablation,
- value-blind or no-learning diet ablation,
- random movement/action baseline,
- social isolation/exposure control,
- hunger-decoupled seed-drop control,
- spatial hotspot or shuffled-food control.

If a control family is absent, the generated plan marks it as `missing` instead of leaving it implicit.

## Evidence Added

New tests verify that:

- `control_matrix_csv` is exported,
- `ablation_control_plan_md` is exported,
- `baseline_body_8` is classified as `reference_baseline`,
- `sensory_control_body_99` is classified as `sensory_access_control`,
- missing memory ablations are explicitly reported as missing.

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

This fix does not create every missing ablation experiment. It makes the absence visible and prevents the publication package from implying causal certainty when paired controls are not present.

## Journal Verdict

This item is fixed as an experimental-design audit. The next research work is to run the missing controls that the package now names.
