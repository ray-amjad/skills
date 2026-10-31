# Prove It

**Skills that make your coding agent prove its work.**

Your agent says "done". The tests pass. The code looks right. Then you open the app and the button does nothing.

Prove It gives your repo its own verification skill: one that launches your real app, drives it the way a user does, saves the evidence and cleans up after itself. Then it keeps that skill honest, and tries to fool it.

Works with Claude Code, Codex and any agent that reads `SKILL.md` files. Free and MIT licensed.

**Learn it in 7 days.** The free email course teaches one idea a day, using real repos and the mistakes agents actually make. You'll also hear about new skills when they land.

**[Get the free 7-day course](https://www.agenticcoding.school)** <!-- TODO: switch to the course page URL once it is live -->

## Install

<details open>
<summary><strong>Claude Code</strong></summary>

```text
/plugin install prove-it --marketplace ray-amjad/skills
```

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add ray-amjad/skills
codex plugin add prove-it@ray-amjad
```

</details>

<details>
<summary><strong>Any other agent, or files you can edit</strong></summary>

```bash
npx skills@latest add ray-amjad/skills
```

Or copy the folders you want from `skills/` into `~/.claude/skills/` (Claude Code) or `~/.agents/skills/` (Codex).

</details>

Then, in the repo you want to verify:

```text
/create-prove-it
```

## Why it exists

Coding agents fail in the same few ways. Each skill fixes one.

### 1. "Done" means the code compiles

**The problem.** The agent reads its own diff, runs the tests and calls it done. Tests mock the parts that break. Nobody opened the app.

**The fix.** [`/create-prove-it`](./skills/create-prove-it/SKILL.md) gives your repo a `prove-<app>` skill that runs the real app, so any agent can type `/prove-<app>` at the end of a change, before it says done. It reads the diff, works out which pages, routes and commands the change reaches, drives those and tries to break them. Or name a flow ("prove checkout") and it proves that. It starts by asking where users actually meet your app (the web page, API, CLI, database, emails, background jobs) and whether your agent can reach each of those from your machine. Where it can't, it suggests a way in: a sandbox, a local emulator, a seeded test account or a headless browser. Then it shows you a brainstorm:

| Method | Catches | Misses | Cost | Reachable now? |
|---|---|---|---|---|
| Browser, driven like a user | The open count not updating after a tick | Whether the task was really saved | Chromium once, ~5s a run | Yes |
| API calls | Empty titles accepted, wrong status codes | What the page does with the response | Free, under 1s | Yes |
| Stored-state check | "Saved" on screen, nothing on disk | Whether a user can see it | Free | Yes |
| Email capture | Reminders that never send | Real delivery | A local mail catcher | No: needs `MAIL_API_KEY` |

You pick the methods. It writes the skill using your repo's real commands and selectors, then runs it once, end to end, and shows you the receipt.

### 2. The verifier goes stale

**The problem.** You rename a button, add a page, change a port. The verification skill still describes last month's app, and the next agent trusts it.

**The fix.** [`/maintain-prove-it`](./skills/maintain-prove-it/SKILL.md) reads the receipts from past prove runs: the steps that failed, the retries, the command that finally worked, the step that broke on a change that had nothing to do with it. Tell it about any bug that slipped past and it adds the check that would have caught it. When the app and the skill disagree, it works out which one is wrong. It fixes the skill, proves every fix live, and reports bugs in the app without touching your code.

### 3. The verifier says PROVED on a broken app

**The problem.** A check that can't fail is worse than no check, because it gives you confidence you haven't earned.

**The fix.** [`/audit-prove-it`](./skills/audit-prove-it/SKILL.md) breaks your change on purpose, in the files it touched, one small realistic bug at a time: a counter off by one, a save that never happens, the right output with the wrong exit code. A fresh agent then runs your verifier without knowing what was planted. You get a scorecard, every miss with the fix for it, and an untouched working tree at the end.

In testing, the first audit of a generated verifier planted 7 bugs. The agents doing the checking caught 5, but the verifier's own scripts caught only 1, because every check ran against a single record. That finding now shapes how `/create-prove-it` writes checks.

## The skills

| Skill | What it does | When |
|---|---|---|
| [`/create-prove-it`](./skills/create-prove-it/SKILL.md) | Brainstorms how your repo can be verified, then generates a `prove-<app>` skill and proves it works | Once per repo, then `/prove-<app>` at the end of every change |
| [`/maintain-prove-it`](./skills/maintain-prove-it/SKILL.md) | Learns from past prove runs and missed bugs, and fixes the skill where it drifted | After prove has run a few times, or a bug slipped past |
| [`/audit-prove-it`](./skills/audit-prove-it/SKILL.md) | Plants bugs in a change and checks whether the verifier catches them | After creating it, then now and then |

## What it adds to your repo

```text
your-repo/
  .claude/skills/prove-<app>/      # .agents/skills/ on Codex
    SKILL.md                       # scope from the diff, start, health check, drive, try to break it, evidence, clean up
    scripts/                       # start, health, stop, scripted checks
  .prove-it/                       # git-ignored
    runs/<timestamp>-<slug>/       # receipts (what was proved, verdicts, retries), screenshots, logs
    audits/<timestamp>/report.md
```

## License

MIT. See [LICENSE](./LICENSE).
