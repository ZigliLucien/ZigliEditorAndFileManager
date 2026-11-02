"""Wheel selection and filesystem ordering for the v60 Tk file chooser."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from zefm.editor.gui.file_chooser import wheel_steps, directory_entries


class WheelTests(unittest.TestCase):
    def test_x11_linux_button_scrolling(self):
        self.assertEqual(wheel_steps(SimpleNamespace(num=4, delta=0)), -1)
        self.assertEqual(wheel_steps(SimpleNamespace(num=5, delta=0)), 1)

    def test_windows_macos_wheel(self):
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=120)), -1)
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=-120)), 1)
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=240)), -2)
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=-240)), 2)
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=1)), -1)
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=-1)), 1)
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=0)), 0)

    def test_directory_sorting(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("z.txt", "A.txt", "b.txt"):
                (root / name).write_text(name)
            for name in ("subDir", "Another"):
                (root / name).mkdir()
            self.assertEqual([p.name for p in directory_entries(root)],
                             ["Another", "subDir", "A.txt", "b.txt", "z.txt"])

    def test_nonexistent_directory(self):
        with TemporaryDirectory() as temp:
            with self.assertRaises(OSError):
                directory_entries(Path(temp) / "not-there")


if __name__ == "__main__":
    unittest.main()
