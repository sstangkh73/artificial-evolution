# ODD Model Description — Verified Core Draft

**Model:** Artificial Evolution temporal-toxicity foraging study

**ODD version followed:** Grimm et al. (2020), https://doi.org/10.18564/jasss.4259

**Code basis:** frozen tag `prereg-resource-age-2026-09-14`
**Status:** the focal toxin, learning, scheduling, and outcome mechanisms below have been checked against the frozen implementation. The full environment state catalogue and parameter tables for E1–E5 remain to be completed before submission.

## 1. Purpose and patterns

The model tests whether a bounded artificial forager can learn an appropriate food choice when one implementation type contains resource states with different consequences. Raw fruit can be toxic, safe, and toxic again as the same food item ages. The focal comparison asks whether supplying food age in the learner's value key restores state-sensitive discrimination, whether this restoration is caused by information rather than memory capacity, and whether it improves survival under different resource payoffs.

The model is evaluated against internally generated patterns rather than an external biological data set:

- encounter-conditional acceptance of objectively safe and toxic fruit;
- learned value by representation key;
- founder follow-up time and cause of death;
- toxin exposure and toxin-related damage;
- resource encounters, availability, and starvation;
- reproducibility under matched seeds and frozen specifications.

The model cannot establish cue discovery because food age is supplied directly to the B2 decision key. It cannot establish an optimal value of information because the learning and choice rules are fixed. The E-series produced no births and therefore cannot establish evolutionary response across generations.

## 2. Entities, state variables, and scales

| Entity | Focal state variables | Role in this study | Implementation |
|---|---|---|---|
| Agent | identifier, position, age, energy, durability, somatic damage, alive/death state, starvation duration, body traits including toxin tolerance, learned food-value map, encounter and ingestion counters | Moves, encounters food, decides whether to eat, learns from realized energy, accumulates toxin costs, and dies | `agents/agent.py`: `Agent`, `tick`, `_food_worth_eating`, `_learn_food_value`, `_apply_toxin`, `_apply_aging`, `_resolve_life_state` |
| Food resource | grid position, implementation kind, nominal energy, source, creation tick, optional parent-plant identifier | Supplies energy and, for raw fruit, an age-dependent toxin load | `world/environment.py`: `FoodResource`, food spawn/decay/consume methods |
| Plant/seed | position, life-cycle state, biomass, creation and fruiting history, dispersal fields | Produces the staple raw-plant resource and maintains a spatially explicit renewable food background | `world/environment.py`: plant lifecycle and `seed_initial_plants` |
| Environment | tick, 100 × 100 grid, food and plant collections, spatial fertility/biome/physical fields, experimental switches and coefficients | Updates resource dynamics before agent actions and supplies the parameters used by agent rules | `world/environment.py`: `Environment`, `step` |
| Experiment run | RNG seed, arm parameters, horizon, initial cohort, event and outcome records | One arm within one matched seed | `scripts/run_long_emergence_watch.py`; `scripts/food_value_study_driver.py` |

Space is a 100 × 100 discrete grid. Distance in sensing and movement rules is measured in grid units. Time is measured in simulation ticks; no conversion to biological time is claimed. The focal confirmatory runs began with 50 generation-0 founders, a population cap of 250, 2,500 mature plants, a standing-food cap of 2,000 for the base food process, 12 natural seed-rain attempts per tick, and 20 toxic-fruit spawn attempts per tick. E6 used an 800-tick horizon; T2-RB used 400 ticks. Runs ended earlier if all agents died.

Founder age was deterministically spread over `[ADULT_AGE, MAX_AGE)` by founder index. This avoids a synchronized age cohort without consuming random numbers. All focal agents used body plan 37. E3 alone added toxin-tolerance variation using a dedicated RNG stream; the E6 and T2-RB founders shared the body plan's baseline tolerance.

## 3. Process overview and scheduling

Each run uses the following order, verified from `scripts/run_long_emergence_watch.py`, `world/environment.py`, and `agents/agent.py`:

