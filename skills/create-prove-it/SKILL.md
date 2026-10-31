---
name: create-prove-it
description: Generate a project-local verification skill (prove-<app>) that an agent runs at the end of a change, before it says done. It works out from the diff (or a flow the user names) which surfaces and user flows the change reaches, then proves them in the real app by launching it, health-checking it, driving it the way a user does (browser, CLI, API, database, logs), trying to break it, saving a receipt and cleaning up. Starts with a brainstorm of every way this repo could be verified, what each catches, what each costs and whether the agent can reach it from here, then lets the user pick. Use for /create-prove-it, "make a verify skill for this repo", "set up verification", "how should the agent check its own work here", "the agent keeps saying done without testing", or whenever a project has no repeatable way for an agent to prove a change works in the real app.
---

# Create Prove It

You are about to give this repo a skill that makes every future agent prove its work in the running app, instead of saying "done" because the code looks right or the tests pass.

The output is a project-local skill named `prove-<app>`, read cold by a future agent in the middle of some other task. Write it for that reader: exact commands, real selectors, no placeholders, nothing it has to work out.

The steps, in order:

1. Map the surfaces
2. Check you can reach them
3. Brainstorm methods, then let the user pick
4. Generate the skill
5. Run it once for real
6. Hand over

Don't skip step 5. A verification skill nobody has run is a guess.

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

Name a primary surface (the one most users touch) and list the rest.

## 2. Check you can reach them

For each surface, find out whether *you*, from this machine and this session, can actually drive it. Do it, don't guess: start the app with its own dev command, hit the health route, look for a browser tool (Playwright MCP, Claude in Chrome, a Playwright install), check Docker, check whether the needed env vars and accounts exist.

If the checkout does not start as-is, fix it if the fix is small and obviously scaffolding (a missing sample config, an empty data dir), and say so. If it is a real break, report it precisely before going further: a skill written against a broken app teaches the wrong steps.

When a surface is out of reach, don't quietly drop it. Suggest the unlock that would make it reachable. See [references/unreachable-surfaces.md](references/unreachable-surfaces.md) for the common blockers and their fixes (sandbox or container, local emulator, headless browser, seeded test account, staging URL, simulator). The user decides whether the unlock is worth it; your job is to make sure they know it exists.

**Presence is not access.** For every key, env var or account the verifier will need, make one cheap authenticated call now (a whoami, a list, a login) and note the result. A variable that is set but empty, a secret that reads back blank or an expired token should surface here, not as a 401 forty minutes into a run. If the app behaves differently by role or plan, check one account per role. Then tell the user, in one message, exactly what is missing and what they would need to supply or sign in to. Stop before anything that takes their card, password or 2FA.

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

**When it runs.** The generated skill runs at the end of a change or PR, before the agent says done. By default it proves the current change: uncommitted work plus the commits on the branch since it left its base. It reads the diff, follows each changed file to the surfaces and user flows it reaches (the same caller-following you did in step 1), drives those in the running app and tries to break them. A user can instead name a flow ("prove checkout"), and then it proves that flow. It never proves a fixed set of features in general: the diff decides what gets driven.

**What goes in it.** Follow [references/skill-template.md](references/skill-template.md). Every section must be filled from what you actually saw in steps 1 to 3:

- **Scope**: how to work out the diff (the base branch, the exact git commands) and a map from the repo's folders to the surfaces and flows they reach, so the next agent can go from a changed file to what to drive in one lookup. Internal code goes in the map with the path you traced in step 1.

