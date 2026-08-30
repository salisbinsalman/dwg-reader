#!/usr/bin/env python3
"""
Viewer-style DWG screenshots → Bedrock vision → hierarchy CSV.

There is no AutoCAD/TrueView GUI on this Mac. Screenshots are produced by:
  ODA (via ezdxf.odafc) reading the DWG + PyMuPDF backend rasterizing a local window
  — the same drawing engine path ODA viewers use, not the old schematic scatter plot.

AI returns hierarchy rows for:
  ORDER, SITE, LINE, PROCESS, SUB-PROCESS, FUNCTION, EQUIPMENT, SUB-EQUIPMENT, MASK
"""

from __future__ import annotations

import dwg_reader.dwg_warn as dwg_warn  # noqa: F401 — silence boto3 Python 3.9 deprecation noise

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dwg_reader.config import DEFAULT_MODEL_ID, HIERARCHY_PROMPT_FILE, LEGEND_PATH
from dwg_reader.dwg_floc_context import (
    DEFAULT_FLOC_CONTEXT,
    build_tplnr,
    description_from_nearby,
    floc_paths_for_function,
    load_floc_context_for_input,
    merge_floc_context,
    normalize_pltxt,
)
from dwg_reader.dwg_prompts import load_prompt
from dwg_reader.dwg_pure_dump import (
    clear_evidence_outputs,
    clear_previous_outputs,
    configure_odafc,
    evidence_dir,
    find_json,
    json_path,
    logs_dir,
    safe_name,
    write_json,
)
from dwg_reader.io import load_json
from dwg_reader.logutil import configure_logging, get_logger
from dwg_reader.models import CSV_COLUMNS
from dwg_reader.tags import normalize_tag

logger = get_logger(__name__)

DEFAULT_SUB_PROCESS = "BR1"
TAG_TOKEN_RE = re.compile(
    r"\b(?:\d{1,3}-\d{1,3}[A-Z0-9][A-Z0-9./-]*|\d{3}[A-Z]{1,4}-?\d+[A-Z0-9.-]*|\d{3}-ST\d+|\d{3}ST-\d+)\b",
    re.IGNORECASE,
)
# Require a sequence number so split fragments (168TI, 168PI, 168HC) are dropped.
_TISSUE_HIER_TAG_RE = re.compile(
    r"^(?:\d{3}[A-Z]{1,4}-?\d+[A-Z0-9.-]*|\d{3}-ST\d+|\d{3}ST-\d+)$",
    re.I,
)
_WU_FN_RE = re.compile(r"^WU\d+$", re.I)
# Matches plain line tags like 35-24-032 or 35-24-1089 (no letter prefix)
_LINE_FN_RE = re.compile(r"^\d{2}-\d{2}-\d+$")

PRIMARY_CATEGORIES = {"tanks", "process_equipment", "pumps", "agitators"}
PARENT_PRIORITY = {
    "tanks": 0,
    "process_equipment": 1,
    "pumps": 2,
    "agitators": 3,
}


def _line_network_context(
    tag: str,
    inventory: Dict[str, Any],
) -> Tuple[str, List[str]]:
    """Build structured line-branch context for LINE-type FUNCTIONs.

    Returns (context_text, extra_candidates).  context_text is empty and
    extra_candidates is [] when tag is not a plain line tag (35-24-NNN).

    Uses fluid-code (line_type) matching: branches of a distribution header
    share its pipe specification.  Function-level headers (other 35-24-NNN
    tags being scored by the orchestrator) are excluded so only leaf branches
    appear as candidates.
    """
    want = normalize_tag(tag)
    if not _LINE_FN_RE.match(want):
        return "", []

    area = want[:5]  # "35-24"
    # Sequence as stored in the inventory (e.g. "032" for 35-24-032)
    fn_seq = want.rsplit("-", 1)[-1]

    # Look up this header's own line_type, nominal_size, and center position
    fn_lt: str = ""
    fn_size: str = ""
    fn_x: Optional[float] = None
    fn_y: Optional[float] = None
    for line in inventory.get("lines") or []:
        raw = str(line.get("line_number") or "").strip().upper()
        m = re.match(r"^(\d{2}-\d{2}-(\d+))", raw)
        if m and m.group(2) == fn_seq and raw.startswith(area):
            fn_lt = str(line.get("line_type") or "").upper()
            fn_size = str(line.get("nominal_size") or "")
            try:
                fn_x = float(line.get("x") or 0) or None
                fn_y = float(line.get("y") or 0) or None
            except (TypeError, ValueError):
                pass
            break

    # Crop radius used by the orchestrator's viewer shot (approximate).
    # Candidates within this radius are "NEARBY" — likely in the visible crop.
    _CROP_RADIUS = 200.0

    # Build the set of all FUNCTION-level headers (= other tags the orchestrator
    # processes; do not list them as branch candidates of each other).
    function_shorts: set = set()
    for fn in inventory.get("functions") or []:
        ft = str(fn.get("function") or "").strip().upper().replace(" ", "")
        m = re.match(r"^(\d{2}-\d{2}-\d+)$", ft)
        if m:
            function_shorts.add(m.group(1))
    # Also exclude the current tag itself
    function_shorts.add(want)

    # Collect same-fluid SIBLING function headers (other LINE FUNCTIONs sharing
    # the same fluid code).  These must appear as PEERS, never as children.
    sibling_fn_headers: List[str] = []
    if fn_lt:
        for line in inventory.get("lines") or []:
            raw = str(line.get("line_number") or "").strip().upper()
            m2 = re.match(r"^(\d{2}-\d{2}-(\d+))", raw)
            if not m2:
                continue
            sib_short = m2.group(1)
            if sib_short == want or not sib_short.startswith(area):
                continue
            if sib_short in function_shorts and str(line.get("line_type") or "").upper() == fn_lt:
                sibling_fn_headers.append(sib_short)
    sibling_fn_headers = sorted(set(sibling_fn_headers))

    # Collect all non-header line labels in the same plant area, with distance
    same_fluid: List[Tuple[str, str, str, bool]] = []  # (short, lt, size, nearby)
    diff_fluid: List[Tuple[str, str, str, bool]] = []
    seen: set = set()
    for line in inventory.get("lines") or []:
        raw = str(line.get("line_number") or "").strip().upper()
        m = re.match(r"^(\d{2}-\d{2}-\d+)", raw)
        if not m:
            continue
        short = m.group(1)
        if short in seen or not short.startswith(area):
            continue
        lt = str(line.get("line_type") or "").upper()
        is_same_fluid = lt and lt == fn_lt
        # Same-fluid function headers are excluded: they are sibling distribution
        # headers (listed in the SIBLING section) and must never be branch candidates.
        # Diff-fluid function headers CAN be children — a connected branch of different
        # fluid is a legitimate EQUIPMENT child even if it is itself a function header.
        if is_same_fluid and short in function_shorts:
            continue
        seen.add(short)
        size = str(line.get("nominal_size") or "")
        # Determine if this candidate is within the crop window
        nearby = False
        if fn_x is not None:
            try:
                lx = float(line.get("x") or 0)
                ly = float(line.get("y") or 0)
                dist = ((lx - fn_x) ** 2 + (ly - fn_y) ** 2) ** 0.5
                nearby = dist <= _CROP_RADIUS
            except (TypeError, ValueError):
                pass
        if is_same_fluid:
            same_fluid.append((short, lt, size, nearby))
        else:
            diff_fluid.append((short, lt, size, nearby))

    same_fluid.sort()
    diff_fluid.sort()

    # If a lower-numbered sibling header shares this fluid code AND the pool has
    # actual same-fluid non-header branches to allocate, that sibling is the
    # "primary" header.  Downgrade TIGHT CIRCUIT to SHARED FLUID so this function
    # only claims branches it can visually confirm (NEARBY), rather than
    # auto-including branches that likely belong to the primary sibling.
    # When the pool is empty (pool=0), framing doesn't affect same-fluid allocation,
    # so we keep TIGHT CIRCUIT to avoid changing diff-fluid visual-confirm behavior.
    has_lower_sibling = any(sib < want for sib in sibling_fn_headers)
    downgrade_to_shared = has_lower_sibling and len(same_fluid) > 0

    # Tight-circuit: pool ≤15 non-header candidates, and not downgraded by a
    # lower-numbered same-fluid sibling with actual branch candidates to share.
    tight_circuit = len(same_fluid) <= 15 and not downgrade_to_shared

    # Nearby same-fluid count (within crop area)
    nearby_same = sum(1 for _, _, _, nb in same_fluid if nb)

    # Format the dossier section
    if tight_circuit:
        circuit_label = (
            f"TIGHT CIRCUIT ({len(same_fluid)} same-fluid lines"
            f" — include ALL as EQUIPMENT children)"
        )
    else:
        circuit_label = (
            f"SHARED FLUID ({len(same_fluid)} same-fluid candidates, {nearby_same} NEARBY in crop"
            f" — multiple headers share [{fn_lt}]. Include NEARBY same-fluid lines as EQUIPMENT."
            f" For lines NOT NEARBY, only include if visibly connected in image.)"
        )
    parts = [
        f"LINE NETWORK CONTEXT for {want} ({fn_lt or '?'} / {fn_size or '?'} mm): {circuit_label}",
    ]
    # Show sibling function headers before the branch list so the AI knows to
    # put them in peers and not claim them as EQUIPMENT children.
    if sibling_fn_headers:
        parts.append(
            f"⚠ SIBLING [{fn_lt or '?'}] FUNCTION HEADERS — put in peers, NEVER as EQUIPMENT children:"
        )
        for sib in sibling_fn_headers[:25]:
            parts.append(f"  {sib}  [{fn_lt}]  FUNCTION-HEADER  → peers only")
    parts.append(f"Non-header lines with SAME fluid code [{fn_lt or '?'}] in this plant area:")
    if same_fluid:
        for short, lt, size, nb in same_fluid[:40]:
            proximity = "NEARBY" if nb else "DISTANT"
            parts.append(f"  {short}  [{lt}/{size}mm]  SAME-FLUID  {proximity}")
    else:
        parts.append("  (none with identical fluid code in this area)")
    if diff_fluid:
        parts.append("Non-header lines with DIFFERENT fluid code — include only if visibly connected:")
        for short, lt, size, nb in diff_fluid[:20]:
            proximity = "NEARBY" if nb else "DISTANT"
            parts.append(f"  {short}  [{lt}/{size}mm]  DIFF-FLUID  {proximity}")

    context_text = "\n".join(parts)
    # Return same-fluid first (high-priority candidates), then diff-fluid
    extra_candidates = (
        [s for s, _, _, _ in same_fluid[:40]]
        + [s for s, _, _, _ in diff_fluid[:20]]
    )
    return context_text, extra_candidates


