#!/usr/bin/env python3
"""Unit tests for V2 legend-driven valve / fitting / service-point classification."""

from __future__ import annotations

import unittest

from dwg_reader.config import LEGEND_PATH
from dwg_reader.dwg_floc_context import ALLOWED_VALVE_TOKENS, apply_sop_valve_type
from dwg_reader.dwg_valve_classify import _parse_one_pass, parse_type_tokens
from dwg_reader.dwg_valve_classify_v2 import (
    GOR_V2_EXPECTED,
    expected_tokens_match,
    load_v2_prompt,
    parse_v2_response,
    v2_prompt_path,
)


class V2PromptTests(unittest.TestCase):
    def test_prompt_file_exists(self) -> None:
        self.assertTrue(v2_prompt_path().is_file())

    def test_legend_is_png(self) -> None:
        self.assertTrue(LEGEND_PATH.is_file())
        self.assertEqual(LEGEND_PATH.suffix.lower(), ".png")
        self.assertGreater(LEGEND_PATH.stat().st_size, 10_000)

    def test_prompt_covers_legend_vocabulary(self) -> None:
        text = load_v2_prompt("168V-385")
        self.assertIn("168V-385", text)
        for token in (
            "HV", "NC", "GLV", "CHK", "3WV", "SV", "AV", "AV-M", "PRV",
            "PLUG", "AAV", "GF", "YSTR", "DRN", "FLS", "SMP",
        ):
            self.assertIn(token, text)
        for phrase in (
            "HAND VALVE", "GLOBE", "CHECK", "DRAINAGE", "FLUSHING", "SAMPLING",
            "THREE", "SAFETY", "STRAINER", "PLUG", "AIR VENT",
        ):
            self.assertIn(phrase, text.upper())
        self.assertIn("ALL drawing standards", text)
        for standard in ("SML", "GOR", "Valmet"):
            self.assertIn(standard, text)


class V2ParserTests(unittest.TestCase):
    def test_hv(self) -> None:
        self.assertEqual(parse_v2_response('{"type": "HV", "attachment": "none"}'), "HV")

    def test_chk(self) -> None:
        self.assertEqual(parse_v2_response('{"type": "CHK", "attachment": "none"}'), "CHK")

    def test_nc_drainage(self) -> None:
        got = parse_v2_response('{"type": "NC", "attachment": "DRN"}')
        self.assertEqual(set(got.split()), {"NC", "DRN"})
        got_alias = parse_v2_response('{"type": "NC", "attachment": "Drainage"}')
        self.assertEqual(set(got_alias.split()), {"NC", "DRN"})

    def test_globe_aliases(self) -> None:
        for raw in (
            '{"type": "GLV", "attachment": "none"}',
            '{"type": "GLOBE", "attachment": "none"}',
            '{"type": "Global Valve", "attachment": "none"}',
            '{"type": "GLOBE VALVE", "attachment": "none"}',
        ):
            self.assertEqual(parse_v2_response(raw), "GLV", raw)

    def test_service_points(self) -> None:
        self.assertIn("FLS", parse_v2_response('{"type": "NC", "attachment": "FLUSHING"}').split())
        self.assertIn("SMP", parse_v2_response('{"type": "NC", "attachment": "SAMPLING"}').split())

    def test_fittings(self) -> None:
        self.assertEqual(parse_v2_response('{"type": "PLUG", "attachment": "none"}'), "PLUG")
        self.assertEqual(parse_v2_response('{"type": "YSTR", "attachment": "none"}'), "YSTR")
        self.assertEqual(parse_v2_response('{"type": "Y strainer", "attachment": "none"}'), "YSTR")
        self.assertEqual(parse_v2_response('{"type": "AAV", "attachment": "none"}'), "AAV")
        self.assertEqual(parse_v2_response('{"type": "GF", "attachment": "none"}'), "GF")

    def test_three_way_and_safety(self) -> None:
        self.assertEqual(parse_v2_response('{"type": "3WV", "attachment": "none"}'), "3WV")
        self.assertEqual(parse_v2_response('{"type": "SV", "attachment": "none"}'), "SV")

    def test_av_with_drain_still_av_drn(self) -> None:
        self.assertEqual(_parse_one_pass('{"type": "AV", "attachment": "DRN"}'), "AV DRN")

    def test_glv_not_collapsed_to_hv(self) -> None:
        self.assertEqual(parse_type_tokens("GLV"), "GLV")
        self.assertEqual(apply_sop_valve_type("GLV HV"), "GLV HV")
        self.assertIn("GLV", ALLOWED_VALVE_TOKENS)


