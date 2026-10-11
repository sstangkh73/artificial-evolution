# When Intermittent Safety Lures the Learner: Sufficiency and Limits of Experience-Based Food Valuation in an Artificial Ecology

**Manuscript type:** Article  
**Target journal:** *Artificial Life*  
**Author:** Chisanupong Injun  
**Affiliation:** Deebuk Phangnga Wittayayon School, Phang Nga 82000, Thailand  
**ORCID:** https://orcid.org/0009-0000-2979-1916  
**Corresponding author:** Chisanupong Injun; chisanupong.injun@gmail.com

## Abstract

Learning from experienced consequences can make an artificial organism adaptive without assigning semantic labels to objects, but it can mislead when one observable category combines hidden states with different consequences. We examine this boundary in a synthetic forager with food values grounded in realized metabolic energy. Study 1 tested type-level valuation in a stationary ecology. Across ten paired 3,000-tick runs, enabling value memory reduced lower-value food consumption from 1,945.3 to 423.0 meals per run; every pair favored learning (mean paired reduction 1,522.3, 95% *t* interval 1,340.7–1,703.9; exact two-sided paired sign-flip *p* = 0.001953). Of 500 treatment agents, 491 experienced both foods, all 491 later skipped the lower-value food, and none skipped it beforehand. Study 2 held the observable food type constant while hiding temporal safety. Fresh fruit yielded 2 energy units, aged fruit 10, and a staple 5. With toxic-state probability *p*, the converged type-only value is `10 - 8p`, so mixed fruit outranks the staple when *p* < 0.625. At 30% toxicity, 63.3% ± 1.3 percentage points of agents using the simulation gate ranked fruit above the staple; this inversion, the **lure**, also occurred under epsilon-greedy, softmax, and greedy sample-average learners. A toxic-safe-toxic age profile produced zero safe-window discrimination because age was absent from the policy input. Embodied consequences were therefore sufficient only when learned categories preserved distinctions required for action. The experiments identify a representational boundary, not mortality, reproductive, or evolutionary effects.

**Keywords:** artificial life; embodied learning; artificial ecology; perceptual aliasing; temporal toxicity; adaptive foraging

## 1. Introduction

Artificial Life investigates living and life-like phenomena by constructing systems in software, hardware, or wetware and studying the organization and behavior that follow (Dorin & Stepney, 2024). The synthetic method is valuable because a model can make a proposed mechanism explicit and experimentally manipulable. It also creates a methodological hazard: a convincing behavior may reflect information, objectives, or categories supplied by the modeler rather than organization acquired by the artificial organism. This distinction matters whenever a system is described as learning, adapting, or exhibiting an emergent behavior.

Foraging is a useful setting in which to examine that distinction. Food connects perception, action, metabolism, and future viability. A forager can be given a semantic input such as “good food,” an externally authored task reward, or a policy that directly selects the preferred resource. Alternatively, the organism can encounter an edible item, experience its energetic consequence through the same metabolism that constrains its behavior, and use that consequence to revise later choices. The latter design does not eliminate a learning signal: realized energy is still an outcome that can reinforce behavior. It does, however, remove a semantic declaration of which resource the researcher intends the organism to prefer.

The relation among embodiment, learning, and adaptation has a long history in Artificial Life. Sims (1994) demonstrated that bodies and controllers can be jointly shaped in simulated physical worlds, while Ha (2019) showed how reinforcement learning can alter agent design as well as policy. These approaches emphasize that the agent's capacities cannot be understood independently of its body and environment. Evolutionary learning was included among the field's open problems by Bedau et al. (2000). Research specifically addressing learning and evolution has likewise shown that lifetime adaptation can alter evolutionary outcomes. Sasaki and Tokoro (1999), for example, evolved learnable neural networks that distinguished food from poison and examined their behavior under environmental change. Bullinaria (2017) investigated direct and imitative learning as interacting components of life-history evolution. These studies place individual learning within longer adaptive processes, but they also show that the learning architecture and the structure of environmental regularities matter.

Recent work in *Artificial Life* sharpens this point. Giannakakis et al. (2025) evolved reward-modulated plasticity rules in embodied foragers and found that task structure, regularization, and network bottlenecks affected which rules emerged and whether they were interpretable. Garbus and Pollack (2024) demonstrated that relatively simple resource actions and an environmental opportunity for congregation could support emergent exchange behavior in a multiagent foraging world. More broadly, Gershenson et al. (2020) distinguish self-organization from outcomes that are more directly imposed, while Gershenson (2023) treats emergence in terms of information present at one descriptive scale but absent at another. The shared lesson is not that simple local rules guarantee adaptation. It is that the organization of the agent-environment system determines what behavior can arise from those rules.

