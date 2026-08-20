#!/usr/bin/env python3
"""
Per-tag valve classification: tight CAD crop + legend → cached type + parent fn.

Fixes the four remaining valve gaps:
  1. Tight crop around the valve insert (not the whole FUNCTION screenshot)
  2. Full legend vocabulary including AV-M
  3. Numeric tags on P-VALVEPOS / P-CVPOS are valves even without VLV in the text
  4. Drain valves under a conveyor/pump are reassigned to the nearest pulper/tank

Cache: outputs/jsons/<stem>.valve_types.json
Export reads this cache; inputs/valve_type_overrides.json still wins.
"""

from __future__ import annotations

import dwg_warn  # noqa: F401 — silence boto3 Python 3.9 deprecation noise

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

from dwg_floc_context import (
    ALLOWED_VALVE_TOKENS,
    apply_sop_valve_type,
    combine_valve_type,
    is_valve_equipment,
)
from dwg_pure_dump import evidence_dir, find_json, json_path, safe_name, write_json

LEGEND_PATH = Path("inputs/legend.png")
DEFAULT_MODEL_ID = "eu.anthropic.claude-sonnet-4-6"
VALVE_LAYERS = frozenset({"P-VALVEPOS", "P-CVPOS", "P-SYMB"})

# Shared bowtie fill rules — white (Shotton P&ID) and red/colored (GOR legend sheets).
_BOWTIE_FILL_RULES = """\
    Inspect EACH triangle separately (left vs right, or top vs bottom):

    CHK : EXACTLY ONE triangle filled solid (white, red, or other color) AND the other
          triangle outline-only (background/black visible inside). Half-and-half bowtie
          = CHK, never NC or HV. If BOTH triangles look the same (both filled or both
          outline) it is NOT CHK. Also CHK if a diagonal bar crosses the bowtie centre.

    NC  : BOTH triangles filled solid (white, red, magenta, or other solid color) —
          normally closed hand valve. Only when NEITHER triangle is outline-only.
          Never NC if one triangle is transparent/outline and the other is filled (CHK).

    HV  : BOTH triangles outline-only / transparent (background/black visible in BOTH).
          Thin line edges with dark interior = HV outline, NOT solid fill. Only when
          neither triangle is filled solid. Never HV if any triangle is filled solid
          (white or colored)."""

_CONVEYOR_RE = re.compile(r"\b(CVYR|CONVEYOR)\b", re.I)
_VESSEL_HINT_RE = re.compile(r"\b(PLPR|PULPER|TNK|TANK|CHEST|VESSEL|THICKENER)\b", re.I)

