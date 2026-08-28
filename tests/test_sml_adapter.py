"""
Tests for dwg_reader/adapters/sml_adapter.py — SML / Valmet PS-21 adapter.
"""
import unittest

from dwg_reader.adapters.sml_adapter import SMLAdapter


class TestSMLAdapterIdentity(unittest.TestCase):
    def setUp(self):
        self.adapter = SMLAdapter()

    def test_ecosystem_name(self):
        self.assertEqual(self.adapter.ecosystem_name, "valmet")

    def test_standard_id(self):
        self.assertEqual(self.adapter.standard_id, "valmet_ps21")

    def test_uses_ai_hierarchy(self):
        self.assertTrue(self.adapter.uses_ai_hierarchy)

    def test_hierarchy_prompt_is_gt_v8(self):
        self.assertEqual(self.adapter.hierarchy_prompt_file, "pid_hierarchy_gt_v8.md")

    def test_layer_map_contains_core_layers(self):
        lm = self.adapter.layer_map
        self.assertIn("P-TANK_POS", lm)
        self.assertEqual(lm["P-TANK_POS"][0], "tanks")
        self.assertIn("P-PUMP_POS", lm)
        self.assertIn("P-VALVEPOS", lm)
        self.assertIn("P-CVPOS", lm)
        self.assertIn("P-INSTRPOS", lm)
        self.assertIn("P-SENSOR_POS", lm)
        self.assertEqual(lm["P-SENSOR_POS"][0], "instruments")
        self.assertIn("P-AGITATOR_POS", lm)

    def test_block_map_is_empty(self):
        # SML uses layer-first — block names carry no category.
        self.assertEqual(self.adapter.block_map, {})

    def test_sensor_layer_is_instrument(self):
        cat, sub, _ = self.adapter.classify_insert({"name": "X", "layer": "P-SENSOR_POS"}, {})
        self.assertEqual(cat, "instruments")
        self.assertEqual(sub, "sensor_symbol")

    def test_finnish_attrs_are_extra_not_tag(self):
        tag, extra = self.adapter.tag_from_insert(
            "SYMBOL",
            {"VENIMI": "BENTONITE PUMP", "VEPOSITIO": "12"},
        )
        self.assertEqual(tag, "SYMBOL")
        self.assertEqual(extra["description"], "BENTONITE PUMP")
        self.assertEqual(extra["position_number"], "12")

    def test_build_hierarchy_raises(self):
        with self.assertRaises(NotImplementedError):
            self.adapter.build_hierarchy({}, {})


class TestSMLAdapterParseTag(unittest.TestCase):
    def setUp(self):
        self.a = SMLAdapter()

    def test_pump_tag(self):
        p = self.a.parse_tag("35-24P518")
        self.assertEqual(p["area"], "35-24")
        self.assertEqual(p["type_letter"], "P")
        self.assertEqual(p["sequence"], "518")
        self.assertEqual(p["full"], "35-24P518")

    def test_tank_tag(self):
        p = self.a.parse_tag("35-24T601")
        self.assertEqual(p["type_letter"], "T")
        self.assertEqual(p["sequence"], "601")

    def test_agitator_tag(self):
        p = self.a.parse_tag("35-24L401")
        self.assertEqual(p["type_letter"], "L")
        self.assertEqual(p["sequence"], "401")

    def test_process_equip_tag(self):
        p = self.a.parse_tag("35-24L009")
        self.assertEqual(p["type_letter"], "L")
        self.assertEqual(p["sequence"], "009")

    def test_pipeline_tag(self):
        p = self.a.parse_tag("35-24-095")
        self.assertEqual(p["area"], "35-24")
        self.assertEqual(p["type_letter"], "")
        self.assertEqual(p["sequence"], "095")

    def test_lowercase_normalised(self):
        p = self.a.parse_tag("35-24p518")
        self.assertEqual(p["full"], "35-24P518")
        self.assertEqual(p["type_letter"], "P")

    def test_spaces_stripped(self):
        p = self.a.parse_tag("  35-24P518  ")
        self.assertEqual(p["full"], "35-24P518")


