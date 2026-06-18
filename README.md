<div align="center">

# CodeStable

![](./asset/PromotionalImage.png)

[English](./README.en.md) · **中文**

**面向严肃工程的 AI 编码工作流**

厌倦了 OpenSpec 的草台、Oh-My-OpenAgent 的过度设计、Superpowers 的散装：CodeStable 是一套轻量、可落地、围绕**人在环**的软件生命周期 harness。

<p>
  <img src="https://img.shields.io/badge/status-beta-F59E0B?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/skills-29-6366F1?style=flat-square" alt="Skills"/>
  <img src="https://img.shields.io/badge/license-MIT-10B981?style=flat-square" alt="License"/>
</p>

</div>

---

## 安装

```bash
npx skills add https://github.com/stellazhan/CodeStable
```

新仓库先接入：

```bash
/cs-onboard
```

日常不知道该用哪个技能时，喊根入口：

```bash
/cs
```

如果 agent 支持自动 skill 触发，`using-codestable` 会在已接入仓库中检查 `.codestable/attention.md`，并把 goal、feature、bug、refactor、architecture、requirements、roadmap、audit、docs、decision、learning、explore 等生命周期任务默认路由到 `cs`。

---

## CodeStable 解决什么

主流 AI 编码框架多在编排 agent：分角色、组队、自动接力、互相评审。CodeStable 编排的是软件本身的生命周期：需求、架构、路线图、特性、问题、决策和沉淀。

<table>
<tr><th></th><th>Agent 编排派</th><th>CodeStable</th></tr>
<tr><td><b>核心实体</b></td><td>Agent / Role / Team</td><td>Requirement / Architecture / Feature / Issue / Decision</td></tr>
<tr><td><b>主线问题</b></td><td>Agent 之间怎么协作</td><td>软件的约束、历史和决策怎么被记录、检索、复用</td></tr>
<tr><td><b>状态存在哪</b></td><td>Agent session / 队列 / 消息总线</td><td>项目里的 <code>.codestable/</code> 文件树</td></tr>
<tr><td><b>对人的定位</b></td><td>越少介入越好</td><td>人在环，程序员对整体把控负责，AI 是执行体</td></tr>
</table>

![](./asset/CodeStableVSAgent.png)

CodeStable 的判断是：严肃软件工程的混乱，很多时候不是 agent 不够强，而是需求、架构、历史约束和决策没有被组织好。Agent 再强，也救不了一个把上下文和软件要素全丢掉的项目。

---

## 核心模型

### 7 个实体

| 实体 | 目录 | 职责 |
|---|---|---|
| 需求 | `.codestable/requirements/` | 记录能力愿景：用户需要什么、系统提供什么、边界在哪 |
| 架构 | `.codestable/architecture/` | 只记系统现状，不写未来计划 |
| 路线图 | `.codestable/roadmap/` | 把大需求拆成概设、接口契约和可执行 feature 清单 |
| 目标 | `.codestable/goals/` | 限定起点和终点，AI 自主迭代并写中英文报告 |
| 特性 | `.codestable/features/` | 从 design 到 implementation 到 acceptance 的闭环 |
| 问题 | `.codestable/issues/` | 从 report 到 root-cause analysis 到 fix-note 的闭环 |
| 知识 | `.codestable/compound/` | learning / trick / decision / explore 的统一沉淀库 |

### 4 个主流程

| 流程 | 技能链 | 说明 |
|---|---|---|
| 特性引入 | `cs-feat` -> `cs-feat-design` -> `cs-feat-impl` -> `cs-feat-accept` | 想清楚、写方案、按清单实现、对照验收 |
| 目标达成 | `cs-goal` | 先 grill 对齐，再自主实现、验证、迭代，直到完成或阻塞 |
| 问题修改 | `cs-issue` -> `cs-issue-report` -> `cs-issue-analyze` -> `cs-issue-fix` | 先记录现象，再找根因，最后定点修复 |
| 代码重构 | `cs-refactor` / `cs-refactor-ff` | 行为不变、结构变；完整流程分 scan / design / apply |

`cs-brainstorm` 是模糊想法的讨论入口，`cs-roadmap` 承接单个 feature 吃不下的大需求，`cs-audit` 用来主动发现风险但不直接修。

---

## 技能总览

