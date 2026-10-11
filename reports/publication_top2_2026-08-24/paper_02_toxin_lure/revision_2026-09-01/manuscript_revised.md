# When Intermittent Safety Lures an Artificial Forager: Temporal Toxicity Under Perceptual Aliasing

**Manuscript type:** Letter  
**Target journal:** *Artificial Life*  
**Author:** Chisanupong Injun  
**Affiliation:** Deebuk Phangnga Wittayayon School, Phang Nga 82000, Thailand  
**ORCID:** https://orcid.org/0009-0000-2979-1916  
**Corresponding author:** Chisanupong Injun; chisanupong.injun@gmail.com

## Abstract

Artificial-life agents often acquire adaptive behavior through local interactions with an environment rather than through semantic labels. Such learning can nevertheless fail when one perceptual category combines ecologically different states. We study a synthetic forager that stores one learned value per food type while food toxicity changes with age. Fresh fruit yielded approximately 2 net energy units, aged fruit 10, and a consistently safe staple 5. If fresh-toxic encounters occur with probability *p*, the converged type-only value is `10 - 8p`; fruit is therefore preferred whenever `p < 0.625`, although some encounters remain toxic. Across 30 seed/runs, 100 agents per seed, and 40 encounters per agent, 63.3% +/- 1.3% of agents using the simulation's value gate ranked fruit above the staple at 30% toxicity. The same inversion, which we call the **lure**, appeared with epsilon-greedy, softmax, and greedy sample-average learners. A non-monotonic toxic-safe-toxic age profile produced zero safe-window discrimination by construction. The result identifies a boundary on emergent value-guided foraging: local outcome learning cannot produce state-sensitive adaptation when the relevant ecological state is absent from the agent's perceptual representation. Fitness consequences in a full evolving ecology remain untested.

**Keywords:** artificial life; adaptive behavior; embodied foraging; perceptual aliasing; time-varying toxicity; value learning

## 1. Introduction

Artificial Life uses synthetic systems to investigate how life-like organization and behavior arise from interactions among organisms, bodies, and environments (Dorin & Stepney, 2024; Gershenson, 2023). Within this tradition, an artificial organism's adaptive behavior need not be specified as a complete policy. It may emerge from local sensory-motor experience, resource constraints, and learning during the organism's lifetime. Foraging provides a particularly direct setting because action, energetic consequence, and future behavior are coupled through the agent-environment loop.

Learning is therefore not an external convenience in ALife models; it can be one component of adaptation alongside evolution. Sasaki and Tokoro (1999) examined learnable neural networks distinguishing food from poison under changing environments, while Bullinaria (2017) studied how direct learning interacts with life-history evolution. More recently, Giannakakis et al. (2025) showed in embodied foraging agents that environmental task structure and network constraints shape the learning rules found by evolution. These studies establish that the form of a learner and the structure of its environment jointly determine adaptive outcomes. Work on emergent resource exchange further illustrates how simple actions and environmental opportunities can support unprogrammed behavior in synthetic foraging worlds (Garbus & Pollack, 2024).

The present study addresses the complementary failure case: what happens when local outcome learning is available, but the perceptual representation collapses ecologically distinct states? Perceptual aliasing and partial observability are classical limitations (Kaelbling et al., 1998; Whitehead & Ballard, 1991), and biological taste-aversion learning likewise depends on cues that distinguish causes of harmful outcomes (Garcia & Koelling, 1966). We do not claim these general principles as new. We ask a narrower ALife question: can a resource that is only intermittently safe reverse an artificial forager's learned avoidance into active preference?

We call this reversal the **lure**. Our contribution is threefold: an analytic boundary for the inversion, a controlled test across four illustrative learning rules, and a representation-level demonstration that a type-only learner cannot target a non-monotonic safe age window. This isolates a constraint on the emergence of adaptive foraging before survival and evolutionary consequences are introduced.

## 2. Methods

### 2.1 Synthetic forager and hidden temporal state

The study used the food-valuation mechanism from a two-dimensional artificial-life simulation containing agents, energy metabolism, and resource interactions. The controlled harness removed spatial search and starvation by keeping agents sated, allowing the valuation mechanism to be tested without a foraging-access bottleneck. Agents updated food value from net energy realized after ingestion; no semantic label specified whether an item was safe or toxic.