Biological work on food learning provides a complementary motivation. Animals can acquire food preferences and aversions by associating sensory cues with post-ingestive consequences (Touzani et al., 2010). Cue structure is essential: the classic cue-to-consequence findings of Garcia and Koelling (1966) show that learning depends on which observations can be associated with which outcomes. The computational analogue is partial observability. When multiple world states produce the same observation, a learner may assign incompatible consequences to one representation. Whitehead and Ballard (1991) termed this problem perceptual aliasing and showed that it can destabilize reinforcement-learning policies. Partially observable Markov decision processes formalize the need to condition decisions on beliefs or memory when the current observation does not identify the underlying state (Kaelbling et al., 1998).

Those principles are established. The present contribution is a controlled Artificial-Life case study of where experience-grounded food valuation changes from sufficient to insufficient. We begin with a stationary ecology in which food type reliably distinguishes energetic value. We then keep the same basic idea—learning a value from realized energy—but make the ecologically decisive variable temporal and hidden. One implementation type, fruit, can be fresh and toxic or aged and safe. A learner storing one value for that type is forced to average unlike states.

This combination creates a distinctive failure. Intermittent safety does more than add uncertainty or slow avoidance. Safe high-value encounters can raise the shared estimate above the value of a consistently safe alternative. The harmful resource is then not merely tolerated; it is ranked as the better choice. We call this inversion the **lure**. The term denotes an operational result, not intention on the part of the food or the learner: a mixed-state resource is luring when the learner's final value for it exceeds the safe comparator while harmful encounters remain possible.

The article addresses four hypotheses. First, under stationary consequences, adding memory of realized energy should reduce consumption of the lower-value food relative to a paired value-blind control. Second, the behavioral change should follow relevant individual experience and disappear when the memory mechanism is disabled. Third, when toxic and safe states share one type representation, the type-level mixture should outrank the safe staple below an analytically defined toxic-state frequency, with finite-sample lure behavior recurring under several illustrative learners. Fourth, a policy whose input contains no age information should have zero ability to select a non-monotonic safe age window.

These hypotheses separate capacity from information. The value-memory architecture is designed; its acquired contents and resulting food choices depend on experience. Study 1 asks whether that capacity is sufficient when the representation preserves a stable outcome distinction. Study 2 asks what fails when it does not. This design does not test whether the learning architecture itself evolves, whether agents understand food semantically, or whether the lure changes survival and reproduction in a full ecology. It instead identifies a precise representational boundary that any broader evolutionary interpretation would first have to cross.

## 2. Conceptual Framework

### 2.1 Outcome-grounded learning rather than semantic instruction

We describe the learner as **outcome-grounded**, not reward-free. After an ingestion event, the metabolism model computes energy from the food's physical composition and the agent's digestive profile. That realized energy changes the agent's energetic state and is also recorded in food-value memory. No separate label says “prefer plant,” “avoid seed,” “fresh fruit is toxic,” or “age three to six is safe.” The architecture supplies an ability to remember and compare consequences, whereas the direction of preference is acquired from those consequences.

This distinction is narrower than a claim of unrestricted emergence. The memory index, update rate, acceptance rule, and available sensory variables are researcher-designed. A behavior is emergent here only in the operational sense that a specific preference or avoidance pattern is not directly encoded and appears through interactions among designed components. This restrained usage follows the broader Artificial-Life need to state which organization is endogenous to a run and which organization was placed in the model (Gershenson et al., 2020; Gershenson, 2023).

### 2.2 Three layers of the decision problem

The food decision can be separated into three layers. The **physical layer** contains the food's composition, age, toxin state, and metabolic effect. The **perceptual layer** maps some of those properties into an observation available to the agent. The **valuation layer** updates a stored estimate and applies a choice rule. In Study 1, implementation food type is a sufficient discriminator for the focal comparison: `raw_seed` and `raw_plant` have different stable energetic consequences. In Study 2, `raw_fruit` aliases fresh-toxic and aged-safe states because age is excluded from the value key.

An estimator cannot recover a distinction its input never represents. Additional sampling may reduce uncertainty about the mixture mean while leaving state discrimination impossible. This is why the study separates two outcomes. The **lure rate** is a finite-sample, learner-dependent measure of how often the mixture is ranked above the staple. **Safe-window discrimination** is a representation-level property: if the action depends on one type value and all ages share that value, eating probability cannot vary with age.

### 2.3 Sufficiency and failure as one experimental arc

Testing only failure would leave open whether the value mechanism can learn a simpler stable distinction. Testing only success would invite an overly broad conclusion that direct energetic experience is generally sufficient for adaptive foraging. The two-study arc creates a positive control and a boundary test. Stationary value learning establishes what the mechanism can do; temporal aliasing identifies the missing information that prevents a superficially similar task from being solved.

## 3. Methods

### 3.1 Simulation platform and claim scope

