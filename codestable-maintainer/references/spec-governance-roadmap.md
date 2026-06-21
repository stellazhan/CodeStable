# Spec Governance And Drift Control Roadmap

This roadmap is the L3/L4 spec-facing extension of
`global-route-governance.md`. The global matrix owns route-time behavior for all
`cs` and `cs-*` flows. This file owns the heavier rules for long-lived specs,
requirement deltas, clarifications, analyze passes, and historical drift.

## Owner Brief（中文）

### 这解决什么

这条路线是全局分流治理矩阵的 L3/L4 专项：让 CodeStable 的长期 spec 可以被人类纠偏，而不是只对 agent 有用。它给 brainstorm 收敛后的正式落档、spec routing、clarification、requirement delta、历史 spec 偏移和 acceptance 一致性检查加上 owner 可读的上下文入口。

目标结果是：当 agent 要修改或依赖长期 spec 时，owner 审的是一小段 decision、clarification 或 delta，而不是被迫通读一份重新生成的大文档。

### 这不解决什么

它不让 CodeStable 自动决定产品方向，不自动合并 spec，也不替代 owner 判断。它也不会把旧 spec 整篇重写。历史文档必须先 inventory 和分类；修复只能通过已批准的 clarification、delta、archive marker 或 compaction review 进行。

### 建议阶段

1. Brainstorm 收敛成可执行方向时，先写对应 unit 的 `approval-report.md`。
2. 写 design / roadmap / req 前，先做 spec routing，列出选中和排除的 spec。
3. Design 或 roadmap 批准前，加 clarification gate。
4. 能力边界变化时生成 requirement delta，并在 acceptance 阶段机械合并。
5. 对长期 spec 加 no-free-rewrite 和 compaction-review 规则。
6. 对已经偏移或旧格式的历史 spec 做 rehabilitation。
7. 所有 spec 相关的人类判断 checkpoint 先给审批报告，再收集拍板。
8. 完成前运行只读 analyze pass，捕捉术语、覆盖、decision、architecture 漂移。

### 需要 owner 拍板什么

- 哪些长期 requirement 可以作为 canonical spec。
- 哪类变化足够小，可以跳过 requirement delta。
- 历史 spec 和当前代码冲突时，是修代码、修文档，还是两边都要改。
- 哪些旧 spec 应标记为 current、historical、superseded 或 drift-suspected。
- AI 提议压缩文档时，是否保留了对人重要的细节。
- 任何 judgment checkpoint 是否给足了背景、术语、取舍、后果和证据。

### 如何证明它有效

Behavior harness 必须用 clean / compacted agent 重放原始失败模式。通过标准是：sterile 场景能证明 agent 会生成 `approval-report.md`、执行 spec routing、询问 clarification、生成 delta、避免 forbidden rewrite、在 compact 后恢复 next action，并在 spec drift 未解决时阻止 acceptance 完成。

## Goal

Make CodeStable long-lived specs human-correctable and agent-consumable without
letting agents freely rewrite requirements or silently drift away from owner
intent.

The global route governance matrix defines when a route must escalate into this
roadmap. The harness roadmap proves that clean agents reproduce both the global
route behavior and these spec-specific behaviors.

## Problems Covered

This roadmap covers the failures raised in the owner discussion:

- brainstorm conclusions can be too short for the owner to understand, challenge,
  or approve;
- human judgment checkpoints can be meaningless when CodeStable asks for
  approval, route choices, tradeoff decisions, review sign-off, subagent
  authorization, merge/finish decisions, or interviews before explaining the
  workflow context, terms, tradeoffs, evidence, and why the judgment matters;
- feature specs and checklists can become useful to agents but hard for humans to
  review;
- Q&A from clarify/grill conversations can evaporate in chat instead of becoming
  durable owner decisions;
- agents can forget to update the right requirement document, or update a
  requirement when the work should stay local to a feature;
- multiple requirement documents can overlap or conflict, leaving the next agent
  unsure which one to use;
- long-lived requirement documents can grow too large, while AI compaction or
  "cleanup" can remove details that mattered to humans;
- historical specs may already be drifted, stale, or organized in the old style;
- a workflow can look implemented in a high-context chat while a fresh or
  compacted agent does not reproduce the same behavior.

## Principles

- Long-lived specs are not freeform scratchpads. Agents modify them only through
  owner-visible deltas, clarifications, or explicit rehabilitation actions.
- The global route matrix decides when a workflow is light enough to stay L0/L1
  and when it must escalate into this L3/L4 spec governance path.
- Human review targets changes and decisions, not whole regenerated specs.
- Chat is not the record. Owner decisions must land in artifacts.
- Code is production reality, but not always product intent. Conflicts between
  code and requirement documents require owner judgment.
- A rule is not stable until a clean behavior-harness scenario reproduces it.

## Target Userflow

### 1. Brainstorm To Decision

When a brainstorm converges and the owner must approve proceeding, CodeStable
writes `approval-report.md` before creating formal design, roadmap, or
requirement changes.

Required artifact:

```text
{relevant .codestable unit}/approval-report.md
```

Required sections follow `approval-conventions.md`.

The agent stops for owner approval before formal spec changes unless the owner
has already explicitly approved the same decision in the current turn.

### 1.5 Human Judgment Context Gate

