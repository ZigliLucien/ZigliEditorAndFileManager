"""v97: safe, configurable, persistent non-LaTeX Run commands."""
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from zefm.editor.run_commands import (
    RunCommands, execute_command, expand_command, validate_argv)


class RunCommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.file = self.root / "cœur ייִדיש.py"
        self.file.write_text("print('hello')\n", encoding="utf-8")
        self.prefs = self.root / "run_commands.json"

    def test_unicode_round_trip_and_clear(self):
        store = RunCommands(self.prefs)
        store.set("python", ["python3", "{file}"])
        self.assertEqual(RunCommands(self.prefs).get("python"),
                         ["python3", "{file}"])
        self.assertIn("python", json.loads(self.prefs.read_text())["modes"])
        store.clear("python")
        self.assertIsNone(RunCommands(self.prefs).get("python"))

    def test_arg_placeholders_keep_spaces_and_unicode(self):
        self.assertEqual(
            expand_command(["python3", "{file}", "--dir={dir}", "{name}"],
                           self.file),
            ["python3", str(self.file.resolve()),
             "--dir=" + str(self.root.resolve()), self.file.name])

    def test_refuse_shell_style_string_and_unknown_placeholder(self):
        for bad in ('python3 "{file}"', ["python3", "{filename}"],
                    [], ["python3", ""], ["python3", "foo{file}{bad}"]):
            with self.subTest(argv=bad):
                with self.assertRaises(ValueError):
                    validate_argv(bad)

    def test_corrupt_json_fails_softly(self):
        self.prefs.write_text("{bad", encoding="utf-8")
        self.assertIsNone(RunCommands(self.prefs).get("python"))
        self.prefs.write_text('{"modes":{"python":"python3 {file}"}}',
                              encoding="utf-8")
        self.assertIsNone(RunCommands(self.prefs).get("python"))

    def test_run_subprocess_uses_no_shell_and_source_directory(self):
        expected = ["python3", str(self.file.resolve())]
        with patch("zefm.editor.run_commands.subprocess.run",
                   return_value=subprocess.CompletedProcess(
                       expected, 0, stdout="ok", stderr="")) as runner:
            result = execute_command(["python3", "{file}"], self.file)
        self.assertTrue(result["ok"])
        self.assertIn("ok", result["log"])
        self.assertEqual(runner.call_args.args[0], expected)
        self.assertEqual(runner.call_args.kwargs["cwd"], str(self.root))
        self.assertNotIn("shell", runner.call_args.kwargs)
        self.assertEqual(runner.call_args.kwargs["timeout"], 30)

    def test_nonzero_return_and_timeout(self):
        with patch("zefm.editor.run_commands.subprocess.run",
                   return_value=subprocess.CompletedProcess(
                       ["python3"], 2, stdout="", stderr="error")):
            result = execute_command(["python3", "{file}"], self.file)
        self.assertFalse(result["ok"])
        self.assertEqual(result["returncode"], 2)
        with patch("zefm.editor.run_commands.subprocess.run",
                   side_effect=subprocess.TimeoutExpired("python3", 30)):
            timeout = execute_command(["python3", "{file}"], self.file)
        self.assertFalse(timeout["ok"])
        self.assertIn("timed out", timeout["log"])

    def test_missing_input_does_not_execute(self):
        with patch("zefm.editor.run_commands.subprocess.run") as runner:
            with self.assertRaises(ValueError):
                execute_command(["python3", "{file}"], self.root / "missing.py")
        runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
