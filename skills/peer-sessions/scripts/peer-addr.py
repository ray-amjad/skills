#!/usr/bin/env python3
"""List live Claude Code sessions and verified peer-messaging addresses."""

import argparse
import json
import os
import sys

from peer_registry import (
    load_records,
    normalized_name,
    parse_version,
    pid_alive,
    socket_status,
)


MIN_VERSION = (2, 1, 224)
NAME_MAX = 40


def row_for(record, own_sock):
    pid = record.get("pid")
    sock = record.get("messagingSocketPath") or ""
    version = record.get("version", "?")
    if not sock:
        state = "unreachable"
        if parse_version(version) < MIN_VERSION:
            reason = "no socket — build predates 2.1.224 (claude --resume to fix)"
        else:
            reason = "no socket — messaging gate off, bind failed, or a thin/bare session"
    elif sock == own_sock:
        state = "self"
        reason = "this session"
    else:
        status = socket_status(sock)
        if status == "live":
            state = "reachable"
            reason = f"uds:{sock}"
        elif status == "denied":
            state = "unverified"
            reason = "socket check denied by sandbox — rerun with process/socket access"
        else:
            state = "unreachable"
            reason = "socket present but not answering (stale — peer may have crashed)"

    return {
        "state": state,
        "name": normalized_name(record),
        "pid": pid,
        "version": version,
        "address": f"uds:{sock}" if state in ("reachable", "self") else None,
        "socketPath": sock or None,
        "reason": reason,
        "sessionId": record.get("sessionId"),
        "cwd": record.get("cwd"),
        "status": record.get("status"),
        "startedAt": record.get("startedAt"),
    }


def me(as_json=False):
    own_sock = os.environ.get("CLAUDE_CODE_MESSAGING_SOCKET")
    if not own_sock:
        message = (
            "No CLAUDE_CODE_MESSAGING_SOCKET in this environment. "
            "Either this build predates 2.1.224 or cross-session messaging is off."
        )
        if as_json:
            print(json.dumps({"error": message}))
        else:
            print(message)
        return 1

    record = next(
        (r for r in load_records() if r.get("messagingSocketPath") == own_sock), None
    )
    payload = {
        "address": f"uds:{own_sock}",
        "sessionId": record.get("sessionId") if record else None,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(payload["address"])
        if payload["sessionId"]:
            print(f"session-id: {payload['sessionId']}")
        else:
            print("(no registry record found for this socket)")
    return 0


def listing(name_filter=None, pid_filter=None, details=False, as_json=False):
    own_sock = os.environ.get("CLAUDE_CODE_MESSAGING_SOCKET")
    rows = []
    for record in load_records():
        pid = record.get("pid")
        if not pid_alive(pid):
            continue
        name = normalized_name(record)
        if name_filter is not None and name != name_filter:
            continue
        if pid_filter is not None and pid != pid_filter:
            continue
        rows.append(row_for(record, own_sock))

    rows.sort(
        key=lambda row: (
            {"reachable": 0, "self": 1, "unverified": 2, "unreachable": 3}[
                row["state"]
            ],
            row["name"],
            row["pid"],
        )
    )
    reachable = sum(1 for row in rows if row["state"] == "reachable")

    if as_json:
        print(json.dumps({"sessions": rows, "reachablePeers": reachable}, indent=2))
        return 0 if rows or (name_filter is None and pid_filter is None) else 1

    if not rows:
        if name_filter is not None or pid_filter is not None:
            print("No live Claude Code sessions matched the requested filters.")
            return 1
        print("No live Claude Code sessions registered on this machine.")
        return 0

    width = min(NAME_MAX, max(len(row["name"]) for row in rows))
    marks = {"reachable": "+", "self": ".", "unverified": "?", "unreachable": "-"}
    for row in rows:
        name = row["name"]
        if len(name) > NAME_MAX:
            name = name[: NAME_MAX - 1] + "…"
        print(
            f"{marks[row['state']]} {name:<{width}}  pid {row['pid']:<7} "
            f"v{row['version']:<9} {row['reason']}"
        )
        if details:
            print(
                f"    session {row['sessionId'] or '?'}  status {row['status'] or '?'}  "
                f"cwd {row['cwd'] or '?'}"
            )

    print(
        f"\n{reachable} reachable peer{'' if reachable == 1 else 's'}. "
        "Send with the bare name from ListAgents, or the uds: address shown above."
    )
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--me", action="store_true", help="show this session's address")
    parser.add_argument("--name", help="show sessions with this exact normalized name")
    parser.add_argument("--pid", type=int, help="show only this process ID")
    parser.add_argument("--details", action="store_true", help="include cwd, status and session ID")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    if args.me and (args.name is not None or args.pid is not None or args.details):
        parser.error("--me cannot be combined with --name, --pid, or --details")
    if args.me:
        return me(args.json)
    return listing(args.name, args.pid, args.details, args.json)


if __name__ == "__main__":
    sys.exit(main())
