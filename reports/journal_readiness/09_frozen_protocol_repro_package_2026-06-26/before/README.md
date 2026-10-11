# Before Fix Report: Frozen Protocol and Reproducibility Package

Date: 2026-06-26

## Objective

Fix journal-readiness item 9: freeze the experiment protocol and reproducibility recipe inside the generated publication package.

## Research Risk

For a journal paper, reviewers need to know exactly what was planned before interpreting results. Without a frozen protocol artifact, the package risks looking post-hoc:

- conditions may look chosen after results,
- outcome definitions may drift,
- seed ranges may be unclear,
- rerun commands may be missing,
- version/provenance may be incomplete.

## Current State

The package exports:

- `runtime_provenance.json`,
- `methods_full.md`,
- `data_availability_statement.md`,
- raw manifest paths,
- figure source data.

This is good, but there is no single machine-readable protocol lock and no concise rerun checklist.

## Hypothesis

The package becomes more publishable if it exports a frozen protocol with condition definitions, outcomes, analysis artifacts, seed policy, and rerun instructions.

## Evidence Supporting

- Runtime provenance exists but is not a full protocol freeze.
- Methods text exists but is not machine-readable.
- Manifest links exist but do not state protocol status or rerun commands.

## Required Fix

Add generated artifacts:

1. `frozen_protocol.json`
2. `reproducibility_checklist.md`
3. manifest entries
4. tests that verify protocol version, independent unit, conditions, outcomes, and rerun command are present

## Success Criteria

- The package contains a protocol version and freeze status.
- Conditions and outcomes are listed in the frozen protocol.
- The seed policy and independent unit are explicit.
- Rerun commands are documented.
- Tests protect the artifact.

## Confidence Before Fix

High. The current package is reproducible enough for internal work, but journal submission needs a clearer protocol lock.
