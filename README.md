# CBOM Scanner

CBOM Scanner is a lightweight, multi-language crypto-bill-of-materials (CBOM) scanner. It parses source code to identify crypto API usage and emits either **CBOM JSON** or **CycloneDX 1.5 JSON** output.

## 1) What this project does

- Scans a local repository for crypto API usage.
- Normalizes findings into a CBOM data model.
- Outputs **CBOM JSON** (native format) or **CycloneDX 1.5 JSON**.

## 2) Supported languages and current detection coverage

**Currently supported scanners** (based on the built-in rulesets):

- **Node.js (JavaScript/TypeScript)**
  - Coverage highlights: `crypto.createCipheriv`, `crypto.createHash`.
- **Go**
  - Coverage highlights: `crypto/aes.NewCipher`, `crypto/cipher.NewGCM`.
- **C (OpenSSL)**
  - Coverage highlights: `EVP_aes_256_gcm`, `EVP_sha256`.

**Placeholder/limited coverage (rules exist but are intentionally minimal today):**

- **Python** (e.g., `hashlib.sha256`, `cryptography.hazmat.primitives.ciphers.Cipher`)
- **Java** (e.g., `javax.crypto.Cipher.getInstance`, `java.security.MessageDigest.getInstance`)
- **Rust** (ruleset present, currently limited)
- **C#** (ruleset present, currently limited)

Rules live in `cbom_scanner/rules/*.yaml` and define the imports/calls the scanner can detect.

## 3) Installation

**Python:** 3.10+ is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

> `requirements.txt` includes runtime dependencies such as `tree-sitter` and `tree-sitter-languages`.

## 4) Usage

### Scan a local repo

```bash
python -m cbom_scanner scan /path/to/repo --out cbom.json --format cbom
```

### Output formats

- `--format cbom` for native CBOM JSON
- `--format cyclonedx` for CycloneDX 1.5 JSON (default)

```bash
python -m cbom_scanner scan /path/to/repo --format cyclonedx --out cyclonedx.json
```

### Include TypeScript

The Node scanner can optionally include TypeScript files:

```bash
python -m cbom_scanner scan /path/to/repo --include-ts --format cbom --out -
```

(`--out -` prints JSON to stdout.)

## 5) Output schema overview

### CBOM JSON (native)

Top-level fields:

- `cbomVersion`: CBOM schema version.
- `generatedAt`: UTC timestamp of generation.
- `component`: repository name (component being scanned).
- `tool`: scanner name and version.
- `cryptoAssets`: list of crypto findings.

Each `cryptoAssets` entry includes:

- `id`: stable hash of evidence + API metadata.
- `assetType`: e.g., `SYMMETRIC`, `HASH`, `UNKNOWN`.
- `algorithm`: normalized algorithm (e.g., `AES`, `SHA-256`, `UNKNOWN`).
- `mode`: cipher mode if known (e.g., `GCM`, `UNKNOWN`).
- `keySizeBits`: normalized key size if known (e.g., `256`, `UNKNOWN`).
- `library`: library/namespace (e.g., `node:crypto`, `openssl`).
- `api`: fully-qualified API name.
- `confidence`: detection confidence (`HIGH`, `MED`, `LOW`).
- `evidence`: file, line, column, function context, and code snippet.
- `notes`: optional notes (e.g., `heuristic` when regex fallback is used).

Example (abbreviated):

```json
{
  "cbomVersion": "1.0",
  "component": "my-repo",
  "cryptoAssets": [
    {
      "id": "<sha256>",
      "assetType": "SYMMETRIC",
      "algorithm": "AES",
      "mode": "GCM",
      "keySizeBits": "256",
      "library": "openssl",
      "api": "EVP_aes_256_gcm",
      "confidence": "HIGH",
      "evidence": { "file": "src/crypto.c", "line": 42, "column": 5 }
    }
  ]
}
```

### CycloneDX 1.5 JSON

Top-level fields:

- `bomFormat`: `CycloneDX`.
- `specVersion`: `1.5`.
- `metadata`: includes tool info and top-level component.
- `components`: list of crypto findings mapped as components with `properties`.

Example (abbreviated):

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "metadata": { "component": { "name": "my-repo" } },
  "components": [
    {
      "name": "AES-GCM",
      "properties": [
        { "name": "cbom:algorithm", "value": "AES" },
        { "name": "cbom:mode", "value": "GCM" }
      ]
    }
  ]
}
```

## 6) How detection works (rules + parsers)

1. **Rule-driven matching:** Each language has a ruleset in `cbom_scanner/rules/*.yaml`. Rules define imports and target calls, plus optional argument indices for algorithm/mode/key size.
2. **AST parsing (tree-sitter):** The scanner uses tree-sitter to locate call sites and extract arguments.
3. **Regex fallback:** If tree-sitter cannot parse a file, a regex-based scan attempts to match calls and literal arguments.
4. **Normalization:** Findings are normalized (e.g., `aes-256-gcm` → `AES`, `GCM`, `256`) and unknowns default to `UNKNOWN`.

### Adding new rules

1. Add or update a rules file in `cbom_scanner/rules/<language>.yaml` with:
   - `imports`: module/package hints.
   - `calls`: call name, API, library, and optional `arg_indexes` for `algorithm`, `mode`, `key_size_bits`.
2. Ensure the scanner for that language exists in `cbom_scanner/scanners/`.
3. Add/extend tests in `tests/fixtures` and `tests/test_scanner.py`.

## 7) Limitations

- **UNKNOWN fields:** If algorithm/mode/key size cannot be inferred, they are set to `UNKNOWN`.
- **Literal-only extraction:** Argument parsing relies on literal values or simple rule-provided values (dynamic values may be missed).
- **Config-driven coverage:** Only APIs present in rule files are detected.
- **Fallback heuristics:** Regex fallback may produce less precise results (noted as `heuristic`).

## 8) Security & privacy guarantees

- **No outbound calls:** The scanner performs local parsing only and does not contact external services.
- **No source modification:** Files are read-only; no changes are written to scanned repositories.

## 9) Development

### Run tests

```bash
pytest
```

### Lint / format

No linting or formatting tools are currently configured in this repository.

## 10) License and contribution notes

No `LICENSE` file is present in this repository. If you intend to open source or redistribute, please add an explicit license.

Contributions are welcome—please open an issue or pull request with a clear description of changes.
