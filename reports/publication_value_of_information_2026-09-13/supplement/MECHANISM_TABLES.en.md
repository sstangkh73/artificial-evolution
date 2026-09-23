# Supplementary mechanism tables

**Status:** Post hoc descriptive analysis performed after the primary results were known. The frozen confirmatory analyses remain unchanged.

**Inferential unit:** Seed. Founder records were aggregated within each run before arm contrasts.

## Integrity and traceability

- E6 design: 450/450 run cells; no missing or duplicate cells.
- T2-RB design: 150/150 run cells; no missing or duplicate cells.
- The baseline manifest independently verified all 600 raw-dump hashes against the archived checksum list.
- Every manuscript-facing number below is traceable to `derived/mechanism_analysis.json` and its source-data CSV files.

## E6 founder-level mechanisms aggregated by seed

| Energy | Arm | Follow-up | D | P(eat safe) | P(eat toxic) | Fruit meals | Staple meals | Staple accept | Ever skipped staple | Toxin excess | Toxin damage | Starvation | Senescence |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | B1 | 144.239 | -0.080 | 0.329 | 0.409 | 17.211 | 17.525 | 1.000 | 0.000 | 2.066 | 10.331 | 0.761 | 0.186 |
| 4 | B2 | 150.713 | 0.666 | 1.000 | 0.334 | 18.354 | 20.051 | 1.000 | 0.000 | 2.101 | 10.506 | 0.728 | 0.217 |
| 4 | B3 | 156.145 | -0.104 | 0.388 | 0.492 | 19.680 | 23.684 | 1.000 | 0.000 | 2.386 | 11.930 | 0.681 | 0.266 |
| 5 | B1 | 150.314 | -0.082 | 0.320 | 0.402 | 18.175 | 18.365 | 1.000 | 0.000 | 2.178 | 10.892 | 0.721 | 0.217 |
| 5 | B2 | 156.063 | 0.684 | 1.000 | 0.316 | 18.871 | 20.251 | 1.000 | 0.000 | 2.149 | 10.744 | 0.702 | 0.245 |
| 5 | B3 | 161.639 | -0.112 | 0.356 | 0.469 | 20.183 | 23.965 | 1.000 | 0.000 | 2.446 | 12.229 | 0.629 | 0.300 |
| 6 | B1 | 156.123 | -0.071 | 0.319 | 0.390 | 19.025 | 18.953 | 1.000 | 0.000 | 2.256 | 11.278 | 0.661 | 0.269 |
| 6 | B2 | 160.169 | 0.712 | 1.000 | 0.288 | 19.061 | 20.025 | 1.000 | 0.000 | 2.150 | 10.749 | 0.649 | 0.277 |
| 6 | B3 | 166.309 | -0.109 | 0.338 | 0.447 | 20.822 | 23.660 | 1.000 | 0.000 | 2.518 | 12.588 | 0.591 | 0.332 |
| 8 | B1 | 172.624 | -0.073 | 0.297 | 0.370 | 21.599 | 21.035 | 1.000 | 0.000 | 2.566 | 12.828 | 0.481 | 0.410 |
| 8 | B2 | 171.341 | 0.748 | 1.000 | 0.252 | 20.103 | 19.343 | 1.000 | 0.000 | 2.237 | 11.186 | 0.544 | 0.351 |
| 8 | B3 | 178.991 | -0.097 | 0.290 | 0.387 | 21.655 | 23.578 | 1.000 | 0.000 | 2.614 | 13.070 | 0.465 | 0.434 |
| 10 | B1 | 207.595 | -0.058 | 0.315 | 0.373 | 26.507 | 27.405 | 0.958 | 0.047 | 3.181 | 15.907 | 0.077 | 0.765 |
| 10 | B2 | 207.078 | 0.654 | 1.000 | 0.346 | 25.724 | 22.275 | 0.436 | 0.717 | 2.984 | 14.922 | 0.088 | 0.740 |
| 10 | B3 | 205.713 | -0.097 | 0.326 | 0.423 | 25.447 | 24.008 | 0.563 | 0.540 | 3.093 | 15.466 | 0.081 | 0.742 |

