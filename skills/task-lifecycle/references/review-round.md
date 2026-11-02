# The review → fix loop

Read this when the PR is open (step 4), or when you run the **already-built** mode in `SKILL.md`.
Bring the PR number, `$BASE`, the branch, and the repo path.

## Round budget

A normal task-lifecycle run gets **at most two complete rounds**. A round that returns `CONFIRMED` or
`[P1]` findings completes only after a fresh fixer resolves every finding it can, commits the fixes and
pushes them to the PR branch. Record a finding the fixer cannot resolve as unresolved, and report it
at the end. Stop early when a review comes back clean.

Go directly to verification after the round 2 fixes. **Never run a third broad or full-diff review in
a normal run, including a review of the round 2 fixes.** Report unresolved findings in the final
message.

The **already-built** mode has no build to pay for, so it may run up to three rounds. The third round
is optional: never repeat an unchanged diff only to spend the available round.

## Review (independent reviewers, in parallel, every round)

Both reviewers read the **same diff**, `git diff origin/$BASE...HEAD`, where
`BASE=$(gh pr view <n> --json baseRefName -q .baseRefName)`. A blocking finding from either one must
be fixed. Start both in one message, so they run at the same time.

- **Reviewer Claude:** a fresh Claude session running a code review of the diff (for example
  `claude -p "/code-review high"` from the repo). Ask it to mark each finding `CONFIRMED` or
  `PLAUSIBLE`.
- **Reviewer Codex:** a fresh `codex exec` with its own review prompt: review the diff for real
  defects, mark each `[P1]` (must fix) or `[P2]` (worth a look), or answer `CLEAN`. Do not give Codex
  the Claude prompt.

If a provider is unavailable, tell the user and continue with the other one. A missing reviewer is a
stated degradation, never a silent drop.

### Size the panel to the diff

**The default is both.** Run Reviewer Claude alone only when the diff obeys EVERY rule:

- fewer than about 30 changed lines;
- no new logic: no new branch, loop or state, and no changed control flow;
- no changed contract that other callers depend on;
- nothing in authentication, access control, money, data migrations, concurrency or secrets.

Any doubt means both. When you report the round, say which panel you ran and why. Spend what you save
on one more verify flow, because a diff this small fails at runtime or not at all. An explicit request
for a thorough review ("review this properly") always gets both.

### Merge the findings

- **Fix now:** a `CONFIRMED` (Claude) or `[P1]` (Codex) finding.
- **Carry, do not fix:** `PLAUSIBLE`, `[P2]`. Report these once, in step 6. Do not send a fixer after
  a maybe.
- **A finding that asks for NEW code must name the path to the state it handles.** That is a click, a
  route, an API call, or a guard that exists in the repo. With no concrete path, the finding is
  **carried soft, not fixed**. Why: otherwise the fixer writes a branch no user enters, and verify can
  never reach it. One grep or one question to the reviewer usually settles it.
- **The two reviewers contradict each other:** do not pick a side. State what each is protecting, find
  the axis on which both hold, and brief the fixer on that shape. Why: a fixer that satisfies one
  reviewer brings back the other's finding in the next round.

A defect that both reviewers flag is the higher-confidence one. Post the merged set to the PR, ending
with a stage marker, and tell the user the count:

```bash
printf '\n<!-- task-lifecycle-round:1 stage:reviewed -->\n' >> findings.md
gh pr comment <n> --body "$(cat findings.md)"
```

If every reviewer you ran comes back clean, capture the fetched remote head. Then post
`<!-- task-lifecycle-round:1 stage:complete head:<full-sha> -->` and go straight to verify.

## Fix (a new fresh subagent, every round)

Brief a **new** subagent with only the findings and the repo path. It fixes exactly those findings,
then commits and pushes to the same PR. Tell it:

- **Findings with one root cause get one design, not N patches.** Why: a locally correct patch can
  break a property the code holds somewhere else.
- **The defect is proven, but the suggested remedy is a guess.** Measure a remedy at production scale
  before you adopt it. You may reject a remedy that you measure as worse, but you must still fix the
  defect and say what you did instead. Precedent in sibling code shows that a technique exists, not
  that it fits.
- **Commit and push after each group of findings.** Why: a run can die inside a fix round, and small
  commits make that round resumable.
- **Append its calls to `.git/task-lifecycle/implementation-notes.md`.** Create the file if it is
  missing (the already-built mode has no builder). Then refresh the PR body
  (`gh pr edit <n> --body-file …`), but only on a PR this run opened. A human's PR keeps its author's
  body.

After the fixer is done, fetch the branch. Confirm that the fixer's final full SHA is an ancestor of
the remote head. Only then post `<!-- task-lifecycle-round:1 stage:complete head:<full-sha> -->`, with
the unresolved count in the visible text. Never post the marker before the push and the ancestry check.
A `stage:reviewed` marker with no valid `stage:complete` marker means the run died inside that
round's fixer. Resume the fixer from the posted findings.

In round 2, review the updated diff again. Keep the fix commit SHA beside the outputs, because fix code
is the least-reviewed code in the diff. Carry forward what you already deferred, so the fixer never
gets the same soft finding twice.
