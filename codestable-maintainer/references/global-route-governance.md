# Global Route Governance Matrix

## Owner Brief（中文）

### 这解决什么

CodeStable 的入口是 `cs` 自动分流，所以 human context 不能只加在
roadmap 或 spec 流程上。所有可能被 `cs` 路由到的流程，都必须先使用同一
套分流治理协议：说明当前 route、context level、升级条件、owner-stop 条
件、允许产物、跳过记录和完成检查。

目标不是让所有流程变重。目标是默认轻量，风险出现时才升级。小修、小探索、
小文档只给短 route brief；一旦工作会改变长期事实、未来 agent 输入、owner
判断边界、worktree 生命周期或公开行为，就升级到 decision、delta、analyze、
rehabilitation 或 finish gate。

### 这不解决什么

它不让 CodeStable 自动替 owner 做产品判断，不把每次 `cs` 调用变成问卷，
不强制每个小改动生成 spec，也不绕过已经存在的 feature / issue / refactor
专用流程。它定义的是所有 route 都必须遵守的轻重分级规则。

### 如何证明它有效

Behavior harness 必须测试这套矩阵本身，而不是只测试某个 roadmap：

- 轻量任务保持轻量，不生成不必要的 requirement delta。
- 模糊任务给 route choice 和 owner context。
- fast path 一旦发现 capability boundary 或 spec drift，升级到 L3。
- goal path 默认自主迭代，但验收冲突、spec/public contract 变化或重复 blocker 会 owner-stop。
- implementation / fix / refactor 过程中发现长期文档错误时，停止直接改 spec。
- finish worktree 检查 learner/context report、`covered_head` 和 inbox 状态。
- clean / compacted actor 能从 artifacts 和 tools 恢复同样的 next action。

## Goal

Make CodeStable routing reliable under short prompts, clean agents, long
contexts, and compacted resumes without turning every route into a heavyweight
approval process.

## Core Rule

Every routed CodeStable workflow must declare:

1. default context level;
2. escalation triggers;
3. owner-stop conditions;
4. allowed artifacts;
5. skip-record format;
6. finish-time checks;
7. behavior harness scenarios.

## Progressive Context Levels

| Level | Use when | Required owner-facing material |
|---|---|---|
| L0: evidence only | The route executes an already approved plan, validator, sync, or status check. | Command/result summary, changed state, next action. |
| L1: route/scope brief | The route is local, reversible, and does not change long-lived intent. | Route, scope, explicit non-goals, skip record when relevant. |
| L2: owner judgment brief | The owner must choose, approve, authorize, accept, defer, or sign off. | Decision, options, recommendation, tradeoffs, evidence, consequence of each answer. |
| L3: spec-change packet | The route changes long-lived specs, future agent inputs, capability boundaries, or public contracts. | Spec router, clarification, delta, analyze finding, owner-stop record. |
| L4: rehabilitation packet | Existing specs are stale, conflicting, old-style, or source-of-truth status is unclear. | Inventory, classification, drift findings, owner decisions, repair path. |

## Route-Time Contract

When `cs` or a root router chooses a child skill, it should emit a short route
brief unless the user is already inside a known stage.

Required fields:

```text
Route: {target skill or stage}
Context: {L0-L4}
Reason: {why this route fits}
Not routing to: {nearby flows excluded, if ambiguous}
Escalation: {what would raise the context level}
Next: {what will happen now}
```

The route brief should be short enough for normal use. It becomes L2 only when
the owner must choose between plausible routes.

## Flow-Time Contract

Each `cs-*` skill must state, in its prompt or shared reference, the behavior it
owns:

- default context level;
- safe automatic actions;
- escalation triggers;
- owner-stop checkpoints;
- artifacts it may create;
- artifacts it must not mutate directly;
- how to record an explicit skip;
- which harness scenario proves the behavior.

The same route can stay light or escalate based on evidence. For example,
`cs-feat-ff` starts at L1 for a small UI tweak, but upgrades to L3 if the work
changes a user-visible capability boundary.

## Finish-Time Contract

Before a route reports completion, it must check whether the work created durable
state that future agents or the owner need:

- code or docs changed;
- long-lived specs, guides, decisions, architecture, or skill prompts changed;
- learner/context report is required;
- review packet, analyze pass, or implementation review is required;
- worktree finish, `covered_head`, or inbox state changed;
- follow-up or human-review backlog exists.

Pure status routes can report L0 evidence. Routes that ask the owner to merge,
accept risk, or defer unresolved findings must upgrade to L2 or higher.

## Efficiency Rules

- Default to the lightest level that preserves correctness.
- Do not create requirement deltas for local changes with no capability-boundary
  effect.
- Do not ask clarification questions unless the missing information has
  material impact.
- Do not run analyze passes on every small edit; run them before high-risk
  approval, acceptance, or direct long-lived spec changes.
- Record skips in one or two lines instead of creating a report when the skip is
  low risk.
- Prefer deltas, decisions, and findings over regenerated full documents.
- If the owner asks for more context, restart the checkpoint with a richer brief
  and treat the failed low-context checkpoint as a harness regression seed.

## Route Matrix

