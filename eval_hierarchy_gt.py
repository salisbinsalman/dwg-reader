#!/usr/bin/env python3
"""Evaluate hierarchy CSV/JSON against GT sheet format."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

GT_COLUMNS = ["SUB-PROCESS", "FUNCTION", "EQUIPMENT", "SUB-EQUIPMENT", "MASK"]


def norm_tag(value: object) -> str:
    s = str(value or "").strip().upper()
    if not s or s == "NAN":
        return ""
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"XV-", "XS-", s)
    # GT uses short line ids: 35-24-192 not 35-24-192-PP-200-E10H2A
    m = re.match(r"^(\d{2}-\d{2}-\d{2,4})(?:-[A-Z].*)?$", s)
    if m:
        return m.group(1)
    return s


def load_gt_rows(path: Path) -> List[Dict[str, str]]:
    path = Path(path)
    if path.suffix.lower() in {".xlsx", ".xlsm", ".xls"}:
        import pandas as pd

        df = pd.read_excel(path)
        rows: List[Dict[str, str]] = []
        for _, raw in df.iterrows():
            row = {}
            for c in GT_COLUMNS:
                # MASK column may be named "MASK (max 30)" in the full workbook.
                if c == "MASK" and c not in df.columns:
                    src = next((col for col in df.columns if str(col).upper().startswith("MASK")), None)
                else:
                    src = c if c in df.columns else None
                val = raw.get(src) if src else ""
                if val is None or (isinstance(val, float) and str(val) == "nan"):
                    val = ""
                row[c] = str(val).strip()
                if row[c].lower() == "nan":
                    row[c] = ""
            rows.append(row)
        return rows

    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for raw in reader:
            rows.append({c: str(raw.get(c) or "").strip() for c in GT_COLUMNS})
        return rows


def function_child_sets(rows: Iterable[Dict[str, str]]) -> Dict[str, Dict[str, Set[str]]]:
    """
    Map FUNCTION tag -> {equipment: set, subequipment: set, all: set}.
    Header-only rows (function set, children empty) create the bucket.
    Child rows inherit the current function.
    """
    out: Dict[str, Dict[str, Set[str]]] = {}
    current: Optional[str] = None
    for row in rows:
        fn = norm_tag(row.get("FUNCTION"))
        eq = norm_tag(row.get("EQUIPMENT"))
        sub = norm_tag(row.get("SUB-EQUIPMENT"))
        if fn:
            current = fn
            out.setdefault(current, {"equipment": set(), "subequipment": set(), "all": set()})
        if not current:
            continue
        bucket = out.setdefault(current, {"equipment": set(), "subequipment": set(), "all": set()})
        if eq and eq != current:
            bucket["equipment"].add(eq)
            bucket["all"].add(eq)
        if eq and eq == current:
            bucket["all"].add(eq)
        if sub:
            bucket["subequipment"].add(sub)
            bucket["all"].add(sub)
    return out


def f1(pred: Set[str], gold: Set[str]) -> Dict[str, float]:
    if not pred and not gold:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "tp": 0, "fp": 0, "fn": 0}
    tp = len(pred & gold)
    fp = len(pred - gold)
    fn = len(gold - pred)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    score = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": score,
        "tp": float(tp),
        "fp": float(fp),
        "fn": float(fn),
    }


def compare_level(pred: Set[str], gold: Set[str]) -> Dict[str, Any]:
    """Hit / miss / extra for one hierarchy level (equipment or sub-equipment)."""
    hits = sorted(pred & gold)
    misses = sorted(gold - pred)  # in GT, missing from our result
    extras = sorted(pred - gold)  # in ours, not in GT
    scores = f1(pred, gold)
    gt_count = len(gold)
    hit_count = len(hits)
    # Hit-rate vs GT only (extras do not affect accuracy).
    accuracy = (hit_count / gt_count) if gt_count else None
    return {
        "gt_count": gt_count,
        "pred_count": len(pred),
        "hit_count": hit_count,
        "miss_count": len(misses),
        "extra_count": len(extras),
        "hits": hits,
        "misses": misses,
        "extras": extras,
        "accuracy": accuracy,
        **scores,
    }


def macro_hit_accuracy(scores: Iterable[Dict[str, Any]], level: str) -> float:
    """Average per-FUNCTION hit/gt accuracy (skips levels with no GT children)."""
    vals = []
    for s in scores:
        if "error" in s:
            continue
        block = s.get(level) or {}
        acc = block.get("accuracy")
        if acc is None:
            continue
        vals.append(float(acc))
    return sum(vals) / len(vals) if vals else 0.0



def score_function(
    function: str,
    pred_rows: List[Dict[str, str]],
    gt_rows: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Per-FUNCTION equipment + sub-equipment hit/miss vs GT."""
    fn = norm_tag(function)
    gold = function_child_sets(gt_rows).get(fn, {"equipment": set(), "subequipment": set(), "all": set()})
    pred = function_child_sets(pred_rows).get(fn, {"equipment": set(), "subequipment": set(), "all": set()})
    equipment = compare_level(pred["equipment"], gold["equipment"])
    subequipment = compare_level(pred["subequipment"], gold["subequipment"])
    return {
        "function": fn,
        "in_gt": fn in function_child_sets(gt_rows),
        "equipment": equipment,
        "subequipment": subequipment,
        "tag_f1": f1(pred["all"], gold["all"]),
    }