def build_equipment_dossier(
    tag: str,
    parent: Dict[str, Any],
    center: Tuple[float, float],
    tag_register: List[Dict[str, Any]],
    inventory: Optional[Dict[str, Any]] = None,
    enrichment: Optional[Dict[str, Any]] = None,
    structural: Optional[Dict[str, Any]] = None,
    radius: float = 200.0,
) -> str:
    """Human-readable CAD context: nearby lines, devices, peers, bindings."""
    cx, cy = center
    want = normalize_tag(tag)
    lines: List[str] = []
    devices: List[str] = []
    peers: List[str] = []
    texts: List[str] = []

    def dist(x: object, y: object) -> Optional[float]:
        try:
            return ((float(x) - cx) ** 2 + (float(y) - cy) ** 2) ** 0.5
        except Exception:
            return None

    # Same-tag family from register
    family = []
    for row in tag_register:
        rt = normalize_tag(str(row.get("resolved_tag") or ""))
        if rt != want:
            # peer primary equipment nearby
            cat = str(row.get("category") or "")
            if cat in PRIMARY_CATEGORIES and row.get("x") is not None:
                d = dist(row.get("x"), row.get("y"))
                if d is not None and d <= radius and rt:
                    peers.append(f"{rt} ({cat}, d={d:.0f})")
            continue
        family.append(
            f"{row.get('category')} @ ({row.get('x')},{row.get('y')}) "
            f"block={row.get('block_name')} nearby={row.get('nearby_tags')}"
        )

    if inventory:
        for key in ("lines", "line_markers", "valves", "control_valves", "instruments", "pumps", "motors", "fittings"):
            for row in inventory.get(key) or []:
                if not isinstance(row, dict):
                    continue
                d = dist(row.get("x"), row.get("y"))
                if d is None or d > radius:
                    continue
                if key == "lines":
                    raw = str(row.get("line_number") or "")
                    short = normalize_tag(raw)
                    if short:
                        lines.append(f"{short}  full={raw}  d={d:.0f}  layer={row.get('layer')}")
                else:
                    label = (
                        row.get("resolved_tag")
                        or row.get("tag")
                        or row.get("text")
                        or row.get("block_name")
                        or row.get("name")
                        or ""
                    )
                    label_n = normalize_tag(str(label)) if label else ""
                    devices.append(f"{key}: {label_n or label}  d={d:.0f}  block={row.get('block_name') or row.get('name')}")

    if enrichment:
        for row in enrichment.get("line_geometry_bindings") or []:
            if not isinstance(row, dict):
                continue
            pos = row.get("label_position") or [None, None]
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                d = dist(pos[0], pos[1])
            else:
                d = None
            if d is None or d > radius:
                continue
            short = normalize_tag(str(row.get("line_number") or ""))
            if short:
                lines.append(
                    f"{short}  bind={row.get('bind_confidence')}  pipe={row.get('bound_pipe_type')}  d={d:.0f}"
                )

    if structural:
        for ent in structural.get("text_entities") or []:
            if not isinstance(ent, dict):
                continue
            pos = ent.get("position") or [None, None]
            if not (isinstance(pos, (list, tuple)) and len(pos) >= 2):
                continue
            d = dist(pos[0], pos[1])
            if d is None or d > radius:
                continue
            txt = str(ent.get("text") or "").strip()
            if not txt:
                continue
            if TAG_TOKEN_RE.search(txt) or any(ch.isdigit() for ch in txt):
                texts.append(f"{normalize_tag(txt) if TAG_TOKEN_RE.search(txt) else txt}  d={d:.0f}  layer={ent.get('layer')}")

    def uniq(seq: List[str], limit: int) -> List[str]:
        seen = set()
        out = []
        for item in seq:
            key = item.split()[0] if item else item
            if key in seen:
                continue
            seen.add(key)
            out.append(item)
            if len(out) >= limit:
                break
        return out

    parts = [
        f"Parent tag: {want}",
        f"Parent category/block: {parent.get('category')} / {parent.get('block_name')}",
        f"Parent XY: ({parent.get('x')}, {parent.get('y')})",
        f"Nearby descriptions: {parent.get('nearby_descriptions')}",
        "",
        "Same-tag CAD family:",
        *([f"- {x}" for x in family[:12]] or ["- (none)"]),
        "",
        "Nearby line numbers (short ids preferred in output):",
        *([f"- {x}" for x in uniq(lines, 25)] or ["- (none)"]),
        "",
        "Nearby devices (valves/instruments/pumps/…):",
        *([f"- {x}" for x in uniq(devices, 30)] or ["- (none)"]),
        "",
        "Nearby peer primary equipment (do NOT nest under parent):",
        *([f"- {x}" for x in uniq(peers, 12)] or ["- (none)"]),
        "",
        "Nearby drawing text tokens:",
        *([f"- {x}" for x in uniq(texts, 40)] or ["- (none)"]),
    ]
    # For LINE-type functions, append full network context (fluid-code branch list)
    if inventory and _LINE_FN_RE.match(want):
        lnet_text, _ = _line_network_context(want, inventory)
        if lnet_text:
            parts.append("")
            parts.append(lnet_text)
    return "\n".join(parts)

def title_context(
    enrichment: Dict[str, Any],
    sheet_title: str,
    input_path: Optional[Path] = None,
) -> Dict[str, str]:
    site = line = ""
    process = sheet_title
    for block in enrichment.get("title_block") or []:
        if not isinstance(block, dict):
            continue
        if block.get("PROJECT1") or block.get("PROJECT2") or block.get("PROJECT3") or block.get("TITLE1"):
            site = str(block.get("PROJECT2") or block.get("PROJECT1") or "").strip() or site
            line = str(block.get("PROJECT3") or block.get("LYH") or "").strip() or line
            process = str(block.get("TITLE1") or "").strip() or process
    floc = (
        load_floc_context_for_input(Path(input_path))
        if input_path
        else merge_floc_context()
    )
    stem_lower = (Path(input_path).stem if input_path else sheet_title).lower()
    # Only force Broke GT codes on the actual Broke System drawing — not every title
    # containing the word "broke" and not other PM03 areas (OCC, CHEM, Vacuum, …).
    if "broke system" in stem_lower or (
        process
        and "broke" in process.lower()
        and "occ" not in process.lower()
        and not input_path
    ):
        floc = merge_floc_context(process_code="BR", sub_process="BR1", process_name="BROKE SYSTEM")
    return {
        "site": site or floc.get("site_name", ""),
        "line": line or floc.get("line_name", ""),
        "process": process or floc.get("process_name", ""),
        "sub_process": floc["sub_process"],
        "plant": floc["plant"],
        "line_code": floc["line_code"],
        "process_code": floc["process_code"],
        "structure_indicator": floc["structure_indicator"],
        "fl_category": floc["fl_category"],
        "maintenance_plant": floc["maintenance_plant"],
        "planning_plant": floc["planning_plant"],
        "fl_type_line": floc["fl_type_line"],
        "process_name": floc.get("process_name", process or "BROKE SYSTEM"),
        "line_name": floc.get("line_name", "PAPER MACHINE 3"),
        "site_name": floc.get("site_name", "SHOTTON MILL LTD"),
    }


