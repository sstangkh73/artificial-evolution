# Experience-Based Food Valuation in an Unlabeled Artificial Ecology

**Manuscript type:** Article — working draft  
**Target journal:** *Artificial Life*  
**Authors:** Chisanupong Injun; additional authorship pending contribution review  
**Affiliation:** Dibuk Phang-nga Wittayayon School, Phang-nga, Thailand  
**Corresponding author:** [CONFIRM EMAIL AND ORCID]

## Abstract

Artificial-life agents are often assigned task rewards or semantic object
categories that make apparently adaptive behavior easier to learn but also embed
part of the solution in the environment. We tested a narrower alternative:
whether embodied agents can change food choice from the energetic consequence of
eating, without receiving labels such as “good,” “bad,” or “food quality.” Agents
inhabited a two-dimensional ecology with a metabolism model that converts food
composition and body-specific digestive capacity into realized energy. The
baseline eating mechanism was value-blind: any encountered item that fit the
agent's mouth could be consumed. The treatment added a type-level running memory
of realized energy and a relative acceptance threshold. We compared memory-off
and memory-on conditions across ten paired random seeds, 3,000 ticks per arm,
using the seed/run as the statistical unit. Agents with value memory consumed a
mean of 423.0 low-value seed meals per run, compared with 1,945.3 without memory.
The paired reduction was 1,522.3 meals (95% interval: 1,340.7–1,703.9); all ten
pairs favored the learning condition (exact two-sided paired randomization
*p*=0.00195). In a matched mechanism control, 10 of 12 agents with memory began
skipping the low-value food, compared with 0 of 12 when memory was disabled; no
agent skipped before directly experiencing the higher-value comparator. These
results support a narrow claim: in the tested abundant-energy regime, memory of
embodied energetic consequences is causally sufficient to produce within-
lifetime diet adaptation without semantic food labels. The experiment does not
establish semantic understanding, social transmission, population-level fitness
benefit, or evolution. Additional environment-transfer and exposure-normalized
tests are specified before journal submission.

**Keywords:** artificial life; embodied learning; food-value learning; unlabeled
environment; artificial ecology; causal ablation

## 1. Introduction

Artificial life investigates life-like organization and behavior by synthesizing
systems in software, hardware, or other media. A persistent methodological
challenge is to distinguish behavior that arises from interactions among agents,
bodies, and environments from behavior that was effectively supplied through
the researcher's representation, reward, or control rules. A simulated agent can
appear to “know” which resource is useful when the environment has already
encoded resource identity, utility, or a task-specific score in the observations
and objective.

The present study adopts an *unlabeled* or *uninformed-world* design principle.
The phrase does not mean that the agent receives no consequences. Energy gained
or lost after eating is an embodied consequence and therefore a learning signal.
Rather, the environment does not provide a semantic declaration that one food is
good, another is bad, or a particular diet is the desired task. Edibility depends
on physical compatibility, and energetic value depends on food composition and
the agent's digestive profile. The scientific question is whether an agent can
use those realized consequences to alter later food choice.

This question connects three literatures. First, artificial-life and embodied-
agent research emphasizes that adaptive behavior is produced by the coupling of
body, controller, and environment rather than by a controller in isolation
(Sims, 1994; Ha, 2019). Second, reinforcement learning formalizes adaptation from
consequences, but its standard task reward often expresses the experimenter's
goal directly (Sutton & Barto, 2018). Third, biological work on learned food
preference and aversion shows that food choice can change through experienced
post-ingestive consequences, while also demonstrating the importance of cues
that distinguish one outcome source from another (Garcia & Koelling, 1966;
Sclafani, 2010).

Our contribution is not a new general reinforcement-learning algorithm. It is a
controlled artificial-life experiment that grounds a simple value memory in the
same energy accounting that constrains metabolism and behavior, then tests the
mechanism at three levels: paired runs, an on/off ablation, and event order within
individual agents. This design addresses three questions:

1. Does enabling memory of realized food energy reduce consumption of a lower-
   value but still edible food?
