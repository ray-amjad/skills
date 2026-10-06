---
name: task-lifecycle
description: The default path for shipping any real change end-to-end — a feature, a non-trivial fix, a "make a change" ask — as a reviewed, verified PR rather than just a diff. Use whenever the user asks to implement, build, add, fix, or ship something in a repo and the change is more than a one-line edit, whether or not they say "PR" or "review" out loud. Runs the full loop by sequencing four sibling skills — plan-phases → build-phases → open a PR → review-panel → verify-flows → confirm with the user before anything merges.
---

# Task lifecycle

You are the orchestrator, and you keep your own hands off the code. Every hands-on step runs in its own fresh subagent; your job is to sequence the stages, carry the artefacts between them, report progress, and finally **stop and ask the user** — you never merge on your own.

```
plan (plan-phases) → build (build-phases) → open PR → review + fix (review-panel) → verify (verify-flows) → confirm
```

Each stage is its own skill. Read each one when you reach its step, not before.

| Stage | Skill | What it hands back |
|---|---|---|
| 1. Plan | **plan-phases** | a phase split in `phases.md`, checked by a second model |
| 2. Build | **build-phases** | one commit per phase on one branch, plus `implementation-notes.md` |
| 3. PR | this file, below | the PR number and URL |
| 4. Review | **review-panel** | findings found, fixed, or carried as open questions |
| 5. Verify | **verify-flows** | one evidence file per user flow |
| 6. Confirm | this file, below | the user's decision |

## Working files

The run's working files live in **`.git/lifecycle/`** inside the repo — `phases.md`, `implementation-notes.md`, `run-state.md`. Under `.git/` deliberately: git never tracks its own directory, so nothing in there can leak into the PR diff, and it survives as long as the clone does. A plan file or notes file written into the worktree lands in the diff and every reviewer reads it as part of the change.

## Brief the goal, not the procedure

Every dispatch hands an agent an **objective and a budget**, not a method. A subagent given a goal can spend its own search on the problem in front of it; one given a procedure can only execute a plan written before anyone had seen the code. When you extend this skill, limit additions to three kinds of thing: facts about the harness that cost a run if unknown, budgets and gates (two review rounds, one verify round, never merge), and traps that came from an actual incident.

## 0. First, check if you're resuming

A full run is long and can stop partway. When a follow-up says "continue", **do not start over** — re-planning and rebuilding on top of an existing branch duplicates work and corrupts the diff. Read, in order:

- **`.git/lifecycle/run-state.md`** — the previous run appended a line at every milestone, so its last line names where you are. It can be one step behind (a run can die between doing the work and writing the line), so it tells you where to look; git and the PR tell you what actually landed.
- **`git log --oneline`** on the branch — commits are named `phase 2: …`, so the highest phase present is the last that landed. Resume with the builder for the *next* phase in `phases.md`; don't re-plan, because a fresh planner cuts the work differently and the split stops lining up with the commits.
- **`gh pr list --head <branch>`** — a PR means the build finished. `gh pr view <n> --comments` — each posted review is a comment, so N review comments = N rounds done.

Tell the user you're resuming and from where, then jump straight to that step. Only fall through to step 1 if nothing exists yet.

## 1–2. Plan, then build

Run **plan-phases**, show the user the split before an hour goes into it, then run **build-phases** against it. Post a one-line milestone between phases so a long build shows movement.

## 3. Open the PR

From the repo, push the branch and open the PR (`gh pr create`). **Paste `implementation-notes.md` into the PR body** under the what-changed text, headings and all, so a reader of the PR sees the calls behind the diff. Capture the PR number — review and fix rounds attach to it.

## 4–5. Review, then verify

Run **review-panel** over the finished PR (at most two review→fix rounds), then **verify-flows** (at most one fix→re-verify). Review reads the diff; verify runs it. Both run once, over the finished whole — never per phase.

## 6. Confirm — do not merge

Your final report is a wrap-up and a genuine question. Include: the PR link; what you built in a sentence or two; the review rounds — findings found, fixed, anything left unaddressed; the verification result, one line per flow with its evidence file; any plausible-but-unconfirmed findings carried from review, called out once here rather than quietly disappearing; and **the Open questions from `implementation-notes.md`, verbatim**, each phrased so the user can answer directly — a question the user never sees is a guess that shipped.

Then ask: **"Want me to merge this, or change anything first?"** — and stop. Merging is the user's call. Do not run `gh pr merge` unless they say yes.

## Keep the record alive

At each milestone (phase split, each build phase, PR opened, each review round, verifying, done), tell the user one line and append the same line to `.git/lifecycle/run-state.md`:

```bash
printf '%s\n' "phase 2/4 done — API routes — $(git rev-parse --short HEAD)" >> .git/lifecycle/run-state.md
```

Write the line **after** the thing it claims is done, never before — a line that runs ahead of the work sends a resumed run past a phase that never landed.
