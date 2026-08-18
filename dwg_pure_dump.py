#!/usr/bin/env python3
"""
Forensic DWG/DXF pure dump utility.

Goals:
- Always produce a low-level binary/text dump for DWG/DXF files.
- If CAD parser backend is available, also produce full structured CAD dump:
  layers, blocks, inserts, entities, attributes, layouts, header vars.

Backends:
- ezdxf direct for DXF
- ezdxf + ODA File Converter for DWG (if odafc addon has converter installed)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


def _patch_odafc_no_focus() -> None:
    """Monkey-patch ezdxf odafc on macOS to prevent ODA from stealing focus.

    Injects no_focus_steal.dylib via DYLD_INSERT_LIBRARIES, which patches
    -[NSApplication activateIgnoringOtherApps:] to a no-op at runtime so the
    ODA process cannot bring itself to the foreground.
    """
    import platform
    import subprocess
    import types

    if platform.system() != "Darwin":
        return
    try:
        import ezdxf.addons.odafc as _odafc
    except ImportError:
        return

    _dylib = Path(__file__).resolve().parent / "no_focus_steal.dylib"
    _orig = _odafc._run_with_no_gui

    def _darwin_no_focus(system, command, arguments):
        if system != "Darwin":
            return _orig(system, command, arguments)
        env = os.environ.copy()
        if _dylib.is_file():
            existing = env.get("DYLD_INSERT_LIBRARIES", "")
            env["DYLD_INSERT_LIBRARIES"] = (
                f"{existing}:{_dylib}" if existing else str(_dylib)
            )
        proc = subprocess.run(
            [command] + arguments, text=True, capture_output=True, env=env
        )
        return types.SimpleNamespace(
            returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr
        )

    _odafc._run_with_no_gui = _darwin_no_focus


_patch_odafc_no_focus()


def configure_odafc() -> Optional[str]:
    """Auto-detect ODA File Converter on macOS/Linux and configure ezdxf odafc."""
    import shutil

    candidates = [
        os.environ.get("ODA_FILE_CONVERTER"),
        os.path.expanduser("~/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter"),
        os.path.expanduser("~/bin/ODAFileConverter"),
        "/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter",
        shutil.which("ODAFileConverter"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        p = Path(candidate).expanduser()
        if p.is_file() and os.access(p, os.X_OK):
            try:
                from ezdxf.addons import odafc  # type: ignore

                odafc.unix_exec_path = str(p.resolve())
                if odafc.is_installed():
                    return str(p.resolve())
            except Exception:
                continue
    return None


def json_safe(value: Any) -> Any:
    """Convert values to JSON-serializable forms."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    # numpy arrays/scalars
    mod = type(value).__module__
    if mod and mod.startswith("numpy"):
        try:
            return value.tolist()
        except Exception:
            return float(value) if hasattr(value, "item") else str(value)
    if hasattr(value, "x") and hasattr(value, "y"):
        return vector(value)
    return str(value)


def write_json(path: Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(json_safe(data), indent=2, ensure_ascii=True),
        encoding="utf-8",
    )


def safe_name(path: Path) -> str:
    return path.stem.replace("/", "_")


def evidence_dir(out_dir: Path) -> Path:
    """Cropped viewer / hierarchy evidence images live under outputs/evidence."""
    path = Path(out_dir) / "evidence"
    path.mkdir(parents=True, exist_ok=True)
    return path


def jsons_dir(out_dir: Path) -> Path:
    """Pipeline / cache JSON files live under outputs/jsons."""
    path = Path(out_dir) / "jsons"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir(out_dir: Path) -> Path:
    """Run logs live under outputs/logs."""
    path = Path(out_dir) / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def json_path(out_dir: Path, filename: str) -> Path:
    """Canonical write path for a JSON artifact."""
    return jsons_dir(out_dir) / filename


def find_json(out_dir: Path, filename: str) -> Path:
    """
    Resolve a JSON artifact: prefer outputs/jsons/, fall back to legacy outputs/ root.
    Returns the preferred jsons path even if missing (caller checks exists()).
    """
    preferred = json_path(out_dir, filename)
    if preferred.exists():
        return preferred
    legacy = Path(out_dir) / filename
    if legacy.exists():
        return legacy
    return preferred


def clear_previous_outputs(
    out_dir: Path,
    base: str,
    suffixes: Optional[Sequence[str]] = None,
) -> List[str]:
    """Remove prior-run artifacts for this drawing stem.

    If ``suffixes`` is None, delete every file matching ``{base}.*`` in
    ``out_dir`` and ``out_dir/jsons``.
    Otherwise delete ``{base}{suffix}`` for each provided suffix from the
    appropriate location (``.json`` → jsons/, else out_dir/).
    """
    out_dir = Path(out_dir)
    if not out_dir.is_dir():
        return []

    removed: List[str] = []
    search_roots = [out_dir, jsons_dir(out_dir)]

    if suffixes is None:
        candidates = []
        for root in search_roots:
            candidates.extend(sorted(root.glob(f"{base}.*")))
    else:
        candidates = []
        for suffix in suffixes:
            name = f"{base}{suffix}"
            if suffix.endswith(".json"):
                candidates.append(json_path(out_dir, name))
                candidates.append(out_dir / name)  # legacy cleanup
            else:
                candidates.append(out_dir / name)

    seen = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        if path.is_file():
            path.unlink()
            removed.append(key)

    if removed:
        print(f"[clean] Removed {len(removed)} previous output(s) for '{base}'")
    return removed


def clear_evidence_outputs(out_dir: Path, base: str, tags: Sequence[str]) -> List[str]:
    """Remove prior cropped evidence images for this drawing + tags."""
    ev = evidence_dir(out_dir)
    removed: List[str] = []
    patterns = [
        f"{base}.viewer_*.png",
        f"{base}.hierarchy_*.png",
        *[f"{base}.viewer_{t}.png" for t in tags],
        *[f"{base}.hierarchy_{t}.png" for t in tags],
        *[f"{base}.hierarchy_{t}_cad.png" for t in tags],
        *[f"{base}.hierarchy_{t}_schematic.png" for t in tags],
    ]
    seen = set()
    for pat in patterns:
        for path in ev.glob(pat):
            key = str(path)
            if key in seen or not path.is_file():
                continue
            seen.add(key)
            path.unlink()
            removed.append(key)
    if removed:
        print(f"[clean] Removed {len(removed)} evidence image(s) for '{base}'")
    return removed


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    entropy = 0.0
    n = len(data)
    for c in freq:
        if c:
            p = c / n
            entropy -= p * math.log2(p)
    return entropy