Skip counts are repeated-contact telemetry and must not be interpreted as independent food-item encounters.

## Primary E6 contrast and endpoint dependence

| Energy | B2-B3 follow-up, mean [95% paired t CI] | Paired dz | P(B2 > B3) | Seeds B2 > B3 / B2 < B3 / tied |
|---:|---:|---:|---:|---:|
| 4 | -5.431 [-8.826, -2.037] | -0.597 | 0.333 | 10 / 20 / 0 |
| 5 | -5.576 [-9.403, -1.749] | -0.544 | 0.367 | 11 / 19 / 0 |
| 6 | -6.141 [-9.989, -2.293] | -0.596 | 0.300 | 9 / 21 / 0 |
| 8 | -7.650 [-11.470, -3.830] | -0.748 | 0.167 | 5 / 25 / 0 |
| 10 | 1.365 [-2.122, 4.852] | 0.146 | 0.567 | 17 / 13 / 0 |

The registered mean slope was 0.890 ticks per energy unit (95% CI 0.059 to 1.722). It met the frozen positive-slope decision rule but did not exceed the SESOI of 1 in the post hoc minimum-effect test (one-sided sign-flip p=0.607).

Leaving out energy 10 gave a slope of -0.578 (95% CI -1.853 to 0.696).

At energy 10, 0.6 x 10 = 6 > 5, so a safe-fruit value can raise the relative threshold above the staple. Staple acceptance fell to 0.436 in B2 and 0.563 in B3, while remaining 0.958 in B1; senescence accounted for about 74-76% of founder outcomes in all three arms. The design therefore cannot separate a payoff effect from this policy-regime change and the senescence ceiling.

## T2-RB realized intake and dose

| Arm | Follow-up | Fruit meals | Staple meals | Fruit accept | Staple accept | Toxin excess | Excess/fruit meal | Toxin damage | Starvation | Senescence |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A2 | 159.261 | 27.070 | 34.808 | 0.941 | 0.829 | 1.877 | 0.069 | 9.384 | 0.417 | 0.500 |
| A3O | 166.362 | 28.934 | 40.164 | 1.000 | 1.000 | 2.107 | 0.073 | 10.534 | 0.370 | 0.556 |
| A3R | 167.189 | 29.158 | 40.332 | 1.000 | 1.000 | 2.048 | 0.070 | 10.240 | 0.371 | 0.553 |

All observed A3O/A3R learned fruit-key means were exactly 6 and fruit acceptance was 1.000. A2 received less realized toxin excess than either constant control while also having shorter follow-up. T2-RB therefore compares variable, choice-requiring toxicity with a fixed-payoff control that required no discrimination; it does not isolate hidden versus visible toxicity at equal realized dose.

| Contrast | Follow-up, mean [95% paired t CI] | Paired dz | P(left > right) | Seeds left > right / left < right / tied |
|---|---:|---:|---:|---:|
| A2-A3R | -7.928 [-11.046, -4.810] | -0.720 | 0.240 | 12 / 38 / 0 |
| A2-A3O | -7.102 [-10.218, -3.985] | -0.645 | 0.260 | 13 / 37 / 0 |

## Causal limitation

In post hoc within-arm-by-energy residuals, follow-up correlated with staple meals per follow-up tick (r=0.985), toxin excess per follow-up tick (r=-0.706), fruit meals per follow-up tick (r=-0.621), and toxin excess per fruit meal (r=-0.483). Rates that divide by follow-up can inherit denominator bias; the toxin-per-meal measure does not use follow-up in its denominator. Archived telemetry does not record agent energy at the decision moment, so starvation-override meals cannot be separated. These descriptive associations do not identify a causal path.
