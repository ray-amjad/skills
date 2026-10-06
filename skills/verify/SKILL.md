---
name: verify
description: Turn a spec and a PR into the list of user flows to verify, then run each flow for real and leave one evidence file per flow. Use whenever a change is about to ship having only been read, not run; whenever the user asks "does it actually work", "verify this", "what should we test", or "list the end-to-end tests"; and as the verify stage of task-lifecycle. Covers both halves, identifying the flows (added, touched, shared) and driving them at the boundary the user experiences.
---

# Verify

A PR names files. A user never touches a file. A user touches a page, a route, a row in a database, an email, a Slack message. Those are surfaces. This skill is the translation from one to the other, then the run:

```
files changed  ->  surfaces changed  ->  a reader per surface  ->  flows to run  ->  one evidence file per flow
```

Every step is one ask you can make of the agent. The exact wording of each ask is in `references/asks.md`. Use those words, not a paraphrase.

## Two rules that hold the whole skill up

1. **The spec leads, the diff audits.** The diff tells you what changed. It cannot tell you what was meant. A verifier that works from the diff alone passes a half-built feature, because it only checks what is there. So the definition of done comes from the spec, written before the builder started, and the diff is the second pass that catches what the spec forgot.
2. **The verifier never shares the builder's context.** Run this skill in a fresh context: a new session, or a subagent that has not seen the build transcript. Hand it the spec and the PR, never the builder's reasoning. A builder that grades its own work grades its own understanding, and that is the thing under test.

## Five contexts, and what each one never sees

A verification run is not one agent. It is one orchestrator and four fresh contexts, and the separation is the point. Each context gets exactly what its job needs. What it never sees is listed on purpose, because that is where the builder's understanding would leak back in.

| Context | Gets | Never sees | Emits | May never do |
|---|---|---|---|---|
| **Orchestrator**, the session that triggered the skill | the user's ask, the repo, the scripts | evidence as a judge; it reads verdicts, not runs | the flow table, the report, the fix-round question | drive a flow by hand, write a verdict, merge |
| **Identifier**, Phase 1 | the spec, the diff, the capabilities manifest | the build transcript | one flow file per flow, the table | boot or drive anything |
| **Setup**, one per flow | the flow file's Fixtures and requires lines, the environment manifest | the diff, the spec | the app up, the seeded state, a handoff manifest (`templates/setup-handoff.json`) | walk the flow under test |
| **Verifier**, one per flow | the flow file and the handoff manifest | the diff, the spec, the setup context's reasoning | the evidence files and a `claim.json` in the result schema | eval or script shortcuts after setup, direct database writes after setup, edits to tracked files |
| **Checker**, one per flow | the flow file, the evidence, the claim | the verifier's transcript, the diff | `result.json`, the verdict that counts | trust an exit code, trust the claim without opening the evidence, fix the product |

Why three per flow and not one. Setup is allowed to cheat: it teleports to the door with seed scripts and direct writes, because everything before the thing under test is not the test. The verifier is not allowed to cheat: it walks through the door by hand, and the harness denies it the shortcuts setup used. And the checker is never the turn that produced the payload, so a verifier cannot grade its own run. The checker opens the evidence, applies the verdict rule, and may downgrade the claim. It never upgrades it.

The orchestrator boots nothing and drives nothing. Setup boots. If the app must outlive the setup context, setup detaches the server (`setsid nohup ... < /dev/null &`) and writes the URL into the handoff manifest, and the orchestrator kills it after the checker returns.

## Phase 1: identify the flows

Work through the steps in order. Each step adds rows to one list, and the list is the deliverable of this phase.

### 1. Read the spec first, if there is one

Open the spec and read sections related to: **Goals** and the **Verification plan**. A good verification plan is one entry per decided verifier, with exact commands, boundary-visible expected results, pass and fail conditions, and the environment each check runs in. Read it as a flow list, because that is what it is:

- one entry in the verification plan is one flow, tag it `added`
- one row in changes to existing behavior is one flow, tag it `touched`
- the environment named per check is the flow's `requires` line

