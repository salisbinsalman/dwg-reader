"""
Per-DWG forensic inventory.

For every DWG in the CSV index, extract:
  - title block fields
  - attribute tags + sample values (first non-empty per tag)
  - block names (non-anonymous)
  - layer names + linetype
  - text entities sample (first 15 meaningful ones from model space)
  - connectivity (from CSV + XDATA appids)
  - app ID groups

Writes: outputs/dwg_per_file_inventory.json
"""

from __future__ import annotations
import csv, json, sys, pathlib, traceback
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

BASE = pathlib.Path(__file__).parent.parent
CSV_PATH = BASE / "resources" / "sml_dwg_index_260806 (1).csv"
REF_BASE = BASE / "inputs" / "Reference"
OUT_PATH = BASE / "outputs" / "dwg_per_file_inventory.json"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# ── helpers ──────────────────────────────────────────────────────────────────

def safe_get(dxf, attr, default=None):
    try:
        return getattr(dxf, attr)
    except Exception:
        return default


def vector(v):
    if v is None:
        return None
    try:
        return [round(float(v.x), 3), round(float(v.y), 3)]
    except Exception:
        return None


_TITLE_KEYS = {
    "TITLE1", "TITLE2", "TITLE3",
    "PROJECT1", "PROJECT2", "PROJECT3",
    "DRAWINGID", "SHEET", "LYH", "CAD", "ARKKI",
    "TUNNUS", "SROIK", "SRVAS",
    "INF1", "INF2", "INF3", "INF4", "INF5", "INF6", "INF14",
    "MRK", "PVM", "MUU", "TAR", "MUUTOS",
    "MRK2", "PVM2", "MUU2", "TAR2", "MUUTOS2", "KPL",
}

_SKIP_TEXT = {"", " ", "  "}

GENIUS_PREFIX = "GENIUS"
PCAD_PREFIX = "PCAD"
IDOK_PREFIX = "IDOK"


def classify_appids(appid_names: list[str]) -> dict:
    genius = [a for a in appid_names if a.startswith(GENIUS_PREFIX)]
    pcad = [a for a in appid_names if a.startswith(PCAD_PREFIX)]
    idok = [a for a in appid_names if a.startswith(IDOK_PREFIX)]
    other_notable = [a for a in appid_names
                     if not any(a.startswith(p) for p in (GENIUS_PREFIX, PCAD_PREFIX, IDOK_PREFIX, "ACAD", "Ac"))
                     and a not in ("ACAD", "STANDARD")]
    return {
        "has_pcad": bool(pcad),
        "has_idok": bool(idok),
        "genius_count": len(genius),
        "pcad_count": len(pcad),
        "idok_count": len(idok),
        "notable_other": other_notable[:10],
    }


# ── per-DWG parse ─────────────────────────────────────────────────────────────

