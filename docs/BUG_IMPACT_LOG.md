# Bug Impact Log

## Purpose

This log records bugs that materially changed simulation behavior,
research interpretation, telemetry quality, or conclusions.

Each entry answers:

- what was wrong
- where it lived
- what it distorted
- how it was detected
- what changed after the fix
- what conclusion should be updated

## Entry Format

- `id`: stable bug identifier
- `status`: `fixed`, `open`, or `ruled_out`
- `severity`: practical research impact
- `area`: subsystem affected
- `affected_files`: main code locations
- `distorted_metrics`: outputs likely biased by the bug
- `research_risk`: how the bug could mislead interpretation
- `before_fix_behavior`: observed system behavior before the fix
- `fix_summary`: what was changed
- `after_fix_behavior`: what changed after the fix
- `current_interpretation`: what we believe now

## Active Summary

- The largest historically confirmed simulation bug was household continuity failure across generations.
- The largest confirmed data-quality bug was missing `tick_metrics.csv` for research-only inheritance runs.
- The most recent confirmed economy bug was projected-energy storage ordering during food consumption.
- Not every plausible explanation turned out to be a bug; some were ruled out by telemetry.

## Bugs

### BUG-001 Household Continuity Failure

- `status`: fixed
- `severity`: critical
- `area`: reproduction, nest ownership, intergenerational household access
- `affected_files`: [C:\artificial-evolution\agents\agent.py](C:\artificial-evolution\agents\agent.py)
- `distorted_metrics`:
  - `gen1_reproduction_block_reason`
  - `nest_food_low`
  - `target_generation_reached`
  - extinction rate in sexed-world tests
- `research_risk`:
  - made the world look harder than it really was
  - made `gen1 -> gen2` failure look like a pure ecology problem
  - could falsely suggest that viable body designs did not exist
- `before_fix_behavior`:
  - `gen1` agents often matured correctly but failed reproduction due to `nest_food_low`
  - adult children did not reliably inherit or resolve access to the relevant family household storage
  - the system frequently collapsed before `gen3`
- `detection_evidence`:
  - debug runs around experiments `042-044`
  - repeated `repro_fail` logs showing `nest_food_low` and household access failure patterns
- `fix_summary`:
  - household nest resolution was updated so grown children could resolve family/shared-home nest ownership more correctly
- `after_fix_behavior`:
  - runs that previously died before `gen3` could now reach `gen3`
  - experiment `045` showed `gen3_adult=True` without lowering world difficulty
- `current_interpretation`:
  - pre-fix extinction results in the sexed world should not be treated as a clean measure of ecological impossibility
  - they were partly driven by a household continuity bug

### BUG-002 Research Tick Telemetry Gap

- `status`: fixed
- `severity`: high
- `area`: telemetry, research artifact export
- `affected_files`:
  - [C:\artificial-evolution\simulation\runner.py](C:\artificial-evolution\simulation\runner.py)
  - [C:\artificial-evolution\simulation\research_artifacts.py](C:\artificial-evolution\simulation\research_artifacts.py)
- `distorted_metrics`:
  - `tick_metrics.csv`
  - `tick_checkpoints.md`
  - any per-tick collapse analysis for research-only runs
- `research_risk`:
  - made some inheritance runs look under-instrumented
  - blocked direct per-tick analysis of collapse timing
  - weakened confidence in claims about when the world actually fell into demographic decline
- `before_fix_behavior`:
  - research-only runs wrote `summary.json`, `events.jsonl`, and `generation_traits.csv`
  - but `tick_metrics.csv` could be empty because `tick_summaries` were only recorded when `capture_dashboard=True`
- `detection_evidence`:
  - repaired run inspection showed empty `tick_metrics.csv` and `tick_checkpoints.md`
  - manifests still pointed to those files, making the gap easy to miss
- `fix_summary`:
  - telemetry capture was moved to a shared condition: record per-tick data whenever either `capture_dashboard` or `capture_research_data` is enabled
- `after_fix_behavior`:
  - repaired inheritance runs now contain full `tick_metrics.csv`
  - checkpoint files now show the actual collapse trajectory
- `current_interpretation`:
  - old research bundles with empty tick metrics should be treated as incomplete telemetry artifacts
  - repaired replacement runs should be used for per-tick demographic analysis

### BUG-003 Projected-Energy Storage Ordering

- `status`: fixed
- `severity`: high
- `area`: household food economy, reproduction preconditions
- `affected_files`: [C:\artificial-evolution\agents\agent.py](C:\artificial-evolution\agents\agent.py)
- `distorted_metrics`:
  - nest food storage totals
  - `store_food` event frequency
  - `nest_food_low` reproduction failures
  - long-run founder-population comparisons
- `research_risk`:
  - could make household buffers look weaker than intended
  - could mislead us into thinking low nest storage was purely ecological
  - could hide the real balance between personal energy and household reserves
- `before_fix_behavior`:
  - food processing called `_store_surplus_food(env, restored_energy)` before the caller added `restored_energy` to `self.energy`
  - storage logic checked old energy, not projected post-meal energy
  - agents could fail to store food on the same tick they had just gained enough energy to do so
- `detection_evidence`:
  - direct code inspection in [C:\artificial-evolution\agents\agent.py](C:\artificial-evolution\agents\agent.py)
  - user hypothesis matched the observed call order exactly
- `fix_summary`:
  - `_store_surplus_food()` now evaluates `projected_energy = self.energy + restored_energy`
  - storage threshold and amount are computed against projected post-meal energy
- `after_fix_behavior`:
  - A/B comparison on founder population `250` worsened aggregate outcomes:
  - `mean_max_generation`: `6.6 -> 4.2`
  - `mean_final_tick`: `594.9 -> 525.2`
  - `mean_matured_children`: `108.5 -> 86.6`
  - `gen>=7 runs`: `6/10 -> 1/10`
- `current_interpretation`:
  - the bug was real, but it had been masking another imbalance
  - pre-fix runs were effectively favoring immediate personal energy retention over household storage
  - after the fix, the simulation reveals that personal-vs-household energy allocation is currently too harsh
  - this is now a design problem, not a hidden bug

## Ruled-Out Hypotheses

### HYP-001 Missing Sex Assignment In Gen1

- `status`: ruled_out
- `severity`: medium
- `area`: reproduction inheritance
- `affected_files`: [C:\artificial-evolution\agents\agent.py](C:\artificial-evolution\agents\agent.py)
- `research_risk`:
  - could have invalidated all `gen1 -> gen2` conclusions if true
- `reason_ruled_out`:
  - `spawn_child()` assigns sex explicitly
  - telemetry showed `gen1` males and females existed
  - failure came from reproduction gates, not missing sex assignment

### HYP-002 Missing Generation/Parent Transmission

- `status`: ruled_out
- `severity`: medium
- `area`: lineage inheritance
- `affected_files`: [C:\artificial-evolution\agents\agent.py](C:\artificial-evolution\agents\agent.py)
- `research_risk`:
  - could have made all higher-generation analysis invalid if true
- `reason_ruled_out`:
  - `generation=self.generation + 1`, `parent_id`, and `other_parent_id` were present
  - lineage tracking and adult-generation counts confirmed inheritance metadata existed

## Use Guidance

- When citing old results, always check whether the run happened before or after the relevant bug fix.
- When comparing historical runs, annotate whether they are:
  - pre-household-fix
  - pre-telemetry-fix
  - pre-storage-order-fix
- A surprising result after a bug fix does not mean the fix was wrong; it can reveal a deeper model imbalance.
