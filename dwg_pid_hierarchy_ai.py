#!/usr/bin/env python3
"""CLI wrapper — implementation lives in `dwg_reader.dwg_pid_hierarchy_ai`."""
from __future__ import annotations

import dwg_reader.dwg_warn as dwg_warn  # noqa: F401

from dwg_reader.dwg_pid_hierarchy_ai import main

if __name__ == "__main__":
    raise SystemExit(main())
