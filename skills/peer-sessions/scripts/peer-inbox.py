#!/usr/bin/env python3
"""Extract verified peer-origin messages from a Claude session transcript."""

import argparse
import json
import sys
import time

from peer_registry import find_record, find_transcript


def peer_messages(path, sender=None, msg_id=None):
    messages = []
    try:
        handle = open(path)
    except OSError as error:
        raise RuntimeError(f"cannot read transcript {path}: {error}") from error
    with handle:
        for line in handle:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            origin = event.get("origin") or {}
            if event.get("type") != "user" or origin.get("kind") != "peer":
                continue
            if not isinstance(origin.get("verifiedPeerPid"), int):
                continue
            if sender is not None and sender not in (
                origin.get("name"),
                origin.get("from"),
            ):
                continue
            if msg_id is not None and origin.get("msg_id") != msg_id:
                continue
            body = origin.get("body")
            if not isinstance(body, str):
                continue
            messages.append(
                {
                    "name": origin.get("name"),
                    "from": origin.get("from"),
                    "verifiedPeerPid": origin.get("verifiedPeerPid"),
                    "msgId": origin.get("msg_id"),
                    "timestamp": event.get("timestamp"),
                    "body": body,
                }
            )
    return messages


def main():
    parser = argparse.ArgumentParser()
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--pid", type=int, help="registry PID of the receiving session")
    target.add_argument("--session-id", help="receiving session ID")
    parser.add_argument("--from", dest="sender", help="exact peer name or uds: address")
    parser.add_argument("--msg-id", help="exact inbound peer message ID")
    parser.add_argument(
        "--all", action="store_true", help="print all matches, not only latest"
    )
    parser.add_argument("--body-only", action="store_true", help="print only message bodies")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--wait", type=float, default=0, metavar="SECONDS")
    args = parser.parse_args()

    session_id = args.session_id
    if args.pid is not None:
        record = find_record(pid=args.pid)
        if record is None:
            parser.error(f"no registry record for pid {args.pid}; use --session-id after exit")
        session_id = record.get("sessionId")
    if not session_id:
        parser.error("target registry record has no sessionId")

    deadline = time.monotonic() + max(args.wait, 0)
    transcript = None
    matches = []
    while True:
        transcript = find_transcript(session_id)
        if transcript:
            matches = peer_messages(transcript, args.sender, args.msg_id)
        if matches or time.monotonic() >= deadline:
            break
        time.sleep(0.5)

    if not matches:
        print("No verified peer messages matched.", file=sys.stderr)
        return 1
    selected = matches if args.all else matches[-1:]

    if args.json:
        print(
            json.dumps(
                {"sessionId": session_id, "transcript": transcript, "messages": selected},
                indent=2,
            )
        )
        return 0

    for index, message in enumerate(selected):
        if index:
            print()
        if not args.body_only:
            print(
                f"from {message['name'] or message['from']} "
                f"pid {message['verifiedPeerPid']} msg_id {message['msgId']} "
                f"at {message['timestamp']}"
            )
        print(message["body"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
