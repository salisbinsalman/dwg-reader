"""Inventory extraction via CAD-ecosystem adapters (KSD / GOR / SML)."""
from __future__ import annotations

import unittest

from dwg_reader.adapters.gor_adapter import GORAdapter
from dwg_reader.adapters.ksd_adapter import KSDAdapter
from dwg_reader.adapters.sml_adapter import SMLAdapter
from dwg_reader.dwg_pid_inventory import build_inventory, validate_inventory


def _ins(handle, name, layer, attrs=None, xy=(0.0, 0.0)):
    return {
        "handle": handle,
        "name": name,
        "layer": layer,
        "insert": [xy[0], xy[1], 0.0],
        "rotation": 0,
        "attributes": [{"tag": k, "text": v} for k, v in (attrs or {}).items()],
    }


def _text(handle, layer, text, xy=(0.0, 0.0)):
    return {
        "handle": handle,
        "layer": layer,
        "text": text,
        "position": [xy[0], xy[1], 0.0],
    }


class TestKSDInventoryBuild(unittest.TestCase):
    def setUp(self):
        self.structural = {
            "inserts": [
                _ins("H1", "EQ", "PS-EQUIP", {"ITEM": "122E-001", "DESCRIPTION": "PULPER"}, (10, 10)),
                _ins("H2", "EQ", "PS-EQUIP", {"ITEM": "126P-001"}, (20, 10)),
                _ins("H3", "instr", "INSTRUMENT", {"KRETS": "126LC", "POSNR": "001"}, (30, 10)),
                _ins("H4", "instr", "INSTRUMENT", {"KRETS": "180LC", "POSNR": "180V-152"}, (40, 10)),
                _ins("H5", "PIPENO", "Pipe ID", {"PIPEID": "126L-002", "PIPEDATA": "200-P96-VE10H2A"}, (50, 10)),
                _ins("H6", "HV", "HAND-VALVE", {}, (60, 10)),
                _ins("H7", "AV", "INSTR-VALVE", {}, (70, 10)),
            ],
            "text_entities": [],
            "entities": [],
        }
        self.inv = build_inventory(self.structural, dwg_stem="KSDM160104102")

    def test_detects_ksd(self):
        tags = {r["tag"] for r in self.inv["process_equipment"]}
        self.assertIn("122E-001", tags)

    def test_pump_from_item(self):
        tags = {r["tag"] for r in self.inv["pumps"]}
        self.assertIn("126P-001", tags)

    def test_krets_composed(self):
        tags = {r["tag"] for r in self.inv["instruments"]}
        self.assertIn("126LC-001", tags)

    def test_posnr_full_tag_not_composed_as_loop(self):
        instr = {r["tag"] for r in self.inv["instruments"]}
        self.assertNotIn("180LC-180V-152", instr)
        valves = {r["tag"] for r in self.inv["valves"]}
        self.assertIn("180V-152", valves)

    def test_pipeid_line(self):
        lines = {r["line_number"] for r in self.inv["lines"]}
        self.assertIn("126L-002", lines)
        self.assertEqual(self.inv["lines"][0]["source"], "ksd_pipe_id")

    def test_valve_layers(self):
        self.assertTrue(any(r["layer"] == "HAND-VALVE" for r in self.inv["valves"]))
        self.assertTrue(any(r["layer"] == "INSTR-VALVE" for r in self.inv["control_valves"]))

    def test_no_valmet_false_empty(self):
        self.assertEqual(self.inv["tanks"], [])

    def test_functions_from_item_tags(self):
        fns = {r["function"] for r in self.inv["functions"]}
        self.assertIn("122E-001", fns)
        self.assertIn("126P-001", fns)
        self.assertNotIn("126L-002", fns)

    def test_insert_coverage(self):
        report = validate_inventory(self.structural, self.inv, adapter=KSDAdapter(), dwg_stem="KSDM160104")
        coverage = next(c for c in report["checks"] if c["category"] == "insert_coverage")
        self.assertTrue(coverage["pass"], coverage)


