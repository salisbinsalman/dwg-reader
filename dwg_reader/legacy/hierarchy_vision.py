#!/usr/bin/env python3
"""
Pilot hierarchy for selected P&ID equipment tags.

Design (anti-hallucination):
  1) Parent from tag register (CAD)
  2) Children from exact same-tag + pipe-endpoint graph (CAD) — not loose proximity
  3) Crop = local DWG entities only (not full-sheet zoom soup)
  4) Bedrock is optional and CONFIRM/REJECT only — cannot invent new links
  5) CSV is the deliverable
"""

from __future__ import annotations

import dwg_reader.dwg_warn as dwg_warn  # noqa: F401 — silence boto3 Python 3.9 deprecation noise

import argparse
import csv
import json
import math
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from dwg_reader.dwg_pure_dump import (
    clear_evidence_outputs,
    clear_previous_outputs,
    configure_odafc,
    evidence_dir,
    find_json,
    json_path,
    safe_name,
    write_json,
)

CSV_COLUMNS = [
    "ORDER",
    "SITE",
    "LINE",
    "PROCESS",
    "SUB-PROCESS",
    "FUNCTION",
    "EQUIPMENT",
    "SUB-EQUIPMENT",
    "MASK",
]

PRIMARY_CATEGORIES = {"tanks", "process_equipment", "pumps", "agitators"}
CHILD_CATEGORIES = {
    "motors",
    "agitators",
    "valves",
    "control_valves",
    "instruments",
    "fittings",
    "terminals",
    "symbols",
}
PARENT_PRIORITY = {
    "tanks": 0,
    "process_equipment": 1,
    "pumps": 2,
    "agitators": 3,
    "motors": 4,
    "control_valves": 5,
    "valves": 6,
    "instruments": 7,
    "fittings": 8,
}


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dist(a: Sequence[float], b: Sequence[float]) -> float:
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def normalize_tag(tag: str) -> str:
    return re.sub(r"\s+", "", tag or "").upper()


def area_from_tag(tag: str) -> Optional[str]:
    m = re.match(r"^(\d{2}-\d{2})", normalize_tag(tag))
    return m.group(1) if m else None


def pick_parent(rows: List[Dict[str, Any]], tag: str) -> Optional[Dict[str, Any]]:
    if not rows:
        return None
    want = normalize_tag(tag)
    exact = [r for r in rows if normalize_tag(str(r.get("resolved_tag") or "")) == want]
    pool = exact or rows

    type_letter = ""
    m = re.match(r"^\d{2}-\d{2}([A-Z]+)\d+", want)
    if m:
        type_letter = m.group(1).upper()
    desc_hints = {
        "L": ("PULPER", "TANK", "VESSEL", "CHEST", "BIN", "SILO", "VAT"),
        "T": ("TANK", "VESSEL", "CHEST"),
        "P": ("PUMP",),
        "AG": ("AGITATOR",),
        "M": ("MOTOR",),
    }
    hints = desc_hints.get(type_letter, ())

    def score(r: Dict[str, Any]) -> Tuple:
        cat = str(r.get("category") or "")
        layer = str(r.get("layer") or "").upper()
        desc = str(r.get("nearby_descriptions") or "").upper()
        hint_hit = any(h in desc for h in hints)
        pos_layer = layer.endswith("_POS") or layer.endswith("POS")
        primary = cat in PRIMARY_CATEGORIES
        return (
            0 if primary else 1,
            0 if hint_hit else 1,
            0 if pos_layer and primary else 1,
            PARENT_PRIORITY.get(cat, 99),
            -len(desc),
        )

    return sorted(pool, key=score)[0]


def collect_tag_rows(tag_register: List[Dict[str, Any]], tag: str) -> List[Dict[str, Any]]:
    want = normalize_tag(tag)
    out = []
    for row in tag_register:
        resolved = normalize_tag(str(row.get("resolved_tag") or ""))
        if resolved == want:
            out.append(row)
    return out


def bbox_square(cx: float, cy: float, half: float) -> Tuple[float, float, float, float]:
    return cx - half, cy - half, cx + half, cy + half


