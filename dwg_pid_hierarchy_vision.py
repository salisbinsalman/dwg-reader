#!/usr/bin/env python3
"""CLI wrapper — legacy CAD-graph hierarchy (not the default pipeline)."""
from __future__ import annotations

import dwg_reader.dwg_warn as dwg_warn  # noqa: F401

from dwg_reader.legacy.hierarchy_vision import main

if __name__ == "__main__":
    raise SystemExit(main())