| Route | Default level | Required behavior |
|---|---|---|
| `cs` | L1 | Explain route, nearby exclusions when ambiguous, context level, and escalation trigger. |
| `cs-onboard` | L2/L4 | Empty repos can stay L1. Existing docs require inventory, mapping, trusted/stale classification, and owner approval before migration. |
| `cs-goal` | L1/L2 | Grill bounded start/end goals, create `state.yaml` plus bilingual goal/iteration docs, and autonomously iterate. Acceptance conflicts, spec/public-contract changes, repeated blockers, budget exhaustion, or risk acceptance trigger owner-stop. |
| `cs-brainstorm` | L1 -> L2 | Freeform discussion stays light. When the owner accepts a direction or asks for the next step, produce owner decision context. |
| `cs-roadmap` | L2/L3 | Owner brief, scope/non-goals, phases, owner decisions, clarifications, and any spec deltas implied by the roadmap. |
| `cs-feat` | L1 | Stage routing and whether this is design, fast-forward, implementation, or acceptance. Ambiguous route requires a route-choice brief. |
| `cs-feat-design` | L2/L3 | Spec router, selected/excluded specs, clarifications, owner-readable design brief, and req-delta draft when capability boundaries change. |
| `cs-feat-ff` | L1/L3 | Small local changes use scope plus skip record. Capability-boundary changes upgrade to design or req-delta flow. |
| `cs-feat-impl` | L0/L3 | Approved checklist execution needs evidence only. Design/checklist/spec deviation requires spec-change review. |
| `cs-feat-accept` | L3 | Analyze findings, req-delta apply summary, architecture/roadmap backwrite summary, and unresolved owner decisions. |
| `cs-issue` | L1 | Issue route summary: report, analyze, or fix, plus next action. |
| `cs-issue-report` | L1 | Reproduction, expected behavior, impact, environment, and evidence. |
| `cs-issue-analyze` | L2 | Root cause, fix options, tradeoffs, risks, and recommendation. |
| `cs-issue-fix` | L0/L3 | Follow approved analysis. If the bug exposes a wrong spec or capability boundary, produce spec-change review. |
| `cs-refactor` | L2 | Behavior-preserving boundary, scope, risks, rollback/verification, and explicit non-goals. |
| `cs-refactor-ff` | L1/L2 | Small refactors use light scope. Cross-module or risky refactors require refactor decision context. |
| `cs-req` | L3 | Requirement draft/update/backfill needs owner context, routing metadata, and no-free-rewrite constraints. |
| `cs-arch` | L1/L3 | Current-state code facts can use L1. Code/doc/intent conflicts need analyze findings and owner decision. |
| `cs-audit` | L1/L2 | Findings summary and evidence. Choosing what to fix or defer requires triage decision context. |
| `cs-explore` | L1/L2 | Question, evidence read, conclusion, and reuse value. Decision/spec changes upgrade to L2/L3. |
| `cs-decide` | L2/L3 | Decision brief, alternatives, tradeoffs, scope, reversal condition, and affected specs. |
| `cs-learn` | L1 | Trigger, lesson, evidence, and future avoidance rule. |
| `cs-trick` | L1/L2 | Applicability, non-applicability, example, and risk. Project-wide rules upgrade to `cs-decide`. |
| `cs-note` | L1 | Why the note belongs in always-loaded attention, target section, and expected lifetime. |
| `cs-guide` | L1/L2 | Target reader, task scenario, source facts. User-visible behavior changes require owner review. |
| `cs-libdoc` | L1 | Public surface source, signature, example, and evidence. Unclear semantics require clarification before writing docs. |
| `finish-worktree` | L2/L3 | Learner/context report freshness, `covered_head`, inbox state, merge readiness, stale-report, unresolved spec/review gates. |

## Global Escalation Triggers

Upgrade to L2/L3 when any route answers one of these questions:

- Should the owner approve, defer, or choose a direction?
- Which long-lived spec is canonical for this work?
- Does this change user-visible capability, public behavior, or future agent
  instructions?
- Does code disagree with requirement, roadmap, architecture, guide, or decision
  docs?
- Is the agent proposing to compact, reorganize, archive, or rewrite long-lived
  docs?
- Is a human answer being treated as permission to proceed?
- Is finish/merge readiness being asserted?

Stay at L0/L1 when the route only:

- executes an approved checklist;
- runs tests, linters, validators, doctor, inbox, or commit planner;
- applies an already approved delta mechanically;
- reports status without changing owner intent or long-lived docs.

## Required Harness Coverage

Every workflow rule added to this matrix must have a behavior scenario or an
explicit non-goal. Core scenarios:

| Scenario | Expected proof |
|---|---|
| `cs-route-brief-minimal` | A short prompt routes to the correct skill, emits L1 context, and does not create heavy artifacts. |
| `goal-autonomous-iteration-docs` | Bounded goal creates machine state, bilingual goal docs, bilingual iteration docs, and does not ask owner for routine technical choices. |
| `goal-code-edits-use-execution-gate` | Goal-wrapped code edits read execution conventions, run the worktree start gate, and stop before code changes when a linked worktree is required. |
| `route-choice-owner-context` | Ambiguous prompt produces options, tradeoffs, recommendation, and owner stop. |
| `fast-path-stays-light` | Small UI/docs/refactor work records a skip and leaves long-lived specs unchanged. |
| `fast-path-escalates-on-boundary` | A fast path that discovers capability-boundary change upgrades to L3 before spec mutation. |
| `issue-fix-escalates-on-wrong-spec` | A bug fix can proceed locally, but wrong long-lived specs become analyze/delta owner review. |
| `guide-user-contract-review` | User-visible guide or libdoc changes that alter public understanding require L2/L3 context. |
| `finish-inbox-stale-report` | Finish checks learner/context report freshness, `covered_head`, inbox status, stale-report, and merge readiness. |
| `compact-resume-next-action` | A compacted actor recovers route, context level, and next action from artifacts/tools instead of chat. |

Required graders:

- transcript grader for route briefs, owner stops, and skip records;
- trajectory grader for required/forbidden workflow actions;
- artifact grader for context packets, deltas, analyze findings, and inbox
  records;
- repo-state grader for forbidden long-lived doc mutations;
- command grader for doctor, worktree inbox, finish, backlog, and maintainer
  verify output.