class GorUserCasesTests(unittest.TestCase):
    """User-labelled GOR WU05 valves — parser + expected token map (no Bedrock)."""

    CASES = {
        "168V-385": ('{"type": "HV", "attachment": "none"}', {"HV"}),
        "168V-389": ('{"type": "CHK", "attachment": "none"}', {"CHK"}),
        "168V-387": ('{"type": "NC", "attachment": "Drainage"}', {"NC", "DRN"}),
        "168V-390": ('{"type": "Global Valve", "attachment": "none"}', {"GLV"}),
    }

    def test_expected_map_matches_user_labels(self) -> None:
        self.assertEqual(set(GOR_V2_EXPECTED), {"168V-385", "168V-389", "168V-387", "168V-390"})
        self.assertEqual(GOR_V2_EXPECTED["168V-385"], frozenset({"HV"}))
        self.assertEqual(GOR_V2_EXPECTED["168V-389"], frozenset({"CHK"}))
        self.assertEqual(GOR_V2_EXPECTED["168V-387"], frozenset({"NC", "DRN"}))
        self.assertEqual(GOR_V2_EXPECTED["168V-390"], frozenset({"GLV"}))

    def test_parser_hits_every_user_case(self) -> None:
        for tag, (raw, expected) in self.CASES.items():
            with self.subTest(tag=tag):
                got = parse_v2_response(raw)
                self.assertTrue(
                    expected_tokens_match(got, frozenset(expected)),
                    f"{tag}: got={got!r} expected={sorted(expected)}",
                )


class VisionParserRegressionTests(unittest.TestCase):
    """Verify the parser correctly handles the JSON a well-prompted vision model should return
    for each previously-failing scored valve.

    These tests do NOT call Bedrock — they confirm the token-normalisation pipeline handles
    the correct model output cleanly.  The actual fix for the failures is in two places:
      1. Improved valve_classify_v2.md prompt (prompt-side: GLV solid rule, FLS/DRN distinction,
         NC vs CHK guidance, GLV vs AV circle-position rule).
      2. Vision-based re-confirmation loops in bedrock_classify_crop
         (_refine_drain_body_fill extended to all service-point attachments with 2-vote consensus;
          _confirm_chk_body_fill now re-checks CHK+FLS and overrides to NC when both votes agree).
    No hardcoded type overrides are used — all final answers come from vision.
    """

    # Each entry: (tag, correct_model_json, expected_token_set)
    CASES = [
        # 35-24-121 / 35-24-123: DRN NC (vision was returning DRN HV — improved
        #   _BODY_FILL_CONFIRM prompt with SML white-ink convention)
        ("35-24-121", '{"type": "NC", "attachment": "DRN"}', {"NC", "DRN"}),
        ("35-24-123", '{"type": "NC", "attachment": "DRN"}', {"NC", "DRN"}),
        # 35-24-108: FLS NC (vision was returning FLS CHK — _confirm_chk_body_fill now
        #   re-examines CHK+FLS and overrides to NC when both votes agree)
        ("35-24-108", '{"type": "NC", "attachment": "FLS"}', {"NC", "FLS"}),
        # 35-24-1105: FLS NC (vision was returning GLV — prompt now states solid triangles
        #   cannot be GLV)
        ("35-24-1105", '{"type": "NC", "attachment": "FLS"}', {"NC", "FLS"}),
        # 35-24-215 / 35-24-198: FLS NC (vision was returning DRN NC — prompt now
        #   clarifies open pipe end = FLS, enclosed shape = DRN)
        ("35-24-215", '{"type": "NC", "attachment": "FLS"}', {"NC", "FLS"}),
        ("35-24-198", '{"type": "NC", "attachment": "FLS"}', {"NC", "FLS"}),
        # 35-24-199: NC (vision was returning CHK — prompt now: same-fill triangles → NC)
        ("35-24-199", '{"type": "NC", "attachment": "none"}', {"NC"}),
        # 35-24-196: HV (vision was returning CHK — prompt now: outline triangles with no
        #   fill difference → HV, not CHK)
        ("35-24-196", '{"type": "HV", "attachment": "none"}', {"HV"}),
        # 168V-390: GLV (vision was returning AV — prompt now clarifies GLV circle is
        #   inside the bowtie, AV actuator is on an external stem)
        ("168V-390", '{"type": "GLV", "attachment": "none"}', {"GLV"}),
    ]

    def test_correct_model_output_passes(self) -> None:
        for tag, raw, expected in self.CASES:
            with self.subTest(tag=tag):
                got = parse_v2_response(raw)
                self.assertTrue(
                    expected_tokens_match(got, frozenset(expected)),
                    f"{tag}: parse_v2_response({raw!r}) → {got!r}, expected subset {sorted(expected)}",
                )

    def test_fls_hv_not_broken(self) -> None:
        """35-24-001 returns FLS HV and PASSES (expected is just HV).
        Verify the parser preserves FLS HV — no hardcoded rule may force it to NC FLS.
        """
        got = parse_v2_response('{"type": "HV", "attachment": "FLS"}')
        tokens = set(got.upper().split())
        self.assertIn("HV", tokens, "HV must be present in FLS HV parse")
        self.assertIn("FLS", tokens, "FLS must be present in FLS HV parse")
        self.assertNotIn("NC", tokens, "NC must NOT be injected — no hardcoded rule allowed")


if __name__ == "__main__":
    unittest.main()
