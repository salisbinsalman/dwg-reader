"""JSON and CSV helpers used by every pipeline stage."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


def json_safe(value: Any) -> Any:
    """Convert values to JSON-serializable forms."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    mod = type(value).__module__
    if mod and mod.startswith("numpy"):
        try:
            return value.tolist()
        except (AttributeError, TypeError, ValueError):
            return float(value) if hasattr(value, "item") else str(value)
    if hasattr(value, "x") and hasattr(value, "y"):
        z = getattr(value, "z", 0.0)
        return [float(value.x), float(value.y), float(z)]
    return str(value)


def write_json(path: Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(json_safe(data), indent=2, ensure_ascii=True),
        encoding="utf-8",
    )


def load_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def cell(value: object) -> str:
    """Normalize a CSV/Excel cell: strip, treat nan/None as empty."""
    s = str(value or "").strip()
    return "" if not s or s.lower() == "nan" else s


def read_csv_rows(path: Path, *, missing_ok: bool = True) -> list[dict[str, str]]:
    path = Path(path)
    if not path.exists():
        if missing_ok:
            return []
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8", newline="") as f:
        return [{k: cell(v) for k, v in row.items()} for row in csv.DictReader(f)]


def write_csv_rows(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fieldnames: Sequence[str],
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: cell(row.get(c, "")) for c in fieldnames})
