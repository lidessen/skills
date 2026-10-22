"""Offline checks for the local delegation event log."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import uuid


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "log.py"


def run_log(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


class DelegationLogTests(unittest.TestCase):
    def test_pending_session_and_later_confirmed_update(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "state" / "delegations.jsonl"
            common = (
                "--log", str(log), "--project", "skills", "--description", "Review routing",
                "--runner", "pi", "--herdr-agent", "reviewer", "--herdr-pane", "pane-7",
            )
            first = run_log(*common, "--status", "started")
            self.assertEqual(first.returncode, 0, first.stderr)
            task_ref = first.stdout.strip()
            self.assertEqual(str(uuid.UUID(task_ref)), task_ref)
            second = run_log(
                *common, "--status", "running", "--task-ref", task_ref,
                "--runner-session-id", "runtime-session-9",
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(second.stdout.strip(), task_ref)

            entries = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(entries), 2)
            self.assertEqual([entry["task_ref"] for entry in entries], [task_ref, task_ref])
            self.assertEqual([entry["runner_session_id"] for entry in entries], [None, "runtime-session-9"])
            self.assertEqual([entry["session_state"] for entry in entries], ["pending", "confirmed"])
            self.assertEqual(entries[0]["herdr_pane_id"], "pane-7")
            self.assertEqual(entries[0]["herdr_agent"], "reviewer")
            self.assertTrue(all(entry["at"].endswith("Z") for entry in entries))
            self.assertEqual(stat.S_IMODE(log.parent.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(log.stat().st_mode), 0o600)

    def test_concurrent_processes_append_complete_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "delegations.jsonl"

            def write(index: int) -> subprocess.CompletedProcess[str]:
                return run_log(
                    "--log", str(log), "--project", "skills", "--description", f"Task {index}",
                    "--runner", "pi", "--status", "started",
                )

            with ThreadPoolExecutor(max_workers=8) as executor:
                results = list(executor.map(write, range(24)))
            self.assertTrue(all(result.returncode == 0 for result in results), results)
            entries = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(entries), 24)
            self.assertEqual(len({entry["task_ref"] for entry in entries}), 24)
            self.assertEqual({entry["description"] for entry in entries}, {f"Task {i}" for i in range(24)})

    def test_relative_xdg_state_home_uses_home_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, HOME=directory, XDG_STATE_HOME="relative-state")
            result = run_log(
                "--project", "skills", "--description", "Path check", "--runner", "pi",
                "--status", "started", env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            log = Path(directory) / ".local" / "state" / "task-delegation" / "delegations.jsonl"
            self.assertTrue(log.is_file())
            self.assertEqual(len(log.read_text(encoding="utf-8").splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
