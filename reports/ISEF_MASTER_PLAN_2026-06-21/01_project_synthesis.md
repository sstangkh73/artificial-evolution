# Project Synthesis

Prepared: `2026-06-21`

## 1. Project in one sentence

`artificial-evolution` is an artificial life research project that asks whether adaptive behavior, ecological coupling, and eventually true evolution can emerge in a simulated world without hand-coded high-level strategies.

## 2. Core scientific question

Current canonical question from [docs/RESEARCH_QUESTION.md](/C:/artificial-evolution/docs/RESEARCH_QUESTION.md):

> Can efficient body structures emerge naturally under environmental constraints and energy limitations?

Based on the newer reports and code, the practical research program is already broader than that one sentence. The project is now testing:

- whether agents can learn reward-place associations
- whether agent actions can causally feed back into plant ecology
- whether proto-farming-like substrate effects can appear without semantic teaching
- whether a self-sustaining, reproductive population can exist long enough for endogenous evolution to matter

## 3. What the codebase currently is

The current system is not just a minimal body-comparison prototype. The main code in [agents/agent.py](/C:/artificial-evolution/agents/agent.py), [agents/body.py](/C:/artificial-evolution/agents/body.py), [world/environment.py](/C:/artificial-evolution/world/environment.py), and [simulation/runner.py](/C:/artificial-evolution/simulation/runner.py) already includes:

- a `100x100` world with four ecological zones, day/night, seasons, food spawning, plant lifecycle, and herd-like large animals
- morphology with a fixed body-cost budget across sensors, muscles, armor, and brain
- a continuous trait space for memory, planning, cooperation, parenting, fear, aggression, metabolism, diet, and reproduction
- life stages, lineage tracking, parent-child relationships, and inherited body plans
- nest, storage, family support, group formation, roles, hunting, materials, and tier-1 tool behavior
- multiple research capture modes including dashboards, paper bundles, publication batches, robustness sweeps, world-discovery runs, and immortal-discovery runs
- early metabolism-physics-v2 work with gut transit and heritable digestion traits

## 4. Strongest evidence-supported findings right now

From the repository's main status documents, especially [reports/project_status_full_2026-06-20.md](/C:/artificial-evolution/reports/project_status_full_2026-06-20.md), the strongest current claims are:

### Confirmed findings

- The simulated world can sustain a plant loop of `seed -> plant -> fruit -> consumed` in tuned `100x100` ecology.
- Agents show strong reward-place learning, with return-to-food-location behavior far above random baseline.
- Seeds moved by agents can re-enter the plant cycle and later return as food, which supports a narrow but real proto-farming substrate claim.
- The project has identified major hidden structural blockers rather than just surface-level tuning issues:
  - deaths in the key mortal experiments were often lifespan-driven, not starvation-driven
  - durability can be a hard reproduction gate independent of energy
  - reproduction is heavily blocked by social/safety gates
  - some multi-seed runs were not true independent replications because movement dynamics were not tied to `args.seed`

### Confirmed negative or narrowing results

- Managed-patch claims had to be narrowed after falsification; productive patches exist, but agent-specific ownership or deliberate patch management is not yet established.
- Site-selection claims are not yet supported; seed dropping is dominated by hunger state rather than a clearly separable planning behavior.
- Population sustainability is not solved; the system repeatedly falls below replacement and has not yet demonstrated a stable mortal evolutionary regime.

These negative results are scientifically valuable because they sharpen the actual bottlenecks instead of hiding them.

## 5. Main scientific bottleneck

The biggest gap between the project's current state and a strong `ISEF`-level flagship claim is:

`There is still no clean demonstration of stable endogenous evolution across generations under valid replication.`

The code already contains inheritance machinery, mutation hooks, and rich ecology. But the reports show that the project is still blocked by:

- unstable or non-self-sustaining population dynamics
- over-constrained reproduction funnels
- confounded behavioral interpretations
- insufficiently trustworthy replication in at least some past experiments

## 6. Best current framing for the project

The strongest honest framing today is not:

`We already achieved open-ended evolution.`

It is closer to:

`We built a rich artificial-life substrate, demonstrated early ecological and learning phenomena, and uncovered the structural conditions that still prevent transition into robust endogenous evolution.`

That framing is credible, evidence-based, and still ambitious enough for `ISEF` if the next experiments convert the current blockers into a clean scientific story.

## 7. What would make this project competition-strong

For `ISEF`, the project becomes much stronger if it can deliver one of these two outcomes:

### Path A: positive breakthrough

- stable mortal populations
- true multi-seed replication
- inherited variation that measurably changes lineage persistence
- a clear result such as morphology-vs-trait evolution, or a demonstrated ecological driver of diversification

### Path B: strong negative-results paper

- rigorous evidence that a rich embodied ecology still fails to produce self-sustaining evolution under specific structural constraints
- careful decomposition of which gates break the transition
- a principled redesign showing why the failure occurs

Either path can be competitive if the experimental design and evidence are clean enough.
