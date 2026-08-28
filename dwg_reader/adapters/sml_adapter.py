#!/usr/bin/env python3
"""
SML / Valmet PS-21 adapter for PM03 drawings.

Tag format:  PP-EE{type}{###}  e.g. 35-24P518, 35-24T601, 35-24L009
Motor tag:   strip type letter, append .1  →  35-24-518.1
Hierarchy:   Claude vision (one call per FUNCTION tag)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from dwg_reader.adapters.base import BaseAdapter
from dwg_reader.dwg_floc_context import abbreviate_pltxt, infer_valve_type


class SMLAdapter(BaseAdapter):
    """SML / Valmet PS-21 adapter.  Covers STOD*, PCSG*, RAU* DWG stems."""

    ecosystem_name = "valmet"
    standard_id = "valmet_ps21"

    # Matches primary-equipment tags: 35-24P518, 35-24L009, 35-24T601
    _EQUIP_TAG_RE = re.compile(r"^\d{2}-\d{2}[A-Z]\d", re.I)
    # Matches pipeline tags: 35-24-095, 36-45-010
    _LINE_TAG_RE = re.compile(r"^\d{2}-\d{2}-\d+$", re.I)
    # Matches motor tags: 35-24-518.1, 35-24-009.2
    _MOTOR_SUFFIX_RE = re.compile(r"\.\d+$")
    # Captures area + sequence for motor derivation: 35-24P518 → (35-24)(518)
    _MOTOR_FROM_EQUIP_RE = re.compile(r"^(\d{2}-\d{2})[A-Z]+(\d+)(.*)$", re.I)

    # ------------------------------------------------------------------
    # Layer / block discovery
    # ------------------------------------------------------------------

    @property
    def layer_map(self) -> Dict[str, Tuple[str, str]]:
        return {
            "P-TANK_POS":      ("tanks", "tank_symbol"),
            "P-PUMP_POS":      ("pumps", "pump_symbol"),
            "P-PUMPS":         ("pumps", "pump_symbol"),
            "P-MOTOR_POS":     ("motors", "motor_symbol"),
            "P-AGITATOR_POS":  ("agitators", "agitator_symbol"),
            "P-EQUIPMENT_POS": ("process_equipment", "equipment_symbol"),
            "P-EQUIPMENTS":    ("process_equipment", "equipment_symbol"),
            "P-VALVEPOS":      ("valves", "valve_symbol"),
            "P-CVPOS":         ("control_valves", "cv_symbol"),
            "P-INSTRPOS":      ("instruments", "instrument_symbol"),
            "P-INSTRU":        ("instruments", "instrument_symbol"),
            "P-SENSOR_POS":    ("instruments", "sensor_symbol"),
            "P-PTERMINAL_POS": ("terminals", "terminal_symbol"),
            "P-FITTINGS":      ("fittings", "fitting_symbol"),
            "P-SYMB":          ("symbols", "diagram_symbol"),
            "P-VENTS":         ("ventilation", "vent_symbol"),
            "P-FAN_POS":       ("ventilation", "fan_symbol"),
            "P-REVISIONS":     ("revisions", "revision_marker"),
            "P-DELIVERY_LIMIT": ("delivery_limits", "delivery_limit"),
            "P-A-SHEET":       ("sheet_graphics", "sheet_block"),
            "T-A-SHEET":       ("sheet_graphics", "sheet_block"),
            "P-OTHER":         ("other_inserts", "other"),
            "P-MARKBALL":      ("other_inserts", "mark_ball"),
            "P-LINEPOS":       ("line_markers", "line_annotation_block"),
        }

    # SML uses layer-first classification — block names carry no category.
    @property
    def block_map(self) -> Dict[str, str]:
        return {}

    @property
    def pipe_layers(self) -> set:
        return {
            "P-FITTINGS",
            "P-LINEPOS",
            "P-EQUIPMENTS",
            "P-WATER",
            "P-SEALING_WATER",
            "P-COOLING_WATER",
            "P-FILTERED_WATER",
            "P-WHITE_WATER",
            "P-REJECT",
            "P-AIR",
            "P-MASS1",
        }

    def classify_insert(
        self,
        ins: Dict[str, Any],
        attrs: Optional[Dict[str, str]] = None,
    ) -> Tuple[str, str, str]:
        layer = ins.get("layer") or ""
        name = (ins.get("name") or "").upper()
        # Ventilation CVs stay under ventilation, not process control valves.
        if layer == "P-VENTS" and name.startswith("CVM"):
            return "ventilation", "vent_control_valve", "high"
        if layer == "P-VENTS" and name.startswith(("PRM", "CTV", "P7A")):
            return "ventilation", "vent_instrument_symbol", "high"
        return super().classify_insert(ins, attrs)

    # ------------------------------------------------------------------
    # Tag parsing
    # ------------------------------------------------------------------

    def parse_tag(self, tag: str) -> Dict[str, str]:
        t = self._norm(tag)
        # Primary equipment: 35-24P518
        m = re.match(r"^(\d{2}-\d{2})([A-Z]+)(\d+)(.*)$", t)
        if m:
            return {
                "area": m.group(1),
                "type_letter": m.group(2),
                "sequence": m.group(3),
                "suffix": m.group(4),
                "full": t,
            }
        # Pipeline: 35-24-095
        m2 = re.match(r"^(\d{2}-\d{2})-(\d+)(.*)$", t)
        if m2:
            return {
                "area": m2.group(1),
                "type_letter": "",
                "sequence": m2.group(2),
                "suffix": m2.group(3),
                "full": t,
            }
        return {"area": "", "type_letter": "", "sequence": t, "suffix": "", "full": t}

    def is_equipment_tag(self, tag: str) -> bool:
        t = self._norm(tag)
        return bool(self._EQUIP_TAG_RE.match(t)) and not self._LINE_TAG_RE.match(t)

    def is_line_tag(self, tag: str) -> bool:
        return bool(self._LINE_TAG_RE.match(self._norm(tag)))

    def is_motor_tag(self, tag: str) -> bool:
        return bool(self._MOTOR_SUFFIX_RE.search(self._norm(tag)))

    # ------------------------------------------------------------------
    # Motor derivation
    # ------------------------------------------------------------------

    def derive_motor_tag(self, equipment_tag: str) -> Optional[str]:
        """35-24P518 → 35-24-518.1  (strip type letter, keep area, append .1)"""
        t = self._norm(equipment_tag)
        m = self._MOTOR_FROM_EQUIP_RE.match(t)
        if not m:
            return None
        area, seq, suffix = m.group(1), m.group(2), m.group(3)
        # Rotor sub-equipment like 35-24L009.1 already carries a decimal suffix.
        if suffix and suffix.startswith("."):
            return f"{area}-{seq}{suffix}"
        return f"{area}-{seq}.1"

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
        # Control-valve layer → automatic valve regardless of description.
        if layer == "P-CVPOS":
            return "AV", True
        return infer_valve_type(tag, eqktx), True

    # ------------------------------------------------------------------
    # Hierarchy building
    # ------------------------------------------------------------------

    @property
    def uses_ai_hierarchy(self) -> bool:
        return True

    @property
    def hierarchy_prompt_file(self) -> str:
        # GT-tuned Broke prompt (v2 default). Do not replace with the thin
        # adapter:valmet core+addendum — that collapsed mill-wide hit-rate.
        return "pid_hierarchy_gt_v8.md"

    def build_hierarchy(
        self,
        inventory: Dict[str, Any],
        ctx: Dict[str, str],
        **kwargs: Any,
    ) -> List[Dict[str, str]]:
        raise NotImplementedError(
            "SML adapter uses Claude vision for hierarchy. "
            "Call run_hierarchy_orchestrator.run_hierarchy_for_tag() per FUNCTION."
        )

    # ------------------------------------------------------------------
    # Description normalisation
    # ------------------------------------------------------------------

    def normalize_description(self, text: str, max_len: int = 40) -> str:
        """Full SML abbreviation pipeline (392-entry workbook + phrase rules)."""
        return abbreviate_pltxt(text, max_len=max_len)
