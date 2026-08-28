"""
Tests for dwg_reader/adapters/ksd_adapter.py — KSD / Andritz adapter.

Rules derived from KSDM160104 PDF and parsed KSDM* DWG attributes
(ITEM / KRETS / PIPEID on PS-EQUIP, INSTRUMENT, Pipe ID).
"""
import unittest

from dwg_reader.adapters.ksd_adapter import KSDAdapter, _AREA_CODES, compose_krets_posnr


class TestKSDAdapterIdentity(unittest.TestCase):
    def setUp(self):
        self.a = KSDAdapter()

    def test_ecosystem_name(self):
        self.assertEqual(self.a.ecosystem_name, "ksd")

    def test_standard_id(self):
        self.assertEqual(self.a.standard_id, "ksd_andritz")

    def test_uses_ai_hierarchy_true(self):
        # Deterministic bypass not yet implemented for KSD.
        self.assertTrue(self.a.uses_ai_hierarchy)

    def test_layer_map_has_ksd_layers(self):
        lm = self.a.layer_map
        self.assertIn("PS-EQUIP", lm)
        self.assertEqual(lm["PS-EQUIP"][0], "process_equipment")
        self.assertIn("HAND-VALVE", lm)
        self.assertIn("INSTR-VALVE", lm)
        self.assertIn("INSTRUMENT", lm)
        self.assertIn("Pipe ID", lm)
        self.assertNotIn("P-TANK_POS", lm)
        self.assertNotIn("P-VALVEPOS", lm)

    def test_build_hierarchy_raises(self):
        with self.assertRaises(NotImplementedError):
            self.a.build_hierarchy({}, {})


class TestKSDAdapterParseTag(unittest.TestCase):
    def setUp(self):
        self.a = KSDAdapter()

    def test_softwood_pulper(self):
        p = self.a.parse_tag("122E-001")
        self.assertEqual(p["machine"], "1")
        self.assertEqual(p["area"], "22")
        self.assertEqual(p["type_letter"], "E")
        self.assertEqual(p["sequence"], "001")
        self.assertEqual(p["area_name"], "Softwood pulping")

    def test_white_water_pump(self):
        p = self.a.parse_tag("132P-001")
        self.assertEqual(p["area"], "32")
        self.assertEqual(p["type_letter"], "P")
        self.assertEqual(p["area_name"], "White water")

    def test_fresh_water_tank(self):
        p = self.a.parse_tag("180T-001")
        self.assertEqual(p["area"], "80")
        self.assertEqual(p["type_letter"], "T")
        self.assertEqual(p["area_name"], "Fresh water")

    def test_broke_valve(self):
        p = self.a.parse_tag("126V-003")
        self.assertEqual(p["area"], "26")
        self.assertEqual(p["type_letter"], "V")

    def test_pipeline_tag(self):
        p = self.a.parse_tag("136L-001")
        self.assertEqual(p["area"], "36")
        self.assertEqual(p["type_letter"], "L")
        self.assertEqual(p["full"], "136L-001")

    def test_ventilation_unit(self):
        p = self.a.parse_tag("168E-001")
        self.assertEqual(p["area"], "68")
        self.assertEqual(p["area_name"], "Machine hall ventilation")
        self.assertEqual(p["process"], "WU")
        self.assertEqual(p["sub_process"], "WUC")

    def test_pulp_dissolving_area_21(self):
        p = self.a.parse_tag("121E-001")
        self.assertEqual(p["area"], "21")
        self.assertEqual(p["area_name"], "Pulp dissolving")

    def test_mist_removal_area_60(self):
        p = self.a.parse_tag("160E-001")
        self.assertEqual(p["area_name"], "Mist removal")

    def test_lowercase_normalised(self):
        p = self.a.parse_tag("132p-001")
        self.assertEqual(p["full"], "132P-001")
        self.assertEqual(p["type_letter"], "P")


