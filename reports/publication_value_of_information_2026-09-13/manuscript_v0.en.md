# When Does a Better Representation Pay? Survival Effects of Resource-Age Information in Artificial Foraging Under Temporal Toxicity

**Manuscript type:** Article

**Target journal:** *Artificial Life* (provisional; current author instructions and article fit must be verified before formatting)

**Author:** Chisanupong Injun
**Status:** confirmatory results integrated; core methods and screened literature drafted; full ODD supplement and public archive still incomplete

## Abstract

Artificial foragers can learn food values from post-ingestive outcomes while still failing when one perceptual category combines ecologically different states. We studied agents that stored one value per food type while fruit toxicity changed with food age. Adding resource age to the value key restored safe-versus-toxic discrimination, whereas a capacity-matched sham did not. In a preregistered confirmatory experiment spanning five realized fruit energies, the seed-level linear slope of the rescue-minus-sham survival effect was positive (0.890 restricted-mean follow-up ticks per energy unit, 95% t CI 0.059 to 1.722; two-sided sign-flip p=0.0365). The point estimate was slightly below the preregistered smallest effect of scientific interest. Level-specific effects were negative at energies 4, 5, 6, and 8 and indistinguishable from zero at 10, so the gradient reflected attenuation of a survival cost at the upper endpoint rather than a demonstrated survival benefit throughout the range. A separate 50-seed replication found shorter follow-up under age-varying toxicity than under a recalibrated constant-potency control (mean paired difference -7.928 ticks, 95% CI -11.046 to -4.810). These results separate representational sufficiency from ecological benefit: information can improve state-sensitive behavior while the fixed policy that uses it still reduces survival under most tested payoffs.

**Keywords:** artificial life; value of information; embodied foraging; perceptual aliasing; partial observability; temporal toxicity; state representation

## 1. Introduction

### 1.1 Problem

Outcome-grounded learning can estimate the average consequence of a food category without representing every state that determines that consequence. When toxicity changes with food age, a type-only estimate combines safe and toxic encounters. This is a form of perceptual aliasing: situations that require different responses are indistinguishable to the decision rule (Chrisman, 1992). An action cannot depend on resource age when age, or a correlated cue, is absent from the decision key.

The existence of this representational limit is established in reinforcement-learning research. Ecological accounts add a second requirement: uncertainty reduction should be evaluated through the decisions and functional consequences it enables (Dall et al., 2005). Formal fitness value further assumes a response chosen to improve long-run fitness (Donaldson-Matasci et al., 2010). Our fixed learner and within-lifetime survival outcome do not satisfy that definition. The empirical question here is narrower: **when does resolving the hidden resource state improve survival-relevant outcomes, and when does it fail to do so?**

### 1.2 Contribution

This article makes three bounded contributions:

1. It demonstrates a full-ecology failure of type-only food valuation under age-dependent toxicity.
2. It uses a resource-age-key rescue and a capacity-matched sham control to identify information as the cause of restored discrimination.
3. It measures whether the survival effect of that information changes with the energetic value of the risky resource.

This focus complements recent artificial-life work showing that task structure and architectural constraints change the learning rules and performance that evolve in embodied foragers (Giannakakis et al., 2025). Here the learning rule is held fixed so that resource-state representation and ecological payoff can be manipulated directly.

The article does not claim that perceptual aliasing is new, that agents discovered food age, or that an evolutionary response occurred across generations.

### 1.3 Hypotheses

**H1: Information sufficiency.** A type-by-age value key produces greater safe-versus-toxic discrimination than a type-only key and a capacity-matched sham key.

**H2: Survival effect of state information.** The paired lifespan difference between the type-by-age learner and the capacity-matched sham changes systematically as risky-fruit energy changes. This is an empirical effect for fixed learning policies, not expected value of perfect information and not reproductive fitness.

**H3: Regime dependence.** The cost of hidden toxicity relative to dose-matched observable toxicity is tested in a new, preregistered R-B replication and is reported regardless of direction.

## 2. Methods

### 2.1 Artificial ecology

The focal experiments used a 100 × 100 discrete world initialized with 50 mortal founders and 2,500 plants. Natural seed rain was fixed at 12, the food-detection threshold at 0.01, and the vision horizon at 200. Agents used body plan 37 under metabolism model v2. Aging, starvation death, and toxin-induced acute energy loss and chronic damage were enabled. The realized gross energy values were 10 for raw fruit and 5 for the plant staple; E6 multiplied raw-fruit energy only and verified the realized values in every output. Except where stated below, runs lasted at most 400 ticks and could end earlier at population extinction. E6 ran for at most 800 ticks, and the legacy-denominator reproduction E4 ran for 3,000 ticks.

