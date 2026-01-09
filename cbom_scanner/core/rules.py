"""Rule loading for language scanners."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class CallRule:
    id: str
    call: str
    api: str
    library: str
    asset_type: Optional[str]
    confidence: str
    algorithm: Optional[str]
    mode: Optional[str]
    key_size_bits: Optional[str]
    arg_indexes: Dict[str, int]


@dataclass(frozen=True)
class RuleSet:
    language: str
    imports: List[str]
    calls: List[CallRule]


def _as_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def load_rules(rule_path: Path) -> RuleSet:
    data = json.loads(rule_path.read_text())
    language = data.get("language", rule_path.stem)
    imports = list(data.get("imports", []))
    calls: List[CallRule] = []
    for rule in data.get("calls", []):
        arg_indexes = {}
        for key in ("algorithm", "mode", "key_size_bits"):
            if key in rule.get("arg_indexes", {}):
                arg_indexes[key] = _as_int(rule["arg_indexes"][key])
        calls.append(
            CallRule(
                id=rule["id"],
                call=rule["call"],
                api=rule.get("api", rule["call"]),
                library=rule.get("library", "UNKNOWN"),
                asset_type=rule.get("asset_type"),
                confidence=rule.get("confidence", "LOW"),
                algorithm=rule.get("algorithm"),
                mode=rule.get("mode"),
                key_size_bits=rule.get("key_size_bits"),
                arg_indexes=arg_indexes,
            )
        )
    return RuleSet(language=language, imports=imports, calls=calls)


def load_rule_sets(rules_dir: Path) -> Dict[str, RuleSet]:
    rule_sets: Dict[str, RuleSet] = {}
    for path in sorted(rules_dir.glob("*.yaml")):
        rule_set = load_rules(path)
        rule_sets[rule_set.language] = rule_set
    return rule_sets


def iter_imports(rule_set: RuleSet) -> Iterable[str]:
    for entry in rule_set.imports:
        yield entry
