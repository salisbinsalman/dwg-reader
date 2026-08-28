"""
Tests for dwg_reader/adapters/__init__.py — adapter registry and factory.
Also tests Ecosystem.adapter property integration with dwg_ecosystem.detect().
"""
import unittest

from dwg_reader.adapters import (
    BaseAdapter,
    GORAdapter,
    KSDAdapter,
    SMLAdapter,
    UnknownEcosystemError,
    adapter_classes,
    adapter_for,
)
from dwg_reader.dwg_ecosystem import Ecosystem, detect


class TestAdapterFactory(unittest.TestCase):
    def test_valmet_returns_sml(self):
        a = adapter_for("valmet")
        self.assertIsInstance(a, SMLAdapter)

    def test_gor_returns_gor(self):
        a = adapter_for("gor")
        self.assertIsInstance(a, GORAdapter)

    def test_ksd_returns_ksd(self):
        a = adapter_for("ksd")
        self.assertIsInstance(a, KSDAdapter)

    def test_unknown_raises(self):
        with self.assertRaises(UnknownEcosystemError):
            adapter_for("unknown_ecosystem")

    def test_empty_string_raises(self):
        with self.assertRaises(UnknownEcosystemError):
            adapter_for("")

    def test_case_insensitive(self):
        self.assertIsInstance(adapter_for("GOR"), GORAdapter)
        self.assertIsInstance(adapter_for("KSD"), KSDAdapter)
        self.assertIsInstance(adapter_for("VALMET"), SMLAdapter)


class TestAdapterRegistry(unittest.TestCase):
    def test_classes_has_three_entries(self):
        classes = adapter_classes()
        self.assertEqual(len(classes), 3)
        self.assertIn("valmet", classes)
        self.assertIn("gor", classes)
        self.assertIn("ksd", classes)

    def test_all_classes_are_base_adapter_subclasses(self):
        for name, cls in adapter_classes().items():
            with self.subTest(name=name):
                self.assertTrue(issubclass(cls, BaseAdapter))

    def test_registry_is_copy(self):
        # Mutating the returned dict must not affect subsequent calls.
        classes = adapter_classes()
        classes["evil"] = SMLAdapter
        self.assertNotIn("evil", adapter_classes())


class TestAdapterInterface(unittest.TestCase):
    """Each adapter must fully implement the BaseAdapter interface."""

    adapters = [SMLAdapter(), GORAdapter(), KSDAdapter()]

    def test_ecosystem_name_nonempty(self):
        for a in self.adapters:
            with self.subTest(a=type(a).__name__):
                self.assertTrue(a.ecosystem_name)

    def test_standard_id_nonempty(self):
        for a in self.adapters:
            with self.subTest(a=type(a).__name__):
                self.assertTrue(a.standard_id)

    def test_layer_map_is_dict(self):
        for a in self.adapters:
            with self.subTest(a=type(a).__name__):
                lm = a.layer_map
                self.assertIsInstance(lm, dict)
                self.assertGreater(len(lm), 0)

    def test_layer_map_values_are_tuples(self):
        for a in self.adapters:
            for layer, val in a.layer_map.items():
                with self.subTest(adapter=type(a).__name__, layer=layer):
                    self.assertIsInstance(val, tuple)
                    self.assertEqual(len(val), 2)

    def test_parse_tag_returns_dict_with_full(self):
        cases = {
            SMLAdapter(): "35-24P518",
            GORAdapter(): "168P-410",
            KSDAdapter(): "122E-001",
        }
        for a, tag in cases.items():
            with self.subTest(adapter=type(a).__name__, tag=tag):
                result = a.parse_tag(tag)
                self.assertIsInstance(result, dict)
                self.assertIn("full", result)

    def test_is_equipment_tag_consistent(self):
        cases = {
            SMLAdapter(): ("35-24P518", True),
            GORAdapter(): ("168P-410", True),
            KSDAdapter(): ("122E-001", True),
        }
        for a, (tag, expected) in cases.items():
            with self.subTest(adapter=type(a).__name__):
                self.assertEqual(a.is_equipment_tag(tag), expected)

    def test_is_line_tag_consistent(self):
        cases = {
            SMLAdapter(): ("35-24-095", True),
            GORAdapter(): ("168L-521", True),
            KSDAdapter(): ("136L-001", True),
        }
        for a, (tag, expected) in cases.items():
            with self.subTest(adapter=type(a).__name__):
                self.assertEqual(a.is_line_tag(tag), expected)

    def test_derive_motor_tag_returns_str_or_none(self):
        cases = {
            SMLAdapter(): "35-24P518",
            GORAdapter(): "168P-410",
            KSDAdapter(): "132P-001",
        }
        for a, tag in cases.items():
            with self.subTest(adapter=type(a).__name__, tag=tag):
                result = a.derive_motor_tag(tag)
                self.assertIsInstance(result, str)
                self.assertTrue(len(result) > 0)

    def test_resolve_valve_type_returns_tuple(self):
        cases = {
            SMLAdapter(): ("35-24HV-548", {}),
            GORAdapter(): ("168V-521", {}),
            KSDAdapter(): ("126V-001", {}),
        }
        for a, (tag, kwargs) in cases.items():
            with self.subTest(adapter=type(a).__name__):
                result = a.resolve_valve_type(tag, **kwargs)
                self.assertIsInstance(result, tuple)
                self.assertEqual(len(result), 2)
                vtype, is_valve = result
                self.assertIsInstance(is_valve, bool)

    def test_load_standard_succeeds(self):
        for a in self.adapters:
            with self.subTest(a=type(a).__name__):
                std = a.load_standard()
                self.assertIsInstance(std, dict)
                self.assertIn("motor_from_equipment", std)

    def test_normalize_description_clips_to_40(self):
        long = "VERY LONG DESCRIPTION THAT SHOULD BE CLIPPED BEFORE FORTY CHARS"
        for a in self.adapters:
            with self.subTest(a=type(a).__name__):
                result = a.normalize_description(long)
                self.assertLessEqual(len(result), 40)


