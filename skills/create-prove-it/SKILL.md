---
name: create-prove-it
description: Generate a project-local verification skill (prove-<app>) that proves this repo's app really works, by launching it, health-checking it, driving it the way a user does (browser, CLI, API, database, logs), capturing evidence and cleaning up. Starts with a brainstorm of every way this repo could be verified, what each catches, what each costs and whether the agent can reach it from here, then lets the user pick. Use for /create-prove-it, "make a verify skill for this repo", "set up verification", "how should the agent check its own work here", "the agent keeps saying done without testing", or whenever a project has no repeatable way for an agent to prove a change works in the real app.
---

# Create Prove It

You are about to give this repo a skill that makes every future agent prove its work in the running app, instead of saying "done" because the code looks right or the tests pass.

The output is a project-local skill named `prove-<app>`, read cold by a future agent in the middle of some other task. Write it for that reader: exact commands, real selectors, no placeholders, nothing it has to work out.

The steps, in order:

1. Map the surfaces
2. Check you can reach them
3. Brainstorm methods, then let the user pick
4. Generate the skill
5. Seed the feature list
6. Run it once for real
7. Hand over

Don't skip step 6. A verification skill nobody has run is a guess.

## 1. Map the surfaces

A surface is where a user, human or program, meets the app. That is the only place a proof counts. Read the repo (README, package scripts, Makefile, routes, CLI entry points, Dockerfile, CI config, existing e2e specs) and list every surface you find:

| Surface | Typical sign in the repo |
|---|---|
| Web UI | pages/routes, a dev server script, HTML/JSX/Svelte/Vue files |
| HTTP API | route handlers, OpenAPI file, `fetch` clients |
| CLI / TUI | a `bin` entry, argparse/commander/clap/cobra, a `main` that reads argv |
| Database / stored state | migrations, ORM models, a JSON/SQLite file, a bucket |
| Background work | queues, cron, workers, webhooks, email sending |
| Desktop / mobile | Electron, Tauri, Xcode or Android projects |
| Library | a package export other code imports |
| Agent / prompt | prompts, tool definitions, an agent loop |

Code that is internal (a helper, a service class) is not a surface. Follow its callers until they end at one of the rows above, and note that path. It tells the future agent where to look when it changes that helper.

Name a primary surface (the one most users touch) and list the rest.

## 2. Check you can reach them

For each surface, find out whether *you*, from this machine and this session, can actually drive it. Do it, don't guess: start the app with its own dev command, hit the health route, look for a browser tool (Playwright MCP, Claude in Chrome, a Playwright install), check Docker, check whether the needed env vars and accounts exist.

If the checkout does not start as-is, fix it if the fix is small and obviously scaffolding (a missing sample config, an empty data dir), and say so. If it is a real break, report it precisely before going further: a skill written against a broken app teaches the wrong steps.

When a surface is out of reach, don't quietly drop it. Suggest the unlock that would make it reachable. See [references/unreachable-surfaces.md](references/unreachable-surfaces.md) for the common blockers and their fixes (sandbox or container, local emulator, headless browser, seeded test account, staging URL, simulator). The user decides whether the unlock is worth it; your job is to make sure they know it exists.

**Presence is not access.** For every key, env var or account the verifier will need, make one cheap authenticated call now (a whoami, a list, a login) and note the result. A variable that is set but empty, a secret that reads back blank or an expired token should surface here, not as a 401 forty minutes into a run. If features differ by role or plan, check one account per role. Then tell the user, in one message, exactly what is missing and what they would need to supply or sign in to. Stop before anything that takes their card, password or 2FA.

## 3. Brainstorm, then let the user pick

This is the step that makes the skill fit the repo instead of being a generic browser script.

Read [references/methods.md](references/methods.md) for the catalogue of verification methods. Keep only the ones that apply to the surfaces you found, and present them as one table:

| # | Method | Surface | Catches | Misses | Cost (setup / per run) | Reachable now? |
|---|---|---|---|---|---|---|

Rules for the table:

- **Catches and Misses are about this repo**, not the method in general. "Catches: the open count in the header not updating after a tick" beats "catches UI bugs".
- **Cost is honest.** Setup cost (install a browser, seed an account) and per-run cost (seconds, tokens, flakiness) are separate numbers.
- **Unreachable rows stay in**, with the unlock in the Reachable column ("No: needs Stripe test keys, or run `stripe listen` locally").

Under the table, recommend a combination in two or three sentences: usually the primary surface driven end to end, plus one cheap check that covers what the primary misses (a stored-state check under a UI flow, a log scan for swallowed errors).

Then ask the user to pick, as a multi-select question with the recommended combo first. Use your agent's question tool if it has one (AskUserQuestion in Claude Code), otherwise ask in chat and wait. If nobody can answer (a headless or scheduled run), go with the recommendation and say clearly in the final report that you chose for them.

## 4. Generate the skill

**Where it goes.** Write it into the project skills folder of the agent you are running in: `.claude/skills/prove-<app>/` for Claude Code, `.agents/skills/prove-<app>/` for Codex. If the repo already uses one of those folders, use that one. In a monorepo where only one package has the app, put it in that package's skills folder. Name it `prove-` plus a short app name (`prove-shop`, `prove-billing-api`), so `/prove-<app>` is what an agent types before saying done. If a `prove-*` skill made by Prove It already exists, don't overwrite it: read it, then extend it or add a sibling, and tell the user which you chose.

