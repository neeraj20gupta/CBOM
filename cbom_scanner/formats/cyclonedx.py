"""CycloneDX 1.5 JSON formatter."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional

from cbom_scanner import __version__
from cbom_scanner.core.models import CryptoFinding


def _finding_component(component: str, finding: CryptoFinding) -> dict:
    properties = [
        {"name": "cbom:algorithm", "value": finding.algorithm},
        {"name": "cbom:mode", "value": finding.mode},
        {"name": "cbom:keySizeBits", "value": finding.key_size_bits},
        {"name": "cbom:library", "value": finding.library},
        {"name": "cbom:api", "value": finding.api},
        {"name": "cbom:assetType", "value": finding.asset_type},
        {"name": "cbom:confidence", "value": finding.confidence},
        {"name": "cbom:evidence:file", "value": finding.evidence.file},
        {"name": "cbom:evidence:line", "value": str(finding.evidence.line)},
        {"name": "cbom:evidence:column", "value": str(finding.evidence.column)},
        {"name": "cbom:evidence:snippet", "value": finding.evidence.snippet},
    ]
    if finding.evidence.function:
        properties.append({"name": "cbom:evidence:function", "value": finding.evidence.function})
    if finding.notes:
        properties.append({"name": "cbom:notes", "value": finding.notes})
    return {
        "type": "library",
        "name": f"{finding.algorithm}-{finding.mode}",
        "version": finding.key_size_bits,
        "properties": properties,
        "bom-ref": finding.id,
        "supplier": {"name": finding.library},
        "description": f"Crypto usage in {component}",
    }


def build_cyclonedx(component: str, findings: Iterable[CryptoFinding]) -> dict:
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tools": [{"name": "cbom-scanner", "version": __version__}],
            "component": {"name": component, "type": "application"},
        },
        "components": [_finding_component(component, finding) for finding in findings],
    }


def write_cyclonedx(path: Optional[Path], component: str, findings: List[CryptoFinding]) -> None:
    payload = build_cyclonedx(component, findings)
    output = json.dumps(payload, indent=2, sort_keys=True)
    if path is None or str(path) == "-":
        print(output)
        return
    path.write_text(output)