Then make the spec ask (`references/asks.md`, ask 1). It is a confirmation, not a search: check every verifier in the plan still names a flow you can run, and list which surfaces the code changed that the plan never mentioned.

If there is no spec, skip to step 2. A bug fix, a dependency bump, a Friday afternoon change often has none, and then the diff is the only pass.

### 2. Ask the diff for the end-to-end tests

Open the PR and make ask 2: **list the end-to-end verification tests that would be done for this feature**. Say end-to-end. Ask for a test matrix, or for tests in general, and the model pads the list with unit tests and integration tests, which are cheap rows that prove nothing about the flow. End-to-end pulls it to the user's side: what changed, which pages, routes, rows and messages that reaches, which inputs and states each one has, and which paths a user would walk.

It over-enumerates. That is what you want here. Cutting a list is easy. Finding the row nobody listed is the hard part. Tag each row:

- `added`, something a user can newly do
- `touched`, an existing flow whose code moved

If the change has no runnable surface at all (docs, CI config, types, a pure refactor), write that as the result and stop. Do not stage a recording. A video of a page the diff never touched looks like proof and is worth less than an honest "nothing here runs".

### 3. Ask who else reads what the diff wrote

The bug a change introduces usually lands in a flow the diff never touched, because two flows share one thing: a table column, a helper component, a route, a piece of session state. The change writes to it through one flow. Another flow reads it, and that flow's files are not in the diff. In a rename, the breadcrumb and the tab title never changed. They read the column the rename wrote.

So make ask 3: **who else reads what this diff wrote**. The agent follows each written column, component, route or state out to every flow that hangs off it. Tag those `shared`. List them in full, even the ones you will not run.

### 4. Reconcile the lists

Put the spec list and the diff list side by side. Where they disagree is the interesting part:

- a flow in the spec that the diff cannot see is an intent the code missed; report it as a finding now, do not wait for the run
- a flow the diff touched that the spec never named is a regression waiting to happen; keep it as `touched`

### 5. Pick the boundary for each flow

Verify at the boundary the user experiences, not the boundary that is convenient. For every surface pick the outermost reader that is still cheap enough:

| Surface | Reader |
|---|---|
| a page or screen | headless browser (Playwright), recorded |
| a route or API | curl or the app's client |
| a database row | psql or the app's query tool |
| an outbound email | a local mail catcher (Mailpit) |
| a chat message, webhook, queue | the receiving service's API or a local shim |

A component test in isolation says nothing about the flow. An API test says nothing about the screen. If any still appear in the list, they are cheap rows, not proof. Keep the row that proves the flow, and drop lower only to find where a fail lives. If the change adds or changes a screen, record the screen, even when a service call would test it faster.

A surface with no reader is not a flow you skip quietly. Mark it **not driven** and say which probe is missing. The not-driven list is what tells you which reader to build next.

### 6. Write one flow file per flow, with a requires line

Use `templates/flow.md`. A flow file is short: a path, the user steps, the expected outcome, what to verify, the fixtures it needs, and a `requires` line. The requires line is the link back to the environment. The environment **provides** capabilities. The flow **requires** some. A flow is runnable when what it requires is a subset of what the environment provides. Anything else is `blocked`, and blocked is a word in the table, never a silent skip.

### 7. Hand over the table

The output of this phase is a table, and it is the input to everything after:

| Flow | Tag | Surface | Reader | Status |
|---|---|---|---|---|
| RENAME-01 lesson title shows on the lessons page | added | page | playwright | runnable |
| RENAME-03 breadcrumb shows the new title | shared | page | playwright | runnable |
| RENAME-05 title in the digest email | shared | email | mailpit | blocked: no smtp |
| RENAME-06 Japanese IME input | touched | page | (none) | not driven |

Then decide what runs. **Added and touched always run.** Shared flows are listed in full, and how many run is a cost call by blast radius: an internal tool runs the top few, a customer-facing change runs them all. Say which tier you chose and why.

## Phase 2: run the flows

