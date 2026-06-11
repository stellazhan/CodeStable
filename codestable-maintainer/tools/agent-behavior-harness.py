#!/usr/bin/env python3
"""Run deterministic CodeStable behavior scenarios against fixture repos."""

from __future__ import annotations

import argparse
import fnmatch
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml  # type: ignore

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


SOURCE_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_ROOT = SOURCE_ROOT / "codestable-maintainer/scenarios"
RUNTIME_TOOL_SOURCE = SOURCE_ROOT / "cs-onboard/tools"


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], root)


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def init_repo(root: Path) -> None:
    root.mkdir(parents=True)
    git(root, "init", "-b", "main")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Test User")
    write_file(root / "README.md", "fixture repo\n")
    git(root, "add", "README.md")
    git(root, "commit", "-m", "init")


def commit_all(root: Path, message: str) -> None:
    git(root, "add", ".")
    git(root, "commit", "-m", message)


def copy_runtime_tools(root: Path) -> None:
    tools = root / ".codestable/tools"
    tools.mkdir(parents=True, exist_ok=True)
    for path in sorted(RUNTIME_TOOL_SOURCE.iterdir()):
        if path.name == "__pycache__" or not path.is_file():
            continue
        if path.suffix in {".py", ".sh"}:
            shutil.copy2(path, tools / path.name)


def write_common_codestable(root: Path) -> None:
    write_file(
        root / ".codestable/attention.md",
        "# Attention\n\n- Read this before routing CodeStable work.\n",
    )
    write_file(
        root / ".codestable/reference/system-overview.md",
        "# System Overview\n\nFeature, issue, refactor, and route governance fixture.\n",
    )
    copy_runtime_tools(root)


def write_feature_unit(root: Path, slug: str = "source-query-coverage") -> Path:
    unit = root / f".codestable/features/2026-06-10-{slug}"
    unit.mkdir(parents=True, exist_ok=True)
    write_file(
        unit / f"{slug}-design.md",
        "---\n"
        "doc_type: feature-design\n"
        f"feature: {slug}\n"
        "requirement: source-discovery\n"
        "status: approved\n"
        "---\n\n"
        "# Design\n\n"
        "capability_boundary: changed\n",
    )
    write_file(
        unit / f"{slug}-checklist.yaml",
        "steps:\n  - id: one\n    status: done\nchecks:\n  - id: verify\n    status: pending\n",
    )
    return unit


def write_requirements(root: Path, ambiguous: bool = True) -> None:
    write_file(
        root / ".codestable/requirements/source-discovery.md",
        "---\n"
        "slug: source-discovery\n"
        "status: current\n"
        "applies_when:\n"
        "  - source discovery\n"
        "  - crawl preflight\n"
        "excludes_when:\n"
        "  - frontend-only display tweak\n"
        "related_architecture:\n"
        "  - architecture/source-ingestion.md\n"
        "owner_review_state: clarified\n"
        "---\n\n"
        "# Source Discovery\n\n"
        "The system records source URL before crawl.\n",
    )
    if ambiguous:
        write_file(
            root / ".codestable/requirements/source-query-coverage.md",
            "---\n"
            "slug: source-query-coverage\n"
            "status: current\n"
            "applies_when:\n"
            "  - source discovery\n"
            "  - evidence coverage\n"
            "  - crawl preflight\n"
            "excludes_when:\n"
            "  - frontend-only display tweak\n"
            "related_architecture:\n"
            "  - architecture/source-ingestion.md\n"
            "owner_review_state: clarified\n"
            "---\n\n"
            "# Source Query Coverage\n\n"
            "The system evaluates query intent coverage before crawl.\n",
        )


def fixture_clean_onboarded(root: Path) -> None:
    init_repo(root)
    write_common_codestable(root)
    commit_all(root, "add codestable fixture")


def fixture_ambiguous_requirements(root: Path) -> None:
    init_repo(root)
    write_common_codestable(root)
    write_requirements(root, ambiguous=True)
    commit_all(root, "add ambiguous requirements")


