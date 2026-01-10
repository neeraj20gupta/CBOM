# CBOMKit upstream study (cbomkit/cbomkit)

## 1) What CBOMKit detects well

* **CycloneDX-centric asset model:** CBOMKit models crypto findings as CycloneDX `Component` data attached to a `CryptographicAsset` record, which makes it easy to flow data into compliance checks and the viewer UI. This is visible in `CryptographicAsset` using CycloneDX types and the API/DB layers that treat assets as components.
* **UI-centric crypto vocabulary:** The frontend ships a crypto dictionary that labels crypto assets by category (algorithm, protocol, certificate, MAC, block cipher, etc.), indicating the viewer experience is organized around normalized asset types and a shared taxonomy.
* **Scanning workflow orchestration:** The backend is structured around scan commands, scan aggregates, and scan metadata (e.g., `ScanAggregate`, `ScanRequest`, `ScanMetadata`) to manage request lifecycle, repository cloning, and scan results.

## 2) Where coverage gaps exist

* **Language breadth:** The public CBOMKit service repository only exposes `JAVA` and `PYTHON` in its language enum, implying upstream scanning focuses on those ecosystems rather than a broader multi-language rule set.
* **Crypto API surface:** The CBOMKit repo itself does not embed detailed per-language crypto rules; it relies on external scanning components (e.g., `cbomkit-hyperion`, `cbomkit-theia`) for detailed detection. That can leave gaps where rule coverage or AST extraction misses config-driven crypto (Node, OpenSSL variants, Go x/crypto, Java JCE).
* **Evidence granularity:** The model centers on CycloneDX components; there is no obvious file/line/function evidence modeling surfaced in the Java domain objects, so evidence quality depends on upstream scanner behavior rather than a strict schema in this repo.

## 3) Design patterns to reuse

* **Vocabulary normalization:** Reuse CBOMKit’s dictionary-driven approach by mapping raw API findings into normalized asset categories and algorithm names.
* **Component modeling:** Align our CBOM JSON output with CycloneDX component metadata to remain compatible with external tooling and UI expectations.
* **Scan lifecycle separation:** Keep scanning, normalization, and formatting as distinct layers (which matches CBOMKit’s separation between scan orchestration, compliance, and presentation).

## 4) Recommendations mapped to this repo

* **Normalization upgrades (cbom_scanner/core/normalizer.py):** Extend canonicalization to match CBOMKit’s emphasis on taxonomy consistency.
* **Evidence quality (cbom_scanner/core/utils.py + language scanners):** Preserve file/line/function/snippet attributes to cover the evidence gap hinted by upstream’s abstracted asset model.
* **Dashboard alignment (new UI):** Mirror the crypto dictionary approach in legends and primitives breakdown to remain compatible with CBOMKit’s viewer semantics.