1. Stop if the wall-clock guard has fired or the live-agent list is empty.
2. Record active nest owners, then advance the environment by one tick.
3. Within the environment update: rotate neural signals; recover fertility; decay managed food, soil disturbance, and existing food; update physical and radiation fields; apply natural seed rain and plant lifecycle; spawn base, low-value, and toxic food; update large animals, nests, hearths, and objects.
4. Compute standing food per live agent, update social groups, and set each agent's survival context.
5. Iterate through a copy of the live-agent list in list order. For each agent: increment age; charge base, brain, and somatic-maintenance energy; resolve starvation or durability death; update internal state; move or act; encounter and decide on food; process ingestion; process gut contents; apply environmental danger; resolve death again; apply aging damage; then evaluate reproduction.
6. When food is eaten, compute digestible energy first. Toxin costs are applied to that bite before value learning and before the net energy is credited to the agent. Thus the learned value is the experienced post-toxin energy.
7. Archive and remove dead agents during the agent loop. Collect newborns separately and append them after all current agents have acted, so newborns first act on the next tick.
8. Aggregate events and telemetry after the agent updates.

Agent order is therefore sequential within a tick, while matched arms begin from the same main RNG seed. The B3 sham mapping consumes no random draw, preventing the representation manipulation itself from shifting the shared RNG stream.

## 4. Design concepts

### Basic principles

The learner updates food values from the net energy obtained after ingestion. Temporal toxicity makes the consequence of a raw-fruit encounter depend on the resource's creation time. Avoidance trades toxin exposure against the opportunity cost of rejecting a high-energy resource.

### Emergence

Acceptance rates, learned values, survival, toxin exposure, and starvation emerge from interactions between the fixed decision rule, spatial encounters, resource turnover, metabolism, and toxin dynamics. The experimenter supplies the food-age cue to B2, the representation mode, toxicity profile, payoff, and all other arm parameters.

### Adaptation and objectives

Within-lifetime adaptation is limited to updating the food-value map. The rule does not optimize expected lifetime or reproductive fitness, and the oracle is only a toxin-avoidance ceiling. It retains the same starvation override as the learners.

### Learning, prediction, and sensing

For a value key `k`, the first consumed item initializes `V(k)` to the realized net energy `r`. Later observations use an exponential moving average:

`V_new(k) = V_old(k) + alpha [r - V_old(k)]`,

where `alpha = 0.3`. A previously unseen key is always sampled once. At energy at or below 6, agents eat regardless of learned value. Otherwise an item is eaten when `V(k) >= 0.6 × max_j V(j)`; if no positive best value exists, it is eaten.

The representation arms are:

- B1, type only: `k = food_kind`;
- B2, type by resource age: `k = food_kind@min(floor(age/20), 8)` in E6;
- B3, capacity-matched sham: the same nine-bin key range, with the bin assigned by a deterministic SplitMix64-style hash of resource creation tick and encounter position;
- B4, oracle: reject fruit whose realized toxin excess is positive, except at the starvation override.

Resource age is `max(0, current_tick - created_tick)`. It is supplied perfectly to B2. The type-only learner cannot condition its decision on this state, and the sham provides the same nominal key capacity without age information.

### Stochasticity

A seeded main `Random` stream controls spatial initialization, food decay and spawn attempts, environmental updates, movement, and other stochastic events. The run seed is held constant across arms within a matched seed. Founder age spreading and B3 key assignment are deterministic and consume no main-stream draws. E3's founder-tolerance variation uses a separate stream seeded as `run_seed XOR 0x70583EED`; this is inactive in E6 and T2-RB.

### Observation

For each run, safe-versus-toxic discrimination is

`D = P(eat | safe encounter) - P(eat | toxic encounter)`.

Founder follow-up is each founder's final attained age minus its deterministic initial age, restricted by the run horizon; the run outcome is the mean over founders. The inferential unit is the seed. Arm contrasts use within-seed paired differences. E6 first computes B2-B3 within each energy and seed, then fits one ordinary-least-squares slope over the five realized energy levels for each seed.

## 5. Initialization

| Parameter | E6 | T2-RB | Source |
|---|---:|---:|---|
| world width × height | 100 × 100 | 100 × 100 | frozen specifications |
| founders | 50 | 50 | frozen specifications |
| founder age spread | deterministic across adult range | deterministic across adult range | frozen specifications and `run_long_emergence_watch.py` |
| body plan | 37 | 37 | frozen specifications |
| initial mature plants | 2,500 | 2,500 | frozen specifications |
| natural seed rain | 12 per tick | 12 per tick | frozen specifications |
| toxic-fruit spawn attempts | 20 per tick | 20 per tick | frozen specifications |
| food detection threshold | 0.01 | 0.01 | frozen specifications |
| vision horizon | 200 | 200 | frozen specifications |
| value learning | enabled | enabled | frozen specifications |
| pickiness | 0.6 | 0.6 | frozen specifications |
| starvation override energy | 6 | 6 | frozen specifications |
| starvation counter threshold | 15 life-state checks | 15 life-state checks | driver default plus enabled starvation death |
| metabolic drain multiplier | 0.2 | 0.5 | frozen specifications |
| run horizon | 800 ticks | 400 ticks | frozen specifications |
| seeds | 30, 20260970–20260999 | 50, 20261000–20261049 | frozen specifications |

