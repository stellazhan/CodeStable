# CodeStable 共享口径

由 `cs-onboard` 复制到项目的 `.codestable/reference/shared-conventions.md`。所有 CodeStable 子技能用项目相对路径 `.codestable/reference/shared-conventions.md` 引用本文件——跨子技能共享但不适合堆在单个技能里的规范的唯一权威版本。

skill 本身不共享文件系统（每个 skill 是独立安装单元），共享口径不能放在某个 skill 内部被别的 skill 引用。放在"工作项目"里对所有 skill 都可达。

## 0. 目录结构与路径命名

onboard 完成后骨架（`cs-onboard` 负责搭建）：

```
.codestable/
├── attention.md           CodeStable 技能启动必读的项目注意事项
├── requirements/          能力愿景层（"用户需要什么、系统提供什么能力来满足"，过去/现在/未来）
│   ├── VISION.md           中心索引（按 status 分组，每条带 pitch 一句话）
│   └── {slug}.md           一个能力一份，扁平（cs-req 产出）
├── architecture/          架构中心目录（"用什么结构实现"，只记现状）
│   ├── ARCHITECTURE.md    总入口（索引 + 关键架构决定）
│   └── {type}-{slug}.md   子系统 / 模块 doc（cs-arch 产出）
├── roadmap/               规划层（"接下来怎么做这块大需求 + 模块怎么切 + 接口怎么定"）
│   └── {slug}/            一个大需求一个子目录（cs-roadmap 产出）
│       ├── {slug}-roadmap.md   主文档：背景 / 范围 / 模块拆分 / 接口契约 / 子 feature 清单 / 排期
│       ├── {slug}-items.yaml   机器可读子 feature 清单，acceptance 回写状态
│       └── drafts/             可选
├── features/              feature spec 聚合根
│   └── YYYY-MM-DD-{slug}/  每个 feature 一个目录
│       ├── {slug}-brainstorm.md  （可选，case 2 时产出）
│       ├── {slug}-design.md      （标准流程）
│       ├── {slug}-checklist.yaml （标准流程）
│       ├── {slug}-implementation-review.md （实现完成门禁）
│       ├── {slug}-acceptance.md  （标准流程）
│       └── {slug}-ff-note.md     （fastforward 通道唯一产物，与上面四份互斥）
├── issues/                issue spec 聚合根
│   └── YYYY-MM-DD-{slug}/
│       ├── {slug}-report.md
│       ├── {slug}-analysis.md   （根因不显然才有）
│       ├── {slug}-implementation-review.md
│       └── {slug}-fix-note.md
├── refactors/             refactor spec 聚合根
│   └── YYYY-MM-DD-{slug}/
│       ├── {slug}-scan.md
│       ├── {slug}-refactor-design.md
│       ├── {slug}-checklist.yaml
│       ├── {slug}-implementation-review.md
│       └── {slug}-apply-notes.md
├── compound/              沉淀类文档统一目录
│   └── YYYY-MM-DD-{doc_type}-{slug}.md
│                          doc_type ∈ {learning, trick, decision, explore}
├── brainstorm/            brainstorm 阶段 spike 实验代码区（cs-brainstorm 临时产出）
│   └── {slug}/            一次 spike 一个子目录，文件名随意
│                          验完不强制清理，结论回写到对应 brainstorm note
├── tools/                 跨工作流共享脚本（onboard 从技能包释放）
└── reference/             共享参考文档（onboard 从技能包释放）
```

### 命名规则

- 需求文档：`requirements/{slug}.md`（能力愿景，不带日期前缀，扁平不分组）；中心索引 `requirements/VISION.md`
- roadmap：`roadmap/{slug}/`（不带日期前缀，平铺不嵌套）
- feature / issue / refactor 目录：带日期前缀 `YYYY-MM-DD-{slug}`
- 沉淀类：`compound/YYYY-MM-DD-{doc_type}-{slug}.md`，日期用**归档当天**
- 架构 doc：`architecture/{type}-{slug}.md`（长效，不带日期前缀）；总入口固定 `ARCHITECTURE.md`
- 项目注意事项入口固定为 `.codestable/attention.md`，所有 CodeStable 子技能启动前必须读取；不再兼容 `AGENTS.md` / `CLAUDE.md` 等外部入口

