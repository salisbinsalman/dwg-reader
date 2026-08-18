#!/usr/bin/env python3
"""
System Integration Tests — valve EQKTX classification.

Fixtures are real hierarchy rows from the Broke System P&ID
(functions P503-P510, T604-T605) as output by the AI hierarchy pipeline.
No Bedrock calls required — tests the full export pipeline on known AI outputs.

Classification paths covered:
  HV  – plain hand valve (AI default, no type token in desc)
  NC  – normally closed (qualifier rule, AI saw filled bowtie)
  DRN – drain valve (qualifier rule, AI saw drain symbol)
  AV  – automatic (immediate rule when AI appends AV token, or FV/XV tag prefix)
  AV  – override (inputs/valve_type_overrides.json forces type regardless of AI)
"""

from __future__ import annotations

import unittest
from pathlib import Path

from export_sap_equipment import build_equipment_rows

ROOT = Path(__file__).resolve().parent

# P&ID crop screenshots produced by the AI hierarchy pipeline.
# Image 1 (P&ID section) + inputs/legend.png (Image 2) were sent to Bedrock
# together; the AI appended type tokens to valve descriptions based on both.
# Open the relevant image to visually verify any classification.
EVIDENCE_IMAGES: dict[str, Path] = {
    fn: p
    for fn in ("35-24P503", "35-24P506", "35-24P507", "35-24P508",
               "35-24P509", "35-24P510", "35-24T604", "35-24T605")
    if (p := ROOT / "outputs" / "evidence" / f"Broke System.viewer_{fn}.png").exists()
}
LEGEND_IMAGE: Path = ROOT / "inputs" / "legend.png"


def _fn_row(fn: str) -> dict:
    return {"FUNCTION": fn, "EQUIPMENT": "", "SUB-EQUIPMENT": "", "DESCRIPTION": ""}


def _eq_row(tag: str, desc: str) -> dict:
    return {"FUNCTION": "", "EQUIPMENT": tag, "SUB-EQUIPMENT": "", "DESCRIPTION": desc}


def _sub_row(tag: str, desc: str) -> dict:
    return {"FUNCTION": "", "EQUIPMENT": "", "SUB-EQUIPMENT": tag, "DESCRIPTION": desc}


