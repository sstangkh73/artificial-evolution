# Correct State Information Is Not Enough: Discrimination and Survival Diverge in a Toxic-Safe-Toxic Artificial Ecology

**Manuscript type:** Article

**Target journal:** *Artificial Life* (author instructions checked September 14, 2026; final requirements must be rechecked at submission)

**Author:** Chisanupong Injun
**Affiliation:** Deebuk Phangnga Wittayayon School
**Postal address:** Phang Nga 82000, Thailand
**Corresponding author:** Chisanupong Injun; chisanupong.injun@gmail.com
**ORCID:** https://orcid.org/0009-0000-2979-1916
## Abstract

Artificial foragers can learn from post-ingestive outcomes while failing when one perceptual category combines states that require different actions. In an internally frozen 450-run experiment using a toxic-safe-toxic resource-age profile, an age-indexed value key restored safe-versus-toxic discrimination across five energies (mean discrimination 0.654-0.748). Type-only and capacity-matched sham keys showed an unexplained age-blind discrimination offset of up to 0.1. Behavioral accuracy yielded no detected survival advantage over the sham: paired age-key-minus-sham founder follow-up was negative at energies 4-8 (-5.431 to -7.650 ticks) and imprecisely positive at energy 10 (+1.365, 95% CI -2.122 to 4.852). The prespecified seed-level slope was positive (0.890 ticks per energy unit, 95% CI 0.059 to 1.722; two-sided sign-flip p = 0.0365), but a post hoc minimum-effect test did not show that it exceeded the prespecified effect scale of 1 (one-sided p = 0.607), and omitting energy 10 changed the slope to -0.578. At energy 10, the relative decision threshold first exceeded staple value, staple acceptance fell to 0.436 in the age-indexed arm, and senescence accounted for 0.740-0.765 of founder outcomes across arms; payoff, policy-regime change, and a survival ceiling therefore cannot be separated. An earlier control comparison was null, while a 50-seed high-drain replication found shorter follow-up under age-varying toxicity than under constant-potency controls despite lower realized toxin dose. Correct state information was sufficient for discrimination but not for survival value under this fixed learning rule, decision threshold, and resource economy.

**Keywords:** artificial life; value of information; embodied foraging; perceptual aliasing; temporal toxicity; state representation

## 1. Introduction

### 1.1 Problem

Outcome-grounded learning can estimate the average consequence of a food category without representing every state that determines that consequence. When toxicity changes with food age, a type-only estimate combines safe and toxic encounters. This is a form of perceptual aliasing: situations that require different responses are indistinguishable to the decision rule (Chrisman, 1992). An action cannot depend on resource age when age, or a correlated cue, is absent from the decision key.

The existence of this representational limit is established in reinforcement-learning research. Ecological accounts add a second requirement: uncertainty reduction should be evaluated through the decisions and functional consequences it enables (Dall et al., 2005). Formal fitness value further assumes a response chosen to improve long-run fitness (Donaldson-Matasci et al., 2010). Our fixed learner and within-lifetime survival outcome do not satisfy that definition. The empirical question here is narrower: **does resolving the hidden resource state improve survival under a fixed learning and decision policy, or can behavioral accuracy and survival diverge?**

### 1.2 Related work and conceptual boundary

Artificial Life uses synthetic systems to examine living and life-like processes while distinguishing virtual, simulated, embodied, and other forms of ALife (Dorin & Stepney, 2024). The present work is a simulated, embodied artificial ecology: it studies a constructed adaptive mechanism without claiming that the software agents are alive. This placement matters because the causal question concerns an agent-environment organization—perception, memory, action, metabolism, and resource renewal—rather than an algorithm evaluated on a detached reward benchmark.

Two literatures motivate the distinction tested here. In reinforcement learning, perceptual aliasing describes the case in which the same observation corresponds to underlying states that require different actions (Chrisman, 1992). Work on selective perception and hidden state likewise separates the distinctions available to an agent from the memory and learning resources needed to exploit them (McCallum, 1996). Adding memory or a state distinction can make an otherwise unsolvable discrimination available to the policy, but that representational result does not by itself specify the utility of the actions that follow. Our B2-B3 comparison is designed around this narrow point: both learners can maintain the same nominal number of values, while only B2 receives a key aligned with the state that changes the consequence of eating.

The ecology-of-information literature treats information use as part of a decision problem. Dall et al. (2005) distinguish uncertainty from the functional value of reducing it. Donaldson-Matasci et al. (2010) formalize fitness value through the difference between optimized long-run outcomes with and without a cue. Classic foraging theory similarly places item acceptance inside a diet-choice problem whose prediction depends on background opportunities and energetic returns (Stephens & Krebs, 1986). These accounts imply that a more informative observation may be behaviorally effective without guaranteeing a positive outcome for a fixed, bounded policy. The present model makes energetic, ingestion, and opportunity consequences explicit so their joint outcome can be measured rather than assumed; its fixed relative threshold is not claimed to be an optimal-foraging solution.

Feeding can itself couple information acquisition and energetic return. Post-ingestive feedback can condition food preference and intake from the experienced nutritional and toxic consequences of ingestion (Provenza, 1995). Scholz et al. (2017) combined *Caenorhabditis elegans* feeding data with a sequential decision model in which sampling both gathers evidence about food availability and obtains nutrients. Their model produced speed-accuracy and exploration-exploitation trade-offs in a changing environment. Our mechanism is deliberately simpler: agents apply a fixed numerical update to post-ingestive net energy rather than model physiological learning, and B2 receives resource age directly rather than discovering a cue by sampling. The common point is that the informational and energetic consequences of feeding occur through the same action and therefore cannot be evaluated independently.

The toxic-safe-toxic fruit profile is a stylized biological analogy, not a fitted description of a particular species. Fleshy fruits can contain secondary metabolites that alter vertebrate fruit choice, and nutrient-toxin titration experiments show that consumer response depends on both components (Cipollini & Levey, 1997). That evidence motivates treating ripening state, energy, and toxicity jointly; it does not establish the model's exact age profile, coefficients, or thresholds as biologically universal.

Artificial-life models make this separation experimentally accessible because representation, learning, bodies, and resource dynamics can be intervened on independently. Giannakakis et al. (2025) showed that task structure and network bottlenecks alter which local learning rules evolve and how well embodied foragers perform. The present study holds the learner fixed and instead manipulates whether its value key preserves a payoff-relevant resource state. This makes the study a causal test of representational content inside a spatial ecology rather than a proposal for a new reinforcement-learning algorithm.

