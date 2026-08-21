#!/usr/bin/env python3
"""
FLOC hierarchy standards for Shotton Mill SAP upload.

Loads standards/sml_floc_structure.json (generated from SML SAP FLOC Structure V3.xlsx)
and provides lookup helpers for line, process, and sub-process codes.

Lookup functions return empty string on miss rather than raising — callers can then
decide whether to fall back to the value already in floc_context_map.json.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Dict

from dwg_reader.paths import STANDARDS_DIR

_STANDARDS_PATH = STANDARDS_DIR / "sml_floc_structure.json"


@lru_cache(maxsize=1)
def _load(path: str) -> Dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _data() -> Dict:
    return _load(str(_STANDARDS_PATH.resolve()))


def lookup_line(code: str) -> str:
    """Return official line name for a Level 2 code ('PM03' → 'PAPER MACHINE 3')."""
    return _data()["lines"].get(str(code or "").strip().upper(), "")


def lookup_process(code: str) -> str:
    """Return official process name for a Level 3 code ('BR' → 'BROKE SYSTEM').

    Returns empty string for unnamed but valid 2-letter codes — all 2-letter
    alphanumeric combinations are acceptable in SAP; unnamed ones simply have no
    official description in the SML standard yet.
    """
    return _data()["processes"].get(str(code or "").strip().upper(), "")


def lookup_sub_process(code: str) -> str:
    """Return registered sub-process name for a Level 4 code ('BHS' → 'BALE HANDLING').

    Returns empty string for codes not yet registered in FLOC V3 — these are new
    sub-process nodes being created during the SAP implementation.
    """
    return _data()["sub_processes"].get(str(code or "").strip().upper(), "")


def is_valid_line(code: str) -> bool:
    """True if code is a registered Level 2 line code."""
    return str(code or "").strip().upper() in _data()["lines"]
