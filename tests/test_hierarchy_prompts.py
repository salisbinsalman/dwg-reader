"""Core + per-standard hierarchy prompt assembly."""
from __future__ import annotations

import unittest

from dwg_reader.dwg_prompts import load_hierarchy_prompt, load_prompt


class HierarchyPromptTests(unittest.TestCase):
    def test_sml_has_valmet_examples_not_wu(self):
        text = load_hierarchy_prompt("valmet")
        self.assertIn("35-24P510", text)
        self.assertIn("STRICT JSON", text)
        self.assertNotIn("FUNCTION=WU12", text)

    def test_gor_has_ventil_example(self):
        text = load_hierarchy_prompt("gor")
        self.assertIn("WU12", text)
        self.assertIn("168V-522", text)
        self.assertIn("STRICT JSON", text)
        self.assertIn("Do **not** emit Valmet tags", text)

    def test_ksd_has_item_example(self):
        text = load_hierarchy_prompt("ksd")
        self.assertIn("122E-001", text)
        self.assertIn("KRETS", text)
        self.assertIn("STRICT JSON", text)

    def test_adapter_prefix(self):
        via_prefix = load_prompt("adapter:gor")
        via_helper = load_hierarchy_prompt("gor")
        self.assertEqual(via_prefix, via_helper)


class PlausibleHierarchyTagTests(unittest.TestCase):
    def test_valmet_and_tissue_shapes(self):
        from dwg_reader.dwg_pid_hierarchy_ai import is_plausible_hierarchy_tag

        self.assertTrue(is_plausible_hierarchy_tag("35-24L009", "35-24L009"))
        self.assertTrue(is_plausible_hierarchy_tag("35-24-189", "35-24L009"))
        self.assertTrue(is_plausible_hierarchy_tag("168L-521", "WU12"))
        self.assertTrue(is_plausible_hierarchy_tag("168V-521", "WU12"))
        self.assertTrue(is_plausible_hierarchy_tag("168P-410", "WU12"))
        self.assertTrue(is_plausible_hierarchy_tag("168-ST521", "WU12"))
        self.assertTrue(is_plausible_hierarchy_tag("168TC1", "WU12"))
        self.assertTrue(is_plausible_hierarchy_tag("122E-001", "122E-001"))
        self.assertTrue(is_plausible_hierarchy_tag("126LC-001", "126P-001"))
        self.assertFalse(is_plausible_hierarchy_tag("126LC-001", "122E-001"))
        self.assertFalse(is_plausible_hierarchy_tag("124L-003", "122E-001"))
        self.assertFalse(is_plausible_hierarchy_tag("122E-003-M2", "122E-003"))
        self.assertFalse(is_plausible_hierarchy_tag("200-96", "WU12"))
        self.assertFalse(is_plausible_hierarchy_tag("168TI", "WU12"))
        self.assertFalse(is_plausible_hierarchy_tag("168PI", "WU12"))


if __name__ == "__main__":
    unittest.main()
