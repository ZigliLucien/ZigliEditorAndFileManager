import json
import tempfile
import unittest
from pathlib import Path
from zefm.editor.recent_files import RecentFiles


class RecentFilesTests(unittest.TestCase):
    def test_record_reorder_dedupe_and_persist(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d)/'config'/'recent.json'
            history=RecentFiles(state, limit=3)
            for name in ('a', 'b', 'c', 'd', 'b'):
                history.record(Path(d)/name)
            self.assertEqual([Path(x).name for x in history.entries], ['b','d','c'])
            self.assertEqual(RecentFiles(state,3).entries, history.entries)
            self.assertEqual(json.loads(state.read_text())['files'],history.entries)

    def test_clear_and_forget(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d)/'recent.json'; h=RecentFiles(state)
            h.record(Path(d)/'alpha');h.record(Path(d)/'beta')
            h.forget(Path(d)/'alpha')
            self.assertEqual(len(h.entries),1)
            h.clear()
            self.assertEqual(RecentFiles(state).entries,[])

    def test_corrupt_state(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d)/'recent.json'
            state.write_text('{not valid',encoding='utf-8')
            self.assertEqual(RecentFiles(state).entries,[])
            state.write_text(json.dumps({'files':[10,None,'one','one','two']}))
            self.assertEqual(RecentFiles(state).entries,['one','two'])

    def test_bad_limits(self):
        with self.assertRaises(ValueError):RecentFiles(limit=0)
        with self.assertRaises(ValueError):RecentFiles(limit=51)
