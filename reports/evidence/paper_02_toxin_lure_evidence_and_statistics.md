# Paper 2 Evidence and Statistics Audit

## Primary hypothesis

When one observable food type mixes fresh-toxic and aged-safe states, a learner
that assigns one value to the type cannot discriminate the states and may rank
the mixed food above a consistently safe staple. This inversion from avoidance
to pursuit is termed the **lure**.

## Analytic result

Let fresh fruit yield `V_f = 2`, aged fruit `V_a = 10`, safe staple `V_s = 5`,
and let `p` be the probability that a fruit encounter is fresh/toxic. A converged
type-only estimate is:

`V_mix(p) = p V_f + (1-p) V_a = 10 - 8p`.

The mixed fruit is ranked above the staple when:

`10 - 8p > 5`, hence `p < 5/8 = 0.625`.

The inability to choose differently by age is stronger than this magnitude
claim: if the policy input contains only one type value, the food's age cannot
change the decision. Safe-window discrimination is therefore zero by
representation, independent of the update rule.

## Controlled empirical design

- Statistical unit: seed/run.
- Replication: 30 seeds.
- Within each seed: 100 simulated agents × 40 encounters.
- Hidden states: fresh/toxic net energy ≈2; aged/safe net energy ≈10.
- Comparator: consistently safe staple value 5.
- Toxic-state frequencies: 20%, 30%, 40%, 50%, 60%.
- Learners: simulation EMA gate, epsilon-greedy sample average, softmax sample
  average, and greedy sample average.

## Headline results

- Simulation gate at 30% toxic encounters: 63.3% ± 1.3 percentage points
  of agents end with fruit ranked above the staple.
- Toxic meals remain approximately 30% at that condition.
- Mean energy is approximately 7.6 per meal versus 10 for the age-aware optimum.
- Across the illustrative rules, lure percentages at 30% toxic are 63.3%±1.3%
  (simulation gate), 92.7%±0.8% (epsilon-greedy), 99.2%±0.3% (softmax), and
  62.1%±1.7% (greedy sample average).
- Non-monotonic safe window: type-only discrimination is 0.0 points by
  representation; the finite simulation reports equal eating probability inside
  and outside the safe window.

Exact regenerated values and CI half-widths are in `../source_data/`.

## Evidence supporting

- The analytic boundary predicts the direction of the finite simulations.
- The lure persists across four illustrative update/choice rules.
- A broad frequency and toxin-severity sweep argues against a single tuned point.
- Constant toxicity is correctly avoided in the same value framework, whereas
  intermittent safety can raise the mixture above the safe comparator.

## Evidence against or limiting

- The four learners are illustrative, not an exhaustive class.
- The controlled harness isolates the toxin and valuation mechanism; it is not a
  full spatial ecology.
- Agent trials within a seed are not independent inferential replicates.
- The sated regime does not demonstrate mortality, survival, reproductive, or
  evolutionary cost.
- Age-aware deferral/storage has not emerged and was not implemented as a result.
- Exact lure percentages depend on initialization, exploration, horizon, and the
  decision rule even though the representation-level discrimination limit does not.

## Alternative explanations

1. Finite-horizon initialization can change the magnitude of the lure.
2. The safe staple value and two-state energies determine the analytic boundary.
3. The effect could become behaviorally irrelevant when spatial search or
   starvation dominates decisions.
4. A richer state representation may solve the failure without storage or
   evolutionary change.

## Confidence

High for the type-only representation limit and the existence of the lure in the
tested mechanisms; moderate for generality beyond those mechanisms; no current
evidence for full-ecology fitness consequences.
