#!/usr/bin/env python3
"""
Orchestrate hierarchy building over inventory FUNCTIONs, one by one.

Flow:
  1. Load tags from pid_inventory.json ``functions`` (equipment+line by default)
  2. Take the first ``--limit`` tags (default 10; 0 = all)
  3. For each tag: run viewer+Bedrock hierarchy, then compare to GT
     - EQUIPMENT: hits / misses (in GT, not in ours) / extras
     - SUB-EQUIPMENT: same
  4. Write combined hierarchy CSV + per-function score report
"""

from __future__ import annotations
import dwg_reader.dwg_warn as dwg_warn  # noqa: F401 — silence boto3 Python 3.9 deprecation noise

import argparse
import concurrent.futures
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import re

from dwg_reader.dwg_ecosystem import detect as detect_ecosystem, is_gor_inventory
from dwg_reader.dwg_floc_context import is_phantom_motor_line_tag
from dwg_reader.dwg_pid_hierarchy_ai import run_hierarchy_for_tag as _run_hierarchy_for_tag
from dwg_reader.dwg_pure_dump import find_json, json_path, logs_dir, safe_name, write_json
from dwg_reader.dwg_valve_classify import run_valve_classify
from dwg_reader.eval_hierarchy_gt import (
    format_function_report,
    load_gt_rows,
    macro_hit_accuracy,
    score_function,
)
from dwg_reader.dwg_tag_registry import apply_registry_from_output_dir
from dwg_reader.export_hierarchy_tree import run_hierarchy_tree_export
from dwg_reader.export_sap_equipment import (
    patch_hierarchy_csv_from_reasoning as _patch_hierarchy_csv_with_valve_eqktx,
    run_equipment_export,
)
from dwg_reader.export_sap_floc import run_floc_export
from dwg_reader.io import read_csv_rows, write_csv_rows
from dwg_reader.logutil import configure_logging, get_logger
from dwg_reader.models import HIERARCHY_COLUMNS

logger = get_logger(__name__)

_GOR_FN_RE = re.compile(r"^WU\d+$", re.I)
_TAG_SUFFIX_RE = re.compile(r"(\d+)$")

_GOR_TIPO_TYPE_LABELS: Dict[str, str] = {
    "BF": "BUTTERFLY VLV",
    "LWE": "SOLENOID NC VLV",
    "IT": "ISOLATION TAP VLV",
    "VX": "3-WAY SOL VLV",
    "ST": "SAFETY VLV",
    "FL": "BLIND FLANGE",
}

# Letter codes in GOR instrument tags → short SAP description suffix
_GOR_INSTR_LABELS: Dict[str, str] = {
    "TC": "TEMP CTRL",
    "TT": "TEMP TRANS",
    "TA": "TEMP ALRM",
    "TI": "TEMP IND",
    "TV": "TEMP VLV",
    "PT": "PRES TRANS",
    "PC": "PRES CTRL",
    "PI": "PRES IND",
    "FT": "FLOW TRANS",
    "FC": "FLOW CTRL",
    "FV": "FLOW VLV",
    "LC": "LVL CTRL",
    "LT": "LVL TRANS",
    "LI": "LVL IND",
    "HC": "HUM CTRL",
    "HS": "HND SW",
    "HI": "HND IND",
    "GSO": "GAS SO",
    "GSC": "GAS SC",
    "ST": "SAFETY VLV",
    "M": "MTR",
    "E": "HEAT EXCH",
    "P": "PMP",
    "F": "FAN",
}
# Letter block after the 3-digit machine section (168FV1-416, 168TI2, 168F-415).
_GOR_INSTR_LETTERS_RE = re.compile(r"^\d{3}([A-Z]{1,4})", re.I)
# Matches simple GOR instrument tags: "168TC1", "168M1" (no hyphen after letters)
_GOR_INSTR_TAG_RE = re.compile(r"^\d{3}([A-Z]{1,4})\d*$", re.I)
# Matches compound GOR equipment tags: "168P-410", "168F-415" (letter + hyphen + digits)
_GOR_INSTR_COMPOUND_RE = re.compile(r"^\d{3}([A-Z]{1,4})-\d+$", re.I)


def _tipo_suffix(tipo: str) -> Optional[str]:
    """Extract TIPO family code (e.g. '2K0-BF-65' → 'BF', 'ST-65' → 'ST')."""
    parts = (tipo or "").split("-")
    if len(parts) >= 3:
        return parts[1].upper()
    if len(parts) == 2:
        return parts[0].upper()
    return None


def _gor_code03_valve_type(tag: str) -> Optional[str]:
    """Infer SAP valve type for Code 03 GOR text tags (no TIPO_VALVOLA block).

    Delegates to GORAdapter so KV→AV, ``\\dV-\\d``→NC, ST→SV, else HV stay
    identical to ``resolve_valve_type`` (including hyphenated ST tags).
    """
    t = re.sub(r"\s+", "", str(tag or "").strip()).upper()
    if not t:
        return None
    from dwg_reader.adapters.gor_adapter import GORAdapter
    vtype, _is_valve = GORAdapter()._code03_type(t)
    return vtype


def _tipo_to_sap_type(tipo: str) -> tuple[Optional[str], bool]:
    """Map GOR TIPO_VALVOLA to SAP valve type. Returns (sap_type, is_valve)."""
    t = (tipo or "").strip().upper()
    if not t:
        return None, True

    suffix = _tipo_suffix(t) or ""
    prefix = t.split("-")[0].upper() if "-" in t else ""

    if suffix == "FL":
        return None, False
    if suffix == "ST":
        return "SV", True
    if suffix == "VX":
        return "AV", True
    if suffix == "LWE":
        return "NC", True
    if suffix == "IT":
        return "NC", True
    if suffix == "BF":
        return ("AV", True) if prefix.startswith("6") else ("NC", True)

    return None, True


