#!/usr/bin/env python3
"""Unit tests for per-tag valve locate, parent inference, and cache-backed export."""

from __future__ import annotations

import unittest

from dwg_floc_context import apply_sop_valve_type, combine_valve_type, infer_valve_type, is_valve_equipment
from dwg_valve_classify import (
    drain_below_valve,
    locate_valve,
    parse_type_tokens,
    pick_parent_fn,
)
from export_sap_equipment import build_equipment_rows


class ParseTypeTokensTests(unittest.TestCase):
    def test_drn_nc(self) -> None:
        self.assertEqual(parse_type_tokens('{"type": "DRN NC"}'), "DRN NC")

    def test_av_m_not_split_into_av(self) -> None:
        self.assertEqual(parse_type_tokens("AV-M"), "AV-M")
        self.assertEqual(parse_type_tokens("AVM"), "AV-M")

    def test_unknown_empty(self) -> None:
        self.assertEqual(parse_type_tokens("UNKNOWN"), "")

    def test_plain_hv(self) -> None:
        self.assertEqual(parse_type_tokens("HV"), "HV")

    def test_av_drops_nc_no(self) -> None:
        self.assertEqual(parse_type_tokens("AV NC"), "AV")
        self.assertEqual(parse_type_tokens("AV NO HV"), "AV")
        self.assertEqual(parse_type_tokens("AV-M NC"), "AV-M")

    def test_hand_drain_keeps_nc(self) -> None:
        self.assertEqual(parse_type_tokens("DRN NC"), "DRN NC")


class AnnotateCropTests(unittest.TestCase):
    def test_writes_marked_png(self) -> None:
        import tempfile
        from pathlib import Path

        from PIL import Image

        from dwg_valve_classify import annotate_valve_crop

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "35-24-001.png"
            Image.new("RGB", (80, 80), (0, 0, 0)).save(src)
            marked = annotate_valve_crop(src, "35-24-001")
            self.assertTrue(marked.exists())
            self.assertGreater(marked.stat().st_size, 0)


class InferAvMTests(unittest.TestCase):
    def test_av_m_beats_av(self) -> None:
        self.assertEqual(infer_valve_type("35-24HV-548", "35-24HV-548 ISOL VLV AV-M"), "AV-M")

    def test_av_still_works(self) -> None:
        self.assertEqual(infer_valve_type("35-24HV-548", "35-24HV-548 ISOL VLV AV"), "AV")


class NumericDrainDetectionTests(unittest.TestCase):
    def test_drn_without_vlv_is_valve(self) -> None:
        self.assertTrue(is_valve_equipment("35-24-161", "35-24-161 DISCH DRN 001-80"))

    def test_spool_text_is_not_valve_without_cad(self) -> None:
        self.assertFalse(is_valve_equipment("35-24-137", "35-24-137 PP-250 CONVEYOR SPOOL"))

    def test_plain_line_not_valve(self) -> None:
        self.assertFalse(is_valve_equipment("35-24-095", "LN 35-24-095 PRESS PLPR PP-200"))


class LocateValveTests(unittest.TestCase):
    def test_snaps_to_nearby_insert(self) -> None:
        texts = {"35-24-137": {"x": 1801.9, "y": 208.7, "layer": "P-VALVEPOS"}}
        inserts = [{"x": 1808.5, "y": 207.5, "layer": "P-VALVEPOS", "name": "PPI_0900A"}]
        loc = locate_valve("35-24-137", text_locations=texts, valve_inserts=inserts)
        self.assertIsNotNone(loc)
        assert loc is not None
        self.assertTrue(loc["is_valve"])
        self.assertEqual(loc["x"], 1808.5)
        self.assertEqual(loc["layer"], "P-VALVEPOS")

    def test_missing_text_returns_none(self) -> None:
        self.assertIsNone(locate_valve("35-24-999", text_locations={}, valve_inserts=[]))


class DrainParentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.functions = [
            {"tag": "35-24L006", "x": 1817.5, "y": 287.5, "kind": "equipment", "description": "BROKE CONVEYOR 3"},
            {"tag": "35-24L005", "x": 1715.0, "y": 272.5, "kind": "equipment", "description": "REEL PULPER"},
            {"tag": "35-24P507", "x": 1875.0, "y": 227.5, "kind": "equipment", "description": "BROKE CONVEYOR 3 PMP"},
        ]
        # Valve 137 CAD point
        self.xy = (1801.96, 208.77)

    def test_drain_moves_off_conveyor_to_pulper(self) -> None:
        parent = pick_parent_fn(
            x=self.xy[0],
            y=self.xy[1],
            hierarchy_fn="35-24L006",
            functions=self.functions,
            valve_type="DRN NC",
        )
        self.assertEqual(parent, "35-24L005")

    def test_non_drain_keeps_hierarchy_parent(self) -> None:
        parent = pick_parent_fn(
            x=self.xy[0],
            y=self.xy[1],
            hierarchy_fn="35-24L006",
            functions=self.functions,
            valve_type="HV",
        )
        self.assertEqual(parent, "35-24L006")

    def test_drain_keeps_pulper_hierarchy_parent(self) -> None:
        parent = pick_parent_fn(
            x=self.xy[0],
            y=self.xy[1],
            hierarchy_fn="35-24L005",
            functions=self.functions,
            valve_type="DRN NC",
        )
        self.assertEqual(parent, "35-24L005")


class CacheBackedExportTests(unittest.TestCase):
    def test_137_from_cache_without_vlv(self) -> None:
        rows = [
            {"FUNCTION": "35-24L006", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-137", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24-137 PP-250 CONVEYOR SPOOL"},
        ]
        cache = {
            "35-24-137": {
                "type": "DRN NC",
                "fn": "35-24L005",
                "layer": "P-VALVEPOS",
                "is_valve": True,
                "source": "vision",
            }
        }
        out = build_equipment_rows(rows, valve_cache=cache)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["EQKTX"], "HV 35-24-137 35-24L005 DRN NC")
        self.assertIn("35-24L005", out[0]["TPLNR"])
        self.assertNotIn("35-24L006", out[0]["TPLNR"])

    def test_cad_layer_marks_numeric_tag_as_valve(self) -> None:
        rows = [
            {"FUNCTION": "35-24L001", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-207", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24-207"},
        ]
        cache = {
            "35-24-207": {
                "type": "",
                "fn": "35-24L001",
                "layer": "P-VALVEPOS",
                "is_valve": True,
                "source": "cad_layer",
            }
        }
        out = build_equipment_rows(rows, valve_cache=cache)
        self.assertTrue(out[0]["EQKTX"].startswith("HV 35-24-207"))

    def test_vision_nc_picks_up_fls_from_description(self) -> None:
        rows = [
            {"FUNCTION": "35-24P512", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": ""},
            {
                "FUNCTION": "",
                "EQUIPMENT": "35-24-209",
                "SUB-EQUIPMENT": "",
                "DESCRIPTION": "35-24-209 FLSH VLV FLS",
            },
        ]
        cache = {
            "35-24-209": {
                "type": "NC",
                "fn": "35-24P512",
                "layer": "P-VALVEPOS",
                "is_valve": True,
                "source": "vision",
            }
        }
        out = build_equipment_rows(rows, valve_cache=cache)
        self.assertEqual(out[0]["EQKTX"], "HV 35-24-209 35-24P512 NC FLS")


class CombineFlushingTests(unittest.TestCase):
    def test_adds_fls_to_white_nc_body(self) -> None:
        self.assertEqual(combine_valve_type("NC", "35-24-209 FLSH VLV FLS"), "NC FLS")

    def test_flushing_word(self) -> None:
        self.assertEqual(infer_valve_type("35-24-1105", "FLUSHING VLV"), "FLS")

    def test_does_not_duplicate(self) -> None:
        self.assertEqual(combine_valve_type("NC FLS", "VLV FLS"), "NC FLS")

    def test_av_plus_desc_nc_stays_av(self) -> None:
        self.assertEqual(combine_valve_type("AV", "LVL VLV AV NC"), "AV")

    def test_sop_av_strips_running_condition(self) -> None:
        self.assertEqual(apply_sop_valve_type("AV NC NO"), "AV")
        self.assertEqual(apply_sop_valve_type("DRN NC"), "DRN NC")


class DrainBelowTests(unittest.TestCase):
    def test_marker_under_valve(self) -> None:
        self.assertTrue(drain_below_valve(1808.5, 207.5, [(1810.0, 140.0)]))

    def test_marker_beside_is_not_drain(self) -> None:
        self.assertFalse(drain_below_valve(1808.5, 207.5, [(1810.0, 210.0)]))


if __name__ == "__main__":
    unittest.main()
