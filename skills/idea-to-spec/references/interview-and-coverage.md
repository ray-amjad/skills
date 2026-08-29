# Interview and coverage

## Build the coverage map

Before question 1, add every relevant area below to the session record. Each area must end with answered decisions or an explicit user-confirmed non-goal; silence is not scope.

- Data model, identity, ownership, lifecycle states, source of truth, and the winner when stores disagree
- Every write path, concurrency boundary, and race
- Authentication and the full exposure surface, including non-production deployments
- Authorization, privacy, consent, and changes to who can read what
- Display and rendering: clocks, timezones, freshness, labels, and missing-name states
- Guardrails, caps, quotas, and refusal behavior
- Execution budget and the process in which each flow runs
- Triggers and termination: what initiates each flow (user action, schedule, event, agent), its named terminal states, and the stopping rule that ends retries and spending
- Migration, cutover, backwards compatibility, and changes to existing behavior
- Failure, retry, idempotency, observability, and alert-channel failure, including how manual triggers are distinguished, audited, and charged against the same guardrails
- Core value transformation and who may override or dispute it
- Coverage boundaries and behavior when there is no acceptable valid result
- Replacement parity for deleted, bypassed, or substituted components, including the fate and verified viability of any replacement scheduler or execution service
- Verifiers: how each goal, invariant, and changed behavior will be proven once implemented, where each check runs, and whether the needed verification environment exists or must be built
- Non-goals

For every new datastore or service, list every existing path that gains a synchronous read or write. Putting a dependency on an existing critical path requires a user decision.

## Ask one decision per turn

Ask the highest-risk unresolved decision—the one constraining the most downstream choices. Each question must:

- contain exactly one decision and no hidden riders;
- offer 2–3 concrete, mutually distinct options;
- mark one option **(Recommended)** and explain its tradeoff;
- propose a concrete value when asking about a threshold, duration, or quantity;
- avoid asking facts or reconfirming facts already present in the brief.

Use the available structured question tool when possible. The only allowed batched messages are the dedicated mutating-surface checklist and the final playback, whose lines must be individually confirmable or vetoable.

If an answer is not falsifiable, re-ask more sharply. If the user avoids a never-default decision twice, explain that the spec cannot proceed without it.

Never-default decisions include authentication/session behavior, credential custody, untrusted-input surfaces, changes to read access, destructive operations, and anything that can overwrite the sole copy of user-authored content.

## Follow topology changes

When an answer kills or reverses a component, record what it kills, creates, and orphans. Rebuild the coverage map and pending questions against the new topology. When answers contradict, name the contradiction and ask the user to resolve it.

## Required product decisions

Ensure the interview resolves:

- the core transformation: what is combined, ranked, inferred, hidden, recommended, automated, or handed off; what correctness means; who can override it; and what evidence remains after disagreement;
- technical operations: state location, execution timing, retries, stale data, sync conflicts, failed automation, and persistently failing work;
- the coverage boundary: unusual inputs, sessions, devices, timezones, content types, user states, and external systems where the logic stops;
- replacement parity: isolation, retries, dashboards, timeout budgets, limits, observability, and failure surfaces supplied implicitly by what is being replaced;
- the verifiers: brainstorm with the user what verification could exist, then decide for each goal, invariant, and changed behavior the check that proves it after implementation, where it lives, and its observable pass signal. Kinds: automated test, schema or type constraint, CI gate, executable probe, browser/E2E run against a test account, an agent-runnable environment (simulator, database branch, service shim, sandbox or dummy account), or human judgment. Prefer checks the implementing agent can run itself and watch fail. An undecided verifier is an unresolved decision; a human-judgment verifier on a load-bearing invariant is an explicit confirmed decision;
- verification infrastructure: whether each chosen verifier's environment already exists (if not, recommend setting one up as separate work and record the best verifier that runs today), and whether verification ends at implementation or extends into post-deploy monitoring with its own stopping rule;
- behavior when no acceptable valid option exists.

For schedules, deadlines, recurring windows, or cross-timezone behavior, ask whether already-created windows remain anchored, move automatically, or move only with explicit consent when context changes.