ONE_PASS_PROMPT = """\
CRITICAL: Output ONLY a single JSON object. No explanation, no steps, no markdown, no prose.
Exactly this format: {{"type": "TOKEN", "attachment": "none"}}

Allowed "type" tokens: NC, HV, AV, AV-M, CHK, PRV, SV, NO, UNKNOWN
Allowed "attachment" values: none, DRN, FLS, SMP

Classify the P&ID valve tagged {TAG}.

IMAGES:
  Image 1 = Full marked crop. Yellow ring marks the APPROXIMATE valve location.
  Image 2 = Tight clean zoom on the target bowtie body (no ring — clearer fill detail).
  Image 3 = Below-valve strip enlarged (check for floor drain / trough / drain arrows).
  Image 4 = Wider branch context (check for D marker, sample funnel, or flush stub).
  Image 5 = Legend (reference only).

STEP 1 — IDENTIFY THE TARGET BOWTIE (Image 1):
  Find the text label "{TAG}" and follow its LEADER LINE or TAG LINE to the bowtie
  it connects to. That bowtie is the ONLY one to classify — ignore all others nearby.
  If the leader line is unclear or absent: the bowtie CLOSEST to the yellow ring
  center is the target. If two bowties are visible, pick the one AT the ring center.
  When the tag sits above several bowties, trace the FULL leader/tag line to its
  endpoint — do not pick a nearby cross-line valve the leader does not touch.
  Brown/red floor drain branches with downward arrows into a U-channel or sump are
  drain (DRN) taps even when a cyan/magenta process line crosses nearby.
  Ignore any valve-type letter in the tag itself (HV/FV/LV); classify the SYMBOL only.
  Return UNKNOWN only if NO bowtie symbol is visible ANYWHERE in the crop — not
  because there are multiple bowties or the target is ambiguous.

STEP 2 — BODY / ACTUATOR TYPE (Image 2):
  Image 2 is a tight zoom centered on the TARGET BOWTIE from STEP 1. Classify only
  the bowtie at the CENTER of Image 2 — any other bowtie visible near the edges is
  a neighboring valve; ignore it entirely.
  Check for a circle actuator on the bowtie stem FIRST:
    AV-M : stem above bowtie leading to a circle with the letter M CLEARLY readable.
           Only AV-M if you can explicitly read "M" inside the circle.
    AV   : a CIRCLE symbol must sit ON the stem line directly connected to the bowtie
           centre (above or below the triangles). HS/LS/FC/XS/HI/FCV numbers inside
           that circle = AV. When uncertain between AV and AV-M, use AV.
           NOT AV if: no circle on the bowtie stem; only plain text nearby (AT, HP,
           SS, bar, DN); instrument boxes elsewhere in the crop; pump/motor/tank symbols.
           Outline-only bowtie with NO circle on its stem → HV, never AV.

  Record the body type (AV / AV-M / NC / HV / CHK / …) then continue to STEP 3 for attachment.
  Actuated valves on drain lines are AV + DRN, not AV alone.

  No circle actuator → hand valve — classify by BODY FILL (Image 2):
{_BOWTIE_FILL_RULES}

    PRV : extra line segments parallel to each triangle base
    SV  : stem on top ending in a horizontal T-cap
    NO  : running-open mark on an outline hand valve (very rare; never when
          any triangle is filled solid)

  NC, HV, and CHK are mutually exclusive — pick exactly one body type.

STEP 3 — ATTACHMENT (Images 1, 2, 3, 4) — all body types including AV / AV-M:
  Pick EXACTLY ONE attachment or "none". Check in this strict order and STOP at the
  first match — do NOT continue to the next rule once a match is found:

    FLS (flush spool) — size "003-50" printed under tag "{TAG}" marks a FLUSHING spool
          per legend → attachment FLS. NOT drainage — no large tou/sump arrow. L-hook or
          blunt stub on the bowtie or a short vertical 003-50 spool = FLS.
          On a vertical branch with two bowties, the UPPER valve tagged 003-50 is FLS;
          the LOWER valve whose pipe hits the drain arrow is DRN — not the upper one.
          Size "003-15" under a tag is usually pipe DN only — NOT automatic FLS.

    DRN — PRIMARY: the pipe FROM this valve ends in a LARGE SOLID FLOW ARROW (filled
          white arrowhead — much larger than normal line direction ticks) pointing
          into a floor trough, tou, sump recess, U-channel, or open drain basin
          (Images 1, 3, 4). The arrow direction may be down, up, left, or right.
          Often a funnel/collector symbol (trapezoid tapering to a point) sits between
          the valve pipe and the large arrow. Large-arrow-to-tou ALWAYS means DRN.

          Also DRN when the capital letter "D" appears on a pipe DIRECTLY connected to
          THIS bowtie's inlet OR outlet (Images 2 and 4). In these P&IDs, drain taps are
          labelled with a capital "D" text placed directly on the pipe — it appears in a
          distinct color (typically orange or red-orange) against the dark background.
          Look on BOTH sides of the bowtie (left = inlet, right = outlet). The D can
          appear close to the bowtie body OR at the far end of the outlet pipe at a
          vessel drain port — both mean DRN for this valve.
          Also look in Image 1: search for a single capital letter "D" (not a number,
          not inside a shape) in a distinct orange or red color on a PIPE that connects
          to this bowtie — it may be at the far left or far right edge of Image 1.
          NOTE: numbered revision bubbles (orange/red filled triangles or circles
          containing numbers like "10", "A1", etc.) are NOT drain markers; ignore them.
          Also DRN if drain arrows drop from THIS bowtie's outlet pipe into a floor
          trough or sump in Image 3 — the arrows must be clearly attached to this
          valve's own pipe, not the general floor area drain of the surroundings.
          Vertical drain branch (size 001-80 under tag) with arrow into U-channel
          below THIS bowtie = DRN.
          On a stacked vertical branch with two bowties IN SERIES on the SAME pipe:
          only the LOWER bowtie whose outlet hits the drain arrow is DRN; the upper is none.
          PARALLEL separate branch lines each with their own bowtie, ALL draining into a
          common funnel/tou collector → EACH bowtie on its own branch is DRN.
          ⚑ Large solid arrow into tou/trough, capital "D" on pipe, OR drain arrow → DRN.

    SMP — a branch pipe ends in a POINTED or FUNNEL-SHAPED sampling symbol at the
          branch TIP (Image 4): a solid filled arrowhead (▲ or ►), pointed funnel,
          or cup/cone shape. The symbol must be POINTED — NOT blunt, NOT T-shaped,
          NOT a plain cut pipe end. A short branch with a pointed far end = SMP
          even if the branch is close to the bowtie body.
          NEVER SMP if the funnel/collector DISCHARGES into a floor U-channel, sump,
          or drain trough (Image 3) — that is DRN. Sample take-offs do NOT connect
          to floor drains.
          NEVER SMP because "003-15" or other pipe-size text appears under the tag —
          that is pipe DN (nominal diameter), NOT a sampling connection. SMP requires
          a VISIBLE pointed funnel/cup/arrowhead at a branch tip that is NOT a floor
          drain connection.
          NOTE: branch end at a floor drain channel (U-channel below) = DRN or FLS,
          never SMP.
          ⚑ Pointed sample funnel NOT into floor drain → SMP. STOP.

    FLS — a small dead-end stub DIRECTLY on THIS bowtie body side (Image 2) with a
          BLUNT, T-SHAPED, or CUT-PIPE end (not pointed/funnel-shaped). Also FLS: a
          flushing spool (often 003-50 = 50mm) whose far branch end is a CUT PIPE
          with NO pointed symbol at its tip. Also FLS: any stub to a floor drain
          U-channel (Image 3).
          CRITICAL: if another BOWTIE SYMBOL (two solid or outline triangles) appears
          on a pipe adjacent to this valve, that element is a SEPARATE VALVE — it is
          NOT an FLS stub for this valve.
          ⚑ Dead-end stub with blunt/cut end (no pointed tip) → FLS. STOP.

    none — plain inline valve: no D marker, no pointed branch end, no dead-end stub.

  Decision order: FLS (003-50 under tag) → DRN → SMP → FLS (stub) → none

STEP 4 — RETURN JSON ONLY (no other text):
  {{"type": "<body>", "attachment": "<SMP|FLS|DRN|none>"}}
  Examples: {{"type": "NC", "attachment": "DRN"}}
            {{"type": "AV", "attachment": "DRN"}}
            {{"type": "HV", "attachment": "none"}}
""".replace("{_BOWTIE_FILL_RULES}", _BOWTIE_FILL_RULES)

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
) -> str:
    """
    Keep hierarchy ownership unless this is a drain on a conveyor/pump.

    Drain valves on this drawing hang off pulpers/tanks; Euclidean nearest
    often picks the neighbouring conveyor (L006 vs L005 for 35-24-137).
    """
    hier = _norm_tag(hierarchy_fn)
    vtype = str(valve_type or "").upper()
    if "DRN" not in vtype.split():
        return hier

    hier_row = next((f for f in functions if f["tag"] == hier), None)
    if hier_row and is_vessel_function(hier_row):
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
    for tok in ("AV-M", "CHK", "PRV", "FLS", "SMP", "DRN", "AUTO", "AV", "NC", "NO", "SV", "HV"):
        if re.search(rf"(?:^|\s){re.escape(tok)}(?:\s|$)", text):
            mapped = "AV" if tok == "AUTO" else tok
            if mapped in ALLOWED_VALVE_TOKENS and mapped not in found:
                found.append(mapped)
    if "UNKNOWN" in text.split() and not found:
        return ""
    return apply_sop_valve_type(strip_attachment_tokens(" ".join(found)))