def parse_one(path: pathlib.Path, csv_row: dict) -> dict:
    from dwg_reader.dwg_pure_dump import configure_odafc
    from ezdxf.addons import odafc

    configure_odafc()
    if not odafc.is_installed():
        return {"error": "ODA not installed"}

    try:
        doc = odafc.readfile(str(path))
    except Exception as e:
        return {"error": str(e)}

    msp = doc.modelspace()

    # ── layers ──────────────────────────────────────────────────────────────
    layers = []
    for lyr in doc.layers:
        layers.append({
            "name": lyr.dxf.name,
            "color": safe_get(lyr.dxf, "color"),
            "linetype": safe_get(lyr.dxf, "linetype"),
        })

    # ── blocks (non-anonymous) ───────────────────────────────────────────────
    blocks = []
    for blk in doc.blocks:
        if blk.name.startswith("*"):
            continue
        blocks.append({"name": blk.name, "entity_count": len(list(blk))})

    # ── inserts + attributes ─────────────────────────────────────────────────
    attr_samples: dict[str, str] = {}   # tag → first non-empty value seen
    all_attr_tags: dict[str, int] = defaultdict(int)  # tag → count
    insert_blocks: list[str] = []

    title_fields: dict[str, str] = {}

    for e in msp:
        if e.dxftype() != "INSERT":
            continue
        bname = safe_get(e.dxf, "name") or ""
        insert_blocks.append(bname)
        try:
            attribs = list(e.attribs)
        except Exception:
            attribs = []
        row_attrs: dict[str, str] = {}
        for a in attribs:
            tag = (safe_get(a.dxf, "tag") or "").strip().upper()
            val = (safe_get(a.dxf, "text") or "").strip()
            if not tag:
                continue
            all_attr_tags[tag] += 1
            if val and tag not in attr_samples:
                attr_samples[tag] = val
            row_attrs[tag] = val
        # title block detection
        hits = {k: v for k, v in row_attrs.items() if k in _TITLE_KEYS and v}
        if hits:
            title_fields.update(hits)

    # ── text entities ────────────────────────────────────────────────────────
    text_samples: list[dict] = []
    seen_texts: set[str] = set()
    for e in msp:
        if e.dxftype() not in ("TEXT", "MTEXT"):
            continue
        try:
            raw = e.plain_mtext() if e.dxftype() == "MTEXT" else safe_get(e.dxf, "text", "")
        except Exception:
            raw = safe_get(e.dxf, "text", "")
        t = (raw or "").strip()
        if not t or t in _SKIP_TEXT or t in seen_texts:
            continue
        if len(t) > 200:
            continue  # skip giant MTEXT blobs
        seen_texts.add(t)
        lyr = safe_get(e.dxf, "layer", "")
        text_samples.append({"layer": lyr, "text": t})
        if len(text_samples) >= 30:
            break

    # ── app IDs ─────────────────────────────────────────────────────────────
    try:
        appid_names = [a.dxf.name for a in doc.appids]
    except Exception:
        appid_names = []
    appid_info = classify_appids(appid_names)

    # ── linetypes ────────────────────────────────────────────────────────────
    linetypes = []
    for lt in doc.linetypes:
        name = safe_get(lt.dxf, "name", "")
        if name in ("BYBLOCK", "BYLAYER", "CONTINUOUS", "Continuous"):
            continue
        desc = safe_get(lt.dxf, "description", "")
        linetypes.append({"name": name, "description": desc})

    # ── text styles ──────────────────────────────────────────────────────────
    styles = []
    for st in doc.styles:
        styles.append({
            "name": safe_get(st.dxf, "name"),
            "font": safe_get(st.dxf, "font"),
        })

    # ── unique insert block names (ordered by frequency) ─────────────────────
    insert_freq: dict[str, int] = defaultdict(int)
    for b in insert_blocks:
        if b and not b.startswith("*"):
            insert_freq[b] += 1
    top_inserts = sorted(insert_freq.items(), key=lambda x: -x[1])

    # ── entity type counts ────────────────────────────────────────────────────
    etype_counts: dict[str, int] = defaultdict(int)
    for e in msp:
        etype_counts[e.dxftype()] += 1

    return {
        "title_block": title_fields,
        "layers": [l["name"] for l in layers],
        "layer_details": layers,
        "linetypes": linetypes,
        "text_styles": styles,
        "blocks_defined": [{"name": b["name"], "entity_count": b["entity_count"]} for b in blocks],
        "top_insert_blocks": [{"name": n, "count": c} for n, c in top_inserts[:30]],
        "attribute_tags": {tag: {"count": cnt, "sample": attr_samples.get(tag, "")}
                           for tag, cnt in sorted(all_attr_tags.items(), key=lambda x: -x[1])},
        "text_samples": text_samples,
        "entity_type_counts": dict(etype_counts),
        "appid_groups": appid_info,
        "connectivity": {
            "csv_assessment": csv_row.get("connectivity_assessment", ""),
            "rel_fields": csv_row.get("relationship_fields", ""),
            "rel_record_count": csv_row.get("relationship_record_count", ""),
        },
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8")))
    results = {}

    total = len(rows)
    for idx, row in enumerate(rows, 1):
        rel = row["relative_path"].replace("Reference/", "", 1)
        path = REF_BASE / rel
        fname = row["filename"]
        folder = row["top_level_folder"]
        key = f"{folder}/{fname}"

        print(f"[{idx:02d}/{total}] {key}", flush=True)

        if not path.exists():
            results[key] = {"error": "file not found", "path": str(path)}
            continue

        try:
            data = parse_one(path, row)
        except Exception as e:
            data = {"error": f"unhandled: {e}", "traceback": traceback.format_exc()[-400:]}

        data["_meta"] = {
            "folder": folder,
            "filename": fname,
            "path": str(path),
            "dwg_version": row.get("dwg_version"),
            "last_saved_by": row.get("last_saved_by"),
            "object_count": row.get("object_count"),
            "entity_count": row.get("entity_count"),
            "xdata_entity_count": row.get("xdata_entity_count"),
        }
        results[key] = data

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nWritten → {OUT_PATH}")


if __name__ == "__main__":
    main()