Both studies used components from the Artificial Evolution Python simulation. Agents occupy a two-dimensional grid, move, encounter resources, expend energy, and ingest items that satisfy physical edibility constraints. The metabolism layer computes digestible energy from food mass and composition together with the agent body's enzyme profile. The studies interrogate within-lifetime food valuation. Although the wider platform contains ecological and evolutionary mechanisms, no selection across generations was part of the reported comparisons.

The two studies intentionally operate at different levels. Study 1 uses the spatial world and its resource encounters, holding the ecology in an abundant-energy regime to isolate valuation from starvation. Study 2 uses a controlled encounter harness that drives the same toxin application and value-update functions while removing search, mortality, and spatial access. This layered design improves mechanistic identification, but it means that Study 2 cannot support claims about survival, population dynamics, or evolutionary fitness.

### 3.2 Study 1: stationary food-value learning

#### 3.2.1 Environment and agents

The stationary experiment used a 100 by 100 grid with 50 founder agents, body configuration 37 (`sensor=2, muscle=2, armor=0, brain=2`), metabolism model v2, and a 3,000-tick horizon. Agents were kept effectively energy-abundant by scaling food energy by 50 and metabolic drain by 0.05. Mortality was disabled, and no births occurred in the frozen runs. The configuration spawned low-value `raw_seed` resources at a rate parameter of 6 per tick while the existing plant life cycle supplied `raw_plant` resources.

The focal foods were both edible. Under the controlled configuration, realized learned values were 50 energy units for `raw_seed` and 250 for `raw_plant`. These names are implementation identifiers used for storage and telemetry; the agent did not receive their human-language meanings or an explicit quality label.

#### 3.2.2 Value-blind and value-memory conditions

The control arm retained the baseline value-blind consumption path. If a resource met ingestion constraints, the agent could eat without comparing the resource's energy with a learned food value. Spatial state and other existing behavior could still affect encounters; only the focal value-memory mechanism was disabled.

The treatment arm enabled a private `food_value_memory` dictionary for each agent, indexed by food type. On the first consumption of a type, the realized energy initialized its value. Later meals updated that value by an exponential moving average,

`V_(t+1)(k) = V_t(k) + alpha [E_t(k) - V_t(k)]`,

where *k* is food type, *E* is realized energy, and `alpha = 0.3`. Unknown types were sampled at least once. For known foods, the agent accepted type *k* when its value was at least a fraction `q = 0.5` of the best value it had learned. Thus, after learning values near 50 and 250, the seed fell below the threshold `0.5 x 250 = 125`. An energy floor allowed indiscriminate eating during emergency starvation, but the abundant-energy regime was selected so that this safeguard would not dominate the focal comparison.

The memory is individual and is neither global nor socially transmitted. Offspring did not arise in the frozen experiment, and no result concerns inherited or imitative learning.

#### 3.2.3 Paired design and outcomes

The confirmatory comparison used ten seeds, `20260610` through `20260619`. Each seed was run once with value memory disabled and once with value memory enabled. All other command-line parameters were identical. Pairing the same seed and configuration across arms controls a substantial part of stochastic variation in world initialization and event generation.

The prespecified primary outcome was the total number of `raw_seed` meals in a run. The seed/run, not the agent or tick, was the inferential unit. Secondary outcomes were low-value meals in three successive 1,000-tick windows and individual event order: first seed meal, first plant meal, and first seed skip. Skip-event counts describe behavior but are not treated as independent observations.

For each seed, the paired effect was `D_i = meals_control,i - meals_memory,i`. We report arm means and standard deviations, the mean paired difference, a 95% *t* interval across ten seed-level differences, and an exact two-sided paired sign-flip test over all `2^10` possible label exchanges. The mean within-pair ratio is descriptive because ratios were not the primary scale. The original analysis also computed an unpaired Mann–Whitney test; it is not used as primary evidence because it ignores the matched design.

The meal outcome is not exposure-normalized. An eligible-choice denominator was not frozen for the primary batch, so meal counts can reflect both acceptance decisions and differences in subsequent encounter trajectories. Event ordering and memory ablation help identify the mechanism, but they do not fully remove this limitation.

### 3.3 Study 2: hidden temporal toxicity

#### 3.3.1 Two hidden states under one observable type

The controlled toxin harness used one observable implementation type, `raw_fruit`, with two age states. Fresh fruit at age zero invoked the simulation's acute toxin pathway and yielded approximately `V_f = 2` net energy units. Aged fruit at or beyond four ticks had detoxified and yielded `V_a = 10`. A consistently safe `raw_plant` staple had stored value `V_s = 5`. The agent's value representation contained the type but not the fruit's age or toxin state.

Let *p* be the probability that an encountered fruit is fresh and toxic. A converged sample-average type estimate is

