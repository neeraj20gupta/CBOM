"""Orchestrator for scanning repositories."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from cbom_scanner.core.models import CryptoFinding
from cbom_scanner.core.options import ScanOptions
from cbom_scanner.core.normalizer import normalize
from cbom_scanner.scanners.base import LanguageScanner


class Orchestrator:
    def __init__(self, scanners: Sequence[LanguageScanner]) -> None:
        self.scanners = scanners

    def discover_files(self, repo_path: Path) -> List[Path]:
        files = [path for path in repo_path.rglob("*") if path.is_file()]
        return sorted(files)

    def scan(self, repo_path: Path, options: ScanOptions) -> List[CryptoFinding]:
        files = self.discover_files(repo_path)
        findings: List[CryptoFinding] = []
        for scanner in self.scanners:
            supported = [path for path in files if scanner.supports(path, options)]
            if not supported:
                continue
            raw_findings = scanner.scan(supported)
            findings.extend(normalize(raw) for raw in raw_findings)
        return sorted(findings, key=lambda finding: finding.id)
