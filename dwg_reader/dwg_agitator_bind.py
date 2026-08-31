#!/usr/bin/env python3
"""CAD bind + tank-coverage + optional vision for Valmet agitators (C-09).

Pipeline:
  1. Bind L401–L499 labels on P-AGITATOR_POS to PPI inserts.
  2. Append bound agitators as EQUIPMENT under the nearest tank FUNCTION.
  3. Report vessels (tanks / pulpers) that still have no agitator child.
  4. Optional tight-crop at the vessel base: propeller yes/no. Nearby L4xx is
     bound; untagged propellers are QA-flagged and never given a made-up tag.
"""

from __future__ import annotations
import dwg_reader.dwg_warn as dwg_warn  # noqa: F401

import argparse
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple

from dwg_reader.config import DEFAULT_AWS_REGION, DEFAULT_MODEL_ID
from dwg_reader.dwg_pid_inventory import (
    _agitator_description,
    _is_agitator_equipment_tag,
    _nearest_texts,
    bind_agitator_tags,
)
from dwg_reader.dwg_pure_dump import find_json, json_path, safe_name, write_json
from dwg_reader.io import read_csv_rows, write_csv_rows
from dwg_reader.logutil import configure_logging, get_logger
from dwg_reader.models import HIERARCHY_COLUMNS
from dwg_reader.paths import evidence_dir

logger = get_logger(__name__)

AGITATOR_EQ_RE = re.compile(r"^\d{2}-\d{2}L(4\d{2})$", re.I)
TANK_FN_RE = re.compile(r"^\d{2}-\d{2}T\d+", re.I)
# Tanks plus process vessels / pulpers (L001–L399). L401–L499 are agitators.
VESSEL_FN_RE = re.compile(r"^\d{2}-\d{2}[TL]\d+$", re.I)

VisionDetect = Callable[[str, Path], bool]

_PROPELLER_PROMPT = """\
This crop is the base of vessel {TAG} on a Valmet P&ID.
Look for a propeller / agitator glyph (three blades, or a PPI agitator symbol)
sitting in the tank or pulper — not a pump, not a valve bowtie, not a motor circle.
Reply with ONLY JSON: {{"propeller": true}} or {{"propeller": false}}
Do not invent equipment tags.
"""


def _norm(tag: str) -> str:
    return re.sub(r"\s+", "", str(tag or "").strip()).upper()


def is_vessel_function(tag: str) -> bool:
    t = _norm(tag)
    if not VESSEL_FN_RE.match(t):
        return False
    return not _is_agitator_equipment_tag(t)


def agitators_under_functions(rows: Sequence[Dict[str, str]]) -> Dict[str, List[str]]:
    """Map each FUNCTION header to L4xx EQUIPMENT children that follow it."""
    out: Dict[str, List[str]] = {}
    current = ""
    for row in rows:
        fn = _norm(row.get("FUNCTION") or "")
        eq = _norm(row.get("EQUIPMENT") or "")
        sub = _norm(row.get("SUB-EQUIPMENT") or "")
        if fn and not eq and not sub:
            current = fn
            out.setdefault(current, [])
            continue
        if current and eq and _is_agitator_equipment_tag(eq):
            out.setdefault(current, []).append(eq)
    return out