`V_mix(p) = p V_f + (1-p) V_a = 10 - 8p`.

The mixture is ranked above the staple when

`10 - 8p > 5`,

which gives the analytic boundary `p < 5/8 = 0.625`. This boundary is conditional on the selected energetic values. It is not a biological constant and does not predict the exact finite-horizon lure rate of every update rule.

#### 3.3.2 Replication and primary measure

For each toxic-state frequency, the experiment used 30 independent seed/runs. Each seed contained 100 agent trials, and each agent received 40 fruit opportunities. The tested toxic fractions were 0.20, 0.30, 0.40, 0.50, and 0.60. Agents were reset to a sated energy state before each opportunity so that the decision rule, rather than starvation, determined whether the fruit was sampled.

The primary finite-sample outcome was the seed-level percentage of agents whose final fruit value exceeded the staple value. Such agents were operationally classified as lured. Secondary outcomes for the simulation gate were toxic meals as a percentage of consumed fruit and mean net energy per consumed fruit. An age-aware comparison that consumed only aged fruit defined a benchmark of zero toxic fruit meals and 10 energy units per fruit. This is a designed comparison, not an evolved policy.

Means and normal-approximation 95% confidence-interval half-widths were calculated across 30 seed-level percentages. Agents within a seed were not counted as independent inferential replicates.

#### 3.3.3 Illustrative learning rules

Four rules were tested to distinguish a representation-level effect from a quirk of the simulation's gate.

1. **Simulation gate:** first tasting followed by an exponential moving average with `alpha = 0.3` and a hard relative acceptance gate with pickiness 0.6. A poor early sample can stop later tasting.
2. **Epsilon-greedy sample average:** optimistic initialization, incremental sample-average updating, and random fruit exploration with probability 0.1.
3. **Softmax sample average:** optimistic initialization, incremental sample-average updating, and Boltzmann choice with temperature 2.
4. **Greedy sample average:** optimistic initialization, incremental sample-average updating, and fruit selection while its estimate exceeds the staple.

These rules span continued stochastic exploration and hard gating, but they are illustrative rather than exhaustive. Their exact lure percentages depend on initialization, update dynamics, exploration, and the 40-opportunity horizon.

#### 3.3.4 Non-monotonic safe-window test

A second condition made fruit toxic before age 3, safe from ages 3 through 6 inclusive, and toxic again from age 7. Each agent trained on 40 randomly sampled ages from 0 through 9. The final policy was then queried once at every age. Safe-window discrimination was defined as

`Delta_window = P(eat | 3 <= age < 7) - P(eat | age < 3 or age >= 7)`.

Because every query presents the same type value and age is absent from the policy input, the type-only representation implies `Delta_window = 0`. The finite simulation therefore checks implementation consistency with a deterministic representational result; it is not an independent statistical discovery.

### 3.4 Reproducibility and evidence boundaries

Compact source-data tables were regenerated from the completed Study-1 JSON runs and from the Study-2 harnesses. Automated tests cover the publication statistics and toxin mechanism. The current article package preserves the source tables, raw stationary runs, analysis code, and a frozen toxin supplement. Before journal upload, the exact generator version for the stationary runs must be tied to a tagged release, the public archive must receive a persistent DOI, and the human author must read and verify every cited work.

No post hoc outcome is presented as a new independent replicate. Study-1 time windows are repeated observations within the same ten runs. Study-1 agent traces are nested within runs. Study-2 agents are nested within seeds. All inferential summaries therefore use the seed/run as the unit.

## 4. Results

### 4.1 Stationary value memory reduced low-value consumption in every pair

The value-blind arm consumed a mean of 1,945.3 low-value seed meals per run (SD 248.2). The value-memory arm consumed 423.0 (SD 65.1). The mean paired reduction was 1,522.3 meals (SD 253.9; 95% *t* interval 1,340.7–1,703.9). All ten paired seeds favored the value-memory condition, and the exact two-sided paired sign-flip test gave *p* = 0.001953125. The mean within-pair control/memory ratio was 4.70.

| Seed | Value blind | Value memory | Paired reduction |
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

The temporal pattern was consistent with acquisition. Mean low-value meals in the value-memory arm declined from 285.6 in ticks 0–1,000 to 106.3 in ticks 1,000–2,000 and 31.1 in ticks 2,000–3,000. The corresponding value-blind means were 709.6, 671.7, and 564.0. These window values are descriptive repeated measures rather than three additional experiments (Figure 1).

![Figure 1](figure_01_stationary_learning.png)

**Figure 1. Stationary food-value learning in the spatial artificial ecology.** (A) Each line joins matched value-blind and value-memory runs for one random seed. Every pair shows lower low-value consumption with memory. (B) Mean low-value meals per 1,000-tick window; ribbons show 95% *t* intervals across the same ten seed/runs. Window observations are descriptive, while the paired 3,000-tick total is the confirmatory outcome.

