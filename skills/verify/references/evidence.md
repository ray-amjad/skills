# Running a flow and leaving evidence

Read this when you boot the app, drive a flow, or write the outcome.

## Three contexts per flow

Setup, verifier, checker. Each is a fresh context. The roles table in `SKILL.md` says what each gets and never sees. The handoff between them is two files:

- **Setup to verifier:** `setup-handoff.json` (`templates/setup-handoff.json`). The app URL, the database URL, the session to inject, the fixture ids setup created, and what was seeded. The verifier reads this and the flow file. Nothing else. If it needs the diff to understand the flow, the flow file is not finished. Send it back to Phase 1.
- **Verifier to checker:** the evidence files and `claim.json`, in the result schema. The checker opens the evidence, checks each layer against the flow file's expectations, and writes `result.json`. It may downgrade a claim. It never upgrades one. Keep claims under the evidence folder and results in their own folder, so the report reads only results.

One setup per flow gives one clean database per flow. Flows that must share state share one setup, and the flow files say so.

## Boot the real thing

Setup boots the app the way the repo boots it: its dev server, its database, its queues if the flow needs them. If the repo has a boot recipe in its docs or its skills, use that. Do not reinvent it, and do not mock the database away.

- Start from a fresh database with the real schema, then seed. If the app has a seed script, run it. If not, drive the app's own API or UI to create what the flow needs. State that you seeded, or could not.
- Setup detaches the server from its shell (`setsid nohup ... > /tmp/dev.log 2>&1 < /dev/null &`) and wait until it answers before you drive anything.
- Setup runs once per flow, so each flow starts from its own database. One flow's rows can mask another flow's bug.

## Drive at the boundary

The verifier walks the flow the way a user would, at the reader the flow file names. No eval, no script shortcut, no direct database write after setup: those were setup's tools, and the harness denies them here. Then assert twice: on what the user sees, and on what the data now says. A 200 with no row written is a fail. A row written behind a page that shows an error is a fail.

Check rows by id, not by count. Read the response body, not only the status. Watch the state the flow claims, not the page that happens to render.

## One evidence file per flow

Every flow leaves exactly one evidence file, and a passed flow with no file is not a pass.

### A flow with a screen: an mp4

A still proves one state. A flow with steps needs a recording. Record with headless Playwright, transcode to H.264 mp4 with ffmpeg. Never a GIF: 256 colours turns app UI into a dithered mess. Never a webm: chat clients are unreliable about it.

```js
import { chromium } from 'playwright'
const b = await chromium.launch({ headless: true })
const ctx = await b.newContext({
  viewport: { width: 1280, height: 800 },
  recordVideo: { dir: '/tmp/rec', size: { width: 1280, height: 800 } },
})
const p = await ctx.newPage()
await p.goto('http://localhost:3000/...')
// interact; pause ~700ms after each step or the proof flashes past in three frames
await ctx.close()                            // the video finalises on CONTEXT close
await p.video().saveAs('/tmp/flow.webm')     // after ctx.close()
await b.close()
```

```bash
ffmpeg -y -i /tmp/flow.webm -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -r 30 \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -movflags +faststart /tmp/flow.mp4
```

A headless recording has no address bar, no tab title, no cursor. Most of what you prove leaves no pixel behind: a URL that stayed the same, a request the app never made, a row that landed. So put the claim in the frame. Before each step, write a caption into the page that carries the live value ("title now: Onboarding v2", "tickets row 42: open"). Hold it long enough to read. Caption the failed step too. That is what turns a broken run into evidence instead of a puzzle.

Then add an independent data check next to the recording: a `psql` query, or the app's own read API, in a short text file or in the final caption. The screen and the data have to agree.

### A flow with no screen: one text file

A webhook, a cron job, an API route, a CLI command has nothing to record. It still needs a file. Put the request, the response and the rows in one file, in the order they ran:

```bash
{
  echo '== request =='
  curl -sS -X POST http://localhost:3000/api/webhooks/bounce -H 'content-type: application/json' -d '{...}'
  echo; echo '== db =='
  psql "$DATABASE_URL" -c "select id, status from tickets where id = 42"
} 2>&1 | tee /tmp/flow-6.txt
```

Do not build a browser recording for a flow like this. A video of a page the flow never touches looks like proof and is worth less than the text.

### A copy or layout change: also read it rendered

A typecheck cannot tell you a sentence you cut was load-bearing. So when the change is wording, labels, empty states or layout, the recording is half the evidence. The other half is a fresh read of the rendered page: what is now missing, orphaned, clipped, or leaning on a heading that no longer says it. Capture every state the change touched, not only the happy one. Error, empty, signed-out and confirmation screens are where trimmed copy does its damage.

## Label what was real

If any part of the flow ran behind a shim, say so in the evidence file: which calls went over real HTTP against real logic, which sat behind a shim, and which rung of the ladder in `references/shims.md` the shim came from. A reader must be able to tell.

## Five layers, each with its own result

The surface you drive is one thing. The layers you check are another. The verdict you emit is a third. Keep them apart. Each layer gets its own result, `green`, `red` or `skipped`, and its own evidence pointer.

1. **Completion.** Did the user reach the end state. Binary. Evidence: the recording, with a timestamp, or the last line of the text file.
2. **Visual correctness.** Does the UI match the spec at each step. One screenshot per step, checked against a reference image or against the assertion list in the flow file. Evidence: the screenshot for the step.
3. **State correctness.** Is the database or store in the expected shape afterwards. Assert on rows, by id, not on the UI's claim about rows. Evidence: the query and its output.
4. **Incidental defects.** Console errors, failed network calls, framework warnings, mount and unmount churn, unexpected re-renders. Collected passively during the run, each with a severity. They never gate the flow.
5. **Side effects.** Emails sent, webhooks fired, jobs enqueued. Often forgotten, often where the real bug hides. Check the mail catcher, the shim's request log, the queue. Gates the verdict only when the flow file names an expected side effect; otherwise `skipped`.

A flow with no screen skips layer 2. A flow file that names no side effect skips layer 5. Say `skipped`, never leave the key out.

## Four verdicts, one rule

- **PASS.** Layers 1 to 3 green, layer 5 green where it applies, no high-severity incidental.
- **PASS-WITH-FINDINGS.** The gate layers are green, and incidentals were logged. The flow works, the code is not clean. This is the only meaning of "partial" in this skill.
- **FAIL.** Layer 1, 2, 3, or an applicable 5, is red. Name the layer and the step.
- **BLOCKED.** You could not verify: the environment is down, a fixture is missing, auth is broken, a service is absent and the shim ladder ran out. Distinct from FAIL so it is never counted as a product defect. Only valid after `references/shims.md`, and `blocked_on` names which rung broke.

Two consequences of the rule. Incidentals never downgrade a flow to FAIL on their own. And a flow that completes never masks a state mismatch: a checkout that shows "Success" and writes nothing to orders is FAIL at layer 3, not partial.

If you know the older three words, the map is: passed is PASS, ran_wrong is FAIL, could_not_boot is BLOCKED. PASS-WITH-FINDINGS is new, and it is the one that stops agents writing "partial" when they mean "I am not sure".

## The result file: a fixed schema, never prose

Every flow ends with one JSON file in the shape of `templates/result.json`: the flow id, the verdict, one entry per layer with its own result and evidence pointer, the incidentals as a list, and one or two sentences of detail. The report reads the folder of them, rejects any that break the shape, and prints the table.

Infrastructure is never a product bug. A result that says BLOCKED with an empty `blocked_on` has not returned a verdict. Send it back with the ladder.

Read the evidence back before you write PASS. The script exiting 0 is not the assertion. The file is.
