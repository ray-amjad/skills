---
name: idea-to-spec
description: Turn a rough feature idea or brief into a verified, implementation-ready technical spec through probed homework, a fresh-agent critique, a one-decision-at-a-time interview, and a confirmed playback. Use it to spec, plan, or define a feature, refactor, migration, workflow, or system change.
---

# Idea to Spec

Turn a rough idea into a short, evidence-backed spec made only of decisions the user made or confirmed. It has four parts: starting point, goals and non-goals, constraints, and proof.

## Sequence

The phases are gates. Never skip one silently.

1. **Homework.** Follow `references/homework.md` before asking question 1.

2. **Draft and critique.** Spend cheap agent effort before expensive user attention.
   - **Skip** only when a wrong build costs a rerun or an unpick (throw it away, or undo some code). A migrate or can't-undo change (data already written, a public API, a sent message) always gets this step. Say which rung of the rework ladder it is (rerun, unpick, migrate, can't undo) and why, in one line.
   - **Draft** the smallest spec from homework facts alone, in the spec's four parts, with every assumption marked as one and every policy value marked **(proposed)**. The draft decides nothing.
   - **Critique:** give the draft and the homework facts (each with source and date) to a fresh-context agent. Not a fork, not yourself, and without your reasoning. It hunts contradictions, unverified premises, silent decisions, missing actors, and arithmetic that breaks real limits, and returns its findings to you.
   - **Fold each finding in** as a homework re-check, a coverage-map area, or an interview question. Nothing from the draft reaches the spec without a decision from the user.

3. **Interview.** Follow `references/interview.md`: one decision per turn, 2 to 3 options, one recommendation.

4. **Check and play back.** Once answers stop changing the design, check them against each other and show the work in the chat:
   - Run each rule on the user's example and an edge case.
   - Give each shared field and irreversible effect one owner, and protect any sole copy of data.
   - For permission changes, a table of who (humans, agents, MCP tools, cron jobs, workers, webhooks) can do what. List every process that holds a new credential; one that also handles untrusted input is the user's decision.
   - For anything removed or renamed, list every reader (file:line). For a cutover, say what stops duplicate or missed work, and rollback.

   Any failure becomes an interview question, or a numbered default-to-veto if it is low-stakes, never a silent assumption. Then send the **playback**: one message that walks the spec's four parts in order, with each decision and its reason, the entrypoints and who owns each irreversible effect, each verifier with its surface and environment (and any environment to set up first), Promote on merge and Left to the agent, checks that did not apply, and a numbered defaults-to-veto list. Write nothing until the user confirms. Re-play any amended part verbatim until it is confirmed.

5. **Write.** Follow `references/spec-output.md`.

## Rules

- Facts come from this session's probes, commands, or primary sources. Never ask the user a fact the environment can answer.
- The user owns every decision: policy, thresholds, providers, durations, compatibility, permissions, destructive behavior. Auth, credentials, untrusted input, read-access changes, destructive actions, and overwriting a sole copy always get an explicit question, never a default-to-veto. A default-to-veto is a low-stakes value the agent proposes in the playback's numbered list; confirming the playback accepts it unless the user vetoes its number, and then it is a decision like any other.
- Working notes (facts with raw output, the draft and critique, the coverage map) go in the project's scratch folder if it has one, uncommitted. Otherwise they stay in the chat.
- Every invariant names where it is enforced or detected, marked machine-runnable or human-judgment. For a human-judgment check, propose a verifier that could replace it (a script, a user flow, a fresh agent with only the goal). A human-only check stays only if the user confirms it, lives in Constraints, and never counts as Proof.
- Every goal, invariant, and changed behavior gets its surface, then its verifier, both decided or confirmed by the user. The surface is where the user actually meets the claim (a page, the app, an API response, a Slack message, a row), and the check reads that surface, not the one that is convenient to test. A fully mocked test proves no goal.
- A verifier closes the loop: the agent runs it, gets pass or fail, and cannot argue past it. It can be a script, a scripted user flow, or a fresh agent that never saw the code and gets only the goal. The building agent reviewing its own work is not a verifier.

## Done

The user confirmed the playback, the spec is published where they chose, and it passes the same quick pass the user would give it:

- **Starting point:** the why is a root cause, and every fact has a source and a date.
- **Goals and non-goals:** each goal is an outcome someone else could check; each non-goal is something an eager agent would otherwise do.
- **Constraints:** every invariant says where it is checked.
- **Proof:** every goal and every machine-checked invariant has a surface and a check, and every check must pass to merge.
