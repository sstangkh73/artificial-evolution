# Repository Inventory

Prepared: `2026-06-21`

## 1. High-level survey

Broad repository scan results at the time of writing:

- total files under the repository root: about `5,988`
- `docs/`: primarily markdown research and design notes
- `reports/`: markdown, figures, PDFs, DOCX, and presentation artifacts
- `data/`: the largest evidence store, including JSON, CSV, markdown summaries, dashboards, JSONL event streams, and logs

This repository is already a research workspace, not just an application codebase.

## 2. Most important code paths

These are the fastest files to read when someone needs the real current behavior:

- [main.py](/C:/artificial-evolution/main.py)
  - CLI entry point and available run modes
- [simulation/runner.py](/C:/artificial-evolution/simulation/runner.py)
  - experiment orchestration, capture modes, search loops, telemetry, and research bundle generation
- [agents/agent.py](/C:/artificial-evolution/agents/agent.py)
  - agent life cycle, instincts, social logic, reproduction gating, storage, and behavior
- [agents/body.py](/C:/artificial-evolution/agents/body.py)
  - body schema, trait space, body generation, and inheritance logic
- [world/environment.py](/C:/artificial-evolution/world/environment.py)
  - ecology, plants, food, nests, large animals, and world physics
- [tests/test_metabolism.py](/C:/artificial-evolution/tests/test_metabolism.py)
  - the only test file currently present; focused on metabolism v2 scaffolding

## 3. Most important written sources

These are the key project documents I would trust first:

- [docs/CURRENT_STATE.md](/C:/artificial-evolution/docs/CURRENT_STATE.md)
  - best compact status split between implemented, partial, and planned
- [docs/PROJECT_OVERVIEW.md](/C:/artificial-evolution/docs/PROJECT_OVERVIEW.md)
  - conceptual phase framing
- [docs/RESEARCH_QUESTION.md](/C:/artificial-evolution/docs/RESEARCH_QUESTION.md)
  - canonical short research question
- [docs/PHASE2_ROADMAP.md](/C:/artificial-evolution/docs/PHASE2_ROADMAP.md)
  - identified gap from search-based success into endogenous evolution
- [reports/project_status_full_2026-06-20.md](/C:/artificial-evolution/reports/project_status_full_2026-06-20.md)
  - strongest single narrative source for recent findings, failed hypotheses, and blockers

## 4. Repository structure by purpose

### Runtime and simulation

- [agents](/C:/artificial-evolution/agents)
- [world](/C:/artificial-evolution/world)
- [simulation](/C:/artificial-evolution/simulation)
- [visualization](/C:/artificial-evolution/visualization)

### Scientific framing and design

- [docs](/C:/artificial-evolution/docs)
- [papers](/C:/artificial-evolution/papers)

### Evidence and outputs

- [data](/C:/artificial-evolution/data)
- [reports](/C:/artificial-evolution/reports)

### Automation and artifact generation

- [scripts](/C:/artificial-evolution/scripts)

### Validation

- [tests](/C:/artificial-evolution/tests)

## 5. What appears mature vs immature

### Relatively mature

- simulation scope and feature richness
- experiment-running infrastructure
- artifact generation for reports and publication bundles
- iterative hypothesis-driven investigation
- willingness to log negative results and adjust claims

### Still immature

- automated test coverage outside metabolism v2
- a single always-up-to-date source-of-truth summary
- clean separation between legacy artifacts and current canonical evidence
- documentation alignment with the real code
- reproducibility guarantees around all stochastic pathways

## 6. Risks when reading this repository

Anyone working here should expect these interpretation risks:

- older docs may understate current implementation
- some reports are phase-local and should not be mistaken for the latest global status
- the `data/` directory contains huge amounts of generated output, including historical states and dead ends
- a result existing in the repo does not automatically mean it is still considered a valid claim

## 7. Practical reading order for new work

Recommended order for future contributors:

1. [reports/ISEF_MASTER_PLAN_2026-06-21/01_project_synthesis.md](/C:/artificial-evolution/reports/ISEF_MASTER_PLAN_2026-06-21/01_project_synthesis.md)
2. [reports/project_status_full_2026-06-20.md](/C:/artificial-evolution/reports/project_status_full_2026-06-20.md)
3. [docs/CURRENT_STATE.md](/C:/artificial-evolution/docs/CURRENT_STATE.md)
4. [main.py](/C:/artificial-evolution/main.py)
5. [simulation/runner.py](/C:/artificial-evolution/simulation/runner.py)
6. [agents/agent.py](/C:/artificial-evolution/agents/agent.py)
7. [world/environment.py](/C:/artificial-evolution/world/environment.py)
8. phase-specific reports relevant to the next experiment

## 8. Bottom line

This repository already contains enough material for a serious research campaign, but it needs stronger curation to support `ISEF` judging, advisor review, and reproducible scientific claims. The new folder is intended to be that curation layer.
