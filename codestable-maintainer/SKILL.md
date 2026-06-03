---
name: codestable-maintainer
description: Maintain the CodeStable skill library and harness. Use when changing CodeStable source skills, shared references, onboarded tools, validator scripts, README skill lists, installed skill copies, or when planning CodeStable harness improvements. Enforces source-repo edits, remote push, fresh-clone verification, and installed-copy diff checks.
---

# CodeStable Maintainer

Use this skill for any CodeStable library change. Do not edit installed copies
first. Installed copies are deployment artifacts; the source of truth is the
local CodeStable repository.

## Source Of Truth

- Source repo: `/Users/john/Code/Github/CodeStable`
- Installed skill roots commonly used on this machine:
  - `/Users/john/.agents/skills`
  - `/Users/john/.codex/skills`
- Fresh-clone verification root: create a temporary directory under `/tmp` or
  the system temp directory.

If the user asks to change a CodeStable skill, workflow, shared convention,
validator, harness tool, or README, switch to the source repo before editing.

## Required Workflow

1. Inspect source repo status and remotes:
   `git status --short --branch` and `git remote -v`.
2. Create or switch to a focused `codex/...` branch unless the user explicitly
   requires another branch.
3. Edit only source repo files. Do not patch `/Users/john/.agents/skills/*` or
   `/Users/john/.codex/skills/*` until after the source change is committed and
   verified.
4. If the change creates or updates a skill, use the active skill-creator
   workflow when it is available. In all cases, validate frontmatter, keep
   `SKILL.md` concise, and place detailed material in `references/` when
   useful.
5. Run relevant local validation:
   - Discover the active skill-creator validator with
     `find /Users/john/.codex /Users/john/.agents -name quick_validate.py -print`
     and run `uvx --with PyYAML python <quick_validate.py> <skill-dir>` for
     changed skills.
   - `pytest` or focused tests for changed harness scripts when tests exist.
   - `git diff --check`.
6. Use a subagent reviewer for implementation review when available. If the
   platform truly cannot launch one, record a fresh self-review fallback
   explicitly in the final report.
7. Commit source changes with a Conventional Commit message.
8. Push the branch to a remote.
9. Fresh-clone the pushed branch into a temporary directory and rerun the key
   validation from the clone. Do not call the work done from the original
   checkout alone.
10. From the fresh clone, enumerate every changed installable unit. For each
    changed skill directory, sync or reinstall it into the installed global
    skill root and diff-check that installed copy against the clone. For changed
    source files that are not installed directly, record `not installed: N/A`
    in the final report with the reason.

## Fresh Clone Verification

Use a branch-aware clone flow:

```bash
tmpdir="$(mktemp -d)"
git clone --branch <branch> --single-branch <remote-url> "$tmpdir/CodeStable"
cd "$tmpdir/CodeStable"
validator="$(find /Users/john/.codex /Users/john/.agents -name quick_validate.py -print -quit)"
uvx --with PyYAML python "$validator" <skill-dir>
```

For installed-copy verification, enumerate every changed installable unit, then
compare each fresh clone skill directory to its installed directory:

```bash
for skill_dir in <changed-skill-dir> ...; do
  diff -ru "$tmpdir/CodeStable/$skill_dir" "/Users/john/.agents/skills/$skill_dir"
done
```

If a changed file is not meant to be installed immediately, say that explicitly
and skip the installed-copy diff only with a reason. Do not treat one clean
skill diff as proof that all installable CodeStable changes were deployed.

## Harness Improvement Planning

For CodeStable harness roadmap or design work, read
`references/harness-improvement-plan.md` first, then
`references/harness-implementation-plan.md` when the task asks what to build
next. Together they capture the current proposal derived from GammaSource and
BetaSoul failures:

- `codestable-doctor`
- worktree start/commit/recovery gates
- review packet generation
- commit planner
- follow-up and human-review backlog detection
- source-push-clone-install verification

## Hard Stops

- Do not edit installed copies before source repo changes are committed and
  pushed.
- Do not claim a CodeStable source change is finished without fresh-clone
  verification.
- Do not claim installed global behavior is updated until the installed copy
  was synced/reinstalled and diff-checked.
- Do not push directly to `main` unless the user explicitly asks for that.