def extract_ascii_strings_with_offsets(data: bytes, min_len: int = 4) -> List[Dict[str, Any]]:
    pattern = re.compile(rb"[ -~]{%d,}" % min_len)
    out = []
    for m in pattern.finditer(data):
        raw = m.group(0)
        out.append(
            {
                "offset": m.start(),
                "length": len(raw),
                "text": raw.decode("latin1", errors="ignore"),
            }
        )
    return out


def extract_utf16le_strings_with_offsets(data: bytes, min_chars: int = 4) -> List[Dict[str, Any]]:
    pattern = re.compile(rb"(?:[\x20-\x7E]\x00){%d,}" % min_chars)
    out = []
    for m in pattern.finditer(data):
        raw = m.group(0)
        try:
            text = raw.decode("utf-16le", errors="ignore")
        except Exception:
            continue
        text = text.strip("\x00").strip()
        if not text:
            continue
        out.append({"offset": m.start(), "length": len(raw), "text": text})
    return out


def maybe_extract_embedded_png(data: bytes, output_dir: Path, base: str) -> List[str]:
    """Extract embedded PNG blobs into outputs/evidence (not the Excel deliverable root)."""
    out_dir = evidence_dir(output_dir)
    # Scan for PNG signatures
    png_sig = b"\x89PNG\r\n\x1a\n"
    iend = b"IEND\xaeB`\x82"
    found: List[str] = []
    count = 0
    start = 0
    while True:
        idx = data.find(png_sig, start)
        if idx < 0:
            break
        end = data.find(iend, idx)
        if end < 0:
            break
        end += len(iend)
        chunk = data[idx:end]
        out_path = out_dir / f"{base}.embedded_png_{count}.png"
        out_path.write_bytes(chunk)
        found.append(str(out_path))
        count += 1
        start = end
    return found


def classify_token_candidates(tokens: Iterable[str]) -> Dict[str, List[str]]:
    pat_line = re.compile(r"\b\d{1,4}-[A-Z0-9]{1,10}-\d{1,5}[A-Z0-9-]*\b")
    pat_instr = re.compile(r"\b(?:PT|TT|FT|LT|PI|TI|FI|LI|PIC|TIC|FIC|LIC|PSV|PCV|FCV|LCV|XV|HV|CV|SDV|ESDV)-?\d{1,5}[A-Z]?\b")
    pat_equip = re.compile(r"\b(?:P|T|TK|V|E|HX|C|COMP|FAN|BLOWER)\d{1,6}[A-Z0-9]*\b")

    def uniq_sorted(values: List[str]) -> List[str]:
        return sorted(set(values))

    line_numbers = []
    instruments = []
    equipment = []
    for t in tokens:
        line_numbers.extend(pat_line.findall(t))
        instruments.extend(pat_instr.findall(t))
        equipment.extend(pat_equip.findall(t))
    return {
        "line_numbers": uniq_sorted(line_numbers),
        "instrument_tags": uniq_sorted(instruments),
        "equipment_tags": uniq_sorted(equipment),
    }


def vector(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "x") and hasattr(value, "y"):
        z = getattr(value, "z", 0.0)
        return [float(value.x), float(value.y), float(z)]
    return value


def safe_get(dxf_obj: Any, attr: str, default: Any = None) -> Any:
    try:
        return getattr(dxf_obj, attr)
    except Exception:
        return default


def dump_entity_geometry(entity: Any) -> Dict[str, Any]:
    t = entity.dxftype()
    d = entity.dxf
    g: Dict[str, Any] = {}

    if t == "LINE":
        g["start"] = vector(safe_get(d, "start"))
        g["end"] = vector(safe_get(d, "end"))
    elif t in ("LWPOLYLINE",):
        pts = []
        try:
            for p in entity.get_points("xyseb"):
                # x, y, start_width, end_width, bulge
                pts.append(list(p))
        except Exception:
            pass
        g["points_xyseb"] = pts
        g["closed"] = bool(getattr(entity, "closed", False))
    elif t in ("POLYLINE",):
        verts = []
        try:
            for v in entity.vertices:
                verts.append(vector(v.dxf.location))
        except Exception:
            pass
        g["vertices"] = verts
        g["is_3d_polyline"] = bool(getattr(entity, "is_3d_polyline", False))
    elif t in ("CIRCLE",):
        g["center"] = vector(safe_get(d, "center"))
        g["radius"] = safe_get(d, "radius")
    elif t in ("ARC",):
        g["center"] = vector(safe_get(d, "center"))
        g["radius"] = safe_get(d, "radius")
        g["start_angle"] = safe_get(d, "start_angle")
        g["end_angle"] = safe_get(d, "end_angle")
    elif t in ("ELLIPSE",):
        g["center"] = vector(safe_get(d, "center"))
        g["major_axis"] = vector(safe_get(d, "major_axis"))
        g["ratio"] = safe_get(d, "ratio")
        g["start_param"] = safe_get(d, "start_param")
        g["end_param"] = safe_get(d, "end_param")
    elif t in ("SPLINE",):
        cps = []
        fit_points = []
        try:
            cps = [vector(p) for p in entity.control_points]
        except Exception:
            pass
        try:
            fit_points = [vector(p) for p in entity.fit_points]
        except Exception:
            pass
        g["degree"] = safe_get(d, "degree")
        g["control_points"] = cps
        g["fit_points"] = fit_points
    elif t in ("INSERT",):
        g["insert"] = vector(safe_get(d, "insert"))
        g["xscale"] = safe_get(d, "xscale", 1.0)
        g["yscale"] = safe_get(d, "yscale", 1.0)
        g["zscale"] = safe_get(d, "zscale", 1.0)
        g["rotation"] = safe_get(d, "rotation", 0.0)
        g["name"] = safe_get(d, "name")
    elif t in ("TEXT",):
        g["insert"] = vector(safe_get(d, "insert"))
        g["align_point"] = vector(safe_get(d, "align_point"))
        g["height"] = safe_get(d, "height")
        g["rotation"] = safe_get(d, "rotation")
        g["text"] = safe_get(d, "text")
    elif t in ("MTEXT",):
        g["insert"] = vector(safe_get(d, "insert"))
        g["char_height"] = safe_get(d, "char_height")
        g["rotation"] = safe_get(d, "rotation")
        try:
            g["text"] = entity.plain_text()
        except Exception:
            g["text"] = safe_get(d, "text")
    elif t in ("ATTRIB", "ATTDEF"):
        g["insert"] = vector(safe_get(d, "insert"))
        g["text"] = safe_get(d, "text")
        g["tag"] = safe_get(d, "tag")
        g["height"] = safe_get(d, "height")
        g["rotation"] = safe_get(d, "rotation")
    elif t == "HATCH":
        g["solid_fill"] = safe_get(d, "solid_fill")
        g["pattern_name"] = safe_get(d, "pattern_name")
        g["pattern_scale"] = safe_get(d, "pattern_scale")
    elif t in ("DIMENSION", "LEADER", "MULTILEADER"):
        g["defpoint"] = vector(safe_get(d, "defpoint"))
    else:
        # fallback: no geometry details known in this dispatcher
        pass
    return g


