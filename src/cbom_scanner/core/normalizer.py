"""Normalization of raw findings into CBOM model."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from typing import Optional

from cbom_scanner.core.models import CryptoFinding, Evidence, RawFinding


_ALG_MAP = {
    "sha1": ("SHA-1", "HASH"),
    "sha224": ("SHA-224", "HASH"),
    "sha256": ("SHA-256", "HASH"),
    "sha384": ("SHA-384", "HASH"),
    "sha512": ("SHA-512", "HASH"),
    "md5": ("MD5", "HASH"),
    "rsa": ("RSA", "ASYMMETRIC"),
    "ecdsa": ("ECDSA", "SIGNATURE"),
    "hmac": ("HMAC", "MAC"),
    "hkdf": ("HKDF", "KDF"),
}


_AES_PREFIXES = ("aes-", "aes_", "aes/")


def _stable_id(raw: RawFinding) -> str:
    payload = "|".join(
        [
            raw.file,
            str(raw.line),
            str(raw.column),
            raw.api,
            raw.algorithm or "UNKNOWN",
            raw.mode or "UNKNOWN",
            raw.key_size_bits or "UNKNOWN",
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _parse_aes(algorithm: str) -> tuple[str, str, str]:
    normalized = algorithm.lower().replace("_", "-")
    normalized = normalized.replace("/", "-")
    parts = normalized.split("-")
    key_size = "UNKNOWN"
    mode = "UNKNOWN"
    if len(parts) >= 2 and parts[1].isdigit():
        key_size = parts[1]
    if len(parts) >= 3:
        mode = parts[2].upper()
    return "AES", mode, key_size


def _normalize_algorithm(raw: RawFinding) -> tuple[str, str, str, Optional[str]]:
    algorithm = raw.algorithm
    mode = raw.mode or "UNKNOWN"
    key_size = raw.key_size_bits or "UNKNOWN"
    asset_type = raw.asset_type
    if algorithm:
        lowered = algorithm.lower()
        if lowered.startswith(_AES_PREFIXES):
            algorithm, mode, key_size = _parse_aes(algorithm)
            asset_type = asset_type or "SYMMETRIC"
        elif lowered in _ALG_MAP:
            algorithm, asset_type = _ALG_MAP[lowered]
        else:
            algorithm = algorithm.upper()
    else:
        algorithm = "UNKNOWN"
    return algorithm, mode, key_size, asset_type


def normalize(raw: RawFinding) -> CryptoFinding:
    algorithm, mode, key_size, asset_type = _normalize_algorithm(raw)
    asset_type = asset_type or "UNKNOWN"
    evidence = Evidence(
        file=raw.file,
        line=raw.line,
        column=raw.column,
        function=raw.function,
        snippet=raw.snippet,
    )
    stable = _stable_id(raw)
    return CryptoFinding(
        id=stable,
        asset_type=asset_type,
        algorithm=algorithm,
        mode=mode,
        key_size_bits=key_size,
        library=raw.library,
        api=raw.api,
        confidence=raw.confidence,
        evidence=evidence,
        notes=raw.notes,
    )
