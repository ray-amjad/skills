# Verification methods

The menu for the brainstorm in step 4. Keep only the rows that match a surface you found. Rewrite "catches" and "misses" in terms of the actual repo before you show them to the user.

Most methods are ways to drive a surface. Four of them (old system parity, shadow traffic, snapshot, an independent test suite) are also answer keys: they say what right looks like. Their rung on the ladder is noted.

## Old system parity

Drive the same action through the old system and the new one, or through two surfaces that should agree (the web app and its API, the API and a new MCP server), then compare the outputs and the stored state each one leaves.

- **Catches:** behaviour that drifted in a port or a refactor, and a new surface that disagrees with the one users already trust: a missing field, a different error for the same bad input, a write that lands differently.
- **Misses:** bugs both systems share, and behaviour the old system never had. Differences that are meant (new ids, timestamps, a bug the new one fixes) need a written list, or every run is noise.
- **Cost:** the old system has to run beside the new one (main in a worktree under `/tmp`, the deployed build, or a second port). Per run, about twice the drive.
- **Answer key:** rung 1, the strongest. Check read parity, error parity and a lifecycle round trip (create, edit, delete through one surface, read back through the other).
- **Where it is used:** a new flow on a surface that copies another (the MCP server and the app), an existing flow when the base commit runs beside the change, and every flow in a migration skill.
- **Misses, again:** when one change edits both sides, they can be wrong the same way and parity still passes. Pair it with the spec then.

## Shadow traffic and output diffs (migrations)

Send the same inputs to the old system and the new one: a copy of real requests, recorded traffic replayed, or a fixed set of cases. Diff the responses, the output files or the stored state byte for byte, after normalising the allowed differences.

- **Catches:** any behaviour the rewrite changed, on inputs nobody thought to write a test for.
- **Misses:** paths the inputs never reach. A diff that ignores too much (a normaliser that strips whole fields) hides real breaks, so keep the allowed-differences list short and agreed with the user.
- **Cost:** the old system keeps running for the whole migration. Shadow traffic needs a place to copy requests (a proxy, a queue tap) and must never let the new system's writes reach real data.
- **Answer key:** rung 1. At the end step, the cases become snapshots in the permanent skill.

## Browser, driven like a user

Drive the real page with Playwright (MCP, library or CLI) or Claude in Chrome: click, type, wait for the result, screenshot.

- **Catches:** broken wiring between page and API, state not refreshing, buttons that do nothing, client-side errors, layout that hides a control.
- **Misses:** whether the data was really saved (the page can show optimistic state), server errors the UI swallows, anything off the clicked path.
- **Cost:** setup is a browser install (Playwright downloads Chromium once). Per run, 10 to 60 seconds. Flakier than the other methods; stable selectors (ARIA labels, test ids) cut most of it.
- **Tip:** a Playwright *script* is reusable and auditable; an MCP session is faster to write but has to be redone each time. Prefer a script for the core flows.
- **Gotcha:** `npx playwright install` deletes older browser builds from the shared cache that other projects may still use. Install the library into a git-ignored folder, pin the version that matches a browser already in the cache, and only run `playwright install` if launching Chromium fails.

## HTTP API calls

`curl` or a small script against the running server. Check status, body and headers.

- **Catches:** wrong status codes, bad validation, missing fields, auth holes, contract drift.
- **Misses:** everything the UI does with the response; anything only the UI sends (headers, ordering).
- **Cost:** near zero setup, under a second per call. The cheapest strong check there is.

## CLI / TUI, run in a real terminal

Run the binary as a user would. Capture stdout, stderr and the exit code. For interactive tools, drive a tmux or PTY session and capture the pane.

- **Catches:** wrong output, wrong exit codes, broken arg parsing, bad error messages, help text drift.
- **Misses:** output that looks right but came from stale or cached state.
- **Cost:** low. Use a separate tmux socket (`tmux -L <name>`) so you never touch the user's sessions.

## Stored-state check

After a drive, read the real store: SQL query, the JSON or SQLite file, the bucket, the cache key.

- **Catches:** the UI or API claiming success while nothing was written, partial writes, wrong values persisted, duplicates.
- **Misses:** whether a user can see it. Pair it with a surface drive, never use it alone.
- **Cost:** low if the store is local. Needs read access and the schema.

## Log and error scan

Tail the server's logs during the drive and scan for errors, warnings and stack traces afterwards.

- **Catches:** errors that were swallowed and turned into a 200 or a blank state, slow queries, retries, deprecation warnings.
- **Misses:** logic bugs that log nothing.
- **Cost:** near zero if the app logs to stdout. Point the start script's output at a file in the run folder.

## Side-effect capture

Catch what leaves the app: emails (Mailpit, a log transport), webhooks (a local listener, `stripe listen`), queue messages, files written.

- **Catches:** "sent" that never sent, wrong recipient, wrong payload.
- **Misses:** delivery in the real provider.
- **Cost:** medium setup (a local catcher), cheap per run.

## Snapshot

Save a known good result before the change (a screenshot, API response bodies, CLI output, generated files) to `.prove-it/snapshots/`, then compare after. Snapshots are answer keys, so commit them.

- **Catches:** layout and output regressions no assertion mentions, a response field that quietly changed, a generated file that grew a line.
- **Misses:** whether the result was right in the first place. A snapshot shows "same as before", not "correct", so a bug in the snapshot becomes the answer. Take it from a version the user trusts (main, the deployed build), never from the change being proved.
- **Cost:** medium. Mask dynamic content (timestamps, ids, avatars, animation) or every run differs. A change that is meant to alter the output needs the user to approve a new snapshot; the checker never replaces one to make a run pass.
- **Answer key:** rung 2.

## Measurable budget

A number the user sets, measured on the running app: layout shift and the other Core Web Vitals from a Chrome DevTools performance trace, page load or response time, an accessibility score, bundle size, zero console errors, cost or tokens per request.

- **Catches:** the page that jumps as it loads, the slow query a change added, the button with no label, the warning nobody reads. Things that work but are worse.
- **Misses:** whether the feature does the right thing. Pair it with a drive, never use it alone.
- **Cost:** low to medium. Pick a tool the agent can run every time (Chrome DevTools MCP, Lighthouse CLI, axe, `curl -w`), and measure more than once when the number is noisy. With no DevTools MCP, measure layout shift in Playwright with a `PerformanceObserver` on `layout-shift` entries.
- **Answer key:** the budget itself, set by the user, never by the checker. Pass or fail is a number, so no judgment is needed.

## Library boundary

Write a tiny sample program that imports the package the way a consumer does (the public export, not `./src/...`) and run it.

- **Catches:** broken exports, packaging mistakes, API changes that break callers.
- **Misses:** internal paths the public API does not reach.
- **Cost:** low.

## Agent / prompt behaviour

Run the agent on a fixed scenario and capture what it does: tool calls, final answer.

- **Catches:** prompt regressions, tools never being called, wrong tool arguments.
- **Misses:** rare paths. Results vary run to run, so judge several runs, not one.
- **Cost:** tokens and minutes per run.

## Existing test suite

Run the repo's own tests.

- **Catches:** what the tests already cover.
- **Misses:** everything the tests mock, and everything the running app does differently from the tests.
- **Cost:** whatever CI costs.
- **Note:** list it so the user sees the trade-off, but it never counts as proof on its own. Proof means the running app was observed.
- **Answer key:** rung 3, but only when the suite does not depend on the code it checks: it drives the public surface and would pass against any correct implementation (Bun's TypeScript tests when it was ported from Zig to Rust). Unit tests written next to the code, or by the agent making the change, are not an answer key.