def dump_entity(entity: Any, owner_space: str) -> Dict[str, Any]:
    d = entity.dxf
    item = {
        "type": entity.dxftype(),
        "handle": safe_get(d, "handle"),
        "layer": safe_get(d, "layer"),
        "color": safe_get(d, "color"),
        "linetype": safe_get(d, "linetype"),
        "lineweight": safe_get(d, "lineweight"),
        "transparency": safe_get(d, "transparency"),
        "owner": safe_get(d, "owner"),
        "owner_space": owner_space,
        "geometry": dump_entity_geometry(entity),
    }
    return item


def point_key(pt: Any, precision: int = 6) -> Optional[str]:
    if not isinstance(pt, list) or len(pt) < 2:
        return None
    try:
        x = round(float(pt[0]), precision)
        y = round(float(pt[1]), precision)
        z = round(float(pt[2]), precision) if len(pt) > 2 else 0.0
        return f"{x}|{y}|{z}"
    except Exception:
        return None


def entity_connection_points(rec: Dict[str, Any]) -> List[List[float]]:
    g = rec.get("geometry", {})
    t = rec.get("type")
    pts: List[List[float]] = []
    if t == "LINE":
        if isinstance(g.get("start"), list):
            pts.append(g["start"])
        if isinstance(g.get("end"), list):
            pts.append(g["end"])
    elif t == "LWPOLYLINE":
        for p in g.get("points_xyseb", []):
            if len(p) >= 2:
                pts.append([float(p[0]), float(p[1]), 0.0])
    elif t == "POLYLINE":
        for p in g.get("vertices", []):
            if isinstance(p, list):
                pts.append(p)
    return pts


def try_get_xdata(entity: Any, appid: str) -> Any:
    try:
        return entity.get_xdata(appid)
    except Exception:
        return None


