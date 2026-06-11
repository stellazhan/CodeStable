# Behavior Harness Tool

`agent-behavior-harness.py` is a maintainer-only regression runner. The first
implementation uses a deterministic scripted actor adapter: it verifies fixture
setup, command behavior, artifact shape, trajectory assertions, and repo-state
guards instead of claiming that a live LLM agent has been evaluated.

This is still useful because every workflow rule can gain a small failing
scenario before prompt or tool changes are called stable. Future live-agent
adapters must keep the same result format and graders.

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

## Scenario Shape

Scenarios live under `codestable-maintainer/scenarios/<suite>/`. They are YAML
files; JSON syntax is valid and keeps parsing deterministic when PyYAML is not
installed.

Important fields:

- `id`: stable scenario id.
- `fixture`: fixture repository builder name.
- `actor.script`: deterministic scripted actions such as `say`, `action`,
  `owner_stop`, `write`, and `run`.
- `expect.transcript`: required text, forbidden text, and owner stops.
- `expect.trajectory`: required and forbidden workflow actions.
- `expect.artifacts`: created files and content checks.
- `expect.git`: allowed or forbidden dirty path globs.
- `expect.commands`: command exit, stdout, and JSON assertions.

## Critical Coverage

The current critical suite covers:

- route brief stays lightweight;
- ambiguous spec routing stops for clarification;
- capability-boundary work creates a req delta;
- accept/analyze blocks spec drift;
- review packets redact secrets;
- owner-judgment context passes strict sufficiency checks;
- backlog remains visible;
- finish inbox reports ready-to-merge state.

## Verifier Integration

`codestable-maintainer/tools/verify.py` runs the critical scripted suite from a
fresh clone whenever workflow-affecting files change. A CodeStable workflow
prompt or tool change is not stable until this suite passes in `sterile` mode,
and live-agent stability remains a separate future adapter layer.
