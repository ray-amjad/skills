# Draft and critique

Run after homework and before the interview. The point is to spend cheap agent effort before expensive user attention: the critiqued draft's open questions become the interview agenda, so questions arrive pre-filtered and pre-grounded.

## Skip condition

For a small, single bounded change with few decision areas, skip this phase and record one line in the session record saying so and why. A skipped phase is declared, never silent.

## Draft the strawman

Using only recorded homework facts, draft the smallest spec that would let another agent implement the change safely. It must contain: assumptions (each one marked as an assumption), non-goals, acceptance criteria, edge cases, observable outcomes, and open questions. Every policy value in it is marked **(proposed)**. The strawman decides nothing — it exists to be attacked.

## Independent critique

Have a fresh-context agent critique the draft — not a fork, and not yourself: a fork inherits the framing that produced the draft's mistakes. Give it the draft and the verified-facts table, not your reasoning. Instruct it explicitly that its final output must be routed back to you. It hunts, not limited to the following:

- internal contradictions between sections;
- unverified premises stated as facts;
- decisions the draft silently made that belong to the user;
- missing coverage areas and actors;
- arithmetic that cannot fit the recorded runtime envelope.

## Fold the findings in

Each critique finding becomes exactly one of: a homework re-check (factual doubts), a coverage-map area, or an interview question. Paste the draft and the critique verbatim into the session record. Nothing from the strawman reaches the final spec without a user decision or playback confirmation — the draft sharpens questions; it never pre-answers them.
