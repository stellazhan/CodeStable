<div align="center">

# CodeStable

![](./asset/PromotionalImage.png)

**English** · [中文](./README.md)

**An AI coding workflow for serious software engineering**

Tired of OpenSpec's flimsiness, Oh-My-OpenAgent's over-engineering, and Superpowers' fragmentation: CodeStable is a lightweight, practical, **human-in-the-loop** lifecycle harness for software work.

<p>
  <img src="https://img.shields.io/badge/status-beta-F59E0B?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/skills-28-6366F1?style=flat-square" alt="Skills"/>
  <img src="https://img.shields.io/badge/license-MIT-10B981?style=flat-square" alt="License"/>
</p>

</div>

---

## Install

```bash
npx skills add https://github.com/stellazhan/CodeStable
```

Onboard a repository first:

```bash
/cs-onboard
```

For daily use, when you are not sure which skill fits, call the root entry:

```bash
/cs
```

If your agent supports automatic skill triggering, `using-codestable` checks for `.codestable/attention.md` in onboarded repositories and routes lifecycle tasks to `cs` by default: features, bugs, refactors, architecture, requirements, roadmap work, audits, docs, decisions, learnings, and code exploration.

---

## What CodeStable Solves

Most AI coding frameworks orchestrate agents: roles, teams, handoffs, review loops, and autonomous pipelines. CodeStable orchestrates the lifecycle of the software itself: requirements, architecture, roadmaps, features, issues, decisions, and accumulated knowledge.

<table>
<tr><th></th><th>Agent orchestration</th><th>CodeStable</th></tr>
<tr><td><b>Core entity</b></td><td>Agent / Role / Team</td><td>Requirement / Architecture / Feature / Issue / Decision</td></tr>
<tr><td><b>Main question</b></td><td>How agents collaborate</td><td>How constraints, history, and decisions are recorded, retrieved, and reused</td></tr>
<tr><td><b>Where state lives</b></td><td>Agent sessions / queues / buses</td><td>The project's <code>.codestable/</code> file tree</td></tr>
<tr><td><b>Human role</b></td><td>Less intervention is better</td><td>Human in the loop; the programmer owns the whole, AI executes efficiently</td></tr>
</table>

![](./asset/CodeStableVSAgent.png)

CodeStable's bet is simple: in serious software work, chaos often comes not from weak agents but from poorly organized software elements. A stronger agent cannot save a project that has lost its requirements, architecture, and history.

---

## Core Model

### 6 entities

| Entity | Directory | Responsibility |
|---|---|---|
| Requirement | `.codestable/requirements/` | Capability intent: what users need, what the system provides, where boundaries are |
| Architecture | `.codestable/architecture/` | Current system map only; no future plans |
| Roadmap | `.codestable/roadmap/` | High-level plan, interface contracts, and executable feature list for large needs |
| Feature | `.codestable/features/` | Design to implementation to acceptance loop |
| Issue | `.codestable/issues/` | Report to root-cause analysis to fix-note loop |
| Knowledge | `.codestable/compound/` | Unified sink for learning / trick / decision / explore records |

### 3 main flows

| Flow | Skill chain | Notes |
|---|---|---|
| Feature delivery | `cs-feat` -> `cs-feat-design` -> `cs-feat-impl` -> `cs-feat-accept` | Think, design, implement by checklist, verify against design |
| Issue fixing | `cs-issue` -> `cs-issue-report` -> `cs-issue-analyze` -> `cs-issue-fix` | Record symptoms, find the root cause, then fix precisely |
| Refactoring | `cs-refactor` / `cs-refactor-ff` | Behavior stays the same; structure changes; full flow is scan / design / apply |

`cs-brainstorm` handles fuzzy ideas, `cs-roadmap` handles needs too large for one feature, and `cs-audit` proactively finds risks without fixing them directly.

---

## Skill Catalog

