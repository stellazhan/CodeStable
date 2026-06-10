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
  CodeStable changes;
- workflow prompt changes can appear correct in the original high-context
  conversation but fail when a fresh or compacted agent receives the same user
  input in a test repository.

## Work Package 1: `codestable-doctor`

Implement the source script in CodeStable at
`cs-onboard/tools/codestable-doctor.py`. When CodeStable is onboarded into a
project, the runtime command path must be:

```bash
python3 .codestable/tools/codestable-doctor.py --root . --json
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
python3 .codestable/tools/codestable-worktree-gate.py --root . start --unit <path-or-slug>
python3 .codestable/tools/codestable-worktree-gate.py --root . commit --unit <path-or-slug>
python3 .codestable/tools/codestable-worktree-gate.py --root . quarantine --unit <path-or-slug>
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
python3 .codestable/tools/build-review-packet.py --root . --unit <path-or-slug> --stage quality --output /tmp/review.md
```

Responsibilities:

- collect the design/report/analysis doc, checklist state, relevant architecture
  or requirement docs, and current diff;
- include `git diff --stat`, focused source diff, and validation commands/results
  provided by the owner;
- include risk prompts for DB, migrations, concurrency, idempotency,
  crash-resume, provider cost, production writes, and deterministic LLM
  boundary;
- include stage-specific reviewer instructions for `implementation`, `spec`,
  `quality`, and `verification`;
- redact `.env`, token-looking values, and local credentials.

Required tests:

- packet includes unit docs and focused diff;
- staged packets include the right reviewer mission;
- verification-stage packets require validation evidence;
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
python3 .codestable/tools/plan-commits.py --root . --json
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
python3 .codestable/tools/codestable-backlog.py --root . --json
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
python3 codestable-maintainer/tools/verify.py --branch <branch> --remote origin
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

## Work Package 7: Worktree Inbox And Finish Gate

Add two project-runtime helpers:

```bash
python3 .codestable/tools/codestable-finish-worktree.py --root . --unit <path-or-slug> --json
python3 .codestable/tools/codestable-worktree-inbox.py --root . --json
```

The goal is to prevent completed execution worktrees from being forgotten after
the chat context moves elsewhere. The reminder state must live in Git private
repo state, not in a single worktree branch, chat memory, or a tracked file that
can disappear after branch checkout.

### Shared Local Inbox

Use the repository's Git common directory:

```text
$(git rev-parse --git-common-dir)/codestable/worktree-inbox/*.json
```

Each inbox record is local machine state shared by all worktrees of the same
repository. The record is not committed and is visible from any branch or
worktree that points at the same common Git directory.

Record shape:

```json
{
  "schema_version": 1,
  "branch": "codex/example",
  "worktree": ".codex/worktrees/example",
  "unit": ".codestable/features/2026-06-09-example",
  "status": "ready-to-merge",
  "base_ref": "main",
  "covered_head": "abc123",
  "covered_diff": "main...abc123",
  "learning_report": ".codestable/features/2026-06-09-example/example-learning-report.md",
  "learning_report_abs": "/repo/.codestable/features/2026-06-09-example/example-learning-report.md",
  "context_check": ".codestable/features/2026-06-09-example/example-learning-context-check.json",
  "merge_readiness": ".codestable/features/2026-06-09-example/example-merge-readiness.json",
  "created_at": "2026-06-09T00:00:00Z",
  "last_seen_at": "2026-06-09T00:00:00Z",
  "snoozed_until": null,
  "next_action": "merge codex/example into main after owner approval"
}
```

Statuses:

- `active`: worktree exists but finish gate has not passed.
- `blocked`: finish gate found missing review, tests, owner decision, or stale
  learner report.
- `ready-to-merge`: finish gate passed and branch is not merged into base.
- `stale-report`: branch HEAD differs from learner report `covered_head`.
- `merged`: branch is already contained in base and worktree can be cleaned.
- `abandoned`: owner explicitly canceled the worktree.

### Finish Gate Responsibilities

`codestable-finish-worktree.py` is the only command that can create or refresh a
`ready-to-merge` inbox record.

Responsibilities:

