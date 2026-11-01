---
name: create-prove-it
description: Generate a project-local verification skill (prove-<app>) that an agent runs at the end of a change, before it says done. It works out from the diff (or a named flow) which surfaces and user flows the change reaches, drives them in the real app (browser, CLI, API, database, logs), compares the result with an answer key the builder did not write (an old system, a snapshot, an independent test suite or a spec), tries to break it and saves a receipt. The proof runs in a fresh sub-agent; a BROKEN verdict goes back to the builder to fix and re-check. Brainstorms the ways to verify this repo and lets the user pick. Works before a feature exists too: it maps the surfaces the feature will add, finds an existing surface to check parity against, or writes the spec first. Use for /create-prove-it, "I'm adding X and want to verify it", "make a verify skill for this repo", "the agent keeps saying done without testing", or when a project has no repeatable way to prove a change works in the real app.
---

# Create Prove It

You are about to give this repo a skill that makes every future agent prove its work in the running app, instead of saying "done" because the code looks right or the tests pass.

The output is a project-local skill named `prove-<app>`, read cold by a future agent in the middle of some other task. Write it for that reader: exact commands, real selectors, no placeholders, nothing it has to work out.

The steps, in order:

1. Map the surfaces
2. Check you can reach them
3. Find the answer key
4. Brainstorm methods, then let the user pick
5. Generate the skill
6. Run it once for real
7. Hand over

Don't skip step 6. A verification skill nobody has run is a guess.

Every check has three parts: a **surface** (where a real user or program meets the change), an **answer key** (what right looks like, written by someone other than the agent that made the change) and a **comparison** (does what happened match the answer key). Steps 1 and 2 find the surfaces, step 3 finds the answer keys, and the generated skill does the comparison.

## If the feature isn't built yet

Sometimes the user wants the verifier before the feature: "I'm adding an MCP server and it should behave like the app and the API." Run the same steps, with three differences:

- **In step 1**, map the surfaces the feature *will* add as well as the ones that exist, and mark the new ones planned.
- **In step 3**, look for an old-system answer key first. A new surface that does the same job as an existing one has an answer key ready: do the same action through both and check they end with identical data. For the MCP server, reading a record through MCP and through the API gives the same fields (read parity), bad input gets the same refusal from both (error parity), and creating, editing and deleting through MCP leaves the same stored state as doing it in the app (lifecycle round trip).
- **Where no existing surface covers a flow, write the spec now, before any code**, to `.prove-it/specs/<feature>.md`, and have the user approve it. One section per flow: what the user does, what they should see, what should be stored, what must not happen. Then name a second answer key for regressions: the app as it is today, kept runnable as an old system or saved as snapshots, for everything the feature should not change.

Then generate the skill as usual. The step 6 run proves what exists today and marks the flows that aren't built yet as pending.

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

## 3. Find the answer key

A check with no answer key only proves the agent agrees with itself. For each main flow, name what the check will compare against, and its rung on this ladder:

| Rung | Answer key | Example |
|---|---|---|
| 1 | An old system that already does the same job | The old version of the app; the Python service a Rust rewrite replaces; the web app and API a new MCP server must match |
| 2 | A snapshot: a saved copy of a result you know is good | A screenshot from before the change, saved API responses, CLI output, generated files |
| 3 | An independent test suite that does not depend on the code it checks | A behaviour suite that drives the public surface, like Bun's TypeScript tests when it was ported from Zig to Rust |
| 4 | A spec: flows and acceptance criteria written before the code | `.prove-it/specs/<feature>.md` |
| 5 | Nothing: the checking agent decides what right means | The weakest. Flag it |

- **Prefer the highest rung you can reach.** Refactors and ports usually get rungs 1 to 3: the behaviour shouldn't change, so the old behaviour is the answer. New features usually get a spec, plus a second answer key for regressions (the old version of the app). Even for a new feature, look for an old system first.
- **Say who wrote it.** A human, the old system, a snapshot taken from a version the user trusts, or a spec agreed before the code. Never the agent that will make future changes: it would grade its own work.
- **A spec has three rules.** It is written before the code. The agent building the change may not edit it; only the user does. It is specific enough to fail: "works well" can never fail, "shows 'Email is required' under the email field and creates no account" can.
- **Flag every flow whose only answer key is "nothing"** and tell the user. Offer the cheapest way up the ladder: a snapshot taken now from main, or a few lines of spec.

