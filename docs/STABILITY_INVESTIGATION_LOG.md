# Stability Investigation Log

## Purpose

This log tracks the ongoing investigation into the main unsolved problem:

- why the population can sometimes reach deep generations
- but still fails to become self-sustaining
- without lowering world difficulty

This file is different from [C:\artificial-evolution\docs\BUG_IMPACT_LOG.md](C:\artificial-evolution\docs\BUG_IMPACT_LOG.md):

- `BUG_IMPACT_LOG.md` records confirmed bugs and their research impact
- this file records broader stability investigation steps, including failed interventions and open hypotheses

## Current Goal

- Baseline founder population for current investigation: `250`
- Current working body: `body_14`
- Main objective:
  - make the system sustain itself through internal dynamics
  - do not reduce world difficulty

## What We Have Done

### 1. Founder Population Search

- Tested founder populations from `2` to `300`
- Current best starting region is around `250`
- Key source:
  - [C:\artificial-evolution\data\founder_population_optimal_search.json](C:\artificial-evolution\data\founder_population_optimal_search.json)
  - [C:\artificial-evolution\reports\founder_population_stage_2026-05-11\founder_population_stage_summary_2026-05-11.pdf](C:\artificial-evolution\reports\founder_population_stage_2026-05-11\founder_population_stage_summary_2026-05-11.pdf)

### 2. Direct Projected-Energy Storage Fix

- Confirmed the food-storage ordering bug
- Fixed storage logic to use projected post-meal energy
- Result:
  - performance became worse
- Key comparison:
  - [C:\artificial-evolution\data\founder_opt_250_storage_fix_comparison.json](C:\artificial-evolution\data\founder_opt_250_storage_fix_comparison.json)

Interpretation:

- the bug was real
- but pre-fix behavior had been masking a deeper imbalance between personal energy retention and household storage

### 3. Household Economy Redesign

- Added a personal energy floor before storing surplus food
- Stored only a fraction of surplus instead of immediately draining energy
- Result:
  - much better than direct storage fix
  - close to baseline performance
  - best run reached `gen9`
- Key comparison:
  - [C:\artificial-evolution\data\founder_opt_250_storage_redesign_comparison.json](C:\artificial-evolution\data\founder_opt_250_storage_redesign_comparison.json)

Interpretation:

- this is currently the best intervention we have tested in recent rounds
- it improves internal balance without making the world easier

### 4. Settlement Overshoot Intervention

- Tried aggressive nest reuse / build spacing logic
- Result:
  - catastrophic collapse
  - mean max generation dropped to `1.0`
- Key comparison:
  - [C:\artificial-evolution\data\founder_opt_250_settlement_overshoot_fix_comparison.json](C:\artificial-evolution\data\founder_opt_250_settlement_overshoot_fix_comparison.json)

Interpretation:

- directly suppressing new nest formation is not the right fix
- it destroys household formation instead of improving stability
- this intervention was rolled back

### 5. Anti-Cohort Reproduction Cooldown

- Tried founder readiness staggering plus reproduction cooldown
- Result:
  - births collapsed too hard
  - mean max generation dropped to `2.5`
- Key comparison:
  - [C:\artificial-evolution\data\founder_opt_250_anti_cohort_comparison.json](C:\artificial-evolution\data\founder_opt_250_anti_cohort_comparison.json)

Interpretation:

- cohort collapse is probably part of the story
- but hard cooldown is not the right tool
- this intervention was rolled back

### 6. Adult Household Withdrawal Alignment

- Changed adult emergency nest withdrawal to use `_nest_owner_id()` instead of `self.agent_id`
- Result:
  - mixed
  - some seeds improved strongly
  - aggregate depth still remained below baseline and below household-redesign-only performance
- Key comparison:
  - [C:\artificial-evolution\data\founder_opt_250_adult_withdrawal_fix_comparison.json](C:\artificial-evolution\data\founder_opt_250_adult_withdrawal_fix_comparison.json)

Interpretation:

- this clue is probably real
- household-aware withdrawal can improve some lineages dramatically
- but by itself it is not yet the full solution
- this should remain an active line of investigation, not a closed case

### 7. Breeder-Priority Household Allocation

- Changed household withdrawal so that:
  - children still retain emergency access
  - breeder-priority adult females can withdraw toward reproduction readiness
  - general adults cannot drain nest buffers as aggressively
- Result:
  - strongest aggregate result so far in the current investigation stage
- Key comparison:
  - [C:\artificial-evolution\data\founder_opt_250_breeder_priority_comparison.json](C:\artificial-evolution\data\founder_opt_250_breeder_priority_comparison.json)

Observed gains versus household-redesign-only baseline:

