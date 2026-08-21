"""Shared warning filters — import early in CLI entry points."""

from __future__ import annotations

import warnings

try:
    from boto3.exceptions import PythonDeprecationWarning

    warnings.filterwarnings("ignore", category=PythonDeprecationWarning)
except ImportError:
    pass
