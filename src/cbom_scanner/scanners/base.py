"""Base scanner interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, List

from cbom_scanner.core.models import RawFinding
from cbom_scanner.core.options import ScanOptions


class LanguageScanner(ABC):
    language: str

    @abstractmethod
    def supports(self, path: Path, options: ScanOptions) -> bool:
        raise NotImplementedError

    @abstractmethod
    def scan(self, files: Iterable[Path]) -> List[RawFinding]:
        raise NotImplementedError
