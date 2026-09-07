# Paper 1 Evidence and Statistics Audit

## Primary hypothesis

Under a matched abundant-energy regime, enabling memory of realized food energy
reduces consumption of the lower-value food relative to the same simulation with
that memory disabled.

## Design

- Independent variable: food-value memory off/on.
- Statistical unit: seed/run, not agent and not tick.
- Pairing: identical seed and configuration across arms.
- Replicates: 10 paired seeds (`20260610`–`20260619`).
- Horizon: 3,000 ticks.
- Primary outcome: total `raw_seed` meals per run.
- Secondary outcomes: 1,000-tick meal windows; per-agent taste-before-skip trace;
  memory-disabled mechanism control.

## Frozen primary result

Generated from the completed paired JSON runs by
`scripts/prepare_top_two_publication_stats.py`:

- No-learning arm: mean 1,945.3 meals/run.
- Value-learning arm: mean 423.0 meals/run.
- Mean paired reduction: 1,522.3 meals, 95% t interval half-width 181.6.
- Every one of 10 paired seeds favors the learning arm.
- Exact two-sided paired sign-flip/randomization p = 0.001953125.
- Mean within-pair ratio = 4.70×; ratio is descriptive, not the primary effect.

The older Mann–Whitney result remains a useful robustness check but is not the
primary test because the experiment was explicitly paired.

## Mechanism evidence

The matched single-seed mechanism control reported:

- memory on: 10/12 agents began skipping `raw_seed`;
- memory off: 0/12 agents began skipping;
- plant meals were equal in the reported matched comparison;
- 0/12 agents skipped the lower-value food without first experiencing the
  higher-value comparator.

This supports the mechanism but must not be treated as 12 independent simulation
replicates. The run/seed remains the inferential unit.

## Evidence supporting

- All paired runs move in the predicted direction.
- The effect is large relative to between-seed variation.
- Disabling the memory removes skipping in the matched mechanism control.
- Agent-level event order supports direct experience before behavior change.

## Evidence against or limiting

- The experiment uses an abundant-energy/sated configuration that isolates diet
  learning from the project's spatial-foraging bottleneck.
- Raw meals are affected by encounters and exposure; a choice-set denominator is
  not yet frozen for the primary batch.
- Only one environment configuration is in the confirmatory set.
- The learning rule and threshold are researcher-designed. The behavioral
  adaptation is learned; the capacity to learn is not itself emergent.
- The study does not demonstrate semantic understanding, social learning,
  population fitness benefit, or evolution.

## Alternative explanations to address

1. Different encounter rates despite paired seeds.
2. A generic persistence change rather than food-value comparison.
3. An abundant-energy artifact that does not transfer to realistic competition.
4. Dependence on the selected pickiness and learning-rate parameters.

## Required additions

- A second environment regime with a frozen protocol.
- Choice opportunities/exposure-normalized consumption.
- Sensitivity analysis for learning rate and pickiness.
- A full public provenance bundle linking code commit, configuration, seed, raw
  runs, analysis, figures, and manuscript table cells.

## Confidence

High for the narrow causal claim in the tested regime; moderate for transfer to a
broader artificial ecology.

