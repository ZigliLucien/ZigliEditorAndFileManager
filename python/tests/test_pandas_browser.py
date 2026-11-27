import tempfile
import unittest
from pathlib import Path

from zefm.server.file_manager import LocalFiles, BrowserError
from zefm.server.pandas_table import dataframe_preview

try:
    import pandas
except ImportError:
    pandas = None


@unittest.skipIf(pandas is None, "optional pandas dependency")
class PandasBrowserTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.files = LocalFiles(self.root)
        self.source = self.root / "data.csv"
        self.source.write_text("Code,Name,Value\n001,Alpha,100\n002,Beta,2\n003,Alpha,10\n", encoding="utf-8")

    def test_numeric_sort_preserves_text(self):
        result = dataframe_preview(self.files, "data.csv", sort="Value", sort_type="number")
        self.assertLess(result.index("<td>002</td>"), result.index("<td>003</td>"))
        self.assertLess(result.index("<td>003</td>"), result.index("<td>001</td>"))
        self.assertIn("<tr><th>2</th>", result)

    def test_column_filter(self):
        result = dataframe_preview(self.files, "data.csv", contains="Alpha", column="Name")
        self.assertIn("2 matching rows of 3", result)
        self.assertNotIn("<td>002</td>", result)

    def test_pagination(self):
        self.source.write_text("N\n" + "\n".join(str(i) for i in range(1, 81)), encoding="utf-8")
        result = dataframe_preview(self.files, "data.csv", page=2, page_size=25)
        self.assertIn("Page 2 of 4", result)
        self.assertIn("<td>26</td>", result)
        self.assertNotIn("<td>25</td>", result)

    def test_validation(self):
        for options in ({"page": 0}, {"page_size": 999}, {"column": "missing"}, {"sort_type": "bad"}):
            with self.assertRaises(BrowserError):
                dataframe_preview(self.files, "data.csv", **options)
