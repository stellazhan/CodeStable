# CodeStable 工具用法参考

本文件由 `cs-onboard` 复制到项目的 `.codestable/reference/tools.md`，所有 CodeStable 子技能用项目相对路径 `.codestable/reference/tools.md` 引用。

`.codestable/tools/` 下共享脚本的完整用法参考。子技能里只写本技能特有的 1-2 行典型查询；完整语法和示例看这里。

---

## 1. search-yaml.py

通用 YAML frontmatter 搜索工具。从项目根目录运行，无需安装额外依赖（PyYAML 可选，有则用，无则内建 fallback parser）。

### 基本语法

```bash
python3 .codestable/tools/search-yaml.py --dir {目录} [--filter key=value]... [--query "全文关键词"] [--sort-by FIELD [--order asc|desc]] [--full] [--json]
```

### filter 语法

- `key=value`：字段精确匹配（大小写不敏感）
- `key~=value`：字符串字段子串匹配；列表字段元素包含匹配
- `key=a|b|c` / `key~=a|b|c`：同一字段多个候选值，候选之间是 OR；在 PowerShell / Bash 中请给整个 filter 加引号，例如 `--filter "doc_type=decision|explore|learning"`

### 排序语法

- `--sort-by FIELD`：按 frontmatter 字段排序（典型字段：`last_reviewed`、`date`、`updated_at`）
- `--order desc|asc`：`desc` 默认，新的在前；`asc` 老的在前（查"谁最久没更新"用这个）
- 字段缺失 / 值为空的文档一律排到最后，不干扰前排结论

### 常用命令

沉淀类文档统一在 `.codestable/compound/`，用 `doc_type` 字段区分四个子技能的产物，内部还有各自的细分字段：

```bash
# 按 doc_type 筛选
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=learning
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter "doc_type=decision|explore|learning" --filter status=active
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=decision --filter status=active
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=trick --filter status=active
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=explore --filter status=active

# doc_type + 子技能内部细分字段
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=learning --filter track=pitfall
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=decision --filter category=constraint
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=trick --filter type=pattern
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=explore --filter type=question

# 按 tag（列表元素包含匹配）
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter tags~=prisma

# 全文搜索
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --query "shadow database"

# 按领域/框架/语言筛选
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=decision --filter area=frontend
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=trick --filter framework~=vue
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=trick --filter language=typescript

# 搜索 feature 方案 doc
python3 .codestable/tools/search-yaml.py --dir .codestable/features --filter doc_type=feature-design --filter status=approved

# 输出控制
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter doc_type=decision --filter status=active --full
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --filter tags~=llm --json

# 按时间排序
python3 .codestable/tools/search-yaml.py --dir .codestable/compound --sort-by date --order desc                     # 最近归档的在前
python3 .codestable/tools/search-yaml.py --dir .codestable/library-docs --sort-by last_reviewed --order asc         # 最久没 review 的在前（找陈旧文档）
python3 .codestable/tools/search-yaml.py --dir .codestable/guides --filter status=current --sort-by last_reviewed --order asc
```

### 典型使用场景

| 场景 | 命令建议 |
|---|---|
| feature-design 开始前查已有归档 | 搜 `.codestable/compound` 目录，按 `--query "{关键词}"` 全文搜；要分类看就加 `--filter "doc_type=learning\|trick\|decision\|explore"` |
| issue-analyze 根因分析前查历史 | 搜 `.codestable/compound` `--filter doc_type=learning --filter track=pitfall`、再搜 `--filter doc_type=trick --filter type=library`，按相关组件/框架过滤 |
| 归档落盘后查重叠 | 搜 `.codestable/compound --query "{关键词}" --json`，看有无语义重叠 |
| 新人了解项目规约 | `--dir .codestable/compound --filter doc_type=decision --filter status=active` |
| 按技术栈浏览技巧 | `--dir .codestable/compound --filter doc_type=trick --filter language={语言} --filter status=active` |
| 找最久没 review 的库文档 / 指南 | `--dir {目录} --filter status=current --sort-by last_reviewed --order asc` |
| 看最近沉淀了哪些经验 | `--dir .codestable/compound --filter doc_type=learning --sort-by date --order desc` |