<table>
<tr><th>分组</th><th>技能</th><th>用途</th></tr>
<tr><td><b>自动入口</b></td><td><code>using-codestable</code></td><td>在已接入仓库中把生命周期任务路由到 <code>cs</code></td></tr>
<tr><td><b>根入口</b></td><td><code>cs</code></td><td>介绍体系，并把开放式诉求路由到正确的 cs 子技能</td></tr>
<tr><td><b>接入</b></td><td><code>cs-onboard</code></td><td>为新仓库或已有零散文档的仓库创建 / 迁移 CodeStable 骨架</td></tr>
<tr><td rowspan="2"><b>需求 & 架构</b></td><td><code>cs-req</code></td><td>维护能力愿景文档，支持 draft / current / outdated</td></tr>
<tr><td><code>cs-arch</code></td><td>维护只记现状的架构地图，不承载未来规划</td></tr>
<tr><td rowspan="3"><b>规划 & 讨论</b></td><td><code>cs-goal</code></td><td>限定起点/终点的目标达成：轻量 grill、自主迭代、中英文报告</td></tr>
<tr><td><code>cs-roadmap</code></td><td>为大需求生成概设、接口契约和子 feature 清单</td></tr>
<tr><td><code>cs-brainstorm</code></td><td>想法模糊时先讨论和分诊：直接 design、轻量 feature、或 roadmap</td></tr>
<tr><td rowspan="5"><b>特性流程</b></td><td><code>cs-feat</code></td><td>新功能子流程入口，只路由不代跑阶段</td></tr>
<tr><td><code>cs-feat-design</code></td><td>起草 <code>{slug}-design.md</code> 和 <code>{slug}-checklist.yaml</code></td></tr>
<tr><td><code>cs-feat-impl</code></td><td>按 checklist 推进实现，遇到方案外情况回方案谈</td></tr>
<tr><td><code>cs-feat-accept</code></td><td>验收实现，并同步 architecture / requirement delta / roadmap 状态</td></tr>
<tr><td><code>cs-feat-ff</code></td><td>小需求快速通道：不写完整 design，但保留可追溯 note</td></tr>
<tr><td rowspan="4"><b>问题流程</b></td><td><code>cs-issue</code></td><td>bug 修复子流程入口</td></tr>
<tr><td><code>cs-issue-report</code></td><td>只记录现象、复现和影响，不猜根因</td></tr>
<tr><td><code>cs-issue-analyze</code></td><td>读代码定位根因，给 2-3 个修复方案让 owner 拍板</td></tr>
<tr><td><code>cs-issue-fix</code></td><td>按已确认方案定点修复、验证、写 fix-note</td></tr>
<tr><td rowspan="2"><b>重构流程</b></td><td><code>cs-refactor</code></td><td>结构 / 性能 / 可读性优化的完整流程</td></tr>
<tr><td><code>cs-refactor-ff</code></td><td>小范围行为等价优化的快速通道</td></tr>
<tr><td rowspan="2"><b>审计 & 探索</b></td><td><code>cs-audit</code></td><td>主动扫描 bug 隐患、安全风险、性能问题、维护债、架构偏离</td></tr>
<tr><td><code>cs-explore</code></td><td>把定向代码探索沉淀成可复用证据</td></tr>
<tr><td rowspan="4"><b>知识沉淀</b></td><td><code>cs-learn</code></td><td>沉淀坑点和最佳实践</td></tr>
<tr><td><code>cs-trick</code></td><td>沉淀可复用模式、库用法和技术技巧</td></tr>
<tr><td><code>cs-decide</code></td><td>记录已拍板的技术选型、架构决定和长期约束</td></tr>
<tr><td><code>cs-note</code></td><td>把短、稳、每次启动都该知道的项目注意事项写入 <code>.codestable/attention.md</code></td></tr>
<tr><td rowspan="2"><b>外部文档</b></td><td><code>cs-guide</code></td><td>写开发者指南 / 用户指南，默认输出到 <code>docs/dev/</code> 和 <code>docs/user/</code></td></tr>
<tr><td><code>cs-libdoc</code></td><td>给公开 API、组件、命令写逐条目参考文档，默认输出到 <code>docs/api/</code></td></tr>
<tr><td><b>浏览器</b></td><td><code>browser-bridge</code></td><td>通过 Chrome 扩展做真实浏览器操作、DOM 抽取和组件证据采集</td></tr>
<tr><td><b>维护</b></td><td><code>codestable-maintainer</code></td><td>维护 CodeStable 源仓、harness、fresh clone verifier 和 main-only installed copy sync</td></tr>
</table>

---

## 运行时结构

`/cs-onboard` 完成后，项目根目录会有 `.codestable/`。这是所有 CodeStable 子技能启动时读取和写入的唯一共享工作区。

```text
your-project/
├── .codestable/
│   ├── attention.md                 # 所有 CodeStable 技能启动必读
│   ├── requirements/                # 能力愿景，含 VISION.md
│   ├── architecture/                # 只记现状的系统地图
│   ├── roadmap/                     # 大需求规划和子 feature 清单
│   ├── goals/                       # bounded goal 状态和双语 iteration 报告
│   ├── features/                    # feature design / checklist / review / acceptance
│   ├── issues/                      # report / analysis / review / fix-note
│   ├── refactors/                   # scan / design / checklist / review / apply-notes
│   ├── compound/                    # learning / trick / decision / explore
│   ├── brainstorm/                  # brainstorm spike 临时代码区
│   ├── tools/                       # onboard 释放的共享脚本
│   └── reference/                   # onboard 释放的共享口径
└── docs/                            # cs-guide / cs-libdoc 默认写这里
```