- `mean_max_generation`: `5.8 -> 7.5`
- `mean_final_tick`: `589.7 -> 649.6`
- `mean_matured_children`: `106.4 -> 145.0`
- `gen>=7 runs`: `4/10 -> 7/10`
- non-extinct runs: `5/10 -> 8/10`

Interpretation:

- this is the best current fix direction
- it supports the hypothesis that household access was not just about total food, but about who gets to draw from household food first
- breeder throughput looks more important than universal adult access

## Best Current Interpretation

At the moment, the system still fails to become self-sustaining because:

1. `replacement rate` after `gen1` is still too low
2. personal energy is still the dominant bottleneck
3. household storage exists, and access/allocation order is a major control point
4. the world can accumulate resources without converting them into enough adult breeders

This means the system is not suffering from pure ecological scarcity.
It is suffering from a conversion problem:

- food exists
- storage exists
- lineages can continue
- but not enough of that surplus becomes stable reproductive continuity

## New High-Priority Suspicions

### SUS-001 Adult Nest Withdrawal Uses The Wrong Owner

Code path:

- [C:\artificial-evolution\agents\agent.py:1517](C:\artificial-evolution\agents\agent.py:1517)

Observed logic:

- children withdraw from `parent_id`
- adults withdraw from `self.agent_id`
- adults do **not** use `_nest_owner_id()` here

Why this matters:

- adults may reproduce against one household nest
- store into one household nest
- but withdraw emergency food from another owner id or from no valid nest at all

Why this is high priority:

- it directly matches the observed paradox:
  - huge stored food totals
  - many `energy_depleted` deaths
  - many `low_energy` reproduction failures

Current status:

- investigated and refined
- simple household-aware adult withdrawal was mixed
- breeder-priority withdrawal produced the best aggregate result so far
- this suspicion should now be treated as a partially confirmed mechanism

### SUS-002 Nests Create Food Out Of Thin Air

Code path:

- [C:\artificial-evolution\world\environment.py:301](C:\artificial-evolution\world\environment.py:301)

Observed logic:

- every new nest is initialized with `food_storage=18`

Why this matters:

- nest construction injects food directly into the world economy
- in best redesign run:
  - final settlements: `306`
  - seeded food from nest creation alone: `306 * 18 = 5508`
  - stored food total: `11851`
- that means about `46.5%` of stored food can be explained by nest seeding alone

Why this is high priority:

- it may distort both ecology and demography
- it may reward overbuilding even when population stability is poor

Current status:

- not fixed yet
- should be tested carefully because removing it may sharply change baseline behavior

### SUS-003 Nest Support Scales With Nest Count

Code path:

- [C:\artificial-evolution\world\environment.py:878](C:\artificial-evolution\world\environment.py:878)

Observed logic:

- every nest gets independent support chances
- more nests means more support-food injections and more local plant spawns

Why this matters:

- the system can create hundreds of nests
- this can inflate household resource surplus even while population shrinks
- it may explain why stored food grows while reproduction still fails

Why this is high priority:

- it creates a disconnect between ecological surplus and demographic success

Current status:

- not fixed yet
- needs direct A/B analysis after checking adult withdrawal logic

## What Is Ruled Out As The Immediate Best Fix

- hard reproduction cooldown
- aggressive nest reuse / nest-spacing suppression
- simply increasing founder count and stopping there
- adult-withdrawal alignment as a standalone silver bullet
- active-nest-only support filtering as a working-state replacement
- direct nest-owner inheritance transfer as a working-state replacement
- juvenile and newly adult withdrawal priority as a working-state replacement

## Latest Loop Outcomes

### LOOP-008 Active-Nest-Only Support Filtering

Goal:

- stop abandoned nests from accumulating support forever

What was changed:

- nest support was limited to nests considered active through occupancy tracking

What happened:

- `long_loop_iteration_02_active_nest_support` still had `0/10` stable runs
- long-depth seeds got worse, not better
- example:
  - seed `11`: `tick 2506 -> 2497`
  - seed `13`: `tick 2478 -> 1153`
- stored food inflation dropped, but extinction still happened

Interpretation:

- abandoned-nest support inflation is real
- but that inflation was also masking a deeper survival dependency
- removing it directly does not create a self-sustaining world

Artifact:

- [C:\artificial-evolution\data\long_loop_iteration_02_active_nest_support.json](C:\artificial-evolution\data\long_loop_iteration_02_active_nest_support.json)

Status:

- rolled back from working state

### LOOP-009 Household-Linked Active Nest Probe

Goal:

- tighten active support so only true household-linked occupants keep a nest active

What was changed:

- active nests were restricted to nests linked through each agent's household owner resolution

What happened:

- probe seeds collapsed extremely early
- examples:
  - seed `11`: `tick 189`, `gen2`
  - seed `13`: `tick 177`, `gen2`
  - seed `15`: `tick 159`, `gen2`

Interpretation:

- broad environmental support is currently part of the world's basic survival scaffold
- removing it this aggressively destroys even medium-depth lineage continuity

Artifacts:

- [C:\artificial-evolution\data\research_runs\long_loop_iter03_probe_seed_11\manifest.json](C:\artificial-evolution\data\research_runs\long_loop_iter03_probe_seed_11\manifest.json)
- [C:\artificial-evolution\data\research_runs\long_loop_iter03_probe_seed_13\manifest.json](C:\artificial-evolution\data\research_runs\long_loop_iter03_probe_seed_13\manifest.json)
- [C:\artificial-evolution\data\research_runs\long_loop_iter03_probe_seed_15\manifest.json](C:\artificial-evolution\data\research_runs\long_loop_iter03_probe_seed_15\manifest.json)

Status:

- ruled out as a candidate working state

### LOOP-010 Nest Inheritance Transfer

Goal:

- keep household capital alive when a nest owner dies

What was changed:

- abandoned nests were transferred to a candidate heir

What happened:

- probe seeds again collapsed near `gen2`
- examples:
  - seed `11`: `tick 194`, `gen2`
  - seed `13`: `tick 201`, `gen2`
  - seed `15`: `tick 291`, `gen2`

Interpretation:

- simple ownership transfer destabilized the household graph too much
- the problem is not solved by naive nest reassignment

Artifacts:

- [C:\artificial-evolution\data\research_runs\long_loop_iter04_inheritance_probe_seed_11\manifest.json](C:\artificial-evolution\data\research_runs\long_loop_iter04_inheritance_probe_seed_11\manifest.json)
- [C:\artificial-evolution\data\research_runs\long_loop_iter04_inheritance_probe_seed_13\manifest.json](C:\artificial-evolution\data\research_runs\long_loop_iter04_inheritance_probe_seed_13\manifest.json)
- [C:\artificial-evolution\data\research_runs\long_loop_iter04_inheritance_probe_seed_15\manifest.json](C:\artificial-evolution\data\research_runs\long_loop_iter04_inheritance_probe_seed_15\manifest.json)

Status:

- rolled back from working state

### LOOP-011 Juvenile And Young-Adult Pipeline Priority

Goal:

- test whether the hidden bottleneck is not current breeders but the pipeline that produces the next breeders

What was changed:

- juveniles and newly adult agents received household food priority in addition to current breeder-priority logic

What happened:

- some deep seeds improved relative to the failed inheritance/support probes
- but they still underperformed the best current long-loop baseline
- examples:
  - seed `11`: `tick 1455`, `gen13`
  - seed `13`: `tick 442`, `gen3`
  - seed `15`: `tick 1145`, `gen11`

Interpretation:

- pipeline fragility is probably real
- but this version did not outperform the current best breeder-priority state

Artifacts:

- [C:\artificial-evolution\data\research_runs\long_loop_iter05_pipeline_probe_seed_11\manifest.json](C:\artificial-evolution\data\research_runs\long_loop_iter05_pipeline_probe_seed_11\manifest.json)
- [C:\artificial-evolution\data\research_runs\long_loop_iter05_pipeline_probe_seed_13\manifest.json](C:\artificial-evolution\data\research_runs\long_loop_iter05_pipeline_probe_seed_13\manifest.json)
- [C:\artificial-evolution\data\research_runs\long_loop_iter05_pipeline_probe_seed_15\manifest.json](C:\artificial-evolution\data\research_runs\long_loop_iter05_pipeline_probe_seed_15\manifest.json)

Status:

- rolled back from working state

## What Remains To Do

### Immediate Next Tests

1. Quantify how much of total stored food comes from:
   - real food collection
   - nest seeding
   - nest support inflation
2. Run parameter search around breeder-priority household constants instead of structural rewrites
3. Measure whether late-run collapse is driven more by breeder starvation, juvenile pipeline thinning, or mate fragmentation

### Questions Still Open

- Are breeders starving while food is trapped in the wrong household owner id?
- Is the system stable only because nest-created food and nest-support food are masking deeper demographic weakness?
- Is the real bottleneck adult female throughput, household access, or both together?

## Current Best Working State

- Keep the `household economy redesign`
- Keep the `breeder-priority household allocation`
- Keep world difficulty unchanged
- Do **not** keep the aggressive settlement or hard cooldown patches
- Household food access matters strongly; breeder-priority allocation is now the best current mechanism
- Investigate targeted allocation tuning next, not universal suppression or world generosity