def evaluate(pred_rows: List[Dict[str, str]], gt_rows: List[Dict[str, str]]) -> Dict[str, Any]:
    gold = function_child_sets(gt_rows)
    pred = function_child_sets(pred_rows)

    per_function = {}
    micros = {"tp": 0, "fp": 0, "fn": 0}
    eq_micro = {"tp": 0, "fp": 0, "fn": 0}
    sub_micro = {"tp": 0, "fp": 0, "fn": 0}

    for fn, g in gold.items():
        p = pred.get(fn, {"equipment": set(), "subequipment": set(), "all": set()})
        tag_scores = f1(p["all"], g["all"])
        eq = compare_level(p["equipment"], g["equipment"])
        sub = compare_level(p["subequipment"], g["subequipment"])
        place_tp = eq["hit_count"] + sub["hit_count"]
        place_fp = eq["extra_count"] + sub["extra_count"]
        place_fn = eq["miss_count"] + sub["miss_count"]
        place_p = place_tp / (place_tp + place_fp) if (place_tp + place_fp) else 0.0
        place_r = place_tp / (place_tp + place_fn) if (place_tp + place_fn) else 0.0
        place_f1 = (2 * place_p * place_r / (place_p + place_r)) if (place_p + place_r) else 0.0
        per_function[fn] = {
            "tag_f1": tag_scores,
            "equipment": eq,
            "subequipment": sub,
            "equipment_f1": {k: eq[k] for k in ("precision", "recall", "f1", "tp", "fp", "fn")},
            "subequipment_f1": {k: sub[k] for k in ("precision", "recall", "f1", "tp", "fp", "fn")},
            "placement_f1": place_f1,
            "pred_tags": sorted(p["all"]),
            "gold_tags": sorted(g["all"]),
            "missing": sorted(g["all"] - p["all"]),
            "extra": sorted(p["all"] - g["all"]),
        }
        micros["tp"] += int(tag_scores["tp"])
        micros["fp"] += int(tag_scores["fp"])
        micros["fn"] += int(tag_scores["fn"])
        eq_micro["tp"] += eq["hit_count"]
        eq_micro["fp"] += eq["extra_count"]
        eq_micro["fn"] += eq["miss_count"]
        sub_micro["tp"] += sub["hit_count"]
        sub_micro["fp"] += sub["extra_count"]
        sub_micro["fn"] += sub["miss_count"]

    def _prf(m: Dict[str, int]) -> Dict[str, float]:
        p = m["tp"] / (m["tp"] + m["fp"]) if (m["tp"] + m["fp"]) else 0.0
        r = m["tp"] / (m["tp"] + m["fn"]) if (m["tp"] + m["fn"]) else 0.0
        f = (2 * p * r / (p + r)) if (p + r) else 0.0
        return {"precision": p, "recall": r, "f1": f, **m}

    micro_p = micros["tp"] / (micros["tp"] + micros["fp"]) if (micros["tp"] + micros["fp"]) else 0.0
    micro_r = micros["tp"] / (micros["tp"] + micros["fn"]) if (micros["tp"] + micros["fn"]) else 0.0
    micro_f1 = (2 * micro_p * micro_r / (micro_p + micro_r)) if (micro_p + micro_r) else 0.0
    macro_f1 = (
        sum(v["tag_f1"]["f1"] for v in per_function.values()) / len(per_function) if per_function else 0.0
    )
    return {
        "accuracy": micro_f1,
        "micro_tag_f1": micro_f1,
        "macro_tag_f1": macro_f1,
        "micro": {"precision": micro_p, "recall": micro_r, **micros},
        "equipment_micro": _prf(eq_micro),
        "subequipment_micro": _prf(sub_micro),
        "per_function": per_function,
        "pred_functions": sorted(pred.keys()),
        "gold_functions": sorted(gold.keys()),
    }


