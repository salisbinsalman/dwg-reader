#!/usr/bin/env python3
"""Run CAD+Vision valve typing on selected tags and print results."""

from __future__ import annotations

import dwg_reader.dwg_warn as dwg_warn  # noqa: F401 — silence boto3 Python 3.9 deprecation noise

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Dict, List

from dwg_reader.dwg_floc_context import infer_valve_type
from dwg_reader.dwg_pure_dump import evidence_dir, find_json, safe_name
from dwg_reader.dwg_valve_classify import (
    apply_wfl_drain_attachment,
    bedrock_classify_crop,
    collect_gor_attribute_tag_locations,
    collect_symb_bowtie_inserts,
    collect_text_locations,
    collect_valve_inserts,
    locate_valve,
    pipe_dn_label_near_tag,
    tight_valve_screenshot,
    valve_ring_frac,
    wfl_drain_line_hint,
)


ALIASES = {
    # User list includes two area-code typos.
    "35-32-1105": "35-24-1105",
    "34-24-215": "35-24-215",
    "168V-390": "168V-390",
}

EXPECTED_TYPES = {
    "35-24-1105": {"NC", "FLS"},
    "35-24-093": {"DRN"},
    "35-24-001": {"HV"},
    "35-24-215": {"NC", "FLS"},
    "35-24-108": {"NC", "FLS"},
    "35-24LV1-560": {"AV"},
    "35-24-137": {"DRN", "NC"},
    "35-24-107": {"DRN", "NC"},
    "35-24-110": {"DRN", "NC"},
    "35-24-230": {"HV"},
    "35-24-105": {"DRN", "NC"},
    "35-24HV-618": {"AV"},
    "35-24-217": {"DRN", "NC"},
    "35-24-121": {"DRN", "NC"},
    "35-24-123": {"DRN", "NC"},
    "35-24-191": {"DRN"},
    "35-24-192": {"DRN"},
    "35-24XV-665": {"DRN"},
    "35-24-198": {"NC", "FLS"},
    "35-24-199": {"NC"},
    "35-24-196": {"HV"},
    "35-27-739": {"HV"},
    "35-27-740": {"CHK"},
    "168V-385": {"HV"},
    "168V-389": {"CHK"},
    "168V-387": {"NC", "DRN"},
    "168V-390": {"GLV"},
}

# Tags that live on a drawing other than the default --input (Broke System).
TAG_INPUT = {
    "35-27-739": "inputs/RAU8F00290.10_Steam and Condensate.dwg",
    "35-27-740": "inputs/RAU8F00290.10_Steam and Condensate.dwg",
    "168V-385": "inputs/GORB18779.05_SH5(12)_Code 14 - P&ID Ventil Unit WU05_SWE Shotton_CE.dwg",
    "168V-389": "inputs/GORB18779.05_SH5(12)_Code 14 - P&ID Ventil Unit WU05_SWE Shotton_CE.dwg",
    "168V-387": "inputs/GORB18779.05_SH5(12)_Code 14 - P&ID Ventil Unit WU05_SWE Shotton_CE.dwg",
    "168V-390": "inputs/GORB18779.05_SH5(12)_Code 14 - P&ID Ventil Unit WU05_SWE Shotton_CE.dwg",
}

DEFAULT_TAGS = (
    "35-32-1105,35-24-093,35-24-001,34-24-215,35-24-108,35-24LV1-560,35-24-137,"
    "35-24-107,35-24-110,35-24-230,35-24-105,35-24HV-618,35-24-217,35-24-121,35-24-123,"
    "35-24-191,35-24-192,35-24XV-665,35-24-198,35-24-199,35-24-196,"
    "35-27-739,35-27-740,"
    "168V-385,168V-389,168V-387,168V-390"
)


def _norm(tag: str) -> str:
    t = "".join(str(tag or "").upper().split())
    return ALIASES.get(t, t)


def _print_table(headers: List[str], table_rows: List[List[str]]) -> None:
    """Print a simple aligned text table."""
    widths = [len(h) for h in headers]
    for row in table_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def _fmt_row(cells: List[str]) -> str:
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    print(_fmt_row(headers))
    print("  ".join("-" * w for w in widths))
    for row in table_rows:
        print(_fmt_row(row))


