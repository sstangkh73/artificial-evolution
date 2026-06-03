# Project Instructions for Codex

When working in `C:\artificial-evolution`, always inspect and apply the local project skills in:

`agents\.skills`

Use the relevant skill before doing task-specific work. These project-local skills are:

- `artificial-life`
- `engineering`
- `experiment-design`
- `hypothesis-testing`
- `log-analysis`
- `paper-writing`
- `peer-review`
- `presentation`
- `research`
- `statistics-analysis`

Skill files are normally named `SKILL.md`; `engineering` currently uses `skill.md`.

For future work in this workspace:

- If the user asks to analyze logs, load `agents\.skills\log-analysis\SKILL.md`.
- If the user asks to design or run experiments, load `experiment-design`, `hypothesis-testing`, and/or `statistics-analysis` as appropriate.
- If the user asks to write reports or papers, load `paper-writing` and `research` as appropriate.
- If the user asks for code changes, load `engineering` and any domain-specific skill that fits the task.
- If the task concerns artificial life, evolution, agents, reproduction, ecology, or simulation behavior, load `artificial-life`.

Treat these skills as project-local guidance. If they conflict with higher-priority system or developer instructions, follow the higher-priority instructions and note the conflict briefly.
