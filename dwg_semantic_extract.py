#!/usr/bin/env python3
"""
P&ID semantic extraction pass.

Categories:
  - equipment
  - lines
  - process
  - sub_process
  - function
  - sub_equipment
  - masks
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dwg_pure_dump import (
    clear_previous_outputs,
    configure_odafc,
    find_json,
    json_path,
    json_safe,
    parse_with_ezdxf,
    safe_name,
    write_json,
)


LINE_NUMBER_RE = re.compile(
    r"^(?P<plant_area>\d{2}-\d{2})-(?P<line_seq>\d{3})-(?P<line_type>[A-Z]+)-(?P<size>\d+)-(?P<pipe_class>[A-Z0-9]+)$"
)
AREA_CODE_RE = re.compile(r"^\d{2}-\d{2}$")
POSITION_TAG_RE = re.compile(r"^\d{2}-\d{2}[A-Z]\d{3}$")
EQUIP_TAG_RE = re.compile(r"^\d{2}-\d{2}[PTV]\d{3,4}$")


EQUIPMENT_LAYERS = {
    "P-EQUIPMENT_POS": "equipment",
    "P-EQUIPMENTS": "equipment",
    "P-TANK_POS": "tank",
    "P-PUMP_POS": "pump",
}

SUB_EQUIPMENT_LAYERS = {
    "P-MOTOR_POS": "motor",
    "P-AGITATOR_POS": "agitator",
}

FUNCTION_LAYER_HINTS = {
    "P-INSTRU": "instrument",
    "P-VALVEPOS": "valve",
    "P-CVPOS": "control_valve",
    "P-INSTRPOS": "instrument_position",
    "P-PTERMINAL_POS": "terminal",
}

PROCESS_LAYERS = {
    "P-WATER": "water_service",
    "P-SEALING_WATER": "sealing_water",
    "P-COOLING_WATER": "cooling_water",
    "P-FILTERED_WATER": "filtered_water",
    "P-WHITE_WATER": "white_water",
    "P-REJECT": "reject",
    "P-AIR": "air",
    "P-VENTS": "ventilation",
}


def fmt_point(pt: Any) -> Optional[str]:
    if not isinstance(pt, list) or len(pt) < 2:
        return None
    z = pt[2] if len(pt) > 2 else 0.0
    return f"{float(pt[0]):.6f},{float(pt[1]):.6f},{float(z):.6f}"


def parse_line_number(text: str) -> Dict[str, Any]:
    text = text.strip().upper()
    m = LINE_NUMBER_RE.match(text)
    if not m:
        return {"line_number": text, "parsed": False}
    return {"line_number": text, "parsed": True, **m.groupdict()}


def block_family(name: str) -> str:
    n = (name or "").upper()
    if n.startswith("PPI_"):
        return "PPI_instrument_equipment"
    if n.startswith("P7A"):
        return "P7A_function_symbol"
    if n.startswith("CVM"):
        return "CVM_control_valve"
    if n.startswith("PRM"):
        return "PRM_instrument"
    if n.startswith("CTV"):
        return "CTV_transmitter"
    if n.startswith("*"):
        return "anonymous_dynamic"
    return "other"


def group_attributes(attrs: List[Dict[str, Any]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for a in attrs or []:
        tag = a.get("tag")
        if tag:
            out[tag] = a.get("text") or a.get("value") or ""
    return out


def build_insert_index(structural: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    by_handle: Dict[str, Dict[str, Any]] = {}
    for ins in structural.get("inserts", []):
        handle = ins.get("handle")
        if not handle:
            continue
        attrs = group_attributes(ins.get("attributes", []))
        by_handle[handle] = {
            **ins,
            "attribute_map": attrs,
        }
    return by_handle


def extract_equipment(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for ins in structural.get("inserts", []):
        layer = ins.get("layer") or ""
        if layer not in EQUIPMENT_LAYERS and layer not in SUB_EQUIPMENT_LAYERS:
            continue
        if layer in SUB_EQUIPMENT_LAYERS:
            continue
        attrs = group_attributes(ins.get("attributes", []))
        rows.append(
            {
                "category": "equipment",
                "equipment_type": EQUIPMENT_LAYERS.get(layer, "equipment"),
                "tag": ins.get("name"),
                "block_name": ins.get("name"),
                "block_family": block_family(ins.get("name", "")),
                "handle": ins.get("handle"),
                "layer": layer,
                "x": ins.get("insert", [None, None, None])[0] if ins.get("insert") else None,
                "y": ins.get("insert", [None, None, None])[1] if ins.get("insert") else None,
                "z": ins.get("insert", [None, None, None])[2] if ins.get("insert") else None,
                "position": fmt_point(ins.get("insert")),
                "rotation": ins.get("rotation"),
                "xscale": ins.get("xscale"),
                "yscale": ins.get("yscale"),
                "zscale": ins.get("zscale"),
                "position_number": attrs.get("ANTPOS"),
                "description": attrs.get("TEKSTI1") or attrs.get("ANTNIMI"),
                "reference": attrs.get("TEKSTI2"),
                "linked_diagram": attrs.get("KAAVIO"),
                "attributes_json": json.dumps(json_safe(attrs), ensure_ascii=True),
            }
        )

    # Equipment labels from P-TEXT / P-EQUIPMENT_POS text
    for t in structural.get("text_entities", []):
        layer = t.get("layer") or ""
        if layer not in ("P-TEXT", "P-EQUIPMENT_POS", "P-EQUIPMENTS"):
            continue
        text = (t.get("text") or "").strip()
        if not text or len(text) < 3:
            continue
        if text in {"START", "STOP", "V", "E", "O", "R", "N", "D", "A1", "A2", "ST", "SS", "SV", "S1", "S2", "S3", "S4", "S5", "S6"}:
            continue
        rows.append(
            {
                "category": "equipment",
                "equipment_type": "text_label",
                "tag": text,
                "block_name": None,
                "block_family": "text_label",
                "handle": t.get("handle"),
                "layer": layer,
                "x": t.get("position", [None, None, None])[0] if t.get("position") else None,
                "y": t.get("position", [None, None, None])[1] if t.get("position") else None,
                "z": t.get("position", [None, None, None])[2] if t.get("position") else None,
                "position": fmt_point(t.get("position")),
                "rotation": t.get("rotation"),
                "xscale": None,
                "yscale": None,
                "zscale": None,
                "position_number": None,
                "description": text,
                "reference": None,
                "linked_diagram": None,
                "attributes_json": "{}",
            }
        )
    return rows


def extract_sub_equipment(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for ins in structural.get("inserts", []):
        layer = ins.get("layer") or ""
        if layer not in SUB_EQUIPMENT_LAYERS:
            continue
        attrs = group_attributes(ins.get("attributes", []))
        rows.append(
            {
                "category": "sub_equipment",
                "sub_equipment_type": SUB_EQUIPMENT_LAYERS.get(layer, "sub_equipment"),
                "parent_block": ins.get("name"),
                "tag": ins.get("name"),
                "handle": ins.get("handle"),
                "layer": layer,
                "position": fmt_point(ins.get("insert")),
                "rotation": ins.get("rotation"),
                "position_number": attrs.get("ANTPOS"),
                "description": attrs.get("TEKSTI1") or attrs.get("ANTNIMI"),
                "attributes_json": json.dumps(json_safe(attrs), ensure_ascii=True),
            }
        )

    rotor_pat = re.compile(r"(ROTOR|AGITATOR|GEAR BOX|MOTOR|PUMP)", re.I)
    for t in structural.get("text_entities", []):
        if t.get("layer") != "P-TEXT":
            continue
        text = (t.get("text") or "").strip()
        if not rotor_pat.search(text):
            continue
        rows.append(
            {
                "category": "sub_equipment",
                "sub_equipment_type": "text_label",
                "parent_block": None,
                "tag": text,
                "handle": t.get("handle"),
                "layer": t.get("layer"),
                "position": fmt_point(t.get("position")),
                "rotation": t.get("rotation"),
                "position_number": None,
                "description": text,
                "attributes_json": "{}",
            }
        )
    return rows


def extract_lines(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    seen = set()

    for t in structural.get("text_entities", []):
        layer = t.get("layer") or ""
        if layer not in ("P-LINEPOS", "P-INSTRPOS_TEXTS", "P-TEXT", "P-FITTINGS"):
            continue
        text = (t.get("text") or "").strip().upper()
        if not text:
            continue

        if layer == "P-LINEPOS" or LINE_NUMBER_RE.match(text):
            if text in seen:
                continue
            seen.add(text)
            parsed = parse_line_number(text)
            rows.append(
                {
                    "category": "lines",
                    "line_number": parsed.get("line_number"),
                    "plant_area": parsed.get("plant_area"),
                    "line_sequence": parsed.get("line_seq"),
                    "line_type": parsed.get("line_type"),
                    "nominal_size": parsed.get("size"),
                    "pipe_class": parsed.get("pipe_class"),
                    "parsed": parsed.get("parsed", False),
                    "handle": t.get("handle"),
                    "layer": layer,
                    "position": fmt_point(t.get("position")),
                    "source": "line_label_text",
                }
            )
        elif AREA_CODE_RE.match(text):
            key = (text, fmt_point(t.get("position")))
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "category": "lines",
                    "line_number": text,
                    "plant_area": text,
                    "line_sequence": None,
                    "line_type": "area_code",
                    "nominal_size": None,
                    "pipe_class": None,
                    "parsed": True,
                    "handle": t.get("handle"),
                    "layer": layer,
                    "position": fmt_point(t.get("position")),
                    "source": "plant_area_code",
                }
            )
        elif POSITION_TAG_RE.match(text.replace(" ", "")):
            norm = text.replace(" ", "")
            if norm in seen:
                continue
            seen.add(norm)
            rows.append(
                {
                    "category": "lines",
                    "line_number": norm,
                    "plant_area": norm[:5] if len(norm) >= 5 else None,
                    "line_sequence": None,
                    "line_type": "position_tag",
                    "nominal_size": None,
                    "pipe_class": None,
                    "parsed": True,
                    "handle": t.get("handle"),
                    "layer": layer,
                    "position": fmt_point(t.get("position")),
                    "source": "position_tag",
                }
            )

    # Line geometry from P-FITTINGS / P-LINEPOS
    for e in structural.get("entities", []):
        layer = e.get("layer") or ""
        if layer not in ("P-FITTINGS", "P-LINEPOS") or e.get("type") not in ("LINE", "LWPOLYLINE", "POLYLINE"):
            continue
        geom = e.get("geometry") or {}
        rows.append(
            {
                "category": "lines",
                "line_number": None,
                "plant_area": None,
                "line_sequence": None,
                "line_type": "geometry",
                "nominal_size": None,
                "pipe_class": None,
                "parsed": False,
                "handle": e.get("handle"),
                "layer": layer,
                "position": json.dumps(json_safe(geom), ensure_ascii=True),
                "source": f"geometry_{e.get('type')}",
            }
        )
    return rows


def extract_process(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    header = structural.get("header_variables") or {}
    doc = structural.get("doc") or {}

    rows.append(
        {
            "category": "process",
            "process_name": header.get("$PROJECTNAME") or "Broke System",
            "process_code": header.get("$PROJECTNUMBER"),
            "drawing_id": None,
            "description": "Drawing / project level process context",
            "from": None,
            "to": None,
            "linked_diagram": None,
            "layer": None,
            "position": None,
            "source": "header",
        }
    )

    # Title block / sheet attributes via inserts with TITLE/PROJECT/KAAVIO
    for ins in structural.get("inserts", []):
        attrs = group_attributes(ins.get("attributes", []))
        if not any(k in attrs for k in ("TITLE1", "PROJECT1", "KAAVIO", "TEKSTI1", "DRAWINGID")):
            continue
        if not any(attrs.get(k) for k in ("TITLE1", "PROJECT1", "KAAVIO", "TEKSTI1", "DRAWINGID")):
            continue
        rows.append(
            {
                "category": "process",
                "process_name": attrs.get("TITLE1") or attrs.get("PROJECT3") or attrs.get("PROJECT1"),
                "process_code": attrs.get("DRAWINGID") or attrs.get("TUNNUS"),
                "drawing_id": attrs.get("DRAWINGID"),
                "description": attrs.get("TEKSTI1") or attrs.get("PROJECT2"),
                "from": attrs.get("TEKSTI1"),
                "to": attrs.get("TEKSTI2"),
                "linked_diagram": attrs.get("KAAVIO"),
                "layer": ins.get("layer"),
                "position": fmt_point(ins.get("insert")),
                "source": f"block:{ins.get('name')}",
            }
        )

    major_labels = {
        "PRODUCTION", "VENTILATION", "BROKE SCREENING", "COARSE SCREENING", "SEALING WATER",
        "COOLING WATER", "WHITE WATER", "BROKE THICKENER", "FLOW MEDIA", "PIPELINES",
        "BROKE HANDLING", "EMERGENCY STOP",
    }
    for t in structural.get("text_entities", []):
        text = (t.get("text") or "").strip()
        up = text.upper().replace("%%U", "")
        if up in major_labels or any(k in up for k in ("WATER", "PULPER", "SCREEN", "BROKE", "FLOW")):
            if len(text) < 4:
                continue
            rows.append(
                {
                    "category": "process",
                    "process_name": text,
                    "process_code": None,
                    "drawing_id": None,
                    "description": text,
                    "from": None,
                    "to": None,
                    "linked_diagram": None,
                    "layer": t.get("layer"),
                    "position": fmt_point(t.get("position")),
                    "source": "text_label",
                }
            )

    for layer, service in PROCESS_LAYERS.items():
        count = sum(1 for e in structural.get("entities", []) if e.get("layer") == layer)
        if count:
            rows.append(
                {
                    "category": "process",
                    "process_name": service,
                    "process_code": layer,
                    "drawing_id": None,
                    "description": f"Entities on service layer {layer}",
                    "from": None,
                    "to": None,
                    "linked_diagram": None,
                    "layer": layer,
                    "position": None,
                    "source": "layer_service",
                    "entity_count": count,
                }
            )
    return rows


def extract_sub_process(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    seen = set()

    sub_process_keywords = (
        "SCREEN", "PULPER", "THICKENER", "REJECT", "FLUSHING", "DILUTION", "DUMP",
        "HANDLING", "SEQUENCE", "INTERLOCK", "SHOWER", "AGITATOR", "ROTOR",
    )

    for ins in structural.get("inserts", []):
        attrs = group_attributes(ins.get("attributes", []))
        for field in ("TEKSTI2", "TEKSTI1"):
            val = (attrs.get(field) or "").strip()
            if not val:
                continue
            key = val.upper()
            if key in seen:
                continue
            if any(k in key for k in sub_process_keywords) or EQUIP_TAG_RE.match(val.replace(" ", "")):
                seen.add(key)
                rows.append(
                    {
                        "category": "sub_process",
                        "sub_process_name": val,
                        "parent_process": attrs.get("TEKSTI1"),
                        "reference_tag": attrs.get("TEKSTI2") if field == "TEKSTI2" else None,
                        "linked_diagram": attrs.get("KAAVIO"),
                        "block_name": ins.get("name"),
                        "layer": ins.get("layer"),
                        "position": fmt_point(ins.get("insert")),
                        "source": f"attribute:{field}",
                    }
                )

    for t in structural.get("text_entities", []):
        text = (t.get("text") or "").strip()
        up = text.upper()
        if not text or up in seen:
            continue
        if "SUB-PROCESS CODE" in up or any(k in up for k in sub_process_keywords):
            seen.add(up)
            rows.append(
                {
                    "category": "sub_process",
                    "sub_process_name": text,
                    "parent_process": None,
                    "reference_tag": None,
                    "linked_diagram": None,
                    "block_name": None,
                    "layer": t.get("layer"),
                    "position": fmt_point(t.get("position")),
                    "source": "text_label",
                }
            )
    return rows


def extract_function(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for ins in structural.get("inserts", []):
        layer = ins.get("layer") or ""
        name = ins.get("name") or ""
        family = block_family(name)
        attrs = group_attributes(ins.get("attributes", []))

        is_function = (
            layer in FUNCTION_LAYER_HINTS
            or family in ("P7A_function_symbol", "PPI_instrument_equipment", "CVM_control_valve", "PRM_instrument", "CTV_transmitter")
            or name.upper().startswith(("CVM", "PRM", "CTV", "P7A", "PPI"))
        )
        if not is_function:
            continue
        if layer in EQUIPMENT_LAYERS or layer in SUB_EQUIPMENT_LAYERS:
            continue

        rows.append(
            {
                "category": "function",
                "function_type": FUNCTION_LAYER_HINTS.get(layer) or family,
                "symbol_block": name,
                "block_family": family,
                "handle": ins.get("handle"),
                "layer": layer,
                "position": fmt_point(ins.get("insert")),
                "rotation": ins.get("rotation"),
                "position_number": attrs.get("ANTPOS"),
                "loop_ref": attrs.get("TEKSTI2"),
                "description": attrs.get("TEKSTI1") or attrs.get("ANTNIMI"),
                "linked_diagram": attrs.get("KAAVIO"),
                "attributes_json": json.dumps(json_safe(attrs), ensure_ascii=True),
            }
        )
    return rows


def extract_masks(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for e in structural.get("entities", []):
        layer = e.get("layer") or ""
        if layer not in ("P-MASS1", "FIMPEC_COLOR", "FIMPEC_BW"):
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
                "category": "masks",
                "mask_type": "mass_balance_region" if layer == "P-MASS1" else "fimpec_mask",
                "handle": e.get("handle"),
                "entity_type": e.get("type"),
                "layer": layer,
                "vertex_count": len(pts),
                "closed": geom.get("closed"),
                "bbox": bbox,
                "geometry_json": json.dumps(json_safe(geom), ensure_ascii=True),
                "source": "geometry",
            }
        )

    # Dynamic/anonymous blocks used as off-page connectors can act as diagram masks/links
    for ins in structural.get("inserts", []):
        if ins.get("layer") == "P-MASS1":
            rows.append(
                {
                    "category": "masks",
                    "mask_type": "mass_balance_insert",
                    "handle": ins.get("handle"),
                    "entity_type": "INSERT",
                    "layer": ins.get("layer"),
                    "vertex_count": None,
                    "closed": None,
                    "bbox": fmt_point(ins.get("insert")),
                    "geometry_json": json.dumps({"block": ins.get("name")}, ensure_ascii=True),
                    "source": "insert",
                }
            )
    return rows


def run_semantic_extraction(structural: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    return {
        "equipment": extract_equipment(structural),
        "lines": extract_lines(structural),
        "process": extract_process(structural),
        "sub_process": extract_sub_process(structural),
        "function": extract_function(structural),
        "sub_equipment": extract_sub_equipment(structural),
        "masks": extract_masks(structural),
    }


def export_semantic_workbook(semantic: Dict[str, List[Dict[str, Any]]], out_path: Path) -> None:
    import pandas as pd

    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary = []
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for sheet, rows in semantic.items():
            summary.append({"sheet": sheet, "row_count": len(rows)})
            pd.DataFrame(rows if rows else [{"note": "empty"}]).to_excel(
                writer, sheet_name=sheet[:31], index=False
            )
        pd.DataFrame(summary).to_excel(writer, sheet_name="summary", index=False)


def load_or_parse(input_path: Path, out_dir: Path, refresh: bool = False) -> Tuple[Dict[str, Any], str]:
    base = safe_name(input_path)
    cached = find_json(out_dir, f"{base}.structural_dump.json")
    if cached.exists() and not refresh:
        return json.loads(cached.read_text(encoding="utf-8")), "cached_json"

    configure_odafc()
    structural, err = parse_with_ezdxf(input_path)
    if structural is None:
        raise RuntimeError(err or "Failed to parse DWG")
    return structural, "live_parse"


def main() -> int:
    parser = argparse.ArgumentParser(description="P&ID semantic extraction pass")
    parser.add_argument("--input", required=True, help="Input DWG/DXF path")
    parser.add_argument("--output-dir", default="outputs", help="Output directory")
    parser.add_argument("--refresh", action="store_true", help="Force live DWG parse instead of cached JSON")
    parser.add_argument(
        "--no-clean-prev",
        action="store_true",
        help="Keep previous semantic outputs instead of clearing them first.",
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
            suffixes=(".semantic.xlsx", ".semantic.json"),
        )

    if args.refresh:
        structural, source = load_or_parse(input_path, out_dir, refresh=True)
    else:
        structural, source = load_or_parse(input_path, out_dir, refresh=False)

    print(f"[1/3] Loaded structural data ({source})")
    semantic = run_semantic_extraction(structural)
    print(f"[2/3] Extracted semantic categories:")
    for k, v in semantic.items():
        print(f"  - {k}: {len(v)}")

    xlsx_out = out_dir / f"{base}.semantic.xlsx"
    export_semantic_workbook(semantic, xlsx_out)
    json_out = json_path(out_dir, f"{base}.semantic.json")
    write_json(json_out, semantic)
    print(f"[3/3] Wrote {xlsx_out}")
    print(f"[3/3] Wrote {json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
