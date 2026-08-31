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
from dwg_reader.run_hierarchy_orchestrator import (
    _append_agitator_equipment_rows,
    _append_missing_machine_functions,
    write_hierarchy_csv,
)


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

    def test_motor_eqktx_pump_example_from_motors_docx(self) -> None:
        """H-04: Example for motors.docx — 35-24P518 → 35-24-518.1."""
        eqktx = _motor_eqktx(
            "35-24-518.1",
            "35-24P518",
            "35-24P518 BROKE REJECT PMP",
        )
        self.assertTrue(eqktx.startswith("35-24-518.1"))
        self.assertIn("MTR", eqktx.upper())
        self.assertIn("BROKE", eqktx.upper())
        self.assertNotIn("PMP", eqktx.upper())


class MissingMachineFunctionTests(unittest.TestCase):
    def test_appends_p518_when_inventory_has_it(self) -> None:
        import csv
        import json

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            hier = td_path / "h.csv"
            write_hierarchy_csv(
                hier,
                [
                    {
                        "SUB-PROCESS": "",
                        "FUNCTION": "35-24L001",
                        "EQUIPMENT": "",
                        "SUB-EQUIPMENT": "",
                        "MASK": "",
                        "DESCRIPTION": "PRESS PLPR",
                    },
                ],
            )
            inv = {
                "functions": [
                    {"function": "35-24L001", "kind": "equipment", "description": "PRESS PLPR"},
                    {
                        "function": "35-24P518",
                        "kind": "equipment",
                        "description": "35-24P518 BROKE REJECT PMP",
                    },
                ]
            }
            inv_path = td_path / "inv.json"
            inv_path.write_text(json.dumps(inv), encoding="utf-8")
            n = _append_missing_machine_functions(hier, inv_path)
            self.assertEqual(n, 1)
            rows = list(csv.DictReader(hier.open(encoding="utf-8")))
            fns = [r["FUNCTION"] for r in rows if r.get("FUNCTION")]
            self.assertIn("35-24P518", fns)

            out = build_equipment_rows(rows)
            by_tag = {r["EQUNR"]: r for r in out}
            self.assertIn("35-24P518", by_tag)
            self.assertIn("35-24-518.1", by_tag)
            self.assertEqual(by_tag["35-24-518.1"]["HEQUI"], "35-24P518")
            self.assertEqual(by_tag["35-24-518.1"]["EQART"], "1101")

    def test_does_not_duplicate_existing_function(self) -> None:
        import json

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            hier = td_path / "h.csv"
            write_hierarchy_csv(
                hier,
                [
                    {
                        "SUB-PROCESS": "",
                        "FUNCTION": "35-24P518",
                        "EQUIPMENT": "",
                        "SUB-EQUIPMENT": "",
                        "MASK": "",
                        "DESCRIPTION": "PMP",
                    },
                ],
            )
            inv_path = td_path / "inv.json"
            inv_path.write_text(
                json.dumps({"functions": [{"function": "35-24P518", "kind": "equipment"}]}),
                encoding="utf-8",
            )
            self.assertEqual(_append_missing_machine_functions(hier, inv_path), 0)