class TestEcosystemAdapterProperty(unittest.TestCase):
    """Ecosystem.adapter property returns the correct adapter instance."""

    def test_valmet_stem_returns_sml_adapter(self):
        eco = detect("Broke System")
        self.assertIsInstance(eco.adapter, SMLAdapter)

    def test_stod_stem_returns_sml_adapter(self):
        eco = detect("STOD206340")
        self.assertIsInstance(eco.adapter, SMLAdapter)

    def test_gorb_stem_returns_gor_adapter(self):
        eco = detect("GORB18779")
        self.assertIsInstance(eco.adapter, GORAdapter)

    def test_gora_stem_returns_gor_adapter(self):
        eco = detect("GORA68210")
        self.assertIsInstance(eco.adapter, GORAdapter)

    def test_ksdm_stem_returns_ksd_adapter(self):
        eco = detect("KSDM160104")
        self.assertIsInstance(eco.adapter, KSDAdapter)

    def test_gor_inventory_signal_returns_gor_adapter(self):
        inventory = {
            "valves": [{"block_name": "TAG VALVOLA", "tag": "168V-521"}]
        }
        eco = detect("", inventory=inventory)
        self.assertIsInstance(eco.adapter, GORAdapter)

    def test_adapter_uses_ai_matches_ecosystem(self):
        gor_eco = detect("GORB18779")
        self.assertTrue(gor_eco.adapter.uses_ai_hierarchy)

        sml_eco = detect("Broke System")
        self.assertTrue(sml_eco.adapter.uses_ai_hierarchy)

        ksd_eco = detect("KSDM160104")
        self.assertTrue(ksd_eco.adapter.uses_ai_hierarchy)


class TestEcosystemProperties(unittest.TestCase):
    def test_is_gor_property(self):
        eco = detect("GORB18779")
        self.assertTrue(eco.is_gor)
        self.assertFalse(eco.is_ksd)
        self.assertFalse(eco.is_valmet)

    def test_is_ksd_property(self):
        eco = detect("KSDM160104")
        self.assertTrue(eco.is_ksd)
        self.assertFalse(eco.is_gor)

    def test_is_valmet_property(self):
        eco = detect("STOD206340")
        self.assertTrue(eco.is_valmet)

    def test_is_tissue_true_for_gor_and_ksd(self):
        self.assertTrue(detect("GORB18779").is_tissue)
        self.assertTrue(detect("KSDM160104").is_tissue)
        self.assertFalse(detect("STOD206340").is_tissue)

    def test_ecosystem_standard_ids_updated(self):
        self.assertEqual(detect("GORB18779").standard_id, "gor_fiorentini")
        self.assertEqual(detect("KSDM160104").standard_id, "ksd_andritz")
        self.assertEqual(detect("STOD206340").standard_id, "valmet_ps21")


class TestMotorDerivationConsistency(unittest.TestCase):
    """Cross-adapter motor derivation — confirm correct suffixes per standard."""

    def test_sml_dot_one_suffix(self):
        motor = SMLAdapter().derive_motor_tag("35-24P518")
        self.assertTrue(motor.endswith(".1"), f"Expected .1 suffix, got: {motor}")

    def test_gor_m1_suffix(self):
        motor = GORAdapter().derive_motor_tag("168P-410")
        self.assertTrue(motor.endswith("-M1"), f"Expected -M1 suffix, got: {motor}")

    def test_ksd_m1_suffix(self):
        motor = KSDAdapter().derive_motor_tag("132P-001")
        self.assertTrue(motor.endswith("-M1"), f"Expected -M1 suffix, got: {motor}")

    def test_sml_strips_type_letter(self):
        motor = SMLAdapter().derive_motor_tag("35-24P518")
        # Motor tag should NOT contain the P type letter
        self.assertNotIn("P", motor.replace("35-24", "").replace("-518.1", ""))
        self.assertEqual(motor, "35-24-518.1")

    def test_gor_preserves_type_letters(self):
        motor = GORAdapter().derive_motor_tag("168F-415")
        self.assertEqual(motor, "168F-415-M1")

    def test_ksd_preserves_type_letter(self):
        motor = KSDAdapter().derive_motor_tag("122E-001")
        self.assertEqual(motor, "122E-001-M1")


if __name__ == "__main__":
    unittest.main()
