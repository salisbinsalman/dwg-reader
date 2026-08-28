"""
Tests for dwg_reader/adapters/gor_adapter.py — GOR Fiorentini Italian adapter.
"""
import unittest

from dwg_reader.adapters.gor_adapter import GORAdapter, _tipo_family, _tipo_prefix


class TestGORAdapterIdentity(unittest.TestCase):
    def setUp(self):
        self.a = GORAdapter()

    def test_ecosystem_name(self):
        self.assertEqual(self.a.ecosystem_name, "gor")

    def test_standard_id(self):
        self.assertEqual(self.a.standard_id, "gor_fiorentini")

    def test_uses_ai_hierarchy_true(self):
        self.assertTrue(self.a.uses_ai_hierarchy)

    def test_hierarchy_prompt_is_adapter_gor(self):
        self.assertEqual(self.a.hierarchy_prompt_file, "adapter:gor")

    def test_layer_map_contains_gor_layers(self):
        lm = self.a.layer_map
        self.assertIn("1-VALVE TEXT GOR", lm)
        self.assertEqual(lm["1-VALVE TEXT GOR"][0], "valves")
        self.assertIn("1-TAG AND INSTRUMENTS GOR", lm)
        self.assertIn("1-EQUIPMENT GOR", lm)
        self.assertIn("Revison 03", lm)
        self.assertEqual(lm["Revison 03"][0], "line_markers")

    def test_block_map_contains_gor_blocks(self):
        bm = self.a.block_map
        self.assertIn("TAG VALVOLA", bm)
        self.assertEqual(bm["TAG VALVOLA"], "valves")
        self.assertIn("LOOPDCS", bm)
        self.assertIn("Pipeno", bm)
        self.assertIn("COIL", bm)


class TestGORAdapterParseTag(unittest.TestCase):
    def setUp(self):
        self.a = GORAdapter()

    def test_compound_equipment_tag(self):
        p = self.a.parse_tag("168P-410")
        self.assertEqual(p["unit_prefix"], "168")
        self.assertEqual(p["type_letters"], "P")
        self.assertEqual(p["sequence"], "410")

    def test_compound_multi_letter(self):
        p = self.a.parse_tag("168TC-001")
        self.assertEqual(p["type_letters"], "TC")
        self.assertEqual(p["sequence"], "001")

    def test_compound_valve_tag(self):
        p = self.a.parse_tag("168V-521")
        self.assertEqual(p["unit_prefix"], "168")
        self.assertEqual(p["type_letters"], "V")
        self.assertEqual(p["sequence"], "521")

    def test_simple_instrument_tag(self):
        p = self.a.parse_tag("168TC1")
        self.assertEqual(p["unit_prefix"], "168")
        self.assertEqual(p["type_letters"], "TC")
        self.assertEqual(p["sequence"], "1")

    def test_normalises_lowercase(self):
        p = self.a.parse_tag("168p-410")
        self.assertEqual(p["full"], "168P-410")


class TestGORAdapterTagClassification(unittest.TestCase):
    def setUp(self):
        self.a = GORAdapter()

    def test_equipment_tag_detected(self):
        self.assertTrue(self.a.is_equipment_tag("168P-410"))
        self.assertTrue(self.a.is_equipment_tag("168F-415"))
        self.assertTrue(self.a.is_equipment_tag("162E-010"))

    def test_hyphen_does_not_make_valve_equipment(self):
        self.assertFalse(self.a.is_equipment_tag("168V-521"))
        self.assertTrue(self.a.is_valve_tag("168V-521"))

    def test_instrument_hyphen_is_not_equipment(self):
        self.assertFalse(self.a.is_equipment_tag("168TC-001"))
        self.assertTrue(self.a.is_instrument_tag("168TC-001"))

    def test_safety_valve_variants(self):
        for tag in ("168-ST521", "168ST-061", "168-ST-096"):
            with self.subTest(tag=tag):
                self.assertTrue(self.a.is_valve_tag(tag))
                self.assertFalse(self.a.is_equipment_tag(tag))
                self.assertEqual(self.a.parse_tag(tag)["type_letters"], "ST")

    def test_line_tag_detected(self):
        self.assertTrue(self.a.is_line_tag("168L-521"))
        self.assertFalse(self.a.is_equipment_tag("168L-521"))

    def test_line_tag_not_equipment(self):
        self.assertFalse(self.a.is_equipment_tag("168L-521"))

    def test_motor_tag_detected(self):
        self.assertTrue(self.a.is_motor_tag("168P-410-M1"))
        self.assertTrue(self.a.is_motor_tag("168F-415-M2"))

    def test_base_tag_not_motor(self):
        self.assertFalse(self.a.is_motor_tag("168P-410"))

    def test_instrument_is_instrument(self):
        self.assertTrue(self.a.is_instrument_tag("168TC1"))


