---
name: maintain-prove-it
description: Improve a repo's generated verification skill (prove-<app>, made by /create-prove-it) from what its past runs learned. Runs after prove has run, at the end of a diff or on demand. Reads the receipts in .prove-it/runs/ (failed and blocked steps, retries, the commands that finally worked, steps that failed for reasons unrelated to the change) and any bug a user reports that slipped past prove, then fixes drifted steps, writes in the working commands, adds the check that would have caught a slipped bug and covers surfaces that recent diffs added. Proves every edit live and reports product bugs without touching product code. Use for /maintain-prove-it, "update the verify skill", "the verifier is out of date", "prove missed this bug", "prove keeps failing on unrelated steps", or after a big merge or refactor.
---

# Maintain Prove It

A verification skill goes stale the day the app changes: a route moves, a button gets renamed, a new surface ships with nothing in the skill that reaches it. A stale skill is worse than none, because the next agent will trust it. Every prove run leaves a receipt that shows where the skill struggled. This pass reads those receipts and folds what they learned back into the skill.

## Rules for the whole pass

- **Only edit the skill's own folder** (SKILL.md, scripts/). Never change product code here.
- **When the app and the skill disagree, work out which one is wrong.** The skill describing something the app no longer does is either *drift* (the app changed on purpose: fix the skill) or a *product bug* (the app broke: report it, don't rewrite the skill to match the bug). Read the commit that changed it. If you still can't tell, ask.
- **Every edit you make to the skill gets proved live before you finish.** An unproven edit is just more drift.
- **Old verdicts are leads, not evidence.** Earlier receipts, closed tickets and status docs tell you where to look. Only this pass's live runs count.
- **Never loosen a check to make a flaky step pass.** Record the failing run, then decide whether the app has a race or the check is ambiguous.

## 1. Find the skill

Look for `prove-*` folders under `.claude/skills/` and `.agents/skills/`, at the repo root and in package folders. Prefer ones with the `prove-it:` marker comment. If there are several, ask which. If there are none, stop and suggest `/create-prove-it`.

## 2. Read the past runs

List the receipts in `.prove-it/runs/`, newest first. Start from the runs since the skill last changed (`git log -1 --format=%cI -- <skill folder>` gives the date). If the skill is uncommitted or there are only a few runs, read them all. For each receipt, note:

- **Failed or blocked steps**, and what the receipt says caused them.
- **Retries and fixes**: the command, port, selector or auth step that finally worked after the written one didn't.
- **Steps that failed for reasons unrelated to the change.** These are the clearest sign of drift: the change was elsewhere, but the skill's own step broke.
- **Not covered** lines that keep coming back, and the unlock each one names.
- **Scope**: the surfaces each diff reached. A changed path the Scope map doesn't list, or a surface the run drove with no recipe in the skill, means the map is behind.

If there are no receipts, say so. Then the only inputs are reported bugs (step 3) and a fresh run on the current change.

## 3. Collect bugs that slipped past

If the user hasn't already said, ask whether anyone reported a bug that prove should have caught. For each one, find the receipt of the run that said PROVED on that change, and work out why it passed: the flow wasn't in scope, the step didn't look at the right thing, or the seed data hid it.

## 4. Sort what you found

Turn the notes into a list of edits, each tied to the receipt or bug that shows it is needed:

- **Drifted step**: the app changed on purpose and the step didn't. Fix the step.
- **Working command**: a retry found what works (a port, a wait, an auth step, a flag). Write it into the skill now, while the receipt still says exactly what it was.
- **Slipped bug**: add the check that would have caught it, and name that kind of bug in the surface's "Could fool you" notes along with what now catches it.
- **New surface or path**: recent diffs added a route, page, command, job or folder the Scope map doesn't reach. Add it to the map, with a drive recipe and "Done looks like" notes. Only call it new if you can name the file that adds it.
- **Removed surface**: take its map row and recipe out, citing the commit that removed it.
- **Launch changes** (new env var, port, service, migration, dependency): update Start and Health.
- **Product bug**: the app is really broken. Record it with the evidence. It is for the user, not this pass.

## 5. Edit and prove live

Make the edits. Then use the skill exactly as written: start, health check, and drive every step you touched, plus at least one break-it probe for each slipped-bug check you added. Where you can, also re-run the Scope step on the diff of a recent receipt and confirm it now names the surfaces that run needed. Save receipts in `.prove-it/runs/` as usual.

When a step fails:

1. Run the health check. If the instance itself is broken, fix the Start or Health section first, restart, and try again.
2. If the app works but the skill's step is wrong (a selector, a route, a command), that's drift: fix the step and re-drive it.
3. If the app is really broken, that's a product bug: record it with the evidence and move on.
4. If you can't reach a surface (missing account, missing service), record the exact prerequisite and the route you tried. If the skill didn't mention that prerequisite, that's drift too. Retry previously blocked surfaces whenever the tooling has changed (new seed data, a new driver, a sandbox).

A new check for a slipped bug counts only if it fails on the broken code. If the broken version is still in history, check it out in a scratch worktree under `/tmp` and run the check there. Otherwise suggest `/audit-prove-it` plant that bug next time.

Clean up after the last drive, including after failed attempts. Then check the evidence is still there and nothing you started is still running.

## 6. Report

- **Outcome:** `current` (nothing needed changing), `updated` (the skill changed, and every change was proved live) or `blocked` (say exactly what stopped you).
- What changed in the skill, one line each, with the receipt or bug that called for it.
- Product bugs found, with evidence. These are for the user to fix, not this pass.
- Surfaces left unproven and why.

If the repo uses git, leave the skill changes uncommitted unless the user asks you to commit.
