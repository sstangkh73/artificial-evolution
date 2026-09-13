# When Does a Better Representation Pay? Survival Effects of Age Information in Artificial Foraging Under Temporal Toxicity

**Manuscript type:** Article

**Target journal:** *Artificial Life* (provisional; current author instructions and article fit must be verified before formatting)

**Author:** Chisanupong Injun
**Status:** evidence-first manuscript scaffold; not submission-ready

## Abstract

Artificial foragers can learn food values from post-ingestive outcomes while still failing when one perceptual category combines ecologically different states. We studied agents that stored one value per food type while fruit toxicity changed with food age. In full-ecology experiments, type-only agents failed to discriminate safe from toxic ages. Adding age to the value key strongly restored discrimination under both monotonic and toxic-safe-toxic profiles, whereas a sham key with the same capacity did not, isolating information rather than memory capacity as the cause. Yet improved discrimination produced little or no lifespan benefit in the tested ecology, and an avoidance oracle shortened lifespan because toxic fruit remained energetically valuable. These results separate the ability to use information from the survival effect of using it. We therefore test whether the paired lifespan effect of an age-informed representation changes as the energetic value of risky fruit is varied while toxicity is held fixed. **[Insert preregistered E6 estimates and trend result only after the confirmatory run.]** The study tests whether representational adequacy alone determines an ecological benefit, or whether that benefit depends on the resource payoffs that the representation changes.

**Keywords:** artificial life; value of information; embodied foraging; perceptual aliasing; partial observability; temporal toxicity; state representation

## 1. Introduction

### 1.1 Problem

Outcome-grounded learning can estimate the average consequence of a food category without representing every state that determines that consequence. When toxicity changes with food age, a type-only estimate combines safe and toxic encounters. This creates a representational limit: an action cannot depend on age when age, or a correlated cue, is absent from the decision key.

The existence of this limit is established in reinforcement learning and partial-observability research. The empirical question here is narrower and ecological: **when does resolving the hidden state improve survival-relevant outcomes, and when is the information nearly worthless?**

### 1.2 Contribution

This article makes three bounded contributions:

1. It demonstrates a full-ecology failure of type-only food valuation under age-dependent toxicity.
2. It uses an age-key rescue and a capacity-matched sham control to identify information as the cause of restored discrimination.
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

#### Study E: Energy-dependent survival effect of age information

**[E6 confirmatory design after the pilot is closed and the addendum is frozen. Compare B2 with capacity-matched B3 within each realized fruit-energy level; retain B1 as a secondary baseline.]**

### 2.4 Outcomes and statistical analysis

The inferential unit is the simulation run. The primary survival outcome for the new confirmatory studies is mean founder follow-up time, computed for each founder as final attained age minus its deterministic initial age and restricted by the prespecified simulation horizon. Arms use matched seeds and are compared with paired differences. Report arm means and standard deviations, mean paired differences, 95% confidence intervals, exact or seeded Monte Carlo two-sided sign-flip tests as prespecified, effect sizes, and directional seed counts. Encounter-dependent behavior is reported as `P(eat | encounter)`; raw meal counts are secondary because rejected food remains available and changes later exposure.

**[Insert the preregistered E6 trend model, multiplicity rule, exclusions, extinction handling, and missing-run handling verbatim from the frozen addendum.]**

## 3. Results

### 3.1 Hidden toxicity changed behavior and lifespan, but concealment did not add cost beyond toxin dose

**[Report E1 T1-T3 and E4. Preserve the null/falsifying T2 result.]**

### 3.2 Age information restored discrimination because it carried relevant state information

Under the monotonic profile, the type-by-age rescue exceeded the capacity-matched sham by 0.7858 discrimination units (95% CI 0.7650 to 0.8066; Cliff's delta 1.00). Under the toxic-safe-toxic profile, the difference was 0.7515 (95% CI 0.7214 to 0.7815; Cliff's delta 1.00). The sham key remained near zero discrimination, showing that the rescue was caused by age information rather than additional key capacity.

### 3.3 Better discrimination did not guarantee longer life

Relative to the type-only learner, the type-by-age learner changed mean founder lifespan by +3.80 ticks under the monotonic profile and -1.29 ticks under the toxic-safe-toxic profile. The avoidance oracle reduced lifespan by 51.96 and 55.47 ticks, respectively, while sharply increasing starvation deaths. In this ecology, rejecting toxic fruit could cost more energy than the avoided toxin damage.

### 3.4 Toxicity generated a within-generation selection differential

**[Report E3 as N1 selection only; include the falsified comparison against dose-matched constant toxicity.]**

### 3.5 The survival effect of age information changed with risky-resource energy

**[Insert E6 confirmatory results, confidence intervals, trend test, and the complete pattern across all preregistered levels. Do not use pilot estimates here.]**

### 3.6 Regime replication

**[Insert the new R-B replication and distinguish it from exploratory E5.]**

## 4. Discussion

### 4.1 Information sufficiency and information value are different questions

The rescue experiment shows that age information is sufficient for state-sensitive discrimination. Its survival consequence is a separate property of the ecology. Under a fixed, bounded learning policy, additional state information can help or hurt because it changes both generalization and action. This empirical contrast must not be interpreted as the nonnegative expected value of perfect information for an optimal decision-maker.

### 4.2 Implications for claims about adaptive behavior

Observing that an agent can represent a relevant state does not establish that acting on that state improves fitness. Conversely, a learner that consumes toxic food is not necessarily making the more costly ecological choice when avoidance carries a larger opportunity cost.

### 4.3 Limitations

- Food age was supplied as a perfect cue; agents did not discover it.
- The value rule was fixed rather than evolved.
- The simulation did not produce births in the E-series, so no cross-generational evolutionary response was measured.
- The avoidance oracle optimized toxin avoidance only and was not an optimal policy.
- The chosen energy, toxin, metabolism, and renewal regimes delimit the quantitative conclusions.
- The current study does not implement storing food for later detoxification.

## 5. Conclusion

Age information can solve a hidden-state discrimination problem without necessarily improving survival. Its survival effect depends on what the fixed learning policy does with that information under the available resource payoffs. **[Revise this conclusion only after E6 and the R-B replication are complete.]**

## Data and Code Availability

**[Replace local paths with a versioned public archive and DOI before submission.]**

## Generative-AI Disclosure

**[Complete with the author-approved record of tools, providers, versions, dates, tasks, and human verification.]**

## References

**[Add only sources whose full texts were read and checked against the claims they support.]**
