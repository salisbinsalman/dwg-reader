"""
CAD ecosystem adapter registry.

Usage::

    from dwg_reader.adapters import adapter_for

    eco = dwg_ecosystem.detect(dwg_stem, ctx=ctx)
    adapter = adapter_for(eco.name)

    motor_tag = adapter.derive_motor_tag("35-24P518")     # SML → "35-24-518.1"
    vtype, ok  = adapter.resolve_valve_type("168V-521", tipo="2K0-BF-65")  # GOR → "NC", True
    parsed     = adapter.parse_tag("122E-001")             # KSD → {area: "22", ...}
"""

from __future__ import annotations

from dwg_reader.adapters.base import BaseAdapter
from dwg_reader.adapters.gor_adapter import GORAdapter
from dwg_reader.adapters.ksd_adapter import KSDAdapter
from dwg_reader.adapters.sml_adapter import SMLAdapter

_REGISTRY: dict[str, type[BaseAdapter]] = {
    "valmet": SMLAdapter,
    "gor":    GORAdapter,
    "ksd":    KSDAdapter,
}


class UnknownEcosystemError(ValueError):
    """Raised when adapter_for() is given a name that is not valmet/gor/ksd."""


def adapter_for(ecosystem_name: str) -> BaseAdapter:
    """Return an initialised adapter for *ecosystem_name* ("valmet" | "gor" | "ksd").

    Unknown names raise UnknownEcosystemError — do not silently run SML
    rules on a KSD/GOR drawing.
    """
    key = str(ecosystem_name or "").strip().lower()
    cls = _REGISTRY.get(key)
    if cls is None:
        known = ", ".join(sorted(_REGISTRY))
        raise UnknownEcosystemError(
            f"Unknown CAD ecosystem {ecosystem_name!r}. Expected one of: {known}."
        )
    return cls()


def adapter_classes() -> dict[str, type[BaseAdapter]]:
    """Return a copy of the adapter-class registry."""
    return dict(_REGISTRY)


__all__ = [
    "BaseAdapter",
    "SMLAdapter",
    "GORAdapter",
    "KSDAdapter",
    "UnknownEcosystemError",
    "adapter_for",
    "adapter_classes",
]