Review reads the diff. Verifying runs it. Boot the real app and drive each runnable flow the way a user would. The detail is in `references/evidence.md`; the rules are:

- **Three fresh contexts per flow: setup, verifier, checker.** See the roles table above. Setup seeds and boots and writes the handoff manifest. The verifier gets the flow file and that manifest, nothing else. The checker gets the flow file, the evidence and the verifier's claim, and writes the verdict.
- **Setup boots the real app the way the repo boots it**, against a real database, fresh or seeded, never mocked away. One setup per flow means one clean slate per flow. Setup states in the manifest what it seeded, or could not. A pass against an empty database proves little.
- **Drive at the boundary you picked** in step 5, then assert on what the user would see and on what the database now says. A 200 with no row written is a fail.
- **A missing external service is not the end.** Work the ladder in `references/shims.md`: a published shim, a mock from the vendor's OpenAPI spec, a shim you write, and only then "could not reach the flow". Point the app at the shim with an environment variable. Never patch the code under verification.
- **One evidence file per flow.** A flow with UI leaves an `.mp4` with a caption per step carrying the live value, plus an independent database check. A flow with no UI leaves one text file with the request, the response and the rows, in the order they ran. Never a GIF. Read the evidence back before you call the flow passed. The assertion is on the evidence, not on the script exiting 0.
- **Separate three things: the surface you drive, the layers you check, the verdict you emit.** Most of the mess in verification comes from collapsing them. You drive one surface. You check five layers, each with its own result. Then one rule turns the layers into one of four verdicts. The layers and the rule are in `references/evidence.md`; the shape is:

  | Layer | Question | Gates the verdict |
  |---|---|---|
  | 1 completion | did the user reach the end state | yes |
  | 2 visual | does the UI match the spec at each step | yes |
  | 3 state | is the database or store in the expected shape after | yes |
  | 4 incidentals | console errors, failed requests, framework warnings, render churn | never |
  | 5 side effects | emails sent, webhooks fired, jobs enqueued | when the flow names one |

- **Four verdicts, and only four.** `PASS`, `PASS-WITH-FINDINGS`, `FAIL`, `BLOCKED`. Incidentals never downgrade a flow to FAIL on their own. A flow that completes never masks a state mismatch: a checkout that shows "Success" and writes nothing to orders is FAIL at layer 3. BLOCKED means you could not verify, and it is never counted as a product defect. The verifier writes its claim and the checker writes the result, both in the fixed schema in `templates/result.json`, layer to verdict to evidence pointer. Never prose. Only the checker's file feeds the report.

## Phase 3: report

One line per flow: the flow id, its tag, the verdict, and for a FAIL the layer and the step. Build that table from the result files only, and refuse any result file that breaks the schema or the verdict rules. Then the blocked list with what each one is missing, and the not-driven list with which reader would unblock it. A flow reported as BLOCKED is honest. A flow quietly dropped is a lie of omission.

Reviewers read the schema, not the run. A few hundred tokens of layer, verdict and evidence pointer replaces re-reading the whole transcript, and "partial" stops being a judgment call.

Fixes are not automatic. A FAIL is a finding: report the layer, the step, observed against expected, and the evidence pointer. A PASS-WITH-FINDINGS lists its incidentals with a severity each. The user decides whether a fix round happens. If they ask for one, it is one round, then one re-run of that flow, and a second FAIL ships as a reported failure.

Do not let a passed flow reach the user as a sentence alone. The user cannot tell that apart from a flow nobody ran.

## Files in this skill

| Read it when | File |
|---|---|
| You are about to ask the agent anything in Phase 1 | `references/asks.md`, the four asks, verbatim |
| You are writing a flow file or the table | `references/flow-spec.md`, the fields and the requires rule |
| Setup is handing the app to the verifier | `templates/setup-handoff.json`, the manifest |
| You are booting, driving or recording a flow, or writing a verdict | `references/evidence.md`, the recording, the five layers, the four verdicts |
| A missing service is blocking a flow | `references/shims.md`, the ladder and the lookup table |
