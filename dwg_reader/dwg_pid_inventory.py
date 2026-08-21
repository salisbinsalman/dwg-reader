#!/usr/bin/env python3
"""
Comprehensive P&ID component inventory extractor (strict layer-first).

Produces dedicated sheets for tanks, process equipment, agitators, pumps,
motors, valves, control valves, instruments, symbols, fittings, terminals,
lines, interconnections, connections, pipe connectivity, and masks.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from dwg_reader.dwg_pure_dump import clear_previous_outputs, find_json, json_path, json_safe, safe_name, write_json
from dwg_reader.dwg_semantic_extract import (
    block_family,
    fmt_point,
    group_attributes,
    load_or_parse,
)
from dwg_reader.logutil import configure_logging, get_logger
from dwg_reader.tags import DN_RE, LINE_NUMBER_RE, parse_line_number

logger = get_logger(__name__)


PROXIMITY_TOL = 12.0

# Strict layer ownership for insert classification.
LAYER_TO_CATEGORY = {
    # SML standard layers
    "P-TANK_POS": ("tanks", "tank_symbol"),
    "P-PUMP_POS": ("pumps", "pump_symbol"),
    "P-PUMPS": ("pumps", "pump_symbol"),
    "P-MOTOR_POS": ("motors", "motor_symbol"),
    "P-AGITATOR_POS": ("agitators", "agitator_symbol"),
    "P-VALVEPOS": ("valves", "valve_symbol"),
    "P-CVPOS": ("control_valves", "control_valve_symbol"),
    "P-EQUIPMENT_POS": ("process_equipment", "equipment_symbol"),
    "P-EQUIPMENTS": ("process_equipment", "equipment_symbol"),
    "P-INSTRU": ("instruments", "instrument_symbol"),
    "P-INSTRPOS": ("instruments", "instrument_position"),
    "P-PTERMINAL_POS": ("terminals", "terminal_symbol"),
    "P-FITTINGS": ("fittings", "fitting_symbol"),
    "P-SYMB": ("symbols", "diagram_symbol"),
    "P-VENTS": ("ventilation", "vent_symbol"),
    "P-FAN_POS": ("ventilation", "fan_symbol"),
    "P-REVISIONS": ("revisions", "revision_marker"),
    "P-DELIVERY_LIMIT": ("delivery_limits", "delivery_limit"),
    "P-A-SHEET": ("sheet_graphics", "sheet_block"),
    "T-A-SHEET": ("sheet_graphics", "sheet_block"),
    "P-OTHER": ("other_inserts", "other"),
    "P-MARKBALL": ("other_inserts", "mark_ball"),
    "P-LINEPOS": ("line_markers", "line_annotation_block"),
    # Valmet/GOR standard layers (Italian engineering, "1-* GOR" naming convention)
    "1-VALVE TEXT GOR": ("valves", "valve_symbol"),
    "1-TAG AND INSTRUMENTS GOR": ("instruments", "instrument_symbol"),
    "1-EQUIPMENT GOR": ("process_equipment", "equipment_symbol"),
    "Revison 03": ("line_markers", "gor_pipe_id"),  # GOR Pipeno pipe-number blocks (typo is in the actual drawing)
}

# Layers that carry pipe/process line geometry in Valmet/GOR drawings.
GOR_PIPE_LAYERS = {
    "1-AIR GOR",
    "1-WATER GOR",
    "1-BACKPRESSURE GOR",
}

# Instrument tag pattern for GOR drawings: starts with 3 digits + letters + optional digits.
# Matches e.g. "168TC1", "168TT1", "168TA1", "168HC", "168P-410", "168P-410-M1".
GOR_INSTR_TAG_RE = re.compile(r"^\s*\d{3}[A-Z]{1,4}[\d\-]*[A-Z]?\d*\s*$", re.I)

# Plant FUNCTION parents match the GT hierarchy FUNCTION column taxonomy:
#   - equipment: vessels/pulpers (L), pumps (P), tanks (T)
#   - instruments: HI / HS / KJ / ES / XS (often split as letter + number on P&ID)
#   - lines: short line ids that are CMMS functional locations (esp. WFL hose lines)
FUNCTION_TAG_RE = re.compile(r"^\d{2}-\d{2}[LPT]\d{2,4}[A-Z]?$", re.I)
# Agitator equipment numbers (L401–L499 per Valmet PS-21) are EQUIPMENT under tanks, not FUNCTIONs.
FUNCTION_AGITATOR_TAG_RE = re.compile(r"^\d{2}-\d{2}L(4\d{2})$", re.I)
_AGITATOR_NUM_RE = re.compile(r"^\d{2}-\d{2}L(4\d{2})$", re.I)
EQUIP_TAG_RE = re.compile(r"^\d{2}-\d{2}[A-Z]\d{2,4}[A-Z]?$", re.I)
FUNCTION_INSTR_LETTERS = {"HI", "HS", "KJ", "ES", "XS"}
FUNCTION_LINE_TYPES = {"WFL", "WAF", "WFC", "PP"}
FUNCTION_LINE_AREA_PREFIXES = ("35-24-", "35-25-")
FUNCTION_EQUIP_CATEGORIES = ("tanks", "process_equipment", "pumps")  # not agitators
FUNCTION_TAG_LAYERS = {
    "P-TANK_POS",
    "P-EQUIPMENT_POS",
    "P-PUMP_POS",
    "P-MOTOR_POS",
    "P-AGITATOR_POS",
    "P-TEXT",
}
FUNCTION_DESC_LAYERS = {"P-TEXT", "P-EQUIPMENT_POS", "P-TANK_POS", "P-PUMP_POS"}
AREA_CODE_RE = re.compile(r"^\d{2}-\d{2}$")
LOOP_NUM_RE = re.compile(r"^\d{3,4}$")  # instrument loop numbers (not 2-digit sizes)
LINE_SHORT_RE = re.compile(r"^(\d{2}-\d{2}-\d{2,4})")
FULL_INSTR_TAG_RE = re.compile(
    r"^(\d{2}-\d{2})(HI|HS|KJ|ES|XS)-?(\d{2,4}[A-Z]?)$",
    re.I,
)
EQUIP_NAME_RE = re.compile(
    r"\b(PULPER|SCREEN|THICKENER|COUCH PIT|COLLECTION TANK|DUMP TOWER|WHITE WATER TOWER|"
    r"BROKE THICKENER|SLABBING|WINDER|REEL|SIZE PRESS|PRESS PULPER)\b",
    re.I,
)
AGITATOR_RE = re.compile(r"\bAGITATOR\b", re.I)
PUMP_LABEL_RE = re.compile(r"\b(GEAR BOX OIL PUMP|VACUUM PUMP|PUMP \(GENERAL\)|OIL PUMP)\b", re.I)
MOTOR_LABEL_RE = re.compile(r"\b(MOTOR POWER|MOTOR SPEED|MOTOR)\b", re.I)
TANK_LABEL_RE = re.compile(r"\b(CONDENSATE TANKS|DUMP TOWER|WHITE WATER TOWER)\b", re.I)
SKIP_TEXT = {
    "START", "STOP", "START/ STOP", "V", "E", "O", "R", "N", "D", "A1", "A2",
    "ST", "SS", "SV", "S1", "S2", "S3", "S4", "S5", "S6", "S1/ST1", "HOLD!",
    "LOCAL/REMOTE", "JOGGING", "INSTRU", "UTM", "DW",
}


def xyz(pt: Any) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    if not isinstance(pt, list) or len(pt) < 2:
        return None, None, None
    z = float(pt[2]) if len(pt) > 2 else 0.0
    return float(pt[0]), float(pt[1]), z


def dist2(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def point_key(x: float, y: float, precision: int = 3) -> str:
    return f"{round(x, precision)}|{round(y, precision)}"


def base_component(
    component_type: str,
    *,
    tag: Optional[str] = None,
    sub_type: Optional[str] = None,
    handle: Optional[str] = None,
    layer: Optional[str] = None,
    block_name: Optional[str] = None,
    insert: Any = None,
    rotation: Any = None,
    attrs: Optional[Dict[str, str]] = None,
    source: str = "",
    confidence: str = "high",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    x, y, z = xyz(insert)
    attrs = attrs or {}
    row = {
        "component_type": component_type,
        "sub_type": sub_type,
        "tag": tag or block_name,
        "block_name": block_name,
        "handle": handle,
        "layer": layer,
        "x": x,
        "y": y,
        "z": z,
        "position": fmt_point(insert),
        "rotation": rotation,
        "position_number": attrs.get("ANTPOS"),
        "description": attrs.get("TEKSTI1") or attrs.get("ANTNIMI") or attrs.get("TEKSTI2"),
        "reference": attrs.get("TEKSTI2"),
        "linked_diagram": attrs.get("KAAVIO"),
        "source": source,
        "confidence": confidence,
    }
    if extra:
        row.update(extra)
    return row


def classify_insert(ins: Dict[str, Any]) -> Optional[Tuple[str, str, str]]:
    """Return (category, sub_type, confidence) using layer-first rules."""
    layer = ins.get("layer") or ""
    name = (ins.get("name") or "").upper()

    if layer in LAYER_TO_CATEGORY:
        cat, sub = LAYER_TO_CATEGORY[layer]
        # Ventilation CVs stay under ventilation, not process control valves.
        if layer == "P-VENTS" and name.startswith("CVM"):
            return "ventilation", "vent_control_valve", "high"
        if layer == "P-VENTS" and name.startswith(("PRM", "CTV", "P7A")):
            return "ventilation", "vent_instrument_symbol", "high"
        return cat, sub, "high"

    # Fallback only for unknown layers with strong block cues.
    if name.startswith("CVM"):
        return "control_valves", block_family(name), "medium"
    # Keep insert_coverage complete on drawings with extra Autodesk layers.
    return "other_inserts", "unmapped_layer", "low"


def extract_from_inserts(structural: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for ins in structural.get("inserts", []):
        classified = classify_insert(ins)
        if not classified:
            continue
        comp_type, sub_type, confidence = classified
        attrs = group_attributes(ins.get("attributes", []))
        block_name = ins.get("name") or ""

        # GOR valve tag block stores the real tag and valve type in attributes.
        extra: Dict[str, Any] = {
            "xscale": ins.get("xscale"),
            "yscale": ins.get("yscale"),
            "attributes_json": json.dumps(json_safe(attrs), ensure_ascii=True),
        }
        if block_name == "TAG VALVOLA" and attrs.get("TAG_VALVOLA"):
            tag = attrs["TAG_VALVOLA"].strip()
            extra["valve_type"] = attrs.get("TIPO_VALVOLA", "").strip() or None
        else:
            tag = block_name

        buckets[comp_type].append(
            base_component(
                comp_type,
                tag=tag,
                sub_type=sub_type,
                handle=ins.get("handle"),
                layer=ins.get("layer"),
                block_name=block_name,
                insert=ins.get("insert"),
                rotation=ins.get("rotation"),
                attrs=attrs,
                source="insert",
                confidence=confidence,
                extra=extra,
            )
        )
    return buckets


def extract_text_labels(structural: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Supplementary labels only. Never used as primary inventory counts."""
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    seen: Set[Tuple[str, str, str]] = set()

    for t in structural.get("text_entities", []):
        text = (t.get("text") or "").strip()
        layer = t.get("layer") or ""
        if not text or text.upper() in SKIP_TEXT or len(text) < 4:
            continue
        # Never treat line numbers as component labels.
        if LINE_NUMBER_RE.match(text.upper()) or DN_RE.match(text):
            continue
        if "%%U" in text and "PUMP DATA" in text.upper():
            continue

        mapped: Optional[Tuple[str, str]] = None
        if AGITATOR_RE.search(text):
            mapped = ("agitators", "text_label")
        elif PUMP_LABEL_RE.search(text):
            mapped = ("pumps", "text_label")
        elif MOTOR_LABEL_RE.search(text) and "PUMP" not in text.upper():
            mapped = ("motors", "text_label")
        elif TANK_LABEL_RE.search(text) or (text.upper() == "TANK" and layer == "P-TANK_POS"):
            mapped = ("tanks", "text_label")
        elif EQUIP_NAME_RE.search(text):
            mapped = ("process_equipment", "text_label")

        if not mapped:
            continue
        cat, sub = mapped
        key = (cat, text.upper(), fmt_point(t.get("position")) or "")
        if key in seen:
            continue
        seen.add(key)
        buckets[cat].append(
            base_component(
                cat,
                tag=text,
                sub_type=sub,
                handle=t.get("handle"),
                layer=layer,
                insert=t.get("position"),
                rotation=t.get("rotation"),
                source="text_label",
                confidence="low",
            )
        )
    return buckets