class TestGORAdapterMotorDerivation(unittest.TestCase):
    def setUp(self):
        self.a = GORAdapter()

    def test_fan_motor(self):
        self.assertEqual(self.a.derive_motor_tag("168F-415"), "168F-415-M1")

    def test_pump_motor(self):
        self.assertEqual(self.a.derive_motor_tag("168P-410"), "168P-410-M1")

    def test_valve_returns_none(self):
        self.assertIsNone(self.a.derive_motor_tag("168V-521"))

    def test_line_tag_returns_none(self):
        self.assertIsNone(self.a.derive_motor_tag("168L-521"))

    def test_already_motor_returns_none(self):
        self.assertIsNone(self.a.derive_motor_tag("168P-410-M1"))


class TestGORAdapterTipoMapping(unittest.TestCase):
    """TIPO_VALVOLA → SAP valve type mapping (Code 14 drawings)."""

    def setUp(self):
        self.a = GORAdapter()

    def _rv(self, tipo):
        return self.a.resolve_valve_type("168V-521", tipo=tipo)

    def test_bf_non_6prefix_is_nc(self):
        vtype, is_valve = self._rv("2K0-BF-65")
        self.assertEqual(vtype, "NC")
        self.assertTrue(is_valve)

    def test_bf_6prefix_is_av(self):
        vtype, is_valve = self._rv("6S6-BF-65")
        self.assertEqual(vtype, "AV")
        self.assertTrue(is_valve)

    def test_lwe_is_nc(self):
        vtype, is_valve = self._rv("4S4-LWE-15")
        self.assertEqual(vtype, "NC")
        self.assertTrue(is_valve)

    def test_lwe_missing_hyphen_normalised(self):
        vtype, is_valve = self._rv("4S4-LWE25")
        self.assertEqual(vtype, "NC")
        self.assertTrue(is_valve)
        self.assertEqual(_tipo_family("4S4-LWE25"), "LWE")

    def test_it_is_nc(self):
        vtype, is_valve = self._rv("4S4-IT-25")
        self.assertEqual(vtype, "NC")
        self.assertTrue(is_valve)

    def test_st_is_sv(self):
        vtype, is_valve = self._rv("ST-65")
        self.assertEqual(vtype, "SV")
        self.assertTrue(is_valve)

    def test_vx_is_av(self):
        vtype, is_valve = self._rv("VX-25")
        self.assertEqual(vtype, "AV")
        self.assertTrue(is_valve)

    def test_fl_is_not_a_valve(self):
        vtype, is_valve = self._rv("3G4-FL-65")
        self.assertIsNone(vtype)
        self.assertFalse(is_valve)

    def test_all_sh12_tipo_codes(self):
        """All TIPO codes observed in SH12 (WU12) — regression suite."""
        cases = [
            ("2K0-BF-65", "NC", True),
            ("6S6-BF-65", "AV", True),
            ("4S4-LWE-15", "NC", True),
            ("4S4-IT-25", "NC", True),
            ("ST-65", "SV", True),
            ("VX-25", "AV", True),
            ("3G4-FL-65", None, False),
        ]
        for tipo, expected_type, expected_is_valve in cases:
            with self.subTest(tipo=tipo):
                vtype, is_valve = self.a.resolve_valve_type("168V-521", tipo=tipo)
                self.assertEqual(vtype, expected_type, f"TIPO {tipo}: wrong type")
                self.assertEqual(is_valve, expected_is_valve, f"TIPO {tipo}: wrong is_valve")


