#!/usr/bin/env python3
"""Unit tests for dwg_ecosystem — ecosystem detection and standards loading."""

from __future__ import annotations

import unittest

from dwg_reader.dwg_ecosystem import Ecosystem, detect


class EcosystemDetectionTests(unittest.TestCase):
    """Stem-based and context-based ecosystem detection."""

    def test_detect_gora_stem(self) -> None:
        eco = detect("GORA68210.05_Code 03 - P&ID AirCap")
        self.assertEqual(eco.name, "gor")
        self.assertTrue(eco.is_tissue)
        self.assertFalse(eco.is_valmet)
        self.assertEqual(eco.standard_id, "gor_fiorentini")

    def test_detect_gorb_stem(self) -> None:
        eco = detect("GORB18781.02_something")
        self.assertEqual(eco.name, "gor")
        self.assertTrue(eco.is_tissue)

    def test_detect_ksdm_stem(self) -> None:
        eco = detect("KSDM160104_010")
        self.assertEqual(eco.name, "ksd")
        self.assertTrue(eco.is_tissue)
        self.assertEqual(eco.standard_id, "ksd_andritz")

    def test_detect_stod_stem(self) -> None:
        eco = detect("STOD206336.11 Stock Preparation and Mixing area")
        self.assertEqual(eco.name, "valmet")
        self.assertTrue(eco.is_valmet)
        self.assertFalse(eco.is_tissue)

    def test_detect_pcsg_stem(self) -> None:
        eco = detect("PCSG028666.03_Surface_size_preparation")
        self.assertEqual(eco.name, "valmet")
        self.assertTrue(eco.is_valmet)

    def test_detect_rau_stem(self) -> None:
        eco = detect("RAU8F00290.10_Steam and Condensate")
        self.assertEqual(eco.name, "valmet")
        self.assertTrue(eco.is_valmet)

    def test_detect_broke_system_defaults_valmet(self) -> None:
        eco = detect("Broke System")
        self.assertEqual(eco.name, "valmet")

    def test_detect_unknown_stem_defaults_valmet_with_warning(self) -> None:
        with self.assertLogs("dwg_reader.dwg_ecosystem", level="WARNING") as cm:
            eco = detect("RandomStem")
        self.assertEqual(eco.name, "valmet")
        self.assertTrue(any("defaulting to valmet" in m for m in cm.output))

    def test_detect_empty_stem_defaults_valmet(self) -> None:
        eco = detect("")
        self.assertEqual(eco.name, "valmet")

    def test_detect_ctx_gor_overrides_stem(self) -> None:
        # Explicit ecosystem in ctx wins even when stem looks like something else
        eco = detect("Broke System", ctx={"ecosystem": "gor"})
        self.assertEqual(eco.name, "gor")
        self.assertTrue(eco.is_tissue)

    def test_detect_ctx_valmet_overrides_gora_stem(self) -> None:
        eco = detect("GORA68210", ctx={"ecosystem": "valmet"})
        self.assertEqual(eco.name, "valmet")
        self.assertTrue(eco.is_valmet)

    def test_detect_ctx_ksd_explicit(self) -> None:
        eco = detect("", ctx={"ecosystem": "ksd"})
        self.assertEqual(eco.name, "ksd")
        self.assertTrue(eco.is_tissue)
        self.assertEqual(eco.standard_id, "ksd_andritz")

    def test_detect_ctx_unknown_value_falls_back_to_stem(self) -> None:
        eco = detect("GORB18781", ctx={"ecosystem": "not_a_real_ecosystem"})
        self.assertEqual(eco.name, "gor")  # stem detection wins

    def test_detect_ctx_none_ecosystem_key_falls_back_to_stem(self) -> None:
        eco = detect("STOD206336", ctx={"ecosystem": None})
        self.assertEqual(eco.name, "valmet")

    def test_detect_inventory_gor_overrides_valmet_stem(self) -> None:
        eco = detect(
            "Broke System",
            inventory={
                "lines": [{"source": "gor_pipe_id"}],
                "valves": [],
                "functions": [],
            },
        )
        self.assertEqual(eco.name, "gor")
        self.assertTrue(eco.is_tissue)

    def test_detect_ctx_still_overrides_gor_inventory(self) -> None:
        eco = detect(
            "GORA68210",
            ctx={"ecosystem": "valmet"},
            inventory={"valves": [{"layer": "1-VALVE TEXT GOR"}]},
        )
        self.assertEqual(eco.name, "valmet")

    def test_is_gor_inventory_signals(self) -> None:
        from dwg_reader.dwg_ecosystem import is_gor_inventory

        self.assertFalse(is_gor_inventory(None))
        self.assertFalse(is_gor_inventory({}))
        self.assertTrue(is_gor_inventory({"valves": [{"block_name": "TAG VALVOLA"}]}))
        self.assertTrue(is_gor_inventory({"valves": [{"layer": "1-VALVE TEXT GOR"}]}))
        self.assertTrue(is_gor_inventory({"functions": [{"function": "WU05"}]}))
        self.assertFalse(is_gor_inventory({"functions": [{"function": "35-24L009"}]}))

    def test_ksd_structural_from_ps_equip(self) -> None:
        from dwg_reader.dwg_ecosystem import is_ksd_structural

        structural = {"inserts": [{"layer": "PS-EQUIP", "name": "EQ", "attributes": []}]}
        self.assertTrue(is_ksd_structural(structural))
        eco = detect("", structural=structural)
        self.assertEqual(eco.name, "ksd")

    def test_ksd_structural_from_krets(self) -> None:
        from dwg_reader.dwg_ecosystem import is_ksd_structural

        structural = {
            "inserts": [{
                "layer": "0",
                "name": "instr",
                "attributes": [{"tag": "KRETS", "text": "126LC"}, {"tag": "POSNR", "text": "001"}],
            }]
        }
        self.assertTrue(is_ksd_structural(structural))

    def test_pipeid_alone_is_not_ksd(self) -> None:
        from dwg_reader.dwg_ecosystem import is_ksd_structural

        structural = {
            "inserts": [{
                "layer": "Revison 03",
                "name": "Pipeno",
                "attributes": [{"tag": "PIPEID", "text": "168L-001"}],
            }]
        }
        self.assertFalse(is_ksd_structural(structural))
        self.assertEqual(detect("", structural=structural).name, "gor")

    def test_gor_structural_from_tag_valvola(self) -> None:
        from dwg_reader.dwg_ecosystem import is_gor_structural

        structural = {"inserts": [{"layer": "0", "name": "TAG VALVOLA", "attributes": []}]}
        self.assertTrue(is_gor_structural(structural))
        self.assertEqual(detect("", structural=structural).name, "gor")

    def test_gora_stem_wins_over_ksd_foreign_layer(self) -> None:
        structural = {"inserts": [{"layer": "1-EQUIPMENT KSD", "name": "EQ", "attributes": []}]}
        eco = detect("GORA68210", structural=structural)
        self.assertEqual(eco.name, "gor")

    def test_ksd_inventory_signal(self) -> None:
        from dwg_reader.dwg_ecosystem import is_ksd_inventory

        self.assertTrue(is_ksd_inventory({"lines": [{"source": "ksd_pipe_id"}]}))
        self.assertTrue(is_ksd_inventory({
            "process_equipment": [{"layer": "PS-EQUIP", "tag": "122E-001"}]
        }))
        self.assertFalse(is_ksd_inventory({"valves": [{"block_name": "TAG VALVOLA"}]}))