def vessel_coverage(
    hierarchy_rows: Sequence[Dict[str, str]],
    inventory: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """One record per tank/pulper FUNCTION in the hierarchy, with agitator children."""
    children = agitators_under_functions(hierarchy_rows)
    fn_xy: Dict[str, Tuple[float, float]] = {}
    for fn in inventory.get("functions") or []:
        tag = _norm(fn.get("function") or "")
        x, y = fn.get("x"), fn.get("y")
        if tag and x is not None and y is not None:
            fn_xy[tag] = (float(x), float(y))

    headers: List[str] = []
    seen: Set[str] = set()
    for row in hierarchy_rows:
        fn = _norm(row.get("FUNCTION") or "")
        eq = (row.get("EQUIPMENT") or "").strip()
        sub = (row.get("SUB-EQUIPMENT") or "").strip()
        if fn and not eq and not sub and fn not in seen and is_vessel_function(fn):
            seen.add(fn)
            headers.append(fn)

    report: List[Dict[str, Any]] = []
    for fn in headers:
        tags = list(children.get(fn) or [])
        x, y = fn_xy.get(fn, (None, None))
        report.append(
            {
                "function": fn,
                "x": x,
                "y": y,
                "agitator_tags": tags,
                "has_agitator": bool(tags),
            }
        )
    return report


def nearby_unbound_l4xx(
    structural: Dict[str, Any],
    x: float,
    y: float,
    used: Set[str],
    *,
    max_dist: float = 80.0,
) -> Optional[str]:
    """Nearest unused L401–L499 label around a vessel."""
    hits = _nearest_texts(
        (x, y),
        structural.get("text_entities") or [],
        max_dist=max_dist,
        layers={"P-AGITATOR_POS", "P-TANK_POS", "P-TEXT", "P-EQUIPMENT_POS"},
        predicate=lambda s: _is_agitator_equipment_tag(s.replace(" ", "")),
        limit=8,
    )
    for h in hits:
        cand = _norm(h.get("text") or "")
        if cand and cand not in used:
            return cand
    return None


def parse_propeller_reply(raw: str) -> bool:
    text = str(raw or "").strip()
    if not text:
        return False
    try:
        start, end = text.find("{"), text.rfind("}")
        blob = text[start : end + 1] if start >= 0 and end > start else text
        data = json.loads(blob)
        return bool(data.get("propeller"))
    except (json.JSONDecodeError, TypeError, ValueError):
        return bool(re.search(r'"propeller"\s*:\s*true', text, re.I))


def bedrock_propeller_present(
    crop_path: Path,
    vessel_tag: str,
    *,
    model_id: str,
    region: str,
) -> bool:
    from dwg_reader.dwg_valve_classify import _bedrock_short_ask

    prompt = _PROPELLER_PROMPT.format(TAG=vessel_tag)
    raw = _bedrock_short_ask(
        prompt,
        crop_path,
        model_id=model_id,
        region=region,
        max_tokens=40,
    )
    return parse_propeller_reply(raw)


def append_agitator_equipment_rows(
    combined_csv: Path,
    inv_path: Path,
    structural_path: Optional[Path] = None,
) -> int:
    """Insert bound L401–L499 agitators as EQUIPMENT under the nearest tank FUNCTION."""
    if not inv_path.exists():
        logger.info("[agitator-bind] inventory not found: %s; skipping", inv_path)
        return 0

    existing = read_csv_rows(combined_csv, missing_ok=True)
    if not existing:
        return 0

    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    if structural_path and structural_path.exists():
        structural = json.loads(structural_path.read_text(encoding="utf-8"))
        n_bound = bind_agitator_tags(inventory, structural)
        if n_bound:
            inv_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
            logger.info("[agitator-bind] bound %d agitator insert tags in inventory", n_bound)

    in_hierarchy: Set[str] = set()
    for row in existing:
        for col in ("FUNCTION", "EQUIPMENT", "SUB-EQUIPMENT"):
            v = _norm(row.get(col) or "")
            if v:
                in_hierarchy.add(v)

    orphans: Dict[str, Dict[str, Any]] = {}
    for item in inventory.get("agitators") or []:
        if str(item.get("source") or "") not in {"insert", "vision"}:
            continue
        tag = _norm(item.get("tag") or "")
        m = AGITATOR_EQ_RE.match(tag)
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
        logger.info("[agitator-bind] no unbound agitator tags to append")
        return 0

    existing_fn_headers = {
        _norm(row.get("FUNCTION") or "")
        for row in existing
        if row.get("FUNCTION") and not row.get("EQUIPMENT") and not row.get("SUB-EQUIPMENT")
    }
    fn_locs: Dict[str, Tuple[float, float]] = {}
    for fn in inventory.get("functions") or []:
        tag = _norm(fn.get("function") or "")
        x, y = fn.get("x"), fn.get("y")
        if tag in existing_fn_headers and x is not None and y is not None:
            fn_locs[tag] = (float(x), float(y))

    tank_locs = {fn: xy for fn, xy in fn_locs.items() if TANK_FN_RE.match(fn)}
    if not tank_locs and not fn_locs:
        logger.info("[agitator-bind] no function positions available; skipping")
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
        if tank_locs:
            best_fn, best_d = _nearest(tank_locs, ox, oy)
            if best_d > 150 and fn_locs:
                alt_fn, alt_d = _nearest(fn_locs, ox, oy)
                if alt_d + 20 < best_d:
                    best_fn, best_d = alt_fn, alt_d
        else:
            best_fn, best_d = _nearest(fn_locs, ox, oy)
        fn_agits.setdefault(best_fn, []).append(tag)
        logger.info("[agitator-bind]   %s → %s (d=%.0f)", tag, best_fn, best_d)

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
        fn = _norm(row.get("FUNCTION") or "")
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
    write_csv_rows(combined_csv, result, HIERARCHY_COLUMNS)
    logger.info("[agitator-bind] appended %d agitator equipment rows → %s", count, combined_csv.name)
    return count


def _used_agitator_tags(inventory: Dict[str, Any], hierarchy_rows: Sequence[Dict[str, str]]) -> Set[str]:
    used: Set[str] = set()
    for row in hierarchy_rows:
        for col in ("FUNCTION", "EQUIPMENT", "SUB-EQUIPMENT"):
            t = _norm(row.get(col) or "")
            if _is_agitator_equipment_tag(t):
                used.add(t)
    for item in inventory.get("agitators") or []:
        t = _norm(item.get("tag") or "")
        if _is_agitator_equipment_tag(t):
            used.add(t)
    return used


def _add_vision_agitator(
    inventory: Dict[str, Any],
    *,
    tag: str,
    x: float,
    y: float,
    structural: Dict[str, Any],
) -> None:
    desc_hits = _nearest_texts(
        (x, y),
        structural.get("text_entities") or [],
        max_dist=80.0,
        layers={"P-TANK_POS", "P-TEXT"},
        limit=15,
    )
    inventory.setdefault("agitators", []).append(
        {
            "source": "vision",
            "tag": tag,
            "x": x,
            "y": y,
            "description": _agitator_description(tag, desc_hits),
            "confidence": "medium",
        }
    )


def run_agitator_bind(
    *,
    hierarchy_csv: Path,
    inventory_json: Path,
    structural_json: Optional[Path] = None,
    input_path: Optional[Path] = None,
    out_dir: Optional[Path] = None,
    vision: bool = False,
    vision_detect: Optional[VisionDetect] = None,
    skip_existing: bool = False,
    model_id: str = DEFAULT_MODEL_ID,
    region: str = DEFAULT_AWS_REGION,
    crop_half: float = 70.0,
    extra_below: float = 90.0,
) -> Dict[str, Any]:
    """CAD bind, append, coverage, optional propeller vision. Writes agitator_bind.json."""
    hier_path = Path(hierarchy_csv)
    inv_path = Path(inventory_json)
    struct_path = Path(structural_json) if structural_json else None
    out = Path(out_dir) if out_dir else hier_path.parent
    base = safe_name(Path(input_path)) if input_path else hier_path.stem.replace(".hierarchy_orchestrator", "")
    cache_path = json_path(out, f"{base}.agitator_bind.json")

    n_appended = append_agitator_equipment_rows(hier_path, inv_path, struct_path)
    rows = read_csv_rows(hier_path, missing_ok=True)
    inventory = json.loads(inv_path.read_text(encoding="utf-8")) if inv_path.exists() else {}
    structural = (
        json.loads(struct_path.read_text(encoding="utf-8"))
        if struct_path and struct_path.exists()
        else {}
    )
    coverage = vessel_coverage(rows, inventory)
    prev = {}
    if skip_existing and cache_path.exists():
        try:
            prev = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prev = {}
    prev_vision = {
        str(v.get("function") or ""): v
        for v in (prev.get("vision") or [])
        if isinstance(v, dict)
    }

    vision_rows: List[Dict[str, Any]] = []
    uncovered = [c for c in coverage if not c["has_agitator"] and c["x"] is not None]
    if vision and uncovered:
        used = _used_agitator_tags(inventory, rows)
        detect = vision_detect
        crop_dir = evidence_dir(out) / "_agitator_crops"
        crop_dir.mkdir(parents=True, exist_ok=True)
        need_render = [c for c in uncovered if not (skip_existing and c["function"] in prev_vision)]
        doc = None
        entity_index = None
        if detect is None and input_path and Path(input_path).exists() and need_render:
            try:
                from dwg_reader.dwg_pid_hierarchy_ai import load_drawing
                from dwg_reader.dwg_valve_classify import build_entity_extent_index

                logger.info("[agitator-bind] opening DWG for %d vessel-base crops", len(need_render))
                doc = load_drawing(Path(input_path))
                entity_index = build_entity_extent_index(doc)
            except Exception as exc:
                logger.warning("[agitator-bind] DWG render unavailable: %s", exc)

        from dwg_reader.dwg_valve_classify import tight_valve_screenshot

        for rec in uncovered:
            fn = rec["function"]
            cached = prev_vision.get(fn) if skip_existing else None
            if cached:
                vision_rows.append(cached)
                continue
            safe_fn = re.sub(r"[^\w.\-]", "_", fn)
            crop_path = crop_dir / f"{safe_fn}.png"
            propeller = False
            bound_tag = None
            qa = ""
            if detect is not None:
                crop_path.parent.mkdir(parents=True, exist_ok=True)
                if not crop_path.exists():
                    crop_path.write_bytes(b"")
                try:
                    propeller = bool(detect(fn, crop_path))
                except Exception as exc:
                    logger.warning("[agitator-bind] vision_detect failed for %s: %s", fn, exc)
            elif doc is not None:
                rendered = tight_valve_screenshot(
                    doc,
                    float(rec["x"]),
                    float(rec["y"]),
                    crop_path,
                    half=crop_half,
                    extra_below=extra_below,
                    entity_index=entity_index,
                )
                if rendered is not None:
                    try:
                        propeller = bedrock_propeller_present(
                            rendered, fn, model_id=model_id, region=region
                        )
                    except Exception as exc:
                        logger.warning("[agitator-bind] Bedrock failed for %s: %s", fn, exc)
            if propeller:
                bound_tag = nearby_unbound_l4xx(structural, float(rec["x"]), float(rec["y"]), used)
                if bound_tag:
                    used.add(bound_tag)
                    _add_vision_agitator(
                        inventory,
                        tag=bound_tag,
                        x=float(rec["x"]),
                        y=float(rec["y"]),
                        structural=structural,
                    )
                else:
                    qa = "PROPELLER SEEN NO TAG"
                    logger.info("[agitator-bind] %s: propeller, no L4xx — QA only", fn)
            vision_rows.append(
                {
                    "function": fn,
                    "propeller": propeller,
                    "tag": bound_tag or "",
                    "qa": qa,
                    "source": "VISION" if propeller else "NONE",
                }
            )

        if any(v.get("tag") for v in vision_rows):
            inv_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
            extra = append_agitator_equipment_rows(hier_path, inv_path, struct_path)
            n_appended += extra
            rows = read_csv_rows(hier_path, missing_ok=True)
            coverage = vessel_coverage(rows, json.loads(inv_path.read_text(encoding="utf-8")))

    report = {
        "drawing": base,
        "appended": n_appended,
        "coverage": coverage,
        "tanks_with_agitator": [c["function"] for c in coverage if c["has_agitator"]],
        "tanks_without_agitator": [c["function"] for c in coverage if not c["has_agitator"]],
        "vision": vision_rows,
        "untagged_propellers": [v["function"] for v in vision_rows if v.get("qa")],
    }
    write_json(cache_path, report)
    logger.info(
        "[agitator-bind] vessels=%d with_agi=%d without=%d vision=%d untagged=%d cache=%s",
        len(coverage),
        len(report["tanks_with_agitator"]),
        len(report["tanks_without_agitator"]),
        len(vision_rows),
        len(report["untagged_propellers"]),
        cache_path.name,
    )
    return report


def run_agitator_bind_from_args(args: argparse.Namespace) -> int:
    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve()
    base = safe_name(input_path)
    hier = Path(args.hierarchy_csv).expanduser().resolve() if args.hierarchy_csv else (
        out_dir / f"{base}.hierarchy_orchestrator.csv"
    )
    inv = find_json(out_dir, f"{base}.pid_inventory.json")
    struct = find_json(out_dir, f"{base}.structural_dump.json")
    if not hier.exists():
        logger.error("[error] Missing hierarchy CSV: %s", hier)
        return 2
    if not inv.exists():
        logger.error("[error] Missing inventory JSON: %s", inv)
        return 2
    run_agitator_bind(
        hierarchy_csv=hier,
        inventory_json=inv,
        structural_json=struct if struct.exists() else None,
        input_path=input_path,
        out_dir=out_dir,
        vision=not bool(args.no_vision),
        skip_existing=bool(args.skip_existing),
        model_id=args.model_id,
        region=args.region,
    )
    return 0


def main() -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="Bind Valmet agitators and crop tank bases for propellers")
    parser.add_argument("--input", default="inputs/Broke System.dwg")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--hierarchy-csv", default="")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--region", default=os.environ.get("AWS_REGION") or DEFAULT_AWS_REGION)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--no-vision", action="store_true", help="CAD bind/append only; skip propeller crops")
    return run_agitator_bind_from_args(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
