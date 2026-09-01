#!/usr/bin/env python3
"""
Per-tag valve classification: tight CAD crop + legend → cached type + parent fn.

Runs for every drawing standard (SML/Valmet, GOR, KSD, …). No CAD type
heuristics and no TIPO overlay — the model reads the crop against
``standards/legend.png``.

Fixes the four remaining valve gaps:
  1. Tight crop around the valve insert (not the whole FUNCTION screenshot)
  2. Full legend vocabulary including AV-M
  3. Numeric tags on P-VALVEPOS / P-CVPOS are valves even without VLV in the text
  4. Drain valves under a conveyor/pump are reassigned to the nearest pulper/tank

Cache: outputs/jsons/<stem>.valve_types.json
Export reads this cache; inputs/valve_type_overrides.json still wins.
"""

from __future__ import annotations

import dwg_reader.dwg_warn as dwg_warn  # noqa: F401 — silence boto3 Python 3.9 deprecation noise

import argparse
import csv
import json
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from dwg_reader.config import DEFAULT_MODEL_ID, LEGEND_PATH
from dwg_reader.dwg_floc_context import (
    ALLOWED_VALVE_TOKENS,
    apply_sop_valve_type,
    combine_valve_type,
    is_pump_equipment,
    is_valve_equipment,
)
from dwg_reader.dwg_valve_classify_v2 import load_v2_prompt, parse_v2_response
from dwg_reader.dwg_pure_dump import evidence_dir, find_json, json_path, safe_name, write_json
from dwg_reader.logutil import configure_logging, get_logger

logger = get_logger(__name__)

VALVE_LAYERS = frozenset({"P-VALVEPOS", "P-CVPOS", "P-SYMB", "1-VALVE TEXT GOR"})

_CONVEYOR_RE = re.compile(r"\b(CVYR|CONVEYOR)\b", re.I)
_VESSEL_HINT_RE = re.compile(r"\b(PLPR|PULPER|TNK|TANK|CHEST|VESSEL|THICKENER)\b", re.I)

# V2 vision prompt lives in prompts/valve_classify_v2.md (loaded via load_v2_prompt).


_EXCLUSIVE_ATTACHMENTS = frozenset({"DRN", "FLS", "SMP"})


def _xy(obj: Any) -> Optional[Tuple[float, float]]:
    if obj is None:
        return None
    if isinstance(obj, dict):
        for key in ("insert", "position", "xy"):
            got = _xy(obj.get(key))
            if got:
                return got
        try:
            return float(obj["x"]), float(obj["y"])
        except (KeyError, TypeError, ValueError):
            return None
    if isinstance(obj, (list, tuple)) and len(obj) >= 2:
        try:
            return float(obj[0]), float(obj[1])
        except (TypeError, ValueError):
            return None
    return None


def _norm_tag(tag: str) -> str:
    return re.sub(r"\s+", "", str(tag or "")).upper()


