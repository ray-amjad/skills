---
name: task-lifecycle
description: 'Ship a repo change as a reviewed and verified PR. Use when the user asks to implement, build, add, fix, or ship a non-trivial change, or wants an existing PR or branch reviewed, fixed and proven to work ("put this branch through the loop"). Not for a read-only review (that is code-review).'
---

# Task lifecycle

build → PR → review → fix → verify → final report → (merge → deploy → live check)

You are the orchestrator. Keep your hands off the code: you dispatch agents, carry results between them, keep the user posted, and stop before any merge. Brief each agent with the goal, not a method.

One builder owns the change. Dispatch it once, and send every fix back to that same builder (continue it with SendMessage) so the branch has one author who knows why the code is the way it is. Reviewers and verifiers are always other, fresh agents that never saw the builder's reasoning, because a builder checking its own work proves nothing. Wait for each agent's result before moving on.

**Build.** The builder works on a new branch in a clean clone. If the ask names an issue with no reproduction, reproduce it first; if that fails, stop and say what was tried. It commits as it goes so a dead run can resume from the branch, and where the spec is silent it decides and records the call in the implementation notes (`references/implementation-notes.md`).

**Review.** Open the PR, then read `references/review-round.md`. Claude's `/code-review` and Codex's `codex review` review the diff independently, and the builder fixes the confident findings. Up to two rounds; stop early when clean.

**Verify.** Read `references/verify-round.md`. A fresh agent drives each changed flow the way a user would, against the real app and a real non-production database, and the builder fixes what fails. Up to two rounds. A missing credential means unverified, said plainly, never swapped for a weaker check.

**Final report.** Present a final report to the user: the PR link and what was built, what review found and what was fixed, what's unresolved, one line per verified flow, and the open questions from the implementation notes with your recommended answers. Then ask "Merge PR #n?" and stop. Merging is the user's call.

**Merge.** When told to: squash-merge, confirm it reads MERGED, watch the deploy finish, then check the changed behavior on the live site without writing into real accounts. If it's broken, say so and ask about reverting. Never revert on your own.
