# ISEF Roadmap

Prepared: `2026-06-21`

## 1. Competition objective

Build this project into an `ISEF`-grade research story with:

- a clear and defensible novelty claim
- reproducible experiments
- a strong causal argument
- honest treatment of negative results
- judge-friendly deliverables that connect implementation to scientific significance

## 2. Best candidate grand thesis today

The most credible current thesis is:

`Rich embodied ecology can generate early learning and ecological feedback, but robust endogenous evolution requires additional structural conditions that are easy to miss and hard to satisfy.`

Why this works for `ISEF`:

- it is ambitious
- it is falsifiable
- it is grounded in original system-building work
- it creates room for either a positive breakthrough or a rigorous negative-results result

## 3. What ISEF judges will care about here

### Scientific quality

- Is the question precise?
- Are variables controlled?
- Are claims narrower than the evidence, not broader?
- Are negative results analyzed rather than ignored?

### Originality

- What is new compared with standard artificial life or agent-based toy simulations?
- Is the project contributing a new substrate, a new failure analysis, or a new empirical result?

### Technical depth

- Did the student build real infrastructure and not just tune a demo?
- Is the system instrumented enough to support actual conclusions?

### Rigor

- Are seeds truly independent?
- Are comparisons fair across conditions?
- Are metrics predeclared and auditable?

### Communication

- Can the project be explained cleanly to judges who are smart but not deep experts in this specific codebase?

## 4. Immediate ISEF-critical gaps

These are the highest-priority problems to close before polishing presentations:

1. `True replication`
   - audit every major stochastic path
   - ensure `args.seed` actually changes behavior in all experiment-critical randomness
   - document the seed model explicitly

2. `Population sustainability`
   - produce at least one reproducible mortal regime that does not trivially collapse before selection can matter
   - if impossible, convert that failure into a formal negative-results result with controlled evidence

3. `Endogenous evolution`
   - show inherited variation affecting outcomes across generations, not just external search over body space

4. `Claim hygiene`
   - maintain a strict wall between:
     - demonstrated findings
     - suggestive observations
     - future goals

5. `Narrative compression`
   - the project currently contains many sub-stories
   - for `ISEF`, one flagship question must dominate the presentation

## 5. Recommended flagship question

Recommended flagship question for the next cycle:

`What structural conditions are necessary for a rich artificial-life world to transition from short-term adaptive behavior into stable endogenous evolution?`

This question is stronger for `ISEF` than a vague open-ended-emergence claim because it gives the project:

- a concrete transition point
- measurable prerequisites
- space for both positive and negative evidence
- a clean story arc from constructed substrate to tested barrier

## 6. Research plan in three stages

### Stage A: credibility foundation

Goal:
make the evidence trustworthy enough that future claims survive scrutiny.

Tasks:

- fix and verify seed plumbing for all behavior-critical randomness
- define a canonical experiment schema and artifact checklist
- standardize primary metrics:
  - births
  - matured offspring
  - lineage persistence
  - replacement ratio or `R0`
  - morphology diversity
  - trait diversity
  - settlement count
  - death reasons
- add a reproducibility note to every new report

Success criterion:

- a reviewer can re-run core experiments and trust that multi-seed means independent replicate runs

### Stage B: transition experiment

Goal:
test whether the system can cross from adaptive substrate into genuine evolutionary dynamics.

Core experiment families:

- `reproduction architecture`
  - current gate model
  - continuous stochastic reproduction
  - de-synchronized mortality
  - clustering/home-fidelity enabled

- `mutation regime separation`
  - no mutation
  - trait-only mutation
  - morphology-only mutation
  - combined mutation

- `ecology pressure`
  - baseline tuned ecology
  - harsher ecology
  - dynamic ecology

Primary outputs:

- lineage branching over generations
- persistence distributions
- diversity trajectories
- evidence of selection rather than pure drift or collapse

Success criterion:

- either a stable evolving regime is found, or a rigorous map of why each candidate regime fails is produced

### Stage C: ISEF packaging

Goal:
turn the strongest result into judge-ready communication.

Deliverables:

- one clean abstract
- one research paper in IMRaD style
- one poster centered on a single causal story
- one short oral explanation with a few figure-heavy panels
- one appendix or evidence index for technical depth

## 7. Decision tree for the next few months

### If stable endogenous evolution is achieved

Then the final story should be:

- what changed structurally
- why that change mattered
- what emergent evolutionary pattern appeared
- how replication supports the claim

### If stability is still not achieved

Then the final story should be:

- why the transition fails
- which structural gates dominate the failure
- what false explanations were ruled out
- what this teaches about artificial-life design

This fallback is still legitimate science and can still be strong at `ISEF` if the method is sharp.

## 8. Concrete near-term execution plan

### Next 1 to 2 weeks

- audit RNG pathways, especially movement and partner behavior
- write one canonical reproducibility protocol
- define the official primary metrics table
- identify the one baseline body or regime that will anchor comparison runs

### Next 2 to 6 weeks

- run the population-stability redesign matrix
- isolate the effects of:
  - home fidelity
  - continuous reproduction
  - mortality desynchronization
  - food scaling
- confirm whether any regime crosses replacement sustainably

### Next 6 to 10 weeks

- run endogenous mutation experiments only after the mortality/reproduction baseline is trustworthy
- analyze lineage persistence and diversity under the successful regime, or publish the barrier map if none succeed

## 9. Suggested deliverable stack inside the repo

To stay aligned with `ISEF`, I recommend adding or maintaining these living artifacts:

- `current flagship question`
- `claim ledger`
  - proven
  - suggestive
  - disproven
- `official baseline protocol`
- `figure priority list`
- `judge-facing summary`
- `advisor-facing technical summary`

## 10. Final recommendation

Do not try to present this as a giant everything-project.

For `ISEF`, the winning move is to compress the work into one sharp scientific transition:

- from ecological substrate
- to learning signal
- to reproductive bottleneck
- to either successful endogenous evolution or a principled explanation of why it fails

That is the version of this project most likely to feel original, rigorous, and memorable.