class TestGORAdapterCode03Fallback(unittest.TestCase):
    """Code 03/13 valve type fallback — no TIPO attribute available."""

    def setUp(self):
        self.a = GORAdapter()

    def test_kv_tag_is_av(self):
        vtype, is_valve = self.a.resolve_valve_type("168KV-521")
        self.assertEqual(vtype, "AV")
        self.assertTrue(is_valve)

    def test_plain_v_tag_is_nc(self):
        vtype, is_valve = self.a.resolve_valve_type("168V-521")
        self.assertEqual(vtype, "NC")
        self.assertTrue(is_valve)

    def test_st_tag_is_sv(self):
        vtype, is_valve = self.a.resolve_valve_type("168ST-065")
        self.assertEqual(vtype, "SV")
        self.assertTrue(is_valve)

    def test_other_tag_defaults_hv(self):
        vtype, is_valve = self.a.resolve_valve_type("168FOO-65")
        self.assertEqual(vtype, "HV")
        self.assertTrue(is_valve)


class TestGORAdapterDescriptions(unittest.TestCase):
    def setUp(self):
        self.a = GORAdapter()

    def test_tipo_description_bf(self):
        self.assertEqual(self.a.tipo_description("2K0-BF-65"), "BUTTERFLY VLV")

    def test_tipo_description_lwe(self):
        self.assertEqual(self.a.tipo_description("4S4-LWE-15"), "SOLENOID NC VLV")

    def test_tipo_description_vx(self):
        self.assertEqual(self.a.tipo_description("VX-25"), "3-WAY SOL VLV")

    def test_tipo_description_st(self):
        self.assertEqual(self.a.tipo_description("ST-65"), "SAFETY VLV")

    def test_tipo_description_fl(self):
        self.assertEqual(self.a.tipo_description("3G4-FL-65"), "BLIND FLANGE")

    def test_instrument_description_tc(self):
        desc = self.a.instrument_description("168TC1")
        self.assertIn("TEMP CTRL", desc)

    def test_instrument_description_fan(self):
        desc = self.a.instrument_description("168F-415")
        self.assertIn("FAN", desc)

    def test_instrument_description_max_40(self):
        self.assertLessEqual(len(self.a.instrument_description("168TC1")), 40)


class TestGORAdapterTipoHelpers(unittest.TestCase):
    def test_tipo_family_three_part(self):
        self.assertEqual(_tipo_family("2K0-BF-65"), "BF")

    def test_tipo_family_two_part(self):
        self.assertEqual(_tipo_family("ST-65"), "ST")

    def test_tipo_prefix_three_part(self):
        self.assertEqual(_tipo_prefix("6S6-BF-65"), "6S6")

    def test_tipo_prefix_two_part(self):
        self.assertEqual(_tipo_prefix("ST-65"), "ST")


class TestGORAdapterLoadStandard(unittest.TestCase):
    def test_load_standard_has_tipo_map(self):
        std = GORAdapter().load_standard()
        self.assertIn("tipo_valvola_map", std)
        self.assertIn("BF_6prefix", std["tipo_valvola_map"])

    def test_load_standard_has_blocks(self):
        std = GORAdapter().load_standard()
        self.assertIn("blocks", std)
        self.assertEqual(std["blocks"]["TAG VALVOLA"], "valve")

    def test_load_standard_has_motor_rule(self):
        std = GORAdapter().load_standard()
        self.assertEqual(std["motor_from_equipment"]["mode"], "append_suffix")
        self.assertEqual(std["motor_from_equipment"]["suffix"], "-M1")


