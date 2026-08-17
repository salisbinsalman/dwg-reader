#!/usr/bin/env python3
"""Unit tests for SAP Equipment export (no Bedrock)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from export_sap_equipment import build_equipment_rows, write_equipment_workbook
from dwg_floc_context import format_line_eqktx, is_line_equipment_tag, normalize_pltxt
from dwg_object_type import classify_equipment, lookup


ROOT = Path(__file__).resolve().parent
HIERARCHY_CSV = ROOT / "outputs/Broke System.hierarchy_orchestrator.csv"


class ObjectTypeClassifierTests(unittest.TestCase):
    """Tests for dwg_object_type.classify_equipment."""

    def _cls(self, tag, desc):
        return classify_equipment(tag, desc)

    # --- tag prefix rules ---
    def test_level_controller_tag(self):
        # LC = Level Controller → 1204 INSTRUMENT LEVEL (not generic 1200)
        code, wc = self._cls("35-24LC-576", "35-24LC-576 LVL CTRL")
        self.assertEqual(code, "1204")
        self.assertEqual(wc, "")

    def test_control_valve_hv_tag(self):
        # HV = Hand Valve → 201 VALVE HAND
        code, wc = self._cls("35-24HV-626", "35-24HV-626 DN300 HND VLV")
        self.assertEqual(code, "201")
        self.assertEqual(wc, "MECH")

    def test_flow_valve_fv_tag(self):
        code, wc = self._cls("35-24FV-570", "35-24FV-570 FLOW VLV")
        self.assertEqual(code, "202")
        self.assertEqual(wc, "MECH")

    def test_switch_xs_tag(self):
        code, wc = self._cls("35-24XS-588", "35-24XS-588 MCS SIG")
        self.assertEqual(code, "1108")

    # --- description keyword rules ---
    def test_motor_keyword(self):
        code, wc = self._cls("35-24-001.1", "35-24-001.1 PRESS PLPR ROTOR 1 MTR")
        self.assertEqual(code, "1101")
        self.assertEqual(wc, "ELEC")

    def test_pump_keyword(self):
        code, wc = self._cls("35-24P519", "35-24P519 PMP")
        self.assertEqual(code, "701")
        self.assertEqual(wc, "MECH")

    def test_pulper_keyword(self):
        code, wc = self._cls("35-24L009", "35-24L009 BROKE ROLL PLPR")
        self.assertEqual(code, "2005")
        self.assertEqual(wc, "MECH")

    def test_hand_valve_keyword(self):
        code, wc = self._cls("35-24-207", "35-24-207 CIRC VLV 003-50")
        self.assertEqual(code, "201")
        self.assertEqual(wc, "MECH")

    def test_pipe_line_keyword(self):
        code, wc = self._cls("35-24-149", "35-24-149 WAA DN300 INLET LINE")
        self.assertEqual(code, "2100")
        self.assertEqual(wc, "MECH")

    def test_thickener_keyword(self):
        code, wc = self._cls("35-24L002", "35-24L002 BROKE THICKENER")
        self.assertEqual(code, "2009")
        self.assertEqual(wc, "MECH")

    # --- lookup helper ---
    def test_lookup(self):
        name, wc = lookup("701")
        self.assertEqual(name, "PUMP CENTRIFUGAL")
        self.assertEqual(wc, "MECH")

    def test_fallback(self):
        code, wc = classify_equipment("35-24-999", "35-24-999 UNKNOWN THING")
        self.assertEqual(code, "9999")
        self.assertEqual(wc, "")

    def test_pump_single_letter_tag(self):
        # "35-24P519" — single-letter no-dash format → P → 701 without needing PMP in description
        code, wc = self._cls("35-24P519", "35-24P519 OUTLET")
        self.assertEqual(code, "701")
        self.assertEqual(wc, "MECH")

    def test_motor_suffix_tag(self):
        # ".N" suffix convention marks motor sub-equipment even with a thin description
        code, wc = self._cls("35-24-001.1", "35-24-001.1 ROTOR 1")
        self.assertEqual(code, "1101")
        self.assertEqual(wc, "ELEC")

    def test_plpr_context_disambiguation(self):
        # PLPR in a child description is context (parent system name), not the equipment type
        code, wc = classify_equipment("35-24-095", "35-24-095 PRESS PLPR OUTLET PP-200")
        self.assertEqual(code, "2100")   # pipe line, not pulper
        self.assertEqual(wc, "MECH")
        code, _ = classify_equipment("35-24-101", "35-24-101 PRESS PLPR SUCT PP-150")
        self.assertEqual(code, "2100")
        # Motor on a pulper still classifies correctly (MTR rule fires first)
        code, wc = classify_equipment("35-24-001.1", "35-24-001.1 PRESS PLPR ROTOR 1 MTR")
        self.assertEqual(code, "1101")
        self.assertEqual(wc, "ELEC")


class FormatLineEqktxTests(unittest.TestCase):
    def test_review_examples(self) -> None:
        self.assertEqual(
            format_line_eqktx(
                "35-24-095",
                normalize_pltxt("35-24-095 PRESS PLPR PP-200 LINE"),
            ),
            "LN 35-24-095 PRESS PLPR PP-200",
        )
        self.assertEqual(
            format_line_eqktx(
                "35-24-096",
                normalize_pltxt("35-24-096 PRESS PLPR PP-900 LINE"),
            ),
            "LN 35-24-096 PRESS PLPR PP-900",
        )

    def test_is_line_equipment_tag(self) -> None:
        self.assertTrue(is_line_equipment_tag("35-24-095"))
        self.assertFalse(is_line_equipment_tag("35-24-001.1"))
        self.assertFalse(is_line_equipment_tag("35-24LC-576"))
        self.assertFalse(is_line_equipment_tag("35-24HV-548"))
        self.assertFalse(is_line_equipment_tag("35-24P519"))

    def test_idempotent_when_already_prefixed(self) -> None:
        text = "LN 35-24-095 PRESS PLPR PP-200"
        self.assertEqual(format_line_eqktx("35-24-095", text), text)

    def test_overflow_line_with_embedded_ln(self) -> None:
        self.assertEqual(
            format_line_eqktx("35-24-189", normalize_pltxt("35-24-189 LN OVFL")),
            "LN 35-24-189 OVFL",
        )

    def test_skips_valve_sub_equipment(self) -> None:
        text = normalize_pltxt("35-24-207 VLV ON 35-24-096")
        self.assertEqual(
            format_line_eqktx("35-24-207", text, hequi="35-24-096"),
            text,
        )

    def test_skips_valve_description_without_hequi(self) -> None:
        text = normalize_pltxt("35-24-234 VLV ON 35-24-093")
        self.assertEqual(format_line_eqktx("35-24-234", text), text)

    def test_applies_without_trailing_line_word(self) -> None:
        self.assertEqual(
            format_line_eqktx("35-24-149", "35-24-149 WAA DN300 INLET"),
            "LN 35-24-149 WAA DN300 INLET",
        )

    def test_max_length_40(self) -> None:
        long_desc = "35-24-095 " + "PRESS PLPR PP-200 EXTRA WORDS " * 3
        out = format_line_eqktx("35-24-095", normalize_pltxt(long_desc))
        self.assertLessEqual(len(out), 40)
        self.assertTrue(out.startswith("LN 35-24-095"))


class EquipmentExportTests(unittest.TestCase):
    def test_build_rows_hequi_and_posnr(self) -> None:
        rows = [
            {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24L009 BROKE ROLL PLPR"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-189", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24-189 LN OVFL"},
            {"FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": "35-24-194", "DESCRIPTION": "35-24-194 HV DRN"},
            {"FUNCTION": "", "EQUIPMENT": "35-24P519", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24P519 PMP"},
        ]
        out = build_equipment_rows(rows)
        self.assertEqual(len(out), 3)
        self.assertEqual(out[0]["EQUNR"], "35-24-189")
        self.assertEqual(out[0]["HEQUI"], "")
        self.assertEqual(out[0]["POSNR"], "0010")
        self.assertEqual(out[0]["TPLNR"], "5001-PM03-BR-BR1-35-24L009")
        self.assertEqual(out[0]["EQTYP"], "P")
        self.assertEqual(out[0]["EQART"], "9999")   # no keyword match → NOT CATEGORIZED
        self.assertEqual(out[0]["GEWRK"], "")
        self.assertEqual(out[0]["SWERK"], "5001")
        self.assertEqual(out[0]["ABCKZ"], "D")
        self.assertEqual(out[0]["INGRP"], "P01")
        self.assertLessEqual(len(out[0]["EQKTX"]), 40)
        # pump tag (35-24P519 PMP) → PUMP CENTRIFUGAL
        self.assertEqual(out[2]["EQART"], "701")
        self.assertEqual(out[2]["GEWRK"], "MECH")

        self.assertEqual(out[1]["EQUNR"], "35-24-194")
        self.assertEqual(out[1]["HEQUI"], "35-24-189")
        self.assertEqual(out[1]["POSNR"], "0010")

        self.assertEqual(out[2]["EQUNR"], "35-24P519")
        self.assertEqual(out[2]["HEQUI"], "")
        self.assertEqual(out[2]["POSNR"], "0020")

    def test_sub_equipment_posnr_resets_per_parent(self) -> None:
        """Review issue 3: subs reset POSNR; top-level continues separately."""
        rows = [
            {"FUNCTION": "35-24L001", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-095", "SUB-EQUIPMENT": "", "DESCRIPTION": "LINE A"},
            {"FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": "35-24LV2-576", "DESCRIPTION": "LVL VLV"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-096", "SUB-EQUIPMENT": "", "DESCRIPTION": "LINE B"},
            {"FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": "35-24-207", "DESCRIPTION": "VLV 1"},
            {"FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": "35-24-217", "DESCRIPTION": "VLV 2"},
            {"FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": "35-24-1105", "DESCRIPTION": "VLV 3"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-093", "SUB-EQUIPMENT": "", "DESCRIPTION": "LINE C"},
        ]
        out = build_equipment_rows(rows)
        by_tag = {r["EQUNR"]: r for r in out}
        self.assertEqual(by_tag["35-24-095"]["POSNR"], "0010")
        self.assertEqual(by_tag["35-24LV2-576"]["POSNR"], "0010")
        self.assertEqual(by_tag["35-24-096"]["POSNR"], "0020")
        self.assertEqual(by_tag["35-24-207"]["POSNR"], "0010")
        self.assertEqual(by_tag["35-24-217"]["POSNR"], "0020")
        self.assertEqual(by_tag["35-24-1105"]["POSNR"], "0030")
        self.assertEqual(by_tag["35-24-093"]["POSNR"], "0030")

    def test_line_eqktx_in_export(self) -> None:
        rows = [
            {"FUNCTION": "35-24L001", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-095", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24-095 PRESS PLPR PP-200 LINE"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-096", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24-096 PRESS PLPR PP-900 LINE"},
            {"FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": "35-24-207", "DESCRIPTION": "35-24-207 VLV ON 35-24-096"},
        ]
        out = build_equipment_rows(rows)
        by_tag = {r["EQUNR"]: r for r in out}
        self.assertEqual(by_tag["35-24-095"]["EQKTX"], "LN 35-24-095 PRESS PLPR PP-200")
        self.assertEqual(by_tag["35-24-096"]["EQKTX"], "LN 35-24-096 PRESS PLPR PP-900")
        self.assertFalse(by_tag["35-24-207"]["EQKTX"].startswith("LN "))

    def test_limit_functions(self) -> None:
        rows = [
            {"FUNCTION": "35-24L001", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-001.1", "SUB-EQUIPMENT": "", "DESCRIPTION": "MTR"},
            {"FUNCTION": "35-24L002", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-002.1", "SUB-EQUIPMENT": "", "DESCRIPTION": "MTR"},
        ]
        out = build_equipment_rows(rows, limit_functions=1)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["EQUNR"], "35-24-001.1")
        self.assertIn("35-24L001", out[0]["TPLNR"])

    def test_write_workbook(self) -> None:
        template = ROOT / "docs/examples/SML-Equipment Template RW.xlsx"
        self.assertTrue(template.exists())
        rows = build_equipment_rows(
            [
                {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": ""},
                {"FUNCTION": "", "EQUIPMENT": "35-24-189", "SUB-EQUIPMENT": "", "DESCRIPTION": "OVFL"},
            ]
        )
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "eq.xlsx"
            write_equipment_workbook(template, out, rows)
            self.assertTrue(out.exists())
            from openpyxl import load_workbook

            wb = load_workbook(out)
            self.assertIn("Equipment", wb.sheetnames)
            ws = wb["Equipment"]
            self.assertEqual(ws.cell(7, 2).value, "5001-PM03-BR-BR1-35-24L009")
            self.assertEqual(ws.cell(7, 3).value, "35-24-189")
            self.assertEqual(ws.cell(7, 7).value, "P")
            self.assertEqual(ws.cell(7, 8).value, "9999")  # "35-24-189 OVFL" → no match


class RealHierarchyLineEqktxTests(unittest.TestCase):
    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_all_numeric_line_equipment_prefixed_with_ln(self) -> None:
        import csv
        import re

        from export_sap_equipment import read_hierarchy_csv

        hierarchy = read_hierarchy_csv(HIERARCHY_CSV)
        out = build_equipment_rows(hierarchy, limit_functions=5)
        line_pat = re.compile(r"^35-24-\d+$")
        valve_markers = ("VLV", "VALVE", " HV", " FV", " LV", " ON 35-24-")

        missing_ln = []
        has_line_word = []
        for row in out:
            tag = row["EQUNR"]
            eqktx = row["EQKTX"]
            if not line_pat.match(tag):
                continue
            if any(m in eqktx for m in valve_markers):
                continue
            if not eqktx.startswith("LN "):
                missing_ln.append((tag, eqktx))
            if eqktx.endswith(" LINE") or eqktx.endswith(" LN"):
                has_line_word.append((tag, eqktx))

        self.assertEqual(missing_ln, [], msg=f"missing LN prefix: {missing_ln[:10]}")
        self.assertEqual(has_line_word, [], msg=f"trailing LINE/LN: {has_line_word[:10]}")

    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_l001_review_line_examples(self) -> None:
        out = build_equipment_rows(
            __import__("export_sap_equipment").read_hierarchy_csv(HIERARCHY_CSV),
            limit_functions=1,
        )
        by_tag = {r["EQUNR"]: r for r in out}
        self.assertEqual(by_tag["35-24-095"]["EQKTX"], "LN 35-24-095 PRESS PLPR PP-200")
        self.assertEqual(by_tag["35-24-096"]["EQKTX"], "LN 35-24-096 PRESS PLPR PP-900")
        self.assertFalse(by_tag["35-24-207"]["EQKTX"].startswith("LN "))


if __name__ == "__main__":
    unittest.main()
