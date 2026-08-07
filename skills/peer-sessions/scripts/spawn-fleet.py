#!/usr/bin/env python3
"""Launch a fleet of Claude Code sessions in cmux and print their addresses.

  spawn-fleet.py NAME:DIR [NAME:DIR ...] [--window] [--per-workspace N] [options]

Each NAME:DIR becomes a session named NAME running in DIR. Sessions are packed
into workspaces (2 per workspace by default, side by side), and the script waits
until every one has published a messaging socket before printing.

Examples:
  spawn-fleet.py orbits:/tmp/lab/orbits planets:/tmp/lab/planets
  spawn-fleet.py --window a:/tmp/a b:/tmp/b c:/tmp/c d:/tmp/d
  spawn-fleet.py --model sonnet --claude-arg --effort=low w1:/tmp/w1 w2:/tmp/w2

Options:
  --window            put the fleet in a NEW cmux window (keeps it out of the
                      user's own tabs; close it later with close-window)
  --per-workspace N   sessions per workspace, 1 or 2 (default 2)
  --prefix NAME       workspace name prefix (default "fleet")
  --model M           passed to every session as --model M
  --claude-arg ARG    extra arg for every session; repeatable
  --timeout SECS      how long to wait for sockets (default 120)
  --permission-mode M default "auto" — see the skill on why bypass breaks messaging

Prints one line per ready session, then a SendMessage-able address list. Exits
non-zero if any session fails to come up, and says which.
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
import time

SESSIONS = os.path.expanduser("~/.claude/sessions")


def cmux(*args):
    """Run a cmux command, returning stdout. Raises with cmux's own message on failure."""
    r = subprocess.run(["cmux", *args], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if r.returncode != 0 or out.startswith("Error"):
        raise RuntimeError(f"cmux {' '.join(args)}\n  → {out}")
    return out


def ref_from(out, kind):
    """cmux prints things like 'OK surface:107 workspace:32' — pull out one ref."""
    for tok in out.split():
        if tok.startswith(f"{kind}:"):
            return tok
    raise RuntimeError(f"no {kind} ref in cmux output: {out!r}")


def live_sockets():
    """Map session name → socket path for every registered live session."""
    found = {}
    if not os.path.isdir(SESSIONS):
        return found
    for fn in os.listdir(SESSIONS):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(SESSIONS, fn)) as fh:
                rec = json.load(fh)
        except (OSError, ValueError):
            continue
        sock = rec.get("messagingSocketPath")
        name = rec.get("name")
        if sock and name and os.path.exists(sock):
            found[name] = sock
    return found


def parse_specs(raw):
    specs = []
    for item in raw:
        if ":" not in item:
            sys.exit(f"error: '{item}' is not NAME:DIR")
        name, _, d = item.partition(":")
        name, d = name.strip(), os.path.abspath(os.path.expanduser(d.strip()))
        if not name:
            sys.exit(f"error: '{item}' has an empty name")
        os.makedirs(d, exist_ok=True)
        specs.append((name, d))
    names = [n for n, _ in specs]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        # Duplicate names make ListAgents ambiguous and sends need disambiguating.
        sys.exit(f"error: duplicate session names: {', '.join(sorted(dupes))}")
    return specs


def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("specs", nargs="+", metavar="NAME:DIR")
    p.add_argument("--window", action="store_true")
    p.add_argument("--per-workspace", type=int, default=2, choices=(1, 2))
    p.add_argument("--prefix", default="fleet")
    p.add_argument("--model")
    p.add_argument("--claude-arg", action="append", default=[])
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--permission-mode", default="auto")
    a = p.parse_args()

    specs = parse_specs(a.specs)
    before = set(live_sockets())

    extra = list(a.claude_arg)
    if a.model:
        extra += ["--model", a.model]

    def launch_cmd(name):
        return " ".join(
            shlex.quote(x) for x in
            ["claude", "--name", name, "--permission-mode", a.permission_mode, *extra]
        )

    window = None
    if a.window:
        window = cmux("new-window").split()[-1]
        print(f"window {window}")

    workspaces = []
    groups = [specs[i:i + a.per_workspace] for i in range(0, len(specs), a.per_workspace)]

    for gi, group in enumerate(groups, 1):
        first_name, first_dir = group[0]
        args = ["new-workspace", "--name", f"{a.prefix}-{gi}", "--cwd", first_dir,
                "--command", launch_cmd(first_name)]
        if window:
            args += ["--window", window]
        if gi == 1:
            args += ["--focus", "true"]
        ws = ref_from(cmux(*args), "workspace")
        workspaces.append(ws)

        # The rest of the group go in splits. A split is a bare shell, so the
        # session is started by typing into it.
        for name, d in group[1:]:
            surface = ref_from(cmux("new-split", "right", "--workspace", ws), "surface")
            cmd = f"cd {shlex.quote(d)} && {launch_cmd(name)}"
            cmux("send", "--workspace", ws, "--surface", surface, cmd)
            cmux("send-key", "--workspace", ws, "--surface", surface, "Enter")

    print(f"workspaces {', '.join(workspaces)}")

    wanted = [n for n, _ in specs]
    start = time.time()
    ready = {}
    while time.time() - start < a.timeout:
        # Only count names that appeared after we started, so a pre-existing
        # session with the same name can't be mistaken for one of ours.
        current = live_sockets()
        ready = {n: s for n, s in current.items() if n in wanted and n not in before}
        if len(ready) == len(wanted):
            break
        time.sleep(2)

    elapsed = int(time.time() - start)
    for name, _ in specs:
        if name in ready:
            print(f"+ {name:<24} {'uds:' + ready[name]}")
        else:
            print(f"- {name:<24} did not register a socket in {a.timeout}s")

    missing = [n for n, _ in specs if n not in ready]
    if missing:
        print(f"\n{len(ready)}/{len(wanted)} ready after {elapsed}s. "
              "Check the pane — a session that stalls on a permission prompt "
              "never registers.", file=sys.stderr)
        return 1

    print(f"\n{len(ready)} ready in {elapsed}s.")
    print("Send with the bare name (expect one [ref] bounce first), or these addresses.")
    if window:
        print(f"Tear down with: cmux close-window --window {window}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
