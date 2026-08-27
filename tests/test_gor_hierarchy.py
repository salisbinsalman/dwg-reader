"""GOR hierarchy: instrument labels, fan motors as sub-equipment, line PIPE text."""

from __future__ import annotations

import unittest

from dwg_reader.export_sap_equipment import build_equipment_rows
from dwg_reader.run_hierarchy_orchestrator import _gor_instr_desc, build_gor_hierarchy


class GorInstrDescTests(unittest.TestCase):
    def test_known_letter_codes(self) -> None:
        self.assertEqual(_gor_instr_desc("168TC1"), "168TC1 TEMP CTRL")
        self.assertEqual(_gor_instr_desc("168TI2"), "168TI2 TEMP IND")
        self.assertEqual(_gor_instr_desc("168TV"), "168TV TEMP VLV")
        self.assertEqual(_gor_instr_desc("168FV1-416"), "168FV1-416 FLOW VLV")
        self.assertEqual(_gor_instr_desc("168GSO1"), "168GSO1 GAS SO")
        self.assertEqual(_gor_instr_desc("168GSC"), "168GSC GAS SC")
        self.assertEqual(_gor_instr_desc("168F-415"), "168F-415 FAN")
        self.assertEqual(_gor_instr_desc("168P-410"), "168P-410 PMP")

    def test_unknown_falls_back_to_inst(self) -> None:
        self.assertEqual(_gor_instr_desc("168ZZ9"), "168ZZ9 INST")


class GorHierarchyBuildTests(unittest.TestCase):
    def _inv(self, **extra):
        base = {
            "functions": [{"function": "WU12", "description": "WU12 VENTIL UNIT"}],
            "lines": [
                {
                    "source": "gor_pipe_id",
                    "line_number": "168L-522",
                    "pipe_class": "W38-VE10H2A",
                    "nominal_size": "65",
                }
            ],
            "valves": [],
            "instruments": extra.get("instruments", []),
        }
        base.update({k: v for k, v in extra.items() if k != "instruments"})
        if "instruments" in extra:
            base["instruments"] = extra["instruments"]
        return base

    def test_line_description_is_pipe_without_dn(self) -> None:
        rows = build_gor_hierarchy(self._inv())
        line = next(r for r in rows if r.get("EQUIPMENT") == "168L-522")
        self.assertEqual(line["DESCRIPTION"], "168L-522 PIPE")
        self.assertNotIn("65", line["DESCRIPTION"])

        out = build_equipment_rows(
            rows,
            ctx={"ecosystem": "gor", "plant": "6001", "line_code": "TM01",
                 "process_code": "WU", "sub_process": "WUC"},
        )
        eqktx = next(r["EQKTX"] for r in out if r["EQUNR"] == "168L-522")
        self.assertEqual(eqktx, "LN 168L-522 PIPE")
        self.assertNotIn("DN", eqktx)

    def test_fan_motors_nested_under_injected_parent(self) -> None:
        inv = self._inv(instruments=[
            {"tag": "168F-415-M1"},
            {"tag": "168F-415-M2"},
            {"tag": "168F-415-M3"},
            {"tag": "168F-415-M4"},
            {"tag": "168TI2"},
            {"tag": "168TV"},
            {"tag": "168GSO1"},
        ])
        rows = build_gor_hierarchy(inv)
        by_eq = [r["EQUIPMENT"] for r in rows if r.get("EQUIPMENT")]
        by_sub = [r["SUB-EQUIPMENT"] for r in rows if r.get("SUB-EQUIPMENT")]
        self.assertIn("168F-415", by_eq)
        self.assertNotIn("168F-415-M1", by_eq)
        self.assertEqual(by_sub.count("168F-415-M1"), 1)
        self.assertIn("168F-415-M4", by_sub)
        ti = next(r for r in rows if r.get("EQUIPMENT") == "168TI2")
        self.assertEqual(ti["DESCRIPTION"], "168TI2 TEMP IND")
        tv = next(r for r in rows if r.get("EQUIPMENT") == "168TV")
        self.assertEqual(tv["DESCRIPTION"], "168TV TEMP VLV")
        gso = next(r for r in rows if r.get("EQUIPMENT") == "168GSO1")
        self.assertEqual(gso["DESCRIPTION"], "168GSO1 GAS SO")

        out = build_equipment_rows(
            rows,
            ctx={"ecosystem": "gor", "plant": "6001", "line_code": "TM01",
                 "process_code": "WU", "sub_process": "WUC"},
        )
        by_tag = {r["EQUNR"]: r for r in out}
        self.assertEqual(by_tag["168F-415-M1"]["HEQUI"], "168F-415")
        self.assertEqual(by_tag["168TI2"]["EQART"], "1202")
        self.assertEqual(by_tag["168TV"]["EQART"], "202")
        self.assertEqual(by_tag["168GSO1"]["EQART"], "1210")
        self.assertNotEqual(by_tag["168TI2"]["EQART"], "9999")


if __name__ == "__main__":
    unittest.main()
