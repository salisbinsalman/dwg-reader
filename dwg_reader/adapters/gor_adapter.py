#!/usr/bin/env python3
"""
GOR Fiorentini Italian P&ID adapter.

Handles Code 03, 13, and 14 drawings (GORA*, GORB* DWG stems).

Numbering is KSDM160104 with a 3-digit mill+area prefix
(162=AirCap 62, 168=ventilation 68, 160=mist 60, 164=wet dust 64).
CAD is Italian GOR layers/blocks — not Andritz KSD and not Valmet P-*.

Tag format:
  {unit_prefix}{type_letters}[-]{sequence}  e.g. 168P-410, 168TC1, 168V-521
Safety valves are irregular: 168-ST521, 168ST-061, 168-ST-096.

Equipment letters: E/A/P/T/X/F. Valve letters: V/ST/VX/KV/HV/FV. L = line.
Two or more ISO letters = instrument. A hyphen does not mean equipment.

Valve type source (inventory / descriptions only — SAP types come from legend vision):
  Code 14: TIPO_VALVOLA block attribute  (2K0-BF-65, 4S4-LWE-15, ST-65, VX-25 …)
           Known family typos like 4S4-LWE25 (missing hyphen) are normalised.
  Code 03/13: tag-pattern fallback       (KV in tag → AV, ^\\d+V-\\d → NC, else HV)

Hierarchy: Claude vision (core prompt + GOR addendum). CAD suffix-matching
repairs valve-under-line nesting after the model returns.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from dwg_reader.adapters.base import BaseAdapter
from dwg_reader.dwg_floc_context import abbreviate_pltxt

# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

# Compound tag: 168P-410, 168F-415, 168VX-521
_COMPOUND_RE = re.compile(r"^(\d{3})([A-Z]{1,4})-(\d+)(.*)$", re.I)
# Simple tag: 168TC1, 168M1, 168TT (letters followed directly by digits or EOS)
_SIMPLE_RE = re.compile(r"^(\d{3})([A-Z]{1,4})(\d*)(.*)$", re.I)
# Safety-valve variants: 168-ST521, 168ST-061, 168-ST-096
_ST_RE = re.compile(r"^(\d{3})-?ST-?(\d+)(.*)$", re.I)
# Line tag: 168L-521
_LINE_RE = re.compile(r"^\d{3}L-\d+$", re.I)
# Motor suffix (hyphenated: 168P-410-M1) and sub-designation (no hyphen: 168F-315M4)
_MOTOR_SUFFIX_RE = re.compile(r"-M\d+$", re.I)
_MOTOR_SUBDESIG_RE = re.compile(r"^M\d+$", re.I)
# Leading letters after unit prefix
_LETTERS_RE = re.compile(r"^\d{3}([A-Z]{1,4})", re.I)

_EQUIP_LETTERS = frozenset({"E", "A", "P", "T", "X", "F"})
_DRIVEN_LETTERS = frozenset({"E", "A", "P", "X", "F"})  # tanks are not driven
_VALVE_LETTERS = frozenset({"V", "ST", "VX", "KV", "HV", "FV"})
_FOREIGN_LAYER_HINTS = ("KSD", "KAWANOE", "METSO", "CHINA")

# ---------------------------------------------------------------------------
# TIPO_VALVOLA → SAP type
# ---------------------------------------------------------------------------

_KNOWN_FAMILIES = ("LWE", "BF", "IT", "ST", "VX", "FL")


def _normalize_tipo(tipo: str) -> str:
    """Insert a missing hyphen before a known family (4S4-LWE25 → 4S4-LWE-25)."""
    t = re.sub(r"\s+", "", (tipo or "")).upper()
    if not t:
        return t
    out: List[str] = []
    for part in t.split("-"):
        if part in _KNOWN_FAMILIES:
            out.append(part)
            continue
        matched = False
        for fam in _KNOWN_FAMILIES:
            if part.startswith(fam) and part != fam:
                rest = part[len(fam):]
                out.append(fam)
                if rest:
                    out.append(rest)
                matched = True
                break
        if not matched:
            out.append(part)
    return "-".join(out)


def _tipo_family(tipo: str) -> str:
    """Extract valve-family code from TIPO_VALVOLA string."""
    parts = _normalize_tipo(tipo).split("-")
    if len(parts) >= 3:
        return parts[1].upper()
    if len(parts) == 2:
        return parts[0].upper()
    return (tipo or "").upper()


def _tipo_prefix(tipo: str) -> str:
    return _normalize_tipo(tipo).split("-")[0].upper()


_TIPO_TO_SAP: Dict[str, Tuple[Optional[str], bool]] = {
    # family: (sap_valve_type, is_valve)
    "LWE": ("NC", True),   # solenoid, normally closed
    "IT":  ("NC", True),   # isolation tap
    "ST":  ("SV", True),   # safety valve
    "VX":  ("AV", True),   # automatic deaerator (actuation valve class)
    "FL":  (None, False),  # blind flange — not a valve
    # BF (butterfly): depends on prefix (6* → AV, else → NC) — handled in code
}

_TIPO_DESCRIPTIONS: Dict[str, str] = {
    "BF":  "BUTTERFLY VLV",
    "LWE": "SOLENOID NC VLV",
    "IT":  "ISOLATION TAP VLV",
    "VX":  "AUTO DEAERATOR",
    "ST":  "SAFETY VLV",
    "FL":  "BLIND FLANGE",
}

# In-line piping components (not strict valves): VX = automatic deaerator
_INLINE_COMPONENT_LETTERS = frozenset({"VX"})

_INSTR_LABELS: Dict[str, str] = {
    "TC":  "TEMP CTRL",
    "TT":  "TEMP TRANS",
    "TA":  "TEMP ALRM",
    "TI":  "TEMP IND",
    "TV":  "TEMP VLV",
    "PT":  "PRES TRANS",
    "PC":  "PRES CTRL",
    "PI":  "PRES IND",
    "FT":  "FLOW TRANS",
    "FC":  "FLOW CTRL",
    "FV":  "FLOW VLV",
    "LC":  "LVL CTRL",
    "LT":  "LVL TRANS",
    "LI":  "LVL IND",
    "HC":  "HUM CTRL",
    "HS":  "HND SW",
    "HI":  "HND IND",
    "GSO": "GAS SO",
    "GSC": "GAS SC",
    "ST":  "SAFETY VLV",
    "M":   "MTR",
    "E":   "HEAT EXCH",
    "P":   "PMP",
    "F":   "FAN",
}


def _is_foreign_layer(layer: str) -> bool:
    upper = (layer or "").upper()
    if "GOR" in upper:
        return False
    return any(hint in upper for hint in _FOREIGN_LAYER_HINTS)


class GORAdapter(BaseAdapter):
    """GOR S.r.l. Italian CAD adapter."""

    ecosystem_name = "gor"
    standard_id = "gor_fiorentini"

    # ------------------------------------------------------------------
    # Layer / block discovery
    # ------------------------------------------------------------------

    @property
    def layer_map(self) -> Dict[str, Tuple[str, str]]:
        return {
            "1-VALVE TEXT GOR":          ("valves", "valve_symbol"),
            "1-TAG AND INSTRUMENTS GOR": ("instruments", "instrument_symbol"),
            "1-EQUIPMENT GOR":           ("process_equipment", "equipment_symbol"),
            # typo is deliberate — the actual drawing layer is mis-spelled
            "Revison 03":                ("line_markers", "gor_pipe_id"),
        }

    @property
    def block_map(self) -> Dict[str, str]:
        return {
            "TAG VALVOLA": "valves",
            "LOOPDCS":     "instruments",
            "Pipeno":      "line_markers",
            "PIPENO":      "line_markers",
            "Pipeid":      "line_markers",
            "COIL":        "process_equipment",
        }

    @property
    def pipe_layers(self) -> set:
        return {
            "1-AIR GOR",
            "1-WATER GOR",
            "1-BACKPRESSURE GOR",
            "1-GAS GOR",
            "2-WATER CUSTOMER",
        }

    def classify_insert(
        self,
        ins: Dict[str, Any],
        attrs: Optional[Dict[str, str]] = None,
    ) -> Tuple[str, str, str]:
        attrs = attrs or {}
        layer = ins.get("layer") or ""
        name = ins.get("name") or ""
        if _is_foreign_layer(layer):
            return "other_inserts", "foreign_layer", "low"
        if name.upper() == "TAG VALVOLA":
            return "valves", "valve_symbol", "high"
        if attrs.get("PIPEID") or name.upper() in ("PIPENO", "PIPEID"):
            return "line_markers", "gor_pipe_id", "high"
        return super().classify_insert(ins, attrs)

    def tag_from_insert(
        self,
        block_name: str,
        attrs: Dict[str, str],
        layer: str = "",
    ) -> Tuple[str, Dict[str, Any]]:
        extra: Dict[str, Any] = {}
        tag_valvola = (attrs.get("TAG_VALVOLA") or "").strip()
        tipo = (attrs.get("TIPO_VALVOLA") or "").strip()
        pipe_id = (attrs.get("PIPEID") or "").strip()
        pipe_data = (attrs.get("PIPEDATA") or "").strip()
        if tipo:
            extra["valve_type"] = _normalize_tipo(tipo)
            extra["tipo_raw"] = tipo
        if pipe_data:
            extra["pipe_data"] = pipe_data
        if tag_valvola:
            return tag_valvola, extra
        if pipe_id:
            return pipe_id, extra
        return block_name, extra

    # ------------------------------------------------------------------
    # Tag parsing
    # ------------------------------------------------------------------

    def parse_tag(self, tag: str) -> Dict[str, str]:
        t = self._norm(tag)
        m_st = _ST_RE.match(t)
        if m_st:
            return {
                "unit_prefix":  m_st.group(1),
                "type_letters": "ST",
                "sequence":     m_st.group(2),
                "suffix":       m_st.group(3),
                "full":         t,
            }
        # Try compound first: 168P-410, 168F-415, 168VX-521
        m = _COMPOUND_RE.match(t)
        if m:
            return {
                "unit_prefix":  m.group(1),
                "type_letters": m.group(2).upper(),
                "sequence":     m.group(3),
                "suffix":       m.group(4),
                "full":         t,
            }
        # Simple: 168TC1, 168M1
        m = _SIMPLE_RE.match(t)
        if m:
            return {
                "unit_prefix":  m.group(1),
                "type_letters": m.group(2).upper(),
                "sequence":     m.group(3),
                "suffix":       m.group(4),
                "full":         t,
            }
        return {"unit_prefix": "", "type_letters": "", "sequence": t, "suffix": "", "full": t}

    def _letters(self, tag: str) -> str:
        return (self.parse_tag(tag).get("type_letters") or "").upper()

    def is_equipment_tag(self, tag: str) -> bool:
        t = self._norm(tag)
        if _LINE_RE.match(t) or self.is_valve_tag(t) or self.is_motor_tag(t):
            return False
        letters = self._letters(t)
        return len(letters) == 1 and letters in _EQUIP_LETTERS

    def is_line_tag(self, tag: str) -> bool:
        return bool(_LINE_RE.match(self._norm(tag)))

    def is_valve_tag(self, tag: str) -> bool:
        letters = self._letters(tag)
        if letters in _VALVE_LETTERS:
            return True
        if letters.startswith("KV"):
            return True
        return bool(_ST_RE.match(self._norm(tag)))

    def is_instrument_tag(self, tag: str) -> bool:
        t = self._norm(tag)
        if self.is_equipment_tag(t) or self.is_line_tag(t) or self.is_valve_tag(t) or self.is_motor_tag(t):
            return False
        letters = self._letters(t)
        return len(letters) >= 2

    def is_motor_tag(self, tag: str) -> bool:
        t = self._norm(tag)
        if _MOTOR_SUFFIX_RE.search(t):
            return True
        # Same-duty sub-designation: 168F-315M4 has suffix "M4" (no hyphen)
        return bool(_MOTOR_SUBDESIG_RE.match(self.parse_tag(t).get("suffix", "")))

    def is_inline_component_tag(self, tag: str) -> bool:
        """Return True for in-line piping components (VX = automatic deaerator).
        These are distinct from valves in the GOR drawing convention even though
        they use TAG VALVOLA blocks and carry a TIPO_VALVOLA attribute."""
        return self._letters(self._norm(tag)) in _INLINE_COMPONENT_LETTERS

    # ------------------------------------------------------------------
    # Motor derivation
    # ------------------------------------------------------------------

    def derive_motor_tag(self, equipment_tag: str) -> Optional[str]:
        """168P-410 → 168P-410-M1. Not applied to tanks, valves, lines, instruments."""
        t = self._norm(equipment_tag)
        if _MOTOR_SUFFIX_RE.search(t):
            return None
        # M4 sub-designation without hyphen — already a motor tag
        if _MOTOR_SUBDESIG_RE.match(self.parse_tag(t).get("suffix", "")):
            return None
        if _LINE_RE.match(t) or self.is_valve_tag(t):
            return None
        letters = self._letters(t)
        if letters in _DRIVEN_LETTERS:
            return f"{t}-M1"
        return None

    # ------------------------------------------------------------------
    # Valve classification
    # ------------------------------------------------------------------

    def resolve_valve_type(
        self,
        tag: str,
        *,
        tipo: Optional[str] = None,
        layer: Optional[str] = None,
        eqktx: str = "",
    ) -> Tuple[Optional[str], bool]:
        if tipo:
            family = _tipo_family(tipo)
            prefix = _tipo_prefix(tipo)
            mapped = _TIPO_TO_SAP.get(family)
            if mapped is not None:
                return mapped
            if family == "BF":
                return ("AV", True) if prefix.startswith("6") else ("NC", True)
            # Unknown TIPO family — treat as valve, type unknown
            return (None, True)
        # Code 03/13 — no TIPO attribute, infer from tag
        return self._code03_type(tag)

    def _code03_type(self, tag: str) -> Tuple[str, bool]:
        """Infer valve type for Code 03/13 text-label tags."""
        t = self._norm(tag)
        if "KV" in t:
            return "AV", True
        if re.match(r"^\d+V-\d", t):
            return "NC", True
        if self.is_valve_tag(t) and self._letters(t) == "ST":
            return "SV", True
        return "HV", True

    # ------------------------------------------------------------------
    # GOR-specific helpers
    # ------------------------------------------------------------------

    def tipo_family(self, tipo: str) -> str:
        return _tipo_family(tipo)

    def tipo_description(self, tipo: str) -> str:
        """Human-readable SAP description for a TIPO_VALVOLA code."""
        family = _tipo_family(tipo)
        return _TIPO_DESCRIPTIONS.get(family, f"{family} VLV" if family else "VLV")

    def instrument_description(self, tag: str) -> str:
        """Short SAP description derived from the GOR instrument letter code."""
        t = self._norm(tag)
        m = _LETTERS_RE.match(t)
        if not m:
            return t[:40]
        letters = m.group(1)
        # Try longest match first
        for length in range(len(letters), 0, -1):
            label = _INSTR_LABELS.get(letters[:length])
            if label:
                return f"{t} {label}"[:40]
        return t[:40]

    def valve_description(self, tag: str, tipo: str) -> str:
        """Combine tag + TIPO description for a GOR valve."""
        sap_type, _ = self.resolve_valve_type(tag, tipo=tipo)
        del sap_type
        label = self.tipo_description(tipo)
        return f"{tag} {label}"[:40]

    # ------------------------------------------------------------------
    # Hierarchy building
    # ------------------------------------------------------------------

    @property
    def uses_ai_hierarchy(self) -> bool:
        return True

    @property
    def hierarchy_crop_half(self) -> Optional[float]:
        # One FUNCTION is the whole ventil unit — zoom out past the default 165.
        return 900.0

    def repair_hierarchy(
        self,
        rows: List[Dict[str, str]],
        inventory: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        """Nest valves under the PIPEID line whose numeric suffix matches."""
        inventory = inventory or {}
        suffix_to_line: Dict[str, str] = {}
        for line in inventory.get("lines") or []:
            ltag = str(line.get("line_number") or "").strip().upper()
            m = re.search(r"(\d+)$", ltag)
            if ltag and m and m.group(1) not in suffix_to_line:
                suffix_to_line[m.group(1)] = ltag
        line_tags = set(suffix_to_line.values())

        def _blank_child(src: Dict[str, str], *, equipment: str = "", sub: str = "", desc: str = "") -> Dict[str, str]:
            nested = dict(src)
            nested["FUNCTION"] = ""
            nested["EQUIPMENT"] = equipment
            nested["SUB-EQUIPMENT"] = sub
            if desc:
                nested["DESCRIPTION"] = desc[:40]
            nested["MASK"] = ""
            return nested

        valve_desc: Dict[str, str] = {}
        for row in rows:
            for tok in (
                str(row.get("EQUIPMENT") or "").strip().upper(),
                str(row.get("SUB-EQUIPMENT") or "").strip().upper(),
            ):
                if tok and self.is_valve_tag(tok):
                    valve_desc.setdefault(tok, str(row.get("DESCRIPTION") or tok)[:40])
        for valve in inventory.get("valves") or []:
            vtag = str(valve.get("tag") or "").strip().upper()
            if vtag and self.is_valve_tag(vtag):
                valve_desc.setdefault(vtag, vtag)

        valves_by_suffix: Dict[str, List[str]] = {}
        for vtag in valve_desc:
            m = re.search(r"(\d+)$", vtag)
            if m:
                valves_by_suffix.setdefault(m.group(1), []).append(vtag)

        template = next((r for r in rows if r.get("EQUIPMENT") or r.get("SUB-EQUIPMENT")), {})
        emitted_valves: set = set()
        out: List[Dict[str, str]] = []
        lines_in_tree: set = set()
        for row in rows:
            fn = str(row.get("FUNCTION") or "").strip()
            eq = str(row.get("EQUIPMENT") or "").strip().upper()
            sub = str(row.get("SUB-EQUIPMENT") or "").strip().upper()
            if fn and not eq and not sub:
                out.append(row)
                continue
            # Drop valve-only rows — re-inserted under the suffix-matching line.
            if (eq and self.is_valve_tag(eq) and not sub) or (sub and self.is_valve_tag(sub) and not eq):
                continue
            out.append(row)
            if eq not in line_tags:
                continue
            lines_in_tree.add(eq)
            m = re.search(r"(\d+)$", eq)
            if not m:
                continue
            for vtag in sorted(set(valves_by_suffix.get(m.group(1), []))):
                if vtag in emitted_valves:
                    continue
                emitted_valves.add(vtag)
                out.append(_blank_child(row, sub=vtag, desc=valve_desc.get(vtag, vtag)))

        # Inventory lines the model omitted.
        for ltag in sorted(line_tags):
            if ltag in lines_in_tree or not template:
                continue
            out.append(_blank_child(template, equipment=ltag, desc=f"{ltag} PIPE"))
            m = re.search(r"(\d+)$", ltag)
            if not m:
                continue
            for vtag in sorted(set(valves_by_suffix.get(m.group(1), []))):
                if vtag in emitted_valves:
                    continue
                emitted_valves.add(vtag)
                out.append(_blank_child(template, sub=vtag, desc=valve_desc.get(vtag, vtag)))

        for vtag in sorted(valve_desc):
            if vtag in emitted_valves or not template:
                continue
            out.append(_blank_child(template, equipment=vtag, desc=valve_desc.get(vtag, vtag)))
        return out

    def build_hierarchy(
        self,
        inventory: Dict[str, Any],
        ctx: Dict[str, str],
        **kwargs: Any,
    ) -> List[Dict[str, str]]:
        """Deterministic GOR hierarchy — delegates to the existing builder."""
        from dwg_reader.run_hierarchy_orchestrator import build_gor_hierarchy
        return build_gor_hierarchy(inventory)

    # ------------------------------------------------------------------
    # Description normalisation
    # ------------------------------------------------------------------

    def normalize_description(self, text: str, max_len: int = 40) -> str:
        return abbreviate_pltxt(text, max_len=max_len)
