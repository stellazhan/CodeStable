# CodeStable Harness Implementation Plan

## Goal

Turn the current CodeStable process from prompt-only discipline into a small set
of deterministic gates and status tools. The target failure mode is simple:
when an agent says a CodeStable-managed task is done, the repository state,
worktree topology, review evidence, commit scope, follow-up backlog, and
installed CodeStable copy should all be checkable from commands.

This plan solves the issues observed in recent GammaSource, BetaSoul, and
CodeStable maintenance work:

- implementation can happen in the coordinator checkout instead of an execution
  worktree;
- a clean `git status` can hide implementation commits already made on `main`;
- data, logs, code, docs, and migration changes can be packed into one commit;
- subagent review catches real issues, but review packets are prepared manually;
- `needs-human-review`, follow-ups, accepted P2s, and `attention.md` candidates
  can disappear after a final report;
- CodeStable source changes can be pushed while installed global skill copies
  remain stale;
- agents can forget to start from `/Users/john/Code/Github/CodeStable` for
  CodeStable changes.

## Work Package 1: `codestable-doctor`

Implement the source script in CodeStable at
`cs-onboard/tools/codestable-doctor.py`. When CodeStable is onboarded into a
project, the runtime command path must be:

```bash
python .codestable/tools/codestable-doctor.py --root . --json
```

Skills and project docs must reference the runtime `.codestable/tools/...`
path, not the CodeStable source-tree path, unless they are explicitly describing
work inside `/Users/john/Code/Github/CodeStable`.

Responsibilities:

- report active feature, issue, refactor, roadmap, and maintenance units;
- report current branch, default branch, linked worktree status, and whether the
  checkout looks like a coordinator or execution worktree;
- group dirty files into code, tests, docs, migrations, data, logs, CodeStable
  artifacts, and unknown;
- list `needs-human-review`, `Human review required`, unresolved `Follow-up`,
  accepted/deferred P2, and `attention.md` candidate items;
- report missing implementation-review evidence for completed implementation
  units;
- emit one `next_action` string for agents and dashboards.

Required tests:

- empty repo with no CodeStable unit reports `status=idle`;
- planning-only dirty docs report planning-safe;
- dirty `src/` change on `main` reports worktree violation;
- completed feature without `{slug}-implementation-review.md` reports blocked;
- `needs-human-review` appears in JSON output with file and line.

Acceptance:

- the command never mutates files;
- JSON output is stable enough for hooks and future UI display;
- it can explain both dirty-tree and clean-tree blocked states.

## Work Package 2: Worktree Start, Commit, And Recovery Gates

Implement the source script in CodeStable at
`cs-onboard/tools/codestable-worktree-gate.py`. When CodeStable is onboarded
into a project, the runtime command paths must be:

```bash
python .codestable/tools/codestable-worktree-gate.py start --root . --unit <path-or-slug>
python .codestable/tools/codestable-worktree-gate.py commit --root . --unit <path-or-slug>
python .codestable/tools/codestable-worktree-gate.py quarantine --root . --unit <path-or-slug>
```

Start gate:

- allow planning and analysis docs in the coordinator checkout;
- require a non-default linked worktree before implementation paths are edited;
- record a task baseline containing default-branch HEAD, current branch,
  worktree path, unit path, and timestamp;
- allow override only when the unit contains `worktree-override.md` with reason,
  scope, and human approval.

Commit gate:

- fail if staged implementation changes are on `main`;
- fail if default branch has implementation commits after the recorded baseline,
  even when the working tree is clean;
- fail completed implementation units without subagent review evidence unless a
  platform-level self-review fallback is explicitly enabled;
- warn when staged files belong to multiple commit buckets.

Recovery gate:

- default to dry-run output that describes the proposed branch/worktree and file
  moves without mutating anything;
- require `--apply` plus an explicit human-approved override before creating
  branches, creating worktrees, moving files, or altering the index;
- create or name a quarantine branch/worktree for accidental implementation
  changes started in the coordinator checkout only after that approval;
