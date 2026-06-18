from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "cs-onboard/tools"
MAINTAINER_TOOLS_DIR = ROOT / "codestable-maintainer/tools"
sys.path.insert(0, str(TOOLS_DIR))

from codestable_common import is_blocking_follow_up_text, scan_backlog  # noqa: E402


def load_tool(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


review_packet = load_tool("build_review_packet", TOOLS_DIR / "build-review-packet.py")
context_packet = load_tool("build_context_packet", TOOLS_DIR / "build-context-packet.py")
context_sufficiency = load_tool("check_context_sufficiency", TOOLS_DIR / "check-context-sufficiency.py")
commit_planner = load_tool("plan_commits", TOOLS_DIR / "plan-commits.py")
backlog_tool = load_tool("codestable_backlog", TOOLS_DIR / "codestable-backlog.py")
maintainer_verify = load_tool("codestable_maintainer_verify", MAINTAINER_TOOLS_DIR / "verify.py")
search_yaml = load_tool("search_yaml", TOOLS_DIR / "search-yaml.py")


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
    (unit / "demo-design.md").write_text("design api_key=SECRET123\n", encoding="utf-8")
    (unit / "demo-checklist.yaml").write_text("steps:\n  - id: one\n    status: done\n", encoding="utf-8")
    return unit


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_review_packet_includes_unit_docs_diff_validation_and_redacts_secrets(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("TOKEN=\"supersecretvalue\"\nprint('x')\n", encoding="utf-8")
    run(repo, "add", ".codestable/features/2026-06-03-demo/demo-checklist.yaml")
    (repo / ".env.local").write_text("API_KEY=should_not_appear\n", encoding="utf-8")

    packet = review_packet.build_packet(
        repo,
        ".codestable/features/2026-06-03-demo",
        ["pytest -q -> passed with Authorization: Bearer abcdefghijklmnop"],
    )

    assert "demo-design.md" in packet
    assert "demo-checklist.yaml" in packet
    assert "Git Diff Stat" in packet
    assert "Staged" in packet
    assert "Untracked Files" in packet
    assert "print('x')" in packet
    assert "pytest -q -> passed" in packet
    assert "deterministic LLM boundary" in packet
    assert "SECRET123" not in packet
    assert "supersecretvalue" not in packet
    assert "abcdefghijklmnop" not in packet
    assert "should_not_appear" not in packet
    assert ".env.local" in packet


def test_review_packet_stages_shape_reviewer_mission_and_keep_default(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("print('x')\n", encoding="utf-8")

    default_packet = review_packet.build_packet(repo, ".codestable/features/2026-06-03-demo", ["pytest -> passed"])
    spec_packet = review_packet.build_packet(
        repo,
        ".codestable/features/2026-06-03-demo",
        ["pytest -> passed"],
        "spec",
    )
    quality_packet = review_packet.build_packet(
        repo,
        ".codestable/features/2026-06-03-demo",
        ["pytest -> passed"],
        "quality",
    )

    assert "- stage: `implementation`" in default_packet
    assert "Implementation Review Packet" in default_packet
    assert "- stage: `spec`" in spec_packet
    assert "Spec Compliance Review Packet" in spec_packet
    assert "built exactly what the approved requirement" in spec_packet
    assert "missing requested behavior" in spec_packet
    assert "- stage: `quality`" in quality_packet
    assert "Code Quality Review Packet" in quality_packet
    assert "clean, tested, maintainable" in quality_packet


def test_verification_stage_requires_fresh_validation_evidence(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)

    for validations in ([], [""], ["   "]):
        try:
            review_packet.build_packet(repo, ".codestable/features/2026-06-03-demo", validations, "verification")
        except ValueError as exc:
            assert "requires at least one" in str(exc)
        else:
            raise AssertionError("verification stage should require validation evidence")

    packet = review_packet.build_packet(
        repo,
        ".codestable/features/2026-06-03-demo",
        ["", "pytest -q\n================ passed ================"],
        "verification",
    )

    assert "Verification Evidence Review Packet" in packet
    assert "Do not accept remembered claims" in packet
    assert "pytest -q" in packet


def test_verification_stage_cli_rejects_blank_validation_inputs(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("   \n", encoding="utf-8")

    for args in (
        ["--validation", "   "],
        ["--validation-file", empty_file.as_posix()],
    ):
        result = subprocess.run(
            [
                sys.executable,
                (TOOLS_DIR / "build-review-packet.py").as_posix(),
                "--root",
                repo.as_posix(),
                "--unit",
                ".codestable/features/2026-06-03-demo",
                "--stage",
                "verification",
                "--output",
                (tmp_path / "packet.md").as_posix(),
                *args,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        assert result.returncode == 1
        assert "requires at least one" in result.stderr


def test_context_packet_builds_lightweight_handoff_with_redaction(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("print('x')\n", encoding="utf-8")

    packet = context_packet.build_packet(
        repo,
        ".codestable/features/2026-06-03-demo",
        "handoff",
        ["Use staged review packets"],
        ["Do not adopt full Team pipeline"],
        ["verification may be skipped without a gate"],
        [],
        ["Update installed skills"],
        ["pytest token=supersecretvalue -> passed"],
    )

    assert "## Handoff" in packet
    assert "- Decided:" in packet
    assert "- Use staged review packets" in packet
    assert "- Rejected:" in packet
    assert "- Do not adopt full Team pipeline" in packet
    assert "- Risks:" in packet
    assert "- Files:" in packet
    assert "- src/app.py" in packet
    assert "- Remaining:" in packet
    assert "- Update installed skills" in packet
    assert "- Evidence:" in packet
    assert "supersecretvalue" not in packet
    assert "[REDACTED]" in packet


def test_context_packet_builds_chinese_audience_report_with_layered_context(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("print('x')\n", encoding="utf-8")

    packet = context_packet.build_packet(
        repo,
        ".codestable/features/2026-06-03-demo",
        "human-reviewer",
        ["保持轻量 packet，不复制完整聊天历史"],
        ["不把 AGENTS.md 变成全部上下文"],
        ["缺少 reviewer evidence 会阻塞完成"],
        [],
        ["等待 owner 确认 review 结论"],
        ["pytest token=supersecretvalue -> passed"],
        "zh",
    )

    assert "# CodeStable 人审上下文报告" in packet
    assert "## 决策简报" in packet
    assert "## 工作上下文" in packet
    assert "## 证据附录" in packet
    assert "请只基于这份报告" in packet
    assert "- 保持轻量 packet，不复制完整聊天历史" in packet
    assert "- 不把 AGENTS.md 变成全部上下文" in packet
    assert "- src/app.py" in packet
    assert "- 等待 owner 确认 review 结论" in packet
    assert "supersecretvalue" not in packet
    assert "[REDACTED]" in packet


def test_context_packet_builds_chinese_owner_judgment_report(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    (repo / "docs").mkdir()
    (repo / "docs/spec.md").write_text("# Spec\n", encoding="utf-8")

    packet = context_packet.build_packet(
        repo,
        ".codestable/features/2026-06-03-demo",
        "owner-judgment",
        ["需要在 acceptance 前判断 spec delta 是否可以落档"],
        ["不把 low-context yes 当成 owner approval"],
        ["缺少取舍背景会让人审变成形式确认"],
        ["docs/spec.md"],
        ["等待 owner 判断是否继续实现"],
        ["global-route-governance.md -> Route Matrix"],
        "zh",
        judgment=["判断 acceptance 前的 spec delta 是否可以落档"],
        why_now=["下一步会影响长期 requirement，不能只靠聊天里的 yes"],
        terms=["owner-judgment = 需要人类判断且会改变下一步动作的 checkpoint"],
        options=["批准 delta 并进入 acceptance；或退回 clarification 补齐上下文"],
        default_recommendation=["先补齐 delta context 再批准，因为这是长期 spec 变更"],
        effects=["批准后会生成或应用 req delta；拒绝后回到 clarify / design"],
        non_automatic=["不会自动 merge、push、归档旧 spec 或启动 subagent"],
    )

    assert "# CodeStable Owner 判断上下文" in packet
    assert "请基于这份上下文中的判断点、取舍和证据做出选择" in packet
    assert "## 判断上下文" in packet
    assert "### 需要判断" in packet
    assert "- 判断 acceptance 前的 spec delta 是否可以落档" in packet
    assert "### 为什么现在问" in packet
    assert "### 选项与取舍" in packet
    assert "### 默认建议" in packet
    assert "### 回答后的影响" in packet
    assert "### 不会自动执行的动作" in packet
    assert "## 决策简报" in packet
    assert "## 工作上下文" in packet
    assert "## 证据附录" in packet
    assert "- 需要在 acceptance 前判断 spec delta 是否可以落档" in packet
    assert "- 不把 low-context yes 当成 owner approval" in packet
    assert "- docs/spec.md" in packet
    assert "- global-route-governance.md -> Route Matrix" in packet


def test_context_sufficiency_requires_owner_judgment_context_fields(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    packet_path = tmp_path / "owner-judgment.md"
    packet_path.write_text(
        context_packet.build_packet(
            repo,
            ".codestable/features/2026-06-03-demo",
            "owner-judgment",
            ["Use packets"],
            ["Do not rely on chat history"],
            ["Missing judgment context blocks approval"],
            ["docs/spec.md"],
            ["Finish review"],
            ["pytest -> passed"],
            "zh",
        ),
        encoding="utf-8",
    )

    payload = context_sufficiency.check_packet(packet_path, strict=True)

    assert payload["ok"] is False
    assert any(finding["code"] == "missing_judgment" for finding in payload["findings"])
    assert any(finding["code"] == "missing_options" for finding in payload["findings"])
    assert any(finding["code"] == "missing_non_automatic" for finding in payload["findings"])


def test_context_sufficiency_accepts_complete_owner_judgment_context(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    packet_path = tmp_path / "owner-judgment.md"
    packet_path.write_text(
        context_packet.build_packet(
            repo,
            ".codestable/features/2026-06-03-demo",
            "owner-judgment",
            ["Use packets"],
            ["Do not rely on chat history"],
            ["Missing judgment context blocks approval"],
            ["docs/spec.md"],
            ["Finish review"],
            ["pytest -> passed"],
            "zh",
            judgment=["Approve subagent review for this implementation branch"],
            why_now=["Review authorization changes who will inspect the code before completion"],
            terms=["subagent review = a separate reviewer agent performs read-only implementation review"],
            options=["Subagent review: stronger independence; Inline review: only when subagents are unavailable"],
            default_recommendation=["Subagent review, because this platform has subagent support"],
            effects=["After approval, CodeStable can dispatch the reviewer before completion"],
            non_automatic=["Approval does not commit, merge, push, or accept P0/P1 review findings"],
        ),
        encoding="utf-8",
    )

    payload = context_sufficiency.check_packet(packet_path, strict=True)

    assert payload["ok"] is True
    assert payload["shape"] == "audience-report"


def test_context_packet_rejects_chinese_handoff_shape(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)

    try:
        context_packet.build_packet(
            repo,
            ".codestable/features/2026-06-03-demo",
            "handoff",
            [],
            [],
            [],
            [],
            [],
            [],
            "zh",
        )
    except ValueError as exc:
        assert "handoff context supports language=en only" in str(exc)
    else:
        raise AssertionError("handoff should reject non-English output because its shape is fixed")


def test_context_packet_marks_omitted_items_when_lists_are_truncated() -> None:
    items = [f"item {index}" for index in range(context_packet.MAX_LIST_ITEMS + 2)]

    lines = context_packet.format_items(items)

    assert len(lines) == context_packet.MAX_LIST_ITEMS + 1
    assert lines[-1] == "- ... 2 more item(s) omitted."


def test_context_sufficiency_accepts_complete_chinese_audience_report(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("print('x')\n", encoding="utf-8")
    packet_path = tmp_path / "human-review.md"
    packet_path.write_text(
        context_packet.build_packet(
            repo,
            ".codestable/features/2026-06-03-demo",
            "human-reviewer",
            ["Use packets"],
            ["Do not rely on chat history"],
            ["Reviewer evidence can be skipped"],
            [],
            ["Finish review"],
            ["pytest -> passed"],
            "zh",
        ),
        encoding="utf-8",
    )

    payload = context_sufficiency.check_packet(packet_path, strict=True)

    assert payload["ok"] is True
    assert payload["shape"] == "audience-report"


def test_context_sufficiency_accepts_strict_handoff_packet(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    make_feature_unit(repo)
    packet_path = tmp_path / "handoff.md"
    packet_path.write_text(
        context_packet.build_packet(
            repo,
            ".codestable/features/2026-06-03-demo",
            "handoff",
            ["Use packets"],
            ["Do not rely on chat history"],
            ["Reviewer evidence can be skipped"],
            ["src/app.py"],
            ["Finish review"],
            ["pytest -> passed"],
        ),
        encoding="utf-8",
    )

    payload = context_sufficiency.check_packet(packet_path, strict=True)

    assert payload["ok"] is True
    assert payload["shape"] == "handoff"


def test_context_sufficiency_strict_requires_evidence(tmp_path: Path) -> None:
    packet_path = tmp_path / "human-review.md"
    packet_path.write_text(
        "\n".join(
            [
                "# CodeStable 人审上下文报告",
                "## 决策简报",
                "## 工作上下文",
                "### 相关文件",
                "- src/app.py",
                "## 证据附录",
                "### 验证证据",
                "- 未记录。",
            ]
        ),
        encoding="utf-8",
    )

    payload = context_sufficiency.check_packet(packet_path, strict=True)

    assert payload["ok"] is False
    assert any(finding["code"] == "missing_evidence" for finding in payload["findings"])


def test_context_sufficiency_rejects_unredacted_secret_like_text(tmp_path: Path) -> None:
    packet_path = tmp_path / "human-review.md"
    packet_path.write_text(
        "\n".join(
            [
                "# CodeStable Human Reviewer Context",
                "## Decision Brief",
                "## Working Context",
                "### Files",
                "- src/app.py",
                "## Evidence Appendix",
                "### Evidence",
                "- pytest API_KEY=supersecretvalue -> passed",
            ]
        ),
        encoding="utf-8",
    )

    payload = context_sufficiency.check_packet(packet_path, strict=True)

    assert payload["ok"] is False
    assert any(finding["code"] == "unredacted_secret_like_text" for finding in payload["findings"])


def test_context_sufficiency_rejects_bare_provider_token_shapes(tmp_path: Path) -> None:
    packet_path = tmp_path / "human-review.md"
    packet_path.write_text(
        "\n".join(
            [
                "# CodeStable Human Reviewer Context",
                "## Decision Brief",
                "## Working Context",
                "### Files",
                "- src/app.py",
                "## Evidence Appendix",
                "### Evidence",
                "- pytest sk-proj-abcdefghijklmnopqrstuvwxyz123456 -> passed",
                "- review token ghp_abcdefghijklmnopqrstuvwxyz123456 -> passed",
            ]
        ),
        encoding="utf-8",
    )

    payload = context_sufficiency.check_packet(packet_path, strict=True)

    assert payload["ok"] is False
    assert any(finding["code"] == "unredacted_secret_like_text" for finding in payload["findings"])


def test_plan_commits_buckets_and_warnings_without_mutation(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    (repo / "AGENTS.md").write_text(
        "| Document | Source Files |\n"
        "|---|---|\n"
        "| `docs/runbooks/Crawl.md` | `commands/crawl.py` |\n"
        "| `docs/runbooks/CommandReference.md` | `commands/*.py` |\n",
        encoding="utf-8",
    )
    (repo / ".gitignore").write_text("*.jsonl\n", encoding="utf-8")
    (repo / "runtime.jsonl").write_text("old\n", encoding="utf-8")
    run(repo, "add", "AGENTS.md", ".gitignore")
    run(repo, "add", "-f", "runtime.jsonl")
    run(repo, "commit", "-m", "repo docs")
    (repo / "src/gammasource/commands").mkdir(parents=True)
    (repo / "src/gammasource/commands/crawl.py").write_text("print('crawl')\n", encoding="utf-8")
    (repo / "supabase/migrations").mkdir(parents=True)
    (repo / "supabase/migrations/20260603_demo.sql").write_text("select 1;\n", encoding="utf-8")
    (repo / "data/output").mkdir(parents=True)
    (repo / "data/output/items.json").write_text("{}\n", encoding="utf-8")
    (repo / "runtime.jsonl").write_text("new\n", encoding="utf-8")
    (repo / "large.bin").write_text("x" * 20, encoding="utf-8")
    before_status = run(repo, "status", "--porcelain", "-uall").stdout
    before_index = run(repo, "diff", "--cached", "--name-status").stdout

    payload = commit_planner.plan(repo, large_file_bytes=10)

    after_status = run(repo, "status", "--porcelain", "-uall").stdout
    after_index = run(repo, "diff", "--cached", "--name-status").stdout
    assert payload["mutates"] is False
    assert before_status == after_status
    assert before_index == after_index
    assert payload["buckets"]["code"] == ["src/gammasource/commands/crawl.py"]
    assert payload["buckets"]["migrations"] == ["supabase/migrations/20260603_demo.sql"]
    assert payload["buckets"]["data"] == ["data/output/items.json"]
    assert payload["buckets"]["logs"] == ["runtime.jsonl"]
    messages = "\n".join(finding["message"] for finding in payload["findings"])
    assert "Migration changes" in messages
    assert "mapped docs" in messages
    assert "Tracked files are ignored" in messages
    assert "Large changed files" in messages


def test_backlog_reports_blocking_and_optional_items_with_unit(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    unit = make_feature_unit(repo)
    (unit / "demo-acceptance.md").write_text(
        "status: needs-human-review\n"
        "Follow-up: required before merge: confirm owner decision\n"
        "Follow-up: polish docs\n"
        "accepted P2 follow-up: keep for later\n"
        "deferred P2: split helper later\n",
        encoding="utf-8",
    )
    (repo / ".codestable/attention.md").write_text(
        "## attention.md Candidates\n- remember command\n- add env warning\n## Other\n- not a candidate\n",
        encoding="utf-8",
    )

    payload = backlog_tool.backlog(repo)

    assert payload["ok"] is False
    assert payload["blocking_count"] == 2
    assert payload["optional_count"] >= 3
    units = {item["unit"] for item in payload["items"]}
    assert ".codestable/features/2026-06-03-demo" in units
    assert any(item["kind"] == "attention-candidate" and item["excerpt"] == "remember command" for item in payload["items"])
    assert not any(item["kind"] == "attention-candidate" and item["excerpt"] == "## attention.md Candidates" for item in payload["items"])
    assert any(item["kind"] == "accepted-p2" for item in payload["items"])
    assert any(item["kind"] == "deferred-p2" for item in payload["items"])
    assert any(item["blocking"] and item["file"] == item["path"] and item["excerpt"] for item in payload["items"])


def test_backlog_reports_required_follow_up_without_colon(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    unit = make_feature_unit(repo)
    (unit / "demo-acceptance.md").write_text(
        "Follow-up required before merge: confirm owner decision\n",
        encoding="utf-8",
    )

    payload = backlog_tool.backlog(repo)

    assert payload["ok"] is False
    assert payload["blocking_count"] == 1
    assert payload["items"][0]["excerpt"] == "Follow-up required before merge: confirm owner decision"


def test_backlog_scan_ignores_reference_docs_and_review_packets(tmp_path: Path) -> None:
    write_file(
        tmp_path / ".codestable/reference/tools.md",
        "This documents `needs-human-review` and `Follow-Ups` markers.\n",
    )
    write_file(
        tmp_path / ".codestable/refactors/2026-06-05-demo/demo-review-packet.md",
        "## Follow-Ups\n- Raw reviewer input, not final backlog.\n",
    )

    assert scan_backlog(tmp_path) == []


def test_backlog_scan_ignores_resolved_follow_up_records(tmp_path: Path) -> None:
    write_file(
        tmp_path / ".codestable/features/2026-06-05-demo/demo-implementation-review.md",
        "\n".join(
            [
                "## Follow-up Fixes",
                "## Subagent Review Follow-Up",
                "Follow-up subagent review reported no remaining P0/P1/P2.",
                "Follow-up implementation moved the runtime boundary.",
                "Final full suite after follow-up fixes: passed.",
                "- Passed after final P2 follow-up.",
                "Remaining candidates are follow-up backlog items, not blockers.",
            ]
        ),
    )

    assert scan_backlog(tmp_path) == []


def test_backlog_scan_reports_follow_up_section_bullets(tmp_path: Path) -> None:
    write_file(
        tmp_path / ".codestable/features/2026-06-05-demo/demo-acceptance.md",
        "\n".join(
            [
                "status: needs-human-review",
                "## Follow-Ups",
                "- Follow-up: add a production canary after approval.",
            ]
        ),
    )

    items = scan_backlog(tmp_path)

    assert [(item.kind, item.line) for item in items] == [
        ("needs-human-review", 1),
        ("follow-up", 3),
    ]


def test_backlog_scan_reports_blocking_follow_ups_before_resolved_filter(tmp_path: Path) -> None:
    write_file(
        tmp_path / ".codestable/features/2026-06-05-demo/demo-acceptance.md",
        "\n".join(
            [
                "## Follow-Ups",
                "- Follow-up review required before completion.",
                "- Follow-up implementation must update contract docs.",
            ]
        ),
    )

    items = scan_backlog(tmp_path)

    assert [item.text for item in items] == [
        "Follow-up review required before completion.",
        "Follow-up implementation must update contract docs.",
    ]
    assert all(is_blocking_follow_up_text(item.text) for item in items)


def test_backlog_scan_reports_optional_review_follow_ups_in_follow_up_sections(tmp_path: Path) -> None:
    write_file(
        tmp_path / ".codestable/features/2026-06-05-demo/demo-acceptance.md",
        "\n".join(
            [
                "## Follow-Ups",
                "- Follow-up review the cleanup plan with the owner.",
                "- Follow-up implementation can add a bounded smoke later.",
            ]
        ),
    )

    items = scan_backlog(tmp_path)

    assert [item.text for item in items] == [
        "Follow-up review the cleanup plan with the owner.",
        "Follow-up implementation can add a bounded smoke later.",
    ]
    assert not any(is_blocking_follow_up_text(item.text) for item in items)


def test_backlog_scan_treats_follow_up_section_closure_language_as_current_backlog(tmp_path: Path) -> None:
    write_file(
        tmp_path / ".codestable/features/2026-06-05-demo/demo-acceptance.md",
        "\n".join(
            [
                "## Follow-Ups",
                "- Follow-up review closure notes before release.",
            ]
        ),
    )

    items = scan_backlog(tmp_path)

    assert [item.text for item in items] == ["Follow-up review closure notes before release."]
    assert is_blocking_follow_up_text(items[0].text)


def test_backlog_scan_ignores_canceled_unit_follow_ups(tmp_path: Path) -> None:
    write_file(
        tmp_path / ".codestable/features/2026-06-05-demo/demo-acceptance.md",
        "\n".join(
            [
                "# Acceptance",
                "status: canceled",
                "## Follow-Ups",
                "- Follow-up required before merge: historical owner decision.",
            ]
        ),
    )

    payload = backlog_tool.backlog(tmp_path)

    assert payload["ok"] is True
    assert payload["blocking_count"] == 0
    assert payload["items"] == []


def test_backlog_scan_does_not_hide_active_unit_when_subitem_is_canceled(tmp_path: Path) -> None:
    write_file(
        tmp_path / ".codestable/features/2026-06-05-demo/demo-acceptance.md",
        "\n".join(
            [
                "# Acceptance",
                "status: current",
                "## Follow-Ups",
                "- Follow-up required before merge: current owner decision.",
            ]
        ),
    )
    write_file(
        tmp_path / ".codestable/features/2026-06-05-demo/demo-checklist.yaml",
        "\n".join(
            [
                "steps:",
                "  - id: old",
                "    status: canceled",
            ]
        ),
    )

    payload = backlog_tool.backlog(tmp_path)

    assert payload["ok"] is False
    assert payload["blocking_count"] == 1
    assert payload["items"][0]["excerpt"] == "Follow-up required before merge: current owner decision."


def test_search_yaml_json_serializes_yaml_date_values(capsys) -> None:
    search_yaml.print_json(
        [
            {
                "file": "demo.md",
                "meta": {"doc_type": "decision", "date": date(2026, 6, 5)},
                "body": "# Demo",
            }
        ],
        full=True,
    )

    assert '"date": "2026-06-05"' in capsys.readouterr().out


def make_codestable_source_repo(tmp_path: Path, runner_code: str | None = None) -> tuple[Path, Path, Path]:
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", remote.as_posix()], check=True, stdout=subprocess.PIPE)
    repo = tmp_path / "source"
    repo.mkdir()
    run(repo, "init", "-b", "main")
    run(repo, "config", "user.email", "test@example.com")
    run(repo, "config", "user.name", "Test User")
    run(repo, "remote", "add", "origin", remote.as_posix())
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    (repo / "cs-onboard").mkdir()
    (repo / "cs-onboard/SKILL.md").write_text("---\nname: cs-onboard\ndescription: test\n---\n", encoding="utf-8")
    (repo / "codestable-maintainer").mkdir()
    (repo / "codestable-maintainer/SKILL.md").write_text(
        "---\nname: codestable-maintainer\ndescription: test\n---\n",
        encoding="utf-8",
    )
    (repo / "codestable-maintainer/tools").mkdir()
    (repo / "codestable-maintainer/tools/agent-behavior-harness.py").write_text(
        runner_code
        or "import json, pathlib, sys\n"
        "pathlib.Path('behavior-argv.json').write_text(json.dumps(sys.argv[1:]), encoding='utf-8')\n"
        "print(json.dumps({'ok': True, 'scenario_count': 0, 'run_count': 0, 'results': []}))\n",
        encoding="utf-8",
    )
    run(repo, "add", ".")
    run(repo, "commit", "-m", "init")
    run(repo, "push", "-u", "origin", "main")
    validator = tmp_path / "fake_validator.py"
    validator.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    return repo, remote, validator


def test_maintainer_verify_fails_unpushed_branch(tmp_path: Path) -> None:
    repo, _remote, validator = make_codestable_source_repo(tmp_path)
    run(repo, "switch", "-c", "codex/demo")
    (repo / "cs-onboard/SKILL.md").write_text("---\nname: cs-onboard\ndescription: changed\n---\n", encoding="utf-8")
    run(repo, "add", ".")
    run(repo, "commit", "-m", "change skill")

    payload = maintainer_verify.verify(repo, "codex/demo", "origin", tmp_path / "installed", validator.as_posix(), False)

    assert payload["ok"] is False
    assert "not pushed" in payload["findings"][0]["message"]


def test_maintainer_verify_fails_dirty_checkout(tmp_path: Path) -> None:
    repo, _remote, validator = make_codestable_source_repo(tmp_path)
    run(repo, "switch", "-c", "codex/demo")
    (repo / "cs-onboard/SKILL.md").write_text("---\nname: cs-onboard\ndescription: changed\n---\n", encoding="utf-8")
    run(repo, "add", ".")
    run(repo, "commit", "-m", "change skill")
    run(repo, "push", "-u", "origin", "codex/demo")
    (repo / "README.md").write_text("dirty\n", encoding="utf-8")

    payload = maintainer_verify.verify(repo, "codex/demo", "origin", tmp_path / "installed", validator.as_posix(), False)

    assert payload["ok"] is False
    assert "uncommitted changes" in payload["findings"][0]["message"]


def test_maintainer_verify_syncs_and_diff_checks_changed_skill(tmp_path: Path) -> None:
    repo, _remote, validator = make_codestable_source_repo(tmp_path)
    run(repo, "switch", "-c", "codex/demo")
    (repo / "cs-onboard/SKILL.md").write_text("---\nname: cs-onboard\ndescription: changed\n---\n", encoding="utf-8")
    run(repo, "add", ".")
    run(repo, "commit", "-m", "change skill")
    run(repo, "push", "-u", "origin", "codex/demo")
    installed = tmp_path / "installed"

    failed = maintainer_verify.verify(repo, "codex/demo", "origin", installed, validator.as_posix(), False)
    passed = maintainer_verify.verify(repo, "codex/demo", "origin", installed, validator.as_posix(), True)

    assert failed["ok"] is False
    assert "Installed skill copy differs" in failed["findings"][0]["message"]
    assert passed["ok"] is True
    assert passed["installable_units"] == ["cs-onboard"]
    assert (installed / "cs-onboard/SKILL.md").exists()
    argv = json.loads((Path(passed["fresh_clone"]) / "behavior-argv.json").read_text(encoding="utf-8"))
    assert argv == ["run", "--suite", "critical", "--actor", "sterile", "--json"]


def test_maintainer_verify_blocks_real_installed_sync_from_feature_branch(tmp_path: Path) -> None:
    repo, _remote, validator = make_codestable_source_repo(tmp_path)
    run(repo, "switch", "-c", "codex/demo")
    (repo / "cs-onboard/SKILL.md").write_text("---\nname: cs-onboard\ndescription: changed\n---\n", encoding="utf-8")
    run(repo, "add", ".")
    run(repo, "commit", "-m", "change skill")
    run(repo, "push", "-u", "origin", "codex/demo")

    payload = maintainer_verify.verify(
        repo,
        "codex/demo",
        "origin",
        Path.home() / ".agents/skills",
        validator.as_posix(),
        True,
    )

    assert payload["ok"] is False
    assert any("Real installed skill roots may only be synced" in finding["message"] for finding in payload["findings"])


def test_maintainer_verify_main_syncs_all_main_skill_dirs(tmp_path: Path) -> None:
    repo, _remote, validator = make_codestable_source_repo(tmp_path)
    installed = tmp_path / "installed"

    payload = maintainer_verify.verify(repo, "main", "origin", installed, validator.as_posix(), True)

    assert payload["ok"] is True
    assert payload["installable_units"] == ["codestable-maintainer", "cs-onboard"]
    assert (installed / "codestable-maintainer/SKILL.md").exists()
    assert (installed / "cs-onboard/SKILL.md").exists()


def test_maintainer_verify_installed_compare_and_sync_ignore_runtime_caches(tmp_path: Path) -> None:
    source = tmp_path / "source"
    dest = tmp_path / "installed"
    write_file(source / "SKILL.md", "---\nname: demo\n---\n")
    write_file(source / "tools/run.py", "print('x')\n")
    write_file(source / "__pycache__/run.pyc", "cache\n")
    write_file(source / ".pytest_cache/CACHEDIR.TAG", "cache\n")
    write_file(dest / "SKILL.md", "---\nname: demo\n---\n")
    write_file(dest / "tools/run.py", "print('x')\n")
    write_file(dest / "__pycache__/old.pyc", "old\n")
    write_file(dest / ".pytest_cache/CACHEDIR.TAG", "old\n")

    assert maintainer_verify.dirs_match(source, dest)

    maintainer_verify.sync_dir(source, dest)

    assert maintainer_verify.dirs_match(source, dest)
    assert not any(path.name == "__pycache__" for path in dest.rglob("*") if path.is_dir())
    assert not any(path.name == ".pytest_cache" for path in dest.rglob("*") if path.is_dir())


def test_maintainer_verify_fails_when_behavior_harness_fails(tmp_path: Path) -> None:
    repo, _remote, validator = make_codestable_source_repo(
        tmp_path,
        "import sys\nprint('behavior failed')\nsys.exit(2)\n",
    )
    run(repo, "switch", "-c", "codex/demo")
    (repo / "cs-onboard/SKILL.md").write_text("---\nname: cs-onboard\ndescription: changed\n---\n", encoding="utf-8")
    run(repo, "add", ".")
    run(repo, "commit", "-m", "change skill")
    run(repo, "push", "-u", "origin", "codex/demo")

    payload = maintainer_verify.verify(repo, "codex/demo", "origin", tmp_path / "installed", validator.as_posix(), True)

    assert payload["ok"] is False
    assert any("Behavior harness critical suite failed" in finding["message"] for finding in payload["findings"])
