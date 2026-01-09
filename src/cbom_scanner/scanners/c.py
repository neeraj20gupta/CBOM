"""C/C++ scanner."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from cbom_scanner.core.models import RawFinding
from cbom_scanner.core.orchestrator import ScanOptions
from cbom_scanner.core.rules import load_rules
from cbom_scanner.scanners.base import LanguageScanner
from cbom_scanner.scanners.common import scan_tree_sitter


class CScanner(LanguageScanner):
    language = "c"

    def __init__(self, rules_path: Path) -> None:
        self.rule_set = load_rules(rules_path)

    def supports(self, path: Path, options: ScanOptions) -> bool:
        return path.suffix in {".c", ".h", ".cpp", ".hpp"}

    def scan(self, files: Iterable[Path]) -> List[RawFinding]:
        findings: List[RawFinding] = []
        for path in files:
            if path.suffix in {".c", ".h"}:
                findings.extend(scan_tree_sitter([path], self.rule_set, "c"))
            else:
                findings.extend(scan_tree_sitter([path], self.rule_set, "cpp"))
        return findings