- move only implementation-scope changes into the execution worktree when
  possible;
- leave data/log churn visible for the commit planner instead of hiding it.

Required tests:

- start gate fails on `main` for an implementation unit;
- start gate passes in a linked `codex/...` worktree;
- commit gate catches a clean `main` that contains a post-baseline implementation
  commit;
- override file permits an explicitly approved exception and records the reason;
- quarantine dry-run proposes a recovery plan without mutating the repo;
- quarantine `--apply` is required before branch/worktree creation or file moves;
- quarantine refuses to run when untracked secrets or env files are present.

Acceptance:

- this package directly prevents "task completed outside the worktree";
- it also detects the harder case where the task already committed to `main`.

## Work Package 3: Review Packet Generator

Implement the source script in CodeStable at
`cs-onboard/tools/build-review-packet.py`. When CodeStable is onboarded into a
project, the runtime command path must be:

```bash
python .codestable/tools/build-review-packet.py --root . --unit <path-or-slug> --output /tmp/review.md
```

Responsibilities:

- collect the design/report/analysis doc, checklist state, relevant architecture
  or requirement docs, and current diff;
- include `git diff --stat`, focused source diff, and validation commands/results
  provided by the owner;
- include risk prompts for DB, migrations, concurrency, idempotency,
  crash-resume, provider cost, production writes, and deterministic LLM
  boundary;
- redact `.env`, token-looking values, and local credentials.

Required tests:

- packet includes unit docs and focused diff;
- packet excludes secret-like files and values;
- packet can be used by a subagent without hidden prior context.

Acceptance:

- `cs-feat-impl`, `cs-issue-fix`, and `cs-refactor-ff` can call this before
  subagent review;
- review evidence remains comparable across runs.

## Work Package 4: Commit Planner

Implement the source script in CodeStable at `cs-onboard/tools/plan-commits.py`.
When CodeStable is onboarded into a project, the runtime command path must be:

```bash
python .codestable/tools/plan-commits.py --root . --json
```

Responsibilities:

- classify changed paths into buckets: code/docs/tests, migrations/database docs,
  data, logs/runtime artifacts, CodeStable docs, installed skill deployment, and
  unknown;
- warn when a migration lacks matching database contract docs;
- warn when source code changes lack mapped runbook docs when a project mapping
  is available;
- warn on tracked ignored paths, large files, and changing file sizes that imply
  live writers;
- never stage or commit by itself.

Required tests:

- mixed GammaSource-like dirty tree produces separate code, data, log, and docs
  buckets;
- migration without docs is flagged;
- tracked ignored runtime file is flagged;
- planner output is deterministic and does not mutate files.

Acceptance:

- agents can produce separate logical commits without relying on memory;
- data/log churn no longer gets hidden inside code commits.

## Work Package 5: Human-Review And Follow-Up Backlog

Implement this as part of `codestable-doctor` or as source script
`cs-onboard/tools/codestable-backlog.py`. When CodeStable is onboarded into a
project, the runtime command path for the separate command must be:

```bash
python .codestable/tools/codestable-backlog.py --root . --json
```

Responsibilities:

- scan CodeStable artifacts for `needs-human-review`, `Human review required`,
  `Follow-up`, `Follow-Ups`, accepted/deferred P2, and `attention.md`
  candidates;
- report file, line, unit, severity, and suggested owner action;
- distinguish blocked human decision points from optional future cleanup.

Required tests:

- backlog items survive after acceptance docs are written;
- accepted P2 items are visible until explicitly closed or converted to an issue;
- output includes line numbers when practical.

Acceptance:

- no final report can make unresolved human decisions disappear from the next
  agent's view.

## Work Package 6: CodeStable Maintainer Verification Command

Add a maintainer-only helper:

```bash
python codestable-maintainer/tools/verify.py --branch <branch> --remote origin
```

Responsibilities:

- assert current checkout is `/Users/john/Code/Github/CodeStable` or an approved
  CodeStable source clone;
