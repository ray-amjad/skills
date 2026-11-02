# Homework

Finish this before asking question 1.

## Ground truth

- Start with the brief: `$0` and every file it references, or the user's request if there is no `$0`. An old spec is not evidence of current behavior.
- Trace every call path, sibling implementation, and reader and writer of the affected state.
- A claim about existing behavior is a probe, not a reading. "Still passes", "already tested", "runs as user X" and "is invoiced" all mean: run it, query it, or call it. Stale or unprobed facts were the largest source of bugs after merge.
- Read the project's invariants list (the architecture note, or wherever its invariants live) and its ADRs. List the invariant IDs this change touches and any ADR that already settles a question, so the spec cites them instead of re-deciding.
- Find the verification environment: which services, staging, simulators, test accounts and helpers already exist and actually run (probe them). Record what each claim could be checked on. Ask the user only for what the environment cannot tell you. A missing environment becomes an interview question: which check needs it, whether to set it up first, and how (recommend an approach). Setting it up becomes the spec's first task. Never swap in a weaker check.
- Find the root cause, not just the symptom.
- Never build a question on an unverified premise; if a probe changes the premise, say so and ask the corrected question.

## Evidence

- **Record every material fact with:** its source (command, file:line, probe or URL), the date, its qualifiers (version, plan, environment), and the narrowly quoted result.
- **For counts or exhaustive lists:** paste the raw command output.
- **When a check is incomplete:** write "I could not verify this" and its consequence. A failed search never eliminates an option.
