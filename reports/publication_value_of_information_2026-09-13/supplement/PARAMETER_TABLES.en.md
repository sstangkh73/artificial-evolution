# Experiment Parameter Tables — E1–E6 and T2-RB

**Generated file.** Run `python scripts/export_experiment_parameter_matrix.py` from the repository root.

These tables report the planned launch configuration preserved in each archived or frozen specification. The companion CSV files combine those explicit settings with defaults parsed from `scripts/food_value_study_driver.py` at the clean Git revision recorded by each run batch. Operational output paths are excluded. Per-run JSON dumps remain the authority for values realized during execution.

## Design and provenance

| Experiment | Ticks | Seeds | Arms | Planned runs | Verified rows | Run revision | Specification | Preregistration commit/tag |
|---|---:|---:|---:|---:|---:|---|---|---|
| E1 | 400 | 20 (20260930–20260949) | 4 | 80 | 80 | `9835d7287c556420b28be0f6b357abd5737b6cda` | `reports/e1_20260912/E1_runs.json` | `fd758ce6854d8a77a0df420222e5a5a22fe13d4c` |
| E2 | 400 | 20 (20260930–20260949) | 8 | 160 | 160 | `52cd6fbda83dbcff3c43171c8c86f1b99ac89ae1` | `reports/e2_20260913/E2_runs.json` | `fd758ce6854d8a77a0df420222e5a5a22fe13d4c` |
| E3 | 400 | 20 (20260930–20260949) | 3 | 60 | 60 | `510d9eb74e674afc02ce58f5bd4ca4a3bcdfde81` | `reports/e3_20260913/E3_runs.json` | `fd758ce6854d8a77a0df420222e5a5a22fe13d4c` |
| E4 | 3000 | 10 (20260610–20260619) | 2 | 20 | 20 | `f2026a615ebb8c4e8180a431cae5452415c78981` | `reports/e4_20260913/E4_runs.json` | `not recorded in spec` |
| E5 | 400 | 20 (20260930–20260949) | 3 | 60 | 60 | `510d9eb74e674afc02ce58f5bd4ca4a3bcdfde81` | `reports/e5_20260913/E5_runs.json` | `fd758ce6854d8a77a0df420222e5a5a22fe13d4c` |
| E6 | 800 | 30 (20260970–20260999) | 15 | 450 | 450 | `3f1af32f9e37655ed9bee5462526921eff226c8a` | `reports/prereg/E6_representation_payoff_spec.json` | `prereg-resource-age-2026-09-14` |
| T2-RB | 400 | 50 (20261000–20261049) | 3 | 150 | 150 | `3f1af32f9e37655ed9bee5462526921eff226c8a` | `reports/prereg/T2_RB_replication_spec.json` | `prereg-resource-age-2026-09-14` |

## Explicit shared settings

### E1

`--model v2 --body 37 --population 50 --founder-age-spread 1 --world 100 --natural-seed-rain 12 --initial-plants 2500 --food-detection-threshold 0.01 --vision-horizon 200 --value-learning --pickiness 0.6 --starvation-energy 6 --mortal --starvation-death --aging --toxic-food 20 --toxin-acute-penalty 50 --toxin-damage-coeff 5 --encounter-telemetry --encounter-age-bin 5 --encounter-age-max-bin 60 --agent-outcome-telemetry --drain-mult 0.2`

### E2

`--model v2 --body 37 --population 50 --founder-age-spread 1 --world 100 --natural-seed-rain 12 --initial-plants 2500 --food-detection-threshold 0.01 --vision-horizon 200 --value-learning --pickiness 0.6 --starvation-energy 6 --mortal --starvation-death --aging --toxic-food 20 --toxin-acute-penalty 50 --toxin-damage-coeff 5 --encounter-telemetry --encounter-age-bin 5 --encounter-age-max-bin 60 --agent-outcome-telemetry --drain-mult 0.2`

### E3

`--model v2 --body 37 --population 50 --founder-age-spread 1 --world 100 --natural-seed-rain 12 --initial-plants 2500 --food-detection-threshold 0.01 --vision-horizon 200 --value-learning --pickiness 0.6 --starvation-energy 6 --mortal --starvation-death --aging --toxic-food 20 --toxin-acute-penalty 50 --toxin-damage-coeff 5 --encounter-telemetry --encounter-age-bin 5 --encounter-age-max-bin 60 --agent-outcome-telemetry --drain-mult 0.2 --founder-toxin-tolerance-spread 0.15`

### E4

`--model v2 --body 37 --drain-mult 0.05 --food-energy-mult 50 --low-value-food 6 --encounter-telemetry --encounter-age-bin 5 --encounter-age-max-bin 60 --agent-outcome-telemetry`

### E5

