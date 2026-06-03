# Research Skills Pack

A practical AI skill pack adapted from the workflow style of `langgptai/awesome-deep-research-prompts` and extended for scientific research, paper writing, log reading, and synthesis.

## Install

Copy the `skills/` folder into your AI workspace, then mention the available skills in `AGENTS.md`, `CLAUDE.md`, or your tool's equivalent instruction file.

```text
skills/
├── deep-research/
├── scientific-research/
├── paper-writing/
├── log-reading/
├── thinking-synthesis/
└── alife-research/
```

## Recommended AGENTS.md entry

```markdown
# Available Skills

Use these skills when the task matches:

- `deep-research`: research planning, source gathering, background synthesis, topic breakdown.
- `scientific-research`: hypothesis design, methodology, experiments, metrics, validity checks.
- `paper-writing`: research paper drafts, IMRaD structure, abstract, discussion, limitations.
- `log-reading`: analyze logs, simulation outputs, diagnostics, failures, regressions.
- `thinking-synthesis`: turn messy notes into clear reasoning, decisions, summaries, next actions.
- `alife-research`: artificial life, agent-based simulation, evolutionary systems, emergent behavior.

Before using any skill, state which skill is being used and why. Never invent citations, results, logs, metrics, or experimental outcomes.
```

## Usage examples

```text
Use the scientific-research skill to design the next experiment for H1-H11.
Use the log-reading skill to analyze this diagnostics output.
Use the paper-writing skill to turn these results into a research-paper draft.
Use the thinking-synthesis skill to summarize my messy notes into decisions and next steps.
```
