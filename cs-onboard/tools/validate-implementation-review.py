#!/usr/bin/env python3
"""Gate CodeStable implementation handoffs.

The check is intentionally small and conservative: implementation diffs should
run in a linked worktree, and completed CodeStable implementation units should
carry an implementation-review note before the agent reports done.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


IMPLEMENTATION_PREFIXES = (
    "app/",
    "backend/",
    "client/",
    "frontend/",
    "lib/",
    "packages/",
    "scripts/",
    "server/",
    "src/",
    "supabase/migrations/",
    "test/",
    "tests/",
)

IMPLEMENTATION_SUFFIXES = (
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".svelte",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
)

UNIT_ROOTS = ("features", "issues", "refactors")


@dataclass(frozen=True)
class ChangedFile:
    status: str
    path: str


@dataclass(frozen=True)
class Finding:
    severity: str
    message: str
    path: str | None = None


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_status(root: Path) -> list[ChangedFile]:
    result = run_git(root, "status", "--porcelain", "-uall")
    if result.returncode != 0:
        return []

    changed: list[ChangedFile] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        status = line[:2]
        raw_path = line[3:]
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", 1)[1]
        changed.append(ChangedFile(status=status, path=raw_path))
    return changed


def is_implementation_path(path: str) -> bool:
    if path.startswith(".codestable/"):
        return False
    return path.startswith(IMPLEMENTATION_PREFIXES) or path.endswith(IMPLEMENTATION_SUFFIXES)


def is_linked_worktree(root: Path) -> bool:
    git_dir = run_git(root, "rev-parse", "--path-format=absolute", "--git-dir")
    common_dir = run_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if git_dir.returncode != 0 or common_dir.returncode != 0:
        return False

    git_dir_path = Path(git_dir.stdout.strip()).resolve()
    common_dir_path = Path(common_dir.stdout.strip()).resolve()
    if git_dir_path != common_dir_path:
        return True

    return ".codex/worktrees" in root.as_posix()


def unit_dir_for(path: str) -> Path | None:
    parts = Path(path).parts
    if len(parts) < 3 or parts[0] != ".codestable" or parts[1] not in UNIT_ROOTS:
        return None
    return Path(*parts[:3])


def review_file_for(unit_dir: Path) -> Path:
    slug = unit_dir.name.split("-", 3)[-1]
    return unit_dir / f"{slug}-implementation-review.md"


def all_checklist_steps_done(path: Path) -> bool:
    if not path.exists():
        return False

    in_steps = False
    saw_step = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped == "steps:":
            in_steps = True
            continue
        if in_steps and stripped and not raw.startswith((" ", "-")):
            break
        if not in_steps:
            continue
        if stripped.startswith("- "):
            saw_step = True
        if stripped.startswith("status:") and stripped.split(":", 1)[1].strip() != "done":
            return False
    return saw_step


def unit_needs_review(root: Path, unit_dir: Path) -> bool:
    unit_root = root / unit_dir
    if unit_dir.parts[1] == "issues":
        return any(unit_root.glob("*-fix-note.md"))

    return any(all_checklist_steps_done(path) for path in unit_root.glob("*-checklist.yaml"))


def find_touched_units(changed: list[ChangedFile]) -> set[Path]:
    units: set[Path] = set()
    for item in changed:
        unit_dir = unit_dir_for(item.path)
        if unit_dir is not None:
            units.add(unit_dir)
    return units


def validate(root: Path) -> tuple[bool, list[Finding], dict[str, object]]:
    changed = git_status(root)
    implementation_changes = [item.path for item in changed if is_implementation_path(item.path)]
    touched_units = sorted(find_touched_units(changed), key=lambda path: path.as_posix())
    findings: list[Finding] = []

    allow_main_checkout = os.environ.get("CODESTABLE_ALLOW_MAIN_CHECKOUT_IMPLEMENTATION") == "1"
    if implementation_changes and not allow_main_checkout and not is_linked_worktree(root):
        findings.append(
            Finding(
                severity="P1",
                message=(
                    "Implementation changes are present outside a linked worktree. "
                    "Create/switch to an execution worktree, or set "
                    "CODESTABLE_ALLOW_MAIN_CHECKOUT_IMPLEMENTATION=1 for an explicit override."
                ),
            )
        )

    missing_review: list[str] = []
    for unit_dir in touched_units:
        if unit_needs_review(root, unit_dir):
            review_path = root / review_file_for(unit_dir)
            if not review_path.exists():
                missing_review.append(review_file_for(unit_dir).as_posix())

    for path in missing_review:
        findings.append(
            Finding(
                severity="P1",
                message="Completed CodeStable implementation unit is missing implementation review evidence.",
                path=path,
            )
        )

    meta = {
        "changed_files": [item.path for item in changed],
        "implementation_changes": implementation_changes,
        "touched_units": [path.as_posix() for path in touched_units],
        "linked_worktree": is_linked_worktree(root),
        "allow_main_checkout": allow_main_checkout,
    }
    return not findings, findings, meta


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to inspect")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    ok, findings, meta = validate(root)

    if args.json:
        print(
            json.dumps(
                {
                    "ok": ok,
                    "findings": [finding.__dict__ for finding in findings],
                    **meta,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif ok:
        print("CodeStable implementation review gate passed.")
    else:
        print("CodeStable implementation review gate failed:")
        for finding in findings:
            suffix = f" ({finding.path})" if finding.path else ""
            print(f"- {finding.severity}: {finding.message}{suffix}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