def format_function_report(score: Dict[str, Any]) -> str:
    """Human-readable per-function hit/miss block."""
    fn = score["function"]
    lines = [f"=== {fn} ==="]
    if not score.get("in_gt"):
        lines.append("  (not present as FUNCTION in GT)")
    for level in ("equipment", "subequipment"):
        block = score[level]
        label = "EQUIPMENT" if level == "equipment" else "SUB-EQUIPMENT"
        acc = block.get("accuracy")
        acc_s = f"{acc*100:.1f}%" if acc is not None else "n/a"
        lines.append(
            f"  {label}: hit={block['hit_count']}/{block['gt_count']}  "
            f"miss={block['miss_count']}  extra={block['extra_count']}  "
            f"acc={acc_s}"
        )
        if block["hits"]:
            lines.append(f"    hits:   {', '.join(block['hits'])}")
        if block["misses"]:
            lines.append(f"    misses: {', '.join(block['misses'])}")
        if block["extras"]:
            lines.append(f"    extras: {', '.join(block['extras'])}")
    return "\n".join(lines)


def rows_from_hierarchy_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for raw in reader:
            rows.append({c: str(raw.get(c) or "").strip() for c in GT_COLUMNS})
        return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Score hierarchy output vs GT")
    parser.add_argument("--gt", default="resources/gt_hierarchy_broke_system.xlsx")
    parser.add_argument("--pred", required=True, help="Predicted hierarchy CSV (GT columns)")
    parser.add_argument("--json-out", default="")
    parser.add_argument(
        "--function",
        default="",
        help="If set, print hit/miss detail for this FUNCTION only",
    )
    args = parser.parse_args()

    gt_rows = load_gt_rows(Path(args.gt))
    pred_rows = rows_from_hierarchy_csv(Path(args.pred))

    if args.function:
        score = score_function(args.function, pred_rows, gt_rows)
        print(format_function_report(score))
        print(json.dumps(score, indent=2))
        return 0

    report = evaluate(pred_rows, gt_rows)
    print(json.dumps(report, indent=2))
    print(f"\nPRIMARY accuracy (micro tag F1): {report['accuracy']*100:.1f}%")
    print(
        f"EQUIPMENT micro F1: {report['equipment_micro']['f1']*100:.1f}%  "
        f"(hit={report['equipment_micro']['tp']} miss={report['equipment_micro']['fn']} "
        f"extra={report['equipment_micro']['fp']})"
    )
    print(
        f"SUB-EQUIPMENT micro F1: {report['subequipment_micro']['f1']*100:.1f}%  "
        f"(hit={report['subequipment_micro']['tp']} miss={report['subequipment_micro']['fn']} "
        f"extra={report['subequipment_micro']['fp']})"
    )
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0 if report["accuracy"] >= 0.60 else 1


if __name__ == "__main__":
    raise SystemExit(main())