class TestKSDAdapterTagClassification(unittest.TestCase):
    def setUp(self):
        self.a = KSDAdapter()

    def test_equipment_tags(self):
        for tag in ["122E-001", "132P-001", "180T-001", "126A-001"]:
            with self.subTest(tag=tag):
                self.assertTrue(self.a.is_equipment_tag(tag))

    def test_valve_is_not_equipment(self):
        self.assertFalse(self.a.is_equipment_tag("126V-003"))
        self.assertTrue(self.a.is_valve_tag("126V-003"))

    def test_line_tag(self):
        self.assertTrue(self.a.is_line_tag("136L-001"))
        self.assertFalse(self.a.is_equipment_tag("136L-001"))

    def test_motor_tag_detected(self):
        self.assertTrue(self.a.is_motor_tag("122E-001-M1"))
        self.assertTrue(self.a.is_motor_tag("132P-001-M2"))

    def test_base_tag_not_motor(self):
        self.assertFalse(self.a.is_motor_tag("122E-001"))

    def test_instrument_tag_classification(self):
        # 122LC-001 is not an equipment tag (4-char letter group), not a line tag
        self.assertFalse(self.a.is_line_tag("122LC-001"))
        self.assertTrue(self.a.is_instrument_tag("122LC-001"))


class TestKSDAdapterMotorDerivation(unittest.TestCase):
    def setUp(self):
        self.a = KSDAdapter()

    def test_pump_motor(self):
        self.assertEqual(self.a.derive_motor_tag("132P-001"), "132P-001-M1")

    def test_equipment_motor(self):
        self.assertEqual(self.a.derive_motor_tag("122E-001"), "122E-001-M1")

    def test_agitator_motor(self):
        self.assertEqual(self.a.derive_motor_tag("122A-001"), "122A-001-M1")

    def test_line_returns_none(self):
        self.assertIsNone(self.a.derive_motor_tag("136L-001"))

    def test_tank_returns_none(self):
        self.assertIsNone(self.a.derive_motor_tag("180T-001"))

    def test_valve_returns_none(self):
        self.assertIsNone(self.a.derive_motor_tag("126V-003"))

    def test_already_motor_returns_none(self):
        self.assertIsNone(self.a.derive_motor_tag("122E-001-M1"))


class TestKSDAdapterValveType(unittest.TestCase):
    def setUp(self):
        self.a = KSDAdapter()

    def test_instr_valve_layer_av(self):
        vtype, is_valve = self.a.resolve_valve_type("126V-001", layer="INSTR-VALVE")
        self.assertEqual(vtype, "AV")
        self.assertTrue(is_valve)

    def test_hand_valve_layer_default_hv(self):
        vtype, is_valve = self.a.resolve_valve_type("126V-001", layer="HAND-VALVE")
        self.assertEqual(vtype, "HV")
        self.assertTrue(is_valve)

    def test_nc_in_desc(self):
        vtype, _ = self.a.resolve_valve_type("126V-001", eqktx="NC VLV")
        self.assertIn("NC", vtype)

    def test_no_tipo_for_ksd(self):
        # KSD doesn't use TIPO codes — tipo kwarg is irrelevant but shouldn't crash.
        vtype, is_valve = self.a.resolve_valve_type("126V-001", tipo=None)
        self.assertTrue(is_valve)


class TestKSDAdapterAreaLookup(unittest.TestCase):
    def setUp(self):
        self.a = KSDAdapter()

    def test_area_info_via_tag(self):
        info = self.a.area_info("122E-001")
        self.assertEqual(info["name"], "Softwood pulping")
        self.assertEqual(info["process"], "PL")
        self.assertEqual(info["sub_process"], "PL1")

    def test_static_lookup(self):
        info = KSDAdapter.lookup_area("26")
        self.assertEqual(info["name"], "Internal broke")
        self.assertEqual(info["process"], "BR")

    def test_unknown_area(self):
        info = self.a.area_info("199E-001")
        self.assertEqual(info, {})

    def test_area_codes_have_all_required_keys(self):
        for code, info in _AREA_CODES.items():
            with self.subTest(code=code):
                self.assertIn("name", info)
                self.assertIn("process", info)
                self.assertIn("sub_process", info)


