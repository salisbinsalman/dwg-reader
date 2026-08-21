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
    """
    path = _resolve_prompt_path(name)
    text = path.read_text(encoding="utf-8")
    if mapping is None:
        return text.strip()
    # Safe for JSON braces in the template: only $var / ${var} are substituted.
    safe = {str(k): "" if v is None else str(v) for k, v in mapping.items()}
    return Template(text).safe_substitute(safe).strip()


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