class EcosystemStandardsTests(unittest.TestCase):
    """Verify standards JSON files load and have required fields."""

    def _required_fields(self) -> list[str]:
        return ["motor_from_equipment", "driven_patterns", "tag_prefix_rules"]

    def test_valmet_standard_required_fields(self) -> None:
        eco = detect("STOD206336")
        for field in self._required_fields():
            self.assertIn(field, eco.standard, msg=f"Missing field: {field}")

    def test_tissue_standard_required_fields(self) -> None:
        eco = detect("GORA68210")
        for field in self._required_fields():
            self.assertIn(field, eco.standard, msg=f"Missing field: {field}")

    def test_valmet_motor_mode(self) -> None:
        eco = detect("STOD206336")
        self.assertEqual(eco.standard["motor_from_equipment"]["mode"], "strip_letter_append_dot_one")

    def test_tissue_motor_mode_and_suffix(self) -> None:
        eco = detect("GORA68210")
        mot = eco.standard["motor_from_equipment"]
        self.assertEqual(mot["mode"], "append_suffix")
        self.assertEqual(mot["suffix"], "-M1")

    def test_valmet_driven_patterns(self) -> None:
        eco = detect("STOD206336")
        driven = eco.standard["driven_patterns"]
        self.assertIn("pump", driven)
        self.assertIn("agitator_l", driven)

    def test_tissue_driven_patterns(self) -> None:
        eco = detect("GORA68210")
        driven = eco.standard["driven_patterns"]
        self.assertIn("pump", driven)
        self.assertIn("agitator", driven)

    def test_valmet_prefix_rules_pump(self) -> None:
        eco = detect("STOD206336")
        self.assertEqual(eco.standard["tag_prefix_rules"]["P"], "701")

    def test_tissue_prefix_rules_pump_and_agitator(self) -> None:
        eco = detect("GORA68210")
        rules = eco.standard["tag_prefix_rules"]
        self.assertEqual(rules["P"], "701")
        self.assertEqual(rules["A"], "2001")

    def test_standard_is_shared_object_for_same_id(self) -> None:
        # Two ecosystems with the same standard_id share one dict (lru_cache)
        eco1 = detect("GORA68210")
        eco2 = detect("GORB18781")
        self.assertIs(eco1.standard, eco2.standard)