**What goes in it.** Follow [references/skill-template.md](references/skill-template.md). Every section must be filled from what you actually saw in steps 1 to 3:

- **Start**: the exact command, an isolated port and data location, and how to tell it is *usable*, not just listening. The start script must fully detach the app (redirect its stdin, stdout and stderr) so a caller doing `RUN=$(start.sh)` gets control back. A start script that hangs its caller is the most common first bug.
- **Health check**: one read-only command that answers "is this instance worth driving?" It also prints identity: which target (local, staging or prod, host, database) and which build (commit or version), so a check never runs against the wrong copy or a stale build. Don't trust "no rows found" until the store has shown a row you know exists.
- **Drive**: one recipe per method the user picked, with this repo's real selectors, routes and commands. Prefer stable handles (ARIA labels, test ids, route paths, exact CLI output) over coordinates or text that changes. Include a **bug fix** recipe: run the probe on the unchanged code first to see the failure and record the value that shows it (status, row count, text), then after the fix to see that value change. If the failure doesn't reproduce first, say so and stop.
- **Deploy check** (only if the user ships by deploying): wait until the new build is actually serving, then drive the public entry point (public URL, published package) with no insider shortcuts, and label each receipt line with the environment it came from.
- **Try to break it**: the probes worth running on this app (empty input, doing it twice, stale state, wrong method, bad id), plus a cold start (empty data, no optional secrets) and one sibling feature that should behave the same way.
- **Evidence and receipt**: where proof is saved and the receipt format.
- **Clean up**: stop only what this run started, and never delete the evidence.
- **Gotchas**: anything that tripped you up in step 2.

**Make the checks hard to fool.** When Prove It was tested, `/audit-prove-it` planted 7 bugs in a sample app. The agents doing the checking caught 5, but the generated scripts caught only 1. The rules below close the gaps it found:

- **Seed more than one record**, some in each state (two done, two open). With one row, "counts only the first", "ticks every row" and an off-by-one counter all pass.
- **Check every action in reverse too**: untick, undo, remove the thing you added.
- **Let stand-ins fail.** A fake email or payment provider that always says yes can't show you the error path. Give it a switch that makes it fail, and check the app reports the failure instead of claiming success.
- **Assert every field in "Done looks like"**, not just the one you care about today.
- **A script pass is not the verdict.** Scripted checks report "checks passed"; only the agent, having looked at the evidence, writes PROVED.

**Scripts.** Put repeatable mechanics in `scripts/` (start, health, stop, and a scripted check per method where possible). Make each one executable and show its exact invocation in SKILL.md. A scripted check is worth a lot here: `/audit-prove-it` can run it blind, and the next agent can rerun it in seconds.

**Evidence location.** Runs save to `.prove-it/runs/<UTC timestamp>-<slug>/` at the repo root. Add `.prove-it/` to `.gitignore`. Write evidence as it is produced, not at the end, so an interrupted run keeps what it proved.

## 5. Seed the feature list

Create `features.md` next to the skill's SKILL.md. It is the list of promises the app makes to its users, each with how to prove it. Start with the 3 to 6 most important user-facing features (from routes, commands, menus, README). Use this shape:

```markdown
| Feature | Surfaces | Touches | Last proved |
|---|---|---|---|
| Add a task | web, api, cli | server.js, public/app.js | 2026-10-30, a1b2c3d, .prove-it/runs/20261030-1412-add-task |

## Add a task
**Promise:** what the user expects, in their words.
**Prove it:** the drive steps, by method.
**Done looks like:** the observable end state, taken from what the user expects rather than from the latest diff, including side effects (row written, file saved, log line).
**Variants:** every role, plan, provider or platform this feature behaves differently on, each marked proved or unproven. The feature isn't proved while a variant is unproven.
**Known and deliberate:** behaviour that looks like a bug but is intended, so nobody reports it.
**Could fool you:** how this check could pass while the feature is broken, and what covers that.
```

"Touches" lists the files or routes the feature runs through. `/maintain-prove-it` matches it against git to work out which features need re-proving. Drop the Variants and Known lines when they don't apply.

The "Could fool you" line is what keeps the list honest, and what `/audit-prove-it` attacks later. If the seed data can't satisfy a feature's precondition, the proof fails and the reason goes in that line. Never weaken a proof to make it pass.

## 6. Run it once for real

Follow the generated skill exactly as written, as if you had never seen this repo: start, health check, drive ONE feature with every method the user picked, run at least one break-it probe, write the receipt, clean up. Then confirm:

- the receipt and screenshots still exist after cleanup,
- no process or port you started is still alive,
- the repo has no new untracked files except `.prove-it/` and the skill itself.

Anything that fails is a bug in the skill. Fix it, run cleanup, run again. Keep going until a clean run passes. Fill in "Last proved" for the feature you drove.

If you had to prove it in a stand-in (a container instead of the user's real setup, a local stack instead of staging), list every step the stand-in did for you that the real target will not.

## 7. Hand over

Report, briefly:

- the surfaces found and which ones are unreachable, with the unlock for each,
- the methods the user picked (or that you picked for them, and why),
- where the skill lives and how to invoke it,
- the receipt from the proving run, with the key evidence inline (command output, response body, a screenshot path),
- what is next: `/maintain-prove-it` after features change, `/audit-prove-it` to see whether the skill can be fooled.