- **Start**: the exact command, an isolated port and data location, and how to tell it is *usable*, not just listening. The start script must fully detach the app (redirect its stdin, stdout and stderr) so a caller doing `RUN=$(start.sh)` gets control back. A start script that hangs its caller is the most common first bug.
- **Health check**: one read-only command that answers "is this instance worth driving?" It also prints identity: which target (local, staging or prod, host, database) and which build (commit or version), so a check never runs against the wrong copy or a stale build. Don't trust "no rows found" until the store has shown a row you know exists.
- **Drive**: one recipe per method the user picked, with this repo's real selectors, routes and commands. Prefer stable handles (ARIA labels, test ids, route paths, exact CLI output) over coordinates or text that changes. Include a **bug fix** recipe: run the probe on the unchanged code first to see the failure and record the value that shows it (status, row count, text), then after the fix to see that value change. If the failure doesn't reproduce first, say so and stop.
- **Deploy check** (only if the user ships by deploying): wait until the new build is actually serving, then drive the public entry point (public URL, published package) with no insider shortcuts, and label each receipt line with the environment it came from.
- **Try to break it**: the probes worth running on this app (empty input, doing it twice, stale state, wrong method, bad id), plus a cold start (empty data, no optional secrets) and one sibling flow that should behave the same way.
- **Evidence and receipt**: where proof is saved and the receipt format.
- **Clean up**: stop only what this run started, and never delete the evidence.
- **Done looks like and could fool you**: per surface or method, a few lines on what a finished change looks like there (the end state a user expects, side effects included), what differs by role, plan or platform, behaviour that looks like a bug but is deliberate, and how a check on that surface could pass while the app is broken. Keep it short. This is what stops the next agent calling a half-done change done.
- **Gotchas**: anything that tripped you up in step 2.

**Make the checks hard to fool.** When Prove It was tested, `/audit-prove-it` planted 7 bugs in a sample app. The agents doing the checking caught 5, but the generated scripts caught only 1. The rules below close the gaps it found:

- **Seed more than one record**, some in each state (two done, two open). With one row, "counts only the first", "ticks every row" and an off-by-one counter all pass.
- **Check every action in reverse too**: untick, undo, remove the thing you added.
- **Let stand-ins fail.** A fake email or payment provider that always says yes can't show you the error path. Give it a switch that makes it fail, and check the app reports the failure instead of claiming success.
- **Assert everything "Done looks like" names for that surface**, not just the field the change is about.
- **A script pass is not the verdict.** Scripted checks report "checks passed"; only the agent, having looked at the evidence, writes PROVED.

**Scripts.** Put repeatable mechanics in `scripts/` (start, health, stop, and a scripted check per method where possible). Make each one executable and show its exact invocation in SKILL.md. A scripted check is worth a lot here: `/audit-prove-it` can run it blind, and the next agent can rerun it in seconds.

**Evidence location.** Runs save to `.prove-it/runs/<UTC timestamp>-<slug>/` at the repo root. Add `.prove-it/` to `.gitignore`. Write evidence as it is produced, not at the end, so an interrupted run keeps what it proved. The receipt records what was proved (the diff range or the flow), the surfaces driven, each step's verdict and evidence, failed and retried steps, and the commands that finally worked. `/maintain-prove-it` reads these receipts later to improve the skill, so don't trim that detail.

## 5. Run it once for real

Follow the generated skill exactly as written, as if you had never seen this repo: start, health check, prove ONE named flow (the main thing the primary surface is for) with every method the user picked, run at least one break-it probe, write the receipt, clean up. Then confirm:

- the receipt and screenshots still exist after cleanup,
- no process or port you started is still alive,
- the repo has no new untracked files except `.prove-it/` and the skill itself.

Anything that fails is a bug in the skill. Fix it, run cleanup, run again. Keep going until a clean run passes. Then check the Scope step on a real diff: run it against the last commit that changed product code and confirm it names the surfaces and flows you would have picked by hand.

If you had to prove it in a stand-in (a container instead of the user's real setup, a local stack instead of staging), list every step the stand-in did for you that the real target will not.

## 6. Hand over

Report, briefly:

- the surfaces found and which ones are unreachable, with the unlock for each,
- the methods the user picked (or that you picked for them, and why),
- where the skill lives and how to invoke it,
- the receipt from the proving run, with the key evidence inline (command output, response body, a screenshot path),
- what is next: run `/prove-<app>` at the end of every change, `/maintain-prove-it` after prove has run a few times (or a bug slipped past it) to fold what the runs learned back into the skill, `/audit-prove-it` to see whether the skill can be fooled.
