# Verify → fix

List the flows the change touches. If it has no runnable surface (docs, CI config, types, a pure refactor), say so and stop and tell the user.

Write each flow's brief before anything boots: the end state the user reaches, the rows the app must write, and the side effects outside the app (email, webhook, queued job).

A fresh agent then boots the app against a real non-production database, fakes only the outside services the brief names, and drives the flow the way a user would: a browser for anything with a screen, real requests for an API.

Codex (GPT-6-Luna) is a good driver.

After a flow is driven, a separate agent that did not drive the flow reads the database, logs and screenshots and gives the verdict. Route on that verdict, never on the driver's claim.

**Evidence,** one entry per flow in the PR's Verified section: screenshots or a recording for anything with a screen; the real request, response and a database query for a backend flow, not just a 200. Never capture a real person's data.

**Outcomes:**
- **Passed.** Done. If a small defect is found along the way, it becomes a new GitHub issue.
- **Ran wrong** (an error, wrong output, a 200 with no row). Back to the builder with evidence, then verify again. Two rounds at most.
- **Couldn't boot** (missing credential, environment or database). No fix loop, because no code change repairs a credential. Report the flow as unverified.
- **Unreachable** (the precondition is a state the app never creates). Report it as unreachable, not failed: failed means the code is wrong, unreachable means it never runs. Ask the user whether to delete that branch or what reaches it.