def fixture_capability_boundary(root: Path) -> None:
    init_repo(root)
    write_common_codestable(root)
    write_requirements(root, ambiguous=False)
    write_feature_unit(root)
    commit_all(root, "add capability boundary feature")


def fixture_drifted_specs(root: Path) -> None:
    init_repo(root)
    write_common_codestable(root)
    write_requirements(root, ambiguous=False)
    write_feature_unit(root)
    write_file(
        root / ".codestable/requirements/source-discovery.md",
        "---\n"
        "slug: source-discovery\n"
        "status: current\n"
        "owner_review_state: drift-suspected\n"
        "applies_when:\n"
        "  - source discovery\n"
        "---\n\n"
        "# Source Discovery\n\n"
        "The current code and requirement disagree about coverage fields.\n",
    )
    commit_all(root, "add drifted specs")


def fixture_review_packet(root: Path) -> None:
    init_repo(root)
    write_common_codestable(root)
    unit = write_feature_unit(root, "demo")
    write_file(unit / "demo-implementation-review.md", "reviewer: subagent\nfindings: none\n")
    commit_all(root, "add review packet base")
    write_file(root / "src/app.py", 'TOKEN="supersecretvalue"\nprint("x")\n')
    write_file(root / ".env.local", "API_KEY=should_not_appear\n")


def fixture_owner_judgment(root: Path) -> None:
    init_repo(root)
    write_common_codestable(root)
    write_feature_unit(root, "demo")
    commit_all(root, "add owner judgment base")


def fixture_backlog(root: Path) -> None:
    init_repo(root)
    write_common_codestable(root)
    unit = write_feature_unit(root, "demo")
    write_file(unit / "demo-acceptance.md", "# Acceptance\n\n## Follow-Ups\n\n- required: owner review required\n")
    commit_all(root, "add backlog fixture")


def fixture_finished_worktree(root: Path) -> None:
    init_repo(root)
    write_common_codestable(root)
    commit_all(root, "add codestable base")
    git(root, "checkout", "-b", "codex/demo")
    write_file(root / "src/app.py", "print('ready')\n")
    commit_all(root, "implement demo")
    head = git(root, "rev-parse", "HEAD").stdout.strip()
    git(root, "checkout", "main")
    common_dir = git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
    record = {
        "schema_version": 1,
        "branch": "codex/demo",
        "worktree": root.as_posix(),
        "unit": ".codestable/features/2026-06-10-demo",
        "status": "ready-to-merge",
        "base_ref": "main",
        "covered_head": head,
        "covered_diff": f"main...{head}",
        "learning_report": ".codestable/features/2026-06-10-demo/demo-learning-report.md",
        "context_check": ".codestable/features/2026-06-10-demo/demo-learning-context-check.json",
        "merge_readiness": ".codestable/features/2026-06-10-demo/demo-merge-readiness.json",
        "created_at": "2026-06-10T00:00:00Z",
        "last_seen_at": "2026-06-10T00:00:00Z",
        "next_action": "merge codex/demo into main after owner approval",
    }
    write_file(Path(common_dir) / "codestable/worktree-inbox/codex_demo.json", json.dumps(record, indent=2) + "\n")


FIXTURES = {
    "clean-onboarded-repo": fixture_clean_onboarded,
    "ambiguous-requirements-repo": fixture_ambiguous_requirements,
    "capability-boundary-repo": fixture_capability_boundary,
    "drifted-specs-repo": fixture_drifted_specs,
    "review-packet-repo": fixture_review_packet,
    "owner-judgment-repo": fixture_owner_judgment,
    "backlog-repo": fixture_backlog,
    "finished-worktree-repo": fixture_finished_worktree,
}


