#!/usr/bin/env python3
"""Regression tests for audit-report fixes (FLOC bleed, pumps, hierarchy cleanup)."""

import unittest
from pathlib import Path

from dwg_reader.dwg_floc_context import is_pump_equipment, is_pump_tag, is_valve_equipment, is_valve_tag
from dwg_reader.dwg_pid_hierarchy_ai import rows_from_ai, title_context
from dwg_reader.export_sap_equipment import _is_valid_equipment_tag
from dwg_reader.adapters.gor_adapter import GORAdapter
from dwg_reader.run_hierarchy_orchestrator import (
    DEFAULT_HIERARCHY_FUNCTION_KINDS,
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
    def test_sanitize_drops_phantom_motor_line(self) -> None:
        rows = [
            {"FUNCTION": "35-24P501", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "COUCH PIT PMP"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-1300", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24-1300 PMP MTR"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-119", "SUB-EQUIPMENT": "", "DESCRIPTION": "SUCT LN"},
        ]
        out = sanitize_hierarchy_rows(rows)
        tags = [r.get("EQUIPMENT") for r in out if r.get("EQUIPMENT")]
        self.assertEqual(tags, ["35-24-119"])

    def test_sanitize_keeps_rotors_drops_phantom_decimal(self) -> None:
        rows = [
            {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "PLPR"},
            {"FUNCTION": "", "EQUIPMENT": "35-24L009.1", "SUB-EQUIPMENT": "", "DESCRIPTION": "RTR 1"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-508.2", "SUB-EQUIPMENT": "", "DESCRIPTION": "PHANTOM"},
        ]
        out = sanitize_hierarchy_rows(rows)
        tags = [r.get("EQUIPMENT") for r in out if r.get("EQUIPMENT")]
        self.assertEqual(tags, ["35-24L009.1"])

    def test_sanitize_pump_takes_tag_from_earlier_pulper(self) -> None:
        """B01: later P519 owns 35-24-192; L009's earlier copy is dropped."""
        rows = [
            {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "PLPR"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-192", "SUB-EQUIPMENT": "", "DESCRIPTION": "SUCT"},
            {"FUNCTION": "35-24P519", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "PMP"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-192", "SUB-EQUIPMENT": "", "DESCRIPTION": "SUCT"},
        ]
        out = sanitize_hierarchy_rows(rows)
        owners = []
        current = ""
        for row in out:
            fn = row.get("FUNCTION") or ""
            eq = row.get("EQUIPMENT") or ""
            if fn and not eq:
                current = fn
            if eq == "35-24-192":
                owners.append(current)
        self.assertEqual(owners, ["35-24P519"])

    def test_seed_childless_function_from_inventory(self) -> None:
        """B03: empty L001 header gets nearby inventory valves/lines."""
        import json
        import tempfile
        from dwg_reader.run_hierarchy_orchestrator import (
            _seed_childless_functions,
            write_hierarchy_csv,
            read_hierarchy_csv,
        )

        with tempfile.TemporaryDirectory() as td:
            csv_path = Path(td) / "h.csv"
            inv_path = Path(td) / "inv.json"
            write_hierarchy_csv(csv_path, [
                {"FUNCTION": "35-24L001", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
                 "MASK": "", "DESCRIPTION": "PRESS PLPR"},
                {"FUNCTION": "35-24L005", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
                 "MASK": "", "DESCRIPTION": "REEL PLPR"},
                {"FUNCTION": "", "EQUIPMENT": "35-24-026", "SUB-EQUIPMENT": "",
                 "MASK": "", "DESCRIPTION": "LN"},
            ])
            inv_path.write_text(json.dumps({
                "functions": [
                    {"function": "35-24L001", "x": 100.0, "y": 100.0},
                    {"function": "35-24L005", "x": 800.0, "y": 800.0},
                ],
                "valves": [{"tag": "35-24-089", "x": 110.0, "y": 105.0, "description": "DRN"}],
                "lines": [{"line_number": "35-24-096", "x": 120.0, "y": 90.0}],
            }), encoding="utf-8")
            n = _seed_childless_functions(csv_path, inv_path, radius=180.0)
            self.assertGreaterEqual(n, 1)
            tags = [r.get("EQUIPMENT") for r in read_hierarchy_csv(csv_path) if r.get("EQUIPMENT")]
            self.assertIn("35-24-089", tags)
            self.assertIn("35-24-096", tags)
            self.assertIn("35-24-026", tags)

    def test_load_inventory_tags_includes_pumps_motors_process(self) -> None:
        import json
        import tempfile
        from dwg_reader.run_hierarchy_orchestrator import _load_inventory_tags

        payload = {
            "functions": [{"function": "35-24L009"}],
            "pumps": [{"tag": "35-24P507"}],
            "tanks": [{"tag": "35-24T601"}],
            "motors": [{"tag": "35-24-009.1"}],
            "process_equipment": [{"resolved_tag": "35-24L009.1"}],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(payload, fh)
            path = Path(fh.name)
        try:
            tags = _load_inventory_tags(path)
        finally:
            path.unlink()
        self.assertEqual(
            tags,
            {"35-24L009", "35-24P507", "35-24T601", "35-24-009.1", "35-24L009.1"},
        )

    def test_instrument_functions_excluded(self) -> None:
        self.assertTrue(_is_instrument_function_tag("55-30ES-506"))
        self.assertFalse(_is_instrument_function_tag("55-30L001"))


class GorCode03Tests(unittest.TestCase):
    """E-04: AirCap Code 03 tags (GORA68210) vs KV→AV / \\dV-\\d→NC / else HV.

    Adapter heuristics remain for inventory descriptions. SAP types come from
    legend vision, not these tag-pattern fallbacks.
    """

    # Tags transcribed from GORA68210.05_Code 03 - P&ID AirCap (1-VALVE TEXT GOR).
    AIRCAP_GOLDEN = {
        "162KV1-575": "AV",
        "162KV2-575": "AV",
        "162KV3-575": "AV",
        "162V-001": "NC",
        "162V-002": "NC",
        "162HV1-500": "HV",
        "162HV1-600": "HV",
        "162V1-570": "HV",  # digit between V and hyphen — not ^\\d+V-\\d
    }

    def _code03(self, tag: str):
        vtype, _is_valve = GORAdapter().resolve_valve_type(tag)
        return vtype

    def test_kv_is_av(self) -> None:
        self.assertEqual(self._code03("162KV1-575"), "AV")

    def test_v_is_nc(self) -> None:
        self.assertEqual(self._code03("162V-001"), "NC")

    def test_st_is_sv(self) -> None:
        self.assertEqual(self._code03("162ST-065"), "SV")
        self.assertEqual(self._code03("168-ST521"), "SV")

    def test_default_hv(self) -> None:
        self.assertEqual(self._code03("162X-001"), "HV")

    def test_aircap_golden_tags(self) -> None:
        adapter = GORAdapter()
        for tag, expected in self.AIRCAP_GOLDEN.items():
            vtype, is_valve = adapter.resolve_valve_type(tag)
            self.assertEqual(vtype, expected, tag)
            self.assertTrue(is_valve, tag)

    def test_aircap_dwg_valve_texts_when_present(self) -> None:
        """E-04: if AirCap DWG/structural JSON is on disk, classify extracted valves."""
        from dwg_reader.dwg_pid_inventory import build_inventory

        candidates = [
            Path("outputs/jsons/GORA68210.05_Code 03 - P&ID AirCap_SWE Shotton_CE.structural.json"),
            Path("outputs/jsons/GORA68210.05_Code 03 - P&ID AirCap_SWE Shotton_CE.pid_inventory.json"),
        ]
        structural_path = next((p for p in candidates if p.exists() and "structural" in p.name), None)
        inv_path = next((p for p in candidates if p.exists() and "inventory" in p.name), None)
        if structural_path is None and inv_path is None:
            self.skipTest("AirCap structural/inventory JSON not present")

        adapter = GORAdapter()
        if structural_path is not None:
            import json
            structural = json.loads(structural_path.read_text(encoding="utf-8"))
            inv = build_inventory(structural, dwg_stem="GORA68210")
        else:
            import json
            inv = json.loads(inv_path.read_text(encoding="utf-8"))

        tags = {r["tag"] for r in inv.get("valves") or []}
        self.assertTrue(tags, "AirCap inventory has no valves")
        for tag in tags:
            adapt, is_valve = adapter.resolve_valve_type(tag)
            self.assertIsNotNone(adapt, tag)
            self.assertTrue(is_valve, tag)
        for tag, expected in self.AIRCAP_GOLDEN.items():
            if tag in tags:
                self.assertEqual(adapter.resolve_valve_type(tag)[0], expected, tag)


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
