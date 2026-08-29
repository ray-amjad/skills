# Spec output and final verification

Use `../templates/technical-spec.md` as the structure, adapting sections to the actual change. Omit irrelevant mechanism detail, but never omit a decided invariant, door, permission, state, failure behavior, compatibility change, or non-goal.

## Where the spec goes

**Default: a GitHub issue in the current repository.** A spec is a work item other people and agents pick up, so it belongs in the issue tracker, not in an untracked local file that only this machine can see.

Write the spec to a scratch file first, then publish it and delete the scratch copy:

```bash
gh issue create --title 'Spec: <topic>' --body-file <scratch>.md
```

Title the issue `Spec: <topic>` so specs are greppable in the issue list. Report the issue URL as the deliverable. Add `--label`, `--assignee`, or `--milestone` only when the user asks; do not invent labels that may not exist in the repository, since `gh issue create` fails outright on an unknown label.

Before publishing, confirm the repository with `gh repo view --json nameWithOwner`. If the working directory is not a GitHub repository, or `gh` is not authenticated, say so and ask where the spec should go rather than silently falling back to a local file.

Updating an existing spec issue is `gh issue edit <number> --body-file <scratch>.md`. Never open a second issue for a revision of the same spec.

Follow an explicit user destination instead. When the user asks for a file, use `specs/YYYY-MM-DD-topic.md` with the current date and a kebab-case topic.

## Writing rules

- Be concise and decision-dense. Write requirements and guarantees, not an implementation laundry list.
- Include only user-decided or playback-confirmed policy. A value the user explicitly deferred may appear in Open Questions; an unasked question sends you back to the interview.
- Give every invariant one enforcement/detection line: schema constraint, unavoidable chokepoint, authorization boundary, runtime guard, or named test — marked machine-runnable or human-judgment. A human-judgment-only check on a load-bearing invariant must be a confirmed decision, not a leftover.
- Name each flow's trigger, terminal states, and stopping rule; a flow that cannot say when it stops is an undecided decision.
- Give every non-trivial door its typed contract, one guarantee, named exits, refusals, required capability, side effects, and boundary tests.
- List the door names alone in a stranger-across-time view and mark irreversible effects.
- Describe current state as verified, including leaking or duplicated effect paths.
- Include the selected architecture and at least one rejected alternative when a real choice existed.
- Include the smallest useful diagram when required by the doors reference.
- Include an executable verification plan: exact commands/requests and observable pass/fail results at system boundaries.

## Required sections

- Executive summary
- Context and verified current state
- Goals and non-goals
- Backwards compatibility
- Proposed architecture and door set
- Detailed contracts, data/state model, permissions, and flows
- Failure, retry, observability, execution budget, and stopping rules
- Migration and cutover
- Changes to existing behavior
- Alternatives considered
- Verification plan
- Verified facts
- Open Questions, only when explicitly deferred

## Changes to existing behavior

Diff every existing surface whose billing, auth, routing, permissions, cost, or semantics changes. Include rewired routes, changed fallbacks, renamed meanings, different retry behavior, and replaced tooling even when the external shape remains. If nothing changes, state that in one line.

## Verified facts

For each fact include scope, source/file:line or URL, date checked, configuration and qualifiers, and the observed result. Use **"I could not verify this"** verbatim for any incomplete check and state the consequence.

## Final consistency read

Before presenting the file:

1. Compare every actor × verb granted in prose with the matrix cell by cell.
2. Confirm every route and in-process door agrees on caller, guarantee, refusal, and effect.
3. Confirm ownership and required values have sources under every writing actor.
4. Confirm every invariant names an enforcement or detection point and marks its check machine-runnable or human-judgment.
5. Re-run each worked example, boundary/failure case, and creation/transition case against its stated rule and stored representation.
6. Recheck batch arithmetic against recorded runtime limits.
7. Diff the spec's decisions against the confirmed playback.
8. Confirm every Open Question was actually asked and explicitly deferred.

Report the issue URL (or file path), a concise executive summary, the door names alone, irreversible effect doors, and any explicitly deferred questions.