2. Does the effect reproduce across random seeds when the world and seed are
   paired between treatment and control?
3. Does the behavior occur after relevant direct experience and disappear when
   the memory mechanism is disabled?

The primary hypothesis was that value-memory agents would consume fewer low-
value seed meals than value-blind agents under a regime in which starvation did
not force indiscriminate eating. The regime was deliberately abundant in energy:
it isolates food valuation from a separately documented spatial-foraging
bottleneck. This choice improves mechanistic identification while limiting
ecological generalization.

## 2. Methods

### 2.1 Simulation and energetic consequences

The study used the Artificial Evolution Python simulation. Agents occupy a
two-dimensional grid world, move, encounter resources, expend energy, and ingest
items that satisfy physical edibility constraints. The metabolism layer computes
digestible energy from food mass and composition together with the body plan's
enzyme profile. The resulting energy is applied to the agent's state. Thus, the
quantity used by the learner is produced by the same mechanism that changes the
agent's energetic condition; it is not a separate experimenter-authored reward
table used only for training.

The focal foods were `raw_seed` and `raw_plant`. Both were edible, but their
realized values differed in the controlled configuration: the lower-value seed
provided approximately 50 energy units and the plant approximately 250. The
labels are implementation identifiers used for logging and memory indexing; no
human-language concept was presented to the agent.

### 2.2 Baseline value-blind consumption

In the control condition, eating was value-blind. When an agent occupied a cell
containing an item that fit its ingestion constraints, the normal consumption
path allowed the item to be eaten without comparing its energetic value with
previous foods. Spatial memory could still influence movement, but the agent did
not maintain a per-type estimate for the consumption decision tested here.

### 2.3 Experience-based value memory

The treatment enabled `food_value_memory`, indexed by implementation food type.
After an agent ate an item, the observed net energy updated the corresponding
memory through an exponential moving average with learning rate 0.3. A relative
acceptance rule compared the remembered value of the encountered food with a
fraction of the best remembered food value. In the focal configuration, the
pickiness fraction was 0.5, so a remembered seed value near 50 fell below the
acceptance threshold of 125 once a plant value near 250 had been experienced.

The rule supplies a capacity to compare outcomes; it does not supply which food
will be valuable. That distinction defines the scope of “emergent” behavior in
this paper: the learned preference is acquired from experience, while the memory
architecture and comparison rule are designed components.

### 2.4 Experimental design

The confirmatory comparison used two arms:

- **A — no learning:** value memory disabled;
- **B — value learning:** value memory enabled.

Each arm used ten seeds, `20260610` through `20260619`, for 3,000 ticks. Seed and
all non-learning configuration values were matched across arms. The abundant-
energy configuration used the same world size, population, food-generation,
metabolic, and body settings in each pair. The seed/run, not the agent or tick,
was the statistical unit.

The primary outcome was total `raw_seed` meals during a run. Secondary outcomes
were meal counts within three successive 1,000-tick windows and agent-level
event sequences recording exposure, learned values, and the first skip.

### 2.5 Mechanism control

A smaller matched run followed 12 agents for 600 ticks with value memory enabled,
then repeated the same configuration and seed with value memory disabled. The
control measured the number of agents that began skipping seeds, total seed
meals, total skips, plant meals, and whether skipping occurred before direct
experience with the higher-value plant comparator.

This 12-agent comparison is a mechanistic trace rather than the primary
inferential experiment. Agents within one simulation are not treated as 12
independent ecological replicates.

### 2.6 Statistical analysis

Because the design used the same random seed in both arms, the primary analysis
was paired. For each seed, we computed the difference in total low-value meals,
`A - B`. We report the mean paired difference, a 95% *t* interval across the ten
seed-level differences, and an exact two-sided paired sign-flip randomization
test over all 2^10 label exchanges. The within-pair ratio is descriptive because
ratios can be unstable and were not specified as the primary scale.

Earlier project reports used a Mann–Whitney test treating arms as independent.
That result is retained only as a robustness check; the paired randomization test
matches the experimental design and is primary here. Confidence intervals across
ticks or agents are not used as substitutes for independent seed replication.

