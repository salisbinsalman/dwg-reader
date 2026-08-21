"""Repo-root and output-directory paths. Independent of process CWD."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STANDARDS_DIR = REPO_ROOT / "standards"
PROMPTS_DIR = REPO_ROOT / "prompts"
RESOURCES_DIR = REPO_ROOT / "resources"


def safe_name(path: Path) -> str:
    return path.stem.replace("/", "_")


def evidence_dir(out_dir: Path) -> Path:
    """Cropped viewer / hierarchy evidence images live under outputs/evidence."""
    path = Path(out_dir) / "evidence"
    path.mkdir(parents=True, exist_ok=True)
    return path


def jsons_dir(out_dir: Path) -> Path:
    """Pipeline / cache JSON files live under outputs/jsons."""
    path = Path(out_dir) / "jsons"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir(out_dir: Path) -> Path:
    """Run logs live under outputs/logs."""
    path = Path(out_dir) / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def json_path(out_dir: Path, filename: str) -> Path:
    """Canonical write path for a JSON artifact."""
    return jsons_dir(out_dir) / filename


def find_json(out_dir: Path, filename: str) -> Path:
    """
    Resolve a JSON artifact: prefer outputs/jsons/, fall back to legacy outputs/ root.

    Returns the preferred jsons path even if missing (caller checks exists()).
    """
    preferred = json_path(out_dir, filename)
    if preferred.exists():
        return preferred
    legacy = Path(out_dir) / filename
    if legacy.exists():
        return legacy
    return preferred