Several *Artificial Life* studies make the comparison more specific. Bullinaria (2017) modeled how direct and imitative learning interact with life-history evolution, linking learning to population change; the present no-birth experiments isolate within-lifetime valuation and survival. Ha (2019) and Giannakakis et al. (2025) show in different ways that performance depends on the structure supplied to an embodied learner, including morphology, task structure, and network constraints. Borg and Channon (2020) further found that access to social information could alter behavior even when poisonous-food discrimination was no better, a useful precedent for measuring behavioral change separately from task performance. Finally, Gershenson et al. (2020) caution that self-organization claims depend on identifying which organization arises from component interactions. We therefore report the age cue, value key, policy, and ecological payoffs as experimenter-supplied components and reserve the empirical claim for the behavior and survival patterns produced by their interaction.

### 1.3 Contribution

This article makes four bounded contributions:

1. It shows that type-only valuation cannot produce age-conditional discrimination when fruit follows a toxic-safe-toxic profile.
2. It shows that age-aligned keys change behavior relative to an equal-capacity sham while failing to improve survival in the primary comparison.
3. It shows that the observed survival consequences are conditional on the fixed learning rule, relative decision threshold, and resource economy; these components were not independently varied.
4. It identifies a regime boundary at the highest tested energy that prevents the prespecified slope from being interpreted uniquely as a payoff effect.

The article does not claim that perceptual aliasing is new, that agents discovered food age, or that an evolutionary response occurred across generations.

### 1.4 Hypotheses

**H1: Information sufficiency.** A type-by-age value key produces greater safe-versus-toxic discrimination than a type-only key and a capacity-matched sham key.

**H2: Directional survival prediction.** The frozen protocol predicted that the paired type-by-age-minus-sham founder follow-up slope would be positive as risky-fruit energy increased, because age information was expected to preserve valuable safe-fruit intake while reducing toxic intake. The statistical decision rule and this mechanistic prediction are evaluated separately; neither is expected value of perfect information or reproductive fitness.

**H3: Within-configuration replication.** In the internally frozen T2-RB experiment, founder follow-up under monotonic age-varying toxicity is compared with recalibrated and original constant-potency controls and reported regardless of direction. Comparisons with earlier drain settings are descriptive because no factorial interaction test was frozen.

## 2. Methods

### 2.1 Artificial ecology

The focal experiments used a 100 × 100 discrete world initialized with 50 mortal founders and 2,500 mature plants. Founders were positioned in the safe, food-rich frontier region and their initial ages were spread deterministically across the adult age range. This prevented a synchronized age cohort without consuming random numbers. The world was spatially heterogeneous in fertility, food density, and environmental danger. Natural seed rain was fixed at 12 attempts per tick, raw fruit at 20 spawn attempts per tick, the food-detection threshold at 0.01, and the vision horizon at 200. Base food and plant-lifecycle processes maintained a renewable raw-plant staple. Rejected items remained in their grid cells until eaten or stochastically decayed, so a decision could alter the agent's later exposure to the same item.

All agents shared a fixed morphological and physiological configuration indexed as body plan 37 in the code: two sensor, muscle, and brain units, no armor, baseline toxin tolerance 0.20, and fixed digestive and metabolic parameters listed in the supplement. The v2 metabolism option recomputed digestible energy from food mass, nutrient composition, and the body's enzyme efficiencies, then rounded it to an integer. Raw fruit had a baseline realized gross energy of 10 and the plant staple had a realized gross energy of 5. E6 applied a raw-fruit-only multiplier after the first rounding step and verified the resulting value in every run output. Aging, starvation death, and toxin-induced acute energy loss and chronic damage were enabled. Except where stated below, runs lasted at most 400 ticks and could end earlier at population extinction. E6 ran for at most 800 ticks, and the legacy-denominator reproduction E4 ran for 3,000 ticks. Simulation ticks and energy are abstract model units and are not mapped to a biological time or calorie scale.

Temporal toxicity was attached to raw fruit. Its toxin fraction was 0.30 and its mass was 1.2, giving an unscaled load of 0.36. In the monotonic profile M, potency was `max(0, 1 - age/120)`. In the non-monotonic profile W, potency was 1 before age 40, 0 from ages 40 through 79, and 1 again from age 80. Resource age was the current simulation tick minus the fruit's creation tick; it was not agent age. Realized toxin excess was `max(0, 0.36 × potency × potency_scale - tolerance)`. A positive excess added five times that value to chronic damage and subtracted 50 times that value from the bite's energy before integer rounding. Constant-potency controls retained the same fruit supply while fixing potency over resource age. They removed age variation but did not guarantee equal realized dose, because each policy changed which fruit was eaten and how often.

The supplementary model description follows the updated ODD protocol (Grimm et al., 2020) and records scheduling, state variables, equations, initialization, and implementation pointers. Supplementary parameter tables report the archived launch configuration for all 38 arms in E1-E6 and T2-RB, including the origin of each effective driver value and each code-fixed ecology setting at the clean Git revision recorded by the batch. Their exporter verified the ordered launch flags, horizons, arms, and seeds for all 980 archived run rows. A separate state-and-process catalogue traces movement, food access, eating, toxin, energy, damage, and survival, and a version audit bounds the code differences among batches. Per-run JSON dumps remain the authority for values realized during execution.

### 2.2 Learning representation

The type-only learner stored one value per food implementation type. For a key not previously encountered, the first consumed item initialized its value to the realized post-toxin energy. Subsequent observations used an exponential moving average, `V_new = V_old + 0.3(r - V_old)`, where `r` was the realized energy from that bite. A known food was accepted when its value was at least 0.6 times `best_known`, the maximum value across every learned key and every food type. Unfamiliar keys were sampled before they had a learned value, and an agent at or below 6 energy accepted any food regardless of its learned value.

The rescue learner stored separate values for 20-tick resource-age bins, capped at bin 8. The sham learner used the same nine-bin key range, but assigned bins with a deterministic hash of a resource's creation tick and encounter location, so the key carried no age information and consumed no random draw. Both schemes split keys for every food type, including the `raw_plant` staple; they did not split fruit alone. This control matched nominal memory capacity and repeated first-sample exploration, but it did not match realized key frequencies or exposure histories because trajectories diverged after behavior differed. An avoidance oracle observed realized toxin excess and rejected items with positive excess, except at the shared starvation override. It was a discrimination ceiling, not an optimal survival or fitness policy.

### 2.3 Experiments

#### Study A: Hidden-state cost and behavioral response