The analysis was regenerated by
`scripts/prepare_top_two_publication_stats.py`. Compact source data are stored in
`reports/publication_top2_2026-08-24/source_data/`.

## 3. Results

### 3.1 Paired multi-seed reduction in low-value meals

The no-learning arm consumed a mean of 1,945.3 low-value seed meals per run
(SD 248.2), whereas the value-learning arm consumed 423.0 (SD 65.1). Every one
of the ten paired seeds showed fewer low-value meals with learning.

The mean paired difference was 1,522.3 meals (SD 253.9; 95% interval
1,340.7–1,703.9). The exact two-sided paired sign-flip test gave
*p*=0.001953125. The mean within-pair no-learning/learning ratio was 4.70×.

| Seed | No learning | Value learning | Paired reduction |
| ---: | ---: | ---: | ---: |
| 20260610 | 1,753 | 367 | 1,386 |
| 20260611 | 1,507 | 521 | 986 |
| 20260612 | 2,036 | 412 | 1,624 |
| 20260613 | 2,078 | 392 | 1,686 |
| 20260614 | 1,881 | 304 | 1,577 |
| 20260615 | 2,292 | 462 | 1,830 |
| 20260616 | 2,207 | 486 | 1,721 |
| 20260617 | 1,645 | 421 | 1,224 |
| 20260618 | 2,066 | 480 | 1,586 |
| 20260619 | 1,988 | 385 | 1,603 |

The time-window summary was also consistent with acquisition rather than a fixed
between-arm offset. Mean low-value meals in the learning arm declined from 285.6
in ticks 0–1,000 to 106.3 in ticks 1,000–2,000 and 31.1 in ticks 2,000–3,000.
The corresponding no-learning means were 709.6, 671.7, and 564.0. These windows
are repeated measurements within runs and are presented descriptively; the
seed-level total remains the primary confirmatory outcome.

### 3.2 Mechanism ablation

In the matched 12-agent mechanism run, 10 of 12 agents with value memory began
skipping the low-value seed. With memory disabled, 0 of 12 began skipping. The
reported totals were 108 versus 382 seed meals and 2,163 versus 0 seed-skip
events; plant meals were 52 in both conditions. Removing the proposed mechanism
therefore removed the target behavior in this configuration.

### 3.3 Direct experience preceded behavioral change

Among agents that experienced both foods in the traced run, 10 of 10 eventually
skipped the lower-value seed. No agent skipped the seed without first tasting the
higher-value plant comparator. The delay from first plant experience to first
seed skip varied from 2 to 59 ticks (mean 14.1), indicating individual acquisition
times rather than one synchronized population switch.

## 4. Discussion

### 4.1 Interpretation

The experiment supports the stated narrow hypothesis. Adding memory of realized
energetic value reduced low-value consumption across every paired seed, produced
a decreasing consumption trajectory, and generated individual behavior changes
after relevant experience. Disabling the memory removed skipping in the matched
mechanism control. Together, the run-level, ablation, and event-order evidence
are more informative than any one aggregate curve.

The result is appropriately described as experience-based and outcome-grounded,
not as learning “without reward.” Realized energy is a consequence that can act
as a reinforcement signal. What is absent is a semantic food-quality label or a
separate task score that tells the agent which food the researcher wants it to
prefer.

### 4.2 Relation to artificial life

The contribution lies in connecting diet learning to the same energetic substrate
that constrains the artificial organism. In a conventional benchmark, reward can
be an external scalar whose relationship to survival is defined by the task
designer. Here, food affects the agent through metabolism first; the learner
observes that realized consequence. This creates a clean experimental bridge
between embodied artificial-life modeling and value learning.

The work also illustrates why “emergence” must be scoped. The acquired preference
was not directly specified, but the capacity for type-level memory, its update
rule, and the acceptance threshold were implemented by the researcher. The
system therefore demonstrates within-lifetime adaptive behavior, not the
spontaneous evolution of a learning architecture.