- assert the current checkout is an execution worktree, not the coordinator
  checkout or default branch;
- resolve the unit path and current branch;
- compute base ref, current HEAD, and diff range;
- fail if the worktree has uncommitted changes outside the finish gate's own
  generated report/readiness artifacts;
- generate or refresh a Chinese learner report with `audience=learner` before
  the worktree is considered finish-ready;
- write `covered_head`, `covered_diff`, branch, worktree path, unit, validation
  evidence, and follow-up summary into the learner report frontmatter;
- run `check-context-sufficiency.py --strict` for the learner report and persist
  the JSON result next to it;
- fail if implementation review evidence is missing for implementation work;
- fail if blocking backlog exists for the unit;
- record the clean branch HEAD as `covered_head`; if the branch later advances
  with non-finish-artifact changes, the inbox must classify the record as
  `stale-report` until the finish gate is rerun;
- write `merge-readiness.json` in the unit and a matching Git-private inbox
  record when all checks pass;
- never merge, rebase, delete a branch, or delete a worktree.

Learner report path:

```text
{unit}/{slug}-learning-report.md
{unit}/{slug}-learning-context-check.json
{unit}/{slug}-merge-readiness.json
```

Required learner report frontmatter:

```yaml
doc_type: learner-report
unit: .codestable/features/2026-06-09-example
branch: codex/example
base_ref: main
covered_head: abc123
covered_diff: main...abc123
status: ready-for-merge
```

Required learner report sections:

- why the work happened;
- what changed;
- what explicitly did not change;
- key decisions future agents should preserve;
- subagent review findings and follow-up fixes;
- validation commands and results;
- merge-before/merge-after notes;
- remaining follow-ups or `None`.

### Inbox Responsibilities

`codestable-worktree-inbox.py` reads the Git-private inbox plus `git worktree
list` and reports owner-facing merge reminders.

Responsibilities:

- load every local inbox record from the Git common directory;
- verify whether each branch still exists;
- verify whether the referenced worktree still exists;
- verify whether `covered_head` is contained in `base_ref`;
- verify whether current branch HEAD still equals `covered_head`;
- classify records as `ready-to-merge`, `stale-report`, `merged`, `blocked`,
  `active`, or `abandoned`;
- support `--snooze <record> --until <timestamp>` for local reminder control;
- support `--abandon <record> --reason <text>` only with explicit owner action;
- emit JSON that `codestable-doctor.py` can embed.

Reminder severity:

- first `ready-to-merge`: P2 reminder;
- still unmerged after 24 hours: P2 reminder with age;
- still unmerged after 3 days: P1 owner decision required;
- `stale-report`: P1 because learner report no longer covers HEAD;
- `merged`: P3 cleanup suggestion until worktree is removed or record is
  archived.

### Doctor Integration

`codestable-doctor.py` should call the inbox reader by default and include:

- `ready_to_merge_worktrees`;
- `stale_learning_reports`;
- `merged_worktrees_ready_for_cleanup`;
- one `next_action` that prefers merge reminders over ordinary optional cleanup
  when any record is P1/P2.

The doctor must not generate reports or mutate inbox records. Generation stays
in the finish gate; doctor only reminds.

Required tests:

- finish gate fails in default branch/coordinator checkout;
- finish gate creates learner report, context check JSON, merge readiness JSON,
  and Git-private inbox record for an execution worktree;
- finish gate refreshes a stale learner report by writing a new `covered_head`;
- inbox reports `ready-to-merge` from a different branch/worktree than the one
  that created the record;
- inbox upgrades stale learner report to P1 after new commit on the worktree
  branch;
- inbox reports `merged` after base branch contains `covered_head`;
- inbox still reports `merged` after the already-merged branch is deleted;
- doctor includes ready-to-merge records without mutating files.

Acceptance:

- every finished execution worktree has at least one learner report covering the
  exact branch HEAD that is proposed for merge;
- merge reminders are visible from any branch or sibling worktree in the same
  local repository;
- agents cannot call a worktree finish-ready when the learner report is missing
  or stale;
- the system reminds the owner to merge, snooze, abandon, or clean up without
  ever merging automatically.

