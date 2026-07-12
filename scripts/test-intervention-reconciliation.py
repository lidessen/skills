#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "intervention-reconciliation.py"
ADAPTER = ROOT / ".codex" / "hooks" / "intervention-reconciliation.py"


class InterventionReconciliationTest(unittest.TestCase):
    def run_cli(self, state_root: Path, *args: str, input: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(CLI), "--state-root", str(state_root), *args],
            input=input,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_observation_and_receipt_are_session_local_and_do_not_retain_prompt_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            state_root = Path(temporary) / "state"
            payload = {
                "session_id": "session-1",
                "turn_id": "turn-1",
                "cwd": str(ROOT),
                "prompt": "Do not retain this secret correction text",
            }
            observed = self.run_cli(state_root, "observe", input=json.dumps(payload))
            self.assertEqual(observed.returncode, 0, observed.stderr)
            state_path = Path(json.loads(observed.stdout)["statePath"])
            self.assertNotIn(payload["prompt"], state_path.read_text())

            anchored = self.run_cli(state_root, "anchor", "--cwd", str(ROOT), "--summary", "terminal and output contracts")
            self.assertEqual(anchored.returncode, 0, anchored.stderr)
            reconciled = self.run_cli(
                state_root,
                "reconcile",
                "--cwd", str(ROOT),
                "--rejected-assumption", "terminal tool payload owns final output",
                "--new-invariant", "terminal tools and output schema are independent",
                "--affected-surface", "contracts",
                "--affected-surface", "tests",
                "--next-probe", "verify each condition independently",
            )
            self.assertEqual(reconciled.returncode, 0, reconciled.stderr)
            status = self.run_cli(state_root, "status", "--cwd", str(ROOT))
            self.assertEqual(status.returncode, 0, status.stderr)
            rendered = json.loads(status.stdout)
            self.assertEqual(rendered["observations"], 1)
            self.assertEqual(rendered["anchor"]["summary"], "terminal and output contracts")
            self.assertEqual(rendered["receipts"][0]["affectedSurfaces"], ["contracts", "tests"])

    def test_codex_adapter_emits_context_and_uses_codex_local_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            environment = {**os.environ, "HOME": temporary}
            payload = {
                "session_id": "session-hook",
                "turn_id": "turn-hook",
                "cwd": str(ROOT),
                "prompt": "The previous boundary was wrong",
            }
            result = subprocess.run(
                ["python3", str(ADAPTER)],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            hook_output = json.loads(result.stdout)
            context = hook_output["hookSpecificOutput"]["additionalContext"]
            self.assertIn("compare it with the active task", context)
            self.assertIn("reconcile --help", context)
            self.assertTrue((Path(temporary) / ".codex" / "intervention-reconciliation").exists())


if __name__ == "__main__":
    unittest.main()
