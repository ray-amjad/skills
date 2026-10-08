---
name: task-lifecycle
description: 'The default path for shipping a repo change as a reviewed and verified PR. Use when the user asks to implement, build, add, fix, or ship a non-trivial change. Also use it, in its already-built mode, when the change already exists and the user wants it reviewed, fixed and verified: "review this PR and fix what it finds", "put this branch through the loop", "check this properly and prove it works", or a follow-up where the code is already on disk. It builds the change with one builder on one branch, opens a PR, runs up to two review-and-fix rounds with Claude and Codex, verifies the change by driving the real app against a real database, and asks the user before merging. Not for a single read-through with no fixing (that is code-review).'
---

# Task lifecycle: build, review, fix, verify, ship

You are the orchestrator. You keep your own hands off the code. Every hands-on step (build, review,
fix, verify) runs in its own fresh subagent or process. You sequence them, carry artefacts between
them, report progress to the user, and **stop and ask the user before any merge**.

There is no plan step. Do not write a plan, a phase split or a `phases.md`, and do not dispatch a
planner. The builder reads the code and decides as it goes.

```
build (one branch) → open PR → [review → fix] ×1–2 → [verify → fix] ×1 → confirm → (merge → deploy → live check)
```

Everything after the build runs **once**, over the finished whole.

**Two modes:**

| The change… | Run |
|---|---|
| still has to be written | steps 0–7 below |
| already exists (a PR, a branch, work on disk) | the **Already built** section, then steps 4–7 |

The two loops after the build are files, and both modes read them. Read each one when you reach it:

| At… | Read |
|---|---|
| Step 4, the PR is open | `references/review-round.md` |
| Step 5, the reviews are done | `references/verify-round.md` |

## Brief the goal, not the procedure

Every dispatch hands an agent an **objective and a budget**, not a method. A subagent with a goal
spends its search on the code in front of it. A subagent with a procedure runs steps written before
anyone saw that code. When you extend this skill, add only three kinds of thing: harness facts that
cost the turn if unknown, budgets and gates, and traps from a real incident.

## Harness facts

- **Wait for every subagent's result** (builders, fixers, verifiers). Never end a turn waiting on a
  background notification that may never arrive. Several foreground calls in one message still run
  at the same time.
- **Subagent budget.** Each subagent starts with a large prefix and re-reads its whole context on
  every request. Never run more than **three at once**. A run that passes **fifteen** subagents
  finishes its current step and reports what is left. A run that needs more is two runs.
- **Run artefacts live in `.git/task-lifecycle/`** (`run-state.md`, `implementation-notes.md`). That
  folder is inside the clone but never committed, so none of it lands in the PR diff.

## Implementation notes: one file, from the first builder to the last fixer

A spec never covers everything, and the builder meets the gaps first. It must decide on the spot. The
notes file is where it records the call, so the decision does not hide in the diff. It is the
builder's out: decide, write it down, keep building. Never stall, and never guess without a trace.

Every builder and fixer appends to **`.git/task-lifecycle/implementation-notes.md`**. The builder
creates it:

```markdown
# Implementation notes — <ask, in a few words>

## Design decisions
Choices made where the spec was ambiguous, and the reading picked.

## Deviations
Places the build departed from the spec on purpose, and why.

## Tradeoffs
Alternatives considered, and why the chosen one won.

## Open questions
Anything the user should confirm or revise. Phrase each one as a question.
```

One to three lines per entry: the file or symbol, the call, the reason. Write it at the moment of the
decision. Do not pad it, and do not put in anything the diff already says. It has three readers: a
resumed builder (step 2), the PR body (step 3, refreshed after each fix round), and you at step 6, where
its *Open questions* go to the user.

## Re-read the issue's state at every stage boundary

When the run fixes a GitHub issue, someone else can close it while you work. Read the state again
before the build, after the PR opens, before each review round and before the merge:

```bash
gh issue view <n> --repo <owner>/<repo> --json state,stateReason,closedAt
```

`CLOSED` ends the run. Search the open PRs for the issue number too, to catch another run before it
merges. A branch-name convention does not prove ownership; only the author login does. If another PR
already closed the issue, comment on yours naming it, close yours as a duplicate, and file anything
only your fix had as its own issue.

