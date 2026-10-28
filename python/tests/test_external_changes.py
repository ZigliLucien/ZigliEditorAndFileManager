import tempfile
import unittest
from pathlib import Path

from zefm.editor.external_changes import disk_signature, changed_on_disk, ExternalChangeDismissals


class ExternalChangesTests(unittest.TestCase):
    def test_change_detection_and_same_content_rewrite(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "example.txt"
            p.write_text("ייִדיש and français", encoding="utf-8")
            original = disk_signature(p)
            self.assertFalse(changed_on_disk(p, original))
            p.write_text("ייִדיש and français", encoding="utf-8")
            self.assertFalse(changed_on_disk(p, original))
            p.write_text("newer browser text", encoding="utf-8")
            self.assertTrue(changed_on_disk(p, original))

    def test_deleted_file_counts_as_changed(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "old.txt"
            p.write_text("hello")
            original = disk_signature(p)
            p.unlink()
            self.assertTrue(changed_on_disk(p, original))
            self.assertIsNone(disk_signature(p))

    def test_missing_file_signature(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "not-created.txt"
            self.assertIsNone(disk_signature(p))
            self.assertFalse(changed_on_disk(p, None))




class ExternalDismissalTests(unittest.TestCase):
    def test_dismissal_is_per_tab_and_revision(self):
        d = ExternalChangeDismissals()
        self.assertTrue(d.pending("a", "before", "after"))
        self.assertTrue(d.pending("b", "before", "after"))
        d.dismiss("a", "after")
        self.assertFalse(d.pending("a", "before", "after"))
        self.assertTrue(d.pending("a", "before", "new-change"))
        self.assertTrue(d.pending("b", "before", "after"))
        d.reset("a")
        self.assertTrue(d.pending("a", "before", "after"))

    def test_missing_file_and_restore(self):
        d = ExternalChangeDismissals()
        self.assertTrue(d.pending("tab", "original", None))
        d.dismiss("tab", None)
        self.assertFalse(d.pending("tab", "original", None))
        self.assertTrue(d.pending("tab", "original", "restored"))
        self.assertFalse(d.pending("tab", "original", "original"))

    def test_clean_buffer_or_untracked_file(self):
        d = ExternalChangeDismissals()
        self.assertFalse(d.pending("a", "equal", "equal"))
        self.assertFalse(d.pending("b", None, None))

if __name__ == "__main__":
    unittest.main()
