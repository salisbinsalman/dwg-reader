#!/usr/bin/env python3
"""Tests for dwg_reader.logutil."""

from __future__ import annotations

import logging
import unittest

from dwg_reader.logutil import configure_logging, dxf_probe_failed, get_logger


class LogutilTests(unittest.TestCase):
    def tearDown(self) -> None:
        root = logging.getLogger("dwg_reader")
        root.handlers.clear()
        root.setLevel(logging.WARNING)
        root.propagate = False
    def test_get_logger_nests_under_package(self) -> None:
        log = get_logger("orch")
        self.assertEqual(log.name, "dwg_reader.orch")

    def test_get_logger_accepts_dunder_name(self) -> None:
        log = get_logger("dwg_reader.dwg_pure_dump")
        self.assertEqual(log.name, "dwg_reader.dwg_pure_dump")

    def test_configure_logging_idempotent(self) -> None:
        a = configure_logging("INFO")
        n = len(a.handlers)
        b = configure_logging("DEBUG")
        self.assertIs(a, b)
        self.assertEqual(len(b.handlers), n)
        self.assertEqual(b.level, logging.DEBUG)
        configure_logging("INFO")

    def test_dxf_probe_failed_does_not_raise(self) -> None:
        dxf_probe_failed(ValueError("missing attr"), "color")


if __name__ == "__main__":
    unittest.main()
