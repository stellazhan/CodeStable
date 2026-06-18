#!/usr/bin/env python3
"""Verify a pushed CodeStable branch from a fresh clone."""

from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


SKILL_DIRS = {
    "browser-bridge",
    "codestable-maintainer",
    "cs",
    "cs-arch",
    "cs-audit",
    "cs-brainstorm",
    "cs-decide",
    "cs-explore",
    "cs-feat",
    "cs-feat-accept",
    "cs-feat-design",
    "cs-feat-ff",
    "cs-feat-impl",
    "cs-goal",
    "cs-guide",
    "cs-issue",
    "cs-issue-analyze",
    "cs-issue-fix",
    "cs-issue-report",
    "cs-learn",
    "cs-libdoc",
    "cs-note",
    "cs-onboard",
    "cs-refactor",
    "cs-refactor-ff",
    "cs-req",
    "cs-roadmap",
    "cs-trick",
    "using-codestable",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    message: str
    path: str | None = None


@dataclass(frozen=True)
class ChangedPath:
    status: str
    path: str


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], root)


def current_branch(root: Path) -> str:
    return git(root, "branch", "--show-current").stdout.strip()


def git_head(root: Path, ref: str = "HEAD") -> str | None:
    result = git(root, "rev-parse", "--verify", ref)
    return result.stdout.strip() if result.returncode == 0 else None


def ensure_source_repo(root: Path) -> list[Finding]:
    required = ["README.md", "cs-onboard/SKILL.md", "codestable-maintainer/SKILL.md"]
    missing = [path for path in required if not (root / path).exists()]
    if missing:
        return [Finding("P1", "Current checkout does not look like the CodeStable source repo.", ", ".join(missing))]
    return []


def remote_ref(root: Path, remote: str, branch: str) -> str | None:
    fetch = git(root, "fetch", remote, branch)
    if fetch.returncode != 0:
        return None
    return git_head(root, f"refs/remotes/{remote}/{branch}") or git_head(root, "FETCH_HEAD")


def remote_default(root: Path, remote: str) -> str:
    ref = git(root, "symbolic-ref", "--quiet", "--short", f"refs/remotes/{remote}/HEAD")
    if ref.returncode == 0 and ref.stdout.strip().startswith(f"{remote}/"):
        return ref.stdout.strip().split("/", 1)[1]
    for candidate in ("main", "master"):
        if git_head(root, f"refs/remotes/{remote}/{candidate}") or git_head(root, candidate):
            return candidate
    return "main"


def changed_file_entries(root: Path, remote: str, branch: str) -> list[ChangedPath]:
    default = remote_default(root, remote)
    base_ref = f"refs/remotes/{remote}/{default}"
    git(root, "fetch", remote, default)
    if not git_head(root, base_ref):
        base_ref = "HEAD~1"
    base = git(root, "merge-base", base_ref, "HEAD")
    start = base.stdout.strip() if base.returncode == 0 and base.stdout.strip() else base_ref
    diff = git(root, "diff", "--name-status", f"{start}..HEAD")
    if diff.returncode != 0:
        return []
    paths: list[ChangedPath] = []
    for line in diff.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        path = parts[-1]
        paths.append(ChangedPath(status=status, path=path))
    return paths


def changed_files(root: Path, remote: str, branch: str) -> list[str]:
    return [item.path for item in changed_file_entries(root, remote, branch)]


def dirty_paths(root: Path) -> list[str]:
    status = git(root, "status", "--porcelain", "-uall")
    if status.returncode != 0:
        return []
    return [line for line in status.stdout.splitlines() if line.strip()]


def changed_skill_dirs(paths: list[str]) -> list[str]:
    skills: set[str] = set()
    for path in paths:
        parts = Path(path).parts
        if parts and parts[0] in SKILL_DIRS:
            skills.add(parts[0])
    return sorted(skills)