<table>
<tr><th>Group</th><th>Skill</th><th>Purpose</th></tr>
<tr><td><b>Auto entry</b></td><td><code>using-codestable</code></td><td>Routes lifecycle tasks to <code>cs</code> in onboarded repositories</td></tr>
<tr><td><b>Root entry</b></td><td><code>cs</code></td><td>Introduces the system and routes open-ended intents to the right cs sub-skill</td></tr>
<tr><td><b>Onboard</b></td><td><code>cs-onboard</code></td><td>Create or migrate the CodeStable skeleton for a repository</td></tr>
<tr><td rowspan="2"><b>Requirements & architecture</b></td><td><code>cs-req</code></td><td>Maintain capability-intent docs with draft / current / outdated states</td></tr>
<tr><td><code>cs-arch</code></td><td>Maintain the current architecture map; no future planning</td></tr>
<tr><td rowspan="2"><b>Planning & discussion</b></td><td><code>cs-roadmap</code></td><td>Produce high-level design, interface contracts, and sub-feature lists for large needs</td></tr>
<tr><td><code>cs-brainstorm</code></td><td>Discuss and triage fuzzy ideas into design, lightweight feature work, or roadmap</td></tr>
<tr><td rowspan="5"><b>Feature flow</b></td><td><code>cs-feat</code></td><td>Feature sub-flow entry; routes instead of running stages itself</td></tr>
<tr><td><code>cs-feat-design</code></td><td>Draft <code>{slug}-design.md</code> and <code>{slug}-checklist.yaml</code></td></tr>
<tr><td><code>cs-feat-impl</code></td><td>Implement by checklist; return to design when reality falls outside the plan</td></tr>
<tr><td><code>cs-feat-accept</code></td><td>Verify implementation and sync architecture / requirement deltas / roadmap status</td></tr>
<tr><td><code>cs-feat-ff</code></td><td>Fast lane for small needs: no full design, but still leaves a traceable note</td></tr>
<tr><td rowspan="4"><b>Issue flow</b></td><td><code>cs-issue</code></td><td>Bug-fixing sub-flow entry</td></tr>
<tr><td><code>cs-issue-report</code></td><td>Record symptoms, reproduction, and impact without guessing root cause</td></tr>
<tr><td><code>cs-issue-analyze</code></td><td>Read code, identify root cause, and offer 2-3 owner-reviewed fix options</td></tr>
<tr><td><code>cs-issue-fix</code></td><td>Apply the approved fix, verify it, and write the fix-note</td></tr>
<tr><td rowspan="2"><b>Refactor flow</b></td><td><code>cs-refactor</code></td><td>Full structure / performance / readability optimization flow</td></tr>
<tr><td><code>cs-refactor-ff</code></td><td>Fast lane for small, behavior-preserving improvements</td></tr>
<tr><td rowspan="2"><b>Audit & exploration</b></td><td><code>cs-audit</code></td><td>Scan for bug risks, security issues, performance problems, maintainability debt, and architecture drift</td></tr>
<tr><td><code>cs-explore</code></td><td>Turn targeted code exploration into reusable evidence</td></tr>
<tr><td rowspan="4"><b>Knowledge sink</b></td><td><code>cs-learn</code></td><td>Capture pitfalls and good practices</td></tr>
<tr><td><code>cs-trick</code></td><td>Capture reusable patterns, library usage, and techniques</td></tr>
<tr><td><code>cs-decide</code></td><td>Record settled technical choices, architecture decisions, and long-term constraints</td></tr>
<tr><td><code>cs-note</code></td><td>Append short, stable, always-loaded project notes to <code>.codestable/attention.md</code></td></tr>
<tr><td rowspan="2"><b>External docs</b></td><td><code>cs-guide</code></td><td>Write developer and user guides, defaulting to <code>docs/dev/</code> and <code>docs/user/</code></td></tr>
<tr><td><code>cs-libdoc</code></td><td>Write per-entry API / component / command reference docs, defaulting to <code>docs/api/</code></td></tr>
<tr><td><b>Browser</b></td><td><code>browser-bridge</code></td><td>Use a Chrome extension for real browser control, DOM extraction, and component evidence</td></tr>
<tr><td><b>Maintenance</b></td><td><code>codestable-maintainer</code></td><td>Maintain CodeStable source, harnesses, fresh-clone verifier, and installed-copy sync</td></tr>
</table>

---

## Runtime Structure

After `/cs-onboard`, the project root contains `.codestable/`. It is the only shared workspace that CodeStable sub-skills read and write at runtime.

```text
your-project/
├── .codestable/
│   ├── attention.md                 # Required read before every CodeStable skill
│   ├── requirements/                # Capability intent, including VISION.md
│   ├── architecture/                # Current system map
│   ├── roadmap/                     # Large-need plans and sub-feature lists
│   ├── features/                    # Feature design / checklist / review / acceptance
│   ├── issues/                      # Report / analysis / review / fix-note
│   ├── refactors/                   # Scan / design / checklist / review / apply-notes
│   ├── compound/                    # Learning / trick / decision / explore
│   ├── brainstorm/                  # Temporary spike area for brainstorm
│   ├── tools/                       # Shared scripts released by onboard
│   └── reference/                   # Shared conventions released by onboard
└── docs/                            # Default output for cs-guide / cs-libdoc
```