def infer_pid_nodes_edges(
    entities: List[Dict[str, Any]],
    inserts: List[Dict[str, Any]],
    texts: List[Dict[str, Any]],
    attrs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # Node sources: inserts + tagged attributes + text tags.
    for ins in inserts:
        node = {
            "node_id": f"INS:{ins.get('handle')}",
            "node_type": "insert",
            "name": ins.get("name"),
            "handle": ins.get("handle"),
            "position": ins.get("insert"),
            "layer": ins.get("layer"),
            "attributes": ins.get("attributes", []),
        }
        nodes.append(node)

    for idx, txt in enumerate(texts):
        text_val = txt.get("text")
        if not isinstance(text_val, str):
            continue
        if re.search(r"\b(?:PT|TT|FT|LT|PI|TI|FI|LI|PIC|TIC|FIC|LIC|PSV|PCV|FCV|LCV|XV|HV|CV|SDV|ESDV)-?\d{1,5}[A-Z]?\b", text_val):
            nodes.append(
                {
                    "node_id": f"TXT:{txt.get('handle') or idx}",
                    "node_type": "instrument_text",
                    "text": text_val,
                    "handle": txt.get("handle"),
                    "position": txt.get("position"),
                    "layer": txt.get("layer"),
                }
            )

    # Build endpoint map for rough connectivity.
    endpoint_map: Dict[str, List[str]] = {}
    linear_types = {"LINE", "LWPOLYLINE", "POLYLINE"}
    for rec in entities:
        if rec.get("type") not in linear_types:
            continue
        edge_id = f"ENT:{rec.get('handle')}"
        pts = entity_connection_points(rec)
        if len(pts) < 2:
            continue
        edges.append(
            {
                "edge_id": edge_id,
                "entity_type": rec.get("type"),
                "handle": rec.get("handle"),
                "layer": rec.get("layer"),
                "owner_space": rec.get("owner_space"),
                "points": pts,
            }
        )
        for p in (pts[0], pts[-1]):
            k = point_key(p)
            if k:
                endpoint_map.setdefault(k, []).append(edge_id)

    # Junction edges where multiple segments touch same coordinate.
    junctions = []
    for k, eids in endpoint_map.items():
        if len(eids) > 1:
            junctions.append({"point_key": k, "connected_edges": sorted(set(eids))})

    return {
        "nodes": nodes,
        "edges": edges,
        "junctions": junctions,
        "counts": {
            "nodes": len(nodes),
            "edges": len(edges),
            "junctions": len(junctions),
        },
    }


def parse_with_ezdxf(path: Path) -> Tuple[Optional[Dict[str, Any]], str]:
    try:
        import ezdxf  # type: ignore
    except Exception as e:
        return None, f"ezdxf import failed: {e}"

    source_doc = None
    backend = ""
    ext = path.suffix.lower()

    if ext == ".dxf":
        try:
            source_doc = ezdxf.readfile(path)
            backend = "ezdxf:dxf-direct"
        except Exception as e:
            return None, f"DXF parse failed: {e}"
    elif ext == ".dwg":
        try:
            from ezdxf.addons import odafc  # type: ignore
        except Exception as e:
            return None, f"ezdxf.odafc unavailable: {e}"
        try:
            oda_path = configure_odafc()
            if not odafc.is_installed():
                return None, (
                    "odafc not installed; cannot parse DWG structurally. "
                    "Install ODA File Converter or set ODA_FILE_CONVERTER env var."
                )
            backend = f"ezdxf:odafc-dwg ({oda_path})"
            source_doc = odafc.readfile(str(path))
        except Exception as e:
            return None, f"DWG parse via odafc failed: {e}"
    else:
        return None, f"Unsupported extension: {ext}"

    doc = source_doc
    header_vars = {}
    for key in doc.header.varnames():
        try:
            val = doc.header.get(key)
            if hasattr(val, "x") and hasattr(val, "y"):
                header_vars[key] = vector(val)
            else:
                header_vars[key] = val
        except Exception:
            header_vars[key] = str(doc.header.get(key, ""))

    layouts = []
    for layout in doc.layouts:
        layouts.append(
            {
                "name": layout.name,
                "taborder": getattr(layout, "taborder", None),
                "is_modelspace": bool(layout.name.upper() == "MODEL"),
            }
        )

    layers = []
    layer_entity_hist = {}
    for layer in doc.layers:
        entry = {
            "name": layer.dxf.name,
            "color": safe_get(layer.dxf, "color"),
            "linetype": safe_get(layer.dxf, "linetype"),
            "lineweight": safe_get(layer.dxf, "lineweight"),
            "plot": safe_get(layer.dxf, "plot"),
            "is_frozen": bool(getattr(layer, "is_frozen", False)),
            "is_locked": bool(getattr(layer, "is_locked", False)),
            "is_off": bool(getattr(layer, "is_off", False)),
            "transparency": safe_get(layer.dxf, "transparency"),
            "description": safe_get(layer.dxf, "description"),
        }
        layers.append(entry)
        layer_entity_hist[layer.dxf.name] = {}

    block_defs = []
    inserts = []
    block_hierarchy = []
    for block in doc.blocks:
        if block.name.startswith("*"):
            # keep anonymous/internal too, but still include
            pass
        entities = []
        nested_refs = []
        for e in block:
            entities.append(dump_entity(e, owner_space=f"BLOCK:{block.name}"))
            if e.dxftype() == "INSERT":
                nested_refs.append(safe_get(e.dxf, "name"))
        block_defs.append(
            {
                "name": block.name,
                "base_point": vector(block.base_point),
                "units": safe_get(block.block.dxf, "units"),
                "entity_count": len(entities),
                "entities": entities,
            }
        )
        if nested_refs:
            block_hierarchy.append({"block": block.name, "contains_inserts": nested_refs})

    all_entities = []

    # Modelspace
    msp = doc.modelspace()
    for e in msp:
        rec = dump_entity(e, owner_space="MODEL")
        all_entities.append(rec)
        lyr = rec.get("layer")
        if lyr in layer_entity_hist:
            t = rec["type"]
            layer_entity_hist[lyr][t] = layer_entity_hist[lyr].get(t, 0) + 1
        if e.dxftype() == "INSERT":
            attrs = []
            try:
                for a in e.attribs:
                    attrs.append(
                        {
                            "tag": safe_get(a.dxf, "tag"),
                            "text": safe_get(a.dxf, "text"),
                            "insert": vector(safe_get(a.dxf, "insert")),
                            "height": safe_get(a.dxf, "height"),
                            "rotation": safe_get(a.dxf, "rotation"),
                            "layer": safe_get(a.dxf, "layer"),
                        }
                    )
            except Exception:
                pass
            inserts.append(
                {
                    "handle": safe_get(e.dxf, "handle"),
                    "name": safe_get(e.dxf, "name"),
                    "insert": vector(safe_get(e.dxf, "insert")),
                    "xscale": safe_get(e.dxf, "xscale", 1.0),
                    "yscale": safe_get(e.dxf, "yscale", 1.0),
                    "zscale": safe_get(e.dxf, "zscale", 1.0),
                    "rotation": safe_get(e.dxf, "rotation", 0.0),
                    "layer": safe_get(e.dxf, "layer"),
                    "attributes": attrs,
                }
            )

    # Paperspace layouts entities
    paperspace_entities = []
    for layout in doc.layouts:
        if layout.name.upper() == "MODEL":
            continue
        for e in layout:
            rec = dump_entity(e, owner_space=f"PAPER:{layout.name}")
            paperspace_entities.append(rec)
            all_entities.append(rec)
            lyr = rec.get("layer")
            if lyr in layer_entity_hist:
                t = rec["type"]
                layer_entity_hist[lyr][t] = layer_entity_hist[lyr].get(t, 0) + 1

    texts = []
    for rec in all_entities:
        if rec["type"] in ("TEXT", "MTEXT"):
            txt = rec["geometry"].get("text")
            texts.append(
                {
                    "handle": rec["handle"],
                    "type": rec["type"],
                    "text": txt,
                    "layer": rec["layer"],
                    "rotation": rec["geometry"].get("rotation"),
                    "height": rec["geometry"].get("height") or rec["geometry"].get("char_height"),
                    "position": rec["geometry"].get("insert"),
                }
            )

    tags = []
    for ins in inserts:
        for a in ins["attributes"]:
            tags.append(
                {
                    "insert_name": ins["name"],
                    "insert_handle": ins["handle"],
                    "tag": a["tag"],
                    "value": a["text"],
                    "position": a["insert"],
                    "layer": a["layer"],
                }
            )

    # Extended entity data (XDATA/EED-like) extraction.
    appids = []
    try:
        appids = [a.dxf.name for a in doc.appids]
    except Exception:
        appids = []
    eed_xdata_dump = []
    for rec, src_entity in []:
        pass
    # We need source entity instances for xdata; gather again from spaces.
    source_entities = []
    for e in msp:
        source_entities.append(("MODEL", e))
    for layout in doc.layouts:
        if layout.name.upper() == "MODEL":
            continue
        for e in layout:
            source_entities.append((f"PAPER:{layout.name}", e))
    for owner_space, ent in source_entities:
        xdata_items = {}
        for appid in appids:
            xd = try_get_xdata(ent, appid)
            if xd:
                xdata_items[appid] = [str(item) for item in xd]
        ext = {
            "handle": safe_get(ent.dxf, "handle"),
            "type": ent.dxftype(),
            "owner_space": owner_space,
            "layer": safe_get(ent.dxf, "layer"),
            "xdicobjhandle": safe_get(ent.dxf, "xdicobjhandle"),
            "reactors": safe_get(ent.dxf, "reactors"),
            "xdata": xdata_items,
        }
        if ext["xdata"] or ext["xdicobjhandle"] or ext["reactors"]:
            eed_xdata_dump.append(ext)

    pid_graph = infer_pid_nodes_edges(all_entities, inserts, texts, tags)

    # CAD tables / styles
    linetypes = []
    try:
        for lt in doc.linetypes:
            linetypes.append(
                {
                    "name": safe_get(lt.dxf, "name"),
                    "description": safe_get(lt.dxf, "description"),
                    "length": safe_get(lt.dxf, "length"),
                }
            )
    except Exception:
        pass

    text_styles = []
    try:
        for st in doc.styles:
            text_styles.append(
                {
                    "name": safe_get(st.dxf, "name"),
                    "font": safe_get(st.dxf, "font"),
                    "bigfont": safe_get(st.dxf, "bigfont"),
                    "height": safe_get(st.dxf, "height"),
                    "width": safe_get(st.dxf, "width"),
                    "oblique": safe_get(st.dxf, "oblique"),
                }
            )
    except Exception:
        pass

    dim_styles = []
    try:
        for ds in doc.dimstyles:
            dim_styles.append(
                {
                    "name": safe_get(ds.dxf, "name"),
                    "dimtxt": safe_get(ds.dxf, "dimtxt"),
                    "dimscale": safe_get(ds.dxf, "dimscale"),
                    "dimasz": safe_get(ds.dxf, "dimasz"),
                    "dimexe": safe_get(ds.dxf, "dimexe"),
                }
            )
    except Exception:
        pass

    appid_table = []
    try:
        for a in doc.appids:
            appid_table.append({"name": safe_get(a.dxf, "name")})
    except Exception:
        pass

    ucs_table = []
    try:
        for u in doc.ucs:
            ucs_table.append(
                {
                    "name": safe_get(u.dxf, "name"),
                    "origin": vector(safe_get(u.dxf, "origin")),
                    "xaxis": vector(safe_get(u.dxf, "xaxis")),
                    "yaxis": vector(safe_get(u.dxf, "yaxis")),
                }
            )
    except Exception:
        pass

    views_table = []
    try:
        for v in doc.views:
            views_table.append(
                {
                    "name": safe_get(v.dxf, "name"),
                    "center": vector(safe_get(v.dxf, "center")),
                    "height": safe_get(v.dxf, "height"),
                    "width": safe_get(v.dxf, "width"),
                }
            )
    except Exception:
        pass

    vports_table = []
    try:
        for vp in doc.viewports:
            vports_table.append(
                {
                    "name": safe_get(vp.dxf, "name"),
                    "center": vector(safe_get(vp.dxf, "center")),
                    "height": safe_get(vp.dxf, "height"),
                    "aspect_ratio": safe_get(vp.dxf, "aspect_ratio"),
                }
            )
    except Exception:
        pass

    # Specialty entity extracts
    specialty_types = {
        "DIMENSION",
        "ALIGNED_DIMENSION",
        "LINEAR_DIMENSION",
        "RADIAL_DIMENSION",
        "DIAMETER_DIMENSION",
        "ANGULAR_DIMENSION",
        "ORDINATE_DIMENSION",
        "ARC_DIMENSION",
        "LEADER",
        "MLEADER",
        "MULTILEADER",
        "HATCH",
        "SOLID",
        "TRACE",
        "IMAGE",
        "WIPEOUT",
        "UNDERLAY",
        "PDFUNDERLAY",
        "DWFUNDERLAY",
        "DGNUNDERLAY",
        "ACAD_TABLE",
        "TABLE",
        "TOLERANCE",
        "SHAPE",
        "BODY",
        "3DSOLID",
        "REGION",
        "SURFACE",
        "MESH",
        "HELIX",
        "LIGHT",
        "CAMERA",
        "SECTION",
        "MLINE",
        "XLINE",
        "RAY",
        "POINT",
        "PROXY",
        "ACAD_PROXY_ENTITY",
    }
    specialty_entities = [e for e in all_entities if e.get("type") in specialty_types or "DIMENSION" in str(e.get("type", "")).upper() or "LEADER" in str(e.get("type", "")).upper() or "UNDERLAY" in str(e.get("type", "")).upper() or "PROXY" in str(e.get("type", "")).upper()]

    # XREFs / block external refs
    xrefs = []
    try:
        for block in doc.blocks:
            try:
                if getattr(block, "is_xref", False) or getattr(block, "xref_path", None):
                    xrefs.append(
                        {
                            "name": block.name,
                            "xref_path": getattr(block, "xref_path", None) or safe_get(block.block.dxf, "xref_path"),
                            "is_xref": bool(getattr(block, "is_xref", False)),
                            "is_dxf_xref": bool(getattr(block, "is_dxf_xref", False)),
                        }
                    )
            except Exception:
                continue
    except Exception:
        pass

    # Groups
    groups = []
    try:
        for name, group in doc.groups:
            handles = []
            try:
                handles = [safe_get(e.dxf, "handle") for e in group]
            except Exception:
                pass
            groups.append({"name": name, "entity_handles": handles, "count": len(handles)})
    except Exception:
        try:
            # older API
            for group in doc.groups:
                groups.append({"name": str(group), "entity_handles": [], "count": 0})
        except Exception:
            pass

    # Title block / drawing metadata from insert attributes
    title_block_fields = []
    title_keys = {
        "TITLE1", "TITLE2", "TITLE3", "PROJECT1", "PROJECT2", "PROJECT3", "DRAWINGID",
        "SHEET", "LYH", "CAD", "ARKKI", "TUNNUS", "SROIK", "SRVAS", "INF1", "INF2",
        "INF3", "INF4", "INF5", "INF6", "INF14", "MRK", "MRK2", "PVM", "PVM2", "TAR",
        "TAR2", "MUU", "MUU2", "MUUTOS", "MUUTOS2", "KPL",
    }
    for ins in inserts:
        attrs = {a.get("tag"): a.get("text") for a in ins.get("attributes", []) if a.get("tag")}
        hits = {k: v for k, v in attrs.items() if k in title_keys and v}
        if hits:
            title_block_fields.append(
                {
                    "block_name": ins.get("name"),
                    "handle": ins.get("handle"),
                    "layer": ins.get("layer"),
                    "insert": ins.get("insert"),
                    "fields": hits,
                }
            )

    # Layout detail enrichment
    layout_details = []
    for layout in doc.layouts:
        detail = {
            "name": layout.name,
            "is_modelspace": bool(layout.name.upper() == "MODEL"),
            "entity_count": 0,
            "plot_layout_flags": safe_get(getattr(layout, "dxf", None), "plot_layout_flags") if hasattr(layout, "dxf") else None,
        }
        try:
            detail["entity_count"] = len(layout)
        except Exception:
            pass
        try:
            detail["plot_paper_size"] = str(getattr(layout, "get_plot_paper_size", lambda: None)())
        except Exception:
            pass
        layout_details.append(detail)

    result = {
        "backend": backend,
        "doc": {
            "dxfversion": doc.dxfversion,
            "acad_release": doc.acad_release,
            "units": header_vars.get("$INSUNITS"),
            "extmin": header_vars.get("$EXTMIN"),
            "extmax": header_vars.get("$EXTMAX"),
            "limmin": header_vars.get("$LIMMIN"),
            "limmax": header_vars.get("$LIMMAX"),
        },
        "header_variables": header_vars,
        "layouts": layouts,
        "layout_details": layout_details,
        "layers": layers,
        "layer_entity_type_counts": layer_entity_hist,
        "linetypes": linetypes,
        "text_styles": text_styles,
        "dim_styles": dim_styles,
        "appids": appid_table,
        "ucs_table": ucs_table,
        "views_table": views_table,
        "vports_table": vports_table,
        "groups": groups,
        "xrefs": xrefs,
        "blocks": block_defs,
        "block_hierarchy": block_hierarchy,
        "inserts": inserts,
        "entities": all_entities,
        "paperspace_entities": paperspace_entities,
        "specialty_entities": specialty_entities,
        "text_entities": texts,
        "attribute_inventory": tags,
        "title_block_fields": title_block_fields,
        "eed_xdata_dump": eed_xdata_dump,
        "pid_graph_candidates": pid_graph,
        "counts": {
            "layers": len(layers),
            "blocks": len(block_defs),
            "inserts": len(inserts),
            "entities_total": len(all_entities),
            "text_entities": len(texts),
            "attributes": len(tags),
            "eed_xdata_records": len(eed_xdata_dump),
            "graph_nodes": pid_graph["counts"]["nodes"],
            "graph_edges": pid_graph["counts"]["edges"],
            "graph_junctions": pid_graph["counts"]["junctions"],
            "linetypes": len(linetypes),
            "text_styles": len(text_styles),
            "dim_styles": len(dim_styles),
            "appids": len(appid_table),
            "groups": len(groups),
            "xrefs": len(xrefs),
            "specialty_entities": len(specialty_entities),
            "title_block_records": len(title_block_fields),
        },
    }
    return result, ""


def parse_with_aspose(path: Path) -> Tuple[Optional[Dict[str, Any]], str]:
    try:
        import aspose.cad as cad  # type: ignore
    except Exception as e:
        return None, f"aspose.cad import failed: {e}"

    if path.suffix.lower() not in (".dwg", ".dxf"):
        return None, "aspose backend supports DWG/DXF only"

    try:
        image = cad.Image.load(str(path))
    except Exception as e:
        return None, f"Aspose load failed: {e}"

    try:
        cad_image = image
        header = {}
        try:
            hdr = cad_image.header
            header["has_header"] = hdr is not None
            summary = getattr(hdr, "summary_info", None)
            if summary is not None:
                header["summary_info"] = str(summary)
        except Exception:
            pass

        layers = []
        try:
            for layer in cad_image.layers:
                layers.append(
                    {
                        "name": str(getattr(layer, "name", None)),
                        "color_id": getattr(layer, "color_id", None),
                        "line_weight": getattr(layer, "line_weight", None),
                        "is_layer_on": getattr(layer, "is_layer_on", None),
                        "is_frozen": getattr(layer, "is_frozen", None),
                        "is_locked": getattr(layer, "is_locked", None),
                    }
                )
        except Exception:
            pass

        entities = []
        inserts = []
        texts = []
        attrs = []
        entity_type_counts: Dict[str, int] = {}

        try:
            for ent in cad_image.entities:
                tname = str(getattr(ent, "type_name", "UNKNOWN"))
                handle = getattr(ent, "object_handle", None)
                layer = getattr(ent, "layer_name", None)
                item = {
                    "type": tname,
                    "handle": str(handle) if handle is not None else None,
                    "layer": str(layer) if layer is not None else None,
                    "visible": getattr(ent, "visible", None),
                    "color_id": getattr(ent, "color_id", None),
                    "linetype_name": str(getattr(ent, "line_type_name", "")) if getattr(ent, "line_type_name", None) is not None else None,
                    "raw_str": str(ent),
                }
                entities.append(item)
                entity_type_counts[tname] = entity_type_counts.get(tname, 0) + 1

                up = tname.upper()
                if "INSERT" in up:
                    inserts.append(item)
                if "TEXT" in up:
                    texts.append(item)
                if "ATTRIB" in up:
                    attrs.append(item)
        except Exception:
            pass

        # Aspose does not expose the same DXF-centric geometry API shape as ezdxf,
        # so we retain robust object-level dumps via string serialization for now.
        graph = infer_pid_nodes_edges(
            entities=[{
                "type": e["type"],
                "handle": e["handle"],
                "layer": e["layer"],
                "owner_space": "MODEL",
                "geometry": {},
            } for e in entities],
            inserts=[{
                "handle": i["handle"],
                "name": i["type"],
                "insert": None,
                "layer": i["layer"],
                "attributes": [],
            } for i in inserts],
            texts=[{
                "handle": t["handle"],
                "type": t["type"],
                "text": t["raw_str"],
                "layer": t["layer"],
                "position": None,
            } for t in texts],
            attrs=[],
        )

        result = {
            "backend": "aspose-cad:direct-dwg",
            "doc": {
                "format": path.suffix.lower().lstrip("."),
                "dxfversion": None,
                "acad_release": None,
                "units": None,
                "extmin": None,
                "extmax": None,
                "limmin": None,
                "limmax": None,
            },
            "header_variables": header,
            "layouts": [],
            "layers": layers,
            "layer_entity_type_counts": {},
            "blocks": [],
            "block_hierarchy": [],
            "inserts": inserts,
            "entities": entities,
            "paperspace_entities": [],
            "text_entities": texts,
            "attribute_inventory": attrs,
            "eed_xdata_dump": [],
            "pid_graph_candidates": graph,
            "counts": {
                "layers": len(layers),
                "blocks": 0,
                "inserts": len(inserts),
                "entities_total": len(entities),
                "text_entities": len(texts),
                "attributes": len(attrs),
                "eed_xdata_records": 0,
                "graph_nodes": graph["counts"]["nodes"],
                "graph_edges": graph["counts"]["edges"],
                "graph_junctions": graph["counts"]["junctions"],
                "entity_type_buckets": entity_type_counts,
            },
        }
        return result, ""
    finally:
        try:
            image.dispose()
        except Exception:
            pass


def flatten_record(record: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Flatten one-level nested dict/list values into JSON strings for tabular export."""
    row: Dict[str, Any] = {}
    for key, val in record.items():
        col = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(val, dict):
            if val:
                row[col] = json.dumps(json_safe(val), ensure_ascii=True)
            else:
                row[col] = ""
        elif isinstance(val, list):
            if val and isinstance(val[0], dict):
                row[col] = json.dumps(json_safe(val), ensure_ascii=True)
            elif val:
                row[col] = json.dumps(json_safe(val), ensure_ascii=True)
            else:
                row[col] = ""
        else:
            row[col] = json_safe(val)
    return row


def records_to_rows(records: Any) -> List[Dict[str, Any]]:
    if not records:
        return []
    if isinstance(records, dict):
        # dict of dicts (e.g. layer_entity_type_counts) -> long format
        if records and all(isinstance(v, dict) for v in records.values()):
            rows = []
            for outer_key, inner in records.items():
                for inner_key, count in inner.items():
                    rows.append({"layer": outer_key, "entity_type": inner_key, "count": count})
            return rows
        return [{"key": k, "value": json.dumps(json_safe(v), ensure_ascii=True)} for k, v in records.items()]
    if isinstance(records, list):
        if records and isinstance(records[0], dict):
            return [flatten_record(r) for r in records]
        return [{"value": json_safe(v)} for v in records]
    return [{"value": json_safe(records)}]


def export_full_workbook(
    out_path: Path,
    structural: Optional[Dict[str, Any]] = None,
    forensic: Optional[Dict[str, Any]] = None,
) -> None:
    """Write one Excel workbook with all data sections as separate sheets."""
    import pandas as pd

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        if structural:
            graph = structural.get("pid_graph_candidates") or {}
            sheets: Dict[str, List[Dict[str, Any]]] = {
                "summary": [
                    {
                        "backend": structural.get("backend"),
                        **(structural.get("doc") or {}),
                        **(structural.get("counts") or {}),
                    }
                ],
                "header_variables": records_to_rows(structural.get("header_variables")),
                "layouts": records_to_rows(structural.get("layouts")),
                "layers": records_to_rows(structural.get("layers")),
                "layer_entity_counts": records_to_rows(structural.get("layer_entity_type_counts")),
                "blocks_summary": records_to_rows(
                    [
                        {
                            "name": b.get("name"),
                            "base_point": b.get("base_point"),
                            "units": b.get("units"),
                            "entity_count": b.get("entity_count"),
                        }
                        for b in (structural.get("blocks") or [])
                    ]
                ),
                "block_hierarchy": records_to_rows(structural.get("block_hierarchy")),
                "entities": records_to_rows(structural.get("entities")),
                "paperspace_entities": records_to_rows(structural.get("paperspace_entities")),
                "inserts": records_to_rows(structural.get("inserts")),
                "text_entities": records_to_rows(structural.get("text_entities")),
                "attributes": records_to_rows(structural.get("attribute_inventory")),
                "eed_xdata": records_to_rows(structural.get("eed_xdata_dump")),
                "graph_nodes": records_to_rows(graph.get("nodes")),
                "graph_edges": records_to_rows(graph.get("edges")),
                "graph_junctions": records_to_rows(graph.get("junctions")),
                "linetypes": records_to_rows(structural.get("linetypes")),
                "text_styles": records_to_rows(structural.get("text_styles")),
                "dim_styles": records_to_rows(structural.get("dim_styles")),
                "appids": records_to_rows(structural.get("appids")),
                "ucs_table": records_to_rows(structural.get("ucs_table")),
                "views_table": records_to_rows(structural.get("views_table")),
                "vports_table": records_to_rows(structural.get("vports_table")),
                "groups": records_to_rows(structural.get("groups")),
                "xrefs": records_to_rows(structural.get("xrefs")),
                "specialty_entities": records_to_rows(structural.get("specialty_entities")),
                "title_block_fields": records_to_rows(structural.get("title_block_fields")),
                "layout_details": records_to_rows(structural.get("layout_details")),
            }
            for sheet_name, rows in sheets.items():
                pd.DataFrame(rows if rows else [{"note": "empty"}]).to_excel(
                    writer, sheet_name=sheet_name[:31], index=False
                )

        if forensic:
            ascii_rows = forensic.get("extracted_strings", {}).get("ascii_strings_with_offsets", [])
            utf16_rows = forensic.get("extracted_strings", {}).get("utf16le_strings_with_offsets", [])
            semantic = forensic.get("semantic_candidates") or {}
            pd.DataFrame([forensic.get("file", {})]).to_excel(writer, sheet_name="forensic_file", index=False)
            pd.DataFrame(ascii_rows).to_excel(writer, sheet_name="ascii_strings", index=False)
            pd.DataFrame(utf16_rows).to_excel(writer, sheet_name="utf16_strings", index=False)
            for key, values in semantic.items():
                pd.DataFrame({"value": values}).to_excel(
                    writer, sheet_name=f"semantic_{key[:20]}"[:31], index=False
                )


def build_forensic_dump(path: Path, out_dir: Path) -> Dict[str, Any]:
    data = path.read_bytes()
    base = safe_name(path)

    ascii_strings = extract_ascii_strings_with_offsets(data)
    utf16_strings = extract_utf16le_strings_with_offsets(data)

    ascii_tokens = [x["text"] for x in ascii_strings]
    utf16_tokens = [x["text"] for x in utf16_strings]
    all_tokens = ascii_tokens + utf16_tokens

    candidates = classify_token_candidates(all_tokens)
    embedded_pngs = maybe_extract_embedded_png(data, out_dir, base)

    forensic = {
        "file": {
            "path": str(path.resolve()),
            "name": path.name,
            "size_bytes": len(data),
            "sha256": sha256_bytes(data),
            "entropy_bits_per_byte": shannon_entropy(data),
            "magic_ascii_6": data[:6].decode("ascii", errors="replace"),
            "magic_hex_8": data[:8].hex(),
            "extension": path.suffix.lower(),
        },
        "binary_signals": {
            "contains_png_markers": all(marker in data for marker in (b"IHDR", b"IDAT", b"IEND")),
            "contains_thumbnail_data_marker": b"Thumbnail_Data" in data,
            "contains_acdb_marker": b"AcDb" in data,
            "contains_acds_marker": b"AcDs" in data,
            "contains_teigha_marker": b"Teigha" in data or b"Open Design Alliance" in data,
        },
        "extracted_strings": {
            "ascii_count": len(ascii_strings),
            "utf16le_count": len(utf16_strings),
            "ascii_strings_with_offsets": ascii_strings,
            "utf16le_strings_with_offsets": utf16_strings,
        },
        "semantic_candidates": candidates,
        "embedded_png_files": embedded_pngs,
    }
    return forensic


def main() -> int:
    parser = argparse.ArgumentParser(description="Forensic DWG/DXF pure dumper.")
    parser.add_argument("--input", required=True, help="Input DWG or DXF path.")
    parser.add_argument("--output-dir", default="outputs", help="Output directory.")
    parser.add_argument(
        "--skip-structural",
        action="store_true",
        help="Skip structural parser attempts; binary dump only.",
    )
    parser.add_argument(
        "--skip-forensic",
        action="store_true",
        help="Skip binary forensic pass; structural parse only.",
    )
    parser.add_argument(
        "--enable-aspose-fallback",
        action="store_true",
        help="Enable Aspose fallback when ezdxf/odafc structural parsing fails.",
    )
    parser.add_argument(
        "--write-json",
        action="store_true",
        help="Write pipeline dump JSON (structural + forensic). Excel remains the deliverable.",
    )
    parser.add_argument(
        "--write-json-splits",
        action="store_true",
        help="Also write per-section dump JSON (layers/blocks/entities/…). Implies --write-json.",
    )
    parser.add_argument(
        "--no-workbook",
        action="store_true",
        help="Skip Excel workbook export.",
    )
    parser.add_argument(
        "--no-clean-prev",
        action="store_true",
        help="Keep previous outputs for this drawing instead of clearing them first.",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    base = safe_name(input_path)
    if not args.no_clean_prev:
        clear_previous_outputs(out_dir, base)

    write_workbook = not args.no_workbook
    write_json_files = bool(args.write_json or args.write_json_splits)
    write_json_splits = bool(args.write_json_splits)

    configure_odafc()

    print(f"[1/5] Loaded file: {input_path}")
    forensic_out = json_path(out_dir, f"{base}.pure_forensic_dump.json")
    forensic = None
    if not args.skip_forensic:
        forensic = build_forensic_dump(input_path, out_dir)
        if write_json_files:
            write_json(forensic_out, forensic)
            print(f"[2/5] Wrote forensic JSON: {forensic_out}")
        else:
            print("[2/5] Skipped forensic JSON (use --write-json to enable)")
    else:
        print("[2/5] Skipped forensic dump by flag")

    structural = None
    structural_error = None
    if not args.skip_structural:
        structural, structural_error = parse_with_ezdxf(input_path)
        if structural is None and args.enable_aspose_fallback:
            asp_structural, asp_error = parse_with_aspose(input_path)
            if asp_structural is not None:
                structural = asp_structural
                structural_error = None
            else:
                if structural_error:
                    structural_error = f"{structural_error}; fallback_aspose_failed: {asp_error}"
                else:
                    structural_error = asp_error

    workbook_out = out_dir / f"{base}.full_dump.xlsx"

    if structural is not None:
        if write_json_files:
            structural_out = json_path(out_dir, f"{base}.structural_dump.json")
            write_json(structural_out, structural)
            print(f"[3/5] Wrote structural dump JSON: {structural_out}")
            if write_json_splits:
                split_map = {
                    "layers": structural.get("layers"),
                    "blocks": structural.get("blocks"),
                    "entities": structural.get("entities"),
                    "attribute_inventory": structural.get("attribute_inventory"),
                    "text_entities": structural.get("text_entities"),
                    "eed_xdata_dump": structural.get("eed_xdata_dump"),
                    "pid_graph_candidates": structural.get("pid_graph_candidates"),
                    "layer_entity_type_counts": structural.get("layer_entity_type_counts"),
                    "inserts": structural.get("inserts"),
                }
                for key, payload in split_map.items():
                    write_json(json_path(out_dir, f"{base}.{key}.json"), payload)
                print("[3/5] Wrote JSON structural split dumps")
        else:
            print("[3/5] Skipped JSON structural dumps (use --write-json to enable)")
    else:
        print(f"[3/5] Structural dump unavailable: {structural_error}")

    if write_workbook and (structural is not None or forensic is not None):
        export_full_workbook(workbook_out, structural=structural, forensic=forensic)
        print(f"[4/5] Wrote workbook: {workbook_out}")
    elif write_workbook:
        print("[4/5] Workbook skipped (no data to export)")
    else:
        print("[4/5] Workbook export disabled")

    structural_json_path = json_path(out_dir, f"{base}.structural_dump.json")
    manifest = {
        "input_file": str(input_path),
        "workbook": str(workbook_out) if write_workbook and workbook_out.exists() else None,
        "forensic_json": str(forensic_out) if write_json_files and forensic is not None else None,
        "structural_json": str(structural_json_path) if write_json_files and structural is not None else None,
        "structural_error": structural_error,
        "evidence_dir": str(evidence_dir(out_dir)),
        "jsons_dir": str(jsons_dir(out_dir)),
        "logs_dir": str(logs_dir(out_dir)),
    }
    manifest_out = json_path(out_dir, f"{base}.dump_manifest.json")
    write_json(manifest_out, manifest)
    print(f"[5/5] Wrote manifest: {manifest_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