### 架构 doc 分组规则（同类聚合）

`architecture/` 下用文件名第一段作 type 标记：`ui-chat.md` 和 `ui-events.md` 同 `ui` 类。**所有架构 doc 必须 `{type}-{slug}.md`**——只有一份的也要带合理 type 段（如 `cli-entry.md`），否则未来同类出现时聚合不了。

**触发**：某 type 在 `architecture/` 根目录达到 ≥6 份时（即新加第 6 份那次），把这一类全部收进同名子目录。

**收入后**：去掉 type 前缀。`ui-chat.md` → `ui/chat.md`。

**只升不降**：删到 ≤5 份也不折回平铺。

**触发时谁负责**：`cs-arch` 的 `backfill` / `update` 模式在 Phase 6 落盘前主动检查并搬迁；命中阈值时这次操作要把"本次新加 / 改的 + 已有同类全部"一起搬，并同步改 `ARCHITECTURE.md` 链接（搬迁本身要在 Phase 5 给用户 review，不偷偷做）。`check` 模式不主动搬迁，但发现 ≥6 仍平铺时在报告末尾列为观察项。

改 `cs-onboard/reference/shared-conventions.md` 模板，新项目 onboard 时带上新版本；已有项目手动同步 `.codestable/reference/shared-conventions.md`。

## 1. 共享元数据口径

**feature spec**：brainstorm / design / acceptance 共用 `doc_type` / `feature` / `status` / `summary` / `tags`。子技能只补特有字段。`status`：brainstorm = `confirmed`（落盘即确认无 draft）；design = `draft` / `approved`；acceptance 见对应技能。

**issue spec**：report / analysis / fix-note 共用 `doc_type` / `issue` / `status` / `tags`。`severity` / `root_cause_type` / `path` 由对应阶段按需补。

**归档类（compound）**：

- learning / trick / decision / explore 四类**统一写入 `.codestable/compound/`**
- 每个文档 frontmatter 顶部带 `doc_type`（learning / trick / decision / explore）作跨子技能归属判定
- 文件名 `YYYY-MM-DD-{doc_type}-{slug}.md`——日期打头便于 `ls` 排序，type 段在中间便于 grep
- 各子技能在 `doc_type` 之外保留专属 frontmatter（learning 的 `track` / trick 的 `type` / decision 的 `category` / explore 的 `type`）
- 各子技能只认自己的 `doc_type` 不读写别家
- `status` 等通用字段语义和本文件保持一致

**外部读者文档**（guidedoc / libdoc）：frontmatter 由各自子技能定义。无特殊说明：`draft` = 待 review，`current` = 当前有效，`outdated` = 代码已变更待同步。

**写作约束**：子技能提字段时优先写"额外字段"或"阶段状态变化"，不重复展开整套通用字段。

## 2. {slug}-checklist.yaml 生命周期

- 是 feature 工作流的唯一执行清单
- 由 `cs-feat-design` 在 design 确认通过后一次生成 `steps` + `checks`
- `cs-feat-ff` **不生成** checklist（也不写 design / acceptance），是跳过 spec 流程直接写代码的超轻量通道；唯一留下的痕迹是动手后回写的 `{slug}-ff-note.md`（轻量回顾，参与 scoped-commit、可被 cs-arch / cs-req backfill 检索到）

`steps` 的粒度是 **编排-计算分离维度的切片策略**——按"先编排骨架、后计算节点、最后持久化与测试"写（最简 Workflow 先行 → 逐个节点填充），**不下沉到 file:line / 函数级**。具体改哪个文件由 implement 阶段决定。

