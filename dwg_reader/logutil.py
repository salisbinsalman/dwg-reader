"""Process-wide logging for the DWG pipeline.

CLI entry points call ``configure_logging()`` once. Library code uses
``get_logger(__name__)``. CAD attribute probes that used to swallow
``Exception`` should call ``dxf_probe_failed`` at DEBUG so failures are
visible without flooding INFO.
"""

from __future__ import annotations

import logging
import sys
from typing import Union

LOGGER_NAME = "dwg_reader"


def get_logger(name: str | None = None) -> logging.Logger:
    if not name:
        return logging.getLogger(LOGGER_NAME)
    if name == LOGGER_NAME or name.startswith(LOGGER_NAME + "."):
        return logging.getLogger(name)
    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def configure_logging(level: Union[int, str] = logging.INFO) -> logging.Logger:
    """Attach a stderr handler to the package logger if none exists yet."""
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger(LOGGER_NAME)
    root.setLevel(level)
    if not root.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        root.addHandler(handler)
        root.propagate = False
    return root


def dxf_probe_failed(exc: BaseException, what: str = "") -> None:
    """Log a skipped CAD attribute/table probe without raising."""
    suffix = f" ({what})" if what else ""
    get_logger("cad").debug("DXF probe skipped%s: %s", suffix, exc)
