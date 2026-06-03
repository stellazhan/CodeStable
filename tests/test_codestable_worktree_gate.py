from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1] / "cs-onboard/tools"
sys.path.insert(0, str(TOOLS_DIR))


def load_tool(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, TOOLS_DIR / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gate = load_tool("codestable_worktree_gate_for_tests", "codestable-worktree-gate.py")
common = load_tool("codestable_common_for_tests", "codestable_common.py")


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


def make_feature_unit(repo: Path) -> Path:
    unit = repo / ".codestable/features/2026-06-03-demo"
    unit.mkdir(parents=True)
    return unit


def approved_override(unit: Path) -> None:
    (unit / "worktree-override.md").write_text(
        "reason: test\nscope: demo\napproval: approved\n",
        encoding="utf-8",
    )


def test_start_gate_blocks_implementation_unit_on_main(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)

    payload = gate.start_gate(repo, ".codestable/features/2026-06-03-demo")

    assert not payload["ok"]
    assert "linked execution worktree" in payload["findings"][0]["message"]
    assert not Path(payload["baseline_path"]).exists()


def test_start_gate_passes_in_real_linked_worktree_and_keeps_status_clean(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    unit = make_feature_unit(repo)
    (unit / "demo-design.md").write_text("design\n", encoding="utf-8")
    run(repo, "add", ".codestable")
    run(repo, "commit", "-m", "add feature unit")
    worktree = tmp_path / "repo-worktree"
    run(repo, "worktree", "add", "-b", "codex/demo", worktree.as_posix())

    payload = gate.start_gate(worktree, ".codestable/features/2026-06-03-demo")

    assert payload["ok"]
    assert payload["linked_worktree"] is True
    assert payload["baseline"]["timestamp"] > 0
    assert Path(payload["baseline_path"]).exists()
    assert run(worktree, "status", "--porcelain").stdout == ""


def test_path_named_codex_worktrees_is_not_enough_for_linked_worktree(tmp_path: Path) -> None:
    repo_parent = tmp_path / ".codex/worktrees"
    repo_parent.mkdir(parents=True)
    repo = repo_parent / "plain-repo"
    repo.mkdir()
    run(repo, "init", "-b", "main")
    run(repo, "config", "user.email", "test@example.com")
    run(repo, "config", "user.name", "Test User")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    unit = make_feature_unit(repo)
    (unit / "demo-design.md").write_text("design\n", encoding="utf-8")
    run(repo, "add", ".")
    run(repo, "commit", "-m", "init")

    payload = gate.start_gate(repo, ".codestable/features/2026-06-03-demo")

    assert not payload["ok"]
    assert payload["linked_worktree"] is False
    assert "linked execution worktree" in payload["findings"][0]["message"]


def test_commit_gate_blocks_staged_implementation_on_default_branch(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("print('x')\n", encoding="utf-8")
    run(repo, "add", "src/app.py")

    payload = gate.commit_gate(repo, ".codestable/features/2026-06-03-demo")

    assert not payload["ok"]
    assert "Staged implementation changes" in payload["findings"][0]["message"]


def test_commit_gate_catches_clean_main_with_post_baseline_implementation_commit(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    unit = make_feature_unit(repo)
    approved_override(unit)
    payload = gate.start_gate(repo, ".codestable/features/2026-06-03-demo")
    assert payload["ok"]

    run(repo, "add", ".codestable")
    run(repo, "commit", "-m", "add unit")
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("print('x')\n", encoding="utf-8")
    run(repo, "add", "src/app.py")
    run(repo, "commit", "-m", "implement on main")
    assert run(repo, "status", "--porcelain").stdout == ""

    payload = gate.commit_gate(repo, ".codestable/features/2026-06-03-demo")

    assert not payload["ok"]
    assert payload["post_baseline_implementation"] == ["src/app.py"]


def test_commit_gate_blocks_completed_unit_missing_review(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    unit = make_feature_unit(repo)
    (unit / "demo-checklist.yaml").write_text(
        "steps:\n"
        "  - id: one\n"
        "    status: done\n",
        encoding="utf-8",
    )

    payload = gate.commit_gate(repo, ".codestable/features/2026-06-03-demo")

    assert not payload["ok"]
    assert payload["findings"][0]["path"] == ".codestable/features/2026-06-03-demo/demo-implementation-review.md"


def test_commit_gate_warns_but_does_not_fail_for_mixed_non_implementation_buckets(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    (repo / "docs").mkdir()
    (repo / "docs/plan.md").write_text("plan\n", encoding="utf-8")
    (repo / "data/output").mkdir(parents=True)
    (repo / "data/output/items.json").write_text("{}\n", encoding="utf-8")
    run(repo, "add", "docs/plan.md", "data/output/items.json")

    payload = gate.commit_gate(repo, ".codestable/features/2026-06-03-demo")

    assert payload["ok"]
    assert payload["warnings"][0]["message"].startswith("Staged files span multiple commit buckets")


def test_quarantine_dry_run_does_not_mutate_repo(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("print('x')\n", encoding="utf-8")
    before_status = run(repo, "status", "--porcelain").stdout
    before_branches = run(repo, "branch", "--list").stdout
    before_worktrees = run(repo, "worktree", "list", "--porcelain").stdout

    payload = gate.quarantine_gate(repo, ".codestable/features/2026-06-03-demo", False)

    assert payload["ok"]
    assert payload["dry_run"] is True
    assert run(repo, "status", "--porcelain").stdout == before_status
    assert run(repo, "branch", "--list").stdout == before_branches
    assert run(repo, "worktree", "list", "--porcelain").stdout == before_worktrees


def test_quarantine_apply_requires_approved_override(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)

    payload = gate.quarantine_gate(repo, ".codestable/features/2026-06-03-demo", True)

    assert not payload["ok"]
    assert "--apply requires worktree-override.md" in payload["findings"][0]["message"]


def test_quarantine_refuses_untracked_secret_like_files(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    (repo / ".env.local").write_text("TOKEN=x\n", encoding="utf-8")

    payload = gate.quarantine_gate(repo, ".codestable/features/2026-06-03-demo", False)

    assert not payload["ok"]
    assert ".env.local" in payload["findings"][0]["path"]


def test_runtime_tool_paths_are_documented() -> None:
    tools_doc = (Path(__file__).resolve().parents[1] / "cs-onboard/reference/tools.md").read_text(encoding="utf-8")

    assert "python .codestable/tools/codestable-doctor.py --root . --json" in tools_doc
    assert "python .codestable/tools/codestable-worktree-gate.py --root . --json start" in tools_doc


def test_missing_unit_cli_returns_json_finding(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    script = TOOLS_DIR / "codestable-worktree-gate.py"

    completed = subprocess.run(
        [sys.executable, script.as_posix(), "--root", repo.as_posix(), "--json", "start", "--unit", "missing"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    payload = json.loads(completed.stdout)
    assert completed.returncode == 1
    assert payload["ok"] is False
    assert payload["findings"][0]["message"] == "unit not found: missing"
    assert "Traceback" not in completed.stderr


def test_missing_codestable_unit_path_returns_json_finding(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    script = TOOLS_DIR / "codestable-worktree-gate.py"

    completed = subprocess.run(
        [
            sys.executable,
            script.as_posix(),
            "--root",
            repo.as_posix(),
            "--json",
            "commit",
            "--unit",
            ".codestable/features/2026-06-03-missing",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    payload = json.loads(completed.stdout)
    assert completed.returncode == 1
    assert payload["findings"][0]["message"] == "unit not found: .codestable/features/2026-06-03-missing"
    assert "Traceback" not in completed.stderr