**design 的职责**：

- 提取 `steps`（4-8 步，每步独立可验证退出信号）：后端节奏 = 编排骨架 → 计算节点逐个填 → 接通持久化 → 测试覆盖；前端 = 静态结构 → 交互逻辑 → 状态接入 → 联调收尾
- 提取 `checks`：第 1 节"明确不做"→ 范围守护；第 2.1 接口 → 名词契约；第 2.2 主流程 + 流程级约束 → 编排骨架；第 2.3 挂载点 → 挂载点；第 3 节场景清单 → 验收场景

**implement 的职责**：

- 按 `steps` 顺序执行，每步完成把 status `pending` → `done`
- 实现到具体文件级时需要拆分某步、或发现微重构是其前置（参考第 7 节反射检查）→ 跟用户对齐后追加 / 拆分 steps，**不偷偷做**
- 不改写 `checks`

**acceptance 的职责**：只更新 `checks[].status`（`pending` → `passed` / `failed`），不重写 `steps`。

**写作约束**：子技能描述 checklist 时只补本阶段读 / 写哪一部分，不重新定义生命周期。

## 2.5 roadmap ↔ feature 衔接协议

`.codestable/roadmap/{slug}/{slug}-items.yaml` 是规划层和 feature 执行层的唯一接口。三个技能共同读写它——是 skill 都读写项目共享产物，不算耦合。

**items.yaml 状态机**：

```
planned  → in-progress  （cs-feat-design 启动 feature 时改）
in-progress → done      （cs-feat-accept 验收完成时改）
planned  → dropped      （cs-roadmap update 模式，用户决定不做时改）
```

`done` / `dropped` 是终态。需要回退重做的新加一条 slug 略改的条目，不改终态。

**cs-roadmap 的职责**：生成和维护 roadmap 主文档 + items.yaml；把 `planned` 改 `dropped`（用户放弃时）；不改 `in-progress` / `done`（feature 技能负责）。

**cs-feat-design 的职责**（从 roadmap 起头时）：

1. design.md frontmatter 加 `roadmap: {roadmap-slug}` + `roadmap_item: {子 feature slug}`
2. items.yaml 对应条目 `status: in-progress` + `feature: YYYY-MM-DD-{slug}`
3. 校验 yaml

直接起 feature（非 roadmap 来）两字段留空，不触发 roadmap 写。

**cs-feat-accept 的职责**：

1. 读 design frontmatter `roadmap` / `roadmap_item`
2. 空 → 跳过
3. 有值 → items.yaml 对应条目 `status: done`；同步主文档子 feature 清单显示状态；校验 yaml

回写是**实际写文件的动作**，验收报告要明确记录回写结果。

**最小闭环标记**：items.yaml 每份只有一条 `minimal_loop: true`，标记"做完后系统能端到端跑通最窄路径"。design 启动 `minimal_loop` 条目时优先级最高。

## 2.6 main 协调 + worktree 执行

CodeStable 默认把"讨论 / 计划"和"改代码"拆开：

- **主协调检出**：用户讨论需求、写 design / analysis / roadmap / checklist 的地方，通常是 `main` 分支所在主 checkout。
- **执行 worktree**：真正改代码的地方。每个 feature / issue / refactor 用独立 git worktree 和独立 `codex/...` 分支，除非用户明确要求直接在当前 checkout 做。

### 计划互通面

worktree 之间不要读取彼此未合并的代码 diff；共享信息只通过计划文档传递：

- `.codestable/features/**`、`.codestable/issues/**`、`.codestable/refactors/**`
- `.codestable/roadmap/**`
- `.codestable/compound/**` 中已确认的 decision / explore / trick / learning
- 必要时由用户指定的临时协调文档

如果一个执行 worktree 发现计划需要调整，先把**计划变更**同步回主协调检出或明确提交到共享分支，再让其他 worktree 读取；不要要求其他 agent 直接去 sibling worktree 读未合并代码。

