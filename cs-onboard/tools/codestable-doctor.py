#!/usr/bin/env python3
"""Report CodeStable lifecycle state without mutating the repository."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from codestable_common import (
    Finding,
    bucket_paths,
    current_branch,
    default_branch,
    git_status,
    is_implementation_path,
    is_linked_worktree,
    iter_baselines,
    iter_units,
    missing_review_findings,
    post_baseline_implementation_changes,
    scan_backlog,
)


def diagnose(root: Path) -> dict[str, object]:
    root = root.resolve()
    changed = git_status(root)
    changed_paths = [item.path for item in changed]
    implementation_changes = [path for path in changed_paths if is_implementation_path(path)]
    units = iter_units(root)
    review_findings = missing_review_findings(root, units)
    backlog = scan_backlog(root)
    post_baseline_blocks: list[dict[str, object]] = []
    for baseline in iter_baselines(root):
        implementation_paths = post_baseline_implementation_changes(root, baseline)
        if implementation_paths:
            post_baseline_blocks.append(
                {
                    "unit": baseline.get("unit"),
                    "default_branch": baseline.get("default_branch"),
                    "default_head": baseline.get("default_head"),
                    "implementation_changes": implementation_paths,
                }
            )
    linked = is_linked_worktree(root)
    branch = current_branch(root)
    default = default_branch(root)

    findings: list[Finding] = []
    if implementation_changes and not linked:
        findings.append(
            Finding(
                severity="P1",
                message="Implementation changes are present outside a linked execution worktree.",
            )
        )
    for block in post_baseline_blocks:
        findings.append(
            Finding(
                severity="P1",
                message="Default branch contains implementation changes after a recorded worktree baseline.",
                path=", ".join(block["implementation_changes"]),
            )
        )
    findings.extend(review_findings)
    if backlog:
        findings.append(
            Finding(
                severity="P2",
                message="CodeStable backlog contains human-review or follow-up items.",
            )
        )

    if any(finding.severity == "P1" for finding in findings):
        status = "blocked"
        next_action = "Resolve P1 findings before reporting the task complete."
    elif implementation_changes:
        status = "implementation-active"
        next_action = "Run implementation review and worktree commit gate before completion."
    elif changed_paths:
        buckets = set(bucket_paths(changed_paths))
        status = "planning-safe" if buckets <= {"codestable", "docs"} else "dirty"
        next_action = "Review dirty buckets and commit only the intended scope."
    elif backlog:
        status = "attention-needed"
        next_action = "Resolve or explicitly defer the backlog items."
    else:
        status = "idle"
        next_action = "No CodeStable lifecycle action is required."

    return {
        "ok": status not in {"blocked"},
        "status": status,
        "next_action": next_action,
        "checkout": {
            "root": root.as_posix(),
            "current_branch": branch,
            "default_branch": default,
            "is_default_branch": branch == default if branch and default else None,
            "linked_worktree": linked,
        },
        "changed_files": changed_paths,
        "dirty_buckets": bucket_paths(changed_paths),
        "implementation_changes": implementation_changes,
        "active_units": [unit.as_posix() for unit in units],
        "backlog": [asdict(item) for item in backlog],
        "post_baseline_blocks": post_baseline_blocks,
        "findings": [asdict(finding) for finding in findings],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to inspect")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    args = parser.parse_args()

    report = diagnose(Path(args.root))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"CodeStable doctor: {report['status']}")
        print(f"Next action: {report['next_action']}")
        for finding in report["findings"]:
            path = f" ({finding['path']})" if finding.get("path") else ""
            print(f"- {finding['severity']}: {finding['message']}{path}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
