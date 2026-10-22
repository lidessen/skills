"""Offline checks for the policy initializer."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "init.py"


class InitPolicyTests(unittest.TestCase):
    def run_init(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_creates_editable_policy_and_preserves_edits_on_repeat(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "policy.md"
            first = self.run_init("--output", str(output))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn("付费 API fallback", output.read_text(encoding="utf-8"))

            output.write_text("human edits\n", encoding="utf-8")
            second = self.run_init("--output", str(output))
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(output.read_text(encoding="utf-8"), "human edits\n")

    def test_dry_run_leaves_no_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "policy.md"
            result = self.run_init("--output", str(output), "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(output.exists())

    def test_missing_parent_is_not_created(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "missing" / "policy.md"
            result = self.run_init("--output", str(output))
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.parent.exists())


if __name__ == "__main__":
    unittest.main()