### 创建执行 worktree 前

动代码前先确认：

1. 当前是否在主协调检出讨论 / 写计划；如果不是，说明风险并按用户偏好继续。
2. spec / checklist / analysis 已在共享计划面可读。
3. worktree 路径、分支名、执行范围、禁止触碰的 sibling worktree 已说清楚。
4. worktree 从当前目标基线创建；不要从另一个功能 worktree 派生，除非用户明确要堆叠开发。

实现单元开始前先运行 worktree start gate；子技能应调用项目运行时路径，不调用 CodeStable 源仓库路径：

```bash
python .codestable/tools/codestable-worktree-gate.py --root . --json start --unit .codestable/features/YYYY-MM-DD-{slug}
```

gate 通过后会记录 Git 私有 baseline；这个 baseline 用于后续发现"工作树已经干净，但默认分支在 baseline 后被提交了实现代码"的情况。

推荐命名：

- 分支：`codex/{slug}`
- 路径：项目内 `.codex/worktrees/{slug}`，或用户已有的 worktree 根目录

### worktree 内执行规则

- 只读共享计划面和本 worktree 的代码；不要把 sibling worktree 的代码当事实来源。
- 如果需要知道其他 worktree 的意图，读它已同步到共享计划面的 design / analysis / roadmap / note。
- 如果发现计划冲突，停下来在主协调检出更新计划或请用户裁决，不靠私下读代码猜。
- worktree 环境缺少本地 env / secrets 时，按项目注意事项补齐或明确标为环境 blocker，不把缺失环境误判成代码失败。

### 批次完成后的独立 code review

每个执行 worktree 写完一批可验收代码后，**输出实现完成汇报之前**必须触发一次独立 code review；review 是实现完成门槛，不等到 commit 才补。

1. 必须使用可用的 subagent / reviewer agent；用户已将 CodeStable implementation review 视为长期授权场景，不需要每次再问。先按风险层级用 review packet 工具生成最小必要输入，再发给 reviewer：

```bash
python .codestable/tools/build-review-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --stage quality --output /tmp/codestable-review.md --validation "{验证命令} -> {结果}"
```

packet 应包含目标 spec / analysis、`git diff --stat`、相关 diff、验证命令和结果；不要把 `.env`、token、secret 或本地凭证贴进 review 输入。

风险层级默认值：

- tiny doc / typo：owner 自查即可。
- small local code：一次 subagent quality review，使用 `--stage quality`。
- normal feature / fix：quality review + owner 验证证据；需求容易走偏时补一次 `--stage spec`。
- schema / security / core runtime：必须分别生成 `--stage spec`、`--stage quality`、`--stage verification`，verification stage 必须带 fresh command output，不接受记忆里的“已跑过”。
- large multi-module：采用分阶段执行；每个阶段交接前生成 handoff context，再让下一阶段 agent / reviewer 读取。

多阶段 handoff 用固定轻量格式，不把完整聊天历史塞给下一阶段：

```bash
python .codestable/tools/build-context-packet.py --root . --unit .codestable/features/YYYY-MM-DD-{slug} --audience handoff --output /tmp/codestable-handoff.md --decided "{已决定}" --remaining "{下一步}"
```

handoff 必须包含 `Decided` / `Rejected` / `Risks` / `Files` / `Remaining` / `Evidence` 六项；没有内容也写 `None recorded.`，避免隐性上下文丢失。

2. reviewer 只审查不改代码，输出按严重度排序的 findings；重点看范围漂移、方案偏离、缺测试、隐性行为变化、并发 / 幂等 / crash-resume 风险。
3. P0 / P1 必须修到 reviewer 无阻塞；P2 由用户或 owner 决定修、记后续 issue，或明确接受风险。
4. 只有当前平台确实没有 subagent 能力时，执行 owner 才能做 fresh self-review fallback，并明确写"当前环境没有 subagent 能力，已用本线程复核替代"。不能因为任务小、时间紧、或觉得 reviewer 多余而跳过 subagent。
5. review 结果落到同一 feature / issue / refactor 目录的 `{slug}-implementation-review.md`；最终汇报、fix-note、apply-notes 可摘要引用，但不能替代这份证据文件。