def _is_agitator_equipment_tag(tag: str) -> bool:
    """True for Valmet L401–L499 agitator equipment numbers."""
    m = _AGITATOR_NUM_RE.match(re.sub(r"\s+", "", str(tag or "").strip()).upper())
    return bool(m and 401 <= int(m.group(1)) <= 499)


def _is_agitator_desc_noise(text: str) -> bool:
    """Skip sizes, codes, and catalog strings near agitator symbols."""
    raw = str(text or "").strip()
    if not raw or len(raw) <= 2:
        return True
    u = raw.upper()
    if u == "TANK":
        return False
    if re.match(r"^[\d.,\s%/]+$", raw):
        return True
    if re.match(r"^\d+[.,]?\d*\s*m", raw, re.I):
        return True
    # Catalog / vendor codes e.g. SFVPT-110-2, 2621 ADTPD
    if re.match(r"^[A-Z]{2,}\d", u.replace("-", "")):
        return True
    if re.match(r"^\d{3,}\s+[A-Z]{2,}", u):
        return True
    # Sheet / title noise often near couch pit
    if u in {"PRODUCTION", "CAPACITY", "DESIGN", "NOTES", "LEGEND"}:
        return True
    if EQUIP_TAG_RE.match(u.replace(" ", "")) or FUNCTION_TAG_RE.match(u.replace(" ", "")):
        return True
    if AGITATOR_RE.search(raw):
        return True
    return False


