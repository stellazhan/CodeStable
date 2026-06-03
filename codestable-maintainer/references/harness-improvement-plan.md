# CodeStable Harness Improvement Plan

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
  stale.

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
.codestable/tools/build-review-packet.py --unit <path-or-slug> --output /tmp/review.md
```

It should collect:

- design / report / analysis doc;
- checklist state;
- `git diff --stat`;
- focused source diff;
- validation commands and results provided by the owner;
- risk hints: DB, migration, concurrency, idempotency, crash-resume, provider
  cost, production writes, deterministic LLM boundary.

Acceptance:

- A reviewer can use the packet without being given hidden prior conclusions.
- Packet generation does not include secrets or local env files.
- P0/P1/P2 findings can be copied into `{slug}-implementation-review.md`.

### 4. Commit Planner

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

### 5. Follow-Up And Human-Review Backlog

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

### 6. CodeStable Source-Push-Clone-Install Verification

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

## Non-Goals

- Do not turn CodeStable into a multi-agent orchestration framework.
- Do not remove human checkpoints.
- Do not auto-commit or auto-publish from planner tools.
- Do not make installed skill copies the source of truth.

## Design Principle

Prompt instructions remain useful, but lifecycle correctness must be checked by
small deterministic tools. The harness should make the correct state obvious
before the agent says "done".
