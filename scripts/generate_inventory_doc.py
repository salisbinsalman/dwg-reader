"""
Generate docs/DWG_PER_FILE_INVENTORY.md from outputs/dwg_per_file_inventory.json
"""

from __future__ import annotations
import json, pathlib, textwrap
from collections import defaultdict

BASE = pathlib.Path(__file__).parent.parent
SRC = BASE / "outputs" / "dwg_per_file_inventory.json"
OUT = BASE / "docs" / "DWG_PER_FILE_INVENTORY.md"

data = json.load(open(SRC, encoding="utf-8"))


def fmt_tags(attr_tags: dict, limit=25) -> str:
    if not attr_tags:
        return "_none_"
    rows = []
    for tag, info in list(attr_tags.items())[:limit]:
        sample = (info.get("sample") or "").strip()
        if len(sample) > 60:
            sample = sample[:57] + "..."
        rows.append(f"  - `{tag}` ×{info['count']} — `{sample}`" if sample else f"  - `{tag}` ×{info['count']}")
    return "\n".join(rows)


def fmt_list(items, limit=20, code=True) -> str:
    if not items:
        return "_none_"
    subset = items[:limit]
    if code:
        parts = [f"`{i}`" for i in subset]
    else:
        parts = [str(i) for i in subset]
    s = ", ".join(parts)
    if len(items) > limit:
        s += f" … +{len(items)-limit} more"
    return s


def fmt_blocks(blocks, limit=25) -> str:
    if not blocks:
        return "_none_"
    rows = []
    for b in blocks[:limit]:
        rows.append(f"  - `{b['name']}` ({b['entity_count']} entities)")
    if len(blocks) > limit:
        rows.append(f"  - … +{len(blocks)-limit} more")
    return "\n".join(rows)


def fmt_text(samples, limit=15) -> str:
    if not samples:
        return "_none_"
    rows = []
    for s in samples[:limit]:
        t = s["text"].replace("\n", " ").strip()
        if len(t) > 80:
            t = t[:77] + "..."
        rows.append(f"  - `{t}` _(layer: {s['layer']})_")
    return "\n".join(rows)


def fmt_linetypes(lts) -> str:
    if not lts:
        return "_standard only_"
    rows = [f"  - `{lt['name']}` — {lt['description']}" for lt in lts[:20]]
    return "\n".join(rows)


def connectivity_badge(row: dict) -> str:
    c = row.get("connectivity", {})
    assessment = c.get("csv_assessment", "")
    fields = c.get("rel_fields", "")
    count = c.get("rel_record_count", "0")
    if "LIN_FROM" in fields:
        return f"✅ LIN_FROM/LIN_TO ({count} records)"
    if "XData present" in assessment:
        return f"⚠️ XDATA present, no named endpoints"
    if "no semantic" in assessment.lower():
        return "🔴 No semantic connectivity"
    return f"— {assessment[:60]}" if assessment else "—"


def appid_badge(ag: dict) -> str:
    parts = []
    if ag.get("has_pcad"):
        parts.append(f"PCAD ×{ag['pcad_count']}")
    if ag.get("has_idok"):
        parts.append(f"IDOK ×{ag['idok_count']}")
    if ag.get("genius_count"):
        parts.append(f"GENIUS ×{ag['genius_count']}")
    other = ag.get("notable_other", [])
    if other:
        parts.append("other: " + ", ".join(other[:3]))
    return " | ".join(parts) if parts else "—"


def entity_summary(ec: dict) -> str:
    if not ec:
        return "—"
    ordered = sorted(ec.items(), key=lambda x: -x[1])
    return ", ".join(f"{t}×{c}" for t, c in ordered[:8])


# ── group keys by folder ──────────────────────────────────────────────────────
folders: dict[str, list[str]] = defaultdict(list)
for key in data:
    folder = key.split("/")[0]
    folders[folder].append(key)

