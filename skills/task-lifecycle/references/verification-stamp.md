# The verification stamp

Every commit says how it was verified, in one git trailer, so anyone can ask the history which changes
were proven and which were not. `none` is a value, never a missing line.

```
Fix refund rounding in calculateRefund()

Verified: checks, /code-review, codex, /prove-app
```

```
Update README typo

Verified: none
```

## What goes on the line

What ran **and passed**, comma separated: `checks` (the local checks CI runs, all green), each reviewer
that ran with no `Important` finding left open (a `Nit` or a filed `Pre-existing` is fine) (`/code-review`, `codex`), and the verify step when every flow
passed (`/prove-<app>`, or `verify` for the three-agent path). Something that ran and did not pass is
left off, and the PR says why. Nothing ran or passed: `Verified: none`. Never round up.

- **A builder commit:** `Verified: checks` if it ran them, else `Verified: none`.
- **The squash commit on the default branch:** the final line, written by you. A squash merge keeps only
  the message you give it, so pass it: `gh pr merge <n> --squash --body-file merge-commit.md`, where the
  file is two or three lines on what changed, a blank line, then the `Verified:` line.

## Asking the history

```bash
git log --format='%h %s  [%(trailers:key=Verified,valueonly)]' origin/main
git log --format='%h %s %(trailers:key=Verified,valueonly)' origin/main | grep ' none$'
```
