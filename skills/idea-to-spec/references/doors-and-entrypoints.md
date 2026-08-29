# Doors and entrypoints

A system's entrypoints are its theory of purpose. Mechanism explains how; doors explain what and why. Treat functions, routes, commands, events, webhooks, and RPC methods that accept untrusted intent or perform meaningful effects as one explicit door set.

## Five design principles

1. **Name a joint, not a tool.** Use a domain action recognizable outside the implementation, not `execute`, `process`, `runQuery`, or another mechanism name.
2. **Compress honestly.** A door's name and signature promise exactly what every exit delivers. Encode cost, partiality, and risk when they matter.
3. **Make refusals real.** Prefer types and structure that make illegal states unrepresentable over checks every caller must remember.
4. **Write for a stranger across time.** Someone should reconstruct the system's purpose from entrypoint names and contracts without reading their bodies.
5. **Keep dangerous doors few and honest.** Funnel each irreversible effect—money, access, deletion, publication, credential minting, external messages—through one named chokepoint.

## Door inventory

Inventory every non-trivial current and proposed door. Include all transports that express the same joint. For each door record:

- domain name and typed signature;
- one-sentence guarantee containing one promise;
- complete named success and failure exits;
- what it refuses and whether the refusal is structural or runtime-only;
- caller identities and required capability;
- trust transition, validation, conversion, and error boundary;
- state transitions and side effects;
- idempotency/concurrency behavior;
- whether it guards an irreversible effect and every alternate path to that effect;
- enforcement/detection points and boundary-level tests.

## Ten-question rubric

Run this forward on each drafted door and backward from each obligation/effect to find missing doors. Stop at the first question that cannot be answered cleanly; that gap returns to the interview.

1. Is the name a domain joint rather than a mechanism?
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

An in-process function, REST route, gRPC method, CLI command, and event that express the same domain joint are one door across transports. Their names, guarantees, refusals, authorization, idempotency, and error semantics must agree. Use protocol semantics honestly: safe and idempotent HTTP verbs, meaningful status codes, preconditions, and idempotency keys where retries could duplicate effects. Never wrap a real failure in a success response.

## Architecture view

When the change spans three or more components, trust boundaries, or dependent stages, include the smallest useful Mermaid context/container/flow diagram. Show actors, system boundaries, the airlock where untrusted input becomes trusted intent, stateful components, external dependencies, and irreversible-effect doors.

Compare at least one plausible alternative door set. Explain why the selected joints, refusals, and chokepoints better express the domain rather than merely why its internal mechanism is convenient.