# Spec output and final verification

Use `../templates/technical-spec.md` as the structure. Every template section is required; adapt its depth, never its presence. Omit irrelevant mechanism detail, but never omit a decided invariant, door, permission, state, failure behavior, compatibility change, or non-goal.

## Where the spec goes

Ask the destination as one decision: **a GitHub issue in the current repository (Recommended)** — a spec is a work item other people and agents pick up, so it belongs in the tracker — or a local file, or a destination the user names. Check `gh repo view --json nameWithOwner` before asking; if the directory is not a GitHub repository or `gh` is unauthenticated, say so and recommend a file instead.

For an issue: write the spec to a scratch file, publish, then delete the scratch copy.

```bash
gh issue create --title 'Spec: <topic>' --body-file <scratch>.md
```

Title it `Spec: <topic>` so specs are greppable. Report the issue URL as the deliverable. Add `--label`, `--assignee`, or `--milestone` only when the user asks — `gh issue create` fails outright on an unknown label. Revisions use `gh issue edit <number> --body-file <scratch>.md`; never open a second issue for the same spec.

For a file: `specs/YYYY-MM-DD-topic.md` with the current date and a kebab-case topic.

## Writing rules

- Be concise and decision-dense. Write requirements and guarantees, not an implementation laundry list.
- Include only user-decided or playback-confirmed policy. A value the user explicitly deferred may appear in Open Questions; an unasked question sends you back to the interview.
- Give every invariant one enforcement/detection line: schema constraint, unavoidable chokepoint, authorization boundary, runtime guard, or named test — marked machine-runnable or human-judgment. A human-judgment-only check on a load-bearing invariant must be a confirmed decision, not a leftover.
- List the door names alone — no signatures or bodies — and mark which guard irreversible effects. The bare list must read as a description of what the system does.
- Describe current state as verified, including leaking or duplicated effect paths.
- Include the smallest useful diagram when required by the doors reference.
- Include an executable verification plan: exact commands/requests and observable pass/fail results at system boundaries. Every entry is a decided or playback-confirmed verifier naming what it proves and the environment it runs in — never invent a verification approach at write time. Where an environment is missing, record the separate-work setup recommendation rather than folding the build into this spec.

## Changes to existing behavior

Diff every existing surface whose billing, auth, routing, permissions, cost, or semantics changes. Include rewired routes, changed fallbacks, renamed meanings, different retry behavior, and replaced tooling even when the external shape remains. If nothing changes, state that in one line.

## Verified facts

Fill the template's table from the session record. Use **"I could not verify this"** verbatim for any incomplete check and state the consequence.

## Final consistency read

These checks re-run earlier work against the published text: writing is a fresh generative act that introduces drift, so you are now checking the document, not the design. Before presenting the spec:

1. Compare every actor × verb granted in prose with the matrix cell by cell.
2. Confirm every route and in-process door agrees on caller, guarantee, refusal, and effect.
3. Diff ownership and required-value sources in the spec against the session record's shown work (consistency check 1).
4. Confirm every invariant names an enforcement or detection point and marks its check machine-runnable or human-judgment.
5. Diff each worked example, boundary/failure case, and creation/transition case against the session record's shown work (consistency check 5); re-execute only rules amended after the consistency pass (a decision-log entry postdating it).
6. Diff batch arithmetic against the session record's runtime-feasibility work (consistency check 6); recompute only where limits or volumes changed afterward.
7. Diff the spec's decisions against the confirmed playback.
8. Confirm every Open Question was actually asked and explicitly deferred.
9. Confirm every goal, invariant, and changed behavior maps to a Verification plan entry whose verifier was decided in the interview; playback confirmation restates interview decisions, it does not originate verifiers.

Report the issue URL (or file path), a concise executive summary, the door names alone, irreversible effect doors, and any explicitly deferred questions.
