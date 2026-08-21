#!/usr/bin/env python3
"""
CAD ecosystem detection for the SML DWG pipeline.

Three distinct CAD ecosystems exist across the 84 Shotton Mill DWGs:
  - valmet : Valmet PS-21 / PM3 (STOD*, PCSG*, RAU*)
  - gor    : GOR S.r.l. Italian ecosystem (GORA*, GORB*)
  - ksd    : KSD / Andritz (KSDM*)

GOR and KSD both follow the Tissue KSDM160104 numbering standard (124P-001 format),
so they share one standard JSON. Valmet follows the SML PS-21 standard (35-24P518 format).

Detection priority: explicit "ecosystem" key in floc_context → DWG stem prefix → default (valmet).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

_STANDARDS_DIR = Path(__file__).parent / "standards"

# Ordered longest-first so that prefix matching is unambiguous.
_STEM_PREFIX_TO_ECOSYSTEM: tuple[tuple[str, str], ...] = (
    ("GORA", "gor"),
    ("GORB", "gor"),
    ("KSDM", "ksd"),
    ("STOD", "valmet"),
    ("PCSG", "valmet"),
    ("RAU",  "valmet"),
)

_ECOSYSTEM_TO_STANDARD: Dict[str, str] = {
    "valmet": "valmet_ps21",
    "gor":    "tissue_ksdm160104",
    "ksd":    "tissue_ksdm160104",
}


@lru_cache(maxsize=8)
def _load_standard(standard_id: str) -> dict:
    p = _STANDARDS_DIR / f"{standard_id}.json"
    with p.open(encoding="utf-8") as fh:
        return json.load(fh)


@dataclass
class Ecosystem:
    """Resolved CAD ecosystem with its loaded naming-standard rules."""

    name: str        # "valmet" | "gor" | "ksd" | "unknown"
    standard_id: str  # "valmet_ps21" | "tissue_ksdm160104"
    standard: dict   # parsed standard JSON

    @property
    def is_tissue(self) -> bool:
        """True for GOR and KSD — both use the Tissue KSDM160104 naming standard."""
        return self.standard_id == "tissue_ksdm160104"

    @property
    def is_valmet(self) -> bool:
        return self.standard_id == "valmet_ps21"


def detect(dwg_stem: str = "", *, ctx: Optional[Dict] = None) -> Ecosystem:
    """Detect and return the Ecosystem for a DWG.

    dwg_stem – filename stem or full path; the stem is extracted automatically.
    ctx      – optional floc_context dict; an explicit "ecosystem" key takes
               precedence over stem-based detection.
    """
    # Explicit ecosystem in context overrides stem detection.
    if ctx:
        explicit = str(ctx.get("ecosystem") or "").strip().lower()
        if explicit in _ECOSYSTEM_TO_STANDARD:
            std_id = _ECOSYSTEM_TO_STANDARD[explicit]
            return Ecosystem(name=explicit, standard_id=std_id, standard=_load_standard(std_id))

    # Derive from the DWG stem.
    stem = Path(dwg_stem).stem.upper() if dwg_stem else ""
    name = "valmet"  # default — Broke System and unlisted stems fall here
    for prefix, eco in _STEM_PREFIX_TO_ECOSYSTEM:
        if stem.startswith(prefix):
            name = eco
            break

    std_id = _ECOSYSTEM_TO_STANDARD.get(name, "valmet_ps21")
    return Ecosystem(name=name, standard_id=std_id, standard=_load_standard(std_id))
