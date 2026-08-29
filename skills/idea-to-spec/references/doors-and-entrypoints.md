# Doors and entrypoints

Doors are the system's entrypoints: every function, route, command, event, webhook, and RPC method that accepts untrusted intent or performs a meaningful effect. Together they should read as a statement of what the system is for — someone who sees only the door names should understand the system's purpose. Design them as one explicit set.

## Five design principles

1. **Name the domain action, not the mechanism.** `publishInvoice`, not `execute`, `process`, or `runQuery` — the name must be recognizable to someone who knows the domain but not the code.
2. **Compress honestly.** A door's name and signature promise exactly what every exit delivers. Encode cost, partiality, and risk when they matter.
3. **Make refusals real.** Prefer types and structure that make illegal states unrepresentable over checks every caller must remember.
4. **Write for a stranger across time.** Someone should reconstruct the system's purpose from entrypoint names and contracts without reading their bodies.
5. **Keep dangerous doors few and honest.** Funnel each irreversible effect—money, access, deletion, publication, credential minting, external messages—through one named chokepoint.

## Door inventory

Inventory every current and proposed door that accepts untrusted input, performs a side effect, or crosses a trust boundary (a pure internal read helper is trivial and may be omitted). Include all transports that express the same domain action. For every door record:

- domain name and typed signature;
- one-sentence guarantee containing one promise;
- complete named success and failure exits;
- what it refuses and whether the refusal is structural or runtime-only;
- caller identities and required capability.

Additionally, for doors with side effects or a trust transition:

- trust transition, validation, conversion, and error boundary;
- state transitions and side effects;
- idempotency/concurrency behavior;
- whether it guards an irreversible effect and every alternate path to that effect;
- enforcement/detection points and boundary-level tests.

## Ten-question rubric

Run the ten questions on each drafted door. Then reverse direction: for each obligation and irreversible effect in the design, name the door that owns it — an unowned effect means a door is missing. Stop evaluating a door at the first question you cannot answer cleanly; record that gap as an interview question and move to the next door.

1. Is the name a domain action rather than a mechanism?
2. Can its guarantee be written as one sentence with one promise?
3. Does the name honestly communicate cost, partiality, and irreversibility?
4. Does its type carry the domain's meaningful distinctions?
5. Are every success, refusal, retry, timeout, and partial-failure exit named?
6. Are illegal states impossible to construct where practical?
7. Is the trust transition explicit and singular?
8. Is this the single dominating door for its irreversible effect?
9. Do validation, authorization, conversion, and the error boundary live at the edge?
10. Could a competent stranger reconstruct intent from the door alone?

## Transport parity

An in-process function, REST route, gRPC method, CLI command, and event that express the same domain action are one door across transports. Their names, guarantees, refusals, authorization, idempotency, and error semantics must agree. Use protocol semantics honestly: safe and idempotent HTTP verbs, meaningful status codes, preconditions, and idempotency keys where retries could duplicate effects. Never wrap a real failure in a success response.

## Architecture view

When the change spans three or more components, trust boundaries, or dependent stages, include one Mermaid context/container/flow diagram showing exactly: actors, system boundaries, the validation point where untrusted input becomes trusted intent, stateful components, external dependencies, and irreversible-effect doors — and nothing else.

When a real choice existed, compare at least one plausible alternative door set. Explain why the chosen doors, refusals, and chokepoints serve callers and the domain better — not just why they were easier to build.
