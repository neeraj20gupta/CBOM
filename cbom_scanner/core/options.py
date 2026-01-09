"""Scan options."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScanOptions:
    include_ts: bool = False
