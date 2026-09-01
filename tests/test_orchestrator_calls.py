#!/usr/bin/env python3
"""Orchestrator calls library functions instead of subprocess CLIs."""

from __future__ import annotations

import inspect
import unittest
from pathlib import Path
from unittest.mock import patch

from dwg_reader.run_hierarchy_orchestrator import (
    _is_gor_inventory,
    main,
    read_hierarchy_csv,
    run_hierarchy_for_tag,
    write_hierarchy_csv,
)


class OrchestratorLibraryCallTests(unittest.TestCase):
    def test_run_hierarchy_for_tag_source_does_not_use_subprocess(self) -> None:
        src = inspect.getsource(run_hierarchy_for_tag)
        self.assertNotIn("subprocess", src)
        self.assertIn("_run_hierarchy_for_tag", src)

    def test_run_hierarchy_for_tag_delegates_to_hierarchy_ai(self) -> None:
        with patch(
            "dwg_reader.run_hierarchy_orchestrator._run_hierarchy_for_tag",
            return_value=7,
        ) as mocked:
            rc = run_hierarchy_for_tag(
                tag="35-24L009",
                input_path=Path("inputs/Broke System.dwg"),
                out_dir=Path("outputs"),
                model_id="model",
                region="eu-west-2",
                prompt_file="pid_hierarchy_gt_v8.md",
                inventory_json=Path("outputs/jsons/x.pid_inventory.json"),
                per_tag_csv=Path("outputs/a.csv"),
                per_tag_json=Path("outputs/a.json"),
                reuse_shots=True,
                no_clean_prev=True,
                aws_profile="foundrydev",
            )
        self.assertEqual(rc, 7)
        mocked.assert_called_once()
        kwargs = mocked.call_args.kwargs
        self.assertEqual(kwargs["tag"], "35-24L009")
        self.assertTrue(kwargs["reuse_shots"])
        self.assertTrue(kwargs["no_clean_prev"])
        self.assertEqual(kwargs["aws_profile"], "foundrydev")

    def test_orchestrator_module_does_not_import_subprocess(self) -> None:
        import dwg_reader.run_hierarchy_orchestrator as orch

        self.assertFalse(hasattr(orch, "subprocess"))

    def test_write_read_hierarchy_csv_via_shared_io(self) -> None:
        import tempfile

        rows = [
            {
                "SUB-PROCESS": "BR1",
                "FUNCTION": "35-24L009",
                "EQUIPMENT": "",
                "SUB-EQUIPMENT": "",
                "MASK": "x",
                "DESCRIPTION": "PULPER",
            }
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "h.csv"
            write_hierarchy_csv(path, rows)
            loaded = read_hierarchy_csv(path)
            self.assertEqual(loaded[0]["FUNCTION"], "35-24L009")
            self.assertEqual(loaded[0]["DESCRIPTION"], "PULPER")

    def test_is_gor_inventory_missing_file_is_false(self) -> None:
        self.assertFalse(_is_gor_inventory(Path("/tmp/no-such-inventory.json")))

    def test_is_gor_inventory_wu_function(self) -> None:
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "inv.json"
            path.write_text(
                json.dumps({"functions": [{"function": "WU12"}]}), encoding="utf-8"
            )
            self.assertTrue(_is_gor_inventory(path))

    def test_is_gor_inventory_valmet_functions_false(self) -> None:
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "inv.json"
            path.write_text(
                json.dumps(
                    {
                        "functions": [{"function": "35-24L009"}],
                        "valves": [],
                        "lines": [],
                    }
                ),
                encoding="utf-8",
            )
            self.assertFalse(_is_gor_inventory(path))

    def test_valve_classify_runs_for_all_standards_without_tipo_patch(self) -> None:
        src = inspect.getsource(main)
        self.assertIn("run_valve_classify", src)
        self.assertIn("all standards", src)
        self.assertNotIn("_patch_gor_valve_types", src)
        self.assertNotIn("gor tipo mapping", src.lower())
        self.assertNotIn("is_gor", src)
        self.assertNotIn("is_valmet", src)

    def test_orchestrator_scores_after_sanitize(self) -> None:
        src = inspect.getsource(main)
        self.assertIn("per_function_pre_sanitize", src)
        self.assertIn("post_sanitize", src)
        self.assertIn("_seed_childless_functions", src)

    def test_valve_and_agitator_vision_always_run(self) -> None:
        src = inspect.getsource(main)
        self.assertIn("run_valve_classify", src)
        self.assertIn("run_agitator_bind", src)
        self.assertIn("skip_existing=False", src)
        self.assertNotIn("skip_existing=bool(args.skip_existing)", src)


if __name__ == "__main__":
    unittest.main()
