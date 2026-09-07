# Evidence bundle

Every quantitative result claimed in the author's CV, abstracts, and competition
submissions is backed by a file in this folder. Nothing here requires the reader
to trust a summary: the raw per-seed numbers, the statistical audit, and the
figures are all present.

Licence: code MIT (`/LICENSE`), data and reports CC BY 4.0 (`/LICENSE-DATA.md`).

## Contents

| File | What it is |
| --- | --- |
| `source_data/paper_01_food_value_paired_seeds.csv` | Per-seed meal counts for the no-learning and value-learning arms, with the paired difference and ratio for each of the 10 seeds. |
| `source_data/paper_02_toxin_learner_comparison.csv` | Percentage of agents lured, by learning rule and toxic fraction, with 95% CI half-widths. |
| `source_data/paper_02_toxin_lure_curve.csv` | Lure percentage, toxic-meal percentage, and mean energy per meal across the toxic-fraction sweep. |
| `source_data/results_snapshot.json` | Machine-readable snapshot of every headline statistic, including the test used and its p-value. |
| `paper_01_food_value_evidence_and_statistics.md` | Claim-to-artifact audit for the food-valuation result: each stated conclusion mapped to the data that supports it, plus the evidence against it. |
| `paper_02_toxin_lure_evidence_and_statistics.md` | Same audit for the temporal-toxicity result, including the analytic boundary and the stated limitations. |
| `figure_temporal_toxicity.png` | Temporal toxicity figure. |
| `figure_toxin_lure_sweep.png` | Parameter sweep showing the lure is a broad region, not a single tuned point. |

## The two headline claims, and exactly how to check them

### 1. Agents learn food value from consequences, with no labels

**Claim.** Turning on experience-based valuation cuts consumption of low-value
food by about 4.6x relative to an identical non-learning control.

**Check it.**

```bash
python - <<'PY'
import csv, statistics
rows = list(csv.DictReader(open('reports/evidence/source_data/paper_01_food_value_paired_seeds.csv')))
nl = sum(int(r['no_learning_meals'])    for r in rows)
vl = sum(int(r['value_learning_meals']) for r in rows)
ratios = [float(r['paired_ratio']) for r in rows]
print('seeds        :', len(rows))
print('pooled ratio : %.2f' % (nl / vl))
print('paired mean  : %.2f' % statistics.mean(ratios))
print('paired median: %.2f' % statistics.median(ratios))
print('all seeds favour learning:', all(r > 1 for r in ratios))
PY
```

Expected: 10 seeds, pooled ratio 4.60, paired mean 4.70, median 4.86, and every
seed favouring the learning arm.

**Statistical note, stated plainly.** Two tests appear in this project's history
and they are not interchangeable:

- The 2026-06-18 report used a **Mann-Whitney U test treating the two arms as
  independent** samples: U = 0, p = 0.0002, Cliff's delta = 1.00.
- The publication package **re-analysed the same runs as paired by seed**, which
  is the correct design because both arms share each seed. The exact two-sided
  sign-flip test on 10 paired seeds gives **p = 0.00195**. This is the smallest
  p-value that 10 paired seeds can produce (2 / 2^10), so no paired test on this
  sample can report a smaller value.

The paired figure is the one to cite. Both are in `results_snapshot.json`.

### 2. Under perceptual aliasing, learned avoidance inverts into pursuit

**Claim.** When toxicity depends on a state the agent cannot observe, a learner
that stores one value per food type ranks a poisonous food above a safe staple.
At a 30% toxic-encounter rate this happens for 63.3% +/- 1.3 of agents under the
cautious simulation-gate rule, and the effect appears under all four rules tested.

**Check it.**

```bash
python - <<'PY'
import csv
rows = [r for r in csv.DictReader(open('reports/evidence/source_data/paper_02_toxin_learner_comparison.csv'))
        if abs(float(r['toxic_fraction']) - 0.3) < 1e-9]
for r in rows:
    print('%-24s %5.1f%% +/- %.1f' % (r['learner'],
                                      float(r['lured_percent_mean']),
                                      float(r['lured_percent_ci95_half_width'])))
PY
```

Expected at 30% toxic encounters: simulation gate 63.3% +/- 1.3, greedy sample
average 62.1% +/- 1.7, epsilon-greedy 92.7% +/- 0.8, softmax 99.2% +/- 0.3.

**Read this before quoting the number.** 63.3% is the figure for the *cautious*
rule. The other three rules are lured more often, not less; a rule that explores
more is lured harder. Quoting 63% as "the" result understates the effect for
three of the four rules, and quoting 99% alone would overstate the cautious case.
Design: 30 seeds, 100 agents per seed, 40 encounters per agent.

## Limitations, kept in the same folder as the results

Both audit files carry an explicit "evidence against or limiting" section. The
main constraints are that the four learners are illustrative rather than an
exhaustive class, that the harness isolates the valuation mechanism rather than
modelling a full spatial ecology, that agent trials within a seed are not
independent inferential replicates, and that the sated regime does not
demonstrate mortality or reproductive cost. These are not hidden in an appendix
because a result whose limits are unstated is not checkable.

## Manuscript status

The manuscript "When Intermittent Safety Lures the Learner: Temporal Toxicity
Under Perceptual Aliasing" was submitted to *Artificial Life* (MIT Press) on
24 August 2026, manuscript ID ARTL-2026-0228. The submission receipt is held by
the author and is available on request. Manuscript drafts are not published here
while they are under consideration; the data and audits behind them are.
