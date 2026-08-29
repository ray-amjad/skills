# Homework and verification

Complete this phase before asking the first decision question.

## Establish ground truth

Read the relevant code, documentation, configuration, research, migrations, tests, and deployment files. Trace actual call paths; do not infer behavior from names. Search for all sibling implementations and all writers/readers of affected state.

When the interview later opens (step 4), start its first message with at most six bullets stating gaps between the brief's mental model and verified reality. State each as a fact with evidence; do not ask the user to confirm it.

## Separate facts from decisions

- **Facts** are already determined by the environment: current behavior, versions, schemas, platform support, plan limits, call sites, and deployment configuration. Discover them yourself.
- **Decisions** select tradeoffs, scope, ownership, risk, compatibility, policy, and what done means. Ask the user.

Never build a decision question on an unverified premise. If the user's answer rejects an option because of a factual claim, verify the claim before pushing back. When verification changes the premise, say so and ask the corrected decision.

## Evidence standard

Record every material factual claim with:

- the exact command, file and line, live probe, or primary-source URL;
- the date checked;
- relevant qualifiers such as version, language, framework variant, deployment, account/plan tier, and environment; 
- the observed text or result, quoted narrowly enough to preserve its qualifiers.

For issues and pull requests, include current state and last-updated date. For current platform behavior, use current official documentation or a live probe; historical bug reports are not current behavior. If sources disagree, prefer a current measurement, then recompute anything derived from the losing source.

If a check is incomplete, record **"I could not verify this"** and its consequence. A failed search never eliminates an option. Keep the option and price the decision under both possible factual outcomes unless stronger evidence resolves it.

For any count or supposedly exhaustive list, paste the command and its raw output into the session record. Do not replace it with a hand-counted or paraphrased list.

## Runtime envelope

For every process that will execute a proposed flow, record from actual configuration or current platform evidence:

- timeout or `maxDuration`;
- memory cap;
- request and response size limits;
- concurrency limits;
- per-second and per-window limits for APIs called in loops;
- queue, cron, worker, or transaction limits relevant to retries and fan-out.

Record file:line for repository configuration. A limit verified for one process does not cover any other process — verify each separately. Do not design a loop, batch, or fan-out until its process envelope is known.

## Compatibility posture

Infer compatibility only when evidence and the brief make it unambiguous:

- Explicit permission for breaking changes and no real downstream users permits them.
- Production users, published APIs, downstream consumers, migration safety, or an explicit compatibility requirement forbids them.

Otherwise ask one decision question. Record the result for the playback and the final **Backwards compatibility** section.

## Urgent out-of-scope findings

Verify an apparent leak, vulnerability, or broken invariant to the same standard as in-scope facts: trace the real path and quote the real code. Report it once in a clearly flagged paragraph, state whether it belongs in this work, and return to the interview.