---

## 2. validate-yaml.py

YAML 语法校验工具。用于验证 frontmatter 语法和必填字段。

```bash
# 校验单个文件的 YAML 语法
python3 .codestable/tools/validate-yaml.py --file {文件路径} --yaml-only

# 校验必填字段
python3 .codestable/tools/validate-yaml.py --file {文件路径} --require doc_type --require status

# 批量校验目录下所有文件
python3 .codestable/tools/validate-yaml.py --dir {目录} --require doc_type --require status
```

---

## 3. validate-implementation-review.py

实现完成门禁。用于 Stop hook 或手动检查：有实现代码变更时应在 linked worktree 内执行；已完成的 feature / issue / refactor 要有 `{slug}-implementation-review.md`，且默认必须声明 subagent reviewer。

```bash
python3 .codestable/tools/validate-implementation-review.py --root . --json
```

若用户明确要求直接在主 checkout 改代码，可临时显式 override：

```bash
CODESTABLE_ALLOW_MAIN_CHECKOUT_IMPLEMENTATION=1 python3 .codestable/tools/validate-implementation-review.py --root .

# 只有平台确实没有 subagent 能力时，才允许 self-review fallback
CODESTABLE_ALLOW_SELF_REVIEW_FALLBACK=1 python3 .codestable/tools/validate-implementation-review.py --root .
```

配到 Codex / Claude Stop hook 时，可调用 `.codestable/tools/codestable-implementation-gate.sh`。

---

## 4. codestable-doctor.py

CodeStable 生命周期状态检查工具。只读，不修改文件。用于开始工作、恢复上下文、最终汇报前判断当前仓库是否还有阻塞项。

```bash
python3 .codestable/tools/codestable-doctor.py --root . --json
```

JSON 关键字段：

- `status`：`idle` / `planning-safe` / `dirty` / `implementation-active` / `attention-needed` / `blocked`
- `checkout`：当前分支、默认分支、是否 linked worktree
- `dirty_buckets`：按 `code` / `tests` / `docs` / `migrations` / `data` / `logs` / `codestable` / `unknown` 分组的 dirty paths
- `implementation_changes`：会触发 worktree 约束的实现文件
- `backlog`：`needs-human-review`、`Follow-up`、accepted/deferred P2、`attention.md` candidates 等待处理项
- `post_baseline_blocks`：工作树干净但默认分支在 gate baseline 之后出现实现变更的阻塞项
- `findings`：按严重度列出的阻塞或待处理问题
- `next_action`：下一步建议

典型用法：

```bash
# 汇报前确认没有遗漏的人审 / follow-up / worktree 阻塞
python3 .codestable/tools/codestable-doctor.py --root . --json
```

---

## 5. codestable-worktree-gate.py

CodeStable worktree 生命周期门禁。用于实现开始前、提交前、以及误在协调检出开工后的恢复规划。

### start

实现开始前运行。feature / issue / refactor 这类实现单元必须在 linked execution worktree 中开始；如果用户明确批准在主检出中实现，单元目录下必须有 `worktree-override.md`，并写明 reason、scope、approval。

```bash
python3 .codestable/tools/codestable-worktree-gate.py --root . --json start --unit .codestable/features/YYYY-MM-DD-slug
```

通过后 gate 会把 baseline 写入 Git 私有路径，不污染工作树。

### commit

提交或最终汇报前运行。它会阻止：

- 默认分支上 staged implementation changes；
- 工作树干净但默认分支在 start baseline 后已经出现 implementation commits；
- 完成的 implementation unit 缺少 subagent implementation review。

```bash
python3 .codestable/tools/codestable-worktree-gate.py --root . --json commit --unit .codestable/features/YYYY-MM-DD-slug
```

