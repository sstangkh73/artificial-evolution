# Code-Version Audit for E1–E6 and T2-RB

**Scope:** causal mechanisms and launch code used by the experiments in the article.

## Why several revisions appear

The studies were executed in sequence. Each batch recorded a clean Git revision, but later studies required new experimental controls. Cross-study code drift could therefore threaten interpretation unless the changes are identified. The article's statistical contrasts remain within a matched-seed batch and a single revision; no primary causal estimate subtracts outcomes produced by different revisions.

## Recorded revisions

| Experiment | Clean run revision | Runs | Relevant change relative to the preceding run revision |
|---|---|---:|---|
| E1 | `9835d7287c556420b28be0f6b357abd5737b6cda` | 80 | Baseline for this audit |
| E2 | `52cd6fbda83dbcff3c43171c8c86f1b99ac89ae1` | 160 | Added the opt-in B4 avoidance oracle and refactored toxin-excess calculation into a shared pure function |
| E3 | `510d9eb74e674afc02ce58f5bd4ca4a3bcdfde81` | 60 | No change to the focal agent, body, environment, metabolism, run-loop, or driver files since E2 |
| E4 | `f2026a615ebb8c4e8180a431cae5452415c78981` | 20 | No change to those focal mechanism files since E3/E5 |
| E5 | `510d9eb74e674afc02ce58f5bd4ca4a3bcdfde81` | 60 | Same focal code revision as E3 |
| E6 | `3f1af32f9e37655ed9bee5462526921eff226c8a` | 450 | Added the opt-in raw-fruit-only energy multiplier used by E6 |
| T2-RB | `3f1af32f9e37655ed9bee5462526921eff226c8a` | 150 | Same frozen revision as E6; multiplier remained at its default 1.0 |

The 980 row total and every ordered launch-flag sequence were checked by `scripts/export_experiment_parameter_matrix.py`. Runtime and revision fields are preserved in `experiment_design_provenance.csv`.

## Mechanism-file diffs

The audit covered:

- `agents/agent.py`
- `agents/body.py`
- `world/environment.py`
- `world/metabolism.py`
- `scripts/run_long_emergence_watch.py`
- `scripts/food_value_study_driver.py`

From E1 to E2, the only focal behavior addition was `diet_oracle_enabled`. It defaults to false. For non-oracle arms, the toxin calculation was split into `_realised_toxin_excess` and `_charge_toxin` without changing the order or formulas applied to a consumed bite. E2's B4 arms explicitly enable the new branch.

There were no changes to the six audited files between the E2 and E3/E5 revisions, or between the E3/E5 and E4 revisions. The intervening commits recorded specifications, analyses, and reports.

From E4 to the frozen E6/T2-RB revision, the only focal mechanism addition was `raw_fruit_energy_multiplier`. It defaults to 1.0 and is applied after the global food-energy multiplier only for `raw_fruit`. E6 explicitly varied it; T2-RB used 1.0. This addition does not retroactively alter E1–E5 outputs.

## Interpretation boundary

E1, E2, E3, E4, and E5 answer different registered questions, so their numerical outcomes are not treated as a single pooled effect. Each arm contrast within those studies shares its revision, seeds, horizon, and base specification. E6 and T2-RB were separately frozen and analyzed at one tag. The version history therefore supports the within-study causal comparisons used in the article, while any narrative comparison of effect sizes across studies remains descriptive.

## Reproduction commands for the audit

```text
git diff 9835d7287c556420b28be0f6b357abd5737b6cda..52cd6fbda83dbcff3c43171c8c86f1b99ac89ae1 -- agents/agent.py agents/body.py world/environment.py world/metabolism.py scripts/run_long_emergence_watch.py scripts/food_value_study_driver.py
git diff 52cd6fbda83dbcff3c43171c8c86f1b99ac89ae1..510d9eb74e674afc02ce58f5bd4ca4a3bcdfde81 -- agents/agent.py agents/body.py world/environment.py world/metabolism.py scripts/run_long_emergence_watch.py scripts/food_value_study_driver.py
git diff 510d9eb74e674afc02ce58f5bd4ca4a3bcdfde81..f2026a615ebb8c4e8180a431cae5452415c78981 -- agents/agent.py agents/body.py world/environment.py world/metabolism.py scripts/run_long_emergence_watch.py scripts/food_value_study_driver.py
git diff f2026a615ebb8c4e8180a431cae5452415c78981..3f1af32f9e37655ed9bee5462526921eff226c8a -- agents/agent.py agents/body.py world/environment.py world/metabolism.py scripts/run_long_emergence_watch.py scripts/food_value_study_driver.py
```