Temporal toxicity was attached to raw fruit. In the monotonic profile M, potency declined with resource age over a 120-tick detoxification interval. In the non-monotonic profile W, fruit was toxic before age 40, safe from ages 40 through 79, and toxic again from age 80. Resource age was the current simulation tick minus the fruit's creation tick; it was not agent age. A consumed toxic fruit imposed an acute energy penalty proportional to excess toxin above the agent's tolerance and added chronic damage. Constant-potency controls retained the same fruit supply while removing the age-dependent hidden state.

A complete model description is being prepared using the updated ODD protocol (Grimm et al., 2020).

### 2.2 Learning representation

The type-only learner stored one value per food implementation type. The rescue learner stored separate values for type-by-age bins. The sham learner used the same number of keys as the rescue learner, but key assignment carried no age information. An avoidance oracle observed toxicity and rejected items with positive excess dose; it was a discrimination ceiling, not an optimal fitness policy.

### 2.3 Experiments

#### Study A: Hidden-state cost and behavioral response

E1 used 20 matched seeds across four arms: food-matched nontoxic fruit (A0), fully potent constant toxicity (A1), age-dependent monotonic detoxification (A2), and constant toxicity calibrated to the preregistered mean-dose target (A3). Its three Holm-controlled tests compared A2-A0 founder attained age, A2-A3 founder attained age, and A2-A1 acceptance conditional on encounter. A1 was a positive control for the learner's ability to avoid a consistently harmful category. E4 separately reran the 10 seeds and 3,000-tick configuration of an earlier food-value experiment with encounter telemetry enabled. E4 tested whether raw meal counts understated selectivity when rejected food remained in the world and could be encountered again.

#### Study B: Information rescue

E2 used the same 20 matched seeds in both toxicity profiles. Each profile crossed four decision systems: type-only values (B1), type-by-resource-age values (B2), the capacity-matched sham (B3), and an oracle that rejected any fruit with positive excess toxin (B4). The preregistered primary outcome was the discrimination index, `P(eat | safe encounter) - P(eat | toxic encounter)`, and the causal contrast was B2-B3 within profile. The M profile used monotonic detoxification over 120 ticks; the W profile used the toxic-safe-toxic window.

#### Study C: Within-generation selection

E3 introduced experimenter-supplied variation in founder toxin tolerance by spreading the baseline value 0.20 over 0.05 to 0.35. Twenty matched seeds ran A0, A2, and A3. The selection differential was the mean tolerance of the half of founders with the longest attained ages minus the mean tolerance of all founders. Continuous tolerance-age slopes were reported as a mechanism check. No birth occurred, so E3 measured differential survival within the founder cohort and no response to selection across generations.

#### Study D: Ecological-regime transfer

E5 repeated A0, A2, and the original A3 control across 20 matched seeds with the drain multiplier increased from 0.2 to 0.5. This simultaneously increased metabolic drain and damage accumulation and shifted deaths toward starvation; E5 therefore tested transfer to the composite R-B regime rather than isolating food scarcity. Its A2-A3 contrast was exploratory. After observing that result, we preregistered T2-RB with 50 new matched seeds. T2-RB compared A2 with both the original constant-potency control (A3O, scale 0.757811) and a dose-recalibrated control (A3R, scale 0.7506672222220914). A2-A3R was primary and A2-A3O was the direct-replication secondary contrast.

#### Study E: Energy-dependent survival effect of resource-age information

After closing the exploratory pilot, we froze the E6 protocol at tag `prereg-resource-age-2026-09-14`. E6 crossed five realized safe-fruit energies (4, 5, 6, 8, and 10 units) with three representations: type only (B1), type by resource-age bin (B2), and a capacity-matched sham bin (B3). Each of 30 new seeds ran all 15 arms, giving 450 runs. B2-B3 was the causal contrast for information content; B1 was a secondary baseline.

### 2.4 Outcomes and statistical analysis

The independent replicate is the seed, with one simulation run per arm within each matched seed. The primary survival outcome for the new confirmatory studies is mean founder follow-up time, computed for each founder as final attained age minus its deterministic initial age and restricted by the prespecified simulation horizon. Arms use matched seeds and are compared with paired differences. We report arm means and standard deviations, mean paired differences, 95% confidence intervals, seeded Monte Carlo two-sided sign-flip tests as prespecified, effect sizes, and directional seed counts. Encounter-dependent behavior is reported as `P(eat | encounter)`; raw meal counts are secondary because rejected food remains available and changes later exposure.

