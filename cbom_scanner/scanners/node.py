"""Node.js (JavaScript/TypeScript) scanner."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from cbom_scanner.core.models import RawFinding
from cbom_scanner.core.orchestrator import ScanOptions
from cbom_scanner.core.rules import load_rules
from cbom_scanner.scanners.base import LanguageScanner
from cbom_scanner.scanners.common import scan_tree_sitter


class NodeScanner(LanguageScanner):
    language = "node"

    def __init__(self, rules_path: Path) -> None:
        self.rule_set = load_rules(rules_path)

    def supports(self, path: Path, options: ScanOptions) -> bool:
        if path.suffix in {".js", ".jsx"}:
            return True
        if options.include_ts and path.suffix in {".ts", ".tsx"}:
            return True
        return False

    def scan(self, files: Iterable[Path]) -> List[RawFinding]:
        findings: List[RawFinding] = []
        for path in files:
            if path.suffix in {".js", ".jsx"}:
                findings.extend(scan_tree_sitter([path], self.rule_set, "javascript"))
            elif path.suffix in {".ts", ".tsx"}:
                findings.extend(scan_tree_sitter([path], self.rule_set, "typescript"))
        return findings
