"""Common scanning utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

import re

from cbom_scanner.core.models import RawFinding
from cbom_scanner.core.rules import CallRule, RuleSet
from cbom_scanner.core.utils import CallSite, collect_call_sites


def _match_call(rule: CallRule, call_site: CallSite) -> bool:
    function_text = call_site.function
    return function_text.endswith(rule.call) or function_text == rule.call


def _safe_arg(args: List[str], index: Optional[int]) -> Optional[str]:
    if index is None:
        return None
    if 0 <= index < len(args):
        return args[index]
    return None


def scan_tree_sitter(
    files: Iterable[Path],
    rule_set: RuleSet,
    language_name: str,
    call_node_type: str = "call_expression",
) -> List[RawFinding]:
    findings: List[RawFinding] = []
    for path in files:
        source_text = path.read_text(encoding="utf-8", errors="replace")
        try:
            call_sites = list(
                collect_call_sites(
                    source_text, language_name, call_node_type=call_node_type
                )
            )
        except RuntimeError:
            return scan_regex(files, rule_set, language_name)
        for call_site in call_sites:
            for rule in rule_set.calls:
                if not _match_call(rule, call_site):
                    continue
                algorithm = rule.algorithm or _safe_arg(
                    call_site.args, rule.arg_indexes.get("algorithm")
                )
                mode = rule.mode or _safe_arg(
                    call_site.args, rule.arg_indexes.get("mode")
                )
                key_size_bits = rule.key_size_bits or _safe_arg(
                    call_site.args, rule.arg_indexes.get("key_size_bits")
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


def scan_regex(
    files: Iterable[Path],
    rule_set: RuleSet,
    call_pattern: str,
) -> List[RawFinding]:
    findings: List[RawFinding] = []
    literal_re = re.compile(r"['\\\"]([^'\\\"]+)['\\\"]")
    for path in files:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for index, line in enumerate(lines, start=1):
            for rule in rule_set.calls:
                if rule.call not in line:
                    continue
                column = line.find(rule.call) + 1
                algorithm = rule.algorithm
                if algorithm is None:
                    match = literal_re.search(line)
                    if match:
                        algorithm = match.group(1)
                findings.append(
                    RawFinding(
                        file=str(path),
                        line=index,
                        column=column,
                        snippet=line.rstrip(),
                        function=None,
                        api=rule.api,
                        library=rule.library,
                        algorithm=algorithm,
                        mode=rule.mode,
                        key_size_bits=rule.key_size_bits,
                        confidence=rule.confidence,
                        asset_type=rule.asset_type,
                        notes="heuristic",
                    )
                )
    return findings
