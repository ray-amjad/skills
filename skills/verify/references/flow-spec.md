# The flow file, the requires line, and the table

Read this when you write a flow file or the hand-over table.

## Why a file per flow

The output of identifying flows is not a run. It is one short file per flow and one table. The file is the handoff: a runner in a fresh context can execute it without the diff, without the spec, and without the builder's transcript. If the file needs the diff to make sense, it is not finished.

## The fields

Use `templates/flow.md`. Frontmatter carries what a script can check. The body carries what a runner reads.

| Field | What goes in it |
|---|---|
| `id` | short, stable, scope plus number, e.g. `INBOX-03` |
| `title` | one sentence a user could act out |
| `tag` | `added`, `touched` or `shared`, which list it came from |
| `surface` | `page`, `route`, `row`, `email`, `message`, `cli`, `file` |
| `reader` | the probe that reads that surface: `playwright`, `curl`, `psql`, `mailpit`, an API name, or `none` |
| `requires` | the capabilities the flow needs from the environment (see below) |
| `touches` | the files or file ranges whose change would make this flow stale |
| Path | where the flow starts |
| User steps | numbered, as a user does them, including the seed calls that set up the state |
| Expected outcome | what the user sees at the end, and what the data says |
| What to verify | the exact check, and the trap that would make a weak check pass |
| Fixtures | the data and actors the flow needs, and where they come from |

Write the expected outcome as something visible at the boundary. "The row exists" is a database claim; "the new title is in the breadcrumb and the tickets row still has id 42" is a flow claim.

Write the trap in "What to verify". Most weak passes come from checking the wrong thing: counting rows instead of checking the row by id, reading a 200 instead of reading the body, watching a page that renders empty for another reason.

## The requires line

The environment **provides** a set of capabilities. Keep that list in one manifest file, and keep the vocabulary small and shared, for example:

```
auth-session       a signed-in session can be injected
org-owner          the seeded actor owns the sandbox organization
postgres-isolated  the run owns its own database
playwright         headless Playwright is installed and smoke checked
seed-api           a seed surface can create the fixtures a flow needs
smtp-catcher       outbound email lands in a local mail catcher
stripe-live        real Stripe behavior is available
```

Each flow **requires** a subset. The rule is one line:

```
runnable  =  requires  is a subset of  provides
```

Anything else is `blocked`, with the missing capabilities named. A flow that requires `stripe-live` against an environment that provides a Stripe shim is blocked, and the table says so before anyone boots a browser.

A surface that no reader can drive is a third state, `not driven`. Blocked means the environment lacks a capability. Not driven means no probe exists for that surface at all (a real IME, a slow network replay, a hardware device). Both are listed. Neither is a skip.

## The table

Five columns. This is what goes back to the thread, the PR, or the user:

| Flow | Tag | Surface | Reader | Status |
|---|---|---|---|---|
| id and title | added, touched, shared | page, route, row, email, message | playwright, curl, psql, mailpit, none | runnable, blocked: missing x, not driven |

The tag is what lets a reader see which list each row came from. Added and touched always run. Shared is listed in full and run by cost tier: an internal tool runs the top few, a customer-facing change runs them all. Write which tier you chose under the table.

The identifier builds this table from the frontmatter of every flow file and the manifest. Every flow file gets a row. No row, no flow.

## Keep the files

Flow files outlive the PR. They are the start of a flow library: the next change to the same surface reuses them, and `touches` is what tells you which ones went stale. Put them in a folder the repo keeps, for example `verification/flows/<scope>/`.
