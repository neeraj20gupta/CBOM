"""CLI for CBOM scanner."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from cbom_scanner.core.orchestrator import Orchestrator
from cbom_scanner.core.options import ScanOptions
from cbom_scanner.formats.cbom import write_cbom
from cbom_scanner.formats.cyclonedx import write_cyclonedx
from cbom_scanner.scanners import (
    CScanner,
    CSharpScanner,
    GoScanner,
    JavaScanner,
    NodeScanner,
    PythonScanner,
    RustScanner,
)


def _build_scanners() -> List:
    rules_dir = Path(__file__).parent / "rules"
    return [
        NodeScanner(rules_dir / "node.yaml"),
        GoScanner(rules_dir / "go.yaml"),
        RustScanner(rules_dir / "rust.yaml"),
        CScanner(rules_dir / "c.yaml"),
        PythonScanner(rules_dir / "python.yaml"),
        JavaScanner(rules_dir / "java.yaml"),
        CSharpScanner(rules_dir / "csharp.yaml"),
    ]


def _scan_repo(args: argparse.Namespace) -> int:
    repo_path = Path(args.repo).resolve()
    orchestrator = Orchestrator(_build_scanners())
    options = ScanOptions(include_ts=args.include_ts)
    findings = orchestrator.scan(repo_path, options)
    component = repo_path.name
    out_path = Path(args.out) if args.out is not None else None
    if args.format == "cbom":
        write_cbom(out_path, component, findings)
    else:
        write_cyclonedx(out_path, component, findings)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cbom_scanner")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan a repository for crypto usage")
    scan.add_argument("repo", help="Path to repository")
    scan.add_argument(
        "--out",
        default="-",
        help="Output JSON path (use '-' for stdout)",
    )
    scan.add_argument(
        "--format",
        choices=["cbom", "cyclonedx"],
        default="cyclonedx",
        help="Output format",
    )
    scan.add_argument(
        "--include-ts",
        action="store_true",
        help="Include TypeScript files in Node scanner",
    )
    scan.set_defaults(func=_scan_repo)
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