class SITValveClassificationTests(unittest.TestCase):
    """
    Each test fixture mirrors a real P&ID section as emitted by dwg_pid_hierarchy_ai.py.
    The AI appends a type token (AV / NC / DRN / HV) to valve descriptions based on
    the symbol legend (Image 2).  build_equipment_rows picks that token up via
    infer_valve_type and assembles the SML EQKTX: HV {stripped-tag} {fn} {type}.
    """

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _eqktx_for(
        self,
        rows: list[dict],
        valve_tag: str,
        *,
        fn: str = "",
    ) -> str:
        """
        Run build_equipment_rows and return the EQKTX for valve_tag.

        Pass fn to get the evidence image path included in failure messages,
        e.g. fn="35-24P503" → outputs/evidence/Broke System.viewer_35-24P503.png
        """
        out = build_equipment_rows(rows)
        target = valve_tag.upper().replace(" ", "")
        matches = [r for r in out if r["EQUNR"] == target]
        img = EVIDENCE_IMAGES.get(fn, "")
        hint = f"\n  P&ID crop : {img}\n  Legend    : {LEGEND_IMAGE}" if img else ""
        self.assertTrue(matches, f"No Equipment row emitted for {valve_tag}{hint}")
        return matches[0]["EQKTX"]

    def _assert_eqktx(self, actual: str, expected: str, valve_tag: str, fn: str = "") -> None:
        img = EVIDENCE_IMAGES.get(fn, "")
        hint = f"\n  P&ID crop : {img}\n  Legend    : {LEGEND_IMAGE}" if img else ""
        self.assertEqual(actual, expected, f"{valve_tag}: expected {expected!r}{hint}")

    # -----------------------------------------------------------------------
    # HV — plain hand valve (AI default, open bowtie with nothing on top)
    # -----------------------------------------------------------------------

    def test_plain_hv_isolation_valve_p503(self) -> None:
        """35-24-234 on pump suction line: AI saw plain open bowtie → HV."""
        rows = [
            _fn_row("35-24P503"),
            _eq_row("35-24-095", "35-24-095 SUCT LN PP-200"),
            _sub_row("35-24-234", "35-24-234 ISOL VLV HV"),
        ]
        actual = self._eqktx_for(rows, "35-24-234", fn="35-24P503")
        self._assert_eqktx(actual, "HV 35-24-234 35-24P503 HV", "35-24-234", "35-24P503")

    def test_plain_hv_isolation_valve_p508(self) -> None:
        """35-24-227 on slabbing pump suction/discharge: AI saw plain bowtie → HV."""
        rows = [
            _fn_row("35-24P508"),
            _eq_row("35-24-025", "35-24-025 SUCT/DIS PP-600"),
            _sub_row("35-24-227", "35-24-227 ISOL VLV HV"),
        ]
        actual = self._eqktx_for(rows, "35-24-227", fn="35-24P508")
        self._assert_eqktx(actual, "HV 35-24-227 35-24P508 HV", "35-24-227", "35-24P508")

    def test_plain_hv_isolation_valve_p510_205(self) -> None:
        """35-24-205 on broke pump suction: AI saw plain bowtie → HV."""
        rows = [
            _fn_row("35-24P510"),
            _eq_row("35-24-062", "35-24-062 SUCT LN PP250"),
            _sub_row("35-24-205", "35-24-205 ISOL VLV HV"),
        ]
        actual = self._eqktx_for(rows, "35-24-205", fn="35-24P510")
        self._assert_eqktx(actual, "HV 35-24-205 35-24P510 HV", "35-24-205", "35-24P510")

    def test_plain_hv_isolation_valve_p510_129(self) -> None:
        """35-24-129/130 on broke pump suction: AI saw plain bowtie → HV."""
        rows = [
            _fn_row("35-24P510"),
            _eq_row("35-24-062", "35-24-062 SUCT LN PP250"),
            _sub_row("35-24-129", "35-24-129 ISOL VLV HV"),
            _sub_row("35-24-130", "35-24-130 ISOL VLV HV"),
        ]
        for tag, expected in [("35-24-129", "HV 35-24-129 35-24P510 HV"),
                               ("35-24-130", "HV 35-24-130 35-24P510 HV")]:
            self._assert_eqktx(self._eqktx_for(rows, tag, fn="35-24P510"), expected, tag, "35-24P510")

    # -----------------------------------------------------------------------
    # NC — normally closed (AI saw filled / black bowtie body)
    # -----------------------------------------------------------------------

    def test_nc_isolation_valve_p503(self) -> None:
        """35-24-217 on pump discharge: AI saw filled bowtie → NC."""
        rows = [
            _fn_row("35-24P503"),
            _eq_row("35-24-096", "35-24-096 DISCH LN PP-900"),
            _sub_row("35-24-217", "35-24-217 ISOL VLV NC"),
        ]
        actual = self._eqktx_for(rows, "35-24-217", fn="35-24P503")
        self._assert_eqktx(actual, "HV 35-24-217 35-24P503 NC", "35-24-217", "35-24P503")

    def test_nc_isolation_valve_t604(self) -> None:
        """35-24-035 on filter tank outlet: AI saw filled bowtie → NC."""
        rows = [
            _fn_row("35-24T604"),
            _eq_row("35-24-148", "35-24-148 OUT LN WAA-150"),
            _sub_row("35-24-035", "35-24-035 ISOL VLV NC"),
        ]
        actual = self._eqktx_for(rows, "35-24-035", fn="35-24T604")
        self._assert_eqktx(actual, "HV 35-24-035 35-24T604 NC", "35-24-035", "35-24T604")

    # -----------------------------------------------------------------------
    # DRN — drain valve (AI saw downward branch to drain symbol)
    # -----------------------------------------------------------------------

    def test_drn_valve_p510(self) -> None:
        """35-24-131 on suction line drain branch: AI saw drain symbol → DRN."""
        rows = [
            _fn_row("35-24P510"),
            _eq_row("35-24-062", "35-24-062 SUCT LN PP250"),
            _sub_row("35-24-131", "35-24-131 DRN VLV DRN"),
        ]
        actual = self._eqktx_for(rows, "35-24-131", fn="35-24P510")
        self._assert_eqktx(actual, "HV 35-24-131 35-24P510 DRN", "35-24-131", "35-24P510")

    # -----------------------------------------------------------------------
    # AV via AI vision — plain-numbered tag, AI detected actuator on symbol
    # -----------------------------------------------------------------------

    def test_av_ai_vision_plain_tag_t604_1136(self) -> None:
        """35-24-1136 on filter tank inlet: AI saw actuator circle → AV token in desc."""
        rows = [
            _fn_row("35-24T604"),
            _eq_row("35-24-146", "35-24-146 IN LN WAA-400"),
            _sub_row("35-24-1136", "35-24-1136 ISOL VLV AV"),
        ]
        actual = self._eqktx_for(rows, "35-24-1136", fn="35-24T604")
        self._assert_eqktx(actual, "HV 35-24-1136 35-24T604 AV", "35-24-1136", "35-24T604")

    def test_av_ai_vision_plain_tag_t604_1117(self) -> None:
        """35-24-1117 on filter tank inlet line: AI saw actuator circle → AV token."""
        rows = [
            _fn_row("35-24T604"),
            _eq_row("35-24-145", "35-24-145 IN LN WAA-300"),
            _sub_row("35-24-1117", "35-24-1117 ISOL VLV AV"),
        ]
        actual = self._eqktx_for(rows, "35-24-1117", fn="35-24T604")
        self._assert_eqktx(actual, "HV 35-24-1117 35-24T604 AV", "35-24-1117", "35-24T604")

    # -----------------------------------------------------------------------
    # AV via LV prefix — level control valves are always automated
    # -----------------------------------------------------------------------

    def test_av_lv2_prefix_strip_position_digit_p503(self) -> None:
        """35-24LV2-576: LV prefix → AV; position digit 2 preserved in stripped tag."""
        rows = [
            _fn_row("35-24P503"),
            _eq_row("35-24-095", "35-24-095 SUCT LN PP-200"),
            _sub_row("35-24LV2-576", "35-24LV2-576 LVL CTRL VLV AV"),
        ]
        actual = self._eqktx_for(rows, "35-24LV2-576", fn="35-24P503")
        self._assert_eqktx(actual, "HV 35-24-2-576 35-24P503 AV", "35-24LV2-576", "35-24P503")

    def test_av_lv1_prefix_strip_position_digit_p509(self) -> None:
        """35-24LV1-513/LV2-513: position digit 1/2 preserved to avoid tag collision."""
        rows = [
            _fn_row("35-24P509"),
            _eq_row("35-24-009", "35-24-009 SUCT LN PP600"),
            _sub_row("35-24LV1-513", "35-24LV1-513 LVL CTRL VLV AV"),
            _sub_row("35-24LV2-513", "35-24LV2-513 LVL CTRL VLV AV"),
        ]
        for tag, expected in [("35-24LV1-513", "HV 35-24-1-513 35-24P509 AV"),
                               ("35-24LV2-513", "HV 35-24-2-513 35-24P509 AV")]:
            self._assert_eqktx(self._eqktx_for(rows, tag, fn="35-24P509"), expected, tag, "35-24P509")

    def test_av_lv_prefix_no_position_digit_t604(self) -> None:
        """35-24LV-621: LV prefix without position digit → no digit in stripped tag."""
        rows = [
            _fn_row("35-24T604"),
            _eq_row("35-24-144", "35-24-144 IN LN WAA-200"),
            _sub_row("35-24LV-621", "35-24LV-621 LVL CTRL VLV AV"),
        ]
        actual = self._eqktx_for(rows, "35-24LV-621", fn="35-24T604")
        self._assert_eqktx(actual, "HV 35-24-621 35-24T604 AV", "35-24LV-621", "35-24T604")

    def test_av_lv_nc_av_desc_immediate_rule_wins(self) -> None:
        """LV1-518 desc has both NC and AV tokens: AV (immediate rule) takes priority over NC."""
        rows = [
            _fn_row("35-24P508"),
            _eq_row("35-24-025", "35-24-025 SUCT/DIS PP-600"),
            _sub_row("35-24LV1-518", "35-24LV1-518 LVL CNTRL VLV NC AV"),
            _sub_row("35-24LV2-518", "35-24LV2-518 LVL CNTRL VLV NC AV"),
        ]
        for tag, expected in [("35-24LV1-518", "HV 35-24-1-518 35-24P508 AV"),
                               ("35-24LV2-518", "HV 35-24-2-518 35-24P508 AV")]:
            self._assert_eqktx(self._eqktx_for(rows, tag, fn="35-24P508"), expected, tag, "35-24P508")

    # -----------------------------------------------------------------------
    # AV via HV prefix + AI detected actuator on symbol
    # -----------------------------------------------------------------------

    def test_av_hv_prefix_ai_detected_actuator_t605(self) -> None:
        """35-24HV-626: HV prefix would default to HV, but AI saw actuator → AV token in desc."""
        rows = [
            _fn_row("35-24T605"),
            _eq_row("35-24-152", "35-24-152 PP 300"),
            _sub_row("35-24HV-626", "35-24HV-626 ISOL VLV AV"),
        ]
        actual = self._eqktx_for(rows, "35-24HV-626", fn="35-24T605")
        self._assert_eqktx(actual, "HV 35-24-626 35-24T605 AV", "35-24HV-626", "35-24T605")

    # -----------------------------------------------------------------------
    # AV via FV tag prefix — flow/control valves are always automated
    # -----------------------------------------------------------------------

    def test_av_fv_prefix_tag_rule_no_desc_token_needed(self) -> None:
        """35-24FV-550: FV prefix alone forces AV even when desc has no AV token."""
        rows = [
            _fn_row("35-24P507"),
            _eq_row("35-24FV-550", "35-24FV-550 FL CTRL VLV"),  # no AV token in desc
        ]
        out = build_equipment_rows(rows)
        matches = [r for r in out if r["EQUNR"] == "35-24FV-550"]
        img = EVIDENCE_IMAGES.get("35-24P507", "")
        self.assertTrue(matches, f"No row emitted for 35-24FV-550\n  P&ID crop : {img}")
        self._assert_eqktx(matches[0]["EQKTX"], "HV 35-24-550 35-24P507 AV", "35-24FV-550", "35-24P507")

if __name__ == "__main__":
    unittest.main(verbosity=2)
