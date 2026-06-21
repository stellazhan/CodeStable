# cs-goal Reference

Use this file for templates and recovery rules after `cs-goal` triggers.

## Directory

```text
.codestable/goals/YYYY-MM-DD-{slug}/
├── state.yaml
├── goal.zh.md
├── goal.en.md
├── functional-acceptance.zh.md
├── functional-acceptance.en.md
└── iterations/
    ├── 001.zh.md
    └── 001.en.md
```

`{slug}` is short English kebab-case, and the date is the goal creation date.
The dated directory name is the filesystem unit; the `state.yaml` `goal` field
remains the bare slug. Reuse an active matching goal instead of creating a
duplicate. The functional acceptance pair is created only during the terminal
acceptance gate, not as empty files at goal start.

## state.yaml Schema

```yaml
schema_version: 1
goal: "{slug}"
status: active # active | complete | blocked
objective: "{owner-level outcome}"
start_point: "{known starting condition}"
acceptance:
  - "{observable done signal}"
non_goals:
  - "{explicitly out of scope}"
budget:
  kind: none # none | time | iterations | token | owner-defined
  limit: null
current_iteration: 0
next_action: "{smallest useful next attempt}"
blocker_signature: null
blocker_count: 0
owner_stop: null
updated_at: "YYYY-MM-DD"
```

Recovery priority:

1. `state.yaml`
2. latest iteration frontmatter
3. Markdown body

## Start Report

`goal.zh.md` and `goal.en.md` are the durable start report produced from the
interview / grill. They must exist before implementation begins. Both files
must include the same objective, starting point, acceptance criteria, non-goals,
owner decisions, unresolved assumptions, and next action.

These reports are human-readable context only. `state.yaml` remains the machine
source of truth so later agents do not infer state from bilingual prose.

## Next Iteration Number

`state.yaml.current_iteration` means the last completed iteration, not the next
in-progress attempt.

Before changing `current_iteration`, compute the next `{nnn}` as:

```text
max(state.yaml.current_iteration, highest existing iterations/{nnn}.*.md) + 1
```

Format it with three digits, then write both language files and leave
`state.yaml.current_iteration` equal to that completed number. Never overwrite
an existing iteration file.

## goal.zh.md Template

```markdown
---
doc_type: goal
goal: {slug}
language: zh
status: active
---

# {目标名}

## 目标

## 起点

## 验收标准

## 明确不做

## 决策与假设

## 当前状态

## 下一步
```

## goal.en.md Template

```markdown
---
doc_type: goal
goal: {slug}
language: en
status: active
---

# {Goal Name}

## Objective

## Starting Point

## Acceptance Criteria

## Non-Goals

## Decisions And Assumptions

## Current State

## Next Action
```

The Chinese and English files must be content-equivalent, not summary versus
full detail.

## Iteration Frontmatter

```yaml
---
doc_type: goal-iteration
goal: "{slug}"
iteration: 1
language: zh # zh | en
status_after: active # active | complete | blocked
next_action: "{same meaning as state.yaml}"
blocker_signature: null
updated_at: "YYYY-MM-DD"
---
```

## Chinese Iteration Headings

```markdown
# Iteration 001

## 本轮理解

## 实现方式

## 本轮变更

## 验证证据

## 遇到的问题

## 下一步尝试

## 状态更新
```

## English Iteration Headings

```markdown
# Iteration 001

## Current Understanding

## Implementation Approach

## Changes This Iteration

## Verification Evidence

## Problems Encountered

## Next Attempt

## State Update
```

Both language files should carry the same facts, evidence, risks, and next
action. Translate meaning, not word order.

## Iteration Rules

- Write reports only at iteration end.
- Include fresh verification evidence, even when the iteration failed.
- If nothing changed, say so and explain what was learned.
- Keep historical failed attempts in iteration reports; do not rewrite them into
  success.
- Update `state.yaml` with the iteration pair so resume sees the same
  completed iteration, next action, and status that humans read.

## Functional Acceptance Report

Before `status: complete`, dispatch a subagent for product-facing functional
acceptance. Record the result in both files:

- `functional-acceptance.zh.md`
- `functional-acceptance.en.md`

The pair must include equivalent content:

- reviewer and subagent role;
- acceptance criteria checked;
- functional evidence beyond tests alone;
- verdict: pass, fail, or inconclusive;
- residual risks and follow-up;
- the final iteration that cites this acceptance.

Tests, linters, and builds are verification evidence, but completion requires
the subagent functional acceptance pair. If subagent dispatch is unavailable or
not authorized, write `approval-report.md` and owner-stop instead of marking the
goal complete.

## Owner Stop Record

When stopping, update `state.yaml`:

```yaml
status: blocked
blocker_signature: "{stable short phrase}"
blocker_count: 3
owner_stop: "{question or approval needed}"
next_action: "Wait for owner decision on {topic}."
```

The latest iteration pair must explain:

- what decision is needed;
- why AI cannot safely continue;
- options or expected answer shape;
- what will happen after the owner answers.

## Relationship To Other Flows

`cs-goal` may create or reference feature, issue, refactor, roadmap, or decision
artifacts when their rules apply. The goal state remains the wrapper for
autonomous iteration; child artifacts remain the source of truth for their own
workflow.
