#!/usr/bin/env python3
"""
CAD ecosystem detection for the SML DWG pipeline.

Three distinct CAD ecosystems exist across the 84 Shotton Mill DWGs:
  - valmet : Valmet PS-21 / PM3 (STOD*, PCSG*, RAU*)
  - gor    : GOR S.r.l. Italian CAD (GORA*, GORB*)
  - ksd    : KSD / Andritz CAD (KSDM*)

GOR and KSD share KSDM160104 *numbering* (xyyz-aaa) but not CAD. Each has
its own standard JSON and adapter. Valmet follows SML PS-21 (35-24P518).

Detection priority:
  explicit ctx['ecosystem']
  → known DWG stem prefix (GORA/GORB/KSDM/STOD/PCSG/RAU)
  → KSD structural fingerprints (PS-EQUIP, KRETS, HAND-VALVE)
  → GOR structural / inventory signals
  → default valmet (Broke System and unlisted stems)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from dwg_reader.paths import STANDARDS_DIR

_STANDARDS_DIR = STANDARDS_DIR

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
    "gor":    "gor_fiorentini",
    "ksd":    "ksd_andritz",
}

_KSD_LAYERS = frozenset({
    "PS-EQUIP",
    "HAND-VALVE",
    "INSTR-VALVE",
    "TXT-HAND-VALVE",
    "TXT-INST-VALVE",
})
_GOR_LAYERS = frozenset({
    "1-VALVE TEXT GOR",
    "1-TAG AND INSTRUMENTS GOR",
    "1-EQUIPMENT GOR",
    "Revison 03",
})


@lru_cache(maxsize=8)
def _load_standard(standard_id: str) -> dict:
    p = _STANDARDS_DIR / f"{standard_id}.json"
    with p.open(encoding="utf-8") as fh:
        return json.load(fh)


def _eco(name: str) -> "Ecosystem":
    std_id = _ECOSYSTEM_TO_STANDARD[name]
    return Ecosystem(name=name, standard_id=std_id, standard=_load_standard(std_id))


@dataclass
class Ecosystem:
    """Resolved CAD ecosystem with its loaded naming-standard rules."""

    name: str        # "valmet" | "gor" | "ksd"
    standard_id: str  # "valmet_ps21" | "gor_fiorentini" | "ksd_andritz"
    standard: dict   # parsed standard JSON

    @property
    def is_tissue(self) -> bool:
        """True for GOR and KSD — both follow KSDM160104 numbering conventions."""
        return self.name in ("gor", "ksd")

    @property
    def is_valmet(self) -> bool:
        return self.standard_id == "valmet_ps21"

    @property
    def is_gor(self) -> bool:
        return self.name == "gor"

    @property
    def is_ksd(self) -> bool:
        return self.name == "ksd"

    @property
    def adapter(self) -> "Any":
        """Return the adapter instance for this ecosystem.

        Import is deferred to avoid a circular-import cycle
        (adapters → dwg_floc_context → dwg_ecosystem).
        """
        from dwg_reader.adapters import adapter_for  # noqa: PLC0415
        return adapter_for(self.name)


def _attr_tags(ins: Dict[str, Any]) -> set[str]:
    tags: set[str] = set()
    for a in ins.get("attributes") or []:
        if isinstance(a, dict):
            raw = a.get("tag") or a.get("name") or ""
            if raw:
                tags.add(str(raw).upper())
    return tags


def is_ksd_structural(structural: Dict[str, Any] | None) -> bool:
    """True when raw CAD dump is Andritz KSD (not GOR Pipeno-with-PIPEID)."""
    if not structural:
        return False
    inserts = structural.get("inserts") or []
    layers = {ins.get("layer") for ins in inserts}
    if layers & _KSD_LAYERS:
        return True
    # KRETS is unique to KSD. PIPEID is not — GOR Pipeno also has it.
    for ins in inserts:
        tags = _attr_tags(ins)
        if "KRETS" in tags:
            return True
        if "ITEM" in tags and ("BENÄMNING" in tags or "BENAMNING" in tags):
            return True
    return False


def is_gor_structural(structural: Dict[str, Any] | None) -> bool:
    """True when raw CAD dump uses GOR Italian layers or TAG VALVOLA blocks."""
    if not structural:
        return False
    inserts = structural.get("inserts") or []
    layers = {ins.get("layer") for ins in inserts}
    if layers & _GOR_LAYERS:
        return True
    texts = structural.get("text_entities") or []
    if {t.get("layer") for t in texts} & _GOR_LAYERS:
        return True
    return any(str(ins.get("name") or "").upper() == "TAG VALVOLA" for ins in inserts)


def is_ksd_inventory(inventory: Dict[str, Any] | None) -> bool:
    """True when inventory JSON was produced from a KSD drawing."""
    if not inventory:
        return False
    if any(ln.get("source") == "ksd_pipe_id" for ln in (inventory.get("lines") or [])):
        return True
    for cat in ("process_equipment", "pumps", "tanks", "agitators", "valves", "instruments"):
        for row in inventory.get(cat) or []:
            layer = str(row.get("layer") or "")
            if layer in _KSD_LAYERS or layer == "PS-EQUIP":
                return True
            if row.get("krets") or row.get("item") or row.get("posnr_raw"):
                return True
    return False


def is_gor_inventory(inventory: Dict[str, Any] | None) -> bool:
    """True when inventory JSON was produced from a GOR drawing (Code 03/13/14)."""
    if not inventory:
        return False
    if any(ln.get("source") == "gor_pipe_id" for ln in (inventory.get("lines") or [])):
        return True
    if any(str(v.get("block_name") or "").upper() == "TAG VALVOLA" for v in (inventory.get("valves") or [])):
        return True
    if any(str(v.get("layer") or "") == "1-VALVE TEXT GOR" for v in (inventory.get("valves") or [])):
        return True
    return any(
        str(fn.get("function") or "").upper().startswith("WU")
        and str(fn.get("function") or "")[2:].isdigit()
        for fn in (inventory.get("functions") or [])
    )


def detect(
    dwg_stem: str = "",
    *,
    ctx: Optional[Dict] = None,
    inventory: Optional[Dict[str, Any]] = None,
    structural: Optional[Dict[str, Any]] = None,
) -> Ecosystem:
    """Detect and return the Ecosystem for a DWG.

    Priority: explicit ctx['ecosystem'] → known stem prefix → KSD CAD → GOR CAD
    / inventory → valmet.
    """
    # Explicit ecosystem in context overrides stem and inventory detection.
    if ctx:
        explicit = str(ctx.get("ecosystem") or "").strip().lower()
        if explicit in _ECOSYSTEM_TO_STANDARD:
            return _eco(explicit)

    stem = Path(dwg_stem).stem.upper() if dwg_stem else ""
    for prefix, eco_name in _STEM_PREFIX_TO_ECOSYSTEM:
        if stem.startswith(prefix):
            return _eco(eco_name)

    if is_ksd_structural(structural) or is_ksd_inventory(inventory):
        return _eco("ksd")

    if is_gor_structural(structural) or is_gor_inventory(inventory):
        return _eco("gor")

    return _eco("valmet")
