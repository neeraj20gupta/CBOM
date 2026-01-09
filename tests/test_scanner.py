from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture()
def orchestrator(tmp_path):
    from cbom_scanner.core.orchestrator import Orchestrator
    from cbom_scanner.scanners import (
        CScanner,
        CSharpScanner,
        GoScanner,
        JavaScanner,
        NodeScanner,
        PythonScanner,
        RustScanner,
    )

    rules_dir = Path(__file__).parents[1] / "cbom_scanner" / "rules"
    return Orchestrator(
        [
            NodeScanner(rules_dir / "node.yaml"),
            GoScanner(rules_dir / "go.yaml"),
            RustScanner(rules_dir / "rust.yaml"),
            CScanner(rules_dir / "c.yaml"),
            PythonScanner(rules_dir / "python.yaml"),
            JavaScanner(rules_dir / "java.yaml"),
            CSharpScanner(rules_dir / "csharp.yaml"),
        ]
    )


def test_scan_crypto_zoo(orchestrator):
    from cbom_scanner.core.options import ScanOptions

    fixture_path = Path(__file__).parent / "fixtures" / "crypto_zoo"
    findings = orchestrator.scan(fixture_path, ScanOptions(include_ts=True))
    algorithms = {finding.algorithm for finding in findings}
    assert "AES" in algorithms
    assert "SHA-256" in algorithms
    assert any(finding.mode == "GCM" for finding in findings)


def test_cbom_output(orchestrator):
    from cbom_scanner.core.options import ScanOptions
    from cbom_scanner.formats.cbom import build_cbom

    fixture_path = Path(__file__).parent / "fixtures" / "crypto_zoo"
    findings = orchestrator.scan(fixture_path, ScanOptions(include_ts=True))
    payload = build_cbom("crypto_zoo", findings)
    assert payload["cbomVersion"] == "1.0"
    assert payload["component"] == "crypto_zoo"
    assert payload["cryptoAssets"]


def test_cyclonedx_output(orchestrator):
    from cbom_scanner.core.options import ScanOptions
    from cbom_scanner.formats.cyclonedx import build_cyclonedx

    fixture_path = Path(__file__).parent / "fixtures" / "crypto_zoo"
    findings = orchestrator.scan(fixture_path, ScanOptions(include_ts=True))
    payload = build_cyclonedx("crypto_zoo", findings)
    assert payload["bomFormat"] == "CycloneDX"
    assert payload["specVersion"] == "1.5"
    assert payload["components"]
