# Coverage gap analysis (current repo)

## Current scanner architecture

* **Languages supported:** Node.js (JS/TS), Go, C (OpenSSL), Python, Java, Rust, C#.
* **Detection approach:** Rules-driven detection via `cbom_scanner/rules/*.yaml`, tree-sitter AST extraction with regex fallback.
* **Output formats:** Native CBOM JSON and CycloneDX 1.5 JSON.
* **UNKNOWN behavior:** Algorithm/mode/key size fall back to `UNKNOWN` when arguments are not literal or rule-defined.
* **Failure modes:**
  * Regex fallback loses function context and can over-match.
  * No constant propagation; identifiers are treated as unknown.
  * Limited rule coverage per language produces undercounted assets.

## Coverage matrix (current)

Legend: ✅ covered, ⚠️ partial, ❌ missing

| Language | Algorithm | Mode | Keysize | KDF | Signature | TLS | RNG | Keygen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Node.js | ⚠️ (hash/cipher literals) | ⚠️ (AES only) | ⚠️ (AES strings only) | ❌ | ❌ | ❌ | ❌ | ❌ |
| Go | ⚠️ (AES) | ⚠️ (GCM only) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| C/OpenSSL | ⚠️ (AES-256-GCM, SHA-256) | ⚠️ (GCM only) | ⚠️ (AES-256 only) | ❌ | ❌ | ❌ | ❌ | ❌ |
| Python | ⚠️ (placeholder) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Java | ⚠️ (placeholder) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Rust | ⚠️ (placeholder) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| C# | ⚠️ (placeholder) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

## Top missing crypto APIs per language

### Node.js / TypeScript
* KDFs: `crypto.pbkdf2`, `crypto.scrypt`, `crypto.hkdf`
* Key management: `crypto.createPublicKey`, `createPrivateKey`, `createSecretKey`
* Key exchange: `crypto.diffieHellman`, `createDiffieHellman`, `createECDH`
* Sign/verify: `crypto.sign`, `crypto.verify`
* WebCrypto: `crypto.webcrypto.subtle.*`

### Go
* `golang.org/x/crypto` packages: `pbkdf2`, `scrypt`, `hkdf`, `chacha20poly1305`, `ssh`
* TLS usage: `crypto/tls` (Listen/Dial/LoadX509KeyPair)
* Cipher modes: `cipher.NewCBCEncrypter`, `cipher.NewCTR`
* Key generation APIs: `rsa.GenerateKey`, `ecdsa.GenerateKey`, `ed25519.GenerateKey`

### C/OpenSSL
* EVP lookups: `EVP_get_cipherbyname`, `EVP_CIPHER_fetch`
* Init wrappers: `EVP_EncryptInit_ex` / `EVP_DecryptInit_ex`
* Keygen: `RSA_generate_key_ex`, `EC_KEY_new_by_curve_name`

## False positive risks + mitigation

* **Rule over-matching:** Avoid matching substring calls that are not crypto-related; prefer `endswith` or fully-qualified call names.
* **Config-driven strings:** Only treat literal algorithm strings or safe constant-propagated values as evidence.
* **OpenSSL heuristics:** For C, avoid guessing algorithm unless it matches a well-known literal (e.g., exact EVP cipher name or literal cipher string).
