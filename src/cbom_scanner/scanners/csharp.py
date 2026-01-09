"""C#/.NET scanner (heuristic)."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from cbom_scanner.core.models import RawFinding
from cbom_scanner.core.orchestrator import ScanOptions
from cbom_scanner.core.rules import load_rules
from cbom_scanner.scanners.base import LanguageScanner
from cbom_scanner.scanners.common import scan_regex


class CSharpScanner(LanguageScanner):
    language = "csharp"

    def __init__(self, rules_path: Path) -> None:
        self.rule_set = load_rules(rules_path)

    def supports(self, path: Path, options: ScanOptions) -> bool:
        return path.suffix == ".cs"

    def scan(self, files: Iterable[Path]) -> List[RawFinding]:
        return scan_regex(files, self.rule_set, "csharp")
