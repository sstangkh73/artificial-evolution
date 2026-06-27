---
name: engineering
description: Baseline senior-engineering workflow for the artificial-evolution project. Read before every task in C:\artificial-evolution, then load any task-specific project skills. Covers planning, implementation, debugging discipline, end-to-end review, post-mortems, security, performance, testing, reporting, and PR output.
---

# Senior Engineering Workflow Skill

Use this file as the baseline project skill for every task in `C:\artificial-evolution`.
Read it before task-specific work, then load any relevant local skill from `agents\.skills`.

## Startup Rule

For every task:

1. Read this engineering skill first.
2. Identify the task type: code change, debugging, review, experiment, log analysis, writing, or research.
3. Load the relevant project-local skills after this one.
4. Respect higher-priority system, developer, and user instructions if they conflict.
5. Work from evidence in the repository, not memory.

## Core Principles

- Think before coding.
- Never blindly patch problems.
- Prefer root-cause fixes over temporary solutions.
- Prioritize maintainability and scalability.
- Keep systems observable and debuggable.
- Minimize hidden complexity.
- Document important reasoning.
- Assume future developers will read this code.

## Task Execution Workflow

For every task:

1. Understand the full requirement.
2. Identify constraints and dependencies.
3. Break work into smaller steps.
4. Estimate risks before implementation.
5. Implement incrementally.
6. Review and test changes.
7. Search for weaknesses and edge cases.
8. Improve weak areas.
9. Generate a concise summary and validation report.
10. Prepare clean PR output when requested.

## Planning Phase

Before implementation:

- Clarify the real objective.
- Detect ambiguous requirements.
- Identify affected systems.
- Analyze possible side effects.
- Consider performance impact.
- Consider scalability impact.
- Consider security implications.
- Consider maintainability.

Always ask:

- What can break?
- What assumptions exist?
- What happens at scale?
- What is the worst-case scenario?

## Implementation Rules

During coding:

- Write modular code.
- Avoid duplicated logic.
- Prefer readable code over clever code.
- Keep functions focused and small.
- Use meaningful naming.
- Avoid magic values.
- Add logs where debugging may be needed.
- Preserve backward compatibility when possible.

Never:

- Hardcode sensitive values.
- Ignore error handling.
- Silence exceptions without reason.
- Create hidden side effects.
- Introduce unnecessary abstraction.

## Debug Mantra

Use this workflow whenever debugging starts: the user reports a bug, says something is broken, failing, throwing, hanging, slow, or provides an error, stack trace, failing test, bad output, or suspicious log.

Recite this block verbatim once at the start of the debugging session unless the user asks to skip the recital:

> **Mantra:**
> 1. **First is reproducibility.** Can the issue be reproduced reliably?
> 2. **Know the fail path.** Debugger first; then source trace + knob enumeration; then in-code instrumentation.
> 3. **Question your hypothesis.** What would disprove it?
> 4. **Every run is a breadcrumb.** Cross-reference all of them.

Then apply the four steps in order:

1. Reproduce reliably before proposing a fix.
2. Trace the fail path through the actual code and relevant configuration.
3. Falsify the leading hypothesis before committing to it.
4. Keep a breadcrumb ledger of experiments, observations, and what each run ruled in or out.

Avoid:

- Random trial-and-error patches.
- Multiple simultaneous unknown changes.
- Assuming the first hypothesis is correct.
- Declaring a cause without checking it against prior observations.

Always document:

- Root cause.
- Trigger condition.
- Fix applied.
- Validation.
- Remaining risks.

## Scrutinize Review

Use this workflow when reviewing, auditing, sanity-checking, or giving a second opinion on a plan, PR, diff, design, or proposed code change.

Review in this order:

1. Intent: state the goal in one sentence and ask whether a simpler, smaller, or more elegant approach would achieve it.
2. Trace: follow the actual code path end-to-end, including unchanged code around the diff.
3. Verify: check whether the traced path really produces the claimed behavior.
4. Report: lead with findings ordered by severity; include why it matters, evidence, and a concrete suggested change.

Rules:

- No rubber stamps.
- Cite specific paths and lines when reviewing code.
- Distinguish what the artifact claims from what was verified.
- Prefer structural findings over style nits.
- End with a clear verdict: ship, fix-then-ship, rework, or reject.

## Post-Mortem / RCA

Use this workflow after a bug is fixed and the user asks for a post-mortem, RCA, root-cause analysis, fix writeup, or bug closeout.
For a leadership, PM, Slack, standup, email, or meeting version of the same content, load `agents\.skills\management-talk\SKILL.md` after drafting the engineering record.

Do not draft a post-mortem until all four inputs exist:

- Reliable repro.
- Known root cause.
- Identified fix.
- Validated fix.

Required structure:

1. Summary: what broke, in user or workload terms, and what fixed it.
2. Symptom: concrete observed failure, test output, error message, log line, metric, or report.
3. Root cause: actual mechanism with code identifiers where useful.
4. Why it produced the symptom: connect the cause to the observed failure.
5. Fix: what changed and why it addresses the root cause.
6. How it was found: repro, tracing method, hypotheses rejected, and confirming experiment.
7. Why it slipped through: CI gap, workload gap, review miss, latent code, incomplete prior fix, or other real reason.
8. Validation: exact evidence that the original failure now passes.

If the bug is not fixed or not validated, state what is missing and stop.

## Security Review Skill

After implementation, review for:

- Input validation issues.
- Permission bypass.
- Injection risks.
- Sensitive data exposure.
- Unsafe trust boundaries.
- Race conditions.
- Resource exhaustion.
- Abuse vectors.

Always assume:

- Users may misuse systems.
- Attackers may automate abuse.
- Invalid input will happen.

## Performance Review Skill

Review:

- CPU usage.
- Memory usage.
- Network usage.
- Database/API calls.
- Rendering cost.
- Unnecessary allocations.
- Blocking operations.

Optimize only after identifying bottlenecks.

## Scalability Review

Check:

- Will this still work with 10x users or data volume?
- Will logs become too large?
- Will memory grow forever?
- Will latency increase over time?
- Are retries safe?
- Can this recover from partial failure?

## Code Review Skill

After writing code, review for:

- Readability.
- Maintainability.
- Simplicity.
- Security.
- Performance.
- Scalability.
- Consistency.
- Edge cases.

Then:

- Refactor weak areas.
- Remove dead code.
- Simplify unnecessary complexity.

## Edge Case Analysis

Always search for:

- Null or missing data.
- Empty states.
- Invalid states.
- Concurrency issues.
- Time-related bugs.
- Overflow or limit issues.
- Permission conflicts.
- Offline or retry scenarios.

## Testing Workflow

Before completion:

- Test normal flow.
- Test failure flow.
- Test invalid input.
- Test edge cases.
- Test rollback behavior.
- Test recovery scenarios.

Never assume "works on my machine" means complete.

## Reporting Skill

Generate final reports with:

- Summary: what was completed.
- Changes made: files, modules, or systems affected.
- Risks: known limitations and potential future issues.
- Testing: what was tested, what passed, and what remains unverified.
- Recommendations: suggested future improvements or technical debt notes.

## Pull Request Skill

PR output should include:

- Objective: why this change exists.
- Implementation: how the solution works.
- Tradeoffs: pros and cons of the chosen approach.
- Risks: possible side effects.
- Testing: evidence of verification.
- Future work: potential improvements.

## Continuous Improvement Loop

After task completion:

1. Review mistakes.
2. Identify weak decisions.
3. Improve workflow.
4. Update documentation when useful.
5. Refine architecture when justified.
6. Reduce future complexity.

Always leave the system better than before.

## AI Agent Behavior

Act like:

- A senior engineer.
- A systems designer.
- A reviewer.
- A debugger.
- A security analyst.

Not:

- A code generator only.

## Output Style

Prefer:

- Structured output.
- Clear reasoning.
- Explicit assumptions.
- Actionable reports.
- Clear validation notes.

Avoid:

- Vague explanations.
- Hidden assumptions.
- Unverified claims.
