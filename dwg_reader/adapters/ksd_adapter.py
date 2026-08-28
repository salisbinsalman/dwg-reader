#!/usr/bin/env python3
"""
KSD / Andritz KSDM160104 adapter for TM01 drawings (KSDM* DWG stems).

Tag format:  xyyz-aaa
  x    — machine digit (1 = TM01, 2 = TM02)
  yy   — 2-digit area code (22=softwood, 24=hardwood, 26=broke, 32=white water…)
  z    — function letter (E=equipment, A=agitator, P=pump, T=tank, V=valve, L=line, X=other)
  aaa  — 3-digit running number (000–999)

CAD encoding (validated on parsed KSDM sheets, not Valmet P-* layers):
  ITEM          — equipment tag (122E-001)
  KRETS + POSNR — instrument loop (126LC + 001 → 126LC-001)
                  POSNR may already be a full tag (180V-152) — do not compose
  PIPEID        — line number (126L-002)
  PIPEDATA      — size-media-spec (200-P96-VE10H2A)
  HAND-VALVE / INSTR-VALVE — manual vs control valves
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from dwg_reader.adapters.base import BaseAdapter
from dwg_reader.dwg_floc_context import abbreviate_pltxt, infer_valve_type

_EQUIP_TAG_RE = re.compile(r"^(\d)(\d{2})([A-Z])-(\d{3})$", re.I)
_LINE_TAG_RE = re.compile(r"^\d{3}L-\d{3}$", re.I)
_VALVE_TAG_RE = re.compile(r"^\d{3}V-\d{3}$", re.I)
_INSTR_TAG_RE = re.compile(r"^\d{3}([A-Z]{2,4})\d*-\d{3}$", re.I)
_MOTOR_SUFFIX_RE = re.compile(r"-M\d+$", re.I)
_FULL_TAG_IN_POSNR_RE = re.compile(r"^\d{3}[A-Z]", re.I)

_EQUIP_LETTERS = frozenset("EAPTX")
_DRIVEN_LETTERS = frozenset("EAPX")  # tanks/valves/lines are not driven

_LETTER_TO_CATEGORY = {
    "E": "process_equipment",
    "A": "agitators",
    "P": "pumps",
    "T": "tanks",
    "X": "process_equipment",
    "V": "valves",
    "L": "line_markers",
}

# KSDM160104 §2 — names from the PDF; FLOC process codes are SML mappings.
_AREA_CODES: Dict[str, Dict[str, str]] = {
    "10": {"name": "General", "process": "GEN", "sub_process": "GEN1"},
    "20": {"name": "Bale handling", "process": "PL", "sub_process": "PL0"},
    "21": {"name": "Pulp dissolving", "process": "PL", "sub_process": "PL0"},
    "22": {"name": "Softwood pulping", "process": "PL", "sub_process": "PL1"},
    "24": {"name": "Hardwood pulping", "process": "PL", "sub_process": "PL2"},
    "26": {"name": "Internal broke", "process": "BR", "sub_process": "BR1"},
    "28": {"name": "Converting broke", "process": "BR", "sub_process": "BR2"},
    "30": {"name": "Pulp mixing", "process": "AP", "sub_process": "AP1"},
    "32": {"name": "White water", "process": "WW", "sub_process": "WW1"},
    "34": {"name": "Shower water", "process": "WW", "sub_process": "WW2"},
    "36": {"name": "Vacuum", "process": "VC", "sub_process": "VC1"},
    "44": {"name": "Steam and condensate", "process": "SC", "sub_process": "SC1"},
    "50": {"name": "Winder", "process": "WN", "sub_process": "WN1"},
    "54": {"name": "Roll handling", "process": "RH", "sub_process": "RH1"},
    "60": {"name": "Mist removal", "process": "WU", "sub_process": "WUC"},
    "62": {"name": "Advantage Aircap and air", "process": "WU", "sub_process": "WUC"},
    "64": {"name": "Advantage wet dust / run", "process": "WU", "sub_process": "WUH"},
    "66": {"name": "Dust control for rewinder", "process": "WU", "sub_process": "WUC"},
    "68": {"name": "Machine hall ventilation", "process": "WU", "sub_process": "WUC"},
    "70": {"name": "Paper machine main", "process": "PM", "sub_process": "PM1"},
    "75": {"name": "Control system", "process": "CS", "sub_process": "CS1"},
    "80": {"name": "Fresh water", "process": "FW", "sub_process": "FW1"},
    "82": {"name": "Compressed air", "process": "CA", "sub_process": "CA1"},
    "84": {"name": "Internal ETP", "process": "ET", "sub_process": "ET1"},
    "88": {"name": "TM chemicals", "process": "CH", "sub_process": "CH1"},
    "90": {"name": "DIP pulping", "process": "DIP", "sub_process": "DIP1"},
    "92": {"name": "DIP flotation", "process": "DIP", "sub_process": "DIP2"},
    "94": {"name": "DIP thickening", "process": "DIP", "sub_process": "DIP3"},
}


def compose_krets_posnr(krets: str, posnr: str) -> Optional[str]:
    """Join KRETS + POSNR, or keep POSNR when it is already a full tag.

    Fresh-water sheets store POSNR as 180V-152. Vacuum sheets mix 001 with
    136E-021. Composing blindly mints garbage.
    """
    k = re.sub(r"\s+", "", krets or "").upper()
    p = re.sub(r"\s+", "", posnr or "").upper()
    if p and (_FULL_TAG_IN_POSNR_RE.match(p) or _EQUIP_TAG_RE.match(p) or _INSTR_TAG_RE.match(p)):
        return p
    if k and p and p.isdigit():
        return f"{k}-{p.zfill(3)}"
    if k:
        return k
    return p or None


class KSDAdapter(BaseAdapter):
    """KSD / Andritz adapter.  Covers KSDM* DWG stems."""

    ecosystem_name = "ksd"
    standard_id = "ksd_andritz"

    @property
    def layer_map(self) -> Dict[str, Tuple[str, str]]:
        # Validated against KSDM160104102 SH03/SH07/SH09 and utility sheets.
        return {
            "PS-EQUIP": ("process_equipment", "equipment_symbol"),
            "HAND-VALVE": ("valves", "valve_symbol"),
            "TXT-HAND-VALVE": ("valves", "valve_text"),
            "INSTR-VALVE": ("control_valves", "cv_symbol"),
            "TXT-INST-VALVE": ("control_valves", "cv_text"),
            "INSTRUMENT": ("instruments", "instrument_symbol"),
            "Pipe ID": ("line_markers", "ksd_pipe_id"),
            "PS-IN": ("instruments", "instrument_line"),
            "PS-IN-P": ("instruments", "instrument_line"),
        }

    @property
    def block_map(self) -> Dict[str, str]:
        return {
            "T": "instruments",
            "instr": "instruments",
            "PIPENO": "line_markers",
            "Pipeno": "line_markers",
            "Pipeid": "line_markers",
            "Line no": "line_markers",
            "LOCALINSTR": "instruments",
            "LOCALINSTRUMENT": "instruments",
        }

    @property
    def pipe_layers(self) -> set:
        return {
            "PS",
            "PS-VACUUM",
            "Fresh water",
            "White water treated",
            "White water untreated",
            "White water treated CWW",
            "Broke",
            "SW Fiber",
            "HW Fiber",
            "Pipe ID",
        }

    def classify_insert(
        self,
        ins: Dict[str, Any],
        attrs: Optional[Dict[str, str]] = None,
    ) -> Tuple[str, str, str]:
        attrs = attrs or {}
        item = (attrs.get("ITEM") or "").strip()
        if item:
            cat = self._category_for_tag(item)
            return cat, "ksd_item", "high"
        posnr = (attrs.get("POSNR") or "").strip()
        krets = (attrs.get("KRETS") or "").strip()
        if posnr and _VALVE_TAG_RE.match(self._norm(posnr)):
            return "valves", "ksd_posnr_valve", "high"
        if posnr and _EQUIP_TAG_RE.match(self._norm(posnr)) and not _LINE_TAG_RE.match(self._norm(posnr)):
            return self._category_for_tag(posnr), "ksd_posnr_equip", "medium"
        if krets or (posnr and posnr.isdigit()):
            return "instruments", "ksd_krets", "high"
        pipe_id = (attrs.get("PIPEID") or "").strip()
        if pipe_id:
            return "line_markers", "ksd_pipe_id", "high"
        layer = ins.get("layer") or ""
        if layer in ("HAND-VALVE", "TXT-HAND-VALVE"):
            return "valves", "valve_symbol", "high"
        if layer in ("INSTR-VALVE", "TXT-INST-VALVE"):
            return "control_valves", "cv_symbol", "high"
        return super().classify_insert(ins, attrs)

    def tag_from_insert(
        self,
        block_name: str,
        attrs: Dict[str, str],
        layer: str = "",
    ) -> Tuple[str, Dict[str, Any]]:
        extra: Dict[str, Any] = {}
        item = (attrs.get("ITEM") or "").strip()
        krets = (attrs.get("KRETS") or "").strip()
        posnr = (attrs.get("POSNR") or "").strip()
        pipe_id = (attrs.get("PIPEID") or "").strip()
        pipe_data = (attrs.get("PIPEDATA") or "").strip()
        desc = (attrs.get("DESCRIPTION") or attrs.get("BENÄMNING") or "").strip()
        model = (attrs.get("MODEL") or "").strip()
        if desc:
            extra["description"] = desc
        if model:
            extra["model"] = model
        if pipe_data:
            extra["pipe_data"] = pipe_data
        if krets:
            extra["krets"] = krets
        if posnr:
            extra["posnr_raw"] = posnr
        if item:
            extra["item"] = item
            return self._norm(item), extra
        composed = compose_krets_posnr(krets, posnr)
        if composed and (krets or _FULL_TAG_IN_POSNR_RE.match(self._norm(posnr))):
            return composed, extra
        if pipe_id:
            return pipe_id, extra
        if composed:
            return composed, extra
        return block_name, extra

    def _category_for_tag(self, tag: str) -> str:
        parsed = self.parse_tag(tag)
        letter = (parsed.get("type_letter") or "").upper()
        if len(letter) == 1:
            return _LETTER_TO_CATEGORY.get(letter, "process_equipment")
        return "instruments"

    def parse_tag(self, tag: str) -> Dict[str, str]:
        t = self._norm(tag)
        m = _EQUIP_TAG_RE.match(t)
        if m:
            area = m.group(2)
            area_info = _AREA_CODES.get(area, {})
            return {
                "machine": m.group(1),
                "area": area,
                "type_letter": m.group(3).upper(),
                "sequence": m.group(4),
                "full": t,
                "area_name": area_info.get("name", ""),
                "process": area_info.get("process", ""),
                "sub_process": area_info.get("sub_process", ""),
            }
        mi = _INSTR_TAG_RE.match(t)
        if mi:
            area = t[1:3]
            area_info = _AREA_CODES.get(area, {})
            return {
                "machine": t[0],
                "area": area,
                "type_letter": mi.group(1),
                "sequence": t[-3:],
                "full": t,
                "area_name": area_info.get("name", ""),
                "process": area_info.get("process", ""),
                "sub_process": area_info.get("sub_process", ""),
            }
        return {
            "machine": "", "area": "", "type_letter": "",
            "sequence": t, "full": t,
            "area_name": "", "process": "", "sub_process": "",
        }

    def is_equipment_tag(self, tag: str) -> bool:
        t = self._norm(tag)
        m = _EQUIP_TAG_RE.match(t)
        if not m:
            return False
        return m.group(3).upper() in _EQUIP_LETTERS

    def is_line_tag(self, tag: str) -> bool:
        return bool(_LINE_TAG_RE.match(self._norm(tag)))

    def is_valve_tag(self, tag: str) -> bool:
        return bool(_VALVE_TAG_RE.match(self._norm(tag)))

    def is_instrument_tag(self, tag: str) -> bool:
        t = self._norm(tag)
        if self.is_equipment_tag(t) or self.is_line_tag(t) or self.is_valve_tag(t):
            return False
        return bool(_INSTR_TAG_RE.match(t))

    def is_motor_tag(self, tag: str) -> bool:
        return bool(_MOTOR_SUFFIX_RE.search(self._norm(tag)))

    def derive_motor_tag(self, equipment_tag: str) -> Optional[str]:
        """122E-001 → 122E-001-M1. Not applied to tanks, valves, or lines."""
        t = self._norm(equipment_tag)
        if _MOTOR_SUFFIX_RE.search(t):
            return None
        m = _EQUIP_TAG_RE.match(t)
        if m and m.group(3).upper() in _DRIVEN_LETTERS:
            return f"{t}-M1"
        return None

    def area_info(self, tag: str) -> Dict[str, str]:
        parsed = self.parse_tag(tag)
        return _AREA_CODES.get(parsed.get("area", ""), {})

    @staticmethod
    def lookup_area(area_code: str) -> Dict[str, str]:
        return _AREA_CODES.get(str(area_code).zfill(2), {})

    def resolve_valve_type(
        self,
        tag: str,
        *,
        tipo: Optional[str] = None,
        layer: Optional[str] = None,
        eqktx: str = "",
    ) -> Tuple[Optional[str], bool]:
        if layer in ("INSTR-VALVE", "TXT-INST-VALVE"):
            return "AV", True
        if layer in ("HAND-VALVE", "TXT-HAND-VALVE"):
            return infer_valve_type(tag, eqktx) if eqktx else "HV", True
        return infer_valve_type(tag, eqktx), True

    @property
    def uses_ai_hierarchy(self) -> bool:
        # Parent/child still needs spatial or BENÄMNING interpretation.
        return True

    @property
    def hierarchy_crop_half(self) -> Optional[float]:
        # Refiner / cleaner packages span ~250–350 drawing units.
        return 320.0

    def build_hierarchy(
        self,
        inventory: Dict[str, Any],
        ctx: Dict[str, str],
        **kwargs: Any,
    ) -> List[Dict[str, str]]:
        raise NotImplementedError(
            "KSD adapter uses Claude vision for hierarchy. "
            "Call run_hierarchy_orchestrator.run_hierarchy_for_tag() per FUNCTION."
        )

    def normalize_description(self, text: str, max_len: int = 40) -> str:
        return abbreviate_pltxt(text, max_len=max_len)