### 4.2 Individual event order matched the proposed mechanism

All 500 treatment agents tasted `raw_seed`. Of these, 491 also tasted the higher-value `raw_plant`, and every one of those 491 later skipped the lower-value seed. The remaining nine agents never recorded plant experience and did not skip the seed. No treatment agent skipped before recording the higher-value comparator. Across the 491 agents that completed this event sequence, delay from first plant experience to first seed skip ranged from 1 to 783 ticks (mean 93.3; median 56). These agent observations are mechanistic traces nested within ten runs, not 491 independent replicates.

The value-memory runs recorded 265,347 seed-skip events in total. The matched value-blind runs recorded none, and none of their 500 agents was classified as a seed skipper. Disabling memory therefore removed the target behavior while leaving the shared spatial configuration unchanged.

### 4.3 Intermittent safety raised a mixed resource above the safe staple

The analytic type mixture `V_mix = 10 - 8p` exceeds the staple value of 5 below 62.5% toxic encounters. At the headline condition of 30% toxicity, its expectation is 7.6. This value is greater than the staple even though a fresh encounter yields only 2 and remains harmful relative to both the staple and aged fruit.

In finite runs using the simulation gate, 63.3% ± 1.3 percentage points of agents ended with fruit ranked above the staple at 30% toxicity. Consumed fruit meals were 30.0% toxic on average, and mean net energy was 7.60 per consumed fruit, compared with 10 and zero toxic meals for the age-aware benchmark. Thus the type-only learner captured approximately 76% of the aged-fruit benchmark energy per meal while continuing to ingest the harmful state.

The simulation-gate lure rate declined as toxic frequency increased: 79.5% at 20%, 63.3% at 30%, 41.8% at 40%, 19.4% at 50%, and 5.6% at 60%. The direction matches the declining mixture value, but the finite percentages do not form a step at the analytic 62.5% boundary because the gate can stop sampling after unfavorable early outcomes.

### 4.4 The lure recurred across four illustrative learners

At 30% toxicity, lure rates were 63.3% ± 1.3 for the simulation gate, 92.7% ± 0.8 for epsilon-greedy, 99.2% ± 0.3 for softmax, and 62.1% ± 1.7 for greedy sample average (Figure 2). Continued exploration did not necessarily rescue the learner. Epsilon-greedy and softmax sampling more reliably estimated the mixed expected value, which remained above the staple, and therefore produced higher lure rates than the hard simulation gate.

| Toxic encounters | Simulation gate | Epsilon-greedy | Softmax | Greedy sample average |
| ---: | ---: | ---: | ---: | ---: |
| 20% | 79.5 ± 1.0 | 97.5 ± 0.5 | 99.8 ± 0.2 | 77.4 ± 1.3 |
| 30% | 63.3 ± 1.3 | 92.7 ± 0.8 | 99.2 ± 0.3 | 62.1 ± 1.7 |
| 40% | 41.8 ± 1.8 | 80.7 ± 1.2 | 94.5 ± 0.9 | 46.8 ± 2.1 |
| 50% | 19.4 ± 1.4 | 58.0 ± 1.6 | 80.2 ± 1.3 | 28.2 ± 1.7 |
| 60% | 5.6 ± 0.8 | 28.4 ± 1.6 | 50.5 ± 1.8 | 10.8 ± 0.9 |

![Figure 2](figure_02_temporal_lure.png)

**Figure 2. Intermittent safety creates a lure under type-only valuation.** (A) Expected mixed-fruit value as a function of toxic-state probability. The mixture exceeds the safe staple below the analytic boundary `p*=0.625`. (B) Percentage of agents whose final fruit value exceeded the staple under four illustrative learners. Points are means across 30 seed/runs; error bars are normal-approximation 95% intervals from seed-level percentages. Each seed contained 100 agents with 40 fruit opportunities per agent.

### 4.5 Type-only valuation could not identify a safe temporal window

In the toxic-safe-toxic condition, the probability of eating was equal inside and outside the safe age window. The resulting discrimination was 0.0 percentage points in every seed. This is the expected implementation consequence of giving the policy one value for all fruit ages. The result does not imply that temporal discrimination is impossible in principle. It implies that it is impossible for this policy until age, a correlated cue, or an inferred belief state enters the decision representation.

## 5. Discussion

### 5.1 Direct consequences were sufficient only under a stable category-outcome map

Study 1 supports the first two hypotheses within the tested abundant-energy ecology. Enabling individual memory of realized energetic consequences reduced consumption of the lower-value food across every paired seed. The decline across time windows, the absence of skipping with memory disabled, and the ordering of individual experience before skipping all agree with the proposed mechanism. The result is stronger than a difference between two final aggregates: the system changed in the predicted direction at run, temporal, and event-order levels.

