"""Agitator symbol→tag binding and motor description coverage."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dwg_reader.dwg_pid_inventory import (
    _agitator_description,
    _is_agitator_equipment_tag,
    bind_agitator_tags,
)
from dwg_reader.export_sap_equipment import _motor_eqktx, build_equipment_rows
from dwg_reader.run_hierarchy_orchestrator import _append_agitator_equipment_rows, write_hierarchy_csv


class AgitatorBindTests(unittest.TestCase):
    def test_is_agitator_range(self) -> None:
        self.assertTrue(_is_agitator_equipment_tag("35-24L401"))
        self.assertTrue(_is_agitator_equipment_tag("35-24L499"))
        self.assertFalse(_is_agitator_equipment_tag("35-24L400"))
        self.assertFalse(_is_agitator_equipment_tag("35-24L002"))
        self.assertFalse(_is_agitator_equipment_tag("PPI_0802A-25_0"))

    def test_agitator_description_prefers_tank_name(self) -> None:
        hits = [
            {"text": "2,7 %", "layer": "P-TANK_POS", "distance": 10},
            {"text": "15 m³", "layer": "P-TANK_POS", "distance": 12},
            {"text": "TANK", "layer": "P-TANK_POS", "distance": 14},
            {"text": "BROKE REJECT", "layer": "P-TANK_POS", "distance": 16},
            {"text": "SFVPT-110-2", "layer": "P-TEXT", "distance": 8},
        ]
        desc = _agitator_description("35-24L404", hits)
        self.assertEqual(desc, "35-24L404 BROKE REJECT AGITATOR TANK")

    def test_bind_nearest_l40x_text(self) -> None:
        structural = {
            "text_entities": [
                {
                    "text": "35-24L404",
                    "layer": "P-AGITATOR_POS",
                    "position": [100.0, 100.0, 0.0],
                },
                {
                    "text": "BROKE REJECT",
                    "layer": "P-TANK_POS",
                    "position": [105.0, 90.0, 0.0],
                },
                {
                    "text": "TANK",
                    "layer": "P-TANK_POS",
                    "position": [105.0, 85.0, 0.0],
                },
            ]
        }
        inventory = {
            "agitators": [
                {
                    "source": "insert",
                    "tag": "PPI_0802A-25_0",
                    "block_name": "PPI_0802A-25_0",
                    "x": 98.0,
                    "y": 99.0,
                    "z": 0.0,
                }
            ]
        }
        n = bind_agitator_tags(inventory, structural)
        self.assertEqual(n, 1)
        item = inventory["agitators"][0]
        self.assertEqual(item["tag"], "35-24L404")
        self.assertIn("BROKE REJECT", item["description"])
        self.assertIn("AGITATOR TANK", item["description"])

    def test_append_agitator_under_tank(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            hier = td_path / "h.csv"
            write_hierarchy_csv(
                hier,
                [
                    {
                        "SUB-PROCESS": "",
                        "FUNCTION": "35-24T606",
                        "EQUIPMENT": "",
                        "SUB-EQUIPMENT": "",
                        "MASK": "",
                        "DESCRIPTION": "BROKE REJECT TANK",
                    },
                    {
                        "SUB-PROCESS": "",
                        "FUNCTION": "",
                        "EQUIPMENT": "35-24-172",
                        "SUB-EQUIPMENT": "",
                        "MASK": "",
                        "DESCRIPTION": "LINE",
                    },
                ],
            )
            inv = {
                "functions": [
                    {"function": "35-24T606", "x": 100.0, "y": 100.0},
                ],
                "agitators": [
                    {
                        "source": "insert",
                        "tag": "35-24L404",
                        "x": 105.0,
                        "y": 102.0,
                        "description": "35-24L404 BROKE REJECT AGITATOR TANK",
                    }
                ],
            }
            inv_path = td_path / "inv.json"
            inv_path.write_text(__import__("json").dumps(inv), encoding="utf-8")
            n = _append_agitator_equipment_rows(hier, inv_path)
            self.assertEqual(n, 1)
            with hier.open(encoding="utf-8") as fh:
                rows = list(__import__("csv").DictReader(fh))
            eq = [r for r in rows if r.get("EQUIPMENT") == "35-24L404"]
            self.assertEqual(len(eq), 1)
            # Parent of agitator is previous FN header T606
            idx = next(i for i, r in enumerate(rows) if r.get("EQUIPMENT") == "35-24L404")
            self.assertEqual(rows[0]["FUNCTION"], "35-24T606")
            self.assertLess(0, idx)

            out = build_equipment_rows(rows)
            motor = next(r for r in out if r["EQUNR"] == "35-24-404.1")
            self.assertEqual(motor["HEQUI"], "35-24L404")
            self.assertIn("BROKE", motor["EQKTX"].upper())
            self.assertIn("MTR", motor["EQKTX"].upper())

    def test_motor_eqktx_example_for_motors(self) -> None:
        # resources/Naming Standards/Example for motors.docx
        eqktx = _motor_eqktx(
            "35-24-404.1",
            "35-24L404",
            "35-24L404 BROKE REJECT AGITATOR TANK",
        )
        self.assertTrue(eqktx.startswith("35-24-404.1"))
        self.assertIn("MTR", eqktx.upper())
        self.assertIn("BROKE", eqktx.upper())


if __name__ == "__main__":
    unittest.main()
