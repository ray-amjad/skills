#!/usr/bin/env python3
"""Shared registry and liveness helpers for peer-session scripts."""

import glob
import json
import os
import socket


SESSIONS = os.environ.get(
    "CLAUDE_SESSIONS_DIR", os.path.expanduser("~/.claude/sessions")
)
PROJECTS = os.environ.get(
    "CLAUDE_PROJECTS_DIR", os.path.expanduser("~/.claude/projects")
)


def parse_version(value):
    try:
        return tuple(int(part) for part in str(value).split(".")[:3])
    except (TypeError, ValueError):
        return (0, 0, 0)


def pid_alive(pid):
    """Check PID existence without spawning `ps` (which sandboxes often block)."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # The process exists, but this caller may not signal it.
        return True
    return True


def socket_status(path, timeout=0.25):
    """Return live, dead, missing, or denied for a Unix messaging socket."""
    if not path or not os.path.exists(path):
        return "missing"
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(timeout)
    try:
        client.connect(path)
        return "live"
    except PermissionError:
        # Sandboxed callers may see a valid socket but be forbidden to connect.
        return "denied"
    except OSError:
        return "dead"
    finally:
        client.close()


def socket_live(path, timeout=0.25):
    return socket_status(path, timeout) == "live"


def load_records(sessions_dir=None):
    records = []
    root = sessions_dir or SESSIONS
    for path in sorted(glob.glob(os.path.join(root, "*.json"))):
        try:
            with open(path) as handle:
                record = json.load(handle)
        except (OSError, ValueError):
            continue
        record["_registryPath"] = path
        records.append(record)
    return records


def normalized_name(record):
    return " ".join((record.get("name") or "(unnamed)").split())


def record_identity(record):
    """Identity for distinguishing a newly launched process from old names."""
    return (record.get("pid"), record.get("sessionId"), record.get("procStart"))


def live_records(require_socket=False, sessions_dir=None):
    records = []
    for record in load_records(sessions_dir):
        if not pid_alive(record.get("pid")):
            continue
        if require_socket and not socket_live(record.get("messagingSocketPath")):
            continue
        records.append(record)
    return records


def find_record(pid=None, session_id=None, sessions_dir=None):
    for record in load_records(sessions_dir):
        if pid is not None and record.get("pid") != pid:
            continue
        if session_id is not None and record.get("sessionId") != session_id:
            continue
        return record
    return None


def find_transcript(session_id, projects_dir=None):
    root = projects_dir or PROJECTS
    pattern = os.path.join(root, "**", f"{session_id}.jsonl")
    candidates = [
        path
        for path in glob.glob(pattern, recursive=True)
        if "subagents" not in os.path.normpath(path).split(os.sep)
    ]
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)
