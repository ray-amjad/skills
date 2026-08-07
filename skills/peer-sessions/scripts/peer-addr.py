#!/usr/bin/env python3
"""Show peer-messaging addresses for Claude Code sessions on this machine.

  peer-addr.py         list live sessions and whether each is addressable
  peer-addr.py --me    print this session's own uds: address, for replies

Sessions register at ~/.claude/sessions/<pid>.json. A session is addressable
only if it published a messaging socket, which requires Claude Code 2.1.224 or
newer — an older session is alive and healthy but invisible to SendMessage.
"""

import glob
import json
import os
import socket
import subprocess
import sys

SESSIONS = os.path.expanduser("~/.claude/sessions")
MIN_VERSION = (2, 1, 224)
NAME_MAX = 40


def parse_version(v):
    try:
        return tuple(int(p) for p in str(v).split(".")[:3])
    except (TypeError, ValueError):
        return (0, 0, 0)


def pid_alive(pid):
    return subprocess.run(["ps", "-p", str(pid)], capture_output=True).returncode == 0


def socket_live(path, timeout=0.25):
    """Connecting is the only honest liveness check — the file can outlive the process."""
    if not path or not os.path.exists(path):
        return False
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(path)
        return True
    except OSError:
        return False
    finally:
        s.close()


def load_records():
    out = []
    for f in sorted(glob.glob(os.path.join(SESSIONS, "*.json"))):
        try:
            with open(f) as fh:
                out.append(json.load(fh))
        except (OSError, ValueError):
            continue
    return out


def me():
    own_sock = os.environ.get("CLAUDE_CODE_MESSAGING_SOCKET")
    if not own_sock:
        print("No CLAUDE_CODE_MESSAGING_SOCKET in this environment.")
        print("Either this build predates 2.1.224 or cross-session messaging is off.")
        return 1

    print(f"uds:{own_sock}")
    for rec in load_records():
        if rec.get("messagingSocketPath") == own_sock:
            sid = rec.get("sessionId")
            if sid:
                # Needed for --resume/--fork-session, not for messaging.
                print(f"session-id: {sid}")
            return 0
    print("(no registry record found for this socket)")
    return 0


def listing():
    own_sock = os.environ.get("CLAUDE_CODE_MESSAGING_SOCKET")
    rows = []
    for rec in load_records():
        pid = rec.get("pid")
        if not isinstance(pid, int) or not pid_alive(pid):
            continue
        sock = rec.get("messagingSocketPath") or ""
        version = rec.get("version", "?")
        if not sock:
            state = "unreachable"
            if parse_version(version) < MIN_VERSION:
                why = "no socket — build predates 2.1.224 (claude --resume to fix)"
            else:
                why = "no socket — messaging gate off, bind failed, or a thin/bare session"
        elif sock == own_sock:
            why = "this session"
            state = "self"
        elif socket_live(sock):
            why = f"uds:{sock}"
            state = "reachable"
        else:
            why = "socket present but not answering (stale — peer may have crashed)"
            state = "unreachable"
        # Names come from --name or are derived, so they can be a whole sentence.
        name = " ".join((rec.get("name") or "(unnamed)").split())
        if len(name) > NAME_MAX:
            name = name[: NAME_MAX - 1] + "…"
        rows.append((state, name, pid, version, why))

    if not rows:
        print("No live Claude Code sessions registered on this machine.")
        return 0

    rows.sort(key=lambda r: ({"reachable": 0, "self": 1, "unreachable": 2}[r[0]], r[1]))
    width = max(len(r[1]) for r in rows)
    marks = {"reachable": "+", "self": ".", "unreachable": "-"}
    for state, name, pid, version, why in rows:
        print(f"{marks[state]} {name:<{width}}  pid {pid:<7} v{version:<9} {why}")

    n = sum(1 for r in rows if r[0] == "reachable")
    print(f"\n{n} reachable peer{'' if n == 1 else 's'}. "
          "Send with the bare name from ListAgents, or the uds: address shown above.")
    return 0


if __name__ == "__main__":
    sys.exit(me() if "--me" in sys.argv[1:] else listing())