The claim remains deliberately narrow. The agent did not discover a new learning rule; it used a designed memory and comparison rule. It did not learn without consequences; realized energy was the signal. It did not infer semantic concepts such as nutrition or toxicity. What the experiment demonstrates is that a minimal type-level memory, grounded in the agent's own metabolic accounting, was causally sufficient to generate acquired diet selectivity when type reliably separated the energetic outcomes relevant to choice.

This positive result connects to Artificial-Life work in which adaptive behavior depends on coupled agent and environment structure. Sims (1994) and Ha (2019) emphasize how embodied design changes the behavioral problem. Here the body contributes through digestion: the stored value is the energy the particular body realizes, not a label attached only for the learner. Giannakakis et al. (2025) show that task structure and network constraints shape evolved plasticity rules; our experiment holds the learning rule fixed and instead changes whether the representation matches the task structure. The two perspectives are complementary. A learning mechanism can be suitable in one ecology and systematically inadequate in another.

### 5.2 The lure is a ranking inversion, not merely noisy learning

Study 2 supports the third and fourth hypotheses. The novel element is not the general fact that hidden state makes decision-making difficult. Perceptual aliasing and partial observability already explain why one observation may be insufficient (Whitehead & Ballard, 1991; Kaelbling et al., 1998). The specific contribution is the temporal-toxicity configuration and its operational inversion: high-value safe encounters can raise a partly toxic resource above a safe comparator, converting avoidance pressure into learned preference.

This distinction matters. If fruit were always toxic with value 2, the same value framework would rank it below the staple at 5. If fruit were always aged and safe with value 10, ranking it above the staple would be adaptive for the immediate energy criterion. When both states share a value, the estimate can be statistically accurate for the mixture and behaviorally inadequate for the underlying decision. More data may improve convergence to the wrong decision variable. The high lure rates of the continued-exploration learners illustrate this point: their problem is not simply insufficient sampling but aggregation across states that require different actions.

The analytic boundary also clarifies what is general and what is protocol-specific. For two outcomes `V_f < V_s < V_a`, the converged mixture outranks the staple whenever

`p < (V_a - V_s) / (V_a - V_f)`.

Changing toxin severity or staple value moves that boundary. Finite-horizon lure percentages additionally depend on exploration, initialization, and update rules. By contrast, zero age-window discrimination follows directly from the omitted variable: any deterministic or stochastic policy whose relevant input is identical at every age must assign identical eating probabilities at every age.

### 5.3 Relationship to learning, evolution, and emergence in Artificial Life

Sasaki and Tokoro (1999) examined learned food-versus-poison distinctions within populations evolving under environmental change. Our system is less ambitious evolutionarily but more diagnostic about representation: it separates a stationary condition in which the food type is informative from a condition in which the same type aliases temporal states. Bullinaria (2017) examines interactions between direct and imitative learning; our agents use only direct experience and private memory. The absence of social transmission is a limitation for ecology, but it also prevents group information from masking the individual representational failure.

Garbus and Pollack (2024) show that environmental opportunities and simple interaction primitives can enable emergent resource exchange. The present results illustrate the inverse methodological lesson: an environmental distinction that is physically real but perceptually unavailable can prevent a relevant behavior from emerging, regardless of how meaningful that distinction appears to an observer with access to the simulator state. The modeler sees fruit age; the agent sees only fruit type.

This observer-agent gap is important when describing emergence. From the outside, one might expect an artificial organism exposed repeatedly to a safe age window to learn when fruit should be eaten. Yet the policy has no variable on which such timing could depend. Calling its failure unintelligent would obscure the designed information bottleneck. Conversely, calling any eventual storage or waiting behavior emergent would be premature unless the model contained item persistence, an action for deferral, a cue or internal state supporting temporal credit, and a selective or learning process that actually produced the behavior.

The results therefore contribute to Artificial Life as a synthetic explanation of a boundary. They show by construction and intervention that local metabolic feedback can generate diet adaptation, then identify the minimal representational change that the next level of behavior requires. This follows the journal's broader tradition of using artificial systems not only to display lifelike outcomes but to test which mechanisms are sufficient for them.

### 5.4 Alternative explanations and what the controls resolve

Several alternative explanations can be evaluated. First, the Study-1 difference could reflect random environmental variation. Pairing seeds and finding the predicted direction in all ten pairs reduces that concern. Second, the treatment could be associated with a fixed policy difference unrelated to experience. The event traces contradict a preexisting seed aversion: no agent skipped before experiencing the higher-value comparator, and agents that never experienced it did not skip. Third, the toxin lure could be a freezing artifact of the simulation gate. Its recurrence under continued-exploration and sample-average learners argues against that narrow explanation.

