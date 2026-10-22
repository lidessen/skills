#!/usr/bin/env python3
"""Keep an Fx conversation in a Herdr pane using Fx's documented CLI.

The bridge accepts one prompt per terminal line. It does not interpret task
content, approve Fx tool requests, choose a model, or retry a failed turn.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import subprocess
import sys
import time
import uuid

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))
from log import append_event, default_log_path


ENTRY_COMMAND = "task-delegation-fx-bridge"
MAX_PROMPT_BYTES = 65536
REPORT_TIMEOUT = 1.5


class BridgeError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def state_root() -> Path:
    configured = os.environ.get("XDG_STATE_HOME", "")
    base = Path(configured) if configured and Path(configured).is_absolute() else Path.home() / ".local" / "state"
    return base / "task-delegation" / "fx-bridge"


def one_line(name: str, value: str, limit: int) -> str:
    value = value.strip()
    if not value or len(value) > limit or any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise BridgeError(f"{name} must be one nonempty line of at most {limit} characters")
    return value


def exact_uuid(value: str) -> str:
    try:
        parsed = str(uuid.UUID(value))
    except ValueError as error:
        raise BridgeError("task-ref must be a UUID") from error
    if parsed != value:
        raise BridgeError("task-ref must be a canonical UUID")
    return parsed


def absolute_existing_dir(name: str, value: str) -> str:
    path = Path(value).expanduser()
    if not path.is_absolute() or not path.is_dir():
        raise BridgeError(f"{name} must be an existing absolute directory")
    return str(path.resolve())


def executable(value: str | None) -> str:
    found = value or shutil.which("fx")
    if not found:
        raise BridgeError("fx executable not found")
    path = Path(found).expanduser()
    if not path.is_absolute() or not path.is_file() or not os.access(path, os.X_OK):
        raise BridgeError("fx-bin must be an executable absolute file")
    return str(path.resolve())


def ensure_resume_entry() -> None:
    """Do not advertise recovery through a missing or unrelated PATH command."""
    found = shutil.which(ENTRY_COMMAND)
    if not found:
        raise BridgeError(f"{ENTRY_COMMAND} is not executable on PATH")
    try:
        if not os.path.samefile(found, Path(__file__).resolve()):
            raise BridgeError(f"{ENTRY_COMMAND} on PATH is not this bridge")
    except OSError as error:
        raise BridgeError(f"{ENTRY_COMMAND} on PATH cannot be verified") from error


def fx_settings_digest(fx_home: str) -> str | None:
    """Fingerprint local Fx routing without retaining settings or credentials."""
    path = Path(fx_home) / ".fx" / "settings.json"
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        if path.is_symlink():
            raise BridgeError("Fx settings link is unreadable")
        return None
    except OSError as error:
        raise BridgeError("Fx settings are unreadable") from error
    return hashlib.sha256(data).hexdigest()


def verify_fx_settings(state: dict) -> None:
    if "fx_settings_sha256" not in state:
        raise BridgeError("saved Fx settings fingerprint is missing")
    if fx_settings_digest(state["fx_home"]) != state["fx_settings_sha256"]:
        raise BridgeError("Fx settings changed; inspect routing before another turn")


def atomic_json(path: Path, value: dict) -> None:
    temporary = path.with_name("." + path.name + "." + secrets.token_hex(6))
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def new_state(args: argparse.Namespace) -> tuple[Path, dict]:
    project = one_line("project", args.project, 80)
    if "/" in project or "\\" in project:
        raise BridgeError("project must be a short label, not a path")
    description = one_line("description", args.description, 240)
    provider = one_line("provider", args.provider, 120)
    model = one_line("model", args.model, 240)
    fx_home = absolute_existing_dir("fx-home", args.fx_home or str(Path.home()))
    cwd = str(Path.cwd().resolve())
    fx_bin = executable(args.fx_bin)
    root = state_root()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    task_ref = str(uuid.uuid4())
    directory = root / task_ref
    directory.mkdir(mode=0o700)
    state = {
        "task_ref": task_ref,
        "project": project,
        "description": description,
        "provider": provider,
        "model": model,
        "fx_home": fx_home,
        "fx_settings_sha256": fx_settings_digest(fx_home),
        "fx_bin": fx_bin,
        "cwd": cwd,
        "no_additional_dirs": args.no_additional_dirs,
        "clean_fx_env": args.clean_fx_env,
        "turn_timeout": args.turn_timeout,
        "turn": 0,
        "turn_status": None,
        "seq": 0,
        "session_id": None,
        "source": "fx-bridge:" + task_ref,
        "agent": "fx-" + task_ref.replace("-", "")[:24],
        "pane_id": None,
        "bridge_state": "initializing",
        "herdr_report_ok": False,
        "herdr_release_ok": None,
        "last_result_path": None,
        "updated_at": utc_now(),
    }
    atomic_json(directory / "state.json", state)
    return directory, state


def read_state(task_ref: str) -> tuple[Path, dict]:
    directory = state_root() / exact_uuid(task_ref)
    try:
        state = json.loads((directory / "state.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BridgeError("bridge state is missing or unreadable") from error
    if state.get("task_ref") != task_ref:
        raise BridgeError("bridge task-ref does not match its state")
    return directory, state


def lock_task(directory: Path) -> int:
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(directory / "bridge.lock", flags, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        os.close(descriptor)
        raise BridgeError("this Fx bridge is already active") from error
    return descriptor


def herdr_environment() -> tuple[str, str]:
    if os.environ.get("HERDR_ENV") != "1":
        raise BridgeError("start/resume must run inside a Herdr pane (HERDR_ENV=1)")
    pane_id = os.environ.get("HERDR_PANE_ID", "")
    binary = os.environ.get("HERDR_BIN_PATH", "")
    socket = os.environ.get("HERDR_SOCKET_PATH", "")
    if not pane_id or not binary or not socket:
        raise BridgeError("Herdr pane ID, binary path, and socket path are required")
    if not Path(binary).is_absolute() or not os.access(binary, os.X_OK):
        raise BridgeError("HERDR_BIN_PATH must be an executable absolute path")
    if not Path(socket).is_absolute():
        raise BridgeError("HERDR_SOCKET_PATH must be absolute")
    return pane_id, binary


def display(kind: str, value: dict) -> None:
    print(kind + " " + json.dumps(value, ensure_ascii=False, separators=(",", ":")), flush=True)


class FxBridge:
    def __init__(self, directory: Path, state: dict, pane_id: str, herdr_bin: str):
        self.directory = directory
        self.state = state
        self.pane_id = pane_id
        self.herdr_bin = herdr_bin
        self.registered = False
        self.report_attempted = False
        self.child: subprocess.Popen | None = None
        os.chdir(state["cwd"])
        self.state["pane_id"] = pane_id

    def save(self) -> None:
        self.state["updated_at"] = utc_now()
        atomic_json(self.directory / "state.json", self.state)

    def next_seq(self) -> int:
        self.state["seq"] = max(time.time_ns(), self.state["seq"] + 1)
        return self.state["seq"]

    def resume_argv(self) -> list[str]:
        if not self.state.get("session_id"):
            return []
        ensure_resume_entry()
        argv = [ENTRY_COMMAND, "resume", "--task-ref", self.state["task_ref"]]
        if len(argv) > 64 or sum(len(item.encode()) for item in argv) > 8192:
            raise BridgeError("Herdr resume command is too large")
        if any("'" in item or any(ord(char) < 32 or ord(char) == 127 for char in item) for item in argv):
            raise BridgeError("Herdr resume command contains an unsupported character")
        return argv

    def report(self, status: str, *, initial: bool = False) -> bool:
        self.state["bridge_state"] = status
        seq = self.next_seq()
        self.save()  # Persist the sequence before sending so a restart cannot reuse it.
        command = [self.herdr_bin, "pane", "report-agent", self.pane_id,
                   "--source", self.state["source"], "--agent", self.state["agent"],
                   "--state", status, "--seq", str(seq)]
        if self.state.get("session_id"):
            command += ["--agent-session-id", self.state["session_id"]]
            command += ["--"] + self.resume_argv()
        self.report_attempted = True
        try:
            result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, timeout=REPORT_TIMEOUT, check=False)
            accepted = result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            accepted = False
        self.state["herdr_report_ok"] = accepted
        self.save()
        if not accepted:
            print("FX_BRIDGE_REPORT_FAILED state=" + status, file=sys.stderr, flush=True)
            if initial:
                raise BridgeError("initial Herdr agent registration failed; no task was sent")
        else:
            self.registered = True
        return accepted

    def release(self) -> None:
        if not self.report_attempted:
            return
        seq = self.next_seq()
        self.state["bridge_state"] = "stopped"
        self.save()
        command = [self.herdr_bin, "pane", "release-agent", self.pane_id,
                   "--source", self.state["source"], "--agent", self.state["agent"],
                   "--seq", str(seq)]
        try:
            result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, timeout=REPORT_TIMEOUT, check=False)
            self.state["herdr_release_ok"] = result.returncode == 0
            if not self.state["herdr_release_ok"]:
                print("FX_BRIDGE_RELEASE_FAILED", file=sys.stderr, flush=True)
        except (OSError, subprocess.TimeoutExpired):
            self.state["herdr_release_ok"] = False
            print("FX_BRIDGE_RELEASE_FAILED", file=sys.stderr, flush=True)
        self.save()

    def log(self, status: str) -> None:
        event = {
            "at": utc_now(),
            "task_ref": self.state["task_ref"],
            "project": self.state["project"],
            "description": self.state["description"],
            "runner": "fx",
            "status": status,
            "herdr_agent": self.state["agent"],
            "herdr_pane_id": self.pane_id,
            "runner_session_id": self.state.get("session_id"),
            "session_state": "confirmed" if self.state.get("session_id") else "pending",
        }
        try:
            append_event(default_log_path(), event)
        except OSError:
            print("FX_BRIDGE_LOG_FAILED", file=sys.stderr, flush=True)

    def fx_command(self, prompt: str) -> list[str]:
        command = [self.state["fx_bin"]]
        if self.state["no_additional_dirs"]:
            command.append("--no-additional-dirs")
        command += ["ask", "--json", "--model", self.state["model"]]
        if self.state.get("session_id"):
            command += ["--resume-id", self.state["session_id"]]
        return command + ["--", prompt]

    def fx_environment(self) -> dict[str, str]:
        if self.state.get("clean_fx_env"):
            temporary = Path(self.state["fx_home"]) / "tmp"
            environment = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                           "TMPDIR": str(temporary) if temporary.is_dir() else "/tmp"}
            for key in ("LANG", "LC_ALL", "LC_CTYPE"):
                if key in os.environ:
                    environment[key] = os.environ[key]
        else:
            environment = {key: value for key, value in os.environ.items()
                           if not key.startswith("FX_") and not key.startswith("HERDR_")}
        environment.update({"HOME": self.state["fx_home"], "FX_PROVIDER": self.state["provider"],
                            "FX_MODEL": self.state["model"], "FX_AUTO_UPGRADE": "0", "FX_HERDR": "0",
                            "FX_ULTRAFAST": "0"})
        return environment

    def stop_child(self) -> None:
        if self.child is None or self.child.poll() is not None:
            return
        try:
            os.killpg(self.child.pid, signal.SIGTERM)
            self.child.wait(timeout=2)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            if self.child.poll() is None:
                try:
                    os.killpg(self.child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                self.child.wait(timeout=2)

    def turn(self, prompt: str) -> None:
        verify_fx_settings(self.state)
        number = self.state["turn"] + 1
        self.state["turn"] = number
        self.state["turn_status"] = "working"
        self.save()
        self.report("working")
        self.log("started")
        timed_out = False
        process_code = None
        stdout = ""
        parsed = None
        failure = None
        try:
            self.child = subprocess.Popen(self.fx_command(prompt), cwd=self.state["cwd"],
                                          env=self.fx_environment(), stdin=subprocess.DEVNULL,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          text=True, encoding="utf-8", errors="replace",
                                          start_new_session=True)
            try:
                stdout, _ = self.child.communicate(timeout=self.state["turn_timeout"])
            except subprocess.TimeoutExpired:
                timed_out = True
                self.stop_child()
                stdout, _ = self.child.communicate(timeout=2)
            process_code = self.child.returncode
        except OSError:
            failure = "fx_start_failed"
        finally:
            self.stop_child()
            self.child = None
        if timed_out:
            failure = "turn_timeout"
        if not timed_out and stdout:
            try:
                parsed = json.loads(stdout)
                if not isinstance(parsed, dict):
                    parsed = None
                    failure = "invalid_fx_json"
            except json.JSONDecodeError:
                failure = "invalid_fx_json"
        elif not timed_out and failure is None:
            failure = "empty_fx_json"
        if parsed is not None:
            fx_code = parsed.get("exit_code")
            returned_model = parsed.get("model")
            returned_session = parsed.get("session_id")
            if isinstance(returned_session, str) and returned_session:
                if self.state.get("session_id") and returned_session != self.state["session_id"]:
                    failure = "fx_session_mismatch"
                else:
                    self.state["session_id"] = returned_session
            if returned_model is not None and returned_model != self.state["model"]:
                failure = "fx_model_mismatch"
            if not isinstance(returned_session, str) or not returned_session:
                failure = "fx_session_missing"
            if type(fx_code) is not int or fx_code != 0 or process_code != 0:
                failure = failure or "fx_nonzero_exit"
        else:
            fx_code = None
        status = "failed" if failure else "completed"
        receipt = {
            "at": utc_now(), "task_ref": self.state["task_ref"], "turn": number,
            "status": status, "failure": failure, "timed_out": timed_out,
            "process_exit_code": process_code, "fx_exit_code": fx_code,
            "provider": self.state["provider"], "requested_model": self.state["model"],
            "session_id": parsed.get("session_id") if parsed is not None else None,
            "fx_receipt": {key: parsed[key] for key in
                           ("exit_code", "final_output", "output", "model", "resolved_provider",
                            "session_id", "steps", "usage", "tool_calls", "error")
                           if parsed is not None and key in parsed},
        }
        result_path = self.directory / f"turn-{number}.json"
        atomic_json(result_path, receipt)
        self.state["turn_status"] = status
        self.state["last_result_path"] = result_path.name
        self.save()
        self.log(status)
        display("FX_BRIDGE_RESULT", {"task_ref": self.state["task_ref"], "turn": number,
                                     "status": status, "failure": failure,
                                     "process_exit_code": process_code, "fx_exit_code": fx_code,
                                     "session_id": self.state.get("session_id"),
                                     "result_path": str(result_path)})
        if failure:
            # A failed turn needs inspection before another prompt. In particular,
            # a missing ID or changed model must never lead to a silent reroute.
            self.report("unknown")
            raise BridgeError(f"Fx turn {number} failed ({failure}); inspect its saved receipt")
        # The bridge is ready for a new line only after the receipt is durable.
        self.report("idle")

    def run(self) -> None:
        try:
            self.report("idle", initial=True)
            display("FX_BRIDGE_READY", {"task_ref": self.state["task_ref"], "agent": self.state["agent"],
                                        "session_id": self.state.get("session_id")})
            while True:
                line = sys.stdin.buffer.readline(MAX_PROMPT_BYTES + 2)
                if not line:
                    return
                if len(line) > MAX_PROMPT_BYTES:
                    while line and not line.endswith(b"\n"):
                        line = sys.stdin.buffer.readline(MAX_PROMPT_BYTES + 2)
                    display("FX_BRIDGE_INPUT_ERROR", {"reason": "prompt_line_too_long"})
                    continue
                try:
                    prompt = line.decode("utf-8").rstrip("\r\n")
                except UnicodeDecodeError:
                    display("FX_BRIDGE_INPUT_ERROR", {"reason": "invalid_utf8"})
                    continue
                if prompt == "/exit":
                    return
                if not prompt.strip():
                    continue
                self.turn(prompt)
        finally:
            self.stop_child()
            self.release()


def inspect(task_ref: str) -> None:
    directory, state = read_state(task_ref)
    last_result = None
    result_path = None
    name = state.get("last_result_path")
    if isinstance(name, str) and name.startswith("turn-") and name.endswith(".json") and "/" not in name:
        result_path = directory / name
        try:
            receipt = json.loads(result_path.read_text(encoding="utf-8"))
            last_result = {key: receipt.get(key) for key in
                           ("turn", "status", "failure", "timed_out", "process_exit_code", "fx_exit_code", "session_id")}
            last_result["final_output"] = receipt.get("fx_receipt", {}).get("final_output")
        except (OSError, json.JSONDecodeError):
            last_result = {"error": "last result is unreadable"}
    print(json.dumps({"task_ref": state["task_ref"], "project": state["project"],
                      "description": state["description"], "provider": state["provider"],
                      "model": state["model"], "agent": state["agent"],
                      "pane_id": state.get("pane_id"), "bridge_state": state.get("bridge_state"),
                      "herdr_report_ok": state.get("herdr_report_ok"), "turn": state["turn"],
                      "herdr_release_ok": state.get("herdr_release_ok"),
                      "turn_status": state.get("turn_status"), "session_id": state.get("session_id"),
                      "result_path": str(result_path) if result_path else None,
                      "last_result": last_result}, ensure_ascii=False))


def positive_timeout(value: str) -> float:
    try:
        result = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("timeout must be a number") from error
    if not 1 <= result <= 86400:
        raise argparse.ArgumentTypeError("timeout must be between 1 and 86400 seconds")
    return result


def interrupt_on_term(_signum: int, _frame: object) -> None:
    raise KeyboardInterrupt


def main(argv: list[str] | None = None) -> int:
    os.umask(0o077)
    signal.signal(signal.SIGTERM, interrupt_on_term)
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    start = sub.add_parser("start", help="Start a new persistent Herdr-pane bridge")
    start.add_argument("--project", required=True)
    start.add_argument("--description", required=True)
    start.add_argument("--provider", required=True)
    start.add_argument("--model", required=True)
    start.add_argument("--fx-home", help="Existing absolute Fx profile home; defaults to current HOME")
    start.add_argument("--fx-bin", help="Absolute Fx executable; defaults to fx on PATH")
    start.add_argument("--no-additional-dirs", action="store_true")
    start.add_argument("--clean-fx-env", action="store_true",
                       help="Pass only a small non-secret environment to Fx")
    start.add_argument("--turn-timeout", type=positive_timeout, default=1800.0, metavar="SECONDS")
    resume = sub.add_parser("resume", help="Reopen a saved Fx bridge without resending a turn")
    resume.add_argument("--task-ref", required=True)
    query = sub.add_parser("inspect", help="Print saved bridge and last-turn status as JSON")
    query.add_argument("--task-ref", required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "inspect":
            inspect(args.task_ref)
            return 0
        ensure_resume_entry()
        pane_id, herdr_bin = herdr_environment()
        if args.action == "start":
            directory, state = new_state(args)
        else:
            directory, state = read_state(args.task_ref)
            absolute_existing_dir("saved fx-home", state["fx_home"])
            absolute_existing_dir("saved cwd", state["cwd"])
            executable(state["fx_bin"])
            verify_fx_settings(state)
            if state.get("turn_status") == "working":
                raise BridgeError("previous turn outcome is uncertain; inspect it before any new prompt")
            if state.get("turn", 0) > 0 and not state.get("session_id"):
                raise BridgeError("no confirmed Fx session ID; resuming would start a new conversation")
        descriptor = lock_task(directory)
        try:
            bridge = FxBridge(directory, state, pane_id, herdr_bin)
            bridge.run()
        finally:
            os.close(descriptor)
        return 0
    except BridgeError as error:
        print("FX_BRIDGE_ERROR " + str(error), file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
