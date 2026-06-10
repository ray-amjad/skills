---
name: spec-developer-v2
description: Interview the user about a rough idea or brief with sharp, non-obvious product and technical questions, then write a concise implementation-ready spec. Use when the user wants to spec something out, develop a vague idea into requirements, or turn a product concept into a detailed plan.
---

Read $1 and interview me in detail using the AskUserQuestionTool about:
- Technical implementation
- UI and UX
- Concerns
- Tradeoffs
- Boundary cases the brief does not mention

Ask non-obvious questions. Do not spend turns confirming what is already clear from the
brief.

Ask one natural question at a time. Keep questions short enough for the user to answer
directly, and do not bundle several decisions into one long prompt. If a draft question
asks for multiple decisions, split it into separate turns and ask the highest-risk decision
first.

Before asking, rewrite list-like questions into the underlying decision. Prefer questions
that force a source of truth, owner, lifecycle transition, override rule, or failure
behavior instead of reciting every possible option.

During the interview, uncover the hidden product invariants and boundary definitions:
source of truth, lifecycle states, identity and permission boundaries, consent, privacy,
what can change silently, what requires confirmation, and what must remain auditable.

Ask at least one question about the product's core value transformation: what gets
combined, simplified, ranked, inferred, netted, hidden, recommended, automated, or handed
off. Clarify what makes the transformed result correct, who can override it, and what
evidence remains when someone disagrees.

Ask at least one technical operations question about where state lives, when decisions run,
and how offline use, retries, stale data, sync conflicts, or failed automation are
reconciled.

Ask at least one coverage-boundary question about where the product logic applies and where
it should stop: unusual inputs, account/session contexts, devices, locations, timezones,
content types, user states, or external systems that do not match the happy path.

If the product depends on schedules, deadlines, recurring windows, bookings, reminders, or
cross-timezone behavior, ask how already-created time windows behave when context changes.
Clarify whether they stay anchored, move automatically, or require explicit consent before
changing.

Ask what the product should do when there is no acceptable valid option, not just when the
best option is unclear.

Before stopping, check whether the interview has covered the hard decisions across:
core transformation, source of truth, lifecycle states, identity/permissions, consent,
privacy, failure/retry behavior, operational timing, user-facing explanations, and major
tradeoffs. If an area is still only implied, ask a targeted follow-up.

Continue interviewing until the design is complete, then write the spec to the file.

When writing the spec, be concise and decision-dense. Organize around decided invariants,
states, permissions, flows, and edge cases. Merge overlapping sections, avoid implementation
laundry lists, preserve every surfaced decision and major non-goal, and put only genuinely
undecided thresholds, providers, policy values, or durations in Open Questions.
