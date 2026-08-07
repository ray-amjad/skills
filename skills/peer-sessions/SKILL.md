---
name: peer-sessions
description: Run a fleet of Claude Code sessions on this machine and make them talk to each other with SendMessage — launch them in cmux windows, panes and splits, address them correctly, hand out work, and collect their replies. Use this skill whenever the user wants two or more Claude sessions working together, mentions SendMessage, ListAgents, peer sessions, cross-session messaging, or agents messaging each other; whenever they want to spin up sessions in new windows, workspaces, panes or splits to watch them work or film a demo; whenever work should be fanned out to parallel sessions rather than subagents; and especially whenever a send fails with "not an agent in this conversation", "re-send with the ref", or any confusion about why one session cannot reach another. Also use it for tearing those sessions down cleanly afterwards.
---

# Peer sessions

Claude Code sessions on this machine can send messages to each other. A message becomes a **user prompt** in the receiving session. This one fact explains each rule below.

The loop: spawn a fleet → send a brief to each peer → end your turn → replies arrive as new user turns → tear down.

## 1. Spawn

```bash
python3 ~/.claude/skills/peer-sessions/scripts/spawn-fleet.py --window \
  orbits:/tmp/lab/orbits planets:/tmp/lab/planets sun:/tmp/lab/sun
```
```
window F8464A83-...
+ orbits    uds:/tmp/cc-socks/17466.sock
+ planets   uds:/tmp/cc-socks/17398.sock
+ sun       uds:/tmp/cc-socks/17585.sock
3 ready in 10s.
```

Each argument is `NAME:DIR`. Flags: `--window` (own window), `--per-workspace 1`, `--model`, `--claude-arg <flag>` (repeatable escape hatch). The script returns when each session is addressable. The script names each session that stalled.

Sessions start with `--permission-mode auto`. This is the only mode that works with no human present. An `--allowedTools` list stalls on the first MCP tool that is not in the list. `--dangerously-skip-permissions` makes the receiver hold inbound messages for human approval. The peer then never sees your brief.

For unusual layouts, manual cmux work, or forks: read `references/manual-rig.md`.

## 2. Send the briefs

```
SendMessage(to: "orbits", message: "...", summary: "5-10 words")
SendMessage(to: "orbits [de6649]", message: "...", summary: "...")
SendMessage(to: "uds:/tmp/cc-socks/17466.sock", message: "...")
```

**The first send with a bare name always bounces** — "not an agent in this conversation, re-send with the ref". That is a confirmation, not a failure. Copy the `[ref]` from the error and send again. Send all briefs in one batch. They bounce together and you re-send them together. A `uds:` address does not bounce.

Each brief that expects a reply must end with your literal address (from `peer-addr.py --me`):

```
When done, message me back:
SendMessage(to: "uds:/tmp/cc-socks/4667.sock", message: "...")
```

The peer cannot find out who you are. Do not make the peer guess. Ask for a fixed reply format ("<name> done: <URL>") — replies from a large fleet then collate with no work. Add a scope guard too ("research and write only, do not touch <repo>"). Peers obey it.

Two rules: `success: true` means the message arrived, not that the peer did the work. A send is one-way — say clearly if you want a reply.

## 3. End your turn

When the briefs are out, **stop**. A peer reply IS the notification. The reply arrives as a new user turn and wakes you. A poll loop on the panes burns tokens and blocks the user. Poll only when you must see the screen (filming, or a quiet session) — recipes in `references/manual-rig.md`.

## 4. Tear down

**When you close the UI, the sessions do not stop.** `close-window` and `close-workspace` return `OK` and each `claude` process stays alive as an addressable orphan. Kill first, then close, then check:

```bash
kill <pid> <pid>                                    # pids from peer-addr.py
cmux close-window --window <uuid>                   # can return OK and not close — see troubleshooting
python3 ~/.claude/skills/peer-sessions/scripts/peer-addr.py   # confirm gone
```

## When something fails

`peer-addr.py` lists each live session and gives a reason for each unreachable one. For the message checkpoints, the 2.1.224 version wall, stale sockets, and stalled permission prompts: read `references/troubleshooting.md`.

One rule is not optional: a peer carries none of the user's authority. If your send is denied, or a peer reports a denial, tell the user. Never route around a permission decision through another session.