The environment is generated from the main run seed. Mature plants are then placed stochastically on walkable, sufficiently fertile cells, with first-fruiting times staggered. Founders are placed by the `frontier_safe_high_food` strategy. Exact E1–E5 initialization differences will be tabulated from their archived specifications in the completed supplement.

## 6. Input data

No empirical external data drive the simulations. Frozen JSON specifications define controlled model inputs, arms, seeds, horizons, and analysis decisions. E6 varies only the raw-fruit energy multiplier and representation arm on the shared base configuration. T2-RB varies the toxicity profile or constant-potency scale on its shared base configuration.

## 7. Submodels

### Food energy

Under metabolism v2, pre-toxin energy for food item `f` and body `b` is computed as

`E0 = round[mass(f) × sum_n composition(f,n) × enzyme(b,n) × density(n)]`.

The code then applies and rounds the global food-energy multiplier, followed by a separately rounded raw-fruit-only multiplier. In the focal body plan, the realized staple energy was 5. E6 verified realized raw-fruit energies of 4, 5, 6, 8, and 10 in every output rather than inferring them from command-line values.

### Temporal toxicity and toxin costs

Raw fruit has mass 1.2 and toxin fraction 0.30. Its unscaled toxin load is therefore 0.36. With resource age `a`, potency is:

- monotonic M: `p(a) = max(0, 1 - a/120)`;
- non-monotonic W: `p(a) = 0` for `40 <= a < 80`, and `1` otherwise;
- constant controls: `p(a) = 1`, multiplied by the specified constant-potency scale.

Realized excess is `x = max(0, 0.36 × p(a) × potency_scale - toxin_tolerance)`. When `x > 0`, chronic damage increases by `5x` and the bite's net energy is `round(E0 - 50x)`. These operations precede value learning and energy credit.

### Aging, starvation, and death

At the start of an agent tick, metabolism and brain costs are multiplied by the experimental drain multiplier. Somatic maintenance also carries an energy price through a fractional debt accumulator. With aging enabled, gross damage per tick is

`g = aging_damage_rate × mass_specific_metabolic_rate / damage_resistance + aging_intake_damage_coeff × absorbed_energy`.

Repair is the smaller of `aging_max_repair_fraction × g` and `somatic_maintenance × repair_efficiency × aging_repair_gain`. Net damage is added after movement, ingestion, toxin costs, gut processing, and environmental danger. Senescence occurs when accumulated damage reaches the configured threshold. The starvation counter advances whenever the life-state resolver sees zero energy and death occurs when the counter reaches 15. Because the resolver runs before and after action, the counter can advance twice within one simulation tick when energy remains zero; successful feeding resets it at the next resolver call. Durability depletion is a separate cause of death.

### Resource renewal and decay

The environment begins with a spatially heterogeneous mature-plant background. Each tick it applies stochastic food decay before plant updates and new food spawn attempts. Raw plant food comes from both the base wild-food process and plant lifecycle; raw fruit comes from the toxin-study spawn process. Existing rejected fruit remains in place until consumed or decayed and can therefore be encountered repeatedly. This is why encounter-conditional acceptance is the behavioral outcome and raw meal count is secondary.

## Verification and validation supplement

The current evidence package separates code verification from model interpretation:

- unit and regression tests cover the focal learning, age-key, sham-key, toxin, telemetry, frozen-spec, and analysis behavior;
- batch validators enforce complete arm-by-seed cells, frozen provenance, effective parameter values, and censoring fields;
- B2-B3 is a controlled information-content contrast, while B2-B1 remains a secondary baseline;
- mechanism gates check discrimination, key coverage, learned safe-versus-toxic values, and exposure;
- E5 and T2-RB test transfer to a higher-drain composite regime;
- the model remains an abstract artificial ecology with a supplied perfect age cue, fixed learning policy, and no demonstrated reproduction in these experiments.

Before submission, this document still requires the full E1–E5 parameter table, a complete catalogue of state variables that affect movement and energy access, software/runtime versions, and a cross-check against the archived public code release.