def _agitator_description(tag: str, desc_hits: List[Dict[str, Any]]) -> str:
    """Build EQKTX-style text: e.g. '35-24L404 BROKE REJECT AGITATOR TANK'."""
    # Prefer tank-layer labels (COUCH PIT, BROKE REJECT) over nearby P-TEXT noise.
    ordered = sorted(
        desc_hits,
        key=lambda h: (0 if h.get("layer") == "P-TANK_POS" else 1, float(h.get("distance") or 999)),
    )
    name_parts: List[str] = []
    has_tank = False
    for h in ordered:
        raw = str(h.get("text") or "").strip()
        if raw.upper() == "TANK":
            has_tank = True
            continue
        if _is_agitator_desc_noise(raw):
            continue
        name_parts.append(raw)
        if len(name_parts) >= 4:
            break
    name = " ".join(name_parts).strip()
    if name and has_tank:
        return f"{tag} {name} AGITATOR TANK"
    if name:
        return f"{tag} {name} AGITATOR"
    if has_tank:
        return f"{tag} AGITATOR TANK"
    return f"{tag} AGITATOR"


def bind_agitator_tags(
    inventory: Dict[str, List[Dict[str, Any]]],
    structural: Dict[str, Any],
) -> int:
    """Bind L401–L499 labels on P-AGITATOR_POS to agitator insert symbols.

    PPI agitator blocks store the block name as ``tag``; the real equipment
    number sits as nearby TEXT on ``P-AGITATOR_POS`` (often within ~10 units).
    Returns how many inserts received a new tag.
    """
    texts = structural.get("text_entities") or []
    used: Set[str] = set()
    for item in inventory.get("agitators") or []:
        if item.get("source") != "insert":
            continue
        existing = re.sub(r"\s+", "", str(item.get("tag") or "").strip()).upper()
        if _is_agitator_equipment_tag(existing):
            used.add(existing)
            continue

    bound = 0
    for item in inventory.get("agitators") or []:
        if item.get("source") != "insert":
            continue
        if item.get("x") is None or item.get("y") is None:
            continue
        existing = re.sub(r"\s+", "", str(item.get("tag") or "").strip()).upper()
        if _is_agitator_equipment_tag(existing):
            if not item.get("description"):
                desc_hits = _nearest_texts(
                    (float(item["x"]), float(item["y"])),
                    texts,
                    max_dist=80.0,
                    layers={"P-TANK_POS", "P-TEXT"},
                    limit=15,
                )
                item["description"] = _agitator_description(existing, desc_hits)
            continue

        pos = (float(item["x"]), float(item["y"]))
        tag_hits = _nearest_texts(
            pos,
            texts,
            max_dist=40.0,
            layers={"P-AGITATOR_POS"},
            predicate=lambda s: _is_agitator_equipment_tag(s.replace(" ", "")),
            limit=8,
        )
        resolved = None
        for h in tag_hits:
            cand = h["text"].replace(" ", "").upper()
            if cand in used:
                continue
            resolved = cand
            break
        if not resolved:
            continue

        used.add(resolved)
        item["tag"] = resolved
        item["confidence"] = "high"
        desc_hits = _nearest_texts(
            pos,
            texts,
            max_dist=80.0,
            layers={"P-TANK_POS", "P-TEXT"},
            limit=15,
        )
        item["description"] = _agitator_description(resolved, desc_hits)
        item["nearby_tags"] = "; ".join(h["text"] for h in tag_hits[:5])
        bound += 1
    return bound


