# Spec Governance Implementation Plan

This file continues `spec-governance-roadmap.md` with rollout details, harness
coverage, and the definition of done.

## Areas Requiring Further Detail

- Artifact schemas for approval reports, clarifications, req deltas,
  compaction reviews, inventory, and analyze reports.
- Owner-stop semantics for spec changes: what must stop for approval, what can
  continue with a recorded default, and how current-turn approval is recognized.
- Skip thresholds for when small UI tweaks, local refactors, or bug fixes do not
  need requirement deltas or roadmap updates.
- Severity model for analyze findings: blocking, warning, deferred backlog, or
  non-goal.
- Canonical conflict policy across code, tests, acceptance, requirements,
  decisions, and architecture.
- Rehabilitation classification criteria for `current-trusted`,
  `current-unreviewed`, `drift-suspected`, `historical`, `superseded`, and
  `orphaned`.
- Compaction safety: how to prove a shortened spec preserves human-important
  detail and where removed detail is archived.
- Language and length budget for owner-facing artifacts.
- Behavior scenario coverage in sterile / compacted agents.

## Skill Integration Roadmap

### SG0: Global Route Governance Dependency

Implement the root protocol in `global-route-governance.md` before treating any
spec-facing update as stable.

Acceptance:

- every routed `cs-*` workflow declares default context level, escalation
  triggers, owner-stop conditions, allowed artifacts, skip-record format,
  finish-time checks, and matching harness scenarios;
- global route scenarios prove small paths stay light and risky paths escalate
  before spec-specific rules run;
- this spec roadmap is invoked only when the global route matrix reaches L3/L4.

### SG1: Approval Report Before Formal Spec Work

Update `cs-brainstorm` so convergence into feature, roadmap, or requirement work
writes `approval-report.md` and stops for approval.

Acceptance:

- brainstorm can remain freeform while exploratory;
- once proceeding needs approval, an owner-readable approval artifact exists;
- the default chat reply stays concise and points to the artifact.

### SG2: Spec Approval Context

Add approval context rules to spec-changing paths in `cs-brainstorm`,
`cs-roadmap`, `cs-feat-design`, `cs-feat-accept`, `cs-req`, `cs-decide`,
`cs-onboard`, and `codestable-maintainer`.

Acceptance:

- any prompt that asks a human to choose, approve, authorize, accept, defer, or
  sign off defines non-obvious terms before asking;
- each checkpoint states why it matters, options or expected answer shape,
  recommendation, evidence, consequences, and next action;
- owner can ask for more context and the agent restarts the checkpoint instead
  of continuing the original low-context flow.

### SG3: Spec Router

Add routing rules and output templates to `cs-feat-design`, `cs-roadmap`,
`cs-req`, and `cs-feat-accept`.

Acceptance:

- selected and excluded specs are visible before edits;
- multiple plausible requirement docs trigger clarification;
- small local changes can explicitly skip requirement deltas.

### SG4: Clarification Gate

Add clarification scanning to `cs-feat-design` and `cs-roadmap` approval paths.

Acceptance:

- at most five high-impact questions;
- answers are appended to `## Clarifications`;
- design/checklist generation does not proceed while blocking clarifications are
  unanswered.

### SG5: Requirement Delta And Mechanical Apply

Add `{slug}-req-delta.md` creation in design/roadmap flows and mechanical apply
in `cs-feat-accept`.

Acceptance:

- capability-boundary changes use deltas;
- small local changes do not create deltas;
- accept updates the target requirement and change log only from an approved
  delta.

### SG6: Historical Spec Rehabilitation

Add a maintainer/onboard path for inventorying and classifying old specs before
new governance rules are enforced.

Acceptance:

- old specs are classified before migration;
- drift findings ask owner whether code, docs, or both need repair;
- no long-lived spec is rewritten without a delta, clarification, archive marker,
  or compaction review.

### SG7: Analyze Pass

Add a read-only analyze pass before design approval and during acceptance.

Acceptance:

- terminology drift, requirement/checklist gaps, and decision conflicts are
  reported;
- the pass never mutates files;
- findings can become backlog items if the owner defers them.

### SG8: Documentation And Tool Surface

Document runtime behavior in `cs-onboard/reference/shared-conventions.md`,
`approval-conventions.md`, `tools.md`, and `tools-context.md` after tools or
prompt flows exist.

Acceptance:

- onboarded projects receive updated conventions;
- project agents know which artifacts are long-lived specs, deltas, historical
  records, approval reports, and auxiliary context packets.

## Behavior Harness Validation Matrix

Every work package above must be paired with behavior scenarios.

| Problem | Scenario | Expected proof |
|---|---|---|
| Global route governance is only described | `cs-route-brief-minimal`, `fast-path-stays-light`, `fast-path-escalates-on-boundary` | Global route scenarios pass before spec-specific scenarios are considered stable. |
| Brainstorm result is too terse to approve | `brainstorm-owner-context` | `approval-report.md` exists and the agent stops before formal spec changes. |
| Human judgment lacks context | `owner-judgment-context` | The approval report defines terms, explains why the judgment matters, states option tradeoffs, shows evidence, and stops. |
| Agent chooses the wrong requirement | `feat-design-clarify` | Spec router lists selected/excluded docs, then asks clarification if ambiguous. |
| Small UI tweak pollutes requirements | `small-ui-no-req-delta` | Requirement files remain unchanged; local feature artifact records the work. |
| Capability boundary changes need owner review | `capability-boundary-req-delta` | A req delta is created and the requirement is not rewritten directly. |
| Old specs are drifted | `drifted-spec-inventory` | Inventory and drift findings are created; no silent cleanup rewrite occurs. |
| AI compaction loses workflow state | `compact-resume-next-action` | A fresh actor recovers next action from artifacts and tools. |
| Long context hides missing implementation | `long-context-noise-routing` | Actor reads attention, runs router, and obeys forbidden mutation checks. |
| AI claims subagent review without authorization | `subagent-permission-boundary` | Actor writes approval report and cannot forge reviewer evidence. |
| Acceptance misses spec drift | `accept-analyze-spec-drift` | Analyze findings block or record owner decisions before accept completes. |

## Definition Of Done

- skill prompts and reference docs define the behavior;
- deterministic validators or artifact schemas exist where practical;
- behavior harness scenarios pass in `sterile` mode for core flows;
- compact/resume scenarios prove state recovery from artifacts, not chat memory;
- every known failure has a regression scenario or explicit non-goal.
