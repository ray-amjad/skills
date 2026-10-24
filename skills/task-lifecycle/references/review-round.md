# Review → fix

Review `git diff origin/$BASE...HEAD`, where `BASE` is the PR's own base branch, not `main` (on a stacked PR, `main` pulls the branch below into scope). Start both built-in reviewers at once: Claude's `/code-review` and Codex's `codex review`. If one is unavailable, say so and carry on with the other; never drop it silently.

- **Fix** what a reviewer marks confirmed or must-fix (`[P1]`): send it to the builder.
- **Carry** the maybes (plausible, `[P2]`) to the final report. Don't send the builder after a maybe.
- **A finding that asks for new code must name the path into that state** (a click, a route, an API call). Without one it is carried, not fixed; otherwise the builder writes a branch no user enters and verify can never reach it.
- **When reviewers contradict,** don't pick a side. Simply tell the builder both and tell it to decide as it has the relevant context.
- **Findings with one root cause get one design,** not N patches.
- **The defect is proven; the suggested fix is a guess.** Reviewers are known for being less good at prescribing fixes. The builder may fix it another way.

The builder commits and pushes after each group of fixes. Post the findings to the PR so a resumed run can see them.

Two rounds at most; stop early when both come back clean.
