# Project Instructions for Codex

When working in `C:\artificial-evolution`, always inspect and apply the local project skills in:

`agents\.skills`

Mandatory startup rule:

1. Before doing any task-specific work, read `agents\.skills\engineering\SKILL.md` every time.
2. Do not rely on remembered skill content from an earlier session; re-open the skill at the start of each new task.
3. After loading `engineering`, read any task-relevant project-local skills before acting.

These project-local skills are:

- `artificial-life`
- `engineering`
- `experiment-design`
- `hypothesis-testing`
- `log-analysis`
- `management-talk`
- `paper-writing`
- `peer-review`
- `presentation`
- `research`
- `statistics-analysis`

Skill files are named `SKILL.md`.

For future work in this workspace:

- Always start by loading `agents\.skills\engineering\SKILL.md`.
- If the user asks to analyze logs, load `agents\.skills\log-analysis\SKILL.md`.
- If the user asks to design or run experiments, load `experiment-design`, `hypothesis-testing`, and/or `statistics-analysis` as appropriate.
- If the user asks to write reports or papers, load `paper-writing` and `research` as appropriate.
- If the user asks for management, leadership, executive, PM, Slack, email, standup, meeting, or less-technical engineering updates, load `management-talk`.
- If the user asks for code changes, load `engineering` and any domain-specific skill that fits the task.
- If the task concerns artificial life, evolution, agents, reproduction, ecology, or simulation behavior, load `artificial-life`.
- If the task is debugging, use the `Debug Mantra` section inside `engineering`.
- If the task is a review, audit, or sanity-check, use the `Scrutinize Review` section inside `engineering`.
- If the task is a fixed-bug writeup, RCA, or post-mortem, use the `Post-Mortem / RCA` section inside `engineering`.
- If a post-mortem or technical summary needs an up-the-org version, load `management-talk`.

Treat these skills as project-local guidance. If they conflict with higher-priority system or developer instructions, follow the higher-priority instructions and note the conflict briefly.
