#!/usr/bin/env python3
"""
Orchestrate hierarchy building over inventory FUNCTIONs, one by one.

Flow:
  1. Load tags from pid_inventory.json ``functions`` (all kinds by default)
  2. Take the first ``--limit`` tags (default 10; 0 = all)
  3. For each tag: run viewer+Bedrock hierarchy, then compare to GT
     - EQUIPMENT: hits / misses (in GT, not in ours) / extras
     - SUB-EQUIPMENT: same
  4. Write combined hierarchy CSV + per-function score report
"""

from __future__ import annotations
import dwg_warn  # noqa: F401 — silence boto3 Python 3.9 deprecation noise (subprocesses too via env)

import argparse
import concurrent.futures
import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dwg_pure_dump import find_json, json_path, logs_dir, safe_name, write_json
from eval_hierarchy_gt import (
    GT_COLUMNS,
    format_function_report,
    load_gt_rows,
    macro_hit_accuracy,
    score_function,
)

# Hierarchy deliverable may include DESCRIPTION for FLOC PLTXT.
HIERARCHY_COLUMNS = list(GT_COLUMNS)
if "DESCRIPTION" not in HIERARCHY_COLUMNS:
    HIERARCHY_COLUMNS = HIERARCHY_COLUMNS + ["DESCRIPTION"]
if "MASK" not in HIERARCHY_COLUMNS:
    HIERARCHY_COLUMNS = HIERARCHY_COLUMNS + ["MASK"]


def load_inventory_functions(path: Path, kinds: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("functions") or []
    if kinds:
        want = {k.lower() for k in kinds}
        rows = [r for r in rows if str(r.get("kind") or "").lower() in want]
    # Keep inventory order; drop duplicate tags (first kind wins).
    out: List[Dict[str, Any]] = []
    seen = set()
    for r in rows:
        tag = str(r.get("function") or "").strip().upper().replace(" ", "")
        if not tag or tag in seen:
            continue
        seen.add(tag)
        row = dict(r)
        row["function"] = tag
        out.append(row)
    return out


def csv_function_headers(rows: List[Dict[str, str]]) -> List[str]:
    out: List[str] = []
    seen = set()
    for row in rows:
        fn = str(row.get("FUNCTION") or "").strip().upper().replace(" ", "")
        eq = str(row.get("EQUIPMENT") or "").strip()
        sub = str(row.get("SUB-EQUIPMENT") or "").strip()
        if fn and not eq and not sub and fn not in seen:
            seen.add(fn)
            out.append(fn)
    return out


def rows_for_function(rows: List[Dict[str, str]], tag: str) -> List[Dict[str, str]]:
    """Keep only the requested FUNCTION header + its inherited children."""
    want = str(tag or "").strip().upper().replace(" ", "")
    out: List[Dict[str, str]] = []
    current = False
    for row in rows:
        fn = str(row.get("FUNCTION") or "").strip().upper().replace(" ", "")
        eq = str(row.get("EQUIPMENT") or "").strip()
        sub = str(row.get("SUB-EQUIPMENT") or "").strip()
        if fn and not eq and not sub:
            current = fn == want
        if current:
            out.append(row)
    return out


def write_hierarchy_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = HIERARCHY_COLUMNS
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in cols})


def read_hierarchy_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return [{c: str(raw.get(c) or "").strip() for c in raw.keys()} for raw in csv.DictReader(f)]


