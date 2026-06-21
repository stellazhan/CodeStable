---
name: cs-goal
description: Goal-driven autonomous workflow for bounded start/end tasks. Use when the owner gives a desired outcome, acceptance result, budget, or asks AI to "reach this goal", "run until accepted", "self-iterate", "autonomous iteration", or "grill me" before implementation. Creates bilingual start, iteration, and functional acceptance artifacts under `.codestable/goals/`.
---

# cs-goal

`cs-goal` handles bounded goals: the owner gives the starting point and desired
end state, then CodeStable interviews / grills lightly, writes a bilingual start
report before implementation, implements autonomously, verifies, requests
subagent functional acceptance before completion, and writes bilingual iteration
reports.

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
5. Read `.codestable/reference/approval-conventions.md` if present.
6. Before code edits, review, commit, finish, or merge work, read
   `.codestable/reference/execution-conventions.md` if present.
7. Inspect `.codestable/goals/` for an active matching goal.
8. Search `.codestable/compound/` and relevant feature / issue / refactor docs
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

Always grill before creating a new goal. Treat interview / grill as the formal
goal start point, not disposable chat. Keep it short and owner-level.

Ask at most 3-5 focused questions. Each round uses one question plus 2-4
meaningfully different choices. Avoid asking for implementation details unless
the answer changes the goal boundary.

If a grill answer requires owner approval of scope, route, budget, risk, or
stopping policy and the options need explanation, first write
`.codestable/goals/{slug}/approval-report.md`. A simple clarifying question can
stay in chat; a decision checkpoint needs the report.

Collect only:

- objective;
- starting point;
- acceptance / done signal;
- non-goals;
- budget or stopping preference if given;
- strict owner-stop conditions that are specific to this goal.

If the owner already gave enough information, summarize it and proceed.
Before any code edit or autonomous implementation attempt, Phase 2 must create
or refresh the bilingual start report pair.

---

## Phase 2: Create Or Resume Goal

Goal directory over its lifecycle:

```text
.codestable/goals/{slug}/
├── state.yaml
├── goal.zh.md
├── goal.en.md
├── functional-acceptance.zh.md
├── functional-acceptance.en.md
└── iterations/
```

Create the functional acceptance pair only during the terminal acceptance gate,
not as empty files at goal start.

`goal.zh.md` and `goal.en.md` are the bilingual start report from the interview
/ grill. They must exist before implementation. Include objective, starting
point, acceptance criteria, non-goals, owner decisions, unresolved assumptions,
and next action. Keep them concise and update them only when the goal boundary
or state changes.

If an active matching goal exists, resume it instead of creating a duplicate.
Read `state.yaml`, the start report pair, then the latest
`iterations/{n}.zh.md` and `{n}.en.md`. If the start report pair is missing,
reconstruct it from state and interview evidence before code edits.

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
Do not mark a goal complete from ordinary test evidence alone; run the terminal
functional acceptance gate first.

## Terminal Functional Acceptance

Before changing `state.yaml.status` to `complete`:

1. Run normal verification with fresh evidence.
2. Dispatch a subagent to perform functional acceptance against the recorded
   owner acceptance criteria and actual product / artifact behavior.
3. Record the result in both `functional-acceptance.zh.md` and
   `functional-acceptance.en.md`, including reviewer, scope, acceptance checks,
   functional evidence, verdict, residual risks, and any follow-up.
4. Reference the functional acceptance pair in the final bilingual iteration.

Functional acceptance is product-facing evidence. It may include black-box usage,
artifact inspection, UI / API workflow checks, fixture output review, or another
owner-relevant proof. Unit tests, linters, and build checks are useful evidence
but are not enough by themselves.

If subagent dispatch is unavailable or not authorized, owner-stop with
`approval-report.md`; do not self-accept the goal as complete.

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

Mark `complete` only when the acceptance signal is satisfied, the subagent
functional acceptance pair records a passing verdict, and evidence is recorded
in the final iteration.

Mark `blocked` only after the same blocker has repeated for at least three
consecutive iterations or the owner-stop rule says the AI cannot safely proceed.
Record `blocker_signature`, `blocker_count`, evidence, and the owner decision
needed. Before asking the owner to decide, write `approval-report.md` in the goal
directory unless the latest iteration pair already contains the full decision
context, options, recommendation, tradeoffs, evidence, consequence, and next
action.

If budget ends before acceptance, stop with approval context instead of
pretending completion.

---

## Exit

A goal run exits with one of:

- `complete`: acceptance evidence, subagent functional acceptance, and final
  bilingual iteration written.
- `blocked`: blocker evidence and owner question recorded.
- `active`: iteration report written and next action recorded, but the current
  turn or budget ends before more work can be done.

Final replies should be short and point to `goal.zh.md`, `goal.en.md`, the
latest bilingual iteration pair, and the functional acceptance pair when the
goal is complete.

---

## Guardrails

- Do not ask the owner to choose routine technical details.
- Do not let bilingual prose override `state.yaml`.
- Do not create duplicate active goals for the same objective.
- Do not skip iteration reports after meaningful work.
- Do not mark completion from tests alone or forge subagent acceptance.
- Do not keep iterating after a strict owner-stop fires.
- Keep every Markdown artifact under 300 lines; split long reports.
