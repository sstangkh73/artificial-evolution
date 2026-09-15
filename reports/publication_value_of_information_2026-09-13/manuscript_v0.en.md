# When Does a Better Representation Pay? Survival Effects of Resource-Age Information in Artificial Foraging Under Temporal Toxicity

**Manuscript type:** Article

**Target journal:** *Artificial Life* (author instructions checked September 14, 2026; final requirements must be rechecked at submission)

**Author:** Chisanupong Injun
**Status:** submission-audited Article draft at target length; author verification, independent reproduction, and public archive still incomplete

## Abstract

Artificial foragers can learn from post-ingestive outcomes while failing when one perceptual category combines states that require different actions. In a preregistered experiment using a toxic-safe-toxic resource-age profile, an age-indexed value key restored safe-versus-toxic discrimination at all five tested fruit energies; type-only and capacity-matched sham keys instead produced slightly negative discrimination. Relative to the type-only learner, the age-indexed learner increased mean founder follow-up at energy 4 (+6.475 ticks, 95% CI 2.149 to 10.801), which survived an exploratory Holm correction across five secondary B2-B1 tests; the increase at energy 5 (+5.749, 0.754 to 10.744) was nominal only. The sham nevertheless had still higher mean follow-up at energies 4–8. Consequently, the registered age-key-minus-sham effects were negative at energies 4, 5, 6, and 8, while the 95% CI included zero at 10. Their seed-level slope was positive (0.890 ticks per energy unit, 95% CI 0.059 to 1.722; two-sided sign-flip p=0.0365), slightly below the preregistered smallest effect of scientific interest and dependent on the energy-10 endpoint. A separate 50-seed replication under monotonic detoxification found shorter follow-up under age-varying toxicity than under a recalibrated constant-potency control (-7.928 ticks, 95% CI -11.046 to -4.810). State information therefore changed behavior reliably, but its survival consequence depended on the comparison policy and tested ecology.

**Keywords:** artificial life; value of information; embodied foraging; perceptual aliasing; temporal toxicity; state representation

## 1. Introduction

### 1.1 Problem

Outcome-grounded learning can estimate the average consequence of a food category without representing every state that determines that consequence. When toxicity changes with food age, a type-only estimate combines safe and toxic encounters. This is a form of perceptual aliasing: situations that require different responses are indistinguishable to the decision rule (Chrisman, 1992). An action cannot depend on resource age when age, or a correlated cue, is absent from the decision key.

The existence of this representational limit is established in reinforcement-learning research. Ecological accounts add a second requirement: uncertainty reduction should be evaluated through the decisions and functional consequences it enables (Dall et al., 2005). Formal fitness value further assumes a response chosen to improve long-run fitness (Donaldson-Matasci et al., 2010). Our fixed learner and within-lifetime survival outcome do not satisfy that definition. The empirical question here is narrower: **when does resolving the hidden resource state improve survival-relevant outcomes, and when does it fail to do so?**

### 1.2 Related work and conceptual boundary

Artificial Life uses synthetic systems to examine living and life-like processes while distinguishing virtual, simulated, embodied, and other forms of ALife (Dorin & Stepney, 2024). The present work is a simulated, embodied artificial ecology: it studies a constructed adaptive mechanism without claiming that the software agents are alive. This placement matters because the causal question concerns an agent-environment organization—perception, memory, action, metabolism, and resource renewal—rather than an algorithm evaluated on a detached reward benchmark.

Two literatures motivate the distinction tested here. In reinforcement learning, perceptual aliasing describes the case in which the same observation corresponds to underlying states that require different actions (Chrisman, 1992). Adding memory or a state distinction can make an otherwise unsolvable discrimination available to the policy, but that representational result does not by itself specify the utility of the actions that follow. Our B2-B3 comparison is designed around this narrow point: both learners can maintain the same nominal number of values, while only B2 receives a key aligned with the state that changes the consequence of eating.

The ecology-of-information literature treats information use as part of a decision problem. Dall et al. (2005) distinguish uncertainty from the functional value of reducing it. Donaldson-Matasci et al. (2010) formalize fitness value through the difference between optimized long-run outcomes with and without a cue. These accounts imply that a more informative observation may be behaviorally effective without guaranteeing a positive outcome for a fixed, bounded policy. The present model makes the relevant energetic, ingestion, and opportunity costs explicit so their joint consequence can be measured rather than assumed.

Feeding can itself couple information acquisition and energetic return. Scholz et al. (2017) combined *Caenorhabditis elegans* feeding data with a sequential decision model in which sampling both gathers evidence about food availability and obtains nutrients. Their model produced speed-accuracy and exploration-exploitation trade-offs in a changing environment. Our mechanism differs in two respects: the agents update post-ingestive values rather than infer ambient food concentration, and B2 receives resource age directly rather than discovering a cue by sampling. The common point is that the informational and energetic consequences of feeding occur through the same action and therefore cannot be evaluated independently.

Artificial-life models make this separation experimentally accessible because representation, learning, bodies, and resource dynamics can be intervened on independently. Giannakakis et al. (2025) showed that task structure and network bottlenecks alter which local learning rules evolve and how well embodied foragers perform. The present study holds the learner fixed and instead manipulates whether its value key preserves a payoff-relevant resource state. This makes the study a causal test of representational content inside a spatial ecology rather than a proposal for a new reinforcement-learning algorithm.

