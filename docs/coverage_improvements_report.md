# Coverage improvements report

## Summary of changes

* Expanded Node.js/TypeScript detection for KDFs, key management, key exchange, signatures, and WebCrypto subtle APIs.
* Added Go support for `x/crypto` primitives, TLS usage, additional cipher modes, and key-generation APIs.
* Expanded OpenSSL coverage to include EVP cipher lookup/initialization and RSA/EC key generation.
* Improved normalization for algorithm/mode canonicalization, curve-derived key sizes, and stable asset fingerprints.
* Added a new crypto-zoo corpus under `testdata/crypto_zoo/{node,go,c}` with unit tests validating coverage and evidence quality.

## Before / after coverage numbers (counts from tests)

| Dataset | Findings count |
| --- | --- |
| Baseline fixtures (`tests/fixtures/crypto_zoo`) | 7 |
| New crypto-zoo corpus (Node) | 22 |
| New crypto-zoo corpus (Go) | 17 |
| New crypto-zoo corpus (C/OpenSSL) | 8 |
| **Total new corpus** | **47** |

## New rules / APIs added

### Node.js / TypeScript
* `crypto.pbkdf2`, `crypto.pbkdf2Sync`
* `crypto.scrypt`, `crypto.scryptSync`
* `crypto.hkdf`
* `crypto.createPublicKey`, `crypto.createPrivateKey`, `crypto.createSecretKey`
* `crypto.generateKey`
* `crypto.diffieHellman`, `crypto.createDiffieHellman`, `crypto.createECDH`
* `crypto.sign`, `crypto.verify`
* `crypto.webcrypto.subtle.digest`, `subtle.sign`, `subtle.verify`

### Go
* `golang.org/x/crypto/{pbkdf2,scrypt,hkdf,chacha20poly1305,ssh}`
* `crypto/tls.{Dial,Listen,LoadX509KeyPair}`
* `crypto/cipher.{NewCBCEncrypter,NewCBCDecrypter,NewCTR}`
* `crypto/{rsa,ecdsa,ed25519}.GenerateKey`

### C / OpenSSL
* `EVP_get_cipherbyname`, `EVP_CIPHER_fetch`
* `EVP_EncryptInit_ex`, `EVP_DecryptInit_ex`
* `RSA_generate_key_ex`, `EC_KEY_new_by_curve_name`

## Remaining gaps + next roadmap items

1. **Config-driven detection** for Node and Go (e.g., algorithm strings built from non-constant expressions).
2. **Java and Python AST upgrades** to cover broader JCE / cryptography usage (currently minimal rulesets).
3. **More OpenSSL primitives** including `EVP_get_digestbyname`, `EVP_PKEY_*`, and `EVP_MAC` families.
4. **Function classification** (encrypt/decrypt/sign/verify/etc.) as structured fields rather than inferred for the UI.
5. **RNG detection** across languages (e.g., `crypto/rand`, `RAND_bytes`, `crypto.randomBytes`).
