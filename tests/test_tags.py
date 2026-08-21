#!/usr/bin/env python3
"""Unit tests for dwg_reader.tags."""

from __future__ import annotations

import unittest

from dwg_reader.tags import normalize_tag, parse_line_number


class NormalizeTagTests(unittest.TestCase):
    def test_normalize_tag_uppercases_and_strips_spaces(self) -> None:
        self.assertEqual(normalize_tag(" 35-24l009 "), "35-24L009")

    def test_normalize_tag_shortens_full_pipe_class(self) -> None:
        self.assertEqual(normalize_tag("35-24-009-PP-600-E10H2A"), "35-24-009")

    def test_normalize_tag_keeps_short_line_id(self) -> None:
        self.assertEqual(normalize_tag("35-24-192"), "35-24-192")

    def test_normalize_tag_empty(self) -> None:
        self.assertEqual(normalize_tag(""), "")

    def test_normalize_tag_equipment_not_collapsed(self) -> None:
        self.assertEqual(normalize_tag("35-24P519"), "35-24P519")


class ParseLineNumberTests(unittest.TestCase):
    def test_parse_line_number_full_spec(self) -> None:
        parsed = parse_line_number("35-24-009-PP-600-E10H2A")
        self.assertTrue(parsed["parsed"])
        self.assertEqual(parsed["plant_area"], "35-24")
        self.assertEqual(parsed["line_seq"], "009")
        self.assertEqual(parsed["line_type"], "PP")

    def test_parse_line_number_dn_size(self) -> None:
        parsed = parse_line_number("DN50")
        self.assertTrue(parsed["parsed"])
        self.assertEqual(parsed["line_type"], "DN_SIZE")
        self.assertEqual(parsed["size"], "50")

    def test_parse_line_number_unparsed_text(self) -> None:
        parsed = parse_line_number("not a line")
        self.assertFalse(parsed["parsed"])
        self.assertEqual(parsed["line_number"], "NOT A LINE")

    def test_parse_line_number_optional_type_segment(self) -> None:
        parsed = parse_line_number("35-24-009-E10H2A")
        self.assertTrue(parsed["parsed"])


if __name__ == "__main__":
    unittest.main()