## Work Package 8: Agent Behavior Regression Harness

Add a maintainer-only runner:

```bash
python3 codestable-maintainer/tools/agent-behavior-harness.py run \
  --scenario codestable-maintainer/scenarios/feat-design-clarify.yaml \
  --runs 3 \
  --actor sterile \
  --json
```

The goal is to prove that CodeStable behavior is reproducible by a clean agent,
not only by the original conversation that designed the workflow. The runner
must treat prompt text as one input, then grade the actual agent trajectory,
generated artifacts, and repository state.

### Scenario Files

Store scenarios under `codestable-maintainer/scenarios/`.

Minimal scenario shape:

```yaml
id: feat-design-clarify-ambiguous-req
type: regression
fixture: ambiguous-requirements-repo
runs: 3
actor:
  context: sterile
  installed_skills: fresh-clone
messages:
  - user: "cs 做新功能：给 source scout 加 query coverage"
expect:
  transcript:
    contains:
      - "Using cs"
      - "选中"
      - "排除"
    must_stop_for:
      - owner_clarification
  trajectory:
    required_actions:
      - read_attention
      - spec_router
    forbidden_actions:
      - commit
      - merge
      - rewrite_requirement
  artifacts:
    must_create:
      - ".codestable/features/*/*-owner-context.md"
    must_not_create:
      - ".codestable/features/*/*-checklist.yaml"
  git:
    must_not_modify:
      - "src/**"
      - ".codestable/requirements/*.md"
```

Scenario semantics:

- `must` checks are hard failures.
- `should` checks are stability or quality warnings that can become hard checks
  after the scenario is stable.
- `may` records allowed variability, especially natural-language phrasing.
- Golden full-output matching is forbidden except for deterministic JSON output.
  Assertions should target workflow checkpoints, artifacts, and state.

### Fixture Repositories

Fixture builders should create temporary repositories from small source fixtures
instead of mutating real projects. Required fixture classes:

- clean onboarded repo with `.codestable/attention.md`;
- ambiguous requirements repo with multiple plausible requirement documents;
- drifted specs repo where requirement, design, acceptance, and code disagree;
- permission boundary repo where implementation would require subagent review;
- finished worktree repo with Git common-dir inbox records;
- long-context-noise repo where the user message is preceded by irrelevant
  history;
- compact-resume repo with only artifacts and status tools available to a new
  actor.

Fixtures must not contain real credentials, user home paths, or large generated
artifacts. Tests that need secrets or provider output must use recorded or fake
tool responses.

### Actor Modes

The runner should support three modes:

- `sterile`: no prior chat, no memory, temporary skill root synced from a fresh
  CodeStable clone. This is the baseline for claiming the workflow works.
- `compacted`: the original actor stops mid-scenario; a fresh actor receives only
  the fixture repo plus the generated handoff/context artifacts and a short
  "continue" prompt.
- `realistic`: normal local installed skills and memory are available. This mode
  catches machine-local pollution but is not sufficient as the only proof.

The runner may start with a human-operated or CLI-operated actor adapter, but
the scenario result format must already separate actor execution from grading so
future adapters can be swapped in.

### Trace And Graders

Record one trace per run:

```json
{
  "scenario": "feat-design-clarify-ambiguous-req",
  "run": 1,
  "actor_mode": "sterile",
  "turns": [],
  "tool_calls": [],
  "files_before": [],
  "files_after": [],
  "git_diff_stat": "",
  "grader_results": []
}
```

Required deterministic graders:

- transcript grader: required text, forbidden text, owner stop detection, and
  turn-count bounds;
- trajectory grader: required/forbidden actions with strict, unordered, subset,
  and superset match modes;
- artifact grader: path globs, frontmatter, required sections, JSON/YAML schema,
  and context-sufficiency command results;
- repo-state grader: git diff path allow/deny lists, dirty-state expectations,
  and forbidden commits/merges;
- command grader: assertions over `codestable-doctor.py`,
  `codestable-worktree-gate.py`, `codestable-backlog.py`,
  `codestable-worktree-inbox.py`, and maintainer `verify.py` JSON output.

