"""Core models for CBOM scanning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Evidence:
    file: str
    line: int
    column: int
    function: Optional[str]
    snippet: str


@dataclass(frozen=True)
class CryptoFinding:
    id: str
    asset_type: str
    algorithm: str
    mode: str
    key_size_bits: str
    library: str
    api: str
    confidence: str
    evidence: Evidence
    notes: Optional[str] = None


@dataclass(frozen=True)
class RawFinding:
    file: str
    line: int
    column: int
    snippet: str
    function: Optional[str]
    api: str
    library: str
    algorithm: Optional[str]
    mode: Optional[str]
    key_size_bits: Optional[str]
    confidence: str
    asset_type: Optional[str]
    notes: Optional[str]
