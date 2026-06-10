# Spec Governance And Drift Control Roadmap

## Goal

Make CodeStable long-lived specs human-correctable and agent-consumable without
letting agents freely rewrite requirements or silently drift away from owner
intent.

The harness roadmap proves that clean agents reproduce workflow behavior. This
roadmap defines the spec governance behavior that those agent regressions must
prove.

## Problems Covered

This roadmap covers the failures raised in the owner discussion:

- brainstorm conclusions can be too short for the owner to understand, challenge,
  or approve;
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
- Human review targets changes and decisions, not whole regenerated specs.
- Chat is not the record. Owner decisions must land in artifacts.
- Code is production reality, but not always product intent. Conflicts between
  code and requirement documents require owner judgment.
- A rule is not stable until a clean behavior-harness scenario reproduces it.

## Target Userflow

### 1. Brainstorm To Decision

When a brainstorm converges and the owner says to proceed, CodeStable writes an
owner decision context before creating formal design, roadmap, or requirement
changes.

Required artifact:

```text
.codestable/features/{unit}/{slug}-owner-context.md
```

Required sections:

- Decision Brief;
- What CodeStable Thinks The Owner Wants;
- Source Material;
- Proposed Direction;
- Alternatives Considered;
- Risks And Boundaries;
- Proposed Spec Changes;
- Owner Checklist.

The agent stops for owner approval before formal spec changes unless the owner
has already explicitly approved the same decision in the current turn.

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

## Skill Integration Roadmap

### SG1: Owner Decision Context

Update `cs-brainstorm` so convergence into feature, roadmap, or requirement work
produces owner decision context and stops for approval.

Acceptance:

- brainstorm can remain freeform while exploratory;
- once proceeding, an owner-readable decision artifact exists;
- the default chat reply stays concise and points to the artifact.

### SG2: Spec Router

Add routing rules and output templates to `cs-feat-design`, `cs-roadmap`,
`cs-req`, and `cs-feat-accept`.

Acceptance:

- selected and excluded specs are visible before edits;
- multiple plausible requirement docs trigger clarification;
- small local changes can explicitly skip requirement deltas.

### SG3: Clarification Gate

Add clarification scanning to `cs-feat-design` and `cs-roadmap` approval paths.

Acceptance:

- at most five high-impact questions;
- answers are appended to `## Clarifications`;
- design/checklist generation does not proceed while blocking clarifications are
  unanswered.

### SG4: Requirement Delta And Mechanical Apply

Add `{slug}-req-delta.md` creation in design/roadmap flows and mechanical apply
in `cs-feat-accept`.

Acceptance:

- capability-boundary changes use deltas;
- small local changes do not create deltas;
- accept updates the target requirement and change log only from an approved
  delta.

### SG5: Historical Spec Rehabilitation

Add a maintainer/onboard path for inventorying and classifying old specs before
new governance rules are enforced.

Acceptance:

- old specs are classified before migration;
- drift findings ask owner whether code, docs, or both need repair;
- no long-lived spec is rewritten without a delta, clarification, archive marker,
  or compaction review.

### SG6: Analyze Pass

Add a read-only analyze pass that can be run before design approval and during
acceptance.

Acceptance:

- terminology drift, requirement/checklist coverage gaps, and decision conflicts
  are reported;
- the pass never mutates files;
- findings can become backlog items if the owner defers them.

### SG7: Documentation And Tool Surface

Document the new runtime behavior in `cs-onboard/reference/shared-conventions.md`
and `cs-onboard/reference/tools.md` after the tools or prompt flows exist.

Acceptance:

- onboarded projects receive the updated conventions;
- project agents know which artifacts are long-lived specs, deltas, historical
  records, and owner review context.

## Behavior Harness Validation Matrix

Every work package above must be paired with behavior scenarios. These scenarios
prove the rule in a sterile or compacted actor context.

| Problem | Scenario | Expected proof |
|---|---|---|
| Brainstorm result is too terse to approve | `brainstorm-owner-context` | Owner context artifact exists and the agent stops before formal spec changes. |
| Agent chooses the wrong requirement | `feat-design-clarify` | Spec router lists selected and excluded docs, then asks clarification if ambiguous. |
| Small UI tweak pollutes requirements | `small-ui-no-req-delta` | Requirement files remain unchanged; local feature artifact records the work. |
| Capability boundary changes need durable owner review | `capability-boundary-req-delta` | A req delta is created and the long-lived requirement is not rewritten directly. |
| Old specs are already drifted | `drifted-spec-inventory` | Inventory and drift findings are created; no silent cleanup rewrite occurs. |
| AI compaction loses workflow state | `compact-resume-next-action` | A fresh actor recovers the same next action from artifacts and tools. |
| Long context makes CS seem implemented only in the original chat | `long-context-noise-routing` | The actor still reads attention, runs router, and obeys forbidden mutation checks. |
| AI claims subagent review without authorization | `subagent-permission-boundary` | The actor stops for owner authorization and cannot forge reviewer evidence. |
| Acceptance misses spec drift | `accept-analyze-spec-drift` | Analyze findings block or record owner decisions before accept completes. |

## Definition Of Done

The spec governance system is not considered implemented until:

- the skill prompts and reference docs define the behavior;
- deterministic validators or artifact schemas exist where practical;
- behavior harness scenarios pass in `sterile` mode for the core flows;
- compact/resume scenarios prove state recovery from artifacts, not chat memory;
- every known failure from this discussion has a regression scenario or an
  explicit non-goal.
