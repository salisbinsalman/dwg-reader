#!/usr/bin/env python3
"""
P&ID enrichment pass.

Adds remaining high-value extracts:
  - tag register (nearby text tags bound to equipment/instruments)
  - line-to-geometry binding
  - control-loop candidates
  - title-block / revision registers
  - CAD tables snapshot
  - specialty object inventory
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dwg_reader.dwg_pure_dump import clear_previous_outputs, find_json, json_path, json_safe, safe_name, write_json
from dwg_reader.dwg_semantic_extract import load_or_parse
from dwg_reader.logutil import configure_logging, get_logger

logger = get_logger(__name__)


EQUIP_TAG_RE = re.compile(r"^\d{2}-\d{2}[A-Z]\d{2,4}[A-Z]?$")
INSTR_AREA_RE = re.compile(r"^\d{2}-\d{2}$")
LINE_RE = re.compile(
    r"^(?P<plant_area>\d{2}-\d{2})-(?P<line_seq>\d{3}(?:/\d+)?)(?:-(?P<line_type>[A-Z]+))?(?:-(?P<size>\d*))?-(?P<pipe_class>[A-Z0-9]+)$"
)
LOOP_HINT_RE = re.compile(r"\b([A-Z]{1,4})\s*-?\s*(\d{2,4}[A-Z]?)\b")


def dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def xy(pt: Any) -> Optional[Tuple[float, float]]:
    if isinstance(pt, list) and len(pt) >= 2:
        return float(pt[0]), float(pt[1])
    return None


def entity_points(entity: Dict[str, Any]) -> List[Tuple[float, float]]:
    g = entity.get("geometry") or {}
    t = entity.get("type")
    pts: List[Tuple[float, float]] = []
    if t == "LINE":
        for k in ("start", "end"):
            p = xy(g.get(k))
            if p:
                pts.append(p)
    elif t == "LWPOLYLINE":
        for p in g.get("points_xyseb", []):
            if len(p) >= 2:
                pts.append((float(p[0]), float(p[1])))
    elif t == "POLYLINE":
        for p in g.get("vertices", []):
            q = xy(p)
            if q:
                pts.append(q)
    return pts


def nearest_texts(
    pos: Tuple[float, float],
    texts: List[Dict[str, Any]],
    *,
    max_dist: float,
    layers: Optional[set] = None,
    predicate=None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    scored = []
    for t in texts:
        if layers and t.get("layer") not in layers:
            continue
        p = xy(t.get("position"))
        if not p:
            continue
        text = (t.get("text") or "").strip()
        if not text:
            continue
        if predicate and not predicate(text):
            continue
        d = dist(pos, p)
        if d <= max_dist:
            scored.append(
                {
                    "text": text,
                    "layer": t.get("layer"),
                    "handle": t.get("handle"),
                    "distance": round(d, 3),
                    "position": t.get("position"),
                }
            )
    scored.sort(key=lambda r: r["distance"])
    return scored[:limit]


def build_tag_register(structural: Dict[str, Any], inventory: Dict[str, Any]) -> List[Dict[str, Any]]:
    texts = structural.get("text_entities", [])
    rows: List[Dict[str, Any]] = []

    primary_cats = [
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
    ]
    for cat in primary_cats:
        for item in inventory.get(cat, []):
            if item.get("source") != "insert":
                continue
            p = xy([item.get("x"), item.get("y"), item.get("z")])
            if not p:
                continue
            tag_hits = nearest_texts(
                p,
                texts,
                max_dist=90,
                layers={"P-TANK_POS", "P-EQUIPMENT_POS", "P-PUMP_POS", "P-MOTOR_POS", "P-AGITATOR_POS", "P-VALVEPOS", "P-CVPOS", "P-INSTRPOS_TEXTS", "P-TEXT", "P-INSTRPOS"},
                predicate=lambda s: bool(EQUIP_TAG_RE.match(s.replace(" ", "")) or INSTR_AREA_RE.match(s)),
            )
            desc_hits = nearest_texts(
                p,
                texts,
                max_dist=120,
                layers={"P-TEXT", "P-EQUIPMENT_POS", "P-TANK_POS"},
                predicate=lambda s: len(s) >= 4 and not EQUIP_TAG_RE.match(s.replace(" ", "")) and not LINE_RE.match(s.upper()),
            )
            resolved_tag = None
            for h in tag_hits:
                cand = h["text"].replace(" ", "")
                if EQUIP_TAG_RE.match(cand):
                    resolved_tag = cand
                    break
            if not resolved_tag and item.get("position_number"):
                resolved_tag = str(item.get("position_number"))

            rows.append(
                {
                    "category": cat,
                    "block_name": item.get("block_name"),
                    "handle": item.get("handle"),
                    "layer": item.get("layer"),
                    "x": item.get("x"),
                    "y": item.get("y"),
                    "resolved_tag": resolved_tag,
                    "nearby_tags": "; ".join(h["text"] for h in tag_hits),
                    "nearby_descriptions": "; ".join(h["text"] for h in desc_hits[:3]),
                    "confidence": "high" if resolved_tag and EQUIP_TAG_RE.match(str(resolved_tag)) else ("medium" if resolved_tag else "low"),
                }
            )
    return rows


def bind_lines_to_geometry(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    texts = [
        t
        for t in structural.get("text_entities", [])
        if t.get("layer") == "P-LINEPOS" and (t.get("text") or "").strip()
    ]
    pipe_layers = {
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
    }
    segments = []
    for e in structural.get("entities", []):
        if e.get("type") not in ("LINE", "LWPOLYLINE", "POLYLINE"):
            continue
        if e.get("layer") not in pipe_layers:
            continue
        pts = entity_points(e)
        if len(pts) < 2:
            continue
        # representative points: start/mid/end
        mid = pts[len(pts) // 2]
        segments.append(
            {
                "handle": e.get("handle"),
                "layer": e.get("layer"),
                "entity_type": e.get("type"),
                "points": pts,
                "anchor": mid,
                "start": pts[0],
                "end": pts[-1],
            }
        )

    rows = []
    for t in texts:
        text = (t.get("text") or "").strip().upper()
        p = xy(t.get("position"))
        if not p:
            continue
        m = LINE_RE.match(text)
        parsed = m.groupdict() if m else {}
        best = None
        best_d = 80.0
        for seg in segments:
            for q in (seg["anchor"], seg["start"], seg["end"]):
                d = dist(p, q)
                if d < best_d:
                    best_d = d
                    best = seg
        rows.append(
            {
                "line_number": text,
                "plant_area": parsed.get("plant_area"),
                "line_sequence": parsed.get("line_seq"),
                "line_type": parsed.get("line_type"),
                "nominal_size": parsed.get("size") or None,
                "pipe_class": parsed.get("pipe_class"),
                "label_handle": t.get("handle"),
                "label_position": t.get("position"),
                "bound_pipe_handle": best.get("handle") if best else None,
                "bound_pipe_layer": best.get("layer") if best else None,
                "bound_pipe_type": best.get("entity_type") if best else None,
                "bind_distance": round(best_d, 3) if best else None,
                "bind_confidence": "high" if best and best_d <= 25 else ("medium" if best and best_d <= 80 else "low"),
            }
        )
    # unique by line number keep closest bind
    best_by_line: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        key = r["line_number"]
        prev = best_by_line.get(key)
        if not prev:
            best_by_line[key] = r
        else:
            pd = prev.get("bind_distance")
            cd = r.get("bind_distance")
            if cd is not None and (pd is None or cd < pd):
                best_by_line[key] = r
    return list(best_by_line.values())


def extract_control_loops(
    structural: Dict[str, Any], inventory: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Heuristic loop candidates from nearby instrument/CV clusters + text."""
    instruments = [r for r in inventory.get("instruments", []) if r.get("source") == "insert"]
    control_valves = [r for r in inventory.get("control_valves", []) if r.get("source") == "insert"]
    texts = structural.get("text_entities", [])

    rows = []
    # Group instruments by nearest area code text
    for inst in instruments:
        p = xy([inst.get("x"), inst.get("y")])
        if not p:
            continue
        area_hits = nearest_texts(
            p,
            texts,
            max_dist=60,
            layers={"P-INSTRPOS_TEXTS", "P-TEXT", "P-INSTRPOS"},
            predicate=lambda s: bool(INSTR_AREA_RE.match(s)),
        )
        area = area_hits[0]["text"] if area_hits else None
        # nearest CV
        nearest_cv = None
        nearest_cv_d = 120.0
        for cv in control_valves:
            cp = xy([cv.get("x"), cv.get("y")])
            if not cp:
                continue
            d = dist(p, cp)
            if d < nearest_cv_d:
                nearest_cv_d = d
                nearest_cv = cv
        rows.append(
            {
                "loop_area": area,
                "instrument_handle": inst.get("handle"),
                "instrument_block": inst.get("block_name"),
                "instrument_layer": inst.get("layer"),
                "instrument_position": [inst.get("x"), inst.get("y"), inst.get("z")],
                "nearest_control_valve_handle": nearest_cv.get("handle") if nearest_cv else None,
                "nearest_control_valve_block": nearest_cv.get("block_name") if nearest_cv else None,
                "distance_to_cv": round(nearest_cv_d, 3) if nearest_cv else None,
                "signal_type_guess": "instrument_to_final_element" if nearest_cv else "measurement_only",
                "confidence": "medium" if nearest_cv and nearest_cv_d <= 80 else "low",
            }
        )

    # Aggregate by area into loop summaries
    by_area: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_area[r.get("loop_area") or "UNKNOWN"].append(r)

    summaries = []
    for area, items in by_area.items():
        cvs = {i.get("nearest_control_valve_handle") for i in items if i.get("nearest_control_valve_handle")}
        summaries.append(
            {
                "loop_area": area,
                "instrument_count": len(items),
                "linked_control_valve_count": len(cvs),
                "instrument_handles": "; ".join(i.get("instrument_handle") or "" for i in items[:30]),
                "control_valve_handles": "; ".join(sorted(h for h in cvs if h)),
                "confidence": "medium" if area != "UNKNOWN" else "low",
            }
        )
    return rows, summaries


