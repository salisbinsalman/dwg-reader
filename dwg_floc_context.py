#!/usr/bin/env python3
"""
SAP Functional Location path + description helpers for Shotton Broke System.

TPLNR / MASK style (matches Broke GT):
  5001
  5001-PM03
  5001-PM03-BR
  5001-PM03-BR-BR1
  5001-PM03-BR-BR1-35-24L009
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

DEFAULT_ABBREV_JSON = Path("inputs/sml_abbreviations.json")

# Locked Broke System / Shotton PM3 defaults (SML + GT MASK).
DEFAULT_FLOC_CONTEXT: Dict[str, str] = {
    "plant": "5001",
    "line_code": "PM03",
    "process_code": "BR",
    "sub_process": "BR1",
    "structure_indicator": "NNNN-XXXX-AA-XXX-XXXXXXXXXX",
    "fl_category": "M",
    "fl_type_line": "0100",
    "maintenance_plant": "5001",
    "planning_plant": "5001",
    "planning_group": "P01",
    "site_name": "SHOTTON MILL LTD",
    "line_name": "PAPER MACHINE 3",
    "process_name": "BROKE SYSTEM",
}

_TAG_TOKEN_RE = re.compile(r"^35-\d{2}[A-Z0-9][A-Z0-9-]*$", re.I)
_NUMERIC_TOKEN_RE = re.compile(r"^\d+$")
_TOKEN_SPLIT_RE = re.compile(r"(\s+|/|-)")


@lru_cache(maxsize=1)
def _load_abbrev_data(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def abbrev_data(json_path: Path = DEFAULT_ABBREV_JSON) -> Dict[str, Any]:
    return _load_abbrev_data(str(json_path.resolve()))


def merge_floc_context(base: Optional[Mapping[str, str]] = None, **overrides: str) -> Dict[str, str]:
    out = dict(DEFAULT_FLOC_CONTEXT)
    if base:
        for k, v in base.items():
            if v is not None and str(v).strip():
                out[k] = str(v).strip()
    for k, v in overrides.items():
        if v is not None and str(v).strip():
            out[k] = str(v).strip()
    return out


def build_tplnr(*parts: str, max_len: int = 30) -> str:
    """Join non-empty parts with '-' and truncate to SAP CHAR 30."""
    cleaned: List[str] = []
    for p in parts:
        s = re.sub(r"\s+", "", str(p or "").strip().upper())
        if s:
            cleaned.append(s)
    if not cleaned:
        return ""
    joined = "-".join(cleaned)
    return joined[:max_len]


def floc_paths_for_function(tag: str, ctx: Optional[Mapping[str, str]] = None) -> Dict[str, str]:
    """Return skeleton + function TPLNR values for one asset FUNCTION."""
    c = merge_floc_context(ctx)
    tag_n = re.sub(r"\s+", "", str(tag or "").strip().upper())
    plant = c["plant"]
    line = build_tplnr(plant, c["line_code"])
    process = build_tplnr(plant, c["line_code"], c["process_code"])
    subprocess = build_tplnr(plant, c["line_code"], c["process_code"], c["sub_process"])
    function = build_tplnr(plant, c["line_code"], c["process_code"], c["sub_process"], tag_n)
    return {
        "plant": plant,
        "line": line,
        "process": process,
        "subprocess": subprocess,
        "function": function,
    }


def _apply_phrase_rules(text: str, rules: List[Dict[str, str]]) -> str:
    out = text
    for rule in rules:
        pattern = str(rule.get("pattern") or "").strip()
        replacement = str(rule.get("replacement") or "").strip()
        if not pattern or not replacement:
            continue
        out = re.sub(rf"\b{re.escape(pattern)}\b", replacement, out, flags=re.I)
    return out


def _lookup_word(word: str, abbr_map: Mapping[str, str]) -> Optional[str]:
    key = word.upper()
    if key in abbr_map:
        return abbr_map[key]
    if key.endswith("S") and len(key) > 4:
        singular = key[:-1]
        if singular in abbr_map:
            return abbr_map[singular]
    return None


def _abbreviate_token(
    token: str,
    *,
    abbr_map: Mapping[str, str],
    preserve: set[str],
    abbr_values: set[str],
) -> str:
    if not token or token.isspace():
        return token
    if _TAG_TOKEN_RE.match(token) or _NUMERIC_TOKEN_RE.match(token):
        return token

    parts = _TOKEN_SPLIT_RE.split(token)
    out: List[str] = []
    for part in parts:
        if not part or part.isspace() or part in {"-", "/"}:
            out.append(part)
            continue
        key = part.upper()
        if key in preserve or key in abbr_values:
            out.append(part)
            continue
        repl = _lookup_word(key, abbr_map)
        if repl and repl != key:
            out.append(repl)
        else:
            out.append(part)
    return "".join(out)


def abbreviate_pltxt(text: str, max_len: int = 40, json_path: Path = DEFAULT_ABBREV_JSON) -> str:
    """
    Normalize PLTXT/EQKTX-style text using SML abbreviation rules.

    Order:
      1. Uppercase + collapse whitespace
      2. Domain phrase rules (Broke System naming patterns)
      3. SML multi-word phrase rules from workbook
      4. Per-token abbreviation lookup (longest phrase wins first)
    """
    data = abbrev_data(json_path)
    s = re.sub(r"\s+", " ", str(text or "").strip()).upper()
    if not s:
        return ""

    s = _apply_phrase_rules(s, data.get("domain_phrase_rules") or [])
    s = _apply_phrase_rules(s, data.get("sml_phrase_rules") or [])

    abbr_map = data.get("abbreviations") or {}
    preserve = {str(x).upper() for x in (data.get("preserve_tokens") or [])}
    abbr_values = {str(x).upper() for x in (data.get("abbreviation_values") or [])}

    tokens = s.split()
    abbreviated = [
        _abbreviate_token(
            tok,
            abbr_map=abbr_map,
            preserve=preserve,
            abbr_values=abbr_values,
        )
        for tok in tokens
    ]
    s = re.sub(r"\s+", " ", " ".join(abbreviated)).strip()
    return s[:max_len]


def normalize_pltxt(text: str, max_len: int = 40) -> str:
    return abbreviate_pltxt(text, max_len=max_len)


# Pure numeric P&ID line tags: 35-24-095 (not 35-24-001.1, 35-24LC-576, …)
_LINE_EQUIPMENT_TAG_RE = re.compile(r"^35-24-\d+$", re.I)
_VALVE_ON_LINE_RE = re.compile(
    r"\b(VLV|VALVE|HV|FV|LV|XV|CV|PV|BV|TV|NC|NO|DRN|AV)\b",
    re.I,
)


def is_line_equipment_tag(tag: str) -> bool:
    """True for pipe line number tags like 35-24-095."""
    tag_u = re.sub(r"\s+", "", str(tag or "").strip()).upper()
    return bool(_LINE_EQUIPMENT_TAG_RE.match(tag_u))


def format_line_eqktx(tag: str, eqktx: str, *, hequi: str = "", max_len: int = 40) -> str:
    """
    SML Equipment Text rule: pipe line rows start with ``LN {tag} …``.

    Applied after normalize_pltxt. Strips trailing LINE/LN markers and rebuilds
    with the LN prefix. Skips valves/fittings on lines (usually sub-equipment).
    """
    tag_u = re.sub(r"\s+", "", str(tag or "").strip()).upper()
    if not is_line_equipment_tag(tag_u):
        return str(eqktx or "")[:max_len]

    text = re.sub(r"\s+", " ", str(eqktx or "").strip()).upper()
    if not text:
        return f"LN {tag_u}"[:max_len]

    if hequi and _VALVE_ON_LINE_RE.search(text):
        return text[:max_len]
    if re.search(r"\b(VLV ON|VALVE ON)\b", text):
        return text[:max_len]

    want = f"LN {tag_u}"
    if text == want or text.startswith(f"{want} "):
        return text[:max_len]

    body = re.sub(r"\s+(LINE|LN)$", "", text).strip()
    if body.startswith(tag_u):
        rest = body[len(tag_u) :].strip()
    else:
        rest = body
    if rest.startswith("LN "):
        rest = rest[3:].strip()

    formatted = f"{want} {rest}".strip() if rest else want
    return formatted[:max_len]


def description_from_nearby(tag: str, nearby: Any, max_len: int = 40) -> str:
    """Rule fallback when vision omits description."""
    tag_n = re.sub(r"\s+", "", str(tag or "").strip().upper())
    if isinstance(nearby, (list, tuple)):
        bits = [str(x).strip() for x in nearby if str(x or "").strip()]
        raw = "; ".join(bits)
    else:
        raw = str(nearby or "").strip()
    candidates = [p.strip() for p in re.split(r"[;|/]", raw) if p.strip()]
    phrase = ""
    for c in sorted(candidates, key=len, reverse=True):
        cu = c.upper()
        if cu.replace(" ", "") == tag_n:
            continue
        if re.search(r"[A-Z]{3,}", cu):
            phrase = cu
            break
    if not phrase and candidates:
        phrase = candidates[0].upper()
    if phrase:
        body = normalize_pltxt(f"{tag_n} {phrase}", max_len=max_len)
    else:
        body = tag_n[:max_len]
    return body


def load_sml_abbreviations(path: Optional[Path] = None) -> Dict[str, str]:
    """Return word -> abbreviation map from JSON (preferred) or workbook."""
    json_path = path or DEFAULT_ABBREV_JSON
    if json_path.suffix.lower() == ".json" and json_path.exists():
        return dict(abbrev_data(json_path).get("abbreviations") or {})
    if json_path.exists() and json_path.suffix.lower() in {".xlsx", ".xls"}:
        try:
            import pandas as pd

            df = pd.read_excel(json_path)
            if len(df.columns) < 2:
                return {}
            out: Dict[str, str] = {}
            for _, row in df.iterrows():
                name = str(row.iloc[0] or "").strip()
                abbr = str(row.iloc[1] or "").strip()
                if name and abbr and name.lower() != "nan" and abbr.lower() != "nan":
                    out[name.upper()] = abbr.upper()
            return out
        except Exception:
            return {}
    if DEFAULT_ABBREV_JSON.exists():
        return dict(abbrev_data(DEFAULT_ABBREV_JSON).get("abbreviations") or {})
    return {}
