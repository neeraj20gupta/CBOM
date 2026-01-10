from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture()
def orchestrator():
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


def test_node_coverage_improvements(orchestrator):
    from cbom_scanner.core.options import ScanOptions

    fixture_path = Path(__file__).parents[1] / "testdata" / "crypto_zoo" / "node"
    findings = orchestrator.scan(fixture_path, ScanOptions(include_ts=True))
    algorithms = {finding.algorithm for finding in findings}
    assert {
        "AES",
        "SHA-256",
        "PBKDF2",
        "SCRYPT",
        "HKDF",
        "RSA",
        "ECDH",
    }.issubset(algorithms)
    assert any(
        finding.algorithm == "AES"
        and finding.mode == "GCM"
        and finding.key_size_bits == "256"
        for finding in findings
    )
    assert any(
        finding.algorithm == "AES"
        and finding.mode == "CBC"
        and finding.key_size_bits == "192"
        for finding in findings
    )
    assert any(
        finding.algorithm == "RSA" and finding.mode == "SHA-256" for finding in findings
    )
    assert all(
        finding.evidence.file and finding.evidence.line > 0 and finding.evidence.column > 0
        for finding in findings
    )


def test_go_coverage_improvements(orchestrator):
    from cbom_scanner.core.options import ScanOptions

    fixture_path = Path(__file__).parents[1] / "testdata" / "crypto_zoo" / "go"
    findings = orchestrator.scan(fixture_path, ScanOptions(include_ts=True))
    algorithms = {finding.algorithm for finding in findings}
    assert {
        "AES",
        "CHACHA20",
        "PBKDF2",
        "SCRYPT",
        "HKDF",
        "TLS",
        "SSH",
        "RSA",
        "ECDSA",
        "ED25519",
    }.issubset(algorithms)
    assert {"GCM", "CBC", "CTR"}.issubset({finding.mode for finding in findings})
    assert any(
        finding.algorithm == "RSA" and finding.key_size_bits == "2048" for finding in findings
    )
    assert any(
        finding.algorithm == "ECDSA" and finding.key_size_bits == "256" for finding in findings
    )


def test_c_coverage_improvements(orchestrator):
    from cbom_scanner.core.options import ScanOptions

    fixture_path = Path(__file__).parents[1] / "testdata" / "crypto_zoo" / "c"
    findings = orchestrator.scan(fixture_path, ScanOptions(include_ts=True))
    algorithms = {finding.algorithm for finding in findings}
    assert {"AES", "RSA", "ECDSA"}.issubset(algorithms)
    assert any(
        finding.algorithm == "AES"
        and finding.mode == "GCM"
        and finding.key_size_bits == "256"
        for finding in findings
    )
    assert any(
        finding.algorithm == "RSA" and finding.key_size_bits == "2048" for finding in findings
    )
    assert any(
        finding.algorithm == "ECDSA" and finding.key_size_bits == "256" for finding in findings
    )
