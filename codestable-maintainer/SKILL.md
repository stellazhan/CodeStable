---
name: codestable-maintainer
description: Maintain the CodeStable skill library and harness. Use when changing CodeStable source skills, shared references, onboarded tools, validator scripts, README skill lists, installed skill copies, when making pushed CodeStable changes available locally, or when planning CodeStable harness improvements. Enforces source-repo edits, remote push, fresh-clone verification, and main-only installed-copy sync.
---

# CodeStable Maintainer

Use this skill for any CodeStable library change. Do not edit installed copies
first. Installed copies are deployment artifacts; the source of truth is the
local CodeStable repository.

## Source Of Truth

- Source repo: `/Users/qiyuanzhan/code/CodeStable`
- Installed skill roots commonly used on this machine:
  - `/Users/qiyuanzhan/.agents/skills`
  - `/Users/qiyuanzhan/.codex/skills`
- Fresh-clone verification root: create a temporary directory under `/tmp` or
  the system temp directory.

If the user asks to change a CodeStable skill, workflow, shared convention,
validator, harness tool, or README, switch to the source repo before editing.

## Required Workflow

1. Inspect source repo status and remotes:
   `git status --short --branch` and `git remote -v`.
2. Create or use a focused linked worktree on a `codex/...` branch unless the
   user explicitly requires another branch. Do not `git switch` / `git checkout`
   the stable source checkout for AI development.
3. Edit only source repo files. Do not patch `/Users/qiyuanzhan/.agents/skills/*` or
   `/Users/qiyuanzhan/.codex/skills/*` until after the source change is committed and
   verified.
4. If the change creates or updates a skill, use the active skill-creator
   workflow when it is available. In all cases, validate frontmatter, keep
   `SKILL.md` concise, and place detailed material in `references/` when
   useful.
5. Run relevant local validation:
   - Discover the active skill-creator validator with
     `find /Users/qiyuanzhan/.codex /Users/qiyuanzhan/.agents -name quick_validate.py -print`
     and run `uvx --with PyYAML python <quick_validate.py> <skill-dir>` for
     changed skills.
   - `pytest` or focused tests for changed harness scripts when tests exist.
   - `git diff --check`.
6. Use a subagent reviewer for implementation review when available. If the
   platform truly cannot launch one, record a fresh self-review fallback
   explicitly in the final report.
7. Commit source changes with a Conventional Commit message.
8. Push the branch to a remote.
9. Run the maintainer verifier from the source checkout against a temporary
   installed root:
   `tmp_installed="$(mktemp -d)/skills"; python3 codestable-maintainer/tools/verify.py --repo . --branch <branch> --remote origin --installed-root "$tmp_installed" --sync-installed --json`.
   This command fresh-clones the pushed branch, validates changed skills, runs
   harness tests when needed, syncs changed installed skill directories into the
   temporary root, and diff-checks that temporary copy.
   Do not suggest shorthand wrappers such as `codestable-maintainer verify` or
   `--sync`; the maintained contract is the explicit `python3
   codestable-maintainer/tools/verify.py ... --sync-installed --json` command.
10. Do not sync real installed roots from a feature branch. To make a CodeStable
    change globally available, merge it to `main`, push `origin/main`, then run
    the verifier from a clean `main` checkout:
    `python3 codestable-maintainer/tools/verify.py --repo . --branch main --remote origin --installed-root /Users/qiyuanzhan/.agents/skills --sync-installed --json`.
    Real installed roots are synchronized only from remote `main`.
11. For changed source files that are not installed directly, record
    `not installed: N/A` in the final report with the reason from verifier
    output.

## Fresh Clone Verification

For feature branches, prefer the maintainer verifier with a temporary installed
root:

```bash
tmp_installed="$(mktemp -d)/skills"
python3 codestable-maintainer/tools/verify.py --repo . --branch <branch> --remote origin --installed-root "$tmp_installed" --sync-installed --json
```

For real installed-copy deployment, first merge and push `origin/main`, then run:

```bash
python3 codestable-maintainer/tools/verify.py --repo . --branch main --remote origin --installed-root /Users/qiyuanzhan/.agents/skills --sync-installed --json
```

Use the manual branch-aware clone flow only when the verifier itself is broken:

```bash
tmpdir="$(mktemp -d)"
git clone --branch <branch> --single-branch <remote-url> "$tmpdir/CodeStable"
cd "$tmpdir/CodeStable"
validator="$(find /Users/qiyuanzhan/.codex /Users/qiyuanzhan/.agents -name quick_validate.py -print -quit)"
uvx --with PyYAML python "$validator" <skill-dir>
```

For temporary installed-copy verification, enumerate every changed installable
unit, then compare each fresh clone skill directory to its temporary installed
directory:

```bash
for skill_dir in <changed-skill-dir> ...; do
  diff -ru "$tmpdir/CodeStable/$skill_dir" "$tmp_installed/$skill_dir"
done
```

If a changed file is not meant to be installed immediately, say that explicitly
and skip the installed-copy diff only with a reason. Do not treat one clean
skill diff as proof that all installable CodeStable changes were deployed.

## Harness Improvement Planning

For CodeStable harness roadmap or design work, read
`references/harness-improvement-plan.md` first, then
`references/harness-implementation-plan.md` when the task asks what to build
next. For the implemented behavior runner, read
`references/behavior-harness-tool.md`. For global `cs` routing, owner approval reports,
context levels, owner-stop/skip rules, finish-time checks, or harness coverage
across routed workflows, also read `references/global-route-governance.md`. For
spec drift, requirement delta, clarification, or human-readable spec governance
work, read `references/spec-governance-roadmap.md`; for rollout tasks, continue
with `references/spec-governance-roadmap-implementation.md`. Together they
capture the current proposal derived from GammaSource, BetaSoul, and CodeStable
workflow failures:

Older harness roadmap references to `owner context`, `owner decision context`,
or `owner judgment context` mean auxiliary context only. Current approval
checkpoints must follow `approval-conventions.md` and write `approval-report.md`
unless a canonical stage report fully satisfies the L2 rule.

- `codestable-doctor`
- worktree start/commit/recovery gates
- review packet generation
- commit planner
- follow-up and human-review backlog detection
- source-push-clone-install verification
- worktree finish reports and merge reminders
- clean-agent behavior regression
- global route governance, spec governance, and drift control

## Hard Stops

- Do not edit installed copies before source repo changes are committed and
  pushed.
- Do not claim a CodeStable source change is finished without fresh-clone
  verification.
- Do not claim installed global behavior is updated until the installed copy
  was synced from remote `main` and diff-checked.
- Do not sync `/Users/qiyuanzhan/.agents/skills` or `/Users/qiyuanzhan/.codex/skills`
  from feature branches, sibling worktrees, or hand-copied patches.
- Do not push directly to `main` unless the user explicitly asks for that.
