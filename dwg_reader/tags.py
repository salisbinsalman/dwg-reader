"""Tag and line-number normalization shared across inventory, hierarchy, and export."""

from __future__ import annotations

import re
from typing import Any

LINE_NUMBER_RE = re.compile(
    r"^(?P<plant_area>\d{2}-\d{2})-(?P<line_seq>\d{3}(?:/\d+)?)(?:-(?P<line_type>[A-Z]+))?(?:-(?P<size>\d*))?-(?P<pipe_class>[A-Z0-9]+)$"
)
DN_RE = re.compile(r"^DN\d+$", re.IGNORECASE)
_SHORT_LINE_RE = re.compile(r"^(\d{2}-\d{2}-\d{2,4})(?:-[A-Z].*)?$")


def normalize_tag(tag: str) -> str:
    """Uppercase, strip spaces, and collapse full pipe-class strings to short line ids."""
    s = re.sub(r"\s+", "", tag or "").upper()
    m = _SHORT_LINE_RE.match(s)
    if m:
        return m.group(1)
    return s


def parse_line_number(text: str) -> dict[str, Any]:
    text = text.strip().upper()
    if DN_RE.match(text):
        return {
            "line_number": text,
            "parsed": True,
            "plant_area": None,
            "line_seq": None,
            "line_type": "DN_SIZE",
            "size": text[2:],
            "pipe_class": None,
        }
    m = LINE_NUMBER_RE.match(text)
    if not m:
        return {"line_number": text, "parsed": False}
    return {"line_number": text, "parsed": True, **m.groupdict()}