def extract_gor_instrument_texts(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract GOR instrument tags from TEXT entities on the GOR instruments layer.

    GOR drawings don't embed instrument tags in block attributes; instead, each
    instrument is labelled by a nearby TEXT entity (e.g. "168TC1", "168P-410").
    This supplements the LOOPDCS-block records with the actual tag strings.
    """
    rows: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for t in structural.get("text_entities", []):
        if t.get("layer") != "1-TAG AND INSTRUMENTS GOR":
            continue
        text = (t.get("text") or "").strip()
        if not text:
            continue
        # Skip pure loop numbers (3-4 digits with no letters) and short words.
        if re.match(r"^\d{3,4}$", text) or len(text) < 4:
            continue
        if not GOR_INSTR_TAG_RE.match(text):
            continue
        key = text.upper()
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            base_component(
                "instruments",
                tag=text,
                sub_type="gor_instrument_tag",
                handle=t.get("handle"),
                layer=t.get("layer"),
                insert=t.get("position"),
                source="text_label",
                confidence="high",
            )
        )
    return rows


def extract_gor_valve_texts(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract GOR Code 03/13 valve tags from TEXT entities on 1-VALVE TEXT GOR.

    In Code 03/13 drawings valves are labelled as plain TEXT entities (e.g. "162KV3-575",
    "162V-001") rather than TAG VALVOLA INSERT blocks used in Code 14.
    """
    rows: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for t in structural.get("text_entities", []):
        if t.get("layer") != "1-VALVE TEXT GOR":
            continue
        text = (t.get("text") or "").strip()
        if not text or len(text) < 4:
            continue
        if re.match(r"^\d{3,4}$", text):
            continue
        if not GOR_INSTR_TAG_RE.match(text):
            continue
        key = text.upper()
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            base_component(
                "valves",
                tag=text,
                sub_type="gor_valve_tag",
                handle=t.get("handle"),
                layer=t.get("layer"),
                insert=t.get("position"),
                source="text_label",
                confidence="high",
            )
        )
    return rows