`--model v2 --body 37 --population 50 --founder-age-spread 1 --world 100 --natural-seed-rain 12 --initial-plants 2500 --food-detection-threshold 0.01 --vision-horizon 200 --value-learning --pickiness 0.6 --starvation-energy 6 --mortal --starvation-death --aging --toxic-food 20 --toxin-acute-penalty 50 --toxin-damage-coeff 5 --encounter-telemetry --encounter-age-bin 5 --encounter-age-max-bin 60 --agent-outcome-telemetry --drain-mult 0.5`

### E6

`--model v2 --body 37 --population 50 --founder-age-spread 1 --world 100 --natural-seed-rain 12 --initial-plants 2500 --food-detection-threshold 0.01 --vision-horizon 200 --value-learning --pickiness 0.6 --starvation-energy 6 --mortal --starvation-death --aging --toxic-food 20 --toxin-acute-penalty 50 --toxin-damage-coeff 5 --toxin-safe-window-start 40 --toxin-safe-window-end 80 --encounter-telemetry --encounter-age-bin 5 --encounter-age-max-bin 60 --agent-outcome-telemetry --drain-mult 0.2`

### T2-RB

`--model v2 --body 37 --population 50 --founder-age-spread 1 --world 100 --natural-seed-rain 12 --initial-plants 2500 --food-detection-threshold 0.01 --vision-horizon 200 --value-learning --pickiness 0.6 --starvation-energy 6 --mortal --starvation-death --aging --toxic-food 20 --toxin-acute-penalty 50 --toxin-damage-coeff 5 --encounter-telemetry --encounter-age-bin 5 --encounter-age-max-bin 60 --agent-outcome-telemetry --drain-mult 0.5`

## Arm-specific changes from each experiment base