class AgitatorBindStepTests(unittest.TestCase):
    """C-09: run_agitator_bind coverage + vision fallback (no Bedrock)."""

    def _write(self, td: Path, rows, inv, structural=None):
        from dwg_reader.run_hierarchy_orchestrator import write_hierarchy_csv
        import json

        hier = td / "Broke System.hierarchy_orchestrator.csv"
        write_hierarchy_csv(hier, rows)
        inv_path = td / "inv.json"
        inv_path.write_text(json.dumps(inv), encoding="utf-8")
        struct_path = None
        if structural is not None:
            struct_path = td / "struct.json"
            struct_path.write_text(json.dumps(structural), encoding="utf-8")
        return hier, inv_path, struct_path

    def test_parse_propeller_reply(self) -> None:
        from dwg_reader.dwg_agitator_bind import parse_propeller_reply

        self.assertTrue(parse_propeller_reply('{"propeller": true}'))
        self.assertFalse(parse_propeller_reply('{"propeller": false}'))
        self.assertTrue(parse_propeller_reply('Sure.\n{"propeller": true}\n'))
        self.assertFalse(parse_propeller_reply("nope"))

    def test_vessel_coverage_flags_tank_without_agitator(self) -> None:
        from dwg_reader.dwg_agitator_bind import run_agitator_bind

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            hier, inv_path, _ = self._write(
                td_path,
                [
                    {
                        "SUB-PROCESS": "",
                        "FUNCTION": "35-24T606",
                        "EQUIPMENT": "",
                        "SUB-EQUIPMENT": "",
                        "MASK": "",
                        "DESCRIPTION": "BROKE REJECT TANK",
                    },
                ],
                {"functions": [{"function": "35-24T606", "x": 100.0, "y": 100.0}], "agitators": []},
            )
            report = run_agitator_bind(
                hierarchy_csv=hier,
                inventory_json=inv_path,
                out_dir=td_path,
                input_path=Path("inputs/Broke System.dwg"),
                vision=False,
            )
            self.assertEqual(report["tanks_without_agitator"], ["35-24T606"])
            self.assertEqual(report["tanks_with_agitator"], [])
            cache = td_path / "jsons" / "Broke System.agitator_bind.json"
            self.assertTrue(cache.is_file())

    def test_vision_yes_binds_nearby_l4xx(self) -> None:
        from dwg_reader.dwg_agitator_bind import run_agitator_bind
        from dwg_reader.run_hierarchy_orchestrator import read_hierarchy_csv

        structural = {
            "text_entities": [
                {
                    "text": "35-24L404",
                    "layer": "P-AGITATOR_POS",
                    "position": [102.0, 98.0, 0.0],
                },
                {
                    "text": "BROKE REJECT",
                    "layer": "P-TANK_POS",
                    "position": [100.0, 90.0, 0.0],
                },
            ]
        }
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            hier, inv_path, struct_path = self._write(
                td_path,
                [
                    {
                        "SUB-PROCESS": "",
                        "FUNCTION": "35-24T606",
                        "EQUIPMENT": "",
                        "SUB-EQUIPMENT": "",
                        "MASK": "",
                        "DESCRIPTION": "BROKE REJECT TANK",
                    },
                ],
                {"functions": [{"function": "35-24T606", "x": 100.0, "y": 100.0}], "agitators": []},
                structural,
            )
            report = run_agitator_bind(
                hierarchy_csv=hier,
                inventory_json=inv_path,
                structural_json=struct_path,
                out_dir=td_path,
                input_path=Path("inputs/Broke System.dwg"),
                vision=True,
                vision_detect=lambda _fn, _crop: True,
            )
            self.assertEqual(report["untagged_propellers"], [])
            rows = read_hierarchy_csv(hier)
            tags = [r.get("EQUIPMENT") for r in rows if r.get("EQUIPMENT")]
            self.assertIn("35-24L404", tags)
            self.assertIn("35-24T606", report["tanks_with_agitator"])

    def test_vision_yes_without_tag_does_not_invent(self) -> None:
        from dwg_reader.dwg_agitator_bind import run_agitator_bind
        from dwg_reader.run_hierarchy_orchestrator import read_hierarchy_csv

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            hier, inv_path, struct_path = self._write(
                td_path,
                [
                    {
                        "SUB-PROCESS": "",
                        "FUNCTION": "35-24T606",
                        "EQUIPMENT": "",
                        "SUB-EQUIPMENT": "",
                        "MASK": "",
                        "DESCRIPTION": "BROKE REJECT TANK",
                    },
                ],
                {"functions": [{"function": "35-24T606", "x": 100.0, "y": 100.0}], "agitators": []},
                {"text_entities": []},
            )
            report = run_agitator_bind(
                hierarchy_csv=hier,
                inventory_json=inv_path,
                structural_json=struct_path,
                out_dir=td_path,
                input_path=Path("inputs/Broke System.dwg"),
                vision=True,
                vision_detect=lambda _fn, _crop: True,
            )
            self.assertEqual(report["untagged_propellers"], ["35-24T606"])
            rows = read_hierarchy_csv(hier)
            tags = [r.get("EQUIPMENT") for r in rows if r.get("EQUIPMENT")]
            self.assertEqual(tags, [])
            self.assertTrue(any(r.get("EQUIPMENT", "").startswith("35-24L") for r in rows) is False)

    def test_vision_no_leaves_tank_alone(self) -> None:
        from dwg_reader.dwg_agitator_bind import run_agitator_bind
        from dwg_reader.run_hierarchy_orchestrator import read_hierarchy_csv

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            hier, inv_path, struct_path = self._write(
                td_path,
                [
                    {
                        "SUB-PROCESS": "",
                        "FUNCTION": "35-24L001",
                        "EQUIPMENT": "",
                        "SUB-EQUIPMENT": "",
                        "MASK": "",
                        "DESCRIPTION": "PRESS PLPR",
                    },
                ],
                {"functions": [{"function": "35-24L001", "x": 50.0, "y": 50.0}], "agitators": []},
                {"text_entities": []},
            )
            report = run_agitator_bind(
                hierarchy_csv=hier,
                inventory_json=inv_path,
                structural_json=struct_path,
                out_dir=td_path,
                input_path=Path("inputs/Broke System.dwg"),
                vision=True,
                vision_detect=lambda _fn, _crop: False,
            )
            self.assertEqual(report["tanks_without_agitator"], ["35-24L001"])
            self.assertFalse(any(v.get("propeller") for v in report["vision"]))
            rows = read_hierarchy_csv(hier)
            self.assertEqual([r.get("EQUIPMENT") for r in rows if r.get("EQUIPMENT")], [])


if __name__ == "__main__":
    unittest.main()