def _append_orphan_valve_rows(
    combined_csv: Path,
    structural_path: Path,
    inv_path: Path,
) -> int:
    """
    Find P-VALVEPOS valve position tags absent from the hierarchy and insert
    them as EQUIPMENT rows under their nearest function by Euclidean distance.

    Returns the count of orphan rows appended.

    Context: in some DWGs (e.g. steam/condensate supply headers) valve tags
    exist on P-VALVEPOS but have no nearby FUNCTION equipment node — they fall
    between the coverage windows of neighbouring functions and are never
    captured by the AI hierarchy step.  This mop-up prevents them from being
    silently dropped before valve classification and SAP export.
    """
    import math
    import re

    VALVE_POS_RE = re.compile(r"^\d{2}-\d{2}-\d{3,4}$")

    if not structural_path.exists():
        print(f"[orphan-mopup] structural dump not found: {structural_path}; skipping")
        return 0

    existing = read_hierarchy_csv(combined_csv)
    if not existing:
        return 0

    # Tags already present anywhere in the hierarchy (function, equipment, sub-equipment).
    in_hierarchy: set = set()
    for row in existing:
        for col in ("FUNCTION", "EQUIPMENT", "SUB-EQUIPMENT"):
            v = (row.get(col) or "").strip().upper()
            if v:
                in_hierarchy.add(v)

    # P-VALVEPOS valve position number texts from structural dump.
    structural = json.loads(structural_path.read_text(encoding="utf-8"))
    valve_locs: Dict[str, Any] = {}  # tag -> (x, y), first occurrence wins
    for t in structural.get("text_entities", []):
        if t.get("layer") != "P-VALVEPOS":
            continue
        txt = (t.get("text") or "").strip().upper()
        if not VALVE_POS_RE.match(txt):
            continue
        pos = t.get("position") or []
        if len(pos) >= 2 and pos[0] is not None and txt not in valve_locs:
            valve_locs[txt] = (float(pos[0]), float(pos[1]))

    orphans = {tag: xy for tag, xy in valve_locs.items() if tag not in in_hierarchy}
    if not orphans:
        print("[orphan-mopup] no orphan valve tags found")
        return 0

    print(f"[orphan-mopup] {len(orphans)} orphan valve tags to assign")

    # Function positions from inventory (only those already in the hierarchy CSV).
    existing_fn_headers: set = {
        row.get("FUNCTION", "").strip().upper()
        for row in existing
        if row.get("FUNCTION") and not row.get("EQUIPMENT") and not row.get("SUB-EQUIPMENT")
    }
    inventory = json.loads(inv_path.read_text(encoding="utf-8"))
    fn_locs: Dict[str, Any] = {}
    for fn in inventory.get("functions") or []:
        tag = str(fn.get("function") or "").strip().upper()
        x, y = fn.get("x"), fn.get("y")
        if tag in existing_fn_headers and x is not None and y is not None:
            fn_locs[tag] = (float(x), float(y))

    if not fn_locs:
        print("[orphan-mopup] no function positions available; skipping")
        return 0

    # Group functions by sub-process prefix (e.g. "35-27") for prefix-aware matching.
    fn_by_prefix: Dict[str, Dict[str, Any]] = {}
    for fn, xy in fn_locs.items():
        pfx = fn[:5]
        fn_by_prefix.setdefault(pfx, {})[fn] = xy

    def _nearest(candidates: Dict[str, Any], ox: float, oy: float):
        return min(
            ((fn, math.hypot(ox - fx, oy - fy)) for fn, (fx, fy) in candidates.items()),
            key=lambda t: t[1],
        )

    # Assign each orphan to its nearest SAME-prefix function; fall back to nearest overall.
    fn_orphans: Dict[str, List[str]] = {}
    for tag, (ox, oy) in sorted(orphans.items()):
        valve_pfx = tag[:5]
        same_prefix_fns = fn_by_prefix.get(valve_pfx, {})
        if same_prefix_fns:
            best_fn, best_d = _nearest(same_prefix_fns, ox, oy)
        else:
            best_fn, best_d = _nearest(fn_locs, ox, oy)
        fn_orphans.setdefault(best_fn, []).append(tag)
        print(f"[orphan-mopup]   {tag} → {best_fn} (d={best_d:.0f})")

    for fn in fn_orphans:
        fn_orphans[fn].sort()

    def _orphan_row(tag: str) -> Dict[str, str]:
        return {
            "SUB-PROCESS": "",
            "FUNCTION": "",
            "EQUIPMENT": tag,
            "SUB-EQUIPMENT": "",
            "MASK": "",
            "DESCRIPTION": f"{tag} VLV",
        }

    # Insert orphan rows after each function's last child row.
    result: List[Dict[str, str]] = []
    pending_orphans: List[str] = []

    for row in existing:
        fn = (row.get("FUNCTION") or "").strip().upper()
        eq = (row.get("EQUIPMENT") or "").strip()
        sub = (row.get("SUB-EQUIPMENT") or "").strip()
        is_fn_header = bool(fn) and not eq and not sub

        if is_fn_header:
            # Flush orphans for the function we are leaving, then move to new one.
            for t in pending_orphans:
                result.append(_orphan_row(t))
            pending_orphans = fn_orphans.get(fn, [])

        result.append(row)

    # Flush orphans that belong to the last function in the file.
    for t in pending_orphans:
        result.append(_orphan_row(t))

    count = sum(len(v) for v in fn_orphans.values())
    write_hierarchy_csv(combined_csv, result)
    print(f"[orphan-mopup] appended {count} orphan valve rows → {combined_csv.name}")
    return count


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
    aws_profile: str,
) -> int:
    cmd = [
        sys.executable,
        str(Path(__file__).resolve().parent / "dwg_pid_hierarchy_ai.py"),
        "--input",
        str(input_path),
        "--output-dir",
        str(out_dir),
        "--tags",
        tag,
        "--model-id",
        model_id,
        "--region",
        region,
        "--prompt-file",
        prompt_file,
        "--inventory-json",
        str(inventory_json),
        "--hierarchy-csv-out",
        str(per_tag_csv),
        "--hierarchy-json-out",
        str(per_tag_json),
    ]
    if reuse_shots:
        cmd.append("--reuse-shots")
    if no_clean_prev:
        cmd.append("--no-clean-prev")

    env = os.environ.copy()
    if aws_profile:
        env["AWS_PROFILE"] = aws_profile
    print(f"\n---------- hierarchy: {tag} ----------")
    print(" ".join(cmd))
    proc = subprocess.run(cmd, env=env)
    return int(proc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run hierarchy one-by-one over inventory equipment and score vs GT"
    )
    parser.add_argument("--input", default="inputs/Broke System.dwg")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument(
        "--inventory-json",
        default="",
        help="pid_inventory.json (default: outputs/jsons/<stem>.pid_inventory.json)",
    )
    parser.add_argument(
        "--gt",
        default="inputs/gt_hierarchy_broke_system.xlsx",
        help="GT hierarchy workbook/CSV for hit-miss scoring",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max number of inventory FUNCTIONs to process (default: 10; 0 = all)",
    )
    parser.add_argument(
        "--kinds",
        default="",
        help="Comma-separated function kinds (equipment,instrument,line). Empty = all inventory FUNCTIONs",
    )
    parser.add_argument(
        "--tags",
        default="",
        help="Optional explicit comma-separated tags (overrides inventory selection)",
    )
    parser.add_argument("--model-id", default="eu.anthropic.claude-sonnet-4-6")
    parser.add_argument("--region", default="eu-west-2")
    parser.add_argument("--prompt-file", default="pid_hierarchy_gt_v8.md")
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Parallel FUNCTION workers (default: 1).",
    )
    parser.add_argument("--aws-profile", default=os.environ.get("AWS_PROFILE", "foundrydev"))
    parser.add_argument(
        "--reuse-shots",
        action="store_true",
        help="Reuse existing viewer PNGs when present",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only list selected equipment + GT child counts; do not call Bedrock",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip FUNCTIONs already present as headers in hierarchy_orchestrator.csv",
    )
    parser.add_argument(
        "--score-only",
        action="store_true",
        help="Skip Bedrock; score existing hierarchy_orchestrator.csv for the selected tags",
    )
    parser.add_argument(
        "--no-export-floc",
        action="store_true",
        help="Skip SAP Functional Location workbook export at the end",
    )
    parser.add_argument(
        "--no-export-equipment",
        action="store_true",
        help="Skip SAP Equipment workbook export at the end",
    )
    parser.add_argument(
        "--no-valve-classify",
        action="store_true",
        help="Skip per-tag tight-crop valve classification before SAP export",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = logs_dir(out_dir)
    base = safe_name(input_path)

    inv_path = (
        Path(args.inventory_json).expanduser().resolve()
        if args.inventory_json
        else find_json(out_dir, f"{base}.pid_inventory.json")
    )
    if not inv_path.exists():
        print(f"[error] Missing inventory JSON: {inv_path}. Run `make inventory` first.", file=sys.stderr)
        return 2

    gt_path = Path(args.gt).expanduser().resolve()
    if not gt_path.exists():
        print(f"[error] Missing GT file: {gt_path}", file=sys.stderr)
        return 2
    gt_rows = load_gt_rows(gt_path)

    if args.tags.strip():
        tags = [t.strip().upper() for t in args.tags.split(",") if t.strip()]
        selected = [{"function": t, "kind": "explicit"} for t in tags]
    else:
        kinds = [k.strip() for k in args.kinds.split(",") if k.strip() and k.strip().lower() != "all"]
        selected = load_inventory_functions(inv_path, kinds=kinds or None)
        if args.limit > 0:
            selected = selected[: args.limit]
        tags = [str(r.get("function") or "").upper() for r in selected if r.get("function")]

    if not tags:
        print("[error] No inventory FUNCTIONs selected.", file=sys.stderr)
        return 2

    all_tags = list(tags)

    combined_csv = out_dir / f"{base}.hierarchy_orchestrator.csv"
    report_json = json_path(out_dir, f"{base}.hierarchy_orchestrator_report.json")
    log_path = log_dir / "hierarchy-orchestrator.log"
    parts_dir = out_dir / "jsons" / "_orchestrator_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)

    combined_rows: List[Dict[str, str]] = []
    per_function_scores: List[Dict[str, Any]] = []

    if args.skip_existing and combined_csv.exists() and not args.score_only:
        existing_headers = set(csv_function_headers(read_hierarchy_csv(combined_csv)))
        before = len(tags)
        tags = [t for t in tags if t not in existing_headers]
        print(f"[skip-existing] {before - len(tags)} already in {combined_csv.name}; {len(tags)} remaining")
        combined_rows = read_hierarchy_csv(combined_csv)

    print(f"Selected {len(all_tags)} FUNCTION(s) from {inv_path.name} ({len(tags)} to run)")
    for i, t in enumerate(tags, 1):
        print(f"  {i:2d}. {t}")

    if args.dry_run:
        print("\n[dry-run] GT child counts:")
        for tag in all_tags:
            score = score_function(tag, [], gt_rows)
            eq = score["equipment"]
            sub = score["subequipment"]
            print(
                f"  {tag}: in_gt={score['in_gt']}  "
                f"EQUIPMENT gt={eq['gt_count']}  SUB-EQUIPMENT gt={sub['gt_count']}"
            )
        return 0

    if args.score_only:
        existing = read_hierarchy_csv(combined_csv)
        if not existing:
            print(f"[error] --score-only but missing {combined_csv}", file=sys.stderr)
            return 2
        combined_rows = existing
        print(f"[score-only] scoring {combined_csv}", flush=True)
    else:
        jobs = max(1, int(args.jobs or 1))
        if jobs > 1:
            print(f"[parallel] running up to {jobs} FUNCTIONs concurrently")
        tag_results: Dict[str, Dict[str, Any]] = {}

        def _run_one(tag: str, index: int) -> Dict[str, Any]:
            tag_csv = parts_dir / f"{tag}.hierarchy.csv"
            tag_json = parts_dir / f"{tag}.hierarchy_ai.json"
            rc = run_hierarchy_for_tag(
                tag=tag,
                input_path=input_path,
                out_dir=out_dir,
                model_id=args.model_id,
                region=args.region,
                prompt_file=args.prompt_file,
                inventory_json=inv_path,
                per_tag_csv=tag_csv,
                per_tag_json=tag_json,
                reuse_shots=args.reuse_shots,
                # Parallel workers must never clear shared outputs.
                no_clean_prev=True if jobs > 1 else (index > 0) or args.reuse_shots or bool(combined_rows),
                aws_profile=args.aws_profile,
            )
            rows = rows_for_function(read_hierarchy_csv(tag_csv), tag)
            return {"function": tag, "exit_code": rc, "rows": rows}

        if jobs == 1:
            for idx, tag in enumerate(tags):
                result = _run_one(tag, idx)
                tag_results[tag] = result
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
                fut_to_tag = {
                    pool.submit(_run_one, tag, idx): tag
                    for idx, tag in enumerate(tags)
                }
                # Workers run in parallel; this loop is single-threaded —
                # merge and CSV writes happen sequentially as futures complete.
                for fut in concurrent.futures.as_completed(fut_to_tag):
                    tag = fut_to_tag[fut]
                    try:
                        tag_results[tag] = fut.result()
                    except Exception as exc:
                        print(f"[error] {tag}: {exc}", file=sys.stderr, flush=True)
                        tag_results[tag] = {"function": tag, "exit_code": 99, "rows": [], "error": str(exc)}
                    r = tag_results[tag]
                    print(
                        f"[done] {tag} exit={r.get('exit_code')} rows={len(r.get('rows') or [])}",
                        flush=True,
                    )

        # Merge in original inventory/tag order for deterministic output.
        for tag in tags:
            result = tag_results.get(tag) or {"function": tag, "exit_code": 99, "rows": []}
            rc = int(result.get("exit_code", 99))
            tag_rows = result.get("rows") or []
            if not tag_rows:
                print(f"[warn] no rows for {tag} (exit={rc}); not appending stale CSV")
                per_function_scores.append(
                    {
                        "function": tag,
                        "error": f"no_rows_exit_{rc}",
                        "in_gt": False,
                        "equipment": {},
                        "subequipment": {},
                    }
                )
                continue
            combined_rows.extend(tag_rows)
            write_hierarchy_csv(combined_csv, combined_rows)
            score = score_function(tag, tag_rows, gt_rows)
            per_function_scores.append(score)
            print(format_function_report(score))

    # Final scores always cover the full selected set from the combined CSV.
    combined_rows = read_hierarchy_csv(combined_csv) if combined_csv.exists() else combined_rows
    per_function_scores = [score_function(tag, combined_rows, gt_rows) for tag in all_tags]
    for score in per_function_scores:
        print(format_function_report(score))

    # Aggregate over selected functions only.
    # Accuracy = hit/gt per FUNCTION, then mean (extras ignored).
    eq_hit = eq_miss = eq_extra = eq_gt = 0
    sub_hit = sub_miss = sub_extra = sub_gt = 0
    for s in per_function_scores:
        if "error" in s:
            continue
        eq = s["equipment"]
        sub = s["subequipment"]
        eq_hit += eq["hit_count"]
        eq_miss += eq["miss_count"]
        eq_extra += eq["extra_count"]
        eq_gt += eq["gt_count"]
        sub_hit += sub["hit_count"]
        sub_miss += sub["miss_count"]
        sub_extra += sub["extra_count"]
        sub_gt += sub["gt_count"]

    eq_acc = macro_hit_accuracy(per_function_scores, "equipment")
    sub_acc = macro_hit_accuracy(per_function_scores, "subequipment")

    summary = {
        "tags": all_tags,
        "limit": args.limit,
        "model_id": args.model_id,
        "prompt_file": args.prompt_file,
        "gt": str(gt_path),
        "inventory": str(inv_path),
        "pred_csv": str(combined_csv),
        "accuracy_definition": "per_function hit/gt, then mean (extras ignored)",
        "equipment": {
            "gt_count": eq_gt,
            "hit": eq_hit,
            "miss": eq_miss,
            "extra": eq_extra,
            "accuracy": eq_acc,
        },
        "subequipment": {
            "gt_count": sub_gt,
            "hit": sub_hit,
            "miss": sub_miss,
            "extra": sub_extra,
            "accuracy": sub_acc,
        },
        "per_function": per_function_scores,
    }
    write_json(report_json, summary)

    print("\n========== ORCHESTRATOR SUMMARY ==========")
    print(f"functions scored: {len(all_tags)}")
    print(
        f"EQUIPMENT:     hit={eq_hit}/{eq_gt}  miss={eq_miss}  extra={eq_extra}  "
        f"acc={eq_acc*100:.1f}% (mean of per-function hit/gt)"
    )
    print(
        f"SUB-EQUIPMENT: hit={sub_hit}/{sub_gt}  miss={sub_miss}  extra={sub_extra}  "
        f"acc={sub_acc*100:.1f}% (mean of per-function hit/gt)"
    )
    print(f"report: {report_json}")
    print(f"combined CSV: {combined_csv}")
    log_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Mop up valve position tags that the AI hierarchy step missed (e.g. valves
    # on steam/condensate supply headers with no nearby FUNCTION equipment node).
    if combined_csv.exists() and combined_csv.stat().st_size > 0:
        structural_path = json_path(out_dir, f"{base}.structural_dump.json")
        _append_orphan_valve_rows(combined_csv, structural_path, inv_path)

    if combined_csv.exists() and combined_csv.stat().st_size > 0:
        limit_s = str(args.limit if args.limit > 0 else 0)
        if not args.no_valve_classify:
            valve_cmd = [
                sys.executable,
                "-u",
                str(Path(__file__).resolve().parent / "dwg_valve_classify.py"),
                "--input",
                str(input_path),
                "--output-dir",
                str(out_dir),
                "--hierarchy-csv",
                str(combined_csv),
                "--model-id",
                args.model_id,
                "--region",
                args.region,
                "--jobs",
                str(max(1, int(getattr(args, "jobs", 1) or 1))),
            ]
            if args.skip_existing:
                valve_cmd.append("--skip-existing")
            print("\n---------- valve classify (tight crop + legend) ----------")
            print(" ".join(valve_cmd), flush=True)
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            if args.aws_profile:
                env["AWS_PROFILE"] = args.aws_profile
            subprocess.run(valve_cmd, check=False, env=env)

        if not args.no_export_floc:
            floc_cmd = [
                sys.executable,
                str(Path(__file__).resolve().parent / "export_sap_floc.py"),
                "--input",
                str(input_path),
                "--output-dir",
                str(out_dir),
                "--hierarchy-csv",
                str(combined_csv),
                "--gt",
                str(gt_path),
                "--limit",
                limit_s,
            ]
            print("\n---------- export SAP FLOC ----------")
            print(" ".join(floc_cmd))
            subprocess.run(floc_cmd, check=False)

        if not args.no_export_equipment:
            eq_cmd = [
                sys.executable,
                str(Path(__file__).resolve().parent / "export_sap_equipment.py"),
                "--input",
                str(input_path),
                "--output-dir",
                str(out_dir),
                "--hierarchy-csv",
                str(combined_csv),
                "--limit",
                limit_s,
            ]
            print("\n---------- export SAP Equipment ----------")
            print(" ".join(eq_cmd))
            subprocess.run(eq_cmd, check=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
