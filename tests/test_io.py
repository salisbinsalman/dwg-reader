#!/usr/bin/env python3
"""Unit tests for dwg_reader.io JSON/CSV helpers."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from dwg_reader.io import (
    cell,
    json_safe,
    load_json,
    read_csv_rows,
    write_csv_rows,
    write_json,
)
from dwg_reader.models import HIERARCHY_COLUMNS


class CellTests(unittest.TestCase):
    def test_cell_strips_and_empty_nan(self) -> None:
        self.assertEqual(cell("  abc  "), "abc")
        self.assertEqual(cell(None), "")
        self.assertEqual(cell("nan"), "")
        self.assertEqual(cell("NaN"), "")
        self.assertEqual(cell(""), "")

    def test_cell_treats_zero_as_empty_matching_export_norm(self) -> None:
        # Historical _norm used `value or ""`, so 0 collapses to empty.
        self.assertEqual(cell(0), "")


class JsonTests(unittest.TestCase):
    def test_write_and_load_json_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "nested" / "out.json"
            write_json(path, {"a": 1, "b": ["x", None]})
            data = load_json(path)
            self.assertEqual(data["a"], 1)
            self.assertEqual(data["b"], ["x", None])

    def test_json_safe_nested_dict_and_tuple(self) -> None:
        out = json_safe({"k": (1, 2), "ok": True})
        json.dumps(out)
        self.assertEqual(out["k"], [1, 2])

    def test_json_safe_xy_object(self) -> None:
        class Pt:
            x = 1.5
            y = 2.5
            z = 0.0

        self.assertEqual(json_safe(Pt()), [1.5, 2.5, 0.0])

    def test_load_json_missing_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_json(Path("/tmp/dwg-reader-missing-does-not-exist.json"))


class CsvTests(unittest.TestCase):
    def test_write_read_hierarchy_csv_roundtrip(self) -> None:
        rows = [
            {
                "SUB-PROCESS": "BR1",
                "FUNCTION": "35-24L009",
                "EQUIPMENT": "",
                "SUB-EQUIPMENT": "",
                "MASK": "5001-PM03-BR-BR1-35-24L009",
                "DESCRIPTION": "WINDER PULPER",
            },
            {
                "SUB-PROCESS": "",
                "FUNCTION": "",
                "EQUIPMENT": "35-24-009",
                "SUB-EQUIPMENT": "",
                "MASK": "35-24-009",
                "DESCRIPTION": "LN",
            },
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "h.csv"
            write_csv_rows(path, rows, HIERARCHY_COLUMNS)
            loaded = read_csv_rows(path)
            self.assertEqual(loaded[0]["FUNCTION"], "35-24L009")
            self.assertEqual(loaded[1]["EQUIPMENT"], "35-24-009")
            self.assertEqual(loaded[0]["DESCRIPTION"], "WINDER PULPER")

    def test_read_csv_missing_ok(self) -> None:
        self.assertEqual(read_csv_rows(Path("/tmp/no-such-hierarchy.csv")), [])

    def test_read_csv_missing_raises_when_not_ok(self) -> None:
        with self.assertRaises(FileNotFoundError):
            read_csv_rows(Path("/tmp/no-such-hierarchy.csv"), missing_ok=False)

    def test_write_csv_drops_extra_keys(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "h.csv"
            write_csv_rows(path, [{"FUNCTION": "A", "NOISE": "x"}], ["FUNCTION"])
            loaded = read_csv_rows(path)
            self.assertEqual(loaded, [{"FUNCTION": "A"}])

    def test_read_csv_normalizes_nan_cells(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "h.csv"
            path.write_text("FUNCTION,EQUIPMENT\n35-24L009,nan\n", encoding="utf-8")
            loaded = read_csv_rows(path)
            self.assertEqual(loaded[0]["EQUIPMENT"], "")


if __name__ == "__main__":
    unittest.main()