def extract_revisions(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for ins in structural.get("inserts", []):
        if ins.get("layer") != "P-REVISIONS":
            continue
        attrs = {a.get("tag"): a.get("text") for a in ins.get("attributes", []) if a.get("tag")}
        filled = {k: v for k, v in attrs.items() if v}
        rows.append(
            {
                "block_name": ins.get("name"),
                "handle": ins.get("handle"),
                "layer": ins.get("layer"),
                "position": ins.get("insert"),
                "revision_mark": filled.get("MRK") or filled.get("MRK2"),
                "date": filled.get("PVM") or filled.get("PVM2"),
                "author": filled.get("MUU") or filled.get("MUU2") or filled.get("TAR"),
                "change": filled.get("MUUTOS") or filled.get("MUUTOS2"),
                "attributes_json": json.dumps(json_safe(filled), ensure_ascii=True),
            }
        )
    return rows


def flatten_title_block(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for rec in structural.get("title_block_fields") or []:
        fields = rec.get("fields") or {}
        row = {
            "block_name": rec.get("block_name"),
            "handle": rec.get("handle"),
            "layer": rec.get("layer"),
            "position": rec.get("insert"),
        }
        row.update(fields)
        rows.append(row)
    # also explode key/value long form
    return rows


def cad_tables_snapshot(structural: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    return {
        "linetypes": structural.get("linetypes") or [],
        "text_styles": structural.get("text_styles") or [],
        "dim_styles": structural.get("dim_styles") or [],
        "appids": structural.get("appids") or [],
        "ucs_table": structural.get("ucs_table") or [],
        "views_table": structural.get("views_table") or [],
        "vports_table": structural.get("vports_table") or [],
        "groups": structural.get("groups") or [],
        "xrefs": structural.get("xrefs") or [],
        "specialty_entities": structural.get("specialty_entities") or [],
        "layout_details": structural.get("layout_details") or [],
    }


def export_enrichment_workbook(payload: Dict[str, Any], out_path: Path) -> None:
    import pandas as pd

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        summary = []
        for sheet, rows in payload.items():
            if not isinstance(rows, list):
                continue
            summary.append({"sheet": sheet, "row_count": len(rows)})
            pd.DataFrame(rows if rows else [{"note": "empty"}]).to_excel(
                writer, sheet_name=sheet[:31], index=False
            )
        pd.DataFrame(summary).to_excel(writer, sheet_name="summary", index=False)


def main() -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="P&ID enrichment extractor")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument(
        "--no-clean-prev",
        action="store_true",
        help="Keep previous enrichment outputs instead of clearing them first.",
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
            suffixes=(".pid_enrichment.xlsx", ".pid_enrichment.json"),
        )

    structural, source = load_or_parse(input_path, out_dir, refresh=args.refresh)
    logger.info(f"[1/4] Loaded structural ({source})")

    inv_path = find_json(out_dir, f"{base}.pid_inventory.json")
    if inv_path.exists():
        inventory = json.loads(inv_path.read_text(encoding="utf-8"))
        logger.info("[2/4] Loaded inventory cache")
    else:
        from dwg_reader.dwg_pid_inventory import build_inventory

        inventory = build_inventory(structural, dwg_stem=input_path.stem)
        logger.info("[2/4] Built inventory live")

    tag_register = build_tag_register(structural, inventory)
    line_bindings = bind_lines_to_geometry(structural)
    loop_details, loop_summaries = extract_control_loops(structural, inventory)
    revisions = extract_revisions(structural)
    title_block = flatten_title_block(structural)
    tables = cad_tables_snapshot(structural)

    payload = {
        "tag_register": tag_register,
        "line_geometry_bindings": line_bindings,
        "control_loop_details": loop_details,
        "control_loop_summaries": loop_summaries,
        "revisions": revisions,
        "title_block": title_block,
        **tables,
    }

    logger.info("[3/4] Enrichment counts:")
    for k, v in payload.items():
        logger.info(f"  - {k}: {len(v)}")

    xlsx_out = out_dir / f"{base}.pid_enrichment.xlsx"
    json_out = json_path(out_dir, f"{base}.pid_enrichment.json")
    export_enrichment_workbook(payload, xlsx_out)
    write_json(json_out, payload)
    logger.info(f"[4/4] Wrote {xlsx_out}")
    logger.info(f"[4/4] Wrote {json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
