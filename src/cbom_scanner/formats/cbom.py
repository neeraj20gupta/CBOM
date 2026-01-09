"""Native CBOM JSON output."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

from cbom_scanner import __version__
from cbom_scanner.core.models import CryptoFinding


def _finding_payload(finding: CryptoFinding) -> dict:
    payload = {
        "id": finding.id,
        "assetType": finding.asset_type,
        "algorithm": finding.algorithm,
        "mode": finding.mode,
        "keySizeBits": finding.key_size_bits,
        "library": finding.library,
        "api": finding.api,
        "confidence": finding.confidence,
        "evidence": {
            "file": finding.evidence.file,
            "line": finding.evidence.line,
            "column": finding.evidence.column,
            "function": finding.evidence.function,
            "snippet": finding.evidence.snippet,
        },
        "notes": finding.notes,
    }
    return payload


def build_cbom(component: str, findings: Iterable[CryptoFinding]) -> dict:
    return {
        "cbomVersion": "1.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "component": component,
        "tool": {"name": "cbom-scanner", "version": __version__},
        "cryptoAssets": [_finding_payload(finding) for finding in findings],
    }


def write_cbom(path: Path, component: str, findings: List[CryptoFinding]) -> None:
    payload = build_cbom(component, findings)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))
