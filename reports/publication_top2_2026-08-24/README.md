# Top-Two International Publication Package

Prepared: 24 August 2026  
Default target: *Artificial Life* (MIT Press)  
Status: working publication package; not yet authorized for submission

## Selected papers

1. **Experience-Based Food Valuation in an Unlabeled Artificial Ecology**
   - Proposed type: full Article.
   - Core contribution: controlled evidence that a type-level memory of realized
     digestible energy changes diet without semantic food labels or an externally
     supplied task score.
   - Primary data: ten paired seeds, 3,000 ticks per arm.

2. **When Intermittent Safety Lures the Learner: Temporal Toxicity Under Perceptual Aliasing**
   - Proposed type: Letter first; expand to Article only after a full-ecology
     survival experiment.
   - Core contribution: a hidden-state mixture can invert learned avoidance into
     pursuit, with an analytic boundary and replication across four illustrative
     learning rules.
   - Primary data: 30 seeds × 100 agents × 40 trials in controlled mechanism tests.

## Package map

- `paper_01_food_value/manuscript_en.md`: English IMRaD manuscript draft.
- `paper_01_food_value/evidence_and_statistics.md`: claim-to-artifact audit.
- `paper_01_food_value/cover_letter_draft.md`: target-journal cover letter.
- `paper_02_toxin_lure/manuscript_en.md`: concise English Letter draft.
- `paper_02_toxin_lure/evidence_and_statistics.md`: analytic and empirical audit.
- `paper_02_toxin_lure/cover_letter_draft.md`: target-journal cover letter.
- `overlap_and_submission_strategy.md`: boundary preventing redundant publication.
- `SUBMISSION_BLOCKERS.md`: work that must be closed before submission.
- `source_data/`: compact, regenerated publication-facing CSV/JSON snapshots.

Regenerate the source-data snapshots with:

```powershell
python scripts\prepare_top_two_publication_stats.py
```

## Current recommendation

Do not submit both manuscripts on the same day. First complete and submit Paper 1,
or post a citable preprint after advisor approval. Paper 2 should then cite Paper 1
as the mechanism baseline and use no Paper-1 result as a second primary result.

The package deliberately distinguishes a polished draft from a submission-ready
article. Authorship, author-approved AI disclosure, reference reading, repository
licensing, code/data archival, and the open statistical issues in
`SUBMISSION_BLOCKERS.md` must be resolved first.