folder_order = ["CHEM_PID", "OCC_PID", "PM03_PID", "TM01_PID"]
ecosystem_map = {
    "CHEM_PID": "Valmet PS-21",
    "OCC_PID": "Valmet PS-21",
    "PM03_PID": "Valmet PS-21 / Flow-diagram sub-type",
    "TM01_PID": "GOR Italian (GORA*/GORB*) / KSD Swedish (KSDM*)",
}

lines = []

lines.append("# DWG Per-File Inventory")
lines.append("")
lines.append("Complete forensic breakdown of every DWG in the dataset.")
lines.append("Generated from ODA File Converter + ezdxf parse of all 84 indexed DWGs.")
lines.append("")
lines.append("**Parse failures:** 15 KSD DWGs fail with `DXFStructureError: missing ENDSEC tag` "
             "— these are marked ❌ and only CSV metadata is available.")
lines.append("")

# summary table
lines.append("## Summary Table")
lines.append("")
lines.append("| # | Folder | Drawing | Title | Objects | Attrs | Conn | Ecosystem |")
lines.append("|---|--------|---------|-------|--------:|------:|------|-----------|")
n = 0
for folder in folder_order:
    for key in folders.get(folder, []):
        n += 1
        v = data[key]
        meta = v.get("_meta", {})
        fname = meta.get("filename", key.split("/")[-1])
        title = v.get("title_block", {}).get("TITLE1", "")
        if not title:
            # try to infer from filename
            title = fname.replace(".dwg", "").replace("_", " ")
        objects = meta.get("object_count", "—")
        attr_count = len(v.get("attribute_tags", {}))
        conn = connectivity_badge(v) if "error" not in v else "❌ parse failed"

        eco = "Valmet PS-21"
        if "GORA" in fname or "GORB" in fname:
            eco = "GOR Italian"
        elif "KSD" in fname:
            eco = "KSD Swedish"
        elif "RAU640" in fname:
            eco = "Valmet flow-diag."

        short_title = title[:40] + "…" if len(title) > 40 else title
        lines.append(f"| {n} | {folder} | `{fname}` | {short_title} | {objects} | {attr_count} | {conn} | {eco} |")

lines.append("")
lines.append("---")
lines.append("")