Hard constraints:

- Sub-skills only use `.codestable/attention.md` as the project attention entry. `AGENTS.md` / `CLAUDE.md` are not CodeStable state sources.
- Shared conventions are not referenced across skill package directories. `cs-onboard` copies `reference/` and `tools/` into the working project's `.codestable/`.
- `requirements/` and `architecture/` are long-lived archives; `roadmap/` is the planning layer; `features/`, `issues/`, and `refactors/` are event records; `compound/` is the single knowledge sink.
- Old `codestable/` / `easysdd/` directories are historical compatibility entry points. Current sub-skills read `.codestable/`.

---

## Current Tool Layer

`cs-onboard` releases deterministic tools into `.codestable/tools/` to guard boundaries where agents tend to drift:

| Tool | Purpose |
|---|---|
| `codestable-doctor.py` | Summarize repository state, worktree state, review / backlog / inbox risks |
| `codestable-ai-branch-guard.py` | Run as an agent hook to block AI branch switches in the coordinator checkout and implementation work on `main` / `master` |
| `codestable-worktree-gate.py` | Check correct worktree usage at start / commit / quarantine |
| `validate-implementation-review.py` | Confirm implementation changes have review evidence |
| `build-review-packet.py` | Build review inputs for implementation / spec / quality review |
| `build-context-packet.py` | Build handoff, human-reviewer, and owner-judgment context packets |
| `check-context-sufficiency.py` | Reject empty or insufficient context packets |
| `codestable-finish-worktree.py` | Produce learning and merge-readiness records when worktree work finishes |
| `codestable-worktree-inbox.py` | Surface ready / stale / blocked work branches from main |
| `plan-commits.py` | Plan grouped commits by CodeStable unit and file ownership |
| `codestable-backlog.py` | Scan unresolved follow-ups, human-review items, P2s, and attention candidates |
| `codestable-spec-governance.py` | Route specs, generate deltas / clarifications, inventory drift, and check acceptance |
| `search-yaml.py` / `validate-yaml.py` | Search and validate frontmatter / YAML artifacts |

---

## Maintainer And Harness

CodeStable itself is maintained through `codestable-maintainer`. The source repository is `/Users/qiyuanzhan/code/CodeStable`; installed copies are deployment artifacts and must not be edited first.

After pushing a branch, run the verifier for fresh-clone checks, skill validation, installed-copy sync, and diff-check:

```bash
python3 codestable-maintainer/tools/verify.py --repo . --branch <branch> --remote origin --installed-root /Users/qiyuanzhan/.agents/skills --sync-installed --json
```

Behavior regression coverage lives in the maintainer harness:

```bash
python3 codestable-maintainer/tools/agent-behavior-harness.py run --suite critical --actor sterile
```

Current stability boundary:

- The `critical` suite is deterministic behavior regression coverage for routing, worktrees, review packets, backlog, spec governance, compact resume, and other high-risk behavior.
- The `live` suite can run a manually triggered real Codex smoke through `--actor live-codex`.
- Scheduled live eval, budget guards, compaction canaries, and a result dashboard are still Phase 2. See `codestable-maintainer/references/live-eval-phase-2.md`.

---

## Design Philosophy

CodeStable takes the opposite stance from OMO: OMO treats human intervention as a failure signal; CodeStable treats the programmer as the in-loop owner of software coding. AI can execute efficiently, but capability boundaries, architecture evolution, acceptance criteria, and trade-offs still need owner judgment.

Software architecture must remain evolvable, observable, and controllable. CodeStable does not chase full automation fantasies; it keeps real projects recoverable when context grows, requirements drift, and multiple humans or agents hand work off.

---

## Roadmap

- [ ] `cs-refactor` is still beta and needs more hardening.
- [ ] Live eval Phase 2: scheduled live smoke, compaction canary, budget guard, and result dashboard.

Issues are welcome. Share real development pain and refactoring experience.

---

<div align="center">

MIT License · by [@liuzhengdong](https://github.com/liuzhengdongfortest)

</div>
