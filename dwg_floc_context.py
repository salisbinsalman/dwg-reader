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


# ---------------------------------------------------------------------------
# Valve equipment text helpers
# ---------------------------------------------------------------------------

# Embedded letter groups that identify a tag as a valve instrument.
_VALVE_LETTER_PREFIXES: frozenset[str] = frozenset(
    {"HV", "FV", "LV", "XV", "CV", "PV", "BV", "TV", "KV", "AV"}
)

# Matches the embedded letter block in tags like 35-24HV-548, 35-24LV2-576.
_VALVE_EMBEDDED_RE = re.compile(r"^35-\d{2}-?([A-Z]+)\d*-?\d", re.I)

# Tag prefixes that unambiguously indicate an automatic / control valve.
_AUTO_VALVE_PREFIXES: frozenset[str] = frozenset({"FV", "XV", "CV", "AV"})

# Keywords that immediately and definitively set the valve type (first match wins).
# AV-M must precede AV so "AV-M" is not swallowed by the shorter AV token.
_VALVE_IMMEDIATE_RULES: list[tuple[str, str]] = [
    ("AV-M", "AV-M"),
    ("AVM", "AV-M"),
    ("AV", "AV"),
    ("AUTO", "AV"),
]

# Keywords that accumulate as qualifiers (DRN NC is valid; collect all matches).
# Each tuple is (keyword, type_token). Longer / more-specific patterns come first
# so they shadow shorter ones (e.g. CHECK before CHK is not needed, both map to CHK).
_VALVE_QUALIFIER_RULES: list[tuple[str, str]] = [
    # Drain
    ("DRN", "DRN"),
    ("DRAIN", "DRN"),
    # Normally-closed / normally-open
    ("NC", "NC"),
    ("NO", "NO"),
    # Pressure reducing
    ("PRV", "PRV"),
    # Safety / relief
    ("SV", "SV"),
    ("RELIEF", "SV"),
    # Check valve — short token and plain-English forms the AI sometimes writes
    ("CHK", "CHK"),
    ("CHECK", "CHK"),
    # Flushing — token and AI abbreviations (FLUSHING before FLUSH: word-boundary)
    ("FLUSHING", "FLS"),
    ("FLSHG", "FLS"),
    ("FLS", "FLS"),
    ("FLSH", "FLS"),
    ("FLUSH", "FLS"),
    # Sampling — token and AI abbreviations
    ("SMP", "SMP"),
    ("SMPL", "SMP"),
    ("SAMPL", "SMP"),
]

# Description contains VLV or VALVE → treat as valve.
_VLV_DESC_RE = re.compile(r"\b(VLV|VALVE)\b", re.I)

# Drain/check/flushing/sampling tokens alone (no VLV needed) also mark a numeric
# tag as a valve — catches drain taps the AI describes as "DRN VLV" but also
# ones where VLV was omitted ("35-24-131 DRN DRN").
_VALVE_TYPE_ONLY_RE = re.compile(
    r"\b(DRN|DRAIN|CHK|CHECK|FLS|FLSH|FLSHG|FLUSHING|FLUSH|SMP|SMPL|NC|PRV|SV)\b", re.I
)

# Attachment tokens that text can name even when vision only saw the valve body.
_ATTACHMENT_TOKENS = ("FLS", "DRN", "SMP", "CHK", "PRV", "SV")
ALLOWED_VALVE_TOKENS = {
    "HV", "NC", "NO", "CHK", "PRV", "SV", "FLS", "SMP", "DRN", "AV", "AV-M",
}


def is_valve_tag(tag: str) -> bool:
    """True for tags with an embedded valve-type letter block: 35-24HV-548, 35-24FV-570."""
    t = re.sub(r"\s+", "", str(tag or "").strip()).upper()
    m = _VALVE_EMBEDDED_RE.match(t)
    return bool(m) and m.group(1).upper() in _VALVE_LETTER_PREFIXES


def strip_valve_prefix(tag: str) -> str:
    """
    Remove embedded valve letters from tag, preserving any position digit.

    35-24HV-548  → 35-24-548    (no position digit)
    35-24LV2-576 → 35-24-2-576  (position digit kept for disambiguation)
    35-24LV1-560 → 35-24-1-560  (avoids collision with LV2-560)
    Plain tags and non-valve tags are returned unchanged.
    """
    t = re.sub(r"\s+", "", str(tag or "").strip()).upper()

    def _rebuild(m: re.Match) -> str:  # type: ignore[type-arg]
        area, pos_digit, number = m.group(1), m.group(2), m.group(3)
        return f"{area}-{pos_digit}-{number}" if pos_digit else f"{area}-{number}"

    return re.sub(r"^(35-\d{2})-?[A-Z]+(\d*)-?(\d+.*)$", _rebuild, t, flags=re.I)