# ── per-folder / per-file sections ───────────────────────────────────────────
n = 0
for folder in folder_order:
    eco_label = ecosystem_map.get(folder, "")
    lines.append(f"## {folder}  ·  {eco_label}")
    lines.append("")

    for key in folders.get(folder, []):
        n += 1
        v = data[key]
        meta = v.get("_meta", {})
        fname = meta.get("filename", "")

        eco = "Valmet PS-21"
        if "GORA" in fname or "GORB" in fname:
            eco = "🇮🇹 GOR Italian"
        elif "KSD" in fname:
            eco = "🇸🇪 KSD Swedish"
        elif "RAU640" in fname:
            eco = "Valmet flow-diagram sub-type"

        lines.append(f"### {n}. `{fname}`")
        lines.append("")

        if "error" in v:
            lines.append(f"> ❌ **Parse failed:** `{v['error']}`")
            lines.append("")
            # still show CSV metadata
            lines.append(f"| Field | Value |")
            lines.append(f"|-------|-------|")
            lines.append(f"| Ecosystem | {eco} |")
            lines.append(f"| DWG version | {meta.get('dwg_version', '—')} |")
            lines.append(f"| Last saved by | `{meta.get('last_saved_by', '—')}` |")
            lines.append(f"| Objects (CSV) | {meta.get('object_count', '—')} |")
            lines.append(f"| Entities (CSV) | {meta.get('entity_count', '—')} |")
            lines.append(f"| XDATA entities (CSV) | {meta.get('xdata_entity_count', '—')} |")
            conn = v.get("connectivity", {})
            lines.append(f"| Connectivity (CSV) | {conn.get('csv_assessment', '—')} |")
            lines.append("")
            lines.append("---")
            lines.append("")
            continue

        tb = v.get("title_block", {})
        layers = v.get("layers", [])
        layer_details = v.get("layer_details", [])
        blocks = v.get("blocks_defined", [])
        top_inserts = v.get("top_insert_blocks", [])
        attr_tags = v.get("attribute_tags", {})
        text_samples = v.get("text_samples", [])
        entity_counts = v.get("entity_type_counts", {})
        appid_groups = v.get("appid_groups", {})
        linetypes = v.get("linetypes", [])
        styles = v.get("text_styles", [])
        connectivity = v.get("connectivity", {})

        # metadata table
        lines.append(f"| Field | Value |")
        lines.append(f"|-------|-------|")
        lines.append(f"| Ecosystem | {eco} |")
        lines.append(f"| DWG version | {meta.get('dwg_version', '—')} |")
        lines.append(f"| Last saved by | `{meta.get('last_saved_by', '—')}` |")
        lines.append(f"| Objects | {meta.get('object_count', '—')} |")
        lines.append(f"| Entities (model space) | {sum(entity_counts.values())} |")
        lines.append(f"| Layers | {len(layers)} |")
        lines.append(f"| Block definitions | {len(blocks)} |")
        lines.append(f"| Unique attribute tags | {len(attr_tags)} |")
        lines.append(f"| App ID fingerprint | {appid_badge(appid_groups)} |")
        lines.append(f"| Connectivity | {connectivity_badge(v)} |")
        lines.append("")

        # title block
        if tb:
            lines.append("**Title block fields:**")
            lines.append("")
            for k, val in tb.items():
                lines.append(f"- `{k}`: {val}")
            lines.append("")

        # entity type counts
        if entity_counts:
            lines.append(f"**Entities:** {entity_summary(entity_counts)}")
            lines.append("")

        # layers
        lines.append(f"**Layers ({len(layers)}):**  ")
        # group by semantic prefix
        layer_names = [l["name"] for l in layer_details]
        lines.append(fmt_list(layer_names, limit=40))
        lines.append("")

        # custom linetypes
        custom_lts = [lt for lt in linetypes if lt["name"] not in
                      ("BYBLOCK", "BYLAYER", "CONTINUOUS", "Continuous",
                       "CENTER", "CENTER2", "HIDDEN", "HIDDEN2",
                       "PHANTOM2", "DASHED", "DOT", "DIVIDE")]
        if custom_lts:
            lines.append(f"**Custom linetypes ({len(custom_lts)}):**")
            lines.append("")
            lines.append(fmt_linetypes(custom_lts))
            lines.append("")

        # block definitions
        if blocks:
            non_sys = [b for b in blocks if b["name"] not in
                       ("GENAXEH", "_ACMFILLEDHALF", "_ACMNONE", "_Closed", "_ACMFILLED15")]
            lines.append(f"**Block definitions ({len(non_sys)}):**")
            lines.append("")
            lines.append(fmt_blocks(non_sys, limit=30))
            lines.append("")

        # top insert blocks
        top_notable = [b for b in top_inserts if not b["name"].startswith("*")][:20]
        if top_notable:
            lines.append(f"**Most-used block inserts:**")
            lines.append("")
            for b in top_notable[:15]:
                lines.append(f"  - `{b['name']}` ×{b['count']}")
            lines.append("")

        # attribute tags
        if attr_tags:
            lines.append(f"**Attribute tags & sample values ({len(attr_tags)} unique tags):**")
            lines.append("")
            lines.append(fmt_tags(attr_tags, limit=30))
            lines.append("")

        # text samples
        if text_samples:
            lines.append(f"**Text entity samples (model space):**")
            lines.append("")
            lines.append(fmt_text(text_samples, limit=20))
            lines.append("")

        # text styles
        if styles:
            style_str = ", ".join(f"`{s['name']}` ({s['font']})" for s in styles if s.get("name"))
            lines.append(f"**Text styles:** {style_str}")
            lines.append("")

        lines.append("---")
        lines.append("")

# ── write ─────────────────────────────────────────────────────────────────────
OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Written {len(lines)} lines → {OUT}")
print(f"File size: {OUT.stat().st_size / 1024:.0f} KB")