class TestKSDAdapterLoadStandard(unittest.TestCase):
    def test_load_standard_has_area_codes(self):
        std = KSDAdapter().load_standard()
        self.assertIn("area_codes", std)
        self.assertIn("22", std["area_codes"])

    def test_load_standard_has_motor_rule(self):
        std = KSDAdapter().load_standard()
        self.assertEqual(std["motor_from_equipment"]["suffix"], "-M1")

    def test_load_standard_has_function_letters(self):
        std = KSDAdapter().load_standard()
        self.assertIn("function_letters", std)
        self.assertIn("E", std["function_letters"])
        self.assertIn("P", std["function_letters"])


class TestKSDAdapterNormalise(unittest.TestCase):
    def test_normalises_to_40_chars(self):
        a = KSDAdapter()
        long_text = "SOFTWOOD PULPING MACHINE NUMBER ONE IN AREA TWENTY TWO"
        result = a.normalize_description(long_text)
        self.assertLessEqual(len(result), 40)

    def test_uppercase(self):
        a = KSDAdapter()
        result = a.normalize_description("softwood pulping")
        self.assertEqual(result, result.upper())


class TestComposeKretsPosnr(unittest.TestCase):
    def test_digit_sequence(self):
        self.assertEqual(compose_krets_posnr("126LC", "001"), "126LC-001")

    def test_unpadded_digits(self):
        self.assertEqual(compose_krets_posnr("126LC", "1"), "126LC-001")

    def test_posnr_already_full_valve_tag(self):
        self.assertEqual(compose_krets_posnr("180LC", "180V-152"), "180V-152")

    def test_posnr_already_full_equipment_tag(self):
        self.assertEqual(compose_krets_posnr("136LC", "136E-021"), "136E-021")

    def test_krets_only(self):
        self.assertEqual(compose_krets_posnr("126LC", ""), "126LC")


class TestKSDInsertExtraction(unittest.TestCase):
    def setUp(self):
        self.a = KSDAdapter()

    def test_item_tag_and_category(self):
        ins = {"name": "EQ", "layer": "PS-EQUIP"}
        attrs = {"ITEM": "122E-001", "DESCRIPTION": "PULPER"}
        cat, _sub, conf = self.a.classify_insert(ins, attrs)
        self.assertEqual(cat, "process_equipment")
        self.assertEqual(conf, "high")
        tag, extra = self.a.tag_from_insert("EQ", attrs)
        self.assertEqual(tag, "122E-001")
        self.assertEqual(extra["description"], "PULPER")

    def test_pump_item_category(self):
        cat, _, _ = self.a.classify_insert({"name": "EQ", "layer": "PS-EQUIP"}, {"ITEM": "126P-001"})
        self.assertEqual(cat, "pumps")

    def test_krets_composed(self):
        attrs = {"KRETS": "126LC", "POSNR": "001"}
        cat, _, _ = self.a.classify_insert({"name": "instr", "layer": "INSTRUMENT"}, attrs)
        self.assertEqual(cat, "instruments")
        tag, extra = self.a.tag_from_insert("instr", attrs)
        self.assertEqual(tag, "126LC-001")
        self.assertEqual(extra["krets"], "126LC")

    def test_posnr_full_tag_not_composed(self):
        attrs = {"KRETS": "180LC", "POSNR": "180V-152"}
        tag, extra = self.a.tag_from_insert("instr", attrs)
        self.assertEqual(tag, "180V-152")
        self.assertEqual(extra["posnr_raw"], "180V-152")

    def test_pipeid(self):
        attrs = {"PIPEID": "126L-002", "PIPEDATA": "200-P96-VE10H2A"}
        cat, _, _ = self.a.classify_insert({"name": "PIPENO", "layer": "Pipe ID"}, attrs)
        self.assertEqual(cat, "line_markers")
        tag, extra = self.a.tag_from_insert("PIPENO", attrs)
        self.assertEqual(tag, "126L-002")
        self.assertEqual(extra["pipe_data"], "200-P96-VE10H2A")

    def test_hand_valve_layer(self):
        cat, _, _ = self.a.classify_insert({"name": "HV", "layer": "HAND-VALVE"}, {})
        self.assertEqual(cat, "valves")

    def test_instr_valve_layer(self):
        cat, _, _ = self.a.classify_insert({"name": "AV", "layer": "INSTR-VALVE"}, {})
        self.assertEqual(cat, "control_valves")


if __name__ == "__main__":
    unittest.main()
