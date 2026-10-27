import json
import tempfile
import unittest
from pathlib import Path
from zefm.editor.working_directory import WorkingDirectory

class DirectoryTests(unittest.TestCase):
    def test_home_and_last(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); sub=root/'sub'; sub.mkdir()
            state=WorkingDirectory(str(root),True)
            self.assertEqual(state.initial_directory(),str(root.resolve()))
            state.used_file(sub/'test.json')
            self.assertEqual(state.initial_directory(),str(sub.resolve()))
            state.set_directory(root)
            self.assertEqual(state.initial_directory(),str(root.resolve()))
    def test_no_remember(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); sub=root/'sub'; sub.mkdir()
            state=WorkingDirectory(str(root),False)
            state.used_file(sub/'test.json')
            self.assertEqual(state.initial_directory(),str(root.resolve()))
    def test_invalid(self):
        with self.assertRaises(ValueError):WorkingDirectory('')
        with self.assertRaises(ValueError):WorkingDirectory('~', 'yes')

    def test_persist_across_instances(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); sub=root/'sub'; sub.mkdir(); state=root/'settings'/'session.json'
            first=WorkingDirectory(str(root),True,state)
            first.used_file(sub/'test.json')
            second=WorkingDirectory(str(root),True,state)
            self.assertEqual(second.initial_directory(),str(sub.resolve()))
            self.assertEqual(json.loads(state.read_text())['last_directory'],str(sub.resolve()))

    def test_stale_and_invalid_state(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); state=root/'session.json'
            state.write_text('{broken')
            self.assertEqual(WorkingDirectory(str(root),True,state).initial_directory(),str(root.resolve()))
            state.write_text(json.dumps({'last_directory':str(root/'gone')}))
            self.assertEqual(WorkingDirectory(str(root),True,state).initial_directory(),str(root.resolve()))

    def test_no_persistence_when_disabled(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); sub=root/'sub';sub.mkdir(); state=root/'session.json'
            wd=WorkingDirectory(str(root),False,state)
            wd.set_directory(sub)
            self.assertFalse(state.exists())
            self.assertEqual(WorkingDirectory(str(root),False,state).initial_directory(),str(root.resolve()))
