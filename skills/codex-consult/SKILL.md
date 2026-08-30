---
name: codex-consult
description: Get an independent second opinion from OpenAI's Codex CLI — a different model with no stake in your work. Three modes. Review — an independent diff review with a pass/fail gate. Challenge — adversarial, tries to break your code. Consult — ask it anything, with follow-ups. Use when asked to "codex review", "codex challenge", "ask codex", "consult codex", or for a "second opinion" on a diff, plan, or decision.
---

# Codex consult

A second opinion is only worth having if it's independent. Codex is a different model, it hasn't seen your reasoning, and it won't defend your choices — so hand it the artefact, take its answer verbatim, and only then add your own view.

## Setup, once per run

```bash
which codex || echo "NOT FOUND"
```

Not found → stop and tell the user: install with `npm install -g @openai/codex`, then `codex login`.

For review mode, find the base branch (`gh pr view --json baseRefName -q .baseRefName`, falling back to the repo default, falling back to `main`) and refresh it — `git fetch origin <base> --quiet` — because a stale local base makes Codex review every merged-but-unfetched commit alongside the actual diff.

## How to run it, all modes

Plain text, never `--json` (it buffers and hangs). Capture to a file so the user sees one clean block, not a stream:

```bash
OUT=$(mktemp /tmp/codex-XXXXXX.txt)
codex <command> ... > "$OUT" 2>&1
```

Run with a generous Bash timeout (10 minutes), end prompts with `< /dev/null`, and always pass maximum reasoning: `-c 'model_reasoning_effort="xhigh"'`. When it finishes, Read the file and present the output **verbatim** — no truncating, no summarising — then add your own take after it, including anywhere you disagree and why. If the output has no response block, retry once; twice means a transient backend failure — say so rather than inventing a verdict.

## Review — `codex review`

```bash
# one commit ahead of base — review exactly that commit:
codex review --commit $(git rev-parse HEAD) -c 'model_reasoning_effort="xhigh"' > "$OUT" 2>&1
# multiple commits — review the branch against base:
codex review --base <base> -c 'model_reasoning_effort="xhigh"' > "$OUT" 2>&1
```

Any user instructions ("focus on security") go in as the prompt argument before the flags. The gate: any `[P1]` finding → **FAIL**; only `[P2]` or nothing → **PASS**. State the gate verdict after the verbatim output. If Claude's own review already ran this session, close with a short cross-model comparison: what both found, what only each found.

## Challenge — adversarial

```bash
codex exec "Review the changes on this branch against <base> (run git diff origin/<base>). Your job is to find ways this code fails in production. Think like an attacker and a chaos engineer: edge cases, race conditions, security holes, resource leaks, silent data corruption. No compliments — just the problems." -s read-only -c 'model_reasoning_effort="xhigh"' > "$OUT" 2>&1
```

If the user gave a focus (`challenge security`), narrow the prompt to it.

## Consult — ask anything

```bash
codex exec "<the user's question, plus any file contents it needs>" -s read-only -c 'model_reasoning_effort="xhigh"' > "$OUT" 2>&1
```

For a plan review, prepend: *"You are a brutally honest technical reviewer. Find the logical gaps, unstated assumptions, missing edge cases, overcomplexity, and sequencing problems. Be terse. Just the problems."* — then the plan.

Follow-ups: the output contains a `session id:` line. To continue the same conversation, `codex exec resume <session-id> "<follow-up>"` with the same flags.

## Rules

- **Read-only.** This skill never modifies files, and Codex runs with `-s read-only`. Its findings are input to your next move, not patches.
- **Verbatim first, synthesis second.** The user asked for Codex's opinion, not your summary of it.
- **Disagreement is the product.** Where Codex and you differ, say so explicitly — that fault line is usually where the real issue lives.