Several *Artificial Life* studies make the comparison more specific. Bullinaria (2017) modeled how direct and imitative learning interact with life-history evolution, linking learning to population change; the present no-birth experiments isolate within-lifetime valuation and survival. Ha (2019) and Giannakakis et al. (2025) show in different ways that performance depends on the structure supplied to an embodied learner, including morphology, task structure, and network constraints. Borg and Channon (2020) further found that access to social information could alter behavior even when poisonous-food discrimination was no better, a useful precedent for measuring behavioral change separately from task performance. Finally, Gershenson et al. (2020) caution that self-organization claims depend on identifying which organization arises from component interactions. We therefore report the age cue, value key, policy, and ecological payoffs as experimenter-supplied components and reserve the empirical claim for the behavior and survival patterns produced by their interaction.

### 1.3 Contribution

This article makes three bounded contributions:

1. It demonstrates a full-ecology failure of type-only food valuation under age-dependent toxicity.
2. It uses a resource-age-key rescue and a capacity-matched sham control to identify information as the cause of restored discrimination.
3. It measures whether the survival effect of that information changes with the energetic value of the risky resource.

The article does not claim that perceptual aliasing is new, that agents discovered food age, or that an evolutionary response occurred across generations.

### 1.4 Hypotheses

**H1: Information sufficiency.** A type-by-age value key produces greater safe-versus-toxic discrimination than a type-only key and a capacity-matched sham key.

**H2: Survival effect of state information.** The paired lifespan difference between the type-by-age learner and the capacity-matched sham changes systematically as risky-fruit energy changes. This is an empirical effect for fixed learning policies, not expected value of perfect information and not reproductive fitness.

**H3: Within-configuration replication.** In the preregistered R-B experiment, founder follow-up under monotonic age-varying toxicity is compared with recalibrated and original constant-potency controls and reported regardless of direction. Comparisons with earlier drain settings are descriptive because no factorial interaction test was preregistered.

## 2. Methods

### 2.1 Artificial ecology

The focal experiments used a 100 × 100 discrete world initialized with 50 mortal founders and 2,500 mature plants. Founders were positioned in the safe, food-rich frontier region and their initial ages were spread deterministically across the adult age range. This prevented a synchronized age cohort without consuming random numbers. The world was spatially heterogeneous in fertility, food density, and environmental danger. Natural seed rain was fixed at 12 attempts per tick, raw fruit at 20 spawn attempts per tick, the food-detection threshold at 0.01, and the vision horizon at 200. Base food and plant-lifecycle processes maintained a renewable raw-plant staple. Rejected items remained in their grid cells until eaten or stochastically decayed, so a decision could alter the agent's later exposure to the same item.

Agents used body plan 37 under metabolism model v2. Digestible energy was calculated from food composition, food mass, and the body's enzyme profile and then rounded to an integer. Raw fruit had a baseline realized gross energy of 10 and the plant staple had a realized gross energy of 5. E6 applied a raw-fruit-only multiplier after the first rounding step and verified the resulting value in every run output. Aging, starvation death, and toxin-induced acute energy loss and chronic damage were enabled. Except where stated below, runs lasted at most 400 ticks and could end earlier at population extinction. E6 ran for at most 800 ticks, and the legacy-denominator reproduction E4 ran for 3,000 ticks. Simulation ticks and energy are abstract model units and are not mapped to a biological time or calorie scale.

Temporal toxicity was attached to raw fruit. Its toxin fraction was 0.30 and its mass was 1.2, giving an unscaled load of 0.36. In the monotonic profile M, potency was `max(0, 1 - age/120)`. In the non-monotonic profile W, potency was 1 before age 40, 0 from ages 40 through 79, and 1 again from age 80. Resource age was the current simulation tick minus the fruit's creation tick; it was not agent age. Realized toxin excess was `max(0, 0.36 × potency × potency_scale - tolerance)`. A positive excess added five times that value to chronic damage and subtracted 50 times that value from the bite's energy before integer rounding. Constant-potency controls retained the same fruit supply while fixing potency over resource age. This construction separated age dependence from the amount of fruit available.

A code-checked model description following the updated ODD protocol accompanies this draft (Grimm et al., 2020). It records scheduling, state variables, equations, initialization, and implementation pointers. A generated supplement reports the archived launch configuration for all 38 arms in E1-E6 and T2-RB, including the origin of each effective driver value and each code-fixed ecology setting at the clean Git revision recorded by the batch. Its exporter verified the ordered launch flags, horizons, arms, and seeds for all 980 archived run rows. A separate state-and-process catalogue traces movement, food access, eating, toxin, energy, damage, and survival, and a version audit bounds the code differences among batches. Per-run JSON dumps remain the authority for values realized during execution.

### 2.2 Learning representation

The type-only learner stored one value per food implementation type. For a key not previously encountered, the first consumed item initialized its value to the realized post-toxin energy. Subsequent observations used an exponential moving average, `V_new = V_old + 0.3(r - V_old)`, where `r` was the realized energy from that bite. A known food was accepted when its value was at least 0.6 times the highest learned food value. Unfamiliar keys were sampled once, and an agent at or below 6 energy accepted any food regardless of its learned value.

The rescue learner stored separate values for 20-tick resource-age bins, capped at bin 8. The sham learner used the same nine-bin key range, but assigned bins with a deterministic hash of a resource's creation tick and encounter location, so the key carried no age information and consumed no random draw. This control separated information content from nominal memory capacity and repeated first-sample exploration. An avoidance oracle observed realized toxin excess and rejected items with positive excess, except at the shared starvation override. It was a discrimination ceiling, not an optimal survival or fitness policy.

### 2.3 Experiments

#### Study A: Hidden-state cost and behavioral response