如果 staged 文件横跨 code / docs / data / logs / migrations 等多个 bucket，命令会给出 P2 warning；它不会替你 stage、unstage 或 commit。

### quarantine

误在主协调检出开始实现时，用 quarantine 先生成恢复计划。默认 dry-run，不创建分支、不创建 worktree、不移动文件、不改 index。

```bash
python3 .codestable/tools/codestable-worktree-gate.py --root . --json quarantine --unit .codestable/features/YYYY-MM-DD-slug
```

只有同时满足以下条件才允许创建 quarantine worktree：

- 显式传 `--apply`
- 单元目录存在带 reason / scope / approval 的 `worktree-override.md`
- 没有未跟踪的 `.env`、token、secret 等敏感文件

```bash
python3 .codestable/tools/codestable-worktree-gate.py --root . --json quarantine --unit .codestable/features/YYYY-MM-DD-slug --apply
```

Phase 1 只创建安全 execution worktree，不自动搬 dirty 文件；文件迁移仍由 owner 显式处理。

---

## 6. build-review-packet.py

独立 subagent review 的输入包生成器。它把本次 unit 文档、diff stat、聚焦 diff、验证结果和风险提示整理成一份可发给 reviewer 的 Markdown，并自动隐藏 `.env` / token / secret 类路径和值。`--stage` 用来区分 review 目的，默认 `implementation` 兼容旧调用。

```bash
python3 .codestable/tools/build-review-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --stage quality --output /tmp/codestable-review.md \
  --validation "uv run pytest -> passed" \
  --validation "CLI smoke -> passed"
```

可选 stage：

- `implementation`：旧默认值，综合实现 review。
- `spec`：检查是否严格满足 requirement / report / analysis / design / checklist，重点抓缺失需求、额外行为和范围漂移。
- `quality`：检查可维护性、安全、边界条件、测试缺口、幂等和 crash-resume 等工程质量。
- `verification`：只看 fresh validation evidence；必须传 `--validation` 或 `--validation-file`，不能接受记忆里的“已跑过”。

适用时机：feature / issue / refactor 代码写完、owner 验证命令跑完之后，触发 subagent reviewer 之前。reviewer 只审查，不修改代码。review 结果仍要落到 `{slug}-implementation-review.md`，packet 只是输入材料。

输出内容：

- unit 下的 `.md` / `.yaml` 关键文档；
- unstaged / staged `git diff --stat`；
- 排除 secret-like 路径后的 focused diff；
- owner 传入的验证命令和结果；
- 数据库 / 迁移 / 并发 / 幂等 / crash-resume / provider cost / deterministic LLM boundary 风险提示。

---

## 7. build-context-packet.py

阶段交接上下文和受众报告生成器。它用于给下一阶段 agent、reviewer、human reviewer、owner 或学习者一份可落盘的 context packet，不复制完整聊天历史。

```bash
python3 .codestable/tools/build-context-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --audience handoff --output /tmp/codestable-handoff.md \
  --decided "Use staged review packets" \
  --rejected "Do not adopt full Team pipeline" \
  --risk "Verification can be skipped if no gate enforces evidence" \
  --remaining "Run maintainer verifier after push" \
  --evidence "uvx --with pytest pytest -> passed"
```

生成中文人审 / 决策 / 学习报告：

```bash
python3 .codestable/tools/build-context-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --audience human-reviewer --language zh --output /tmp/codestable-human-review.md \
  --decided "保持轻量 context packet，不复制完整聊天历史" \
  --rejected "不把 AGENTS.md 变成全部上下文" \
  --risk "缺少 reviewer evidence 会阻塞完成" \
  --remaining "等待 owner 确认 review 结论" \
  --evidence "uvx --with pytest pytest -> passed"
```

audience:

- `handoff`：下一阶段 agent / reviewer 的轻量交接。
- `human-reviewer`：给人审的完整 context 报告。
- `owner-decision`：给 owner 拍板风险 / 后续事项的决策简报。
- `learner`：学习报告，解释为什么改、改了什么、如何验证。
- `interviewee`：访谈 / 复盘前的上下文提纲。

handoff 固定输出：

- `Decided`
- `Rejected`
- `Risks`
- `Files`
- `Remaining`
- `Evidence`

非 handoff audience 输出 `Decision Brief` / `Working Context` / `Evidence Appendix` 三层结构；`--language zh` 会输出中文标题和说明。未显式传 `--file` 时，工具会列当前 changed files；secret-like 路径会标记为 redacted，文本中的 token / secret / api key 会被脱敏。handoff 目标长度是 10-20 行，适合在创建下一阶段 subagent 前阅读；受众报告可以更长，但仍只放可验证结论和证据索引。

---

## 8. check-context-sufficiency.py

context packet 完整性检查器。它只读已生成的 handoff / audience report，检查结构是否可识别、是否还有未脱敏 secret-like 文本；`--strict` 还要求有至少一个 concrete file 和 evidence 条目。

```bash
python3 .codestable/tools/check-context-sufficiency.py --file /tmp/codestable-human-review.md --strict --json
```

适用时机：

- dispatch human reviewer / subagent reviewer 前，确认 packet 不依赖隐藏聊天历史。
- 给 owner 决策或学习报告前，确认文件和证据没有空着。
- 发现输出里仍有 token / secret / api key 时，先重新生成或手动脱敏，再发给接收方。

JSON 关键字段：

- `ok`：是否通过。
- `shape`：`handoff` / `audience-report` / `null`。
- `findings`：P1 问题清单，包含 `missing_files`、`missing_evidence`、`unredacted_secret_like_text`、`unknown_context_shape`。

---

## 9. plan-commits.py

提交规划器。只读，不 stage、不 commit。用于提交前把 dirty tree 按逻辑 bucket 拆开，并发现 migration doc-sync、runbook doc-sync、tracked ignored、large file、live writer 等风险。

```bash
python3 .codestable/tools/plan-commits.py --root . --json
```

主要 bucket：

- `code` / `tests` / `docs`
- `migrations` / `database_docs`
- `data`
- `logs`
- `codestable`
- `installed_skill`
- `unknown`

典型 findings：

- migration 有变化但缺少 `docs/database/` 合同文档；
- 项目 `AGENTS.md` 声明了 source ↔ docs 映射，但 source 改了对应 runbook 没改；
- 已追踪文件现在被 `.gitignore` 忽略；
- 大文件或正在被写入的文件混进提交。

这个工具只给出建议。是否拆 commit、怎么 stage，仍由执行者按项目规则决定。

---

## 10. codestable-backlog.py

CodeStable 人审 / 后续事项积压扫描器。它只读 `.codestable/`，用于最终汇报前确认没有把人工决策点或 follow-up 隐藏掉。

```bash
python3 .codestable/tools/codestable-backlog.py --root . --json
```

会扫描：

- `needs-human-review`
- `Human review required`
- 显式 `Follow-up:` 行，以及 `## Follow-Ups` 章节下的 bullet
- accepted / deferred P2
- `attention.md` candidates

扫描会跳过 `.codestable/reference/` 和 `*-review-packet.md`，避免把工具说明或 reviewer 输入包里的示例文字当成当前 backlog。已解决的 follow-up 记录（例如 follow-up fixes / review closure / no remaining P0-P2）不会重复上报；但 `## Follow-Ups` 章节下的 bullet 会被视为当前 backlog。

JSON 每个 item 带 `kind`、`severity`、`blocking`、`file`、`line`、`unit`、`action`、`excerpt`。`needs-human-review` / `Human review required` 一律 P1；带 `required`、`must`、`blocking`、`before merge/publish/release/ship/completion` 的 follow-up 也会升为 P1。其他 follow-up / P2 / attention candidates 是 P2，必须解决、转 issue，或明确延期。
