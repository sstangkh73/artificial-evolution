# After Fix Report: Frozen Protocol and Reproducibility Package

Date: 2026-06-26

## Objective

Complete journal-readiness item 9 by freezing protocol and rerun information inside each publication package.

## What Changed

`simulation/publication_artifacts.py` now writes:

- `frozen_protocol.json`
- `reproducibility_checklist.md`
- manifest keys:
  - `frozen_protocol_json`
  - `reproducibility_checklist_md`

`simulation/runner.py` now includes `snapshot_interval` in runtime provenance so rerun templates can be reconstructed more accurately.

## Before

The package had runtime provenance and methods text, but no single frozen protocol artifact. A reviewer had to assemble the protocol from multiple files.

## After

`frozen_protocol.json` now records:

- protocol version,
- freeze status,
- independent unit,
- seed policy,
- condition registry,
- primary outcomes,
- secondary outcomes,
- required artifact list,
- rerun command template,
- runtime provenance.

`reproducibility_checklist.md` now provides a reviewer-facing checklist before submission.

## Evidence Added

New tests verify that:

- `frozen_protocol_json` is exported,
- protocol version is present,
- independent unit is `seed_run`,
- required artifacts include `generalization_audit.csv`,
- rerun command includes the study seed count,
- checklist includes the rerun template section.

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

This freezes the generated package protocol. For a final submission, the team should run a fresh journal batch and treat that generated `frozen_protocol.json` as the submission lock.

## Journal Verdict

Fixed. The package now has a clear reproducibility spine.
