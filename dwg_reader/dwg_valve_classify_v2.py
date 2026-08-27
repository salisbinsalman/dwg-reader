"""V2 vision classification: legend-driven valve / fitting / service-point types.

No CAD type heuristics. The model reads the crop against ``standards/legend.png``
using ``prompts/valve_classify_v2.md``. This module only loads that prompt and
normalises the JSON reply into SOP tokens.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict

from dwg_reader.dwg_floc_context import ALLOWED_VALVE_TOKENS, apply_sop_valve_type
from dwg_reader.paths import PROMPTS_DIR

V2_PROMPT_FILE = "valve_classify_v2.md"

# Body tokens the V2 legend can emit (plus SML AV/PRV/SV already in SOP).
V2_BODY_TOKENS = frozenset(
    {
        "HV",
        "NC",
        "NO",
        "GLV",
        "CHK",
        "3WV",
        "SV",
        "AV",
        "AV-M",
        "PRV",
        "PLUG",
        "AAV",
        "GF",
        "YSTR",
    }
)
V2_ATTACHMENTS = frozenset({"DRN", "FLS", "SMP"})

_BODY_ALIASES: Dict[str, str] = {
    "HV": "HV",
    "HAND": "HV",
    "HANDOPEN": "HV",
    "NC": "NC",
    "NO": "NO",
    "GLV": "GLV",
    "GLOBE": "GLV",
    "GLOBAL": "GLV",
    "GV": "GLV",
    "GLB": "GLV",
    "GLOB": "GLV",
    "GLOBVALVE": "GLV",
    "GLOBEVALVE": "GLV",
    "GLOBALVALVE": "GLV",
    "CHK": "CHK",
    "CHECK": "CHK",
    "NRV": "CHK",
    "3WV": "3WV",
    "TWV": "3WV",
    "THREEWAY": "3WV",
    "3WAY": "3WV",
    "SV": "SV",
    "SAFETY": "SV",
    "PSV": "SV",
    "AV": "AV",
    "AV-M": "AV-M",
    "AVM": "AV-M",
    "PRV": "PRV",
    "PLUG": "PLUG",
    "AAV": "AAV",
    "AIRVENT": "AAV",
    "GF": "GF",
    "FILTER": "GF",
    "GASFILTER": "GF",
    "YSTR": "YSTR",
    "STRAINER": "YSTR",
    "YSTRAINER": "YSTR",
}

_ATTACH_ALIASES: Dict[str, str] = {
    "NONE": "",
    "NULL": "",
    "-": "",
    "DRN": "DRN",
    "DRAIN": "DRN",
    "DRAINAGE": "DRN",
    "FLS": "FLS",
    "FLUSH": "FLS",
    "FLUSHING": "FLS",
    "SMP": "SMP",
    "SAMPLE": "SMP",
    "SAMPLING": "SMP",
}

_FITTINGS = frozenset({"PLUG", "AAV", "GF", "YSTR"})


def v2_prompt_path() -> Path:
    return PROMPTS_DIR / V2_PROMPT_FILE


def load_v2_prompt(tag: str) -> str:
    text = v2_prompt_path().read_text(encoding="utf-8")
    return text.replace("{TAG}", str(tag or "").strip() or "UNKNOWN")


def _alias_body(raw: str) -> str:
    key = re.sub(r"[^A-Z0-9]+", "", str(raw or "").upper())
    if key in _BODY_ALIASES:
        return _BODY_ALIASES[key]
    compact = key.replace("VALVE", "")
    if compact in _BODY_ALIASES:
        return _BODY_ALIASES[compact]
    return ""


def _alias_attachment(raw: str) -> str:
    key = re.sub(r"[^A-Z0-9]+", "", str(raw or "").upper())
    if not key or key in {"NONE", "NULL"}:
        return ""
    return _ATTACH_ALIASES.get(key, key if key in V2_ATTACHMENTS else "")


def _exclusive_body(body: str) -> str:
    tokens = [t for t in str(body or "").upper().split() if t in ALLOWED_VALVE_TOKENS]
    if "AV-M" in tokens:
        tokens = [t for t in tokens if t in {"AV-M"} | V2_ATTACHMENTS]
    elif "AV" in tokens:
        tokens = [t for t in tokens if t in {"AV"} | V2_ATTACHMENTS]
    elif "CHK" in tokens:
        tokens = [t for t in tokens if t not in {"NC", "HV", "NO", "GLV", "3WV"}]
    elif "GLV" in tokens:
        tokens = [t for t in tokens if t not in {"HV", "NC", "NO"}]
    elif "3WV" in tokens:
        tokens = [t for t in tokens if t not in {"HV", "NC", "NO"}]
    elif "NC" in tokens:
        tokens = [t for t in tokens if t not in {"HV", "NO"}]
    elif "HV" in tokens:
        tokens = [t for t in tokens if t != "NO"]
    return apply_sop_valve_type(" ".join(tokens))


def merge_v2_type(body: str, attachment: str) -> str:
    """SOP-ordered token string from a V2 body + service-point attachment."""
    body_tok = _alias_body(body) or str(body or "").upper().strip()
    att = _alias_attachment(attachment)
    if body_tok in _FITTINGS:
        return apply_sop_valve_type(body_tok)
    parts = [t for t in body_tok.split() if t]
    if att and att not in parts:
        parts.append(att)
    return _exclusive_body(" ".join(parts))


def parse_v2_response(raw: str) -> str:
    """Parse ``{"type": "...", "attachment": "..."}`` into SOP tokens (e.g. ``NC DRN``)."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", str(raw or "").strip())
    obj = None
    try:
        obj = json.loads(text)
    except Exception:
        m = re.search(
            r"\{[^{}]*\"type\"[^{}]*\}",
            text,
            re.I | re.S,
        )
        if m:
            try:
                obj = json.loads(m.group(0))
            except Exception:
                obj = None
    if isinstance(obj, dict):
        return merge_v2_type(str(obj.get("type") or ""), str(obj.get("attachment") or "none"))
    # Bare token / prose fallback.
    upper = re.sub(r"[^A-Z0-9\-\s]", " ", text.upper())
    body = ""
    for word in upper.replace("AVM", "AV-M").split():
        mapped = _alias_body(word)
        if mapped and mapped in V2_BODY_TOKENS:
            body = mapped
            if mapped not in {"HV", "NC"}:
                break
    att = ""
    for word in upper.split():
        mapped = _alias_attachment(word)
        if mapped:
            att = mapped
            break
    return merge_v2_type(body, att) if body else ""


# Canonical expected types for the GOR WU05 cases the user labelled.
GOR_V2_EXPECTED: Dict[str, frozenset[str]] = {
    "168V-385": frozenset({"HV"}),
    "168V-389": frozenset({"CHK"}),
    "168V-387": frozenset({"NC", "DRN"}),
    "168V-390": frozenset({"GLV"}),
}


def expected_tokens_match(got: str, expected: frozenset[str]) -> bool:
    return expected.issubset(set(str(got or "").upper().split()))