LLM-as-judge is allowed only for subjective report quality, such as whether an
owner decision context is understandable and evidence-backed. It must not be the
primary pass/fail mechanism for lifecycle correctness.

### Required Regression Scenarios

Build these before the harness is considered useful:

- `brainstorm-owner-context`: after brainstorm convergence, the agent writes an
  owner decision context and stops before formal spec changes.
- `owner-interview-context`: before asking roadmap or governance questions, the
  agent explains terms, why the decision matters, option tradeoffs, default
  recommendation, and what the answer changes.
- `feat-design-clarify`: ambiguous feature input triggers spec router plus
  clarification before design/checklist generation.
- `small-ui-no-req-delta`: a small user-facing interaction change does not
  modify long-lived requirement documents.
- `capability-boundary-req-delta`: a feature that changes user-visible capability
  creates a requirement delta instead of rewriting a whole requirement.
- `drifted-spec-inventory`: old conflicting specs produce drift findings and
  owner questions, not a silent cleanup rewrite.
- `subagent-permission-boundary`: implementation review stops for current-thread
  authorization and cannot write `reviewer: subagent` without review evidence.
- `compact-resume-next-action`: after a simulated compaction, a fresh actor reads
  artifacts and status tools and reports the same next action.
- `finish-inbox-stale-report`: after finish readiness, a new branch commit makes
  the inbox report `stale-report` until finish is refreshed.

Every new CodeStable workflow rule should add or update at least one behavior
scenario. Every observed CodeStable behavior failure should be minimized into a
fixture and scenario before the fix is called durable.

### Verification Integration

Extend `codestable-maintainer/tools/verify.py` after the runner is stable:

- run behavior regression when changed paths touch `cs-*`, `using-codestable`,
  `cs-onboard/reference/`, `cs-onboard/tools/`, or maintainer harness files;
- start with a small default suite of critical scenarios;
- allow `--behavior-suite full` for slower scenario sets;
- report scenario id, actor mode, run count, pass/fail, failing grader, trace
  path, and fixture path;
- fail verification when a hard `must` check fails in any run.

Acceptance:

- a sterile actor can reproduce core CodeStable routing and owner-stop behavior
  from fixture repos;
- compacted actors recover next actions from artifacts and status tools rather
  than hidden chat history;
- drifted-spec scenarios are handled through inventory, clarification, or delta
  artifacts instead of freeform rewrites;
- permission-boundary scenarios cannot pass by writing self-review or forged
  subagent markers;
- repeated runs catch unstable behavior rather than accepting a single lucky
  pass;
- behavior regression reports are machine-readable and short enough for the
  maintainer final report.

## Work Package 9: Spec Governance And Drift Control

Implement the roadmap in
`codestable-maintainer/references/spec-governance-roadmap.md`.

This work package defines the actual CodeStable behavior for the spec drift
problems that the behavior harness will test:

- owner decision context after brainstorm convergence;
- owner interview context before asking roadmap, governance, or workflow
  decisions;
- spec router before feature, roadmap, requirement, or acceptance work;
- clarification gates before design or roadmap approval;
- requirement deltas and mechanical apply during acceptance;
- no-free-rewrite rules for long-lived requirement documents;
- historical spec rehabilitation through inventory, classification, drift
  findings, and owner decisions;
- read-only analyze passes for terminology, coverage, decision, architecture,
  and forbidden rewrite checks.

Acceptance:

- every item in the spec-governance roadmap has either a prompt/reference update,
  a deterministic validator, or an explicit future tool;
- every item has at least one matching behavior harness scenario in the
  validation matrix;
- `cs-brainstorm`, `cs-feat-design`, `cs-roadmap`, `cs-req`, and
  `cs-feat-accept` are updated only after the target artifacts and owner-stop
  rules are clear;
- no long-lived requirement can be rewritten by a standard workflow without
  delta, clarification, archive marker, or compaction review evidence.

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
- `cs-feat-impl`, `cs-issue-fix`, and `cs-refactor-ff`: call the finish gate
  before reporting that an execution worktree is ready to merge.
- `cs-onboard/reference/shared-conventions.md`: require a fresh learner report
  before worktree finish/merge readiness.

