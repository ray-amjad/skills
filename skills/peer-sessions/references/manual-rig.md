# Manual rigging, forks, and paths that the skill does not cover

Read this when `spawn-fleet.py` does not fit: unusual layouts, filming, forks, or a `claude`/`cmux` capability that the skill does not name.

## The cmux object model

A **window** holds workspaces. A workspace holds panes. A pane holds a **surface** (the terminal that you type into). Workspaces and surfaces use short refs (`workspace:26`, `surface:93`). Windows use full UUIDs.

## One workspace, two sessions

```bash
cmux new-workspace --name peer-demo --cwd <dir> \
  --command "claude --name alpha --permission-mode auto" --focus true
# → OK workspace:26

cmux new-split right --workspace workspace:26 --focus true
# → OK surface:93 workspace:26
cmux send     --workspace workspace:26 --surface surface:93 "claude --name beta --permission-mode auto"
cmux send-key --workspace workspace:26 --surface surface:93 Enter
```

`new-split` gives you a shell, not a session. You start the second session when you type into that shell. `new-split` prints the new surface id. You need `cmux tree --workspace W` only for the first pane's surface, because cmux never prints that surface back.

## A separate window

```bash
cmux new-window
# → OK 013D22DA-F68D-43E8-A7CB-F6B7E7251336

cmux new-workspace --name space-lab --cwd <dir> \
  --window 013D22DA-F68D-43E8-A7CB-F6B7E7251336 \
  --command "claude --name gamma --permission-mode auto" --focus true
```

Then split, send, and send-key as above. `cmux list-windows` shows the windows that exist.

## Watch the panes

```bash
cmux read-screen --workspace W --surface S --lines 30
```

To wait for a session, poll for the spinner. A session that works renders `Word… (12s`. An idle session does not contain `… (`. Check for a stalled permission prompt in the same loop. "The session waits for a human" and "the session is done" look the same on screen:

```bash
screen=$(cmux read-screen --workspace W --surface S --lines 40)
grep -qF '… ('                     <<< "$screen"   # still working
grep -qF 'Do you want to proceed?' <<< "$screen"   # stalled — needs an answer
```

Give the poll a large time ceiling. Research plus writing runs for several minutes. Poll only when you need eyes on the screen. If you asked the peer to reply, end your turn instead.

## Fork a session

`--fork-session` starts a peer from the history of an existing conversation, under a **new** session id:

```bash
claude --resume <sessionId> --fork-session --name reviewer-a --permission-mode auto
```

The fork starts with the full transcript and a fresh id. The original session continues, and you can address both. Without `--fork-session`, `--resume` uses the same id and the sessions collide.

Session id vs socket: the socket (`uds:...`) is the address of a running *process*. The session id is the address of a *conversation on disk*. Get your own id from `peer-addr.py --me`. Get another session's id from `sessionId` in `~/.claude/sessions/<pid>.json`.

To fork one session N ways is better than to write the same long brief N times.

## When you need something that this file does not cover

Read the help. Do not guess. Do not assume a thing is impossible:

```bash
COLUMNS=200 claude --help    # a pipe through head kills it with SIGPIPE;
claude agents --help         # narrow terminals wrap it into noise
cmux --help
```

Fleet flags that come up often: `--add-dir` (a second writable directory), `--model` / `--effort` (cheap workers beside one expensive reviewer), `--agent` / `--append-system-prompt` (a standing role, so you do not repeat it in each brief), `--worktree` (own git worktree per session when the fleet edits one repo). Check the spelling of each flag in the help before you use it. Flags change between versions.

cmux also has more commands than the ones above: `respawn-pane`, `swap-pane`, `find-window`, `pipe-pane`, `notify`, `set-progress`.