def infer_valve_type(tag: str, eqktx: str) -> str:
    """
    Infer the SAP valve type suffix from abbreviated description and tag prefix.

    Priority:
      1. AV/AUTO in description → "AV" (automatic valve — definitive, stops search)
      2. DRN/NC/NO/PRV/SV/CHK/FLS/SMP in description → accumulated (e.g. "DRN NC")
      3. FV/XV/CV/AV tag prefix → "AV" (control valve by tag convention)
      4. Default → "HV" (hand valve)

    Note: visual AV/HV ambiguity (e.g. 35-24HV-548 may be AV per symbol shape)
    requires classify_valve_block.py + inputs/valve_type_overrides.json.
    """
    desc = str(eqktx or "").upper()
    tag_u = re.sub(r"\s+", "", str(tag or "")).upper()

    for keyword, suffix in _VALVE_IMMEDIATE_RULES:
        if re.search(rf"\b{re.escape(keyword)}\b", desc):
            return suffix

    qualifiers: list[str] = []
    for keyword, suffix in _VALVE_QUALIFIER_RULES:
        if re.search(rf"\b{re.escape(keyword)}\b", desc) and suffix not in qualifiers:
            qualifiers.append(suffix)
    if qualifiers:
        return " ".join(qualifiers)

    m = _VALVE_EMBEDDED_RE.match(tag_u)
    if m and m.group(1).upper() in _AUTO_VALVE_PREFIXES:
        return "AV"

    return "HV"


def attachment_tokens_from_text(eqktx: str) -> List[str]:
    """FLS/DRN/… named in the description, independent of body fill (NC vs HV)."""
    desc = str(eqktx or "").upper()
    found: List[str] = []
    for keyword, suffix in _VALVE_QUALIFIER_RULES:
        if suffix not in _ATTACHMENT_TOKENS:
            continue
        if re.search(rf"\b{re.escape(keyword)}\b", desc) and suffix not in found:
            found.append(suffix)
    return found


def combine_valve_type(primary: str, eqktx: str) -> str:
    """Keep vision/override body type; add at most one attachment token text named but vision missed."""
    tokens: List[str] = []
    cleaned = re.sub(r"[^A-Z0-9\-\s]", " ", str(primary or "").upper())
    cleaned = cleaned.replace("AVM", "AV-M").replace("AV_M", "AV-M")
    for tok in cleaned.split():
        if tok in ALLOWED_VALVE_TOKENS and tok not in tokens:
            tokens.append(tok)
    has_attachment = any(t in tokens for t in _ATTACHMENT_TOKENS)
    if not has_attachment:
        for tok in attachment_tokens_from_text(eqktx):
            if tok not in tokens:
                tokens.append(tok)
                break
    return apply_sop_valve_type(" ".join(tokens))


def apply_sop_valve_type(raw: str) -> str:
    """
    Shotton SOP valve-type cleanup:
      - Process-controlled (AV / AV-M): do not add running condition NC/NO (or HV).
      - Hand drain/flush keep NC/NO, e.g. DRN NC.
      - DRN / FLS / SMP are mutually exclusive — at most one.
    """
    cleaned = re.sub(r"[^A-Z0-9\-\s]", " ", str(raw or "").upper())
    cleaned = cleaned.replace("AVM", "AV-M").replace("AV_M", "AV-M")
    tokens: List[str] = []
    for tok in cleaned.split():
        if tok in ALLOWED_VALVE_TOKENS and tok not in tokens:
            tokens.append(tok)
    exclusive = [t for t in ("DRN", "FLS", "SMP") if t in tokens]
    if len(exclusive) > 1:
        keep = exclusive[0]
        tokens = [t for t in tokens if t not in ("DRN", "FLS", "SMP") or t == keep]
    controlled = "AV-M" in tokens or "AV" in tokens
    if controlled:
        tokens = [t for t in tokens if t not in {"NC", "NO", "HV"}]
        if "AV-M" in tokens:
            tokens = [t for t in tokens if t != "AV"]
    order = ("AV-M", "AV", "DRN", "NC", "NO", "FLS", "SMP", "CHK", "PRV", "SV", "HV")
    return " ".join(t for t in order if t in tokens)


