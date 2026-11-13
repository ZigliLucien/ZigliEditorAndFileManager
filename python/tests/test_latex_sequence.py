"""v91: deterministic LaTeX passes and bibliography tool selection."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import unittest
from unittest.mock import patch

from zefm.server.latex_sequence import bibliography_tool, run_tex_sequence


class TexSequenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.work = self.root / ".zefm-build"
        self.work.mkdir()
        self.source = self.root / "paper.tex"
        self.source.write_text(r"\documentclass{article}\begin{document}x\end{document}")
        self.command = ["lualatex", "-no-shell-escape",
                        "-output-directory=" + str(self.work), str(self.source)]

    def test_two_passes_without_bibliography(self):
        calls = []
        def fake_run(argv, **kwargs):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")
        with patch("zefm.server.latex_sequence.subprocess.run", side_effect=fake_run):
            rc, log, elapsed = run_tex_sequence(self.command, self.source, self.work)
        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], self.command)
        self.assertIn("pass 2", log)

    def test_bibtex_then_two_more_latex_passes(self):
        calls = []
        def fake_run(argv, **kwargs):
            calls.append((argv, kwargs))
            if len(calls) == 1:
                (self.work / "paper.aux").write_text(
                    r"\relax" + "\n" + r"\bibdata{refs}" + "\n")
            return subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")
        with patch("zefm.server.latex_sequence.shutil.which",
                   return_value="/usr/bin/bibtex"), \
             patch("zefm.server.latex_sequence.subprocess.run", side_effect=fake_run):
            rc, log, _ = run_tex_sequence(self.command, self.source, self.work)
        self.assertEqual(rc, 0)
        self.assertEqual([call[0][0] for call in calls],
                         ["lualatex", "/usr/bin/bibtex", "lualatex", "lualatex"])
        self.assertEqual(calls[1][1]["cwd"], str(self.work))
        self.assertIn(str(self.source.parent), calls[1][1]["env"]["BIBINPUTS"])
        self.assertIn("bibtex", log)

    def test_biber_is_preferred_when_bcf_exists(self):
        calls = []
        def fake_run(argv, **kwargs):
            calls.append(argv)
            if len(calls) == 1:
                (self.work / "paper.bcf").write_text("<controlfile/>")
                (self.work / "paper.aux").write_text(r"\bibdata{other}")
            return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")
        with patch("zefm.server.latex_sequence.shutil.which",
                   return_value="/usr/bin/biber"), \
             patch("zefm.server.latex_sequence.subprocess.run", side_effect=fake_run):
            rc, _, _ = run_tex_sequence(self.command, self.source, self.work)
        self.assertEqual(rc, 0)
        self.assertEqual(calls[1][0], "/usr/bin/biber")
        self.assertIn("--input-directory", calls[1])
        self.assertEqual(len(calls), 4)

    def test_missing_bibliography_executable_never_claims_success(self):
        calls = []
        def fake_run(argv, **kwargs):
            calls.append(argv)
            (self.work / "paper.aux").write_text(r"\bibdata{refs}")
            return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")
        with patch("zefm.server.latex_sequence.shutil.which", return_value=None), \
             patch("zefm.server.latex_sequence.subprocess.run", side_effect=fake_run):
            rc, log, _ = run_tex_sequence(self.command, self.source, self.work)
        self.assertEqual(rc, 127)
        self.assertIn("bibtex is needed", log)
        self.assertEqual(len(calls), 1)

    def test_failure_stops_before_followup_pass(self):
        with patch("zefm.server.latex_sequence.subprocess.run",
                   return_value=subprocess.CompletedProcess(
                       self.command, 1, stdout="! error", stderr="")) as runner:
            rc, log, _ = run_tex_sequence(self.command, self.source, self.work)
        self.assertEqual(rc, 1)
        self.assertIn("! error", log)
        runner.assert_called_once()

    def test_timeout_is_reported_and_bounded(self):
        with patch("zefm.server.latex_sequence.subprocess.run",
                   side_effect=subprocess.TimeoutExpired(self.command, 45)):
            with self.assertRaisesRegex(RuntimeError, "timed out"):
                run_tex_sequence(self.command, self.source, self.work)

    def test_metadata_detection(self):
        self.assertIsNone(bibliography_tool(self.work, "paper"))
        (self.work / "paper.aux").write_text(r"\bibdata{refs}")
        self.assertEqual(bibliography_tool(self.work, "paper"), "bibtex")
        (self.work / "paper.bcf").write_text("control")
        self.assertEqual(bibliography_tool(self.work, "paper"), "biber")


if __name__ == "__main__":
    unittest.main()
