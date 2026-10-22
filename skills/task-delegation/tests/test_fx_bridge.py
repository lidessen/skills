"""Offline behavior checks for the Fx/Herdr bridge; no real runner is invoked."""

from __future__ import annotations

import json
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import textwrap
import unittest


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "fx_bridge.py"


HERDR_STUB = r"""
import json
import os
import sys

with open(os.environ["FAKE_HERDR_LOG"], "a", encoding="utf-8") as stream:
    stream.write(json.dumps(sys.argv[1:]) + "\n")
if os.environ.get("FAKE_HERDR_FAIL") == "1":
    sys.exit(7)
print("{}")
"""


FX_STUB = r"""
import json
import os
import sys
import time

path = os.environ["FAKE_FX_LOG"]
with open(path, "a+", encoding="utf-8") as stream:
    stream.seek(0)
    number = len(stream.readlines()) + 1
    stream.write(json.dumps({
        "argv": sys.argv[1:],
        "provider": os.environ.get("FX_PROVIDER"),
        "model_env": os.environ.get("FX_MODEL"),
        "auto_upgrade": os.environ.get("FX_AUTO_UPGRADE"),
        "home": os.environ.get("HOME"),
    }) + "\n")

mode = os.environ.get("FAKE_FX_MODE", "success")
if mode == "sleep":
    time.sleep(6)
if mode == "error":
    print(json.dumps({
        "exit_code": 2, "final_output": "", "session_id": "fx-session-7",
        "model": "provider/example-model",
    }))
    sys.exit(3)

args = sys.argv[1:]
session_id = "fx-session-7"
if mode == "mismatch" and "--resume-id" in args:
    session_id = "fx-session-unexpected"
if mode == "missing":
    session_id = None
print(json.dumps({
    "exit_code": 0,
    "final_output": "OK-" + str(number),
    "session_id": session_id,
    "model": args[args.index("--model") + 1],
    "tool_calls": [],
}))
"""


def option(args: list[str], name: str) -> str:
    return args[args.index(name) + 1]


def read_jsonl(path: Path) -> list[dict | list]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


class FxBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.settings = self.home / ".fx" / "settings.json"
        self.settings.parent.mkdir()
        self.settings.write_text(json.dumps({
            "provider": "magpie",
            "models": {"magpie": "provider/example-model"},
            "providers": {"magpie": {
                "protocol": "openai-chat-completions",
                "base_url": "http://127.0.0.1:9/v1",
                "auth": {"type": "none"},
            }},
        }), encoding="utf-8")
        self.state_home = self.root / "state"
        self.state_home.mkdir()
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()
        self.herdr_log = self.root / "herdr.jsonl"
        self.fx_log = self.root / "fx.jsonl"
        self.herdr = self.write_stub("fake-herdr", HERDR_STUB)
        self.fx = self.write_stub("fake-fx", FX_STUB)
        self.entry = self.bin_dir / "task-delegation-fx-bridge"
        self.entry.symlink_to(SCRIPT)
        self.socket = self.root / "fake-herdr.sock"
        self.socket.touch()
        self.env = {
            "HOME": str(self.home),
            "XDG_STATE_HOME": str(self.state_home),
            "PATH": str(self.bin_dir) + os.pathsep + os.defpath,
            "HERDR_ENV": "1",
            "HERDR_PANE_ID": "pane-test-17",
            "HERDR_BIN_PATH": str(self.herdr),
            "HERDR_SOCKET_PATH": str(self.socket),
            "FAKE_HERDR_LOG": str(self.herdr_log),
            "FAKE_FX_LOG": str(self.fx_log),
        }

    def write_stub(self, name: str, body: str) -> Path:
        path = self.bin_dir / name
        path.write_text("#!" + sys.executable + "\n" + textwrap.dedent(body), encoding="utf-8")
        path.chmod(0o700)
        return path

    def command(self, *args: str, input_text: str = "", extra_env: dict[str, str] | None = None,
                timeout: float = 15) -> subprocess.CompletedProcess[str]:
        env = {**self.env, **(extra_env or {})}
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args], cwd=self.root,
                              env=env, input=input_text, capture_output=True, text=True,
                              timeout=timeout, check=False)

    def start_args(self, *, turn_timeout: str = "8") -> tuple[str, ...]:
        return ("start", "--project", "Meowland", "--description", "Synthetic bridge check",
                "--provider", "magpie", "--model", "provider/example-model",
                "--fx-home", str(self.home), "--fx-bin", str(self.fx),
                "--no-additional-dirs", "--turn-timeout", turn_timeout)

    def state(self) -> tuple[Path, dict]:
        root = self.state_home / "task-delegation" / "fx-bridge"
        directories = [item for item in root.iterdir() if item.is_dir()]
        self.assertEqual(len(directories), 1)
        directory = directories[0]
        return directory, json.loads((directory / "state.json").read_text(encoding="utf-8"))

    def test_start_then_resume_uses_real_fx_session_and_monotonic_reports(self) -> None:
        private_prompt = "Canary_NonSecret_Prompt_Do_Not_Log"
        first = self.command(*self.start_args(), input_text=private_prompt + "\n/exit\n")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("FX_BRIDGE_READY", first.stdout)
        self.assertIn("FX_BRIDGE_RESULT", first.stdout)
        directory, state = self.state()
        task_ref = state["task_ref"]
        self.assertEqual(state["session_id"], "fx-session-7")
        self.assertEqual(state["turn_status"], "completed")
        self.assertEqual(state["bridge_state"], "stopped")
        first_receipt = json.loads((directory / "turn-1.json").read_text(encoding="utf-8"))
        self.assertEqual(first_receipt["status"], "completed")
        self.assertEqual(first_receipt["fx_receipt"]["final_output"], "OK-1")
        self.assertEqual((first_receipt["process_exit_code"], first_receipt["fx_exit_code"]), (0, 0))

        inspected = self.command("inspect", "--task-ref", task_ref)
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        snapshot = json.loads(inspected.stdout)
        self.assertEqual(snapshot["session_id"], "fx-session-7")
        self.assertEqual(snapshot["last_result"]["final_output"], "OK-1")

        second = self.command("resume", "--task-ref", task_ref, input_text="Continue simply\n/exit\n")
        self.assertEqual(second.returncode, 0, second.stderr)
        _, resumed_state = self.state()
        self.assertEqual(resumed_state["task_ref"], task_ref)
        self.assertEqual(resumed_state["turn"], 2)
        second_receipt = json.loads((directory / "turn-2.json").read_text(encoding="utf-8"))
        self.assertEqual(second_receipt["status"], "completed")
        self.assertEqual(second_receipt["fx_receipt"]["final_output"], "OK-2")

        fx_calls = read_jsonl(self.fx_log)
        self.assertEqual(len(fx_calls), 2)
        self.assertNotIn("--resume-id", fx_calls[0]["argv"])
        self.assertEqual(option(fx_calls[1]["argv"], "--resume-id"), "fx-session-7")
        self.assertTrue(all(option(call["argv"], "--model") == "provider/example-model"
                            and call["provider"] == "magpie"
                            and call["model_env"] == "provider/example-model"
                            and call["auto_upgrade"] == "0"
                            and Path(call["home"]).resolve() == self.home.resolve()
                            for call in fx_calls))

        events = read_jsonl(self.herdr_log)
        reports = [event for event in events if event[:2] == ["pane", "report-agent"]]
        releases = [event for event in events if event[:2] == ["pane", "release-agent"]]
        self.assertEqual(len(releases), 2)
        self.assertEqual([option(report, "--state") for report in reports],
                         ["idle", "working", "idle", "idle", "working", "idle"])
        self.assertTrue(all(option(event, "--source") == "fx-bridge:" + task_ref
                            for event in reports + releases))
        self.assertFalse(any(option(event, "--source").startswith("herdr:")
                             for event in reports + releases))
        sequences = [int(option(event, "--seq")) for event in events]
        self.assertEqual(sequences, sorted(set(sequences)))
        with_resume = [event for event in reports if "--agent-session-id" in event]
        self.assertTrue(with_resume)
        self.assertTrue(all(option(event, "--agent-session-id") == "fx-session-7"
                            and event[event.index("--") + 1:] ==
                            ["task-delegation-fx-bridge", "resume", "--task-ref", task_ref]
                            for event in with_resume))

        log_path = self.state_home / "task-delegation" / "delegations.jsonl"
        log_text = log_path.read_text(encoding="utf-8")
        self.assertNotIn(private_prompt, log_text)
        log_events = read_jsonl(log_path)
        self.assertEqual([event["status"] for event in log_events],
                         ["started", "completed", "started", "completed"])
        self.assertEqual({event["task_ref"] for event in log_events}, {task_ref})
        self.assertEqual(log_events[-1]["runner_session_id"], "fx-session-7")

    def test_fx_failure_keeps_receipt_and_never_reports_success(self) -> None:
        result = self.command(*self.start_args(), input_text="Fail synthetically\n/exit\n",
                              extra_env={"FAKE_FX_MODE": "error"})
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Fx turn 1 failed", result.stderr)
        directory, state = self.state()
        receipt = json.loads((directory / "turn-1.json").read_text(encoding="utf-8"))
        self.assertEqual(state["turn_status"], "failed")
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(receipt["failure"], "fx_nonzero_exit")
        self.assertEqual((receipt["process_exit_code"], receipt["fx_exit_code"]), (3, 2))
        statuses = [event["status"] for event in
                    read_jsonl(self.state_home / "task-delegation" / "delegations.jsonl")]
        self.assertEqual(statuses, ["started", "failed"])
        self.assertNotIn("completed", statuses)

    def test_timeout_keeps_failed_receipt_and_stops_fx_child(self) -> None:
        result = self.command(*self.start_args(turn_timeout="1"),
                              input_text="Wait synthetically\n/exit\n",
                              extra_env={"FAKE_FX_MODE": "sleep"}, timeout=10)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Fx turn 1 failed", result.stderr)
        directory, state = self.state()
        receipt = json.loads((directory / "turn-1.json").read_text(encoding="utf-8"))
        self.assertEqual(state["turn_status"], "failed")
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(receipt["failure"], "turn_timeout")
        self.assertTrue(receipt["timed_out"])
        statuses = [event["status"] for event in
                    read_jsonl(self.state_home / "task-delegation" / "delegations.jsonl")]
        self.assertEqual(statuses, ["started", "failed"])

    def test_missing_session_never_starts_a_second_conversation(self) -> None:
        result = self.command(*self.start_args(), input_text="First\nSecond\n/exit\n",
                              extra_env={"FAKE_FX_MODE": "missing"})
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Fx turn 1 failed", result.stderr)
        directory, state = self.state()
        receipt = json.loads((directory / "turn-1.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["failure"], "fx_session_missing")
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(state["turn"], 1)
        self.assertIsNone(state["session_id"])
        self.assertEqual(len(read_jsonl(self.fx_log)), 1)
        reports = [event for event in read_jsonl(self.herdr_log)
                   if event[:2] == ["pane", "report-agent"]]
        self.assertEqual([option(event, "--state") for event in reports],
                         ["idle", "working", "unknown"])
        self.assertEqual([event["status"] for event in
                          read_jsonl(self.state_home / "task-delegation" / "delegations.jsonl")],
                         ["started", "failed"])
        resumed = self.command("resume", "--task-ref", state["task_ref"],
                               input_text="Must not send\n/exit\n")
        self.assertEqual(resumed.returncode, 1)
        self.assertIn("no confirmed Fx session ID", resumed.stderr)
        self.assertEqual(len(read_jsonl(self.fx_log)), 1)

    def test_exit_without_prompt_only_releases_agent(self) -> None:
        result = self.command(*self.start_args(), input_text="/exit\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read_jsonl(self.fx_log), [])
        events = read_jsonl(self.herdr_log)
        self.assertEqual([event[:2] for event in events],
                         [["pane", "report-agent"], ["pane", "release-agent"]])
        self.assertEqual(read_jsonl(self.state_home / "task-delegation" / "delegations.jsonl"), [])

    def test_missing_bridge_entry_rejects_start_before_fx_request(self) -> None:
        self.entry.unlink()
        result = self.command(*self.start_args(), input_text="Must not send\n/exit\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("task-delegation-fx-bridge", result.stderr)
        self.assertEqual(read_jsonl(self.fx_log), [])
        self.assertEqual(read_jsonl(self.herdr_log), [])

    def test_missing_bridge_entry_rejects_resume_before_fx_request(self) -> None:
        first = self.command(*self.start_args(), input_text="First\n/exit\n")
        self.assertEqual(first.returncode, 0, first.stderr)
        _, state = self.state()
        self.entry.unlink()
        resumed = self.command("resume", "--task-ref", state["task_ref"],
                               input_text="Must not send\n/exit\n")
        self.assertEqual(resumed.returncode, 1)
        self.assertIn("task-delegation-fx-bridge", resumed.stderr)
        self.assertEqual(len(read_jsonl(self.fx_log)), 1)

    def test_changed_fx_settings_rejects_resume_before_fx_request(self) -> None:
        first = self.command(*self.start_args(), input_text="First\n/exit\n")
        self.assertEqual(first.returncode, 0, first.stderr)
        _, state = self.state()
        self.settings.write_text('{"provider":"changed"}', encoding="utf-8")
        resumed = self.command("resume", "--task-ref", state["task_ref"],
                               input_text="Must not send\n/exit\n")
        self.assertEqual(resumed.returncode, 1)
        self.assertEqual(len(read_jsonl(self.fx_log)), 1)

    def test_changed_fx_settings_after_ready_rejects_first_prompt(self) -> None:
        proc = subprocess.Popen([sys.executable, "-B", str(SCRIPT), *self.start_args()],
                                cwd=self.root, env=self.env, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, bufsize=1)
        try:
            self.assertTrue(select.select([proc.stdout], [], [], 5)[0],
                            "bridge did not publish ready status")
            ready = proc.stdout.readline()
            self.assertIn("FX_BRIDGE_READY", ready)
            self.settings.write_text('{"provider":"changed"}', encoding="utf-8")
            stdout, stderr = proc.communicate("Must not send\n/exit\n", timeout=10)
            self.assertEqual(proc.returncode, 1, stderr + stdout)
            self.assertEqual(read_jsonl(self.fx_log), [])
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=5)

    def test_failed_herdr_registration_does_not_send_model_request(self) -> None:
        result = self.command(*self.start_args(), input_text="Do not deliver\n/exit\n",
                              extra_env={"FAKE_HERDR_FAIL": "1"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("initial Herdr agent registration failed", result.stderr)
        self.assertEqual(read_jsonl(self.fx_log), [])
        self.assertEqual(read_jsonl(self.state_home / "task-delegation" / "delegations.jsonl"), [])
        events = read_jsonl(self.herdr_log)
        self.assertEqual([event[:2] for event in events],
                         [["pane", "report-agent"], ["pane", "release-agent"]])
        self.assertLess(int(option(events[0], "--seq")), int(option(events[1], "--seq")))


if __name__ == "__main__":
    unittest.main()