class TestGORInsertExtraction(unittest.TestCase):
    def setUp(self):
        self.a = GORAdapter()

    def test_tag_valvola_attrs(self):
        ins = {"name": "TAG VALVOLA", "layer": "1-VALVE TEXT GOR"}
        attrs = {"TAG_VALVOLA": "168V-521", "TIPO_VALVOLA": "2K0-BF-65"}
        cat, _, _ = self.a.classify_insert(ins, attrs)
        self.assertEqual(cat, "valves")
        tag, extra = self.a.tag_from_insert("TAG VALVOLA", attrs)
        self.assertEqual(tag, "168V-521")
        self.assertEqual(extra["valve_type"], "2K0-BF-65")

    def test_tipo_typo_normalised_in_extra(self):
        tag, extra = self.a.tag_from_insert(
            "TAG VALVOLA",
            {"TAG_VALVOLA": "168V-001", "TIPO_VALVOLA": "4S4-LWE25"},
        )
        self.assertEqual(tag, "168V-001")
        self.assertEqual(extra["valve_type"], "4S4-LWE-25")
        self.assertEqual(extra["tipo_raw"], "4S4-LWE25")

    def test_pipeno_pipeid(self):
        attrs = {"PIPEID": "168L-521", "PIPEDATA": "65-W38-VE10H2A"}
        cat, _, _ = self.a.classify_insert({"name": "Pipeno", "layer": "Revison 03"}, attrs)
        self.assertEqual(cat, "line_markers")
        tag, extra = self.a.tag_from_insert("Pipeno", attrs)
        self.assertEqual(tag, "168L-521")
        self.assertEqual(extra["pipe_data"], "65-W38-VE10H2A")

    def test_foreign_ksd_layer_is_other(self):
        cat, sub, _ = self.a.classify_insert({"name": "EQ", "layer": "1-EQUIPMENT KSD"}, {})
        self.assertEqual(cat, "other_inserts")
        self.assertEqual(sub, "foreign_layer")

    def test_foreign_kawanoe_layer_is_other(self):
        cat, sub, _ = self.a.classify_insert({"name": "X", "layer": "KAWANOE-EQUIP"}, {})
        self.assertEqual(cat, "other_inserts")
        self.assertEqual(sub, "foreign_layer")


class TestGORRepairHierarchy(unittest.TestCase):
    def setUp(self):
        self.a = GORAdapter()

    def test_reparents_valve_and_injects_inventory(self):
        rows = [
            {"SUB-PROCESS": "WUC", "FUNCTION": "WU12", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "", "DESCRIPTION": "WU12"},
            {"SUB-PROCESS": "WUC", "FUNCTION": "", "EQUIPMENT": "168L-521", "SUB-EQUIPMENT": "", "MASK": "", "DESCRIPTION": "PIPE"},
            {"SUB-PROCESS": "WUC", "FUNCTION": "", "EQUIPMENT": "168L-533", "SUB-EQUIPMENT": "", "MASK": "", "DESCRIPTION": "PIPE"},
            {"SUB-PROCESS": "WUC", "FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": "168VX-521", "MASK": "", "DESCRIPTION": "VX"},
        ]
        inv = {
            "lines": [{"line_number": "168L-521"}, {"line_number": "168L-532"}],
            "valves": [{"tag": "168V-521"}, {"tag": "168-ST521"}, {"tag": "168VX-521"}],
        }
        out = self.a.repair_hierarchy(rows, inv)
        subs_under_521 = []
        current = ""
        for r in out:
            eq = r.get("EQUIPMENT") or ""
            sub = r.get("SUB-EQUIPMENT") or ""
            if eq:
                current = eq
            if sub and current == "168L-521":
                subs_under_521.append(sub)
        self.assertIn("168VX-521", subs_under_521)
        self.assertIn("168V-521", subs_under_521)
        self.assertIn("168-ST521", subs_under_521)
        self.assertIn("168L-532", {r.get("EQUIPMENT") for r in out})


if __name__ == "__main__":
    unittest.main()
