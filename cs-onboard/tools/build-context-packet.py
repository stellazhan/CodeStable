#!/usr/bin/env python3
"""Build lightweight context packets for CodeStable stage handoffs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from codestable_common import git_status, is_secret_like_path, redact_text, resolve_unit


MAX_LIST_ITEMS = 20


def format_items(items: list[str], empty: str = "None recorded.") -> list[str]:
    if not items:
        return [f"- {empty}"]
    return [f"- {redact_text(item)}" for item in items[:MAX_LIST_ITEMS]]


def changed_files(root: Path) -> list[str]:
    paths = []
    for item in git_status(root):
        if is_secret_like_path(item.path):
            paths.append(f"{item.path} [redacted secret-like path]")
        else:
            paths.append(item.path)
    return sorted(paths)


def build_handoff_packet(
    root: Path,
    unit_value: str,
    decided: list[str],
    rejected: list[str],
    risks: list[str],
    files: list[str],
    remaining: list[str],
    evidence: list[str],
) -> str:
    root = root.resolve()
    unit_dir = resolve_unit(root, unit_value)
    file_items = files or changed_files(root)

    lines: list[str] = [
        "# CodeStable Handoff Context",
        "",
        f"- root: `{root.as_posix()}`",
        f"- unit: `{unit_dir.as_posix()}`",
        "",
        "## Handoff",
        "",
        "- Decided:",
        *format_items(decided),
        "- Rejected:",
        *format_items(rejected),
        "- Risks:",
        *format_items(risks),
        "- Files:",
        *format_items(file_items),
        "- Remaining:",
        *format_items(remaining),
        "- Evidence:",
        *format_items(evidence),
        "",
    ]
    return "\n".join(lines)


def build_packet(
    root: Path,
    unit_value: str,
    audience: str,
    decided: list[str],
    rejected: list[str],
    risks: list[str],
    files: list[str],
    remaining: list[str],
    evidence: list[str],
) -> str:
    if audience != "handoff":
        raise ValueError(f"unknown context audience: {audience}")
    return build_handoff_packet(root, unit_value, decided, rejected, risks, files, remaining, evidence)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--unit", required=True, help="CodeStable unit path or slug")
    parser.add_argument("--audience", choices=["handoff"], required=True, help="Context audience")
    parser.add_argument("--output", required=True, help="Output Markdown file")
    parser.add_argument("--decided", action="append", default=[], help="Decision to include; repeat as needed")
    parser.add_argument("--rejected", action="append", default=[], help="Rejected option to include; repeat as needed")
    parser.add_argument("--risk", action="append", default=[], help="Risk to include; repeat as needed")
    parser.add_argument("--file", action="append", default=[], help="File to include; defaults to current changed files")
    parser.add_argument("--remaining", action="append", default=[], help="Remaining work item; repeat as needed")
    parser.add_argument("--evidence", action="append", default=[], help="Evidence line to include; repeat as needed")
    args = parser.parse_args()

    try:
        packet = build_packet(
            Path(args.root),
            args.unit,
            args.audience,
            args.decided,
            args.rejected,
            args.risk,
            args.file,
            args.remaining,
            args.evidence,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(packet, encoding="utf-8")
    print(output.as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
