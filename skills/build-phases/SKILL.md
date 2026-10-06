---
name: build-phases
description: Build a phased plan with one fresh builder subagent per phase, run successively on a single branch, one commit per phase, while keeping an implementation-notes file of every decision the spec didn't make. Use as the build stage of task-lifecycle, or standalone whenever a plan or spec is already cut into phases and needs building without one context window carrying the whole thing.
---

# Build in phases

Each phase gets its own builder, and each builder starts in a brand new context window. The reason is the size of specs: one builder carrying a large spec end to end lands somewhere around 400,000–700,000 tokens, and it reasons about the last phase through a context stuffed with the first — and builds it worst. Splitting the work is what keeps each window sharp.

**Successively, never in parallel.** Every builder works in the same clone on the same branch, and concurrent writers to one worktree clobber each other. Dispatch builder 1, wait, dispatch builder 2, and so on. A one-phase plan is just this loop run once.

## Brief each builder fully

A builder starts fresh with **no memory of the request**, so the brief carries everything:

- **Its phase, as the scope** — with the rest of the plan for context and an explicit *build phase N only; phases N+1… are someone else's job, do not start them*. Without that line a capable builder helpfully runs ahead and you lose the boundary.
- **What the previous builders actually did** — the branch name, their summaries, the files they touched, anywhere they deviated. It's on disk, but say it: the new builder shouldn't have to rediscover the shape its predecessor established.
- If there's a spec, plan, or issue: **read it first and build to it** — nothing more, nothing less.
- Start from the phase's brief, but **verify before trusting it**: it's a map drawn by an agent that wasn't building, so if the code contradicts it, the code wins — and the builder should say so when it reports back.
- Builder 1 creates a **new branch**, never the default one; every later builder **stays on it** — no re-branching, no rebasing.
- Keep the diff focused — unrelated cleanup muddies the review and the verification.
- **Commit at the end of the phase, with the phase in the message** (`phase 2: …`). That naming is what lets a resumed run count which phases already landed. Leave the branch checked out and do **not** open a PR — that's the orchestrator's job.
- Return a short summary: branch name, what it built, files touched, anywhere the brief was wrong.

A builder checking its own phase as it goes — type-checker, linter, that area's tests — is ordinary care, not a review round.

**Do not review or fix between phases.** One PR, one review, over the finished branch. Per-phase review multiplies reviewer dispatches until the build can't finish, and it's the wrong diff anyway: the defects that matter in a phased plan live *between* phases, in the contract phase 2 assumed and phase 3 broke, and only a reviewer holding the whole change can see them.

## Keep implementation notes — one file, from the first builder to the last fixer

A spec never covers everything. The builder is the first to meet the gaps — a field the spec doesn't name, two readings of one sentence, a precedent in the code that contradicts the plan — and it decides on the spot, because it has to. Without a record, every one of those decisions hides in the diff, and the user finds it in review, in production, or never. The notes file is the sanctioned place to make the call *and* keep the user in the loop: decide, write it down, move on — never stall on a question nobody can answer mid-run, and never guess without a trace.

Every builder and every fixer appends to **`.git/lifecycle/implementation-notes.md`** — under `.git/` so it never lands in the PR diff. Builder 1 creates it with four headings, kept in this order:

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

Each entry is one to three lines: the file or symbol, the call, the reason. Write **as you go**, not as a memory exercise at the end — the decision is clearest at the moment it's made. A phase that made no calls worth writing adds nothing, and that's a normal outcome; don't pad the file.

The file has three readers: **the next builder** reads it before starting, so a decision phase 1 made isn't re-decided the other way in phase 3; **the PR body** carries it, so anyone reading the PR sees the calls behind the diff; and **the final report** lifts out the *Open questions* verbatim so the user actually answers them.

What does *not* go in it: a narrative of the work, a list of files touched, or anything the diff already says. The notes hold only what a reader cannot recover from the diff — the reasoning.
