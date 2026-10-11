# Supplementary Material

## Article

**When Intermittent Safety Lures the Learner: Sufficiency and Limits of Experience-Based Food Valuation in an Artificial Ecology**

**Author:** Chisanupong Injun  
**Affiliation:** Deebuk Phangnga Wittayayon School, Phang Nga 82000, Thailand  
**Contact:** chisanupong.injun@gmail.com

## Contents

- `source_data/`: compact CSV and JSON tables used for manuscript values.
- `study_1_raw_runs/`: the 20 completed paired JSON runs (`A` value blind; `B` value memory).
- `study_2_frozen/`: the previously frozen self-contained toxin harness, minimum engine source, tests, source tables, hashes, and its reproduction instructions.
- `analysis/prepare_top_two_publication_stats.py`: analysis that produces the compact cross-study source tables from completed runs and toxin harnesses.
- `verify_article_results.py`: independent checks of the principal article values from the packaged data.
- `SHA256SUMS.txt`: package file hashes.

## Quick verification

From this directory:

```powershell
python verify_article_results.py
```

For the frozen toxin mechanism and its tests:

```powershell
Set-Location study_2_frozen
python scripts/regenerate_paper2_source_data.py
python -m unittest tests.test_toxin
```

The article uses the seed/run as the inferential unit. Agents and ticks nested within a seed are not treated as independent replicates.

## Important provenance note

The completed Study-1 JSON runs and publication-facing analysis are included. Before public release, the author must identify and tag the exact historical generator commit for those runs. The current project working tree contains later uncommitted changes to `scripts/food_value_study_driver.py`; that live file is therefore not included here as if it were the frozen generator.

## Claim boundary

The package supports within-lifetime stationary food-value adaptation, an analytic and finite-sample temporal-toxicity lure, and a type-only safe-window discrimination limit. It does not demonstrate mortality cost, survival cost, reproductive cost, selection, evolved deferral, or evolutionary fitness.

