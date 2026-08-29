---
name: idea-to-spec
description: Develop a rough feature idea or brief into a verified, implementation-ready technical spec through codebase homework, a one-decision-at-a-time interview, explicit entrypoint and trust-boundary design, a strawman draft critiqued by a fresh-context agent, consistency checks, and a user-confirmed playback before writing. Use it to spec, plan, or define a feature, refactor, migration, workflow, or system change.
---

# Idea to Spec

Turn a rough idea into a concise, evidence-backed spec containing only decisions the user made or explicitly confirmed. Treat the system's entrypoints—the "doors" through which intent enters and effects occur—as first-class design artifacts.

## Required sequence

The phases are gates. Do not reorder them, and never skip one silently. The only phase with a declared skip condition is step 4; a skip is one recorded line in the session record.

1. **Resolve the brief.** Read `$0` and every file it references. If `$0` is absent, use the user's request as the brief. Locate relevant project research and existing specs, but do not treat an old spec as evidence of current behavior.
2. **Create the session record.** Copy `templates/session-record.md` into the project's scratchpad directory; if the project has no scratchpad convention, use `.idea-to-spec/`. Do not commit the record unless the user asks.
3. **Homework.** Read `references/homework-and-verification.md` completely and follow it before asking question 1. Record current-state evidence and the runtime envelope.
4. **Draft and critique.** Read `references/draft-and-critique.md` completely. Draft the smallest strawman spec from homework facts alone, have a fresh-context agent critique it, and seed the interview agenda with what survives. Skippable only via the reference's declared skip condition, recorded in the session record.
5. **Interview.** Read `references/interview-and-coverage.md` completely. Build the coverage map, then ask exactly one decision per turn with 2–3 contrastive options and one visible recommendation. The interview is not finished until every goal, invariant, and changed behavior has a decided verifier.
6. **Design the doors.** Before closing the interview, read `references/doors-and-entrypoints.md` completely. Inventory the door set, dangerous effects, transport surfaces, refusals, and trust transitions. Door-design gaps are decisions, not assumptions.
7. **Prove consistency.** Read `references/consistency-and-playback.md` completely. Build the verb × actor matrix, run every applicable conditional inventory and every consistency check, and paste the shown work into the session record.
8. **Playback gate.** Send the exact full playback plus numbered defaults-to-veto. Paste that exact message into the session record. Do not write the spec until the user confirms it. Re-play amended portions until confirmed.
9. **Write and verify the spec.** After the playback is confirmed, ask one final decision: where the spec should be published, recommending a GitHub issue in the current repository. Then read `references/spec-output.md` completely and use `templates/technical-spec.md`. Re-read the published spec and run its final checks.

## Non-negotiable rules

- Facts come from current-session reads, commands, measurements, or primary-source fetches. Never ask the user a fact the environment can answer.
- The user owns decisions. The spec contains no policy, threshold, provider, duration, compatibility promise, permission, or destructive behavior they did not decide or confirm.
- Authentication, credentials, exposure to untrusted input, read-access changes, destructive actions, and overwriting a sole copy require explicit questions. They cannot be defaults-to-veto.
- Every invariant names an enforcement or detection point, marked machine-runnable or human-judgment-only; human-only checks on load-bearing invariants are explicit confirmed decisions.
- Verifiers are interview decisions. For every goal, invariant, and changed behavior, the user decides or confirms the check that proves it once implemented, and the spec's Verification plan contains only these decided verifiers. If a chosen verifier needs infrastructure that does not exist yet, recommend building it as separate work and record the best verifier that runs today.
- Every long-running or multi-item flow names its trigger, its terminal states, and its stopping rule — when it stops retrying and spending.
- Every changed flow appears in **Changes to existing behavior**.
- Every non-trivial door has a typed contract, one guarantee, named failures, real refusals, and a single owner for irreversible effects.
- An Open Question is allowed only when the user was asked and explicitly deferred it. An unasked question means the interview is unfinished.
- If a required check cannot run, write **"I could not verify this"** with its scope and consequence. Do not turn missing evidence into a decision.

## Done

Done means the confirmed spec is published at the destination the user chose; its facts are traceable; its decisions match the playback; its door set explains the system's purpose; its permission prose matches its actor matrix; its runtime arithmetic fits measured limits; and no required work remains hidden in Open Questions.