E1 used profile M and 20 matched seeds across four arms: food-matched nontoxic fruit (A0), fully potent constant toxicity (A1), monotonic age-dependent detoxification (A2), and constant toxicity calibrated to the preregistered mean-dose target (A3). Its three Holm-controlled tests compared A2-A0 founder attained age, A2-A3 founder attained age, and A2-A1 acceptance conditional on encounter. A1 was a positive control for the learner's ability to avoid a consistently harmful category.

#### Study B: Information rescue

E2 used the same 20 matched seeds in both toxicity profiles. Each profile crossed four decision systems: type-only values (B1), type-by-resource-age values (B2), the capacity-matched sham (B3), and an oracle that rejected any fruit with positive excess toxin (B4). The preregistered primary outcome was the discrimination index, `P(eat | safe encounter) - P(eat | toxic encounter)`, and the causal contrast was B2-B3 within profile. The M profile used monotonic detoxification over 120 ticks; the W profile used the toxic-safe-toxic window.

#### Study C: Within-generation selection

E3 used profile M and introduced experimenter-supplied variation in founder toxin tolerance by spreading the baseline value 0.20 over 0.05 to 0.35. Twenty matched seeds ran A0, A2, and A3. The selection differential was the mean tolerance of the half of founders with the longest attained ages minus the mean tolerance of all founders. Continuous tolerance-age slopes were reported as a mechanism check. No birth occurred, so E3 measured differential survival within the founder cohort and no response to selection across generations.

#### Study D: Exposure-denominator validation

E4 reran the 10 seeds and 3,000-tick configuration of an earlier stationary food-value experiment with encounter telemetry enabled. That experiment used low-value raw seed and higher-value raw plant rather than the raw-fruit toxin system. E4 tested whether raw meal counts understated selectivity when rejected food remained in the world and could be encountered again. It is a measurement validation and is not pooled with E1 or used as evidence about temporal toxicity.

#### Study E: Ecological transfer and within-configuration replication

E5 used profile M and repeated A0, A2, and the original A3 control across 20 matched seeds with the drain multiplier increased from 0.2 to 0.5. This directly increased metabolic energy expenditure and shifted deaths toward starvation while the aging and toxin-damage processes remained active; E5 therefore tested transfer to the composite R-B configuration rather than isolating a single mortality process. Its A2-A3 contrast was exploratory. After observing that result, we preregistered T2-RB with 50 new matched seeds, also under profile M. T2-RB compared A2 with both the original constant-potency control (A3O, scale 0.757811) and a dose-recalibrated control (A3R, scale 0.7506672222220914). A2-A3R was primary and A2-A3O was the direct-replication secondary contrast. No interaction between drain setting and toxicity profile was tested.

#### Study F: Energy-dependent survival effect of resource-age information

After closing the exploratory pilot, we froze the E6 protocol at tag `prereg-resource-age-2026-09-14`. E6 used the non-monotonic toxic-safe-toxic profile W and crossed five realized safe-fruit energies (4, 5, 6, 8, and 10 units) with three representations: type only (B1), type by resource-age bin (B2), and a capacity-matched sham bin (B3). Each of 30 new seeds ran all 15 arms, giving 450 runs. B2-B3 was the registered causal contrast for age-aligned information content, B2-B1 was a prespecified secondary comparison, and B3-B1 is reported descriptively to expose the survival effect of irrelevant partitioning.

### 2.4 Outcomes and statistical analysis

The independent replicate is the seed, with one simulation run per arm within each matched seed. The primary survival outcome for the new confirmatory studies is mean founder follow-up time, computed for each founder as final attained age minus its deterministic initial age and restricted by the prespecified simulation horizon. Arms use matched seeds and are compared with paired differences. We report arm means and standard deviations, mean paired differences, 95% confidence intervals, seeded Monte Carlo two-sided sign-flip tests as prespecified, effect sizes, and directional seed counts. Encounter-dependent behavior is reported as `P(eat | encounter)`; raw meal counts are secondary because rejected food remains available and changes later exposure.

For E6, we computed B2-B3 at each energy within each seed and fitted one ordinary-least-squares slope over the five realized energies. The 30 seed-level slopes were tested with a seeded, two-sided Monte Carlo sign-flip test using 200,000 draws. The preregistered decision rule required a positive mean slope and a 95% CI excluding zero; the smallest effect of scientific interest was 1 follow-up tick per energy unit. Level-specific B2-B3 tests were Holm-adjusted across the five energies. B2-B1 was preregistered as a secondary level-specific comparison without multiplicity adjustment; we additionally report an exploratory Holm correction across its five energy levels to show which nominal findings survive family-wise control. Runtime failures were to be rerun only at the failed arm-seed cell and retained in the audit trail; no failures occurred. Simulations could stop at population extinction. No founder was censored in either new confirmatory study, so the death-only sensitivity equals the primary restricted-mean follow-up outcome.

### 2.5 Execution, provenance, and verification

E6 and T2-RB specifications, seeds, directional rules, exclusions, smallest effects of scientific interest, and analysis procedures were frozen before their outcome files were generated. The tag `prereg-resource-age-2026-09-14` identifies commit `3f1af32f9e37655ed9bee5462526921eff226c8a`. Confirmatory runs were executed from a clean detached worktree at that tag. Each output recorded requested flags, effective model parameters, source revision, platform, Python version, run duration, completion state, and arm/seed identity.

Batch validators required one complete output for every planned arm-by-seed cell, the frozen revision, expected effective parameters, no silent reuse, and explicit failure and censoring fields. All 600 confirmatory cells passed. A SHA-256 manifest covers 616 confirmatory files, including raw dumps and derived results; a separate verification pass reproduced all 616 hashes. Unit and regression tests covered age-key assignment, the capacity-matched sham, raw-fruit-only energy scaling, toxin timing, encounter telemetry, provenance guards, validators, and analysis behavior. Figure scripts consume the frozen result tables and export the plotted seed-level values as CSV. The E4 figure additionally checks `encounters = ate + skipped` and `telemetry ate = raw meals` within every run.

