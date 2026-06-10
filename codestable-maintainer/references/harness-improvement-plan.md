# CodeStable Harness Improvement Plan

## Owner Brief（中文）

### 这解决什么

这条路线把 CodeStable 从“靠提示词自觉执行流程”推进到“可以被工具和干净 agent 回归验证的工作流系统”。它重点解决：

- agent 在主协调 checkout 里直接实现，忘记开 execution worktree；
- `git status` 看起来干净，但实现已经被提交到 `main`；
- code / docs / data / logs / migration 被混进一个提交；
- subagent review、human review、follow-up、attention 候选在对话结束后消失；
- CodeStable 源仓库已改，但本地安装副本仍然旧；
- 当前长上下文里看似实现了流程，换成 fresh / compacted agent 后行为漂移。

### 这不解决什么

它不替 owner 做产品判断，不自动 commit、merge、push，也不把 CodeStable 变成重型 multi-agent 编排系统。它只让“现在处于什么状态、下一步该做什么、是否满足完成门槛”变得可检查。

### 建议阶段

1. Doctor + worktree gate：先防止在错误 checkout 完成实现。
2. Review packet + commit planner：让 review 输入和提交拆分机械化。
3. Backlog + source/install verify：让 human-review debt 和安装漂移可见。
4. Human/subagent context packet：让上下文交接和人审报告完整但不污染默认回答。
5. Finish inbox：让完成的 worktree 在任何分支都能提醒合并/刷新/清理。
6. Agent behavior harness：用 sterile / compacted agent 重放场景，验证 CS 行为是否稳定复现。
7. Spec governance：把文档偏移、人类可读、req delta、clarify 等机制纳入正式 workflow，并用 behavior harness 验证。

### 需要 owner 拍板什么

- 哪些 workflow 行为必须作为硬门槛，哪些先作为 warning。
- 是否接受 sterile actor 作为“流程已稳定”的最低证明。
- 哪些历史失败必须进入 behavior regression suite。
- 哪些操作永远不能自动化，例如 merge、commit、spec rewrite。

### 如何证明它有效

每个阶段都要有 deterministic command 或 behavior scenario 证明。最终标准不是“prompt 写了”，而是 fresh clone、临时安装副本、fixture repo、干净 agent、多次重跑都能得到同样的 artifact、gate 状态和 forbidden mutation 检查结果。

## Purpose

Improve CodeStable from a prompt-led workflow into a lightweight, verifiable
lifecycle harness. The goal is not to automate humans out of the loop. The goal
is to make lifecycle state, review gates, worktree topology, commit scope, and
install verification machine-checkable.

This plan is grounded in recurring GammaSource and BetaSoul failures:

- implementation often starts in the coordinator checkout instead of an
  execution worktree;
- `git status` based checks miss implementation commits already made on `main`;
- large `data/output` and log churn gets mixed with code/docs commits;
- subagent implementation review catches real P1/P2 issues, but review packet
  preparation is manual and inconsistent;
- `needs-human-review`, `Follow-up`, and `attention.md` candidates can disappear
  after an acceptance report;
- CodeStable source changes can look correct while installed skill copies remain
  stale;
- a high-context conversation can make a CodeStable prompt look implemented even
  though a fresh or compacted agent does not reliably reproduce the intended
  workflow;
- long-lived specs can drift, become human-unreadable, or be rewritten by agents
  without a small owner-reviewable change boundary.

## Proposed Capabilities

### 1. `codestable-doctor`

Add a read-only status command:

```bash
.codestable/tools/codestable-doctor.py --json
```

It should report:

- active feature / issue / roadmap units;
- checklist `pending` / `done` / `passed` / `failed` state;
- `needs-human-review` acceptance reports;
- missing or non-subagent implementation reviews;
- dirty tree grouping by code, docs, migrations, data, logs, and CodeStable
  artifacts;
- unresolved `Follow-up`, `attention.md Candidates`, and accepted P2 items;
- next recommended workflow action.

Acceptance:

- A repo with docs-only planning changes is reported as planning-safe.
- A repo with implementation changes on `main` reports a worktree violation.
- A repo with `needs-human-review` does not report workflow complete.
- JSON output is stable enough for Stop hooks or dashboards.

### 2. Worktree Start, Commit, And Recovery Gates

Existing implementation review validation catches some issues at the end. The
worktree rule needs three gates.

#### Start Gate

```bash
.codestable/tools/codestable-worktree-gate.py start --unit <path-or-slug>
```

Rules:

- design / roadmap / planning docs may be edited in the coordinator checkout;
- implementation paths (`src/`, `tests/`, `supabase/migrations/`, scripts, app
  code) require a linked execution worktree;
- overrides require a `worktree-override.md` inside the unit directory with
  reason, scope, and human approval.

#### Commit Gate

```bash
.codestable/tools/codestable-worktree-gate.py commit --unit <path-or-slug>
```

Rules:

- staged implementation changes on `main` fail;
- implementation commits created on `main` after task baseline fail, even when
  the working tree is clean;
- completed implementation units require implementation-review evidence;
- mixed code/data/log/docs scope emits commit planner warnings.

#### Recovery Tool

```bash
.codestable/tools/codestable-worktree-gate.py quarantine --unit <path-or-slug>
```

Purpose:

- move accidental implementation changes from coordinator checkout into a new
  execution worktree;
- keep planning docs in the coordinator checkout when appropriate;
- leave data/log churn for the commit planner instead of hiding it.

Acceptance:

- On `main`, modifying `src/app.py` fails start gate.
- In a linked worktree, the same modification passes.
- A clean `main` with a new implementation commit after baseline still fails
  commit gate.
- `worktree-override.md` is required for explicit override.

### 3. Review Packet Generator

Add:

```bash
.codestable/tools/build-review-packet.py --unit <path-or-slug> --stage quality --output /tmp/review.md
```

It should collect:

- design / report / analysis doc;
- checklist state;
- `git diff --stat`;
- focused source diff;
- validation commands and results provided by the owner;
- risk hints: DB, migration, concurrency, idempotency, crash-resume, provider
  cost, production writes, deterministic LLM boundary.
- stage-specific reviewer mission for `spec`, `quality`, `verification`, or the
  backwards-compatible `implementation` default.

Acceptance:

- A reviewer can use the packet without being given hidden prior conclusions.
- Packet generation does not include secrets or local env files.
- P0/P1/P2 findings can be copied into `{slug}-implementation-review.md`.
- Verification-stage packets require fresh validation evidence.

### 4. Handoff Context Packet And Human Reports

Add:

```bash
.codestable/tools/build-context-packet.py --unit <path-or-slug> --audience handoff --output /tmp/handoff.md
.codestable/tools/build-context-packet.py --unit <path-or-slug> --audience human-reviewer --language zh --output /tmp/human-review.md
.codestable/tools/check-context-sufficiency.py --file /tmp/human-review.md --strict --json
```

It should collect either a compact handoff or an audience-specific report with:

- decided;
- rejected;
- risks;
- files;
- remaining;
- evidence.

Audience report modes are `human-reviewer`, `owner-decision`, `learner`, and
`interviewee`. They use a layered `Decision Brief` -> `Working Context` ->
`Evidence Appendix` structure so human-facing detail lives in an artifact rather
than in the default chat reply.

Acceptance:

- Next-stage agents and human reviewers can read the packet without prior chat
  history.
- The handoff is short enough for human review.
- Chinese human reports can be generated with complete context and evidence
  pointers.
- Strict context checks fail when file or evidence entries are missing, or when
  secret-like text was not redacted before dispatch.
- Secret-like paths and values are redacted.

### 5. Commit Planner

Add:

```bash
.codestable/tools/plan-commits.py --json
```

It should classify dirty paths into suggested commits:

- code/docs/tests feature or fix commit;
- migration + database docs commit;
- `data:` commit for `data/input` and `data/output`;
- tracked crawl artifacts;
- tracked runtime logs;
- pure CodeStable planning docs.

It should warn on:

- live writers (`lsof` / changing file size);
- ignored-but-tracked paths;
- large file risk;
- migration without database contract docs;
- source change without mapped runbook docs.

Acceptance:

- GammaSource-like mixed worktrees produce separate code, docs, data, and log
  buckets.
- The planner never stages or commits by itself.

### 6. Follow-Up And Human-Review Backlog

Extend `codestable-doctor` or add:

```bash
.codestable/tools/codestable-backlog.py --json
```

It should scan CodeStable artifacts for:

- `needs-human-review`;
- `Human review required`;
- `Follow-up` / `Follow-Ups`;
- accepted or deferred P2 findings;
- `attention.md Candidates`;
- requirement / roadmap / architecture backwrite TODOs.

Acceptance:

- Human decision points are visible after the original acceptance turn ends.
- Each backlog item links to the source file and line number when practical.

### 7. CodeStable Source-Push-Clone-Install Verification

Add or document a maintainer-only workflow:

```bash
codestable-maintainer verify --branch <branch>
```

Minimum manual sequence:

1. edit `/Users/john/Code/Github/CodeStable`;
2. run local tests and skill validation;
3. commit and push branch;
4. fresh clone pushed branch;
5. validate from clone;
6. sync installed global skill copy from clone;
7. diff installed copy against clone.

Acceptance:

- A source change cannot be called complete from only the original checkout.
- Installed global skill copy is either diff-clean against the clone or the
  final report says installation was intentionally skipped.

### 8. Agent Behavior Regression Harness

Add a maintainer-only behavior harness that runs CodeStable scenarios in clean
fixture repositories with a fresh agent actor:

```bash
python3 codestable-maintainer/tools/agent-behavior-harness.py run \
  --scenario codestable-maintainer/scenarios/feat-design-clarify.yaml \
  --runs 3 \
  --actor sterile
```