Before CodeStable asks the owner or a human reviewer to judge, approve, choose,
authorize, defer, accept, merge, finish, or answer an interview-style question,
it must write enough context into the relevant unit's `approval-report.md` for
the human to decide meaningfully. A canonical stage report can replace this only
when it already contains decision, options, recommendation, tradeoffs, evidence,
consequence, and next action.

This gate applies to interviews, approval prompts, review sign-offs, route
choices, spec-change decisions, subagent authorization, finish/merge readiness,
and any other CodeStable checkpoint where a human answer changes what happens
next.

Required judgment preface:

- what decision is being made;
- why this question is being asked now;
- definitions for non-obvious terms;
- the background failure or risk this decision addresses;
- the concrete effect of each option;
- the default recommendation and why it is safe;
- what will happen after the owner answers;
- which actions remain non-automatic regardless of the answer.

The agent must not ask shorthand questions such as "Do you accept sterile
actor?" until it has explained what `sterile actor` means, why it matters, and
what accepting it changes.

For multi-question interviews, each decision section should follow the
`approval-report.md` shape. For single approval or judgment checkpoints, use the
same fields compactly inside that report.

If the owner or reviewer says the checkpoint lacks context, CodeStable must
restart with a context brief before collecting the answer. The failed checkpoint
should be treated as a behavior-harness regression seed.

### 2. Spec Router Before Spec Work

Before `cs-feat-design`, `cs-roadmap`, `cs-req update`, or any spec-changing
workflow, CodeStable runs a spec routing pass.

The router must report:

- selected requirement, roadmap, architecture, and decision documents;
- explicitly excluded documents and why they are not in scope;
- whether the task is allowed to skip long-lived requirements;
- whether clarification is required before writing design or deltas.

Long-term routing metadata belongs in `requirements/VISION.md` and individual
requirement frontmatter:

```yaml
applies_when: []
excludes_when: []
related_architecture: []
owner_review_state: unreviewed | clarified | current | drift-suspected
```

### 3. Clarification Gate

Before a design or roadmap is approved, CodeStable scans for meaningful missing
or partial coverage. It asks at most five owner questions and writes each answer
into a durable `## Clarifications` section.

Question categories:

- scope;
- data model;
- UX;
- non-functional constraints;
- integration;
- edge cases;
- lifecycle/ownership;
- terminology;
- completion signal.

Each clarification entry records the question, answer, session date, and the
spec section it anchors.

### 4. Requirement Delta Instead Of Free Rewrite

When a feature changes user-visible capability or boundary, CodeStable creates a
small requirement delta in the feature directory instead of rewriting the whole
requirement.

Required artifact:

```text
.codestable/features/{unit}/{slug}-req-delta.md
```

Required sections:

- ADDED Requirements;
- MODIFIED Requirements;
- REMOVED Requirements;
- Scenarios;
- Owner Decision.

Acceptance applies the delta mechanically during `cs-feat-accept` after owner
approval and records the merge in the requirement change log.

### 5. No-Free-Rewrite Rule

Agents must not freely rewrite long-lived requirement documents to "clean them
up" or "make them shorter".

Allowed edits:

- apply an approved requirement delta;
- append or update `## Clarifications`;
- add routing metadata;
- mark a document historical, superseded, drift-suspected, or current;
- apply an approved compaction review.

Compaction requires a separate review artifact:

```text
.codestable/requirements/{slug}-compaction-review.md
```

It lists what will be kept, moved to appendix, deleted, or replaced, and why.

### 6. Historical Spec Rehabilitation

Old specs are repaired through inventory and owner decisions, not wholesale
rewrite.

Required flow:

1. inventory existing specs;
2. classify each as `current-trusted`, `current-unreviewed`,
   `drift-suspected`, `historical`, `superseded`, or `orphaned`;
3. generate drift findings for conflicts across requirements, design,
   acceptance, architecture, decisions, code, and tests;
4. ask owner questions for conflicts where code and requirement intent disagree;
5. repair through clarification, delta, archive markers, or explicit design
   follow-up.

Required artifact:

```text
.codestable/spec-governance/{YYYY-MM-DD}-{slug}-inventory.md
```

### 7. Analyze Pass

Before accept completes, and before high-risk design approval, CodeStable runs a
read-only consistency pass.

Checks:

- duplicate or conflicting requirements;
- ambiguous terminology;
- missing requirement to checklist coverage;
- checklist items not tied back to design;
- decision documents that conflict with proposed changes;
- architecture current-state mismatch;
- stale or missing clarifications;
- forbidden free rewrites.

The analyze pass reports findings and recommended owner actions. It does not
change files by itself.

## Relationship To Global Route Governance

The context levels, route matrix, route-time contract, flow-time contract,
finish-time contract, skip rules, and route-level harness scenarios are defined
in `global-route-governance.md`.

This roadmap only owns the L3/L4 specialization:

- how a route proves it has crossed from local work into long-lived spec change;
- which spec artifacts are allowed to change;
- how clarifications and requirement deltas are recorded;
- how old or conflicting specs are rehabilitated;
- how analyze findings block, warn, or become owner decisions.

The global matrix must stay the source of truth for whether a lightweight route
can remain L0/L1. This file must not require heavy spec artifacts for small
feature fast paths, local refactors, simple bug fixes, status checks, or docs
updates that do not change capability boundaries or future agent behavior.

## Implementation Plan

Detailed rollout, harness matrix, and definition of done live in
`spec-governance-roadmap-implementation.md`.