E1 used profile M and 20 matched seeds across four arms: food-matched nontoxic fruit (A0), fully potent constant toxicity (A1), monotonic age-dependent detoxification (A2), and constant toxicity calibrated to the frozen potential-dose target (A3). After the acute toxin penalty and integer rounding, A3 returned a constant net value of 6 per fruit bite. Its three Holm-controlled tests compared A2-A0 founder attained age, A2-A3 founder attained age, and A2-A1 acceptance conditional on encounter. A1 was a positive control for the learner's ability to avoid a consistently harmful category.

#### Study B: Information rescue

E2 used the same 20 matched seeds in both toxicity profiles. Each profile crossed four decision systems: type-only values (B1), type-by-resource-age values (B2), the capacity-matched sham (B3), and an oracle that rejected any fruit with positive excess toxin (B4). The internally frozen primary outcome was the discrimination index, `P(eat | safe encounter) - P(eat | toxic encounter)`, and the causal contrast was B2-B3 within profile. The M profile used monotonic detoxification over 120 ticks; the W profile used the toxic-safe-toxic window.

#### Study C: Within-generation selection

E3 used profile M and introduced experimenter-supplied variation in founder toxin tolerance by spreading the baseline value 0.20 over 0.05 to 0.35. Twenty matched seeds ran A0, A2, and A3. The selection differential was the mean tolerance of the half of founders with the longest attained ages minus the mean tolerance of all founders. Continuous tolerance-age slopes were reported as a mechanism check. No birth occurred, so E3 measured differential survival within the founder cohort and no response to selection across generations.

#### Study D: Exposure-denominator validation

E4 reran the 10 seeds and 3,000-tick configuration of an earlier stationary food-value experiment with encounter telemetry enabled. That experiment used low-value raw seed and higher-value raw plant rather than the raw-fruit toxin system. E4 tested whether raw meal counts understated selectivity when rejected food remained in the world and could be encountered again. It is a measurement validation and is not pooled with E1 or used as evidence about temporal toxicity.

#### Study E: High-drain transfer and within-configuration replication

E5 used profile M and repeated A0, A2, and the original A3 control across 20 matched seeds with the drain multiplier increased from 0.2 to 0.5. This directly increased metabolic energy expenditure and shifted deaths toward starvation while the aging and toxin-damage processes remained active; E5 therefore tested transfer to a composite high-drain configuration rather than isolating a single mortality process. Its A2-A3 contrast was exploratory. After observing that result, we internally froze a replication with 50 new matched seeds under the same profile and high-drain configuration. We refer to this replication by its archived study identifier, T2-RB. It compared A2 with both the original constant-potency control (A3O, potency scale 0.7578; full precision in the supplement) and a recalibrated control (A3R, 0.7507; full precision in the supplement). Both controls returned a constant post-rounding net fruit value of 6. A2-A3R was primary and A2-A3O was the direct-replication secondary contrast. No interaction between drain setting and toxicity profile was tested.

#### Study F: Energy-dependent survival effect of resource-age information

After closing the exploratory pilot, we internally froze the E6 protocol at Git tag `prereg-resource-age-2026-09-14`. E6 used the non-monotonic toxic-safe-toxic profile W and crossed five realized safe-fruit energies (4, 5, 6, 8, and 10 units) with three representations: type only (B1), type by resource-age bin (B2), and a capacity-matched sham bin (B3). Each of 30 new seeds ran all 15 arms, giving 450 runs. B2-B3 was the frozen primary contrast for age-aligned information content, B2-B1 was a prespecified secondary comparison, and B3-B1 is reported descriptively to expose the survival effect of irrelevant partitioning.

### 2.4 Outcomes and statistical analysis

The independent replicate is the seed, with one simulation run per arm within each matched seed. The primary survival outcome for the new confirmatory studies is mean founder follow-up time, computed for each founder as final attained age minus its deterministic initial age and restricted by the prespecified simulation horizon. Arms use matched seeds and are compared with paired differences. We report arm means and standard deviations, mean paired differences, 95% paired confidence intervals, seeded Monte Carlo two-sided sign-flip tests as specified, paired standardized mean differences (*d*<sub>z</sub>), paired probability of superiority, and directional seed counts. Primary probabilities and directional counts are shown in the supplementary mechanism tables; complete seed-level contrasts and learned values by key are provided in the source-data CSV files. Unpaired Cliff's delta from the archived analyses is supplementary rather than the principal effect size. Encounter-dependent behavior is reported as `P(eat | encounter)`; raw meal and skip counts are secondary because rejected food remains available and can be counted again on later ticks.

For E6, we computed B2-B3 at each energy within each seed and fitted one ordinary-least-squares slope over the five realized energies. The 30 seed-level slopes were tested with a seeded, two-sided Monte Carlo sign-flip test using 200,000 draws. The frozen decision rule required a positive mean slope and a 95% CI excluding zero; the planning effect scale was 1 follow-up tick per energy unit. The protocol also specified an encounter-coverage gate: B2 had to average at least 30 fruit encounters per founder at each energy level before H2 would be interpreted. Level-specific B2-B3 tests were Holm-adjusted across the five energies. B2-B1 was frozen as a secondary level-specific comparison without multiplicity adjustment; we additionally report an exploratory Holm correction across its five energy levels. After the primary result was known, we added a one-sided minimum-effect sign-flip sensitivity against slope 1, leave-one-energy-out slopes, founder-level intake and mortality summaries, paired effect sizes, and within-arm-by-energy residual correlations using intake rates and toxin excess per fruit meal; these analyses cannot change the frozen H2 decision. Rate variables that divide by follow-up can inherit denominator bias and are reported descriptively. Runtime failures were to be rerun only at the failed arm-seed cell and retained in the audit trail; no failures occurred. Simulations could stop at population extinction. No founder was censored in either new confirmatory study, so the death-only sensitivity equals the primary restricted-mean follow-up outcome.

### 2.5 Execution, provenance, and verification

E6 and T2-RB specifications, seeds, directional rules, exclusions, smallest effects of scientific interest, and analysis procedures were internally frozen at a Git tag before their outcome files were generated. This was not an externally timestamped public preregistration. The tag `prereg-resource-age-2026-09-14` identifies commit `3f1af32f9e37655ed9bee5462526921eff226c8a`; confirmatory runs were executed from a clean detached worktree at that tag. Matched seeds aligned initial stochastic inputs, but trajectories diverged as soon as behavior differed. Each output recorded requested flags, effective model parameters, source revision, platform, Python version, run duration, completion state, and arm/seed identity. The E2 oracle and discrimination outcome were implemented after the earlier narrative freeze, and the E6 encounter-gate interpretation was fixed after the primary result was known; both timings are listed in the supplementary deviation audit.

