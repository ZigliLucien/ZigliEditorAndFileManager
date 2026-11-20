"""Regression: fast JSON/JSONL record navigation without full path parsing."""
import json
import unittest

from zefm.editor.json_records import record_bounds, record_index, adjacent_record


class RecordOffsetTests(unittest.TestCase):
    def test_jsonl_and_multiline_records(self):
        text = '{"a": 1}\n{\n "b": [1, 2]\n}\n{"c": 3}\n'
        bounds = record_bounds(text)
        self.assertEqual(len(bounds), 3)
        self.assertEqual([text[a:b] for a, b in bounds],
                         ['{"a": 1}', '{\n "b": [1, 2]\n}', '{"c": 3}'])
        self.assertEqual(record_index(bounds, bounds[1][0]), 1)
        self.assertEqual(adjacent_record(bounds, bounds[1][0], 1), bounds[2][0])
        self.assertEqual(adjacent_record(bounds, bounds[1][0], -1), bounds[0][0])
        self.assertIsNone(adjacent_record(bounds, bounds[2][0], 1))

    def test_large_stream(self):
        data = "".join(json.dumps({"id": i}) + "\n" for i in range(10000))
        bounds = record_bounds(data)
        self.assertEqual(len(bounds), 10000)
        self.assertEqual(record_index(bounds, bounds[-1][0]), 9999)

    def test_invalid_json(self):
        with self.assertRaises(json.JSONDecodeError):
            record_bounds('{"a":1}\nnot-json')
        with self.assertRaises(json.JSONDecodeError):
            record_bounds("   ")


if __name__ == "__main__":
    unittest.main()
