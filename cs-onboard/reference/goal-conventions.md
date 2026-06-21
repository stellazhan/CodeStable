# Goal Conventions

This file is copied by `cs-onboard` to
`.codestable/reference/goal-conventions.md`. It defines the shared runtime shape
for `cs-goal`.

## Purpose

Goals are bounded start/end work units. The owner defines the outcome and
acceptance signal; AI interviews / grills briefly, writes a bilingual start
report, implements, verifies, self-iterates, and writes bilingual reports. A
goal can close only after subagent functional acceptance of the produced result.

Use goals when the request says "reach this result", "run until accepted",
"self-iterate", "AI implements autonomously", or "grill me first".

## Directory

```text
.codestable/goals/{slug}/
├── state.yaml
├── goal.zh.md
├── goal.en.md
├── functional-acceptance.zh.md
├── functional-acceptance.en.md
└── iterations/
    ├── 001.zh.md
    └── 001.en.md
```

`state.yaml` is the machine source of truth. Markdown is human-readable context.
Recovery priority is `state.yaml` > latest iteration frontmatter > Markdown
body.

The functional acceptance pair is created only during the terminal acceptance
gate, not as empty files at goal start.

`goal.zh.md` and `goal.en.md` are the start report from interview / grill. They
must exist before implementation and include objective, start point, acceptance,
non-goals, owner decisions, unresolved assumptions, and next action.

## State Model

```text
active | complete | blocked
```

Required `state.yaml` fields:

- `schema_version`
- `goal`
- `status`
- `objective`
- `start_point`
- `acceptance`
- `non_goals`
- `budget`
- `current_iteration`
- `next_action`
- `blocker_signature`
- `blocker_count`
- `owner_stop`
- `updated_at`

`current_iteration` means the last completed iteration, not the next
in-progress attempt.

## Iteration Numbering

Before changing `current_iteration`, compute the next `{nnn}` as:

```text
max(state.yaml.current_iteration, highest existing iterations/{nnn}.*.md) + 1
```

Write both `iterations/{nnn}.zh.md` and `iterations/{nnn}.en.md`, then leave
`state.yaml.current_iteration` equal to that completed number. Never overwrite
an existing iteration file.

## Reporting

Each completed iteration writes two equivalent files:

- `iterations/{nnn}.zh.md`
- `iterations/{nnn}.en.md`

Reports are not command logs. One iteration equals a coherent implementation and
verification attempt. Both languages must include the same understanding,
implementation approach, changes, verification evidence, problems, next attempt,
and state update.

Before `status: complete`, write:

- `functional-acceptance.zh.md`
- `functional-acceptance.en.md`

This pair records subagent functional acceptance of the product / artifact
against the owner acceptance criteria. Include reviewer, scope, functional
evidence, verdict, residual risks, and the final iteration that cites it. Tests
alone are not enough to complete a goal.

## Strict Owner Stops

Stop only when:

- acceptance criteria conflict;
- objective / start / terminal condition has major ambiguity;
- continuing changes long-lived specs, public contract, or capability boundary
  beyond the recorded goal;
- the same blocker repeats for three consecutive iterations;
- budget is exhausted or nearly exhausted;
- risk acceptance, secrets, destructive action, external purchase, merge, or
  deployment approval is required.

Routine technical choices and ordinary failed attempts stay AI-owned.
