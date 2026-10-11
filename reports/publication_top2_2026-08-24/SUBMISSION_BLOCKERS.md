# Submission Blockers

These are release gates, not optional polish.

## Shared blockers

- [ ] Confirm the exact English author name, affiliation, postal address, and
  corresponding-author email.
- [ ] Decide authorship using actual contributions. Advisor status must be either
  co-author with a CRediT role or acknowledgment, not an automatic title credit.
- [ ] Create/confirm ORCID for every author.
- [ ] Add an OSI-approved repository license or explain why code cannot be public.
- [ ] Commit the exact analysis and experiment scripts used by each paper.
- [ ] Freeze a tagged release and archive code plus source data in a DOI-granting
  repository before final acceptance.
- [ ] Replace local Windows paths in the data-availability statement with public,
  persistent links.
- [ ] Read every cited source used to support a scientific statement. Bibliographic
  correctness alone is not sufficient.
- [ ] Confirm that all figures are English, vector PDF/EPS where possible, and have
  dedicated source-data files.
- [ ] Add the final, author-approved generative-AI disclosure to manuscript and
  cover letter. Record tool name, provider, model/version if available, dates,
  tasks, and human verification.
- [ ] Run the complete test suite from a clean checkout and record commit hash,
  Python version, OS, dependency versions, and command output.

## Paper 1 blockers

- [ ] Treat seeds as paired in the primary analysis. Retain the exact paired
  randomization result and paired effect interval generated in `source_data`.
- [ ] Add a prespecified environment-transfer test (at minimum a second world size
  or food-density regime) so the conclusion is not restricted to one abundant-
  energy configuration.
- [ ] Add a choice-set/exposure denominator. Raw meal counts alone combine choice,
  encounter frequency, and population exposure.
- [ ] Decide whether the single-seed 10/12 versus 0/12 mechanism control is a
  secondary mechanistic result or rerun it across paired seeds.
- [ ] Explain why learning is described as outcome-grounded rather than
  “reward-free.” Realized energy is an internal consequence and functions as a
  learning signal.
- [ ] Expand the related-work review before targeting a 6,000–12,000-word Article.

## Paper 2 blockers

- [ ] Label the four learners as illustrative, not exhaustive or universally
  representative.
- [ ] Verify whether the Letter format may include the required supplementary code
  and source data without exceeding the journal's length expectations.
- [ ] Report the deterministic analytic boundary separately from finite-sample
  learner percentages.
- [ ] Do not state a mortality, survival, selection, or fitness cost. It has not
  been demonstrated in the controlled sated regime.
- [ ] Do not claim that storing or deferring food emerged. Those mechanisms remain
  future work.
- [ ] If upgraded to a full Article, run a preregistered full-ecology experiment
  comparing type-only, type×state, and age-aware controls on survival-relevant
  outcomes.

## Current verdict

- Paper 1: **fix-then-submit**.
- Paper 2 as a Letter: **minor scientific expansion plus release engineering**, but
  still not ready to upload until shared blockers are closed.