几条硬约束：

- 子技能只读 `.codestable/attention.md` 作为项目注意事项入口，不兼容 `AGENTS.md` / `CLAUDE.md` 作为 CodeStable 状态源。
- 共享口径不放在某个 skill 包里互相引用；`cs-onboard` 会把 `reference/` 和 `tools/` 复制到工作项目的 `.codestable/` 下。
- `requirements/` 和 `architecture/` 是长效档案；`roadmap/` 是规划层；`goals/` 是自主迭代目标；`features/`、`issues/`、`refactors/` 是事件执行记录；`compound/` 是唯一知识沉淀目录。
- 旧版 `codestable/` / `easysdd/` 目录属于历史兼容入口，当前子技能只认 `.codestable/`。

---

## 当前工具层

`cs-onboard` 会释放一组确定性工具到 `.codestable/tools/`，用来补上 agent 容易漂移的边界：

| 工具 | 作用 |
|---|---|
| `codestable-doctor.py` | 汇总当前仓库状态、worktree 状态、review / backlog / inbox 风险 |
| `codestable-ai-branch-guard.py` | 作为 agent hook 阻止 AI 切换主检出分支或在 `main` / `master` 上实现 |
| `codestable-worktree-gate.py` | 在 start / commit / quarantine 三个节点检查是否在正确 worktree 内 |
| `validate-implementation-review.py` | 确认实现类变更有 implementation review 证据 |
| `build-review-packet.py` | 为 implementation / spec / quality review 生成可审查输入包 |
| `build-context-packet.py` | 为 handoff、human reviewer、owner judgment 生成上下文包 |
| `check-context-sufficiency.py` | 检查上下文包是否足够，不允许空洞 review |
| `codestable-finish-worktree.py` | 完成 worktree 时生成 learning / merge readiness 记录 |
| `codestable-worktree-inbox.py` | 在主分支可见地提醒哪些工作分支 ready / stale / blocked |
| `plan-commits.py` | 按 CodeStable 单元和文件归属规划分组提交 |
| `codestable-backlog.py` | 扫描 unresolved follow-up、human-review、P2 和 attention candidates |
| `codestable-spec-governance.py` | 做 spec 路由、delta、clarification、drift inventory 和 acceptance 检查 |
| `search-yaml.py` / `validate-yaml.py` | 检索和校验 frontmatter / YAML 产物 |

---

## Maintainer 与 Harness

CodeStable 自身变更走 `codestable-maintainer`。源仓是 `/Users/qiyuanzhan/code/CodeStable`，installed copies 只是部署产物，不能先改 installed copy。

分支变更推送后，用 verifier 做 fresh clone、技能校验、临时 installed copy 同步和 diff-check：

```bash
tmp_installed="$(mktemp -d)/skills"
python3 codestable-maintainer/tools/verify.py --repo . --branch <branch> --remote origin --installed-root "$tmp_installed" --sync-installed --json
```

真实 `/Users/qiyuanzhan/.agents/skills` 只从远端 `main` 更新。分支合入并推送到 `origin/main` 后再运行：

```bash
python3 codestable-maintainer/tools/verify.py --repo . --branch main --remote origin --installed-root /Users/qiyuanzhan/.agents/skills --sync-installed --json
```

行为回归由 maintainer harness 覆盖：

```bash
python3 codestable-maintainer/tools/agent-behavior-harness.py run --suite critical --actor sterile
```

当前稳定边界：

- `critical` suite 是确定性行为回归，用场景测试覆盖 routing、worktree、review packet、backlog、spec-governance、compact resume 等高风险行为。
- `live` suite 可用 `--actor live-codex` 做人工触发的真实 Codex smoke。
- 调度化 live eval、budget guard、compaction canary、dashboard 仍在 Phase 2，详见 `codestable-maintainer/references/live-eval-phase-2.md`。

---

## 设计哲学

CodeStable 与 OMO 的哲学相反：OMO 认为人介入是失败信号；CodeStable 认为程序员是软件编码里的在环对象。AI 可以高效执行，但需求边界、架构演进、验收标准和取舍仍需要 owner 判断。

软件架构必须可演进、可观测、可控制。CodeStable 不追求全自动幻想，而是让真实项目在上下文膨胀、需求漂移、多人 / 多 agent 接力时还能被人接住。

---

## Roadmap

- [ ] `cs-refactor` 仍在 beta，需要继续强化。
- [ ] Live eval Phase 2：调度化 live smoke、compaction canary、budget guard 和结果 dashboard。

欢迎在 Issue 区贴真实开发困境和重构经验。

---

## Star History

[![Star History Chart](https://api.star-history.com/chart?repos=liuzhengdongfortest/CodeStable&type=date&legend=top-left)](https://www.star-history.com/?repos=liuzhengdongfortest%2FCodeStable&type=date&legend=top-left)

<div align="center">

MIT License · 作者 [@liuzhengdong](https://github.com/liuzhengdongfortest)

</div>