Batch validators required one complete output for every planned arm-by-seed cell, the frozen code revision, expected effective parameters, no silent reuse, and explicit failure and censoring fields. All 600 confirmatory cells passed. The historical SHA-256 manifest records 600 raw dumps and 16 original derived artifacts. A separate hash audit rechecked all 450 E6 and 150 T2-RB raw files without mismatch. At that audited snapshot, a machine-readable inventory recorded 52 derived, manuscript, figure, audit, and code artifacts without modifying the historical manifest. Unit and regression tests covered age-key assignment, the capacity-matched sham, raw-fruit-only energy scaling, toxin timing, encounter telemetry, provenance guards, validators, founder-to-seed aggregation, missing and duplicate cells, paired contrasts, and deterministic derived output. Figure scripts consume source tables and export plotted seed-level values as CSV. The E4 figure additionally checks `encounters = ate + skipped` and `telemetry ate = raw meals` within every run.

## 3. Results

### 3.1 Information sufficiency: age-aligned keys restored discrimination

In E2, B2 exceeded the equal-capacity B3 sham by 0.7858 discrimination units under monotonic detoxification (95% CI 0.7650 to 0.8066) and by 0.7515 under the toxic-safe-toxic profile (0.7214 to 0.7815). E6 reproduced the behavior across all five fruit energies: B2 mean discrimination ranged from 0.654 to 0.748, with `P(eat | safe) = 1.000` and `P(eat | toxic) = 0.252-0.346`. Every B2 run contained all nine resource-age keys and assigned higher learned values to safe bins than to toxic bins (Figure 1A; Supplementary Mechanism Tables).

The E2 avoidance oracle B4 produced the highest discrimination but not the longest survival. Mean founder attained age was 308.01 ticks under profile M and 286.82 under profile W; within each profile, these means were 51.964-55.761 ticks lower than the corresponding B1-B3 means. B4 therefore served as a discrimination ceiling, not a survival optimum.

The prespecified numerical expectations that B1 and B3 would have zero discrimination were not met exactly. Across E6, B1 ranged from -0.082 to -0.058 and B3 from -0.112 to -0.097; E2 showed deviations of similar size. Neither representation encoded age, so these signs cannot be interpreted as learned toxin-state discrimination. They instead define a systematic offset of up to about 0.1 in magnitude in the age-blind arms. Its source was not identified because unique-item and first-encounter discrimination could not be reconstructed; repeated encounters and starvation-override timing remain candidates rather than established causes. B2 remained well beyond this offset, supporting information sufficiency while precluding interpretation of the small B1/B3 signs.

### 3.2 Primary survival contrast: B2 did not outperform the sham

All 450 E6 runs passed the frozen batch validator. The primary B2-B3 contrast was negative at energies 4, 5, 6, and 8 and imprecisely positive at 10 (Table 1; Figure 2). Paired standardized mean differences (*d*<sub>z</sub>) were -0.597, -0.544, -0.596, -0.748, and +0.146, respectively. Correct state information therefore changed behavior without producing a detected survival advantage over the equal-capacity sham at any tested level.

**Table 1. E6 founder follow-up by representation and realized fruit energy.** Arm entries are mean follow-up ticks across 30 seeds. Contrasts are within-seed mean differences with 95% paired t CIs. B2-B3 was the frozen primary contrast; B2-B1 was prespecified secondary.

| Energy | B1 mean | B2 mean | B3 mean | Primary B2-B3 [95% CI] | Secondary B2-B1 [95% CI] |
|---:|---:|---:|---:|---:|---:|
| 4 | 144.239 | 150.713 | 156.145 | -5.431 [-8.826, -2.037] | +6.475 [2.149, 10.801] |
| 5 | 150.314 | 156.063 | 161.639 | -5.576 [-9.403, -1.749] | +5.749 [0.754, 10.744] |
| 6 | 156.123 | 160.169 | 166.309 | -6.141 [-9.989, -2.293] | +4.045 [-0.429, 8.520] |
| 8 | 172.624 | 171.341 | 178.991 | -7.650 [-11.470, -3.830] | -1.283 [-4.987, 2.422] |
| 10 | 207.595 | 207.078 | 205.713 | +1.365 [-2.122, 4.852] | -0.517 [-3.406, 2.372] |

The mean seed-level B2-B3 slope was positive (0.890 ticks per energy unit, SD 2.227; 95% t CI 0.059 to 1.722; two-sided sign-flip p = 0.0365), meeting the frozen statistical decision rule. The observed SD exceeded the planning value of 1.624, reducing normal-approximation power for a slope of 1 from 0.92 to about 0.69. A post hoc minimum-effect test did not establish a slope greater than 1 (one-sided sign-flip p = 0.607). Omitting energy 10 changed the slope to -0.578 (95% CI -1.853 to 0.696). Thus the statistical rule was met, the effect did not exceed the planned effect scale, and the frozen mechanistic prediction was not supported by the level-specific contrasts.

### 3.3 Energy 10 coincided with a policy-regime change and senescence ceiling

At energy 10, a learned safe-fruit value set a relative threshold of 0.6 × 10 = 6, above the staple value of 5. The continuous crossing occurs at 5 / 0.6 = 8.33, between the tested energies 8 and 10 (Figure 2A). Staple acceptance consequently fell to 0.436 in B2 and 0.563 in B3, compared with 0.958 in B1; 0.717 of B2 founders and 0.540 of B3 founders rejected staple at least once. No staple rejection occurred at energies 4-8. At the same endpoint, senescence accounted for 0.740-0.765 of founder outcomes across arms. The single non-negative B2-B3 contrast therefore occurred where both the decision policy and the available survival range changed.

**Table 2. E6 intake, realized toxin excess, and mortality.** Values are means across seed-level founder aggregates. Meal counts are descriptive; skip/encounter telemetry can count repeated contact with the same item.

