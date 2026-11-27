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

    def test_json_records_and_nested_values(self):
        import json
        source = self.root / "papers.json"
        records = [{"id": "001", "year": 2020, "authors": [{"name": "Ada"}]},
                   {"id": "002", "year": 2023, "authors": [], "notes": None}]
        source.write_text(json.dumps(records), encoding="utf-8")
        result = dataframe_preview(self.files, source.name, contains="Ada", column="authors")
        self.assertIn("1 matching rows of 2", result)
        data = json.loads(dataframe_preview(self.files, source.name, export="json"))
        self.assertEqual(data[0]["id"], "001")
        self.assertEqual(data[0]["year"], 2020)
        self.assertEqual(data[0]["authors"], [{"name": "Ada"}])
        self.assertIsNone(data[1]["notes"])

    def test_jsonl_and_table_orientation(self):
        import json
        source = self.root / "data.jsonl"
        source.write_text('{"id":"001","amount":10}\n{"id":"002","amount":2}\n', encoding="utf-8")
        data = json.loads(dataframe_preview(self.files, source.name, sort="amount",
                                           sort_type="number", export="json"))
        self.assertEqual([row["id"] for row in data], ["002", "001"])
        table = self.root / "table.json"
        table.write_text(json.dumps({"schema": {"fields": []}, "data": data}), encoding="utf-8")
        self.assertEqual(json.loads(dataframe_preview(self.files, table.name, export="json")), data)

    def test_invalid_jsonl(self):
        source = self.root / "bad.jsonl"
        source.write_text('{"id":1}\ninvalid\n', encoding="utf-8")
        with self.assertRaises(BrowserError):
            dataframe_preview(self.files, source.name)

    def test_clickable_urls_in_nested_json(self):
        import json
        source = self.root / "links.jsonl"
        record = {"url": "https://example.org/p?a=1&b=2",
                  "pdf": {"url": "https://example.org/p.pdf"},
                  "notes": "<script>alert(1)</script> javascript:alert(1)"}
        source.write_text(json.dumps(record) + "\n", encoding="utf-8")
        result = dataframe_preview(self.files, source.name)
        self.assertIn('href="https://example.org/p?a=1&amp;b=2"', result)
        self.assertIn('href="https://example.org/p.pdf"', result)
        self.assertIn('target="_blank" rel="noopener noreferrer"', result)
        self.assertNotIn("<script>", result)
        self.assertNotIn('href="javascript:', result)
        self.assertEqual(json.loads(dataframe_preview(self.files, source.name, export="json")), [record])

    def test_cache_reuses_source_and_invalidates(self):
        from unittest.mock import patch
        from zefm.server import pandas_table as table
        with patch.object(table, "_read_frame", wraps=table._read_frame) as read:
            dataframe_preview(self.files, "data.csv", page=1)
            dataframe_preview(self.files, "data.csv", sort="Value", sort_type="number")
            dataframe_preview(self.files, "data.csv", contains="Alpha")
            self.assertEqual(read.call_count, 1)
            self.source.write_text("Code,Name,Value\n009,New,12345\n", encoding="utf-8")
            result = dataframe_preview(self.files, "data.csv")
            self.assertEqual(read.call_count, 2)
            self.assertIn("<td>009</td>", result)
            self.assertNotIn("<td>001</td>", result)

    def test_cache_full_export_is_not_truncated(self):
        import json
        self.source.write_text("N\n" + "\n".join(str(i) for i in range(1100)), encoding="utf-8")
        dataframe_preview(self.files, "data.csv")
        records = json.loads(dataframe_preview(self.files, "data.csv", export="json"))
        self.assertEqual(len(records), 1100)
        self.assertEqual(records[-1]["N"], "1099")

    def test_bib_preview_and_export_share_parse(self):
        from unittest.mock import patch
        from zefm.server import pandas_table as table
        try:
            from bibtexparser.bparser import BibTexParser
        except ImportError:
            self.skipTest("optional bibtexparser 1.x dependency")
        source = self.root / "refs.bib"
        source.write_text("@article{a, title={A}, year={2025}}\n"
                          "@article{b, title={B}, year={2024}}\n", encoding="utf-8")
        with patch.object(table, "_read_bib_records", wraps=table._read_bib_records) as read:
            dataframe_preview(self.files, source.name)
            dataframe_preview(self.files, source.name, sort="year")
            dataframe_preview(self.files, source.name, export="bib")
            self.assertEqual(read.call_count, 1)

    def test_decimal_totals_all_matching_rows(self):
        import json
        source = self.root / "budget.json"
        records = [{"category": "Food", "amount": "0.10", "budget": "1.00"},
                   {"category": "Food", "amount": "0.20", "budget": "2.00"},
                   {"category": "Other", "amount": "99.00", "budget": "99.00"},
                   {"category": "Food", "amount": None, "budget": "0.00"}]
        source.write_text(json.dumps(records), encoding="utf-8")
        original = source.read_bytes()
        options = dict(contains="Food", column="category", total1="amount", total2="budget")
        result = dataframe_preview(self.files, source.name, **options)
        self.assertIn("<strong>0.30</strong>", result)
        self.assertIn("<strong>3.00</strong>", result)
        exported = json.loads(dataframe_preview(self.files, source.name, export="json", **options))
        self.assertEqual(len(exported), 4)
        self.assertEqual(exported[-1]["__summary__"], "Total")
        self.assertEqual(exported[-1]["amount"], "0.30")
        self.assertEqual(source.read_bytes(), original)

    def test_totals_beyond_preview_limit(self):
        self.source.write_text("Amount\n" + "0.01\n" * 1100, encoding="utf-8")
        result = dataframe_preview(self.files, "data.csv", total1="Amount", page=2)
        self.assertIn("<strong>11.00</strong>", result)
        self.assertIn("1100 matching rows of 1100", result)

    def test_total_invalid_numeric_value(self):
        with self.assertRaises(BrowserError):
            dataframe_preview(self.files, "data.csv", total1="Name")
