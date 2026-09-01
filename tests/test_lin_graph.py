#!/usr/bin/env python3
"""R27/B04: LIN_FROM / LIN_TO XDATA graph from structural dump fixtures."""

from __future__ import annotations

import unittest

from dwg_reader.dwg_lin_graph import neighbors, parse_lin_from_to, valve_line_collision_tags
from dwg_reader.dwg_pid_inventory import build_inventory


class LinFromToParseTests(unittest.TestCase):
    def test_parses_ezdxf_tuple_strings(self) -> None:
        structural = {
            "eed_xdata_dump": [
                {
                    "handle": "A1",
                    "layer": "P-PIPE",
                    "xdata": {
                        "PCAD": [
                            "(1000, 'LIN_FROM')",
                            "(1000, '35-24L005')",
                            "(1000, 'LIN_TO')",
                            "(1000, '35-24-137')",
                        ]
                    },
                }
            ]
        }
        edges = parse_lin_from_to(structural)
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]["from"], "35-24L005")
        self.assertEqual(edges[0]["to"], "35-24-137")
        self.assertIn("35-24L005", neighbors(edges, "35-24-137"))

    def test_collision_is_intersection_only(self) -> None:
        structural = {
            "text_entities": [
                {"layer": "P-VALVEPOS", "text": "35-24-137"},
                {"layer": "P-LINEPOS", "text": "35-24-137"},
                {"layer": "P-VALVEPOS", "text": "35-24-096"},
            ]
        }
        hits = valve_line_collision_tags(structural=structural, inventory={})
        self.assertEqual(hits, {"35-24-137"})

    def test_inventory_stores_lin_from_to(self) -> None:
        structural = {
            "inserts": [],
            "text_entities": [
                {"handle": "T1", "layer": "P-VALVEPOS", "text": "35-24-137", "position": [1, 2, 0]},
                {"handle": "T2", "layer": "P-LINEPOS", "text": "35-24-137", "position": [3, 4, 0]},
            ],
            "entities": [],
            "eed_xdata_dump": [
                {
                    "handle": "E1",
                    "layer": "0",
                    "xdata": {
                        "PCAD": [
                            "(1000, 'LIN_FROM')",
                            "(1000, '35-24P519')",
                            "(1000, 'LIN_TO')",
                            "(1000, '35-24L009')",
                        ]
                    },
                }
            ],
        }
        inv = build_inventory(structural, dwg_stem="Broke System")
        self.assertTrue(inv.get("lin_from_to"))
        self.assertEqual(inv["lin_from_to"][0]["from"], "35-24P519")
        self.assertIn("35-24-137", inv.get("valve_line_collisions") or [])

    def test_parses_taky_pos_schema_values(self) -> None:
        """Broke dump: LIN_FROM/LIN_TO are TAKY field names; tags live in POS-INFO."""
        structural = {
            "eed_xdata_dump": [
                {
                    "handle": "365DE",
                    "layer": "P-LINEPOS",
                    "xdata": {
                        "PCAD-TAKY-INFO": [
                            "(1000, 'LIOSASTO')",
                            "(1000, 'LIN_FROM')",
                            "(1000, 'LIN_TO')",
                        ],
                        "PCAD-POS-INFO": [
                            "(1000, '1470296')",
                            "(1000, '35')",
                            "(1000, '35-24L005 REEL PULPER ')",
                            "(1000, '35-24P506 REEL PULPER PUMP ')",
                        ],
                    },
                }
            ]
        }
        edges = parse_lin_from_to(structural)
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]["from"], "35-24L005")
        self.assertEqual(edges[0]["to"], "35-24P506")


if __name__ == "__main__":
    unittest.main()