def extract_lines(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for t in structural.get("text_entities", []):
        if t.get("layer") != "P-LINEPOS":
            continue
        text = (t.get("text") or "").strip().upper()
        if not text or text in seen:
            continue
        seen.add(text)
        parsed = parse_line_number(text)
        x, y, z = xyz(t.get("position"))
        rows.append(
            {
                "component_type": "lines",
                "line_number": parsed.get("line_number"),
                "plant_area": parsed.get("plant_area"),
                "line_sequence": parsed.get("line_seq"),
                "line_type": parsed.get("line_type"),
                "nominal_size": parsed.get("size") or None,
                "pipe_class": parsed.get("pipe_class"),
                "parsed": bool(parsed.get("parsed")),
                "handle": t.get("handle"),
                "layer": t.get("layer"),
                "x": x,
                "y": y,
                "z": z,
                "position": fmt_point(t.get("position")),
                "source": "line_label",
                "confidence": "high" if parsed.get("parsed") else "medium",
            }
        )
    return rows


def extract_interconnections(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for ins in structural.get("inserts", []):
        name = ins.get("name") or ""
        attrs = group_attributes(ins.get("attributes", []))
        if not (attrs.get("TEKSTI1") and attrs.get("KAAVIO")):
            continue
        if name.upper() not in ("KIPAS_VIITTA",) and not name.startswith("*"):
            continue
        rows.append(
            {
                "component_type": "interconnections",
                "connector_block": name,
                "from_process": attrs.get("TEKSTI1"),
                "to_reference": attrs.get("TEKSTI2"),
                "linked_diagram": attrs.get("KAAVIO"),
                "handle": ins.get("handle"),
                "layer": ins.get("layer"),
                "position": fmt_point(ins.get("insert")),
                "source": "off_page_connector",
                "confidence": "high",
            }
        )
    return rows


def extract_masks(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for e in structural.get("entities", []):
        layer = e.get("layer") or ""
        if layer != "P-MASS1":
            continue
        geom = e.get("geometry") or {}
        pts = geom.get("points_xyseb") or geom.get("vertices") or []
        bbox = None
        if pts:
            xs = [p[0] for p in pts if len(p) >= 2]
            ys = [p[1] for p in pts if len(p) >= 2]
            if xs and ys:
                bbox = f"{min(xs):.3f},{min(ys):.3f},{max(xs):.3f},{max(ys):.3f}"
        rows.append(
            {
                "component_type": "masks",
                "mask_type": "mass_balance_region",
                "handle": e.get("handle"),
                "entity_type": e.get("type"),
                "layer": layer,
                "vertex_count": len(pts),
                "closed": geom.get("closed"),
                "bbox": bbox,
                "geometry_json": json.dumps(json_safe(geom), ensure_ascii=True),
                "source": "geometry",
                "confidence": "high",
            }
        )
    return rows


def entity_endpoints(entity: Dict[str, Any]) -> List[Tuple[float, float]]:
    g = entity.get("geometry") or {}
    t = entity.get("type")
    pts: List[Tuple[float, float]] = []
    if t == "LINE":
        for key in ("start", "end"):
            p = g.get(key)
            if isinstance(p, list) and len(p) >= 2:
                pts.append((float(p[0]), float(p[1])))
    elif t == "LWPOLYLINE":
        for p in g.get("points_xyseb", []):
            if len(p) >= 2:
                pts.append((float(p[0]), float(p[1])))
        if pts and g.get("closed"):
            pts.append(pts[0])
    elif t == "POLYLINE":
        for p in g.get("vertices", []):
            if isinstance(p, list) and len(p) >= 2:
                pts.append((float(p[0]), float(p[1])))
    return pts


def extract_pipe_segments(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    pipe_layers = {
        # SML standard pipe layers
        "P-FITTINGS",
        "P-LINEPOS",
        "P-EQUIPMENTS",
        "P-WATER",
        "P-SEALING_WATER",
        "P-COOLING_WATER",
        "P-FILTERED_WATER",
        "P-WHITE_WATER",
        "P-REJECT",
        "P-AIR",
        "P-MASS1",
    } | GOR_PIPE_LAYERS
    for e in structural.get("entities", []):
        if e.get("type") not in ("LINE", "LWPOLYLINE", "POLYLINE"):
            continue
        layer = e.get("layer") or ""
        if layer not in pipe_layers:
            continue
        pts = entity_endpoints(e)
        if len(pts) < 2:
            continue
        rows.append(
            {
                "component_type": "pipe_segments",
                "handle": e.get("handle"),
                "entity_type": e.get("type"),
                "layer": layer,
                "start_x": pts[0][0],
                "start_y": pts[0][1],
                "end_x": pts[-1][0],
                "end_y": pts[-1][1],
                "vertex_count": len(pts),
                "length": sum(
                    math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
                    for i in range(len(pts) - 1)
                ),
                "geometry_json": json.dumps(json_safe(e.get("geometry")), ensure_ascii=True),
                "confidence": "high",
            }
        )
    return rows


def build_connectivity(
    components: List[Dict[str, Any]],
    pipe_segments: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    # Only high-confidence insert components participate in snap connectivity.
    comp_points: List[Tuple[str, str, float, float]] = []
    for c in components:
        if c.get("source") != "insert" or c.get("confidence") != "high":
            continue
        x, y = c.get("x"), c.get("y")
        if x is None or y is None:
            continue
        comp_points.append((c.get("component_type", ""), c.get("tag") or c.get("handle", ""), float(x), float(y)))

    endpoint_map: Dict[str, List[str]] = defaultdict(list)
    connections: List[Dict[str, Any]] = []
    pipe_connectivity: List[Dict[str, Any]] = []
    tol2 = PROXIMITY_TOL ** 2

    for seg in pipe_segments:
        seg_id = seg.get("handle")
        ends = [
            (seg.get("start_x"), seg.get("start_y"), "start"),
            (seg.get("end_x"), seg.get("end_y"), "end"),
        ]
        linked: List[str] = []
        for ex, ey, end_name in ends:
            if ex is None or ey is None:
                continue
            key = point_key(float(ex), float(ey))
            endpoint_map[key].append(seg_id)

            best = None
            best_d = tol2
            for ctype, ctag, cx, cy in comp_points:
                d = dist2((float(ex), float(ey)), (cx, cy))
                if d <= best_d:
                    best_d = d
                    best = (ctype, ctag, d)
            if best:
                ctype, ctag, d = best
                linked.append(f"{ctype}:{ctag}")
                connections.append(
                    {
                        "component_type": "connections",
                        "pipe_handle": seg_id,
                        "pipe_layer": seg.get("layer"),
                        "endpoint": end_name,
                        "endpoint_x": ex,
                        "endpoint_y": ey,
                        "connected_component_type": ctype,
                        "connected_tag": ctag,
                        "connection_method": "nearest_proximity",
                        "distance": math.sqrt(d),
                        "confidence": "medium" if d > 1e-6 else "high",
                    }
                )

        pipe_connectivity.append(
            {
                "component_type": "pipe_connectivity",
                "pipe_handle": seg_id,
                "layer": seg.get("layer"),
                "entity_type": seg.get("entity_type"),
                "start_x": seg.get("start_x"),
                "start_y": seg.get("start_y"),
                "end_x": seg.get("end_x"),
                "end_y": seg.get("end_y"),
                "length": seg.get("length"),
                "connected_components": "; ".join(sorted(set(linked))),
                "connection_count": len(set(linked)),
                "confidence": "medium",
            }
        )

    for key, seg_ids in endpoint_map.items():
        uniq = sorted(set(seg_ids))
        if len(uniq) < 2:
            continue
        x_str, y_str = key.split("|")
        connections.append(
            {
                "component_type": "connections",
                "pipe_handle": "|".join(uniq),
                "pipe_layer": None,
                "endpoint": "junction",
                "endpoint_x": float(x_str),
                "endpoint_y": float(y_str),
                "connected_component_type": "pipe_junction",
                "connected_tag": "|".join(uniq),
                "connection_method": "shared_endpoint",
                "distance": 0.0,
                "confidence": "high",
            }
        )

    return connections, pipe_connectivity


def merge_buckets(*dicts: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for d in dicts:
        for k, v in d.items():
            out[k].extend(v)
    return dict(out)


def primary_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [r for r in rows if r.get("source") == "insert" and r.get("confidence") == "high"]


def _nearest_texts(
    pos: Tuple[float, float],
    texts: List[Dict[str, Any]],
    *,
    max_dist: float,
    layers: Optional[Set[str]] = None,
    predicate=None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    scored: List[Dict[str, Any]] = []
    for t in texts:
        if layers and t.get("layer") not in layers:
            continue
        x, y, _ = xyz(t.get("position"))
        if x is None or y is None:
            continue
        text = (t.get("text") or "").strip()
        if not text:
            continue
        if predicate and not predicate(text):
            continue
        d = math.hypot(x - pos[0], y - pos[1])
        if d <= max_dist:
            scored.append({"text": text, "layer": t.get("layer"), "distance": round(d, 3)})
    scored.sort(key=lambda r: r["distance"])
    return scored[:limit]


def _line_size_and_type(raw: str, line_type: str) -> Tuple[str, int]:
    raw = raw.strip().upper()
    lt = (line_type or "").upper()
    if not lt:
        mm = re.match(r"^\d{2}-\d{2}-\d{2,4}(?:/\d+)?-([A-Z]+)", raw)
        lt = mm.group(1) if mm else ""
    size = -1
    if lt:
        sm = re.search(rf"-{re.escape(lt)}-(\d*)-", raw)
        if sm:
            size = int(sm.group(1)) if sm.group(1) else 0  # 0 = blank DN
    return lt, size


def build_functions(
    inventory: Dict[str, List[Dict[str, Any]]],
    structural: Dict[str, Any],
) -> List[Dict[str, Any]]:
    from dwg_reader.pid_functions import build_functions as _build_functions

    return _build_functions(inventory, structural)


_GOR_LAYERS = {"1-VALVE TEXT GOR", "1-TAG AND INSTRUMENTS GOR", "1-EQUIPMENT GOR"}
_WU_RE = re.compile(r"^WU\d+$", re.I)


def _is_gor_structural(structural: Dict[str, Any]) -> bool:
    return any(ins.get("layer") in _GOR_LAYERS for ins in structural.get("inserts", []))


_GOR_PREFIX_RE = re.compile(r"^(\d{3})[A-Z]", re.I)


def _detect_gor_unit_id(structural: Dict[str, Any]) -> Optional[str]:
    # First: explicit WU-format function label (Code 14)
    for t in structural.get("text_entities", []):
        if t.get("layer") not in ("1-AIR GOR", "1-TAG AND INSTRUMENTS GOR", "1-FLOW TEXT GOR"):
            continue
        text = (t.get("text") or "").strip()
        if _WU_RE.match(text):
            return text.upper()
    # Fallback: derive function ID from dominant 3-digit tag prefix (Code 03/13)
    # e.g. "162KV3-575" → "162", "162V-001" → "162"
    prefix_count: Dict[str, int] = {}
    for t in structural.get("text_entities", []):
        if t.get("layer") not in ("1-VALVE TEXT GOR", "1-TAG AND INSTRUMENTS GOR"):
            continue
        text = (t.get("text") or "").strip()
        m = _GOR_PREFIX_RE.match(text)
        if m:
            p = m.group(1)
            prefix_count[p] = prefix_count.get(p, 0) + 1
    if prefix_count:
        return max(prefix_count, key=lambda k: prefix_count[k])
    return None


def extract_gor_pipe_ids(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract pipe IDs from GOR Pipeno INSERT blocks (PIPEID + PIPEDATA attributes)."""
    rows: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for ins in structural.get("inserts", []):
        if ins.get("name") != "Pipeno":
            continue
        attrs = group_attributes(ins.get("attributes", []))
        pipe_id = (attrs.get("PIPEID") or "").strip()
        pipe_data = (attrs.get("PIPEDATA") or "").strip()
        if not pipe_id:
            continue
        key = pipe_id.upper()
        if key in seen:
            continue
        seen.add(key)
        # PIPEDATA: "65-W38-VE10H2A" → size=65, pipe_class=W38-VE10H2A
        size_str = ""
        pipe_class = pipe_data
        if pipe_data:
            first, *rest = pipe_data.split("-", 1)
            if first.isdigit():
                size_str = first
                pipe_class = rest[0] if rest else ""
        x, y, z = xyz(ins.get("insert"))
        rows.append({
            "component_type": "lines",
            "line_number": pipe_id,
            "plant_area": None,
            "line_sequence": None,
            "line_type": "GOR_PIPE",
            "nominal_size": size_str or None,
            "pipe_class": pipe_class or None,
            "parsed": True,
            "handle": ins.get("handle"),
            "layer": ins.get("layer"),
            "x": x,
            "y": y,
            "z": z,
            "position": fmt_point(ins.get("insert")),
            "source": "gor_pipe_id",
            "confidence": "high",
        })
    return rows


def build_gor_functions(
    inventory: Dict[str, List[Dict[str, Any]]],
    structural: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Emit a FUNCTION row for each GOR ventil unit (e.g. WU12) found in the drawing."""
    if not _is_gor_structural(structural):
        return []
    unit_id = _detect_gor_unit_id(structural)
    if not unit_id:
        return []
    x: Optional[float] = None
    y: Optional[float] = None
    for cat in ("valves", "instruments", "process_equipment"):
        for item in inventory.get(cat) or []:
            if item.get("x") is not None and item.get("y") is not None:
                x, y = float(item["x"]), float(item["y"])
                break
        if x is not None:
            break
    # Count all valves (inserts for Code 14, text_label for Code 03/13)
    valve_count = sum(1 for v in (inventory.get("valves") or []) if v.get("tag") and str(v.get("tag")).upper() != "TAG VALVOLA")
    return [{
        "function": unit_id,
        "kind": "equipment",
        "category": "process_equipment",
        "block_name": "",
        "handle": "",
        "layer": "1-AIR GOR",
        "x": x or 0.0,
        "y": y or 0.0,
        "z": 0.0,
        "description": f"{unit_id} VENTIL UNIT ({valve_count} VLV)",
        "nearby_tags": unit_id,
        "confidence": "high",
        "source": "cad",
    }]


def build_inventory(structural: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    inserts = extract_from_inserts(structural)
    labels = extract_text_labels(structural)
    gor_instr = extract_gor_instrument_texts(structural)
    gor_valves = extract_gor_valve_texts(structural)
    buckets = merge_buckets(inserts, labels)
    if gor_instr:
        buckets["instruments"] = buckets.get("instruments", []) + gor_instr
    if gor_valves:
        buckets["valves"] = buckets.get("valves", []) + gor_valves

    lines = extract_lines(structural) + extract_gor_pipe_ids(structural)
    interconnections = extract_interconnections(structural)
    masks = extract_masks(structural)
    pipe_segments = extract_pipe_segments(structural)

    primary_components: List[Dict[str, Any]] = []
    for key in (
        "tanks",
        "process_equipment",
        "agitators",
        "pumps",
        "motors",
        "valves",
        "control_valves",
        "instruments",
        "fittings",
        "terminals",
    ):
        primary_components.extend(primary_rows(buckets.get(key, [])))

    connections, pipe_connectivity = build_connectivity(primary_components, pipe_segments)

    inventory: Dict[str, List[Dict[str, Any]]] = {
        "tanks": buckets.get("tanks", []),
        "process_equipment": buckets.get("process_equipment", []),
        "agitators": buckets.get("agitators", []),
        "pumps": buckets.get("pumps", []),
        "motors": buckets.get("motors", []),
        "valves": buckets.get("valves", []),
        "control_valves": buckets.get("control_valves", []),
        "instruments": buckets.get("instruments", []),
        "fittings": buckets.get("fittings", []),
        "terminals": buckets.get("terminals", []),
        "symbols": buckets.get("symbols", []),
        "ventilation": buckets.get("ventilation", []),
        "line_markers": buckets.get("line_markers", []),
        "revisions": buckets.get("revisions", []),
        "delivery_limits": buckets.get("delivery_limits", []),
        "sheet_graphics": buckets.get("sheet_graphics", []),
        "other_inserts": buckets.get("other_inserts", []),
        "lines": lines,
        "interconnections": interconnections,
        "masks": masks,
        "connections": connections,
        "pipe_connectivity": pipe_connectivity,
        "pipe_segments": pipe_segments,
        "primary_components": primary_components,
    }
    # Bind L401–L499 labels to PPI agitator inserts before FUNCTION extraction.
    bind_agitator_tags(inventory, structural)
    inventory["functions"] = build_functions(inventory, structural)
    if not inventory["functions"]:
        inventory["functions"] = build_gor_functions(inventory, structural)
    return inventory


def validate_inventory(structural: Dict[str, Any], inventory: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    insert_by_layer = Counter(i.get("layer") for i in structural.get("inserts", []))
    checks = {
        "tanks": ["P-TANK_POS"],
        "pumps": ["P-PUMP_POS", "P-PUMPS"],
        "motors": ["P-MOTOR_POS"],
        "agitators": ["P-AGITATOR_POS"],
        "valves": ["P-VALVEPOS", "1-VALVE TEXT GOR"],
        "control_valves": ["P-CVPOS"],
        "process_equipment": ["P-EQUIPMENT_POS", "P-EQUIPMENTS", "1-EQUIPMENT GOR"],
        "instruments": ["P-INSTRU", "P-INSTRPOS", "1-TAG AND INSTRUMENTS GOR"],
        "fittings": ["P-FITTINGS"],
        "terminals": ["P-PTERMINAL_POS"],
        "symbols": ["P-SYMB"],
        "ventilation": ["P-VENTS", "P-FAN_POS"],
        "line_markers": ["P-LINEPOS", "Revison 03"],
        "revisions": ["P-REVISIONS"],
        "delivery_limits": ["P-DELIVERY_LIMIT"],
        "sheet_graphics": ["P-A-SHEET", "T-A-SHEET"],
        "other_inserts": ["P-OTHER", "P-MARKBALL"],
    }

    report_rows = []
    all_pass = True
    claimed_layers = {l for cat, layers in checks.items() if cat != "other_inserts" for l in layers}
    for cat, layers in checks.items():
        if cat == "other_inserts":
            # Include explicit other layers plus any insert layer not claimed elsewhere
            # (matches classify_insert fallback → other_inserts).
            gt = sum(
                n
                for layer, n in insert_by_layer.items()
                if layer in layers or layer not in claimed_layers
            )
        else:
            gt = sum(insert_by_layer[l] for l in layers)
        inv_insert = sum(1 for r in inventory.get(cat, []) if r.get("source") == "insert")
        inv_text = sum(1 for r in inventory.get(cat, []) if r.get("source") == "text_label")
        ok = inv_insert == gt
        all_pass = all_pass and ok
        report_rows.append(
            {
                "category": cat,
                "ground_truth_inserts": gt,
                "inventory_inserts": inv_insert,
                "inventory_text_labels": inv_text,
                "delta_inserts": inv_insert - gt,
                "pass": ok,
            }
        )

    line_gt = {
        (t.get("text") or "").strip().upper()
        for t in structural.get("text_entities", [])
        if t.get("layer") == "P-LINEPOS" and (t.get("text") or "").strip()
    }
    # GOR: Pipeno INSERT blocks carry PIPEID attribute (not text entities)
    for _ins in structural.get("inserts", []):
        if _ins.get("name") == "Pipeno":
            _attrs = group_attributes(_ins.get("attributes", []))
            _pid = (_attrs.get("PIPEID") or "").strip().upper()
            if _pid:
                line_gt.add(_pid)
    line_inv = {r.get("line_number") for r in inventory.get("lines", [])}
    lines_ok = line_gt == line_inv
    all_pass = all_pass and lines_ok
    report_rows.append(
        {
            "category": "lines",
            "ground_truth_inserts": len(line_gt),
            "inventory_inserts": len(line_inv),
            "inventory_text_labels": sum(1 for r in inventory.get("lines", []) if not r.get("parsed")),
            "delta_inserts": len(line_inv) - len(line_gt),
            "pass": lines_ok,
        }
    )

    mask_gt = sum(1 for e in structural.get("entities", []) if e.get("layer") == "P-MASS1")
    mask_inv = len(inventory.get("masks", []))
    masks_ok = mask_gt == mask_inv
    all_pass = all_pass and masks_ok
    report_rows.append(
        {
            "category": "masks",
            "ground_truth_inserts": mask_gt,
            "inventory_inserts": mask_inv,
            "inventory_text_labels": 0,
            "delta_inserts": mask_inv - mask_gt,
            "pass": masks_ok,
        }
    )

    # Instrument pollution check: instruments must only come from instru layers
    bad_instr = [
        r for r in inventory.get("instruments", [])
        if r.get("source") == "insert"
        and r.get("layer") not in ("P-INSTRU", "P-INSTRPOS", "1-TAG AND INSTRUMENTS GOR")
    ]
    valve_fp = [
        r for r in inventory.get("valves", [])
        if r.get("source") == "text_label" and LINE_NUMBER_RE.match((r.get("tag") or "").upper())
    ]
    pollution_ok = len(bad_instr) == 0 and len(valve_fp) == 0
    all_pass = all_pass and pollution_ok
    report_rows.append(
        {
            "category": "pollution_checks",
            "ground_truth_inserts": 0,
            "inventory_inserts": len(bad_instr),
            "inventory_text_labels": len(valve_fp),
            "delta_inserts": len(bad_instr) + len(valve_fp),
            "pass": pollution_ok,
            "notes": f"bad_instruments={len(bad_instr)}; valve_line_number_fp={len(valve_fp)}",
        }
    )

    # Full insert coverage: every insert handle must appear in exactly one category sheet.
    classified_handles = set()
    handle_cats = defaultdict(set)
    coverage_cats = [
        "tanks", "process_equipment", "agitators", "pumps", "motors", "valves",
        "control_valves", "instruments", "fittings", "terminals", "symbols",
        "ventilation", "line_markers", "revisions", "delivery_limits",
        "sheet_graphics", "other_inserts",
    ]
    for cat in coverage_cats:
        for r in inventory.get(cat, []):
            if r.get("source") == "insert" and r.get("handle"):
                classified_handles.add(r["handle"])
                handle_cats[r["handle"]].add(cat)
    all_handles = {i.get("handle") for i in structural.get("inserts", []) if i.get("handle")}
    missing = all_handles - classified_handles
    duplicates = {h: sorted(cats) for h, cats in handle_cats.items() if len(cats) > 1}
    coverage_ok = len(missing) == 0 and len(duplicates) == 0
    all_pass = all_pass and coverage_ok
    report_rows.append(
        {
            "category": "insert_coverage",
            "ground_truth_inserts": len(all_handles),
            "inventory_inserts": len(classified_handles),
            "inventory_text_labels": len(missing),
            "delta_inserts": len(classified_handles) - len(all_handles),
            "pass": coverage_ok,
            "notes": f"missing={len(missing)}; cross_category_dups={len(duplicates)}",
        }
    )

    return {
        "all_pass": all_pass,
        "checks": report_rows,
        "counts": {k: len(v) for k, v in inventory.items()},
        "missing_insert_handles": sorted(missing)[:50],
        "cross_category_duplicates": duplicates,
    }


def export_inventory_workbook(
    inventory: Dict[str, List[Dict[str, Any]]],
    validation: Dict[str, Any],
    out_path: Path,
) -> None:
    import pandas as pd

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Put functions first so it is easy to find in Excel.
    sheet_order = ["functions"] + [k for k in inventory.keys() if k != "functions"]
    summary = [{"sheet": k, "row_count": len(inventory.get(k) or [])} for k in sheet_order]
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for sheet in sheet_order:
            rows = inventory.get(sheet) or []
            pd.DataFrame(rows if rows else [{"note": "empty"}]).to_excel(
                writer, sheet_name=sheet[:31], index=False
            )
        pd.DataFrame(summary).to_excel(writer, sheet_name="summary", index=False)
        pd.DataFrame(validation.get("checks", [])).to_excel(writer, sheet_name="validation", index=False)


def main() -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="Strict P&ID component inventory extractor")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument(
        "--no-clean-prev",
        action="store_true",
        help="Keep previous inventory outputs instead of clearing them first.",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    base = safe_name(input_path)
    if not args.no_clean_prev:
        clear_previous_outputs(
            out_dir,
            base,
            suffixes=(
                ".pid_inventory.xlsx",
                ".pid_inventory.json",
                ".pid_validation.json",
            ),
        )

    structural, source = load_or_parse(input_path, out_dir, refresh=args.refresh)
    logger.info(f"[1/4] Loaded structural data ({source})")

    inventory = build_inventory(structural)
    logger.info("[2/4] Inventory counts:")
    for k, v in inventory.items():
        logger.info(f"  - {k}: {len(v)}")
    funcs = inventory.get("functions") or []
    logger.info(f"  functions (unique): {len(funcs)}")
    by_kind: Dict[str, int] = {}
    for r in funcs:
        by_kind[r.get("kind") or "unknown"] = by_kind.get(r.get("kind") or "unknown", 0) + 1
    if by_kind:
        logger.info("    by kind: " + ", ".join(f"{k}={v}" for k, v in sorted(by_kind.items())))
    logger.info("    source: cad")
    if funcs:
        logger.info("    sample: " + ", ".join(r["function"] for r in funcs[:10]) + ("…" if len(funcs) > 10 else ""))

    validation = validate_inventory(structural, inventory)
    logger.info(f"[3/4] Validation all_pass={validation['all_pass']}")
    for row in validation["checks"]:
        mark = "PASS" if row.get("pass") else "FAIL"
        logger.info(f"  [{mark}] {row['category']}: gt={row['ground_truth_inserts']} "
            f"inserts={row['inventory_inserts']} text={row['inventory_text_labels']} "
            f"delta={row['delta_inserts']}")

    xlsx_out = out_dir / f"{base}.pid_inventory.xlsx"
    json_out = json_path(out_dir, f"{base}.pid_inventory.json")
    report_out = json_path(out_dir, f"{base}.pid_validation.json")
    export_inventory_workbook(inventory, validation, xlsx_out)
    write_json(json_out, inventory)
    write_json(report_out, validation)
    logger.info(f"[4/4] Wrote {xlsx_out}")
    logger.info(f"[4/4] Wrote {json_out}")
    logger.info(f"[4/4] Wrote {report_out}")
    return 0 if validation["all_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