## 0. First, check if you're resuming

When a follow-up says "continue", or you pick up a run that died mid-way, **do not start over.** A
rebuild on top of an existing branch duplicates work and corrupts the diff. Read, in order:

- **`.git/task-lifecycle/run-state.md`** — the milestone log the dead run wrote on purpose. Its last
  line says where to look. It can be one step behind, so git and the PR confirm what actually landed.
- **`.git/task-lifecycle/implementation-notes.md`** — hand it to the next builder unchanged.
- **Git and the PR, the source of truth:**
  - commits on the branch with no PR → the build died part-way. Dispatch a builder to finish it, on
    the same branch, with the notes file and the commit list;
  - `gh pr list --head <branch> --json number,url` returns a PR → step 3 is done;
  - `gh pr view <n> --comments` → the `task-lifecycle-round` stage markers from
    `references/review-round.md`. Advance past a round only for a `stage:complete` marker whose full
    `head` SHA is an ancestor of the fetched PR head. If only `stage:reviewed` exists, resume that
    round's fixer from the posted findings. Do not count ordinary review comments as rounds;
  - a `## Verified` section with real entries in the PR body → jump to step 6.

The PR wins when the sources disagree. Tell the user "Resuming — picking up at <step>." and go there.

## 1. Clone, and judge the issue

Work in a clean clone or worktree of the repo, never on top of someone's uncommitted changes.

**If the ask names a GitHub issue, judge it by its evidence first.** An issue with clear reproduction
steps or evidence is the spec. An issue without them is reproduced first. If you cannot reproduce it,
comment what you tried, tell the user, and stop. Step 5 proves the fix, not the defect.

## 2. Build — one fresh builder

Dispatch **one builder** for the whole change. Brief it with the objective, not a method, because it
has no memory of the request:

- the ask in your own words, the repo path, and the path to any spec or issue the user named. **It
  reads the spec first; the spec is the source of truth for scope**, and it builds to it;
- it finds where the change goes itself, and it decides as it goes. It appends each call to the
  implementation notes;
- it creates a **new branch**, never the default one;
- keep the diff focused;
- **commit as it goes**, in small coherent commits, so a run that dies mid-build leaves a resumable
  branch. Leave the branch checked out, and **do not open a PR**;
- return: branch, repo path, what it built, files touched, and anything it could not finish.

A builder that runs the type checker, linter and tests for its own area is ordinary care. If it
returns with work left undone, dispatch one more builder on the same branch to finish it, with the
first builder's summary and the notes file. **Never two builders at once**: they share one clone and
one branch, and concurrent writers clobber each other. Do not review or fix before the PR: only a
reviewer holding the whole change sees the defects that matter.

```bash
printf '%s\n' "build done — <branch> — $(git rev-parse --short HEAD)" >> .git/task-lifecycle/run-state.md
```

## 3. Open the PR

```bash
git push -u origin <branch>
gh pr create --title "<title>" --body-file body.md
```

The body has four sections: `## What changed and why` (with the issue link), `## Implementation notes`
(paste the whole notes file), `## Verified` (`Not verified — pending` until step 5), and `## Source`
(the ask or spec it came from).

**If the repo deploys previews (Vercel, Netlify, and so on), check the preview before step 6.** A red
check is not always a build failure: read why it is red. Never call a change ready while its preview is
red without saying why. A build that fails on a missing environment variable stops the run; adding
secrets is the user's job.

## 4. Review → fix, up to two rounds

**The loop is in `references/review-round.md`. Read it now.** It owns the two-round contract, the
reviewer panel, how to size the panel to the diff, the fix brief, the stage markers, and the route to
verification.

## 5. Verify it actually works

**The loop is in `references/verify-round.md`. Read it now.** It owns the flow briefs, the
one-file-per-flow evidence rule and the outcomes you route on.

## 6. Confirm — and do not merge

The final reply includes:

- the PR link, and what you built in a sentence or two;
- the review rounds: findings, what you fixed, what is unresolved;
- the verification: one line per flow, in the checker's own outcome word. An `unreachable_state` flow
  is *unreachable*, not *failed*. Name the branch it covered and ask whether to keep it;
- the open questions from the implementation notes, each with your recommended answer;
- then ONE question: "Merge PR #<n>?"

Stop there. Merging is the user's call. An unsettled judgement goes to the user with both readings
written out. Do not spawn a second-opinion subagent on another model to settle it.

If the user has set up an explicit merge rule for unattended runs (for example "merge when checks are
green and verify passed"), you may follow it, and say which rule and which conditions you tested. Test
"the checks are green" with `gh pr checks <n> --watch`, not by eye. An unresolved finding or a
`ran_wrong` flow fails any such rule. A condition about your own certainty fails if you guessed.

## 7. Merge, babysit the deploy, check the live site

You get here when the user says "merge it". Do all four, in one turn:

1. **Merge.** `gh pr merge <n> --squash --delete-branch`, then confirm with
   `gh pr view <n> --json state` that it reads `MERGED` before you say it is merged.
2. **Babysit the deploy** until it reaches a terminal state, if the repo deploys on merge. Check that
   the deployment you are watching is the merge commit. A failed deploy is a result, not a retry loop.
   Read the log, say what broke, and retry only an infrastructure fault.
3. **Check the live site.** A green deploy proves the build, not the feature. Drive the real
   production URL the way step 5 drives the app. The floor is one flow for the changed behaviour, plus
   the nearest flow the change could break. Production is not a test database: do not sign up, buy,
   delete, or write into anyone's account unless the user gave you a test account for it. A flow that
   needs a write you may not make is `could_not_boot`, with the refused write named.
4. **Report** one line per flow. If the live check fails, name the merge commit and ask whether to
   revert. **Never revert on your own.**

## Already built: the loop without the build

Use this when the change exists: a PR, a branch, or work already on disk. Skip steps 1–3. Then run
steps 4–7 with these four differences.

**1. Establish the diff yourself.** Getting it wrong wastes the whole run on the wrong code.
- A PR: `gh pr checkout <n>`. A PR with no `## Verified` section is unverified.
- A branch: check it out.
- Work on disk: **commit it to a branch first**, because both reviewers read
  `git diff origin/$BASE...HEAD`, and an uncommitted tree is invisible to them.
- A branch with no PR: open one first (step 3's body shape), so the findings have an anchor.

`BASE` is the PR's own base, not `main`: on a stacked PR, `main` pulls the branch below into scope.
**An empty diff means you resolved the target wrong.** Ask which change they mean.

**2. Check you can push before you promise fixes.**

```bash
gh pr view <n> --json state,baseRefName,headRefName,isCrossRepository,maintainerCanModify
```

A fork without `maintainerCanModify`, or a target on the default branch, is **review-only**. Post the
findings to the PR, say why you cannot push, and offer the fixes as a separate branch. Otherwise,
`git fetch` and fast-forward before each fix round, because a human's branch can move. Never
force-push.

**3. No building.** A fixer here fixes findings. It does not finish a half-built feature. If the
reviewers say the change is *incomplete* (a missing migration, a UI with no handler), stop, report
what is missing, and offer a full task-lifecycle run. "Review this *and* add X" is two jobs.

**4. Bigger budgets, because the build's share is free.** Review → fix: up to three rounds. Verify →
fix: up to two. Do not count ordinary review comments as completed rounds. An explicit request for a
thorough review gets both reviewers, even on a small diff. On resume, the PR is the record.

## Keep the user informed

A long run with no output looks like a hang. Say one line at each milestone: build started, build
done, PR opened, each review, each fix, verifying, done. Do not narrate every command. In the same
breath, append the milestone to `.git/task-lifecycle/run-state.md`:

```bash
printf '%s\n' "PR #482 opened — https://github.com/…" >> .git/task-lifecycle/run-state.md
printf '%s\n' "review round 1 done — 3 findings, all fixed" >> .git/task-lifecycle/run-state.md
```

Write the line **after** the thing it claims is done, never before. Why: a line that runs ahead of
the work sends a resumed run past work that never landed.