def explain_valve_type(
    tag: str,
    eqktx: str,
) -> tuple[str, str, str]:
    """
    Return (type_token, source_code, reasoning) using the same priority chain as infer_valve_type.

    source_code is one of:
      AI_IMMEDIATE  – AI appended AV/AUTO token
      AI_QUALIFIER  – AI appended DRN/NC/CHK/SV/FLS/SMP/PRV/NO qualifier(s)
      TAG_PREFIX    – FV/XV/CV/AV tag prefix (no description token needed)
      DEFAULT_HV    – no token, no auto prefix; falls back to hand-valve default
    """
    desc = str(eqktx or "").upper()
    tag_u = re.sub(r"\s+", "", str(tag or "")).upper()

    # Immediate rules — AV / AUTO anywhere in description
    for keyword, suffix in _VALVE_IMMEDIATE_RULES:
        if re.search(rf"\b{re.escape(keyword)}\b", desc):
            return (
                suffix,
                "AI_IMMEDIATE",
                f"AI token '{keyword}' in description → {suffix} (immediate rule, stops search)",
            )

    # Qualifier rules — accumulate DRN / NC / CHK / SV / FLS / SMP / PRV / NO
    qualifiers: list[str] = []
    found_kws: list[str] = []
    for keyword, suffix in _VALVE_QUALIFIER_RULES:
        if re.search(rf"\b{re.escape(keyword)}\b", desc) and suffix not in qualifiers:
            qualifiers.append(suffix)
            found_kws.append(keyword)
    if qualifiers:
        result = " ".join(qualifiers)
        return (
            result,
            "AI_QUALIFIER",
            f"AI qualifier token(s) {found_kws} in description → {result}",
        )

    # Tag prefix — FV / XV / CV / AV
    m = _VALVE_EMBEDDED_RE.match(tag_u)
    if m and m.group(1).upper() in _AUTO_VALVE_PREFIXES:
        pfx = m.group(1).upper()
        return (
            "AV",
            "TAG_PREFIX",
            f"Tag prefix '{pfx}' is in auto-valve set (FV/XV/CV/AV) → AV by tag convention"
            "; no description token needed",
        )

    return (
        "HV",
        "DEFAULT_HV",
        "No AV/qualifier token in description; no auto prefix → default hand valve",
    )


def is_valve_equipment(tag: str, eqktx: str) -> bool:
    """
    True when this equipment row should receive HV-format text.

    For tags with any embedded letter prefix (XS, LC, NC, …) that is NOT in
    the valve set, trust the tag — they are instruments, not valves — even when
    the description incidentally contains VLV (e.g. from a copied tag reference).
    Description-based VLV detection only applies to plain numeric line tags
    (35-24-NNN) that carry no instrument-type prefix of their own.
    """
    if is_valve_tag(tag):
        return True
    t = re.sub(r"\s+", "", str(tag or "").strip()).upper()
    if _VALVE_EMBEDDED_RE.match(t):
        # Has a letter-group prefix but it's not a valve prefix → instrument, not valve.
        return False
    desc = str(eqktx or "")
    # VLV / VALVE is the primary signal.
    if _VLV_DESC_RE.search(desc):
        return True
    # Drain/check/flush/sample tokens alone also identify a numeric tag as a valve,
    # catching cases where the AI omitted VLV from the description.
    return bool(_VALVE_TYPE_ONLY_RE.search(desc))


def format_valve_eqktx(
    tag: str,
    parent_fn: str,
    eqktx: str,
    *,
    valve_type_override: str | None = None,
    max_len: int = 40,
) -> str:
    """
    SML valve Equipment Text rule: HV {stripped-tag} {parent-fn} {valve-type}.

    'HV' is the fixed SML valve-equipment format marker (not the valve subtype).
    The subtype suffix (AV, DRN, NC, HV, …) comes from description keywords or tag
    prefix inference, and may be overridden by inputs/valve_type_overrides.json after
    running classify_valve_block.py.

    Applies to instrument valve tags (35-24HV-548) and plain line tags identified as
    valves via description keywords (35-24-207 VLV ON 35-24-096).
    """
    stripped = strip_valve_prefix(tag)
    fn = re.sub(r"\s+", "", str(parent_fn or "").strip()).upper()
    valve_type = valve_type_override if valve_type_override is not None else infer_valve_type(tag, eqktx)
    valve_type = apply_sop_valve_type(valve_type)

    parts = ["HV", stripped]
    if fn:
        parts.append(fn)
    if valve_type:
        parts.append(valve_type)

    return " ".join(parts)[:max_len]


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
