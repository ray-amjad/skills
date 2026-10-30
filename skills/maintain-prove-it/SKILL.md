---
name: maintain-prove-it
description: Keep a repo's generated verification skill (prove-<app>, made by /create-prove-it) and its features.md current as the app changes. Finds what changed since each feature was last proved, updates the feature list, re-proves features live in the running app, fixes the skill where it drifted and reports real product bugs without touching product code. Use for /maintain-prove-it, "update the verify skill", "the verifier is out of date", "we added features, refresh the feature list", after a big merge or refactor, or when a prove-* skill fails on steps that have nothing to do with the change being checked.
---

# Maintain Prove It

A verification skill goes stale the day the app changes: a route moves, a button gets renamed, a new feature ships with no proof attached. A stale skill is worse than none, because the next agent will trust it. This pass brings the skill back in line with the app and stamps every feature with fresh proof.

## Rules for the whole pass

- **Only edit the skill's own folder** (SKILL.md, features.md, scripts/). Never change product code here.
- **When the app and the skill disagree, work out which one is wrong.** The skill describing something the app no longer does is either *drift* (the app changed on purpose: fix the skill) or a *product bug* (the app broke: report it, don't rewrite the skill to match the bug). Read the commit that changed it. If you still can't tell, ask.
- **Every claim you add to the skill gets proved live before you finish.** An unproven edit is just more drift.
- **Old verdicts are leads, not evidence.** Earlier receipts, closed tickets and status docs tell you where to look. Only this pass's live receipts count.

## 1. Find the skill

Look for `prove-*` folders under `.claude/skills/` and `.agents/skills/`, at the repo root and in package folders. Prefer ones with the `prove-it:` marker comment and a `features.md`. If there are several, ask which. If there are none, stop and suggest `/create-prove-it`.

## 2. Work out what changed

Each feature in features.md records the commit it was last proved at and the files it touches. For each feature, list what changed since its own proof and match it against its Touches column:

```bash
git diff <its last-proved commit>..HEAD --name-only
```

A feature whose files changed needs re-proving. Say which ones you skipped and why. If a feature has no commit recorded (an older skill), use the skill's last commit and add the column as you go.

Then look at the whole range since the oldest proof and sort the changes into:

- **Touches a mapped feature**: that feature needs re-proving and probably a doc update.
- **New user-facing surface** (a new route, page, command, flag, job): a candidate new feature. Only call it new if you can name the file that adds it.
- **Removed surface**: its feature entry goes, or gets marked removed with the commit.
- **Launch changes** (new env var, port, service, migration, dependency): the Start and Health sections need updating. A hosting, infrastructure or dependency change makes every feature stale, so re-prove them all.
- **Internal only**: follow it to the surface it reaches. If it reaches a mapped feature, that feature needs re-proving.

If the user asked for a full pass, re-prove every feature regardless of the diff.

## 3. Update the feature list

Edit features.md: add new features (Promise, Prove it, Done looks like, Could fool you), update the ones whose steps changed, remove the dead ones. Keep the table and the sections in sync.

## 4. Re-prove live

Use the skill exactly as written: start, health check, then drive every feature on your list with the methods the skill names, plus at least one break-it probe per changed feature. Save a receipt per feature in `.prove-it/runs/`.

When a step fails:

1. Run the health check. If the instance itself is broken, fix the Start or Health section first, restart, and try again.
2. If the app works but the skill's step is wrong (a selector, a route, a command), that's drift: fix the step and re-drive it.
3. If the app is really broken, that's a product bug: record it with the evidence, mark the feature BROKEN, and move on.
4. If you can't reach a feature (missing account, missing service), record the exact prerequisite and the route you tried. If the skill didn't mention that prerequisite, that's drift too. Retry previously blocked features whenever the tooling has changed (new seed data, a new driver, a sandbox).

Never loosen a check to make a flaky step pass. Record the failing run, then decide whether the app has a race or the check is ambiguous.

Clean up after the last drive, including after failed attempts. Then check the evidence is still there and nothing you started is still running.

## 5. Learn from what slipped through

If someone reported a bug the verifier missed, add the check that would have caught it, name that kind of bug in the feature's "Could fool you" line, and suggest `/audit-prove-it` plant it next time. If it took trial and error to make a feature provable, write the exact commands, ports and auth steps that finally worked into the skill now, while you still know them.

## 6. Stamp and report

Update "Last proved" for every feature you proved: date, commit and receipt path. Then report:

- **Outcome:** `current` (nothing needed changing), `updated` (the skill changed, and every change was proved live) or `blocked` (say exactly what stopped you).
- What changed in the skill, one line each.
- Product bugs found, with evidence. These are for the user to fix, not this pass.
- Features left unproven and why.

If the repo uses git, leave the skill changes uncommitted unless the user asks you to commit.
