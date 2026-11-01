---
name: maintain-prove-it
description: Improve a repo's generated verification skill from what its past runs learned. Works on both kinds made by /create-prove-it, the permanent prove-<app> and a temporary prove-<migration>. Reads the receipts in .prove-it/runs/ (failed and blocked steps, retries, the commands that finally worked, steps that failed for reasons unrelated to the change, how each change was sorted into checks) and any bug that slipped past prove, then fixes drifted steps, writes in the working commands, adds the check that would have caught a slipped bug and a section for any new surface. For a temporary skill it checks whether the migration is done and, if so, suggests the end step. Never rewrites an answer key (spec, snapshot, old system) to match the app. Proves every edit live and reports product bugs without touching product code. Use for /maintain-prove-it, "update the verify skill", "the verifier is out of date", "prove missed this bug", "prove keeps failing on unrelated steps", or after a big merge or migration milestone.
---

# Maintain Prove It

A verification skill goes stale the day the app changes: a route moves, a button gets renamed, a new surface ships with nothing in the skill that reaches it. A stale skill is worse than none, because the next agent will trust it. Every prove run leaves a receipt that shows where the skill struggled. This pass reads those receipts and folds what they learned back into the skill.

## Rules for the whole pass

- **Only edit the skill's own folder** (SKILL.md, scripts/). Never change product code here.
- **When the app and the skill disagree, work out which one is wrong.** The skill describing something the app no longer does is either *drift* (the app changed on purpose: fix the skill) or a *product bug* (the app broke: report it, don't rewrite the skill to match the bug). Read the commit that changed it. If you still can't tell, ask.
- **Answer keys are not the skill's steps.** The user's spec, the snapshots in `.prove-it/snapshots/` and the old system a flow is compared with say what right looks like. A drifted step can be fixed, but an answer key that disagrees with the app is reported to the user, never rewritten to match. Only the user changes one.
- **Every edit you make to the skill gets proved live before you finish.** An unproven edit is just more drift.
- **Old verdicts are leads, not evidence.** Earlier receipts, closed tickets and status docs tell you where to look. Only this pass's live runs count.
- **Never loosen a check to make a flaky step pass.** Record the failing run, then decide whether the app has a race or the check is ambiguous.

## 1. Find the skill

Look for `prove-*` folders under `.claude/skills/` and `.agents/skills/`, at the repo root and in package folders. Prefer ones with the `prove-it:` marker comment. The marker says which kind it is: `permanent skill` (the app, one section per surface) or `temporary migration skill` (one migration, deleted at its end step). If there are several, ask which. If there are none, stop and suggest `/create-prove-it`.

## 2. Read the past runs

List the receipts in `.prove-it/runs/`, newest first. Start from the runs since the skill last changed (`git log -1 --format=%cI -- <skill folder>` gives the date). If the skill is uncommitted or there are only a few runs, read them all. For each receipt, note:

- **Failed or blocked steps**, and what the receipt says caused them.
- **Retries and fixes**: the command, port, selector or auth step that finally worked after the written one didn't.
- **Steps that failed for reasons unrelated to the change.** These are the clearest sign of drift: the change was elsewhere, but the skill's own step broke.
- **Not covered** lines that keep coming back, and the unlock each one names.
- **Scope**: the surfaces each diff reached. A changed path the Scope map doesn't list, or a surface the run drove with no section in the skill, means the map is behind.
- **What the change touches**: each flow the run listed as new or existing, its answer key, and any smoke test. A run that checked the whole app, skipped an existing flow behind shared code the change touched, or checked a new flow on parity alone when the change edited both sides, means the Sort checklist or the Scope map's shared-code rows need fixing.
- **Answer keys used**: new flows marked `no answer key` again and again means specs aren't reaching the skill. Say so, and suggest where the user could put them (the PR body, a file in the diff).

If there are no receipts, say so. Then the only inputs are reported bugs (step 4) and a fresh run on the current change.

## 3. For a temporary skill, check whether the migration is done

Look at the evidence, not the plan. When every area in the Scope table is moved and the last run is green, suggest the end step now, before the PR that deletes the old system: the snapshots must be recorded while the old system still runs. Also suggest it if the old system's code is removed or about to be, or all traffic is on the new system. The end step is: save the cases as snapshots, add them to `prove-<app>`, prove them there, then delete the temporary skill. Don't run it without their OK. If the old system is already gone and the end step never ran, say so plainly: the cases can no longer be recorded from it, so the snapshots must come from the last receipts that ran it, or the new system as it is now, marked as the weaker key.

If it isn't done, update the Scope table's Moved column from the commits since the skill last changed.

## 4. Collect bugs that slipped past

If the user hasn't already said, ask in your first message, before the other work, whether anyone reported a bug that prove should have caught. For each one, find the receipt of the run that said PROVED on that change, and work out why it passed: the flow wasn't in scope, the step didn't look at the right thing, or the seed data hid it.

## 5. Sort what you found

Turn the notes into a list of edits, each tied to the receipt or bug that shows it is needed:

- **Drifted step**: the app changed on purpose and the step didn't. Fix the step.
- **Working command**: a retry found what works (a port, a wait, an auth step, a flag). Write it into the skill now, while the receipt still says exactly what it was.
- **Slipped bug**: add the check that would have caught it, and name that kind of bug in the surface's "Could fool you" notes along with what now catches it. If the flow had no answer key (rung 5), propose one: a parity check against an old system, a snapshot from a trusted version, or spec lines the user approves.
- **New surface or path**: recent diffs added a route, page, command, job or folder the Scope map doesn't reach. Add it to the map. A new path on a known surface goes into that surface's section. A whole new surface gets its own section, with a drive recipe, what it copies (its parity answer key, if an existing surface does the same job) and "Done looks like" notes. Only call it new if you can name the file that adds it.
- **Shared code moved**: a schema, auth, nav or shared module was added, split or renamed. Update its row in the Scope map so the skill still finds the existing flows behind it.
- **Removed surface**: take its map row and recipe out, citing the commit that removed it.
- **Launch changes** (new env var, port, service, migration, dependency): update Start and Health.
- **Answer key disagrees with the app**: a spec line, a snapshot or the old system no longer matches what the app does. Don't touch it. Report it with the evidence, and the commit that changed the behaviour, so the user can decide whether the app or the answer key is wrong.
- **Product bug**: the app is really broken. Record it with the evidence. It is for the user, not this pass.

## 6. Edit and prove live

Make the edits. Then use the skill exactly as written: start, health check, and drive every step you touched, plus at least one break-it probe for each slipped-bug check you added. Where you can, also re-run the Scope step on the diff of a recent receipt and confirm it now names the surfaces that run needed. Save receipts in `.prove-it/runs/` as usual.

When a step fails:

1. Run the health check. If the instance itself is broken, fix the Start or Health section first, restart, and try again.
2. If the app works but the skill's step is wrong (a selector, a route, a command), that's drift: fix the step and re-drive it.
3. If the app is really broken, that's a product bug: record it with the evidence and move on.
4. If you can't reach a surface (missing account, missing service), record the exact prerequisite and the route you tried. If the skill didn't mention that prerequisite, that's drift too. Retry previously blocked surfaces whenever the tooling has changed (new seed data, a new driver, a sandbox).

A new check for a slipped bug counts only if it fails on the broken code. If the broken version is still in history, check it out in a scratch worktree under `/tmp` and run the check there. Otherwise suggest `/audit-prove-it` plant that bug next time.

Clean up after the last drive, including after failed attempts. Then check the evidence is still there and nothing you started is still running.

## 7. Report

- **Outcome:** `current` (nothing needed changing), `updated` (the skill changed, and every change was proved live) or `blocked` (say exactly what stopped you).
- What changed in the skill, one line each, with the receipt or bug that called for it.
- Product bugs found, with evidence. These are for the user to fix, not this pass.
- Answer keys that disagree with the app, and answer keys you propose, for the user to approve.
- For a temporary skill: whether the migration looks done, the evidence, and whether you suggested the end step.
- Surfaces left unproven and why.

If the repo uses git, leave the skill changes uncommitted unless the user asks you to commit.
