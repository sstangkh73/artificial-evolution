# When Does a Better Representation Pay? Survival Effects of Resource-Age Information in Artificial Foraging Under Temporal Toxicity

**Manuscript type:** Article

**Target journal:** *Artificial Life* (provisional; current author instructions and article fit must be verified before formatting)

**Author:** Chisanupong Injun
**Status:** confirmatory results integrated; methods, literature, references, and archive still incomplete

## Abstract

Artificial foragers can learn food values from post-ingestive outcomes while still failing when one perceptual category combines ecologically different states. We studied agents that stored one value per food type while fruit toxicity changed with food age. Adding resource age to the value key restored safe-versus-toxic discrimination, whereas a capacity-matched sham did not. In a preregistered confirmatory experiment spanning five realized fruit energies, the seed-level linear slope of the rescue-minus-sham survival effect was positive (0.890 restricted-mean follow-up ticks per energy unit, 95% t CI 0.059 to 1.722; two-sided sign-flip p=0.0365). The point estimate was slightly below the preregistered smallest effect of scientific interest. Level-specific effects were negative at energies 4, 5, 6, and 8 and indistinguishable from zero at 10, so the gradient reflected attenuation of a survival cost at the upper endpoint rather than a demonstrated survival benefit throughout the range. A separate 50-seed replication found shorter follow-up under age-varying toxicity than under a recalibrated constant-potency control (mean paired difference -7.928 ticks, 95% CI -11.046 to -4.810). These results separate representational sufficiency from ecological benefit: information can improve state-sensitive behavior while the fixed policy that uses it still reduces survival under most tested payoffs.

**Keywords:** artificial life; value of information; embodied foraging; perceptual aliasing; partial observability; temporal toxicity; state representation

## 1. Introduction

### 1.1 Problem

Outcome-grounded learning can estimate the average consequence of a food category without representing every state that determines that consequence. When toxicity changes with food age, a type-only estimate combines safe and toxic encounters. This creates a representational limit: an action cannot depend on age when age, or a correlated cue, is absent from the decision key.

The existence of this limit is established in reinforcement learning and partial-observability research. The empirical question here is narrower and ecological: **when does resolving the hidden state improve survival-relevant outcomes, and when is the information nearly worthless?**

### 1.2 Contribution

This article makes three bounded contributions:

1. It demonstrates a full-ecology failure of type-only food valuation under age-dependent toxicity.
2. It uses a resource-age-key rescue and a capacity-matched sham control to identify information as the cause of restored discrimination.
3. It measures whether the survival effect of that information changes with the energetic value of the risky resource.

The article does not claim that perceptual aliasing is new, that agents discovered food age, or that an evolutionary response occurred across generations.

### 1.3 Hypotheses

**H1: Information sufficiency.** A type-by-age value key produces greater safe-versus-toxic discrimination than a type-only key and a capacity-matched sham key.

**H2: Survival effect of state information.** The paired lifespan difference between the type-by-age learner and the capacity-matched sham changes systematically as risky-fruit energy changes. This is an empirical effect for fixed learning policies, not expected value of perfect information and not reproductive fitness.

**H3: Regime dependence.** The cost of hidden toxicity relative to dose-matched observable toxicity is tested in a new, preregistered R-B replication and is reported regardless of direction.

## 2. Methods

### 2.1 Artificial ecology

**[Describe world size, population, resource renewal, metabolism, mortality, food energies, toxin load and damage, and stopping rules from the frozen E-series specifications.]**

### 2.2 Learning representation

The type-only learner stored one value per food implementation type. The rescue learner stored separate values for type-by-age bins. The sham learner used the same number of keys as the rescue learner, but key assignment carried no age information. An avoidance oracle observed toxicity and rejected items with positive excess dose; it was a discrimination ceiling, not an optimal fitness policy.

### 2.3 Experiments

#### Study A: Hidden-state cost and behavioral response

**[E1: A0, A1, A2, A3; paired seeds; preregistered T1-T3; E4 exposure-denominator correction.]**

#### Study B: Information rescue

**[E2: B1-B4 under monotonic M and non-monotonic W profiles; discrimination index as the primary outcome.]**

#### Study C: Within-generation selection

**[E3: toxin-tolerance selection differential only. State explicitly that births were zero and no response across generations was measured.]**

#### Study D: Ecological-regime transfer

**[E5 and the new preregistered R-B replication. Separate confirmatory and exploratory results.]**

#### Study E: Energy-dependent survival effect of resource-age information

After closing the exploratory pilot, we froze the E6 protocol at tag `prereg-resource-age-2026-09-14`. E6 crossed five realized safe-fruit energies (4, 5, 6, 8, and 10 units) with three representations: type only (B1), type by resource-age bin (B2), and a capacity-matched sham bin (B3). Each of 30 new seeds ran all 15 arms, giving 450 runs. B2-B3 was the causal contrast for information content; B1 was a secondary baseline.

### 2.4 Outcomes and statistical analysis

The independent replicate is the seed, with one simulation run per arm within each matched seed. The primary survival outcome for the new confirmatory studies is mean founder follow-up time, computed for each founder as final attained age minus its deterministic initial age and restricted by the prespecified simulation horizon. Arms use matched seeds and are compared with paired differences. We report arm means and standard deviations, mean paired differences, 95% confidence intervals, seeded Monte Carlo two-sided sign-flip tests as prespecified, effect sizes, and directional seed counts. Encounter-dependent behavior is reported as `P(eat | encounter)`; raw meal counts are secondary because rejected food remains available and changes later exposure.

