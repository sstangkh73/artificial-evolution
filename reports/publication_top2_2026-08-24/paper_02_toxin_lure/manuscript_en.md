# When Intermittent Safety Lures the Learner: Temporal Toxicity Under Perceptual Aliasing

**Manuscript type:** Letter  
**Target journal:** *Artificial Life*  
**Author:** Chisanupong Injun  
**Affiliation:** Deebuk Phangnga Wittayayon School, Phang Nga 82000, Thailand  
**ORCID:** https://orcid.org/0009-0000-2979-1916  
**Corresponding author:** Chisanupong Injun; chisanupong.injun@gmail.com

## Abstract

A learner that avoids a consistently harmful food may fail when the same food is
safe only in a hidden temporal state. We demonstrate a counterintuitive failure
in an artificial-life food-learning mechanism: intermittent safety can raise the
food's type-level average above a safe staple and invert avoidance into pursuit.
Fresh fruit yielded approximately 2 net energy units, aged fruit 10, and the
staple 5. If fresh/toxic encounters occur with probability *p*, the converged
type-only value is `10 - 8p`; the fruit is therefore preferred whenever
`p < 0.625`, despite some encounters being poisonous. In controlled experiments
with 30 seeds, 100 agents per seed, and 40 encounters per agent, 63.3% ± 1.3% of agents
using the simulation's value gate ranked fruit above the staple when 30% of
encounters were toxic. The lure persisted across epsilon-greedy, softmax, greedy
sample-average, and the simulation's exponential-moving-average gate; at the
same toxin frequency, the corresponding lure rates were 92.7% ± 0.8%, 99.2% ± 0.3%,
62.1% ± 1.7%, and 63.3% ± 1.3%. A type-only value also produced zero age discrimination by
construction in a non-monotonic safe-window condition. These results separate an
analytic representation limit from learner-specific finite-sample magnitude.
They do not establish a mortality or evolutionary cost in the controlled sated
regime. The contribution is the lure—inversion from learned avoidance to pursuit
under intermittent safety—not the general concept of partial observability.

**Keywords:** artificial life; perceptual aliasing; time-varying toxicity;
value learning; partial observability; negative result

## 1. Introduction

Food-learning mechanisms commonly attach one learned value to an observable food
type. This is sufficient when outcomes are stationary: a consistently poor or
toxic food can acquire a low value and be avoided. Naturalistic resources,
however, change with age. A fruit may be unsafe when unripe, safe when ripe, and
unsafe again after spoilage. If the temporal state is hidden, one type label
aliases multiple outcome states.

Perceptual aliasing and partial observability are classical problems
(Whitehead & Ballard, 1991; Kaelbling et al., 1998). We do not claim otherwise.
We ask a narrower artificial-life question: can time-varying safety do more than
obscure the correct decision—can it reverse learned avoidance into active
pursuit? We call that reversal the **lure**.

The study builds on an outcome-grounded food-value mechanism in which agents
update value from net energy after ingestion. Here we isolate a distinct hidden-state
experiment and make two claims: (1) type-only value cannot discriminate age by
representation; and (2) when safe and toxic states are mixed, their average can
rank above a safe alternative and lure several finite-sample learners.

## 2. Methods

### 2.1 Hidden temporal states

The controlled two-state food had one observable implementation type,
`raw_fruit`, but two ages. Fresh fruit invoked the simulation's real toxin path
and yielded approximately `Vf = 2` net energy. Aged fruit had detoxified and
yielded `Va = 10`. A consistently safe staple had value `Vs = 5`. Food age was not
available to the type-only value representation.

If fresh/toxic fruit occurs with probability *p*, a converged sample-average
learner estimates

`Vmix(p) = pVf + (1-p)Va = 10 - 8p`.

The mixed fruit outranks the staple when `Vmix > 5`, or `p < 0.625`. This boundary
is a property of the chosen outcomes, not a universal biological constant
(Figure 1A).

### 2.2 Learners and replication

We evaluated four illustrative rules: the simulation's one-shot-plus-EMA value
gate, epsilon-greedy sample average, softmax sample average, and greedy sample
average. Each condition used 30 seeds; within each seed, 100 agents experienced
40 fruit opportunities. Toxic-state frequencies were 20%, 30%, 40%, 50%, and
60%. The seed/run was the statistical unit. Agent percentages were computed
within seed and summarized across seeds using the mean and a normal-approximation
95% confidence interval, calculated as the mean plus or minus 1.96 standard
errors across the 30 seed-level percentages.

The primary outcome was the percentage of agents whose final fruit value exceeded
the safe-staple value. Secondary outcomes were toxic-meal fraction and energy per
meal. An age-aware policy that consumed only aged fruit defined the comparison
upper bound: zero toxic meals and 10 energy units per consumed fruit.

### 2.3 Non-monotonic safe window

A second condition made fruit toxic before age 3, safe from ages 3–6, and toxic
again from age 7 onward. We measured the difference between the probability of
eating inside and outside the safe window. Because a type-only policy receives
the same stored value at every age, this discrimination is zero by construction;
the finite simulation checks implementation consistency rather than estimating
an uncertain theoretical quantity.