| Experiment | Arm | Parameter | Value |
|---|---|---|---|
| E1 | `A0` | `toxin_potency_scale` | `0` |
| E1 | `A1` | `toxin_potency_scale` | `1` |
| E1 | `A2` | `toxin_detox_ticks` | `120` |
| E1 | `A3` | `toxin_potency_scale` | `0.757811` |
| E2 | `B1_M` | `toxin_detox_ticks` | `120` |
| E2 | `B1_M` | `food_value_key_mode` | `type` |
| E2 | `B2_M` | `toxin_detox_ticks` | `120` |
| E2 | `B2_M` | `food_value_key_mode` | `type_age` |
| E2 | `B2_M` | `food_value_age_bin` | `20` |
| E2 | `B2_M` | `food_value_age_max_bin` | `8` |
| E2 | `B3_M` | `toxin_detox_ticks` | `120` |
| E2 | `B3_M` | `food_value_key_mode` | `type_sham` |
| E2 | `B3_M` | `food_value_age_bin` | `20` |
| E2 | `B3_M` | `food_value_age_max_bin` | `8` |
| E2 | `B4_M` | `toxin_detox_ticks` | `120` |
| E2 | `B4_M` | `diet_oracle` | `true` |
| E2 | `B1_W` | `toxin_safe_window_start` | `40` |
| E2 | `B1_W` | `toxin_safe_window_end` | `80` |
| E2 | `B1_W` | `food_value_key_mode` | `type` |
| E2 | `B2_W` | `toxin_safe_window_start` | `40` |
| E2 | `B2_W` | `toxin_safe_window_end` | `80` |
| E2 | `B2_W` | `food_value_key_mode` | `type_age` |
| E2 | `B2_W` | `food_value_age_bin` | `20` |
| E2 | `B2_W` | `food_value_age_max_bin` | `8` |
| E2 | `B3_W` | `toxin_safe_window_start` | `40` |
| E2 | `B3_W` | `toxin_safe_window_end` | `80` |
| E2 | `B3_W` | `food_value_key_mode` | `type_sham` |
| E2 | `B3_W` | `food_value_age_bin` | `20` |
| E2 | `B3_W` | `food_value_age_max_bin` | `8` |
| E2 | `B4_W` | `toxin_safe_window_start` | `40` |
| E2 | `B4_W` | `toxin_safe_window_end` | `80` |
| E2 | `B4_W` | `diet_oracle` | `true` |
| E3 | `A0` | `toxin_potency_scale` | `0` |
| E3 | `A2` | `toxin_detox_ticks` | `120` |
| E3 | `A3` | `toxin_potency_scale` | `0.757811` |
| E4 | `A_no_learning` | `(none)` | `inherits base` |
| E4 | `B_value_learning` | `value_learning` | `true` |
| E5 | `A0` | `toxin_potency_scale` | `0` |
| E5 | `A2` | `toxin_detox_ticks` | `120` |
| E5 | `A3` | `toxin_potency_scale` | `0.757811` |
| E6 | `V10_B1` | `raw_fruit_energy_mult` | `1.0` |
| E6 | `V10_B1` | `food_value_key_mode` | `type` |
| E6 | `V10_B2` | `raw_fruit_energy_mult` | `1.0` |
| E6 | `V10_B2` | `food_value_key_mode` | `type_age` |
| E6 | `V10_B2` | `food_value_age_bin` | `20` |
| E6 | `V10_B2` | `food_value_age_max_bin` | `8` |
| E6 | `V10_B3` | `raw_fruit_energy_mult` | `1.0` |
| E6 | `V10_B3` | `food_value_key_mode` | `type_sham` |
| E6 | `V10_B3` | `food_value_age_bin` | `20` |
| E6 | `V10_B3` | `food_value_age_max_bin` | `8` |
| E6 | `V08_B1` | `raw_fruit_energy_mult` | `0.8` |
| E6 | `V08_B1` | `food_value_key_mode` | `type` |
| E6 | `V08_B2` | `raw_fruit_energy_mult` | `0.8` |
| E6 | `V08_B2` | `food_value_key_mode` | `type_age` |
| E6 | `V08_B2` | `food_value_age_bin` | `20` |
| E6 | `V08_B2` | `food_value_age_max_bin` | `8` |
| E6 | `V08_B3` | `raw_fruit_energy_mult` | `0.8` |
| E6 | `V08_B3` | `food_value_key_mode` | `type_sham` |
| E6 | `V08_B3` | `food_value_age_bin` | `20` |
| E6 | `V08_B3` | `food_value_age_max_bin` | `8` |
| E6 | `V06_B1` | `raw_fruit_energy_mult` | `0.6` |
| E6 | `V06_B1` | `food_value_key_mode` | `type` |
| E6 | `V06_B2` | `raw_fruit_energy_mult` | `0.6` |
| E6 | `V06_B2` | `food_value_key_mode` | `type_age` |
| E6 | `V06_B2` | `food_value_age_bin` | `20` |
| E6 | `V06_B2` | `food_value_age_max_bin` | `8` |
| E6 | `V06_B3` | `raw_fruit_energy_mult` | `0.6` |
| E6 | `V06_B3` | `food_value_key_mode` | `type_sham` |
| E6 | `V06_B3` | `food_value_age_bin` | `20` |
| E6 | `V06_B3` | `food_value_age_max_bin` | `8` |
| E6 | `V05_B1` | `raw_fruit_energy_mult` | `0.5` |
| E6 | `V05_B1` | `food_value_key_mode` | `type` |
| E6 | `V05_B2` | `raw_fruit_energy_mult` | `0.5` |
| E6 | `V05_B2` | `food_value_key_mode` | `type_age` |
| E6 | `V05_B2` | `food_value_age_bin` | `20` |
| E6 | `V05_B2` | `food_value_age_max_bin` | `8` |
| E6 | `V05_B3` | `raw_fruit_energy_mult` | `0.5` |
| E6 | `V05_B3` | `food_value_key_mode` | `type_sham` |
| E6 | `V05_B3` | `food_value_age_bin` | `20` |
| E6 | `V05_B3` | `food_value_age_max_bin` | `8` |
| E6 | `V04_B1` | `raw_fruit_energy_mult` | `0.4` |
| E6 | `V04_B1` | `food_value_key_mode` | `type` |
| E6 | `V04_B2` | `raw_fruit_energy_mult` | `0.4` |
| E6 | `V04_B2` | `food_value_key_mode` | `type_age` |
| E6 | `V04_B2` | `food_value_age_bin` | `20` |
| E6 | `V04_B2` | `food_value_age_max_bin` | `8` |
| E6 | `V04_B3` | `raw_fruit_energy_mult` | `0.4` |
| E6 | `V04_B3` | `food_value_key_mode` | `type_sham` |
| E6 | `V04_B3` | `food_value_age_bin` | `20` |
| E6 | `V04_B3` | `food_value_age_max_bin` | `8` |
| T2-RB | `A2` | `toxin_detox_ticks` | `120` |
| T2-RB | `A3O` | `toxin_potency_scale` | `0.757811` |
| T2-RB | `A3R` | `toxin_potency_scale` | `0.7506672222220914` |

## Machine-readable tables

- `experiment_parameter_matrix.csv`: one row per arm, including design fields and every effective scientific driver parameter.
- `experiment_parameter_origins.csv`: one row per arm and parameter, with origin marked as `driver_default`, `base_spec`, or `arm_spec`.
- `experiment_design_provenance.csv`: seed ranges, horizons, run counts, specification locations, and freeze identifiers.

The exporter also verifies every archived result row against the expected arm, seed, horizon, and ordered launch-flag sequence. The seed range notation is a compact description of the archived seed list; the exporter checks uniqueness but does not assume contiguity. Boolean driver flags are written as `true` or `false`, `null` denotes an argparse default of `None`, and a blank wide-matrix cell means that the parameter was absent from that run revision's driver.
