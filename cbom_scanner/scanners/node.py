"""Node.js (JavaScript/TypeScript) scanner."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

import re

from cbom_scanner.core.models import RawFinding
from cbom_scanner.core.orchestrator import ScanOptions
from cbom_scanner.core.rules import load_rules
from cbom_scanner.core.utils import collect_call_sites
from cbom_scanner.scanners.base import LanguageScanner
from cbom_scanner.scanners.common import scan_regex


_CONST_ASSIGN_RE = re.compile(
    r"\bconst\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<quote>['\"`])(?P<value>[^\n]*?)(?P=quote)"
)


def _collect_const_strings(source_text: str) -> dict[str, str]:
    constants: dict[str, str] = {}
    for line in source_text.splitlines():
        match = _CONST_ASSIGN_RE.search(line)
        if not match:
            continue
        value = match.group("value")
        if match.group("quote") == "`" and "${" in value:
            continue
        constants[match.group("name")] = value
    return constants


def _safe_arg(args: List[str], index: Optional[int]) -> Optional[str]:
    if index is None:
        return None
    if 0 <= index < len(args):
        return args[index]
    return None


def _resolve_arg(args: List[str], index: Optional[int], constants: dict[str, str]) -> Optional[str]:
    arg = _safe_arg(args, index)
    if not arg:
        return None
    if arg in constants:
        return constants[arg]
    if "${" in arg:
        return None
    return arg


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
            source_text = path.read_text(encoding="utf-8", errors="replace")
            language_name = "javascript"
            if path.suffix in {".ts", ".tsx"}:
                language_name = "typescript"
            try:
                call_sites = list(collect_call_sites(source_text, language_name))
            except RuntimeError:
                findings.extend(scan_regex([path], self.rule_set, language_name))
                continue
            constants = _collect_const_strings(source_text)
            for call_site in call_sites:
                for rule in self.rule_set.calls:
                    function_text = call_site.function
                    if not (function_text.endswith(rule.call) or function_text == rule.call):
                        continue
                    algorithm = rule.algorithm or _resolve_arg(
                        call_site.args, rule.arg_indexes.get("algorithm"), constants
                    )
                    mode = rule.mode or _resolve_arg(
                        call_site.args, rule.arg_indexes.get("mode"), constants
                    )
                    key_size_bits = rule.key_size_bits or _resolve_arg(
                        call_site.args, rule.arg_indexes.get("key_size_bits"), constants
                    )
                    findings.append(
                        RawFinding(
                            file=str(path),
                            line=call_site.line,
                            column=call_site.column,
                            snippet=call_site.snippet,
                            function=call_site.function_context,
                            api=rule.api,
                            library=rule.library,
                            algorithm=algorithm,
                            mode=mode,
                            key_size_bits=key_size_bits,
                            confidence=rule.confidence,
                            asset_type=rule.asset_type,
                            notes=None,
                        )
                    )
        return findings
