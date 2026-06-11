# Behavior Harness Tool

`agent-behavior-harness.py` is a maintainer-only regression runner. The first
implementation uses a deterministic scripted actor adapter: it verifies fixture
setup, command behavior, artifact shape, trajectory assertions, and repo-state
guards instead of claiming that a live LLM agent has been evaluated.

This is still useful because every workflow rule can gain a small failing
scenario before prompt or tool changes are called stable. Future live-agent
adapters must keep the same result format and graders.

The runner also has an explicit `live-codex` adapter for manual live-agent
trajectory checks. It shells out to `codex exec --json --ephemeral` inside the
fixture repository, captures JSONL events as trace text, and best-effort
extracts tool command trajectories. Live runs are intentionally not part of the
default verifier because they are model- and environment-dependent.

## Run

```bash
python3 codestable-maintainer/tools/agent-behavior-harness.py run \
  --suite critical \
  --actor sterile \
  --json
```

You can run a single scenario:

```bash
python3 codestable-maintainer/tools/agent-behavior-harness.py run \
  --scenario codestable-maintainer/scenarios/critical/feat-design-clarify.yaml \
  --actor sterile \
  --json
```

Passing `--scenario` suppresses the default critical suite unless another
scenario is also passed.

Run the live Codex smoke suite explicitly:

```bash
python3 codestable-maintainer/tools/agent-behavior-harness.py run \
  --suite live \
  --actor live-codex \
  --keep-fixtures \
  --json
```

Set `CODESTABLE_HARNESS_CODEX_BIN=/path/to/codex` to test a specific Codex CLI
binary. Live scenarios should focus on high-risk agent decisions such as
whether the agent ran worktree gates, stopped for review authorization, or
avoided installed-copy edits.

## Scenario Shape

Scenarios live under `codestable-maintainer/scenarios/<suite>/`. They are YAML
files; JSON syntax is valid and keeps parsing deterministic when PyYAML is not
installed.

Important fields:

- `id`: stable scenario id.
- `fixture`: fixture repository builder name.
- `setup.files`: optional files written before actor execution. Paths can use
  `{root}`, `{work}`, or `{source}`.
- `actor.script`: deterministic scripted actions such as `say`, `action`,
  `owner_stop`, `write`, and `run`.
- `expect.transcript`: required text, forbidden text, and owner stops.
  `forbidden_regex` supports Python regular expressions when a substring check
  is too coarse, for example forbidding a wrapper command at the start of a
  line while still allowing text that says the wrapper is rejected.
- `expect.trajectory`: required and forbidden workflow actions.
  `required_contains` and `forbidden_contains` allow substring checks across
  live-agent tool trajectories.
- `expect.runtime`: runtime-level checks. Live Codex timeouts fail by default;
  use `allow_timeout: true` only for parser/diagnostic scenarios that
  intentionally test partial timeout traces.
- `expect.artifacts`: existing/created files and content checks.
- `expect.git`: allowed or forbidden dirty path globs.
- `expect.commands`: command exit, stdout/stderr, and JSON assertions,
  including `contains_item` checks for JSON arrays.
- `expect.external`: hash-based checks for non-repo files under the temporary
  work root, for example installed-copy sentinels.

Path strings may use `{root}` for the fixture repo, `{work}` for the scenario
temporary root, and `{source}` for the CodeStable source checkout containing
the harness.

Live scenarios live under `codestable-maintainer/scenarios/live/`. Their
`actor.prompt` is sent to `codex exec`; optional `actor.timeout_seconds` and
`actor.codex_args` customize the live run.

Live trajectory extraction also emits coarse normalized actions when possible,
including `action:worktree_gate` for `codestable-worktree-gate.py` invocations
and `action:git`, `action:git_commit`, or `action:git_merge` for common git
command forms. Scripted `run` steps use the same normalization, and
`forbidden_actions: ["commit", "merge"]` also blocks those normalized commit or
merge actions. Keep raw substring checks for diagnostics, but prefer normalized
actions for high-risk forbidden behavior.

`sterile`, `compacted`, and `realistic` are actor-mode labels for deterministic
scripted scenarios today. They are useful proxy regressions for tool-level
guardrails under misleading context, but they are not yet a live compaction
eval. Use `live-codex` scenarios when grading actual Codex behavior.

## Critical Coverage

The current critical suite covers:

- route brief stays lightweight;
- ambiguous route choices produce owner context before selecting a canonical
  requirement;
- fast paths stay light for local refactors and small UI tweaks, record a
  lightweight note, and leave long-lived requirements unchanged;
- fast paths that discover capability-boundary changes escalate to L3 before
  mutating specs;
- compacted and realistic-context regressions still re-check repo state before
  trusting older conversation context;
- compacted resume recovers the finish route, context level, and next action
  from worktree inbox artifacts instead of chat;
- long-context noise does not bypass attention reads, spec routing, owner stops,
  or forbidden mutation checks;
- brainstorm convergence writes owner decision context and stops before formal
  spec changes;
- ambiguous spec routing stops for clarification;
- capability-boundary work creates a req delta;
- accept/analyze blocks spec drift;
- issue fixes can proceed locally while wrong long-lived specs escalate to
  analyze/delta owner review instead of silent requirement edits;
- drifted historical specs produce an inventory artifact and owner follow-up
  before cleanup or rewrite;
- long-lived requirements are not freely rewritten without an approved delta or
  owner clarification;
- guide/libdoc updates that change user-visible understanding require owner
  review context before public contract mutation;
- implementation starts only in a linked execution worktree, and a path named
  `.codex/worktrees/...` is not enough by itself;
- completed implementation units require implementation review evidence before
  closeout;
- review authorization is requested before code work when the current thread has
  not already chosen the review path;
- subagent review evidence cannot be forged before current-thread review
  authorization;
- CodeStable maintainer work starts in the source repo, then commits, pushes,
  fresh-clone verifies, and syncs installed copies;
- mature onboarded repositories keep existing `docs/` contracts instead of
  migrating or rewriting them by default;
- capability-status answers distinguish shipped surfaces from planned or
  unverified surfaces;
- handoff context packets carry full working detail while the default response
  stays concise;
- review packets redact secrets;
- verification packets reject blank validation evidence;
- owner-judgment context passes strict sufficiency checks;
- backlog remains visible;
- canceled units do not surface historical follow-up items as current blockers;
- missing unit paths stop with structured JSON findings instead of tracebacks;
- doctor findings from pre-existing lifecycle state stay separate from unrelated
  refresh results;
- finish inbox reports ready-to-merge and stale-report state from another branch
  without auto-merging;
- mixed dirty worktrees are planned into logical commit buckets instead of one
  snapshot commit.

## Verifier Integration

`codestable-maintainer/tools/verify.py` runs the critical scripted suite from a
fresh clone whenever workflow-affecting files change. A CodeStable workflow
prompt or tool change is not stable until this suite passes in `sterile` mode,
and live-agent stability remains a separate manual eval layer until the live
adapter is reliable enough for scheduled runs.
