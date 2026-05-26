---
name: using-codestable
description: Use when starting any coding or project-maintenance conversation. If the current repository has .codestable/attention.md, CodeStable is active and lifecycle tasks must route through cs before answering or acting.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a narrow task, skip this skill unless the parent task explicitly asks you to run CodeStable routing.
</SUBAGENT-STOP>

# Using CodeStable

This skill is the CodeStable auto-entry guard. It mirrors the Superpowers `using-superpowers` pattern: a broad entry skill decides whether the workflow system applies, then routes to the real process skill.

`using-codestable` does not replace `cs`. It only decides whether an onboarded repository should enter CodeStable. `cs` remains the router for choosing the concrete `cs-*` workflow.

---

## Rule

At the start of any coding or project-maintenance task, check whether the current repository has `.codestable/attention.md`.

If it exists, CodeStable is active. For lifecycle tasks, route through `cs` before answering, asking clarifying questions, reading broad code context, or making changes.

If the platform has explicit skill invocation, invoke `cs`. If it does not, follow the `cs` skill's routing rules directly: read `.codestable/attention.md`, inspect the CodeStable workspace, then choose the right `cs-*` workflow.

---

## Lifecycle Tasks

Route through `cs` when the user asks about:

- New features, changed behavior, or product capability work
- Bugs, regressions, broken commands, bad docs, or unexpected behavior
- Refactors, cleanup, performance, maintainability, or structure changes
- Requirements, architecture, roadmap, planning, design, or acceptance
- Audits, reviews, risk scans, or "what should we improve?"
- Code exploration, "how does X work?", or module orientation
- Decisions, conventions, learnings, tricks, or things worth remembering
- Developer guides, user guides, API docs, or library docs
- Workflow continuation: "next step", "continue", "start implementing", "validate", "finish", "merge", or "close this out"

When in doubt and `.codestable/attention.md` exists, prefer entering `cs`. `cs` can still decide that the task is too small or should route elsewhere.

---

## Skip Cases

Do not route through `cs` when:

- The user explicitly says "skip CodeStable", "don't use cs", "direct fix", or equivalent
- The task is a trivial one-off command or answer: current time, simple translation, short rewrite, basic shell output
- The repository has no `.codestable/attention.md`
- You are a subagent with a narrow delegated task and the parent already chose the workflow
- The request is outside software lifecycle work, such as general chat or unrelated personal admin

If the user explicitly asks to onboard CodeStable in a repository without `.codestable/attention.md`, route to `cs-onboard`.

---

## Minimal Behavior

Be low-noise. This skill should not add a ceremony layer to every response.

- If CodeStable is inactive, continue normally.
- If CodeStable is active and the task is a lifecycle task, say briefly: `Using cs because this repo is onboarded with CodeStable.`
- Then route to `cs` and follow its output.

---

## Responsibility Split

- `using-codestable`: detects active CodeStable repositories and decides whether CodeStable should be entered.
- `cs`: reads the active CodeStable context and routes to exactly one `cs-*` workflow.
- Concrete `cs-*` skills: perform the real workflow.

Do not put feature, issue, refactor, or docs workflow logic in this skill. Keep it as the auto-entry guard.
