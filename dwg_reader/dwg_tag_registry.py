#!/usr/bin/env python3
"""Cross-drawing equipment-tag registry.

Per-drawing runs otherwise emit the same tag twice. On collision, keep the
instance from the drawing where the tag is a FUNCTION header; EQUIPMENT beats
SUB-EQUIPMENT. Equal-rank collisions keep the first drawing that claimed the tag.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Mapping, MutableMapping, Sequence, Tuple

from dwg_reader.io import cell as _norm, read_csv_rows

ROLE_RANK = {
    "FUNCTION": 3,
    "EQUIPMENT": 2,
    "SUB-EQUIPMENT": 1,
}

Claim = Dict[str, str]  # {role, drawing}


def _norm_tag(tag: str) -> str:
    return _norm(tag).upper().replace(" ", "")


def row_tag_and_role(row: Mapping[str, str]) -> Tuple[str, str]:
    """Return (tag, role) for a hierarchy row. Empty tag means a structural row."""
    fn = _norm_tag(row.get("FUNCTION") or "")
    eq = _norm_tag(row.get("EQUIPMENT") or "")
    sub = _norm_tag(row.get("SUB-EQUIPMENT") or "")
    if fn and not eq and not sub:
        return fn, "FUNCTION"
    if eq:
        return eq, "EQUIPMENT"
    if sub:
        return sub, "SUB-EQUIPMENT"
    return "", ""


class TagRegistry:
    """Persistent {tag: {role, drawing}} claims."""

    def __init__(self, claims: MutableMapping[str, Claim] | None = None) -> None:
        self.claims: Dict[str, Claim] = dict(claims or {})

    @classmethod
    def load(cls, path: Path) -> "TagRegistry":
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()
        raw = data.get("claims") if isinstance(data, dict) else None
        claims: Dict[str, Claim] = {}
        if isinstance(raw, dict):
            for tag, claim in raw.items():
                if isinstance(claim, dict) and claim.get("role") and claim.get("drawing"):
                    claims[_norm_tag(str(tag))] = {
                        "role": str(claim["role"]),
                        "drawing": str(claim["drawing"]),
                    }
        return cls(claims)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"claims": self.claims}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def winner(self, tag: str, role: str, drawing: str) -> bool:
        """True if this (tag, role, drawing) should be kept. Updates the claim."""
        tag_n = _norm_tag(tag)
        if not tag_n:
            return True
        incoming = ROLE_RANK.get(role, 0)
        existing = self.claims.get(tag_n)
        existing_rank = ROLE_RANK.get((existing or {}).get("role") or "", 0)
        if existing is None or incoming > existing_rank:
            self.claims[tag_n] = {"role": role, "drawing": drawing}
            return True
        return existing.get("drawing") == drawing and incoming >= existing_rank


def compute_winners(
    drawing_rows: Sequence[Tuple[str, Sequence[Mapping[str, str]]]],
) -> Dict[str, Claim]:
    """Two-pass: highest role wins; ties keep the first drawing in ``drawing_rows``."""
    best: Dict[str, Claim] = {}
    for drawing, rows in drawing_rows:
        for row in rows:
            tag, role = row_tag_and_role(row)
            if not tag:
                continue
            rank = ROLE_RANK.get(role, 0)
            current = best.get(tag)
            if current is None or rank > ROLE_RANK.get(current["role"], 0):
                best[tag] = {"role": role, "drawing": drawing}
    return best


def filter_rows_for_drawing(
    rows: Sequence[Mapping[str, str]],
    drawing: str,
    winners: Mapping[str, Claim],
) -> List[Dict[str, str]]:
    """Keep rows whose tag is unclaimed or won by ``drawing``."""
    out: List[Dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        tag, _role = row_tag_and_role(row)
        if not tag:
            out.append(dict(row))
            continue
        claim = winners.get(tag)
        if claim is not None and claim.get("drawing") != drawing:
            continue
        if tag in seen:
            continue
        seen.add(tag)
        out.append(dict(row))
    return out


def dedupe_hierarchies(
    drawing_rows: Sequence[Tuple[str, Sequence[Mapping[str, str]]]],
) -> Dict[str, List[Dict[str, str]]]:
    """Filter every drawing's rows so each tag is kept in exactly one drawing."""
    winners = compute_winners(drawing_rows)
    return {
        drawing: filter_rows_for_drawing(rows, drawing, winners)
        for drawing, rows in drawing_rows
    }


def apply_registry_to_rows(
    rows: Sequence[Mapping[str, str]],
    *,
    drawing: str,
    registry: TagRegistry,
) -> List[Dict[str, str]]:
    """Sequential claim: skip tags already owned at equal-or-higher rank elsewhere."""
    out: List[Dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        tag, role = row_tag_and_role(row)
        if not tag:
            out.append(dict(row))
            continue
        if tag in seen:
            continue
        if not registry.winner(tag, role, drawing):
            continue
        seen.add(tag)
        out.append(dict(row))
    return out


def apply_registry_from_output_dir(
    current_rows: Sequence[Mapping[str, str]],
    *,
    drawing: str,
    out_dir: Path,
) -> List[Dict[str, str]]:
    """Recompute winners from every ``*.hierarchy_orchestrator.csv`` in ``out_dir``.

    The current drawing's in-memory rows replace the on-disk copy so a FUNCTION
    header in this run beats an EQUIPMENT row written by an earlier drawing.
    """
    suffix = ".hierarchy_orchestrator.csv"
    items: List[Tuple[str, Sequence[Mapping[str, str]]]] = [
        (path.name[: -len(suffix)], read_csv_rows(path, missing_ok=True))
        for path in sorted(out_dir.glob(f"*{suffix}"))
        if path.name[: -len(suffix)] != drawing
    ]
    items.append((drawing, list(current_rows)))
    winners = compute_winners(items)
    filtered = filter_rows_for_drawing(current_rows, drawing, winners)
    registry = TagRegistry(winners)
    registry.save(out_dir / "tag_registry.json")
    return filtered