review 文件必须包含单独一行 `reviewer: subagent`，这样 validator 才能确认不是 self-review 解释文本误命中。只有 fallback 时才写 `reviewer: self`，并配合环境变量 `CODESTABLE_ALLOW_SELF_REVIEW_FALLBACK=1`。

review 不是 acceptance 的替代品；它只保证代码批次质量，acceptance 仍按 design / checklist 做闭环。`cs-onboard` 释放的 `.codestable/tools/validate-implementation-review.py` 可作为 Stop hook 门禁：有实现代码变更时必须在 linked worktree 内执行（除非显式 override），已完成的 feature / issue / refactor 必须有 implementation-review 文件。

提交或最终汇报前运行 commit gate：

```bash
python .codestable/tools/codestable-worktree-gate.py --root . --json commit --unit .codestable/features/YYYY-MM-DD-{slug}
```

日常恢复上下文或最终汇报前可运行 doctor：

```bash
python .codestable/tools/codestable-doctor.py --root . --json
```

若只想看未关闭的人审和 follow-up，可运行：

```bash
python .codestable/tools/codestable-backlog.py --root . --json
```

### 复杂实现的 subagent 执行选择

review 强制用 subagent；实现是否用 subagent 取决于复杂度。动手前如果发现这次实现跨 3 个以上子系统、需要并行拆片、涉及高风险迁移 / 并发 / runtime contract，或单线程上下文承载明显吃紧，先停下来问用户是否切换为 subagent-driven implementation。用户同意后按最佳实践拆成互不重叠的写入范围：每个 worker 只负责自己的文件 / 模块，主线程保留集成、验证和最终 review。

## 3. 阶段收尾推荐

**feature-acceptance** 收尾按顺序判断：

1. `cs-learn`：沉淀经验
2. `cs-decide`：长期约束 / 选型
3. `cs-guide`：开发者 / 用户指南
4. `cs-libdoc`：公开 API 参考
5. `scoped-commit`

**issue-fix** 收尾按顺序判断：

1. `cs-learn`：坑点
2. `cs-decide`：暴露的长期约束
3. `scoped-commit`

**feature-ff** 收尾按顺序判断（比标准 acceptance 短，没有 architecture / req 回写动作）：

1. `cs-learn`：动手过程暴露的坑
2. `cs-decide`：动手过程拍板的长期约束
3. `scoped-commit`

**统一规则**：一律一句话提示；用户说"不用"立即跳过；不强制；上游主动提示，下游承接执行。

## 4. 收尾提交（scoped-commit）

acceptance / issue-fix 走完后把本次产物提交为一个 commit：

- **范围**：本次工作改到的代码 + 相关 spec 文档 + 本次实际更新过的架构 doc + 本次实际更新过的 roadmap items.yaml / 主文档
- **不该进**：和本次工作无关的顺手修改；属于"下次另起 feature / issue"的扩大范围
- **提交前确认**：用户没明确同意不要 `git commit`
- **commit message**：一句话说清"做了什么"，不贴 spec 目录路径

提交前先运行 commit planner，确认 dirty tree 需要几个逻辑 commit：

```bash
python .codestable/tools/plan-commits.py --root . --json
```

planner 只读，不替你 stage。它会把 code/docs/tests、migrations/database_docs、data、logs、CodeStable 文档、installed skill deployment、unknown 分开，并提示 migration/database docs、runbook doc-sync、tracked ignored、large file、live writer 风险。

子技能只描述本阶段特有提交范围，通用规则看这里。

## 5. 归档检索规则

feature-design / issue-analyze / issue-fix 动手前到 `.codestable/compound/` 搜已有沉淀：