## 3. Results

At 30% toxic encounters, the simulation gate lured 63.3% ± 1.3% of agents
(Figure 1B; mean and seed-level 95% half-width). Toxic meals remained
approximately 30%, and mean energy was approximately 7.6 per consumed fruit,
76% of the age-aware upper bound.

The effect was not confined to the simulation gate. At the same toxin frequency,
lure rates were 92.7% ± 0.8% for epsilon-greedy, 99.2% ± 0.3% for softmax, and
62.1% ± 1.7% for greedy sample average. Exploration did not necessarily rescue the learner;
continued sampling could instead make the estimate converge more reliably to a
mixture that remained above the staple.

Across toxin frequencies, the lure declined as predicted as the toxic state
became more common. The simulation-gate means were approximately 80%, 63%, 42%,
19%, and 6% at 20%, 30%, 40%, 50%, and 60% toxic encounters. Finite-horizon and
decision-rule effects caused lure percentages to fall before the analytic
62.5% boundary; the analytic result specifies the converged mixture ranking, not
an exact finite-horizon percentage.

In the non-monotonic safe-window condition, eating probability was equal inside
and outside the safe window, yielding 0.0 discrimination points. This confirms
the implementation of the stronger representation claim: one value for one type
cannot select different actions by an unobserved age.

![Figure 1](figure_01_temporal_toxicity.png)

**Figure 1. Temporal-state aliasing creates a lure.** (A) Analytic mixed-fruit
value compared with the consistently safe staple; the mixed fruit is preferred
while the toxic-state frequency is below 62.5%. (B) Percentage of agents whose
final fruit value exceeded the staple across four learners. Points show means
across 30 seed/runs and error bars show normal-approximation 95% confidence
intervals (±1.96 standard errors across seed-level percentages). Each seed
contained 100 agents with 40 fruit opportunities per agent.

## 4. Discussion

The key result is an inversion. A constant poison with value 2 is ranked below
the safe staple and can be avoided. When the same poison sometimes becomes a
high-value safe food, the mixed estimate can exceed the staple and turn avoidance
into pursuit. Intermittent safety is therefore not merely harder to learn; under
a type-only representation it can make the hazardous option appear best.

The analytic and empirical claims must remain separate. Zero age discrimination
follows directly from the missing state variable and does not depend on a
particular update rule. Lure magnitude does depend on exploration, initialization,
horizon, and choice policy. Four rules demonstrate that the effect is not unique
to the original gate, but they do not exhaust all learners.

The study also does not show that the lure reduces survival. The sated controlled
regime isolates valuation from spatial search and starvation, but it removes the
population consequences that would justify a fitness claim. A full Article would
need a preregistered ecological comparison among type-only, type-by-state, and
age-aware policies, using survival and reproduction as outcomes.

Finally, the result does not demonstrate storage or deferred consumption. Those
behaviors require state cues, item persistence, and temporal credit assignment;
they remain hypotheses for future work.

## 5. Conclusion

When hidden toxic and safe states share one learned food value, intermittent
safety can invert learned avoidance into pursuit. The lure has a simple analytic
boundary and appears across four illustrative learners in controlled simulations.
Its current scope is representational and behavioral, not evolutionary: the next
test is whether correcting state aliasing changes survival-relevant outcomes in
a full artificial ecology.

## Data and Code Availability

The source-data tables, analysis script, toxin experiment harnesses, and the
minimum simulation source required to reproduce the results are provided as
supplementary material with this submission. A public archival repository will
be added to the published record if the manuscript is accepted.

## Author Contributions

Chisanupong Injun: Conceptualization, methodology, software, validation, formal
analysis, investigation, data curation, visualization, writing - original draft,
and writing - review and editing.

## Acknowledgments

The author thanks the school project advisor and Deebuk Phangnga Wittayayon
School for administrative and institutional support. The advisor is not listed
as an author because the research, software, experiments, analysis, and
manuscript were completed by the author.

## Ethics Statement

This study used only software agents in a computer simulation and involved no
human participants, human data, animals, or biological specimens.

## Generative-AI Disclosure

OpenAI Codex (OpenAI; https://openai.com/codex; accessed August 24, 2026)
assisted with evidence auditing, statistical and claim-boundary review, and
manuscript drafting. The system is not an author. The human author reviewed the
work and accepts full responsibility for the manuscript.

## Funding Statement

This research received no external funding.

## Competing Interests

The author declares no competing interests.

## References

Garcia, J., & Koelling, R. A. (1966). Relation of cue to consequence in
avoidance learning. *Psychonomic Science, 4*, 123–124.
https://doi.org/10.3758/BF03342209

Kaelbling, L. P., Littman, M. L., & Cassandra, A. R. (1998). Planning and acting
in partially observable stochastic domains. *Artificial Intelligence, 101*(1–2),
99–134. https://doi.org/10.1016/S0004-3702(98)00023-X

Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction*
(2nd ed.). MIT Press.

Whitehead, S. D., & Ballard, D. H. (1991). Learning to perceive and act by trial
and error. *Machine Learning, 7*, 45–83.
https://doi.org/10.1023/A:1022619109594