One observable implementation type, `raw_fruit`, had two hidden age states. Fresh fruit invoked the simulation's toxin pathway and yielded approximately `Vf = 2` net energy units. Aged fruit had detoxified and yielded `Va = 10`. A consistently safe staple had value `Vs = 5`. Age was not supplied to the type-only value representation.

If a fruit encounter is fresh and toxic with probability *p*, a converged sample-average learner estimates

`Vmix(p) = pVf + (1-p)Va = 10 - 8p`.

The mixed fruit outranks the staple when `Vmix > 5`, hence `p < 0.625`. This threshold follows from the selected energetic outcomes; it is not proposed as a biological constant.

### 2.2 Experimental design and outcomes

Each condition comprised 30 independent seed/runs. Within each seed, 100 agents experienced 40 fruit opportunities. Toxic-state frequencies were 20%, 30%, 40%, 50%, and 60%. We evaluated the simulation's one-shot-plus-exponential-moving-average value gate, epsilon-greedy sample average, softmax sample average, and greedy sample average. These rules test whether the lure is confined to the simulation-specific gate; they are not an exhaustive survey of learning algorithms.

The primary outcome was the seed-level percentage of agents whose final fruit value exceeded the staple value. Secondary outcomes were toxic-meal fraction and energy per meal. Means and normal-approximation 95% confidence-interval half-widths were calculated across the 30 seed-level percentages; agents within a seed were not treated as independent inferential replicates. An age-aware policy consuming only aged fruit defined an upper comparison of zero toxic meals and 10 energy units per fruit.

A second condition imposed a non-monotonic age profile: toxic before age 3, safe from ages 3 through 6, and toxic again from age 7. Safe-window discrimination was the difference between eating probability inside and outside that window. A policy receiving the same type value at every age must have zero discrimination by representation; simulation checked that implementation consequence.

## 3. Results

At 30% toxic encounters, 63.3% +/- 1.3% of agents using the simulation gate ended with fruit valued above the safe staple (Figure 1). Toxic meals remained approximately 30%, and mean energy was approximately 7.6 per consumed fruit, compared with 10 for the age-aware policy.

The inversion occurred under all four tested rules. At 30% toxicity, lure rates were 63.3% +/- 1.3% for the simulation gate, 92.7% +/- 0.8% for epsilon-greedy, 99.2% +/- 0.3% for softmax, and 62.1% +/- 1.7% for greedy sample average. Continued exploration did not necessarily rescue the learner: it could make the estimate converge more reliably toward a mixed value that remained above the staple. Across increasing toxic-state frequencies, simulation-gate lure rates declined from 79.5% at 20% toxicity to 5.6% at 60%, consistent in direction with the analytic boundary while retaining learner- and horizon-specific finite-sample effects.

In the non-monotonic condition, eating probability was equal inside and outside the safe window, giving 0.0 discrimination points. The finite result confirmed the stronger structural claim: one stored value for one food type cannot select different actions according to an unobserved age.

![Figure 1](figure_01_temporal_toxicity_revised.png)

**Figure 1. Intermittent safety creates a lure under type-only valuation.** (A) The analytic mixed-fruit value exceeds the safe staple below 62.5% toxic encounters. (B) Percentage of agents whose final fruit value exceeded the staple across four learning rules. Points are means across 30 seed/runs; error bars are normal-approximation 95% intervals from seed-level percentages. Each seed contained 100 agents with 40 fruit opportunities per agent.

## 4. Discussion

The result connects a classical information limitation to an ALife question about emergent adaptation. A permanently harmful food with value 2 is ranked below the safe staple and can be avoided. When that food sometimes reaches a high-value safe state, collapsing both states into one value can raise its estimated worth above the staple. Intermittent safety then does not merely obscure the correct action; it changes the learned ranking from avoidance to preference.

This finding complements ALife studies in which learning rules, embodiment, or environmental structure enable adaptive behavior. Here, environmental structure and representation interact to prevent the desired behavior from emerging. The result also clarifies what additional organization would be required: a perceptible freshness cue and state-conditioned value could permit within-lifetime discrimination, whereas storage followed by delayed consumption would additionally require item persistence, temporal credit assignment, and an action policy capable of deferral. Those mechanisms should be tested rather than inferred from the present result.

