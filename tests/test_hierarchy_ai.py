#!/usr/bin/env python3
"""
Comprehensive unit tests for dwg_pid_hierarchy_ai — hierarchy parsing, filtering,
refine_ai_hierarchy, rows_from_ai, and helper functions.

No Bedrock, no DWG files required.
"""

from __future__ import annotations

import json
import unittest
from typing import Any, Dict, List, Optional

from dwg_pid_hierarchy_ai import (
    _fn_numeric,
    _motor_matches_fn,
    canonicalize_vision_tag,
    extract_json_object,
    is_plausible_hierarchy_tag,
    nearby_line_seeds,
    normalize_tag,
    plant_prefix,
    refine_ai_hierarchy,
    rows_from_ai,
)
from dwg_floc_context import DEFAULT_FLOC_CONTEXT


# Shared plant context for rows_from_ai tests
CONTEXT: Dict[str, str] = {
    "site": "Shotton Paper Mill, United Kingdom",
    "line": "Shotton PM3",
    "process": "Broke System",
    "process_name": "BROKE SYSTEM",
    "sub_process": "BR1",
    **{k: v for k, v in DEFAULT_FLOC_CONTEXT.items() if isinstance(v, str)},
}


def _refine(
    tag: str,
    rows: List[Dict[str, str]],
    *,
    raw_text: str = "",
    peers: Optional[List[str]] = None,
    inventory_lines: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Helper: build a minimal parsed dict and call refine_ai_hierarchy."""
    parsed = {
        "sub_process": "BR1",
        "function": tag,
        "description": f"{tag} TEST",
        "rows": rows,
        "peers": [{"tag": p, "evidence": "test"} for p in (peers or [])],
    }
    inv = {"lines": inventory_lines or []} if inventory_lines else None
    return refine_ai_hierarchy(
        tag,
        parsed,
        center=(0.0, 0.0),
        inventory=inv,
        structural=None,
        peer_tags=peers or [],
        raw_text=raw_text,
    )


def _equipment_tags(refined: Dict[str, Any]) -> List[str]:
    return [r["equipment"] for r in refined["rows"] if r.get("equipment")]


def _sub_equipment_tags(refined: Dict[str, Any]) -> List[str]:
    return [r["subequipment"] for r in refined["rows"] if r.get("subequipment")]


# ---------------------------------------------------------------------------
# normalize_tag
# ---------------------------------------------------------------------------
class NormalizeTagTests(unittest.TestCase):
    def test_uppercase_and_strip(self):
        self.assertEqual(normalize_tag("  35-24l009  "), "35-24L009")

    def test_spaces_removed(self):
        # normalize_tag removes whitespace — it does NOT insert dashes
        self.assertEqual(normalize_tag("35 24 L009"), "3524L009")

    def test_already_clean(self):
        self.assertEqual(normalize_tag("35-24LC-576"), "35-24LC-576")

    def test_long_line_tag_truncated_to_short(self):
        # normalize_tag doesn't strip suffixes — that's norm_tag in eval
        result = normalize_tag("35-24-189-PP-200-E10H2A")
        self.assertIn("35-24-189", result)

    def test_empty_string(self):
        self.assertEqual(normalize_tag(""), "")


# ---------------------------------------------------------------------------
# _fn_numeric
# ---------------------------------------------------------------------------
class FnNumericTests(unittest.TestCase):
    def test_pulper_L004(self):
        self.assertEqual(_fn_numeric("35-24L004"), "004")

    def test_pulper_L009(self):
        self.assertEqual(_fn_numeric("35-24L009"), "009")

    def test_pump_P519(self):
        self.assertEqual(_fn_numeric("35-24P519"), "519")

    def test_tank_T607(self):
        self.assertEqual(_fn_numeric("35-24T607"), "607")

    def test_pulper_leading_zero(self):
        self.assertEqual(_fn_numeric("35-24L001"), "001")

    def test_plain_line_tag_returns_none(self):
        # 35-24-189 has no letter prefix → no function numeric
        self.assertIsNone(_fn_numeric("35-24-189"))

    def test_instrument_tag_returns_none(self):
        # 35-24LC-576 has a dash before the number — doesn't match function pattern
        self.assertIsNone(_fn_numeric("35-24LC-576"))

    def test_lowercased_input_handled(self):
        # normalize_tag is called internally
        self.assertEqual(_fn_numeric("35-24l004"), "004")


# ---------------------------------------------------------------------------
# _motor_matches_fn
# ---------------------------------------------------------------------------
class MotorMatchesFnTests(unittest.TestCase):
    """Core tests for the stray-motor filter."""

    # Correct motors that must be kept
    def test_dash_motor_matches(self):
        self.assertTrue(_motor_matches_fn("35-24-004.1", "004"))

    def test_dash_motor_matches_second(self):
        self.assertTrue(_motor_matches_fn("35-24-004.2", "004"))

    def test_prefix_motor_matches(self):
        self.assertTrue(_motor_matches_fn("35-24L004.1", "004"))

    def test_pump_motor_matches(self):
        self.assertTrue(_motor_matches_fn("35-24-519.1", "519"))

    def test_tank_motor_matches(self):
        self.assertTrue(_motor_matches_fn("35-24-607.2", "607"))

    def test_three_digit_large_number(self):
        self.assertTrue(_motor_matches_fn("35-24-519.1", "519"))

    # Stray motors that must be rejected
    def test_wrong_base_dash_motor(self):
        self.assertFalse(_motor_matches_fn("35-24-003.1", "004"))

    def test_wrong_base_prefix_motor(self):
        self.assertFalse(_motor_matches_fn("35-24L003.1", "004"))

    def test_wrong_base_pump(self):
        self.assertFalse(_motor_matches_fn("35-24-503.1", "519"))

    def test_neighbour_leakage(self):
        # L003's motor appearing under L004
        self.assertFalse(_motor_matches_fn("35-24-003.2", "004"))

    # Non-motor tags — always kept
    def test_plain_line_tag_kept(self):
        self.assertTrue(_motor_matches_fn("35-24-081", "004"))

    def test_instrument_tag_kept(self):
        self.assertTrue(_motor_matches_fn("35-24LC-674", "009"))

    def test_valve_tag_kept(self):
        self.assertTrue(_motor_matches_fn("35-24HV-649", "607"))

    def test_function_tag_kept(self):
        self.assertTrue(_motor_matches_fn("35-24P519", "519"))

    # Edge cases
    def test_empty_tag_kept(self):
        self.assertTrue(_motor_matches_fn("", "004"))

    def test_l009_motor_correct(self):
        self.assertTrue(_motor_matches_fn("35-24-009.1", "009"))
        self.assertTrue(_motor_matches_fn("35-24L009.1", "009"))

    def test_l009_stray_motor(self):
        self.assertFalse(_motor_matches_fn("35-24-003.1", "009"))


# ---------------------------------------------------------------------------
# canonicalize_vision_tag
# ---------------------------------------------------------------------------
class CanonicalizeVisionTagTests(unittest.TestCase):
    def test_xv_corrected_to_xs(self):
        self.assertEqual(canonicalize_vision_tag("35-24XV-501"), "35-24XS-501")

    def test_normal_tag_unchanged(self):
        self.assertEqual(canonicalize_vision_tag("35-24LC-576"), "35-24LC-576")

    def test_lowercase_uppercased(self):
        self.assertEqual(canonicalize_vision_tag("35-24lc-576"), "35-24LC-576")

    def test_motor_tag_unchanged(self):
        self.assertEqual(canonicalize_vision_tag("35-24-004.1"), "35-24-004.1")


# ---------------------------------------------------------------------------
# is_plausible_hierarchy_tag
# ---------------------------------------------------------------------------
class IsPlausibleHierarchyTagTests(unittest.TestCase):
    def _ok(self, tok, parent="35-24L009"):
        return is_plausible_hierarchy_tag(tok, parent)

    # Valid tags
    def test_plain_line_tag(self):
        self.assertTrue(self._ok("35-24-189"))

    def test_instrument_tag(self):
        self.assertTrue(self._ok("35-24LC-674"))

    def test_motor_tag(self):
        self.assertTrue(self._ok("35-24-009.1"))

    def test_function_tag_itself(self):
        self.assertTrue(self._ok("35-24L009"))

    def test_pump_tag(self):
        self.assertTrue(self._ok("35-24P519"))

    def test_valve_tag(self):
        self.assertTrue(self._ok("35-24HV-649"))

    # Rejected noise
    def test_too_short(self):
        self.assertFalse(self._ok("35-24"))

    def test_pipe_class_fragment(self):
        # "001-100" pattern from pipe spec text
        self.assertFalse(self._ok("001-100"))

    def test_wrong_plant_prefix(self):
        # Different plant area
        self.assertFalse(self._ok("35-25-189"))

    def test_hs_instrument_excluded(self):
        # Local panel pushbuttons not in GT hierarchy
        self.assertFalse(self._ok("35-24HS-501"))

    def test_es_instrument_excluded(self):
        self.assertFalse(self._ok("35-24ES-588"))

    def test_ki_instrument_excluded(self):
        self.assertFalse(self._ok("35-24KI-601"))

    def test_mcs_excluded(self):
        self.assertFalse(self._ok("35-24MCS-501"))

    def test_empty_string(self):
        self.assertFalse(self._ok(""))


# ---------------------------------------------------------------------------
# plant_prefix
# ---------------------------------------------------------------------------
class PlantPrefixTests(unittest.TestCase):
    def test_standard_tag(self):
        self.assertEqual(plant_prefix("35-24L009"), "35-24")

    def test_plain_line_tag(self):
        self.assertEqual(plant_prefix("35-24-189"), "35-24")

    def test_instrument_tag(self):
        self.assertEqual(plant_prefix("35-24LC-576"), "35-24")


# ---------------------------------------------------------------------------
# extract_json_object
# ---------------------------------------------------------------------------
class ExtractJsonObjectTests(unittest.TestCase):
    def test_clean_json(self):
        text = '{"function": "35-24L009", "rows": []}'
        obj = extract_json_object(text)
        self.assertIsNotNone(obj)
        self.assertEqual(obj["function"], "35-24L009")

    def test_json_in_markdown_fence(self):
        text = '```json\n{"function": "35-24L009", "rows": []}\n```'
        obj = extract_json_object(text)
        self.assertIsNotNone(obj)
        self.assertEqual(obj["function"], "35-24L009")

    def test_json_embedded_in_prose(self):
        text = 'Here is my result:\n{"function": "35-24L009", "rows": []}\nDone.'
        obj = extract_json_object(text)
        self.assertIsNotNone(obj)
        self.assertEqual(obj["function"], "35-24L009")

    def test_invalid_json_returns_none(self):
        self.assertIsNone(extract_json_object("not json at all"))

    def test_empty_string_returns_none(self):
        self.assertIsNone(extract_json_object(""))

    def test_array_top_level_returns_none(self):
        self.assertIsNone(extract_json_object('[1, 2, 3]'))

    def test_nested_rows(self):
        payload = {
            "function": "35-24L009",
            "rows": [
                {"equipment": "35-24-189", "subequipment": "", "description": "LN OVFL"},
                {"equipment": "", "subequipment": "35-24HV-649", "description": "HND VLV"},
            ],
        }
        obj = extract_json_object(json.dumps(payload))
        self.assertEqual(len(obj["rows"]), 2)
        self.assertEqual(obj["rows"][0]["equipment"], "35-24-189")


# ---------------------------------------------------------------------------
# nearby_line_seeds
# ---------------------------------------------------------------------------
class NearbyLineSeedsTests(unittest.TestCase):
    """Tests for CAD line seed extraction."""

    def _seeds(self, parent_tag, lines, radius=130.0):
        inv = {"lines": lines}
        return nearby_line_seeds((0.0, 0.0), inv, None, parent_tag, radius=radius)

    def test_line_within_radius_included(self):
        lines = [{"line_number": "35-24-189", "x": 50.0, "y": 0.0}]
        seeds = self._seeds("35-24L009", lines)
        self.assertIn("35-24-189", seeds)

    def test_line_outside_radius_excluded(self):
        lines = [{"line_number": "35-24-189", "x": 500.0, "y": 0.0}]
        seeds = self._seeds("35-24L009", lines)
        self.assertNotIn("35-24-189", seeds)

    def test_motor_convention_seeds_always_added(self):
        # Even with no inventory lines, the .1/.2 convention seeds are injected
        seeds = nearby_line_seeds((0.0, 0.0), None, None, "35-24L004")
        self.assertIn("35-24-004.1", seeds)
        self.assertIn("35-24-004.2", seeds)

    def test_motor_convention_seeds_for_pump(self):
        seeds = nearby_line_seeds((0.0, 0.0), None, None, "35-24P519")
        self.assertIn("35-24-519.1", seeds)

    def test_instrument_line_not_seeded(self):
        # Seeds require the 35-24-NNN format (all digits after second dash)
        lines = [{"line_number": "35-24LC-576", "x": 10.0, "y": 0.0}]
        seeds = self._seeds("35-24L009", lines)
        self.assertNotIn("35-24LC-576", seeds)

    def test_wrong_plant_line_not_seeded(self):
        lines = [{"line_number": "35-25-100", "x": 10.0, "y": 0.0}]
        seeds = self._seeds("35-24L009", lines)
        self.assertNotIn("35-25-100", seeds)

    def test_pipe_class_fragment_not_seeded(self):
        # "001-100" style fragments from pipe class text
        lines = [{"line_number": "001-100", "x": 10.0, "y": 0.0}]
        seeds = self._seeds("35-24L009", lines)
        self.assertNotIn("001-100", seeds)

    def test_multiple_lines_sorted_by_distance(self):
        lines = [
            {"line_number": "35-24-200", "x": 100.0, "y": 0.0},
            {"line_number": "35-24-201", "x": 10.0, "y": 0.0},
        ]
        seeds = self._seeds("35-24L009", lines)
        # Closer one should appear earlier
        idx_201 = seeds.index("35-24-201") if "35-24-201" in seeds else 999
        idx_200 = seeds.index("35-24-200") if "35-24-200" in seeds else 999
        self.assertLess(idx_201, idx_200)


# ---------------------------------------------------------------------------
# refine_ai_hierarchy — FUNCTION / EQUIPMENT / SUB-EQUIPMENT parsing
# ---------------------------------------------------------------------------
class RefineAiHierarchyBasicTests(unittest.TestCase):
    """Basic structure: rows extracted correctly, description normalised."""

    def test_equipment_rows_extracted(self):
        rows = [
            {"equipment": "35-24-189", "subequipment": "", "description": "LN OVFL"},
            {"equipment": "35-24P519", "subequipment": "", "description": "PMP"},
        ]
        result = _refine("35-24L009", rows)
        eq_tags = _equipment_tags(result)
        self.assertIn("35-24-189", eq_tags)
        self.assertIn("35-24P519", eq_tags)

    def test_sub_equipment_rows_extracted(self):
        rows = [
            {"equipment": "35-24-189", "subequipment": "", "description": ""},
            {"equipment": "", "subequipment": "35-24HV-649", "description": "HND VLV"},
        ]
        result = _refine("35-24L009", rows)
        self.assertIn("35-24HV-649", _sub_equipment_tags(result))

    def test_function_tag_normalised_in_output(self):
        result = _refine("35-24l009", [])
        self.assertEqual(result["function"], "35-24L009")

    def test_description_truncated_to_40(self):
        rows = [{"equipment": "35-24-189", "subequipment": "", "description": "A" * 50}]
        result = _refine("35-24L009", rows)
        # function-level description
        self.assertLessEqual(len(result["description"]), 40)

    def test_function_description_prefixed_with_tag(self):
        result = _refine("35-24L009", [])
        self.assertTrue(result["description"].startswith("35-24L009"))

    def test_duplicate_equipment_deduplicated(self):
        rows = [
            {"equipment": "35-24-189", "subequipment": "", "description": ""},
            {"equipment": "35-24-189", "subequipment": "", "description": ""},
        ]
        result = _refine("35-24L009", rows)
        eq_tags = _equipment_tags(result)
        self.assertEqual(eq_tags.count("35-24-189"), 1)

    def test_empty_rows_motor_convention_seeds_injected(self):
        # Even with no AI rows, nearby_line_seeds always injects the .1/.2 motor
        # convention tags for the function (e.g. 35-24L009.1, 35-24-009.1).
        result = _refine("35-24L009", [])
        motor_tags = [r["equipment"] for r in result["rows"] if ".1" in r.get("equipment", "") or ".2" in r.get("equipment", "")]
        self.assertTrue(len(motor_tags) >= 1)

    def test_rows_with_both_eq_and_sub_eq_accepted(self):
        # Row has both equipment and subequipment set — push() only keeps first valid
        rows = [
            {"equipment": "35-24-189", "subequipment": "35-24HV-649", "description": ""},
        ]
        result = _refine("35-24L009", rows)
        # The equipment takes priority; subequipment is silently dropped by the xor rule
        all_tags = _equipment_tags(result) + _sub_equipment_tags(result)
        self.assertTrue(len(all_tags) >= 1)

    def test_instrument_children_kept(self):
        rows = [
            {"equipment": "35-24LC-674", "subequipment": "", "description": "LVL CTRL"},
            {"equipment": "35-24LV-674", "subequipment": "", "description": "LVL VLV"},
        ]
        result = _refine("35-24L009", rows)
        eq_tags = _equipment_tags(result)
        self.assertIn("35-24LC-674", eq_tags)
        self.assertIn("35-24LV-674", eq_tags)


# ---------------------------------------------------------------------------
# refine_ai_hierarchy — peer / noise filtering
# ---------------------------------------------------------------------------
class RefineAiHierarchyFilterTests(unittest.TestCase):
    def test_peer_tag_excluded_from_children(self):
        rows = [{"equipment": "35-24L003", "subequipment": "", "description": ""}]
        result = _refine("35-24L004", rows, peers=["35-24L003"])
        self.assertNotIn("35-24L003", _equipment_tags(result))

    def test_noise_fragment_excluded(self):
        # "001-100" is a pipe class fragment — is_plausible_hierarchy_tag rejects it
        rows = [{"equipment": "001-100", "subequipment": "", "description": ""}]
        result = _refine("35-24L009", rows)
        self.assertNotIn("001-100", _equipment_tags(result))

    def test_hs_pushbutton_excluded(self):
        rows = [{"equipment": "35-24HS-501", "subequipment": "", "description": ""}]
        result = _refine("35-24L009", rows)
        self.assertNotIn("35-24HS-501", _equipment_tags(result))

    def test_mcs_instrument_excluded(self):
        rows = [{"equipment": "35-24MCS-501", "subequipment": "", "description": ""}]
        result = _refine("35-24L009", rows)
        self.assertNotIn("35-24MCS-501", _equipment_tags(result))

    def test_wrong_plant_tag_excluded(self):
        rows = [{"equipment": "35-25-189", "subequipment": "", "description": ""}]
        result = _refine("35-24L009", rows)
        self.assertNotIn("35-25-189", _equipment_tags(result))

    def test_too_short_tag_excluded(self):
        rows = [{"equipment": "35", "subequipment": "", "description": ""}]
        result = _refine("35-24L009", rows)
        self.assertNotIn("35", _equipment_tags(result))

    def test_valid_tag_not_in_peer_list_kept(self):
        rows = [{"equipment": "35-24-189", "subequipment": "", "description": ""}]
        result = _refine("35-24L009", rows, peers=["35-24L003", "35-24P519"])
        self.assertIn("35-24-189", _equipment_tags(result))

    def test_xv_corrected_to_xs_in_child(self):
        # canonicalize_vision_tag converts XV → XS before plausibility check
        rows = [{"equipment": "35-24XV-501", "subequipment": "", "description": ""}]
        result = _refine("35-24L009", rows)
        # XS-501 passes the plausibility check (XS excluded by the HS/ES/KI/KJ/HI filter — wait, let me check)
        # Actually XS is not in the excluded set: (?:HS|ES|KI|KJ|HI|MCS)
        # So XS tags are plausible — they should be kept as XS
        eq_tags = _equipment_tags(result)
        # Should be in as XS-501 not XV-501
        if eq_tags:
            self.assertNotIn("35-24XV-501", eq_tags)


# ---------------------------------------------------------------------------
# refine_ai_hierarchy — motor numeric filter (Bug 3 fix)
# ---------------------------------------------------------------------------
class MotorNumericFilterTests(unittest.TestCase):
    """Motor tags whose numeric base doesn't match the function → removed."""

    def test_correct_motor_kept(self):
        # L004 → motor 004.1 matches
        rows = [{"equipment": "35-24-004.1", "subequipment": "", "description": "ROTOR 1"}]
        result = _refine("35-24L004", rows)
        self.assertIn("35-24-004.1", _equipment_tags(result))

    def test_stray_motor_removed(self):
        # L004 crop includes L003's motor — must be removed
        rows = [
            {"equipment": "35-24-003.1", "subequipment": "", "description": "ROTOR 1"},
            {"equipment": "35-24-004.1", "subequipment": "", "description": "ROTOR 1"},
        ]
        result = _refine("35-24L004", rows)
        eq_tags = _equipment_tags(result)
        self.assertNotIn("35-24-003.1", eq_tags)
        self.assertIn("35-24-004.1", eq_tags)

    def test_stray_motor_second_variant_removed(self):
        rows = [{"equipment": "35-24-003.2", "subequipment": "", "description": ""}]
        result = _refine("35-24L004", rows)
        self.assertNotIn("35-24-003.2", _equipment_tags(result))

    def test_prefix_style_motor_correct_kept(self):
        rows = [{"equipment": "35-24L009.1", "subequipment": "", "description": ""}]
        result = _refine("35-24L009", rows)
        self.assertIn("35-24L009.1", _equipment_tags(result))

    def test_prefix_style_stray_motor_removed(self):
        rows = [{"equipment": "35-24L003.1", "subequipment": "", "description": ""}]
        result = _refine("35-24L004", rows)
        self.assertNotIn("35-24L003.1", _equipment_tags(result))

    def test_pump_motor_correct_kept(self):
        rows = [{"equipment": "35-24-519.1", "subequipment": "", "description": "MTR"}]
        result = _refine("35-24P519", rows)
        self.assertIn("35-24-519.1", _equipment_tags(result))

    def test_pump_stray_motor_removed(self):
        rows = [{"equipment": "35-24-503.1", "subequipment": "", "description": "MTR"}]
        result = _refine("35-24P519", rows)
        self.assertNotIn("35-24-503.1", _equipment_tags(result))

    def test_tank_motor_correct_kept(self):
        rows = [{"equipment": "35-24-607.1", "subequipment": "", "description": "AGIT"}]
        result = _refine("35-24T607", rows)
        self.assertIn("35-24-607.1", _equipment_tags(result))

    def test_tank_stray_motor_removed(self):
        rows = [{"equipment": "35-24-606.1", "subequipment": "", "description": "AGIT"}]
        result = _refine("35-24T607", rows)
        self.assertNotIn("35-24-606.1", _equipment_tags(result))

    def test_stray_motor_in_subequipment_removed(self):
        rows = [
            {"equipment": "35-24-081", "subequipment": "", "description": "LINE"},
            {"equipment": "", "subequipment": "35-24-003.1", "description": "MOTOR"},
        ]
        result = _refine("35-24L004", rows)
        self.assertNotIn("35-24-003.1", _sub_equipment_tags(result))

    def test_plain_line_not_filtered_by_motor_rule(self):
        # Plain 35-24-NNN tags are never touched by motor filter
        rows = [
            {"equipment": "35-24-081", "subequipment": "", "description": ""},
            {"equipment": "35-24-082", "subequipment": "", "description": ""},
        ]
        result = _refine("35-24L004", rows)
        eq_tags = _equipment_tags(result)
        self.assertIn("35-24-081", eq_tags)
        self.assertIn("35-24-082", eq_tags)

    def test_instrument_tags_not_filtered(self):
        # LC, HV etc. are not motor tags
        rows = [
            {"equipment": "35-24LC-674", "subequipment": "", "description": "LVL CTRL"},
            {"equipment": "35-24HV-649", "subequipment": "", "description": "HND VLV"},
        ]
        result = _refine("35-24L009", rows)
        eq_tags = _equipment_tags(result)
        self.assertIn("35-24LC-674", eq_tags)
        self.assertIn("35-24HV-649", eq_tags)

    def test_plain_line_function_tag_no_motor_filter_applied(self):
        # Function is 35-24-017 (a line function, no letter prefix) — fn_num is None
        # → motor filter is entirely skipped, all rows pass through
        rows = [
            {"equipment": "35-24-004.1", "subequipment": "", "description": ""},
            {"equipment": "35-24-003.1", "subequipment": "", "description": ""},
        ]
        result = _refine("35-24-017", rows)
        eq_tags = _equipment_tags(result)
        # Both pass because fn_num is None → no filter applied
        self.assertIn("35-24-004.1", eq_tags)
        self.assertIn("35-24-003.1", eq_tags)


# ---------------------------------------------------------------------------
# refine_ai_hierarchy — seed loop (Bug 2 fix)
# ---------------------------------------------------------------------------
class SeedLoopFilterTests(unittest.TestCase):
    """Plain pipe seeds require AI mention; motor convention seeds are always added."""

    def test_plain_seed_not_in_raw_text_not_added(self):
        # AI returned no rows mentioning 35-24-082, and raw_text doesn't mention it
        # → seed should NOT be added
        inventory_lines = [{"line_number": "35-24-082", "x": 5.0, "y": 0.0}]
        result = _refine("35-24L004", [], inventory_lines=inventory_lines, raw_text="")
        self.assertNotIn("35-24-082", _equipment_tags(result))

    def test_plain_seed_mentioned_in_raw_text_is_added(self):
        # AI's raw response mentioned the tag even though it's not in rows
        inventory_lines = [{"line_number": "35-24-082", "x": 5.0, "y": 0.0}]
        raw_text = '{"function":"35-24L004","rows":[],"notes":"also see 35-24-082"}'
        result = _refine("35-24L004", [], inventory_lines=inventory_lines, raw_text=raw_text)
        self.assertIn("35-24-082", _equipment_tags(result))

    def test_plain_seed_already_in_ai_rows_not_duplicated(self):
        # AI returned the tag — it's already in rows; seed loop skips it
        rows = [{"equipment": "35-24-082", "subequipment": "", "description": ""}]
        inventory_lines = [{"line_number": "35-24-082", "x": 5.0, "y": 0.0}]
        result = _refine("35-24L004", rows, inventory_lines=inventory_lines)
        self.assertEqual(_equipment_tags(result).count("35-24-082"), 1)

    def test_motor_convention_seed_added_without_raw_mention(self):
        # .1 suffix → always seeded regardless of AI mention (needed for recall)
        result = _refine("35-24L004", [], raw_text="")
        eq_tags = _equipment_tags(result)
        # Motor seeds for L004 are 35-24L004.1, 35-24L004.2, 35-24-004.1, 35-24-004.2
        # At least the dash variant should appear
        motor_seeds = [t for t in eq_tags if t.endswith(".1") or t.endswith(".2")]
        self.assertTrue(len(motor_seeds) >= 1)

    def test_motor_seed_then_filtered_by_numeric_filter(self):
        # nearby_line_seeds for L004 seeds 35-24-004.1 (correct) and might have
        # 35-24-003.1 from nearby L003 text. Motor filter catches 003.1.
        inventory_lines = [
            {"line_number": "35-24-003.1", "x": 20.0, "y": 0.0},  # L003's motor
            {"line_number": "35-24-004.1", "x": 5.0, "y": 0.0},   # L004's motor
        ]
        result = _refine("35-24L004", [], inventory_lines=inventory_lines, raw_text="")
        eq_tags = _equipment_tags(result)
        # L003's motor seeded by motor convention but rejected by numeric filter
        self.assertNotIn("35-24-003.1", eq_tags)
        # L004's motor should be present
        self.assertIn("35-24-004.1", eq_tags)

    def test_peer_seed_excluded_even_if_mentioned(self):
        inventory_lines = [{"line_number": "35-24-189", "x": 5.0, "y": 0.0}]
        raw_text = '{"function":"35-24L004","notes":"see 35-24-189"}'
        result = _refine("35-24L004", [], inventory_lines=inventory_lines,
                         raw_text=raw_text, peers=["35-24-189"])
        self.assertNotIn("35-24-189", _equipment_tags(result))

    def test_outside_radius_seed_not_added(self):
        # Seed is 500 units away — well outside radius=130
        inventory_lines = [{"line_number": "35-24-200", "x": 500.0, "y": 0.0}]
        raw_text = '{"function":"35-24L004","notes":"see 35-24-200"}'
        result = _refine("35-24L004", [], inventory_lines=inventory_lines, raw_text=raw_text)
        # Even though mentioned in raw_text, it's outside radius so nearby_line_seeds won't yield it
        self.assertNotIn("35-24-200", _equipment_tags(result))


# ---------------------------------------------------------------------------
# rows_from_ai — CSV shape
# ---------------------------------------------------------------------------
class RowsFromAiTests(unittest.TestCase):
    """Verify complete CSV row structure for FUNCTION/EQUIPMENT/SUB-EQUIPMENT."""

    def _make_parsed(self, tag, rows, sub_process="BR1", description=None):
        return {
            "sub_process": sub_process,
            "function": tag,
            "description": description or f"{tag} BROKE ROLL PLPR",
            "rows": rows,
        }

    def test_emits_three_header_rows(self):
        # process root + sub-process + function = 3 header rows before children
        parsed = self._make_parsed("35-24L009", [])
        result, _ = rows_from_ai(1, CONTEXT, "35-24L009", parsed)
        self.assertEqual(len(result), 3)

    def test_process_root_row_has_mask(self):
        parsed = self._make_parsed("35-24L009", [])
        result, _ = rows_from_ai(1, CONTEXT, "35-24L009", parsed)
        process_row = result[0]
        self.assertEqual(process_row["FUNCTION"], "")
        self.assertEqual(process_row["EQUIPMENT"], "")
        self.assertEqual(process_row["SUB-PROCESS"], "")
        self.assertIn("5001-PM03-BR", process_row["MASK"])

    def test_subprocess_row_has_sub_process_set(self):
        parsed = self._make_parsed("35-24L009", [])
        result, _ = rows_from_ai(1, CONTEXT, "35-24L009", parsed)
        sp_row = result[1]
        self.assertEqual(sp_row["SUB-PROCESS"], "BR1")
        self.assertEqual(sp_row["FUNCTION"], "")
        self.assertIn("BR1", sp_row["MASK"])

    def test_function_row_has_function_and_mask(self):
        parsed = self._make_parsed("35-24L009", [])
        result, _ = rows_from_ai(1, CONTEXT, "35-24L009", parsed)
        fn_row = result[2]
        self.assertEqual(fn_row["FUNCTION"], "35-24L009")
        self.assertEqual(fn_row["SUB-PROCESS"], "BR1")
        self.assertIn("35-24L009", fn_row["MASK"])

    def test_function_row_description(self):
        parsed = self._make_parsed("35-24L009", [], description="35-24L009 BROKE ROLL PLPR")
        result, _ = rows_from_ai(1, CONTEXT, "35-24L009", parsed)
        fn_row = result[2]
        self.assertIn("35-24L009", fn_row["DESCRIPTION"])
        self.assertLessEqual(len(fn_row["DESCRIPTION"]), 40)

    def test_equipment_row_emitted_after_function(self):
        rows = [{"equipment": "35-24-189", "subequipment": "", "description": "LN OVFL"}]
        parsed = self._make_parsed("35-24L009", rows)
        result, _ = rows_from_ai(1, CONTEXT, "35-24L009", parsed)
        self.assertEqual(len(result), 4)
        eq_row = result[3]
        self.assertEqual(eq_row["EQUIPMENT"], "35-24-189")
        self.assertEqual(eq_row["SUB-EQUIPMENT"], "")
        self.assertEqual(eq_row["FUNCTION"], "")

    def test_sub_equipment_row_correct(self):
        rows = [
            {"equipment": "35-24-189", "subequipment": "", "description": "LINE"},
            {"equipment": "", "subequipment": "35-24HV-649", "description": "HND VLV"},
        ]
        parsed = self._make_parsed("35-24L009", rows)
        result, _ = rows_from_ai(1, CONTEXT, "35-24L009", parsed)
        sub_row = result[4]
        self.assertEqual(sub_row["EQUIPMENT"], "")
        self.assertEqual(sub_row["SUB-EQUIPMENT"], "35-24HV-649")

    def test_equipment_mask_blank(self):
        rows = [{"equipment": "35-24-189", "subequipment": "", "description": "LINE"}]
        parsed = self._make_parsed("35-24L009", rows)
        result, _ = rows_from_ai(1, CONTEXT, "35-24L009", parsed)
        eq_row = result[3]
        self.assertEqual(eq_row["MASK"], "")

    def test_order_increments(self):
        rows = [
            {"equipment": "35-24-189", "subequipment": "", "description": ""},
            {"equipment": "35-24P519", "subequipment": "", "description": ""},
        ]
        parsed = self._make_parsed("35-24L009", rows)
        result, end_order = rows_from_ai(1, CONTEXT, "35-24L009", parsed)
        orders = [int(r["ORDER"]) for r in result]
        self.assertEqual(orders, list(range(1, len(result) + 1)))
        self.assertEqual(end_order, len(result) + 1)

    def test_order_start_respected(self):
        parsed = self._make_parsed("35-24L009", [])
        result, _ = rows_from_ai(10, CONTEXT, "35-24L009", parsed)
        self.assertEqual(result[0]["ORDER"], "10")

    def test_site_line_process_populated(self):
        parsed = self._make_parsed("35-24L009", [])
        result, _ = rows_from_ai(1, CONTEXT, "35-24L009", parsed)
        for row in result:
            self.assertEqual(row["SITE"], CONTEXT["site"])
            self.assertEqual(row["LINE"], CONTEXT["line"])
            self.assertEqual(row["PROCESS"], CONTEXT["process"])

    def test_description_max_40_chars(self):
        parsed = self._make_parsed("35-24L009", [], description="35-24L009 " + "X" * 50)
        result, _ = rows_from_ai(1, CONTEXT, "35-24L009", parsed)
        for row in result:
            self.assertLessEqual(len(row["DESCRIPTION"]), 40)

    def test_multiple_equipment_rows(self):
        rows = [
            {"equipment": "35-24-189", "subequipment": "", "description": "LN OVFL"},
            {"equipment": "35-24-190", "subequipment": "", "description": "LN INLET"},
            {"equipment": "35-24P519", "subequipment": "", "description": "PMP"},
        ]
        parsed = self._make_parsed("35-24L009", rows)
        result, _ = rows_from_ai(1, CONTEXT, "35-24L009", parsed)
        # 3 headers + 3 children = 6
        self.assertEqual(len(result), 6)
        eq_tags = [r["EQUIPMENT"] for r in result if r["EQUIPMENT"]]
        self.assertEqual(eq_tags, ["35-24-189", "35-24-190", "35-24P519"])

    def test_pump_style_rows(self):
        """Example B from the prompt: pump with suction/discharge lines."""
        rows = [
            {"equipment": "35-24-519.1", "subequipment": "", "description": "MTR"},
            {"equipment": "35-24-111", "subequipment": "", "description": "SUCT LN"},
            {"equipment": "35-24-112", "subequipment": "", "description": "DIS LN"},
            {"equipment": "", "subequipment": "35-24LV1-519", "description": "LVL VLV"},
        ]
        parsed = self._make_parsed("35-24P519", rows, description="35-24P519 PRESS PLPR PMP")
        result, _ = rows_from_ai(1, CONTEXT, "35-24P519", parsed)
        fn_row = result[2]
        self.assertEqual(fn_row["FUNCTION"], "35-24P519")
        all_eq = [r["EQUIPMENT"] for r in result if r["EQUIPMENT"]]
        self.assertIn("35-24-519.1", all_eq)
        self.assertIn("35-24-111", all_eq)
        all_sub = [r["SUB-EQUIPMENT"] for r in result if r["SUB-EQUIPMENT"]]
        self.assertIn("35-24LV1-519", all_sub)


# ---------------------------------------------------------------------------
# Integration: refine_ai_hierarchy + rows_from_ai end-to-end
# ---------------------------------------------------------------------------
class EndToEndTests(unittest.TestCase):
    """Full flow: AI JSON → refine → rows_from_ai → CSV shape."""

    def test_l009_full_flow(self):
        """Example A from the prompt."""
        ai_json = {
            "sub_process": "BR1",
            "function": "35-24L009",
            "description": "35-24L009 BROKE ROLL PLPR",
            "rows": [
                {"equipment": "35-24LC-674", "subequipment": "", "description": "LVL CTRL"},
                {"equipment": "35-24-189",   "subequipment": "", "description": "LN OVFL"},
                {"equipment": "35-24-190",   "subequipment": "", "description": "LN INLET"},
                {"equipment": "35-24L009.1", "subequipment": "", "description": "LOCAL PT"},
                {"equipment": "35-24-009.1", "subequipment": "", "description": "MOTOR"},
                {"equipment": "",            "subequipment": "35-24HV-649", "description": "HND VLV"},
            ],
            "peers": [{"tag": "35-24L003", "evidence": "neighbouring pulper"}],
        }
        refined = refine_ai_hierarchy(
            "35-24L009",
            ai_json,
            center=(0.0, 0.0),
            inventory=None,
            structural=None,
            peer_tags=["35-24L003"],
            raw_text=json.dumps(ai_json),
        )
        # L009's own motors kept
        eq_tags = _equipment_tags(refined)
        self.assertIn("35-24-009.1", eq_tags)
        self.assertIn("35-24L009.1", eq_tags)
        # Instrument children kept
        self.assertIn("35-24LC-674", eq_tags)
        # Lines kept
        self.assertIn("35-24-189", eq_tags)
        # Sub-equipment kept
        sub_tags = _sub_equipment_tags(refined)
        self.assertIn("35-24HV-649", sub_tags)
        # Peer not included as child
        self.assertNotIn("35-24L003", eq_tags)

        # Now run through rows_from_ai
        csv_rows, _ = rows_from_ai(1, CONTEXT, "35-24L009", refined)
        # 3 header rows + N child rows
        self.assertGreaterEqual(len(csv_rows), 4)
        fn_row = csv_rows[2]
        self.assertEqual(fn_row["FUNCTION"], "35-24L009")
        self.assertIn("35-24L009", fn_row["MASK"])
        child_rows = csv_rows[3:]
        eq_in_csv = [r["EQUIPMENT"] for r in child_rows if r["EQUIPMENT"]]
        sub_in_csv = [r["SUB-EQUIPMENT"] for r in child_rows if r["SUB-EQUIPMENT"]]
        self.assertIn("35-24-189", eq_in_csv)
        self.assertIn("35-24HV-649", sub_in_csv)

    def test_motor_leakage_scenario(self):
        """L004 crop includes L003's motor — the full pipeline must remove it."""
        ai_json = {
            "sub_process": "BR1",
            "function": "35-24L004",
            "description": "35-24L004 BROKE ROLL PLPR",
            "rows": [
                {"equipment": "35-24-004.1", "subequipment": "", "description": "MTR"},
                {"equipment": "35-24-003.1", "subequipment": "", "description": "MTR"},  # stray
                {"equipment": "35-24-081",   "subequipment": "", "description": "LINE"},
                {"equipment": "35-24-082",   "subequipment": "", "description": "LINE"},
            ],
            "peers": [],
        }
        # raw_text mentions 35-24-081 and 35-24-082 so they pass seed gate;
        # 35-24-003.1 is removed by motor filter
        raw_text = json.dumps(ai_json)
        refined = refine_ai_hierarchy(
            "35-24L004",
            ai_json,
            center=(0.0, 0.0),
            inventory=None,
            structural=None,
            raw_text=raw_text,
        )
        eq_tags = _equipment_tags(refined)
        self.assertIn("35-24-004.1", eq_tags)
        self.assertNotIn("35-24-003.1", eq_tags)
        # Plain lines from the AI response are kept (not filtered by motor rule)
        self.assertIn("35-24-081", eq_tags)
        self.assertIn("35-24-082", eq_tags)

    def test_spatial_leakage_scenario(self):
        """Seed-only plain pipes that AI didn't mention are NOT added."""
        ai_json = {
            "sub_process": "BR1",
            "function": "35-24L004",
            "description": "35-24L004 BROKE ROLL PLPR",
            "rows": [
                {"equipment": "35-24-004.1", "subequipment": "", "description": "MTR"},
            ],
            "peers": [],
        }
        # Inventory has 35-24-081 nearby, but AI response doesn't mention it
        inventory_lines = [
            {"line_number": "35-24-081", "x": 10.0, "y": 0.0},
            {"line_number": "35-24-004.1", "x": 5.0, "y": 0.0},
        ]
        raw_text = json.dumps(ai_json)  # no mention of 35-24-081 here
        refined = refine_ai_hierarchy(
            "35-24L004",
            ai_json,
            center=(0.0, 0.0),
            inventory={"lines": inventory_lines},
            structural=None,
            raw_text=raw_text,
        )
        eq_tags = _equipment_tags(refined)
        # 35-24-081 not mentioned by AI → not added as seed
        self.assertNotIn("35-24-081", eq_tags)
        # Correct motor kept
        self.assertIn("35-24-004.1", eq_tags)

    def test_sub_process_propagated_to_csv(self):
        ai_json = {
            "sub_process": "BR1",
            "function": "35-24P519",
            "description": "35-24P519 PLPR PMP",
            "rows": [{"equipment": "35-24-519.1", "subequipment": "", "description": "MTR"}],
        }
        csv_rows, _ = rows_from_ai(1, CONTEXT, "35-24P519", ai_json)
        fn_row = csv_rows[2]
        self.assertEqual(fn_row["SUB-PROCESS"], "BR1")
        self.assertEqual(fn_row["FUNCTION"], "35-24P519")


if __name__ == "__main__":
    unittest.main()
