# Interview

## Coverage map

Before question 1, list the areas the change touches: data, access, behavior, runtime, change, entrypoints, proof, non-goals. Each ends in a decision or a confirmed non-goal. Silence is not scope. A new synchronous dependency on an existing critical path needs a decision from the user.

## Asking

- Ask the highest-risk open decision first.
- One decision per turn, with 2 to 3 distinct options, one marked **(Recommended)** with its tradeoff.
- For a quantity, propose a concrete value.
- Never ask a fact, and never re-ask something the brief already settles.
- Use the structured question tool when it's available.
- The only batched messages allowed are the entrypoint checklist and the playback.
- If an answer can't be falsified, re-ask it more sharply. If the user dodges an always-ask decision (the list in `SKILL.md` Rules) twice, say that the spec can't proceed without it.
- When answers contradict each other, name the contradiction and ask the user to resolve it. When an answer kills, creates or orphans an area, rebuild the coverage map.

## Entrypoints

For each entrypoint the change adds or touches (route, command, webhook, event, job), settle what it refuses, its edge cases (equal to the limit, empty versus error), and one owner for each irreversible effect (money, access, deletion, messages). Every transport answers the same. For an entrypoint that changes data, send one checklist the user confirms line by line: session and revocation, CSRF, brute force, non-prod exposure.

## Lasting or local

When a new invariant or a notable decision comes up, ask whether it holds only for this change or permanently. Permanent ones go in the spec's Promote on merge block: invariants to the project's invariants list with an ID, decisions to an ADR.

## Smallest product

On product shape, recommend the smallest version that meets the goals, and let the user extend it. Over-decided shape was often reversed within a day. Spend the interview's depth on non-goals, invariants, boundaries, and when to stop and ask.

Before closing, list the choices you think are the building agent's to make (naming, layout, test framework, scheduling mechanism) and put them in the playback as Left to the agent.
