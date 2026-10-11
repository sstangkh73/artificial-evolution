# Submission Readiness — Expanded Article

## What this revision changes

- Reclassifies the work from a sub-2,000-word Letter to an Article.
- Merges the completed stationary food-value experiment with the temporal-toxicity experiment under one causal arc:
  `stationary value learning succeeds -> hidden temporal state removes discrimination -> intermittent safety creates the lure`.
- Expands the scientific text to 6,245 words before references, with a 245-word abstract.
- Adds a stand-alone cover letter that explains the model, both studies, principal results, journal fit, prior manuscript ID, and claim boundaries.
- Engages 15 sources, including nine articles or editorials from *Artificial Life*.
- Adds a paired-run figure, a temporal-toxicity figure, two detailed result tables, four hypotheses, explicit controls, alternative explanations, and a prospective experiment program.
- Corrects the learned-flavor reference authorship to Touzani, Bodnar, and Sclafani (2010).

## Evidence verified in this revision

- Study 1: 10 paired seed/runs, 3,000 ticks each.
- Value blind: mean 1,945.3 low-value meals/run (SD 248.2).
- Value memory: mean 423.0 (SD 65.1).
- Mean paired reduction: 1,522.3; 95% t interval 1,340.7–1,703.9.
- Exact two-sided paired sign-flip p = 0.001953125; all 10 pairs favor memory.
- Treatment event trace: 500 agents tasted the low-value food; 491 also tasted the higher-value comparator; all 491 subsequently skipped the low-value food; zero skipped before comparator experience.
- Matched value-blind runs: zero agents skipped and zero skip events.
- Study 2: analytic lure boundary p < 0.625 for values 2, 10, and 5.
- Study 2 finite design: 30 seed/runs, 100 agents/seed, 40 opportunities/agent.
- At 30% toxicity: simulation gate 63.3% ± 1.3 points lured; epsilon-greedy 92.7% ± 0.8; softmax 99.2% ± 0.3; greedy sample average 62.1% ± 1.7.
- Safe-window discrimination: 0.0 points by representation and finite implementation.
- Targeted automated checks: 23/23 tests passed on September 1, 2026.
- Final rendered article: 26 letter-size pages; final cover letter: 2 letter-size pages.
- Visual QA covered every rendered page; the result tables, figures, references, and cover-letter signature block render without clipping or overlap.
- Supplement verification script and all packaged SHA-256 checks passed; the final ZIP contains 45 files and excludes Python cache artifacts.

## Release gates before uploading to ScholarOne

1. The human author must read every cited source and verify that each statement is supported; metadata verification alone is insufficient.
2. Freeze the exact code and analysis in a tagged release and deposit it in a DOI-granting public repository; replace the manuscript placeholder with the persistent URL.
3. Resolve exact generator provenance for the completed Study-1 raw runs. The current working tree contains uncommitted changes to `scripts/food_value_study_driver.py`, so it must not be represented as the exact historical generator until verified.
4. Add an OSI-approved repository license and record Python, operating-system, and dependency versions from a clean checkout.
5. Confirm that the English author name, school spelling, postal address, email, ORCID, acknowledgments, and CRediT statement are final.
6. Review and approve the generative-AI disclosure so it matches the actual tools, version information available to the author, access dates, and human verification performed.

## Scientific risk that remains

The Article is substantially deeper than the rejected Letter, but added prose does not replace missing experiments. Study 1 still uses one abundant-energy environment and a meal-count outcome without an eligible-choice denominator. Study 2 is a controlled sated harness and does not establish mortality, survival, reproduction, selection, or evolutionary fitness. The strongest submission would add a preregistered full-ecology comparison of type-only, type-by-age, and age-aware/deferral policies, plus exposure-normalized choice logging in at least two frozen ecological regimes.

The current manuscript states these limitations and does not claim the missing results. It is a defensible detailed Article draft, not yet a fully released submission package.
