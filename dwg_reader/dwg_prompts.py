#!/usr/bin/env python3
"""Load prompt templates from the prompts/ directory."""

from __future__ import annotations

from pathlib import Path
from string import Template
from typing import Mapping, Optional

from dwg_reader.paths import PROMPTS_DIR


def load_prompt(name: str, mapping: Optional[Mapping[str, object]] = None) -> str:
    """
    Load ``prompts/<name>`` and optionally substitute ``$placeholders``.

    ``name`` may include an extension (``pid_hierarchy_from_shot.md``) or not;
    if no extension is given, ``.md`` then ``.txt`` are tried.

    Special form ``adapter:<ecosystem>`` concatenates the shared core with the
    matching standard addendum (sml / gor / ksd).
    """
    if str(name).startswith("adapter:"):
        return load_hierarchy_prompt(str(name).split(":", 1)[1], mapping)

    path = _resolve_prompt_path(name)
    text = path.read_text(encoding="utf-8")
    if mapping is None:
        return text.strip()
    # Safe for JSON braces in the template: only $var / ${var} are substituted.
    safe = {str(k): "" if v is None else str(v) for k, v in mapping.items()}
    return Template(text).safe_substitute(safe).strip()


_ECO_ADDENDUM = {
    "valmet": "sml",
    "sml": "sml",
    "gor": "gor",
    "ksd": "ksd",
}


def load_hierarchy_prompt(
    ecosystem: str,
    mapping: Optional[Mapping[str, object]] = None,
) -> str:
    """Shared core + per-standard addendum for hierarchy vision."""
    key = _ECO_ADDENDUM.get(str(ecosystem or "").strip().lower(), "sml")
    core = load_prompt("pid_hierarchy_core.md", mapping)
    addendum = load_prompt(f"pid_hierarchy_addendum_{key}.md", mapping)
    return f"{core}\n\n---\n\n{addendum}"


def _resolve_prompt_path(name: str) -> Path:
    candidate = Path(name)
    if candidate.is_absolute() and candidate.is_file():
        return candidate

    direct = PROMPTS_DIR / name
    if direct.is_file():
        return direct

    stem = name
    for ext in (".md", ".txt"):
        if stem.endswith(ext):
            break
        path = PROMPTS_DIR / f"{stem}{ext}"
        if path.is_file():
            return path

    raise FileNotFoundError(f"Prompt not found: {name} (looked under {PROMPTS_DIR})")