| Energy | Arm | Fruit meals | Staple meals | Staple accept | Toxin excess | Toxin damage | Starvation | Senescence |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 4 | B1 | 17.211 | 17.525 | 1.000 | 2.066 | 10.331 | 0.761 | 0.186 |
| 4 | B2 | 18.354 | 20.051 | 1.000 | 2.101 | 10.506 | 0.728 | 0.217 |
| 4 | B3 | 19.680 | 23.684 | 1.000 | 2.386 | 11.930 | 0.681 | 0.266 |
| 5 | B1 | 18.175 | 18.365 | 1.000 | 2.178 | 10.892 | 0.721 | 0.217 |
| 5 | B2 | 18.871 | 20.251 | 1.000 | 2.149 | 10.744 | 0.702 | 0.245 |
| 5 | B3 | 20.183 | 23.965 | 1.000 | 2.446 | 12.229 | 0.629 | 0.300 |
| 6 | B1 | 19.025 | 18.953 | 1.000 | 2.256 | 11.278 | 0.661 | 0.269 |
| 6 | B2 | 19.061 | 20.025 | 1.000 | 2.150 | 10.749 | 0.649 | 0.277 |
| 6 | B3 | 20.822 | 23.660 | 1.000 | 2.518 | 12.588 | 0.591 | 0.332 |
| 8 | B1 | 21.599 | 21.035 | 1.000 | 2.566 | 12.828 | 0.481 | 0.410 |
| 8 | B2 | 20.103 | 19.343 | 1.000 | 2.237 | 11.186 | 0.544 | 0.351 |
| 8 | B3 | 21.655 | 23.578 | 1.000 | 2.614 | 13.070 | 0.465 | 0.434 |
| 10 | B1 | 26.507 | 27.405 | 0.958 | 3.181 | 15.907 | 0.077 | 0.765 |
| 10 | B2 | 25.724 | 22.275 | 0.436 | 2.984 | 14.922 | 0.088 | 0.740 |
| 10 | B3 | 25.447 | 24.008 | 0.563 | 3.093 | 15.466 | 0.081 | 0.742 |

In a post hoc descriptive analysis of within-arm-by-energy residuals, follow-up correlated positively with staple meals per follow-up tick (*r* = 0.985) and negatively with toxin excess per follow-up tick (*r* = -0.706), fruit meals per follow-up tick (*r* = -0.621), and toxin excess per fruit meal (*r* = -0.483). The first three rates divide by follow-up and can inherit denominator bias; the toxin-per-meal measure does not use follow-up in its denominator. These associations suggest that seeds whose founders ate staple more frequently and received less toxin per fruit meal tended to survive longer, but they do not identify a causal path. Archived telemetry did not record agent energy at the decision moment, so starvation-override meals could not be separated; meal timing, search cost, and unique-item re-encounters also remain unresolved.

### 3.4 Secondary and descriptive E6 contrasts

Relative to B1, B2 increased follow-up at energy 4 by +6.475 ticks (95% CI 2.149 to 10.801; exploratory Holm-adjusted p = 0.02125). The energy-5 difference was +5.749 (0.754 to 10.744) but did not survive the exploratory five-level correction; intervals included zero at energies 6, 8, and 10. B3-B1, a descriptive comparison that was not prespecified, was +11.906, +11.325, +10.186, and +6.367 ticks at energies 4-8 before becoming -1.881 at 10. These results explain why a positive B2-B1 contrast does not imply that age-aligned information beat the primary equal-capacity control.

### 3.5 E1: null under an imperfect constant-potency control

E1 established a toxin cost relative to nontoxic fruit (A2-A0 -27.729 ticks, 95% CI -33.691 to -21.767) but did not support the prediction that age-varying toxicity imposed an additional cost beyond A3 (A2-A3 +1.080, -2.390 to 4.550; Figure 3). In the A1 positive control, the mean learned fruit value was 2.000, below the staple value of 5.000, and mean fruit acceptance was 0.354. A3 returned a constant learned fruit value of 6 and was accepted at every observed encounter. Realized toxin excess was lower in A2 than A3 (2.114 versus 2.371 per founder), so this comparison did not isolate hidden state at equal realized dose.

### 3.6 High-drain replication (T2-RB): deficit under constant-payoff controls

The exploratory high-drain E5 result was opposite to its frozen narrative prediction and motivated T2-RB. All 150 T2-RB runs passed validation. A2 reduced mean founder follow-up relative to A3R by 7.928 ticks (95% CI -11.046 to -4.810; paired *d*<sub>z</sub> = -0.720) and relative to A3O by 7.102 ticks (-10.218 to -3.985; *d*<sub>z</sub> = -0.645; Figure 4). The A3 controls were not independent robustness tests: both returned a constant learned fruit value of 6, were accepted at every encounter, and differed in mean toxin damage by only 2.9%. A2 had lower realized toxin excess (1.877 per founder) than A3R (2.048) or A3O (2.107) while also having fewer staple meals and shorter follow-up (Table 3). T2-RB therefore compares variable, choice-requiring toxicity with fixed-payoff controls that required no discrimination; it does not isolate hidden versus visible toxicity at equal realized dose.

**Table 3. T2-RB realized behavior, intake, dose, and mortality.** Values are means across 50 seed-level founder aggregates.

| Arm | Follow-up | Fruit n | Staple n | P(eat fruit) | P(eat staple) | Toxin | Toxin/meal | Damage | Starved | Senescent |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A2 | 159.261 | 27.070 | 34.808 | 0.941 | 0.829 | 1.877 | 0.069 | 9.384 | 0.417 | 0.500 |
| A3O | 166.362 | 28.934 | 40.164 | 1.000 | 1.000 | 2.107 | 0.073 | 10.534 | 0.370 | 0.556 |
| A3R | 167.189 | 29.158 | 40.332 | 1.000 | 1.000 | 2.048 | 0.070 | 10.240 | 0.371 | 0.553 |

### 3.7 Prediction and deviation audit

For clarity, the article uses only the H1-H3 numbering defined in Section 1.4; the supplementary prediction audit retains the original protocol identifiers solely for traceability. H1 was supported because B2 discrimination exceeded both age-blind representations, although the auxiliary zero-discrimination expectations for B1 and B3 were not met exactly. H2 met its frozen statistical rule but not its level-specific mechanistic rationale or minimum-effect sensitivity. H3 yielded a replicated deficit relative to both constant-payoff controls. Two auxiliary frozen predictions outside the article's H1-H3 set were not supported: E1 did not show an additional age-varying toxicity cost beyond A3, and E3 did not show stronger tolerance selection than the constant-toxicity arm. The E5 regime prediction also failed. The deviation audit records that the E2 oracle and discrimination outcome were implemented after the initial narrative freeze, E4 was a retroactive denominator check, the E6 encounter-coverage gate was interpreted after the primary result, and the archived telemetry cannot identify starvation-override meals.

### 3.8 Supporting results moved out of the main causal chain

E3 showed a positive within-generation toxin-tolerance selection differential relative to the nontoxic control (+0.0255, 95% CI 0.0191 to 0.0319) but did not support the prediction that age-varying toxicity would strengthen selection relative to constant toxicity (-0.0083, -0.0135 to -0.0032). No births occurred, so this was differential founder survival rather than evolutionary change. E4 separately showed that rejection can inflate repeated encounters with persistent food: learning reduced low-value meals while increasing recorded contacts, supporting encounter-conditional acceptance as the behavioral denominator (Figure 5). Neither result changes the primary E6 survival interpretation.

