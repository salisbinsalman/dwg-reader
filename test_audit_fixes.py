#!/usr/bin/env python3
"""Regression tests for audit-report fixes (FLOC bleed, pumps, hierarchy cleanup)."""

import unittest
from pathlib import Path

from dwg_floc_context import is_pump_equipment, is_pump_tag, is_valve_equipment, is_valve_tag
from dwg_pid_hierarchy_ai import rows_from_ai, title_context
from export_sap_equipment import _is_valid_equipment_tag
from run_hierarchy_orchestrator import (
    DEFAULT_HIERARCHY_FUNCTION_KINDS,
    _gor_code03_valve_type,
    _is_instrument_function_tag,
    load_inventory_functions,
    sanitize_hierarchy_rows,
)


class TitleContextTests(unittest.TestCase):
    def test_occ_drawing_uses_floc_map_not_br1(self) -> None:
        occ = Path("inputs/Reference/OCC_PID/STOD206340.10 OCC Pulping line 1.dwg")
        ctx = title_context({"title_block": [{"TITLE1": "OCC PULPING LINE 1"}]}, occ.stem, occ)
        self.assertEqual(ctx["sub_process"], "OC1")
        self.assertEqual(ctx["process_code"], "OC")
        self.assertNotIn("BR1", ctx["sub_process"])

    def test_broke_system_still_uses_br1(self) -> None:
        broke = Path("inputs/Broke System.dwg")
        ctx = title_context({"title_block": [{"TITLE1": "BROKE SYSTEM"}]}, broke.stem, broke)
        self.assertEqual(ctx["sub_process"], "BR1")
        self.assertEqual(ctx["process_code"], "BR")

    def test_ai_sub_process_bleed_ignored(self) -> None:
        occ = Path("inputs/Reference/OCC_PID/STOD206340.10 OCC Pulping line 1.dwg")
        ctx = title_context({"title_block": []}, occ.stem, occ)
        parsed = {
            "sub_process": "BR1",
            "function": "55-30L001",
            "description": "55-30L001 OCC PULPER",
            "rows": [{"equipment": "55-30-001", "subequipment": "", "description": "LN"}],
        }
        rows, _ = rows_from_ai(1, ctx, "55-30L001", parsed)
        subprocess_masks = [r["MASK"] for r in rows if r.get("SUB-PROCESS") and not r.get("FUNCTION")]
        self.assertTrue(all("BR1" not in m for m in subprocess_masks))
        self.assertTrue(any("OC1" in m for m in subprocess_masks))


class PumpValveTests(unittest.TestCase):
    def test_pump_tags_not_valves(self) -> None:
        for tag in ("36-45P502", "55-30P501", "35-23P501"):
            self.assertTrue(is_pump_tag(tag))
            self.assertTrue(is_pump_equipment(tag, f"{tag} BROKE ROLL PLPR PMP"))
            self.assertFalse(is_valve_equipment(tag, f"{tag} VLV ON LINE"))

    def test_fv_tag_is_valve_any_area(self) -> None:
        self.assertTrue(is_valve_tag("36-45FV-015"))
        self.assertTrue(is_valve_equipment("36-45FV-015", "CTRL VLV"))


class HierarchyCleanupTests(unittest.TestCase):
    def test_sanitize_drops_phantom_and_duplicates(self) -> None:
        rows = [
            {"FUNCTION": "55-30L001", "EQUIPMENT": "", "SUB-EQUIPMENT": ""},
            {"FUNCTION": "", "EQUIPMENT": "55-30-001", "SUB-EQUIPMENT": ""},
            {"FUNCTION": "", "EQUIPMENT": "55-30L001.1", "SUB-EQUIPMENT": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-13T072", "SUB-EQUIPMENT": ""},
            {"FUNCTION": "55-30P519", "EQUIPMENT": "", "SUB-EQUIPMENT": ""},
            {"FUNCTION": "", "EQUIPMENT": "55-30-001", "SUB-EQUIPMENT": ""},
        ]
        out = sanitize_hierarchy_rows(rows)
        tags = [r.get("EQUIPMENT") for r in out if r.get("EQUIPMENT")]
        self.assertEqual(tags, ["55-30-001"])

    def test_instrument_functions_excluded(self) -> None:
        self.assertTrue(_is_instrument_function_tag("55-30ES-506"))
        self.assertFalse(_is_instrument_function_tag("55-30L001"))


class GorCode03Tests(unittest.TestCase):
    def test_kv_is_av(self) -> None:
        self.assertEqual(_gor_code03_valve_type("162KV1-575"), "AV")

    def test_v_is_nc(self) -> None:
        self.assertEqual(_gor_code03_valve_type("162V-001"), "NC")

    def test_default_hv(self) -> None:
        self.assertEqual(_gor_code03_valve_type("162X-001"), "HV")


class ExportFilterTests(unittest.TestCase):
    def test_template_junk_rejected(self) -> None:
        self.assertFalse(_is_valid_equipment_tag("CHAR 30"))
        self.assertFalse(_is_valid_equipment_tag("Functional Location"))
        self.assertTrue(_is_valid_equipment_tag("162V-001"))


class InventoryFunctionKindTests(unittest.TestCase):
    def test_default_kinds_exclude_instruments(self) -> None:
        inv = Path("outputs/jsons/STOD206340.10 OCC Pulping line 1.pid_inventory.json")
        if not inv.exists():
            self.skipTest("OCC inventory not present")
        rows = load_inventory_functions(inv, kinds=list(DEFAULT_HIERARCHY_FUNCTION_KINDS))
        kinds = {str(r.get("kind") or "").lower() for r in rows}
        self.assertNotIn("instrument", kinds)


if __name__ == "__main__":
    unittest.main()
