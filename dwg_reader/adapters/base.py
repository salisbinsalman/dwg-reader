#!/usr/bin/env python3
"""
Abstract base class for P&ID CAD ecosystem adapters.

Each adapter encapsulates the naming-standard rules for one CAD ecosystem
(SML/Valmet PS-21, GOR Fiorentini Italian, KSD Andritz Swedish) and exposes
a uniform interface for tag parsing, motor derivation, valve-type resolution,
description normalisation, and hierarchy building.

The pipeline calls adapter methods instead of hardcoding ecosystem checks.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dwg_reader.paths import STANDARDS_DIR


class BaseAdapter(ABC):
    """Adapter interface for one CAD naming standard."""

    ecosystem_name: str = ""   # "valmet" | "gor" | "ksd"
    standard_id: str = ""      # matches the standards/*.json filename stem

    # ------------------------------------------------------------------
    # Layer / block discovery
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def layer_map(self) -> Dict[str, Tuple[str, str]]:
        """Map CAD layer name → (category, sub_type).

        Category is one of: tanks, pumps, motors, agitators, valves,
        control_valves, instruments, process_equipment, fittings,
        lines, line_markers.
        """

    @property
    def block_map(self) -> Dict[str, str]:
        """Map CAD block name → category.

        Return empty dict for adapters where blocks carry no category
        information (e.g. SML where entity category comes from the layer).
        """
        return {}

    @property
    def pipe_layers(self) -> set:
        """Layers that carry pipe/process-line geometry (LINE/LWPOLYLINE)."""
        return set()

    def classify_insert(
        self,
        ins: Dict[str, Any],
        attrs: Optional[Dict[str, str]] = None,
    ) -> Tuple[str, str, str]:
        """Return (category, sub_type, confidence) for one INSERT.

        Default: layer_map, then block_map, then other_inserts.
        Adapters override when attributes beat layer names (KSD ITEM/KRETS).
        """
        del attrs  # unused in the generic path
        layer = ins.get("layer") or ""
        name = (ins.get("name") or "")
        mapped = self.layer_map.get(layer)
        if mapped:
            return mapped[0], mapped[1], "high"
        block_cat = self.block_map.get(name) or self.block_map.get(name.upper())
        if block_cat:
            return block_cat, "block_symbol", "medium"
        return "other_inserts", "unmapped_layer", "low"

    def tag_from_insert(
        self,
        block_name: str,
        attrs: Dict[str, str],
        layer: str = "",
    ) -> Tuple[str, Dict[str, Any]]:
        """Return (tag, extra_fields) for an INSERT.

        Default: use the block name as the tag (Valmet symbols). Extra may
        carry standard-specific attributes without changing the tag.
        """
        del layer
        extra: Dict[str, Any] = {}
        if attrs.get("VENIMI"):
            extra["description"] = attrs["VENIMI"]
        if attrs.get("VEPOSITIO"):
            extra["position_number"] = attrs["VEPOSITIO"]
        return block_name, extra

    def is_valve_tag(self, tag: str) -> bool:
        """True for valve tags. Default: never — valves are layer-classified."""
        del tag
        return False

    # ------------------------------------------------------------------
    # Tag parsing
    # ------------------------------------------------------------------

    @abstractmethod
    def parse_tag(self, tag: str) -> Dict[str, str]:
        """Decompose a tag string into its components.

        Returned dict always has at least:
          full         – normalised tag (uppercase, no spaces)
          type_letter  – single letter identifying equipment type (may be "")
          sequence     – numeric running-number string (may be full tag if unparsed)
        """

    @abstractmethod
    def is_equipment_tag(self, tag: str) -> bool:
        """True for primary-equipment tags (pump, tank, agitator, process machine)."""

    @abstractmethod
    def is_line_tag(self, tag: str) -> bool:
        """True for pipeline / line-number tags."""

    def is_instrument_tag(self, tag: str) -> bool:
        """True for instrument tags (default: anything that is neither equipment nor line)."""
        return not self.is_equipment_tag(tag) and not self.is_line_tag(tag)

    def is_motor_tag(self, tag: str) -> bool:
        """True when a tag already represents a motor (by suffix convention)."""
        return False

    # ------------------------------------------------------------------
    # Motor derivation
    # ------------------------------------------------------------------

    @abstractmethod
    def derive_motor_tag(self, equipment_tag: str) -> Optional[str]:
        """Return the motor tag for a driven-equipment tag, or None if not applicable."""

    # ------------------------------------------------------------------
    # Valve classification
    # ------------------------------------------------------------------

    @abstractmethod
    def resolve_valve_type(
        self,
        tag: str,
        *,
        tipo: Optional[str] = None,
        layer: Optional[str] = None,
        eqktx: str = "",
    ) -> Tuple[Optional[str], bool]:
        """Resolve SAP valve type for one valve record.

        Returns (sap_valve_type, is_valve).
          sap_valve_type: "NC" | "HV" | "AV" | "SV" | "CHK" | None
          is_valve:       False only when the TIPO code identifies a non-valve
                          component (e.g. GOR blind flange FL code).
        ``tipo`` carries the raw TIPO_VALVOLA attribute for GOR Code-14 drawings.
        ``layer`` is the CAD layer name (used by SML/KSD to distinguish HV / AV).
        ``eqktx`` is the equipment description text (used for keyword inference).
        """

    # ------------------------------------------------------------------
    # Hierarchy building
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def uses_ai_hierarchy(self) -> bool:
        """True if hierarchy building requires a Claude vision call."""

    @property
    def hierarchy_prompt_file(self) -> str:
        """Prompt id for vision hierarchy (``adapter:<ecosystem>`` or a prompts/ file)."""
        return f"adapter:{self.ecosystem_name}"

    @property
    def hierarchy_crop_half(self) -> Optional[float]:
        """Override adaptive-zoom max half-size (CAD units), or None for the CLI default."""
        return None

    def repair_hierarchy(
        self,
        rows: List[Dict[str, str]],
        inventory: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        """Post-process AI hierarchy rows. Default: unchanged."""
        del inventory
        return rows

    @abstractmethod
    def build_hierarchy(
        self,
        inventory: Dict[str, Any],
        ctx: Dict[str, str],
        **kwargs: Any,
    ) -> List[Dict[str, str]]:
        """Build hierarchy CSV rows from inventory + FLOC context.

        For AI-backed adapters this raises NotImplementedError — the caller
        should use run_hierarchy_orchestrator.run_hierarchy_for_tag() directly.
        """

    # ------------------------------------------------------------------
    # Description normalisation
    # ------------------------------------------------------------------

    def normalize_description(self, text: str, max_len: int = 40) -> str:
        """Normalise a free-text description to SAP PLTXT format (≤40 chars, UPPERCASE)."""
        s = re.sub(r"\s+", " ", str(text or "").strip()).upper()
        return s[:max_len]

    # ------------------------------------------------------------------
    # Standard JSON loader
    # ------------------------------------------------------------------

    @lru_cache(maxsize=1)
    def load_standard(self) -> Dict[str, Any]:
        """Load and return the standard JSON for this adapter (cached)."""
        p = STANDARDS_DIR / f"{self.standard_id}.json"
        with p.open(encoding="utf-8") as fh:
            return json.load(fh)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _norm(tag: str) -> str:
        return re.sub(r"\s+", "", str(tag or "")).upper()