## 3. Results

### 3.1 Hidden toxicity changed behavior and lifespan, but concealment did not add cost beyond toxin dose

All 80 E1 runs completed without failure. Relative to food-matched nontoxic fruit, age-dependent toxicity reduced mean founder attained age by 27.73 ticks (A2-A0, 95% CI -33.69 to -21.77; Holm-adjusted exact sign-flip p=0.00000572; Cliff's delta -0.635). All 20 paired differences were negative. However, A2 did not reduce age relative to the preregistered constant-potency control: A2-A3 was +1.08 ticks (95% CI -2.39 to 4.55; adjusted p=0.522; delta 0.100). Thus E1 supported a cost of toxin exposure but did not support the predicted additional survival cost of hiding toxicity in resource age (Figure 1A).

The behavioral positive control passed. A1's learned fruit value fell to 2.00, below the learned staple value of 5.00, and its mean encounter-conditional acceptance was 0.354. A2 instead learned a mixed value of 7.01 and accepted 0.711 of encounters. The A2-A1 acceptance difference was 0.357 (95% CI 0.323 to 0.391; adjusted p=0.00000572; delta 1.000), showing that the type-only learner could avoid constant toxicity but not resolve age-dependent toxicity (Figure 1B).

### 3.2 Age information restored discrimination because it carried relevant state information

Under the monotonic profile, the type-by-age rescue exceeded the capacity-matched sham by 0.7858 discrimination units (95% CI 0.7650 to 0.8066; Cliff's delta 1.00). Under the toxic-safe-toxic profile, the difference was 0.7515 (95% CI 0.7214 to 0.7815; Cliff's delta 1.00). B2 therefore acquired the intended age-sensitive behavior in both profiles (Figure 2A).

The sham was not behaviorally neutral. Its mean discrimination was slightly negative in E2 and ranged from -0.112 to -0.097 across all five E6 energy levels, while the corresponding type-only range was -0.082 to -0.058. Negative `D` means that an arm accepted a greater fraction of toxic-window encounters than safe-window encounters. Because neither B1 nor B3 encoded age, this sign cannot be interpreted as learned toxin-state discrimination. B3's deterministic pseudo-categories can acquire different values through their encounter histories, and acceptance then changes which persistent fruit are encountered again. The current telemetry does not separate pseudo-category learning from this exposure feedback. B3 is therefore a control for nominal key capacity and repeated first sampling, but its behavioral and survival effects must be reported rather than treated as zero.

### 3.3 Better discrimination did not guarantee longer life

Relative to the type-only learner, the type-by-age learner changed mean founder lifespan by +3.80 ticks under the monotonic profile and -1.29 ticks under the toxic-safe-toxic profile. The avoidance oracle reduced lifespan by 51.96 and 55.47 ticks, respectively, while sharply increasing starvation deaths. In this ecology, rejecting toxic fruit could cost more energy than the avoided toxin damage (Figure 2B).

### 3.4 Toxicity generated a within-generation selection differential

Founder toxin tolerance showed a positive within-generation selection differential under both toxic treatments but not under the nontoxic control. Mean differentials were +0.0034 for A0 (95% CI -0.0022 to 0.0089), +0.0289 for A2 (0.0221 to 0.0358), and +0.0372 for A3 (0.0315 to 0.0430). A2-A0 was +0.0255 (95% CI 0.0191 to 0.0319; exact sign-flip p=0.0000019; Cliff's delta 0.86). The predicted stronger selection under hidden toxicity was not observed: A2-A3 was -0.0083 (95% CI -0.0135 to -0.0032; p=0.0040; delta -0.315). The constant-potency control produced the larger differential, consistent with its greater realized toxin intake. Because all runs remained in generation 0, these effects describe selective survival among founders rather than evolutionary change (Figure 3A).

### 3.5 The separate denominator study validated encounter-conditional acceptance

E4 reproduced the earlier raw-meal means exactly (1,945.3 without learning versus 423.0 with learning) in its stationary raw-seed/raw-plant system and exposed a larger difference in acceptance per opportunity. The value-learning arm encountered the persistent low-value resource 26,945.3 times on average and accepted 0.0161 of encounters, whereas the no-learning arm had 1,945.3 encounters and accepted all of them. The paired acceptance difference was 0.9839 (95% CI 0.9812 to 0.9865; exact sign-flip p=0.00195). Raw meal count therefore understated selectivity because rejection increased later re-encounters (Figure 3B). This result validates the encounter denominator used elsewhere; it is not a toxin-profile comparison.

### 3.6 E6 separated age information from type-only and sham survival effects

All 450 E6 runs under profile W passed the frozen batch validator. Table 1 reports all three arms and the two prespecified contrasts. Relative to B1, B2 increased mean follow-up at energy 4 by +6.475 ticks (95% CI 2.149 to 10.801; unadjusted sign-flip p=0.00425; exploratory Holm-adjusted p=0.02125). At energy 5 the increase was +5.749 ticks (0.754 to 10.744; unadjusted p=0.02614; adjusted p=0.10456), so it was nominal only. Its B2-B1 confidence intervals included zero at energies 6, 8, and 10; their exploratory Holm-adjusted p values were 0.22638, 0.96870, and 0.96870, respectively. Thus only the energy-4 B2-B1 result survived the exploratory five-level family-wise correction.

**Table 1. E6 founder follow-up by representation and realized fruit energy.** Arm entries are mean restricted follow-up ticks across 30 seeds. Contrasts are within-seed mean differences with 95% t CIs. B2-B3 was the registered primary contrast; B2-B1 was prespecified secondary without a preregistered multiplicity correction. Exact unadjusted and exploratory Holm-adjusted p values are reported in the text.

| Energy | B1 mean | B2 mean | B3 mean | B2-B1 [95% CI] | B2-B3 [95% CI] |
|---:|---:|---:|---:|---:|---:|
| 4 | 144.239 | 150.713 | 156.145 | +6.475 [2.149, 10.801] | -5.431 [-8.826, -2.037] |
| 5 | 150.314 | 156.063 | 161.639 | +5.749 [0.754, 10.744] | -5.576 [-9.403, -1.749] |
| 6 | 156.123 | 160.169 | 166.309 | +4.045 [-0.429, 8.520] | -6.141 [-9.989, -2.293] |
| 8 | 172.624 | 171.341 | 178.991 | -1.283 [-4.987, 2.422] | -7.650 [-11.470, -3.830] |
| 10 | 207.595 | 207.078 | 205.713 | -0.517 [-3.406, 2.372] | +1.365 [-2.122, 4.852] |

B3 also changed survival relative to B1. The unregistered descriptive B3-B1 differences were +11.906 ticks at energy 4 (95% CI 7.725 to 16.087), +11.325 at 5 (5.524 to 17.126), +10.186 at 6 (5.700 to 14.672), +6.367 at 8 (1.148 to 11.587), and -1.881 at 10 (-5.410 to 1.647). These results explain how B2 can have positive nominal contrasts against B1 at energies 4 and 5 while still underperforming B3: irrelevant partitioning itself produced a survival advantage over type-only valuation through energy 8. Because B3-B1 was not a registered inferential family, these intervals are descriptive and do not establish a general benefit of arbitrary memory partitioning.

The registered B2-B3 analysis asks the narrower causal question of whether age alignment adds benefit beyond the same nominal key capacity. The level-specific differences were -5.431 ticks at energy 4 (95% CI -8.826 to -2.037; Holm-adjusted p=0.0120), -5.576 at 5 (-9.403 to -1.749; adjusted p=0.0120), -6.141 at 6 (-9.989 to -2.293; adjusted p=0.0120), -7.650 at 8 (-11.470 to -3.830; adjusted p=0.00265), and +1.365 at 10 (-2.122 to 4.852; adjusted p=0.4448). Age alignment therefore carried a survival cost relative to the sham at energies 4 through 8, with no detected difference at 10.

Across levels, the mean seed-level B2-B3 slope was 0.890 ticks per energy unit (SD 2.227; median 0.381; 95% t CI 0.059 to 1.722; bootstrap CI 0.130 to 1.696; seeded two-sided sign-flip p=0.0365). Eighteen of 30 slopes were positive and 12 were negative. The manuscript H2 decision rule, registered as H6.1 in the frozen protocol, was therefore met. The point estimate was slightly below the preregistered smallest effect of scientific interest of 1 tick per energy unit, while its confidence interval included that threshold.

The mechanism gate passed at all five levels. B2's mean discrimination index ranged from 0.654 to 0.748; B1 ranged from -0.082 to -0.058 and B3 from -0.112 to -0.097. Every B2 run contained all nine resource-age keys and assigned higher learned values to safe bins than to toxic bins. Mean fruit encounters per founder ranged from 48.7 to 65.5 across energy levels, above the preregistered threshold of 30. A stricter post hoc check found that individual runs fell below 30 at energies 4, 5, and 6. This does not change the preregistered level-mean gate, but it limits claims that every seed had equally strong exposure.

A leave-one-energy-out analysis was conducted after seeing the primary result and is descriptive only. The slope remained positive with a confidence interval excluding zero when energies 4, 5, 6, or 8 were omitted. Omitting energy 10 changed the slope to -0.58 ticks per energy unit (95% CI -1.85 to 0.70; p=0.36). The primary linear result therefore depends materially on the highest-energy endpoint and should not be described as a smooth gradient across the full range (Figure 4).

### 3.7 R-B replication within the high-drain configuration

The exploratory E5 transfer first suggested a deficit in R-B: A2-A3O was -6.15 ticks across 20 matched seeds (95% CI -12.01 to -0.29; p=0.042), opposite to the preregistered E5 prediction. The drain manipulation changed both energy expenditure and damage accumulation, and this contrast was not the primary registered test, so it motivated rather than substituted for a new replication. No cross-experiment interaction was tested.

All 150 R-B replication runs passed the frozen batch validator. Across 50 matched seeds, age-varying toxicity (A2) reduced mean founder follow-up relative to the recalibrated constant-potency control (A3R) by 7.928 ticks (95% t CI -11.046 to -4.810; bootstrap CI -10.967 to -4.938; two-sided sign-flip p=0.000020). Thirty-eight seeds favored A3R, 12 favored A2, and none tied. The point estimate exceeded the preregistered 5-tick smallest effect of scientific interest, although the t interval narrowly included -5. The direct-replication comparison with the original constant-potency control (A3O) agreed: A2-A3O was -7.102 ticks (95% CI -10.218 to -3.985; p=0.000035). The two control definitions therefore led to the same directional conclusion. Unpaired Cliff's delta was negligible for both contrasts (-0.134 and -0.118), reflecting large between-seed overlap despite the matched-seed difference (Figure 5).

## 4. Discussion

### 4.1 Information sufficiency and information value are different questions

The rescue experiment establishes the representational result directly. B2 and B3 offered the learner the same nominal nine-key range and the same first-sample and update rules. Only B2 aligned those keys with resource age. B2 then separated safe from toxic encounters in both the monotonic and toxic-safe-toxic profiles, while B3 remained slightly negative. Every confirmatory B2 run also populated all nine keys and learned a higher value for safe than toxic bins. Extra storage or repeated exploration alone therefore does not explain B2's positive discrimination. At the same time, B3's negative discrimination and its survival advantage over B1 at four energy levels show that the sham altered behavior and ecological outcomes. The B2-B3 contrast controls capacity, but it compares two active partitioning rules rather than an informative treatment with an inert placebo.

That result answers whether the supplied representation is sufficient for the behavioral distinction. It does not answer whether the changed behavior improves survival. The difference matters because formal fitness-value arguments compare optimized responses over relevant long-run consequences (Donaldson-Matasci et al., 2010). These agents instead used a fixed exponential moving average, a fixed relative-value threshold, and a starvation override. The experiment measures the consequence of adding state information to that particular bounded policy. It does not estimate the expected value of perfect information for an optimal decision maker.

This distinction also explains why describing B4 as an optimal policy would be incorrect. The oracle observed realized toxin excess and nearly maximized safe-versus-toxic discrimination, but it optimized only the immediate rule “avoid positive excess toxin,” subject to the starvation override. It did not compare the lifetime energy gained from fruit with acute damage, chronic damage, future search, or mortality risk. Its 52- to 55-tick deficit and greater starvation mortality show that perfect toxin classification can be coupled to a poor ecological objective.

### 4.2 Representation changes generalization and action

The type-only learner generalized every raw-fruit outcome to a single value. This compression was useful when the correct action was stable across fruit encounters and harmful when safe and toxic ages called for different actions. E1's positive control showed that the same learner could avoid a consistently harmful fruit category: its learned fruit value fell below the staple and acceptance declined. Under age-dependent toxicity, post-ingestive outcomes were averaged, the fruit value remained above the staple, and acceptance stayed high. The limitation was therefore not a complete inability to learn from consequences. It was an inability to condition that learning on a state absent from the key.

B2 reduced this aliasing by splitting experience over resource-age bins. The split imposed its own learning dynamics: each unfamiliar bin had to be sampled, and estimates generalized over fewer observations. B3 controlled the nominal number of bins and that repeated first-sample burden without supplying the relevant temporal structure. The B2-B3 contrast therefore identifies the effect of aligning memory with resource state under a common capacity, although it does not claim that all possible exploration histories or key-frequency distributions were identical.

The ecological consequence came from the action induced by the representation. B2's higher discrimination meant that it rejected more toxic fruit. Rejection lowered toxin exposure but also relinquished energy and left the resource in the world for possible re-encounter. B1 and B3 instead accepted toxic-window fruit more often than safe-window fruit on the encounter-conditional scale. For B3, deterministic hash bins created history-dependent pseudo-categories that could change later acceptance despite carrying no intended age signal. In the present model, classifying toxicity was only one component of the survival problem, and an irrelevant representation could still alter survival through exploration and exposure.

The first-taste rule also gives ingestion two roles: it provides immediate energy and supplies the observation used to update the value map. This resembles the coupling of sampling and feeding studied by Scholz et al. (2017), but here the consequence can include toxin damage and the acquired information is stored under an experimentally manipulated key. The B2 result shows that receiving the relevant state distinction changes what can be learned from the sample; the survival result shows that the resulting exploitation rule must still be evaluated in its resource economy. The separation parallels Borg and Channon's (2020) finding that access to information can change behavior even when poisonous-food discrimination does not improve: behavioral responsiveness and task benefit require separate outcomes.

### 4.3 Payoff bounded the registered contrast; drain comparisons remain descriptive

E6 met its preregistered directional decision rule: the mean B2-B3 slope was positive and its 95% interval excluded zero. The strength and shape of the result require restraint. The estimate of 0.890 tick per energy unit was slightly smaller than the preregistered 1-tick smallest effect of scientific interest, and 12 of 30 seed-level slopes were negative. More decisively, the level-specific estimates did not show a sequence of increasingly positive benefits. B2 outperformed the type-only B1 at energy 4 after the exploratory five-level Holm correction; the energy-5 result was positive only at the nominal, unadjusted level. The sham B3 improved still more. B2 had lower follow-up than B3 at energies 4, 5, 6, and 8, while the energy-10 contrast was positive but imprecise and not significant after Holm adjustment. Removing that endpoint erased the positive B2-B3 slope.

The supported interpretation is therefore an attenuation of a survival cost at the upper tested payoff, not a smooth dose-response curve and not proof of a general break-even point. One plausible process is that B2's selective rejection sacrifices energy at lower fruit payoffs, whereas a high safe-fruit payoff better compensates the costs of sampling and selective intake. The observed discrimination and starvation pattern support the presence of the toxin-energy trade-off, but the current factorial design does not decompose learning cost, search cost, acute toxin cost, and chronic damage into separate causal paths. A denser, newly preregistered energy series around the upper endpoint would be needed to locate a transition.

The comparisons across E1 and E5 are descriptive. E1 used drain multiplier 0.2 and found no A2-A3 difference; exploratory E5 used 0.5 and found an A2 deficit. Those experiments also differed in run realization and were not analyzed in a factorial model, so they do not estimate a drain-by-toxicity-profile interaction. T2-RB provides a stronger conclusion within the high-drain configuration: with new matched seeds, profile-M age-varying toxicity reduced follow-up relative to both constant-potency controls. It replicates that within-configuration deficit. Establishing drain as a moderator would require a newly preregistered factorial experiment that crosses drain and toxicity profile within one seed design.

### 4.4 Selection within a cohort is not evolutionary change

E3 provides a separate view of the toxin mechanism. When founders varied in toxin tolerance, the longer-lived half of the cohort had higher mean tolerance under both toxic conditions and not under the nontoxic control. This is a within-generation selection differential: a statistical association between a supplied trait and differential survival. The constant-potency arm produced a larger differential than the age-dependent arm, contrary to the prediction that concealment would intensify selection. Its greater realized toxin intake provides a mechanistically consistent explanation.

No births occurred, so the model did not realize inheritance, reproduction, or a response to selection in these experiments. Calling the E3 pattern “evolution” would collapse distinct levels of evidence. The result supports selective survival among founders and shows that the toxin implementation can act on tolerance. Demonstrating evolutionary change would require sustained reproduction, transmission of tolerance, and a preregistered population-level change across generations.

### 4.5 Exposure is partly produced by behavior

E4 exposed a measurement issue that matters beyond this particular model. A rejected food item remained in place and could be encountered again. Consequently, learning reduced low-value meals from 1,945.3 to 423.0 per run while increasing mean encounters from 1,945.3 to 26,945.3. The raw meal ratio suggested a 4.6-fold difference, whereas acceptance conditional on encounter differed by approximately 62-fold. The act of rejection changed the denominator of future opportunities.

This feedback means that meal count is not a direct measure of selectivity in a persistent-resource environment. It combines the probability of accepting an encountered item with the exposure process generated by earlier choices. We therefore treat `P(eat | encounter)` as the behavioral outcome and report meals and encounters separately. The telemetry invariant that every no-learning encounter became a meal, together with exact reproduction of the historical meal totals, provides a direct check on the denominator.

### 4.6 Evidential strengths and remaining uncertainty

Several design features narrow the causal claims. Matched seeds reduce variation from shared stochastic initial conditions. The B3 sham distinguishes information content from nominal key capacity. Constant-potency controls distinguish temporal state dependence from fruit supply and approximate toxin dose. The E6 payoff manipulation changes raw-fruit energy after the common metabolic calculation while leaving staple energy fixed, and effective realized values are checked in outputs. The analysis reports null, opposite-direction, and endpoint-dependent findings rather than retaining only supportive contrasts.

The confirmatory work was separated from the exploratory pilot by a frozen tag and new seed ranges. Validators checked every planned cell and its effective parameters, and the raw and derived files have a verified checksum manifest. These controls protect the interpretation from silent parameter failure and incomplete batches. They do not remove model uncertainty or make a single implementation representative of biological foraging.

### 4.7 Limitations and next tests

- Food age was supplied as a perfect cue; agents did not discover it.
- The value rule was fixed rather than evolved.
- The simulation did not produce births in the E-series, so no cross-generational evolutionary response was measured.
- The avoidance oracle optimized toxin avoidance only and was not an optimal policy.
- The chosen energy, toxin, metabolism, and renewal regimes delimit the quantitative conclusions, and simulation units are not calibrated to a biological species.
- The E6 linear trend depended materially on the energy-10 endpoint; the experiment did not establish a smooth response curve or locate a general break-even payoff.
- Some individual E6 runs at energies 4-6 fell below the post hoc stricter threshold of 30 fruit encounters per founder, although every preregistered level mean exceeded 30 and every B2 run showed the learned safe-versus-toxic value separation.
- The current study does not implement storing food for later detoxification.

The next discriminating experiments are specific. A dense, preregistered energy series near 8-12 would test whether the energy-10 pattern replicates and estimate a transition without reusing the current seeds. A factorial manipulation of payoff and metabolic drain would separate their interaction from the composite R-B transfer. Replacing perfect age with noisy or learned sensory cues would test whether the rescue survives realistic observation error. Comparing the fixed learner with a policy optimized for survival would connect the empirical B2-B3 effect to formal decision value. Finally, enabling sustained reproduction would permit a separate study of evolutionary response. These are extensions of the current claim boundary rather than conditions for interpreting the completed experiments.

## 5. Conclusion

Resource-age information solved the hidden-state discrimination problem under both monotonic and toxic-safe-toxic profiles. In E6, B2 improved survival relative to the type-only learner at fruit energy 4 after an exploratory five-level Holm correction; the energy-5 increase was nominal only. The capacity-matched sham produced larger survival gains through energy 8, however, so age alignment carried a cost relative to B3 at four of five levels. The registered positive B2-B3 slope depended on the energy-10 endpoint and did not establish a smooth payoff response. Separately, T2-RB supported a within-configuration cost of monotonic age-varying toxicity relative to two constant-potency controls. Representation, comparison policy, and resource ecology jointly determined the survival result.

## Data and Code Availability

The release package has been assembled locally as five licensed bundles containing the 600 confirmatory raw dumps, derived evidence, manuscript and methods files, frozen preregistration, and the focal code and tests. A machine-readable inventory and flat SHA-256 list verify 696 files. **[Insert the versioned public archive citation, DOI, and code-release tag after deposit and download-back verification; do not submit this placeholder.]**

## Supplementary Materials

The working supplement contains the ODD model description; the complete experiment launch-parameter and code-fixed-setting tables; the focal state/process catalogue; the code-version audit; an independent-reproduction protocol and deterministic smoke signatures; preregistration and validation records; source-data tables for all figures; the analysis and figure-generation scripts; and a public-archive manifest with machine-readable inventory and checksums. Public archive links will be finalized after deposit.

## Funding

**[Author confirmation required. If accurate: This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.]**

## Competing Interests

**[Author confirmation required. If accurate: The author declares no competing interests.]**

## Ethics Statement

**[Author confirmation required. Proposed statement: This study used only computer simulations and involved no human participants or live animals; institutional ethics approval was therefore not required.]**

## Author Contributions

**[Author confirmation required. Complete a CRediT statement covering conceptualization, methodology, software, validation, formal analysis, investigation, data curation, visualization, writing, and project administration.]**

## Generative-AI Disclosure

**[Author approval required; add any AI use not recorded here.]** OpenAI Codex using GPT-6 (OpenAI, 2026; https://openai.com/codex/; accessed September 13–14, 2026) assisted with code and evidence audits, experiment and analysis tooling, execution checks, literature screening, figures, parameter exports, and drafting and editing manuscript and supplement text. The human author made the scientific decisions and is responsible for verifying the source papers, code, outputs, statistics, figures, claims, citations, and submitted wording. A detailed task-level record is included in the supplementary AI-use log.

## References

Borg, J. M., & Channon, A. (2020). The effect of social information use without learning on the evolution of social behavior. *Artificial Life, 26*(4), 431–454. https://doi.org/10.1162/artl_a_00328

Bullinaria, J. A. (2017). Imitative and direct learning as interacting factors in life history evolution. *Artificial Life, 23*(3), 374–405. https://doi.org/10.1162/ARTL_a_00237

Chrisman, L. (1992). Reinforcement learning with perceptual aliasing: The perceptual distinctions approach. In *Proceedings of the Tenth National Conference on Artificial Intelligence* (pp. 183–188). AAAI Press. https://cdn.aaai.org/AAAI/1992/AAAI92-029.pdf

Dall, S. R. X., Giraldeau, L.-A., Olsson, O., McNamara, J. M., & Stephens, D. W. (2005). Information and its use by animals in evolutionary ecology. *Trends in Ecology & Evolution, 20*(4), 187–193. https://doi.org/10.1016/j.tree.2005.01.010

Donaldson-Matasci, M. C., Bergstrom, C. T., & Lachmann, M. (2010). The fitness value of information. *Oikos, 119*(2), 219–230. https://doi.org/10.1111/j.1600-0706.2009.17781.x

Dorin, A., & Stepney, S. (2024). What is Artificial Life today, and where should it go? *Artificial Life, 30*(1), 1–15. https://doi.org/10.1162/artl_e_00435

Gershenson, C., Trianni, V., Werfel, J., & Sayama, H. (2020). Self-organization and Artificial Life. *Artificial Life, 26*(3), 391–408. https://doi.org/10.1162/artl_a_00324

Giannakakis, E., Khajehabdollahi, S., & Levina, A. (2025). Network bottlenecks and task structure control the evolution of interpretable learning rules in a foraging agent. *Artificial Life, 31*(2), 177–194. https://doi.org/10.1162/artl_a_00458

Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., Giske, J., Groeneveld, J., Johnston, A. S. A., Miles, A., Nabe-Nielsen, J., Polhill, J. G., Radchuk, V., Rohwäder, M.-S., Stillman, R. A., Thiele, J. C., & Ayllón, D. (2020). The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism. *Journal of Artificial Societies and Social Simulation, 23*(2), Article 7. https://doi.org/10.18564/jasss.4259

Ha, D. (2019). Reinforcement learning for improving agent design. *Artificial Life, 25*(4), 352–365. https://doi.org/10.1162/artl_a_00301

OpenAI. (2026). *Codex (GPT-6)* [Large language model]. https://openai.com/codex/

Scholz, M., Dinner, A. R., Levine, E., & Biron, D. (2017). Stochastic feeding dynamics arise from the need for information and energy. *Proceedings of the National Academy of Sciences, 114*(35), 9261–9266. https://doi.org/10.1073/pnas.1703958114

## Figure captions

**Figure 1. Hidden toxicity changed survival and behavior.** (A) Mean founder attained age in E1 under food-matched nontoxic fruit (A0), fully potent constant toxicity (A1), age-dependent toxicity (A2), and the dose-matched constant-potency control (A3). (B) Acceptance conditional on fruit encounter. Colored points are independent seeds; black diamonds and bars are means and descriptive 95% t intervals.

**Figure 2. Resource-age information restored discrimination without guaranteeing survival benefit.** (A) Safe-minus-toxic acceptance under type-only (B1), type-by-age (B2), capacity-matched sham (B3), and avoidance-oracle (B4) policies in monotonic and toxic-safe-toxic profiles. (B) Within-seed attained-age differences relative to B1. Points are independent seeds; diamonds and bars are means and descriptive 95% t intervals.

**Figure 3. Within-generation selection and the exposure-denominator check.** (A) E3 toxin-tolerance selection differentials for the nontoxic, age-dependent, and constant-potency arms. No births occurred. (B) E4 acceptance per low-value raw-seed encounter with value learning disabled or enabled; annotations give mean raw meals and telemetry-deduplicated encounters. Points are independent seeds; diamonds and bars are means and descriptive 95% t intervals.

**Figure 4. Confirmatory survival effects and mechanism across risky-resource payoffs.** (A) E6 paired restricted mean founder follow-up contrasts for B2-B3, B2-B1, and the descriptive B3-B1 comparison at five realized fruit energies. Thin gray lines show within-seed B2-B3 values; colored markers and bars show contrast means and 95% t intervals. (B) Discrimination for the type-only, resource-age, and sham representations. All 450 profile-W runs passed the frozen validator.

**Figure 5. Preregistered R-B replication.** Paired founder follow-up contrasts for age-varying toxicity against the original (A3O) and recalibrated (A3R) constant-potency controls. Colored points are seed-level paired differences; gray lines connect contrasts within seed; black diamonds and bars are means and 95% t intervals. The dashed line marks the preregistered -5-tick smallest effect of scientific interest. All 150 runs passed the frozen validator.
