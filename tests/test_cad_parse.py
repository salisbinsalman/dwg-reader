#!/usr/bin/env python3
"""Tests for split CAD parse and FUNCTION collectors."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dwg_reader.ezdxf_parse import (
    open_ezdxf_document,
    specialty_entities,
    text_entities,
    title_block_fields,
)
from dwg_reader.pid_functions import FunctionIndex, function_text_points, min_dist


class OpenEzdxfDocumentTests(unittest.TestCase):
    def test_rejects_unsupported_extension(self) -> None:
        doc, backend, err = open_ezdxf_document(Path("/tmp/not-a-drawing.txt"))
        self.assertIsNone(doc)
        self.assertEqual(backend, "")
        self.assertIn("Unsupported extension", err)

    def test_missing_dxf_returns_parse_error(self) -> None:
        missing = Path(tempfile.gettempdir()) / "dwg-reader-missing-no-such.dxf"
        if missing.exists():
            missing.unlink()
        doc, backend, err = open_ezdxf_document(missing)
        self.assertIsNone(doc)
        self.assertTrue("DXF parse failed" in err or "ezdxf import failed" in err)


class TextAndTitleHelpersTests(unittest.TestCase):
    def test_text_entities_keep_text_and_mtext_only(self) -> None:
        rows = text_entities(
            [
                {"type": "LINE", "handle": "1", "layer": "0", "geometry": {}},
                {
                    "type": "TEXT",
                    "handle": "2",
                    "layer": "P-TEXT",
                    "geometry": {"text": "35-24L009", "insert": [1, 2, 0], "height": 3},
                },
            ]
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["text"], "35-24L009")

    def test_title_block_fields_filter_known_keys(self) -> None:
        inserts = [
            {
                "name": "TITLE",
                "handle": "A",
                "layer": "0",
                "insert": [0, 0, 0],
                "attributes": [
                    {"tag": "TITLE1", "text": "Broke System"},
                    {"tag": "NOISE", "text": "x"},
                ],
            }
        ]
        fields = title_block_fields(inserts)
        self.assertEqual(len(fields), 1)
        self.assertEqual(fields[0]["fields"]["TITLE1"], "Broke System")

    def test_specialty_entities_match_type_substrings(self) -> None:
        found = specialty_entities(
            [
                {"type": "LINE"},
                {"type": "ACAD_PROXY_ENTITY"},
                {"type": "MLEADER"},
            ]
        )
        self.assertEqual([e["type"] for e in found], ["ACAD_PROXY_ENTITY", "MLEADER"])


class FunctionIndexTests(unittest.TestCase):
    def test_function_text_points_skips_empty_and_unplaced(self) -> None:
        pts = function_text_points(
            {
                "text_entities": [
                    {"text": "  ", "position": [1, 2, 0]},
                    {"text": "HI", "position": None},
                    {"text": "35-24L009", "position": [10.0, 20.0, 0], "layer": "P-TEXT"},
                ]
            }
        )
        self.assertEqual(len(pts), 1)
        self.assertEqual(pts[0]["norm"], "35-24L009")
        self.assertEqual(pts[0]["x"], 10.0)

    def test_upsert_keeps_lower_rank(self) -> None:
        bag = FunctionIndex()
        bag.upsert("35-24L009", {"kind": "equipment", "category": "tanks"}, 0)
        bag.upsert("35-24L009", {"kind": "equipment", "category": "pumps"}, 2)
        rows = bag.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["category"], "tanks")
        self.assertNotIn("category_rank", rows[0])
        self.assertEqual(rows[0]["source"], "cad")

    def test_upsert_skips_agitator_function_tags(self) -> None:
        bag = FunctionIndex()
        bag.upsert("35-24L401", {"kind": "equipment"}, 0)
        self.assertEqual(bag.rows(), [])

    def test_min_dist_default_when_empty(self) -> None:
        self.assertEqual(min_dist(0, 0, []), 9999.0)


class OdafcPatchTests(unittest.TestCase):
    def test_dylib_is_bound_on_successful_import_path(self) -> None:
        import inspect

        from dwg_reader.dwg_pure_dump import _patch_odafc_no_focus

        src = inspect.getsource(_patch_odafc_no_focus)
        self.assertIn("    _dylib = REPO_ROOT", src)
        self.assertNotIn("        _dylib = REPO_ROOT", src)

    def test_patched_runner_dylib_fallback_does_not_raise(self) -> None:
        try:
            import ezdxf.addons.odafc as odafc
        except ImportError:
            self.skipTest("ezdxf odafc missing")
        from dwg_reader.dwg_pure_dump import _patch_odafc_no_focus

        _patch_odafc_no_focus()
        result = odafc._run_with_no_gui("Darwin", "/usr/bin/true", [])
        self.assertEqual(result.returncode, 0)


class MakefileHierarchyTests(unittest.TestCase):
    def test_make_hierarchy_aliases_hierarchy_ai(self) -> None:
        makefile = Path(__file__).resolve().parents[1] / "Makefile"
        text = makefile.read_text(encoding="utf-8")
        self.assertIn("hierarchy: hierarchy-ai", text)
        self.assertNotIn("dwg_pid_hierarchy_vision.py --input", text.split("hierarchy-ai:")[0])

    def test_prompt_file_default_is_v8(self) -> None:
        makefile = Path(__file__).resolve().parents[1] / "Makefile"
        text = makefile.read_text(encoding="utf-8")
        self.assertIn("PROMPT_FILE ?= pid_hierarchy_gt_v8.md", text)


if __name__ == "__main__":
    unittest.main()
