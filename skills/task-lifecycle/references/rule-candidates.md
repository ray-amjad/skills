# Misses become rules

When a defect gets past review, teach the reviewers instead of adding another one. This page turns each
miss into a proposed `REVIEW.md` rule (see `review-round.md`) and lands it once it has happened twice.

## What counts as a miss

A defect the reviewers read and passed, then caught by something later: a verify flow that
`ran_wrong`, red CI on a logic defect (not a flaky job), a broken live check after merge, a revert, or
a defect the user pointed out.

## Is it a review rule?

Only if a reviewer could have seen it in the diff alone. Write it as a trigger plus a check: "when a
change touches X, check Y". If it takes the running app to see, it is a verify rule instead: put it in
the repo's verification skill or notes.

## The ledger: one GitHub issue per pattern

```bash
gh label create review-rule --description "Proposed REVIEW.md rule" --force
gh issue list --label review-rule --state open --search "<two or three words of the pattern>"
```

- **No match: open an issue.** The rule in one line as the title; the target file, the rule text and
  the PR with the commit that fixed the miss in the body. The target is the `REVIEW.md` in the nearest
  folder above the defect that the pattern belongs to, or the root file when it holds across the repo
  (never a test, fixture or vendored folder).
- **A match: second hit.** Comment the PR on the issue, then open the rule as its own PR off the default
  branch, editing only that `REVIEW.md`, and ask the user to merge it. It takes effect once merged,
  because rules are always read from the default branch. Never add the rule to the PR that had the miss.

A finding the builder rejected with a reason, raised again on a later PR, is a candidate "Do not
report" line. When you open a rule PR, prune the same file: a rule whose path or API is gone is removed
in that PR.
