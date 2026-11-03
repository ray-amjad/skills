---
name: task-lifecycle
description: 'The default path for shipping a repo change as a reviewed and verified PR. Use when the user asks to implement, build, add, fix, or ship a non-trivial change. Also use it, in its already-built mode, when the change already exists and the user wants it reviewed, fixed and verified: "review this PR and fix what it finds", "put this branch through the loop", "check this properly and prove it works", or a follow-up where the code is already on disk. It builds the change with one builder on one branch, opens a PR, runs up to two review-and-fix rounds with Claude and Codex, verifies the change by driving the real app against a real database, and asks the user before merging. Not for a single read-through with no fixing (that is code-review).'
---

# Task lifecycle: build, review, fix, verify, ship

You are the orchestrator. You keep your own hands off the code: every hands-on step (build, review,
fix, verify) runs in a subagent or process. You sequence them, report progress to the user, and
**stop and ask the user before any merge**.

**One builder owns the change.** Every fix (review findings, failed flows, red CI) goes back to it,
because it knows why the code is the way it is. Reviewers and verifiers are always fresh agents. Use
a new builder only when the original is gone, and give it the branch and the open findings.

```
build (one branch) → open PR → [review → fix] ×1–2 → [verify → fix] ×1 → confirm → (merge → deploy → live check)
```

There is no plan step. The builder reads the code and decides as it goes.

| The change… | Run |
|---|---|
| still has to be written | steps 0–7 below |
| already exists (a PR, a branch, work on disk) | the **Already built** section, then steps 4–7 |

## 0. Resuming

When a follow-up says "continue", or a run died mid-way, **do not start over.** Git and the PR are
the record:

- commits on the branch with no PR → the build died part-way. Have a builder finish it on the same
  branch;
- an open PR for the branch → step 3 is done;
- `task-lifecycle-round` stage markers in the PR comments (see `references/review-round.md`) → the
  review rounds done. If only `stage:reviewed` exists, send that round's findings to the builder;
- a `## Verified` section with real entries in the PR body → jump to step 6.

Tell the user "Resuming — picking up at <step>." and go there.

## 1. Clone, and judge the issue

Work in a clean clone or worktree, never on top of someone's uncommitted changes. If the ask names a
GitHub issue, an issue with clear reproduction steps is the spec. One without them is reproduced
first; if you cannot reproduce it, say what you tried and stop. If the issue gets closed while you
work, stop.

## 2. Build — one builder

Dispatch **one builder** for the whole change. Brief it with the objective, not a method: the ask in
your own words, the repo path, and any spec or issue (the spec is the source of truth for scope). It
works on a **new branch**, keeps the diff focused, commits as it goes, and does not open a PR. It
returns the branch, what it built, and anything it could not finish. Keep it: fixes come back to it.

If it returns with work left undone, have it (or, if it is gone, a new builder on the same branch)
finish. **Never two builders at once.** Do not review or fix before the PR.

## 3. Open the PR

Push the branch and open the PR. The body has `## What changed and why` (with the issue link),
`## Verified` (`Not verified — pending` until step 5), and `## Source` (the ask or spec).

If the repo deploys previews, check the preview before step 6. Never call a change ready while its
preview is red without saying why.

## 4. Review → fix, up to two rounds

Read `references/review-round.md` now.

## 5. Verify it actually works

Read `references/verify-round.md` now.

## 6. Confirm — and do not merge

The final reply has the PR link and what you built, the review findings (fixed and unresolved), one
line per verified flow in the checker's own outcome word, any open questions with your recommended
answer, and then ONE question: "Merge PR #<n>?"

Stop there. Merging is the user's call, unless the user has set an explicit merge rule for unattended
runs (for example "merge when checks are green and verify passed"). An unresolved finding or a
`ran_wrong` flow fails any such rule.

## 7. Merge, watch the deploy, check the live site

When the user says "merge it":

1. **Merge** (`gh pr merge <n> --squash --delete-branch`) and confirm the PR reads `MERGED`.
2. **Watch the deploy** of the merge commit to a terminal state, if the repo deploys on merge. Retry
   only an infrastructure fault.
3. **Check the live site**: the changed flow plus the nearest flow it could break. Production is not a
   test database: do not write into anyone's account without a test account from the user.
4. **Report** one line per flow. If the live check fails, ask whether to revert. **Never revert on
   your own.**

## Already built: the loop without the build

Use this when the change exists. Skip steps 1–3, then run 4–7 with these differences:

1. **Establish the diff.** Check out the PR or branch; commit work on disk to a branch and open a PR
   first. `BASE` is the PR's own base, not `main`. An empty diff means you picked the wrong target:
   ask.
2. **Check you can push.** A fork you cannot modify, or a target on the default branch, is
   review-only: post the findings and say why you cannot push. Never force-push.
3. **No building.** The first agent you send to fix round 1 becomes the builder for every later fix.
   It fixes findings; it does not finish a half-built feature. If the reviewers say the change is
   incomplete, stop and offer a full run.
4. **Bigger budgets:** up to three review rounds and two verify rounds.

## Keep the user informed

Say one line at each milestone: build started, build done, PR opened, each review, each fix,
verifying, done. Do not narrate every command.
