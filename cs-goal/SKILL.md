---
name: cs-goal
description: Goal-driven autonomous workflow for bounded start/end tasks. Use when the owner gives a desired outcome, acceptance result, budget, or asks AI to "reach this goal", "run until accepted", "self-iterate", "autonomous iteration", or "grill me" before implementation. Creates bilingual goal and iteration artifacts under `.codestable/goals/`.
---

# cs-goal

`cs-goal` handles bounded goals: the owner gives the starting point and desired
end state, then CodeStable grills lightly, implements autonomously, verifies, and
writes bilingual iteration reports.

This is a goal wrapper, not a replacement for feature / issue / refactor rules.
When the goal crosses a capability boundary, exposes a bug root cause, or needs
behavior-preserving refactor governance, create or reference the matching
feature / issue / refactor artifacts inside the goal iteration.

Read `reference.md` for artifact templates, `state.yaml` schema, report
headings, and recovery rules.

---

## Startup

Before acting:

1. Read `.codestable/attention.md`.
2. Read `.codestable/reference/system-overview.md` if present.
3. Read this skill's `reference.md`.
4. Read `.codestable/reference/goal-conventions.md` if present.
5. Before code edits, review, commit, finish, or merge work, read
   `.codestable/reference/execution-conventions.md` if present.
6. Inspect `.codestable/goals/` for an active matching goal.
7. Search `.codestable/compound/` and relevant feature / issue / refactor docs
   when the goal names an existing area.

If `.codestable/` is missing, route to `cs-onboard`.

---

## When To Use

Use `cs-goal` when the owner expresses a bounded destination:

- "starting from this broken state, make the tests pass";
- "reach this acceptance result";
- "run autonomously and self-iterate";
- "keep trying until complete or blocked";
- "grill me first, then implement";
- "I care about the outcome, not the technical choices".

Do not use it for:

- pure design, roadmap, or discussion requests with no implementation goal;
- open-ended brainstorming where the owner does not yet know the end state;
- status checks or audits that do not ask the AI to drive toward completion.

---

## State Model

Mirror Codex's simple goal state:

```text
active | complete | blocked
```

`state.yaml` is the machine source of truth. Markdown is for humans. Recovery
priority is:

1. `.codestable/goals/{slug}/state.yaml`
2. latest iteration frontmatter
3. Markdown body text

Never infer the current machine state from bilingual narrative when `state.yaml`
has a clear value.

---

## Phase 1: Grill Alignment

Always grill before creating a new goal. Keep it short and owner-level.

Ask at most 3-5 focused questions. Each round uses one question plus 2-4
meaningfully different choices. Avoid asking for implementation details unless
the answer changes the goal boundary.

Collect only:

- objective;
- starting point;
- acceptance / done signal;
- non-goals;
- budget or stopping preference if given;
- strict owner-stop conditions that are specific to this goal.

If the owner already gave enough information, summarize it and proceed.

---

## Phase 2: Create Or Resume Goal

New goal directory:

```text
.codestable/goals/{slug}/
├── state.yaml
├── goal.zh.md
├── goal.en.md
└── iterations/
```

`goal.zh.md` and `goal.en.md` contain equivalent human-readable goal context.
Keep them concise and update them only when the goal state changes.

If an active matching goal exists, resume it instead of creating a duplicate.
Read `state.yaml`, then the latest `iterations/{n}.zh.md` and `{n}.en.md`.

---

## Phase 3: Autonomous Iteration

One iteration is a coherent implementation / verification attempt, not a single
command.

Loop while `state: active`:

1. Choose the smallest useful next attempt from `state.yaml`.
2. Implement using existing CodeStable constraints, including worktree, review,
   spec-governance, and commit rules when they apply.
3. Verify with fresh commands or evidence.
4. Before changing `state.yaml.current_iteration`, derive the next zero-padded
   iteration number from
   `state.yaml.current_iteration` and existing `iterations/{nnn}.*.md` files;
   never overwrite a prior report.
5. Update `state.yaml` for the completed attempt, leaving
   `current_iteration: {n}`.
6. Write exactly one bilingual report pair for that completed iteration:
   `iterations/{nnn}.zh.md` and `iterations/{nnn}.en.md`.
7. Continue autonomously unless an owner-stop condition fires.

Do not write reports after every command. Reports are iteration summaries.

---

## Strict Owner Stops

Stop and ask the owner only when:

- acceptance criteria conflict or are no longer enough to decide completion;
- the objective, start point, or terminal condition has a major ambiguity;
- continuing would change long-lived specs, public contract, or capability
  boundary beyond the recorded goal;
- the same blocker repeats for three consecutive iterations;
- budget is exhausted or nearly exhausted;
- the next step requires explicit human risk acceptance, secrets, destructive
  action, external purchase, or merge / deployment approval.

Normal technical choices, test failures, implementation alternatives, and local
refactors are AI-owned unless they cross one of the stops above.

---

## Completion And Blocked Rules

Mark `complete` only when the acceptance signal is satisfied and evidence is
recorded in the final iteration.

Mark `blocked` only after the same blocker has repeated for at least three
consecutive iterations or the owner-stop rule says the AI cannot safely proceed.
Record `blocker_signature`, `blocker_count`, evidence, and the owner decision
needed.

If budget ends before acceptance, stop with owner context instead of pretending
completion.

---

## Exit

A goal run exits with one of:

- `complete`: acceptance evidence recorded, final bilingual iteration written.
- `blocked`: blocker evidence and owner question recorded.
- `active`: iteration report written and next action recorded, but the current
  turn or budget ends before more work can be done.

Final replies should be short and point to `goal.zh.md`, `goal.en.md`, and the
latest bilingual iteration pair.

---

## Guardrails

- Do not ask the owner to choose routine technical details.
- Do not let bilingual prose override `state.yaml`.
- Do not create duplicate active goals for the same objective.
- Do not skip iteration reports after meaningful work.
- Do not keep iterating after a strict owner-stop fires.
- Keep every Markdown artifact under 300 lines; split long reports.
