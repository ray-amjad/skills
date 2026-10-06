---
id: SCOPE-01
title: One sentence a user could act out
tag: added            # added | touched | shared
surface: page         # page | route | row | email | message | cli | file
reader: playwright    # playwright | curl | psql | mailpit | <api name> | none
priority: high
requires:
  - auth-session
  - postgres-isolated
  - playwright
touches:
  - "src/path/to/file.ts:10-40"
discovered_on: YYYY-MM-DD
mutates: true
---

## Spec

### Path

/where/the/flow/starts

### User steps

1. Seed or create the state the flow needs, and say how (seed API, UI, SQL).
2. Do the thing, as a user does it.
3. Read the surface where the result lands.
4. Read the data behind it (psql, the app's read API).

### Expected outcome

The end state the user reaches (layer 1). Write it as something visible at the boundary.

### Expected screens

One line per step, what the UI shows (layer 2). A reference screenshot path if one exists, else the assertion.

### Expected state

The rows or keys that exist afterwards, by id (layer 3). Give the query.

### Expected side effects

Emails, webhooks, enqueued jobs the flow must produce (layer 5), and where to read each one. Write "none" if there are none, so the runner marks the layer skipped instead of guessing.

### What to verify

The exact check. Then the trap: what would make a weak check pass here (row by id, not by count; the body, not the status; the state the flow claims, not a page that renders empty for another reason).

### Fixtures

The actors and data this flow needs, and where each one comes from.
