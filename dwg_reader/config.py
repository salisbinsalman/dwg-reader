"""Single source of truth for model, prompt, and legend defaults."""

from __future__ import annotations

from pathlib import Path

from dwg_reader.paths import STANDARDS_DIR

DEFAULT_MODEL_ID = "eu.anthropic.claude-sonnet-4-6"
HIERARCHY_PROMPT_FILE = "pid_hierarchy_gt_v8.md"
DEFAULT_AWS_REGION = "eu-west-2"
LEGEND_PATH = STANDARDS_DIR / "legend.png"


def legend_path(override: str | Path | None = None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    return LEGEND_PATH
