#!/usr/bin/env python3
"""Tests for dwg_floc_standards — FLOC hierarchy lookup."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STANDARDS_DIR = ROOT / "standards"


class FlocStructureJsonTests(unittest.TestCase):
    """Validate sml_floc_structure.json content vs source xlsx expectations."""

    def _data(self) -> dict:
        with open(STANDARDS_DIR / "sml_floc_structure.json", encoding="utf-8") as f:
            return json.load(f)

    def test_required_top_level_keys(self) -> None:
        data = self._data()
        for key in ("meta", "lines", "processes", "sub_processes"):
            self.assertIn(key, data)

    def test_known_lines_present(self) -> None:
        lines = self._data()["lines"]
        self.assertIn("PM03", lines)
        self.assertIn("TM01", lines)
        self.assertEqual(lines["PM03"], "PAPER MACHINE 3")
        self.assertEqual(lines["TM01"], "TISSUE MACHINE 1")

    def test_known_named_processes_present(self) -> None:
        procs = self._data()["processes"]
        self.assertEqual(procs["BR"], "BROKE SYSTEM")
        self.assertEqual(procs["SP"], "STOCK PREP")
        self.assertEqual(procs["AF"], "APPROACH FLOW")
        self.assertEqual(procs["SC"], "STEAM AND CONDENSATE SYSTEMS")
        self.assertEqual(procs["VS"], "VACUUM SYSTEM")
        self.assertEqual(procs["WS"], "WATER SYSTEMS")

    def test_known_sub_processes_present(self) -> None:
        subs = self._data()["sub_processes"]
        self.assertEqual(subs["BHS"], "BALE HANDLING")
        self.assertEqual(subs["IA1"], "INSTRUMENT AIR")
        self.assertEqual(subs["AT1"], "ANAEROBIC TREATMENT 1")
        self.assertEqual(subs["WM1"], "FRESH WTR")   # xlsx stores abbreviated form
        self.assertEqual(subs["SW1"], "SEALING WATER")

    def test_processes_count(self) -> None:
        # 74 named processes confirmed from xlsx
        self.assertEqual(len(self._data()["processes"]), 74)

    def test_sub_processes_count(self) -> None:
        # 126 registered sub-processes from xlsx
        self.assertEqual(len(self._data()["sub_processes"]), 126)


class FlocStandardsLookupTests(unittest.TestCase):
    """Unit tests for dwg_floc_standards lookup functions."""

    def setUp(self) -> None:
        from dwg_reader.dwg_floc_standards import lookup_line, lookup_process, lookup_sub_process, is_valid_line
        self.line = lookup_line
        self.process = lookup_process
        self.sub = lookup_sub_process
        self.valid_line = is_valid_line

    def test_lookup_line_pm03(self) -> None:
        self.assertEqual(self.line("PM03"), "PAPER MACHINE 3")

    def test_lookup_line_tm01(self) -> None:
        self.assertEqual(self.line("TM01"), "TISSUE MACHINE 1")

    def test_lookup_line_unknown_returns_empty(self) -> None:
        self.assertEqual(self.line("XX99"), "")

    def test_lookup_line_empty_input(self) -> None:
        self.assertEqual(self.line(""), "")

    def test_lookup_process_br(self) -> None:
        self.assertEqual(self.process("BR"), "BROKE SYSTEM")

    def test_lookup_process_sp(self) -> None:
        self.assertEqual(self.process("SP"), "STOCK PREP")

    def test_lookup_process_unnamed_returns_empty(self) -> None:
        # WW is a valid 2-letter code but has no name in V3
        self.assertEqual(self.process("WW"), "")

    def test_lookup_sub_process_bhs(self) -> None:
        self.assertEqual(self.sub("BHS"), "BALE HANDLING")

    def test_lookup_sub_process_ia1(self) -> None:
        self.assertEqual(self.sub("IA1"), "INSTRUMENT AIR")

    def test_lookup_sub_process_at1(self) -> None:
        self.assertEqual(self.sub("AT1"), "ANAEROBIC TREATMENT 1")

    def test_lookup_sub_process_new_returns_empty(self) -> None:
        # BR1, WW1 etc. are new sub-processes not yet in V3 Level 4
        self.assertEqual(self.sub("BR1"), "")
        self.assertEqual(self.sub("WW1"), "")

    def test_is_valid_line_pm03(self) -> None:
        self.assertTrue(self.valid_line("PM03"))

    def test_is_valid_line_unknown(self) -> None:
        self.assertFalse(self.valid_line("ZZ99"))


class FlocStandardsIntegrationTests(unittest.TestCase):
    """Verify FLOC standards are wired into export_sap_floc build_floc_rows."""

    def test_build_floc_rows_uses_floc_standards_for_line_name(self) -> None:
        from dwg_reader.export_sap_floc import build_floc_rows

        ctx = {
            "plant": "5001",
            "line_code": "TM01",
            "process_code": "BR",
            "sub_process": "BR1",
            # deliberately omit line_name and process_name — standards should fill them
        }
        rows = build_floc_rows([], ctx=ctx)
        by_tplnr = {r["TPLNR"]: r for r in rows}
        line_row = by_tplnr.get("5001-TM01")
        self.assertIsNotNone(line_row, "Line row must exist")
        # normalize_pltxt abbreviates MACHINE → MACH per SML Abbreviation Standard
        self.assertEqual(line_row["PLTXT"], "TISSUE MACH 1")

    def test_build_floc_rows_uses_floc_standards_for_process_name(self) -> None:
        from dwg_reader.export_sap_floc import build_floc_rows

        ctx = {
            "plant": "5001",
            "line_code": "PM03",
            "process_code": "SP",
            "sub_process": "SP1",
        }
        rows = build_floc_rows([], ctx=ctx)
        by_tplnr = {r["TPLNR"]: r for r in rows}
        process_row = by_tplnr.get("5001-PM03-SP")
        self.assertIsNotNone(process_row, "Process row must exist")
        self.assertEqual(process_row["PLTXT"], "STOCK PREP")

    def test_build_floc_rows_explicit_name_overrides_standards(self) -> None:
        from dwg_reader.export_sap_floc import build_floc_rows

        ctx = {
            "plant": "5001",
            "line_code": "TM01",
            "process_code": "SP",
            "sub_process": "BHS",
            "line_name": "MY CUSTOM LINE",
            "process_name": "MY CUSTOM PROCESS",
        }
        rows = build_floc_rows([], ctx=ctx)
        by_tplnr = {r["TPLNR"]: r for r in rows}
        line_row = by_tplnr.get("5001-TM01")
        # normalize_pltxt abbreviates LINE → LN per SML Abbreviation Standard
        self.assertEqual(line_row["PLTXT"], "MY CUSTOM LN")
        process_row = by_tplnr.get("5001-TM01-SP")
        # normalize_pltxt abbreviates PROCESS → PROS per SML Abbreviation Standard
        self.assertEqual(process_row["PLTXT"], "MY CUSTOM PROS")

    def test_sub_process_row_uses_registered_sub_process_name(self) -> None:
        from dwg_reader.export_sap_floc import build_floc_rows

        ctx = {
            "plant": "5001",
            "line_code": "TM01",
            "process_code": "SP",
            "sub_process": "BHS",
            # BHS = BALE HANDLING in FLOC V3 Level 4
        }
        rows = build_floc_rows([], ctx=ctx)
        by_tplnr = {r["TPLNR"]: r for r in rows}
        sub_row = by_tplnr.get("5001-TM01-SP-BHS")
        self.assertIsNotNone(sub_row, "Sub-process row must exist")
        # normalize_pltxt abbreviates HANDLING → HDLG per SML Abbreviation Standard
        self.assertEqual(sub_row["PLTXT"], "BALE HDLG")


class KsdFlocContextTests(unittest.TestCase):
    """Verify all 23 KSD DWGs have proper FLOC context entries."""

    def _ctx(self) -> dict:
        with open(STANDARDS_DIR / "floc_context_map.json", encoding="utf-8") as f:
            return json.load(f)

    def test_all_ksd_entries_present(self) -> None:
        ctx = self._ctx()
        ksd_stems = [k for k, v in ctx.items() if v.get("ecosystem") == "ksd"]
        self.assertEqual(len(ksd_stems), 23, f"Expected 23 KSD entries, got {len(ksd_stems)}: {ksd_stems}")

    def test_ksd_entries_have_tm01_line(self) -> None:
        ctx = self._ctx()
        for stem, entry in ctx.items():
            if entry.get("ecosystem") == "ksd":
                self.assertEqual(entry["line_code"], "TM01", f"{stem} must be TM01")

    def test_ksd_bale_handling_entry(self) -> None:
        ctx = self._ctx()
        entry = ctx.get("KSDM160104102_04_SH01_Bale handling_C")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["ecosystem"], "ksd")
        self.assertEqual(entry["process_code"], "SP")
        self.assertEqual(entry["sub_process"], "BHS")

    def test_ksd_vacuum_system_entry(self) -> None:
        ctx = self._ctx()
        entry = ctx.get("KSDM160104106_08_SH01_Vacuum system_C")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["process_code"], "VS")
        self.assertEqual(entry["sub_process"], "VU1")

    def test_ksd_steam_condensate_entry(self) -> None:
        ctx = self._ctx()
        entry = ctx.get("KSDM160104107_09_SH01_Steam and condensate system_C")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["process_code"], "SC")
        self.assertEqual(entry["sub_process"], "SC1")

    def test_ksd_sealing_water_uses_sw1(self) -> None:
        ctx = self._ctx()
        entry = ctx.get("KSDM160104112_05_SH01_Sealing water system_C")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["sub_process"], "SW1")

    def test_ksd_mill_air_uses_ia1(self) -> None:
        ctx = self._ctx()
        entry = ctx.get("KSDM160104108_06_SH01_Mill air system_C")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["process_code"], "IA")
        self.assertEqual(entry["sub_process"], "IA1")

    def test_all_ksd_entries_have_required_fields(self) -> None:
        ctx = self._ctx()
        required = {"ecosystem", "plant", "line_code", "process_code", "sub_process",
                    "site_name", "line_name", "process_name"}
        for stem, entry in ctx.items():
            if entry.get("ecosystem") != "ksd":
                continue
            missing = required - set(entry)
            self.assertFalse(missing, f"{stem} missing fields: {missing}")

    def test_total_context_entries_covers_index(self) -> None:
        ctx = self._ctx()
        # Broke System is a working-copy extra; index stems must all be mapped.
        self.assertGreaterEqual(len(ctx), 84)
        self.assertIn("Broke System", ctx)
        self.assertIn("RAU6401403_03_FLOW_DIAGRAM_OCPRO", ctx)

    def test_every_index_filename_stem_is_mapped(self) -> None:
        """F-04: every stem in sml_dwg_index must have a floc_context_map entry."""
        import csv

        ctx = self._ctx()
        index_path = ROOT / "resources" / "sml_dwg_index_260806 (1).csv"
        self.assertTrue(index_path.is_file(), f"missing {index_path}")
        stems: set[str] = set()
        with index_path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("filename") or "").strip()
                if not name:
                    continue
                stems.add(Path(name).stem)
        missing = sorted(stems - set(ctx))
        self.assertEqual(missing, [], f"index stems not in floc_context_map.json: {missing}")
        extra_ok = {"Broke System"}
        extra = set(ctx) - stems
        unexpected = sorted(extra - extra_ok)
        self.assertEqual(
            unexpected, [],
            f"map keys not in index (besides {sorted(extra_ok)}): {unexpected}",
        )


class AbbreviationsCompleteTests(unittest.TestCase):
    """Verify sml_abbreviations.json matches xlsx."""

    def _abbrev_json(self) -> dict:
        with open(STANDARDS_DIR / "sml_abbreviations.json", encoding="utf-8") as f:
            return json.load(f)

    def test_total_abbreviations(self) -> None:
        data = self._abbrev_json()
        # 384 entries in xlsx (381 from initial parse — both counts depending on xlsx read mode)
        self.assertGreaterEqual(len(data["abbreviations"]), 380)

    def test_missing_entries_now_present(self) -> None:
        abbrevs = self._abbrev_json()["abbreviations"]
        # Spot-check previously missing entries
        self.assertEqual(abbrevs.get("BALE HANDLING"), None)  # not a word→abbr entry; check actual ones
        self.assertEqual(abbrevs.get("WHITE WATER"), "WW")
        self.assertEqual(abbrevs.get("YANKEE DRYER"), "YD")
        self.assertEqual(abbrevs.get("SEALING WATER"), None)  # SEALING is in xlsx, SEALING WATER is not a row
        self.assertEqual(abbrevs.get("NORMALLY OPEN"), "NO")
        self.assertEqual(abbrevs.get("NORMALLY CLOSED"), "NC")
        self.assertEqual(abbrevs.get("STEAM TRAP"), "ST")
        self.assertEqual(abbrevs.get("MOTOR"), "MTR")  # xlsx has MOTOR → MTR
        self.assertEqual(abbrevs.get("AGITATOR"), "AGI")

    def test_agitator_abbreviation_unchanged(self) -> None:
        self.assertEqual(self._abbrev_json()["abbreviations"]["AGITATOR"], "AGI")

    def test_pump_abbreviation_unchanged(self) -> None:
        self.assertEqual(self._abbrev_json()["abbreviations"]["PUMP"], "PMP")


if __name__ == "__main__":
    unittest.main()
