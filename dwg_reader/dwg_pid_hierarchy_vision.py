#!/usr/bin/env python3
"""Deprecated shim — CAD-graph hierarchy lives in ``dwg_reader.legacy``."""

from __future__ import annotations

from dwg_reader.legacy.hierarchy_vision import main

__all__ = ["main"]