## 4. Discussion

### 4.1 Information sufficiency and information value are different questions

The rescue experiment establishes the representational result directly. B2 and B3 offered the learner the same nominal nine-key range and the same first-sample and update rules. Only B2 aligned those keys with resource age. B2 then separated safe from toxic encounters in both the monotonic and toxic-safe-toxic profiles, while B3 showed the same systematic age-blind offset of up to about 0.1 in magnitude seen in B1. The source of that offset was not identified. Every confirmatory B2 run populated all nine keys and learned a higher value for safe than toxic bins. Extra storage or repeated exploration alone therefore does not explain B2's large positive discrimination. At the same time, B3's survival advantage over B1 at four energy levels shows that the sham altered behavior and ecological outcomes. The B2-B3 contrast controls capacity, but it compares two active partitioning rules rather than an informative treatment with an inert placebo.

That result answers whether the supplied representation is sufficient for the behavioral distinction. It does not answer whether the changed behavior improves survival. The difference matters because formal fitness-value arguments compare optimized responses over relevant long-run consequences (Donaldson-Matasci et al., 2010). These agents instead used a fixed exponential moving average, a fixed relative-value threshold, and a starvation override. The experiment measures the consequence of adding state information to that particular bounded policy. It does not estimate the expected value of perfect information for an optimal decision maker.

This distinction also explains why describing B4 as an optimal policy would be incorrect. The oracle observed realized toxin excess and nearly maximized safe-versus-toxic discrimination, but it optimized only the immediate rule “avoid positive excess toxin,” subject to the starvation override. It did not compare the lifetime energy gained from fruit with acute damage, chronic damage, future search, or mortality risk. As reported in Section 3.1, its mean attained age was 51.964-55.761 ticks below the corresponding learner means across the two profiles. Perfect toxin classification can therefore be coupled to a poor ecological objective.

### 4.2 Representation changes generalization and action

The type-only learner generalized every raw-fruit outcome to a single value. This compression was useful when the correct action was stable across fruit encounters and harmful when safe and toxic ages called for different actions. E1's positive control showed that the same learner could avoid a consistently harmful fruit category: its learned fruit value fell below the staple and acceptance declined. Under age-dependent toxicity, post-ingestive outcomes were averaged, the fruit value remained above the staple, and acceptance stayed high. The limitation was therefore not a complete inability to learn from consequences. It was an inability to condition that learning on a state absent from the key.

B2 reduced this aliasing by splitting experience over resource-age bins. The split imposed its own learning dynamics: each unfamiliar bin had to be sampled, and estimates generalized over fewer observations. B3 controlled the nominal number of bins and that repeated first-sample burden without supplying the relevant temporal structure. The B2-B3 contrast therefore identifies the effect of aligning memory with resource state under a common capacity, although it does not claim that all possible exploration histories or key-frequency distributions were identical.

The ecological consequence cannot be reduced to “rejecting toxic fruit costs energy.” At energy 4, B2 ate more fruit and more staple than B1 while receiving essentially the same toxin excess; B3 received the most toxin and nevertheless had the longest follow-up. Post hoc rate-based descriptives showed that follow-up was positively associated with staple meals per tick and negatively associated with toxin per fruit meal within arm-by-energy cells. The former rate divides by follow-up and is not free of denominator coupling, while the toxin-per-meal association remains descriptive rather than causal. The available telemetry cannot identify meals taken under the starvation override, meal timing, search cost, or unique-item re-encounters. B3's deterministic hash bins could still create history-dependent pseudo-categories and alter behavior, but the causal path from those changes to survival remains unidentified.

The first-taste rule also gives ingestion two roles: it provides immediate energy and supplies the observation used to update the value map. This resembles the coupling of sampling and feeding studied by Scholz et al. (2017), but here the consequence can include toxin damage and the acquired information is stored under an experimentally manipulated key. The B2 result shows that receiving the relevant state distinction changes what can be learned from the sample; the survival result shows that the resulting exploitation rule must still be evaluated in its resource economy. The separation parallels Borg and Channon's (2020) finding that access to information can change behavior even when poisonous-food discrimination does not improve: behavioral responsiveness and task benefit require separate outcomes.

### 4.3 The upper endpoint mixed payoff with a policy-regime change

E6 met its frozen directional decision rule: the mean B2-B3 slope was positive and its 95% interval excluded zero. That statistical verdict does not rescue the prespecified mechanism. B2 had lower follow-up than B3 at energies 4, 5, 6, and 8; only the energy-10 estimate was non-negative, and its interval included zero. The slope estimate of 0.890 was below the planning effect scale of 1, the post hoc minimum-effect test failed, and removing energy 10 reversed the slope.

The tested energy 10 is the first level above the continuous policy boundary at 5 / 0.6 = 8.33. B2 and B3 began rejecting staple, while senescence dominated mortality and compressed further survival differences. The design therefore cannot distinguish a pure payoff response from threshold discontinuity, starvation override, first-sample burden across staple keys, meal timing, search or metabolic cost, behavior-generated exposure, or the senescence ceiling. The evidence supports endpoint dependence, not an attenuation mechanism or a break-even payoff.

The comparisons across E1 and E5 are descriptive. E1 used drain multiplier 0.2 and found no A2-A3 difference; exploratory E5 used 0.5 and found an A2 deficit opposite to its prediction. Those experiments were not analyzed in a factorial model, so they do not estimate a drain-by-toxicity-profile interaction. T2-RB reproduces a deficit within the high-drain configuration, but its constant controls offered a fixed payoff that required no discrimination and received more realized toxin than A2. The result is therefore a cost of variable, choice-requiring toxicity relative to that control policy, not an isolated cost of hidden state or equal realized dose. Establishing drain as a moderator would require a newly frozen factorial experiment that crosses drain and toxicity profile within one seed design.

### 4.4 Selection within a cohort is not evolutionary change

E3 provides a separate view of the toxin mechanism. When founders varied in toxin tolerance, the longer-lived half of the cohort had higher mean tolerance under both toxic conditions and not under the nontoxic control. This is a within-generation selection differential: a statistical association between a supplied trait and differential survival. The constant-potency arm produced a larger differential than the age-dependent arm, contrary to the prediction that concealment would intensify selection. Its greater realized toxin intake provides a mechanistically consistent explanation.