### 4.1 Limitations and future work

The controlled sated regime isolates valuation but does not measure mortality, survival, reproduction, population dynamics, or evolutionary fitness. Lure magnitude also depends on initialization, exploration, update rule, decision horizon, and the selected energy values. Four learners demonstrate recurrence, not universality. Finally, zero safe-window discrimination is an analytic consequence of omitted state, so the simulation is an implementation check rather than an independent estimate of that theoretical result.

The next experiment should compare type-only, type-by-age, and age-aware deferral policies in a preregistered full ecology, with survival and reproduction as outcomes. Until then, the supported conclusion is representational and behavioral: local experience can ground food value, yet it cannot yield state-sensitive adaptation when the ecologically decisive state is unavailable to the learner.

## 5. Conclusion

An artificial forager that learns one value per food type can be drawn toward a partly toxic resource when safe encounters inflate the shared estimate. This lure has a simple analytic boundary, appears across four tested learning rules, and prevents exploitation of a hidden non-monotonic safe window. The result identifies a precise limit on emergent value-guided behavior without claiming an evolutionary cost that has not yet been measured.

## Data and Code Availability

Source-data tables, analysis scripts, toxin experiment harnesses, and the minimum simulation source required to reproduce the reported results accompany this submission as supplementary material. A versioned public archival repository will be added to the published record if the manuscript is accepted.

## Author Contributions

Chisanupong Injun: Conceptualization, methodology, software, validation, formal analysis, investigation, data curation, visualization, writing - original draft, and writing - review and editing.

## Acknowledgments

The author thanks the school project advisor and Deebuk Phangnga Wittayayon School for administrative and institutional support. The advisor is not listed as an author because the research, software, experiments, analysis, and manuscript were completed by the author.

## Ethics Statement

The study used only software agents in a computer simulation and involved no human participants, human data, animals, or biological specimens.

## Generative-AI Disclosure

OpenAI Codex (OpenAI; https://openai.com/codex; accessed September 1, 2026) assisted with literature discovery, evidence auditing, statistical and claim-boundary review, and manuscript drafting. The system is not an author. The human author reviewed the work and accepts full responsibility for the manuscript.

## Funding Statement

This research received no external funding.

## Competing Interests

The author declares no competing interests.

## References

Bullinaria, J. A. (2017). Imitative and direct learning as interacting factors in life history evolution. *Artificial Life, 23*(3), 374-405. https://doi.org/10.1162/ARTL_a_00237

Dorin, A., & Stepney, S. (2024). What is Artificial Life today, and where should it go? *Artificial Life, 30*(1), 1-15. https://doi.org/10.1162/artl_e_00435

Garbus, J., & Pollack, J. (2024). Emergent resource exchange and tolerated theft behavior using multiagent reinforcement learning. *Artificial Life, 30*(1), 28-47. https://doi.org/10.1162/artl_a_00423

Garcia, J., & Koelling, R. A. (1966). Relation of cue to consequence in avoidance learning. *Psychonomic Science, 4*, 123-124. https://doi.org/10.3758/BF03342209

Gershenson, C. (2023). Emergence in Artificial Life. *Artificial Life, 29*(2), 153-167. https://doi.org/10.1162/artl_a_00397

Giannakakis, E., Khajehabdollahi, S., & Levina, A. (2025). Network bottlenecks and task structure control the evolution of interpretable learning rules in a foraging agent. *Artificial Life, 31*(2), 177-194. https://doi.org/10.1162/artl_a_00458

Kaelbling, L. P., Littman, M. L., & Cassandra, A. R. (1998). Planning and acting in partially observable stochastic domains. *Artificial Intelligence, 101*(1-2), 99-134. https://doi.org/10.1016/S0004-3702(98)00023-X

Sasaki, T., & Tokoro, M. (1999). Evolving learnable neural networks under changing environments with various rates of inheritance of acquired characters: Comparison of Darwinian and Lamarckian evolution. *Artificial Life, 5*(3), 203-223. https://doi.org/10.1162/106454699568746

Whitehead, S. D., & Ballard, D. H. (1991). Learning to perceive and act by trial and error. *Machine Learning, 7*, 45-83. https://doi.org/10.1023/A:1022619109594
