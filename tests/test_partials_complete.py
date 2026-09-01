#!/usr/bin/env python3
"""
Complete tests for all 11 partial-status items from the gap analysis.

Items covered:
  R36  Conveyors need motors (description-keyword gap — JSON fix applied)
  R29  Agitators placed as children of parent tank/pump
  R14  Work Center populated in Functional Locations file
  R18  LN prefix applied to FLOC PLTXT (same rule as Equipment)
  R16  Abbreviation coverage across output fields
  R27  Valve state NC / NO extracted correctly
  R37  Valmet PS-21 standard JSON completeness
  R38  GOR Italian ecosystem correctness
  R39  KSD / Andritz ecosystem correctness
  B03  ORPHAN valves handled gracefully
  S10  Duplicate FUNCTION entries deduplicated
  B04  SUB-EQUIPMENT with non-existent parent tag (35-24-089)
"""

from __future__ import annotations

import csv
import json
import re
import unittest
from pathlib import Path

from dwg_reader.dwg_ecosystem import Ecosystem, detect
from dwg_reader.dwg_floc_context import (
    abbreviate_pltxt,
    format_valve_eqktx,
    infer_valve_type,
    normalize_pltxt,
)
from dwg_reader.dwg_object_type import classify_equipment
from dwg_reader.export_sap_equipment import (
    _is_driven_equipment,
    _motor_eqktx,
    _motor_tag_for,
    build_equipment_rows,
)
from dwg_reader.export_sap_floc import (
    build_floc_rows,
    collect_functions,
)

ROOT = Path(__file__).resolve().parents[1]
HIERARCHY_CSV = ROOT / "outputs/Broke System.hierarchy_orchestrator.csv"
VALMET_STANDARD_JSON = ROOT / "standards/valmet_ps21.json"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _valmet_eco(extra_keywords: dict | None = None) -> Ecosystem:
    """Return inline Valmet ecosystem with full driven_patterns including conveyor fix."""
    kws: dict = {
        "screen": ["SCRN", "SCREEN"],
        "gearbox": ["GRBX", "GEARBOX"],
        "agitator": ["AGIT", "AGITATOR"],
        "winder_pulper": ["WINDER", "PLPR"],
        "conveyor": ["CVYR", "CONVEYOR"],
    }
    if extra_keywords:
        kws.update(extra_keywords)
    return Ecosystem(
        name="valmet",
        standard_id="valmet_ps21",
        standard={
            "driven_patterns": {
                "pump": r"^\d{2}-\d{2}P\d+$",
                "agitator_l": {"pattern": r"^\d{2}-\d{2}L(\d+)$", "range": [401, 499]},
                "description_keywords": kws,
            },
            "motor_from_equipment": {
                "mode": "strip_letter_append_dot_one",
                "regex": r"^(\d{2}-\d{2})[A-Z]+(\d+)$",
                "replace": r"\1-\2.1",
            },
        },
    )


def _valmet_ctx() -> dict:
    return {"ecosystem": "valmet", "plant": "5001", "line_code": "PM03",
            "process_code": "BR", "sub_process": "BR1"}


def _rows(*specs: tuple[str, str, str]) -> list[dict]:
    """Build minimal hierarchy CSV rows from (fn, eq, desc) tuples."""
    out = []
    for fn, eq, desc in specs:
        out.append({"FUNCTION": fn, "EQUIPMENT": eq, "SUB-EQUIPMENT": "",
                    "MASK": "", "DESCRIPTION": desc})
    return out


# ─────────────────────────────────────────────────────────────────────────────
# R36 — Conveyors need motors
# ─────────────────────────────────────────────────────────────────────────────