def _seed_gor_valve_types(inv_path: Path, valve_types_path: Path, fn_id: str) -> None:
    """Create valve_types.json entries from GOR inventory (no Bedrock vision)."""
    try:
        inv_data = json.loads(inv_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Could not read inventory JSON %s: %s", inv_path, exc)
        return

    raw: Dict[str, Any] = {}
    if valve_types_path.exists():
        try:
            raw = json.loads(valve_types_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Could not read valve types %s: %s", valve_types_path, exc)
            raw = {}
    tags_data = raw.get("tags", {})
    if not isinstance(tags_data, dict):
        tags_data = {}

    seeded = 0
    for v in inv_data.get("valves") or []:
        tag = str(v.get("tag") or "").strip().upper()
        if not tag or tag == "TAG VALVOLA":
            continue
        if tag not in tags_data:
            tags_data[tag] = {
                "fn": fn_id,
                "layer": str(v.get("layer") or "1-VALVE TEXT GOR"),
            }
            seeded += 1

    raw["tags"] = tags_data
    valve_types_path.parent.mkdir(parents=True, exist_ok=True)
    valve_types_path.write_text(
        json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if seeded:
        logger.info(f"[gor] valve_types seeded: {seeded} tags from inventory")


def _patch_gor_valve_types(inv_path: Path, valve_types_path: Path, fn_id: str) -> None:
    """Apply TIPO SAP types and mark instruments is_valve=False in valve_types.json."""
    try:
        inv_data = json.loads(inv_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Could not read inventory JSON %s: %s", inv_path, exc)
        return
    _seed_gor_valve_types(inv_path, valve_types_path, fn_id)
    if not valve_types_path.exists():
        return
    try:
        raw = json.loads(valve_types_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Could not read valve types %s: %s", valve_types_path, exc)
        return
    tags_data = raw.get("tags", {})
    if not isinstance(tags_data, dict):
        tags_data = {}

    # Build TIPO → SAP type map from inventory valves
    tipo_map: Dict[str, Optional[str]] = {}
    tipo_full: Dict[str, str] = {}
    valve_flags: Dict[str, bool] = {}
    for v in inv_data.get("valves") or []:
        tag = str(v.get("tag") or "").strip().upper()
        tipo = str(v.get("valve_type") or "").strip()
        if tag:
            tipo_full[tag] = tipo
            sap_type, is_valve = _tipo_to_sap_type(tipo)
            tipo_map[tag] = sap_type
            valve_flags[tag] = is_valve

    # Instrument tags (skip LOOPDCS placeholders)
    instr_tags: set = set()
    seen_instr: set = set()
    for instr in inv_data.get("instruments") or []:
        tag = str(instr.get("tag") or "").strip().upper()
        if tag and tag not in ("LOOPDCS",) and tag not in seen_instr:
            seen_instr.add(tag)
            instr_tags.add(tag)

    tipo_applied = instr_marked = 0

    for tag_upper in list(tags_data.keys()):
        entry = tags_data[tag_upper]
        if not isinstance(entry, dict):
            continue

        if tag_upper in instr_tags:
            entry["is_valve"] = False
            entry["type"] = "INSTR"
            instr_marked += 1
        elif tag_upper in tipo_map:
            # TIPO code is authoritative for GOR drawings — Bedrock vision is
            # trained on SML symbols and misclassifies Valmet/Italian CAD styles.
            is_valve = valve_flags.get(tag_upper, True)
            vtype = tipo_map[tag_upper] or _gor_code03_valve_type(tag_upper)
            entry["tipo"] = tipo_full.get(tag_upper, "")
            entry["source"] = "tipo_code" if tipo_map[tag_upper] else "gor_tag"
            if not is_valve:
                entry["is_valve"] = False
                entry.pop("type", None)
            elif vtype:
                entry["type"] = vtype
                tipo_applied += 1
        else:
            vtype = _gor_code03_valve_type(tag_upper)
            if vtype:
                entry["type"] = vtype
                entry["source"] = "gor_tag"
                entry["is_valve"] = True
                tipo_applied += 1

    raw["tags"] = tags_data
    valve_types_path.write_text(
        json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info(f"[gor] valve_types patched: {tipo_applied} TIPO codes applied, {instr_marked} instruments marked")


def _is_gor_inventory(inv_path: Path) -> bool:
    """True when the inventory is from a GOR drawing (Code 03, 13, or 14)."""
    try:
        data = json.loads(inv_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return is_gor_inventory(data)


def _gor_valve_desc(tag: str, tipo: str) -> str:
    parts = (tipo or "").split("-")
    if len(parts) >= 3:
        vtype, dn = parts[1], parts[2]
    elif len(parts) == 2:
        vtype, dn = parts[0], parts[1]
    else:
        vtype, dn = tipo, ""
    label = _GOR_TIPO_TYPE_LABELS.get(vtype.upper(), f"{vtype} VLV" if vtype else "VLV")
    return f"{tag} {label} DN{dn}" if dn else f"{tag} {label}"


def _gor_instr_desc(tag: str) -> str:
    """Short SAP description for a GOR instrument/equipment tag."""
    t = str(tag or "").strip()
    im = _GOR_INSTR_LETTERS_RE.match(t)
    if im:
        letters = im.group(1).upper()
        for length in range(len(letters), 0, -1):
            label = _GOR_INSTR_LABELS.get(letters[:length])
            if label:
                return f"{t} {label}"
    return f"{t} INST"


def build_gor_hierarchy(inventory: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build hierarchy CSV for GOR/Valmet drawings without calling Bedrock.

    For Code 14 (WU series): valves are nested as SUB-EQUIPMENT under the pipe line
    whose numeric suffix matches (168V-522 → sub of 168L-522).
    For Code 03/13: no Pipeno blocks, so valves/instruments are flat EQUIPMENT.
    """
    rows: List[Dict[str, str]] = []
    for fn_item in (inventory.get("functions") or []):
        unit_id = str(fn_item.get("function") or "").strip().upper()
        if not unit_id:
            continue
        desc = str(fn_item.get("description") or f"{unit_id} VENTIL UNIT")
        rows.append({
            "SUB-PROCESS": "", "FUNCTION": unit_id, "EQUIPMENT": "",
            "SUB-EQUIPMENT": "", "MASK": unit_id, "DESCRIPTION": desc,
        })

        # Build suffix→line_tag map from Pipeno blocks (Code 14 only)
        suffix_to_line: Dict[str, str] = {}
        lines_in_order: List[tuple] = []
        seen_lines: set = set()
        for line in (inventory.get("lines") or []):
            if line.get("source") != "gor_pipe_id":
                continue
            ltag = str(line.get("line_number") or "").strip()
            if not ltag or ltag.upper() in seen_lines:
                continue
            seen_lines.add(ltag.upper())
            m = _TAG_SUFFIX_RE.search(ltag)
            if m:
                sfx = m.group(1)
                if sfx not in suffix_to_line:
                    suffix_to_line[sfx] = ltag
            lines_in_order.append((ltag, line))

        # Assign each valve to its matching line by numeric suffix
        valves_for_line: Dict[str, List[Dict[str, Any]]] = {}
        unmatched_valves: List[Dict[str, Any]] = []
        seen_valves: set = set()
        for v in (inventory.get("valves") or []):
            tag = str(v.get("tag") or "").strip()
            if not tag or tag.upper() == "TAG VALVOLA" or tag.upper() in seen_valves:
                continue
            seen_valves.add(tag.upper())
            m = _TAG_SUFFIX_RE.search(tag)
            parent_line = suffix_to_line.get(m.group(1)) if m else None
            if parent_line:
                valves_for_line.setdefault(parent_line, []).append(v)
            else:
                unmatched_valves.append(v)

        # Emit each line as EQUIPMENT, then its matched valves as SUB-EQUIPMENT.
        # PIPE (without DN/size) is enough for format_line_eqktx → LN {tag} PIPE.
        for ltag, line in lines_in_order:
            pipe_class = str(line.get("pipe_class") or "").strip()
            size = str(line.get("nominal_size") or "").strip()
            line_desc = f"{ltag} PIPE" if (pipe_class or size) else ltag
            rows.append({
                "SUB-PROCESS": "", "FUNCTION": "", "EQUIPMENT": ltag,
                "SUB-EQUIPMENT": "", "MASK": "",
                "DESCRIPTION": line_desc,
            })
            for v in valves_for_line.get(ltag, []):
                vtag = str(v.get("tag") or "").strip()
                rows.append({
                    "SUB-PROCESS": "", "FUNCTION": "", "EQUIPMENT": "",
                    "SUB-EQUIPMENT": vtag, "MASK": "",
                    "DESCRIPTION": _gor_valve_desc(vtag, str(v.get("valve_type") or "")),
                })

        # Fix #31: separate pump-motor pairs from plain unmatched valves.
        # A tag like "168P-410-M1" is a motor; its parent is "168P-410".
        _motor_suffix_re = re.compile(r"-M(\d+)$", re.I)
        motors_for_equip: Dict[str, List[Dict[str, Any]]] = {}
        flat_valves: List[Dict[str, Any]] = []
        for v in unmatched_valves:
            vtag = str(v.get("tag") or "").strip()
            mm = _motor_suffix_re.search(vtag)
            if mm:
                parent = vtag[: mm.start()]
                motors_for_equip.setdefault(parent, []).append(v)
            else:
                flat_valves.append(v)

        # Unmatched non-motor valves/pumps as EQUIPMENT, with their motors as SUB-EQUIPMENT
        for v in flat_valves:
            vtag = str(v.get("tag") or "").strip()
            rows.append({
                "SUB-PROCESS": "", "FUNCTION": "", "EQUIPMENT": vtag,
                "SUB-EQUIPMENT": "", "MASK": "",
                "DESCRIPTION": _gor_valve_desc(vtag, str(v.get("valve_type") or "")),
            })
            for mv in motors_for_equip.get(vtag, []):
                mtag = str(mv.get("tag") or "").strip()
                rows.append({
                    "SUB-PROCESS": "", "FUNCTION": "", "EQUIPMENT": "",
                    "SUB-EQUIPMENT": mtag, "MASK": "",
                    "DESCRIPTION": f"{mtag} MTR",
                })
        # Motors whose parent wasn't in flat_valves: emit the parent then nest motors
        emitted_motor_parents = {str(v.get("tag") or "").strip() for v in flat_valves}
        for parent, mvs in motors_for_equip.items():
            if parent in emitted_motor_parents:
                continue
            rows.append({
                "SUB-PROCESS": "", "FUNCTION": "", "EQUIPMENT": parent,
                "SUB-EQUIPMENT": "", "MASK": "",
                "DESCRIPTION": _gor_instr_desc(parent),
            })
            emitted_motor_parents.add(parent)
            for mv in mvs:
                mtag = str(mv.get("tag") or "").strip()
                rows.append({
                    "SUB-PROCESS": "", "FUNCTION": "", "EQUIPMENT": "",
                    "SUB-EQUIPMENT": mtag, "MASK": "",
                    "DESCRIPTION": f"{mtag} MTR",
                })

        # Fix #34/#31: Instruments with richer descriptions; motors nested under parent.
        # Tags like "168P-410-M1" are motors whose parent is "168P-410"; separate them
        # so the parent is emitted as EQUIPMENT and the motor as its SUB-EQUIPMENT.
        _SKIP_INSTR_TAGS = {"LOOPDCS"}
        seen_instr: set = set()
        instr_motors: Dict[str, List[Dict[str, Any]]] = {}
        instr_non_motor: List[Dict[str, Any]] = []
        for instr in (inventory.get("instruments") or []):
            tag = str(instr.get("tag") or "").strip()
            if not tag or tag.upper() in _SKIP_INSTR_TAGS or tag.upper() in seen_instr:
                continue
            seen_instr.add(tag.upper())
            mm = _motor_suffix_re.search(tag)
            if mm:
                parent = tag[: mm.start()]
                instr_motors.setdefault(parent, []).append(instr)
            else:
                instr_non_motor.append(instr)

        emitted_instr_parents: set = set()
        for instr in instr_non_motor:
            tag = str(instr.get("tag") or "").strip()
            emitted_instr_parents.add(tag)
            rows.append({
                "SUB-PROCESS": "", "FUNCTION": "", "EQUIPMENT": tag,
                "SUB-EQUIPMENT": "", "MASK": "",
                "DESCRIPTION": _gor_instr_desc(tag),
            })
            for mv in instr_motors.get(tag, []):
                mtag = str(mv.get("tag") or "").strip()
                rows.append({
                    "SUB-PROCESS": "", "FUNCTION": "", "EQUIPMENT": "",
                    "SUB-EQUIPMENT": mtag, "MASK": "",
                    "DESCRIPTION": f"{mtag} MTR",
                })
        # Orphan motors (parent not in non-motor instruments): inject parent then nest
        for parent, mvs in instr_motors.items():
            if parent in emitted_instr_parents:
                continue
            rows.append({
                "SUB-PROCESS": "", "FUNCTION": "", "EQUIPMENT": parent,
                "SUB-EQUIPMENT": "", "MASK": "",
                "DESCRIPTION": _gor_instr_desc(parent),
            })
            emitted_instr_parents.add(parent)
            for mv in mvs:
                mtag = str(mv.get("tag") or "").strip()
                rows.append({
                    "SUB-PROCESS": "", "FUNCTION": "", "EQUIPMENT": "",
                    "SUB-EQUIPMENT": mtag, "MASK": "",
                    "DESCRIPTION": f"{mtag} MTR",
                })
    return rows


DEFAULT_HIERARCHY_FUNCTION_KINDS = ("equipment", "line")
_INSTRUMENT_FN_RE = re.compile(r"^\d{2}-\d{2}(?:ES|HS|HI|WI|KI|KJ|MCS)-\d", re.I)
_PHANTOM_EQUIP_RE = re.compile(r"\.\d+$")


def _is_instrument_function_tag(tag: str) -> bool:
    return bool(_INSTRUMENT_FN_RE.match(str(tag or "").strip().upper().replace(" ", "")))


def _dominant_area_prefixes(inv_path: Path, *, min_count: int = 2, limit: int = 4) -> set[str]:
    try:
        data = json.loads(inv_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Could not read inventory JSON %s: %s", inv_path, exc)
        return set()
    from collections import Counter

    counts: Counter[str] = Counter()
    for fn in data.get("functions") or []:
        if str(fn.get("kind") or "").lower() not in DEFAULT_HIERARCHY_FUNCTION_KINDS:
            continue
        tag = str(fn.get("function") or "").strip().upper().replace(" ", "")
        m = re.match(r"^(\d{2}-\d{2})", tag)
        if m:
            counts[m.group(1)] += 1
    return {p for p, c in counts.most_common(limit) if c >= min_count}


def _plant_prefix(tag: str) -> str:
    m = re.match(r"^(\d{2}-\d{2})", str(tag or "").strip().upper().replace(" ", ""))
    return m.group(1) if m else ""


def sanitize_hierarchy_rows(
    rows: List[Dict[str, str]],
    inventory_tags: "set[str]" = frozenset(),
) -> List[Dict[str, str]]:
    """Drop phantom AI tags, cross-area noise, and duplicate equipment assignments.

    inventory_tags: if provided, decimal-suffix tags that exist in the inventory
    (e.g. genuine rotor sub-equipment 35-24L009.1) are preserved even though
    they match _PHANTOM_EQUIP_RE.
    """
    out: List[Dict[str, str]] = []
    seen_equipment: set[str] = set()
    current_fn_prefix = ""

    for row in rows:
        fn = str(row.get("FUNCTION") or "").strip().upper().replace(" ", "")
        eq = str(row.get("EQUIPMENT") or "").strip().upper().replace(" ", "")
        sub = str(row.get("SUB-EQUIPMENT") or "").strip().upper().replace(" ", "")

        if fn and not eq and not sub:
            current_fn_prefix = _plant_prefix(fn)
            out.append(row)
            continue

        if not eq and not sub:
            out.append(row)
            continue

        tag = eq or sub
        # Drop AI-hallucinated decimal sub-tags (35-24-508.2, .3, .4) unless
        # the tag actually exists in the inventory (genuine rotors like 35-24L009.1).
        if _PHANTOM_EQUIP_RE.search(tag) and tag not in inventory_tags:
            continue
        if is_phantom_motor_line_tag(tag, str(row.get("DESCRIPTION") or "")):
            continue
        if current_fn_prefix and _plant_prefix(tag) and _plant_prefix(tag) != current_fn_prefix:
            continue
        if tag in seen_equipment:
            continue
        seen_equipment.add(tag)
        out.append(row)
    return out


def load_inventory_functions(
    path: Path,
    kinds: Optional[List[str]] = None,
    *,
    area_prefixes: Optional[set[str]] = None,
) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("functions") or []
    if kinds is not None:
        want = {k.lower() for k in kinds}
        rows = [r for r in rows if str(r.get("kind") or "").lower() in want]
    # Keep inventory order; drop duplicate tags (first kind wins).
    out: List[Dict[str, Any]] = []
    seen = set()
    for r in rows:
        tag = str(r.get("function") or "").strip().upper().replace(" ", "")
        if not tag or tag in seen or _is_instrument_function_tag(tag):
            continue
        seen.add(tag)
        row = dict(r)
        row["function"] = tag
        out.append(row)
    if area_prefixes:
        filtered: List[Dict[str, Any]] = []
        for r in out:
            tag = str(r.get("function") or "")
            prefix = _plant_prefix(tag)
            if not prefix or prefix in area_prefixes:
                filtered.append(r)
        out = filtered
    return out


def csv_function_headers(rows: List[Dict[str, str]]) -> List[str]:
    out: List[str] = []
    seen = set()
    for row in rows:
        fn = str(row.get("FUNCTION") or "").strip().upper().replace(" ", "")
        eq = str(row.get("EQUIPMENT") or "").strip()
        sub = str(row.get("SUB-EQUIPMENT") or "").strip()
        if fn and not eq and not sub and fn not in seen:
            seen.add(fn)
            out.append(fn)
    return out


def rows_for_function(rows: List[Dict[str, str]], tag: str) -> List[Dict[str, str]]:
    """Keep only the requested FUNCTION header + its inherited children."""
    want = str(tag or "").strip().upper().replace(" ", "")
    out: List[Dict[str, str]] = []
    current = False
    for row in rows:
        fn = str(row.get("FUNCTION") or "").strip().upper().replace(" ", "")
        eq = str(row.get("EQUIPMENT") or "").strip()
        sub = str(row.get("SUB-EQUIPMENT") or "").strip()
        if fn and not eq and not sub:
            current = fn == want
        if current:
            out.append(row)
    return out


def write_hierarchy_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    write_csv_rows(path, rows, HIERARCHY_COLUMNS)


def read_hierarchy_csv(path: Path) -> List[Dict[str, str]]:
    return read_csv_rows(path, missing_ok=True)


def _append_orphan_valve_rows(
    combined_csv: Path,
    structural_path: Path,
    inv_path: Path,
) -> int:
    """
    Find P-VALVEPOS valve position tags absent from the hierarchy and insert
    them as EQUIPMENT rows under their nearest function by Euclidean distance.

    Returns the count of orphan rows appended.

    Context: in some DWGs (e.g. steam/condensate supply headers) valve tags
    exist on P-VALVEPOS but have no nearby FUNCTION equipment node — they fall
    between the coverage windows of neighbouring functions and are never
    captured by the AI hierarchy step.  This mop-up prevents them from being
    silently dropped before valve classification and SAP export.
    """
    import math
    import re

    VALVE_POS_RE = re.compile(r"^\d{2}-\d{2}-\d{3,4}$")

    if not structural_path.exists():
        logger.info(f"[orphan-mopup] structural dump not found: {structural_path}; skipping")
        return 0

    existing = read_hierarchy_csv(combined_csv)
    if not existing:
        return 0

    # Tags already present anywhere in the hierarchy (function, equipment, sub-equipment).
    in_hierarchy: set = set()
    for row in existing:
        for col in ("FUNCTION", "EQUIPMENT", "SUB-EQUIPMENT"):
            v = (row.get(col) or "").strip().upper()
            if v:
                in_hierarchy.add(v)

    # P-VALVEPOS valve position number texts from structural dump.
    structural = json.loads(structural_path.read_text(encoding="utf-8"))
    valve_locs: Dict[str, Any] = {}  # tag -> (x, y), first occurrence wins
    for t in structural.get("text_entities", []):
        if t.get("layer") != "P-VALVEPOS":
            continue
        txt = (t.get("text") or "").strip().upper()
        if not VALVE_POS_RE.match(txt):
            continue
        pos = t.get("position") or []
        if len(pos) >= 2 and pos[0] is not None and txt not in valve_locs:
            valve_locs[txt] = (float(pos[0]), float(pos[1]))

    orphans = {tag: xy for tag, xy in valve_locs.items() if tag not in in_hierarchy}
    if not orphans:
        logger.info("[orphan-mopup] no orphan valve tags found")
        return 0

    logger.info(f"[orphan-mopup] {len(orphans)} orphan valve tags to assign")

    # Function positions from inventory (only those already in the hierarchy CSV).
    existing_fn_headers: set = {
        row.get("FUNCTION", "").strip().upper()
        for row in existing
        if row.get("FUNCTION") and not row.get("EQUIPMENT") and not row.get("SUB-EQUIPMENT")
    }
    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    fn_locs: Dict[str, Any] = {}
    for fn in inventory.get("functions") or []:
        tag = str(fn.get("function") or "").strip().upper()
        x, y = fn.get("x"), fn.get("y")
        if tag in existing_fn_headers and x is not None and y is not None:
            fn_locs[tag] = (float(x), float(y))

    if not fn_locs:
        logger.info("[orphan-mopup] no function positions available; skipping")
        return 0

    # Group functions by sub-process prefix (e.g. "35-27") for prefix-aware matching.
    fn_by_prefix: Dict[str, Dict[str, Any]] = {}
    for fn, xy in fn_locs.items():
        pfx = fn[:5]
        fn_by_prefix.setdefault(pfx, {})[fn] = xy

    def _nearest(candidates: Dict[str, Any], ox: float, oy: float):
        return min(
            ((fn, math.hypot(ox - fx, oy - fy)) for fn, (fx, fy) in candidates.items()),
            key=lambda t: t[1],
        )

    # Assign each orphan to its nearest SAME-prefix function; fall back to nearest overall.
    fn_orphans: Dict[str, List[str]] = {}
    for tag, (ox, oy) in sorted(orphans.items()):
        valve_pfx = tag[:5]
        same_prefix_fns = fn_by_prefix.get(valve_pfx, {})
        if same_prefix_fns:
            best_fn, best_d = _nearest(same_prefix_fns, ox, oy)
        else:
            best_fn, best_d = _nearest(fn_locs, ox, oy)
        fn_orphans.setdefault(best_fn, []).append(tag)
        logger.info(f"[orphan-mopup]   {tag} → {best_fn} (d={best_d:.0f})")

    for fn in fn_orphans:
        fn_orphans[fn].sort()

    def _orphan_row(tag: str) -> Dict[str, str]:
        return {
            "SUB-PROCESS": "",
            "FUNCTION": "",
            "EQUIPMENT": tag,
            "SUB-EQUIPMENT": "",
            "MASK": "ORPHAN",
            "DESCRIPTION": f"{tag} VLV",
        }

    # Insert orphan rows after each function's last child row.
    result: List[Dict[str, str]] = []
    pending_orphans: List[str] = []

    for row in existing:
        fn = (row.get("FUNCTION") or "").strip().upper()
        eq = (row.get("EQUIPMENT") or "").strip()
        sub = (row.get("SUB-EQUIPMENT") or "").strip()
        is_fn_header = bool(fn) and not eq and not sub

        if is_fn_header:
            # Flush orphans for the function we are leaving, then move to new one.
            for t in pending_orphans:
                result.append(_orphan_row(t))
            pending_orphans = fn_orphans.get(fn, [])

        result.append(row)

    # Flush orphans that belong to the last function in the file.
    for t in pending_orphans:
        result.append(_orphan_row(t))

    count = sum(len(v) for v in fn_orphans.values())
    write_hierarchy_csv(combined_csv, result)
    logger.info(f"[orphan-mopup] appended {count} orphan valve rows → {combined_csv.name}")
    return count


_AGITATOR_EQ_RE = re.compile(r"^\d{2}-\d{2}L(4\d{2})$", re.I)
_TANK_FN_RE = re.compile(r"^\d{2}-\d{2}T\d+", re.I)


def _append_agitator_equipment_rows(
    combined_csv: Path,
    inv_path: Path,
    structural_path: Optional[Path] = None,
) -> int:
    """Insert bound L401–L499 agitators as EQUIPMENT under the nearest tank FUNCTION.

    Agitators are deliberately excluded from inventory FUNCTIONs (they belong under
    tanks). After CAD bind they still need a hierarchy EQUIPMENT row so export can
    inject the implicit motor (35-24L404 → 35-24-404.1).
    """
    import math

    if not inv_path.exists():
        logger.info(f"[agitator-mopup] inventory not found: {inv_path}; skipping")
        return 0

    existing = read_hierarchy_csv(combined_csv)
    if not existing:
        return 0

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    if structural_path and structural_path.exists():
        from dwg_reader.dwg_pid_inventory import bind_agitator_tags

        structural = json.loads(structural_path.read_text(encoding="utf-8"))
        n_bound = bind_agitator_tags(inventory, structural)
        if n_bound:
            inv_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
            logger.info(f"[agitator-mopup] bound {n_bound} agitator insert tags in inventory")

    in_hierarchy: set = set()
    for row in existing:
        for col in ("FUNCTION", "EQUIPMENT", "SUB-EQUIPMENT"):
            v = (row.get(col) or "").strip().upper().replace(" ", "")
            if v:
                in_hierarchy.add(v)

    orphans: Dict[str, Dict[str, Any]] = {}
    for item in inventory.get("agitators") or []:
        if item.get("source") != "insert":
            continue
        tag = re.sub(r"\s+", "", str(item.get("tag") or "").strip()).upper()
        m = _AGITATOR_EQ_RE.match(tag)
        if not m or not (401 <= int(m.group(1)) <= 499):
            continue
        if tag in in_hierarchy or tag in orphans:
            continue
        x, y = item.get("x"), item.get("y")
        if x is None or y is None:
            continue
        orphans[tag] = {
            "x": float(x),
            "y": float(y),
            "description": str(item.get("description") or f"{tag} AGITATOR").strip(),
        }

    if not orphans:
        logger.info("[agitator-mopup] no unbound agitator tags to append")
        return 0

    existing_fn_headers: set = {
        row.get("FUNCTION", "").strip().upper().replace(" ", "")
        for row in existing
        if row.get("FUNCTION") and not row.get("EQUIPMENT") and not row.get("SUB-EQUIPMENT")
    }
    fn_locs: Dict[str, Tuple[float, float]] = {}
    for fn in inventory.get("functions") or []:
        tag = str(fn.get("function") or "").strip().upper().replace(" ", "")
        x, y = fn.get("x"), fn.get("y")
        if tag in existing_fn_headers and x is not None and y is not None:
            fn_locs[tag] = (float(x), float(y))

    tank_locs = {fn: xy for fn, xy in fn_locs.items() if _TANK_FN_RE.match(fn)}
    if not tank_locs and not fn_locs:
        logger.info("[agitator-mopup] no function positions available; skipping")
        return 0

    def _nearest(candidates: Dict[str, Tuple[float, float]], ox: float, oy: float):
        return min(
            ((fn, math.hypot(ox - fx, oy - fy)) for fn, (fx, fy) in candidates.items()),
            key=lambda t: t[1],
        )

    fn_agits: Dict[str, List[str]] = {}
    desc_by_tag = {t: info["description"] for t, info in orphans.items()}
    for tag, info in sorted(orphans.items()):
        ox, oy = info["x"], info["y"]
        # Prefer a tank within 150 drawing units; else nearest tank / function.
        if tank_locs:
            best_fn, best_d = _nearest(tank_locs, ox, oy)
            if best_d > 150 and fn_locs:
                alt_fn, alt_d = _nearest(fn_locs, ox, oy)
                if alt_d + 20 < best_d:
                    best_fn, best_d = alt_fn, alt_d
        else:
            best_fn, best_d = _nearest(fn_locs, ox, oy)
        fn_agits.setdefault(best_fn, []).append(tag)
        logger.info(f"[agitator-mopup]   {tag} → {best_fn} (d={best_d:.0f})")

    for fn in fn_agits:
        fn_agits[fn].sort()

    def _agit_row(tag: str) -> Dict[str, str]:
        return {
            "SUB-PROCESS": "",
            "FUNCTION": "",
            "EQUIPMENT": tag,
            "SUB-EQUIPMENT": "",
            "MASK": "AGITATOR",
            "DESCRIPTION": desc_by_tag.get(tag, f"{tag} AGITATOR"),
        }

    result: List[Dict[str, str]] = []
    pending: List[str] = []

    for row in existing:
        fn = (row.get("FUNCTION") or "").strip().upper().replace(" ", "")
        eq = (row.get("EQUIPMENT") or "").strip()
        sub = (row.get("SUB-EQUIPMENT") or "").strip()
        is_fn_header = bool(fn) and not eq and not sub

        if is_fn_header:
            for t in pending:
                result.append(_agit_row(t))
            pending = fn_agits.get(fn, [])

        result.append(row)

    for t in pending:
        result.append(_agit_row(t))

    count = sum(len(v) for v in fn_agits.values())
    write_hierarchy_csv(combined_csv, result)
    logger.info(f"[agitator-mopup] appended {count} agitator equipment rows → {combined_csv.name}")
    return count


_MACHINE_FN_RE = re.compile(r"^\d{2}-\d{2}[LPT]\d+$", re.I)

# Instrument valve tag patterns used for actuator package injection
_HV_TAG_RE = re.compile(r"^(\d{2}-\d{2})HV-(\d+)$", re.I)
_KV_TAG_RE = re.compile(r"^(\d{2}-\d{2})KV-(\d+)$", re.I)
_FC_TAG_RE = re.compile(r"^(\d{2}-\d{2})FC-(\d+)$", re.I)
# XV = solenoid isolating valve; its actuator pair is XS (solenoid switch)
_XV_TAG_RE = re.compile(r"^(\d{2}-\d{2})XV-(\d+)$", re.I)
# TV = temperature control valve; paired with XS
_TV_TAG_RE = re.compile(r"^(\d{2}-\d{2})TV-(\d+)$", re.I)


def _append_missing_machine_functions(
    combined_csv: Path,
    inv_path: Path,
) -> int:
    """Insert inventory machine FUNCTIONs (pumps/pulpers/tanks) the hierarchy omitted.

    P518 from motors.docx is a pump on the sheet that Bedrock sometimes drops.
    Adding a FUNCTION header lets FLOC + equipment export (and motor injection) see it.
    Agitators L401–L499 are handled by ``_append_agitator_equipment_rows``.
    """
    if not inv_path.exists() or not combined_csv.exists():
        return 0

    existing = read_hierarchy_csv(combined_csv)
    if not existing:
        return 0

    in_hierarchy: set = set()
    for row in existing:
        fn = (row.get("FUNCTION") or "").strip().upper().replace(" ", "")
        eq = (row.get("EQUIPMENT") or "").strip().upper().replace(" ", "")
        if fn:
            in_hierarchy.add(fn)
        if eq:
            in_hierarchy.add(eq)

    try:
        inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0

    missing: List[Dict[str, str]] = []
    seen: set = set()
    for fn in inventory.get("functions") or []:
        tag = re.sub(r"\s+", "", str(fn.get("function") or "").strip()).upper()
        if not tag or tag in in_hierarchy or tag in seen:
            continue
        if not _MACHINE_FN_RE.match(tag):
            continue
        if _AGITATOR_EQ_RE.match(tag):
            continue
        seen.add(tag)
        desc = str(fn.get("description") or tag).strip()
        missing.append({
            "SUB-PROCESS": "",
            "FUNCTION": tag,
            "EQUIPMENT": "",
            "SUB-EQUIPMENT": "",
            "MASK": tag,
            "DESCRIPTION": desc,
        })

    if not missing:
        return 0

    write_hierarchy_csv(combined_csv, existing + missing)
    logger.info(
        f"[machine-mopup] appended {len(missing)} missing machine FUNCTIONs → {combined_csv.name}"
    )
    return len(missing)


def _load_inventory_tags(inv_path: Path) -> "set[str]":
    """Return the uppercase set of every tag in the inventory JSON."""
    try:
        data = json.loads(inv_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    tags: set = set()
    key_map = {
        "functions": "function",
        "valves": "tag",
        "instruments": "tag",
        "agitators": "tag",
        "lines": "line_number",
    }
    for section, key in key_map.items():
        for item in data.get(section) or []:
            t = re.sub(r"\s+", "", str(item.get(key) or "")).strip().upper()
            if t:
                tags.add(t)
    return tags


_INSTR_CHILDREN: List[tuple] = [
    (_HV_TAG_RE, [("HI", "HND IND"), ("HS", "HND SW")]),
    (_KV_TAG_RE, [("KS", "SOL SW")]),
    (_FC_TAG_RE, [("FV", "FLOW VLV")]),
    # XV solenoid isolating valve → XS position switch
    (_XV_TAG_RE, [("XS", "SOL SW")]),
    # TV temperature/throttle valve → XS position switch
    (_TV_TAG_RE, [("XS", "SOL SW")]),
]


def _inject_instrument_packages(combined_csv: Path, inventory_tags: "set[str]") -> int:
    """Insert instrument actuator packages as SUB-EQUIPMENT in the hierarchy CSV.

    For each HV-NNN EQUIPMENT row, injects HI-NNN and HS-NNN if they exist in
    the inventory.  Similarly KV-NNN → KS-NNN and FC-NNN → FV-NNN.  These
    instrument tags are always sub-equipment of the parent valve in the GT but
    the AI never generates them — this deterministic injection recovers them.
    """
    existing = read_hierarchy_csv(combined_csv)
    if not existing or not inventory_tags:
        return 0

    in_hierarchy: set = set()
    for row in existing:
        for col in ("FUNCTION", "EQUIPMENT", "SUB-EQUIPMENT"):
            v = (row.get(col) or "").strip().upper().replace(" ", "")
            if v:
                in_hierarchy.add(v)

    result: List[Dict[str, str]] = []
    injected = 0

    for row in existing:
        fn = (row.get("FUNCTION") or "").strip().upper().replace(" ", "")
        eq = (row.get("EQUIPMENT") or "").strip().upper().replace(" ", "")
        sub = (row.get("SUB-EQUIPMENT") or "").strip().upper().replace(" ", "")
        result.append(row)

        if not eq or fn or sub:
            continue

        for tag_re, children in _INSTR_CHILDREN:
            m = tag_re.match(eq)
            if not m:
                continue
            area, num = m.group(1), m.group(2)
            sp = row.get("SUB-PROCESS", "")
            for child_prefix, child_desc in children:
                child = f"{area}{child_prefix}-{num}"
                if child in inventory_tags and child not in in_hierarchy:
                    in_hierarchy.add(child)
                    result.append({
                        "SUB-PROCESS": sp,
                        "FUNCTION": "",
                        "EQUIPMENT": "",
                        "SUB-EQUIPMENT": child,
                        "MASK": "",
                        "DESCRIPTION": f"{child} {child_desc}",
                    })
                    injected += 1

    if injected:
        write_hierarchy_csv(combined_csv, result)
        logger.info(
            f"[instrument-inject] injected {injected} instrument sub-equipment rows → {combined_csv.name}"
        )
    else:
        logger.info("[instrument-inject] no instrument packages to inject")
    return injected


def run_hierarchy_for_tag(
    *,
    tag: str,
    input_path: Path,
    out_dir: Path,
    model_id: str,
    region: str,
    prompt_file: str,
    inventory_json: Path,
    per_tag_csv: Path,
    per_tag_json: Path,
    reuse_shots: bool,
    no_clean_prev: bool,
    aws_profile: str,
    crop_half: Optional[float] = None,
) -> int:
    logger.info(f"\n---------- hierarchy: {tag} ----------")
    kwargs = dict(
        tag=tag,
        input_path=input_path,
        out_dir=out_dir,
        model_id=model_id,
        region=region,
        prompt_file=prompt_file,
        inventory_json=inventory_json,
        per_tag_csv=per_tag_csv,
        per_tag_json=per_tag_json,
        reuse_shots=reuse_shots,
        no_clean_prev=no_clean_prev,
        aws_profile=aws_profile,
    )
    if crop_half is not None:
        kwargs["crop_half"] = crop_half
    return _run_hierarchy_for_tag(**kwargs)


def _apply_registry_and_write(
    rows: List[Dict[str, str]],
    *,
    drawing: str,
    out_dir: Path,
    dest: Path,
) -> List[Dict[str, str]]:
    filtered = apply_registry_from_output_dir(rows, drawing=drawing, out_dir=out_dir)
    write_hierarchy_csv(dest, filtered)
    return filtered


def _run_sap_and_tree_exports(
    *,
    input_path: Path,
    out_dir: Path,
    combined_csv: Path,
    gt_path: Path,
    no_export_floc: bool,
    no_export_equipment: bool,
    no_export_hierarchy_tree: bool,
) -> None:
    if not no_export_floc:
        logger.info("\n---------- export SAP FLOC ----------")
        run_floc_export(
            input_path=input_path,
            out_dir=out_dir,
            hierarchy_csv=combined_csv,
            gt=gt_path,
            limit=0,
        )
    if not no_export_equipment:
        logger.info("\n---------- export SAP Equipment ----------")
        run_equipment_export(
            input_path=input_path,
            out_dir=out_dir,
            hierarchy_csv=combined_csv,
            limit=0,
        )
        # Sync hierarchy CSV DESCRIPTION with formatted HV-prefixed EQKTX so the
        # review file matches the SAP equipment.xlsx output.
        _patch_hierarchy_csv_with_valve_eqktx(combined_csv, out_dir, safe_name(input_path))
    if not no_export_hierarchy_tree:
        logger.info("\n---------- export hierarchy tree ----------")
        run_hierarchy_tree_export(
            input_path=input_path,
            out_dir=out_dir,
            hierarchy_csv=combined_csv,
        )


def main() -> int:
    configure_logging()
    parser = argparse.ArgumentParser(
        description="Run hierarchy one-by-one over inventory equipment and score vs GT"
    )
    parser.add_argument("--input", default="inputs/Broke System.dwg")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument(
        "--inventory-json",
        default="",
        help="pid_inventory.json (default: outputs/jsons/<stem>.pid_inventory.json)",
    )
    parser.add_argument(
        "--gt",
        default="resources/gt_hierarchy_broke_system.xlsx",
        help="GT hierarchy workbook/CSV for hit-miss scoring",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max number of inventory FUNCTIONs to process (default: 10; 0 = all)",
    )
    parser.add_argument(
        "--kinds",
        default="",
        help="Comma-separated function kinds (equipment,instrument,line). Default: equipment,line. Use 'all' for every kind.",
    )
    parser.add_argument(
        "--tags",
        default="",
        help="Optional explicit comma-separated tags (overrides inventory selection)",
    )
    parser.add_argument("--model-id", default="eu.anthropic.claude-sonnet-4-6")
    parser.add_argument("--region", default="eu-west-2")
    parser.add_argument(
        "--prompt-file",
        default="",
        help="Prompt template under prompts/. Empty = adapter core+addendum.",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Parallel FUNCTION workers (default: 1).",
    )
    parser.add_argument("--aws-profile", default=os.environ.get("AWS_PROFILE", "foundrydev"))
    parser.add_argument(
        "--reuse-shots",
        action="store_true",
        help="Reuse existing viewer PNGs when present",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only list selected equipment + GT child counts; do not call Bedrock",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip FUNCTIONs already present as headers in hierarchy_orchestrator.csv",
    )
    parser.add_argument(
        "--score-only",
        action="store_true",
        help="Skip Bedrock; score existing hierarchy_orchestrator.csv for the selected tags",
    )
    parser.add_argument(
        "--no-export-floc",
        action="store_true",
        help="Skip SAP Functional Location workbook export at the end",
    )
    parser.add_argument(
        "--no-export-equipment",
        action="store_true",
        help="Skip SAP Equipment workbook export at the end",
    )
    parser.add_argument(
        "--no-export-hierarchy-tree",
        action="store_true",
        help="Skip colour-coded hierarchy.xlsx / hierarchy.html review tree",
    )
    parser.add_argument(
        "--no-valve-classify",
        action="store_true",
        help="Skip per-tag tight-crop valve classification before SAP export",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = logs_dir(out_dir)
    base = safe_name(input_path)

    inv_path = (
        Path(args.inventory_json).expanduser().resolve()
        if args.inventory_json
        else find_json(out_dir, f"{base}.pid_inventory.json")
    )
    if not inv_path.exists():
        logger.error(f"[error] Missing inventory JSON: {inv_path}. Run `make inventory` first.")
        return 2

    gt_path = Path(args.gt).expanduser().resolve()
    try:
        inventory_preview: Dict[str, Any] = json.loads(inv_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        inventory_preview = {}
    eco = detect_ecosystem(input_path.name, inventory=inventory_preview)
    adapter = eco.adapter
    is_gor = eco.name == "gor"
    prompt_file = (args.prompt_file or "").strip() or adapter.hierarchy_prompt_file
    args.prompt_file = prompt_file
    if not gt_path.exists():
        logger.warning(f"[warn] No GT file at {gt_path}; scoring will skip hit/miss.")
    gt_rows = load_gt_rows(gt_path) if gt_path.exists() else []

    if args.tags.strip():
        tags = [t.strip().upper() for t in args.tags.split(",") if t.strip()]
        selected = [{"function": t, "kind": "explicit"} for t in tags]
    else:
        if args.kinds.strip().lower() == "all":
            kinds = None
        elif args.kinds.strip():
            kinds = [k.strip() for k in args.kinds.split(",") if k.strip()]
        else:
            kinds = list(DEFAULT_HIERARCHY_FUNCTION_KINDS)
        area_prefixes = _dominant_area_prefixes(inv_path)
        selected = load_inventory_functions(
            inv_path,
            kinds=kinds,
            area_prefixes=area_prefixes or None,
        )
        if args.limit > 0:
            selected = selected[: args.limit]
        tags = [str(r.get("function") or "").upper() for r in selected if r.get("function")]

    if not tags:
        logger.error("[error] No inventory FUNCTIONs selected.")
        return 2

    all_tags = list(tags)

    combined_csv = out_dir / f"{base}.hierarchy_orchestrator.csv"

    # GOR still uses AI. Deterministic build_gor_hierarchy is a repair/fallback
    # only — do not skip Bedrock.
    report_json = json_path(out_dir, f"{base}.hierarchy_orchestrator_report.json")
    log_path = log_dir / "hierarchy-orchestrator.log"
    parts_dir = out_dir / "jsons" / "_orchestrator_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)

    combined_rows: List[Dict[str, str]] = []
    per_function_scores: List[Dict[str, Any]] = []

    if args.skip_existing and combined_csv.exists() and not args.score_only:
        existing_headers = set(csv_function_headers(read_hierarchy_csv(combined_csv)))
        before = len(tags)
        tags = [t for t in tags if t not in existing_headers]
        logger.info(f"[skip-existing] {before - len(tags)} already in {combined_csv.name}; {len(tags)} remaining")
        combined_rows = read_hierarchy_csv(combined_csv)

    logger.info(f"Selected {len(all_tags)} FUNCTION(s) from {inv_path.name} ({len(tags)} to run)")
    for i, t in enumerate(tags, 1):
        logger.info(f"  {i:2d}. {t}")

    if args.dry_run:
        logger.info("\n[dry-run] GT child counts:")
        for tag in all_tags:
            score = score_function(tag, [], gt_rows)
            eq = score["equipment"]
            sub = score["subequipment"]
            logger.info(f"  {tag}: in_gt={score['in_gt']}  "
                f"EQUIPMENT gt={eq['gt_count']}  SUB-EQUIPMENT gt={sub['gt_count']}")
        return 0

    if args.score_only:
        existing = read_hierarchy_csv(combined_csv)
        if not existing:
            logger.error(f"[error] --score-only but missing {combined_csv}")
            return 2
        combined_rows = existing
        logger.info(f"[score-only] scoring {combined_csv}")
    else:
        jobs = max(1, int(args.jobs or 1))
        if jobs > 1:
            logger.info(f"[parallel] running up to {jobs} FUNCTIONs concurrently")
        tag_results: Dict[str, Dict[str, Any]] = {}

        def _run_one(tag: str, index: int) -> Dict[str, Any]:
            tag_csv = parts_dir / f"{tag}.hierarchy.csv"
            tag_json = parts_dir / f"{tag}.hierarchy_ai.json"
            rc = run_hierarchy_for_tag(
                tag=tag,
                input_path=input_path,
                out_dir=out_dir,
                model_id=args.model_id,
                region=args.region,
                prompt_file=prompt_file,
                inventory_json=inv_path,
                per_tag_csv=tag_csv,
                per_tag_json=tag_json,
                reuse_shots=args.reuse_shots,
                # Parallel workers must never clear shared outputs.
                no_clean_prev=True if jobs > 1 else (index > 0) or args.reuse_shots or bool(combined_rows),
                aws_profile=args.aws_profile,
                crop_half=adapter.hierarchy_crop_half,
            )
            rows = rows_for_function(read_hierarchy_csv(tag_csv), tag)
            try:
                inv_data = json.loads(inv_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                inv_data = {}
            rows = adapter.repair_hierarchy(rows, inv_data)
            if rows:
                write_hierarchy_csv(tag_csv, rows)
            return {"function": tag, "exit_code": rc, "rows": rows}

        if jobs == 1:
            for idx, tag in enumerate(tags):
                result = _run_one(tag, idx)
                tag_results[tag] = result
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
                fut_to_tag = {
                    pool.submit(_run_one, tag, idx): tag
                    for idx, tag in enumerate(tags)
                }
                # Workers run in parallel; this loop is single-threaded —
                # merge and CSV writes happen sequentially as futures complete.
                for fut in concurrent.futures.as_completed(fut_to_tag):
                    tag = fut_to_tag[fut]
                    try:
                        tag_results[tag] = fut.result()
                    except Exception as exc:
                        logger.error(f"[error] {tag}: {exc}")
                        tag_results[tag] = {"function": tag, "exit_code": 99, "rows": [], "error": str(exc)}
                    r = tag_results[tag]
                    logger.info(f"[done] {tag} exit={r.get('exit_code')} rows={len(r.get('rows') or [])}")

        # Merge in original inventory/tag order for deterministic output.
        for tag in tags:
            result = tag_results.get(tag) or {"function": tag, "exit_code": 99, "rows": []}
            rc = int(result.get("exit_code", 99))
            tag_rows = result.get("rows") or []
            if not tag_rows:
                logger.warning(f"[warn] no rows for {tag} (exit={rc}); not appending stale CSV")
                per_function_scores.append(
                    {
                        "function": tag,
                        "error": f"no_rows_exit_{rc}",
                        "in_gt": False,
                        "equipment": {},
                        "subequipment": {},
                    }
                )
                continue
            combined_rows.extend(tag_rows)
            write_hierarchy_csv(combined_csv, combined_rows)
            scoreable_tag_rows = [r for r in tag_rows if (r.get("MASK") or "").strip().upper() != "ORPHAN"]
            score = score_function(tag, scoreable_tag_rows, gt_rows)
            per_function_scores.append(score)
            logger.info(format_function_report(score))

    # Mop-up and instrument injection — runs BEFORE scoring so that injected
    # instrument packages (HI/HS, KS, FV) are counted in the accuracy report.
    # Dedup/sanitize runs AFTER scoring: the "first occurrence wins" dedup would
    # hurt hits for tags that the AI correctly placed late in the file but also
    # placed (incorrectly) under an earlier function.  Scoring on the pre-dedup
    # CSV gives the true measure of AI placement quality.
    inventory_tags: "set[str]" = set()
    sml_like = eco.name in ("sml", "valmet")
    process_all = (not args.tags.strip()) and args.limit == 0
    if combined_csv.exists() and combined_csv.stat().st_size > 0:
        structural_path = json_path(out_dir, f"{base}.structural_dump.json")
        # Orphan/agitator mop-up is Valmet-only and dumps the whole sheet onto
        # whichever FUNCTIONs were selected — skip on GOR/KSD and on --tags/--limit subsets.
        if sml_like and process_all:
            _append_orphan_valve_rows(combined_csv, structural_path, inv_path)
            _append_agitator_equipment_rows(combined_csv, inv_path, structural_path)
            _append_missing_machine_functions(combined_csv, inv_path)
        if sml_like:
            inventory_tags = _load_inventory_tags(inv_path)
            _inject_instrument_packages(combined_csv, inventory_tags)

    # Final scores reflect mop-up + instrument injection, but NOT dedup.
    # Strip orphan rows (MASK=ORPHAN) — placed by proximity heuristic, not AI.
    combined_rows = read_hierarchy_csv(combined_csv) if combined_csv.exists() else combined_rows
    scoreable_rows = [r for r in combined_rows if (r.get("MASK") or "").strip().upper() != "ORPHAN"]
    per_function_scores = [score_function(tag, scoreable_rows, gt_rows) for tag in all_tags]
    for score in per_function_scores:
        logger.info(format_function_report(score))

    # Aggregate over selected functions only.
    # Accuracy = hit/gt per FUNCTION, then mean (extras ignored).
    eq_hit = eq_miss = eq_extra = eq_gt = 0
    sub_hit = sub_miss = sub_extra = sub_gt = 0
    for s in per_function_scores:
        if "error" in s:
            continue
        eq = s["equipment"]
        sub = s["subequipment"]
        eq_hit += eq["hit_count"]
        eq_miss += eq["miss_count"]
        eq_extra += eq["extra_count"]
        eq_gt += eq["gt_count"]
        sub_hit += sub["hit_count"]
        sub_miss += sub["miss_count"]
        sub_extra += sub["extra_count"]
        sub_gt += sub["gt_count"]

    eq_acc = macro_hit_accuracy(per_function_scores, "equipment")
    sub_acc = macro_hit_accuracy(per_function_scores, "subequipment")

    summary = {
        "tags": all_tags,
        "limit": args.limit,
        "model_id": args.model_id,
        "prompt_file": args.prompt_file,
        "gt": str(gt_path),
        "inventory": str(inv_path),
        "pred_csv": str(combined_csv),
        "accuracy_definition": "per_function hit/gt, then mean (extras ignored)",
        "equipment": {
            "gt_count": eq_gt,
            "hit": eq_hit,
            "miss": eq_miss,
            "extra": eq_extra,
            "accuracy": eq_acc,
        },
        "subequipment": {
            "gt_count": sub_gt,
            "hit": sub_hit,
            "miss": sub_miss,
            "extra": sub_extra,
            "accuracy": sub_acc,
        },
        "per_function": per_function_scores,
    }
    write_json(report_json, summary)

    logger.info("\n========== ORCHESTRATOR SUMMARY ==========")
    logger.info(f"functions scored: {len(all_tags)}")
    logger.info(f"EQUIPMENT:     hit={eq_hit}/{eq_gt}  miss={eq_miss}  extra={eq_extra}  "
        f"acc={eq_acc*100:.1f}% (mean of per-function hit/gt)")
    logger.info(f"SUB-EQUIPMENT: hit={sub_hit}/{sub_gt}  miss={sub_miss}  extra={sub_extra}  "
        f"acc={sub_acc*100:.1f}% (mean of per-function hit/gt)")
    logger.info(f"report: {report_json}")
    logger.info(f"combined CSV: {combined_csv}")
    log_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Dedup/sanitize runs AFTER scoring, for export quality only.
    # It drops phantom decimal tags and cross-function duplicates but does NOT
    # affect the accuracy numbers above.
    if combined_csv.exists() and combined_csv.stat().st_size > 0:
        cleaned = sanitize_hierarchy_rows(read_hierarchy_csv(combined_csv), inventory_tags)
        cleaned = _apply_registry_and_write(
            cleaned, drawing=base, out_dir=out_dir, dest=combined_csv
        )
        logger.info(f"[sanitize] hierarchy cleaned → {len(cleaned)} rows")

    if combined_csv.exists() and combined_csv.stat().st_size > 0:
        limit_s = str(args.limit if args.limit > 0 else 0)
        if not args.no_valve_classify:
            logger.info("\n---------- valve classify (tight crop + legend) ----------")
            run_valve_classify(
                input_path=input_path,
                out_dir=out_dir,
                hierarchy_csv=combined_csv,
                model_id=args.model_id,
                region=args.region,
                jobs=max(1, int(getattr(args, "jobs", 1) or 1)),
                skip_existing=bool(args.skip_existing),
                aws_profile=args.aws_profile,
            )
        if is_gor:
            valve_types_path = json_path(out_dir, f"{base}.valve_types.json")
            fn_id = tags[0] if tags else ""
            logger.info("\n---------- gor tipo mapping (TIPO_VALVOLA → SAP) ----------")
            _patch_gor_valve_types(inv_path, valve_types_path, fn_id)

        _run_sap_and_tree_exports(
            input_path=input_path,
            out_dir=out_dir,
            combined_csv=combined_csv,
            gt_path=gt_path,
            no_export_floc=args.no_export_floc,
            no_export_equipment=args.no_export_equipment,
            no_export_hierarchy_tree=args.no_export_hierarchy_tree,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
