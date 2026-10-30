---
name: audit-prove-it
description: Try to fool a repo's verification skill (prove-<app>, made by /create-prove-it). Plants one deliberate bug at a time in the app, has the skill check the app without knowing what was planted, records whether it caught the bug, reverts exactly, and reports every miss with a suggested fix to the skill. Use for /audit-prove-it, "can the verifier be fooled", "test the verify skill", "is our verification any good", "mutation test the verifier", or after creating or heavily editing a prove-* skill.
---

# Audit Prove It

A verification skill that says PROVED on a broken app is worse than none: it gives false confidence. The only way to know it works is to break the app on purpose and see if it notices. This skill does that, safely, and reports every bug that slipped past.

## Safety first

You are about to edit product code on purpose. These rules keep that from hurting anyone:

- **Only in a git repo, only on local files.** Never against a shared, staging or production instance.
- **Never mutate a file that has uncommitted changes.** Check `git status --porcelain <file>` first. Pick another target or ask the user. This is what makes the revert exact.
- **One planted bug at a time.** Plant, check, revert, confirm the revert, then the next.
- **Confirm every revert** with `git diff --quiet -- <file>` (exit 0) before moving on. If it isn't clean, stop everything and restore with `git checkout -- <file>`.
- **Never commit, push or stash a planted bug.** At the end, `git status` must look exactly as it did at the start, plus any receipts in `.prove-it/` and the report.

## 1. Find the skill and baseline it

Find the `prove-*` skill (under `.claude/skills/` or `.agents/skills/`, with the `prove-it:` marker comment) and its features.md. If there are none, stop and suggest `/create-prove-it`.

Record `git status --porcelain` so you can compare at the end.

Run the skill once on the untouched app. **Every feature you'll target must come back PROVED.** If the clean app already fails, any "catch" later means nothing. Fix that first, or suggest `/maintain-prove-it`, and leave that feature out of the audit.

## 2. Plan the bugs

Plan 4 to 8 bugs, spread across features and across layers, so the audit finds the blind spots instead of hitting the same check eight times. [references/mutation-catalogue.md](references/mutation-catalogue.md) lists bug types by layer. Aim them at the "Could fool you" lines in features.md first, since those are the skill's own admitted weak spots.

Each bug must be:

- **Real**: something a plausible code change could cause, not a syntax error that crashes startup (that only tests the health check, and one of those is enough).
- **User-visible**: a user, or a program calling the app, would notice. If nobody could notice, no verifier should catch it.
- **Small**: a line or two, so the revert is trivial.

Write the plan as a table before you touch anything: id, feature, layer, file, the change, what a user would see.

## 3. Plant, check blind, revert

For each bug:

1. **Plant** the change. Restart the app if the skill's Start section says code changes need a restart.
2. **Check blind.** The checker must not know what you planted, or it will go looking for it, which proves nothing. If your agent can start a sub-agent (the Agent tool in Claude Code, or a subagent in Codex), give it only this: "Use the `prove-<app>` skill to verify `<feature>` in this repo, or the whole app. Report PROVED or BROKEN with evidence." No hint about the bug, the file or the layer. Tell it not to read `git diff`, `git status`, `git log` or `.prove-it/audits/`: the working tree is dirty during the check, so any of these would give the bug away. Tell it to keep any scratch files inside its run folder. If you can't start a sub-agent, run the skill's scripted checks only and mark the result "not blind" in the report.
3. **Score** it, and note *what* caught it: the skill's scripts, or the checking agent going off-script. A verifier whose scripts catch little relies on every future agent being as diligent as this one, so report both numbers. Results: **caught** (BROKEN, and the evidence names the planted symptom), **caught by luck** (BROKEN for an unrelated reason), or **missed** (PROVED, or BROKEN with evidence that doesn't touch the planted bug). If you aren't sure the evidence names the symptom, have a second sub-agent read the evidence and decide.
4. **Revert** with `git checkout -- <file>`, confirm with `git diff --quiet -- <file>`, run the skill's clean-up so no planted-bug instance stays alive.

## 4. Report

Restore check first: `git status --porcelain` matches the start. Then run the skill once more on the clean app. Any BROKEN verdict now is a false alarm, and it goes in the report too: a verifier that cries wolf gets ignored.

Write `.prove-it/audits/<UTC timestamp>/report.md` and show it:

```
# Prove It audit: <app>, <date>
Score: <caught>/<planted> caught (<n> by the scripts alone), <n> false alarms

| # | Feature | Layer | Planted bug | Result | Evidence |
|---|---|---|---|---|---|

## Misses
### <id>: <bug>
Why it slipped through: <the check that should have seen it and why it didn't>
Fix to the skill: <the exact step, probe or check to add>
```

Say plainly what the score means. A handful of planted bugs shows the misses this run found. A perfect score doesn't mean the verifier catches everything, so the next audit should use a different mix of layers.

For each miss, the fix is about the skill, never the app. Typical fixes: check stored state after the UI says success, read the error text instead of only the status code, check the exit code as well as the output, scan logs for swallowed errors, check the count or the second item, not just the first.

## 5. Offer to close the gaps

Ask the user whether to apply the fixes. If yes, edit only the skill's folder, then re-plant just the missed bugs and run the blind check again. A fix counts only when the re-run catches the bug. Revert and confirm as before. Add the bug that used to slip through to that feature's "Could fool you" line along with what now catches it.
