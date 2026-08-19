#!/usr/bin/env python3
"""User-requested valve regression cases and accuracy gate."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REASONING_CSV = ROOT / "outputs" / "Broke System.valve_reasoning.csv"

# User-provided tags include two typos; map to the drawing namespace.
TAG_ALIASES = {
    "35-32-1105": "35-24-1105",
    "34-24-215": "35-24-215",
}

EXPECTED_TYPES = {
    "35-24-1105": {"NC", "FLS"},
    "35-24-093": {"DRN"},
    "35-24-001": {"HV"},
    "35-24-215": {"NC", "FLS"},
    "35-24-108": {"NC", "FLS"},
    "35-24LV1-560": {"AV"},
    "35-24-137": {"DRN", "NC"},
    "35-24-107": {"DRN", "NC"},
    "35-24-110": {"DRN", "NC"},
    "35-24-230": {"HV"},
    "35-24-105": {"DRN", "NC"},
    "35-24HV-618": {"AV"},
    "35-24-217": {"DRN", "NC"},
    "35-24-121": {"DRN", "NC"},
    "35-24-123": {"DRN", "NC"},
    "35-24-191": {"DRN"},
    "35-24-192": {"DRN"},
    "35-24XV-665": {"DRN"},
    "35-24-198": {"NC", "FLS"},
    "35-24-199": {"NC"},
    "35-24-196": {"HV"},
}


def _norm_tag(tag: str) -> str:
    return TAG_ALIASES.get(str(tag or "").strip().upper(), str(tag or "").strip().upper())


class UserValveCasesTests(unittest.TestCase):
    def _rows(self) -> dict[str, dict[str, str]]:
        if not REASONING_CSV.exists():
            self.skipTest(f"Missing {REASONING_CSV}; run valve classify + equipment export first")
        with REASONING_CSV.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        return {str(r.get("EQUNR") or "").strip().upper(): r for r in rows}

    def test_each_case_expected_tokens(self) -> None:
        rows = self._rows()
        for tag, expected in EXPECTED_TYPES.items():
            with self.subTest(tag=tag):
                self.assertIn(tag, rows, f"{tag} missing from valve_reasoning.csv")
                got = set(str(rows[tag].get("TYPE") or "").upper().split())
                self.assertTrue(
                    expected.issubset(got),
                    f"{tag}: expected tokens {sorted(expected)} within TYPE={rows[tag].get('TYPE')!r}",
                )

    def test_user_cases_accuracy_at_least_80_percent(self) -> None:
        rows = self._rows()
        total = 0
        hit = 0
        misses: list[str] = []
        for tag, expected in EXPECTED_TYPES.items():
            total += 1
            got = set(str(rows.get(tag, {}).get("TYPE") or "").upper().split())
            ok = expected.issubset(got)
            if ok:
                hit += 1
            else:
                misses.append(f"{tag}: got={sorted(got)} expected={sorted(expected)}")
        acc = (hit / total) if total else 0.0
        self.assertGreaterEqual(
            acc,
            0.80,
            f"User-case accuracy {acc*100:.1f}% < 80%. Misses: {'; '.join(misses)}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