No births occurred, so the model did not realize inheritance, reproduction, or a response to selection in these experiments. Calling the E3 pattern “evolution” would collapse distinct levels of evidence. The result supports selective survival among founders and shows that the toxin implementation can act on tolerance. Demonstrating evolutionary change would require sustained reproduction, transmission of tolerance, and a prospectively frozen population-level analysis across generations.

### 4.5 Exposure is partly produced by behavior

E4 exposed a measurement issue that matters beyond this particular model. A rejected food item remained in place and could be encountered again. Consequently, learning reduced low-value meals from 1,945.3 to 423.0 per run while increasing mean encounters from 1,945.3 to 26,945.3. The raw meal ratio suggested a 4.6-fold difference, whereas acceptance conditional on encounter differed by approximately 62-fold. The act of rejection changed the denominator of future opportunities.

This feedback means that meal count is not a direct measure of selectivity in a persistent-resource environment. It combines the probability of accepting an encountered item with the exposure process generated by earlier choices. We therefore treat `P(eat | encounter)` as the behavioral outcome and report meals and encounters separately. The telemetry invariant that every no-learning encounter became a meal, together with exact reproduction of the historical meal totals, provides a direct check on the denominator.

### 4.6 Evidential strengths and remaining uncertainty

Several design features narrow the causal claims. Matched seeds align initial stochastic inputs, although their trajectories diverge after behavior changes. The B3 sham distinguishes information content from nominal key capacity but not from all key-frequency or first-sample histories. Constant-potency controls remove temporal variation while retaining fruit supply; they do not match realized dose and, after rounding, they create a fixed payoff accepted at every observed encounter. The E6 payoff manipulation changes raw-fruit energy while leaving staple energy fixed, and effective values are checked in outputs. The analysis reports null, opposite-direction, and endpoint-dependent findings rather than retaining only supportive contrasts.

The confirmatory work was separated from the exploratory pilot by a frozen tag and new seed ranges. Validators checked every planned cell and its effective parameters, and the raw and derived files have a verified checksum manifest. This is strong internal provenance, not an externally timestamped preregistration. These controls protect the interpretation from silent parameter failure and incomplete batches; they do not remove model uncertainty or make a single implementation representative of biological foraging.

### 4.7 Limitations and next tests

- Food age was supplied as a perfect cue; agents did not discover it.
- The value rule was fixed rather than evolved.
- The simulation did not produce births in the E-series, so no cross-generational evolutionary response was measured.
- The avoidance oracle optimized toxin avoidance only and was not an optimal policy.
- Pickiness 0.6 combined with staple value 5 creates a continuous policy boundary at safe-fruit value 8.33; the starvation override can modify behavior around that boundary but does not create it. Neither component was varied.
- Learning rate 0.3, 20-tick age bins capped at 8, and the acute and chronic toxin coefficients lack sensitivity analysis.
- The small nonzero `D` of age-blind arms is a systematic offset of up to about 0.1 in magnitude whose source was not identified; unique-item or first-encounter discrimination and decision-time starvation state could not be reconstructed from the archived telemetry.
- The E6 linear trend depended materially on the energy-10 endpoint and a senescence-dominated ceiling; the experiment did not establish a smooth response curve or general break-even payoff.
- The frozen encounter-coverage gate wording was ambiguous. The requirement of at least 30 B2 fruit encounters per founder passed under the level-mean interpretation fixed after the primary result, but a stricter per-run reading failed at energies 4-6.
- Archived telemetry cannot identify starvation-override meals, so intake correlations cannot establish their causal path.
- The internally frozen Git history was not an externally timestamped public preregistration.
- The chosen energy, toxin, metabolism, and renewal regimes delimit the quantitative conclusions, and simulation units are not calibrated to a biological species.
- The current study does not implement storing food for later detoxification.

The next discriminating experiments are specific. A publicly timestamped series crossing fruit payoff with pickiness and starvation threshold would test whether the energy-10 pattern is a policy discontinuity. A factorial manipulation of payoff and metabolic drain would separate their interaction from the composite high-drain transfer. A control that partitions fruit but not staple would isolate the first-sample burden induced by sham and age keys. Instrumenting decision-time energy, unique resource identity, meal timing, and search cost would separate the candidate causal paths. Replacing perfect age with noisy or learned sensory cues would test whether the rescue survives observation error, while sustained reproduction would permit a separate study of evolutionary response. These are new studies and must not be mixed with the frozen dataset.

## 5. Conclusion

Resource-age information solved the hidden-state discrimination problem under both monotonic and toxic-safe-toxic profiles, but it did not improve survival over the equal-capacity sham. The primary B2-B3 contrasts were negative at energies 4-8 and uncertain at 10. Although the frozen positive-slope rule was met, the slope did not exceed the planned effect scale and depended on the endpoint where the relative threshold began rejecting staple and mortality became senescence-dominated. T2-RB likewise showed a deficit relative to fixed-payoff controls despite lower realized toxin dose in the age-varying arm. In this artificial ecology, correct state information was behaviorally sufficient but not sufficient for survival value under the fixed learner and policy.

## Data and Code Availability

The public release will provide the confirmatory data, derived results, and analysis code in five bundles with a machine-readable inventory and flat SHA-256 list. A separate baseline hash audit verified all 600 confirmatory raw dumps without mismatch. **[Insert the versioned public archive citation, DOI, and code-release tag after deposit and download-back verification; do not submit this placeholder.]**

## Supplementary Materials

Supplementary materials include the ODD model description; complete experiment launch-parameter and code-fixed-setting tables; the focal state/process catalogue; the code-version audit; an independent-reproduction protocol and deterministic smoke signatures; internally frozen protocols and validation records; source-data tables for all figures; supplementary mechanism tables; prediction and deviation audits; analysis and figure-generation scripts; and a public-archive manifest with machine-readable inventory and checksums. Public archive links will be finalized after deposit.

## Funding

**[Author confirmation required. If accurate: This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.]**

## Competing Interests

**[Author confirmation required. If accurate: The author declares no competing interests.]**

## Ethics Statement

This study used only computer simulations and involved no human participants or live animals; institutional ethics approval was therefore not required.

## Author Contributions

**[Author confirmation required. Complete a CRediT statement covering conceptualization, methodology, software, validation, formal analysis, investigation, data curation, visualization, writing, and project administration.]**

## Generative-AI Disclosure