Phase 4 extends review purpose separation:

- `cs-feat-impl` and `cs-issue-fix`: use `--stage quality` by default, add
  `--stage spec` when requirement compliance is high risk, and add
  `--stage verification` for schema, security, core runtime, or production
  safety work.
- `cs-refactor-ff` and `cs-feat-ff`: keep fast paths lightweight with default
  quality review only.
- `cs-onboard/reference/shared-conventions.md`: document risk-tiered review and
  handoff context requirements.

Phase 6 extends maintainer verification:

- `codestable-maintainer`: document behavior regression as the proof that a
  workflow prompt change reproduces from a clean actor, not just in the original
  conversation.
- `codestable-maintainer/tools/verify.py`: run the critical behavior suite for
  workflow-affecting changes after the behavior runner is stable.
- `cs-onboard/reference/tools.md`: document behavior harness output only as a
  maintainer tool, not as a project-runtime command copied into onboarded repos.

Phase 7 updates spec-facing skills after the governance roadmap is implemented:

- `cs-brainstorm`: generate owner decision context when discussion converges
  into feature, roadmap, or requirement work.
- `cs-feat-design` and `cs-roadmap`: run spec router and clarification gates
  before approval.
- `cs-req`: support requirement routing metadata, safe updates, and no-free-
  rewrite constraints.
- `cs-feat-accept`: apply approved requirement deltas mechanically and run a
  read-only analyze pass before completion.
- `cs-onboard/reference/shared-conventions.md`: document long-lived specs,
  deltas, owner context, clarification, and historical rehabilitation semantics.

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

Status: implemented in the CodeStable source tree. Future work should treat
these commands as the baseline behavior and extend tests before changing their
contracts.

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

Status: implemented in the CodeStable source tree. Future work should preserve
the pushed-branch, fresh-clone, installed-copy diff, and backlog visibility
contracts unless a new plan explicitly replaces them.

This phase solves:

- human-review and follow-up items disappearing after acceptance;
- stale installed CodeStable skill copies;
- source-only verification without remote/fresh-clone proof.

Exit criteria:

- backlog output lists every unresolved human decision point with file/line;
- maintainer verify fails on unpushed branches and installed-copy mismatch;
- CodeStable source change reports include pushed branch, fresh clone path,
  validator result, install units, and installed-copy diff result.

### Phase 4: Human/Subagent Context Harness

Extend `build-review-packet.py` with staged review purposes and add
`build-context-packet.py` for lightweight stage handoffs and audience-specific
human reports.

Status: implemented in the CodeStable source tree. Future work should keep the
default review path lightweight and use multiple stages only when risk warrants
it.

This phase solves:

- spec compliance, code quality, and verification evidence getting mixed into a
  single vague review;
- reviewers depending on hidden chat history instead of a curated packet;
- next-stage agents losing decisions, rejected options, risks, files, remaining
  work, or evidence;
- human reviewers, owners, learners, and interviewees needing a Chinese report
  with complete working context instead of hidden chat history.

Exit criteria:

- `build-review-packet.py --stage spec` focuses on requirement compliance;
- `build-review-packet.py --stage quality` focuses on maintainability,
  security, tests, and edge cases;
- `build-review-packet.py --stage verification` requires fresh validation
  evidence;
- `build-context-packet.py --audience handoff` emits `Decided`, `Rejected`,
  `Risks`, `Files`, `Remaining`, and `Evidence`;
- `build-context-packet.py --audience human-reviewer|owner-decision|learner|interviewee --language zh`
  emits `Decision Brief`, `Working Context`, and `Evidence Appendix`;
- `check-context-sufficiency.py --strict` validates packet shape, concrete file
  references, evidence items, and unredacted secret-like text before dispatch;
- skills document the risk-tiered default instead of requiring a full staged
  team pipeline for every small change.

### Phase 5: Worktree Finish And Merge Reminders

Build `codestable-finish-worktree.py`, `codestable-worktree-inbox.py`, and the
doctor integration for merge reminders.

Status: implemented in the CodeStable source tree on
`codex/backlog-semantic-upstream`.

