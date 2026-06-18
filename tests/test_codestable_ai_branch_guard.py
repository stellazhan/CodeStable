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


guard = load_tool("codestable_ai_branch_guard", "codestable-ai-branch-guard.py")


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


def test_blocks_git_switch_command(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    payload = {"tool_name": "Bash", "tool_input": {"command": "git switch codex/demo"}}

    result = guard.guard_payload(payload, repo, {"main", "master"})

    assert not result.ok
    assert result.reason == "branch_switch_command"


def test_blocks_git_switch_with_global_options(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    payload = {"tool_name": "Bash", "tool_input": {"command": f"git -C {repo.as_posix()} switch codex/demo"}}

    result = guard.guard_payload(payload, repo, {"main", "master"})

    assert not result.ok
    assert result.reason == "branch_switch_command"


def test_allows_git_worktree_add_command(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "git worktree add -b codex/demo .codex/worktrees/demo HEAD"},
    }

    result = guard.guard_payload(payload, repo, {"main", "master"})

    assert result.ok


def test_blocks_implementation_edit_on_main(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    payload = {"tool_name": "Write", "tool_input": {"file_path": repo / "src/app.py"}}

    result = guard.guard_payload(payload, repo, {"main", "master"})

    assert not result.ok
    assert result.reason == "implementation_edit_on_protected_branch"
    assert result.paths == ("src/app.py",)


def test_allows_codestable_planning_edit_on_main(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": repo / ".codestable/features/2026-06-18-demo/demo-design.md"},
    }

    result = guard.guard_payload(payload, repo, {"main", "master"})

    assert result.ok


def test_pre_commit_blocks_staged_implementation_on_main(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("print('x')\n", encoding="utf-8")
    run(repo, "add", "src/app.py")

    result = guard.guard_git_hook(repo, "pre-commit", {"main", "master"})

    assert not result.ok
    assert result.reason == "pre_commit_implementation_on_protected_branch"
    assert result.paths == ("src/app.py",)


def test_allows_implementation_edit_in_linked_worktree_branch(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    worktree = tmp_path / "repo-worktree"
    run(repo, "worktree", "add", "-b", "codex/demo", worktree.as_posix())
    payload = {"tool_name": "Write", "tool_input": {"file_path": worktree / "src/app.py"}}

    result = guard.guard_payload(payload, worktree, {"main", "master"})

    assert result.ok


def test_cli_blocks_hook_json_with_status_two(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    payload = {"tool_name": "Bash", "tool_input": {"command": "git checkout main"}}

    result = subprocess.run(
        [
            sys.executable,
            (TOOLS_DIR / "codestable-ai-branch-guard.py").as_posix(),
            "--root",
            repo.as_posix(),
            "--json",
        ],
        input=json.dumps(payload),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 2
    assert json.loads(result.stdout)["reason"] == "branch_switch_command"


def test_codex_hook_definition_invokes_branch_guard() -> None:
    hook_path = Path(__file__).resolve().parents[1] / "cs-onboard/hooks/hooks.codex.json"
    payload = json.loads(hook_path.read_text(encoding="utf-8"))

    hook_command = payload["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

    assert "codestable-ai-branch-guard.py" in hook_command
    assert "PreToolUse" in payload["hooks"]
