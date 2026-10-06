---
name: review-panel
description: Adversarially review a finished diff with fresh subagents from more than one model in parallel, merge their findings, and fix in rounds — at most two. Use as the review stage of task-lifecycle, on any open PR or branch that needs review before merging, or standalone when the user says "review this properly", "get a second opinion on this diff", or "run the panel".
---

# Review panel

Review runs in **fresh subagents that see only the diff**, prompted to try to break the change. A reviewer that also wrote the code rationalises its own choices; one with no memory of your intent is honest by construction. And there are at least **two, from two different models**, because two models with two different mandates catch what one alone rationalises away.

```
[review (Claude + a second model, in parallel) → merge findings → fix (fresh subagent)] × at most 2 → done
```

Stop early the moment a round comes back clean.

## The panel

- **Reviewer A — Claude, fresh subagent.** Give it only the diff (or the PR number) and the mandate: find correctness defects — inputs and state that produce wrong output, crashes, or silent corruption. If the harness has a built-in review skill (`/code-review`), that is this reviewer; run it at medium or high depending on the size of the change.
- **Reviewer B — a different model.** If the Codex CLI is installed, run the **codex-consult** skill in review mode (`codex review`). No Codex, or it fails to authenticate → **say so and run with one reviewer**. A missing reviewer is a stated degradation, never a silent drop.

Dispatch both in one message so they run in parallel. Each returns findings, not fixes.

## Size the panel to the diff

A tiny diff doesn't need the full panel — but the exemption is narrow. Dropping to one reviewer needs **every** condition to hold at once:

- fewer than about 30 lines changed;
- no new logic — no new branch, loop, or state, and no changed control flow;
- no changed contract that other callers depend on;
- nothing touching authentication, access control, money, data migrations, or concurrency.

Any doubt sends the diff to the full panel. Diff size is a weak proxy for review difficulty — a 12-line change to an access check still gets everyone.

## Merge, then fix

Merge the reviewers' findings into one list, deduplicating. A finding flagged independently by both models is higher-confidence — mark it. Separate **confirmed** findings (a concrete failure scenario a reader can follow) from **plausible** ones (suspicious but unproven).

Then dispatch **one fresh fixer subagent** given only the findings and the repo — not the review transcripts, not your intent — so it repairs what the review actually found rather than defending what anyone meant. The fixer commits its fixes to the same branch and, if the change came from a phased build, appends any judgement calls to `.git/lifecycle/implementation-notes.md`.

Post each round's findings as a PR comment (`gh pr comment`) so the PR carries the review record — and so a resumed run can count rounds done.

## The budget

**At most two review→fix rounds.** Round 2 reviews only what round 1's fixes touched plus any finding it disputed. After round 2, whatever remains is reported, not fixed:

- **Confirmed findings that weren't fixed** — say so plainly, with the reason.
- **Plausible, unconfirmed findings** — carry them to the final report as open questions ("Also flagged — plausible, unconfirmed: `file:line` — <failure scenario>"), never silently dropped and never counted as fixed.

The panel finds defects; it doesn't gate the merge. The merge decision belongs to the user, with the findings in front of them.