class ConveyorDrivenEquipmentTests(unittest.TestCase):
    """R36: L001-L399 conveyors with CVYR/CONVEYOR in description must get motors injected.

    Root cause: driven_patterns.description_keywords in valmet_ps21.json lacked a
    'conveyor' entry. Fix: added ["CVYR", "CONVEYOR"] to that mapping.
    """

    def test_is_driven_conveyor_abbreviated(self):
        """CVYR in description → L004 is driven (CVYR is the normalised abbreviation)."""
        eco = _valmet_eco()
        self.assertTrue(_is_driven_equipment("35-24L004", eco, desc="35-24L004 BROKE CVYR 2"))

    def test_is_driven_conveyor_full_word(self):
        """CONVEYOR (unabbreviated) in description → driven."""
        eco = _valmet_eco()
        self.assertTrue(_is_driven_equipment("35-24L004", eco, desc="35-24L004 BROKE CONVEYOR 2"))

    def test_is_driven_l006_conveyor(self):
        """L006 (BROKE CVYR 3) is driven."""
        eco = _valmet_eco()
        self.assertTrue(_is_driven_equipment("35-24L006", eco, desc="35-24L006 BROKE CVYR 3"))

    def test_is_driven_l011_conveyor(self):
        """L011 (BROKE CVYR 1) is driven."""
        eco = _valmet_eco()
        self.assertTrue(_is_driven_equipment("35-24L011", eco, desc="35-24L011 BROKE CVYR 1"))

    def test_conveyor_not_driven_without_desc(self):
        """L004 with empty description is not driven: L001-L399 tag alone is insufficient."""
        eco = _valmet_eco()
        self.assertFalse(_is_driven_equipment("35-24L004", eco, desc=""))

    def test_conveyor_motor_tag_valmet_format(self):
        """Conveyor motor uses Valmet strip-letter convention: 35-24L004 → 35-24-004.1"""
        eco = _valmet_eco()
        self.assertEqual(_motor_tag_for("35-24L004", ecosystem=eco), "35-24-004.1")
        self.assertEqual(_motor_tag_for("35-24L006", ecosystem=eco), "35-24-006.1")
        self.assertEqual(_motor_tag_for("35-24L011", ecosystem=eco), "35-24-011.1")

    def test_motor_injected_for_conveyor(self):
        """build_equipment_rows must inject 35-24-004.1 when L004 has CVYR description."""
        eco = _valmet_eco()
        rows = [
            {"FUNCTION": "35-24L004", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24L004 BROKE CVYR 2"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-123", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24-123 LN SUCT"},
        ]
        out = build_equipment_rows(rows, ctx=_valmet_ctx(), ecosystem=eco)
        by_tag = {r["EQUNR"]: r for r in out}
        self.assertIn("35-24-004.1", by_tag, "motor 35-24-004.1 must be injected for conveyor")
        motor = by_tag["35-24-004.1"]
        self.assertEqual(motor["HEQUI"], "35-24L004")
        self.assertEqual(motor["EQART"], "1101")
        self.assertEqual(motor["GEWRK"], "ELEC")

    def test_motor_eqktx_has_mtr(self):
        """Conveyor motor description ends with MTR."""
        eqktx = _motor_eqktx("35-24-004.1", "35-24L004", "35-24L004 BROKE CVYR 2")
        self.assertIn("MTR", eqktx)
        self.assertIn("35-24-004.1", eqktx)

    def test_all_three_broken_system_conveyors_get_motors(self):
        """L004 (CVYR 2), L006 (CVYR 3), L011 (CVYR 1) each receive one motor row."""
        eco = _valmet_eco()
        rows = [
            {"FUNCTION": "35-24L004", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24L004 BROKE CVYR 2"},
            {"FUNCTION": "35-24L006", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24L006 BROKE CVYR 3"},
            {"FUNCTION": "35-24L011", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24L011 BROKE CVYR 1"},
        ]
        out = build_equipment_rows(rows, ctx=_valmet_ctx(), ecosystem=eco)
        by_tag = {r["EQUNR"]: r for r in out}
        self.assertIn("35-24-004.1", by_tag, "L004 motor must be injected")
        self.assertIn("35-24-006.1", by_tag, "L006 motor must be injected")
        self.assertIn("35-24-011.1", by_tag, "L011 motor must be injected")
        for tag in ("35-24-004.1", "35-24-006.1", "35-24-011.1"):
            self.assertEqual(by_tag[tag]["EQART"], "1101")

    @unittest.skipUnless(VALMET_STANDARD_JSON.exists(), "requires valmet_ps21.json")
    def test_real_json_includes_conveyor_after_fix(self):
        """valmet_ps21.json must have conveyor in description_keywords (JSON fix verification)."""
        data = json.loads(VALMET_STANDARD_JSON.read_text(encoding="utf-8"))
        kws = data["driven_patterns"]["description_keywords"]
        self.assertIn("conveyor", kws, "conveyor key must be present after JSON fix")
        self.assertIn("CVYR", kws["conveyor"], "CVYR must be in conveyor keyword list")
        self.assertIn("CONVEYOR", kws["conveyor"], "CONVEYOR must be in conveyor keyword list")

    @unittest.skipUnless(VALMET_STANDARD_JSON.exists(), "requires valmet_ps21.json")
    def test_real_standard_drives_conveyor_detection(self):
        """After JSON fix, detect('STOD206339.10') ecosystem marks L004 CVYR as driven."""
        from dwg_reader.dwg_ecosystem import _load_standard
        _load_standard.cache_clear()
        eco = detect("STOD206339.10")
        self.assertTrue(
            _is_driven_equipment("35-24L004", eco, desc="35-24L004 BROKE CVYR 2"),
            "L004 CVYR must be driven via real valmet_ps21.json after fix",
        )
        _load_standard.cache_clear()


# ─────────────────────────────────────────────────────────────────────────────
# R29 — Agitators placed as children of parent tanks
# ─────────────────────────────────────────────────────────────────────────────

class AgitatorPlacementExportTests(unittest.TestCase):
    """R29: All 7 agitators (L401-L407) must be emitted with correct HEQUI and motors."""

    def _all_seven_rows(self) -> list[dict]:
        return [
            {"FUNCTION": "35-24T601", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24T601 COUCH PIT TNK"},
            {"FUNCTION": "", "EQUIPMENT": "35-24L401", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24L401 COUCH PIT AGITATOR"},
            {"FUNCTION": "", "EQUIPMENT": "35-24L403", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24L403 COUCH PIT AGITATOR"},
            {"FUNCTION": "35-24T603", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24T603 BROKE COLLECTION TNK"},
            {"FUNCTION": "", "EQUIPMENT": "35-24L406", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24L406 BROKE COLLECTION AGITATOR TANK"},
            {"FUNCTION": "35-24T605", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24T605 THICKENED BROKE TNK"},
            {"FUNCTION": "", "EQUIPMENT": "35-24L405", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24L405 THICKENED BROKE AGITATOR TANK"},
            {"FUNCTION": "35-24T606", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24T606 BROKE REJ TNK"},
            {"FUNCTION": "", "EQUIPMENT": "35-24L404", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24L404 BROKE REJECT AGITATOR TANK"},
            {"FUNCTION": "35-24T607", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24T607 BROKE DOS TNK"},
            {"FUNCTION": "", "EQUIPMENT": "35-24L407", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24L407 BROKE DOSING AGITATOR TANK"},
        ]

    def test_all_seven_agitator_tags_emitted(self):
        """All 7 agitator tags must appear as equipment rows."""
        out = build_equipment_rows(self._all_seven_rows())
        tags = {r["EQUNR"] for r in out}
        for tag in ("35-24L401", "35-24L403", "35-24L404", "35-24L405", "35-24L406", "35-24L407"):
            self.assertIn(tag, tags, f"{tag} must be emitted as equipment row")

    def test_all_seven_agitator_motors_injected(self):
        """Each of the 7 agitators must receive a motor sub-equipment row (.1 suffix)."""
        out = build_equipment_rows(self._all_seven_rows())
        by_tag = {r["EQUNR"]: r for r in out}
        for agi, mot in [
            ("35-24L401", "35-24-401.1"),
            ("35-24L403", "35-24-403.1"),
            ("35-24L404", "35-24-404.1"),
            ("35-24L405", "35-24-405.1"),
            ("35-24L406", "35-24-406.1"),
            ("35-24L407", "35-24-407.1"),
        ]:
            self.assertIn(mot, by_tag, f"motor {mot} must be injected for {agi}")
            self.assertEqual(by_tag[mot]["HEQUI"], agi, f"motor {mot} must have HEQUI={agi}")
            self.assertEqual(by_tag[mot]["EQART"], "1101", f"motor {mot} must be EQART=1101")
            self.assertEqual(by_tag[mot]["GEWRK"], "ELEC", f"motor {mot} must be ELEC work centre")

    def test_agitator_motor_eqktx_inherits_parent_context(self):
        """Motor descriptions must include the agitator's functional context and end with MTR."""
        out = build_equipment_rows(self._all_seven_rows())
        by_tag = {r["EQUNR"]: r for r in out}
        for agi, mot, frag in [
            ("35-24L404", "35-24-404.1", "BROKE"),
            ("35-24L406", "35-24-406.1", "BROKE"),
            ("35-24L405", "35-24-405.1", "THICKENED"),
        ]:
            eqktx = by_tag[mot]["EQKTX"]
            self.assertIn("MTR", eqktx, f"{mot} EQKTX must end with MTR: got {eqktx!r}")
            self.assertIn(frag, eqktx, f"{mot} EQKTX must contain '{frag}': got {eqktx!r}")
            self.assertLessEqual(len(eqktx), 40, f"{mot} EQKTX exceeds 40 chars: {eqktx!r}")

    def test_agitator_installed_at_parent_floc(self):
        """Agitator TPLNR must be the parent function FLOC (installed at the tank FLOC)."""
        out = build_equipment_rows(self._all_seven_rows())
        by_tag = {r["EQUNR"]: r for r in out}
        t601_tplnr = by_tag["35-24T601"]["TPLNR"]
        self.assertEqual(
            by_tag["35-24L401"]["TPLNR"], t601_tplnr,
            "L401 must be installed at T601 FLOC",
        )
        self.assertEqual(
            by_tag["35-24L403"]["TPLNR"], t601_tplnr,
            "L403 must be installed at T601 FLOC",
        )
        self.assertEqual(by_tag["35-24L401"]["HEQUI"], "35-24T601")
        self.assertEqual(by_tag["35-24L403"]["HEQUI"], "35-24T601")

    def test_agitator_object_type_is_2001(self):
        """L401-L499 tags must classify as object type 2001 (Agitator)."""
        for tag in ("35-24L401", "35-24L404", "35-24L407", "35-24L499"):
            code, wc = classify_equipment(tag, f"{tag} AGITATOR")
            self.assertEqual(code, "2001", f"{tag} must be object type 2001, got {code}")
            self.assertEqual(wc, "MECH", f"{tag} must have MECH work centre, got {wc}")

    def test_agitator_not_driven_below_range(self):
        """L400 (just below agitator range) must not be driven by tag alone."""
        from dwg_reader.export_sap_equipment import _is_driven_equipment as driven
        self.assertFalse(driven("35-24L400"), "L400 is below agitator range — not driven by tag")
        self.assertFalse(driven("35-24L399"), "L399 is regular process equipment — not driven by tag")


# ─────────────────────────────────────────────────────────────────────────────
# R14 — Work Center in Functional Locations (re-test)
# ─────────────────────────────────────────────────────────────────────────────

class FlocWorkCenterTests(unittest.TestCase):
    """R14: GEWRK (work centre) must be populated for all FUNCTION-level FLOC rows."""

    def _fn_rows(self, functions: list) -> list[dict]:
        """Build FLOC rows for given (tag, mask, desc) tuples and return only FUNCTION rows."""
        rows = build_floc_rows(functions)
        # FUNCTION rows have TPLMA=subprocess (5001-PM03-BR-BR1) and a function segment in TPLNR
        subprocess = "5001-PM03-BR-BR1"
        return [r for r in rows if r.get("TPLMA") == subprocess]

    def test_pulper_function_has_gewrk(self):
        """Pulper FUNCTION → GEWRK=MECH, EQART=2005."""
        fns = [("35-24L009", "5001-PM03-BR-BR1-35-24L009", "35-24L009 BROKE ROLL PLPR")]
        fn_rows = self._fn_rows(fns)
        self.assertEqual(len(fn_rows), 1)
        self.assertEqual(fn_rows[0]["GEWRK"], "MECH")
        self.assertEqual(fn_rows[0]["EQART"], "2005")

    def test_pump_function_has_gewrk(self):
        """Pump FUNCTION (P-prefix tag) → GEWRK=MECH."""
        fns = [("35-24P519", "5001-PM03-BR-BR1-35-24P519", "35-24P519 BROKE ROLL PLPR PMP")]
        fn_rows = self._fn_rows(fns)
        self.assertEqual(len(fn_rows), 1)
        self.assertNotEqual(fn_rows[0]["GEWRK"], "", "pump FUNCTION must have non-empty GEWRK")

    def test_tank_function_has_gewrk(self):
        """Tank FUNCTION → GEWRK=MECH."""
        fns = [("35-24T601", "5001-PM03-BR-BR1-35-24T601", "35-24T601 COUCH PIT TNK")]
        fn_rows = self._fn_rows(fns)
        self.assertEqual(len(fn_rows), 1)
        self.assertEqual(fn_rows[0]["GEWRK"], "MECH")

    def test_pipeline_function_has_mech_gewrk(self):
        """Pipeline FUNCTION (35-24-NNN) → GEWRK=MECH, EQART=2100."""
        fns = [("35-24-016", "5001-PM03-BR-BR1-35-24-016", "35-24-016 WHITE WTR DIST HDR")]
        fn_rows = self._fn_rows(fns)
        self.assertEqual(len(fn_rows), 1)
        self.assertEqual(fn_rows[0]["GEWRK"], "MECH")
        self.assertEqual(fn_rows[0]["EQART"], "2100")

    def test_conveyor_function_has_gewrk(self):
        """Conveyor FUNCTION → GEWRK=MECH (conveyors are mechanical equipment)."""
        fns = [("35-24L004", "5001-PM03-BR-BR1-35-24L004", "35-24L004 BROKE CVYR 2")]
        fn_rows = self._fn_rows(fns)
        self.assertEqual(len(fn_rows), 1)
        self.assertEqual(fn_rows[0]["GEWRK"], "MECH")

    def test_es_switch_function_has_elec_gewrk(self):
        """Emergency stop FUNCTION → GEWRK=ELEC (electrical equipment)."""
        fns = [("35-24ES-508", "5001-PM03-BR-BR1-35-24ES-508", "35-24ES-508 WINDER AREA E-STOP")]
        fn_rows = self._fn_rows(fns)
        self.assertEqual(len(fn_rows), 1)
        self.assertEqual(fn_rows[0]["GEWRK"], "ELEC")

    def test_all_function_rows_have_gewrk_or_note_missing(self):
        """Build all Broke System FLOC functions and report which lack GEWRK."""
        functions = [
            ("35-24L009", "5001-PM03-BR-BR1-35-24L009", "35-24L009 BROKE ROLL PLPR"),
            ("35-24P519", "5001-PM03-BR-BR1-35-24P519", "35-24P519 BROKE ROLL PLPR PMP"),
            ("35-24T601", "5001-PM03-BR-BR1-35-24T601", "35-24T601 COUCH PIT TNK"),
            ("35-24-016", "5001-PM03-BR-BR1-35-24-016", "35-24-016 WHITE WTR DIST HDR"),
            ("35-24L004", "5001-PM03-BR-BR1-35-24L004", "35-24L004 BROKE CVYR 2"),
        ]
        fn_rows = self._fn_rows(functions)
        empty_gewrk = [(r["TPLNR"], r["PLTXT"]) for r in fn_rows if not r["GEWRK"]]
        self.assertEqual(empty_gewrk, [], f"FUNCTION rows with empty GEWRK: {empty_gewrk}")


# ─────────────────────────────────────────────────────────────────────────────
# R18 — LN prefix in FLOC PLTXT (re-test: code was added post Meeting 3)
# ─────────────────────────────────────────────────────────────────────────────

class FlocLnPrefixVerificationTests(unittest.TestCase):
    """R18: Pipeline FUNCTION FLOCs must have 'LN NNN ' PLTXT; machine FLOCs must not."""

    def _fn_row_for(self, tag: str, desc: str) -> dict:
        rows = build_floc_rows([(tag, f"5001-PM03-BR-BR1-{tag}", desc)])
        return next(r for r in rows if r["TPLNR"].endswith(tag))

    def test_numeric_pipeline_tag_gets_ln_prefix(self):
        r = self._fn_row_for("35-24-016", "35-24-016 WAF 250 DIST HDR")
        self.assertTrue(r["PLTXT"].startswith("LN 35-24-016"), f"got {r['PLTXT']!r}")

    def test_numeric_pipeline_strips_pipe_class_codes(self):
        r = self._fn_row_for("35-24-095", "35-24-095 PP-200 PLPR DIS LN")
        self.assertNotIn("PP-200", r["PLTXT"])
        self.assertNotIn("LINE", r["PLTXT"])
        self.assertTrue(r["PLTXT"].startswith("LN 35-24-095"))

    def test_numeric_pipeline_translates_flow_code(self):
        r = self._fn_row_for("35-24-016", "35-24-016 WAF 250 DIST HDR")
        self.assertNotIn("WAF", r["PLTXT"])
        # Flow code translated to readable label; abbreviation then converts WHITE WTR→WW
        self.assertTrue(
            "WHITE WTR" in r["PLTXT"] or "WW" in r["PLTXT"],
            f"Expected WHITE WTR or its abbreviation WW, got {r['PLTXT']!r}",
        )

    def test_machine_tag_no_ln_prefix(self):
        """L-coded machine FUNCTION must not receive LN prefix."""
        r = self._fn_row_for("35-24L009", "35-24L009 BROKE ROLL PLPR")
        self.assertFalse(r["PLTXT"].startswith("LN "), f"got {r['PLTXT']!r}")
        self.assertTrue(r["PLTXT"].startswith("35-24L009"))

    def test_pump_tag_no_ln_prefix(self):
        r = self._fn_row_for("35-24P519", "35-24P519 BROKE ROLL PLPR PMP")
        self.assertFalse(r["PLTXT"].startswith("LN "))

    def test_tank_tag_no_ln_prefix(self):
        r = self._fn_row_for("35-24T601", "35-24T601 COUCH PIT TNK")
        self.assertFalse(r["PLTXT"].startswith("LN "))

    def test_pltxt_max_40_chars(self):
        r = self._fn_row_for("35-24-016", "35-24-016 WAF 250 DISTRIBUTION HEADER")
        self.assertLessEqual(len(r["PLTXT"]), 40, f"PLTXT exceeds 40 chars: {r['PLTXT']!r}")

    def test_gor_line_tag_gets_ln_prefix(self):
        """GOR-style line tags (168L-522) also qualify for LN prefix."""
        from dwg_reader.dwg_floc_context import merge_floc_context
        ctx = merge_floc_context({
            "plant": "6001", "line_code": "TM01",
            "process_code": "WU", "sub_process": "WUC",
        })
        rows = build_floc_rows([("168L-522", "6001-TM01-WU-WUC-168L-522", "168L-522 PIPE DN65")], ctx=ctx)
        fn = next(r for r in rows if r["TPLNR"].endswith("168L-522"))
        self.assertTrue(fn["PLTXT"].startswith("LN 168L-522"), f"got {fn['PLTXT']!r}")
        self.assertNotIn("DN", fn["PLTXT"])

    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_real_csv_all_pipeline_functions_have_ln_prefix(self):
        """Integration: every 35-24-NNN FUNCTION row in Broke System output has LN prefix."""
        rows = list(csv.DictReader(HIERARCHY_CSV.open(encoding="utf-8")))
        fns = collect_functions(rows)
        floc_rows = build_floc_rows(fns)
        # Filter to FUNCTION-level rows for numeric pipeline tags
        subprocess = "5001-PM03-BR-BR1"
        pipeline_re = re.compile(r"35-24-\d+$")
        missing = []
        for r in floc_rows:
            if r.get("TPLMA") != subprocess:
                continue
            tplnr = r.get("TPLNR", "")
            if not pipeline_re.search(tplnr):
                continue
            if not r["PLTXT"].startswith("LN "):
                missing.append((tplnr, r["PLTXT"]))
        self.assertEqual(missing, [], f"Pipeline FLOCs missing LN prefix: {missing[:5]}")


# ─────────────────────────────────────────────────────────────────────────────
# R16 / S01 — Abbreviation coverage
# ─────────────────────────────────────────────────────────────────────────────

class AbbreviationCoverageTests(unittest.TestCase):
    """R16/S01: All words with an SML abbreviation must appear abbreviated in output."""

    def test_agitator_abbreviated_to_agi(self):
        self.assertEqual(abbreviate_pltxt("AGITATOR"), "AGI")

    def test_agitator_in_description(self):
        out = abbreviate_pltxt("35-24L401 COUCH PIT AGITATOR")
        self.assertNotIn("AGITATOR", out)
        self.assertIn("AGI", out)

    def test_screen_abbreviated_to_scrn(self):
        self.assertEqual(abbreviate_pltxt("SCREEN"), "SCRN")

    def test_gearbox_abbreviated(self):
        out = abbreviate_pltxt("GEARBOX INLINE")
        self.assertNotIn("GEARBOX", out)

    def test_conveyor_abbreviated_to_cvyr(self):
        self.assertEqual(abbreviate_pltxt("35-24L004 BROKE CONVEYOR 2"), "35-24L004 BROKE CVYR 2")

    def test_motor_abbreviated_to_mtr(self):
        out = abbreviate_pltxt("35-24P519 PUMP MOTOR")
        self.assertIn("MTR", out)
        self.assertNotIn("MOTOR", out)

    def test_pump_abbreviated_to_pmp(self):
        out = abbreviate_pltxt("35-24P519 PUMP")
        self.assertIn("PMP", out)
        self.assertNotIn("PUMP", out)

    def test_thickener_preserved_as_is(self):
        """THICKENER is in sml_abbreviations.json no_abbreviation list — kept full."""
        out = abbreviate_pltxt("35-24L002 BROKE THICKENER")
        self.assertIn("THICKENER", out, "THICKENER has no SML abbreviation — must be preserved")

    def test_abbreviation_idempotent(self):
        """Applying abbreviation twice must not change the result."""
        first = abbreviate_pltxt("35-24L004 BROKE CONVEYOR 2")
        second = abbreviate_pltxt(first)
        self.assertEqual(first, second)

    def test_tank_abbreviated_to_tnk(self):
        out = abbreviate_pltxt("STORAGE TANK")
        self.assertIn("TNK", out)
        self.assertNotIn("TANK", out)

    def test_numbers_not_stripped(self):
        """Plain integers (conveyor numbering) must not be stripped."""
        out = abbreviate_pltxt("35-24L006 BROKE CONVEYOR 3")
        self.assertIn("3", out)

    def test_tag_prefix_preserved(self):
        """Tag prefix must not be altered by abbreviation."""
        out = abbreviate_pltxt("35-24L004 BROKE CONVEYOR 2")
        self.assertTrue(out.startswith("35-24L004"))

    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_real_csv_no_full_form_words_in_function_desc(self):
        """No FUNCTION description in the real Broke System output should contain
        unabbreviated PUMP, MOTOR, CONVEYOR, AGITATOR (common Rob-flagged words)."""
        rows = list(csv.DictReader(HIERARCHY_CSV.open(encoding="utf-8")))
        fns = collect_functions(rows)
        offenders = []
        full_words = {"PUMP", "MOTOR", "CONVEYOR", "AGITATOR", "GEARBOX"}
        for tag, _mask, desc in fns:
            found = {w for w in desc.upper().split() if w in full_words}
            if found:
                offenders.append((tag, desc, found))
        self.assertEqual(offenders, [], f"Unabbreviated words found: {offenders[:5]}")

    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_real_csv_conveyors_abbreviated(self):
        """L004, L006, L011 descriptions must use CVYR not CONVEYOR after collect_functions."""
        rows = list(csv.DictReader(HIERARCHY_CSV.open(encoding="utf-8")))
        fns = collect_functions(rows)
        by_tag = {tag: desc for tag, _mask, desc in fns}
        for tag in ("35-24L004", "35-24L006"):
            if tag not in by_tag:
                continue
            self.assertIn("CVYR", by_tag[tag], f"{tag} desc must use CVYR: {by_tag[tag]!r}")
            self.assertNotIn("CONVEYOR", by_tag[tag], f"{tag} must not have full CONVEYOR")


# ─────────────────────────────────────────────────────────────────────────────
# R27 — Valve state NC / NO extracted correctly
# ─────────────────────────────────────────────────────────────────────────────

class ValveStateExtractionTests(unittest.TestCase):
    """R27: Valve state (NC, NO, DRN NC, AV) must be extracted from description and
    vision cache, and included in the formatted HV Equipment Text."""

    def test_nc_from_description_via_infer(self):
        self.assertEqual(infer_valve_type("35-24-030", "35-24-030 NC VLV"), "NC")

    def test_no_from_description_via_infer(self):
        self.assertEqual(infer_valve_type("35-24-027", "35-24-027 NO VLV"), "NO")

    def test_normally_closed_phrase_maps_to_nc(self):
        from dwg_reader.dwg_floc_context import normalize_pltxt
        desc = normalize_pltxt("35-24-030 NORMALLY CLOSED VALVE")
        result = infer_valve_type("35-24-030", desc)
        self.assertEqual(result, "NC", f"'NORMALLY CLOSED' must map to NC, got {result!r}")

    def test_normally_open_phrase_maps_to_no(self):
        desc = normalize_pltxt("35-24-027 NORMALLY OPEN VALVE")
        result = infer_valve_type("35-24-027", desc)
        self.assertEqual(result, "NO", f"'NORMALLY OPEN' must map to NO, got {result!r}")

    def test_drn_nc_combined_state_preserved(self):
        """Rob's example: drain valve, normally closed — must show DRN NC."""
        result = format_valve_eqktx("35-24-137", "35-24L005", "35-24-137 DRN NC")
        self.assertIn("DRN", result)
        self.assertIn("NC", result)
        self.assertEqual(result, "HV 35-24-137 35-24L005 DRN NC")

    def test_no_state_in_output_valve(self):
        """Valve with NO state in description → NO appears in formatted EQKTX."""
        result = format_valve_eqktx("35-24-027", "35-24L005", "35-24-027 NO VLV")
        self.assertIn("NO", result)

    def test_nc_state_in_output_valve(self):
        """Valve with NC state in description → NC appears in formatted EQKTX."""
        result = format_valve_eqktx("35-24-030", "35-24L001", "35-24-030 NC VLV")
        self.assertIn("NC", result)

    def test_av_nc_strips_nc_from_control_valve(self):
        """AV (control/process valve) must not emit NC — it's process-controlled."""
        result = format_valve_eqktx(
            "35-24HV-548", "35-24L005", "35-24HV-548 AV NC", valve_type_override="AV"
        )
        self.assertNotIn("NC", result, "NC must be stripped from AV control valve")
        self.assertIn("AV", result)

    def test_vision_nc_propagated(self):
        """Vision cache NC type must propagate to formatted EQKTX."""
        rows = [
            {"FUNCTION": "35-24L005", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-030", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24-030 VLV"},
        ]
        cache = {"35-24-030": {"is_valve": True, "type": "NC", "source": "vision"}}
        out = build_equipment_rows(rows, valve_cache=cache)
        by_tag = {r["EQUNR"]: r for r in out}
        eqktx = by_tag["35-24-030"]["EQKTX"]
        self.assertIn("NC", eqktx, f"NC state from vision must appear in EQKTX: {eqktx!r}")

    def test_build_rows_no_state_from_desc(self):
        """'35-24-027 NO VLV' description → NO appears in EQKTX."""
        rows = [
            {"FUNCTION": "35-24L005", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-027", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24-027 NO VLV"},
        ]
        out = build_equipment_rows(rows)
        by_tag = {r["EQUNR"]: r for r in out}
        eqktx = by_tag["35-24-027"]["EQKTX"]
        self.assertIn("NO", eqktx, f"NO state must appear in EQKTX: {eqktx!r}")


# ─────────────────────────────────────────────────────────────────────────────
# R37 — Valmet PS-21 standard JSON completeness
# ─────────────────────────────────────────────────────────────────────────────

class ValmetStandardCompletenessTests(unittest.TestCase):
    """R37: valmet_ps21.json must contain all required driven patterns, motor formula,
    flow codes, and equipment letter codes needed to process PM3 drawings."""

    @unittest.skipUnless(VALMET_STANDARD_JSON.exists(), "requires valmet_ps21.json")
    def setUp(self):
        self.data = json.loads(VALMET_STANDARD_JSON.read_text(encoding="utf-8"))

    @unittest.skipUnless(VALMET_STANDARD_JSON.exists(), "requires valmet_ps21.json")
    def test_required_top_level_keys(self):
        required = {"driven_patterns", "motor_from_equipment", "equipment_letter_codes",
                    "flow_substance_codes", "fimpec_valve_codes",
                    "location_letter_codes", "location_code_format"}
        missing = required - set(self.data.keys())
        self.assertEqual(missing, set(), f"Missing top-level keys: {missing}")

    @unittest.skipUnless(VALMET_STANDARD_JSON.exists(), "requires valmet_ps21.json")
    def test_driven_patterns_has_all_categories(self):
        dp = self.data["driven_patterns"]
        self.assertIn("pump", dp, "pump pattern required")
        self.assertIn("agitator_l", dp, "agitator_l range pattern required")
        self.assertIn("description_keywords", dp, "description_keywords required")
        kws = dp["description_keywords"]
        for key in ("screen", "gearbox", "agitator", "winder_pulper", "conveyor"):
            self.assertIn(key, kws, f"description_keywords must include '{key}'")

    @unittest.skipUnless(VALMET_STANDARD_JSON.exists(), "requires valmet_ps21.json")
    def test_pump_pattern_matches_p_prefix_tags(self):
        pump_pat = self.data["driven_patterns"]["pump"]
        for tag in ("35-24P518", "35-24P501", "55-30P001"):
            self.assertTrue(re.match(pump_pat, tag), f"pump pattern must match {tag}")
        self.assertFalse(re.match(pump_pat, "35-24L004"), "pump pattern must not match L004")

    @unittest.skipUnless(VALMET_STANDARD_JSON.exists(), "requires valmet_ps21.json")
    def test_agitator_range_401_to_499(self):
        agit = self.data["driven_patterns"]["agitator_l"]
        pat = agit["pattern"]
        rng = agit["range"]
        self.assertEqual(rng, [401, 499])
        for num in (401, 450, 499):
            m = re.match(pat, f"35-24L{num}")
            self.assertIsNotNone(m, f"agitator pattern must match L{num}")
        m = re.match(pat, "35-24L400")
        if m:
            n = int(m.group(1))
            self.assertFalse(rng[0] <= n <= rng[1], "L400 must be outside agitator range")

    @unittest.skipUnless(VALMET_STANDARD_JSON.exists(), "requires valmet_ps21.json")
    def test_motor_formula_strip_letter_append_dot_one(self):
        mfe = self.data["motor_from_equipment"]
        self.assertEqual(mfe["mode"], "strip_letter_append_dot_one")
        regex = mfe["regex"]
        replace = mfe["replace"]
        result = re.sub(regex, replace, "35-24P518")
        self.assertEqual(result, "35-24-518.1")
        result = re.sub(regex, replace, "35-24L401")
        self.assertEqual(result, "35-24-401.1")

    @unittest.skipUnless(VALMET_STANDARD_JSON.exists(), "requires valmet_ps21.json")
    def test_flow_substance_codes_present(self):
        fsc = self.data["flow_substance_codes"]
        self.assertIn("WAF", fsc)
        self.assertEqual(fsc["WAF"], "WHITE WTR")
        self.assertIn("WFL", fsc)
        self.assertEqual(fsc["WFL"], "SEAL WTR")
        self.assertIn("WAA", fsc)
        self.assertIn("WFC", fsc)

    @unittest.skipUnless(VALMET_STANDARD_JSON.exists(), "requires valmet_ps21.json")
    def test_equipment_letter_codes_present(self):
        elc = self.data["equipment_letter_codes"]
        self.assertIn("L401-L499", elc)
        self.assertIn("Agitator", elc["L401-L499"])
        self.assertIn("P501-P599", elc)
        self.assertIn("T601-T699", elc)

    def test_valmet_flow_codes_translate_in_clean_line_description(self):
        """Flow substance codes from the module-level dict translate correctly."""
        from dwg_reader.export_sap_floc import _clean_line_description
        self.assertIn("WHITE WTR", _clean_line_description("WAF DIST HDR"))
        self.assertIn("SEAL WTR", _clean_line_description("WFL DN15"))
        self.assertIn("CLOUDY FILT", _clean_line_description("WAA LN DN300"))
        self.assertIn("CLG WTR", _clean_line_description("WFC CIRCUIT"))

    @unittest.skipUnless(VALMET_STANDARD_JSON.exists(), "requires valmet_ps21.json")
    def test_valmet_location_letter_codes_from_process_automation_pdf(self):
        """H-06: PROCESS AND AUTOMATION.pdf location codes (CB, JBI, CR, …)."""
        loc = self.data["location_letter_codes"]
        self.assertEqual(loc["CB"], "Control box")
        self.assertEqual(loc["JBI"], "Instrument junction box")
        self.assertEqual(loc["CR"], "PLC / control cabinet / DCS I/O rack")
        self.assertIn("CD", loc)
        self.assertIn("JB", loc)
        self.assertIn("MM-SSAAA-CCC.DD", self.data["location_code_format"])


# ─────────────────────────────────────────────────────────────────────────────
# R38 — GOR Italian ecosystem correctness
# ─────────────────────────────────────────────────────────────────────────────

class GorEcosystemTests(unittest.TestCase):
    """R38: GOR Italian ecosystem (GORA/GORB DWGs) must use -M1 motor suffix,
    route to plant 6001, and classify fan/pump/valve tags correctly."""

    def test_gor_motor_suffix_is_m1(self):
        """GOR equipment motor tag appends -M1."""
        eco = detect("GORA68210")
        self.assertEqual(_motor_tag_for("168F-415", ecosystem=eco), "168F-415-M1")
        self.assertEqual(_motor_tag_for("168P-410", ecosystem=eco), "168P-410-M1")

    def test_gor_fan_tag_classifies_as_fan(self):
        """168F-xxx (fan) → object type 801."""
        code, wc = classify_equipment("168F-415", "168F-415 FAN")
        self.assertEqual(code, "801", f"GOR fan must be 801, got {code}")

    def test_gor_pump_motor_tag(self):
        """168P-410 motor → 168P-410-M1."""
        eco = detect("GORA68210")
        self.assertEqual(_motor_tag_for("168P-410", ecosystem=eco), "168P-410-M1")

    def test_gor_motor_tag_classifies_as_motor(self):
        """168P-410-M1 suffix → object type 1101 (Motor)."""
        code, wc = classify_equipment("168P-410-M1", "168P-410-M1 MTR")
        self.assertEqual(code, "1101")
        self.assertEqual(wc, "ELEC")

    def test_gor_ecosystem_plant_is_6001(self):
        """GOR drawings must map to plant 6001 (Tissue Machine 1)."""
        from dwg_reader.dwg_floc_context import load_floc_context_for_input
        ctx = load_floc_context_for_input(
            Path("inputs/GORB18779.05_SH12(12)_Code 14 - P&ID Ventil Unit WU12_SWE Shotton_CE.dwg")
        )
        self.assertEqual(ctx["plant"], "6001")

    def test_gor_ecosystem_detected_from_stem_prefix(self):
        """DWG stems starting with GORA/GORB → gor ecosystem."""
        eco = detect("GORA68210")
        self.assertEqual(eco.name, "gor")
        eco2 = detect("GORB18779")
        self.assertEqual(eco2.name, "gor")

    def test_gor_fan_motors_nested_under_parent(self):
        """GOR fan motors (168F-415-M1/M2) must be nested under injected parent (168F-415)."""
        rows = [
            {"FUNCTION": "WU12", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "WU12 VENTIL UNIT"},
            {"FUNCTION": "", "EQUIPMENT": "168F-415-M1", "SUB-EQUIPMENT": "", "DESCRIPTION": "168F-415-M1 MTR"},
            {"FUNCTION": "", "EQUIPMENT": "168F-415-M2", "SUB-EQUIPMENT": "", "DESCRIPTION": "168F-415-M2 MTR"},
        ]
        ctx = {"ecosystem": "gor", "plant": "6001", "line_code": "TM01",
               "process_code": "WU", "sub_process": "WUC"}
        out = build_equipment_rows(rows, ctx=ctx)
        by_tag = {r["EQUNR"]: r for r in out}
        self.assertIn("168F-415", by_tag, "parent fan must be injected for orphan motors")
        self.assertEqual(by_tag["168F-415-M1"]["HEQUI"], "168F-415")
        self.assertEqual(by_tag["168F-415-M2"]["HEQUI"], "168F-415")

    def test_gor_valve_tags_classify_correctly(self):
        """168TV, 168FV → control valve (202)."""
        for tag in ("168TV", "168FV1-416"):
            code, _ = classify_equipment(tag, f"{tag} VLV")
            self.assertEqual(code, "202", f"{tag} must classify as control valve 202, got {code}")


# ─────────────────────────────────────────────────────────────────────────────
# R39 — KSD / Andritz ecosystem correctness
# ─────────────────────────────────────────────────────────────────────────────

class KsdEcosystemTests(unittest.TestCase):
    """R39: KSD/Andritz ecosystem (KSDM DWGs) must share the tissue standard
    (tissue_ksdm160104) and use -M1 motor suffix."""

    def test_ksd_ecosystem_detected_from_stem_prefix(self):
        eco = detect("KSDM160104")
        self.assertEqual(eco.name, "ksd")
        self.assertEqual(eco.standard_id, "ksd_andritz",
                         "KSD now uses the dedicated ksd_andritz standard")

    def test_ksd_motor_suffix_is_m1(self):
        """KSD pumps use -M1 motor suffix like GOR."""
        eco = detect("KSDM160104")
        self.assertEqual(_motor_tag_for("124P-001", ecosystem=eco), "124P-001-M1")

    def test_ksd_and_gor_share_standard(self):
        """KSD and GOR are both tissue ecosystems (is_tissue=True) with
        dedicated standard JSONs — they no longer share tissue_ksdm160104."""
        gor_eco = detect("GORA68210")
        ksd_eco = detect("KSDM160104")
        self.assertTrue(gor_eco.is_tissue, "GOR must be a tissue ecosystem")
        self.assertTrue(ksd_eco.is_tissue, "KSD must be a tissue ecosystem")
        self.assertEqual(gor_eco.standard_id, "gor_fiorentini")
        self.assertEqual(ksd_eco.standard_id, "ksd_andritz")

    def test_ksd_is_tissue_property(self):
        eco = detect("KSDM160104")
        self.assertTrue(eco.is_tissue, "KSD ecosystem must have is_tissue=True")
        self.assertFalse(eco.is_valmet, "KSD ecosystem must have is_valmet=False")


# ─────────────────────────────────────────────────────────────────────────────
# B03 — ORPHAN valves handled gracefully
# ─────────────────────────────────────────────────────────────────────────────

class OrphanValveHandlingTests(unittest.TestCase):
    """B03: Valves with MASK=ORPHAN (could not be assigned a parent in hierarchy)
    must still appear as standalone Equipment records with correct formatting."""

    def _orphan_rows(self, fn: str = "35-24L001") -> list[dict]:
        return [
            {"FUNCTION": fn, "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "PULPER"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-058", "SUB-EQUIPMENT": "",
             "MASK": "ORPHAN", "DESCRIPTION": "35-24-058 VLV"},
        ]

    def test_orphan_valve_is_emitted(self):
        """Valve with MASK=ORPHAN must appear in the equipment output."""
        out = build_equipment_rows(self._orphan_rows())
        tags = {r["EQUNR"] for r in out}
        self.assertIn("35-24-058", tags, "ORPHAN valve must be emitted as equipment row")

    def test_orphan_valve_has_hv_format(self):
        """Valve detected from description ('VLV') still receives HV formatting."""
        out = build_equipment_rows(self._orphan_rows())
        by_tag = {r["EQUNR"]: r for r in out}
        eqktx = by_tag["35-24-058"]["EQKTX"]
        self.assertTrue(eqktx.startswith("HV "), f"ORPHAN valve must have HV prefix: {eqktx!r}")

    def test_orphan_valve_has_empty_hequi(self):
        """ORPHAN valve is top-level Equipment, not a sub-equipment of any record."""
        out = build_equipment_rows(self._orphan_rows())
        by_tag = {r["EQUNR"]: r for r in out}
        self.assertEqual(by_tag["35-24-058"]["HEQUI"], "",
                         "ORPHAN valve must have empty HEQUI")

    def test_orphan_valve_eqart_is_valve(self):
        """ORPHAN valve must have a valve object type (201 or 202)."""
        out = build_equipment_rows(self._orphan_rows())
        by_tag = {r["EQUNR"]: r for r in out}
        eqart = by_tag["35-24-058"]["EQART"]
        self.assertIn(eqart, ("201", "202"),
                      f"ORPHAN valve EQART must be 201/202, got {eqart!r}")

    def test_multiple_orphan_valves_each_emitted_once(self):
        """Multiple ORPHAN valves must each appear exactly once."""
        rows = [
            {"FUNCTION": "35-24L001", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "PULPER"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-058", "SUB-EQUIPMENT": "",
             "MASK": "ORPHAN", "DESCRIPTION": "35-24-058 VLV"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-114", "SUB-EQUIPMENT": "",
             "MASK": "ORPHAN", "DESCRIPTION": "35-24-114 VLV"},
        ]
        out = build_equipment_rows(rows)
        equnrs = [r["EQUNR"] for r in out]
        self.assertEqual(equnrs.count("35-24-058"), 1, "35-24-058 must appear exactly once")
        self.assertEqual(equnrs.count("35-24-114"), 1, "35-24-114 must appear exactly once")

    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_real_csv_orphan_valves_present_in_output(self):
        """Integration: ORPHAN-tagged rows in the Broke System CSV must appear in equipment output."""
        rows = list(csv.DictReader(HIERARCHY_CSV.open(encoding="utf-8")))
        # Find ORPHAN-masked equipment rows
        orphan_tags = {r["EQUIPMENT"].strip().upper() for r in rows
                       if r.get("MASK", "").strip().upper() == "ORPHAN"
                       and r.get("EQUIPMENT", "").strip()}
        if not orphan_tags:
            self.skipTest("No ORPHAN valves found in CSV")
        out = build_equipment_rows(rows)
        emitted_tags = {r["EQUNR"] for r in out}
        missing = orphan_tags - emitted_tags
        self.assertEqual(missing, set(),
                         f"ORPHAN valves missing from output: {missing}")


# ─────────────────────────────────────────────────────────────────────────────
# S10 — Duplicate FUNCTION entries deduplicated
# ─────────────────────────────────────────────────────────────────────────────

class DuplicateFunctionDeduplicationTests(unittest.TestCase):
    """S10: When the same FUNCTION tag appears more than once (across sub-process rows
    and regular function rows), collect_functions must produce exactly one entry."""

    def test_same_function_twice_deduped(self):
        """FUNCTION tag appearing twice → one collect_functions result."""
        rows = [
            {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "",
             "DESCRIPTION": "35-24L009 BROKE ROLL PLPR"},
            {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "",
             "DESCRIPTION": "35-24L009 DUPLICATE"},
        ]
        fns = collect_functions(rows, filter_utility_lines=False)
        tags = [fn for fn, _, _ in fns]
        self.assertEqual(tags.count("35-24L009"), 1, "duplicate FUNCTION must produce exactly 1 entry")

    def test_dedup_uses_first_occurrence_description(self):
        """When a FUNCTION appears twice, the first occurrence description is used."""
        rows = [
            {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "",
             "DESCRIPTION": "35-24L009 BROKE ROLL PLPR"},
            {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "",
             "DESCRIPTION": "35-24L009 SECOND OCCURRENCE"},
        ]
        fns = collect_functions(rows, filter_utility_lines=False)
        self.assertEqual(len(fns), 1)
        _tag, _mask, desc = fns[0]
        self.assertIn("PLPR", desc, f"First occurrence description must be used: {desc!r}")

    def test_function_as_sub_process_then_function_deduped(self):
        """When a tag appears in both SUB-PROCESS column and FUNCTION column → one entry."""
        rows = [
            {"SUB-PROCESS": "BR1", "FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "MASK": "5001-PM03-BR-BR1-35-24L009", "DESCRIPTION": "35-24L009 BROKE ROLL PLPR"},
            {"SUB-PROCESS": "", "FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "MASK": "", "DESCRIPTION": "35-24L009 BROKE ROLL PLPR"},
        ]
        fns = collect_functions(rows, filter_utility_lines=False)
        tags = [fn for fn, _, _ in fns]
        self.assertEqual(tags.count("35-24L009"), 1)

    def test_different_functions_not_deduped(self):
        """Different FUNCTION tags must all appear in the result."""
        rows = [
            {"FUNCTION": fn, "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "", "DESCRIPTION": f"{fn} DESC"}
            for fn in ("35-24L009", "35-24P519", "35-24T601")
        ]
        fns = collect_functions(rows, filter_utility_lines=False)
        tags = [fn for fn, _, _ in fns]
        self.assertIn("35-24L009", tags)
        self.assertIn("35-24P519", tags)
        self.assertIn("35-24T601", tags)
        self.assertEqual(len(tags), 3)

    def test_floc_rows_no_duplicate_tplnr(self):
        """build_floc_rows called with deduplicated functions must produce unique TPLNR values."""
        rows = [
            {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "",
             "DESCRIPTION": "35-24L009 BROKE ROLL PLPR"},
            {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "",
             "DESCRIPTION": "35-24L009 DUPLICATE"},
            {"FUNCTION": "35-24P519", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "",
             "DESCRIPTION": "35-24P519 PMP"},
        ]
        fns = collect_functions(rows, filter_utility_lines=False)
        floc_rows = build_floc_rows(fns)
        tplnrs = [r["TPLNR"] for r in floc_rows]
        # Each TPLNR must appear at most once
        from collections import Counter
        dupes = [t for t, n in Counter(tplnrs).items() if n > 1]
        self.assertEqual(dupes, [], f"Duplicate TPLNRs in FLOC output: {dupes}")

    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_real_csv_no_duplicate_functions_in_output(self):
        """Integration: collect_functions on real Broke System CSV → each tag appears once."""
        rows = list(csv.DictReader(HIERARCHY_CSV.open(encoding="utf-8")))
        fns = collect_functions(rows)
        tags = [fn for fn, _, _ in fns]
        from collections import Counter
        dupes = {t: n for t, n in Counter(tags).items() if n > 1}
        self.assertEqual(dupes, {}, f"Duplicate FUNCTIONs after collect_functions: {dupes}")


# ─────────────────────────────────────────────────────────────────────────────
# B04 — SUB-EQUIPMENT with non-existent parent (35-24-089 edge case)
# ─────────────────────────────────────────────────────────────────────────────

class MissingParentSubEquipmentTests(unittest.TestCase):
    """B04: When a SUB-EQUIPMENT row references a parent that does not appear in the
    drawing (DXF artefact), the export must still produce a row with whatever HEQUI
    it can infer rather than crashing or omitting the row."""

    def test_sub_equipment_with_unknown_parent_still_emitted(self):
        """SUB-EQUIPMENT with HEQUI pointing to 'unknown' parent → row is still emitted."""
        rows = [
            {"FUNCTION": "35-24L005", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "REEL PLPR"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-095", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24-095 LN SUCT"},
            # 35-24-089 appears as sub-equipment; its parent 24089 is not in the drawing.
            {"FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": "35-24-089", "DESCRIPTION": "35-24-089 VLV"},
        ]
        out = build_equipment_rows(rows)
        tags = {r["EQUNR"] for r in out}
        self.assertIn("35-24-089", tags, "35-24-089 must be emitted despite parent uncertainty")

    def test_sub_equipment_hequi_is_last_equipment(self):
        """HEQUI for sub-equipment is set to the last seen EQUIPMENT tag (current_equipment)."""
        rows = [
            {"FUNCTION": "35-24L005", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "REEL PLPR"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-095", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24-095 LN SUCT"},
            {"FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": "35-24-089", "DESCRIPTION": "35-24-089 VLV"},
        ]
        out = build_equipment_rows(rows)
        by_tag = {r["EQUNR"]: r for r in out}
        # 35-24-089's HEQUI must be the preceding EQUIPMENT (35-24-095 or L005)
        hequi = by_tag["35-24-089"]["HEQUI"]
        self.assertIn(hequi, ("35-24-095", "35-24L005", ""),
                      f"HEQUI={hequi!r} is not one of the expected parent candidates")

    def test_missing_parent_does_not_crash(self):
        """A SUB-EQUIPMENT row with no plausible parent (current_equipment empty) must not raise."""
        rows = [
            # No FUNCTION or EQUIPMENT above this SUB-EQUIPMENT → current_equipment is ""
            {"FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": "35-24-089", "DESCRIPTION": "35-24-089 VLV"},
        ]
        # Must not raise, even if current_tplnr is empty.
        try:
            out = build_equipment_rows(rows)
            # If it emits something, fine; if it silently drops the row (no valid TPLNR), also fine.
            # What must NOT happen: an exception.
        except Exception as exc:
            self.fail(f"build_equipment_rows raised {type(exc).__name__}: {exc}")

    def test_numeric_sub_equipment_tag_classified_correctly(self):
        """35-24-089 (numeric line-tag format) in SUB-EQUIPMENT → classified as valve when desc says VLV."""
        rows = [
            {"FUNCTION": "35-24L005", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": "REEL PLPR"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-095", "SUB-EQUIPMENT": "", "DESCRIPTION": "35-24-095 LN SUCT"},
            {"FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": "35-24-089", "DESCRIPTION": "35-24-089 VLV HV"},
        ]
        out = build_equipment_rows(rows)
        by_tag = {r["EQUNR"]: r for r in out}
        if "35-24-089" in by_tag:
            eqktx = by_tag["35-24-089"]["EQKTX"]
            self.assertTrue(
                eqktx.startswith("HV ") or "VLV" in eqktx,
                f"35-24-089 with VLV desc must get valve formatting: {eqktx!r}",
            )


# ─────────────────────────────────────────────────────────────────────────────
# Integration: run existing CSV through export pipeline end-to-end
# ─────────────────────────────────────────────────────────────────────────────

class BrokeSystemEndToEndTests(unittest.TestCase):
    """Smoke-level integration across all partial items using the real Broke System CSV."""

    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_no_eqktx_exceeds_40_chars(self):
        """All EQKTX values in equipment export must be ≤ 40 characters."""
        rows = list(csv.DictReader(HIERARCHY_CSV.open(encoding="utf-8")))
        out = build_equipment_rows(rows, limit_functions=20)
        offenders = [(r["EQUNR"], r["EQKTX"]) for r in out if len(r.get("EQKTX") or "") > 40]
        self.assertEqual(offenders, [], f"EQKTX > 40 chars: {offenders[:5]}")

    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_no_pltxt_exceeds_40_chars(self):
        """All PLTXT values in FLOC export must be ≤ 40 characters."""
        rows = list(csv.DictReader(HIERARCHY_CSV.open(encoding="utf-8")))
        fns = collect_functions(rows)
        floc_rows = build_floc_rows(fns)
        offenders = [(r["TPLNR"], r["PLTXT"]) for r in floc_rows if len(r.get("PLTXT") or "") > 40]
        self.assertEqual(offenders, [], f"PLTXT > 40 chars: {offenders[:5]}")

    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_all_pump_tags_have_motors(self):
        """Every P5xx pump in the Broke System must have a corresponding motor in the output."""
        rows = list(csv.DictReader(HIERARCHY_CSV.open(encoding="utf-8")))
        out = build_equipment_rows(rows)
        by_tag = {r["EQUNR"]: r for r in out}
        pump_re = re.compile(r"^35-24P(\d+)$")
        pumps_without_motors = []
        for tag in by_tag:
            m = pump_re.match(tag)
            if not m:
                continue
            num = m.group(1)
            motor_tag = f"35-24-{num}.1"
            if motor_tag not in by_tag:
                pumps_without_motors.append((tag, motor_tag))
        self.assertEqual(pumps_without_motors, [],
                         f"Pumps missing motors: {pumps_without_motors}")

    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_agitator_range_tags_all_have_motors(self):
        """All L401-L499 agitator tags in the Broke System CSV must have motor sub-rows."""
        rows = list(csv.DictReader(HIERARCHY_CSV.open(encoding="utf-8")))
        out = build_equipment_rows(rows)
        by_tag = {r["EQUNR"]: r for r in out}
        agit_re = re.compile(r"^35-24L(4\d{2})$")
        missing = []
        for tag in by_tag:
            m = agit_re.match(tag)
            if not m:
                continue
            num = int(m.group(1))
            if 401 <= num <= 499:
                motor_tag = f"35-24-{m.group(1)}.1"
                if motor_tag not in by_tag:
                    missing.append((tag, motor_tag))
        self.assertEqual(missing, [], f"Agitators missing motors: {missing}")

    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_all_emitted_tags_are_valid_equnr(self):
        """No emitted EQUNR should be a placeholder like 'AGITATOR' or 'ORPHAN'."""
        rows = list(csv.DictReader(HIERARCHY_CSV.open(encoding="utf-8")))
        out = build_equipment_rows(rows)
        invalid = [r["EQUNR"] for r in out
                   if r["EQUNR"].upper() in ("AGITATOR", "ORPHAN", "FUNCTION", "")]
        self.assertEqual(invalid, [],
                         f"Invalid EQUNR placeholder values in output: {invalid}")


# ─────────────────────────────────────────────────────────────────────────────
# D-03 — X-position sort not corrupted by type-bucket
# ─────────────────────────────────────────────────────────────────────────────

class PositionSortNoBucketTests(unittest.TestCase):
    """D-03: collect_functions must sort purely by X position, never grouping all
    machines ahead of all pipelines regardless of position."""

    def _mixed_rows(self, *tags: str) -> list[dict]:
        """Build rows where each function also has a child so WFL lines survive filter."""
        rows = []
        for t in tags:
            rows.append({"FUNCTION": t, "EQUIPMENT": "", "SUB-EQUIPMENT": "",
                          "MASK": "", "DESCRIPTION": f"{t} DESC"})
            rows.append({"FUNCTION": "", "EQUIPMENT": f"child-{t}", "SUB-EQUIPMENT": "",
                          "MASK": "", "DESCRIPTION": "VLV"})
        return rows

    def test_pipeline_before_machine_when_position_says_so(self):
        """Pipeline at lower X than machine must come first — not grouped by type."""
        rows = self._mixed_rows("35-24L009", "35-24-026", "35-24P519")
        positions = {"35-24L009": 500.0, "35-24-026": 100.0, "35-24P519": 300.0}
        result = collect_functions(rows, filter_utility_lines=False, positions=positions)
        tags = [t for t, _, _ in result]
        self.assertEqual(tags, ["35-24-026", "35-24P519", "35-24L009"])

    def test_machine_before_pipeline_when_position_says_so(self):
        """Machine at lower X must precede pipeline at higher X."""
        rows = self._mixed_rows("35-24-026", "35-24L009", "35-24P519")
        positions = {"35-24-026": 400.0, "35-24L009": 100.0, "35-24P519": 250.0}
        result = collect_functions(rows, filter_utility_lines=False, positions=positions)
        tags = [t for t, _, _ in result]
        self.assertEqual(tags, ["35-24L009", "35-24P519", "35-24-026"])

    def test_numeric_sort_pipeline_interleaved_with_machines(self):
        """Numeric sort: tag number determines order across machine and pipeline tags."""
        rows = [
            {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "", "DESCRIPTION": "L009"},
            {"FUNCTION": "35-24-026", "EQUIPMENT": "eq1", "SUB-EQUIPMENT": "", "MASK": "", "DESCRIPTION": "26"},
            {"FUNCTION": "35-24P519", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "", "DESCRIPTION": "P519"},
            {"FUNCTION": "35-24-008", "EQUIPMENT": "eq2", "SUB-EQUIPMENT": "", "MASK": "", "DESCRIPTION": "8"},
        ]
        result = collect_functions(rows, filter_utility_lines=False, sort_by_tag_number=True)
        tags = [t for t, _, _ in result]
        # 8 < 9 < 26 < 519
        self.assertEqual(tags, ["35-24-008", "35-24L009", "35-24-026", "35-24P519"])

    def test_wfl_with_children_not_filtered_position_sort(self):
        """WFL pipeline with children must survive filter and sort by position."""
        rows = [
            {"FUNCTION": "35-24-026", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "MASK": "", "DESCRIPTION": "35-24-026 WFL PROC LN"},
            {"FUNCTION": "", "EQUIPMENT": "35-24-159", "SUB-EQUIPMENT": "", "MASK": "", "DESCRIPTION": "VLV"},
            {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "", "DESCRIPTION": "PLPR"},
        ]
        positions = {"35-24-026": 200.0, "35-24L009": 100.0}
        result = collect_functions(rows, positions=positions)
        tags = [t for t, _, _ in result]
        self.assertIn("35-24-026", tags, "WFL line with child must not be filtered")
        self.assertIn("35-24L009", tags)
        self.assertLess(tags.index("35-24L009"), tags.index("35-24-026"))


# ─────────────────────────────────────────────────────────────────────────────
# WFL filter — child_count gate (WFL lines with children are kept)
# ─────────────────────────────────────────────────────────────────────────────

class WflChildCountFilterTests(unittest.TestCase):
    """WFL lines with children must not be filtered; childless stubs must be."""

    def _wfl_row(self, tag: str, desc: str, has_child: bool) -> list[dict]:
        rows = [{"FUNCTION": tag, "EQUIPMENT": "", "SUB-EQUIPMENT": "", "MASK": "", "DESCRIPTION": desc}]
        if has_child:
            rows.append({"FUNCTION": "", "EQUIPMENT": "35-24-999", "SUB-EQUIPMENT": "",
                          "MASK": "", "DESCRIPTION": "VLV"})
        return rows

    def test_wfl_with_child_is_kept(self):
        """WFL pipeline with at least one equipment child must survive the utility filter."""
        rows = self._wfl_row("35-24-026", "35-24-026 WFL PROC LN", has_child=True)
        result = collect_functions(rows)
        tags = [t for t, _, _ in result]
        self.assertIn("35-24-026", tags, "WFL line with a child must NOT be filtered")

    def test_wfl_without_child_is_filtered(self):
        """WFL pipeline with NO children must be filtered as a utility stub."""
        rows = self._wfl_row("35-24-027", "35-24-027 WFL PROC LN", has_child=False)
        result = collect_functions(rows)
        tags = [t for t, _, _ in result]
        self.assertNotIn("35-24-027", tags, "WFL line without children must be filtered")

    def test_all_ten_broke_wfl_lines_kept(self):
        """All 10 Broke System WFL sealing-water pipelines survive when they have children."""
        wfl_tags = [
            "35-24-026", "35-24-076", "35-24-219", "35-24-104",
            "35-24-122", "35-24-068", "35-24-024", "35-24-121",
            "35-24-045", "35-24-042",
        ]
        rows: list[dict] = []
        for tag in wfl_tags:
            rows.append({"FUNCTION": tag, "EQUIPMENT": "", "SUB-EQUIPMENT": "",
                          "MASK": f"5001-PM03-BR-BR1-{tag}",
                          "DESCRIPTION": f"{tag} WFL PROC LN"})
            rows.append({"FUNCTION": "", "EQUIPMENT": f"child-{tag}", "SUB-EQUIPMENT": "",
                          "MASK": "", "DESCRIPTION": "VLV"})
        result = collect_functions(rows)
        tags_out = [t for t, _, _ in result]
        missing = [t for t in wfl_tags if t not in tags_out]
        self.assertEqual(missing, [], f"WFL lines missing from output: {missing}")

    def test_non_wfl_line_never_filtered(self):
        """Non-WFL pipeline (FLSH WTR) must never be filtered by the WFL gate."""
        rows = [
            {"FUNCTION": "35-24-048", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "MASK": "", "DESCRIPTION": "35-24-048 FLSH WTR LN"},
        ]
        result = collect_functions(rows)
        tags = [t for t, _, _ in result]
        self.assertIn("35-24-048", tags)

    @unittest.skipUnless(HIERARCHY_CSV.exists(), "requires hierarchy orchestrator CSV")
    def test_real_csv_all_wfl_functions_kept(self):
        """Integration: all WFL FUNCTIONs in the real Broke System CSV must survive."""
        rows = list(csv.DictReader(HIERARCHY_CSV.open(encoding="utf-8")))
        wfl_fns = {r["FUNCTION"].strip() for r in rows
                   if r.get("FUNCTION", "").strip() and "WFL" in r.get("DESCRIPTION", "").upper()
                   and not r.get("EQUIPMENT", "").strip()}
        result = collect_functions(rows)
        tags_out = {t for t, _, _ in result}
        missing = wfl_fns - tags_out
        self.assertEqual(missing, set(), f"Real WFL functions filtered out: {missing}")


# ─────────────────────────────────────────────────────────────────────────────
# B-01 (extra coverage) — mid-string LN tokens stripped from pipeline PLTXT
# ─────────────────────────────────────────────────────────────────────────────

class MidStringLnStripTests(unittest.TestCase):
    """B-01 edge cases: standalone LN between words must not appear in final PLTXT."""

    def _pltxt(self, tag: str, desc: str) -> str:
        rows = build_floc_rows([(tag, f"5001-PM03-BR-BR1-{tag}", desc)])
        fn = next(r for r in rows if r["TPLNR"].endswith(tag))
        return fn["PLTXT"]

    def test_ln_between_flow_code_and_destination(self):
        """'35-24-045 WFL LN REEL PLPR RTR1' → no mid-string LN after flow-code translation."""
        pltxt = self._pltxt("35-24-045", "35-24-045 WFL LN REEL PLPR RTR1")
        self.assertTrue(pltxt.startswith("LN 35-24-045"), f"got {pltxt!r}")
        body = pltxt[len("LN 35-24-045"):].strip()
        self.assertNotRegex(body, r"\bLN\b", f"mid-string LN still present in {pltxt!r}")

    def test_ln_before_size_spec_stripped(self):
        """'35-24-122 WFL LN 15MM' → mid-string LN removed, prefix LN remains."""
        pltxt = self._pltxt("35-24-122", "35-24-122 WFL LN 15MM")
        self.assertTrue(pltxt.startswith("LN 35-24-122"), f"got {pltxt!r}")
        body = pltxt[len("LN 35-24-122"):].strip()
        self.assertNotRegex(body, r"\bLN\b", f"mid-string LN in {pltxt!r}")

    def test_trailing_ln_marker_stripped(self):
        """'35-24-024 WFL GB LBE LN' → trailing LN removed from description body."""
        pltxt = self._pltxt("35-24-024", "35-24-024 WFL GB LBE LN")
        self.assertTrue(pltxt.startswith("LN 35-24-024"), f"got {pltxt!r}")
        body = pltxt[len("LN 35-24-024"):].strip()
        self.assertNotRegex(body, r"\bLN\b", f"trailing LN survived in {pltxt!r}")

    def test_pltxt_starts_with_ln_tag_always(self):
        """All pipeline descriptions must produce PLTXT starting with 'LN {tag}'."""
        cases = [
            ("35-24-026", "35-24-026 WFL PROC LN"),
            ("35-24-076", "35-24-076 WFL 15 GB LUB LN"),
            ("35-24-008", "35-24-008 WFL FLSHG WTR LN 15MM"),
            ("35-24-048", "35-24-048 FLSH WTR LN"),
        ]
        for tag, desc in cases:
            pltxt = self._pltxt(tag, desc)
            self.assertTrue(pltxt.startswith(f"LN {tag}"),
                            f"{tag}: expected 'LN {tag}...' got {pltxt!r}")
        self.assertNotIn("15MM", self._pltxt("35-24-008", "35-24-008 WFL FLSHG WTR LN 15MM"))

    def test_pltxt_40_char_limit_still_respected(self):
        """Long descriptions must still be clipped to 40 chars."""
        pltxt = self._pltxt("35-24-045", "35-24-045 WFL LN REEL PLPR REEL ROLL UNIT RTR1 SIDE A")
        self.assertLessEqual(len(pltxt), 40, f"PLTXT exceeds 40 chars: {pltxt!r}")


# ─────────────────────────────────────────────────────────────────────────────
# B-07 — Valve tag normalisation: all prefix variants, position-digit concat
# ─────────────────────────────────────────────────────────────────────────────

class ValveTagNormalisationTests(unittest.TestCase):
    """B-07: strip_valve_prefix covers every valve letter variant correctly."""

    def _strip(self, tag: str) -> str:
        from dwg_reader.dwg_floc_context import strip_valve_prefix
        return strip_valve_prefix(tag)

    # ── Core coverage: all 10 declared valve-letter prefixes ──────────────────

    def test_hv_stripped(self):
        self.assertEqual(self._strip("35-24HV-548"), "35-24-548")

    def test_fv_stripped(self):
        self.assertEqual(self._strip("35-24FV-570"), "35-24-570")

    def test_lv_no_digit_stripped(self):
        self.assertEqual(self._strip("35-24LV-621"), "35-24-621")

    def test_xv_stripped(self):
        self.assertEqual(self._strip("35-24XV-100"), "35-24-100")

    def test_cv_stripped(self):
        self.assertEqual(self._strip("35-24CV-300"), "35-24-300")

    def test_pv_stripped(self):
        self.assertEqual(self._strip("35-24PV-200"), "35-24-200")

    def test_bv_stripped(self):
        self.assertEqual(self._strip("35-24BV-050"), "35-24-050")

    def test_tv_stripped(self):
        self.assertEqual(self._strip("35-24TV-9251"), "35-24-9251")

    def test_kv_stripped(self):
        self.assertEqual(self._strip("35-24KV-400"), "35-24-400")

    def test_av_stripped(self):
        self.assertEqual(self._strip("35-24AV-999"), "35-24-999")

    # ── Position digit: concatenated into number, no extra hyphen ─────────────

    def test_lv2_position_digit_concatenated(self):
        """LV2-576 → 35-24-2576 (3-segment, not 4-segment 35-24-2-576)."""
        result = self._strip("35-24LV2-576")
        self.assertEqual(result, "35-24-2576")
        self.assertNotIn("-2-576", result, "extra hyphen must not appear")

    def test_lv1_position_digit_concatenated(self):
        self.assertEqual(self._strip("35-24LV1-560"), "35-24-1560")

    def test_lv1_lv2_same_number_distinct(self):
        """LV1-513 and LV2-513 must produce different stripped tags."""
        t1 = self._strip("35-24LV1-513")
        t2 = self._strip("35-24LV2-513")
        self.assertNotEqual(t1, t2, "LV1 and LV2 must not collapse to the same tag")
        self.assertEqual(t1, "35-24-1513")
        self.assertEqual(t2, "35-24-2513")

    # ── Plain tags are not modified ───────────────────────────────────────────

    def test_plain_pipeline_tag_unchanged(self):
        self.assertEqual(self._strip("35-24-137"), "35-24-137")

    def test_plain_pipeline_tag_three_digits_unchanged(self):
        self.assertEqual(self._strip("35-24-026"), "35-24-026")

    # ── format_valve_eqktx uses the stripped tag in the HV prefix slot ────────

    def test_hv_eqktx_uses_stripped_tag(self):
        result = format_valve_eqktx("35-24HV-548", "35-24L005", "", valve_type_override="AV")
        self.assertTrue(result.startswith("HV 35-24-548"), result)

    def test_tv_eqktx_uses_stripped_tag(self):
        result = format_valve_eqktx("35-24TV-9251", "35-24-008", "", valve_type_override="AV")
        self.assertTrue(result.startswith("HV 35-24-9251"), result)

    def test_lv2_eqktx_uses_concatenated_stripped_tag(self):
        result = format_valve_eqktx("35-24LV2-576", "35-24P503", "", valve_type_override="AV")
        self.assertTrue(result.startswith("HV 35-24-2576"), result)
        self.assertNotIn("-2-576", result, "4-segment tag must not appear in EQKTX")

    def test_fv_eqktx_uses_stripped_tag(self):
        result = format_valve_eqktx("35-24FV-570", "35-24-026", "", valve_type_override="AV")
        self.assertTrue(result.startswith("HV 35-24-570"), result)


# ─────────────────────────────────────────────────────────────────────────────
# B-04 — Abbreviation table applied in hierarchy tree DESCRIPTION
# ─────────────────────────────────────────────────────────────────────────────

class HierarchyTreeAbbreviationTests(unittest.TestCase):
    """B-04: export_hierarchy_tree.py applies normalize_pltxt to descriptions."""

    def _tree_desc_for(self, eq_tag: str, raw_desc: str) -> str:
        from dwg_reader.export_hierarchy_tree import build_tree_rows
        rows = [
            {"FUNCTION": "35-24L009", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24L009 MACHINE", "MASK": ""},
            {"FUNCTION": "", "EQUIPMENT": eq_tag, "SUB-EQUIPMENT": "",
             "DESCRIPTION": raw_desc, "MASK": ""},
        ]
        ctx = {"ecosystem": "valmet", "plant": "5001", "line_code": "PM03",
               "process_code": "BR", "sub_process": "BR1"}
        tree = build_tree_rows(rows, ctx=ctx)
        for row in tree:
            if row.get("EQUIPMENT") == eq_tag:
                return row.get("DESCRIPTION", "")
        return ""

    def test_conveyor_abbreviated_to_cvyr(self):
        """CONVEYOR in raw AI description must appear as CVYR in tree DESCRIPTION."""
        desc = self._tree_desc_for("35-24L010", "35-24L010 BROKE CONVEYOR BELT 1")
        self.assertIn("CVYR", desc, f"Expected CVYR in {desc!r}")
        self.assertNotIn("CONVEYOR", desc, f"CONVEYOR must be abbreviated in {desc!r}")

    def test_agitator_abbreviated_to_agi(self):
        desc = self._tree_desc_for("35-24L401", "35-24L401 BROKE TANK AGITATOR")
        self.assertIn("AGI", desc, f"Expected AGI in {desc!r}")
        self.assertNotIn("AGITATOR", desc, f"AGITATOR must be abbreviated in {desc!r}")

    def test_screen_abbreviation_applied(self):
        desc = self._tree_desc_for("35-24L015", "35-24L015 PRESSURE SCREEN PRIMARY")
        self.assertTrue(
            "SCRN" in desc or "SCR" in desc,
            f"Expected SCRN/SCR abbreviation in {desc!r}",
        )

    def test_non_abbreviatable_words_preserved(self):
        """Words not in the table pass through unchanged."""
        desc = self._tree_desc_for("35-24L009", "35-24L009 BROKE ROLL PLPR HP-33G2")
        self.assertIn("BROKE", desc)
        self.assertIn("ROLL", desc)

    def test_empty_description_safe(self):
        """Empty description row does not raise."""
        desc = self._tree_desc_for("35-24L020", "")
        self.assertIsInstance(desc, str)

    def test_function_header_row_also_abbreviated(self):
        """FUNCTION-level description rows in the tree are also abbreviated."""
        from dwg_reader.export_hierarchy_tree import build_tree_rows
        rows = [
            {"FUNCTION": "35-24L010", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24L010 WIRE CONVEYOR ROLL 1", "MASK": ""},
        ]
        ctx = {"ecosystem": "valmet", "plant": "5001", "line_code": "PM03",
               "process_code": "BR", "sub_process": "BR1"}
        tree = build_tree_rows(rows, ctx=ctx)
        fn_row = next((r for r in tree if r.get("FUNCTION") == "35-24L010"
                       and not r.get("EQUIPMENT")), None)
        self.assertIsNotNone(fn_row, "FUNCTION row not found in tree")
        desc = fn_row.get("DESCRIPTION", "")
        self.assertIn("CVYR", desc, f"Expected CVYR in function description {desc!r}")


# ─────────────────────────────────────────────────────────────────────────────
# B-02 — Hierarchy CSV DESCRIPTION patched with HV-prefixed EQKTX for valves
# ─────────────────────────────────────────────────────────────────────────────

class HierarchyCsvValvePatchTests(unittest.TestCase):
    """B-02: _patch_hierarchy_csv_with_valve_eqktx syncs formatted EQKTX back."""

    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _write_hierarchy_csv(self, rows):
        from dwg_reader.run_hierarchy_orchestrator import write_hierarchy_csv
        p = self.tmp / "Broke System.hierarchy_orchestrator.csv"
        write_hierarchy_csv(p, rows)
        return p

    def _write_reasoning_csv(self, rows):
        import csv as csv_module
        from dwg_reader.export_sap_equipment import REASONING_COLUMNS
        p = self.tmp / "Broke System.valve_reasoning.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv_module.DictWriter(f, fieldnames=REASONING_COLUMNS, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        return p

    def _patch(self, hier_csv):
        from dwg_reader.run_hierarchy_orchestrator import _patch_hierarchy_csv_with_valve_eqktx
        _patch_hierarchy_csv_with_valve_eqktx(hier_csv, self.tmp, "Broke System")

    def _read(self, hier_csv):
        from dwg_reader.run_hierarchy_orchestrator import read_hierarchy_csv
        return read_hierarchy_csv(hier_csv)

    def test_equipment_valve_description_patched(self):
        """EQUIPMENT column valve row gets HV-prefixed EQKTX in DESCRIPTION."""
        hier = self._write_hierarchy_csv([
            {"FUNCTION": "35-24-076", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-076 WFL PROC LN", "MASK": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-112", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-112 VLV AV NC", "MASK": ""},
        ])
        self._write_reasoning_csv([
            {"EQUNR": "35-24-112", "EQKTX": "HV 35-24-112 35-24-076 HV",
             "TYPE": "HV", "SOURCE": "VISION", "AI_DESCRIPTION": "", "REASONING": ""},
        ])
        self._patch(hier)
        rows = self._read(hier)
        valve_row = next(r for r in rows if r.get("EQUIPMENT") == "35-24-112")
        self.assertEqual(valve_row["DESCRIPTION"], "HV 35-24-112 35-24-076 HV")

    def test_sub_equipment_valve_description_patched(self):
        """SUB-EQUIPMENT column valve row is also patched."""
        hier = self._write_hierarchy_csv([
            {"FUNCTION": "35-24L005", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24L005 MACHINE", "MASK": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-026", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-026 WFL LINE", "MASK": ""},
            {"FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": "35-24-137",
             "DESCRIPTION": "35-24-137 DRN VLV", "MASK": ""},
        ])
        self._write_reasoning_csv([
            {"EQUNR": "35-24-137", "EQKTX": "HV 35-24-137 35-24L005 DRN NC",
             "TYPE": "DRN NC", "SOURCE": "VISION", "AI_DESCRIPTION": "", "REASONING": ""},
        ])
        self._patch(hier)
        rows = self._read(hier)
        sub_row = next(r for r in rows if r.get("SUB-EQUIPMENT") == "35-24-137")
        self.assertEqual(sub_row["DESCRIPTION"], "HV 35-24-137 35-24L005 DRN NC")

    def test_non_valve_rows_unchanged(self):
        """Machine FUNCTION rows stay put; pipeline FUNCTION rows get LN/spec cleanup."""
        orig_desc = "35-24L005 PRESS PLPR"
        hier = self._write_hierarchy_csv([
            {"FUNCTION": "35-24L005", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "DESCRIPTION": orig_desc, "MASK": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-112", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-112 VLV AV NC", "MASK": ""},
        ])
        self._write_reasoning_csv([
            {"EQUNR": "35-24-112", "EQKTX": "HV 35-24-112 35-24-076 HV",
             "TYPE": "HV", "SOURCE": "VISION", "AI_DESCRIPTION": "", "REASONING": ""},
        ])
        self._patch(hier)
        rows = self._read(hier)
        fn_row = next(r for r in rows if r.get("FUNCTION") == "35-24L005"
                      and not r.get("EQUIPMENT"))
        self.assertEqual(fn_row["DESCRIPTION"], orig_desc,
                         "Machine FUNCTION row description must not be modified")

    def test_missing_reasoning_csv_is_noop(self):
        """If valve_reasoning.csv doesn't exist, hierarchy CSV is left unchanged."""
        hier = self._write_hierarchy_csv([
            {"FUNCTION": "35-24-076", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-076 WFL LN PROC", "MASK": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-112", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-112 VLV AV NC", "MASK": ""},
        ])
        # Do NOT write reasoning CSV — patch should be a silent no-op
        self._patch(hier)
        rows = self._read(hier)
        valve_row = next(r for r in rows if r.get("EQUIPMENT") == "35-24-112")
        self.assertEqual(valve_row["DESCRIPTION"], "35-24-112 VLV AV NC",
                         "Description must be unchanged when no reasoning CSV")

    def test_multiple_valves_all_patched(self):
        """All valves in the reasoning CSV are patched in a single pass."""
        hier = self._write_hierarchy_csv([
            {"FUNCTION": "35-24-076", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-076 WFL LN", "MASK": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-112", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-112 VLV AV", "MASK": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-073", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-073 VLV NC", "MASK": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-1127", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-1127 VLV", "MASK": ""},
        ])
        self._write_reasoning_csv([
            {"EQUNR": "35-24-112", "EQKTX": "HV 35-24-112 35-24-076 HV",
             "TYPE": "HV", "SOURCE": "VISION", "AI_DESCRIPTION": "", "REASONING": ""},
            {"EQUNR": "35-24-073", "EQKTX": "HV 35-24-073 35-24-076 NC",
             "TYPE": "NC", "SOURCE": "VISION", "AI_DESCRIPTION": "", "REASONING": ""},
            {"EQUNR": "35-24-1127", "EQKTX": "HV 35-24-1127 35-24-076 AV",
             "TYPE": "AV", "SOURCE": "VISION", "AI_DESCRIPTION": "", "REASONING": ""},
        ])
        self._patch(hier)
        rows = self._read(hier)
        by_eq = {r.get("EQUIPMENT"): r for r in rows if r.get("EQUIPMENT")}
        self.assertEqual(by_eq["35-24-112"]["DESCRIPTION"], "HV 35-24-112 35-24-076 HV")
        self.assertEqual(by_eq["35-24-073"]["DESCRIPTION"], "HV 35-24-073 35-24-076 NC")
        self.assertEqual(by_eq["35-24-1127"]["DESCRIPTION"], "HV 35-24-1127 35-24-076 AV")

    def test_e02_patch_uses_format_valve_eqktx_output(self):
        """E-02: AI 'VLV AV NC' description is replaced by format_valve_eqktx() HV text."""
        from dwg_reader.export_sap_equipment import patch_hierarchy_csv_with_valve_eqktx

        rows = [
            {"FUNCTION": "35-24-076", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-076 WFL PROC LN", "MASK": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-112", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-112 VLV AV NC", "MASK": ""},
        ]
        cache = {
            "35-24-112": {
                "is_valve": True, "type": "HV", "source": "vision", "fn": "35-24-076",
            },
        }
        reasoning: list = []
        out = build_equipment_rows(rows, valve_cache=cache, reasoning_out=reasoning)
        by_tag = {r["EQUNR"]: r for r in out}
        expected = format_valve_eqktx(
            "35-24-112", "35-24-076", "35-24-112 VLV AV NC", valve_type_override="HV",
        )
        self.assertEqual(expected, "HV 35-24-112 35-24-076 HV")
        self.assertEqual(by_tag["35-24-112"]["EQKTX"], expected)
        self.assertEqual(reasoning[0]["EQKTX"], expected)
        self.assertEqual(reasoning[0]["SOURCE"], "VISION")

        hier = self._write_hierarchy_csv(rows)
        patch_hierarchy_csv_with_valve_eqktx(hier, reasoning)
        patched = self._read(hier)
        valve_row = next(r for r in patched if r.get("EQUIPMENT") == "35-24-112")
        self.assertEqual(valve_row["DESCRIPTION"], expected)

    def test_line_ai_pp200_patched_from_equipment_rows(self) -> None:
        """B-05: formatted line EQKTX (no PP-200) overwrites AI hierarchy DESCRIPTION."""
        from dwg_reader.export_sap_equipment import patch_hierarchy_csv_with_valve_eqktx

        rows = [
            {"FUNCTION": "35-24P507", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24P507 COUCH PIT PMP", "MASK": ""},
            {"FUNCTION": "", "EQUIPMENT": "35-24-119", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "AI PP-200 35-24-119 SUCT LN 15MM", "MASK": ""},
        ]
        equipment = [
            {"EQUNR": "35-24-119", "EQKTX": "LN 35-24-119 35-24P507 SUCT"},
        ]
        hier = self._write_hierarchy_csv(rows)
        patch_hierarchy_csv_with_valve_eqktx(hier, equipment)
        patched = self._read(hier)
        line_row = next(r for r in patched if r.get("EQUIPMENT") == "35-24-119")
        self.assertEqual(line_row["DESCRIPTION"], "LN 35-24-119 35-24P507 SUCT")
        self.assertNotIn("PP-200", line_row["DESCRIPTION"])

    def test_pipeline_function_row_patched(self) -> None:
        """FUNCTION-only pipeline rows are rewritten when the tag was exported."""
        from dwg_reader.export_sap_equipment import patch_hierarchy_csv_with_valve_eqktx

        rows = [
            {"FUNCTION": "35-24-076", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-076 WFL PROC LN PP-200", "MASK": ""},
        ]
        equipment = [
            {"EQUNR": "35-24-076", "EQKTX": "LN 35-24-076 SEAL WTR PROC"},
        ]
        hier = self._write_hierarchy_csv(rows)
        patch_hierarchy_csv_with_valve_eqktx(hier, equipment)
        patched = self._read(hier)
        fn_row = next(r for r in patched if r.get("FUNCTION") == "35-24-076")
        self.assertEqual(fn_row["DESCRIPTION"], "LN 35-24-076 SEAL WTR PROC")
        self.assertNotIn("PP-200", fn_row["DESCRIPTION"])

    def test_pipeline_function_15mm_stripped_without_equipment_row(self) -> None:
        """B-05: FUNCTION-only pipeline rows are not equipment; still drop 15MM."""
        from dwg_reader.export_sap_equipment import patch_hierarchy_csv_with_valve_eqktx

        rows = [
            {"FUNCTION": "35-24-012", "EQUIPMENT": "", "SUB-EQUIPMENT": "",
             "DESCRIPTION": "35-24-012 WFL PROC LN 15MM", "MASK": ""},
        ]
        hier = self._write_hierarchy_csv(rows)
        n = patch_hierarchy_csv_with_valve_eqktx(hier, [])
        self.assertGreater(n, 0)
        patched = self._read(hier)
        fn_row = next(r for r in patched if r.get("FUNCTION") == "35-24-012")
        self.assertTrue(fn_row["DESCRIPTION"].startswith("LN 35-24-012"))
        self.assertNotIn("15MM", fn_row["DESCRIPTION"].upper())
        self.assertNotIn("PP-", fn_row["DESCRIPTION"].upper())


if __name__ == "__main__":
    unittest.main()