def collect_text_locations(structural: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Map exact drawing text → {x,y,layer}. Prefers valve-layer entries for duplicate tags."""
    all_locs: Dict[str, List[Dict[str, Any]]] = {}
    for ent in structural.get("text_entities") or []:
        if not isinstance(ent, dict):
            continue
        txt = _norm_tag(str(ent.get("text") or ""))
        xy = _xy(ent)
        if not txt or xy is None:
            continue
        layer = str(ent.get("layer") or "")
        all_locs.setdefault(txt, []).append({"x": xy[0], "y": xy[1], "layer": layer})
    out: Dict[str, Dict[str, Any]] = {}
    for txt, locs in all_locs.items():
        # When a tag label appears multiple times, prefer the valve-layer occurrence —
        # reference copies on annotation layers would snap to the wrong position.
        valve_locs = [loc for loc in locs if loc["layer"] in VALVE_LAYERS]
        out[txt] = (valve_locs or locs)[0]
    return out


def collect_gor_attribute_tag_locations(structural: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """GOR drawings store valve tags in TAG VALVOLA INSERT attributes, not TEXT entities.

    Returns a tag→{x,y,layer} map that can be merged into text_locations so the
    rest of the valve-locate pipeline treats them like any other located tag.
    """
    out: Dict[str, Dict[str, Any]] = {}
    for ins in structural.get("inserts") or []:
        if not isinstance(ins, dict):
            continue
        if ins.get("name") != "TAG VALVOLA":
            continue
        xy = _xy(ins)
        if xy is None:
            continue
        tag_val = ""
        for a in ins.get("attributes", []):
            if isinstance(a, dict) and (a.get("tag") or "").upper() == "TAG_VALVOLA":
                tag_val = str(a.get("text") or a.get("value") or "").strip()
                break
        if not tag_val:
            continue
        key = _norm_tag(tag_val)
        if key:
            out[key] = {"x": xy[0], "y": xy[1], "layer": "1-VALVE TEXT GOR"}
    return out


_PIPE_DN_TEXT_RE = re.compile(r"^003-\d+$", re.I)


def pipe_dn_label_near_tag(
    tag: str,
    text_locations: Dict[str, Dict[str, Any]],
    structural: Dict[str, Any],
    *,
    radius: float = 20.0,
) -> bool:
    """True when a 003-xx pipe DN label sits beside the valve tag (NC isolation spool)."""
    loc = text_locations.get(_norm_tag(tag))
    if not loc:
        return False
    x0, y0 = float(loc["x"]), float(loc["y"])
    for ent in structural.get("text_entities") or []:
        if not isinstance(ent, dict):
            continue
        txt = str(ent.get("text") or "").strip()
        if not _PIPE_DN_TEXT_RE.fullmatch(txt):
            continue
        xy = _xy(ent)
        if xy and abs(xy[0] - x0) <= radius and abs(xy[1] - y0) <= radius:
            return True
    return False


def collect_valve_inserts(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for ins in structural.get("inserts") or []:
        if not isinstance(ins, dict):
            continue
        layer = str(ins.get("layer") or "")
        if layer not in VALVE_LAYERS:
            continue
        xy = _xy(ins)
        if xy is None:
            continue
        rows.append(
            {
                "x": xy[0],
                "y": xy[1],
                "layer": layer,
                "name": str(ins.get("name") or ""),
            }
        )
    return rows


_DRAIN_HINT_RE = re.compile(r"DRAIN|TROUGH|SUMP|\bDRN\b", re.I)


def collect_drain_markers(structural: Dict[str, Any]) -> List[Tuple[float, float]]:
    """CAD points that look like drain troughs / DRN labels (SOP: drain sits below the valve)."""
    pts: List[Tuple[float, float]] = []
    for ins in structural.get("inserts") or []:
        if not isinstance(ins, dict):
            continue
        blob = " ".join(
            str(ins.get(k) or "")
            for k in ("name", "block", "block_name", "layer", "type")
        )
        if not _DRAIN_HINT_RE.search(blob):
            continue
        xy = _xy(ins)
        if xy:
            pts.append(xy)
    for ent in structural.get("text_entities") or []:
        if not isinstance(ent, dict):
            continue
        if not _DRAIN_HINT_RE.search(str(ent.get("text") or "")):
            continue
        xy = _xy(ent)
        if xy:
            pts.append(xy)
    return pts


def drain_below_valve(
    x: float,
    y: float,
    markers: List[Tuple[float, float]],
    *,
    dx: float = 60.0,   # lateral tolerance — ~3× bowtie half-width in CAD units
    down: float = 160.0,  # vertical search depth — measured from drawing: trough is 80-150 units below valve
) -> bool:
    """True if a drain marker sits under the valve (CAD Y-up)."""
    for mx, my in markers:
        if abs(mx - x) <= dx and (y - down) <= my <= (y - 6):
            return True
    return False


def collect_functions(inventory: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for fn in inventory.get("functions") or []:
        if not isinstance(fn, dict):
            continue
        tag = _norm_tag(str(fn.get("function") or ""))
        xy = _xy(fn)
        if not tag or xy is None:
            continue
        desc = str(fn.get("description") or fn.get("nearby_descriptions") or "")
        rows.append(
            {
                "tag": tag,
                "x": xy[0],
                "y": xy[1],
                "kind": str(fn.get("kind") or ""),
                "description": desc,
            }
        )
    return rows


def nearest(rows: Iterable[Dict[str, Any]], x: float, y: float) -> Optional[Dict[str, Any]]:
    best = None
    best_d = None
    for row in rows:
        d = ((float(row["x"]) - x) ** 2 + (float(row["y"]) - y) ** 2) ** 0.5
        if best_d is None or d < best_d:
            best, best_d = row, d
    if best is None:
        return None
    out = dict(best)
    out["distance"] = best_d
    return out


_WFL_LINE_RE = re.compile(r"\bWFL\b", re.I)


def wfl_drain_line_hint(tag: str, inventory: Optional[Dict[str, Any]] = None) -> bool:
    """True when inventory marks this tag as a white-water floor (WFL) drain line."""
    want = _norm_tag(tag)
    for fn in (inventory or {}).get("functions") or []:
        if not isinstance(fn, dict):
            continue
        if _norm_tag(str(fn.get("function") or "")) != want:
            continue
        blob = " ".join(
            str(fn.get(k) or "")
            for k in ("description", "nearby_descriptions", "line_number", "kind")
        )
        if _WFL_LINE_RE.search(blob):
            return True
    return False


def collect_symb_bowtie_inserts(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Bowtie/check symbols on P-SYMB — some WFL drain taps lack P-VALVEPOS inserts."""
    rows: List[Dict[str, Any]] = []
    for ins in structural.get("inserts") or []:
        if not isinstance(ins, dict):
            continue
        if str(ins.get("layer") or "") != "P-SYMB":
            continue
        name = str(ins.get("name") or ins.get("block_name") or "")
        if not name.startswith("P7A130"):
            continue
        xy = _xy(ins)
        if xy is None:
            continue
        rows.append({"x": xy[0], "y": xy[1], "layer": "P-SYMB", "name": name})
    return rows


def _snap_valve_insert(
    x: float,
    y: float,
    valve_inserts: List[Dict[str, Any]],
    *,
    wfl_drain_hint: bool = False,
    symb_inserts: Optional[List[Dict[str, Any]]] = None,
    snap_radius: float = 40.0,
) -> Tuple[Optional[Dict[str, Any]], float]:
    """Pick the valve insert a tag label points at."""
    candidates: List[Tuple[float, Dict[str, Any]]] = []
    for row in valve_inserts:
        d = ((float(row["x"]) - x) ** 2 + (float(row["y"]) - y) ** 2) ** 0.5
        if d <= snap_radius:
            candidates.append((d, row))
    if not candidates:
        return None, 0.0
    candidates.sort(key=lambda item: item[0])
    best_d, best = candidates[0]

    # WFL tags above the tank sump often sit beside a process cross-header valve
    # while the leader line continues down the brown drain branch (35-24-121).
    if wfl_drain_hint and best_d < 12.0 and (y - float(best["y"])) < 12.0:
        for row in symb_inserts or []:
            sx, sy = float(row["x"]), float(row["y"])
            drop = y - sy
            if 20.0 <= drop <= 36.0 and abs(sx - x) < 12.0:
                out = dict(row)
                return out, ((sx - x) ** 2 + (sy - y) ** 2) ** 0.5
    return best, best_d


def apply_wfl_drain_attachment(vtype: str, *, wfl_drain_hint: bool) -> str:
    """WFL floor-line isolation valves are drain taps by SOP."""
    if not wfl_drain_hint:
        return vtype
    tokens = str(vtype or "").upper().split()
    if not tokens or any(t in tokens for t in ("DRN", "FLS", "SMP")):
        return vtype
    body = strip_attachment_tokens(" ".join(tokens))
    if body.split()[0] in {"NC", "HV", "CHK", "NO"}:
        return merge_body_and_attachment(body, "DRN")
    return vtype


def locate_valve(
    tag: str,
    *,
    text_locations: Dict[str, Dict[str, Any]],
    valve_inserts: List[Dict[str, Any]],
    symb_inserts: Optional[List[Dict[str, Any]]] = None,
    wfl_drain_hint: bool = False,
) -> Optional[Dict[str, Any]]:
    """Find drawing XY for a tag and snap to the nearest valve insert."""
    want = _norm_tag(tag)
    loc = text_locations.get(want)
    if loc is None:
        return None
    x, y = float(loc["x"]), float(loc["y"])
    snapped_row, snap_d = _snap_valve_insert(
        x,
        y,
        valve_inserts,
        wfl_drain_hint=wfl_drain_hint,
        symb_inserts=symb_inserts,
    )
    snapped = None
    if snapped_row is not None:
        snapped = dict(snapped_row)
        snapped["distance"] = snap_d
    if snapped is not None and snapped["distance"] <= 40.0:  # ~2× bowtie half-width snap tolerance
        x, y = float(snapped["x"]), float(snapped["y"])
        layer = str(snapped.get("layer") or loc.get("layer") or "")
        block = str(snapped.get("name") or "")
        dist = snapped["distance"]
    else:
        layer = str(loc.get("layer") or "")
        block = ""
        dist = 0.0
    return {
        "tag": want,
        "x": x,
        "y": y,
        "layer": layer,
        "block": block,
        "text_layer": str(loc.get("layer") or ""),
        "insert_distance": dist,
        "is_valve": layer in VALVE_LAYERS or str(loc.get("layer") or "") in VALVE_LAYERS,
    }


def is_vessel_function(fn: Dict[str, Any]) -> bool:
    tag = str(fn.get("tag") or "")
    desc = str(fn.get("description") or "")
    if _CONVEYOR_RE.search(desc) or _CONVEYOR_RE.search(tag):
        return False
    if re.match(r"^35-\d{2}[LT]\d+", tag, re.I):
        return True
    return bool(_VESSEL_HINT_RE.search(desc))


def pick_parent_fn(
    *,
    x: float,
    y: float,
    hierarchy_fn: str,
    functions: List[Dict[str, Any]],
    valve_type: str = "",
    radius: float = 250.0,
    valve_tag: str = "",
    lin_edges: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Keep hierarchy ownership unless the parent is a conveyor or this is a drain.

    Drain valves and any valve sitting on a conveyor (L006 vs L005 for HV-548 /
    35-24-137) reassign to the nearest pulper/tank. LIN_FROM/LIN_TO neighbors
    that are vessels win when the graph is present (R27/B04).
    """
    hier = _norm_tag(hierarchy_fn)
    vtype = str(valve_type or "").upper()

    if valve_tag and lin_edges:
        from dwg_reader.dwg_lin_graph import neighbors as lin_neighbors

        nbs = lin_neighbors(lin_edges, valve_tag)
        vessel_hits = [
            fn for fn in functions
            if fn.get("tag") in nbs and is_vessel_function(fn)
        ]
        if vessel_hits:
            vessel_hits.sort(key=lambda fn: (fn["x"] - x) ** 2 + (fn["y"] - y) ** 2)
            return vessel_hits[0]["tag"]

    hier_row = next((f for f in functions if f["tag"] == hier), None)
    if hier_row and is_vessel_function(hier_row):
        return hier

    is_conveyor_parent = bool(
        hier_row
        and (
            _CONVEYOR_RE.search(str(hier_row.get("description") or ""))
            or _CONVEYOR_RE.search(str(hier_row.get("tag") or ""))
        )
    )
    if not is_conveyor_parent and "DRN" not in vtype.split():
        return hier

    vessels = []
    for fn in functions:
        if fn.get("kind") and fn["kind"] not in {"equipment", ""}:
            continue
        if not is_vessel_function(fn):
            continue
        d = ((fn["x"] - x) ** 2 + (fn["y"] - y) ** 2) ** 0.5
        if d <= radius:
            vessels.append((d, fn["tag"]))
    if vessels:
        vessels.sort()
        return vessels[0][1]
    return hier


def strip_attachment_tokens(vtype: str) -> str:
    """Remove mutually-exclusive attachment tokens (classified in a separate vision pass)."""
    return " ".join(t for t in str(vtype or "").split() if t not in _EXCLUSIVE_ATTACHMENTS)


def merge_body_and_attachment(body: str, attachment: str) -> str:
    """Combine body classify + single attachment token; enforce exclusivity."""
    parts = [t for t in strip_attachment_tokens(body).split() if t]
    att = str(attachment or "").upper().strip()
    if att in _EXCLUSIVE_ATTACHMENTS and att not in parts:
        parts.append(att)
    return apply_sop_valve_type(" ".join(parts))


def parse_type_tokens(raw: str) -> str:
    text = re.sub(r"[^A-Z0-9\-\s]", " ", str(raw or "").upper())
    text = text.replace("AVM", "AV-M").replace("AV_M", "AV-M")
    found: List[str] = []
    # Longer tokens first so AV-M is not split into AV.
    text = text.replace("GLOBE", "GLV").replace("GLOBAL", "GLV")
    for tok in (
        "AV-M", "YSTR", "3WV", "PLUG", "AAV", "GLV", "CHK", "PRV",
        "FLS", "SMP", "DRN", "AUTO", "AV", "NC", "NO", "SV", "GF", "HV",
    ):
        if re.search(rf"(?:^|\s){re.escape(tok)}(?:\s|$)", text):
            mapped = "AV" if tok == "AUTO" else tok
            if mapped in ALLOWED_VALVE_TOKENS and mapped not in found:
                found.append(mapped)
    if "UNKNOWN" in text.split() and not found:
        return ""
    return apply_sop_valve_type(strip_attachment_tokens(" ".join(found)))


def _log(msg: str) -> None:
    logger.info(msg)


def build_entity_extent_index(doc) -> List[Tuple[Any, float, float, float, float]]:
    """Compute modelspace bboxes once so each crop is a cheap window filter."""
    from ezdxf import bbox as ezbbox

    indexed: List[Tuple[Any, float, float, float, float]] = []
    n = 0
    for entity in doc.modelspace():
        n += 1
        try:
            ext = ezbbox.extents([entity], fast=True)
            if ext is None or not ext.has_data:
                continue
            indexed.append(
                (
                    entity,
                    float(ext.extmin.x),
                    float(ext.extmin.y),
                    float(ext.extmax.x),
                    float(ext.extmax.y),
                )
            )
        except Exception:
            continue
        if n % 2000 == 0:
            _log(f"  [index] scanned {n} entities...")
    _log(f"  [index] {len(indexed)} drawable of {n} modelspace entities")
    return indexed


def tight_valve_screenshot(
    doc,
    x: float,
    y: float,
    out_path: Path,
    half: float = 42.0,
    dpi: int = 220,
    extra_below: float = 0.0,
    entity_index: Optional[List[Tuple[Any, float, float, float, float]]] = None,
) -> Optional[Path]:
    """ODA/PyMuPDF raster around the valve; extra_below zooms out toward the drain."""
    try:
        from ezdxf import bbox as ezbbox
        from ezdxf.addons.drawing import Frontend, RenderContext
        from ezdxf.addons.drawing import layout as ezlayout
        from ezdxf.addons.drawing import pymupdf as ez_pymupdf
        from ezdxf.math import BoundingBox2d
    except Exception as exc:
        _log(f"[warn] CAD render unavailable: {exc}")
        return None

    below = max(0.0, float(extra_below or 0.0))
    xmin, ymin, xmax, ymax = x - half, y - half - below, x + half, y + half
    ents = []
    if entity_index is not None:
        for entity, ex0, ey0, ex1, ey1 in entity_index:
            if ex1 < xmin or ex0 > xmax or ey1 < ymin or ey0 > ymax:
                continue
            ents.append(entity)
    else:
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
        return None

    ctx = RenderContext(doc)
    backend = ez_pymupdf.PyMuPdfBackend()
    Frontend(ctx, backend).draw_entities(ents)
    backend.finalize()
    span = max(xmax - xmin, ymax - ymin, 1.0)
    page = ezlayout.Page(120, 120, units=ezlayout.Units.mm)
    settings = ezlayout.Settings(
        fit_page=False,
        scale=120.0 / span,
        page_alignment=ezlayout.PageAlignment.MIDDLE_CENTER,
    )
    png = backend.get_pixmap_bytes(
        page=page,
        settings=settings,
        dpi=dpi,
        fmt="png",
        render_box=BoundingBox2d([(xmin, ymin), (xmax, ymax)]),
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(png)
    return out_path


def valve_ring_frac(half: float, extra_below: float) -> Tuple[float, float]:
    """Yellow-ring position in the PNG (cx, cy from top-left, 0-1)."""
    height = max(2.0 * half + max(0.0, extra_below), 1.0)
    return 0.5, half / height


def annotate_valve_crop(
    crop_path: Path,
    tag: str,
    cx_frac: float = 0.5,
    cy_frac: float = 0.5,
) -> Path:
    """Yellow ring on the TARGET valve + tag label."""
    from PIL import Image, ImageDraw, ImageFont

    im = Image.open(crop_path).convert("RGB")
    w, h = im.size
    cx, cy = int(w * cx_frac), int(h * cy_frac)
    r = max(28, min(w, h) // 8)
    draw = ImageDraw.Draw(im)
    for t in (4, 2):
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline="#FFD400", width=t)
    label = str(tag or "")
    try:
        font = ImageFont.truetype("Arial", 12)
    except Exception:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
    draw.rectangle((6, 6, 6 + 7 * max(len(label), 1) + 8, 24), fill="#000000")
    draw.text((10, 8), label, fill="#FFD400", font=font)
    marked = crop_path.with_name(f"{crop_path.stem}.marked.png")
    im.save(marked)
    return marked


def zoom_center_png(
    crop_path: Path,
    frac: float = 0.32,
    cx_frac: float = 0.5,
    cy_frac: float = 0.5,
) -> bytes:
    """Bytes of a zoom around the TARGET (not necessarily the image centre)."""
    from PIL import Image
    from io import BytesIO

    im = Image.open(crop_path).convert("RGB")
    w, h = im.size
    cw = max(32, int(w * frac))
    ch = max(32, int(h * frac))
    cx, cy = int(w * cx_frac), int(h * cy_frac)
    x0 = min(max(0, cx - cw // 2), max(0, w - cw))
    y0 = min(max(0, cy - ch // 2), max(0, h - ch))
    resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.NEAREST)
    zoom = im.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), resample)
    buf = BytesIO()
    zoom.save(buf, format="PNG")
    return buf.getvalue()


def below_valve_png(
    crop_path: Path,
    *,
    half: float = 42.0,
    extra_below: float = 60.0,
    include_drop_frac: float = 0.08,
) -> bytes:
    """Enlarged bottom strip — the extra_below zone where drain troughs appear."""
    from PIL import Image
    from io import BytesIO

    im = Image.open(crop_path).convert("RGB")
    w, h = im.size
    total = max(2.0 * half + max(0.0, extra_below), 1.0)
    below_frac = max(0.25, min(0.65, extra_below / total + include_drop_frac))
    y0 = max(0, int(h * (1.0 - below_frac)))
    strip = im.crop((0, y0, w, h))
    resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.NEAREST)
    zoom = strip.resize((w, h), resample)
    buf = BytesIO()
    zoom.save(buf, format="PNG")
    return buf.getvalue()


_bedrock_lock = threading.Lock()
_bedrock_clients: Dict[Tuple[str, str], Any] = {}
_legend_bytes: Optional[bytes] = None


def body_zoom_png(
    crop_path: Path,
    cx_frac: float = 0.5,
    cy_frac: float = 0.5,
) -> bytes:
    """Bowtie zoom biased slightly below the tag so the leader-line valve is centred."""
    return zoom_center_png(
        crop_path,
        frac=0.46,
        cx_frac=cx_frac,
        cy_frac=min(0.82, cy_frac + 0.07),
    )


def branch_context_png(
    crop_path: Path,
    frac: float = 0.62,
    cx_frac: float = 0.5,
    cy_frac: float = 0.5,
) -> bytes:
    """Wider zoom around the target valve — shows side/down branches for attachment typing."""
    return zoom_center_png(crop_path, frac=frac, cx_frac=cx_frac, cy_frac=cy_frac)


ATTACHMENT_VALUES = frozenset({"DRN", "FLS", "SMP", "NONE"})

ATTACHMENT_PROMPT = """\
You MUST respond with ONLY a JSON object. No explanation, no markdown, no steps.
Format: {{"attachment": "none"}} or {{"attachment": "DRN"}} or {{"attachment": "FLS"}} or {{"attachment": "SMP"}}

Valve {TAG}. Image 1 = marked crop (yellow ring ≈ target). Image 2 = bowtie zoom.
Image 3 = branch context (pipes connected to target). Image 4 = legend. Image 5 = below valve.

Find label "{TAG}" in Image 1 and follow its leader/tag line to the bowtie it
attaches to. Pick EXACTLY ONE attachment for THAT valve only, not other nearby
bowties. If the tag points to the UPPER valve on a vertical branch and a separate
downstream valve drains to floor, the upper valve is not DRN unless its own pipe
enters the floor recess.

Pick EXACTLY ONE (mutually exclusive — never combine):

  SMP — sample take-off branch from the target valve's pipe ending in a sampling
        ARROWHEAD or funnel/cup symbol (Image 3), per legend SAMPLING. The branch
        does NOT discharge into a floor sump. Angled sample spool (003-50) ending
        in a sample point = SMP.

  FLS — small L-hook / stub welded to the SIDE of the target bowtie body (Image 2),
        per legend FLUSHING (horizontal stub + short vertical leg on the bowtie).
        OR a horizontal spool/tee branch (003-50) from a process header holding an
        isolation bowtie — flush connection, NOT a sample funnel.

  DRN — the pipe FROM the target valve runs downward and discharges into a floor
        trough, sump recess, U-channel, or open drain (Image 5). Downward arrow at
        branch end directly BELOW the target bowtie (no other valve in between).
        Vessel/tank bottom outlet line turning downward after the valve (often
        marked "D") = DRN. Size 001-80 often appears under the tag.

  none — plain in-line valve; no sample funnel, no L-hook, no floor drain
         directly below THIS bowtie. If a second downstream valve on the same
         branch reaches the floor drain, the upper valve is none.

Decision order (first match wins):
  1. Sample funnel/cup/arrowhead on branch, NOT into floor → SMP
  2. L-hook on target bowtie side → FLS (ignore unrelated floor lines elsewhere)
  3. This valve's pipe drops into floor recess/trough/U-channel → DRN
  4. else → none
"""


def parse_attachment_response(raw: str) -> str:
    """Parse attachment token from JSON or truncated prose."""
    text = str(raw or "").strip()
    if not text:
        return ""
    try:
        obj = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", text))
        if isinstance(obj, dict):
            val = str(obj.get("attachment") or "none").upper().strip()
            return "" if val in {"", "NONE", "NULL"} else val if val in _EXCLUSIVE_ATTACHMENTS else ""
    except Exception:
        pass
    for m in re.finditer(r'"attachment"\s*:\s*"(DRN|FLS|SMP|none)"', text, re.I):
        val = m.group(1).upper()
        if val in _EXCLUSIVE_ATTACHMENTS:
            return val
    upper = text.upper()
    # Prose fallback when JSON is truncated (maxTokens cut-off).
    for tok in ("FLS", "SMP", "DRN"):
        if re.search(rf"\b{tok}\b", upper):
            return tok
    if re.search(r"\b(NONE|PLAIN|NO ATTACHMENT)\b", upper):
        return ""
    return ""


FLS_FLUSH_RETRY_PROMPT = """\
You MUST respond with ONLY a JSON object.
Format: {{"attachment": "FLS"}} or {{"attachment": "DRN"}} or {{"attachment": "none"}}

Valve {TAG}. Follow the leader line from "{TAG}" to its bowtie.

  FLS — a short stub on THIS bowtie ends with a BLUNT OPEN PIPE END pointing into open air.
        No arrows, no funnel, no enclosure at the stub tip. Just a cut pipe in empty space.

  DRN — the stub or branch from THIS bowtie's own pipe reaches a drain / sump.
        Drain indicators that count ONLY when directly on the "{TAG}" bowtie's branch:
        • Large solid white downward arrows on this pipe branch → DRN
        • A row of small solid downward arrows (3–8 in a band) on this branch → DRN
        • A funnel or trapezoid at the branch end, followed by an arrow/channel below → DRN
        • This branch entering a rectangular box, U-trough, sump, or basin → DRN
        ⚠ Drain indicators visible beside a DIFFERENT labelled bowtie do NOT count for "{TAG}".

  none — plain inline valve; no service stub or drain branch on the "{TAG}" bowtie.

Key: open stub tip → FLS.  Arrows/funnel/enclosure on THIS bowtie's branch → DRN.  Neither → none.
"""

DRAIN_RETRY_PROMPT = """\
You MUST respond with ONLY a JSON object.
Format: {{"attachment": "DRN"}} or {{"attachment": "none"}}

Valve {TAG}. Follow the leader line from label "{TAG}" to its bowtie.

DRN — pipe from THIS bowtie reaches a floor drain / sump. Accept ANY of these visual forms:
      • One or more LARGE SOLID FLOW ARROWS (filled white arrowheads) pointing into a trough/tou.
      • A ROW of small solid downward arrows (3–8 arrows in a band) on a nearby pipe line.
      • A FUNNEL or TRAPEZOID shape at the pipe end (sometimes with a further arrow into a U-channel).
      • Pipe entering a RECTANGULAR BOX, U-trough, sump recess, or basin.
      • THIS valve's branch pipe connects at a T-junction / manifold that routes down to a drain.
        (Other bowties on PARALLEL branches at the same junction are EACH ALSO DRN independently.)
      Arrow direction may be down/up/left/right. Often a funnel/collector sits between the pipe and
      the trough. Parallel branches each with their own bowtie ALL draining to the same tou → each DRN.

none — plain in-line valve; or upper bowtie IN SERIES on one vertical pipe whose lower
       neighbour reaches the drain (not this bowtie's own pipe to the tou).
"""

DRN_DIRECT_RETRY_PROMPT = """\
You MUST respond with ONLY a JSON object.
Format: {{"attachment": "DRN"}} or {{"attachment": "none"}}

Valve {TAG}. Does THIS bowtie's own pipe branch reach a floor drain / sump? Accept ANY form:
• Large solid flow arrows on THIS branch pointing into a tou/trough/sump → DRN
• A funnel, trapezoid, or collector at THIS branch end, with an arrow/channel below → DRN
• THIS branch entering a rectangular box, U-trough, sump recess, or basin → DRN
• A row of small downward arrows on THIS branch → DRN
• THIS valve's own pipe enters a T-junction / manifold whose outlet goes to a drain → DRN
  (Other bowties on SEPARATE PARALLEL branches at the same T-junction are ALSO DRN independently
   — they are NOT "in series" with THIS bowtie and do NOT block this bowtie from being DRN.)

none — ONLY when the EXACT SAME pipe passes FIRST through THIS bowtie and then through a
      SECOND bowtie before reaching the drain, with no branch point between them.
      A valve on its OWN BRANCH pipe entering a common drain manifold IS DRN even if other
      bowties connect to the same manifold from different branches.
"""

FLS_STUB_ONLY_PROMPT = """\
You MUST respond with ONLY a JSON object.
Format: {{"attachment": "FLS"}} or {{"attachment": "none"}}

Valve {TAG}. Trace the leader line to its bowtie. Ignore all other bowties and their labels.

FLS means the {TAG} bowtie has a SHORT PIPE STUB with an OPEN BLUNT END. Look for:
  • An L-hook: a short branch off the main pipe that turns 90° and ends openly in empty space.
  • A horizontal spool / short tee branch with the tip cut clean — no fitting, no arrow, no funnel.
  • The stub end points into EMPTY SPACE — nothing at the tip whatsoever.
  The stub may be SMALL OR SUBTLE — even a short extension of 5–10 mm counts if the end is open.

  FLS → an open-ended stub like the above is on the {TAG} bowtie's own pipe
  none → no open-ended stub on {TAG}; or only drain indicators (arrows, funnels, boxes) visible,
         which may belong to a DIFFERENT neighboring bowtie — those do NOT count for {TAG}.
"""

VESSEL_DRN_RETRY_PROMPT = """\
You MUST respond with ONLY a JSON object.
Format: {{"attachment": "DRN"}} or {{"attachment": "none"}}

Valve {TAG} on a line leaving a vessel/tank bottom: horizontal run through the
bowtie then an elbow turning downward with a flow arrow = DRN.
Otherwise none.
"""

TJUNC_DRN_PROMPT = """\
You MUST respond with ONLY a JSON object.
Format: {{"attachment": "DRN"}} or {{"attachment": "none"}}

Valve {TAG} is an actuated valve (AV). Look at its pipe path in Images 1–2.

DRN — {TAG}'s pipe connects to a SHARED VERTICAL DRAIN MANIFOLD: a vertical pipe that
      routes flow down to a drain/trough/sump. Recognise this topology:
        • {TAG}'s pipe runs horizontally to a T-junction.
        • A VERTICAL manifold pipe descends from that T-junction.
        • Other valves (191, 192, etc.) sit ON the vertical manifold below the T-junction.
        • Drain indicators (large solid arrows, funnel, U-channel) sit at the BOTTOM of the manifold.
      {TAG} IS DRN even when the drain indicators appear below other valves — the shared manifold
      means {TAG}'s pipe ultimately reaches the drain.

none — {TAG}'s pipe goes only to a process vessel, pump, or header, with no drain manifold visible.
"""

SMP_CONFIRM_PROMPT = """\
You MUST respond with ONLY a JSON object.
Format: {{"attachment": "SMP"}} or {{"attachment": "DRN"}} or {{"attachment": "FLS"}} or {{"attachment": "none"}}

Valve {TAG}. Follow leader line to bowtie. Check branch end and floor area below:
  DRN — funnel/collector/trapezoid on THIS pipe discharges into a floor U-channel,
        sump recess, or drain trough (Image 3). Parallel branches each with a bowtie
        ALL feeding the same tou → each is DRN.
  SMP — sample funnel/cup/arrowhead at branch tip that does NOT connect to floor drain.
  FLS — no funnel; horizontal spool / tee flush on a vertical leg, or L-hook on bowtie.
  none — plain inline isolation valve; no pointed sample symbol; "003-15" or similar
         size text under tag is pipe DN only, not sampling.
"""


def _bedrock_attachment_ask(
    prompt: str,
    marked: Path,
    *,
    model_id: str,
    region: str,
    extra_images: Optional[List[bytes]] = None,
) -> str:
    content: List[Dict[str, Any]] = [
        {"text": prompt},
        {"image": {"format": "png", "source": {"bytes": marked.read_bytes()}}},
    ]
    for img in extra_images or []:
        content.append({"image": {"format": "png", "source": {"bytes": img}}})
    client = _bedrock_client(region)
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": content}],
        inferenceConfig={"maxTokens": 80, "temperature": 0},
    )
    parts = [b["text"] for b in response.get("output", {}).get("message", {}).get("content", []) if "text" in b]
    return parse_attachment_response("\n".join(parts).strip())


def refine_attachment(
    attachment: str,
    *,
    tag: str,
    marked: Path,
    crop_path: Path,
    model_id: str,
    region: str,
    cx_frac: float,
    cy_frac: float,
    crop_half: float,
    extra_below: float,
    body: str,
) -> str:
    """Targeted retries when the first attachment pass is empty or ambiguous."""
    att = str(attachment or "").upper().strip()
    body_tokens = set(strip_attachment_tokens(body).split())

    if not att and body_tokens & {"NC", "HV", "NO", "AV", "AV-M", "CHK"}:
        att = _bedrock_attachment_ask(
            FLS_FLUSH_RETRY_PROMPT.replace("{TAG}", tag),
            marked,
            model_id=model_id,
            region=region,
            extra_images=[
                branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac),
                below_valve_png(crop_path, half=crop_half, extra_below=extra_below),
            ],
        )
        if att != "FLS" and _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag)):
            # For plain-numeric tags, run an FLS-only ask before DRAIN_RETRY.  This prevents
            # a neighbouring bowtie's drain indicators from overriding a subtle FLS stub:
            # FLS_STUB_ONLY focuses solely on an open pipe-end on the {TAG} bowtie, so
            # neighbour drain shapes cannot cause a false DRN.
            fls_only = _bedrock_attachment_ask(
                FLS_STUB_ONLY_PROMPT.replace("{TAG}", tag),
                marked,
                model_id=model_id,
                region=region,
                extra_images=[
                    branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac),
                    below_valve_png(crop_path, half=crop_half, extra_below=extra_below),
                ],
            )
            if fls_only == "FLS":
                att = "FLS"
        if att != "FLS":
            # Non-plain-numeric tags are actuated valves (XV, HV, LV) whose drain indicator
            # may sit further below the body; use 2× extra_below so the funnel/U-channel is
            # visible.  Plain-numeric manual valves use the standard below height.
            _drain_extra_below = (
                extra_below * 2
                if not _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag))
                else extra_below
            )
            att = _bedrock_attachment_ask(
                DRAIN_RETRY_PROMPT.replace("{TAG}", tag),
                marked,
                model_id=model_id,
                region=region,
                extra_images=[
                    branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac),
                    below_valve_png(crop_path, half=crop_half, extra_below=_drain_extra_below),
                ],
            ) or att
            if not att:
                att = _bedrock_attachment_ask(
                    VESSEL_DRN_RETRY_PROMPT.replace("{TAG}", tag),
                    marked,
                    model_id=model_id,
                    region=region,
                    extra_images=[branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac)],
                )
            # Second-chance DRAIN_RETRY for plain-numeric tags: temperature=0 can still
            # produce stochastic misses; a second call at the same prompt recovers them
            # without changing the risk profile (DRN_DIRECT_RETRY still gates below).
            if not att and _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag)):
                att = _bedrock_attachment_ask(
                    DRAIN_RETRY_PROMPT.replace("{TAG}", tag),
                    marked,
                    model_id=model_id,
                    region=region,
                    extra_images=[
                        branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac),
                        below_valve_png(crop_path, half=crop_half, extra_below=extra_below),
                    ],
                )

    if att == "DRN":
        if _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag)):
            # Post-DRN FLS check: a subtle FLS stub may have been missed earlier while
            # a neighbour's drain triggered DRAIN_RETRY.  body_zoom_png gives a tighter
            # view of the bowtie area than branch_context or below_valve, which helps
            # surface small L-hooks.  This only fires when att is already "DRN" so it
            # cannot affect valves (like 35-27-739) whose att never reaches "DRN".
            # Two zoom levels (4× and 6.7×) at different magnifications: subtle FLS
            # L-hooks may only become visible at a specific zoom level.  Accept 1-of-2
            # FLS votes — the lower bar is safe because DRN_DIRECT_RETRY still gates
            # below, and plain-numeric DRN valves without stubs reliably return "none".
            _fls_stub_votes = 0
            _stub_cy_low = min(0.82, cy_frac + 0.07)
            # Five zoom variants — NO branch_context so a close neighbour's drain trough
            # (e.g. 35-24-093 sits within 20 drawing-units of 35-24-1105) cannot appear
            # in the extra image and pollute the FLS decision.
            # Checks 1–2: biased below cy_frac (downward stubs).
            # Checks 3–4: centred at cy_frac (horizontal L-hook stubs).
            # Check 5: tight 5× zoom at cy_frac (most isolated view of the bowtie body).
            for _stub_frac, _stub_cy in (
                (0.25, _stub_cy_low),
                (0.15, _stub_cy_low),
                (0.30, cy_frac),
                (0.46, cy_frac),
                (0.20, cy_frac),
            ):
                _v = _bedrock_attachment_ask(
                    FLS_STUB_ONLY_PROMPT.replace("{TAG}", tag),
                    marked,
                    model_id=model_id,
                    region=region,
                    extra_images=[
                        zoom_center_png(crop_path, frac=_stub_frac, cx_frac=cx_frac, cy_frac=_stub_cy),
                    ],
                )
                if _v == "FLS":
                    _fls_stub_votes += 1
            if not _fls_stub_votes:
                # Sixth check: call Bedrock with ONLY the tight body zoom and NO marked
                # image.  All previous checks pass `marked` (full crop) as Image 1, which
                # still shows the neighbouring valve's drain trough even when extra_images
                # is clean.  Removing the marked image eliminates the last contamination
                # path so the model can judge only the bowtie body at 5× magnification.
                _zoom_only = zoom_center_png(crop_path, frac=0.15, cx_frac=cx_frac, cy_frac=cy_frac)
                _c6 = _bedrock_client(region)
                _r6 = _c6.converse(
                    modelId=model_id,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"text": FLS_STUB_ONLY_PROMPT.replace("{TAG}", tag)},
                            {"image": {"format": "png", "source": {"bytes": _zoom_only}}},
                        ],
                    }],
                    inferenceConfig={"maxTokens": 80, "temperature": 0},
                )
                _parts6 = [b["text"] for b in _r6.get("output", {}).get("message", {}).get("content", []) if "text" in b]
                _v6 = parse_attachment_response("\n".join(_parts6).strip())
                if _v6 == "FLS":
                    _fls_stub_votes += 1
            if _fls_stub_votes >= 1:
                att = "FLS"
        if att == "DRN":
            direct = _bedrock_attachment_ask(
                DRN_DIRECT_RETRY_PROMPT.replace("{TAG}", tag),
                marked,
                model_id=model_id,
                region=region,
                extra_images=[
                    branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac),
                    below_valve_png(crop_path, half=crop_half, extra_below=extra_below),
                ],
            )
            if not direct:
                att = ""

    if att == "SMP":
        confirm = _bedrock_attachment_ask(
            SMP_CONFIRM_PROMPT.replace("{TAG}", tag),
            marked,
            model_id=model_id,
            region=region,
            extra_images=[
                branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac),
                below_valve_png(crop_path, half=crop_half, extra_below=extra_below),
            ],
        )
        if confirm in ("FLS", "SMP", "DRN"):
            att = confirm
        else:
            att = ""

    return att


def bedrock_classify_attachment(
    crop_path: Path,
    legend_path: Path,
    *,
    tag: str,
    model_id: str,
    region: str,
    cx_frac: float = 0.5,
    cy_frac: float = 0.5,
    crop_half: float = 42.0,
    extra_below: float = 60.0,
    marked_path: Optional[Path] = None,
) -> str:
    """Vision pass: exactly one of DRN / FLS / SMP / none."""
    global _legend_bytes
    marked = marked_path or crop_path
    content: List[Dict[str, Any]] = [
        {"text": ATTACHMENT_PROMPT.replace("{TAG}", tag or crop_path.stem)},
        {"image": {"format": "png", "source": {"bytes": marked.read_bytes()}}},
        {
            "image": {
                "format": "png",
                "source": {"bytes": zoom_center_png(marked, cx_frac=cx_frac, cy_frac=cy_frac)},
            }
        },
        {
            "image": {
                "format": "png",
                "source": {"bytes": branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac)},
            }
        },
    ]
    if legend_path.exists():
        if _legend_bytes is None:
            with _bedrock_lock:
                if _legend_bytes is None:
                    _legend_bytes = legend_path.read_bytes()
        suffix = legend_path.suffix.lower().lstrip(".")
        fmt = suffix if suffix in {"png", "jpg", "jpeg", "gif", "webp"} else "png"
        content.append({"image": {"format": fmt, "source": {"bytes": _legend_bytes}}})
    content.append(
        {
            "image": {
                "format": "png",
                "source": {"bytes": below_valve_png(crop_path, half=crop_half, extra_below=extra_below)},
            }
        }
    )

    client = _bedrock_client(region)
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": content}],
        inferenceConfig={"maxTokens": 200, "temperature": 0},
    )
    parts = [b["text"] for b in response.get("output", {}).get("message", {}).get("content", []) if "text" in b]
    return parse_attachment_response("\n".join(parts).strip())


def _bedrock_client(region: str):
    import boto3
    from botocore.config import Config

    # Key on (region, profile) so that credential changes are not silently ignored.
    key = (region, os.environ.get("AWS_PROFILE", ""))
    with _bedrock_lock:
        client = _bedrock_clients.get(key)
        if client is None:
            client = boto3.client(
                "bedrock-runtime",
                region_name=region,
                config=Config(
                    connect_timeout=15,
                    read_timeout=120,
                    retries={"max_attempts": 2, "mode": "standard"},
                ),
            )
            _bedrock_clients[key] = client
        return client


def _normalize_body_type(body: str) -> str:
    """Resolve mutually exclusive body tokens after vision parse."""
    tokens = [t for t in str(body or "").upper().split() if t in ALLOWED_VALVE_TOKENS]
    if "CHK" in tokens:
        tokens = [t for t in tokens if t not in {"NC", "HV", "NO", "GLV", "3WV"}]
    elif "GLV" in tokens:
        tokens = [t for t in tokens if t not in {"HV", "NC", "NO"}]
    elif "3WV" in tokens:
        tokens = [t for t in tokens if t not in {"HV", "NC", "NO"}]
    elif "NC" in tokens:
        tokens = [t for t in tokens if t not in {"HV", "NO"}]
    elif "HV" in tokens:
        tokens = [t for t in tokens if t != "NO"]
    return apply_sop_valve_type(" ".join(tokens))


_JSON_RETRY_PROMPT = """\
Respond with ONLY a JSON object — no other text.
Format: {{"type": "NC", "attachment": "FLS"}}
Classify valve {TAG} from the images. type = NC|HV|GLV|CHK|3WV|SV|AV|AV-M|PRV|PLUG|AAV|GF|YSTR. attachment = DRN|FLS|SMP|none.
"""

_HV_CONFIRM_PROMPT = """\
Respond with ONLY a JSON object: {{"type": "HV", "attachment": "none"}} or {{"type": "AV", "attachment": "none"}}
Valve {TAG}. Is there a CIRCLE on the stem directly attached to the bowtie centre?
Plain text (AT, HP) or distant instruments do NOT count. No circle on stem → HV.
"""

_GLV_AV_CONFIRM_PROMPT = """\
Respond with ONLY a JSON object: {{"type": "GLV", "attachment": "none"}} or {{"type": "AV", "attachment": "none"}}
Valve {TAG}. The symbol has a circle — determine whether it is a globe seat or an actuator.

GLV (globe valve): the SMALL CIRCLE sits INSIDE the bowtie, at the exact point where the two
     outline triangle tips meet. It is part of the valve body — no stem separates it from the
     bowtie body. Both triangles must be OUTLINE (empty interior).

AV  (actuated valve): the circle is on a STEM that extends AWAY from the bowtie body. A visible
     rod or line connects the bowtie centre to a circle or box that is physically outside the body.

Decisive test: can you see a stem/rod between the bowtie and the circle?
  Yes → AV.  No (circle is at the junction itself) → GLV.
"""

_GLV_SOLID_CONFIRM_PROMPT = """\
Respond with ONLY a JSON object: {{"type": "GLV", "attachment": "none"}} or {{"type": "NC", "attachment": "none"}}
Valve {TAG}: examine the two bowtie triangles closely.

GLV → BOTH triangles are OUTLINE (dark/hollow interior, no fill at all).
NC  → BOTH triangles are SOLID-FILLED (white, light, or coloured). In SML/Shotton drawings
      white ink on a dark P&ID background = solid fill = NC.

If the triangles are solid, or if an L-hook / pipe stub is visible near the bowtie → NC.
If both triangles are genuinely hollow/outline with no fill → GLV.
"""


def _bedrock_short_ask(
    prompt: str,
    marked: Path,
    *,
    model_id: str,
    region: str,
    max_tokens: int = 80,
    extra_images: Optional[List[bytes]] = None,
) -> str:
    client = _bedrock_client(region)
    content: List[Dict[str, Any]] = [
        {"text": prompt},
        {"image": {"format": "png", "source": {"bytes": marked.read_bytes()}}},
    ]
    for img in extra_images or []:
        content.append({"image": {"format": "png", "source": {"bytes": img}}})
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": content}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0},
    )
    parts = [
        b["text"]
        for b in response.get("output", {}).get("message", {}).get("content", [])
        if "text" in b
    ]
    return "\n".join(parts).strip()


_PLAIN_NUMERIC_TAG_RE = re.compile(r"^\d{2}-\d{2}-\d+$", re.I)


_FILL_CONFIRM_PROMPT = """\
Respond with ONLY a JSON object: {{"type": "NC", "attachment": "none"}} or {{"type": "HV", "attachment": "none"}}
Valve {TAG}: follow the leader/tag line from label "{TAG}" to the bowtie it connects to.
Classify ONLY that bowtie — ignore other nearby bowties.
SOLID fill (opaque interior — white, grey, red, or any colour that blocks the background) → NC.
OUTLINE only (hollow interior — the drawing background shows through the triangle) → HV.
Both triangles must be assessed: if BOTH solid → NC; if BOTH outline → HV.
"""


_BODY_FILL_CONFIRM = """\
Respond with ONLY a JSON object: {{"type": "NC", "attachment": "none"}} or {{"type": "HV", "attachment": "none"}} or {{"type": "CHK", "attachment": "none"}}
Valve {TAG} bowtie only: BOTH triangles solid fill (white/red/colored) → NC. BOTH outline → HV.
EXACTLY one filled + one outline → CHK.
SML/Shotton convention: white triangles on a dark P&ID background = solid fill = NC.
If BOTH triangles look identical (both same shade) → NC, not CHK.
"""

_CHK_CONFIRM_PROMPT = """\
Respond with ONLY a JSON object: {{"type": "CHK", "attachment": "none"}} or {{"type": "NC", "attachment": "none"}}
Valve {TAG}. Image 2: tight zoom centred on the {TAG} bowtie. Image 3: drawing legend.

Step 1 — In Image 1, find label "{TAG}" and TRACE ITS LEADER LINE to the VALVE BODY where it terminates.
          The valve body is a two-triangle bowtie symbol or, in Valmet drawings, a large inline arrowhead.
          The leader line terminates AT the valve body — that is the ONLY symbol to assess.

Step 2 — Find the CHK (check valve) entry in the legend (Image 3).

Step 3 — Compare ONLY the {TAG} valve body (where the leader line ends) to the CHK legend entry.
  CHK if the valve body itself (at the leader line end) has EXACTLY ONE solid half + ONE outline half,
       OR matches the CHK arrowhead shown in the legend.
  NC if both halves of the valve body are identically solid-filled.

Critical: large arrows or arrowheads that are NOT where the {TAG} leader line terminates are
FLOW DIRECTION MARKERS or DRAIN ARROWS — they are SEPARATE elements, not the CHK valve body.
Drain flow arrows (on the drain pipe below the valve) look like solid arrowheads but are NOT check
valves. Only the symbol at the precise end of the {TAG} leader line should be assessed.
"""


def _refine_drain_body_fill(
    result: str,
    *,
    tag: str,
    marked: Path,
    crop_path: Path,
    model_id: str,
    region: str,
    cx_frac: float,
    cy_frac: float,
) -> str:
    """Re-check bowtie fill on service-point valves (DRN/FLS/SMP) misread as CHK or HV.

    Uses two confirmation calls with a compact zoom; requires consensus to override.
    Only changes the body type — the service-point attachment is preserved.
    """
    tokens = str(result or "").upper().split()
    has_service_point = any(t in tokens for t in _EXCLUSIVE_ATTACHMENTS)
    if not has_service_point:
        return result
    body_tokens = [t for t in tokens if t in {"NC", "HV", "CHK", "NO"}]
    if not body_tokens or body_tokens[0] == "NC":
        return result
    attach = [t for t in tokens if t in _EXCLUSIVE_ATTACHMENTS]
    # Two confirmation votes; require consensus to override the initial reading.
    votes: List[str] = []
    for _ in range(2):
        raw = _bedrock_short_ask(
            _BODY_FILL_CONFIRM.replace("{TAG}", tag),
            marked,
            model_id=model_id,
            region=region,
            extra_images=[body_zoom_png(crop_path, cx_frac=cx_frac, cy_frac=cy_frac)],
        )
        fixed = _parse_one_pass(raw)
        if fixed:
            body = strip_attachment_tokens(fixed).split()[0]
            if body in {"NC", "HV", "CHK"}:
                votes.append(body)
    if len(votes) == 2 and votes[0] == votes[1]:
        return merge_body_and_attachment(votes[0], attach[0] if attach else "")
    return result


def _normalize_service_point_body(result: str) -> str:
    """Service-point valves (DRN/FLS/SMP) are always hand-closed (NC), never CHK or HV.

    Vision sometimes misreads the bowtie fill when the service-point geometry crowds
    the symbol.  This rule is semantically airtight: you open a drain/flush/sample
    valve to use it, so the running state must be NC.  Actuated valves (AV/AV-M) are
    excluded because those can appear with DRN as a drain-to-sump attachment.
    """
    tokens = str(result or "").upper().split()
    service = [t for t in tokens if t in _EXCLUSIVE_ATTACHMENTS]
    if not service:
        return result
    if "AV" in tokens or "AV-M" in tokens or "NC" in tokens:
        return result
    if "CHK" in tokens or "HV" in tokens or "NO" in tokens or "GLV" in tokens:
        return merge_body_and_attachment("NC", service[0])
    return result


def _confirm_hv_not_false_av(
    result: str,
    *,
    tag: str,
    marked: Path,
    model_id: str,
    region: str,
) -> str:
    """Plain numeric tags (35-24-230) are usually HV unless a circle sits on the stem."""
    tokens = str(result or "").upper().split()
    if "AV" not in tokens or "AV-M" in tokens:
        return result
    if not _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag)):
        return result
    raw = _bedrock_short_ask(
        _HV_CONFIRM_PROMPT.replace("{TAG}", tag),
        marked,
        model_id=model_id,
        region=region,
    )
    fixed = _parse_one_pass(raw)
    return fixed if fixed else result


def _confirm_av_not_glv(
    result: str,
    *,
    tag: str,
    marked: Path,
    crop_path: Path,
    model_id: str,
    region: str,
    cx_frac: float = 0.5,
    cy_frac: float = 0.5,
) -> str:
    """Re-confirm AV/GLV on non-plain-numeric tags — circle on stem or inside bowtie?

    GOR globe valves (GLV) have a circle sitting inside the bowtie at the triangle junction.
    Actuated valves (AV) have a circle on a stem extending away from the bowtie body.
    Fires for BOTH AV and GLV results so that a stochastic GLV from the main pass on an
    actuated-valve tag can be corrected back to AV.
    Plain numeric tags are already handled by _confirm_hv_not_false_av.
    """
    tokens = str(result or "").upper().split()
    has_av = "AV" in tokens and "AV-M" not in tokens
    has_glv = "GLV" in tokens
    if not (has_av or has_glv):
        return result
    if _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag)):
        return result  # handled by _confirm_hv_not_false_av
    raw = _bedrock_short_ask(
        _GLV_AV_CONFIRM_PROMPT.replace("{TAG}", tag),
        marked,
        model_id=model_id,
        region=region,
    )
    fixed = _parse_one_pass(raw)
    if not fixed:
        # Retry once — verbose first responses sometimes prevent JSON extraction.
        raw = _bedrock_short_ask(
            _GLV_AV_CONFIRM_PROMPT.replace("{TAG}", tag),
            marked,
            model_id=model_id,
            region=region,
        )
        fixed = _parse_one_pass(raw)
    if not fixed:
        # Both attempts failed: pass through _normalize_service_point_body so semantically
        # impossible tokens (e.g. "DRN GLV") are corrected before they escape.
        return _normalize_service_point_body(result)
    fixed_body = strip_attachment_tokens(fixed)
    orig_attach = [t for t in tokens if t in _EXCLUSIVE_ATTACHMENTS]
    # Only carry the original attachment forward when the confirmed body is AV — actuated
    # valves can drain to a sump (AV DRN).  GLV is a process regulating valve and cannot
    # carry a service-point attachment; carrying DRN onto GLV would produce an invalid token.
    if orig_attach and fixed_body == "AV":
        return merge_body_and_attachment("AV", orig_attach[0])
    return fixed_body


def _confirm_nc_vs_hv(
    result: str,
    *,
    tag: str,
    marked: Path,
    crop_path: Path,
    model_id: str,
    region: str,
    cx_frac: float,
    cy_frac: float,
    pipe_dn_near: bool = False,
) -> str:
    """Re-check fill when plain numeric tag gets NC vs HV wrong."""
    tokens = str(result or "").upper().split()
    if not _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag)):
        return result
    if not tokens or tokens[0] != "NC":
        return result
    if any(t in tokens for t in ("AV", "AV-M", "DRN", "FLS", "SMP")):
        return result
    if pipe_dn_near:
        return result
    tight_cx = max(0.35, min(0.55, cx_frac - 0.05))
    hv_votes = 0
    for cx_off, frac in ((cx_frac, 0.20), (tight_cx, 0.12), (cx_frac, 0.30)):
        for _ in range(2):
            raw = _bedrock_short_ask(
                _FILL_CONFIRM_PROMPT.replace("{TAG}", tag),
                marked,
                model_id=model_id,
                region=region,
                max_tokens=120,
                extra_images=[zoom_center_png(crop_path, frac=frac, cx_frac=cx_off, cy_frac=cy_frac)],
            )
            fixed = _parse_one_pass(raw)
            if fixed and strip_attachment_tokens(fixed).split()[0] == "HV":
                hv_votes += 1
        if hv_votes >= 2:
            break
    if hv_votes < 2:
        return result
    attach = [t for t in tokens if t in _EXCLUSIVE_ATTACHMENTS]
    return merge_body_and_attachment("HV", attach[0] if attach else "")


def _confirm_chk_body_fill(
    result: str,
    *,
    tag: str,
    marked: Path,
    crop_path: Path,
    model_id: str,
    region: str,
    cx_frac: float,
    cy_frac: float,
) -> str:
    """Re-check CHK on plain numeric tags — adjacent half-filled bowties bleed into outline valves."""
    tokens = str(result or "").upper().split()
    if "CHK" not in tokens:
        return result
    if any(t in tokens for t in ("AV", "AV-M", "SMP")):
        return result
    if not _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag)):
        return result
    # Left-bias tight zoom isolates the ring-centre bowtie when a CHK neighbour sits to the right.
    # FLS is NOT excluded: vision re-confirms the body when CHK+FLS appears (check valves cannot
    # have flushing stubs — the bowtie is very likely solid NC misread as CHK).
    tight_cx = max(0.35, min(0.55, cx_frac - 0.05))
    tight = zoom_center_png(crop_path, frac=0.12, cx_frac=tight_cx, cy_frac=cy_frac)
    votes: List[str] = []
    for _ in range(2):
        raw = _bedrock_short_ask(
            _FILL_CONFIRM_PROMPT.replace("{TAG}", tag),
            marked,
            model_id=model_id,
            region=region,
            max_tokens=120,
            extra_images=[tight],
        )
        fixed = _parse_one_pass(raw)
        if fixed:
            body = strip_attachment_tokens(fixed).split()[0]
            if body in {"NC", "HV"}:
                votes.append(body)
    attach = [t for t in tokens if t in _EXCLUSIVE_ATTACHMENTS]
    if len(votes) == 2 and votes[0] == votes[1] == "HV":
        return merge_body_and_attachment("HV", attach[0] if attach else "")
    if len(votes) == 2 and votes[0] == votes[1] == "NC":
        return merge_body_and_attachment("NC", attach[0] if attach else "")
    return result


def _confirm_nc_vs_chk(
    result: str,
    *,
    tag: str,
    marked: Path,
    crop_path: Path,
    model_id: str,
    region: str,
    cx_frac: float,
    cy_frac: float,
) -> str:
    """Last-chance CHK upgrade for plain-numeric NC valves with no service point.

    The main V2 pass biases toward NC when fill difference is ambiguous; this tight-zoom
    re-check surfaces cases where the body-zoom clearly shows one-half-solid / one-half-outline.
    Requires 2/2 unanimous CHK votes to convert — high bar prevents false CHK on plain NC.
    """
    tokens = str(result or "").upper().split()
    if not tokens or tokens[0] != "NC":
        return result
    if any(t in tokens for t in _EXCLUSIVE_ATTACHMENTS):
        return result
    if not _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag)):
        return result
    tight = zoom_center_png(crop_path, frac=0.30, cx_frac=cx_frac, cy_frac=cy_frac)
    extras: List[bytes] = [tight]
    if _legend_bytes is not None:
        extras.append(_legend_bytes)
    chk_votes = 0
    for _ in range(2):
        raw = _bedrock_short_ask(
            _CHK_CONFIRM_PROMPT.replace("{TAG}", tag),
            marked,
            model_id=model_id,
            region=region,
            max_tokens=120,
            extra_images=extras,
        )
        fixed = _parse_one_pass(raw)
        if fixed and strip_attachment_tokens(fixed).split()[0] == "CHK":
            chk_votes += 1
    if chk_votes >= 2:
        return "CHK"
    return result


def _parse_one_pass(raw: str) -> str:
    """Parse {"type": "NC", "attachment": "DRN"} → "NC DRN" (V2 legend tokens)."""
    return parse_v2_response(raw)


def bedrock_classify_crop(
    crop_path: Path,
    legend_path: Path,
    *,
    model_id: str,
    region: str,
    tag: str = "",
    cx_frac: float = 0.5,
    cy_frac: float = 0.5,
    crop_half: float = 42.0,
    extra_below: float = 60.0,
    pipe_dn_near: bool = False,
) -> str:
    """Single Bedrock call: body + attachment classified together from 5 images."""
    global _legend_bytes

    marked = annotate_valve_crop(crop_path, tag, cx_frac=cx_frac, cy_frac=cy_frac)
    prompt = load_v2_prompt(tag or crop_path.stem)

    if legend_path.exists() and _legend_bytes is None:
        with _bedrock_lock:
            if _legend_bytes is None:
                _legend_bytes = legend_path.read_bytes()

    content: List[Dict[str, Any]] = [
        {"text": prompt},
        # Image 1: full marked crop with yellow ring + tag label (for locating the target)
        {"image": {"format": "png", "source": {"bytes": marked.read_bytes()}}},
        # Image 2: tight bowtie zoom from clean crop (no ring overlay — clearer for NC vs HV fill)
        {"image": {"format": "png", "source": {"bytes": body_zoom_png(crop_path, cx_frac=cx_frac, cy_frac=cy_frac)}}},
        # Image 3: below-valve strip (drain detection)
        {"image": {"format": "png", "source": {"bytes": below_valve_png(crop_path, half=crop_half, extra_below=extra_below)}}},
        # Image 4: branch context (sample funnel / flush branch detection)
        {"image": {"format": "png", "source": {"bytes": branch_context_png(crop_path, cx_frac=cx_frac, cy_frac=cy_frac)}}},
    ]
    if _legend_bytes is not None:
        suffix = legend_path.suffix.lower().lstrip(".")
        fmt = suffix if suffix in {"png", "jpg", "jpeg", "gif", "webp"} else "png"
        content.append({"image": {"format": fmt, "source": {"bytes": _legend_bytes}}})

    client = _bedrock_client(region)
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": content}],
        inferenceConfig={"maxTokens": 256, "temperature": 0},
    )
    parts = [b["text"] for b in response.get("output", {}).get("message", {}).get("content", []) if "text" in b]
    raw = "\n".join(parts).strip()
    result = _parse_one_pass(raw)
    if not result:
        retry_raw = _bedrock_short_ask(
            _JSON_RETRY_PROMPT.replace("{TAG}", tag or crop_path.stem),
            marked,
            model_id=model_id,
            region=region,
            max_tokens=100,
        )
        result = _parse_one_pass(retry_raw)
    if result:
        result_tokens = set(result.split())
        body_only = strip_attachment_tokens(result)

        # GLV on a plain-numeric tag: re-confirm the triangles are actually outline.
        # Solid triangles + a circle = NC + service-point attachment, not GLV.
        if "GLV" in result_tokens and _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag or "")):
            raw2 = _bedrock_short_ask(
                _GLV_SOLID_CONFIRM_PROMPT.replace("{TAG}", tag or crop_path.stem),
                marked,
                model_id=model_id,
                region=region,
                extra_images=[body_zoom_png(crop_path, cx_frac=cx_frac, cy_frac=cy_frac)],
            )
            confirmed = _parse_one_pass(raw2)
            if confirmed and strip_attachment_tokens(confirmed).split()[0] == "NC":
                # Solid triangles: reclassify body as NC and determine attachment.
                att2 = _bedrock_attachment_ask(
                    FLS_FLUSH_RETRY_PROMPT.replace("{TAG}", tag or crop_path.stem),
                    marked,
                    model_id=model_id,
                    region=region,
                    extra_images=[
                        branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac),
                        below_valve_png(crop_path, half=crop_half, extra_below=extra_below),
                    ],
                )
                result = merge_body_and_attachment("NC", att2)
                result_tokens = set(result.split())
                body_only = strip_attachment_tokens(result)

        if "SMP" in result_tokens:
            att = refine_attachment(
                "SMP",
                tag=tag or crop_path.stem,
                marked=marked,
                crop_path=crop_path,
                model_id=model_id,
                region=region,
                cx_frac=cx_frac,
                cy_frac=cy_frac,
                crop_half=crop_half,
                extra_below=extra_below,
                body=body_only,
            )
            result = merge_body_and_attachment(body_only, att)
        elif "FLS" in result_tokens and "DRN" not in result_tokens:
            att = _bedrock_attachment_ask(
                FLS_FLUSH_RETRY_PROMPT.replace("{TAG}", tag or crop_path.stem),
                marked,
                model_id=model_id,
                region=region,
                extra_images=[
                    branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac),
                    below_valve_png(crop_path, half=crop_half, extra_below=extra_below),
                ],
            )
            if att == "DRN":
                result = merge_body_and_attachment(body_only, "DRN")
            elif att not in ("FLS", "none", ""):
                # Only override FLS if a different non-empty attachment (e.g. SMP) is returned.
                result = merge_body_and_attachment(body_only, att)
            elif _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag or "")):
                # FLS confirmed (or ambiguous none): challenge with DRAIN prompt as second opinion.
                # Genuine FLS (open pipe end) won't have the large solid drain arrow DRN requires.
                drn_att = _bedrock_attachment_ask(
                    DRAIN_RETRY_PROMPT.replace("{TAG}", tag or crop_path.stem),
                    marked,
                    model_id=model_id,
                    region=region,
                    extra_images=[
                        branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac),
                        below_valve_png(crop_path, half=crop_half, extra_below=extra_below),
                    ],
                )
                if drn_att == "DRN":
                    result = merge_body_and_attachment(body_only, "DRN")
        elif "DRN" in result_tokens and "FLS" not in result_tokens and _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag or "")):
            # DRN on a plain-numeric tag: require 2 FLS votes to convert; one ambiguous vote keeps DRN.
            # FLS (open pipe end) and DRN (enclosed shape) are often confused in Shotton crops.
            _fls_votes: List[str] = []
            for _ in range(2):
                _fls_votes.append(
                    _bedrock_attachment_ask(
                        FLS_FLUSH_RETRY_PROMPT.replace("{TAG}", tag or crop_path.stem),
                        marked,
                        model_id=model_id,
                        region=region,
                        extra_images=[
                            branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac),
                            below_valve_png(crop_path, half=crop_half, extra_below=extra_below),
                        ],
                    )
                )
            if _fls_votes.count("FLS") >= 2:
                # Unanimous FLS: convert DRN → FLS.
                result = merge_body_and_attachment(body_only, "FLS")
        elif "DRN" not in result_tokens and "FLS" not in result_tokens:
            att = refine_attachment(
                "",
                tag=tag or crop_path.stem,
                marked=marked,
                crop_path=crop_path,
                model_id=model_id,
                region=region,
                cx_frac=cx_frac,
                cy_frac=cy_frac,
                crop_half=crop_half,
                extra_below=extra_below,
                body=body_only,
            )
            if att:
                result = merge_body_and_attachment(body_only, att)
    return _normalize_service_point_body(
        _confirm_nc_vs_chk(
            _confirm_chk_body_fill(
                _confirm_nc_vs_hv(
                    _refine_drain_body_fill(
                        _confirm_av_not_glv(
                            _confirm_hv_not_false_av(
                                result,
                                tag=tag or crop_path.stem,
                                marked=marked,
                                model_id=model_id,
                                region=region,
                            ),
                            tag=tag or crop_path.stem,
                            marked=marked,
                            crop_path=crop_path,
                            model_id=model_id,
                            region=region,
                            cx_frac=cx_frac,
                            cy_frac=cy_frac,
                        ),
                        tag=tag or crop_path.stem,
                        marked=marked,
                        crop_path=crop_path,
                        model_id=model_id,
                        region=region,
                        cx_frac=cx_frac,
                        cy_frac=cy_frac,
                    ),
                    tag=tag or crop_path.stem,
                    marked=marked,
                    crop_path=crop_path,
                    model_id=model_id,
                    region=region,
                    cx_frac=cx_frac,
                    cy_frac=cy_frac,
                    pipe_dn_near=pipe_dn_near,
                ),
                tag=tag or crop_path.stem,
                marked=marked,
                crop_path=crop_path,
                model_id=model_id,
                region=region,
                cx_frac=cx_frac,
                cy_frac=cy_frac,
            ),
            tag=tag or crop_path.stem,
            marked=marked,
            crop_path=crop_path,
            model_id=model_id,
            region=region,
            cx_frac=cx_frac,
            cy_frac=cy_frac,
        )
    )


def hierarchy_valve_rows(hierarchy_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """One record per EQUIPMENT/SUB-EQUIPMENT that might be a valve.

    Relies on FUNCTION header rows appearing before their children in the CSV,
    which is the invariant maintained by write_hierarchy_csv / the orchestrator.
    """
    out: List[Dict[str, str]] = []
    current_fn = ""
    seen = set()
    for row in hierarchy_rows:
        fn = str(row.get("FUNCTION") or "").strip().upper().replace(" ", "")
        eq = str(row.get("EQUIPMENT") or "").strip().upper().replace(" ", "")
        sub = str(row.get("SUB-EQUIPMENT") or "").strip().upper().replace(" ", "")
        desc = str(row.get("DESCRIPTION") or "")
        if fn and not eq and not sub:
            current_fn = fn
            continue
        tag = eq or sub
        if not tag or tag in seen:
            continue
        if is_pump_equipment(tag, desc):
            continue
        seen.add(tag)
        out.append({"tag": tag, "fn": current_fn, "description": desc})
    return out


def load_valve_cache(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    # Allow {"tags": {...}} wrapper or a flat tag map.
    blob = data.get("tags") if isinstance(data.get("tags"), dict) else data
    out: Dict[str, Dict[str, Any]] = {}
    for k, v in blob.items():
        if k in {"input", "model_id", "region", "legend", "tags"}:
            continue
        if isinstance(v, dict) and ("type" in v or "is_valve" in v or "layer" in v):
            out[_norm_tag(k)] = v
    return out


def _crop_meta_path(crop_path: Path) -> Path:
    return crop_path.with_suffix(".meta.json")


def crop_matches_window(crop_path: Path, half: float, extra_below: float) -> bool:
    meta = _crop_meta_path(crop_path)
    if not crop_path.exists() or crop_path.stat().st_size <= 0 or not meta.exists():
        return False
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return abs(float(data.get("half") or 0) - half) < 0.5 and abs(
        float(data.get("extra_below") or 0) - extra_below
    ) < 0.5


def write_crop_meta(crop_path: Path, half: float, extra_below: float) -> None:
    _crop_meta_path(crop_path).write_text(
        json.dumps({"half": half, "extra_below": extra_below}, indent=2),
        encoding="utf-8",
    )


def main() -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="Per-tag tight-crop valve classification")
    parser.add_argument("--input", default="inputs/Broke System.dwg")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--hierarchy-csv", default="")
    parser.add_argument("--legend", default=str(LEGEND_PATH))
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--region", default=os.environ.get("AWS_REGION") or "eu-west-2")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--crop-half", type=float, default=42.0)
    parser.add_argument(
        "--extra-below",
        type=float,
        default=60.0,
        help="Extra CAD units below the valve so the drain trough is in the crop (SOP zoom-out)",
    )
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--locate-only", action="store_true", help="Write CAD locations, skip Bedrock")
    parser.add_argument("--limit", type=int, default=0, help="Max tags to classify (0 = all candidates)")
    return run_valve_classify_from_args(parser.parse_args())


def run_valve_classify(
    *,
    input_path: Path,
    out_dir: Path,
    hierarchy_csv: Path,
    model_id: str,
    region: str,
    jobs: int = 1,
    skip_existing: bool = False,
    aws_profile: str = "",
) -> int:
    if aws_profile:
        os.environ["AWS_PROFILE"] = aws_profile
    os.environ["PYTHONUNBUFFERED"] = "1"
    args = argparse.Namespace(
        input=str(input_path),
        output_dir=str(out_dir),
        hierarchy_csv=str(hierarchy_csv),
        legend=str(LEGEND_PATH),
        model_id=model_id,
        region=region,
        jobs=jobs,
        crop_half=42.0,
        extra_below=60.0,
        skip_existing=skip_existing,
        locate_only=False,
        limit=0,
    )
    return run_valve_classify_from_args(args)


def run_valve_classify_from_args(args: argparse.Namespace) -> int:

    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve()
    base = safe_name(input_path)
    legend_path = Path(args.legend).expanduser().resolve()
    cache_path = json_path(out_dir, f"{base}.valve_types.json")

    hier_path = Path(args.hierarchy_csv).expanduser().resolve() if args.hierarchy_csv else out_dir / f"{base}.hierarchy_orchestrator.csv"
    struct_path = find_json(out_dir, f"{base}.structural_dump.json")
    inv_path = find_json(out_dir, f"{base}.pid_inventory.json")
    if not hier_path.exists():
        logger.error(f"[error] Missing hierarchy CSV: {hier_path}")
        return 2
    if not struct_path.exists():
        logger.error(f"[error] Missing structural dump: {struct_path}")
        return 2

    with hier_path.open(encoding="utf-8", newline="") as f:
        hierarchy_rows = [{k: str(v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]
    structural = json.loads(struct_path.read_text(encoding="utf-8"))
    inventory = json.loads(inv_path.read_text(encoding="utf-8")) if inv_path.exists() else {}

    text_locations = collect_text_locations(structural)
    # GOR drawings store valve tags in block attributes, not TEXT entities — merge them in.
    text_locations.update(collect_gor_attribute_tag_locations(structural))
    valve_inserts = collect_valve_inserts(structural)
    symb_inserts = collect_symb_bowtie_inserts(structural)
    drain_markers = collect_drain_markers(structural)
    functions = collect_functions(inventory)
    cache = load_valve_cache(cache_path) if args.skip_existing else {}

    candidates = hierarchy_valve_rows(hierarchy_rows)
    located: List[Dict[str, Any]] = []
    wfl_tags = {
        _norm_tag(str(fn.get("function") or ""))
        for fn in (inventory.get("functions") or [])
        if isinstance(fn, dict) and _WFL_LINE_RE.search(
            " ".join(
                str(fn.get(k) or "")
                for k in ("description", "nearby_descriptions", "line_number", "kind")
            )
        )
    }
    for rec in candidates:
        tag = rec["tag"]
        loc = locate_valve(
            tag,
            text_locations=text_locations,
            valve_inserts=valve_inserts,
            symb_inserts=symb_inserts,
            wfl_drain_hint=_norm_tag(tag) in wfl_tags,
        )
        if loc is None:
            continue
        desc = rec.get("description") or ""
        is_valve = bool(loc["is_valve"] or is_valve_equipment(rec["tag"], desc))
        if not is_valve:
            continue
        loc["fn_hierarchy"] = rec["fn"]
        loc["description"] = desc
        loc["is_valve"] = True
        located.append(loc)

    if args.limit > 0:
        located = located[: args.limit]

    _log(f"[valve-classify] {len(located)} CAD-located valves (of {len(candidates)} hierarchy tags)")
    crop_dir = evidence_dir(out_dir) / "_valve_crops"
    crop_dir.mkdir(parents=True, exist_ok=True)

    to_vision: List[Dict[str, Any]] = []
    for loc in located:
        tag = loc["tag"]
        prev = cache.get(tag) or {}
        if args.skip_existing and prev.get("type"):
            continue
        to_vision.append(loc)

    extra_below = float(args.extra_below or 0.0)
    cx_frac, cy_frac = valve_ring_frac(args.crop_half, extra_below)

    def _crop_path(tag: str) -> Path:
        # Sanitize the tag so characters like '/' don't traverse into subdirectories.
        safe = re.sub(r"[^\w.\-]", "_", tag)
        return crop_dir / f"{safe}.png"

    if not args.locate_only and to_vision:
        need_render: List[Dict[str, Any]] = []
        for loc in to_vision:
            crop_path = _crop_path(loc["tag"])
            if crop_matches_window(crop_path, args.crop_half, extra_below):
                loc["crop"] = str(crop_path)
            else:
                need_render.append(loc)

        if need_render:
            from dwg_reader.dwg_pid_hierarchy_ai import load_drawing

            _log(
                f"[valve-classify] opening DWG for {len(need_render)} zoom-out crops "
                f"(half={args.crop_half:.0f}, extra_below={extra_below:.0f})..."
            )
            doc = load_drawing(input_path)
            _log("[valve-classify] DWG open; indexing entity extents...")
            entity_index = build_entity_extent_index(doc)
            for i, loc in enumerate(need_render, 1):
                crop_path = _crop_path(loc["tag"])
                _log(f"  [crop] {i}/{len(need_render)} {loc['tag']}")
                rendered = tight_valve_screenshot(
                    doc,
                    loc["x"],
                    loc["y"],
                    crop_path,
                    half=args.crop_half,
                    extra_below=extra_below,
                    entity_index=entity_index,
                )
                loc["crop"] = str(rendered) if rendered else ""
                if rendered is not None:
                    write_crop_meta(crop_path, args.crop_half, extra_below)
                else:
                    _log(f"  [warn] no crop for {loc['tag']}")
        else:
            _log(f"[valve-classify] reusing {len(to_vision)} zoom-out crop PNGs (skip DWG)")

        jobs = max(1, int(args.jobs or 1))

        def _one(loc: Dict[str, Any]) -> Tuple[str, str]:
            crop = Path(loc.get("crop") or "")
            if not crop.exists():
                return loc["tag"], ""
            _log(f"  [vision] start {loc['tag']}")
            try:
                vtype = bedrock_classify_crop(
                    crop,
                    legend_path,
                    model_id=args.model_id,
                    region=args.region,
                    tag=loc["tag"],
                    cx_frac=cx_frac,
                    cy_frac=cy_frac,
                    crop_half=float(args.crop_half),
                    extra_below=extra_below,
                    pipe_dn_near=pipe_dn_label_near_tag(loc["tag"], text_locations, structural),
                )
                return loc["tag"], vtype
            except Exception as exc:
                _log(f"  [warn] Bedrock failed for {loc['tag']}: {exc}")
                return loc["tag"], ""

        types: Dict[str, str] = {}
        # _record is only ever called from the main thread (sequential or as_completed loop),
        # so no lock is needed on the counter.
        done_n = 0

        def _record(tag: str, vtype: str) -> None:
            nonlocal done_n
            types[tag] = vtype
            done_n += 1
            _log(f"  [vision] {done_n}/{len(to_vision)} {tag} → {vtype or 'UNKNOWN'}")

        if jobs == 1:
            for loc in to_vision:
                tag, vtype = _one(loc)
                _record(tag, vtype)
        else:
            _log(f"[valve-classify] {jobs} parallel Bedrock workers for {len(to_vision)} tags")
            with ThreadPoolExecutor(max_workers=jobs) as pool:
                futs = {pool.submit(_one, loc): loc["tag"] for loc in to_vision}
                for fut in as_completed(futs):
                    tag, vtype = fut.result()
                    _record(tag, vtype)
        for loc in to_vision:
            loc["type"] = types.get(loc["tag"] or "") or loc.get("type") or ""
    else:
        for loc in to_vision:
            loc.setdefault("type", "")

    # Merge into cache with parent inference.
    for loc in located:
        tag = loc["tag"]
        vtype = combine_valve_type(
            str(loc.get("type") or (cache.get(tag) or {}).get("type") or ""),
            str(loc.get("description") or ""),
        )
        parent = pick_parent_fn(
            x=float(loc["x"]),
            y=float(loc["y"]),
            hierarchy_fn=str(loc.get("fn_hierarchy") or ""),
            functions=functions,
            valve_type=vtype,
            valve_tag=tag,
            lin_edges=inventory.get("lin_from_to") or [],
        )
        cache[tag] = {
            "type": vtype,
            "fn": parent,
            "fn_hierarchy": loc.get("fn_hierarchy") or "",
            "layer": loc.get("layer") or "",
            "block": loc.get("block") or "",
            "x": loc["x"],
            "y": loc["y"],
            "is_valve": True,
            "source": "vision" if vtype else "cad_layer",
        }

    payload = {
        "input": str(input_path),
        "legend": str(legend_path) if legend_path.exists() else None,
        "model_id": args.model_id,
        "region": args.region,
        "count": len(cache),
        "tags": cache,
    }
    write_json(cache_path, payload)
    _log(f"[valve-classify] wrote {cache_path} ({len(cache)} tags)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