def _log(msg: str) -> None:
    print(msg, flush=True)


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

Valve {TAG}. Check attachment for THIS bowtie only:
  FLS — size "003-50" under tag, OR L-hook / horizontal stub welded to bowtie side,
        OR short vertical spool with blunt/cut pipe end. Flush connection — NOT floor drain.
  DRN — large solid arrow into tou/sump/U-channel from THIS valve's pipe.
  none — plain inline valve (e.g. 003-15 is pipe size only, no flush stub, no drain).
Pick FLS when 003-50 appears under the tag unless a large tou arrow is on THIS pipe.
"""

DRAIN_RETRY_PROMPT = """\
You MUST respond with ONLY a JSON object.
Format: {{"attachment": "DRN"}} or {{"attachment": "none"}}

Valve {TAG}. Follow the leader line from label "{TAG}" to its bowtie.

DRN — pipe from THIS bowtie ends in a LARGE SOLID FLOW ARROW (filled white arrowhead,
      much bigger than normal line ticks) pointing into a floor trough, tou, sump recess,
      or U-channel — arrow direction may be down/up/left/right. Often a funnel/collector
      (trapezoid) sits between the pipe and the arrow. Parallel branches each with their
      own bowtie ALL draining to the same tou → each is DRN.

none — plain in-line valve; or upper bowtie IN SERIES on one vertical pipe whose lower
       neighbour reaches the drain (not this bowtie's own pipe to the tou).
"""

DRN_DIRECT_RETRY_PROMPT = """\
You MUST respond with ONLY a JSON object.
Format: {{"attachment": "DRN"}} or {{"attachment": "none"}}

Valve {TAG}. Does THIS bowtie's own pipe feed a large solid drain arrow into a
tou/trough/sump (directly or via a funnel collector)?

DRN — yes: this bowtie's branch reaches the tou (parallel branches each get DRN).

none — only if this is the UPPER bowtie IN SERIES on one vertical pipe and a
      second bowtie below it sits between this valve and the tou.
"""

VESSEL_DRN_RETRY_PROMPT = """\
You MUST respond with ONLY a JSON object.
Format: {{"attachment": "DRN"}} or {{"attachment": "none"}}

Valve {TAG} on a line leaving a vessel/tank bottom: horizontal run through the
bowtie then an elbow turning downward with a flow arrow = DRN.
Otherwise none.
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
        if att != "FLS":
            att = _bedrock_attachment_ask(
                DRAIN_RETRY_PROMPT.replace("{TAG}", tag),
                marked,
                model_id=model_id,
                region=region,
                extra_images=[
                    branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac),
                    below_valve_png(crop_path, half=crop_half, extra_below=extra_below),
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

    if att == "DRN":
        direct = _bedrock_attachment_ask(
            DRN_DIRECT_RETRY_PROMPT.replace("{TAG}", tag),
            marked,
            model_id=model_id,
            region=region,
            extra_images=[branch_context_png(marked, cx_frac=cx_frac, cy_frac=cy_frac)],
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
        tokens = [t for t in tokens if t not in {"NC", "HV", "NO"}]
    elif "NC" in tokens:
        tokens = [t for t in tokens if t not in {"HV", "NO"}]
    elif "HV" in tokens:
        tokens = [t for t in tokens if t != "NO"]
    return apply_sop_valve_type(" ".join(tokens))


_JSON_RETRY_PROMPT = """\
Respond with ONLY a JSON object — no other text.
Format: {{"type": "NC", "attachment": "FLS"}}
Classify valve {TAG} from the images. type = NC|HV|AV|AV-M|CHK|PRV|SV|NO. attachment = DRN|FLS|SMP|none.
"""

_HV_CONFIRM_PROMPT = """\
Respond with ONLY a JSON object: {{"type": "HV", "attachment": "none"}} or {{"type": "AV", "attachment": "none"}}
Valve {TAG}. Is there a CIRCLE on the stem directly attached to the bowtie centre?
Plain text (AT, HP) or distant instruments do NOT count. No circle on stem → HV.
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
BOTH triangles solid fill (white, red, or colored) → NC. BOTH outline-only (dark interior) → HV.
"""


_BODY_FILL_CONFIRM = """\
Respond with ONLY a JSON object: {{"type": "NC", "attachment": "none"}} or {{"type": "HV", "attachment": "none"}} or {{"type": "CHK", "attachment": "none"}}
Valve {TAG} bowtie only: BOTH triangles solid fill (white/red/colored) → NC. BOTH outline → HV.
EXACTLY one filled (white/red/colored) + one outline → CHK.
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
    """Re-check bowtie fill on drain valves often misread as CHK or HV."""
    tokens = str(result or "").upper().split()
    if "DRN" not in tokens:
        return result
    body_tokens = [t for t in tokens if t in {"NC", "HV", "CHK", "NO"}]
    if not body_tokens or body_tokens[0] == "NC":
        return result
    raw = _bedrock_short_ask(
        _BODY_FILL_CONFIRM.replace("{TAG}", tag),
        marked,
        model_id=model_id,
        region=region,
        extra_images=[body_zoom_png(crop_path, cx_frac=cx_frac, cy_frac=cy_frac)],
    )
    fixed = _parse_one_pass(raw)
    if not fixed:
        return result
    new_body = strip_attachment_tokens(fixed).split()[0]
    attach = [t for t in tokens if t in _EXCLUSIVE_ATTACHMENTS]
    return merge_body_and_attachment(new_body, attach[0] if attach else "")


def _normalize_drain_hand_body(result: str) -> str:
    """Hand drain valves on this P&ID are normally closed (NC), not CHK/HV."""
    tokens = str(result or "").upper().split()
    if "DRN" not in tokens or "AV" in tokens or "AV-M" in tokens or "NC" in tokens:
        return result
    if "CHK" in tokens or "HV" in tokens:
        attach = [t for t in tokens if t in _EXCLUSIVE_ATTACHMENTS] or ["DRN"]
        return merge_body_and_attachment("NC", attach[0])
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
    for cx_off, frac in ((cx_frac, 0.20), (tight_cx, 0.12)):
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
    if any(t in tokens for t in ("AV", "AV-M", "FLS", "SMP")):
        return result
    if not _PLAIN_NUMERIC_TAG_RE.match(_norm_tag(tag)):
        return result
    # Left-bias tight zoom isolates the ring-centre bowtie when a CHK neighbour sits to the right.
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
    if len(votes) == 2 and votes[0] == votes[1] == "HV":
        attach = [t for t in tokens if t in _EXCLUSIVE_ATTACHMENTS]
        return merge_body_and_attachment("HV", attach[0] if attach else "")
    return result


def _parse_one_pass(raw: str) -> str:
    """Parse {"type": "NC", "attachment": "DRN"} → "NC DRN"."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    obj = None
    try:
        obj = json.loads(text)
    except Exception:
        m = re.search(r"\{[^{}]*\"type\"[^{}]*\"attachment\"[^{}]*\}", text, re.I | re.S)
        if m:
            try:
                obj = json.loads(m.group(0))
            except Exception:
                pass
    if isinstance(obj, dict):
        body = _normalize_body_type(strip_attachment_tokens(parse_type_tokens(str(obj.get("type") or ""))))
        att_raw = str(obj.get("attachment") or "none").upper().strip()
        attachment = att_raw if att_raw in _EXCLUSIVE_ATTACHMENTS else ""
        return merge_body_and_attachment(body, attachment)
    # Fallback: extract tokens from raw text
    body = _normalize_body_type(strip_attachment_tokens(parse_type_tokens(raw)))
    attachment = parse_attachment_response(raw)
    return merge_body_and_attachment(body, attachment) if body else ""


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
    prompt = ONE_PASS_PROMPT.replace("{TAG}", tag or crop_path.stem)

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
            elif att != "FLS":
                result = merge_body_and_attachment(body_only, att)
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
    return _normalize_drain_hand_body(
        _confirm_chk_body_fill(
            _confirm_nc_vs_hv(
                _refine_drain_body_fill(
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
                pipe_dn_near=pipe_dn_near,
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
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve()
    base = safe_name(input_path)
    legend_path = Path(args.legend).expanduser().resolve()
    cache_path = json_path(out_dir, f"{base}.valve_types.json")

    hier_path = Path(args.hierarchy_csv).expanduser().resolve() if args.hierarchy_csv else out_dir / f"{base}.hierarchy_orchestrator.csv"
    struct_path = find_json(out_dir, f"{base}.structural_dump.json")
    inv_path = find_json(out_dir, f"{base}.pid_inventory.json")
    if not hier_path.exists():
        print(f"[error] Missing hierarchy CSV: {hier_path}", file=sys.stderr)
        return 2
    if not struct_path.exists():
        print(f"[error] Missing structural dump: {struct_path}", file=sys.stderr)
        return 2

    with hier_path.open(encoding="utf-8", newline="") as f:
        hierarchy_rows = [{k: str(v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]
    structural = json.loads(struct_path.read_text(encoding="utf-8"))
    inventory = json.loads(inv_path.read_text(encoding="utf-8")) if inv_path.exists() else {}

    text_locations = collect_text_locations(structural)
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
            from dwg_pid_hierarchy_ai import load_drawing

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
                return loc["tag"], apply_wfl_drain_attachment(
                    vtype,
                    wfl_drain_hint=_norm_tag(loc["tag"]) in wfl_tags,
                )
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