OpenAI Codex (OpenAI, 2026) assisted with code and evidence audits, experiment and analysis tooling, execution checks, literature screening, figures, parameter exports, and manuscript and supplement drafting, editing, submission-format review, and PDF verification on September 13-19 and September 23, 2026. Anthropic Claude Opus 5 (Anthropic, 2026; model ID `claude-opus-5`) was used through the Claude Code desktop app for adversarial manuscript reviews on September 15 and 16, 2026. Review claims were treated as hypotheses and checked against source papers, code, or raw data before use. The human author made the scientific decisions and remains responsible for the source verification, code, outputs, statistics, figures, claims, citations, declarations, and submitted wording. A task-level record, including whether a model identifier was exposed in each session, is included in the supplementary AI-use log.

## References

Anthropic. (2026). *Claude Opus 5* [Large language model]. https://www.anthropic.com/claude

Borg, J. M., & Channon, A. (2020). The effect of social information use without learning on the evolution of social behavior. *Artificial Life, 26*(4), 431–454. https://doi.org/10.1162/artl_a_00328

Bullinaria, J. A. (2017). Imitative and direct learning as interacting factors in life history evolution. *Artificial Life, 23*(3), 374–405. https://doi.org/10.1162/ARTL_a_00237

Cipollini, M. L., & Levey, D. J. (1997). Why are some fruits toxic? Glycoalkaloids in *Solanum* and fruit choice by vertebrates. *Ecology, 78*(3), 782–798. https://doi.org/10.1890/0012-9658(1997)078[0782:WASFTG]2.0.CO;2

Chrisman, L. (1992). Reinforcement learning with perceptual aliasing: The perceptual distinctions approach. In *Proceedings of the Tenth National Conference on Artificial Intelligence* (pp. 183–188). AAAI Press. https://cdn.aaai.org/AAAI/1992/AAAI92-029.pdf

Dall, S. R. X., Giraldeau, L.-A., Olsson, O., McNamara, J. M., & Stephens, D. W. (2005). Information and its use by animals in evolutionary ecology. *Trends in Ecology & Evolution, 20*(4), 187–193. https://doi.org/10.1016/j.tree.2005.01.010

Donaldson-Matasci, M. C., Bergstrom, C. T., & Lachmann, M. (2010). The fitness value of information. *Oikos, 119*(2), 219–230. https://doi.org/10.1111/j.1600-0706.2009.17781.x

Dorin, A., & Stepney, S. (2024). What is Artificial Life today, and where should it go? *Artificial Life, 30*(1), 1–15. https://doi.org/10.1162/artl_e_00435

Gershenson, C., Trianni, V., Werfel, J., & Sayama, H. (2020). Self-organization and Artificial Life. *Artificial Life, 26*(3), 391–408. https://doi.org/10.1162/artl_a_00324

Giannakakis, E., Khajehabdollahi, S., & Levina, A. (2025). Network bottlenecks and task structure control the evolution of interpretable learning rules in a foraging agent. *Artificial Life, 31*(2), 177–194. https://doi.org/10.1162/artl_a_00458

Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., Giske, J., Groeneveld, J., Johnston, A. S. A., Miles, A., Nabe-Nielsen, J., Polhill, J. G., Radchuk, V., Rohwäder, M.-S., Stillman, R. A., Thiele, J. C., & Ayllón, D. (2020). The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism. *Journal of Artificial Societies and Social Simulation, 23*(2), Article 7. https://doi.org/10.18564/jasss.4259

Ha, D. (2019). Reinforcement learning for improving agent design. *Artificial Life, 25*(4), 352–365. https://doi.org/10.1162/artl_a_00301

McCallum, R. A. (1996). *Reinforcement learning with selective perception and hidden state* (Doctoral dissertation, University of Rochester). http://hdl.handle.net/1802/842

OpenAI. (2026). *Codex* [AI coding agent]. https://openai.com/codex/

Provenza, F. D. (1995). Postingestive feedback as an elementary determinant of food preference and intake in ruminants. *Journal of Range Management, 48*(1), 2–17. https://doi.org/10.2307/4002498

Scholz, M., Dinner, A. R., Levine, E., & Biron, D. (2017). Stochastic feeding dynamics arise from the need for information and energy. *Proceedings of the National Academy of Sciences, 114*(35), 9261–9266. https://doi.org/10.1073/pnas.1703958114

Stephens, D. W., & Krebs, J. R. (1986). *Foraging theory*. Princeton University Press.

## Figure captions

**Figure 1. Resource-age information restored discrimination without guaranteeing survival benefit.** (A) Safe-minus-toxic acceptance under type-only (B1), type-by-age (B2), capacity-matched sham (B3), and avoidance-oracle (B4) policies in monotonic and toxic-safe-toxic profiles. (B) Within-seed attained-age differences relative to B1. Attained-age and founder follow-up differences are identical within a matched seed because founder initial ages are deterministic. Points are independent seeds; diamonds and bars are means and descriptive 95% t intervals.

**Figure 2. Survival contrasts and discrimination across risky-resource payoffs.** (A) E6 paired founder follow-up contrasts for B2-B3, B2-B1, and the descriptive B3-B1 comparison. Thin gray lines show within-seed B2-B3 values; colored markers and bars show contrast means and 95% t intervals. The dashed line is at safe-fruit value 8.33, where 0.6 × safe-fruit value equals staple value 5; energy 10 is the first tested level above this boundary. (B) Discrimination for the type-only, resource-age, and sham representations. All 450 profile-W runs passed the frozen validator.

**Figure 3. Hidden toxicity changed survival and behavior.** (A) Mean founder attained age in E1 under food-matched nontoxic fruit (A0), fully potent constant toxicity (A1), age-dependent toxicity (A2), and the constant-potency control (A3). A3 returned a constant post-rounding net fruit value of 6 and was accepted at every observed fruit encounter. (B) Acceptance conditional on fruit encounter. Colored points are independent seeds; black diamonds and bars are means and descriptive 95% t intervals.

**Figure 4. Internally frozen high-drain replication (T2-RB).** Paired founder follow-up contrasts for age-varying toxicity against the original (A3O) and recalibrated (A3R) constant-potency controls. Colored points are seed-level paired differences; gray lines connect contrasts within seed; black diamonds and bars are means and 95% t intervals. The dashed line marks the frozen -5-tick effect scale. All 150 runs passed the frozen validator.

**Figure 5. Within-generation selection and the exposure-denominator check.** (A) E3 toxin-tolerance selection differentials for the nontoxic, age-dependent, and constant-potency arms. No births occurred. (B) E4 acceptance per low-value raw-seed encounter with value learning disabled or enabled; annotations give mean raw meals and telemetry-deduplicated encounters. Points are independent seeds; diamonds and bars are means and descriptive 95% t intervals.