def load_scenario(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if HAS_YAML:
        payload = yaml.safe_load(text)
    else:
        payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError(f"scenario must be an object: {path}")
    payload.setdefault("_path", path.as_posix())
    return payload


def scenario_paths(args: argparse.Namespace) -> list[Path]:
    paths: list[Path] = []
    for value in args.scenario or []:
        path = Path(value)
        if not path.is_absolute():
            path = SOURCE_ROOT / path
        paths.append(path)
    if args.suite and not paths:
        suite_root = SCENARIO_ROOT / args.suite
        paths.extend(sorted(suite_root.glob("*.yaml")))
    if not paths:
        paths.extend(sorted((SCENARIO_ROOT / "critical").glob("*.yaml")))
    return paths


def substitute(value: object, root: Path, work: Path) -> object:
    if isinstance(value, str):
        return value.replace("{root}", root.as_posix()).replace("{work}", work.as_posix())
    if isinstance(value, list):
        return [substitute(item, root, work) for item in value]
    if isinstance(value, dict):
        return {str(key): substitute(item, root, work) for key, item in value.items()}
    return value


def dirty_paths(root: Path) -> list[str]:
    status = git(root, "status", "--porcelain", "-uall")
    paths: list[str] = []
    for line in status.stdout.splitlines():
        if not line:
            continue
        raw = line[3:].strip('"')
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        paths.append(raw)
    return sorted(paths)


def glob_exists(root: Path, pattern: str) -> bool:
    return any(root.glob(pattern))


def path_matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def json_path(payload: object, path: str) -> object:
    current = payload
    for part in path.split("."):
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            current = current[part]
        else:
            raise KeyError(path)
    return current


def check_json_assertions(payload: object, assertions: list[dict[str, object]]) -> list[str]:
    failures: list[str] = []
    for assertion in assertions:
        path = str(assertion["path"])
        try:
            value = json_path(payload, path)
        except (KeyError, IndexError, ValueError, TypeError):
            failures.append(f"missing json path {path}")
            continue
        if "equals" in assertion and value != assertion["equals"]:
            failures.append(f"{path} expected {assertion['equals']!r}, got {value!r}")
        if "contains" in assertion and str(assertion["contains"]) not in str(value):
            failures.append(f"{path} does not contain {assertion['contains']!r}")
        if "min_len" in assertion and len(value) < int(assertion["min_len"]):  # type: ignore[arg-type]
            failures.append(f"{path} length is below {assertion['min_len']}")
    return failures


def grade_result(grader: str, ok: bool, message: str) -> dict[str, object]:
    return {"grader": grader, "ok": ok, "message": message, "severity": None if ok else "P1"}


def run_actor(root: Path, work: Path, scenario: dict[str, object]) -> tuple[list[str], list[str], list[dict[str, object]]]:
    transcript: list[str] = []
    trajectory: list[str] = []
    tool_calls: list[dict[str, object]] = []
    actor = scenario.get("actor") if isinstance(scenario.get("actor"), dict) else {}
    script = actor.get("script", []) if isinstance(actor, dict) else []
    if not isinstance(script, list):
        raise ValueError("actor.script must be a list")
    for step in script:
        if not isinstance(step, dict):
            continue
        if "say" in step:
            text = str(substitute(step["say"], root, work))
            transcript.append(text)
        if "action" in step:
            trajectory.append(str(step["action"]))
        if "owner_stop" in step:
            value = str(step["owner_stop"])
            trajectory.append(f"owner_stop:{value}")
            transcript.append(f"OWNER STOP: {value}")
        if "write" in step and isinstance(step["write"], dict):
            target = str(substitute(step["write"].get("path", ""), root, work))
            content = str(substitute(step["write"].get("content", ""), root, work))
            write_file(root / target, content)
            trajectory.append(f"write:{target}")
        if "run" in step:
            cmd = substitute(step["run"], root, work)
            if not isinstance(cmd, list) or not all(isinstance(part, str) for part in cmd):
                raise ValueError("actor run step must be a list of strings")
            result = run(cmd, root)
            call = {
                "cmd": cmd,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
            tool_calls.append(call)
            trajectory.append("run:" + " ".join(cmd))
            transcript.append(result.stdout)
            if result.stderr:
                transcript.append(result.stderr)
    return transcript, trajectory, tool_calls


def grade_transcript(expect: dict[str, object], transcript: str, trajectory: list[str]) -> list[dict[str, object]]:
    checks = expect.get("transcript", {})
    if not isinstance(checks, dict):
        return []
    results: list[dict[str, object]] = []
    for needle in checks.get("contains", []) or []:
        results.append(grade_result("transcript", str(needle) in transcript, f"contains {needle!r}"))
    for needle in checks.get("forbidden", []) or []:
        results.append(grade_result("transcript", str(needle) not in transcript, f"forbids {needle!r}"))
    for stop in checks.get("must_stop_for", []) or []:
        value = f"owner_stop:{stop}"
        results.append(grade_result("transcript", value in trajectory, f"stops for {stop!r}"))
    return results


def grade_trajectory(expect: dict[str, object], trajectory: list[str]) -> list[dict[str, object]]:
    checks = expect.get("trajectory", {})
    if not isinstance(checks, dict):
        return []
    results: list[dict[str, object]] = []
    for action in checks.get("required_actions", []) or []:
        results.append(grade_result("trajectory", str(action) in trajectory, f"requires action {action!r}"))
    for action in checks.get("forbidden_actions", []) or []:
        results.append(grade_result("trajectory", str(action) not in trajectory, f"forbids action {action!r}"))
    return results


def grade_artifacts(root: Path, expect: dict[str, object]) -> list[dict[str, object]]:
    checks = expect.get("artifacts", {})
    if not isinstance(checks, dict):
        return []
    results: list[dict[str, object]] = []
    for pattern in checks.get("must_create", []) or []:
        results.append(grade_result("artifact", glob_exists(root, str(pattern)), f"creates {pattern!r}"))
    for pattern in checks.get("must_not_create", []) or []:
        results.append(grade_result("artifact", not glob_exists(root, str(pattern)), f"does not create {pattern!r}"))
    for item in checks.get("contains", []) or []:
        if not isinstance(item, dict):
            continue
        path = root / str(item.get("path", ""))
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        results.append(grade_result("artifact", str(item.get("text", "")) in text, f"{path} contains text"))
    for item in checks.get("forbidden_text", []) or []:
        if not isinstance(item, dict):
            continue
        path = root / str(item.get("path", ""))
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        results.append(grade_result("artifact", str(item.get("text", "")) not in text, f"{path} forbids text"))
    return results


def grade_git(root: Path, expect: dict[str, object]) -> list[dict[str, object]]:
    checks = expect.get("git", {})
    if not isinstance(checks, dict):
        return []
    dirty = dirty_paths(root)
    results: list[dict[str, object]] = []
    for pattern in checks.get("must_not_modify", []) or []:
        matches = [path for path in dirty if fnmatch.fnmatch(path, str(pattern))]
        results.append(grade_result("repo-state", not matches, f"does not modify {pattern!r}: {matches}"))
    for pattern in checks.get("must_modify", []) or []:
        results.append(grade_result("repo-state", any(fnmatch.fnmatch(path, str(pattern)) for path in dirty), f"modifies {pattern!r}"))
    return results


def grade_commands(root: Path, work: Path, expect: dict[str, object]) -> list[dict[str, object]]:
    commands = expect.get("commands", [])
    if not isinstance(commands, list):
        return []
    results: list[dict[str, object]] = []
    for index, command in enumerate(commands):
        if not isinstance(command, dict):
            continue
        cmd = substitute(command.get("cmd", []), root, work)
        if not isinstance(cmd, list) or not all(isinstance(part, str) for part in cmd):
            results.append(grade_result("command", False, f"command {index} must be a list of strings"))
            continue
        result = run(cmd, root)
        expected_code = int(command.get("exit_code", 0))
        results.append(grade_result("command", result.returncode == expected_code, f"{cmd} exits {expected_code}"))
        for needle in command.get("stdout_contains", []) or []:
            results.append(grade_result("command", str(needle) in result.stdout, f"{cmd} stdout contains {needle!r}"))
        for needle in command.get("stdout_forbidden", []) or []:
            results.append(grade_result("command", str(needle) not in result.stdout, f"{cmd} stdout forbids {needle!r}"))
        if command.get("json"):
            try:
                payload = json.loads(result.stdout)
            except json.JSONDecodeError as exc:
                results.append(grade_result("command", False, f"{cmd} did not emit JSON: {exc}"))
            else:
                for failure in check_json_assertions(payload, command["json"]):  # type: ignore[arg-type]
                    results.append(grade_result("command-json", False, f"{cmd}: {failure}"))
    return results


def files_snapshot(root: Path) -> list[str]:
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file() and ".git" not in path.parts)


def run_one(scenario: dict[str, object], run_index: int, actor_mode: str, keep: bool = False) -> dict[str, object]:
    scenario_id = str(scenario.get("id") or Path(str(scenario.get("_path", "scenario"))).stem)
    fixture = str(scenario.get("fixture") or "clean-onboarded-repo")
    if fixture not in FIXTURES:
        raise ValueError(f"unknown fixture: {fixture}")
    work_root = Path(tempfile.mkdtemp(prefix=f"codestable-behavior-{scenario_id}-"))
    repo = work_root / "repo"
    FIXTURES[fixture](repo)
    before = files_snapshot(repo)
    transcript_lines, trajectory, tool_calls = run_actor(repo, work_root, scenario)
    transcript = "\n".join(transcript_lines)
    expect = scenario.get("expect") if isinstance(scenario.get("expect"), dict) else {}
    grader_results: list[dict[str, object]] = []
    grader_results.extend(grade_transcript(expect, transcript, trajectory))
    grader_results.extend(grade_trajectory(expect, trajectory))
    grader_results.extend(grade_artifacts(repo, expect))
    grader_results.extend(grade_git(repo, expect))
    grader_results.extend(grade_commands(repo, work_root, expect))
    diff_stat = git(repo, "diff", "--stat").stdout
    payload = {
        "scenario": scenario_id,
        "run": run_index,
        "actor_mode": actor_mode,
        "actor_adapter": "scripted",
        "fixture": fixture,
        "repo": repo.as_posix() if keep else None,
        "turns": transcript_lines,
        "tool_calls": tool_calls,
        "trajectory": trajectory,
        "files_before": before,
        "files_after": files_snapshot(repo),
        "git_diff_stat": diff_stat,
        "grader_results": grader_results,
        "ok": all(result["ok"] for result in grader_results),
    }
    if not keep:
        shutil.rmtree(work_root, ignore_errors=True)
    return payload


def run_scenarios(paths: list[Path], actor_mode: str, runs_override: int | None, keep: bool = False) -> dict[str, object]:
    scenario_results = []
    for path in paths:
        scenario = load_scenario(path)
        scenario_runs = runs_override or int(scenario.get("runs", 1))
        for run_index in range(1, scenario_runs + 1):
            scenario_results.append(run_one(scenario, run_index, actor_mode, keep))
    return {
        "ok": all(result["ok"] for result in scenario_results),
        "scenario_count": len(paths),
        "run_count": len(scenario_results),
        "results": scenario_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Run behavior scenarios")
    run_parser.add_argument("--scenario", action="append", help="Scenario YAML path; repeatable")
    run_parser.add_argument("--suite", help="Scenario suite under codestable-maintainer/scenarios")
    run_parser.add_argument("--actor", choices=["sterile", "compacted", "realistic"], default="sterile")
    run_parser.add_argument("--runs", type=int, help="Override run count for each scenario")
    run_parser.add_argument("--keep-fixtures", action="store_true", help="Keep temporary fixture repos for debugging")
    run_parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args()

    if args.command == "run":
        paths = scenario_paths(args)
        payload = run_scenarios(paths, args.actor, args.runs, args.keep_fixtures)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("CodeStable behavior harness:", "passed" if payload["ok"] else "failed")
            for result in payload["results"]:
                status = "passed" if result["ok"] else "failed"
                print(f"- {result['scenario']} run {result['run']}: {status}")
                for grader in result["grader_results"]:
                    if not grader["ok"]:
                        print(f"  - {grader['grader']}: {grader['message']}")
        return 0 if payload["ok"] else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