def existing_skill_dirs(root: Path) -> list[str]:
    return sorted(skill for skill in SKILL_DIRS if (root / skill / "SKILL.md").exists())


def is_real_installed_root(path: Path) -> bool:
    resolved = path.expanduser().resolve()
    candidates = [
        Path.home() / ".agents/skills",
        Path.home() / ".codex/skills",
    ]
    return any(resolved == candidate.expanduser().resolve() for candidate in candidates)


def changed_noninstalled(paths: list[str], skills: list[str]) -> list[dict[str, str]]:
    skill_roots = set(skills)
    result = []
    for path in paths:
        parts = Path(path).parts
        if parts and parts[0] in skill_roots:
            continue
        result.append({"path": path, "install": "not installed: N/A", "reason": "source-only or repository-level file"})
    return result


def discover_validator(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for root in (Path.home() / ".codex", Path.home() / ".agents"):
        if not root.exists():
            continue
        for path in root.rglob("quick_validate.py"):
            return path.as_posix()
    return None


def validate_skill(clone: Path, skill: str, validator: str | None) -> Finding | None:
    if not validator:
        return Finding("P1", "Skill validator quick_validate.py was not found.", skill)
    result = run(["uvx", "--with", "PyYAML", "python", validator, skill], clone)
    if result.returncode != 0:
        return Finding("P1", f"Skill validation failed: {result.stdout}{result.stderr}", skill)
    return None


def run_tests_if_needed(clone: Path, paths: list[str]) -> Finding | None:
    needs_tests = any(path.startswith(("cs-onboard/tools/", "codestable-maintainer/tools/", "tests/")) for path in paths)
    if not needs_tests:
        return None
    result = run(["uvx", "pytest", "-q"], clone)
    if result.returncode != 0:
        return Finding("P1", f"Harness tests failed: {result.stdout}{result.stderr}")
    return None


def run_behavior_suite_if_needed(clone: Path, paths: list[str]) -> Finding | None:
    prefixes = (
        "cs/",
        "cs-",
        "using-codestable/",
        "cs-onboard/reference/",
        "cs-onboard/tools/",
        "codestable-maintainer/SKILL.md",
        "codestable-maintainer/references/",
        "codestable-maintainer/scenarios/",
        "codestable-maintainer/tools/agent-behavior-harness.py",
    )
    needs_behavior = any(path.startswith(prefixes) for path in paths)
    if not needs_behavior:
        return None
    runner = clone / "codestable-maintainer/tools/agent-behavior-harness.py"
    if not runner.exists():
        return Finding("P1", "Behavior harness runner is missing.", runner.relative_to(clone).as_posix())
    result = run(
        [
            "python3",
            runner.relative_to(clone).as_posix(),
            "run",
            "--suite",
            "critical",
            "--actor",
            "sterile",
            "--json",
        ],
        clone,
    )
    if result.returncode != 0:
        return Finding("P1", f"Behavior harness critical suite failed: {result.stdout}{result.stderr}")
    return None


def dirs_match(left: Path, right: Path) -> bool:
    if not right.exists():
        return False
    comparison = filecmp.dircmp(left, right, ignore=["__pycache__", ".pytest_cache"])
    if comparison.left_only or comparison.right_only or comparison.diff_files or comparison.funny_files:
        return False
    return all(dirs_match(Path(comparison.left) / sub, Path(comparison.right) / sub) for sub in comparison.common_dirs)


def sync_dir(source: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)
    for cache_name in ("__pycache__", ".pytest_cache"):
        for cache in dest.rglob(cache_name):
            shutil.rmtree(cache)


def verify(
    repo: Path,
    branch: str,
    remote: str,
    installed_root: Path,
    validator: str | None,
    sync_installed: bool,
) -> dict[str, object]:
    repo = repo.resolve()
    findings = ensure_source_repo(repo)
    current = current_branch(repo)
    if current != branch:
        findings.append(Finding("P1", "Current branch does not match requested branch.", f"{current} != {branch}"))
    dirty = dirty_paths(repo)
    if dirty:
        findings.append(Finding("P1", "Source checkout has uncommitted changes; commit and push before verification.", "\n".join(dirty)))

    default_branch = remote_default(repo, remote)
    remote_head = remote_ref(repo, remote, branch)
    local_head = git_head(repo)
    if not remote_head:
        findings.append(Finding("P1", "Branch is not pushed or remote branch cannot be fetched.", branch))
    elif remote_head != local_head:
        findings.append(Finding("P1", "Local HEAD does not match remote branch HEAD.", f"{local_head} != {remote_head}"))

    if sync_installed and is_real_installed_root(installed_root) and branch != default_branch:
        findings.append(
            Finding(
                "P1",
                "Real installed skill roots may only be synced from the remote default branch. Use a temporary installed root for feature-branch verification.",
                f"{branch} != {default_branch}",
            )
        )

    remote_url = git(repo, "remote", "get-url", remote).stdout.strip()
    entries = changed_file_entries(repo, remote, branch)
    paths = [entry.path for entry in entries]
    skills = existing_skill_dirs(repo) if sync_installed and branch == default_branch else changed_skill_dirs(paths)
    noninstalled = changed_noninstalled(paths, skills)
    clone_path: str | None = None

    if findings:
        return {
            "ok": False,
            "findings": [asdict(finding) for finding in findings],
            "changed_files": paths,
            "installable_units": skills,
            "noninstalled": noninstalled,
            "fresh_clone": clone_path,
        }

    clone_root = Path(tempfile.mkdtemp(prefix="codestable-verify-"))
    clone = clone_root / "CodeStable"
    clone_result = run(["git", "clone", "--branch", branch, "--single-branch", remote_url, clone.as_posix()], repo)
    clone_path = clone.as_posix()
    if clone_result.returncode != 0:
        findings.append(Finding("P1", f"Fresh clone failed: {clone_result.stderr.strip()}"))
    else:
        validator_path = discover_validator(validator)
        for entry in entries:
            if not entry.status.startswith("D") and not (clone / entry.path).exists():
                findings.append(Finding("P1", "Changed file is missing from fresh clone.", entry.path))
        for skill in skills:
            finding = validate_skill(clone, skill, validator_path)
            if finding:
                findings.append(finding)
        test_finding = run_tests_if_needed(clone, paths)
        if test_finding:
            findings.append(test_finding)
        behavior_finding = run_behavior_suite_if_needed(clone, paths)
        if behavior_finding:
            findings.append(behavior_finding)
        for skill in skills:
            source = clone / skill
            dest = installed_root / skill
            if sync_installed:
                sync_dir(source, dest)
            if not dirs_match(source, dest):
                findings.append(Finding("P1", "Installed skill copy differs from fresh clone.", skill))

    return {
        "ok": not any(finding.severity == "P1" for finding in findings),
        "findings": [asdict(finding) for finding in findings],
        "changed_files": paths,
        "installable_units": skills,
        "noninstalled": noninstalled,
        "fresh_clone": clone_path,
        "sync_installed": sync_installed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="CodeStable source checkout")
    parser.add_argument("--branch", required=True, help="Branch to verify")
    parser.add_argument("--remote", default="origin", help="Remote name")
    parser.add_argument("--installed-root", default=str(Path.home() / ".agents/skills"))
    parser.add_argument("--validator", default=None, help="Explicit skill quick_validate.py path")
    parser.add_argument("--sync-installed", action="store_true", help="Sync installed skill copies from fresh clone before diffing")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = verify(
        Path(args.repo),
        args.branch,
        args.remote,
        Path(args.installed_root),
        args.validator,
        args.sync_installed,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("CodeStable maintainer verify:", "passed" if payload["ok"] else "failed")
        for finding in payload["findings"]:
            path = f" ({finding['path']})" if finding.get("path") else ""
            print(f"- {finding['severity']}: {finding['message']}{path}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