### 4.3 Alternative explanations and remaining controls

Pairing seeds controls a substantial portion of world stochasticity, and the
mechanism ablation reduces the plausibility that a fixed configuration difference
caused the effect. Nevertheless, raw meal counts conflate preference with
encounter and exposure. A stronger submission package should log every eligible
choice set and report the probability of accepting a seed conditional on seeing
one, with comparator availability recorded at the same event.

The abundant-energy regime is another deliberate but important restriction. It
prevents emergency hunger from forcing consumption and thereby isolates the
learning mechanism. It does not show that the same policy improves survival in a
competitive ecology. Transfer to a second frozen environment and sensitivity to
learning rate and pickiness are required before broad ecological claims.

### 4.4 Implications for the companion temporal-toxicity study

This study establishes a stationary baseline: type-level value memory can learn
to avoid a consistently lower-value food. A separate study asks what happens
when a single food type contains hidden temporal states with different outcomes.
That companion manuscript treats the present result only as a baseline and does
not reuse the meal-reduction result as a second contribution.

## 5. Limitations

1. The confirmatory batch covers one abundant-energy environment.
2. The primary outcome is a meal count rather than an exposure-normalized choice
   probability.
3. The mechanistic 12-agent control is one matched seed and is not an independent
   multi-seed replication.
4. Agent architecture, memory indexing, learning rate, and pickiness are designed.
5. The simulation is two-dimensional and abstracts biochemical and sensory detail.
6. No population-level fitness, social transmission, semantic understanding, or
   evolutionary adaptation is demonstrated.

## 6. Conclusion

In ten paired simulations, memory of realized energetic consequences consistently
reduced consumption of a lower-value but edible food. The effect disappeared in
a matched memory-disabled control, and individual behavioral changes followed
direct experience with the higher-value comparator. The evidence supports a
specific artificial-life result: outcome-grounded memory is sufficient to
produce within-lifetime diet adaptation without semantic food-quality labels in
the tested regime. The next scientific step is not a broader claim but a harder
test—exposure-normalized choice and transfer across ecological conditions.

## Data and Code Availability

The current local evidence bundle includes paired raw runs, compact source-data
CSVs, analysis code, and figure-generating scripts. Before submission, these
materials will be frozen at a tagged commit and archived in a public repository
with a persistent DOI. Final URL: [TO ADD].

## Author Contributions

[TO COMPLETE USING CRediT AFTER AUTHORSHIP REVIEW.]

## Generative-AI Disclosure

OpenAI Codex was used during publication preparation to help audit repository
evidence, identify statistical and claim-overlap risks, draft manuscript text,
and structure reproducibility materials. It was not treated as an author. Before
submission, the human authors must verify every analysis, citation, claim, and
sentence; record the model/version and access dates available to them; revise
this statement to match the final use; and accept full responsibility for the
work.

## Competing Interests

The authors declare [TO CONFIRM].

## References

Garcia, J., & Koelling, R. A. (1966). Relation of cue to consequence in
avoidance learning. *Psychonomic Science, 4*, 123–124.
https://doi.org/10.3758/BF03342209

Ha, D. (2019). Reinforcement learning for improving agent design.
*Artificial Life, 25*(4), 352–365. https://doi.org/10.1162/artl_a_00301

Sclafani, A. (2010). Neuropharmacology of learned flavor preferences.
*Pharmacology Biochemistry and Behavior, 97*(1), 55–62.
https://doi.org/10.1016/j.pbb.2010.06.001

Sims, K. (1994). Evolving virtual creatures. In *Proceedings of SIGGRAPH '94*
(pp. 15–22).

Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction*
(2nd ed.). MIT Press.

Whitehead, S. D., & Ballard, D. H. (1991). Learning to perceive and act by trial
and error. *Machine Learning, 7*, 45–83.
https://doi.org/10.1023/A:1022619109594

> Reference gate: every cited source must be read and checked by the human authors
> before submission. The present list is a verified bibliographic starting set,
> not a substitute for a completed literature review.

