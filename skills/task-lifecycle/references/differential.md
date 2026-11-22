# Differential and property flows

Two checks for code a click-through can't cover well. In both, the inputs come from a generator, not
from the agent that wrote the code, so they don't share its blind spots. If the repo has its
own verification skill that already covers these, use it; this page is for repos without one.

## Differential: the old code is the answer key

For a change that must keep behaviour: a refactor, a migration, a library swap, a rewrite, an
optimisation. Run the base and the head on the same inputs and diff what comes out. Any difference
is a defect or a breaking change, unless the brief approved it.

**The brief, written before anything runs** (written after the first diff, it invites explaining a
difference away):

- **The answer key:** the merge-base, checked out beside the head (`git worktree add --detach
  <dir>/base <merge-base>`), with one seeded database (a fresh copy per side when the code writes).
- **What is compared:** a function's return value, an endpoint's response plus the rows it wrote, a
  job's output plus its side effects.
- **Inputs:** the brief's own edge cases, plus generated ones: `fast-check` for JS/TS, Hypothesis for
  Python, proptest for Rust. At least 1,000 cases for a pure function, at least 100 for anything that
  touches the database. Record the seed. Generated or seeded inputs only, never production data.
- **Normalise:** what may differ and doesn't matter (timestamps, generated ids, key order, unordered
  rows, whitespace). Name each one; normalise nothing else.
- **Approved differences:** each intended change, as "for inputs like X, the head returns Y where the
  base returned Z". Empty is the usual case for a refactor.

**Verdict.** No difference beyond the approved list: `passed`. Any other: `ran_wrong`, with the
shrunk counterexample, both outputs side by side, and the seed. An approved difference that never
showed up is reported too: the intended change may not have happened.

**Evidence** is one text file: the command, the seed, the number of inputs, the normalisations, then
each difference or `0 differences in N inputs`. The harness itself is never committed: it only means
something while the base exists to compare against.

## Property: a rule that can't break

For code that must hold a rule over every input: a parser or serialiser, money, a retry, a migration,
a normaliser. The brief states the property in one line, then a generator tries to break it:

- **Round trip:** decode(encode(x)) equals x.
- **Invariant:** something always true ("a balance never goes negative").
- **Idempotent:** doing it twice equals doing it once (a migration, a retried webhook).
- **Equivalent:** the fast version returns what a slow, obviously correct one returns.

No counterexample: `passed`, and the property goes to the builder to commit as a real test, so CI keeps
running it. A counterexample: `ran_wrong`, with the shrunk input and the seed. The checker reruns the
recorded seed once before it gives either verdict.
