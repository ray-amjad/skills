# The four asks

Each step of Phase 1 is one message to the agent. The wording matters, because two of these lean on terms the model already knows and one leans on a question it would not think to ask itself. Paste them. Do not paraphrase.

Make every ask from a fresh context that has not seen the build. The builder's transcript carries the builder's understanding, and that understanding is what is under test.

## Ask 1: confirm the spec (only when a spec exists)

```
Here is the spec and here is the PR.

Check that every verifier in the spec's Verification plan still names a flow you can run
against this PR. For each one, write the flow as one sentence a user could act out, and
name the surface it lands on (page, route, row, email, message).

Then list every surface the code changed that the plan never mentions.

Two lists back: "in the plan" and "changed but not in the plan". Do not run anything yet.
```

Why this first: the plan was written by the person who knew what the feature was for, at the moment they knew it best. This ask is a confirmation, not a search.

## Ask 2: the end-to-end tests

```
List the end-to-end verification tests that would be done for this feature.
```

That is the whole prompt, and the words end-to-end are the part that does the work. Ask for a test matrix, or for tests without a qualifier, and the model pads the list with unit tests and integration tests. Those are cheap rows that prove nothing about a flow, and you spend the next step cutting them. End-to-end keeps the list on the user's side. Expect back: what changed, which pages, routes, rows and messages it reaches, which inputs and states each has, and the paths a user would walk through them.

Expect it to over-enumerate. Keep the list. Then tag each row `added` (something a user can newly do) or `touched` (an existing flow whose code moved).

If it comes back with "nothing here has a runnable surface" (docs, CI, types, a pure refactor), that is a valid answer and the verification result. Say it. Do not stage a recording.

## Ask 3: who else reads what the diff wrote

```
For every column, component, route, helper or piece of state this diff writes to, list
every flow that reads it, including flows whose files are not in the diff.
Name the shared thing, then the flow that reads it, then the surface where a user would
see it. Tag each one "shared".
```

Why this exists: the diff cannot write this list on its own. The bug a change introduces usually lands in a flow the diff never touched, because two flows share one column or one component. In a rename, the breadcrumb and the tab title never changed. They read the column the rename wrote. Ask who else reads the same bytes.

## Ask 4: pick the boundary

```
For each flow, name the outermost reader that still costs little: a recorded browser for a
page, curl for a route, psql for a row, a mail catcher for an email, the receiving API for a
message. If the change adds or changes a screen, the reader is the screen.
Mark any surface that has no reader available as "not driven" and say which probe is missing.
```

If component tests or API tests still appear in the list, they are cheap rows. They locate a fail. They do not prove the flow. The row that proves the flow is the one at the boundary the user experiences, and that is the row you keep.

## After the asks

Reconcile the spec list and the diff list. A flow in the spec that the diff cannot see is an intent the code missed: report it now. A flow the diff touched that the spec never named stays as `touched`. Then write one flow file per flow (`templates/flow.md`) and produce the table (`references/flow-spec.md`).