The controls do not resolve every alternative. Study-1 meal counts combine choice with exposure. Once an agent skips a seed, its movement and later encounters may diverge from its paired control, so the total effect includes feedback between valuation and trajectory. This feedback is ecologically meaningful but makes the primary outcome less specific than an acceptance probability conditional on a matched choice set. A future frozen batch should log every eligible encounter, comparator availability, and accept/skip decision.

The abundant-energy regime is another controlled simplification. It prevents starvation from forcing indiscriminate eating and thereby reveals the valuation mechanism. It does not establish that the same preference improves survival when energy is scarce, competitors alter access, or low-value food becomes necessary. Similarly, Study 2 resets agents to a sated state and supplies controlled encounters. Its lure could become more or less behaviorally important in a spatial ecology.

### 5.5 What would solve the hidden-state problem?

The simplest intervention is not necessarily a more complicated learner. It is a representation containing information correlated with the consequence. If fruit age were perceptible, the value key could become `(food type, age bin)`, permitting separate estimates for fresh and aged states. If age were not directly perceptible but correlated cues existed, a recurrent controller or belief-state estimator could infer it from history. These alternatives correspond to the general POMDP response of augmenting the effective state with memory or beliefs (Kaelbling et al., 1998).

Selective consumption of an already aged item is distinct from active storage. Storage followed by delayed eating requires at least four additional capacities: persistent item identity, an action that changes the time of consumption, a way to associate the later consequence with the earlier deferral decision, and a policy that trades immediate opportunity against future value. None is demonstrated here. The safe-window result should therefore motivate an experiment on those capacities, not be reported as evidence that deferral evolved.

### 5.6 Implications for experimental design in synthetic ecologies

The paired studies suggest a practical audit for claims about learned or emergent foraging. First, identify the physical variable that changes the consequence. Second, state exactly which proxy for that variable is available to the agent. Third, specify the value key or state representation that stores experience. Fourth, include a positive control in which the proposed learner can succeed. Fifth, include an ablation that removes the mechanism. Sixth, distinguish analytic impossibility from finite-sample performance. Finally, keep the outcome scale aligned with the claim: meal choice supports a behavioral conclusion, whereas survival, reproduction, and selection require full-ecology outcomes.

This audit also helps separate an externally authored task reward from a consequence grounded in the artificial organism. Reward functions are not inherently inappropriate; reinforcement learning explicitly studies adaptation through reward (Sutton & Barto, 2018). The important issue is transparency about where the objective originates. In our system, metabolic energy is both a component of the artificial organism's state and the learned consequence, but the experimental regime still determines which consequences matter and which choices are available.

## 6. Limitations and Required Next Experiments

The article has six principal limitations. First, Study 1 contains only ten paired seeds from one abundant-energy environment. The effect is internally consistent but environmental transfer has not been tested. Second, the Study-1 primary outcome lacks an eligible-choice denominator, so consumption conflates acceptance, encounter, and trajectory feedback. Third, the learning rate and pickiness threshold were fixed rather than subjected to a preregistered sensitivity analysis. Fourth, the four Study-2 learners are illustrative, and their lure magnitudes do not establish universality across learning architectures. Fifth, the toxin harness isolates valuation from spatial ecology and does not measure mortality, survival, reproduction, or selection. Sixth, the simulation abstracts sensory physiology, digestion, toxicity, and time; the numeric boundary belongs to the chosen outcomes.

The next submission-strengthening program should be prospective. A preregistered experiment should cross representation with environment: type-only value, type-by-age value, and an age-aware deferral controller should be compared in at least two frozen ecological regimes. Study-1 choice opportunities should be logged so that acceptance probability can be estimated conditional on exposure. Study-2 outcomes should include energy balance, mortality, survival time, and reproduction only after the full spatial ecology is enabled. Seed/run should remain the inferential unit, and analysis choices should be fixed before inspecting the new outcomes.

These additions would support a stronger evolutionary claim. They are not necessary for the present representational conclusion, but they are necessary before saying that the lure lowers fitness, creates selection for temporal perception, or causes storage behavior to evolve.

## 7. Conclusion

Experience-based food valuation was sufficient to produce acquired diet selectivity in a stationary artificial ecology. Across ten paired seed/runs, the value-memory mechanism reduced low-value consumption in every pair, and individual agents changed behavior only after experiencing the higher-value comparator. The same type-level representation became insufficient when fruit safety varied with hidden age. Intermittent high-value encounters raised the mixed resource above a safe staple across an analytic region and across four illustrative learners, while a non-monotonic safe window remained invisible to the policy.

The combined result is a boundary statement about adaptive behavior in Artificial Life. Embodied consequences can ground useful learning without semantic food-quality labels, but consequences alone do not guarantee state-sensitive behavior. The distinctions needed for action must be available in perception, memory, or inferred state. Where those distinctions are absent, an artificial organism may accurately learn the value of a mixture and still choose harmfully within it.