def load_hierarchy_rows(path: Path) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    current_fn = ""
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            fn = str(row.get("FUNCTION") or "").strip().upper().replace(" ", "")
            eq = str(row.get("EQUIPMENT") or "").strip().upper().replace(" ", "")
            sub = str(row.get("SUB-EQUIPMENT") or "").strip().upper().replace(" ", "")
            desc = str(row.get("DESCRIPTION") or "").strip()
            if fn and not eq and not sub:
                current_fn = fn
                continue
            tag = eq or sub
            if tag:
                out[tag] = {"fn": current_fn, "description": desc}
    return out


def _input_for_tag(tag: str, default_input: str) -> str:
    return TAG_INPUT.get(tag, default_input)


def _group_tags_by_input(tags: List[str], default_input: str) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {}
    for tag in tags:
        inp = _input_for_tag(tag, default_input)
        groups.setdefault(inp, []).append(tag)
    return groups


def _load_drawing_context(input_path: Path, out_dir: Path, hierarchy_csv: str) -> Dict[str, object]:
    base = safe_name(input_path)
    hier_path = (
        Path(hierarchy_csv).expanduser().resolve()
        if hierarchy_csv
        else out_dir / f"{base}.hierarchy_orchestrator.csv"
    )
    struct_path = find_json(out_dir, f"{base}.structural_dump.json")
    if not struct_path.exists():
        raise SystemExit(f"Missing structural dump: {struct_path}")
    structural = json.loads(struct_path.read_text(encoding="utf-8"))
    inv_path = find_json(out_dir, f"{base}.pid_inventory.json")
    inventory = json.loads(inv_path.read_text(encoding="utf-8")) if inv_path.exists() else {}
    text_locations = collect_text_locations(structural)
    text_locations.update(collect_gor_attribute_tag_locations(structural))
    return {
        "input_path": input_path,
        "hierarchy": load_hierarchy_rows(hier_path) if hier_path.exists() else {},
        "structural": structural,
        "inventory": inventory,
        "text_locations": text_locations,
        "valve_inserts": collect_valve_inserts(structural),
        "symb_inserts": collect_symb_bowtie_inserts(structural),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe valve types from CAD+Vision for selected tags")
    parser.add_argument("--input", default="inputs/Broke System.dwg")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--hierarchy-csv", default="")
    parser.add_argument("--legend", default="standards/legend.png")
    parser.add_argument("--model-id", default="eu.anthropic.claude-sonnet-4-6")
    parser.add_argument("--region", default="eu-west-2")
    parser.add_argument("--aws-profile", default="foundrydev")
    parser.add_argument(
        "--tags",
        default=DEFAULT_TAGS,
        help="Comma-separated tags to test",
    )
    parser.add_argument("--crop-half", type=float, default=42.0)
    parser.add_argument("--extra-below", type=float, default=60.0)
    parser.add_argument("--skip-vision", action="store_true")
    args = parser.parse_args()
    os.environ["AWS_PROFILE"] = str(args.aws_profile or "foundrydev")

    out_dir = Path(args.output_dir).expanduser().resolve()
    default_input = str(Path(args.input).expanduser().resolve())
    legend_path = Path(args.legend).expanduser().resolve()
    tags = [_norm(t) for t in args.tags.split(",") if t.strip()]
    tag_groups = _group_tags_by_input(tags, default_input)
    rows: List[Dict[str, str]] = []

    crop_dir = evidence_dir(out_dir) / "_valve_crops"
    crop_dir.mkdir(parents=True, exist_ok=True)
    cx_frac, cy_frac = valve_ring_frac(float(args.crop_half), float(args.extra_below))

    if not args.skip_vision:
        from dwg_reader.dwg_pid_hierarchy_ai import load_drawing
    else:
        load_drawing = None  # type: ignore[assignment,misc]

    for input_name, group_tags in tag_groups.items():
        ctx = _load_drawing_context(Path(input_name), out_dir, args.hierarchy_csv)
        hierarchy = ctx["hierarchy"]
        structural = ctx["structural"]
        inventory = ctx["inventory"]
        text_locations = ctx["text_locations"]
        valve_inserts = ctx["valve_inserts"]
        symb_inserts = ctx["symb_inserts"]
        doc = load_drawing(ctx["input_path"]) if load_drawing is not None else None
        if len(tag_groups) > 1:
            print(f"\n--- {Path(input_name).name} ({len(group_tags)} tags) ---", flush=True)

        for tag in group_tags:
            meta = hierarchy.get(tag) or {"fn": "", "description": ""}
            desc = meta.get("description") or ""
            fn = meta.get("fn") or ""
            loc = locate_valve(
                tag,
                text_locations=text_locations,
                valve_inserts=valve_inserts,
                symb_inserts=symb_inserts,
                wfl_drain_hint=wfl_drain_line_hint(tag, inventory),
            )
            cad_type = infer_valve_type(tag, desc) if desc else ""
            vision_type = ""
            crop_file = ""
            vision_error = ""
            if loc and doc is not None:
                crop_path = crop_dir / f"{tag}.png"
                rendered = tight_valve_screenshot(
                    doc,
                    float(loc["x"]),
                    float(loc["y"]),
                    crop_path,
                    half=float(args.crop_half),
                    extra_below=float(args.extra_below),
                )
                if rendered:
                    crop_file = str(rendered)
                    if not args.skip_vision:
                        try:
                            vision_type = apply_wfl_drain_attachment(
                                bedrock_classify_crop(
                                    rendered,
                                    legend_path,
                                    model_id=args.model_id,
                                    region=args.region,
                                    tag=tag,
                                    cx_frac=cx_frac,
                                    cy_frac=cy_frac,
                                    crop_half=float(args.crop_half),
                                    extra_below=float(args.extra_below),
                                    pipe_dn_near=pipe_dn_label_near_tag(tag, text_locations, structural),
                                ),
                                wfl_drain_hint=wfl_drain_line_hint(tag, inventory),
                            )
                            print(f"  [vision] {tag} → {vision_type!r}", flush=True)
                        except Exception as exc:  # noqa: BLE001 - report per-tag vision failures
                            vision_error = f"{type(exc).__name__}: {exc}"
                            print(f"  [vision] {tag} ERROR: {vision_error}", flush=True)

            rows.append(
                {
                    "tag": tag,
                    "function": fn,
                    "description": desc,
                    "cad_type": cad_type,
                    "vision_type": vision_type,
                    "vision_error": vision_error,
                    "x": str(loc["x"]) if loc else "",
                    "y": str(loc["y"]) if loc else "",
                    "layer": str(loc.get("layer") or "") if loc else "",
                    "crop": crop_file,
                }
            )

    headers = [
        "tag",
        "function",
        "expected",
        "cad_type",
        "vision_type",
        "chosen",
        "pass",
        "layer",
        "x",
        "y",
    ]
    table_rows: List[List[str]] = []
    total = 0
    passed = 0
    hits: List[str] = []
    misses: List[Dict[str, str]] = []
    for r in rows:
        expected = EXPECTED_TYPES.get(r["tag"], set())
        chosen = (r["vision_type"] or r["cad_type"] or "").strip()
        got_tokens = set(chosen.upper().split())
        ok = (not expected) or expected.issubset(got_tokens)
        total += 1
        if ok:
            passed += 1
            hits.append(r["tag"])
        else:
            misses.append({"tag": r["tag"], "expected": " ".join(sorted(expected)), "got": chosen})
        x = r["x"]
        y = r["y"]
        try:
            x = f"{float(x):.1f}" if x else ""
            y = f"{float(y):.1f}" if y else ""
        except ValueError:
            pass
        table_rows.append(
            [
                r["tag"],
                r["function"],
                " ".join(sorted(expected)) or "—",
                r["cad_type"] or "—",
                r["vision_type"] or "—",
                chosen or "—",
                "PASS" if ok else "FAIL",
                r["layer"] or "—",
                x,
                y,
            ]
        )
        if r["vision_error"]:
            print(f"  [error] {r['tag']}: {r['vision_error']}", flush=True)

    print()
    _print_table(headers, table_rows)

    print()
    print("=" * 60)
    print(f"  ACCURACY: {(passed/total*100) if total else 0:.1f}%  ({passed}/{total})")
    print("=" * 60)
    if hits:
        print(f"\n  HITS ({len(hits)}):")
        for t in hits:
            print(f"    ✓ {t}")
    if misses:
        print(f"\n  MISSES ({len(misses)}):")
        for m in misses:
            print(f"    ✗ {m['tag']}  expected: {m['expected']}  got: {m['got'] or 'EMPTY'}")
    print()
    print(f"  VALVES TESTED: {', '.join(r['tag'] for r in rows)}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