- 总是先搜 `architecture/` 和 `compound/`
- 在 `compound/` 用 `doc_type` 过滤（learning / trick / decision / explore）
- 搜到的结果只作参考输入，不盲目套用——可能已 `outdated` 或不适合当前上下文
- 搜到和当前方向冲突的 decision → **必须**正面回应"为什么仍然这么做"或调整方向

子技能只补本阶段查询命令。完整搜索语法看 `.codestable/reference/tools.md`。

## 6. 归档类子技能共享守护规则

`cs-learn` / `cs-trick` / `cs-decide` / `cs-explore` 共享下面这组规则。子技能正文只写特有反模式，通用看这里：

1. **只增不删**——已归档除非被明确取代（`status=superseded`）否则不删；理由丢失成本极高
2. **宁缺毋滥**——用户说不出理由的节直接省略，不要 AI 编造
3. **不替用户写实质内容**——AI 负责起草结构和串联语言，实质结论必须来自用户或可追溯的代码证据
4. **attention.md 检查**——写完后若沉淀暴露出"每次启动都该知道"的一两行硬约束，提示用户用 `cs-note` 追加到 `.codestable/attention.md`；不要直接改外部 AI 入口
5. **起草前先查重叠**——动手写前用 `search-yaml.py --query` 查语义相近的旧文档。命中就把候选列给用户在三条路径里选：
   - **更新已有**（默认优先）：沿用原文件名和原创建日期，**不新建**；frontmatter 补 `updated: YYYY-MM-DD`；超出小修在文末加"YYYY-MM-DD 更新"简述
   - **supersede**：旧文档保留原文，`status: superseded` + `superseded-by: {新文件名}`，正文顶部加 `**[已取代]** 见 {新 slug}`；新文档 frontmatter 带 `supersedes: {旧文件名}`
   - **确实是不同主题**：新建，文末"相关文档"列出已有那条说明区别
6. **识别用户意图是"改已有"还是"记新的"**——用户说"改 / 更新 / 修订 / 补充 {某条}"、明确指向某条旧文档、或话题高度重合时默认走"更新已有"，不要闷头新建。分不清就问。

各子技能只认自己的 `doc_type`，不读写别家产物。

## 7. 写代码时的反射检查

`cs-feat-impl` 和 `cs-issue-fix` 共用。AI 默认会往"大函数 / 大文件 / god class / 处处特殊分支"漂，这一节把漂移截在发生那一刻。

**不是阈值，是触发器**——硬数字会诱发为拆而拆把自然聚合的代码切碎。每条都是"遇到 X 情况就停下来问自己"。

| 触发场景 | 停下来问自己 |
|---|---|
| 要往一个已经很长的文件追加代码时 | 文件承担几件事？新加的是已有职责延伸还是第 N+1 件事？是第 N+1 就默认新建文件 |
| 要给已经很多方法的类加方法时 | 新方法是核心职责的自然扩展，还是把类推向"什么都能干"？ |
| 写的函数已超过一屏时 | 函数在做几件事？几件事就拆 |
| 要加 `if (特殊情况) { 特殊处理 }` 分支时 | 抽象维度选错了？正确做法可能是把特殊路径和通用路径分成不同函数 / 策略 / 类 |
| 要 copy-paste 一段代码时 | 能抽成共用还是只字面相似？能抽就抽 |
| 要给函数加第 4+ 个参数时 | 函数做的事是不是太多了？参数列表是 API 恶化的早期信号 |
| 要新写"万能工具类 / helper"时 | 真没归属还是只是想不起来放哪儿就先堆 util？ |

**停下来之后**：反射检查只把问题提出来，结论用户定。停下来想清楚的动作（拆 / 新建 / 重命名 / 抽共用）会让改动超出现有 steps 范围 → 跟用户对齐再决定（纳入当前推进 / 记顺手发现留后续）。

不许偷偷拆完继续写，也不许忽略信号硬冲。默认动作是停、问、再继续。
