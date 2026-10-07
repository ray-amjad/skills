# Spec output

## Publish

Ask one question: where should the spec go? Recommend **a GitHub issue in the current repo** (check `gh repo view --json nameWithOwner` first), with a local file or a user-named destination as the alternatives.

- **Issue:** `gh issue create --title 'Spec: <topic>' --body-file <file>`. No labels unless asked. Revise with `gh issue edit`, never a second issue.
- **File:** `specs/YYYY-MM-DD-topic.md`.

## The spec

Four sections, in this order. Add an extra only when the change needs it, and never write "None".

**1. Starting point**
- **Why:** the root cause, not the symptom, and the evidence behind it (report, log line, failing request).
- **Current state:** only the facts that drive a decision, each with its source (file:line, command, URL) and the date checked, including traps documented in the files being touched. Mark an unverified fact **I could not verify this**, with its consequence and the safe behavior meanwhile.
- **First task, before any code:** re-probe the load-bearing facts; if one is false, stop and report. Then set up any environment that Verifies on marks as missing.

**2. Goals and non-goals**
- **Goals:** numbered outcomes someone else could check.
- **Non-goals:** what an eager agent would otherwise do, including behavior left unchanged on purpose and any tempting rejected alternative, one-line reason each. Items the user chose to defer are listed here, marked deferred.

**3. Constraints**
- **Invariants:** a table of invariant, where it is enforced or detected, machine or human. Cite the project's existing invariants by ID ("must still satisfy N-1"); never copy their text. An existing invariant this change breaks is said out loud and updated where it lives.
- **Stop and ask / left to the agent:** when to halt and report, and which choices are explicitly the building agent's.
- **Extras**, only when the change needs them:
  - **Compatibility** (existing callers, users, or data): the posture, plus a Surface / Before / After table.
  - **Permissions** (who can read or write changes): the verb × actor table.
  - **Entrypoints** (new or changed): each one's refusals, edge cases as worked examples, and the single owner of each irreversible effect.
  - **Ordering and cutover** (a sequence matters): the order, what breaks if it is compressed, and rollback.
  - **Stopping rules** (anything that retries, loops, or spends): trigger, terminal states, and caps, each checked against the real timeout, rate limit, or memory limit it must fit, with its source.
  - **Promote on merge** (a lasting rule or decision): new invariants for the project's invariants list with an ID, and decisions as ADRs, in the same PR.

**4. Proof**
- **Verifies on:** the services and environments the checks run against, and any environment or helper to set up first.
- A table of #, proves, surface, check, where it runs, pass signal.
- Every check must pass to merge. Pass means every step shows its stated result; anything else fails the step. Its fixture can actually be seeded, and it never silently skips. Add an **After deploy** list only if the user decided on one, including when it stops.

## Writing rules

- Keep it short. Split a big one into child specs, each with its own proof. Never cut a decided invariant, non-goal, permission or refusal to fit.
- Write what and why, not how. No SQL, joins, file-by-file steps, or hard-coded numbers or slugs unless a probe backs them.

After publishing, run Done's four checks on the published spec and diff it against the confirmed playback; fix anything with `gh issue edit` (or the file). Then report the URL or path, the entrypoints, the irreversible effects, and anything deferred.
