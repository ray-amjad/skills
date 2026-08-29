# Interview and coverage

## Build the coverage map

Before question 1, add every area below to the session record as a coverage-map row. Every area gets a one-line disposition; marking one not applicable requires a stated reason. Each applicable area must end in answered decisions or an explicit user-confirmed non-goal — silence is not scope. The map is the required-decisions checklist; there is no second list.

- Data model, identity, ownership, lifecycle states, source of truth, and the winner when stores disagree
- Every write path, concurrency boundary, and race
- Authentication and the full exposure surface, including non-production deployments
- Authorization, privacy, consent, and changes to who can read what
- Display and rendering: clocks, timezones, freshness, labels, and missing-name states
- Guardrails, caps, quotas, and refusal behavior
- Execution budget and the process in which each flow runs; state location, execution timing, stale data, and sync conflicts
- Triggers and termination: what initiates each flow (user action, schedule, event, agent), its named terminal states, and the stopping rule that ends retries and spending; failed automation and persistently failing work
- Migration, cutover, backwards compatibility, and changes to existing behavior
- Failure, retry, idempotency, observability, and alert-channel failure, including how manual triggers are distinguished, audited, and charged against the same guardrails
- Core value transformation: what is combined, ranked, inferred, hidden, recommended, automated, or handed off; what correctness means; who may override or dispute it; and what evidence remains after disagreement
- Coverage boundaries: unusual inputs, sessions, devices, timezones, content types, user states, and external systems where the logic stops — and behavior when no acceptable valid result exists
- Replacement parity for deleted, bypassed, or substituted components: isolation, retries, dashboards, timeout budgets, limits, observability, and failure surfaces supplied implicitly by what is being replaced, including the fate and verified viability of whatever takes over its work
- Verifiers: brainstorm with the user what verification could exist, then decide for each goal, invariant, and changed behavior the check that proves it once implemented, where it runs, and its observable pass signal. Kinds: automated test, schema or type constraint, CI gate, executable probe, browser/E2E run against a test account, an agent-runnable environment (simulator, database branch, service shim, sandbox or dummy account), or human judgment. Prefer checks the implementing agent can run itself and watch fail. If a chosen verifier's environment does not exist, recommend setting it up as separate work and record the best verifier that runs today; also decide whether verification ends at implementation or extends into post-deploy monitoring with its own stopping rule. An undecided verifier is an unresolved decision; a human-judgment verifier on a load-bearing invariant is an explicit confirmed decision
- Non-goals

For every new datastore or service, list every existing path that gains a synchronous read or write, and record that list under the session record's Critical-path couplings. Putting a dependency on an existing critical path requires a user decision.

For schedules, deadlines, recurring windows, or cross-timezone behavior, ask whether already-created windows remain anchored, move automatically, or move only with explicit consent when context changes.

## Ask one decision per turn

Ask the highest-risk unresolved decision—the one constraining the most downstream choices. Each question must:

- contain exactly one decision and no hidden riders;
- offer 2–3 concrete, mutually distinct options;
- mark one option **(Recommended)** and explain its tradeoff;
- propose a concrete value when asking about a threshold, duration, or quantity;
- avoid asking facts or reconfirming facts already present in the brief.

Use the available structured question tool when possible. Log every answered decision in the session record's Decision log, and append default-to-veto candidates to its Defaults-to-veto candidates section as they arise.

The only allowed batched messages are the dedicated mutating-surface checklist — every line of which the user must explicitly confirm or amend, with any unaddressed line re-asked as its own question, never treated as accepted — and the final playback, whose numbered defaults-to-veto lines are the only place in the session where a non-veto counts as acceptance.

If an answer is not falsifiable, re-ask more sharply. If the user avoids a never-default decision twice, explain that the spec cannot proceed without it. Never-default decisions are listed in SKILL.md's non-negotiable rules: authentication and session behavior, credential custody, exposure to untrusted input, changes to read access, destructive operations, and anything that can overwrite a sole copy of data (user-authored or not).

## Follow topology changes

When an answer kills or reverses a component, record what it kills, creates, and orphans. Rebuild the coverage map and pending questions against the new topology. When answers contradict, name the contradiction and ask the user to resolve it.