def collect_candidate_tags(
    tag: str,
    center: Tuple[float, float],
    tag_register: List[Dict[str, Any]],
    inventory: Optional[Dict[str, Any]] = None,
    structural: Optional[Dict[str, Any]] = None,
    radius: float = 220.0,
) -> List[str]:
    """Gather nearby CAD/inventory tags to ground the vision model."""
    cx, cy = center
    want = normalize_tag(tag)
    found: Dict[str, float] = {}
    if _WU_FN_RE.match(want):
        radius = max(radius, 800.0)
    elif _TISSUE_HIER_TAG_RE.match(want):
        radius = max(radius, 350.0)

    def consider(raw: object, x: Optional[float] = None, y: Optional[float] = None, weight: float = 1.0) -> None:
        if raw is None:
            return
        text = str(raw)
        for m in TAG_TOKEN_RE.finditer(text):
            tok = normalize_tag(m.group(0))
            if len(tok) < 5:
                continue
            dist = 0.0
            if x is not None and y is not None:
                dist = ((float(x) - cx) ** 2 + (float(y) - cy) ** 2) ** 0.5
                if dist > radius:
                    continue
            score = dist / max(weight, 1e-6)
            prev = found.get(tok)
            if prev is None or score < prev:
                found[tok] = score
            # Also keep short line form 35-24-189 from 35-24-189-PP-300-...
            parts = tok.split("-")
            if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
                short = f"{parts[0]}-{parts[1]}-{parts[2]}"
                prev_s = found.get(short)
                if prev_s is None or score < prev_s:
                    found[short] = score

    for row in tag_register:
        x = row.get("x")
        y = row.get("y")
        consider(row.get("resolved_tag"), x, y, weight=1.5)
        consider(row.get("nearby_tags"), x, y)
        consider(row.get("nearby_descriptions"), x, y, weight=0.7)

    if inventory:
        for key, rows in inventory.items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                x, y = row.get("x"), row.get("y")
                for field in (
                    "resolved_tag",
                    "tag",
                    "line_number",
                    "text",
                    "attribute_tag",
                    "name",
                    "mask",
                    "nearby_tags",
                ):
                    consider(row.get(field), x, y)
                plant = str(row.get("plant_area") or "").strip()
                seq = str(row.get("line_sequence") or "").strip()
                if plant and seq:
                    consider(f"{plant}-{seq}", x, y, weight=1.2)

    if structural:
        for ent in structural.get("text_entities") or []:
            if not isinstance(ent, dict):
                continue
            pos = ent.get("position") or [None, None]
            x = pos[0] if isinstance(pos, (list, tuple)) and len(pos) >= 2 else ent.get("x")
            y = pos[1] if isinstance(pos, (list, tuple)) and len(pos) >= 2 else ent.get("y")
            consider(ent.get("text"), x, y, weight=1.4)
        for ent in structural.get("inserts") or []:
            if not isinstance(ent, dict):
                continue
            x, y = ent.get("x"), ent.get("y")
            consider(ent.get("name"), x, y, weight=0.5)
            attrs = ent.get("attributes") or {}
            if isinstance(attrs, dict):
                for val in attrs.values():
                    consider(val, x, y, weight=1.3)
            elif isinstance(attrs, list):
                for item in attrs:
                    if isinstance(item, dict):
                        consider(item.get("text") or item.get("value") or item.get("tag"), x, y, weight=1.3)

    found.setdefault(want, 0.0)

    # For LINE-type functions, add ALL same-fluid branch lines as candidates
    # (radius filtering alone misses far-away branches of distribution headers).
    if inventory and _LINE_FN_RE.match(want):
        _, extra_cands = _line_network_context(want, inventory)
        for tok in extra_cands:
            tok_n = normalize_tag(tok)
            if tok_n and tok_n not in found:
                # Score 5000 = low priority vs nearby items (scored 0–radius)
                found[tok_n] = 5000.0

    # Keep candidates in the same plant/area family as the parent when possible
    prefix = plant_prefix(want)
    ordered = [
        t
        for t, _ in sorted(found.items(), key=lambda kv: (kv[1], kv[0]))
        if t == want or t.startswith(prefix) or prefix in t
    ]
    if len(ordered) < 8:
        ordered = [t for t, _ in sorted(found.items(), key=lambda kv: (kv[1], kv[0]))]
    return ordered[:100]


def parent_from_inventory(inventory: Optional[Dict[str, Any]], tag: str) -> Optional[Dict[str, Any]]:
    """Inventory functions carry x/y for instruments and lines; tag_register often does not."""
    want = normalize_tag(tag)
    for row in (inventory or {}).get("functions") or []:
        if normalize_tag(str(row.get("function") or "")) != want:
            continue
        try:
            x = float(row.get("x"))
            y = float(row.get("y"))
        except (TypeError, ValueError):
            return None
        return {
            "category": row.get("category") or row.get("kind") or "functions",
            "block_name": row.get("block_name") or "",
            "handle": row.get("handle") or "",
            "layer": row.get("layer") or "",
            "x": x,
            "y": y,
            "resolved_tag": want,
            "nearby_tags": row.get("nearby_tags") or "",
            "nearby_descriptions": row.get("description") or "",
            "confidence": row.get("confidence") or "medium",
        }
    return None


