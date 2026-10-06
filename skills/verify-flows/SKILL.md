---
name: verify-flows
description: Prove a change actually works by running it — boot the real app against a real database, drive each user flow end-to-end, and leave one evidence file per flow. Use as the verify stage of task-lifecycle, or standalone whenever the user asks "does it actually work?", wants proof beyond passing tests, or a change is about to ship having only ever been read, not run.
---

# Verify the flows

Review reads the diff. Verifying **runs** it. A change that has only been reviewed has never executed, and the failure modes that survive review — a migration that doesn't apply, a route that 500s on real data, a button wired to nothing — are exactly the ones running it catches in minutes.

Verification runs in **its own fresh subagent** — booting a server and driving a browser is noisy, and isolating it keeps the main thread clean.

## Enumerate the flows first

From the spec or the diff, list the user flows the change creates or touches — each one a sentence: "a signed-in user transfers ownership and the ex-owner loses access". That list is the contract for this stage; name any flow you can't cover, and say why, rather than quietly covering less.

## Drive them for real

- **Boot the real app** the way the repo boots it — its dev server, its database (fresh or seeded, never mocked away), its queues if the flow needs them. If the repo has a boot recipe in its own docs or skills, use that rather than reinventing it.
- **Seed the data the flow needs**, then walk the flow the way a user would: Playwright for a web UI, the CLI for a CLI, curl for an API. Assert on what the user would see *and* on what the database now says — a 200 with no row written is a failure.
- **Screenshots or recordings for UI flows, transcripts for API/CLI flows.**

## One evidence file per flow

Each flow leaves behind its own proof: a screen recording or screenshot series for a UI flow, a text log of requests and responses for an API flow. Write them somewhere the user can open (`.git/lifecycle/evidence/`, or wherever the run keeps artefacts) and **read the evidence back before claiming the flow passed** — the assertion is on the evidence, not on the script exiting 0.

## Three outcomes, one budget

- **Pass** — report the flow as passing, with its evidence file.
- **Broke** — one round of fixes goes in (a fresh fixer subagent, briefed with the failure and the evidence), and that flow is re-verified **once**. A flow that fails again ships as a reported failure, not a second fix loop — the user decides what happens next.
- **Couldn't run** — the app wouldn't boot, a dependency is missing, the flow needs credentials you don't have. Say exactly that. A flow reported as "couldn't verify" is honest; a flow quietly skipped is a lie of omission.

The final report gets one line per flow: what was driven, pass/fail/couldn't-run, and the evidence file. If verify caught a runtime failure that was then fixed, say so — same as a review-driven fix.
