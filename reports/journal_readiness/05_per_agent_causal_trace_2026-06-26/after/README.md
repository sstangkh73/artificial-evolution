# After Fix Report: Per-Agent Causal Trace

Date: 2026-06-26

## Objective

Complete journal-readiness item 5 by exporting a per-agent causal trace that connects individual experience, memory, food choice, social contact, and events across publication runs.

## What Changed

`simulation/runner.py` now carries enriched `agent_outcome_rows` into `write_publication_artifacts()`.

`simulation/research_artifacts.py` and `simulation/runner.py` now include these research agent fields when present:

- `skipped_food_by_type_json`
- `food_value_memory_json`

`simulation/publication_artifacts.py` now writes:

- `agent_causal_trace.csv`
- manifest key: `agent_causal_trace_csv`
- figure source:
  - `figure_11_agent_causal_trace.csv`

## Before

Publication batches loaded per-run `agent_outcomes.csv`, but used those rows only for aggregate proxies such as:

- mean memory sites,
- social contact rate,
- object experimentation rate.

The final publication package did not export one cross-run table where reviewers could inspect same-agent evidence.

## After

The generated `agent_causal_trace.csv` includes per-agent fields such as:

- condition, replicate, seed, agent id,
- generation and alive status,
- immortal flag,
- friend count and social-contact flag,
- memory-site totals,
- raw seed meals,
- raw plant meals,
- raw seed skips,
- learned raw seed and raw plant values,
- food-consumed and food-skipped event counts,
- seed-picked and seed-dropped event counts,
- first raw seed tick,
- first raw plant tick,
- first raw seed skip tick,
- `seed_skip_without_recorded_taste`,
- `experienced_seed_and_plant_before_seed_skip`,
- `learning_evidence_class`.

The trace uses event logs plus agent counters, and avoids inflating evidence by taking the maximum between event counts and agent counters for overlapping food-type counts.

## Evidence Added

New tests verify that:

- a same-agent sequence of raw seed taste, raw plant taste, and later raw seed skip becomes `direct_experience_before_skip`,
- an event-only agent who skips raw seed without recorded taste becomes `skip_without_recorded_seed_taste`,
- the exported trace preserves these flags in `agent_causal_trace.csv`.

## Validation

Commands run:

```text
python -m unittest tests.test_publication_journal_readiness_artifacts
python -m unittest discover -s tests
python -m compileall main.py simulation tests
```

Result:

```text
Ran 32 tests
OK
```

## Remaining Risk

This artifact makes causal inspection possible, but it does not guarantee that all old runs contain skip/value-memory fields. Old per-run manifests created before this change may have only meal counters and memory counts. New runs will carry the richer fields.

## Journal Verdict

This item is fixed at the evidence-packaging level. Learning claims can now be tied to same-agent traces instead of only aggregate condition means.