class EcosystemMotorHelperTests(unittest.TestCase):
    """Motor tag derivation and driven-equipment detection via ecosystem."""

    def setUp(self) -> None:
        from dwg_reader.export_sap_equipment import _is_driven_equipment, _motor_tag_for
        self._motor = _motor_tag_for
        self._driven = _is_driven_equipment

    def test_tissue_motor_from_pump(self) -> None:
        eco = detect("GORA68210")
        self.assertEqual(self._motor("124P-001", ecosystem=eco), "124P-001-M1")

    def test_tissue_motor_from_agitator(self) -> None:
        eco = detect("GORA68210")
        self.assertEqual(self._motor("124A-003", ecosystem=eco), "124A-003-M1")

    def test_valmet_motor_from_pump(self) -> None:
        eco = detect("STOD206336")
        self.assertEqual(self._motor("35-24P518", ecosystem=eco), "35-24-518.1")

    def test_valmet_motor_no_ecosystem_kwarg(self) -> None:
        # Backwards-compatible: no ecosystem kwarg → Valmet path
        self.assertEqual(self._motor("35-24P518"), "35-24-518.1")

    def test_tissue_is_driven_pump(self) -> None:
        eco = detect("GORA68210")
        self.assertTrue(self._driven("124P-001", eco))

    def test_tissue_is_driven_agitator(self) -> None:
        eco = detect("GORA68210")
        self.assertTrue(self._driven("124A-001", eco))

    def test_tissue_tank_is_not_driven(self) -> None:
        eco = detect("GORA68210")
        self.assertFalse(self._driven("124T-001", eco))

    def test_tissue_machine_is_not_driven(self) -> None:
        eco = detect("GORA68210")
        self.assertFalse(self._driven("124E-001", eco))

    def test_valmet_is_driven_pump(self) -> None:
        eco = detect("STOD206336")
        self.assertTrue(self._driven("35-24P518", eco))

    def test_valmet_is_driven_agitator_range(self) -> None:
        eco = detect("STOD206336")
        self.assertTrue(self._driven("35-24L401", eco))
        self.assertTrue(self._driven("35-24L499", eco))

    def test_valmet_is_not_driven_low_l_range(self) -> None:
        eco = detect("STOD206336")
        self.assertFalse(self._driven("35-24L002", eco))

    def test_tissue_motor_for_non_driven_tag_still_returns_suffix(self) -> None:
        # _motor_tag_for appends -M1 blindly for tissue; _is_driven_equipment is
        # the guard — it returns False for tanks so the injection loop skips them.
        eco = detect("GORA68210")
        self.assertEqual(self._motor("124T-001", ecosystem=eco), "124T-001-M1")
        self.assertFalse(self._driven("124T-001", eco))

    def test_tissue_motor_injection_via_build_equipment_rows(self) -> None:
        """GOR pump in hierarchy gets -M1 motor injected when ecosystem=gor in ctx."""
        from dwg_reader.export_sap_equipment import build_equipment_rows

        rows = [
            {"FUNCTION": "124L-001", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "PULPER"},
            {"FUNCTION": "", "EQUIPMENT": "124P-001", "SUB-EQUIPMENT": "", "DESCRIPTION": "PUMP"},
        ]
        ctx = {
            "ecosystem": "gor",
            "plant": "5001",
            "line_code": "TM01",
            "process_code": "AC",
            "sub_process": "AC1",
        }
        out = build_equipment_rows(rows, ctx=ctx)
        by_tag = {r["EQUNR"]: r for r in out}
        self.assertIn("124P-001-M1", by_tag, "Tissue pump motor must be injected")
        motor = by_tag["124P-001-M1"]
        self.assertEqual(motor["HEQUI"], "124P-001")
        self.assertEqual(motor["EQART"], "1101")
        self.assertEqual(motor["GEWRK"], "ELEC")

    def test_valmet_motor_not_injected_for_tissue_pump_without_ctx(self) -> None:
        """Without ecosystem context, a tissue-format pump doesn't trigger Valmet injection."""
        from dwg_reader.export_sap_equipment import build_equipment_rows

        # 124P-001 doesn't match the Valmet pump RE (^\d{2}-\d{2}P\d+$) so no motor
        rows = [
            {"FUNCTION": "124L-001", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": ""},
            {"FUNCTION": "", "EQUIPMENT": "124P-001", "SUB-EQUIPMENT": "", "DESCRIPTION": "PUMP"},
        ]
        out = build_equipment_rows(rows)  # no ctx → valmet default
        tags = [r["EQUNR"] for r in out]
        self.assertNotIn("124P-001-M1", tags)
        self.assertNotIn("124P-001.1", tags)


class TissueTagObjectTypeTests(unittest.TestCase):
    """Verify dwg_object_type classifies Tissue / KSDM160104 tags correctly."""

    def _cls(self, tag: str, desc: str = "") -> tuple[str, str]:
        from dwg_reader.dwg_object_type import classify_equipment
        return classify_equipment(tag, desc)

    def test_tissue_pump_prefix_classifies_701(self) -> None:
        code, wc = self._cls("124P-001", "124P-001 PUMP")
        self.assertEqual(code, "701")
        self.assertEqual(wc, "MECH")

    def test_tissue_pump_no_description_still_701(self) -> None:
        # Tag prefix step fires before description keywords
        code, wc = self._cls("124P-001")
        self.assertEqual(code, "701")

    def test_tissue_agitator_prefix_classifies_2001(self) -> None:
        code, wc = self._cls("124A-003", "124A-003 AGITATOR")
        self.assertEqual(code, "2001")

    def test_tissue_motor_suffix_classifies_1101(self) -> None:
        # -M1 suffix triggers motor classification
        code, wc = self._cls("124P-001-M1", "124P-001-M1 MOTOR")
        self.assertEqual(code, "1101")
        self.assertEqual(wc, "ELEC")

    def test_tissue_motor_suffix_no_description(self) -> None:
        code, wc = self._cls("124P-001-M1")
        self.assertEqual(code, "1101")
        self.assertEqual(wc, "ELEC")

    def test_valmet_motor_suffix_still_works(self) -> None:
        code, wc = self._cls("35-24-518.1", "MOTOR")
        self.assertEqual(code, "1101")
        self.assertEqual(wc, "ELEC")

    def test_tissue_tag_does_not_affect_valmet_tags(self) -> None:
        # Valmet pump tag must not be caught by the Tissue step
        code, wc = self._cls("35-24P519", "35-24P519 PUMP")
        self.assertEqual(code, "701")  # via _TAG_NODASH_RE step 2, not tissue step


if __name__ == "__main__":
    unittest.main()