## Data and Code Availability

Compact source tables, the completed paired Study-1 runs, analysis scripts, the Study-2 experiment harnesses, and the minimum simulation source required to reproduce the toxin results accompany the draft package. Before submission, the materials will be frozen at a tagged commit and deposited in a public DOI-granting repository. Persistent URL: [TO ADD BEFORE SUBMISSION].

## Author Contributions

Chisanupong Injun: Conceptualization, methodology, software, validation, formal analysis, investigation, data curation, visualization, writing—original draft, and writing—review and editing.

## Acknowledgments

The author thanks the school project advisor and Deebuk Phangnga Wittayayon School for administrative and institutional support. The advisor is not listed as an author because the research, software, experiments, analysis, and manuscript were completed by the author.

## Ethics Statement

The study used only software agents in a computer simulation and involved no human participants, human data, animals, or biological specimens.

## Generative-AI Disclosure

OpenAI Codex (OpenAI; https://openai.com/codex; accessed September 1, 2026) assisted with literature discovery, evidence auditing, statistical and claim-boundary review, manuscript restructuring, and drafting. The system is not an author. The human author must read the cited sources, verify every analysis and statement, revise the disclosure to match the final workflow, and accept full responsibility before submission.

## Funding Statement

This research received no external funding.

## Competing Interests

The author declares no competing interests.

## References

Bedau, M. A., McCaskill, J. S., Packard, N. H., Rasmussen, S., Adami, C., Green, D. G., Ikegami, T., Kaneko, K., & Ray, T. S. (2000). Open problems in artificial life. *Artificial Life, 6*(4), 363–376. https://doi.org/10.1162/106454600300103683

Bullinaria, J. A. (2017). Imitative and direct learning as interacting factors in life history evolution. *Artificial Life, 23*(3), 374–405. https://doi.org/10.1162/ARTL_a_00237

Dorin, A., & Stepney, S. (2024). What is Artificial Life today, and where should it go? *Artificial Life, 30*(1), 1–15. https://doi.org/10.1162/artl_e_00435

Garbus, J., & Pollack, J. (2024). Emergent resource exchange and tolerated theft behavior using multiagent reinforcement learning. *Artificial Life, 30*(1), 28–47. https://doi.org/10.1162/artl_a_00423

Garcia, J., & Koelling, R. A. (1966). Relation of cue to consequence in avoidance learning. *Psychonomic Science, 4*(1), 123–124. https://doi.org/10.3758/BF03342209

Gershenson, C. (2023). Emergence in Artificial Life. *Artificial Life, 29*(2), 153–167. https://doi.org/10.1162/artl_a_00397

Gershenson, C., Trianni, V., Werfel, J., & Sayama, H. (2020). Self-organization and Artificial Life. *Artificial Life, 26*(3), 391–408. https://doi.org/10.1162/artl_a_00324

Giannakakis, E., Khajehabdollahi, S., & Levina, A. (2025). Network bottlenecks and task structure control the evolution of interpretable learning rules in a foraging agent. *Artificial Life, 31*(2), 177–194. https://doi.org/10.1162/artl_a_00458

Ha, D. (2019). Reinforcement learning for improving agent design. *Artificial Life, 25*(4), 352–365. https://doi.org/10.1162/artl_a_00301

Kaelbling, L. P., Littman, M. L., & Cassandra, A. R. (1998). Planning and acting in partially observable stochastic domains. *Artificial Intelligence, 101*(1–2), 99–134. https://doi.org/10.1016/S0004-3702(98)00023-X

Sasaki, T., & Tokoro, M. (1999). Evolving learnable neural networks under changing environments with various rates of inheritance of acquired characters: Comparison of Darwinian and Lamarckian evolution. *Artificial Life, 5*(3), 203–223. https://doi.org/10.1162/106454699568746

Sims, K. (1994). Evolving virtual creatures. In *Proceedings of the 21st Annual Conference on Computer Graphics and Interactive Techniques* (pp. 15–22). Association for Computing Machinery. https://doi.org/10.1145/192161.192167

Sutton, R. S., & Barto, A. G. (2018). *Reinforcement learning: An introduction* (2nd ed.). MIT Press.

Touzani, K., Bodnar, R. J., & Sclafani, A. (2010). Neuropharmacology of learned flavor preferences. *Pharmacology Biochemistry and Behavior, 97*(1), 55–62. https://doi.org/10.1016/j.pbb.2010.06.001

Whitehead, S. D., & Ballard, D. H. (1991). Learning to perceive and act by trial and error. *Machine Learning, 7*, 45–83. https://doi.org/10.1023/A:1022619109594
