#!/usr/bin/env python3
"""
Export hierarchy EQUIPMENT / SUB-EQUIPMENT rows into the SML Equipment load workbook.

Reads hierarchy CSV (orchestrator) and writes a workbook shaped
like docs/examples/SML-Equipment Template RW.xlsx.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

from dwg_floc_context import floc_paths_for_function, format_line_eqktx, merge_floc_context, normalize_pltxt
from dwg_object_type import classify_equipment
from dwg_pure_dump import json_path, safe_name, write_json

TEMPLATE_DEFAULT = Path("docs/examples/SML-Equipment Template RW.xlsx")
SHEET_NAME = "Equipment"
DATA_START_ROW = 7  # 1-based; row 7 is the sample Boiler in the template

SAP_COLUMNS = [
    "TPLNR",
    "EQUNR",
    "HEQUI",
    "POSNR",
    "EQKTX",
    "EQTYP",
    "EQART",
    "INGRP",
    "GEWRK",
    "IWERK",
    "SWERK",
    "KOSTL",
    "GWLDT",
    "GWLEN",
    "ABCKZ",
    "STORT",
    "BEGRU",
]


def _norm(value: object) -> str:
    s = str(value or "").strip()
    return "" if not s or s.lower() == "nan" else s


def read_hierarchy_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return [{k: _norm(v) for k, v in row.items()} for row in csv.DictReader(f)]


def build_equipment_rows(
    hierarchy_rows: Sequence[Dict[str, str]],
    *,
    limit_functions: int = 0,
    ctx: Optional[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    """
    Walk hierarchy stream and emit one Equipment row per EQUIPMENT / SUB-EQUIPMENT.

    FUNCTION headers set the install TPLNR. SUB-EQUIPMENT gets HEQUI = last EQUIPMENT.
    """
    c = merge_floc_context(ctx)
    plant = c["plant"]
    allowed: Optional[Set[str]] = None
    if limit_functions > 0:
        seen_fns: List[str] = []
        for row in hierarchy_rows:
            fn = _norm(row.get("FUNCTION")).upper().replace(" ", "")
            eq = _norm(row.get("EQUIPMENT"))
            sub = _norm(row.get("SUB-EQUIPMENT"))
            if fn and not eq and not sub and fn not in seen_fns:
                seen_fns.append(fn)
                if len(seen_fns) >= limit_functions:
                    break
        allowed = set(seen_fns)

    def blank_row(**kwargs: str) -> Dict[str, str]:
        row = {k: "" for k in SAP_COLUMNS}
        row["EQTYP"] = "P"
        row["INGRP"] = c.get("planning_group", "P01")
        row["IWERK"] = plant
        row["SWERK"] = plant
        row["ABCKZ"] = "D"
        row["BEGRU"] = "001"
        row.update(kwargs)
        return row

    out: List[Dict[str, str]] = []
    current_fn = ""
    current_tplnr = ""
    current_equipment = ""
    top_pos_by_tplnr: Dict[str, int] = {}
    sub_pos_by_parent: Dict[str, int] = {}
    emitted: Set[str] = set()

    for row in hierarchy_rows:
        fn = _norm(row.get("FUNCTION")).upper().replace(" ", "")
        eq = _norm(row.get("EQUIPMENT")).upper().replace(" ", "")
        sub = _norm(row.get("SUB-EQUIPMENT")).upper().replace(" ", "")
        desc = normalize_pltxt(_norm(row.get("DESCRIPTION")))

        if fn and not eq and not sub:
            if allowed is not None and fn not in allowed:
                current_fn = ""
                current_tplnr = ""
                current_equipment = ""
                continue
            current_fn = fn
            current_tplnr = floc_paths_for_function(fn, c)["function"]
            current_equipment = ""
            continue

        if allowed is not None and current_fn and current_fn not in allowed:
            continue
        if not current_tplnr:
            continue

        if eq:
            tag = eq
            hequi = ""
            current_equipment = eq
        elif sub:
            tag = sub
            hequi = current_equipment
        else:
            continue

        if tag in emitted:
            continue
        emitted.add(tag)

        if hequi:
            parent_key = f"{current_tplnr}|{hequi}"
            sub_pos_by_parent[parent_key] = sub_pos_by_parent.get(parent_key, 0) + 10
            posnr = f"{sub_pos_by_parent[parent_key]:04d}"
        else:
            top_pos_by_tplnr[current_tplnr] = top_pos_by_tplnr.get(current_tplnr, 0) + 10
            posnr = f"{top_pos_by_tplnr[current_tplnr]:04d}"
        eqktx = desc if desc else normalize_pltxt(tag)
        if eqktx and not eqktx.startswith(tag):
            eqktx = normalize_pltxt(f"{tag} {eqktx}")
        eqart, gewrk = classify_equipment(tag, eqktx)
        eqktx = format_line_eqktx(tag, eqktx, hequi=hequi)
        out.append(
            blank_row(
                TPLNR=current_tplnr[:30],
                EQUNR=tag[:18],
                HEQUI=hequi[:18],
                POSNR=posnr,
                EQKTX=eqktx[:40],
                EQART=eqart,
                GEWRK=gewrk,
            )
        )
    return out


def write_equipment_workbook(
    template_path: Path,
    out_path: Path,
    equipment_rows: List[Dict[str, str]],
) -> None:
    from openpyxl import load_workbook

    wb = load_workbook(template_path)
    ws = wb[SHEET_NAME] if SHEET_NAME in wb.sheetnames else wb.active

    # Strip template comments (Turkish column metadata) — they get restructured
    # to a different internal path by openpyxl, which breaks some xlsx readers.
    for cell in ws._cells.values():
        if cell.comment is not None:
            cell.comment = None

    # Clear prior data from the sample row downward (keep header block rows 1-6).
    if ws.max_row >= DATA_START_ROW:
        ws.delete_rows(DATA_START_ROW, ws.max_row - DATA_START_ROW + 1)

    for r_i, row in enumerate(equipment_rows, start=DATA_START_ROW):
        ws.cell(r_i, 1, value=None)  # ID column unused
        for c_i, key in enumerate(SAP_COLUMNS, start=2):
            ws.cell(r_i, c_i, value=row.get(key) or None)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)


def resolve_hierarchy_csv(out_dir: Path, base: str, explicit: str = "") -> Optional[Path]:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        return p if p.exists() else None
    primary = out_dir / f"{base}.hierarchy_orchestrator.csv"
    return primary if primary.exists() else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Export SAP Equipment workbook")
    parser.add_argument("--hierarchy-csv", default="")
    parser.add_argument("--input", default="inputs/Broke System.dwg", help="Used for output stem")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--template", default=str(TEMPLATE_DEFAULT))
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional max FUNCTIONs whose children to export (0 = all)",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir).expanduser().resolve()
    base = safe_name(Path(args.input))
    hier_path = resolve_hierarchy_csv(out_dir, base, args.hierarchy_csv)
    if not hier_path:
        print(f"[error] Missing hierarchy CSV under {out_dir}", flush=True)
        return 2

    template = Path(args.template).expanduser().resolve()
    if not template.exists():
        print(f"[error] Missing template: {template}", flush=True)
        return 2

    hierarchy_rows = read_hierarchy_csv(hier_path)
    equipment_rows = build_equipment_rows(hierarchy_rows, limit_functions=args.limit)
    out_xlsx = out_dir / f"{base}.equipment.xlsx"
    write_equipment_workbook(template, out_xlsx, equipment_rows)

    tplnrs = sorted({r["TPLNR"] for r in equipment_rows})
    report: Dict[str, Any] = {
        "hierarchy_csv": str(hier_path),
        "output": str(out_xlsx),
        "equipment_row_count": len(equipment_rows),
        "tplnr_count": len(tplnrs),
        "tplnrs": tplnrs,
        "with_hequi": sum(1 for r in equipment_rows if r.get("HEQUI")),
    }
    report_path = json_path(out_dir, f"{base}.equipment_report.json")
    write_json(report_path, report)
    print(
        f"Wrote {out_xlsx} ({len(equipment_rows)} equipment rows, "
        f"{len(tplnrs)} FLOCs, {report['with_hequi']} with HEQUI)"
    )
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
