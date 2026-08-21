"""Split ezdxf structural dump into named collectors.

``parse_with_ezdxf`` in ``dwg_pure_dump`` delegates here so the CAD walk is
testable in pieces without a 500-line function.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dwg_reader.logutil import dxf_probe_failed

# Imported lazily inside collectors that need dump helpers to avoid a cycle
# at module import time (dump.main → parse_with_ezdxf → this module).


def open_ezdxf_document(path: Path) -> Tuple[Optional[Any], str, str]:
    """Open a DXF/DWG via ezdxf. Returns ``(doc, backend, error)``."""
    from dwg_reader.dwg_pure_dump import configure_odafc

    try:
        import ezdxf  # type: ignore
    except Exception as e:
        return None, "", f"ezdxf import failed: {e}"

    ext = path.suffix.lower()
    if ext == ".dxf":
        try:
            return ezdxf.readfile(path), "ezdxf:dxf-direct", ""
        except Exception as e:
            return None, "", f"DXF parse failed: {e}"
    if ext != ".dwg":
        return None, "", f"Unsupported extension: {ext}"
    try:
        from ezdxf.addons import odafc  # type: ignore
    except Exception as e:
        return None, "", f"ezdxf.odafc unavailable: {e}"
    try:
        oda_path = configure_odafc()
        if not odafc.is_installed():
            return None, "", (
                "odafc not installed; cannot parse DWG structurally. "
                "Install ODA File Converter or set ODA_FILE_CONVERTER env var."
            )
        return odafc.readfile(str(path)), f"ezdxf:odafc-dwg ({oda_path})", ""
    except Exception as e:
        return None, "", f"DWG parse via odafc failed: {e}"


def header_vars(doc: Any) -> Dict[str, Any]:
    from dwg_reader.dwg_pure_dump import vector

    out: Dict[str, Any] = {}
    for key in doc.header.varnames():
        try:
            val = doc.header.get(key)
            if hasattr(val, "x") and hasattr(val, "y"):
                out[key] = vector(val)
            else:
                out[key] = val
        except Exception as e:
            dxf_probe_failed(e, key)
            out[key] = str(doc.header.get(key, ""))
    return out


def layout_summaries(doc: Any) -> List[Dict[str, Any]]:
    return [
        {
            "name": layout.name,
            "taborder": getattr(layout, "taborder", None),
            "is_modelspace": bool(layout.name.upper() == "MODEL"),
        }
        for layout in doc.layouts
    ]


def layer_table(doc: Any) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, int]]]:
    from dwg_reader.dwg_pure_dump import safe_get

    layers: List[Dict[str, Any]] = []
    hist: Dict[str, Dict[str, int]] = {}
    for layer in doc.layers:
        layers.append(
            {
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
        )
        hist[layer.dxf.name] = {}
    return layers, hist


def block_table(doc: Any) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    from dwg_reader.dwg_pure_dump import dump_entity, safe_get, vector

    block_defs: List[Dict[str, Any]] = []
    block_hierarchy: List[Dict[str, Any]] = []
    for block in doc.blocks:
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
    return block_defs, block_hierarchy


def _bump_layer_hist(hist: Dict[str, Dict[str, int]], rec: Dict[str, Any]) -> None:
    lyr = rec.get("layer")
    if lyr in hist:
        t = rec["type"]
        hist[lyr][t] = hist[lyr].get(t, 0) + 1


def insert_record(entity: Any) -> Dict[str, Any]:
    from dwg_reader.dwg_pure_dump import safe_get, vector

    attrs: List[Dict[str, Any]] = []
    try:
        for a in entity.attribs:
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
    except Exception as e:
        dxf_probe_failed(e, "INSERT attribs")
    return {
        "handle": safe_get(entity.dxf, "handle"),
        "name": safe_get(entity.dxf, "name"),
        "insert": vector(safe_get(entity.dxf, "insert")),
        "xscale": safe_get(entity.dxf, "xscale", 1.0),
        "yscale": safe_get(entity.dxf, "yscale", 1.0),
        "zscale": safe_get(entity.dxf, "zscale", 1.0),
        "rotation": safe_get(entity.dxf, "rotation", 0.0),
        "layer": safe_get(entity.dxf, "layer"),
        "attributes": attrs,
    }


def model_and_paper_entities(
    doc: Any, layer_entity_hist: Dict[str, Dict[str, int]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    from dwg_reader.dwg_pure_dump import dump_entity

    all_entities: List[Dict[str, Any]] = []
    inserts: List[Dict[str, Any]] = []
    for e in doc.modelspace():
        rec = dump_entity(e, owner_space="MODEL")
        all_entities.append(rec)
        _bump_layer_hist(layer_entity_hist, rec)
        if e.dxftype() == "INSERT":
            inserts.append(insert_record(e))

    paperspace_entities: List[Dict[str, Any]] = []
    for layout in doc.layouts:
        if layout.name.upper() == "MODEL":
            continue
        for e in layout:
            rec = dump_entity(e, owner_space=f"PAPER:{layout.name}")
            paperspace_entities.append(rec)
            all_entities.append(rec)
            _bump_layer_hist(layer_entity_hist, rec)
    return all_entities, inserts, paperspace_entities


def text_entities(all_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    texts: List[Dict[str, Any]] = []
    for rec in all_entities:
        if rec["type"] not in ("TEXT", "MTEXT"):
            continue
        texts.append(
            {
                "handle": rec["handle"],
                "type": rec["type"],
                "text": rec["geometry"].get("text"),
                "layer": rec["layer"],
                "rotation": rec["geometry"].get("rotation"),
                "height": rec["geometry"].get("height") or rec["geometry"].get("char_height"),
                "position": rec["geometry"].get("insert"),
            }
        )
    return texts


def attribute_inventory(inserts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    tags: List[Dict[str, Any]] = []
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
    return tags


def eed_xdata_dump(doc: Any) -> List[Dict[str, Any]]:
    from dwg_reader.dwg_pure_dump import safe_get, try_get_xdata

    try:
        appids = [a.dxf.name for a in doc.appids]
    except Exception as e:
        dxf_probe_failed(e, "appids")
        appids = []
    source_entities = [("MODEL", e) for e in doc.modelspace()]
    for layout in doc.layouts:
        if layout.name.upper() == "MODEL":
            continue
        source_entities.extend((f"PAPER:{layout.name}", e) for e in layout)
    dump: List[Dict[str, Any]] = []
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
            dump.append(ext)
    return dump


def _try_table(name: str, iterator: Any, row_fn: Any) -> List[Any]:
    rows: List[Any] = []
    try:
        for item in iterator:
            rows.append(row_fn(item))
    except Exception as e:
        dxf_probe_failed(e, name)
    return rows


def symbol_tables(doc: Any) -> Dict[str, List[Any]]:
    from dwg_reader.dwg_pure_dump import safe_get, vector

    return {
        "linetypes": _try_table(
            "linetypes",
            doc.linetypes,
            lambda lt: {
                "name": safe_get(lt.dxf, "name"),
                "description": safe_get(lt.dxf, "description"),
                "length": safe_get(lt.dxf, "length"),
            },
        ),
        "text_styles": _try_table(
            "styles",
            doc.styles,
            lambda st: {
                "name": safe_get(st.dxf, "name"),
                "font": safe_get(st.dxf, "font"),
                "bigfont": safe_get(st.dxf, "bigfont"),
                "height": safe_get(st.dxf, "height"),
                "width": safe_get(st.dxf, "width"),
                "oblique": safe_get(st.dxf, "oblique"),
            },
        ),
        "dim_styles": _try_table(
            "dimstyles",
            doc.dimstyles,
            lambda ds: {
                "name": safe_get(ds.dxf, "name"),
                "dimtxt": safe_get(ds.dxf, "dimtxt"),
                "dimscale": safe_get(ds.dxf, "dimscale"),
                "dimasz": safe_get(ds.dxf, "dimasz"),
                "dimexe": safe_get(ds.dxf, "dimexe"),
            },
        ),
        "appids": _try_table("appids", doc.appids, lambda a: {"name": safe_get(a.dxf, "name")}),
        "ucs_table": _try_table(
            "ucs",
            doc.ucs,
            lambda u: {
                "name": safe_get(u.dxf, "name"),
                "origin": vector(safe_get(u.dxf, "origin")),
                "xaxis": vector(safe_get(u.dxf, "xaxis")),
                "yaxis": vector(safe_get(u.dxf, "yaxis")),
            },
        ),
        "views_table": _try_table(
            "views",
            doc.views,
            lambda v: {
                "name": safe_get(v.dxf, "name"),
                "center": vector(safe_get(v.dxf, "center")),
                "height": safe_get(v.dxf, "height"),
                "width": safe_get(v.dxf, "width"),
            },
        ),
        "vports_table": _try_table(
            "viewports",
            doc.viewports,
            lambda vp: {
                "name": safe_get(vp.dxf, "name"),
                "center": vector(safe_get(vp.dxf, "center")),
                "height": safe_get(vp.dxf, "height"),
                "aspect_ratio": safe_get(vp.dxf, "aspect_ratio"),
            },
        ),
    }


_SPECIALTY_TYPES = {
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


def specialty_entities(all_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for e in all_entities:
        t = str(e.get("type", "")).upper()
        if e.get("type") in _SPECIALTY_TYPES or any(
            k in t for k in ("DIMENSION", "LEADER", "UNDERLAY", "PROXY")
        ):
            out.append(e)
    return out


def xrefs(doc: Any) -> List[Dict[str, Any]]:
    from dwg_reader.dwg_pure_dump import safe_get

    found: List[Dict[str, Any]] = []
    try:
        for block in doc.blocks:
            try:
                if getattr(block, "is_xref", False) or getattr(block, "xref_path", None):
                    found.append(
                        {
                            "name": block.name,
                            "xref_path": getattr(block, "xref_path", None)
                            or safe_get(block.block.dxf, "xref_path"),
                            "is_xref": bool(getattr(block, "is_xref", False)),
                            "is_dxf_xref": bool(getattr(block, "is_dxf_xref", False)),
                        }
                    )
            except Exception as e:
                dxf_probe_failed(e, f"xref:{getattr(block, 'name', '?')}")
                continue
    except Exception as e:
        dxf_probe_failed(e, "blocks/xrefs")
    return found


def groups(doc: Any) -> List[Dict[str, Any]]:
    from dwg_reader.dwg_pure_dump import safe_get

    found: List[Dict[str, Any]] = []
    try:
        for name, group in doc.groups:
            handles = []
            try:
                handles = [safe_get(e.dxf, "handle") for e in group]
            except Exception as e:
                dxf_probe_failed(e, f"group:{name}")
            found.append({"name": name, "entity_handles": handles, "count": len(handles)})
    except Exception as e:
        dxf_probe_failed(e, "groups")
        try:
            for group in doc.groups:
                found.append({"name": str(group), "entity_handles": [], "count": 0})
        except Exception as e2:
            dxf_probe_failed(e2, "groups-legacy")
    return found


_TITLE_KEYS = {
    "TITLE1", "TITLE2", "TITLE3", "PROJECT1", "PROJECT2", "PROJECT3", "DRAWINGID",
    "SHEET", "LYH", "CAD", "ARKKI", "TUNNUS", "SROIK", "SRVAS", "INF1", "INF2",
    "INF3", "INF4", "INF5", "INF6", "INF14", "MRK", "MRK2", "PVM", "PVM2", "TAR",
    "TAR2", "MUU", "MUU2", "MUUTOS", "MUUTOS2", "KPL",
}


def title_block_fields(inserts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    fields: List[Dict[str, Any]] = []
    for ins in inserts:
        attrs = {a.get("tag"): a.get("text") for a in ins.get("attributes", []) if a.get("tag")}
        hits = {k: v for k, v in attrs.items() if k in _TITLE_KEYS and v}
        if hits:
            fields.append(
                {
                    "block_name": ins.get("name"),
                    "handle": ins.get("handle"),
                    "layer": ins.get("layer"),
                    "insert": ins.get("insert"),
                    "fields": hits,
                }
            )
    return fields


def layout_details(doc: Any) -> List[Dict[str, Any]]:
    from dwg_reader.dwg_pure_dump import safe_get

    details: List[Dict[str, Any]] = []
    for layout in doc.layouts:
        detail: Dict[str, Any] = {
            "name": layout.name,
            "is_modelspace": bool(layout.name.upper() == "MODEL"),
            "entity_count": 0,
            "plot_layout_flags": safe_get(getattr(layout, "dxf", None), "plot_layout_flags")
            if hasattr(layout, "dxf")
            else None,
        }
        try:
            detail["entity_count"] = len(layout)
        except Exception as e:
            dxf_probe_failed(e, f"layout.len:{layout.name}")
        try:
            detail["plot_paper_size"] = str(getattr(layout, "get_plot_paper_size", lambda: None)())
        except Exception as e:
            dxf_probe_failed(e, f"layout.plot:{layout.name}")
        details.append(detail)
    return details


def parse_ezdxf_document(path: Path) -> Tuple[Optional[Dict[str, Any]], str]:
    from dwg_reader.dwg_pure_dump import infer_pid_nodes_edges

    doc, backend, err = open_ezdxf_document(path)
    if doc is None:
        return None, err

    hv = header_vars(doc)
    layouts = layout_summaries(doc)
    layers, layer_entity_hist = layer_table(doc)
    block_defs, block_hierarchy = block_table(doc)
    all_entities, inserts, paperspace_entities = model_and_paper_entities(doc, layer_entity_hist)
    texts = text_entities(all_entities)
    tags = attribute_inventory(inserts)
    eed = eed_xdata_dump(doc)
    pid_graph = infer_pid_nodes_edges(all_entities, inserts, texts, tags)
    tables = symbol_tables(doc)
    specialty = specialty_entities(all_entities)
    xref_rows = xrefs(doc)
    group_rows = groups(doc)
    title_fields = title_block_fields(inserts)
    details = layout_details(doc)

    result = {
        "backend": backend,
        "doc": {
            "dxfversion": doc.dxfversion,
            "acad_release": doc.acad_release,
            "units": hv.get("$INSUNITS"),
            "extmin": hv.get("$EXTMIN"),
            "extmax": hv.get("$EXTMAX"),
            "limmin": hv.get("$LIMMIN"),
            "limmax": hv.get("$LIMMAX"),
        },
        "header_variables": hv,
        "layouts": layouts,
        "layout_details": details,
        "layers": layers,
        "layer_entity_type_counts": layer_entity_hist,
        "linetypes": tables["linetypes"],
        "text_styles": tables["text_styles"],
        "dim_styles": tables["dim_styles"],
        "appids": tables["appids"],
        "ucs_table": tables["ucs_table"],
        "views_table": tables["views_table"],
        "vports_table": tables["vports_table"],
        "groups": group_rows,
        "xrefs": xref_rows,
        "blocks": block_defs,
        "block_hierarchy": block_hierarchy,
        "inserts": inserts,
        "entities": all_entities,
        "paperspace_entities": paperspace_entities,
        "specialty_entities": specialty,
        "text_entities": texts,
        "attribute_inventory": tags,
        "title_block_fields": title_fields,
        "eed_xdata_dump": eed,
        "pid_graph_candidates": pid_graph,
        "counts": {
            "layers": len(layers),
            "blocks": len(block_defs),
            "inserts": len(inserts),
            "entities_total": len(all_entities),
            "text_entities": len(texts),
            "attributes": len(tags),
            "eed_xdata_records": len(eed),
            "graph_nodes": pid_graph["counts"]["nodes"],
            "graph_edges": pid_graph["counts"]["edges"],
            "graph_junctions": pid_graph["counts"]["junctions"],
            "linetypes": len(tables["linetypes"]),
            "text_styles": len(tables["text_styles"]),
            "dim_styles": len(tables["dim_styles"]),
            "appids": len(tables["appids"]),
            "groups": len(group_rows),
            "xrefs": len(xref_rows),
            "specialty_entities": len(specialty),
            "title_block_records": len(title_fields),
        },
    }
    return result, ""