class TestSMLAdapterTagClassification(unittest.TestCase):
    def setUp(self):
        self.a = SMLAdapter()

    def test_pump_is_equipment(self):
        self.assertTrue(self.a.is_equipment_tag("35-24P518"))

    def test_tank_is_equipment(self):
        self.assertTrue(self.a.is_equipment_tag("35-24T601"))

    def test_agitator_is_equipment(self):
        self.assertTrue(self.a.is_equipment_tag("35-24L401"))

    def test_pipeline_is_line(self):
        self.assertTrue(self.a.is_line_tag("35-24-095"))
        self.assertFalse(self.a.is_equipment_tag("35-24-095"))

    def test_pipeline_not_equipment(self):
        self.assertFalse(self.a.is_equipment_tag("35-24-189"))

    def test_motor_tag_detected(self):
        self.assertTrue(self.a.is_motor_tag("35-24-518.1"))
        self.assertTrue(self.a.is_motor_tag("35-24-009.2"))

    def test_non_motor_not_detected(self):
        self.assertFalse(self.a.is_motor_tag("35-24P518"))

    def test_valve_tag_is_not_equipment_by_tag_alone(self):
        # Two-letter valve prefix (HV) doesn't match the single-letter equipment
        # pattern. Valves are classified by CAD layer (P-VALVEPOS), not tag format.
        self.assertFalse(self.a.is_equipment_tag("35-24HV-548"))

    def test_instrument_is_not_equipment_not_line(self):
        self.assertFalse(self.a.is_equipment_tag("35-24PI-9082"))
        self.assertFalse(self.a.is_line_tag("35-24PI-9082"))
        self.assertTrue(self.a.is_instrument_tag("35-24PI-9082"))


class TestSMLAdapterMotorDerivation(unittest.TestCase):
    def setUp(self):
        self.a = SMLAdapter()

    def test_pump_motor(self):
        self.assertEqual(self.a.derive_motor_tag("35-24P518"), "35-24-518.1")

    def test_tank_no_motor(self):
        # Tanks are not driven — but the pattern still matches; motor is implicit.
        # The adapter produces the tag; caller decides whether to inject it.
        self.assertEqual(self.a.derive_motor_tag("35-24T601"), "35-24-601.1")

    def test_agitator_motor(self):
        self.assertEqual(self.a.derive_motor_tag("35-24L401"), "35-24-401.1")

    def test_process_equip_motor(self):
        self.assertEqual(self.a.derive_motor_tag("35-24L009"), "35-24-009.1")

    def test_pipeline_returns_none(self):
        self.assertIsNone(self.a.derive_motor_tag("35-24-095"))

    def test_multi_letter_type_returns_none(self):
        # Valve tag 35-24HV-548 has a hyphen after the letters, which breaks
        # the motor-from-equipment regex (needs digit immediately after letters).
        # Valves don't have motors — the adapter correctly returns None.
        self.assertIsNone(self.a.derive_motor_tag("35-24HV-548"))

    def test_rotor_subequip(self):
        # 35-24L009.1 is a rotor — its motor tag is itself (strip L, keep .1)
        result = self.a.derive_motor_tag("35-24L009.1")
        self.assertEqual(result, "35-24-009.1")


class TestSMLAdapterValveType(unittest.TestCase):
    def setUp(self):
        self.a = SMLAdapter()

    def test_cvpos_layer_returns_av(self):
        vtype, is_valve = self.a.resolve_valve_type("35-24HV-548", layer="P-CVPOS")
        self.assertEqual(vtype, "AV")
        self.assertTrue(is_valve)

    def test_valvepos_layer_infers_from_desc(self):
        vtype, is_valve = self.a.resolve_valve_type(
            "35-24HV-548", layer="P-VALVEPOS", eqktx="HV 35-24-548 35-24P518 NC"
        )
        self.assertEqual(vtype, "NC")

    def test_default_hv(self):
        vtype, is_valve = self.a.resolve_valve_type("35-24-131", eqktx="VLV ON LINE")
        self.assertEqual(vtype, "HV")
        self.assertTrue(is_valve)

    def test_av_in_desc(self):
        vtype, _ = self.a.resolve_valve_type("35-24FV-570", eqktx="AV FLOW CTRL")
        self.assertEqual(vtype, "AV")

    def test_drn_qualifier(self):
        vtype, _ = self.a.resolve_valve_type("35-24-131", eqktx="DRN VLV")
        self.assertIn("DRN", vtype)


class TestSMLAdapterNormalise(unittest.TestCase):
    def setUp(self):
        self.a = SMLAdapter()

    def test_abbreviates_pump(self):
        result = self.a.normalize_description("COUCH PIT PUMP")
        self.assertLessEqual(len(result), 40)
        self.assertEqual(result, result.upper())

    def test_clips_to_40(self):
        long_text = "VERY LONG DESCRIPTION THAT EXCEEDS THE FORTY CHARACTER LIMIT FOR SAP"
        result = self.a.normalize_description(long_text)
        self.assertLessEqual(len(result), 40)

    def test_empty_string(self):
        self.assertEqual(self.a.normalize_description(""), "")


class TestSMLAdapterLoadStandard(unittest.TestCase):
    def test_load_standard_has_motor_from_equipment(self):
        std = SMLAdapter().load_standard()
        self.assertIn("motor_from_equipment", std)
        self.assertEqual(std["motor_from_equipment"]["mode"], "strip_letter_append_dot_one")

    def test_load_standard_has_flow_codes(self):
        std = SMLAdapter().load_standard()
        self.assertIn("flow_substance_codes", std)
        self.assertEqual(std["flow_substance_codes"]["WAF"], "WHITE WTR")


if __name__ == "__main__":
    unittest.main()
