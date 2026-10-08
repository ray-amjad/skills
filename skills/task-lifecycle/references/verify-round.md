# The verify → fix loop

Read this at step 5, after the review rounds, or in the **already-built** mode. Wait for every
subagent's result before you route.

## Run it

List the flows the change touches. In the already-built mode, derive them from the diff. If the change
has no runnable surface (docs, CI config, types, a pure refactor), say so and record nothing.

A verification is three subagents in a row:

1. **SETUP** boots the app against a real database (a local or throwaway one, never production),
   seeds the data the flow needs, and fakes any outside service the brief names (email, payments,
   webhooks) so the side effect can be read back.
2. The **VERIFIER** drives the flow as a user would: a real browser for anything with a screen, real
   requests for an API. It reports what it did and saw.
3. The **CHECKER** did not drive the flow. It reads the database, the logs and the screenshots, and
   writes the verdict.

**Route on the checker's verdict, never on the verifier's claim.** Running the verifier on a different
model from the builder (for example Codex, `codex exec` at high reasoning effort) catches more,
because it does not share the builder's blind spots. If the verifier cannot run, record
`could_not_boot` and report the flow as unverified. Do not quietly swap in a weaker check.

**A flow's brief names three things:** the end state the user reaches, the rows the app must write,
and the side effects outside the app (email, webhook, queued job). A side effect you name is a failure
when it is missing, unless you mark it `optional`. Write the brief before setup runs, because setup
fakes only the services the brief names.

## Evidence: one flow, one file, in the PR

- **A user-facing flow:** a screen recording or a numbered sequence of screenshots of the flow. A
  changed screen is user-facing, even when an API call would test it faster.
- **A backend flow with no UI:** the real request, response and database output in one text file,
  `… 2>&1 | tee flow-<n>.txt`. Do not fake a browser recording.
- **Always:** an independent database check (`psql "$DATABASE_URL" -c "select …"` or the equivalent)
  that the data landed, not only a 200.

A flow described only in prose is a claim, not evidence.

The PR's `## Verified` section gets **one entry per flow, in order**, including flows with no picture.
Count the entries before you publish. Evidence in a PR is public for as long as the repo is: never
capture a real user's name, email, or data.

## Route on the outcome

The checker reports **which of five outcomes** the flow hit:

- **`passed`:** go to confirm.
- **`passed` with `defects`:** still a pass. Give each defect a home. The default is a GitHub issue,
  with the checker's screenshot or log line as evidence, linked from the flow's `## Verified` entry.
  Fix it in this PR only when the user asks, or when it is a few lines in a file this diff already
  changes. That fix shares the one fix round below. Say which defects you filed and which you fixed.
- **`ran_wrong`** (an error, wrong output, a 200 with no row): tell the user. Then dispatch **one**
  fresh fixer with only the verify evidence, have it commit and push, and **re-verify once**. If the
  flow still fails, stop and report it. **One round is the cap** (two in the already-built mode),
  because each cycle boots a server and drives a browser.
- **`could_not_boot`** (missing credential, missing env, the database would not start): **do not
  fix-loop**, because no app change repairs a credential. Record it, attach the text evidence, say
  plainly that the flow is unverified, and go to confirm.
- **`unreachable_state`** (the precondition is a state the app never creates): **do not fix-loop, and
  do not build a better harness.** **Report it as UNREACHABLE, never as failed.** *Failed* says the
  code is wrong. *Unreachable* says the code never runs. If every flow for the user's actual ask
  passed, the change is verified. Name the branch the flow was covering, and put it in the final reply
  as an open question: delete it, or keep it and say what reaches it. A verifier that only ran out of
  ideas is `could_not_boot`, and gets a sharper brief.
