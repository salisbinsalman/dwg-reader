#!/usr/bin/env python3
"""Package layout, CLI wrappers, and path resolution."""

from __future__ import annotations

import importlib
import unittest
from pathlib import Path

from dwg_reader.config import DEFAULT_MODEL_ID, HIERARCHY_PROMPT_FILE, LEGEND_PATH
from dwg_reader.paths import (
    PROMPTS_DIR,
    REPO_ROOT,
    STANDARDS_DIR,
    find_json,
    json_path,
    safe_name,
)


class PathTests(unittest.TestCase):
    def test_repo_root_contains_makefile_and_package(self) -> None:
        self.assertTrue((REPO_ROOT / "Makefile").is_file())
        self.assertTrue((REPO_ROOT / "dwg_reader" / "__init__.py").is_file())

    def test_standards_and_prompts_resolve_from_package_not_cwd(self) -> None:
        self.assertTrue((STANDARDS_DIR / "sml_object_types.json").is_file())
        self.assertTrue(PROMPTS_DIR.is_dir())
        self.assertTrue((PROMPTS_DIR / HIERARCHY_PROMPT_FILE).is_file())

    def test_legend_path_exists(self) -> None:
        self.assertEqual(LEGEND_PATH, STANDARDS_DIR / "legend.png")
        self.assertTrue(LEGEND_PATH.is_file())

    def test_safe_name_uses_stem(self) -> None:
        self.assertEqual(safe_name(Path("inputs/Broke System.dwg")), "Broke System")

    def test_find_json_prefers_jsons_dir(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            preferred = json_path(out, "x.json")
            preferred.write_text("{}", encoding="utf-8")
            (out / "x.json").write_text('{"legacy": true}', encoding="utf-8")
            found = find_json(out, "x.json")
            self.assertEqual(found, preferred)

    def test_find_json_falls_back_to_legacy_root(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            legacy = out / "x.json"
            legacy.write_text("{}", encoding="utf-8")
            found = find_json(out, "x.json")
            self.assertEqual(found, legacy)

    def test_default_model_id(self) -> None:
        self.assertTrue(DEFAULT_MODEL_ID.startswith("eu.anthropic."))

    def test_hierarchy_prompt_file_is_v8(self) -> None:
        self.assertEqual(HIERARCHY_PROMPT_FILE, "pid_hierarchy_gt_v8.md")


class CliWrapperTests(unittest.TestCase):
    MODULES = (
        "dwg_pure_dump",
        "dwg_pid_inventory",
        "dwg_pid_enrich",
        "dwg_pid_hierarchy_ai",
        "dwg_valve_classify",
        "run_hierarchy_orchestrator",
        "export_sap_floc",
        "export_sap_equipment",
        "eval_hierarchy_gt",
    )

    def test_wrappers_exist_at_repo_root(self) -> None:
        for name in self.MODULES:
            self.assertTrue((REPO_ROOT / f"{name}.py").is_file(), name)

    def test_package_modules_export_main(self) -> None:
        for name in self.MODULES:
            mod = importlib.import_module(f"dwg_reader.{name}")
            self.assertTrue(callable(mod.main), name)

    def test_hierarchy_ai_exports_run_hierarchy_for_tag(self) -> None:
        from dwg_reader.dwg_pid_hierarchy_ai import (
            run_hierarchy_for_tag,
            run_hierarchy_from_args,
        )

        self.assertTrue(callable(run_hierarchy_for_tag))
        self.assertTrue(callable(run_hierarchy_from_args))

    def test_valve_and_export_library_entrypoints(self) -> None:
        from dwg_reader.dwg_valve_classify import run_valve_classify
        from dwg_reader.export_sap_equipment import run_equipment_export
        from dwg_reader.export_sap_floc import run_floc_export

        self.assertTrue(callable(run_valve_classify))
        self.assertTrue(callable(run_equipment_export))
        self.assertTrue(callable(run_floc_export))

    def test_vision_module_is_legacy_shim(self) -> None:
        from dwg_reader.dwg_pid_hierarchy_vision import main as shim_main
        from dwg_reader.legacy.hierarchy_vision import main as legacy_main

        self.assertIs(shim_main, legacy_main)
        self.assertTrue((REPO_ROOT / "dwg_reader" / "legacy" / "hierarchy_vision.py").is_file())
        self.assertTrue((REPO_ROOT / "dwg_reader" / "ezdxf_parse.py").is_file())
        self.assertTrue((REPO_ROOT / "dwg_reader" / "pid_functions.py").is_file())


if __name__ == "__main__":
    unittest.main()