## 4. Brainstorm, then let the user pick

This is the step that makes the skill fit the repo instead of being a generic browser script.

Read [references/methods.md](references/methods.md) for the catalogue of verification methods. Keep only the ones that apply to the surfaces you found, and present them as one table:

| # | Method | Surface | Answer key | Catches | Misses | Cost (setup / per run) | Reachable now? |
|---|---|---|---|---|---|---|---|

Rules for the table:

- **Catches and Misses are about this repo**, not the method in general. "Catches: the open count in the header not updating after a tick" beats "catches UI bugs".
- **Cost is honest.** Setup cost (install a browser, seed an account) and per-run cost (seconds, tokens, flakiness) are separate numbers.
- **Answer key names the rung** ("1: same call through the REST API", "4: spec", "5: nothing"). A method with no answer key can still catch crashes and swallowed errors, but say so.
- **Unreachable rows stay in**, with the unlock in the Reachable column ("No: needs Stripe test keys, or run `stripe listen` locally").

Under the table, recommend a combination in two or three sentences: usually the primary surface driven end to end, plus one cheap check that covers what the primary misses (a stored-state check under a UI flow, a log scan for swallowed errors).

Then ask the user to pick, as a multi-select question with the recommended combo first. Use your agent's question tool if it has one (AskUserQuestion in Claude Code), otherwise ask in chat and wait. If nobody can answer (a headless or scheduled run), go with the recommendation and say clearly in the final report that you chose for them.

## 5. Generate the skill

**Where it goes.** Write it into the project skills folder of the agent you are running in: `.claude/skills/prove-<app>/` for Claude Code, `.agents/skills/prove-<app>/` for Codex. If the repo already uses one of those folders, use that one. In a monorepo where only one package has the app, put it in that package's skills folder. Name it `prove-` plus a short app name (`prove-shop`, `prove-billing-api`), so `/prove-<app>` is what an agent types before saying done. If a `prove-*` skill made by Prove It already exists, don't overwrite it: read it, then extend it or add a sibling, and tell the user which you chose.

**When it runs.** The generated skill runs at the end of a change or PR, before the agent says done. By default it proves the current change: uncommitted work plus the commits on the branch since it left its base. It reads the diff, follows each changed file to the surfaces and user flows it reaches (the same caller-following you did in step 1), drives those in the running app and tries to break them. A user can instead name a flow ("prove checkout"), and then it proves that flow. It never proves a fixed set of features in general: the diff decides what gets driven.

**What goes in it.** Follow [references/skill-template.md](references/skill-template.md). Every section must be filled from what you actually saw in steps 1 to 4:

- **Scope**: how to work out the diff (the base branch, the exact git commands) and a map from the repo's folders to the surfaces and flows they reach, so the next agent can go from a changed file to what to drive in one lookup. Internal code goes in the map with the path you traced in step 1.

