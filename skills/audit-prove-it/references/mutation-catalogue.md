# Bugs to plant, by layer

Plant them in the files the target change or flow runs through. Pick across layers. A good audit has at least one bug the UI hides, one the API hides and one that only shows in stored state or logs.

## UI only (data is fine, the screen lies)
- A counter or total that reads one item off (`open - 1`), or counts the wrong items.
- A list that drops its last item, or shows items in the wrong order.
- A status that never updates on screen after an action (no refresh), while the API is correct.
- A button whose label is right but whose handler calls the wrong action.
- An error message the UI never shows (a swallowed error state).

## API (the response is wrong)
- A wrong status code on success (200 instead of 201) or on failure (200 with an error body).
- Validation removed: empty or bad input is accepted.
- A field missing or renamed in the response.
- A filter or search that ignores its parameter.
- An update that changes the wrong field, or the wrong record.

## Stored state (the response says yes, nothing is saved)
- The save call commented out, so the response returns the new object but nothing persists.
- A write that hits the wrong record, or writes a stale copy.
- Delete that returns success but leaves the row.
- An ID generator that repeats.

## CLI
- Correct output with the wrong exit code (0 on failure, or 1 on success).
- Errors printed to stdout instead of stderr.
- A flag that is parsed but ignored.
- Output that is right for one item but wrong for several (only the first line).

## Errors and logs
- A try/catch that swallows a failure and returns an empty success.
- A thrown error that only shows in the server log while the user sees a normal page.

## Side effects
- An email, webhook or job that is logged as sent but never queued.
- A side effect sent twice.

## Shared code and parity
- A change in a shared function both surfaces call (the app and the MCP server), so parity still matches. Only the spec catches it.
- A schema or auth change that breaks an existing flow the new feature never uses. The skill has to count that flow as touched and check it against the app before the change.

## Migrations (new system only)
- A field that differs only in a way the allowed-differences list happens to ignore (a trimmed string, a rounded number).
- Correct output for the cases on file, wrong for a nearby input (an empty list, a unicode name, the largest id).

## Startup (use at most one)
- A missing env default or a broken import, so the app fails to start. This only tests the health check.
