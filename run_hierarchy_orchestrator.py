#!/usr/bin/env python3
"""CLI wrapper — implementation lives in `dwg_reader.run_hierarchy_orchestrator`."""
from __future__ import annotations

import dwg_reader.dwg_warn as dwg_warn  # noqa: F401

from dwg_reader.run_hierarchy_orchestrator import main

if __name__ == "__main__":
    raise SystemExit(main())