- **Answer keys**: per flow, the answer key, its rung, where it lives (the old system's command, the snapshot path, the spec file) and who wrote it, with the rule: never edit an answer key to make a check pass. If the app and the answer key disagree, the verdict is BROKEN; only the user changes an answer key.
- **Check in a fresh agent**: the agent that made the change works out the scope, then, if it can start a sub-agent, hands the proof to a fresh one with only the flows, the surfaces and the answer keys. Not its plan or its reasoning: a checker that knows what was meant sees what it expects. If it can't start one, it runs the proof itself and marks the receipt "not independent".
- **If it is BROKEN**: the findings (failing steps, the answer key each was compared with, the evidence) go back to the agent that made the change. It fixes the app, never the answer key or the check, and the check runs again on the same flows. Cap it at 3 rounds, then report what is still broken.
- **Start**: the exact command, an isolated port and data location, and how to tell it is *usable*, not just listening. The start script must fully detach the app (redirect its stdin, stdout and stderr) so a caller doing `RUN=$(start.sh)` gets control back. A start script that hangs its caller is the most common first bug.
- **Health check**: one read-only command that answers "is this instance worth driving?" It also prints identity: which target (local, staging or prod, host, database) and which build (commit or version), so a check never runs against the wrong copy or a stale build. Don't trust "no rows found" until the store has shown a row you know exists.
- **Drive**: one recipe per method the user picked, with this repo's real selectors, routes and commands. Prefer stable handles (ARIA labels, test ids, route paths, exact CLI output) over coordinates or text that changes. Include a **bug fix** recipe: run the probe on the unchanged code first to see the failure and record the value that shows it (status, row count, text), then after the fix to see that value change. If the failure doesn't reproduce first, say so and stop.
- **Deploy check** (only if the user ships by deploying): wait until the new build is actually serving, then drive the public entry point (public URL, published package) with no insider shortcuts, and label each receipt line with the environment it came from.
- **Try to break it**: the probes worth running on this app (empty input, doing it twice, stale state, wrong method, bad id), plus a cold start (empty data, no optional secrets) and one sibling flow that should behave the same way.
- **Evidence and receipt**: where proof is saved and the receipt format.
- **Clean up**: stop only what this run started, and never delete the evidence.
- **Done looks like and could fool you**: where a flow has a higher answer key, point at it instead of restating it. Otherwise, per surface or method, a few lines on what a finished change looks like there (the end state a user expects, side effects included), what differs by role, plan or platform, behaviour that looks like a bug but is deliberate, and how a check on that surface could pass while the app is broken. Keep it short. This is what stops the next agent calling a half-done change done.
- **Gotchas**: anything that tripped you up in step 2.

**Make the checks hard to fool.** When Prove It was tested, `/audit-prove-it` planted 7 bugs in a sample app. The agents doing the checking caught 5, but the generated scripts caught only 1. The rules below close the gaps it found:

- **Seed more than one record**, some in each state (two done, two open). With one row, "counts only the first", "ticks every row" and an off-by-one counter all pass.
- **Check every action in reverse too**: untick, undo, remove the thing you added.
- **Let stand-ins fail.** A fake email or payment provider that always says yes can't show you the error path. Give it a switch that makes it fail, and check the app reports the failure instead of claiming success.
- **Assert everything the answer key and "Done looks like" name for that surface**, not just the field the change is about.
- **A script pass is not the verdict.** Scripted checks report "checks passed"; only the agent, having looked at the evidence, writes PROVED.

**Scripts.** Put repeatable mechanics in `scripts/` (start, health, stop, and a scripted check per method where possible). Make each one executable and show its exact invocation in SKILL.md. A scripted check is worth a lot here: `/audit-prove-it` can run it blind, and the next agent can rerun it in seconds.

**Evidence location.** Runs save to `.prove-it/runs/<UTC timestamp>-<slug>/` at the repo root. Add `.prove-it/runs/` and `.prove-it/audits/` to `.gitignore`. Specs and snapshots (`.prove-it/specs/`, `.prove-it/snapshots/`) are answer keys, so commit them. Write evidence as it is produced, not at the end, so an interrupted run keeps what it proved. The receipt records what was proved (the diff range or the flow), who checked it, the surfaces driven, each step's verdict, evidence and the answer key it was compared with, failed and retried steps, and the commands that finally worked. `/maintain-prove-it` reads these receipts later to improve the skill, so don't trim that detail.

## 6. Run it once for real

Follow the generated skill exactly as written, as if you had never seen this repo: start, health check, prove ONE named flow (the main thing the primary surface is for) with every method the user picked, in a fresh sub-agent if you can start one, run at least one break-it probe, write the receipt, clean up. Then confirm:

- the receipt and screenshots still exist after cleanup,
- no process or port you started is still alive,
- the repo has no new untracked files except `.prove-it/` and the skill itself.

Anything that fails is a bug in the skill. Fix it, run cleanup, run again. Keep going until a clean run passes. Then check the Scope step on a real diff: run it against the last commit that changed product code and confirm it names the surfaces and flows you would have picked by hand.

For a feature that isn't built yet, prove what exists today (the old system the new surface must match, the snapshots) and list the planned flows as pending in the receipt.

If you had to prove it in a stand-in (a container instead of the user's real setup, a local stack instead of staging), list every step the stand-in did for you that the real target will not.

## 7. Hand over

Report, briefly:

- the surfaces found and which ones are unreachable, with the unlock for each,
- the answer key and rung for each main flow, and every flow left on "nothing",
- the methods the user picked (or that you picked for them, and why),
- where the skill lives and how to invoke it,
- the receipt from the proving run, with the key evidence inline (command output, response body, a screenshot path),
- what is next: run `/prove-<app>` at the end of every change, `/maintain-prove-it` after prove has run a few times (or a bug slipped past it) to fold what the runs learned back into the skill, `/audit-prove-it` to see whether the skill can be fooled.
