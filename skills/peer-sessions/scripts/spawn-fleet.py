#!/usr/bin/env python3
"""Launch named Claude Code sessions in cmux and verify their live sockets."""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time

from peer_registry import live_records, normalized_name, record_identity, socket_live


UUID = re.compile(r"^[0-9A-Fa-f]{8}(-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12}$")


def cmux(*args):
    """Run cmux and ask for UUIDs beside refs. Refs renumber; UUIDs do not."""
    result = subprocess.run(
        ["cmux", "--id-format", "both", *args], capture_output=True, text=True
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0 or output.startswith("Error"):
        raise RuntimeError(f"cmux {' '.join(args)}\n  → {output}")
    return output


def id_from(output, kind):
    """Take the durable id for `kind` out of `OK surface:22 (UUID) workspace:10 (UUID)`."""
    tokens = output.replace("(", " ").replace(")", " ").split()
    for index, token in enumerate(tokens):
        if not token.startswith(f"{kind}:"):
            continue
        if index + 1 < len(tokens) and UUID.match(tokens[index + 1]):
            return tokens[index + 1]
        return token
    raise RuntimeError(f"no {kind} id in cmux output: {output!r}")


def workspace_uuid(ref):
    """`new-workspace` prints a ref only. Refs renumber, so trade it for a UUID."""
    if UUID.match(ref):
        return ref
    # `list-workspaces` covers the caller's window only, so read every window.
    match = re.search(
        rf"workspace {re.escape(ref)}(?![0-9])\s+([0-9A-Fa-f-]{{36}})",
        cmux("tree", "--all"),
    )
    return match.group(1) if match else ref


def caller_context():
    """Return the window, workspace, and surface UUIDs that this script runs in."""
    try:
        payload = json.loads(cmux("identify"))
    except (RuntimeError, ValueError):
        return {}
    caller = payload.get("caller") or {}
    return {
        "window": caller.get("window_id"),
        "workspace": caller.get("workspace_id"),
        "surface": caller.get("surface_id"),
    }


def parse_specs(raw):
    specs = []
    for item in raw:
        if ":" not in item:
            sys.exit(f"error: '{item}' is not NAME:DIR")
        name, _, directory = item.partition(":")
        name = name.strip()
        directory = os.path.abspath(os.path.expanduser(directory.strip()))
        if not name:
            sys.exit(f"error: '{item}' has an empty name")
        os.makedirs(directory, exist_ok=True)
        specs.append((name, directory))
    names = [name for name, _ in specs]
    duplicates = {name for name in names if names.count(name) > 1}
    if duplicates:
        sys.exit(f"error: duplicate session names: {', '.join(sorted(duplicates))}")
    return specs


def new_matching_records(before, wanted):
    return [
        record
        for record in live_records()
        if record_identity(record) not in before and normalized_name(record) in wanted
    ]


def ready_by_name(records):
    ready = {}
    for record in records:
        socket_path = record.get("messagingSocketPath")
        if not socket_live(socket_path):
            continue
        name = normalized_name(record)
        previous = ready.get(name)
        if previous is None or (record.get("startedAt") or 0) > (
            previous.get("startedAt") or 0
        ):
            ready[name] = record
    return ready


def print_cleanup(records, layout):
    pids = sorted(
        {record.get("pid") for record in records if isinstance(record.get("pid"), int)}
    )
    print("\nTeardown is off by default: hand this block to the user, and run it")
    print("only when they ask. Kill the processes before closing their UI:")
    if pids:
        print("  kill " + " ".join(str(pid) for pid in pids))
    else:
        print("  No launched PID registered yet; inspect the panes before closing them.")
    if layout["placement"] == "window":
        print(f"  cmux close-window --window {layout['window']}")
        print("  # close-window can return OK and leave the window open.")
        print("  # If it stays in cmux list-windows, ask the user for a Cmd+W.")
    elif layout["placement"] == "workspace":
        for workspace in layout["workspaces"]:
            print(f"  cmux close-workspace --workspace {workspace}")
    else:
        # Split placement lives in the caller's own workspace. Close the new
        # panes only. Never close this workspace or this window.
        for surface in layout["surfaces"]:
            print(
                f"  cmux close-surface --workspace {layout['workspace']} "
                f"--surface {surface}"
            )
    print("  python3 ~/.claude/skills/peer-sessions/scripts/peer-addr.py")


def start_session(workspace, surface, directory, command):
    """Type a launch command into a shell that cmux already opened."""
    full = f"cd {shlex.quote(directory)} && {command}"
    cmux("send", "--workspace", workspace, "--surface", surface, full)
    cmux("send-key", "--workspace", workspace, "--surface", surface, "Enter")


def build_splits(specs, launch_cmd, caller, direction, focus):
    """Put each session in a new pane beside the caller's pane."""
    workspace = caller.get("workspace")
    anchor = caller.get("surface")
    if not workspace or not anchor:
        sys.exit(
            "error: --placement split needs a cmux terminal. "
            "Run it inside cmux, or use --placement workspace|window."
        )
    if len(specs) > 3 and direction in ("right", "left"):
        print(
            f"note: {len(specs)} side panes get narrow. "
            "Use --direction down, or --placement workspace.",
            file=sys.stderr,
        )
    surfaces = []
    for name, directory in specs:
        output = cmux(
            "new-split",
            direction,
            "--workspace",
            workspace,
            "--surface",
            anchor,
            "--focus",
            focus,
        )
        surface = id_from(output, "surface")
        surfaces.append(surface)
        start_session(workspace, surface, directory, launch_cmd(name))
        anchor = surface  # chain, so the panes line up in spec order
    return {
        "placement": "split",
        "window": caller.get("window"),
        "workspace": workspace,
        "workspaces": [],
        "surfaces": surfaces,
    }


def build_workspaces(specs, launch_cmd, window, prefix, per_workspace, direction, focus):
    """Put each group of sessions in its own workspace."""
    workspaces = []
    surfaces = []
    groups = [
        specs[index : index + per_workspace]
        for index in range(0, len(specs), per_workspace)
    ]
    for group_index, group in enumerate(groups, 1):
        first_name, first_dir = group[0]
        cmux_args = [
            "new-workspace",
            "--name",
            f"{prefix}-{group_index}",
            "--cwd",
            first_dir,
            "--command",
            launch_cmd(first_name),
        ]
        if window:
            cmux_args += ["--window", window]
        cmux_args += ["--focus", focus if group_index == 1 else "false"]
        workspace = workspace_uuid(id_from(cmux(*cmux_args), "workspace"))
        workspaces.append(workspace)

        for name, directory in group[1:]:
            output = cmux(
                "new-split", direction, "--workspace", workspace, "--focus", "false"
            )
            surface = id_from(output, "surface")
            surfaces.append(surface)
            start_session(workspace, surface, directory, launch_cmd(name))
    return {"window": window, "workspaces": workspaces, "surfaces": surfaces}


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("specs", nargs="+", metavar="NAME:DIR")
    parser.add_argument(
        "--placement",
        choices=("split", "workspace", "window"),
        default="workspace",
        help="split: panes beside this one. workspace: new workspaces in this "
        "window. window: a new window (default: workspace)",
    )
    parser.add_argument(
        "--window", action="store_true", help="alias for --placement window"
    )
    parser.add_argument(
        "--direction",
        choices=("right", "left", "up", "down"),
        default="right",
        help="direction of each new pane (default: right)",
    )
    parser.add_argument(
        "--focus",
        choices=("true", "false"),
        help="move the UI to the fleet (default: false for split, true otherwise)",
    )
    parser.add_argument("--per-workspace", type=int, default=2, choices=(1, 2))
    parser.add_argument("--prefix", default="fleet")
    parser.add_argument("--model")
    parser.add_argument("--claude-arg", action="append", default=[])
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--permission-mode", default="auto")
    args = parser.parse_args()

    placement = "window" if args.window else args.placement
    focus = args.focus or ("false" if placement == "split" else "true")

    specs = parse_specs(args.specs)
    before = {record_identity(record) for record in live_records()}
    wanted = {name for name, _ in specs}

    extra = list(args.claude_arg)
    if args.model:
        extra += ["--model", args.model]

    def launch_cmd(name):
        return " ".join(
            shlex.quote(value)
            for value in [
                "claude",
                "--name",
                name,
                "--permission-mode",
                args.permission_mode,
                *extra,
            ]
        )

    caller = caller_context()

    if placement == "split":
        layout = build_splits(specs, launch_cmd, caller, args.direction, focus)
        print(f"workspace {layout['workspace']} (this one)")
        print(f"panes {', '.join(layout['surfaces'])}")
    else:
        if placement == "window":
            window = cmux("new-window").split()[-1]
            print(f"window {window} (new)")
        else:
            window = caller.get("window")
            print(f"window {window or '(focused)'} (this one)")
        layout = build_workspaces(
            specs,
            launch_cmd,
            window,
            args.prefix,
            args.per_workspace,
            args.direction,
            focus,
        )
        layout["placement"] = placement
        print(f"workspaces {', '.join(layout['workspaces'])}")

    started = time.time()
    records = []
    ready = {}
    while time.time() - started < args.timeout:
        records = new_matching_records(before, wanted)
        ready = ready_by_name(records)
        if len(ready) == len(wanted):
            break
        time.sleep(2)

    elapsed = int(time.time() - started)
    records = new_matching_records(before, wanted)
    ready = ready_by_name(records)

    if focus == "true" and layout["workspaces"]:
        # A new window opens on its own default workspace, so `--focus true` on
        # the first workspace does not stick. Select it again here, after every
        # session has booted. An earlier switch races the launch command that
        # cmux types into the new shell, and scrambles it.
        cmux("select-workspace", "--workspace", layout["workspaces"][0])
    for name, _ in specs:
        if name in ready:
            record = ready[name]
            print(
                f"+ {name:<24} pid {record['pid']:<7} "
                f"uds:{record['messagingSocketPath']}"
            )
        else:
            print(f"- {name:<24} did not register a live socket in {args.timeout}s")

    missing = [name for name, _ in specs if name not in ready]
    if missing:
        print(
            f"\n{len(ready)}/{len(wanted)} ready after {elapsed}s. "
            "Check the pane — a stalled permission prompt never registers.",
            file=sys.stderr,
        )
        print_cleanup(records, layout)
        return 1

    print(f"\n{len(ready)} ready in {elapsed}s.")
    print("Send with a uds: address above, or a freshly resolved ListAgents name/ref.")
    print_cleanup(records, layout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