class TestGORCode14InventoryBuild(unittest.TestCase):
    def setUp(self):
        self.structural = {
            "inserts": [
                _ins(
                    "G1",
                    "TAG VALVOLA",
                    "1-VALVE TEXT GOR",
                    {"TAG_VALVOLA": "168V-521", "TIPO_VALVOLA": "2K0-BF-65"},
                    (1, 1),
                ),
                _ins(
                    "G2",
                    "Pipeno",
                    "Revison 03",
                    {"PIPEID": "168L-521", "PIPEDATA": "65-W38-VE10H2A"},
                    (2, 1),
                ),
                _ins("G3", "FOREIGN", "1-EQUIPMENT KSD", {}, (3, 1)),
            ],
            "text_entities": [],
            "entities": [],
        }
        self.inv = build_inventory(self.structural, dwg_stem="GORA68208")

    def test_valve_tag_from_attr(self):
        tags = {r["tag"] for r in self.inv["valves"]}
        self.assertIn("168V-521", tags)
        valve = next(r for r in self.inv["valves"] if r["tag"] == "168V-521")
        self.assertEqual(valve["valve_type"], "2K0-BF-65")

    def test_pipeid_line(self):
        lines = {r["line_number"] for r in self.inv["lines"]}
        self.assertIn("168L-521", lines)
        self.assertEqual(self.inv["lines"][0]["source"], "gor_pipe_id")

    def test_foreign_layer_other_inserts(self):
        others = [r for r in self.inv["other_inserts"] if r["handle"] == "G3"]
        self.assertEqual(len(others), 1)
        self.assertEqual(others[0]["sub_type"], "foreign_layer")

    def test_insert_coverage(self):
        report = validate_inventory(self.structural, self.inv, adapter=GORAdapter())
        coverage = next(c for c in report["checks"] if c["category"] == "insert_coverage")
        self.assertTrue(coverage["pass"], coverage)


class TestGORCode03InventoryBuild(unittest.TestCase):
    def setUp(self):
        self.structural = {
            "inserts": [],
            "text_entities": [
                _text("T1", "1-TAG AND INSTRUMENTS GOR", "162E-010", (1, 1)),
                _text("T2", "1-TAG AND INSTRUMENTS GOR", "162TC1", (2, 1)),
                _text("T3", "1-VALVE TEXT GOR", "162V-001", (3, 1)),
                _text("T4", "1-VALVE TEXT GOR", "162KV3-575", (4, 1)),
            ],
            "entities": [],
        }
        self.inv = build_inventory(self.structural, dwg_stem="GORA68210")

    def test_equipment_text_not_instrument(self):
        instr = {r["tag"] for r in self.inv["instruments"]}
        self.assertNotIn("162E-010", instr)
        equip = {r["tag"] for r in self.inv["process_equipment"]}
        self.assertIn("162E-010", equip)

    def test_instrument_text(self):
        instr = {r["tag"] for r in self.inv["instruments"]}
        self.assertIn("162TC1", instr)

    def test_valve_texts(self):
        valves = {r["tag"] for r in self.inv["valves"]}
        self.assertIn("162V-001", valves)
        self.assertIn("162KV3-575", valves)


class TestSMLSensorLayer(unittest.TestCase):
    def test_sensor_pos_is_instrument(self):
        structural = {
            "inserts": [_ins("S1", "SENSOR", "P-SENSOR_POS", {}, (1, 1))],
            "text_entities": [],
            "entities": [],
        }
        inv = build_inventory(structural, dwg_stem="Broke System")
        self.assertEqual(len(inv["instruments"]), 1)
        self.assertEqual(inv["instruments"][0]["layer"], "P-SENSOR_POS")
        report = validate_inventory(structural, inv, adapter=SMLAdapter())
        coverage = next(c for c in report["checks"] if c["category"] == "insert_coverage")
        self.assertTrue(coverage["pass"], coverage)


if __name__ == "__main__":
    unittest.main()
