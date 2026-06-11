# Live Eval Phase 2 Addendum

## Status

This addendum records the boundary between the completed behavior-harness
roadmap and future live-agent hardening work.

The current stable definition is:

- deterministic critical scenarios pass in `sterile` mode;
- compacted and realistic actor labels are scripted proxy regressions;
- `live-codex` scenarios pass as an explicit manual smoke suite;
- fresh-clone maintainer verification passes and installed copies are synced.

The current stable definition does not require scheduled live evals or true
live compaction evals.

## Current Layer

`codestable-maintainer/tools/verify.py` should continue to run deterministic
critical scenarios from a fresh clone. This is the default verifier because it
is repeatable, cheap enough for maintainer use, and independent of model and
local Codex CLI drift.

`live-codex` remains a manual smoke layer. It is useful for checking high-risk
decisions such as worktree gates, review authorization, source-before-installed
ordering, and maintainer verifier command shape. A live pass is evidence, but
it is not the same kind of evidence as deterministic verifier output.

## Phase 2 Scope

Scheduled live eval and true live compaction eval are future work. Start Phase 2
only when the owner wants to claim that real live agents, not only scripted
proxy actors, are stable across model changes, long contexts, compaction, and
scheduled regression runs.

Phase 2 should add:

- a repeatable scheduler or CI-safe runner for selected live scenarios;
- a true compaction/resume harness where a live actor resumes from artifacts
  without the original chat context;
- drift reporting that separates model nondeterminism from CodeStable workflow
  regressions;
- an explicit promotion rule for deciding when a live behavior is stable enough
  to become a deterministic guardrail or remain manual evidence.

## Non-Goals For Current Stable

- Do not add live scenarios to the default maintainer verifier.
- Do not block source sync or installed-copy sync on live Codex availability.
- Do not call scripted `compacted` actor mode a true live compaction eval.
- Do not treat one successful live smoke run as proof of scheduled stability.