For E6, we computed B2-B3 at each energy within each seed and fitted one ordinary-least-squares slope over the five realized energies. The 30 seed-level slopes were tested with a seeded, two-sided Monte Carlo sign-flip test using 200,000 draws. The preregistered decision rule required a positive mean slope and a 95% CI excluding zero; the smallest effect of scientific interest was 1 follow-up tick per energy unit. Level-specific B2-B3 tests were Holm-adjusted across the five energies. Runtime failures were to be rerun only at the failed arm-seed cell and retained in the audit trail; no failures occurred. Simulations could stop at population extinction. No founder was censored in either new confirmatory study, so the death-only sensitivity equals the primary restricted-mean follow-up outcome.

## 3. Results

### 3.1 Hidden toxicity changed behavior and lifespan, but concealment did not add cost beyond toxin dose

**[Report E1 T1-T3 and E4. Preserve the null/falsifying T2 result.]**

### 3.2 Age information restored discrimination because it carried relevant state information

Under the monotonic profile, the type-by-age rescue exceeded the capacity-matched sham by 0.7858 discrimination units (95% CI 0.7650 to 0.8066; Cliff's delta 1.00). Under the toxic-safe-toxic profile, the difference was 0.7515 (95% CI 0.7214 to 0.7815; Cliff's delta 1.00). The sham key remained near zero discrimination, showing that the rescue was caused by age information rather than additional key capacity.

### 3.3 Better discrimination did not guarantee longer life

Relative to the type-only learner, the type-by-age learner changed mean founder lifespan by +3.80 ticks under the monotonic profile and -1.29 ticks under the toxic-safe-toxic profile. The avoidance oracle reduced lifespan by 51.96 and 55.47 ticks, respectively, while sharply increasing starvation deaths. In this ecology, rejecting toxic fruit could cost more energy than the avoided toxin damage.

### 3.4 Toxicity generated a within-generation selection differential

**[Report E3 as N1 selection only; include the falsified comparison against dose-matched constant toxicity.]**

### 3.5 The survival effect of resource-age information changed with risky-resource energy

All 450 E6 runs passed the frozen batch validator. The mean seed-level B2-B3 slope was 0.890 ticks per energy unit (SD 2.227; median 0.381; 95% t CI 0.059 to 1.722; bootstrap CI 0.130 to 1.696; seeded two-sided sign-flip p=0.0365). Eighteen of 30 slopes were positive and 12 were negative. The manuscript H2 decision rule, registered as H6.1 in the frozen protocol, was therefore met. The point estimate was slightly below the preregistered smallest effect of scientific interest of 1 tick per energy unit, while its confidence interval included that threshold.

The level-specific pattern qualified the linear result. Mean B2-B3 follow-up differences were -5.431 ticks at energy 4 (95% CI -8.826 to -2.037; Holm-adjusted p=0.0120), -5.576 at 5 (-9.403 to -1.749; adjusted p=0.0120), -6.141 at 6 (-9.989 to -2.293; adjusted p=0.0120), -7.650 at 8 (-11.470 to -3.830; adjusted p=0.00265), and +1.365 at 10 (-2.122 to 4.852; adjusted p=0.4448). Thus, resource-age information did not show a confirmed survival benefit at any single tested level. The positive preregistered slope arose because the survival cost seen from energies 4 through 8 was absent at energy 10.

The mechanism gate passed at all five levels. B2's mean discrimination index ranged from 0.654 to 0.748, while B3 ranged from -0.112 to -0.097. Every B2 run contained all nine resource-age keys and assigned higher learned values to safe bins than to toxic bins. Mean fruit encounters per founder ranged from 48.7 to 65.5 across energy levels, above the preregistered threshold of 30. A stricter post hoc check found that individual runs fell below 30 at energies 4, 5, and 6. This does not change the preregistered level-mean gate, but it limits claims that every seed had equally strong exposure.

A leave-one-energy-out analysis was conducted after seeing the primary result and is descriptive only. The slope remained positive with a confidence interval excluding zero when energies 4, 5, 6, or 8 were omitted. Omitting energy 10 changed the slope to -0.58 ticks per energy unit (95% CI -1.85 to 0.70; p=0.36). The primary linear result therefore depends materially on the highest-energy endpoint and should not be described as a smooth gradient across the full range.

### 3.6 Regime replication

All 150 R-B replication runs passed the frozen batch validator. Across 50 matched seeds, age-varying toxicity (A2) reduced mean founder follow-up relative to the recalibrated constant-potency control (A3R) by 7.928 ticks (95% t CI -11.046 to -4.810; bootstrap CI -10.967 to -4.938; two-sided sign-flip p=0.000020). Thirty-eight seeds favored A3R, 12 favored A2, and none tied. The point estimate exceeded the preregistered 5-tick smallest effect of scientific interest, although the t interval narrowly included -5. The direct-replication comparison with the original constant-potency control (A3O) agreed: A2-A3O was -7.102 ticks (95% CI -10.218 to -3.985; p=0.000035). The two control definitions therefore led to the same directional conclusion. Unpaired Cliff's delta was negligible for both contrasts (-0.134 and -0.118), reflecting large between-seed overlap despite the matched-seed difference.

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

**[Add only sources whose full texts were read and checked against the claims they support.]**
