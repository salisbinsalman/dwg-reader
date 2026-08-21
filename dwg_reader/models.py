"""Shared column lists for hierarchy CSV rows."""

from __future__ import annotations

# GT scoring columns (eval workbook). DESCRIPTION is a deliverable extra.
GT_COLUMNS: list[str] = [
    "SUB-PROCESS",
    "FUNCTION",
    "EQUIPMENT",
    "SUB-EQUIPMENT",
    "MASK",
]

HIERARCHY_COLUMNS: list[str] = [*GT_COLUMNS, "DESCRIPTION"]

CSV_COLUMNS: list[str] = [
    "ORDER",
    "SITE",
    "LINE",
    "PROCESS",
    *HIERARCHY_COLUMNS,
]
