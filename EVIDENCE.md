# Evidence index

This file exists so that every claim made about this project — in a CV, an
abstract, or a competition submission — can be checked by a reader who has no
access to the author and no reason to take anything on trust.

Each row names the claim, the artifact that supports it, and the command that
reproduces it. If a claim has no artifact, it says so.

Repository: https://github.com/sstangkh73/artificial-evolution
Author ORCID: https://orcid.org/0009-0000-2979-1916
Licence: code MIT (`LICENSE`), data and reports CC BY 4.0 (`LICENSE-DATA.md`)

## Scale of the codebase

| Claim | How to check |
| --- | --- |
| 68 Python modules | `git ls-files '*.py' \| wc -l` |
| ~33,000 lines of Python | `git ls-files '*.py' \| xargs cat \| wc -l` |
| 10 automated test files, 93 cases, all passing | `python -m unittest discover -s tests -v` — reports `Ran 93 tests ... OK` |

Counts are file counts in this repository at the current commit. They are not
estimates, and they will change as the project grows; the commands above always
return the current truth rather than a number frozen in a document.

## Simulation features

| Claim | Where it lives |
| --- | --- |
| 100x100 grid world | `world/` |
| Four ecological zones with different risk and food density | `world/`, described in `docs/WORLD_RULES.md` |
| Day/night and seasonal cycles affecting vision and food spawning | `world/`, `docs/WORLD_PHYSICS_V2.md` |
| Metabolism, ageing, toxins | `simulation/`, `docs/BODY_SYSTEM.md`, `tests/test_metabolism.py`, `tests/test_aging_physics.py`, `tests/test_toxin.py` |
| Material gathering and object assembly | `simulation/`, `docs/TECH_TREE.md` |
| Deterministic runs under a locked seed | `tests/test_seed_independence.py` |

## Experimental results

Full detail, raw per-seed numbers, and the statistical audits are in
[`reports/evidence/`](reports/evidence/README.md), which also carries the
limitations of each result.

| Claim | Artifact |
| --- | --- |
| Low-value food consumption cut ~4.6x by experience-based valuation, 10 paired seeds | `reports/evidence/source_data/paper_01_food_value_paired_seeds.csv` |
| Paired significance: exact two-sided sign-flip p = 0.00195 | `reports/evidence/source_data/results_snapshot.json` |
| Complete separation between arms (Cliff's delta = 1.00, Mann-Whitney U = 0) | `reports/food_value_learning_full_report_2026-06-18.th.md`, table 4 |
| Under perceptual aliasing, 63.3% +/- 1.3 of agents lured at 30% toxic encounters (cautious rule) | `reports/evidence/source_data/paper_02_toxin_learner_comparison.csv` |
| Effect reproduces across all four learning rules (62.1% to 99.2%) | same file |
| The lure is a broad parameter region, not a tuned point | `reports/evidence/figure_toxin_lure_sweep.png` |
| No agent avoided low-value food without first tasting a better option (0 of 12) | `reports/agent_food_value_individual_tracking_2026-06-23.th.md` |

### One correction, stated openly

Earlier write-ups of this project reported **p = 0.0002** for the food-valuation
result. That figure came from a Mann-Whitney U test treating the two arms as
**independent** samples. Because both arms share the same 10 seeds, the correct
analysis is **paired**, and the exact two-sided sign-flip test gives
**p = 0.00195** — which is the floor for 10 paired seeds.

The conclusion is unchanged and the effect size is if anything easier to defend
(every seed favours the learning arm; the arms do not overlap). Only the test
and its p-value change. Documents written before 2026-08-24 carry the older
number; `reports/evidence/` carries the corrected one.

## Research process

| Claim | Artifact |
| --- | --- |
| Conclusions red-teamed before release | `reports/red_team_pre_submission_2026-07-01.th.md`, `reports/red_team_2_pre_submission_2026-07-01.th.md` |
| Every red-team objection tracked to a resolution | `reports/red_team_resolution_2026-07-14.th.md` |
| Claim-to-artifact audit for each manuscript conclusion | `reports/evidence/paper_01_food_value_evidence_and_statistics.md`, `reports/evidence/paper_02_toxin_lure_evidence_and_statistics.md` |
| Structured reading programme of 34 foundational papers | `papers/READING_LIST.md` — the list and the author's ordering rationale. The paper PDFs themselves are third-party copyrighted works and are deliberately not redistributed here. |
| Release gates recorded before, not after, submission | `reports/publication_top2_2026-08-24/SUBMISSION_BLOCKERS.md` (local; available on request) |

## What is deliberately not published here

- **Manuscript drafts under journal consideration.** "When Intermittent Safety
  Lures the Learner" was submitted to *Artificial Life* (MIT Press) on
  24 August 2026, manuscript ID ARTL-2026-0228. The submission receipt exists and
  is available on request. The data and audits behind the manuscript are public
  in `reports/evidence/`; the manuscript text is not, while it is under review.
- **Third-party paper PDFs** under `papers/`, for copyright reasons. The reading
  list is published instead.
- **Large generated run artifacts** — dashboards, research runs, and publication
  packages — which are excluded by `.gitignore` because of size. The compact
  source data that every published number depends on is in
  `reports/evidence/source_data/`.
