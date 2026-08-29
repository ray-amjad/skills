# Consistency and playback

Complete all applicable artifacts and checks before the playback. Paste the actual work—not a claim that it passed—into the session record.

## Conditional inventories

For each inventory whose trigger is absent, record one line saying why it was skipped.

### Deletion inventory

When anything is deleted, bypassed, or routed around, list every affected file, service, and path; every env var it reads; every cap, floor, quota, refusal, metadata key, event, and marker it writes; and every consumer of those outputs with file:line. Mark each item kept, retired, or rescoped. Retiring behavior requires an explicit user decision.

### Meaning inventory

When an existing name survives but points to something different, quote today's definition, state the proposed definition, and list every reader of the old meaning with file:line. A changed referent is an explicit decision, never "existing behavior."

### Cutover-overlap check

For every migration or de facto migration, identify the old-and-new overlap window and what prevents duplicate work, then the neither-live window and what prevents missed work. Confirm ordering and rollback behavior as decisions.

### Mutating-surface checklist

For authenticated or mutating surfaces, send one dedicated checklist before playback. Each line has a recommended choice and can be vetoed independently:

- session mechanism and cookie attributes;
- session lifetime and revocation;
- brute-force protections;
- CSRF protection and accepted HTTP methods for mutation;
- behavior and exposure on non-production deployments.

## Verb × actor matrix

Create one row per verb found in the brief, mockups, current product, tooling, and proposed design, including verbs being removed. Create one column per human surface, machine caller, and internal path. For each allowed actor × verb cell, state:

- required identity/capability;
- ownership/identity columns populated;
- effects on children, history, schedules, and dependent records;
- hard/soft deletion and what surviving history references.

Every mockup control appears by name in the matrix or in Non-goals. Unresolved cells return to the interview.

## Trust-boundary sweep

For every datastore or service introduced or newly connected, list each process holding its credential. If a credential-bearing process handles untrusted input, make that placement an explicit decision.

## Six consistency checks

1. **Required and unique values:** For every required/unique column, show its source at creation, migration/backfill, and every copy/duplicate path, for every writing actor.
2. **Critical-path dependencies:** For every new dependency, name its failure detector and show that the detector does not depend on the failed component.
3. **Sole copies:** For every field becoming the sole copy, name protection from both deletion and overwrite.
4. **Existing-file constraints:** For every existing file changed by the proposal, read it and show how the design respects constraints documented there.
5. **Rules executed:** Run each algorithm against the user's example, one live case, and the boundary/failure case the rule exists to handle. Include creation from an empty/NULL state and every lifecycle transition where relevant. Show arithmetic for schedules, dedupe keys, cadence, caps, and similar rules, and confirm stored types can represent the promised distinction.
6. **Runtime feasibility:** For every loop/batch/fan-out, calculate items × round trips × realistic latency and compare it with the measured process budget. An unbounded batch under a bounded runtime is an unresolved decision.

Any failure becomes another interview decision or, if low-stakes and eligible, a numbered default-to-veto. It never becomes a silent assumption or an unasked Open Question.

## Playback gate

When answers stop changing the topology, send a written playback containing:

- every decision and its reasoning;
- the final door set and dangerous-effect chokepoints;
- compatibility posture, migration/cutover, permissions, and ownership;
- every non-goal;
- skipped conditional inventories and reasons;
- a short numbered defaults-to-veto list for low-stakes residue only.

Paste the exact sent text into the session record. Do not summarize it there. Wait for confirmation. If the user changes or vetoes a line, paste the exact amended playback as a new record entry—never a summary—and re-play the affected picture until confirmed. Any later line citation must point to exact sent text. Only then may spec writing begin.
