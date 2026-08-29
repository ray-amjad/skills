---
name: idea-to-spec
description: Develop a rough feature idea or brief into a verified, implementation-ready technical spec through codebase homework, a one-decision-at-a-time interview, explicit entrypoint and trust-boundary design, a strawman draft critiqued by a fresh-context agent, consistency checks, and a user-confirmed playback before writing. Use it to spec, plan, or define a feature, refactor, migration, workflow, or system change.
---

# Idea to Spec

Turn a rough idea into a concise, evidence-backed spec containing only decisions the user made or explicitly confirmed. Treat the system's entrypoints—the "doors" through which intent enters and effects occur—as first-class design artifacts.

## Required sequence

The phases are gates. Do not reorder them, and never skip one silently. The only phase with a declared skip condition is step 3; a skip is one recorded line in the session record.

1. **Resolve the brief and create the session record.** Read `$0` and every file it references; if `$0` is absent, use the user's request as the brief. Locate relevant project research and existing specs, but do not treat an old spec as evidence of current behavior. Copy `templates/session-record.md` into the project's scratchpad directory (default `.idea-to-spec/`); do not commit it unless the user asks.
2. **Homework.** Read `references/homework-and-verification.md` completely and follow it before asking question 1. Record current-state evidence and the runtime envelope.
3. **Draft and critique.** Read `references/draft-and-critique.md` completely. Draft the smallest strawman spec from homework facts alone, have a fresh-context agent critique it, and seed the interview agenda with what survives. Skippable only via the reference's declared skip condition.
4. **Interview.** Read `references/interview-and-coverage.md` completely. Build the coverage map, then ask exactly one decision per turn with 2–3 contrastive options and one visible recommendation.
5. **Design the doors — the interview is still open.** Read `references/doors-and-entrypoints.md` completely. Inventory the door set, dangerous effects, transport surfaces, refusals, and trust transitions. Door-design gaps are decisions and return to the interview. The interview closes only when the door inventory is complete and every goal, invariant, and changed behavior — including any surfaced by door work — has a decided verifier.
6. **Prove consistency.** Read `references/consistency-and-playback.md` completely. Build the verb × actor matrix, run every applicable conditional inventory and every consistency check, and paste the shown work into the session record.
7. **Playback gate.** Follow the playback section of the reference already read in step 6 — no new file. Send the exact full playback plus a numbered defaults-to-veto list: low-stakes proposed values that confirming the playback accepts unless the user vetoes their numbered line. Paste the exact sent message into the session record. Do not write the spec until the user confirms; re-play amended portions until confirmed.
8. **Write and verify the spec.** After confirmation, read `references/spec-output.md` completely, ask the one destination decision it defines, then write the spec with `templates/technical-spec.md`, publish it, re-read it, and run its final checks.

## Non-negotiable rules

- Facts come from current-session reads, commands, measurements, or primary-source fetches. Never ask the user a fact the environment can answer.
- The user owns decisions. The spec contains no policy, threshold, provider, duration, compatibility promise, permission, or destructive behavior they did not decide or confirm.
- Never-default decisions require explicit questions and can never be defaults-to-veto: authentication and session behavior, credential custody, exposure to untrusted input, changes to read access, destructive operations, and anything that can overwrite a sole copy of data (user-authored or not).
- Every invariant names an enforcement or detection point, marked machine-runnable or human-judgment-only; a human-only check on a load-bearing invariant is an explicit confirmed decision.
- Verifiers are interview decisions. For every goal, invariant, and changed behavior, the user decides or confirms the check that proves it once implemented, and the spec's Verification plan contains only these decided verifiers.
- Every long-running or multi-item flow names its trigger, its terminal states, and its stopping rule — when it stops retrying and spending.
- Every changed flow appears in **Changes to existing behavior**.
- Every non-trivial door — one that accepts untrusted input, performs a side effect, or crosses a trust boundary — has a typed contract, one guarantee, named failures, real refusals, and a single owner for irreversible effects.
- An Open Question is allowed only when the user was asked and explicitly deferred it. An unasked question means the interview is unfinished.
- If a required check cannot run, write **"I could not verify this"** with its scope and consequence. Do not turn missing evidence into a decision.

## Done

Done means the confirmed spec is published at the destination the user chose; its facts are traceable; its decisions match the playback; its door-names list reads as a plain statement of what the system does; its permission prose matches its actor matrix; its runtime arithmetic fits measured limits; and no required work remains hidden in Open Questions.
