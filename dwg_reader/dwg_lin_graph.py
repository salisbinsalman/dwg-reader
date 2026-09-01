#!/usr/bin/env python3
"""Parse Valmet PCAD LIN_FROM / LIN_TO XDATA into a directed tag graph (R27/B04)."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Set, Tuple

from dwg_reader.tags import normalize_tag

# 35-24P519, 35-24L009, 35-24-137, 35-24L009.1, 35-24-009.1
_TAG_RE = re.compile(r"\d{2}-\d{2}(?:[A-Z]+\d+|\-\d+)(?:\.\d+)?", re.I)
_FROM_RE = re.compile(r"LIN_FROM", re.I)
_TO_RE = re.compile(r"LIN_TO", re.I)


def _tokens_from_xdata_items(items: Iterable[Any]) -> List[str]:
    out: List[str] = []
    for item in items or []:
        text = str(item or "")
        # ezdxf dumps tuples like "(1000, 'LIN_FROM')" or bare strings.
        inner = re.findall(r"'([^']+)'|\"([^\"]+)\"", text)
        if inner:
            for a, b in inner:
                tok = (a or b).strip()
                if tok:
                    out.append(tok)
        else:
            stripped = text.strip()
            if stripped:
                out.append(stripped)
    return out


def _tag_in(text: str) -> str:
    m = _TAG_RE.search(str(text or ""))
    return normalize_tag(m.group(0)) if m else ""


def _align_schema_values(names: List[str], values: List[str]) -> List[Tuple[str, str]]:
    """Pair PCAD-TAKY-INFO field names with PCAD-POS-INFO values.

    POS-INFO often has one extra leading record id (24 values vs 23 names).
    """
    if len(values) == len(names) + 1:
        values = values[1:]
    return list(zip(names, values))


def parse_lin_from_to(structural: Dict[str, Any] | None) -> List[Dict[str, str]]:
    """Return unique edges ``{from, to, handle, layer}`` from ``eed_xdata_dump``."""
    edges: List[Dict[str, str]] = []
    seen: Set[Tuple[str, str]] = set()
    dump = (structural or {}).get("eed_xdata_dump") or []
    for rec in dump:
        xdata = rec.get("xdata") or {}
        handle = str(rec.get("handle") or "")
        layer = str(rec.get("layer") or "")
        src = dst = ""

        # Valmet PCAD: field names in *-TAKY-INFO, values in matching *-POS-INFO.
        name_keys = [k for k in xdata if "TAKY" in str(k).upper()]
        for nk in name_keys:
            base = str(nk).replace("TAKY-INFO", "POS-INFO").replace("TAKY_INFO", "POS_INFO")
            vk = base if base in xdata else (
                "PCAD-POS-INFO" if "PCAD-POS-INFO" in xdata else ""
            )
            if not vk:
                continue
            paired = _align_schema_values(
                _tokens_from_xdata_items(xdata.get(nk) or []),
                _tokens_from_xdata_items(xdata.get(vk) or []),
            )
            for name, val in paired:
                if _FROM_RE.fullmatch(name) or name.upper().endswith("LIN_FROM"):
                    src = _tag_in(val) or src
                elif _TO_RE.fullmatch(name) or name.upper().endswith("LIN_TO"):
                    dst = _tag_in(val) or dst

        if not (src and dst):
            tokens: List[str] = []
            for appid, items in xdata.items():
                if _FROM_RE.search(str(appid)) or _TO_RE.search(str(appid)):
                    tokens.append(str(appid))
                tokens.extend(_tokens_from_xdata_items(items))
            i = 0
            while i < len(tokens):
                tok = tokens[i]
                if _FROM_RE.fullmatch(tok) or tok.upper().endswith("LIN_FROM"):
                    if i + 1 < len(tokens):
                        nxt = _tag_in(tokens[i + 1])
                        if nxt:
                            src = nxt
                            i += 2
                            continue
                if _TO_RE.fullmatch(tok) or tok.upper().endswith("LIN_TO"):
                    if i + 1 < len(tokens):
                        nxt = _tag_in(tokens[i + 1])
                        if nxt:
                            dst = nxt
                            i += 2
                            continue
                i += 1
        if src and dst and src != dst:
            key = (src, dst)
            if key not in seen:
                seen.add(key)
                edges.append({"from": src, "to": dst, "handle": handle, "layer": layer})
    return edges


def neighbors(edges: List[Dict[str, str]], tag: str) -> Set[str]:
    t = normalize_tag(tag)
    out: Set[str] = set()
    for e in edges:
        if e["from"] == t:
            out.add(e["to"])
        if e["to"] == t:
            out.add(e["from"])
    return out


def valve_line_collision_tags(
    *,
    structural: Dict[str, Any] | None = None,
    inventory: Dict[str, Any] | None = None,
) -> Set[str]:
    """Short line ids that also appear as P-VALVEPOS / inventory valves (R09/R23)."""
    valve_ids: Set[str] = set()
    line_ids: Set[str] = set()
    _short = re.compile(r"^\d{2}-\d{2}-\d+$")

    for t in (structural or {}).get("text_entities") or []:
        layer = str(t.get("layer") or "")
        raw = normalize_tag(str(t.get("text") or ""))
        if not _short.match(raw):
            continue
        if layer == "P-VALVEPOS" or layer == "P-CVPOS":
            valve_ids.add(raw)
        if layer == "P-LINEPOS":
            line_ids.add(raw)

    for v in (inventory or {}).get("valves") or []:
        raw = normalize_tag(str(v.get("tag") or ""))
        if _short.match(raw):
            valve_ids.add(raw)
    for v in (inventory or {}).get("control_valves") or []:
        raw = normalize_tag(str(v.get("tag") or ""))
        if _short.match(raw):
            valve_ids.add(raw)
    for line in (inventory or {}).get("lines") or []:
        raw = normalize_tag(str(line.get("line_number") or ""))
        if _short.match(raw):
            line_ids.add(raw)

    return valve_ids & line_ids
