# After Fix Report: Literature and Novelty Framing

Date: 2026-06-26

## Objective

Complete journal-readiness item 10 by adding novelty framing and claim-to-evidence mapping to every publication package.

## What Changed

`simulation/publication_artifacts.py` now writes:

- `novelty_framing.md`
- `claim_evidence_map.csv`
- manifest keys:
  - `novelty_framing_md`
  - `claim_evidence_map_csv`
- figure source:
  - `figure_15_claim_evidence_map.csv`

## Before

The package had claim limits, methods, and data artifacts, but not a concise literature/novelty frame. The manuscript could drift between artificial life, embodied cognition, RL, ecology, and open-ended evolution.

## After

The package now frames the contribution as:

- an artificial-life simulation study of experience-sensitive behavior,
- a reproducible telemetry and evidence package,
- not a new RL algorithm,
- not proof of intentional farming,
- not proof of social transmission,
- not proof of open-ended evolution.

`claim_evidence_map.csv` maps claims to:

- manuscript role,
- current status,
- evidence artifacts,
- required evidence,
- reviewer risk.

## Evidence Added

New tests verify that:

- novelty framing is exported,
- the framing includes experience-sensitive behavior,
- the framing explicitly says this is not proof of open-ended evolution,
- direct same-agent experience can support the individual-learning claim,
- intentional farming/open-ended evolution remains prohibited by claim scope.

## Validation

Commands run:

```text
python -m unittest tests.test_publication_journal_readiness_artifacts
python -m unittest discover -s tests
python -m compileall main.py simulation tests
```

Result:

```text
Ran 34 tests
OK
```

## Remaining Risk

This artifact gives a safe novelty frame, but final manuscript references still need to be filled with actual citations chosen for the target journal.

## Journal Verdict

Fixed at the package/framing level. The paper now has a safer claim hierarchy and a clearer novelty lane.
