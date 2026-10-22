#!/usr/bin/env python3
"""Append one compact delegation event to a user-level JSONL log."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import stat
import sys
import uuid


def default_log_path() -> Path:
    configured = os.environ.get("XDG_STATE_HOME", "")
    base = Path(configured) if configured and Path(configured).is_absolute() else Path.home() / ".local" / "state"
    return base / "task-delegation" / "delegations.jsonl"


def short_text(parser: argparse.ArgumentParser, name: str, value: str, limit: int = 240) -> str:
    value = value.strip()
    if not value or len(value) > limit or any(ord(char) < 32 for char in value):
        parser.error(f"{name} must be one nonempty line of at most {limit} characters")
    return value


def append_event(path: Path, event: dict) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError("log path is not a regular file")
        line = (json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        try:
            remaining = memoryview(line)
            while remaining:
                written = os.write(descriptor, remaining)
                if written == 0:
                    raise OSError("log append made no progress")
                remaining = remaining[written:]
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="Short project label, not a path")
    parser.add_argument("--description", required=True, help="Short, non-sensitive task summary")
    parser.add_argument("--runner", required=True, help="Actual runtime name")
    parser.add_argument("--status", required=True, help="Short observed task status")
    parser.add_argument("--task-ref", help="UUID printed by an earlier event for this task")
    parser.add_argument("--herdr-agent", help="Herdr agent name when known")
    parser.add_argument("--herdr-pane", help="Herdr pane ID when known")
    parser.add_argument("--runner-session-id", help="Session ID returned by the target runtime")
    parser.add_argument("--log", type=Path, help="Alternate absolute log path for isolated tests")
    args = parser.parse_args(argv)

    project = short_text(parser, "project", args.project, 80)
    if "/" in project or "\\" in project:
        parser.error("project must be a short label, not a path")
    description = short_text(parser, "description", args.description)
    runner = short_text(parser, "runner", args.runner, 80)
    status = short_text(parser, "status", args.status, 80)
    herdr_agent = short_text(parser, "herdr-agent", args.herdr_agent, 160) if args.herdr_agent else None
    herdr_pane = short_text(parser, "herdr-pane", args.herdr_pane, 160) if args.herdr_pane else None
    runner_session = (
        short_text(parser, "runner-session-id", args.runner_session_id, 240)
        if args.runner_session_id else None
    )
    if args.task_ref:
        try:
            task_ref = str(uuid.UUID(args.task_ref))
        except ValueError:
            parser.error("task-ref must be a UUID")
    else:
        task_ref = str(uuid.uuid4())

    path = args.log if args.log is not None else default_log_path()
    if not path.is_absolute():
        parser.error("log path must be absolute")
    event = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "task_ref": task_ref,
        "project": project,
        "description": description,
        "runner": runner,
        "status": status,
        "herdr_agent": herdr_agent,
        "herdr_pane_id": herdr_pane,
        "runner_session_id": runner_session,
        "session_state": "confirmed" if runner_session else "pending",
    }
    try:
        append_event(path, event)
    except OSError as error:
        print(f"Cannot append delegation log: {error}", file=sys.stderr)
        return 1
    print(task_ref)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