It should evaluate behavior through trace, artifacts, and repository state, not
through a broad "looks good" answer judgment:

- fixture repositories for clean, ambiguous, drifted, and finished-worktree
  states;
- scripted user turns that simulate real CodeStable usage;
- actor modes for `sterile`, `compacted`, and `realistic` contexts;
- transcript checks for required checkpoints and owner stops;
- trajectory checks for required/forbidden workflow actions;
- artifact checks for generated files, frontmatter, sections, and JSON/YAML
  schemas;
- repo-state checks for forbidden mutations and allowed diff scopes;
- command checks for `doctor`, worktree gates, backlog, finish inbox, and
  maintainer verify outputs;
- repeated runs so a single lucky pass is not treated as stability.

Acceptance:

- a fresh no-history actor can reproduce core CodeStable routing behavior from a
  fixture repo and user prompt;
- compact/resume scenarios recover the same `next_action` from artifacts and
  status tools, not from chat memory;
- drifted-spec scenarios produce inventory, clarification, or delta artifacts
  instead of freely rewriting long-lived specs;
- permission-boundary scenarios stop for owner authorization and cannot forge
  subagent review evidence;
- behavior regression failures can be promoted into new scenario YAML files.

### 9. Spec Governance And Drift Control

Add the workflow behavior defined in
`codestable-maintainer/references/spec-governance-roadmap.md`:

- owner decision context after brainstorm convergence;
- spec router before design, roadmap, requirement, or acceptance work;
- clarification gates with durable `## Clarifications` entries;
- requirement deltas instead of whole-document rewrites;
- no-free-rewrite constraints for long-lived specs;
- historical spec rehabilitation through inventory and drift findings;
- read-only analyze pass before high-risk design approval or acceptance.

Acceptance:

- owners review small decision contexts and deltas rather than regenerated
  long-lived specs;
- old specs are classified before migration instead of silently cleaned up;
- requirement updates are mechanically traceable to approved deltas or
  clarifications;
- behavior harness scenarios prove the original drift, routing, compaction, and
  human-review failures are fixed.

## Suggested Roadmap

### Phase 1: Doctor And Worktree Gate

- Add `codestable-doctor.py`.
- Add `codestable-worktree-gate.py`.
- Extend tests for main checkout, linked worktree, override, and post-baseline
  commits.
- Update `cs-feat-impl`, `cs-issue-fix`, `cs-refactor-ff`, and
  `shared-conventions.md` to call the start gate before implementation.

### Phase 2: Review And Commit Harness

- Add `build-review-packet.py`.
- Add `plan-commits.py`.
- Update implementation skills to generate packets before subagent review.
- Update final reporting templates to include commit plan buckets.

### Phase 3: Backlog And Source Install Verification

- Add backlog scanning.
- Add maintainer skill and source-push-clone-install workflow.
- Add README entries and onboarded reference docs.

### Phase 4: Human/Subagent Context Harness

- Extend `build-review-packet.py` with `--stage spec|quality|verification`.
- Add `build-context-packet.py --audience handoff`.
- Update shared conventions and implementation skills with risk-tiered review
  defaults.

### Phase 5: Worktree Finish And Merge Reminders

- Add `codestable-finish-worktree.py`.
- Add `codestable-worktree-inbox.py`.
- Integrate inbox reminders into `codestable-doctor.py`.
- Require a fresh learner report before worktree finish readiness.

### Phase 6: Agent Behavior Regression Harness

- Add scenario YAML fixtures for clean routing, clarify, drifted specs,
  permission boundaries, compact/resume, and finish inbox reminders.
- Add a maintainer-only runner that executes those scenarios with sterile,
  compacted, and realistic actor contexts.
- Add deterministic graders for transcript checkpoints, trajectory actions,
  artifacts, git diff scope, and tool JSON output.
- Extend `codestable-maintainer/tools/verify.py` so behavior regression becomes
  part of CodeStable workflow changes once the runner is stable.

### Phase 7: Spec Governance And Drift Control

- Implement the roadmap in `references/spec-governance-roadmap.md`.
- Update brainstorm, design, roadmap, req, and accept workflows with owner
  context, router, clarification, delta, rehabilitation, and analyze-pass rules.
- Add behavior scenarios for each governance failure mode before calling the
  behavior stable.

## Non-Goals

- Do not turn CodeStable into a multi-agent orchestration framework.
- Do not remove human checkpoints.
- Do not auto-commit or auto-publish from planner tools.
- Do not make installed skill copies the source of truth.
- Do not make LLM-as-judge the primary pass/fail mechanism for lifecycle
  correctness.

## Design Principle

Prompt instructions remain useful, but lifecycle correctness must be checked by
small deterministic tools. Agent behavior must also be checked from clean
scenario replays, because a workflow that only works in a long, high-context
conversation is not stable enough to call implemented.
