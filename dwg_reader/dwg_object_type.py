#!/usr/bin/env python3
"""
Equipment object-type classifier for SML SAP upload.

Reads standards/sml_object_types.json and classifies each equipment item
by tag pattern (P&ID letter codes) then description keywords, returning
(eqart_code, work_centre) for use in the equipment export.

Lookup hierarchy:
    1. Tag prefix  e.g. "35-24LC-576" → prefix "LC" → 1200 (INSTRUMENT LEVEL)
    2. Motor suffix (.1 / -M1) → 1101, before description keywords
    3. Description keywords (ordered, first match wins)
    4. Fallback → blank EQART (Rob: leave unknown types empty for review)
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

from dwg_reader.paths import STANDARDS_DIR

DEFAULT_JSON = STANDARDS_DIR / "sml_object_types.json"

# Extracts P&ID instrument letter code from tags like "35-24LC-576", "35-24LV2-576"
_TAG_PREFIX_RE = re.compile(r"^35-24([A-Z]{2,})\d*-", re.IGNORECASE)
# Single-letter no-dash tags like "35-24P519", "35-24M023"
_TAG_NODASH_RE = re.compile(r"^35-24([A-Z])\d+$", re.IGNORECASE)
# Motor sub-equipment suffixes: "35-24-001.1" (Valmet) or "124P-001-M1" (Tissue KSDM160104)
_MOTOR_SUFFIX_RE = re.compile(r"(\.\d+|-M\d+)$")
# Tissue / KSDM160104 tag format: "124P-001", "136A-003", "145T-001"
_TISSUE_TAG_PREFIX_RE = re.compile(r"^\d{3}([A-Z])-\d{3}$", re.IGNORECASE)
# Tissue prefix → SAP object type code (applied only when _TISSUE_TAG_PREFIX_RE matches)
# Codes sourced from SML OBJECT TYPE LIST V3 EXPANDED.xlsx
_TISSUE_PREFIX_RULES: Dict[str, str] = {
    "P": "701",   # Pump centrifugal
    "A": "2001",  # Agitator / mixer
    "T": "601",   # Tank (description keywords refine further: SILO→602, VESSEL→604)
    "E": "2000",  # Process machines (description keywords refine to: PULPER→2005, REFINER→2002)
}

# GOR/Valmet-Tissue tag format: "168TC1", "168P-410", "168TT2", "168L-522", "168VX-521"
# First group: 3-digit machine section; second group: 1-4 letter instrument code
_GOR_TAG_PREFIX_RE = re.compile(r"^\d{3}([A-Z]{1,4})(?:-?\d|$)", re.IGNORECASE)
# GOR letter-code → SAP object type code
_GOR_PREFIX_RULES: Dict[str, str] = {
    "P": "701",    # Pump centrifugal
    "L": "2100",   # Pipe line
    "V": "201",    # Valve hand
    "VX": "201",   # 3-way valve
    "FV": "202",   # Flow valve (auto)
    "TV": "202",   # Temperature valve (auto)
    "ST": "203",   # Safety / relief valve
    "F": "801",    # Fan
    "TC": "1202",  # Instrument temperature (controller)
    "TT": "1202",  # Instrument temperature (transmitter)
    "TA": "1202",  # Instrument temperature (alarm)
    "TI": "1202",  # Instrument temperature (indicator)
    "PT": "1201",  # Instrument pressure (transmitter)
    "PC": "1201",  # Instrument pressure (controller)
    "PI": "1201",  # Instrument pressure (indicator)
    "FT": "1203",  # Instrument flow (transmitter)
    "FC": "1203",  # Instrument flow (controller)
    "LT": "1204",  # Instrument level (transmitter)
    "LC": "1204",  # Instrument level (controller)
    "LI": "1204",  # Instrument level (indicator)
    "HC": "1210",  # Instrument other (hand controller / humidity)
    "HS": "1210",  # Instrument other (hand switch)
    "HI": "1210",  # Instrument other (hand indicator)
    "GSO": "1210", # Gas shut-off
    "GSC": "1210", # Gas shut-close
    "E": "2030",   # Heat exchanger
    "M": "1101",   # Motor / actuator
}


@lru_cache(maxsize=1)
def _load(path: str) -> Dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _data(json_path: Path) -> Dict:
    return _load(str(json_path.resolve()))


def lookup(code: str, json_path: Path = DEFAULT_JSON) -> Tuple[str, str]:
    """Return (name, work_centre) for a numeric object type code string."""
    d = _data(json_path)
    entry = d["object_types"].get(str(code), {})
    return entry.get("name", ""), entry.get("work_centre", "")


def classify_equipment(
    tag: str,
    eqktx: str,
    json_path: Path = DEFAULT_JSON,
) -> Tuple[str, str]:
    """
    Return (eqart_code, work_centre) for one equipment row.

    tag   – the EQUNR value (e.g. "35-24LC-576", "35-24-095")
    eqktx – the normalised description (upper-case, max 40 chars)
    """
    d = _data(json_path)
    prefix_rules: Dict[str, str] = d["tag_prefix_rules"]
    kw_rules: List[Dict] = d["description_keyword_rules"]
    obj_types: Dict[str, Dict] = d["object_types"]

    def _resolve(code: str) -> Tuple[str, str]:
        entry = obj_types.get(code, {})
        return code, entry.get("work_centre", "")

    # 1. Tag prefix — multi-letter dash format: "35-24LC-576"
    m = _TAG_PREFIX_RE.match(tag)
    if m:
        prefix = m.group(1).upper()
        if prefix in prefix_rules:
            return _resolve(prefix_rules[prefix])

    # 2. Tag prefix — single-letter no-dash format: "35-24P519"
    m = _TAG_NODASH_RE.match(tag)
    if m:
        prefix = m.group(1).upper()
        if prefix in prefix_rules:
            return _resolve(prefix_rules[prefix])
        # L401–L499 = Agitator per SML PS-21 / Valmet PM3 number-series convention
        if prefix == "L":
            num_m = re.search(r"(\d+)$", tag)
            if num_m and 401 <= int(num_m.group(1)) <= 499:
                return _resolve("2001")

    # 2.5 Tissue / KSDM160104 tag format: "124P-001" → prefix P → 701
    m = _TISSUE_TAG_PREFIX_RE.match(tag)
    if m:
        prefix = m.group(1).upper()
        if prefix in _TISSUE_PREFIX_RULES:
            return _resolve(_TISSUE_PREFIX_RULES[prefix])

    # 2.6 Motor sub-equipment suffix BEFORE description keywords.
    # Otherwise a motor copied from a pulper/winder parent ("WINDER PLPR")
    # classifies as 2005 MECH instead of 1101 ELEC.
    # Rotors (35-24L009.1) share the decimal suffix but are equipment, not motors.
    if re.match(r"^\d{2}-\d{2}[A-Z]+\d+\.\d+$", tag, re.I):
        return _resolve("2000")
    if _MOTOR_SUFFIX_RE.search(tag):
        return _resolve("1101")

    # 2.7 GOR/Valmet-Tissue instrument tags: "168TC1", "168P-410", "168TT2"
    m = _GOR_TAG_PREFIX_RE.match(tag)
    if m:
        prefix = m.group(1).upper()
        # Try longest match first (VX before V; TC before T; FV before F)
        for length in range(len(prefix), 0, -1):
            if prefix[:length] in _GOR_PREFIX_RULES:
                return _resolve(_GOR_PREFIX_RULES[prefix[:length]])

    # 3. Description keyword rules (ordered — first match wins)
    desc_upper = eqktx.upper()
    for rule in kw_rules:
        if all(kw in desc_upper for kw in rule["match"]):
            return _resolve(rule["code"])

    # 4. Fallback — blank, not 9999. Unknown types must be reviewed, not invented.
    return "", ""