- assert branch is pushed to remote;
- fresh-clone the branch;
- validate every changed skill with the active skill-creator validator;
- run relevant tests when harness scripts changed;
- enumerate every changed installable unit and diff-check installed copies;
- report non-installed source files as `not installed: N/A`.

Required tests:

- unpushed branch fails;
- fresh clone missing the changed file fails;
- changed skill validates and installs cleanly;
- installed copy mismatch fails;
- README-only source docs are reported as not installed.

Acceptance:

- CodeStable source changes cannot be called complete from only the original
  checkout;
- installed global skill behavior is provably in sync with the pushed source.

## Skill Updates Required

Update these skills after the tools exist:

- `cs-feat-impl`: run worktree start gate before implementation and build review
  packet before subagent review.
- `cs-issue-fix`: same start gate and review packet behavior for fixes.
- `cs-refactor-ff`: keep the flow lightweight, but still run the worktree gate
  and subagent review packet for code edits.
- `cs-feat-ff`: allow fast-forward work, but call out explicit override when the
  user chooses the current checkout.
- `cs-onboard/reference/shared-conventions.md`: document gates as the source of
  truth for worktree and review requirements.
- `cs-onboard/reference/tools.md`: document every new `.codestable/tools/...`
  runtime command, arguments, JSON output shape, and safe usage examples.
- `codestable-maintainer`: replace the manual verify checklist with the new
  `verify.py` command once it exists.

## Implementation Order

### Phase 1: Stop Wrong-Worktree Completion

Build `codestable-doctor.py` and `codestable-worktree-gate.py`.

This phase solves:

- work done in the coordinator checkout;
- clean `git status` hiding post-baseline `main` implementation commits;
- missing review evidence for completed implementation units.

Exit criteria:

- all worktree-gate tests pass;
- implementation skills mention the start/commit gate;
- `cs-onboard/reference/tools.md` documents the runtime `.codestable/tools/...`
  commands;
- a dirty or post-baseline `main` implementation cannot pass the gate.

### Phase 2: Make Review And Commits Mechanical

Build `build-review-packet.py` and `plan-commits.py`.

This phase solves:

- inconsistent subagent review inputs;
- mixed commits containing code, data, logs, docs, or migrations;
- missed project doc-sync warnings when path mappings are available.

Exit criteria:

- reviewer packet can be generated from a real feature/issue/refactor unit;
- commit planner splits a mixed GammaSource-like tree into separate buckets;
- `cs-onboard/reference/tools.md` documents review-packet and commit-planner
  commands with examples;
- skills require packet generation before implementation-review output.

### Phase 3: Preserve Backlog And Verify CodeStable Deployment

Build `codestable-backlog.py` or extend doctor, then build
`codestable-maintainer/tools/verify.py`.

This phase solves:

- human-review and follow-up items disappearing after acceptance;
- stale installed CodeStable skill copies;
- source-only verification without remote/fresh-clone proof.

Exit criteria:

- backlog output lists every unresolved human decision point with file/line;
- maintainer verify fails on unpushed branches and installed-copy mismatch;
- CodeStable source change reports include pushed branch, fresh clone path,
  validator result, install units, and installed-copy diff result.

## Global Acceptance Criteria

The harness is considered effective only when all of these are true:

- An agent cannot complete implementation on `main` without an explicit override
  artifact.
- A clean working tree with implementation commits already made on `main` is
  still detected as blocked.
- A mixed dirty tree produces a commit plan with separate buckets.
- Every completed implementation unit has subagent review evidence or an
  explicit platform fallback.
- Human-review and follow-up backlog items remain visible across turns.
- CodeStable changes are edited in source, pushed, fresh-cloned, validated, and
  installed/diff-checked before being called done.

## Non-Goals

- Do not auto-commit or auto-merge.
- Do not replace human review decisions.
- Do not turn CodeStable into a heavyweight orchestration framework.
- Do not use installed skill copies as the source of truth.
