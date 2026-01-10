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
    "sha3-256": ("SHA3-256", "HASH"),
    "sha3-384": ("SHA3-384", "HASH"),
    "sha3-512": ("SHA3-512", "HASH"),
    "md5": ("MD5", "HASH"),
    "rsa": ("RSA", "ASYMMETRIC"),
    "ecdsa": ("ECDSA", "SIGNATURE"),
    "ed25519": ("ED25519", "SIGNATURE"),
    "hmac": ("HMAC", "MAC"),
    "hkdf": ("HKDF", "KDF"),
    "pbkdf2": ("PBKDF2", "KDF"),
    "scrypt": ("SCRYPT", "KDF"),
    "chacha20": ("CHACHA20", "AEAD"),
    "chacha20-poly1305": ("CHACHA20", "AEAD"),
    "tls": ("TLS", "PROTOCOL"),
    "ssh": ("SSH", "PROTOCOL"),
    "x.509": ("X.509", "CERTIFICATE"),
}


_AES_PREFIXES = ("aes-", "aes_", "aes/")


def _stable_id(raw: RawFinding, algorithm: str, mode: str) -> str:
    payload = "|".join(
        [
            raw.file,
            str(raw.line),
            raw.api,
            algorithm,
            mode,
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


def _parse_signature_algorithm(algorithm: str) -> Optional[tuple[str, str]]:
    normalized = algorithm.lower().replace("_", "-").replace("/", "-")
    if "rsa" in normalized and "sha" in normalized:
        for digest in ("sha1", "sha224", "sha256", "sha384", "sha512"):
            if digest in normalized:
                return "RSA", _ALG_MAP[digest][0]
    if "ecdsa" in normalized and "sha" in normalized:
        for digest in ("sha1", "sha224", "sha256", "sha384", "sha512"):
            if digest in normalized:
                return "ECDSA", _ALG_MAP[digest][0]
    return None


def _normalize_mode(mode: Optional[str]) -> str:
    if not mode:
        return "UNKNOWN"
    normalized = mode.replace("_", "-").replace("/", "-")
    return normalized.upper()


def _normalize_key_size(key_size_bits: Optional[str]) -> str:
    if not key_size_bits:
        return "UNKNOWN"
    normalized = key_size_bits.replace("_", "-")
    curve_map = {
        "p256": "256",
        "p-256": "256",
        "prime256v1": "256",
        "secp256r1": "256",
        "secp256k1": "256",
        "nid-x9-62-prime256v1": "256",
        "p384": "384",
        "p-384": "384",
        "secp384r1": "384",
        "nid-secp384r1": "384",
        "p521": "521",
        "p-521": "521",
        "secp521r1": "521",
        "nid-secp521r1": "521",
    }
    lowered = normalized.lower()
    for key, size in curve_map.items():
        if key in lowered:
            return size
    return key_size_bits


def _normalize_algorithm(raw: RawFinding) -> tuple[str, str, str, Optional[str]]:
    algorithm = raw.algorithm
    mode = raw.mode or "UNKNOWN"
    key_size = raw.key_size_bits or "UNKNOWN"
    asset_type = raw.asset_type
    if algorithm:
        lowered = algorithm.lower()
        compact = lowered.replace("-", "").replace("_", "")
        if lowered.startswith(_AES_PREFIXES):
            algorithm, mode, key_size = _parse_aes(algorithm)
            asset_type = asset_type or "SYMMETRIC"
        elif lowered.startswith("evp_"):
            normalized = lowered.replace("evp_", "").replace("()", "")
            if normalized.startswith("aes_"):
                algorithm, mode, key_size = _parse_aes(normalized)
                asset_type = asset_type or "SYMMETRIC"
            elif normalized in _ALG_MAP:
                algorithm, mapped_type = _ALG_MAP[normalized]
                asset_type = asset_type or mapped_type
            else:
                algorithm = algorithm.upper()
        elif compact in _ALG_MAP:
            algorithm, mapped_type = _ALG_MAP[compact]
            asset_type = asset_type or mapped_type
        elif lowered.startswith("sha") and "-" not in lowered:
            if lowered in _ALG_MAP:
                algorithm, mapped_type = _ALG_MAP[lowered]
                asset_type = asset_type or mapped_type
        elif lowered in _ALG_MAP:
            algorithm, mapped_type = _ALG_MAP[lowered]
            asset_type = asset_type or mapped_type
            if lowered == "chacha20-poly1305":
                mode = "POLY1305"
        elif lowered.startswith("chacha20") and "poly1305" in lowered:
            algorithm = "CHACHA20"
            mode = "POLY1305"
            asset_type = asset_type or "AEAD"
        elif signature := _parse_signature_algorithm(algorithm):
            algorithm, mode = signature
            asset_type = asset_type or "SIGNATURE"
        else:
            algorithm = algorithm.upper()
    else:
        algorithm = "UNKNOWN"
    return algorithm, _normalize_mode(mode), _normalize_key_size(key_size), asset_type


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
    stable = _stable_id(raw, algorithm, mode)
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
