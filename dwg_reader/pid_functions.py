"""FUNCTION parent extraction, split from the inventory walk."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Any, Dict, List, Set


class FunctionIndex:
    """Keep the highest-priority row per function tag."""

    def __init__(self) -> None:
        self.best: Dict[str, Dict[str, Any]] = {}

    def upsert(self, tag: str, row: Dict[str, Any], rank: int) -> None:
        from dwg_reader.dwg_pid_inventory import _is_agitator_equipment_tag

        tag = tag.strip().upper()
        if not tag or "." in tag:
            return
        if _is_agitator_equipment_tag(tag):
            return
        prev = self.best.get(tag)
        if prev and int(prev.get("category_rank", 99)) <= rank:
            return
        row = dict(row)
        row["function"] = tag
        row["source"] = "cad"
        row["category_rank"] = rank
        self.best[tag] = row

    def rows(self) -> List[Dict[str, Any]]:
        out = sorted(self.best.values(), key=lambda r: (r.get("kind") or "", r["function"]))
        for r in out:
            r.pop("category_rank", None)
        return out


def function_text_points(structural: Dict[str, Any]) -> List[Dict[str, Any]]:
    from dwg_reader.dwg_pid_inventory import xyz

    text_pts: List[Dict[str, Any]] = []
    for t in structural.get("text_entities") or []:
        x, y, _ = xyz(t.get("position"))
        if x is None or y is None:
            continue
        raw = (t.get("text") or "").strip()
        if not raw:
            continue
        text_pts.append(
            {
                "text": raw,
                "norm": raw.replace(" ", "").upper(),
                "x": x,
                "y": y,
                "layer": t.get("layer"),
            }
        )
    return text_pts


def min_dist(x: float, y: float, pts: List[Dict[str, Any]]) -> float:
    return min((math.hypot(x - p["x"], y - p["y"]) for p in pts), default=9999.0)


def collect_equipment_functions(
    inventory: Dict[str, List[Dict[str, Any]]],
    texts: List[Dict[str, Any]],
    bag: FunctionIndex,
) -> None:
    from dwg_reader.dwg_pid_inventory import (
        EQUIP_TAG_RE,
        FUNCTION_DESC_LAYERS,
        FUNCTION_EQUIP_CATEGORIES,
        FUNCTION_TAG_LAYERS,
        FUNCTION_TAG_RE,
        LINE_NUMBER_RE,
        _is_agitator_equipment_tag,
        _nearest_texts,
    )

    for cat in FUNCTION_EQUIP_CATEGORIES:
        for item in inventory.get(cat) or []:
            if item.get("source") != "insert":
                continue
            if item.get("x") is None or item.get("y") is None:
                continue
            pos = (float(item["x"]), float(item["y"]))
            tag_hits = _nearest_texts(
                pos,
                texts,
                max_dist=90.0,
                layers=FUNCTION_TAG_LAYERS,
                predicate=lambda s: bool(EQUIP_TAG_RE.match(s.replace(" ", ""))),
            )
            desc_hits = _nearest_texts(
                pos,
                texts,
                max_dist=120.0,
                layers=FUNCTION_DESC_LAYERS,
                predicate=lambda s: (
                    len(s) >= 4
                    and not EQUIP_TAG_RE.match(s.replace(" ", ""))
                    and not LINE_NUMBER_RE.match(s.upper())
                ),
            )
            resolved = None
            for h in tag_hits:
                cand = h["text"].replace(" ", "").upper()
                if not FUNCTION_TAG_RE.match(cand):
                    continue
                if _is_agitator_equipment_tag(cand):
                    continue
                resolved = cand
                break
            if not resolved and item.get("position_number"):
                cand = str(item["position_number"]).replace(" ", "").upper()
                if FUNCTION_TAG_RE.match(cand) and not _is_agitator_equipment_tag(cand):
                    resolved = cand
            if not resolved:
                continue
            rank = {"tanks": 0, "process_equipment": 1, "pumps": 2}.get(cat, 9)
            bag.upsert(
                resolved,
                {
                    "kind": "equipment",
                    "category": cat,
                    "block_name": item.get("block_name"),
                    "handle": item.get("handle"),
                    "layer": item.get("layer"),
                    "x": item.get("x"),
                    "y": item.get("y"),
                    "z": item.get("z"),
                    "description": "; ".join(h["text"] for h in desc_hits[:3]),
                    "nearby_tags": "; ".join(h["text"] for h in tag_hits[:5]),
                    "confidence": "high",
                },
                rank,
            )


def collect_instrument_functions(text_pts: List[Dict[str, Any]], bag: FunctionIndex) -> None:
    from dwg_reader.dwg_pid_inventory import (
        AREA_CODE_RE,
        FULL_INSTR_TAG_RE,
        FUNCTION_INSTR_LETTERS,
        LOOP_NUM_RE,
    )

    for t in text_pts:
        m = FULL_INSTR_TAG_RE.match(t["norm"])
        if not m:
            continue
        tag = f"{m.group(1)}{m.group(2).upper()}-{m.group(3).upper()}"
        bag.upsert(
            tag,
            {
                "kind": "instrument",
                "category": "instruments",
                "block_name": "",
                "handle": "",
                "layer": t.get("layer"),
                "x": t["x"],
                "y": t["y"],
                "z": 0.0,
                "description": t["text"],
                "nearby_tags": tag,
                "confidence": "high",
            },
            10,
        )

    letters = [t for t in text_pts if t["norm"] in FUNCTION_INSTR_LETTERS]
    nums = [t for t in text_pts if LOOP_NUM_RE.match(t["norm"])]
    areas = [t for t in text_pts if AREA_CODE_RE.match(t["norm"])]
    cands: List[Dict[str, Any]] = []
    for L in letters:
        best_n = None
        best_nd = 30.0
        for n in nums:
            d = math.hypot(n["x"] - L["x"], n["y"] - L["y"])
            if d < best_nd:
                best_nd = d
                best_n = n
        if not best_n:
            continue
        best_a = None
        best_ad = 80.0
        for a in areas:
            d = math.hypot(a["x"] - L["x"], a["y"] - L["y"])
            if d < best_ad:
                best_ad = d
                best_a = a
        area = best_a["norm"] if best_a else "35-24"
        cands.append(
            {
                "tag": f"{area}{L['norm']}-{best_n['norm']}",
                "letter": L["norm"],
                "num": best_n["norm"],
                "area": area,
                "x": L["x"],
                "y": L["y"],
                "nd": best_nd,
                "layer": L.get("layer"),
                "text": L["text"],
                "num_text": best_n["text"],
            }
        )

    by_num: Dict[str, Set[str]] = defaultdict(set)
    for c in cands:
        if c["letter"] in {"HI", "HS"}:
            by_num[c["num"]].add(c["letter"])

    mcs = [t for t in text_pts if "MCS" in t["text"].upper() and "SIGNAL" in t["text"].upper()]
    shower = [t for t in text_pts if "SHOWER" in t["text"].upper()]
    panel = [
        t
        for t in text_pts
        if any(
            k in t["text"].upper().replace(" ", "")
            for k in ("LOCAL/REMOTE", "JOGGING", "START/STOP", "EMERGENCYSTOP", "LOCALPANEL")
        )
        or ("START" in t["text"].upper() and "STOP" in t["text"].upper())
    ]
    kjes = [c for c in cands if c["letter"] in {"KJ", "ES"}]
    valve_same = []
    for t in text_pts:
        m = re.match(r"^(?:\d{2}-\d{2})?(HV|XV|XSV|LV\d?)-(\d+)$", t["norm"])
        if m:
            valve_same.append({"num": m.group(2), "x": t["x"], "y": t["y"]})

    def near_valve(c: Dict[str, Any], radius: float = 60.0) -> bool:
        return any(
            v["num"] == c["num"] and math.hypot(c["x"] - v["x"], c["y"] - v["y"]) <= radius
            for v in valve_same
        )

    kept_instr: Set[str] = set()
    cand_by_tag = {c["tag"]: c for c in cands}
    for c in cands:
        letter = c["letter"]
        tag = c["tag"]
        if letter in {"KJ", "ES"}:
            kept_instr.add(tag)
            continue
        if letter == "XS":
            if min_dist(c["x"], c["y"], mcs) < 40 or min_dist(c["x"], c["y"], kjes) < 50:
                kept_instr.add(tag)
            continue
        if letter not in {"HI", "HS"}:
            continue
        paired = by_num[c["num"]] >= {"HI", "HS"}
        d_sh = min_dist(c["x"], c["y"], shower)
        d_pn = min_dist(c["x"], c["y"], panel)
        d_kj = min_dist(c["x"], c["y"], kjes)
        if (not paired) and near_valve(c) and d_pn >= 100 and d_kj >= 120:
            continue
        if letter == "HS" and (d_pn < 100 or d_kj < 120):
            kept_instr.add(tag)
        elif paired and (d_sh < 80 or d_pn < 100 or d_kj < 150):
            kept_instr.add(tag)
        elif letter == "HI" and (d_sh < 55 or d_kj < 150):
            kept_instr.add(tag)

    for tag in list(kept_instr):
        m = re.match(r"^(\d{2}-\d{2})(HI|HS)-(\d+)$", tag)
        if not m:
            continue
        other = "HS" if m.group(2) == "HI" else "HI"
        other_tag = f"{m.group(1)}{other}-{m.group(3)}"
        if other_tag in cand_by_tag:
            kept_instr.add(other_tag)

    for tag in kept_instr:
        c = cand_by_tag.get(tag)
        if not c:
            continue
        bag.upsert(
            tag,
            {
                "kind": "instrument",
                "category": "instruments",
                "block_name": "",
                "handle": "",
                "layer": c.get("layer"),
                "x": c["x"],
                "y": c["y"],
                "z": 0.0,
                "description": f"{c['text']} {c['num_text']} ({c['area']})",
                "nearby_tags": f"{c['text']}; {c['num_text']}; {c['area']}",
                "confidence": "high" if c["nd"] <= 25 else "medium",
            },
            11 if c["nd"] <= 25 else 12,
        )


def collect_line_functions(
    inventory: Dict[str, List[Dict[str, Any]]],
    text_pts: List[Dict[str, Any]],
    bag: FunctionIndex,
) -> None:
    from dwg_reader.dwg_pid_inventory import (
        FUNCTION_LINE_AREA_PREFIXES,
        LINE_SHORT_RE,
        _is_agitator_equipment_tag,
        _line_size_and_type,
    )

    dlim = [
        (float(i["x"]), float(i["y"]))
        for i in inventory.get("delivery_limits") or []
        if i.get("x") is not None and i.get("y") is not None
    ]
    agi_pts = [t for t in text_pts if _is_agitator_equipment_tag(t["norm"])]

    line_best: Dict[str, Dict[str, Any]] = {}
    for item in inventory.get("lines") or []:
        raw = str(item.get("line_number") or "").strip().upper()
        m = LINE_SHORT_RE.match(raw)
        if not m or item.get("x") is None or item.get("y") is None:
            continue
        short = m.group(1)
        if not short.startswith(FUNCTION_LINE_AREA_PREFIXES):
            continue
        lt, size = _line_size_and_type(raw, str(item.get("line_type") or ""))
        x, y = float(item["x"]), float(item["y"])
        dd = min((math.hypot(x - a, y - b) for a, b in dlim), default=9999.0)
        prev = line_best.get(short)
        if prev and float(prev["dd"]) <= dd:
            continue
        line_best[short] = {
            "raw": raw,
            "lt": lt,
            "size": size,
            "dd": dd,
            "item": item,
            "x": x,
            "y": y,
        }

    for short, info in line_best.items():
        lt = info["lt"]
        size = int(info["size"])
        dd = float(info["dd"])
        x, y = float(info["x"]), float(info["y"])
        ok = False
        conf = "medium"
        rank = 22
        if lt == "WFL":
            ok, conf, rank = True, "high", 20
        elif lt == "WFC" and size == 0:
            ok, conf, rank = True, "high", 21
        elif lt == "WAF":
            if short.startswith("35-25-"):
                ok, conf, rank = True, "high", 21
            elif size >= 250 and dd <= 250:
                ok, conf, rank = True, "medium", 22
            elif size == 150 and dd <= 90:
                ok, conf, rank = True, "medium", 22
            elif 0 < size <= 20 and dd <= 300:
                ok, conf, rank = True, "medium", 22
        elif lt == "PP" and size == 250 and min_dist(x, y, agi_pts) < 40:
            ok, conf, rank = True, "medium", 22
        if not ok:
            continue
        item = info["item"]
        bag.upsert(
            short,
            {
                "kind": "line",
                "category": "lines",
                "block_name": "",
                "handle": item.get("handle"),
                "layer": item.get("layer"),
                "x": item.get("x"),
                "y": item.get("y"),
                "z": item.get("z"),
                "description": info["raw"],
                "nearby_tags": short,
                "confidence": conf,
            },
            rank,
        )


def build_functions(
    inventory: Dict[str, List[Dict[str, Any]]],
    structural: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Build the FUNCTION list from CAD only (GT hierarchy taxonomy shape):

      1. equipment  — L / P / T primary machines (tanks, process_equipment, pumps)
      2. instrument — HI / HS / KJ / ES / XS (panel / shower / e-stop / MCS)
      3. line       — WFL hose lines + white-water / cooling utility headers

    One row per unique function tag. ``source`` is always ``cad``.
    """
    texts = structural.get("text_entities") or []
    text_pts = function_text_points(structural)
    bag = FunctionIndex()
    collect_equipment_functions(inventory, texts, bag)
    collect_instrument_functions(text_pts, bag)
    collect_line_functions(inventory, text_pts, bag)
    return bag.rows()