def pick_parent(
    tag_register: List[Dict[str, Any]],
    tag: str,
    inventory: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    want = normalize_tag(tag)
    rows = [r for r in tag_register if normalize_tag(str(r.get("resolved_tag") or "")) == want]
    if not rows:
        return parent_from_inventory(inventory, tag)
    type_letter = ""
    m = re.match(r"^\d{2}-\d{2}([A-Z]+)\d+", want)
    if m:
        type_letter = m.group(1).upper()
    hints = {
        "L": ("PULPER", "TANK", "VESSEL", "CHEST", "AGITATOR"),
        "T": ("TANK", "VESSEL", "CHEST"),
        "P": ("PUMP",),
        "A": ("AGITATOR", "MIXER"),
        "E": ("PULPER", "REFINER", "MACHINE"),
    }.get(type_letter, ())
    # L401–L499 = Agitator per SML PS-21 / Valmet PM3 — override generic L hints
    if type_letter == "L":
        num_m = re.search(r"(\d+)$", want)
        if num_m and 401 <= int(num_m.group(1)) <= 499:
            hints = ("AGITATOR", "MIXER")

    def score(r: Dict[str, Any]) -> Tuple:
        cat = str(r.get("category") or "")
        layer = str(r.get("layer") or "").upper()
        desc = str(r.get("nearby_descriptions") or "").upper()
        return (
            0 if cat in PRIMARY_CATEGORIES else 1,
            0 if any(h in desc for h in hints) else 1,
            0 if layer.endswith("_POS") or layer.endswith("POS") else 1,
            PARENT_PRIORITY.get(cat, 99),
        )

    return sorted(rows, key=score)[0]


def crop_center(tag: str, parent: Dict[str, Any], tag_register: List[Dict[str, Any]]) -> Tuple[float, float]:
    want = normalize_tag(tag)
    pts = [(float(parent["x"]), float(parent["y"]))]
    for row in tag_register:
        if normalize_tag(str(row.get("resolved_tag") or "")) != want:
            continue
        if row.get("category") in PRIMARY_CATEGORIES and row.get("x") is not None:
            pts.append((float(row["x"]), float(row["y"])))
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def tight_crop_window(
    doc,
    center: Tuple[float, float],
    parent: Dict[str, Any],
    tag: str,
    tag_register: List[Dict[str, Any]],
    half_max: float = 95.0,
    half_min: float = 55.0,
    margin: float = 18.0,
) -> Tuple[float, float, float, float]:
    """Zoom to content around parent instead of a large empty black frame."""
    from ezdxf import bbox as ezbbox

    cx, cy = center
    want = normalize_tag(tag)
    xs = [cx, float(parent["x"])]
    ys = [cy, float(parent["y"])]

    # Same-tag inserts pull the frame in
    for row in tag_register:
        if normalize_tag(str(row.get("resolved_tag") or "")) != want:
            continue
        if row.get("x") is None or row.get("y") is None:
            continue
        x, y = float(row["x"]), float(row["y"])
        if abs(x - cx) <= half_max and abs(y - cy) <= half_max:
            xs.append(x)
            ys.append(y)

    # Local entity extents near parent (ignore far outliers inside the max window)
    probe = (cx - half_max, cy - half_max, cx + half_max, cy + half_max)
    for entity in doc.modelspace():
        try:
            ext = ezbbox.extents([entity], fast=True)
            if ext is None or not ext.has_data:
                continue
            if ext.extmax.x < probe[0] or ext.extmin.x > probe[2] or ext.extmax.y < probe[1] or ext.extmin.y > probe[3]:
                continue
            mx = (ext.extmin.x + ext.extmax.x) / 2.0
            my = (ext.extmin.y + ext.extmax.y) / 2.0
            # keep only denser core near parent
            if abs(mx - cx) <= half_max * 0.72 and abs(my - cy) <= half_max * 0.72:
                # shrink contribution of huge lines by clamping corners toward parent
                xs.append(max(probe[0], min(probe[2], float(ext.extmin.x))))
                xs.append(max(probe[0], min(probe[2], float(ext.extmax.x))))
                ys.append(max(probe[1], min(probe[3], float(ext.extmin.y))))
                ys.append(max(probe[1], min(probe[3], float(ext.extmax.y))))
        except Exception:
            continue

    xmin, xmax = min(xs) - margin, max(xs) + margin
    ymin, ymax = min(ys) - margin, max(ys) + margin
    # square window centered on content
    w = max(xmax - xmin, ymax - ymin, half_min * 2)
    w = min(w, half_max * 2)
    ccx = (xmin + xmax) / 2.0
    ccy = (ymin + ymax) / 2.0
    # bias center slightly toward parent so highlight stays framed
    ccx = 0.65 * ccx + 0.35 * float(parent["x"])
    ccy = 0.65 * ccy + 0.35 * float(parent["y"])
    half = w / 2.0
    return ccx - half, ccy - half, ccx + half, ccy + half


def load_drawing(input_path: Path):
    import ezdxf

    configure_odafc()
    if input_path.suffix.lower() == ".dxf":
        return ezdxf.readfile(str(input_path))
    from ezdxf.addons import odafc

    return odafc.readfile(str(input_path))


def _cad_to_pix(
    x: float,
    y: float,
    bbox: Tuple[float, float, float, float],
    width: int,
    height: int,
) -> Tuple[int, int]:
    xmin, ymin, xmax, ymax = bbox
    px = int(round((x - xmin) / max(xmax - xmin, 1e-6) * (width - 1)))
    # CAD Y up → image Y down
    py = int(round((ymax - y) / max(ymax - ymin, 1e-6) * (height - 1)))
    return px, py


def overlay_parent_box(
    png_bytes: bytes,
    bbox: Tuple[float, float, float, float],
    parent: Dict[str, Any],
    title: str,
    highlight: Tuple[float, float, float, float],
) -> bytes:
    """Draw red parent box; keep full frame so nearby objects stay visible."""
    from io import BytesIO

    from PIL import Image, ImageDraw, ImageFont

    im = Image.open(BytesIO(png_bytes)).convert("RGB")
    draw = ImageDraw.Draw(im)
    hx0, hy0, hx1, hy1 = highlight
    x0, y0 = _cad_to_pix(hx0, hy0, bbox, im.width, im.height)
    x1, y1 = _cad_to_pix(hx1, hy1, bbox, im.width, im.height)
    left, right = sorted([x0, x1])
    top, bottom = sorted([y0, y1])
    pad = max(6, im.width // 100)
    left, top = max(0, left - pad), max(0, top - pad)
    right, bottom = min(im.width - 1, right + pad), min(im.height - 1, bottom + pad)

    for t in range(5):
        draw.rectangle([left - t, top - t, right + t, bottom + t], outline=(220, 38, 38))

    label = f"PARENT {title}"
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", max(20, im.width // 50))
    except Exception:
        font = ImageFont.load_default()
    ty = max(4, top - max(30, im.height // 35))
    tw = draw.textbbox((0, 0), label, font=font)[2]
    th = draw.textbbox((0, 0), label, font=font)[3]
    draw.rectangle([left, ty, left + tw + 12, ty + th + 8], fill=(185, 28, 28))
    draw.text((left + 6, ty + 3), label, fill=(254, 226, 226), font=font)

    out = BytesIO()
    im.save(out, format="PNG", optimize=True)
    return out.getvalue()


def parent_highlight_box(
    doc,
    parent: Dict[str, Any],
    tag: str,
    tag_register: List[Dict[str, Any]],
    pad: float = 24.0,
    cluster_radius: float = 55.0,
) -> Tuple[float, float, float, float]:
    """Red box = parent only (nearby same-tag symbols / local equipment graphics)."""
    from ezdxf import bbox as ezbbox

    want = normalize_tag(tag)
    px, py = float(parent["x"]), float(parent["y"])
    xs = [px]
    ys = [py]
    for row in tag_register:
        if normalize_tag(str(row.get("resolved_tag") or "")) != want:
            continue
        if row.get("x") is None or row.get("y") is None:
            continue
        x, y = float(row["x"]), float(row["y"])
        if (x - px) ** 2 + (y - py) ** 2 > cluster_radius ** 2:
            continue
        if row.get("category") in PRIMARY_CATEGORIES or row.get("handle") == parent.get("handle"):
            xs.append(x)
            ys.append(y)

    equip_layers = {
        "P-EQUIPMENTS",
        "P-EQUIPMENT_POS",
        "P-PUMPS",
        "P-PUMP_POS",
        "P-TANKS",
        "P-TANK_POS",
        "P-AGITATORS",
        "P-AGITATOR_POS",
        "P-MOTOR_POS",
        "P-MOTORS",
    }
    for entity in doc.modelspace():
        try:
            layer = str(getattr(entity.dxf, "layer", "") or "")
            if layer not in equip_layers and entity.dxftype() != "INSERT":
                continue
            ext = ezbbox.extents([entity], fast=True)
            if ext is None or not ext.has_data:
                continue
            mx = (ext.extmin.x + ext.extmax.x) / 2.0
            my = (ext.extmin.y + ext.extmax.y) / 2.0
            if (mx - px) ** 2 + (my - py) ** 2 > cluster_radius ** 2:
                continue
            if (ext.extmax.x - ext.extmin.x) > 120 or (ext.extmax.y - ext.extmin.y) > 120:
                continue
            xs.extend([float(ext.extmin.x), float(ext.extmax.x)])
            ys.extend([float(ext.extmin.y), float(ext.extmax.y)])
        except Exception:
            continue

    return min(xs) - pad, min(ys) - pad * 0.7, max(xs) + pad, max(ys) + pad


def adaptive_view_window(
    parent: Dict[str, Any],
    tag: str,
    tag_register: List[Dict[str, Any]],
    highlight: Tuple[float, float, float, float],
    half_min: float = 110.0,
    half_max: float = 170.0,
) -> Tuple[float, float, float, float]:
    """
    Zoom from nearby-element distances:
    - sparse/far neighbors (big vessel areas like L009) → more zoomed out
    - dense clusters (pump skids like P519) → a bit tighter
    Always keep room so peer equipment / attached objects are visible.
    """
    import math

    px, py = float(parent["x"]), float(parent["y"])
    want = normalize_tag(tag)
    dists: List[float] = []
    neighbor_pts: List[Tuple[float, float]] = [(px, py)]

    for row in tag_register:
        if row.get("x") is None or row.get("y") is None:
            continue
        x, y = float(row["x"]), float(row["y"])
        d = math.hypot(x - px, y - py)
        if d < 2 or d > half_max * 1.35:
            continue
        # Prefer hierarchy-relevant categories for distance cue
        cat = str(row.get("category") or "")
        resolved = normalize_tag(str(row.get("resolved_tag") or ""))
        useful = (
            cat in PRIMARY_CATEGORIES
            or cat in {"valves", "control_valves", "instruments", "motors", "fittings", "agitators"}
            or resolved == want
        )
        if not useful:
            continue
        dists.append(d)
        neighbor_pts.append((x, y))

    if dists:
        dists.sort()
        close = [d for d in dists if d <= 75.0]
        if len(close) >= 6:
            # Dense cluster (typical pump skid) → keep closer zoom like previous P519
            close.sort()
            q = close[len(close) // 2]
            half = q * 1.85
        else:
            # Spread layout (vessel + remote attachments) → zoom out for hierarchy context
            q = dists[int(0.78 * (len(dists) - 1))]
            half = q * 1.60
    else:
        half = (half_min + half_max) / 2.0

    # Ensure highlight (parent red-box cluster) fits with extra context margin
    hx0, hy0, hx1, hy1 = highlight
    need = max(hx1 - hx0, hy1 - hy0) / 2.0 + 45.0
    half = max(half, need, half_min)
    half = min(half, half_max)

    # Center biased to parent, but include highlight center
    hcx, hcy = (hx0 + hx1) / 2.0, (hy0 + hy1) / 2.0
    cx = 0.55 * px + 0.45 * hcx
    cy = 0.55 * py + 0.45 * hcy
    return cx - half, cy - half, cx + half, cy + half


def viewer_screenshot(
    doc,
    center: Tuple[float, float],
    parent: Dict[str, Any],
    tag: str,
    tag_register: List[Dict[str, Any]],
    out_path: Path,
    half_max: float = 170.0,
    half_min: float = 110.0,
    dpi: int = 260,
) -> Path:
    """ODA-backed viewer raster: distance-adaptive zoom + red parent highlight."""
    from ezdxf import bbox as ezbbox
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing import layout as ezlayout
    from ezdxf.addons.drawing import pymupdf as ez_pymupdf
    from ezdxf.math import BoundingBox2d

    highlight = parent_highlight_box(doc, parent, tag, tag_register)
    xmin, ymin, xmax, ymax = adaptive_view_window(
        parent,
        tag,
        tag_register,
        highlight,
        half_min=half_min,
        half_max=half_max,
    )
    bbox = (xmin, ymin, xmax, ymax)

    ents = []
    for entity in doc.modelspace():
        try:
            ext = ezbbox.extents([entity], fast=True)
            if ext is None or not ext.has_data:
                continue
            if ext.extmax.x < xmin or ext.extmin.x > xmax or ext.extmax.y < ymin or ext.extmin.y > ymax:
                continue
            ents.append(entity)
        except Exception:
            continue
    if not ents:
        raise RuntimeError(f"No entities in viewer window for {tag}")

    ctx = RenderContext(doc)
    backend = ez_pymupdf.PyMuPdfBackend()
    Frontend(ctx, backend).draw_entities(ents)
    try:
        from ezdxf.addons.drawing.properties import Properties

        props = Properties()
        props.color = "#000000"
        props.lineweight = 0.01
        corners = [
            ((xmin, ymin), (xmax, ymin)),
            ((xmax, ymin), (xmax, ymax)),
            ((xmax, ymax), (xmin, ymax)),
            ((xmin, ymax), (xmin, ymin)),
        ]
        for a, b in corners:
            backend.draw_line(a, b, props)
    except Exception:
        pass
    backend.finalize()

    span = max(xmax - xmin, ymax - ymin)
    page = ezlayout.Page(210, 210, units=ezlayout.Units.mm)
    settings = ezlayout.Settings(
        fit_page=False,
        scale=210.0 / span,
        page_alignment=ezlayout.PageAlignment.MIDDLE_CENTER,
    )
    png = backend.get_pixmap_bytes(
        page=page,
        settings=settings,
        dpi=dpi,
        fmt="png",
        render_box=BoundingBox2d([(xmin, ymin), (xmax, ymax)]),
    )
    png = overlay_parent_box(png, bbox, parent, title=tag, highlight=highlight)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(png)
    from io import BytesIO

    from PIL import Image

    im = Image.open(BytesIO(png))
    logger.info(f"[shot] {tag}: {len(ents)} ents, window={xmax-xmin:.0f}x{ymax-ymin:.0f} "
        f"-> {out_path.name} ({im.width}x{im.height})")
    return out_path


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def build_hierarchy_prompt(
    tag: str,
    parent: Dict[str, Any],
    context: Dict[str, str],
    prompt_file: str = HIERARCHY_PROMPT_FILE,
    candidates: Optional[List[str]] = None,
    parent_dossier: str = "",
) -> str:
    """Render the engineer-grade hierarchy brief from ``prompts/``."""
    nearby = parent.get("nearby_descriptions")
    if isinstance(nearby, (list, tuple)):
        nearby_text = "; ".join(str(x) for x in nearby if x)
    else:
        nearby_text = str(nearby or "")
    cand = candidates or []
    cand_text = ", ".join(cand) if cand else "(none)"
    paths = floc_paths_for_function(tag, context)
    return load_prompt(
        prompt_file,
        {
            "site": context.get("site", ""),
            "line": context.get("line", ""),
            "process": context.get("process", ""),
            "sub_process": context.get("sub_process", DEFAULT_SUB_PROCESS),
            "tag": tag,
            "floc_path": paths.get("function", ""),
            "parent_category": parent.get("category") or "",
            "parent_block": parent.get("block_name") or "",
            "nearby_text": nearby_text,
            "candidates": cand_text,
            "parent_dossier": parent_dossier or "(no dossier)",
        },
    )


def model_supports_vision(model_id: str) -> bool:
    mid = (model_id or "").lower()
    if mid.startswith("openai.") or "gpt-oss" in mid:
        return False
    vision_hints = (
        "anthropic",
        "claude",
        "nova",
        "kimi",
        "moonshot",
        "ministral",
        "magistral",
        "gemma",
        "qwen3-vl",
    )
    return any(h in mid for h in vision_hints)


def bedrock_hierarchy_from_shot(
    image_path: Path,
    tag: str,
    parent: Dict[str, Any],
    context: Dict[str, str],
    model_id: str,
    region: str,
    prompt_file: str = HIERARCHY_PROMPT_FILE,
    candidates: Optional[List[str]] = None,
    parent_dossier: str = "",
    legend_path: Optional[Path] = None,
) -> Dict[str, Any]:
    import boto3

    prompt = build_hierarchy_prompt(
        tag,
        parent,
        context,
        prompt_file=prompt_file,
        candidates=candidates,
        parent_dossier=parent_dossier,
    )
    use_vision = model_supports_vision(model_id) and image_path.exists()
    if not use_vision:
        prompt = (
            prompt
            + "\n\nNOTE: This model cannot view the screenshot. "
            "Build the hierarchy ONLY from the CAD dossier, whitelist candidates, "
            "and ownership rules above. Prefer omission over invention.\n"
        )

    content: List[Dict[str, Any]] = [{"text": prompt}]
    if use_vision:
        content.append({"image": {"format": "png", "source": {"bytes": image_path.read_bytes()}}})
        if legend_path and legend_path.exists():
            suffix = legend_path.suffix.lower().lstrip(".")
            fmt = suffix if suffix in {"png", "jpg", "jpeg", "gif", "webp"} else "png"
            content.append({"image": {"format": fmt, "source": {"bytes": legend_path.read_bytes()}}})

    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": content}],
        inferenceConfig={"maxTokens": 3500, "temperature": 0},
    )
    text_parts = [b["text"] for b in response.get("output", {}).get("message", {}).get("content", []) if "text" in b]
    raw = "\n".join(text_parts).strip()
    return {
        "raw_text": raw,
        "parsed": extract_json_object(raw),
        "model_id": model_id,
        "region": region,
        "prompt_file": prompt_file,
        "candidates": candidates or [],
        "prompt_chars": len(prompt),
        "vision": use_vision,
    }


def _mask_value(*parts: str, explicit: str = "") -> str:
    """Deterministic SAP-style MASK/TPLNR (CHAR 30). Ignores free-form AI masks."""
    if explicit:
        # Only accept explicit if it already looks like 5001-... path.
        ex = re.sub(r"\s+", "", str(explicit).strip().upper())
        if ex.startswith("5001-") or ex == "5001":
            return ex[:30]
    return build_tplnr(*parts)


def plant_prefix(tag: str) -> str:
    t = normalize_tag(tag)
    m = re.match(r"^(\d{2}-\d{2})", t)
    if m:
        return m.group(1)
    # GOR/KSD mill+area: 122E-001 / 168L-521 → "122" / "168"
    m = re.match(r"^(\d{3})", t)
    if m:
        return m.group(1)
    return t[:5]


_FN_NUM_RE = re.compile(r"^\d{2}-\d{2}[A-Z]+(\d+)$")
_LINE_FN_RE = re.compile(r"^\d{2}-\d{2}-\d+$")  # 35-24-008 — piping header as FUNCTION
_MOTOR_NUM_DASH_RE = re.compile(r"^\d{2}-\d{2}-(\d+)\.\d+$")    # 35-24-004.1
_MOTOR_NUM_PFX_RE = re.compile(r"^\d{2}-\d{2}[A-Z]+(\d+)\.\d+$")  # 35-24L004.1


def _fn_numeric(tag: str) -> Optional[str]:
    """Numeric identifier from a function tag like 35-24L004 → '004'."""
    m = _FN_NUM_RE.match(normalize_tag(tag))
    return m.group(1) if m else None


def _motor_matches_fn(tag: str, fn_num: str) -> bool:
    """True if tag is not a motor tag, or its numeric base matches fn_num."""
    if not tag:
        return True
    for pat in (_MOTOR_NUM_DASH_RE, _MOTOR_NUM_PFX_RE):
        m = pat.match(tag)
        if m:
            return m.group(1) == fn_num
    return True


def is_plausible_hierarchy_tag(tok: str, parent_tag: str) -> bool:
    """Reject dimension fragments / off-area noise; keep GT-like tag shapes."""
    t = normalize_tag(tok)
    if not t or len(t) < 5:
        return False
    if _WU_FN_RE.match(t):
        return True
    # GOR / KSD: 168P-410, 168V-521, 168TC1, 122E-001, 126LC-001, 168-ST521
    if _TISSUE_HIER_TAG_RE.match(t) and not re.match(r"^\d{3,4}-\d{2,4}$", t):
        if re.search(r"-M[2-9]$", t):
            return False
        parent_area = re.match(r"^(\d{3})", normalize_tag(parent_tag))
        child_area = re.match(r"^(\d{3})", t)
        if parent_area and child_area and parent_area.group(1) != child_area.group(1):
            return False
        return True
    if len(t) < 6:
        return False
    # 001-100 / 003-50 style fragments from pipe class text
    if re.match(r"^\d{3,4}-\d{2,4}$", t):
        return False
    prefix = plant_prefix(parent_tag)
    if prefix and not t.startswith(prefix):
        return False
    # Local panel / MCS pushbuttons are not in the GT hierarchy sheet
    if re.search(r"(?:HS|ES|KI|KJ|HI|MCS)-\d+", t):
        return False
    # Gearbox housing 35-24P519.1 is vessel-only; pumps use 35-24-519.1
    pm = re.match(r"^(\d{2}-\d{2})([A-Z]+)(\d+)$", normalize_tag(parent_tag))
    if pm and not pm.group(2).startswith("L") and re.match(
        rf"^{re.escape(normalize_tag(parent_tag))}\.\d+$", t
    ):
        return False
    # 35-24L009 / 35-24-189 / 35-24LC-674 / 35-24LV1-674 / 35-24XS-681
    return bool(re.match(r"^\d{2}-\d{2}(?:[A-Z]|-\d)[A-Z0-9./-]*$", t))


def text_tag_locations(structural: Optional[Dict[str, Any]]) -> Dict[str, Tuple[float, float]]:
    """Map normalized tag -> first text position found in structural dump."""
    out: Dict[str, Tuple[float, float]] = {}
    if not structural:
        return out
    for ent in structural.get("text_entities") or []:
        if not isinstance(ent, dict):
            continue
        txt = str(ent.get("text") or "").strip()
        if not txt:
            continue
        pos = ent.get("position") or [None, None]
        if not (isinstance(pos, (list, tuple)) and len(pos) >= 2):
            continue
        try:
            xy = (float(pos[0]), float(pos[1]))
        except Exception:
            continue
        for m in TAG_TOKEN_RE.finditer(txt):
            tok = normalize_tag(m.group(0))
            out.setdefault(tok, xy)
            # also short line form
            parts = tok.split("-")
            if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit() and parts[2][:1].isdigit():
                short = normalize_tag(f"{parts[0]}-{parts[1]}-{parts[2]}")
                out.setdefault(short, xy)
    return out


def canonicalize_vision_tag(tok: str) -> str:
    """Normalize CAD/vision tag spellings toward GT conventions."""
    t = normalize_tag(tok)
    # Vision often misreads XS as XV on Valmet interlock symbols — not GOR/KSD.
    if re.match(r"^\d{2}-\d{2}", t):
        t = re.sub(r"XV-", "XS-", t)
    return normalize_tag(t)


def nearby_line_seeds(
    center: Tuple[float, float],
    inventory: Optional[Dict[str, Any]],
    structural: Optional[Dict[str, Any]],
    parent_tag: str,
    radius: float = 140.0,
) -> List[str]:
    """CAD line short-ids near the parent — strong EQUIPMENT candidates."""
    cx, cy = center
    seeds: Dict[str, float] = {}

    def add(raw: object, x: object, y: object, weight: float = 1.0) -> None:
        try:
            d = ((float(x) - cx) ** 2 + (float(y) - cy) ** 2) ** 0.5
        except Exception:
            return
        if d > radius:
            return
        tok = canonicalize_vision_tag(str(raw or ""))
        if not is_plausible_hierarchy_tag(tok, parent_tag):
            return
        if not (
            re.match(r"^\d{2}-\d{2}-\d{2,4}(?:\.\d+)?$", tok)
            or re.match(r"^\d{3}L-\d+$", tok, re.I)
        ):
            return
        score = d / max(weight, 1e-6)
        prev = seeds.get(tok)
        if prev is None or score < prev:
            seeds[tok] = score

    if inventory:
        for row in inventory.get("lines") or []:
            if not isinstance(row, dict):
                continue
            lt = str(row.get("line_type") or "").upper()
            # Auxiliary WAF/WAA headers are rarely owned children in this GT sheet
            weight = 0.35 if lt in {"WAF", "WAA", "WFC", "WFL"} else 1.0
            if lt in {"WAF", "WAA", "WFC"} and weight < 0.5:
                # skip unless very close
                try:
                    d = ((float(row["x"]) - cx) ** 2 + (float(row["y"]) - cy) ** 2) ** 0.5
                except Exception:
                    continue
                if d > 55:
                    continue
            add(row.get("line_number"), row.get("x"), row.get("y"), weight=weight)
    if structural:
        for ent in structural.get("text_entities") or []:
            if not isinstance(ent, dict):
                continue
            pos = ent.get("position") or [None, None]
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                add(ent.get("text"), pos[0], pos[1], weight=1.1)

    # Branch / local point conventions for this parent equipment.
    # L### vessels: .1/.2 gearbox housings + .3/.4 oil-pump motors.
    # P### / T###: only the main drive motor `.1` — never invent `.2/.3/.4`.
    want = normalize_tag(parent_tag)
    m = re.match(r"^(\d{2}-\d{2})([A-Z]+)(\d+)$", want)
    if m:
        area, letters, num = m.group(1), m.group(2), m.group(3)
        if letters.startswith("L"):
            # .1/.2 gearbox + main motors are the GT convention.
            # .3/.4 oil-pump motors only if CAD already has that tag — seeding
            # them on every vessel is a large extras source (L001.3, 001.4, …).
            known = set(seeds)
            if inventory:
                for key, rows in inventory.items():
                    if not isinstance(rows, list):
                        continue
                    for row in rows:
                        if not isinstance(row, dict):
                            continue
                        for field in ("tag", "line_number", "resolved_tag", "function"):
                            tok = canonicalize_vision_tag(str(row.get(field) or ""))
                            if tok:
                                known.add(tok)
            for suffix in (".1", ".2"):
                for cand in (f"{want}{suffix}", f"{area}-{num}{suffix}"):
                    seeds.setdefault(canonicalize_vision_tag(cand), 5.0)
            for suffix in (".3", ".4"):
                for cand in (f"{want}{suffix}", f"{area}-{num}{suffix}"):
                    tok = canonicalize_vision_tag(cand)
                    if tok in known:
                        seeds.setdefault(tok, 5.0)
        else:
            # Pumps/tanks: motor line form only (35-24-519.1), not P519.1 gearbox housing.
            seeds.setdefault(canonicalize_vision_tag(f"{area}-{num}.1"), 5.0)

    return [t for t, _ in sorted(seeds.items(), key=lambda kv: kv[1])]


def refine_ai_hierarchy(
    tag: str,
    parsed: Dict[str, Any],
    *,
    center: Tuple[float, float],
    inventory: Optional[Dict[str, Any]],
    structural: Optional[Dict[str, Any]],
    peer_tags: Optional[List[str]] = None,
    raw_text: str = "",
    candidates: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Filter noise, drop peers, merge high-value CAD line seeds."""
    want = normalize_tag(tag)
    peers = {normalize_tag(p) for p in (peer_tags or []) if p}
    peers.discard(want)
    # Tags confirmed by CAD data can bypass the prefix filter (covers cross-plant refs
    # like 53-24LC-621 that are legitimately owned by a 35-24 function in the GT).
    cad_confirmed = {normalize_tag(c) for c in (candidates or []) if c}
    refined_rows: List[Dict[str, str]] = []
    seen = set()
    raw_compact = re.sub(r"\s+", "", (raw_text or "")).upper()

    def push(equipment: str = "", subequipment: str = "", mask: str = "", description: str = "") -> None:
        eq = canonicalize_vision_tag(equipment) if equipment else ""
        sub = canonicalize_vision_tag(subequipment) if subequipment else ""
        for tok in (eq, sub):
            if not tok:
                continue
            if tok in peers:
                return
            # Line FUNCTIONs are piping headers — never gearbox/motor `.N` children.
            if _LINE_FN_RE.match(want) and re.search(r"\.\d+$", tok):
                return
            # KSD/GOR: only -M1 on driven equipment (cad whitelist must not revive -M2).
            if re.search(r"-M[2-9]$", tok) and not re.match(r"^\d{2}-\d{2}", tok):
                return
            if tok not in cad_confirmed and not is_plausible_hierarchy_tag(tok, want):
                return
        key = (eq, sub)
        if key in seen or (not eq and not sub):
            return
        seen.add(key)
        # Child MASK left blank in GT; do not invent deep paths here.
        desc = normalize_pltxt(description) if description else ""
        if not desc and (eq or sub):
            desc = (eq or sub)[:40]
        refined_rows.append(
            {
                "equipment": eq,
                "subequipment": sub,
                "mask": "",
                "description": desc,
            }
        )

    for child in parsed.get("rows") or []:
        if not isinstance(child, dict):
            continue
        push(
            str(child.get("equipment") or ""),
            str(child.get("subequipment") or ""),
            str(child.get("mask") or ""),
            str(child.get("description") or ""),
        )

    # GOR ventil units are one FUNCTION for the whole sheet — inject nearby lines.
    # KSD/Valmet keep the mention-guard so neighbouring machines do not leak in.
    tissue_unit = bool(_WU_FN_RE.match(want))
    seed_radius = 800.0 if tissue_unit else 130.0
    for line_id in nearby_line_seeds(center, inventory, structural, want, radius=seed_radius):
        if line_id in peers:
            continue
        if any(r.get("equipment") == line_id or r.get("subequipment") == line_id for r in refined_rows):
            continue
        is_motor_convention = bool(re.search(r"\.\d+$", line_id))
        if not is_motor_convention and not tissue_unit and line_id.upper() not in raw_compact:
            continue
        push(equipment=line_id)

    # Drop motor tags whose numeric base doesn't match this function's number.
    # 35-24-003.1 under function 35-24L004 is leakage from the L003 crop — remove it.
    fn_num = _fn_numeric(want)
    if fn_num:
        refined_rows = [
            r for r in refined_rows
            if _motor_matches_fn(r.get("equipment", ""), fn_num)
            and _motor_matches_fn(r.get("subequipment", ""), fn_num)
        ]

    out = dict(parsed)
    out["function"] = want
    # FUNCTION-level description (PLTXT)
    fn_desc = normalize_pltxt(str(parsed.get("description") or ""))
    if not fn_desc:
        nearby = None
        if inventory:
            # best-effort: pull dossier-ish nearby from structural later via caller
            pass
        fn_desc = description_from_nearby(want, parsed.get("nearby_text") or raw_text)
    if not fn_desc.startswith(want):
        fn_desc = normalize_pltxt(f"{want} {fn_desc}")
    out["description"] = fn_desc[:40]
    out["rows"] = refined_rows
    return out


def resolve_cross_function_tags(
    function_payloads: List[Dict[str, Any]],
    locations: Dict[str, Tuple[float, float]],
) -> None:
    """
    GT sometimes lists the same line under multiple FUNCTIONs (e.g. 35-24-189).
    Do not strip shared tags. Kept as a no-op hook for future heuristics.
    """
    return


def rows_from_ai(
    order_start: int,
    context: Dict[str, str],
    tag: str,
    parsed: Dict[str, Any],
    parent: Optional[Dict[str, Any]] = None,
) -> Tuple[List[Dict[str, str]], int]:
    """
    Emit GT-shaped hierarchy rows with deterministic SAP MASK paths:

      process root MASK
      SUB-PROCESS + MASK
      SUB-PROCESS + FUNCTION + MASK + DESCRIPTION
      EQUIPMENT / SUB-EQUIPMENT children (MASK blank; DESCRIPTION when available)
    """
    rows: List[Dict[str, str]] = []
    order = order_start
    want = normalize_tag(tag)
    # SUB-PROCESS comes from per-drawing FLOC context — never from AI few-shot bleed.
    sub_process = str(context.get("sub_process") or DEFAULT_SUB_PROCESS).strip()
    function = normalize_tag(parsed.get("function") or want) or want
    paths = floc_paths_for_function(function, context)
    fn_desc = normalize_pltxt(str(parsed.get("description") or ""))
    if not fn_desc:
        nearby = (parent or {}).get("nearby_descriptions")
        fn_desc = description_from_nearby(function, nearby)
    if fn_desc and not fn_desc.startswith(function):
        fn_desc = normalize_pltxt(f"{function} {fn_desc}")

    def add_row(
        *,
        sub: str = "",
        fn: str = "",
        equipment: str = "",
        subequipment: str = "",
        mask: str = "",
        description: str = "",
    ) -> None:
        nonlocal order
        rows.append(
            {
                "ORDER": str(order),
                "SITE": context.get("site", ""),
                "LINE": context.get("line", ""),
                "PROCESS": context.get("process", ""),
                "SUB-PROCESS": sub,
                "FUNCTION": fn,
                "EQUIPMENT": equipment,
                "SUB-EQUIPMENT": subequipment,
                "MASK": mask[:30],
                "DESCRIPTION": normalize_pltxt(description)[:40],
            }
        )
        order += 1

    add_row(
        mask=paths["process"],
        description=context.get("process_name") or context.get("process") or "BROKE SYSTEM",
    )
    add_row(
        sub=sub_process,
        mask=paths["subprocess"],
        description=context.get("process_name") or "BROKE SYSTEM",
    )
    add_row(
        sub=sub_process,
        fn=function,
        mask=paths["function"],
        description=fn_desc,
    )

    raw_rows = parsed.get("rows")
    if isinstance(raw_rows, list) and raw_rows:
        for child in raw_rows:
            if not isinstance(child, dict):
                continue
            eq = normalize_tag(str(child.get("equipment") or "").strip())
            sub_eq = normalize_tag(str(child.get("subequipment") or "").strip())
            child_desc = str(child.get("description") or "").strip()
            if eq and sub_eq:
                add_row(equipment=eq, description=child_desc or eq)
                add_row(subequipment=sub_eq, description="")
            elif eq:
                add_row(equipment=eq, description=child_desc or eq)
            elif sub_eq:
                add_row(subequipment=sub_eq, description=child_desc or sub_eq)
        return rows, order

    # Backward compatible: old subequipment[] schema
    for child in parsed.get("subequipment") or []:
        if not isinstance(child, dict):
            continue
        name = str(child.get("name") or child.get("tag") or "").strip()
        if not name:
            continue
        mask = str(child.get("mask") or "").strip()
        token = mask if TAG_TOKEN_RE.search(mask or "") else name
        m = TAG_TOKEN_RE.search(token)
        tag_token = normalize_tag(m.group(0) if m else token)
        add_row(equipment=tag_token, description=tag_token)
    return rows, order


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    from dwg_reader.io import write_csv_rows

    write_csv_rows(path, rows, CSV_COLUMNS)


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
    aws_profile: str = "",
    crop_half: Optional[float] = None,
) -> int:
    """Library entry used by the orchestrator instead of subprocess."""
    if aws_profile:
        os.environ["AWS_PROFILE"] = aws_profile
    args = argparse.Namespace(
        input=str(input_path),
        output_dir=str(out_dir),
        tags=tag,
        crop_half=float(crop_half) if crop_half is not None else 165.0,
        crop_half_min=105.0,
        dpi=260,
        model_id=model_id,
        region=region,
        shots_only=False,
        prompt_file=prompt_file,
        reuse_shots=reuse_shots,
        legend=str(LEGEND_PATH),
        inventory_json=str(inventory_json),
        hierarchy_csv_out=str(per_tag_csv),
        hierarchy_json_out=str(per_tag_json),
        no_clean_prev=no_clean_prev,
    )
    return run_hierarchy_from_args(args)


def main() -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="Viewer screenshots + Bedrock hierarchy CSV")
    parser.add_argument("--input", default="inputs/Broke System.dwg")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--tags", default="35-24L009,35-24P519")
    parser.add_argument(
        "--crop-half",
        type=float,
        default=165.0,
        help="Max half-size of adaptive zoom window (CAD units)",
    )
    parser.add_argument(
        "--crop-half-min",
        type=float,
        default=105.0,
        help="Min half-size of adaptive zoom window (CAD units)",
    )
    parser.add_argument("--dpi", type=int, default=260)
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--region", default=None)
    parser.add_argument("--shots-only", action="store_true", help="Only write viewer PNGs, skip Bedrock")
    parser.add_argument(
        "--prompt-file",
        default=HIERARCHY_PROMPT_FILE,
        help="Prompt template under prompts/ (default: pid_hierarchy_gt_v8.md)",
    )
    parser.add_argument(
        "--reuse-shots",
        action="store_true",
        help="Reuse existing evidence viewer PNGs instead of re-rendering",
    )
    parser.add_argument(
        "--legend",
        default=str(LEGEND_PATH),
        help="Legend PNG sent as Image 2 for valve type classification (default: standards/legend.png)",
    )
    parser.add_argument(
        "--inventory-json",
        default="",
        help="Optional pid_inventory.json for candidate tags (default: jsons/<stem>.pid_inventory.json)",
    )
    parser.add_argument(
        "--hierarchy-csv-out",
        default="",
        help="Optional explicit path for hierarchy CSV output (default: <output-dir>/<stem>.hierarchy.csv)",
    )
    parser.add_argument(
        "--hierarchy-json-out",
        default="",
        help="Optional explicit path for hierarchy AI JSON output (default: outputs/jsons/<stem>.hierarchy_ai.json)",
    )
    parser.add_argument("--no-clean-prev", action="store_true")
    return run_hierarchy_from_args(parser.parse_args())


def run_hierarchy_from_args(args: argparse.Namespace) -> int:

    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    ev_dir = evidence_dir(out_dir)
    log_dir = logs_dir(out_dir)
    base = safe_name(input_path)
    tags = [normalize_tag(t) for t in args.tags.split(",") if t.strip()]
    legend_path: Optional[Path] = Path(args.legend).expanduser().resolve() if args.legend else None
    if legend_path and not legend_path.exists():
        logger.warning(f"[warn] Legend not found at {legend_path}; valve type tokens will be omitted")
        legend_path = None
    elif legend_path:
        logger.info(f"[legend] {legend_path.name} will be sent as Image 2 for valve classification")
    out_csv = (
        Path(args.hierarchy_csv_out).expanduser().resolve()
        if args.hierarchy_csv_out
        else out_dir / f"{base}.hierarchy.csv"
    )
    out_json = (
        Path(args.hierarchy_json_out).expanduser().resolve()
        if args.hierarchy_json_out
        else json_path(out_dir, f"{base}.hierarchy_ai.json")
    )
    enr_path = find_json(out_dir, f"{base}.pid_enrichment.json")
    inv_path = (
        Path(args.inventory_json).expanduser()
        if args.inventory_json
        else find_json(out_dir, f"{base}.pid_inventory.json")
    )

    if not enr_path.exists():
        logger.warning(f"[warn] No enrichment JSON at {enr_path}; dossier will use inventory only.")
        enrichment = {}
    else:
        enrichment = load_json(enr_path)

    if not args.no_clean_prev:
        clear_previous_outputs(
            out_dir,
            base,
            suffixes=(
                ".hierarchy.csv",
                ".hierarchy.xlsx",  # legacy cleanup only
                ".hierarchy_ai.json",
            ),
        )
        if not args.reuse_shots:
            clear_evidence_outputs(out_dir, base, tags)
            for t in tags:
                legacy = out_dir / f"{base}.viewer_{t}.png"
                if legacy.is_file():
                    legacy.unlink()

    tag_register = enrichment.get("tag_register") or []
    inventory = load_json(inv_path) if inv_path.exists() else None
    structural_path = find_json(out_dir, f"{base}.structural_dump.json")
    structural = load_json(structural_path) if structural_path.exists() else None
    context = title_context(enrichment, input_path.stem, input_path)
    region = args.region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "eu-west-2"

    doc = None
    if not args.reuse_shots or args.shots_only:
        logger.info("[1/3] Opening DWG via ODA for viewer screenshots...")
        doc = load_drawing(input_path)
        logger.info("[1/3] DWG opened")
    else:
        logger.info("[1/3] Reusing existing viewer screenshots")

    results = []
    csv_rows: List[Dict[str, str]] = []
    order = 1
    function_payloads: List[Dict[str, Any]] = []
    tag_locations = text_tag_locations(structural)

    for tag in tags:
        logger.info(f"\n=== {tag} ===")
        parent = pick_parent(tag_register, tag, inventory=inventory)
        if not parent:
            logger.warning(f"[warn] No parent coords for {tag}")
            results.append({"tag": tag, "error": "parent_not_found"})
            continue
        center = crop_center(tag, parent, tag_register)
        shot = ev_dir / f"{base}.viewer_{tag}.png"
        if doc is not None:
            viewer_screenshot(
                doc,
                center,
                parent,
                tag,
                tag_register,
                shot,
                half_max=args.crop_half,
                half_min=args.crop_half_min,
                dpi=args.dpi,
            )
            logger.info(f"[2/3] Viewer shot: {shot}")
        elif not shot.exists():
            logger.error(f"[error] Missing shot {shot}; re-run without --reuse-shots")
            results.append({"tag": tag, "error": "missing_shot"})
            continue
        else:
            logger.info(f"[2/3] Reused shot: {shot}")

        candidates = collect_candidate_tags(
            tag, center, tag_register, inventory=inventory, structural=structural
        )
        dossier = build_equipment_dossier(
            tag,
            parent,
            center,
            tag_register,
            inventory=inventory,
            enrichment=enrichment,
            structural=structural,
        )
        logger.info(f"    candidates={len(candidates)} dossier_chars={len(dossier)}")

        if args.shots_only:
            results.append(
                {
                    "tag": tag,
                    "shot": str(shot),
                    "parent": parent,
                    "candidates": candidates,
                    "dossier": dossier,
                    "ai": None,
                }
            )
            continue

        try:
            ai = bedrock_hierarchy_from_shot(
                shot,
                tag,
                parent,
                context,
                args.model_id,
                region,
                prompt_file=args.prompt_file,
                candidates=candidates,
                parent_dossier=dossier,
                legend_path=legend_path,
            )
            logger.info(f"[3/3] Bedrock hierarchy received ({args.model_id})")
        except Exception as e:
            logger.error(f"[3/3] Bedrock failed: {e}")
            results.append({"tag": tag, "shot": str(shot), "parent": parent, "error": str(e)})
            continue

        parsed = ai.get("parsed") or {}
        if not parsed:
            logger.warning("[warn] Could not parse AI JSON; raw saved in hierarchy_ai.json")
            results.append(
                {
                    "tag": tag,
                    "shot": str(shot),
                    "parent": parent,
                    "candidates": candidates,
                    "dossier": dossier,
                    "ai": ai,
                }
            )
            continue

        peer_tags = [
            normalize_tag(p.get("tag") or p.get("name") or "")
            for p in (parsed.get("peers") or [])
            if isinstance(p, dict)
        ]
        peer_tags.extend([t for t in tags if t != tag])
        refined = refine_ai_hierarchy(
            tag,
            parsed,
            center=center,
            inventory=inventory,
            structural=structural,
            peer_tags=peer_tags,
            raw_text=str(ai.get("raw_text") or ""),
            candidates=candidates,
        )
        function_payloads.append(
            {
                "tag": tag,
                "function": normalize_tag(refined.get("function") or tag),
                "parsed": refined,
                "center": center,
                "ai": ai,
                "shot": str(shot),
                "parent": parent,
                "candidates": candidates,
                "dossier": dossier,
            }
        )
        logger.info(f"    function={refined.get('function')} "
            f"child_rows={len(refined.get('rows') or [])} "
            f"confidence={refined.get('confidence')}")

    if function_payloads:
        resolve_cross_function_tags(function_payloads, tag_locations)
        for payload in function_payloads:
            new_rows, order = rows_from_ai(
                order,
                context,
                payload["tag"],
                payload["parsed"],
                parent=payload.get("parent"),
            )
            csv_rows.extend(new_rows)
            results.append(
                {
                    "tag": payload["tag"],
                    "shot": payload["shot"],
                    "parent": payload["parent"],
                    "candidates": payload["candidates"],
                    "dossier": payload["dossier"],
                    "ai": payload["ai"],
                    "refined_rows": payload["parsed"].get("rows"),
                }
            )

    write_json(
        out_json,
        {
            "input": str(input_path),
            "mode": "viewer_shot_ai_gt",
            "evidence_dir": str(ev_dir),
            "site": context["site"],
            "line": context["line"],
            "process": context["process"],
            "sub_process": context.get("sub_process"),
            "model_id": args.model_id,
            "region": region,
            "prompt_file": args.prompt_file,
            "legend": str(legend_path) if legend_path else None,
            "results": results,
        },
    )
    if csv_rows:
        write_csv(out_csv, csv_rows)
        logger.info(f"\nWrote {out_csv} ({len(csv_rows)} rows)")
    else:
        logger.info("\nNo hierarchy CSV rows written (shots-only or AI parse failure)")
    logger.info(f"Evidence images: {ev_dir}")
    logger.info(f"JSON: {out_json}")
    logger.info(f"Logs dir: {log_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())