For E6, we computed B2-B3 at each energy within each seed and fitted one ordinary-least-squares slope over the five realized energies. The 30 seed-level slopes were tested with a seeded, two-sided Monte Carlo sign-flip test using 200,000 draws. The preregistered decision rule required a positive mean slope and a 95% CI excluding zero; the smallest effect of scientific interest was 1 follow-up tick per energy unit. Level-specific B2-B3 tests were Holm-adjusted across the five energies. Runtime failures were to be rerun only at the failed arm-seed cell and retained in the audit trail; no failures occurred. Simulations could stop at population extinction. No founder was censored in either new confirmatory study, so the death-only sensitivity equals the primary restricted-mean follow-up outcome.

## 3. Results

### 3.1 Hidden toxicity changed behavior and lifespan, but concealment did not add cost beyond toxin dose

All 80 E1 runs completed without failure. Relative to food-matched nontoxic fruit, age-dependent toxicity reduced mean founder attained age by 27.73 ticks (A2-A0, 95% CI -33.69 to -21.77; Holm-adjusted exact sign-flip p=0.00000572; Cliff's delta -0.635). All 20 paired differences were negative. However, A2 did not reduce age relative to the preregistered constant-potency control: A2-A3 was +1.08 ticks (95% CI -2.39 to 4.55; adjusted p=0.522; delta 0.100). Thus E1 supported a cost of toxin exposure but did not support the predicted additional survival cost of hiding toxicity in resource age (Figure 1A).

The behavioral positive control passed. A1's learned fruit value fell to 2.00, below the learned staple value of 5.00, and its mean encounter-conditional acceptance was 0.354. A2 instead learned a mixed value of 7.01 and accepted 0.711 of encounters. The A2-A1 acceptance difference was 0.357 (95% CI 0.323 to 0.391; adjusted p=0.00000572; delta 1.000), showing that the type-only learner could avoid constant toxicity but not resolve age-dependent toxicity (Figure 1B).

E4 reproduced the earlier raw-meal means exactly (1,945.3 without learning versus 423.0 with learning) and exposed a larger difference in acceptance per opportunity. The value-learning arm encountered the persistent resource 26,945.3 times on average and accepted 0.0161 of encounters, whereas the no-learning arm had 1,945.3 encounters and accepted all of them. The paired acceptance difference was 0.9839 (95% CI 0.9812 to 0.9865; exact sign-flip p=0.00195). Raw meal count therefore understated selectivity because rejection increased later re-encounters (Figure 3B).

### 3.2 Age information restored discrimination because it carried relevant state information

Under the monotonic profile, the type-by-age rescue exceeded the capacity-matched sham by 0.7858 discrimination units (95% CI 0.7650 to 0.8066; Cliff's delta 1.00). Under the toxic-safe-toxic profile, the difference was 0.7515 (95% CI 0.7214 to 0.7815; Cliff's delta 1.00). The sham key remained near zero discrimination, showing that the rescue was caused by age information rather than additional key capacity (Figure 2A).

### 3.3 Better discrimination did not guarantee longer life

Relative to the type-only learner, the type-by-age learner changed mean founder lifespan by +3.80 ticks under the monotonic profile and -1.29 ticks under the toxic-safe-toxic profile. The avoidance oracle reduced lifespan by 51.96 and 55.47 ticks, respectively, while sharply increasing starvation deaths. In this ecology, rejecting toxic fruit could cost more energy than the avoided toxin damage (Figure 2B).

### 3.4 Toxicity generated a within-generation selection differential

Founder toxin tolerance showed a positive within-generation selection differential under both toxic treatments but not under the nontoxic control. Mean differentials were +0.0034 for A0 (95% CI -0.0022 to 0.0089), +0.0289 for A2 (0.0221 to 0.0358), and +0.0372 for A3 (0.0315 to 0.0430). A2-A0 was +0.0255 (95% CI 0.0191 to 0.0319; exact sign-flip p=0.0000019; Cliff's delta 0.86). The predicted stronger selection under hidden toxicity was not observed: A2-A3 was -0.0083 (95% CI -0.0135 to -0.0032; p=0.0040; delta -0.315). The constant-potency control produced the larger differential, consistent with its greater realized toxin intake. Because all runs remained in generation 0, these effects describe selective survival among founders rather than evolutionary change (Figure 3A).

### 3.5 The survival effect of resource-age information changed with risky-resource energy

All 450 E6 runs passed the frozen batch validator. The mean seed-level B2-B3 slope was 0.890 ticks per energy unit (SD 2.227; median 0.381; 95% t CI 0.059 to 1.722; bootstrap CI 0.130 to 1.696; seeded two-sided sign-flip p=0.0365). Eighteen of 30 slopes were positive and 12 were negative. The manuscript H2 decision rule, registered as H6.1 in the frozen protocol, was therefore met. The point estimate was slightly below the preregistered smallest effect of scientific interest of 1 tick per energy unit, while its confidence interval included that threshold.

The level-specific pattern qualified the linear result. Mean B2-B3 follow-up differences were -5.431 ticks at energy 4 (95% CI -8.826 to -2.037; Holm-adjusted p=0.0120), -5.576 at 5 (-9.403 to -1.749; adjusted p=0.0120), -6.141 at 6 (-9.989 to -2.293; adjusted p=0.0120), -7.650 at 8 (-11.470 to -3.830; adjusted p=0.00265), and +1.365 at 10 (-2.122 to 4.852; adjusted p=0.4448). Thus, resource-age information did not show a confirmed survival benefit at any single tested level. The positive preregistered slope arose because the survival cost detected from energies 4 through 8 was no longer detected at energy 10.

The mechanism gate passed at all five levels. B2's mean discrimination index ranged from 0.654 to 0.748, while B3 ranged from -0.112 to -0.097. Every B2 run contained all nine resource-age keys and assigned higher learned values to safe bins than to toxic bins. Mean fruit encounters per founder ranged from 48.7 to 65.5 across energy levels, above the preregistered threshold of 30. A stricter post hoc check found that individual runs fell below 30 at energies 4, 5, and 6. This does not change the preregistered level-mean gate, but it limits claims that every seed had equally strong exposure.

A leave-one-energy-out analysis was conducted after seeing the primary result and is descriptive only. The slope remained positive with a confidence interval excluding zero when energies 4, 5, 6, or 8 were omitted. Omitting energy 10 changed the slope to -0.58 ticks per energy unit (95% CI -1.85 to 0.70; p=0.36). The primary linear result therefore depends materially on the highest-energy endpoint and should not be described as a smooth gradient across the full range (Figure 4).

### 3.6 Regime replication

The exploratory E5 transfer first suggested a deficit in R-B: A2-A3O was -6.15 ticks across 20 matched seeds (95% CI -12.01 to -0.29; p=0.042), opposite to the preregistered E5 prediction. The drain manipulation changed both energy expenditure and damage accumulation, and this contrast was not the primary registered test, so it motivated rather than substituted for a new replication.

All 150 R-B replication runs passed the frozen batch validator. Across 50 matched seeds, age-varying toxicity (A2) reduced mean founder follow-up relative to the recalibrated constant-potency control (A3R) by 7.928 ticks (95% t CI -11.046 to -4.810; bootstrap CI -10.967 to -4.938; two-sided sign-flip p=0.000020). Thirty-eight seeds favored A3R, 12 favored A2, and none tied. The point estimate exceeded the preregistered 5-tick smallest effect of scientific interest, although the t interval narrowly included -5. The direct-replication comparison with the original constant-potency control (A3O) agreed: A2-A3O was -7.102 ticks (95% CI -10.218 to -3.985; p=0.000035). The two control definitions therefore led to the same directional conclusion. Unpaired Cliff's delta was negligible for both contrasts (-0.134 and -0.118), reflecting large between-seed overlap despite the matched-seed difference (Figure 5).

## 4. Discussion

### 4.1 Information sufficiency and information value are different questions

The rescue experiment shows that resource-age information is sufficient for state-sensitive discrimination. Its survival consequence is a separate property of the ecology. Under a fixed, bounded learning policy, additional state information can help or hurt because it changes both generalization and action. E6 confirmed the preregistered positive linear slope, but the level-specific and leave-one-out results show that this was an endpoint-dependent attenuation of cost. This empirical contrast must not be interpreted as the nonnegative expected value of perfect information for an optimal decision-maker.

### 4.2 Implications for claims about adaptive behavior

Observing that an agent can represent a relevant state does not establish that acting on that state improves fitness. Conversely, a learner that consumes toxic food is not necessarily making the more costly ecological choice when avoidance carries a larger opportunity cost.

### 4.3 Limitations

- Food age was supplied as a perfect cue; agents did not discover it.
- The value rule was fixed rather than evolved.
- The simulation did not produce births in the E-series, so no cross-generational evolutionary response was measured.
- The avoidance oracle optimized toxin avoidance only and was not an optimal policy.
- The chosen energy, toxin, metabolism, and renewal regimes delimit the quantitative conclusions.
- The E6 linear trend depended materially on the energy-10 endpoint; the experiment did not establish a smooth response curve or locate a general break-even payoff.
- Some individual E6 runs at energies 4-6 fell below the post hoc stricter threshold of 30 fruit encounters per founder, although every preregistered level mean exceeded 30 and every B2 run showed the learned safe-versus-toxic value separation.
- The current study does not implement storing food for later detoxification.

## 5. Conclusion

Resource-age information solved the hidden-state discrimination problem but reduced survival at four of five tested payoffs relative to a capacity-matched sham. A preregistered positive slope showed that this cost was no longer detected at the highest tested payoff, although the endpoint dependence prevents a general claim of gradual improvement. The separate R-B replication also supported a survival cost of age-varying toxicity relative to two constant-potency controls. Representational adequacy and ecological benefit are therefore distinct empirical questions for bounded artificial foragers.

## Data and Code Availability

**[Replace local paths with a versioned public archive and DOI before submission.]**

## Generative-AI Disclosure

**[Complete with the author-approved record of tools, providers, versions, dates, tasks, and human verification.]**

## References

Chrisman, L. (1992). Reinforcement learning with perceptual aliasing: The perceptual distinctions approach. In *Proceedings of the Tenth National Conference on Artificial Intelligence* (pp. 183–188). AAAI Press. https://cdn.aaai.org/AAAI/1992/AAAI92-029.pdf

Dall, S. R. X., Giraldeau, L.-A., Olsson, O., McNamara, J. M., & Stephens, D. W. (2005). Information and its use by animals in evolutionary ecology. *Trends in Ecology & Evolution, 20*(4), 187–193. https://doi.org/10.1016/j.tree.2005.01.010

Donaldson-Matasci, M. C., Bergstrom, C. T., & Lachmann, M. (2010). The fitness value of information. *Oikos, 119*(2), 219–230. https://doi.org/10.1111/j.1600-0706.2009.17781.x

Giannakakis, E., Khajehabdollahi, S., & Levina, A. (2025). Network bottlenecks and task structure control the evolution of interpretable learning rules in a foraging agent. *Artificial Life, 31*(2), 177–194. https://doi.org/10.1162/artl_a_00458

Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., Giske, J., Groeneveld, J., Johnston, A. S. A., Miles, A., Nabe-Nielsen, J., Polhill, J. G., Radchuk, V., Rohwäder, M.-S., Stillman, R. A., Thiele, J. C., & Ayllón, D. (2020). The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism. *Journal of Artificial Societies and Social Simulation, 23*(2), Article 7. https://doi.org/10.18564/jasss.4259

## Figure captions

**Figure 1. Hidden toxicity changed survival and behavior.** (A) Mean founder attained age in E1 under food-matched nontoxic fruit (A0), fully potent constant toxicity (A1), age-dependent toxicity (A2), and the dose-matched constant-potency control (A3). (B) Acceptance conditional on fruit encounter. Colored points are independent seeds; black diamonds and bars are means and descriptive 95% t intervals.

**Figure 2. Resource-age information restored discrimination without guaranteeing survival benefit.** (A) Safe-minus-toxic acceptance under type-only (B1), type-by-age (B2), capacity-matched sham (B3), and avoidance-oracle (B4) policies in monotonic and toxic-safe-toxic profiles. (B) Within-seed attained-age differences relative to B1. Points are independent seeds; diamonds and bars are means and descriptive 95% t intervals.

**Figure 3. Within-generation selection and the exposure-denominator check.** (A) E3 toxin-tolerance selection differentials for the nontoxic, age-dependent, and constant-potency arms. No births occurred. (B) E4 acceptance per low-value raw-seed encounter with value learning disabled or enabled; annotations give mean raw meals and telemetry-deduplicated encounters. Points are independent seeds; diamonds and bars are means and descriptive 95% t intervals.

**Figure 4. Confirmatory survival effect and mechanism across risky-resource payoffs.** (A) E6 B2-B3 restricted mean founder follow-up at five realized fruit energies. Thin lines connect values within each seed; markers and bars show means and 95% t intervals. (B) Discrimination for the resource-age and sham representations. All 450 runs passed the frozen validator.

**Figure 5. Preregistered R-B replication.** Paired founder follow-up contrasts for age-varying toxicity against the original (A3O) and recalibrated (A3R) constant-potency controls. Colored points are seed-level paired differences; gray lines connect contrasts within seed; black diamonds and bars are means and 95% t intervals. The dashed line marks the preregistered -5-tick smallest effect of scientific interest. All 150 runs passed the frozen validator.