def entity_xy(entity: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    for key in ("insert", "position", "start", "center"):
        val = entity.get(key)
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            try:
                return float(val[0]), float(val[1])
            except Exception:
                pass
    if entity.get("x") is not None and entity.get("y") is not None:
        try:
            return float(entity["x"]), float(entity["y"])
        except Exception:
            return None
    return None


def build_pipe_component_graph(
    inventory: Dict[str, Any],
    snap_tol: float = 40.0,
) -> Tuple[Dict[str, set], Dict[str, Dict[str, Any]]]:
    nodes: Dict[str, Dict[str, Any]] = {}
    for cat in (
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
        for row in inventory.get(cat, []):
            if row.get("source") != "insert":
                continue
            handle = str(row.get("handle") or "")
            if not handle or row.get("x") is None or row.get("y") is None:
                continue
            nodes[handle] = {
                "handle": handle,
                "category": cat,
                "block_name": row.get("block_name"),
                "layer": row.get("layer"),
                "x": float(row["x"]),
                "y": float(row["y"]),
            }

    def q(v: float) -> float:
        return round(float(v), 1)

    # component -> set of quantized endpoints it touches
    comp_endpoints: Dict[str, set] = defaultdict(set)
    endpoint_comps: Dict[Tuple[float, float], List[str]] = defaultdict(list)
    # segment -> endpoints
    seg_ends: Dict[str, List[Tuple[float, float]]] = {}
    tol2 = snap_tol * snap_tol

    node_list = list(nodes.items())
    for seg in inventory.get("pipe_segments", []):
        handle = str(seg.get("handle") or "")
        pts: List[Tuple[float, float]] = []
        # prefer full polyline vertices when present
        try:
            geom = json.loads(seg.get("geometry_json") or "{}")
            raw_pts = geom.get("points_xyseb") or []
            for p in raw_pts:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    pts.append((float(p[0]), float(p[1])))
        except Exception:
            pts = []
        if len(pts) < 2:
            sx, sy, ex, ey = seg.get("start_x"), seg.get("start_y"), seg.get("end_x"), seg.get("end_y")
            if None in (sx, sy, ex, ey):
                continue
            pts = [(float(sx), float(sy)), (float(ex), float(ey))]
        seg_ends[handle] = pts
        # sample start/end + every vertex (for short segs) / stride for long
        sample = pts if len(pts) <= 8 else [pts[0], pts[len(pts) // 2], pts[-1]]
        for exf, eyf in sample:
            for ch, node in node_list:
                if (node["x"] - exf) ** 2 + (node["y"] - eyf) ** 2 <= tol2:
                    key = (q(exf), q(eyf))
                    endpoint_comps[key].append(ch)
                    comp_endpoints[ch].add(key)

    adj: Dict[str, set] = defaultdict(set)
    # same endpoint cluster
    for handles in endpoint_comps.values():
        uniq = sorted(set(handles))
        for i, a in enumerate(uniq):
            for b in uniq[i + 1 :]:
                adj[a].add(b)
                adj[b].add(a)

    # opposite ends / shared segment
    for pts in seg_ends.values():
        touched = set()
        for exf, eyf in (pts[0], pts[-1]):
            touched.update(endpoint_comps.get((q(exf), q(eyf)), []))
        uniq = sorted(touched)
        for i, a in enumerate(uniq):
            for b in uniq[i + 1 :]:
                adj[a].add(b)
                adj[b].add(a)

    return adj, nodes


def graph_neighbors_multi(adj: Dict[str, set], starts: List[str], max_hops: int = 2) -> Dict[str, int]:
    best: Dict[str, int] = {}
    for start in starts:
        if not start:
            continue
        seen = {start: 0}
        queue = [start]
        while queue:
            cur = queue.pop(0)
            if seen[cur] >= max_hops:
                continue
            for nxt in adj.get(cur, ()):
                if nxt not in seen:
                    seen[nxt] = seen[cur] + 1
                    queue.append(nxt)
        for k, hops in seen.items():
            if k == start:
                continue
            if k not in best or hops < best[k]:
                best[k] = hops
    return best


def build_cad_candidates(
    tag: str,
    parent: Dict[str, Any],
    tag_register: List[Dict[str, Any]],
    inventory: Dict[str, Any],
    radius: float,
) -> List[Dict[str, Any]]:
    px, py = float(parent["x"]), float(parent["y"])
    want = normalize_tag(tag)
    parent_handle = str(parent.get("handle") or "")
    adj, nodes = build_pipe_component_graph(inventory)

    # Seed graph from ALL exact-tag primary inserts (POS + equipment graphic)
    seed_handles = [parent_handle]
    for row in tag_register:
        if normalize_tag(str(row.get("resolved_tag") or "")) != want:
            continue
        if row.get("category") in PRIMARY_CATEGORIES and row.get("handle"):
            seed_handles.append(str(row["handle"]))
    hop_map = graph_neighbors_multi(adj, seed_handles, max_hops=2)

    tag_by_handle = {
        str(r.get("handle")): normalize_tag(str(r.get("resolved_tag") or ""))
        for r in tag_register
        if r.get("handle")
    }
    register_by_handle = {str(r.get("handle")): r for r in tag_register if r.get("handle")}

    seen = set()
    cands: List[Dict[str, Any]] = []

    def add_row(row: Dict[str, Any], reason: str, confidence: str, hops: Optional[int] = None) -> None:
        handle = str(row.get("handle") or "")
        if not handle or handle == parent_handle or handle in seen:
            return
        try:
            x, y = float(row["x"]), float(row["y"])
        except Exception:
            return
        seen.add(handle)
        cands.append(
            {
                "candidate_id": handle,
                "category": row.get("category"),
                "block_name": row.get("block_name"),
                "handle": handle,
                "layer": row.get("layer"),
                "x": x,
                "y": y,
                "distance_to_parent": round(dist((px, py), (x, y)), 2),
                "resolved_tag": row.get("resolved_tag"),
                "nearby_tags": row.get("nearby_tags"),
                "nearby_descriptions": row.get("nearby_descriptions"),
                "cad_relation_guess": reason,
                "cad_confidence": confidence,
                "graph_hops": hops,
            }
        )

    for row in tag_register:
        if normalize_tag(str(row.get("resolved_tag") or "")) != want:
            continue
        try:
            d = dist((px, py), (float(row["x"]), float(row["y"])))
        except Exception:
            continue
        if d > radius:
            continue
        cat = str(row.get("category") or "")
        if cat in CHILD_CATEGORIES:
            add_row(row, "same_tag_child", "high")
        elif cat in PRIMARY_CATEGORIES:
            add_row(row, "same_tag_symbol", "medium")

    for handle, hops in hop_map.items():
        node = nodes.get(handle)
        if not node:
            continue
        resolved = tag_by_handle.get(handle, "")
        base = register_by_handle.get(handle, {})
        row = {
            "category": node["category"],
            "block_name": node["block_name"],
            "handle": handle,
            "layer": node["layer"],
            "x": node["x"],
            "y": node["y"],
            "resolved_tag": base.get("resolved_tag") or resolved or None,
            "nearby_tags": base.get("nearby_tags"),
            "nearby_descriptions": base.get("nearby_descriptions"),
        }
        if resolved and resolved != want:
            # Connected in process, but owned by another equipment tag — not our subequipment.
            if node["category"] in PRIMARY_CATEGORIES:
                add_row(row, "pipe_linked_peer", "high", hops=hops)
            else:
                add_row(row, "pipe_linked_foreign", "medium", hops=hops)
        elif node["category"] in CHILD_CATEGORIES or resolved == want:
            # Untagged pipe neighbors: keep only 1-hop to avoid flooding via long headers.
            if not resolved and hops and hops > 1:
                continue
            add_row(row, "pipe_linked_child", "high" if hops == 1 else "medium", hops=hops)

    cands.sort(
        key=lambda c: (
            0 if "child" in c["cad_relation_guess"] else 1,
            c.get("graph_hops") if c.get("graph_hops") is not None else 99,
            c["distance_to_parent"],
        )
    )
    return cands


def load_drawing_doc(input_path: Path):
    import ezdxf

    configure_odafc()
    if input_path.suffix.lower() == ".dxf":
        return ezdxf.readfile(str(input_path))
    from ezdxf.addons import odafc

    return odafc.readfile(str(input_path))


def entities_in_bbox(msp, bbox: Tuple[float, float, float, float]):
    import ezdxf.bbox as ezbbox

    xmin, ymin, xmax, ymax = bbox
    for entity in msp:
        try:
            ext = ezbbox.extents([entity], fast=True)
            if ext is None or not ext.has_data:
                continue
            if ext.extmax.x < xmin or ext.extmin.x > xmax or ext.extmax.y < ymin or ext.extmin.y > ymax:
                continue
            yield entity
        except Exception:
            continue


def render_cad_crop(
    doc,
    bbox: Tuple[float, float, float, float],
    out_path: Path,
    parent: Optional[Dict[str, Any]] = None,
    title: str = "",
    dpi: int = 220,
) -> Optional[Path]:
    """Render only local entities — avoids full-sheet pixel soup."""
    try:
        from ezdxf.addons.drawing import Frontend, RenderContext
        from ezdxf.addons.drawing import matplotlib as ezdxf_matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle
    except Exception as e:
        print(f"[warn] CAD render unavailable: {e}")
        return None

    xmin, ymin, xmax, ymax = bbox
    cx, cy = (xmin + xmax) / 2.0, (ymin + ymax) / 2.0
    half = max((xmax - xmin), (ymax - ymin), 100.0) / 2.0
    xmin, ymin, xmax, ymax = bbox_square(cx, cy, half)

    ents = list(entities_in_bbox(doc.modelspace(), (xmin, ymin, xmax, ymax)))
    if not ents:
        print(f"[warn] No entities in window ({xmin:.1f},{ymin:.1f})-({xmax:.1f},{ymax:.1f})")
        return None

    fig = plt.figure(figsize=(10, 10), dpi=dpi)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    Frontend(RenderContext(doc), ezdxf_matplotlib.MatplotlibBackend(ax)).draw_entities(ents)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    ax.set_axis_off()

    if parent and parent.get("x") is not None:
        px, py = float(parent["x"]), float(parent["y"])
        ax.add_patch(Circle((px, py), half * 0.07, fill=False, edgecolor="#dc2626", linewidth=2.0))
        ax.text(
            px,
            min(py + half * 0.12, ymax - 2),
            f"PARENT {title}",
            color="#b91c1c",
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="bottom",
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor="white", dpi=dpi, pad_inches=0.02)
    plt.close(fig)
    print(f"[render] {len(ents)} local entities -> {out_path.name}")
    return out_path


def bedrock_confirm(
    image_path: Path,
    parent: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    model_id: str,
    region: str,
) -> Dict[str, Any]:
    """Vision may only confirm/reject CAD candidates — never invent new ones."""
    import boto3

    brief = [
        {
            "candidate_id": c["candidate_id"],
            "category": c["category"],
            "resolved_tag": c.get("resolved_tag"),
            "cad_relation_guess": c["cad_relation_guess"],
            "graph_hops": c.get("graph_hops"),
            "distance_to_parent": c["distance_to_parent"],
        }
        for c in candidates[:40]
    ]
    prompt = f"""
You are QA-checking a P&ID crop. CAD already proposed candidate links.
You may ONLY confirm or reject those candidates. Do NOT invent new equipment or links.

Parent: tag={parent.get('resolved_tag')} category={parent.get('category')} block={parent.get('block_name')}
Label hints: {parent.get('nearby_descriptions')}

For each candidate_id return decision:
- confirm_subequipment
- confirm_instrument
- confirm_peer
- reject
- uncertain

Return STRICT JSON:
{{
  "equipment_label": "...",
  "function_name": "...",
  "decisions": [
    {{"candidate_id":"...","decision":"...","confidence":"high|medium|low","reason":"..."}}
  ],
  "notes": ["..."]
}}

CAD candidates:
{json.dumps(brief, indent=2)}
""".strip()

    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [
                    {"text": prompt},
                    {"image": {"format": "png", "source": {"bytes": image_path.read_bytes()}}},
                ],
            }
        ],
        inferenceConfig={"maxTokens": 1600, "temperature": 0},
    )
    text_parts = [b["text"] for b in response.get("output", {}).get("message", {}).get("content", []) if "text" in b]
    raw = "\n".join(text_parts).strip()
    return {"raw_text": raw, "parsed": extract_json_object(raw), "model_id": model_id, "region": region}


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


def fuse_hierarchy(
    tag: str,
    parent: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    vision: Optional[Dict[str, Any]],
    sheet_title: str,
) -> Dict[str, Any]:
    area = area_from_tag(tag) or "unknown"
    vision_parsed = (vision or {}).get("parsed") if vision else None
    decisions = {}
    if vision_parsed and isinstance(vision_parsed.get("decisions"), list):
        for d in vision_parsed["decisions"]:
            if d.get("candidate_id"):
                decisions[d["candidate_id"]] = d

    children, peers, rejected, uncertain = [], [], [], []
    for c in candidates:
        guess = c["cad_relation_guess"]
        # CAD default mapping
        if guess in {"same_tag_child", "pipe_linked_child"}:
            relation = "subequipment" if c["category"] != "instruments" else "instrument_serving_parent"
        elif guess in {"pipe_linked_peer", "same_tag_symbol"}:
            relation = "peer_equipment"
        elif guess == "pipe_linked_foreign":
            relation = "foreign_equipment_link"
        else:
            relation = "uncertain"
        confidence = c["cad_confidence"]
        source = "cad"

        d = decisions.get(c["candidate_id"])
        if d:
            source = "cad+vision"
            decision = d.get("decision")
            if decision == "reject":
                # Vision can reject weak CAD guesses, but not strong pipe/same-tag children
                if guess in {"same_tag_child", "pipe_linked_child"} and c.get("cad_confidence") == "high":
                    confidence = "medium"
                    source = "cad_kept_over_vision_reject"
                else:
                    relation = "rejected"
                    confidence = d.get("confidence") or "medium"
            elif decision == "confirm_subequipment":
                relation = "subequipment"
            elif decision == "confirm_instrument":
                relation = "instrument_serving_parent"
            elif decision == "confirm_peer":
                relation = "peer_equipment"
            elif decision == "uncertain":
                confidence = "low"

        item = {**c, "final_relation": relation, "final_confidence": confidence, "source": source, "vision_reason": (d or {}).get("reason")}
        if relation in {"subequipment", "instrument_serving_parent"}:
            children.append(item)
        elif relation == "peer_equipment":
            peers.append(item)
        elif relation == "rejected":
            rejected.append(item)
        else:
            uncertain.append(item)

    function_name = sheet_title
    equipment_label = (parent.get("nearby_descriptions") or parent.get("block_name") or "").split(";")[0].strip()
    if vision_parsed:
        function_name = vision_parsed.get("function_name") or function_name
        equipment_label = vision_parsed.get("equipment_label") or equipment_label

    return {
        "target_tag": tag,
        "function": {"name": function_name, "area_code": area, "confidence": "high" if area != "unknown" else "medium"},
        "equipment": {
            "tag": tag,
            "category": parent.get("category"),
            "block_name": parent.get("block_name"),
            "handle": parent.get("handle"),
            "layer": parent.get("layer"),
            "x": parent.get("x"),
            "y": parent.get("y"),
            "label": equipment_label,
            "confidence": parent.get("confidence", "high"),
        },
        "subequipment": children,
        "peer_equipment": peers,
        "rejected": rejected,
        "other_or_uncertain": uncertain,
        "vision": {
            "used": bool(vision_parsed),
            "model_id": (vision or {}).get("model_id"),
            "notes": (vision_parsed or {}).get("notes") if vision_parsed else [],
            "raw_text": (vision or {}).get("raw_text") if vision else None,
        },
        "counts": {
            "candidates": len(candidates),
            "subequipment": len(children),
            "peer_equipment": len(peers),
            "rejected": len(rejected),
            "other_or_uncertain": len(uncertain),
            "pipe_linked": sum(1 for c in candidates if str(c.get("cad_relation_guess", "")).startswith("pipe_")),
        },
    }


def title_context(enrichment: Dict[str, Any], sheet_title: str) -> Dict[str, str]:
    site = line = ""
    process = sheet_title
    for block in enrichment.get("title_block") or []:
        if not isinstance(block, dict):
            continue
        if block.get("PROJECT1") or block.get("PROJECT2") or block.get("PROJECT3") or block.get("TITLE1"):
            site = str(block.get("PROJECT2") or block.get("PROJECT1") or "").strip() or site
            line = str(block.get("PROJECT3") or block.get("LYH") or "").strip() or line
            process = str(block.get("TITLE1") or "").strip() or process
    return {"site": site, "line": line, "process": process}


def mask_value(*parts: Any, max_len: int = 30) -> str:
    text = ":".join(str(p).strip() for p in parts if p is not None and str(p).strip())
    return re.sub(r"\s+", " ", text).strip()[:max_len]


def subequipment_label(child: Dict[str, Any]) -> str:
    cat = str(child.get("category") or "item")
    rel = str(child.get("final_relation") or "")
    tag = child.get("resolved_tag") or child.get("block_name") or child.get("handle")
    handle = child.get("handle")
    link = child.get("cad_relation_guess") or ""
    prefix = "instrument" if rel == "instrument_serving_parent" else cat.rstrip("s")
    base = f"{prefix} {tag}"
    if handle and str(tag) != str(handle):
        base += f" ({handle})"
    if link.startswith("pipe_"):
        base += " [pipe]"
    elif link.startswith("same_tag"):
        base += " [tag]"
    return base


def hierarchy_to_csv_rows(results: List[Dict[str, Any]], context: Dict[str, str]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    order = 1
    for result in results:
        if result.get("error"):
            continue
        equipment = result.get("equipment") or {}
        function = result.get("function") or {}
        equip_tag = str(equipment.get("tag") or result.get("target_tag") or "")
        equip_label = str(equipment.get("label") or "").split(";")[0].strip()
        equipment_cell = f"{equip_tag} {equip_label}".strip() if equip_label else equip_tag
        function_cell = str(function.get("name") or context["process"])
        sub_process = str(function.get("area_code") or "")

        rows.append(
            {
                "ORDER": str(order),
                "SITE": context["site"],
                "LINE": context["line"],
                "PROCESS": context["process"],
                "SUB-PROCESS": sub_process,
                "FUNCTION": function_cell,
                "EQUIPMENT": equipment_cell,
                "SUB-EQUIPMENT": "",
                "MASK": mask_value(equip_tag, equipment.get("category")),
            }
        )
        order += 1
        for child in result.get("subequipment") or []:
            rows.append(
                {
                    "ORDER": str(order),
                    "SITE": context["site"],
                    "LINE": context["line"],
                    "PROCESS": context["process"],
                    "SUB-PROCESS": sub_process,
                    "FUNCTION": function_cell,
                    "EQUIPMENT": equipment_cell,
                    "SUB-EQUIPMENT": subequipment_label(child),
                    "MASK": mask_value(child.get("category"), child.get("handle") or child.get("block_name")),
                }
            )
            order += 1
    return rows


def write_hierarchy_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def export_csv_from_payload(payload: Dict[str, Any], enrichment: Dict[str, Any], out_csv: Path) -> int:
    context = title_context(enrichment, str(payload.get("sheet_title") or "Unknown"))
    rows = hierarchy_to_csv_rows(payload.get("results") or [], context)
    write_hierarchy_csv(out_csv, rows)
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Connectivity-first P&ID hierarchy pilot")
    parser.add_argument("--input", default="inputs/Broke System.dwg")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--tags", default="35-24L009,35-24P519")
    parser.add_argument("--radius", type=float, default=80.0)
    parser.add_argument("--crop-half", type=float, default=130.0, help="Half-size of square CAD crop window")
    parser.add_argument("--model-id", default="eu.anthropic.claude-sonnet-4-5-20250929-v1:0")
    parser.add_argument("--region", default=None)
    parser.add_argument(
        "--vision-confirm",
        action="store_true",
        help="Optional Bedrock confirm/reject of CAD links (cannot invent).",
    )
    parser.add_argument("--skip-bedrock", action="store_true", help="Deprecated alias; CAD-only is default")
    parser.add_argument("--from-json", action="store_true")
    parser.add_argument("--no-clean-prev", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    base = safe_name(input_path)
    tags = [normalize_tag(t) for t in args.tags.split(",") if t.strip()]
    out_csv = out_dir / f"{base}.hierarchy.csv"
    out_json = json_path(out_dir, f"{base}.hierarchy_vision.json")
    enr_path = find_json(out_dir, f"{base}.pid_enrichment.json")

    if args.from_json:
        n = export_csv_from_payload(load_json(out_json), load_json(enr_path), out_csv)
        print(f"Wrote {out_csv} ({n} rows)")
        return 0

    if not args.no_clean_prev:
        clear_previous_outputs(
            out_dir,
            base,
            suffixes=(".hierarchy.csv", ".hierarchy.xlsx", ".hierarchy_vision.json"),
        )
        clear_evidence_outputs(out_dir, base, tags)
        for t in tags:
            for legacy in (
                out_dir / f"{base}.hierarchy_{t}.png",
                out_dir / f"{base}.hierarchy_{t}_cad.png",
                out_dir / f"{base}.hierarchy_{t}_schematic.png",
            ):
                if legacy.is_file():
                    legacy.unlink()

    inv_path = find_json(out_dir, f"{base}.pid_inventory.json")
    structural_path = find_json(out_dir, f"{base}.structural_dump.json")
    for required in (inv_path, enr_path, structural_path):
        if not required.exists():
            print(f"[error] Missing {required}. Run `make all` first.", file=sys.stderr)
            return 2

    inventory = load_json(inv_path)
    enrichment = load_json(enr_path)
    tag_register = enrichment.get("tag_register") or []
    sheet_title = input_path.stem
    context = title_context(enrichment, sheet_title)
    region = args.region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "eu-west-2"
    use_vision = bool(args.vision_confirm) and not args.skip_bedrock

    print("[0/4] Opening DWG for local CAD crops...")
    drawing_doc = load_drawing_doc(input_path)
    print("[0/4] DWG opened")

    results = []
    for tag in tags:
        print(f"\n=== {tag} ===")
        rows = collect_tag_rows(tag_register, tag)
        parent = pick_parent(rows, tag)
        if not parent:
            print(f"[warn] No parent for {tag}")
            results.append({"target_tag": tag, "error": "parent_not_found"})
            continue

        print(f"[1/4] Parent: {parent.get('category')} / {parent.get('block_name')} @ ({parent.get('x')}, {parent.get('y')})")
        candidates = build_cad_candidates(tag, parent, tag_register, inventory, radius=args.radius)
        pipe_n = sum(1 for c in candidates if str(c.get("cad_relation_guess", "")).startswith("pipe_"))
        print(f"[2/4] CAD candidates: {len(candidates)} (pipe-linked={pipe_n})")

        # Center crop on cluster of same-tag primary symbols, not only POS insert.
        centers = [(float(parent["x"]), float(parent["y"]))]
        for row in rows:
            if row.get("category") in PRIMARY_CATEGORIES and row.get("x") is not None:
                centers.append((float(row["x"]), float(row["y"])))
        cx = sum(p[0] for p in centers) / len(centers)
        cy = sum(p[1] for p in centers) / len(centers)
        bbox = bbox_square(cx, cy, args.crop_half)
        crop_path = evidence_dir(out_dir) / f"{base}.hierarchy_{tag}.png"
        rendered = render_cad_crop(drawing_doc, bbox, crop_path, parent=parent, title=tag)
        if not rendered:
            print("[error] CAD crop failed", file=sys.stderr)
            return 3
        print(f"[3/4] Wrote local DWG crop: {crop_path}")

        vision = None
        if use_vision:
            try:
                vision = bedrock_confirm(crop_path, parent, candidates, args.model_id, region)
                print(f"[4/4] Bedrock confirm/reject done ({args.model_id})")
            except Exception as e:
                print(f"[4/4] Bedrock failed ({e}); using CAD-only")
                vision = None
        else:
            print("[4/4] CAD-only hierarchy (no vision invent step)")

        fused = fuse_hierarchy(tag, parent, candidates, vision, sheet_title=sheet_title)
        fused["crop_image"] = str(crop_path)
        fused["crop_type"] = "cad_local"
        fused["bbox"] = {"xmin": bbox[0], "ymin": bbox[1], "xmax": bbox[2], "ymax": bbox[3]}
        results.append(fused)
        print(
            f"    children={fused['counts']['subequipment']} "
            f"peers={fused['counts']['peer_equipment']} "
            f"pipe_linked={fused['counts']['pipe_linked']} "
            f"vision={fused['vision']['used']}"
        )

    payload = {
        "input": str(input_path),
        "sheet_title": sheet_title,
        "site": context["site"],
        "line": context["line"],
        "process": context["process"],
        "tags": tags,
        "mode": "vision_confirm" if use_vision else "cad_connectivity_only",
        "model_id": args.model_id if use_vision else None,
        "region": region,
        "results": results,
    }
    write_json(out_json, payload)
    csv_rows = hierarchy_to_csv_rows(results, context)
    write_hierarchy_csv(out_csv, csv_rows)
    print(f"\nWrote {out_csv} ({len(csv_rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