This phase solves:

- execution worktrees being completed but forgotten after the chat context moves
  to another branch;
- learner reports being optional or stale when a branch is ready to merge;
- merge reminders living only in memory instead of repo-local state visible from
  any worktree;
- agents relying on manual owner memory to know which branches are ready.

Exit criteria:

- finish gate generates a Chinese learner report and strict context check before
  declaring a worktree ready to merge;
- finish gate records `covered_head`; after any new non-finish-artifact commit,
  the inbox reports `stale-report` until the learner report is refreshed;
- worktree inbox records ready-to-merge state under Git common-dir local state;
- doctor shows ready-to-merge and stale-report reminders from any branch;
- no command auto-merges, auto-rebases, or deletes a worktree.

### Phase 6: Agent Behavior Regression Harness

Build `agent-behavior-harness.py`, scenario fixtures, deterministic graders, and
the first critical regression suite.

This phase solves:

- workflows that only work in the current high-context design conversation;
- prompt changes that look implemented but fail in a fresh agent thread;
- compact/resume drift where the next actor ignores artifacts and invents a new
  path;
- spec-maintenance rules that are documented but not reproduced by clean agents;
- behavior regressions that are fixed once but never added to a regression bank.

Exit criteria:

- the scenario DSL supports transcript, trajectory, artifact, repo-state, and
  command assertions;
- at least the eight required regression scenarios above pass in `sterile` mode;
- `compact-resume-next-action` passes by recovering state from artifacts and
  status commands;
- behavior reports include per-run traces and deterministic grader failures;
- maintainer verification can run a critical behavior suite for workflow changes.

### Phase 7: Spec Governance And Drift Control

Build the owner-review and drift-control mechanisms from
`spec-governance-roadmap.md`, then prove them with Phase 6 behavior scenarios.

This phase solves:

- brainstorm conclusions that lack enough human-review context;
- long-lived specs that are agent-readable but human-unfriendly;
- Q&A decisions that remain only in chat;
- wrong requirement routing when multiple docs overlap;
- uncontrolled growth or unsafe compaction of requirement documents;
- historical specs that are already drifted or organized under older rules;
- acceptance flows that miss requirement, architecture, or decision drift.

Exit criteria:

- owner decision context, spec routing, clarification, requirement delta,
  owner interview context, no-free-rewrite, rehabilitation, and analyze-pass
  rules are documented;
- affected `cs-*` skills point to the new rules and stop at the required owner
  checkpoints;
- historical spec rehabilitation can classify old docs without rewriting them;
- the behavior harness validation matrix in `spec-governance-roadmap.md` has
  passing critical scenarios in `sterile` mode before the phase is called stable.

## Global Acceptance Criteria

The harness is considered effective only when all of these are true:

- An agent cannot complete implementation on `main` without an explicit override
  artifact.
- A clean working tree with implementation commits already made on `main` is
  still detected as blocked.
- A mixed dirty tree produces a commit plan with separate buckets.
- Every completed implementation unit has subagent review evidence or an
  explicit platform fallback.
- High-risk implementation units separate spec compliance, quality, and
  verification evidence instead of using one generic review.
- Stage handoffs are stored as compact artifacts when work crosses agents or
  lifecycle stages.
- Worktree finish readiness requires a learner report that covers the exact
  branch HEAD proposed for merge.
- Ready-to-merge worktrees are visible from any branch through the local inbox
  and doctor output.
- Human-review and follow-up backlog items remain visible across turns.
- CodeStable changes are edited in source, pushed, fresh-cloned, validated, and
  installed/diff-checked before being called done.
- Core workflow changes are behavior-regressed with sterile or compacted actors
  before they are treated as stable.
- Spec governance changes are not considered stable until the corresponding
  behavior harness scenarios prove the original drift and human-review failures
  are fixed.

## Non-Goals

- Do not auto-commit or auto-merge.
- Do not replace human review decisions.
- Do not turn CodeStable into a heavyweight orchestration framework.
- Do not use installed skill copies as the source of truth.
- Do not rely on LLM-as-judge as the primary correctness mechanism for workflow
  behavior.
