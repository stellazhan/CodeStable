from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "cs-onboard/tools"
MAINTAINER_TOOLS_DIR = ROOT / "codestable-maintainer/tools"
sys.path.insert(0, str(TOOLS_DIR))


def load_tool(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


spec_governance = load_tool("codestable_spec_governance_for_tests", TOOLS_DIR / "codestable-spec-governance.py")
behavior_harness = load_tool("agent_behavior_harness_for_tests", MAINTAINER_TOOLS_DIR / "agent-behavior-harness.py")


CRITICAL_SCENARIO_IDS = {
    "accept-analyze-spec-drift",
    "backlog-canceled-not-blocker",
    "backlog-visible",
    "blank-validation-rejected",
    "brainstorm-owner-context",
    "capability-boundary-req-delta",
    "capability-status-answer",
    "compact-resume-next-action",
    "compacted-worktree-start-gate",
    "cs-route-brief-minimal",
    "doctor-preexisting-findings-separated",
    "drifted-spec-inventory",
    "fast-path-escalates-on-boundary",
    "fast-path-stays-light",
    "finish-inbox-cross-branch-report",
    "feat-design-clarify",
    "finish-inbox-ready",
    "finish-inbox-stale-report",
    "guide-user-contract-review",
    "handoff-context-packet",
    "implementation-review-required",
    "issue-fix-escalates-on-wrong-spec",
    "long-context-noise-routing",
    "maintainer-source-before-installed",
    "maintainer-verify-sync-required",
    "mature-onboard-no-doc-migration",
    "missing-unit-path-blocked",
    "mixed-dirty-tree-commit-plan",
    "no-match-owner-stop",
    "owner-judgment-context",
    "path-named-worktree-not-linked",
    "realistic-spec-no-free-rewrite",
    "review-authorization-before-code",
    "review-packet-redacts-secrets",
    "route-choice-owner-context",
    "small-ui-no-req-delta",
    "spec-no-free-rewrite",
    "subagent-permission-boundary",
    "worktree-start-gate-linked-pass",
    "worktree-start-gate-main-stop",
}


def run(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    run(repo, "init", "-b", "main")
    run(repo, "config", "user.email", "test@example.com")
    run(repo, "config", "user.name", "Test User")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    run(repo, "add", "README.md")
    run(repo, "commit", "-m", "init")
    return repo


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def add_spec_fixture(repo: Path) -> Path:
    write_file(repo / ".codestable/attention.md", "# Attention\n")
    write_file(
        repo / ".codestable/requirements/source-discovery.md",
        "---\n"
        "slug: source-discovery\n"
        "status: current\n"
        "applies_when:\n"
        "  - source discovery\n"
        "  - crawl preflight\n"
        "excludes_when:\n"
        "  - frontend-only display tweak\n"
        "owner_review_state: clarified\n"
        "---\n\n"
        "# Source Discovery\n",
    )
    write_file(
        repo / ".codestable/requirements/source-query-coverage.md",
        "---\n"
        "slug: source-query-coverage\n"
        "status: current\n"
        "applies_when:\n"
        "  - source discovery\n"
        "  - evidence coverage\n"
        "  - crawl preflight\n"
        "owner_review_state: clarified\n"
        "---\n\n"
        "# Source Query Coverage\n",
    )
    unit = repo / ".codestable/features/2026-06-10-source-query-coverage"
    write_file(
        unit / "source-query-coverage-design.md",
        "---\n"
        "doc_type: feature-design\n"
        "feature: source-query-coverage\n"
        "requirement: source-discovery\n"
        "status: approved\n"
        "---\n\n"
        "# Design\n\n"
        "capability_boundary: changed\n",
    )
    return unit


def test_spec_router_selects_and_excludes_requirement_docs(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    add_spec_fixture(repo)

    routed = spec_governance.route_specs(repo, "source scout query coverage before crawl")
    skipped = spec_governance.route_specs(repo, "frontend-only display tweak")

    assert routed["ok"]
    assert len(routed["selected_specs"]) == 2
    assert routed["clarification_required"] is True
    assert skipped["allowed_to_skip_requirement_delta"] is True
    assert skipped["excluded_specs"]


def test_spec_router_no_match_requires_owner_clarification(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    add_spec_fixture(repo)

    routed = spec_governance.route_specs(repo, "add billing invoice export")
    small_unmatched = spec_governance.route_specs(repo, "small billing invoice export")

    assert routed["selected_specs"] == []
    assert routed["clarification_required"] is True
    assert routed["allowed_to_skip_requirement_delta"] is False
    assert "Ask owner" in routed["next_action"]
    assert small_unmatched["selected_specs"] == []
    assert small_unmatched["clarification_required"] is True
    assert small_unmatched["allowed_to_skip_requirement_delta"] is False


def test_inventory_treats_old_current_spec_without_owner_review_as_unreviewed(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write_file(
        repo / ".codestable/requirements/legacy-current.md",
        "---\nslug: legacy-current\nstatus: current\n---\n\n# Legacy Current\n",
    )

    payload = spec_governance.inventory(repo)

    assert payload["items"][0]["classification"] == "current-unreviewed"
    assert payload["counts"]["current-unreviewed"] == 1


def test_inventory_can_write_human_readable_artifact(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write_file(
        repo / ".codestable/requirements/drifted.md",
        "---\nslug: drifted\nstatus: current\nowner_review_state: drift-suspected\n---\n\n# Drifted\n",
    )

    payload = spec_governance.write_inventory(repo, ".codestable/spec-governance/inventory.md")
    second = spec_governance.write_inventory(repo, ".codestable/spec-governance/inventory.md")
    text = (repo / ".codestable/spec-governance/inventory.md").read_text(encoding="utf-8")

    assert payload["ok"]
    assert payload["path"] == ".codestable/spec-governance/inventory.md"
    assert payload["changed"] is True
    assert second["changed"] is False
    assert payload["counts"]["drift-suspected"] == 1
    assert "doc_type: spec-governance-inventory" in text
    assert "drift-suspected" in text
    assert "Owner Follow-Up" in text


def test_requirement_delta_allows_analyze_to_pass_without_rewriting_requirement(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    add_spec_fixture(repo)
    run(repo, "add", ".")
    run(repo, "commit", "-m", "add spec fixture")

    delta = spec_governance.create_delta(
        repo,
        ".codestable/features/2026-06-10-source-query-coverage",
        "source-discovery",
        ["The system records query intent coverage before crawl."],
        [],
        [],
        ["source scout records coverage gap"],
        "approved",
    )
    analysis = spec_governance.analyze(repo, ".codestable/features/2026-06-10-source-query-coverage")

    assert delta["ok"]
    assert delta["path"].endswith("source-query-coverage-req-delta.md")
    assert analysis["ok"]
    assert analysis["findings"] == []
    assert run(repo, "status", "--porcelain").stdout.strip().startswith("?? .codestable/features")


def test_analyze_blocks_missing_delta_and_dirty_requirement_rewrite(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    add_spec_fixture(repo)
    run(repo, "add", ".")
    run(repo, "commit", "-m", "add spec fixture")
    write_file(repo / ".codestable/requirements/source-discovery.md", "# AI rewrite without delta\n")

    analysis = spec_governance.analyze(repo, ".codestable/features/2026-06-10-source-query-coverage")

    codes = {finding["code"] for finding in analysis["findings"]}
    assert analysis["ok"] is False
    assert "missing_approved_req_delta" in codes
    assert "forbidden_requirement_rewrite" in codes


def test_record_clarification_is_idempotent(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    add_spec_fixture(repo)
    target = ".codestable/requirements/source-discovery.md"

    first = spec_governance.record_clarification(repo, target, "What is covered?", "Intent gaps.", "RQ-1")
    second = spec_governance.record_clarification(repo, target, "What is covered?", "Intent gaps.", "RQ-1")
    text = (repo / target).read_text(encoding="utf-8")

    assert first["changed"] is True
    assert second["changed"] is False
    assert text.count("What is covered?") == 1


def test_behavior_harness_runs_critical_suite() -> None:
    paths = sorted((ROOT / "codestable-maintainer/scenarios/critical").glob("*.yaml"))

    payload = behavior_harness.run_scenarios(paths, "sterile", 1)

    assert payload["ok"], payload
    assert {result["scenario"] for result in payload["results"]} == CRITICAL_SCENARIO_IDS
    assert payload["scenario_count"] == len(CRITICAL_SCENARIO_IDS)
    assert payload["run_count"] == payload["scenario_count"]
    assert all(result["repo"] is None for result in payload["results"])
    assert all(result["actor_adapter"] == "scripted" for result in payload["results"])


def test_behavior_harness_scenario_path_suppresses_default_suite() -> None:
    class Args:
        scenario = ["codestable-maintainer/scenarios/critical/cs-route-brief-minimal.yaml"]
        suite = "critical"

    paths = behavior_harness.scenario_paths(Args)

    assert [path.name for path in paths] == ["cs-route-brief-minimal.yaml"]


def test_behavior_harness_runs_context_mode_regressions() -> None:
    compacted = behavior_harness.run_scenarios(
        [ROOT / "codestable-maintainer/scenarios/critical/compacted-worktree-start-gate.yaml"],
        "compacted",
        1,
    )
    realistic = behavior_harness.run_scenarios(
        [ROOT / "codestable-maintainer/scenarios/critical/realistic-spec-no-free-rewrite.yaml"],
        "realistic",
        1,
    )

    assert compacted["ok"], compacted
    assert realistic["ok"], realistic
    assert compacted["results"][0]["actor_mode"] == "compacted"
    assert realistic["results"][0]["actor_mode"] == "realistic"


def test_behavior_harness_live_codex_actor_uses_jsonl_trace(tmp_path: Path, monkeypatch) -> None:
    fake_codex = tmp_path / "codex"
    argv_path = tmp_path / "argv.json"
    fake_codex.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import os\n"
        "import sys\n"
        "with open(os.environ['CODESTABLE_FAKE_CODEX_ARGV_PATH'], 'w', encoding='utf-8') as fh:\n"
        "    json.dump(sys.argv, fh)\n"
        "print(json.dumps({'type': 'function_call', 'name': 'shell', 'cmd': ['python3', '.codestable/tools/codestable-worktree-gate.py', '--root', '.', '--json', 'start']}))\n"
        "print(json.dumps({'type': 'message', 'text': 'OWNER STOP: linked_worktree_required'}))\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    monkeypatch.setenv("CODESTABLE_HARNESS_CODEX_BIN", fake_codex.as_posix())
    monkeypatch.setenv("CODESTABLE_FAKE_CODEX_ARGV_PATH", argv_path.as_posix())
    scenario_path = tmp_path / "live.yaml"
    prompt = "Implement the demo safely."
    scenario_path.write_text(
        json.dumps(
            {
                "id": "live-fake",
                "fixture": "worktree-start-required-repo",
                "actor": {
                    "prompt": prompt,
                    "codex_args": ["--profile", "live-harness-test"],
                },
                "expect": {
                    "transcript": {"contains": ["linked_worktree_required"]},
                    "trajectory": {
                        "required_actions": ["codex_exec"],
                        "required_contains": ["codestable-worktree-gate.py"],
                    },
                    "git": {"must_not_modify": ["**"]},
                },
            }
        ),
        encoding="utf-8",
    )

    payload = behavior_harness.run_scenarios([scenario_path], "live-codex", 1)

    assert payload["ok"], payload
    result = payload["results"][0]
    assert result["actor_adapter"] == "live-codex"
    assert result["trajectory"][0] == "codex_exec"
    assert any("codestable-worktree-gate.py" in item for item in result["trajectory"])
    argv = json.loads(argv_path.read_text(encoding="utf-8"))
    assert argv[:8] == [
        fake_codex.as_posix(),
        "--ask-for-approval",
        "never",
        "exec",
        "--json",
        "--ephemeral",
        "--sandbox",
        "workspace-write",
    ]
    assert argv[-3:] == ["--profile", "live-harness-test", prompt]


def test_behavior_harness_live_transcript_regex_handles_nested_item_text(tmp_path: Path, monkeypatch) -> None:
    fake_codex = tmp_path / "codex"
    fake_codex.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "print(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Do not use codestable-maintainer verify as a wrapper.\\nUse python3 codestable-maintainer/tools/verify.py --repo . --branch main --remote origin --installed-root /Users/john/.agents/skills --sync-installed --json'}}))\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    monkeypatch.setenv("CODESTABLE_HARNESS_CODEX_BIN", fake_codex.as_posix())
    scenario_path = tmp_path / "live-regex.yaml"
    scenario_path.write_text(
        json.dumps(
            {
                "id": "live-regex",
                "fixture": "clean-onboarded-repo",
                "actor": {"prompt": "show verifier"},
                "expect": {
                    "transcript": {
                        "contains": ["python3 codestable-maintainer/tools/verify.py"],
                        "forbidden_regex": ["(?m)^\\s*codestable-maintainer verify\\b"],
                    },
                    "trajectory": {"required_actions": ["codex_exec"]},
                    "git": {"must_not_modify": ["**"]},
                },
            }
        ),
        encoding="utf-8",
    )

    payload = behavior_harness.run_scenarios([scenario_path], "live-codex", 1)

    assert payload["ok"], payload


def test_behavior_harness_live_codex_timeout_keeps_partial_jsonl_trace(tmp_path: Path, monkeypatch) -> None:
    fake_codex = tmp_path / "codex"
    fake_codex.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import time\n"
        "print(json.dumps({'type': 'function_call', 'name': 'shell', 'cmd': ['python3', '.codestable/tools/codestable-worktree-gate.py']}), flush=True)\n"
        "time.sleep(5)\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    monkeypatch.setenv("CODESTABLE_HARNESS_CODEX_BIN", fake_codex.as_posix())
    scenario_path = tmp_path / "live-timeout.yaml"
    scenario_path.write_text(
        json.dumps(
            {
                "id": "live-timeout",
                "fixture": "worktree-start-required-repo",
                "actor": {
                    "prompt": "Implement the demo safely.",
                    "timeout_seconds": 1,
                },
                "expect": {
                    "transcript": {"contains": ["CODEX TIMEOUT"]},
                    "trajectory": {
                        "required_actions": ["codex_exec", "codex_timeout"],
                        "required_contains": ["codestable-worktree-gate.py"],
                    },
                    "runtime": {"allow_timeout": True},
                    "git": {"must_not_modify": ["**"]},
                },
            }
        ),
        encoding="utf-8",
    )

    payload = behavior_harness.run_scenarios([scenario_path], "live-codex", 1)

    assert payload["ok"], payload
    result = payload["results"][0]
    assert result["trajectory"][-1] == "codex_timeout"
    assert any("codestable-worktree-gate.py" in item for item in result["trajectory"])


def test_behavior_harness_timeout_fails_unless_explicitly_allowed() -> None:
    denied = behavior_harness.grade_runtime({}, ["codex_exec", "codex_timeout"])
    allowed = behavior_harness.grade_runtime(
        {"runtime": {"allow_timeout": True}},
        ["codex_exec", "codex_timeout"],
    )

    assert denied == [
        {
            "grader": "runtime",
            "ok": False,
            "message": "codex run timed out",
            "severity": "P1",
        }
    ]
    assert allowed[0]["ok"] is True


def test_behavior_harness_normalizes_high_risk_command_actions() -> None:
    assert behavior_harness.command_actions(["python3", ".codestable/tools/codestable-worktree-gate.py"]) == [
        "action:worktree_gate"
    ]
    assert behavior_harness.command_actions(["git", "status"]) == ["action:git"]
    assert behavior_harness.command_actions("/opt/homebrew/bin/zsh -lc 'git -C . commit -m demo'") == [
        "action:git",
        "action:git_commit"
    ]
    assert behavior_harness.command_actions("/opt/homebrew/bin/zsh -lc 'git merge codex/demo'") == [
        "action:git",
        "action:git_merge"
    ]


def test_behavior_harness_forbidden_actions_cover_normalized_git_commands() -> None:
    results = behavior_harness.grade_trajectory(
        {"trajectory": {"forbidden_actions": ["commit", "merge"]}},
        ["action:git_commit", "action:git_merge"],
    )

    assert [result["ok"] for result in results] == [False, False]
