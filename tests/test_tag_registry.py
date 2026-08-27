#!/usr/bin/env python3
"""Cross-drawing tag registry: keep FUNCTION-header instance on collision."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dwg_reader.dwg_tag_registry import (
    TagRegistry,
    apply_registry_from_output_dir,
    apply_registry_to_rows,
    compute_winners,
    dedupe_hierarchies,
    row_tag_and_role,
)
from dwg_reader.io import write_csv_rows
from dwg_reader.models import HIERARCHY_COLUMNS


def _row(fn="", eq="", sub="", desc=""):
    return {
        "SUB-PROCESS": "BR1",
        "FUNCTION": fn,
        "EQUIPMENT": eq,
        "SUB-EQUIPMENT": sub,
        "MASK": "",
        "DESCRIPTION": desc,
    }


class RowRoleTests(unittest.TestCase):
    def test_function_header(self) -> None:
        self.assertEqual(row_tag_and_role(_row(fn="35-24L009")), ("35-24L009", "FUNCTION"))

    def test_equipment(self) -> None:
        self.assertEqual(row_tag_and_role(_row(eq="35-24-095")), ("35-24-095", "EQUIPMENT"))

    def test_sub_equipment(self) -> None:
        self.assertEqual(row_tag_and_role(_row(sub="35-24-207")), ("35-24-207", "SUB-EQUIPMENT"))


class DedupeHierarchiesTests(unittest.TestCase):
    def test_function_header_beats_sub_equipment(self) -> None:
        drawing_a = [
            _row(fn="35-24L001"),
            _row(eq="35-24L009", desc="as child"),
        ]
        drawing_b = [
            _row(fn="35-24L009", desc="header"),
            _row(eq="35-24-189"),
        ]
        result = dedupe_hierarchies([("sheet-a", drawing_a), ("sheet-b", drawing_b)])
        a_tags = {row_tag_and_role(r)[0] for r in result["sheet-a"]}
        b_tags = {row_tag_and_role(r)[0] for r in result["sheet-b"]}
        self.assertNotIn("35-24L009", a_tags)
        self.assertIn("35-24L009", b_tags)
        self.assertIn("35-24L001", a_tags)
        self.assertIn("35-24-189", b_tags)

    def test_equipment_beats_sub_equipment(self) -> None:
        a = [_row(fn="35-24L001"), _row(sub="35-24-095")]
        b = [_row(fn="35-24L002"), _row(eq="35-24-095")]
        result = dedupe_hierarchies([("a", a), ("b", b)])
        self.assertNotIn("35-24-095", {row_tag_and_role(r)[0] for r in result["a"]})
        self.assertIn("35-24-095", {row_tag_and_role(r)[0] for r in result["b"]})

    def test_equal_rank_keeps_first_drawing(self) -> None:
        a = [_row(fn="35-24L001"), _row(eq="35-24-095")]
        b = [_row(fn="35-24L002"), _row(eq="35-24-095")]
        result = dedupe_hierarchies([("a", a), ("b", b)])
        self.assertIn("35-24-095", {row_tag_and_role(r)[0] for r in result["a"]})
        self.assertNotIn("35-24-095", {row_tag_and_role(r)[0] for r in result["b"]})


class SequentialRegistryTests(unittest.TestCase):
    def test_later_function_header_takes_over_claim(self) -> None:
        registry = TagRegistry()
        first = apply_registry_to_rows(
            [_row(fn="35-24L001"), _row(eq="35-24L009")],
            drawing="sheet-a",
            registry=registry,
        )
        self.assertIn("35-24L009", {row_tag_and_role(r)[0] for r in first})
        second = apply_registry_to_rows(
            [_row(fn="35-24L009")],
            drawing="sheet-b",
            registry=registry,
        )
        self.assertEqual([row_tag_and_role(r)[0] for r in second], ["35-24L009"])
        self.assertEqual(registry.claims["35-24L009"]["drawing"], "sheet-b")
        self.assertEqual(registry.claims["35-24L009"]["role"], "FUNCTION")

    def test_later_sub_equipment_is_dropped(self) -> None:
        registry = TagRegistry()
        apply_registry_to_rows([_row(fn="35-24L009")], drawing="sheet-a", registry=registry)
        later = apply_registry_to_rows(
            [_row(fn="35-24L001"), _row(sub="35-24L009")],
            drawing="sheet-b",
            registry=registry,
        )
        self.assertNotIn("35-24L009", {row_tag_and_role(r)[0] for r in later})
        self.assertIn("35-24L001", {row_tag_and_role(r)[0] for r in later})


class OutputDirRegistryTests(unittest.TestCase):
    def test_recompute_winners_from_existing_csvs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            write_csv_rows(
                out / "SheetA.hierarchy_orchestrator.csv",
                [_row(fn="35-24L001"), _row(eq="35-24L009", desc="child")],
                HIERARCHY_COLUMNS,
            )
            current = [_row(fn="35-24L009", desc="header"), _row(eq="35-24-189")]
            filtered = apply_registry_from_output_dir(
                current, drawing="SheetB", out_dir=out
            )
            tags = {row_tag_and_role(r)[0] for r in filtered}
            self.assertIn("35-24L009", tags)
            self.assertIn("35-24-189", tags)
            saved = TagRegistry.load(out / "tag_registry.json")
            self.assertEqual(saved.claims["35-24L009"]["drawing"], "SheetB")
            self.assertEqual(saved.claims["35-24L009"]["role"], "FUNCTION")


class WinnersTests(unittest.TestCase):
    def test_compute_winners_picks_function(self) -> None:
        winners = compute_winners(
            [
                ("a", [_row(eq="35-24L009")]),
                ("b", [_row(fn="35-24L009")]),
            ]
        )
        self.assertEqual(winners["35-24L009"]["drawing"], "b")
        self.assertEqual(winners["35-24L009"]["role"], "FUNCTION")


if __name__ == "__main__":
    unittest.main()
