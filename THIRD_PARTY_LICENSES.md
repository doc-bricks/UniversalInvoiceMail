# Third-Party Licenses & Level 1 SBOM

**Project:** UniversalInvoiceMail (`doc-bricks/UniversalInvoiceMail`)<br>
**Canonical Project License:** MIT License (`MIT`)<br>
**Audit Date:** 2026-09-23<br>
**Auditor:** Antigravity / Gemini (via GithubBot Pfad A)<br>
**Version:** `2.3.0`<br>
**Umbrella Ecosystem:** `open-bricks` / `doc-bricks`<br>
**Notice Attribution:** See canonical root [`NOTICE`](NOTICE) file.

---

## 1. Overview & Compliance Architecture

UniversalInvoiceMail is an open-source, local-first Windows desktop application for collecting invoices and receipts from email accounts (IMAP / Gmail), converting attachments into PDF format, keeping a secure local archive, and exporting DATEV-compatible booking batches (`EXTF_*.csv`). The application is licensed under the permissive **MIT License**. All direct runtime libraries, transitive packages, and development toolchains have been cataloged and audited for license compatibility, non-infringement, security vulnerability floors, and strict local execution guarantees. Canonical attribution is declared in the root [`NOTICE`](NOTICE) file.

This inventory is derived directly from `pyproject.toml`, `requirements.txt`, and runtime dependency inspection.

### 10 Governance- & Runtime-Invarianten

| Invariant Code | Category | Name & Guarantee | Verification Boundary |
|---|---|---|---|
| `INV-LOCAL-01` | Architecture | **100% Local-First Execution** | All mailbox processing, PDF conversion, OCR indexing, and private archive files remain strictly on the local machine; zero external telemetry or cloud analytics. |
| `INV-CRED-02` | Security | **Encrypted Credential Isolation** | Account passwords and authentication tokens are secured via `keyring` in the Windows Credential Manager (DPAPI) or ephemeral memory; never committed or saved in plaintext config files. |
| `INV-PRIVACY-03` | Privacy | **Redacted Bundle Export Boundary** | Exported invoice review bundles (`universalinvoicemail-invoicebundle-v1.json`) redact mail bodies and binary attachments by default, preserving document privacy during PWA review. |
| `INV-DATEV-04` | Compliance | **Strict DATEV Validation Pre-Save** | DATEV settings dialog enforces syntactical account number validation (4–8 digits), case-insensitive keyword uniqueness, and trimmed whitespace before persisting configuration. |
| `INV-FLOOR-05` | Security | **Hardened Vulnerability Floors** | Dependencies enforce patched security baselines, specifically `Pillow>=12.3.0` (resolving 26+ CVEs/GHSAs including GHSA-4x4j-2g7c-83w6), `keyring>=25.0.0`, and `pytest>=9.1.1` (mitigating CVE-2025-7117). |
| `INV-TLS-06` | Network | **Enforced TLS Transport Security** | Mail retrieval strictly requires TLS transport (`IMAP4_SSL` on port 993, HTTPS for OAuth2/Google endpoints); unencrypted plaintext transmissions are rejected. |
| `INV-LEASTPRIV-07` | Permission | **Least-Privilege API Scopes** | Google OAuth2 integration requests only minimal read/metadata scopes required for invoice search and fetch; administrative or whole-account mutations are barred. |
| `INV-LAZYLOAD-08` | Runtime | **Lazy Optional Dependency Boundary** | Google client libraries (`google-api-python-client`, `google-auth-oauthlib`) are loaded lazily on demand; standard IMAP users operate with zero Google library overhead. |
| `INV-OFFLINE-09` | Usability | **Zero-Network Conversion Fallbacks** | Attachment processing (PDF rendering, image stitching, DOCX/XLSX conversion, OCR) functions entirely offline without external SaaS API dependencies. |
| `INV-SLA-10` | Governance | **48h Security SLA & 5-Day Triage** | Documented response commitment in `SECURITY.md` establishing a 48-hour initial response window and 5-day triage SLA for all verified vulnerability reports. |

---

## 2. Direct Runtime Dependencies

| Package | Declared Constraint | SPDX License | Upstream Project / Repository | Compatibility Analysis |
|---|---|---|---|---|
| **PySide6** | `>=6.5.0` | `LGPL-3.0-only` | [The Qt Company](https://doc.qt.io/qtforpython-6/) | **Weak Copyleft / Permissive**: Dynamic linking under LGPLv3 is fully compatible with MIT-licensed host applications without viral license contagion. |
| **keyring** | `>=25.0.0` | `MIT` | [jaraco/keyring](https://github.com/jaraco/keyring) | **Permissive**: Fully compatible with MIT. Interfaces directly with Windows DPAPI Credential Vault. |
| **Pillow** | `>=12.3.0` | `HPND-sell-variant` | [python-pillow/Pillow](https://github.com/python-pillow/Pillow) | **Permissive**: Historical Permission Notice and Disclaimer. Hardened floor resolves multiple historical image processing CVEs. |
| **openpyxl** | `>=3.1.0` | `MIT` | [openpyxl](https://foss.heptapod.net/openpyxl/openpyxl) | **Permissive**: Fully compatible with MIT. Used for Excel invoice and attachment parsing. |
| **python-docx** | `>=1.1.0` | `MIT` | [python-docx](https://github.com/python-docx/python-docx) | **Permissive**: Fully compatible with MIT. Used for DOCX attachment extraction. |
| **xhtml2pdf** | `>=0.2.17` | `Apache-2.0` | [xhtml2pdf](https://github.com/xhtml2pdf/xhtml2pdf) | **Permissive**: HTML-to-PDF rendering engine compatible with MIT host projects. |
| **reportlab** | `>=4.2.0` | `BSD-3-Clause` | [ReportLab](https://www.reportlab.com/) | **Permissive**: Standard BSD license, fully compatible with MIT applications. |
| **pypdfium2** | `>=4.26.0` | `Apache-2.0 AND BSD-3-Clause` | [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) | **Permissive**: PDFium bindings licensed under Apache-2.0 and BSD-3-Clause; no copyleft contagion. |
| **pypdf** | `>=5.0.0` | `BSD-3-Clause` | [py-pdf/pypdf](https://github.com/py-pdf/pypdf) | **Permissive**: Pure Python PDF extraction and manipulation library under BSD-3-Clause. |
| **docx2pdf** | `>=0.1.8` | `MIT` | [AlJohri/docx2pdf](https://github.com/AlJohri/docx2pdf) | **Permissive**: Windows COM automation wrapper for Word-to-PDF conversion under MIT. |
| **pytesseract** | `>=0.3.13` | `Apache-2.0` | [madmaze/pytesseract](https://github.com/madmaze/pytesseract) | **Permissive**: Python wrapper for Tesseract-OCR CLI under Apache-2.0. |

---

## 3. Transitive Runtime Dependencies

| Package | SPDX License | Parent Dependency | Purpose |
|---|---|---|---|
| **shiboken6** | `LGPL-3.0-only` | PySide6 | C++/Python binding generator runtime |
| **pywin32-ctypes** | `BSD-3-Clause` | keyring | Pure-ctypes Windows Credential Vault interaction |
| **jaraco.classes** | `MIT` | keyring | Class utilities |
| **jaraco.context** | `MIT` | keyring | Context manager helpers |
| **jaraco.functools** | `MIT` | keyring | Function decoration and memoization |

---

## 4. Optional Dependencies (Gmail API & OAuth2)

| Package | Declared Constraint | SPDX License | Purpose | Compatibility |
|---|---|---|---|---|
| **google-api-python-client** | `>=2.100.0` | `Apache-2.0` | Gmail API client | Permissive, loaded dynamically on demand |
| **google-auth-oauthlib** | `>=1.1.0` | `Apache-2.0` | OAuth2 browser flow | Permissive, isolated to Google accounts |
| **google-auth** | `>=2.23.0` | `Apache-2.0` | Core Google token manager | Permissive, token storage in keyring |

---

## 5. Development & Test Toolchain

| Package | Declared Constraint | SPDX License | Purpose |
|---|---|---|---|
| **pytest** | `>=9.1.1` | `MIT` | Test runner and assertions (hardened against CVE-2025-7117) |
| **pluggy** | `>=1.6.0` | `MIT` | Pytest plugin framework |
| **iniconfig** | `>=2.0.0` | `MIT` | INI configuration parser |
| **packaging** | `>=24.0` | `Apache-2.0 OR BSD-2-Clause` | Version comparison and PEP compliance |
| **ruff** | `>=0.9.0` | `MIT OR Apache-2.0` | Fast Python linter and formatter |

---

## 6. License Compatibility & Security Summary

1. **Zero Strong Copyleft**: The application contains no GPL, AGPL, or SSPL licensed libraries. All runtime components are licensed under permissive (MIT, BSD-3-Clause, Apache-2.0, HPND-sell-variant) or weak-copyleft (LGPL-3.0-only) terms.
2. **LGPLv3 Compliance**: `PySide6` and `shiboken6` are dynamically loaded via standard Python imports (`import PySide6`). No static compilation or binary modification of Qt binaries occurs. Users are free to swap or upgrade Qt libraries in their Python environment.
3. **Execution Elevation**: The application requires standard user permissions (`asInvoker`). It does not request or require Windows Administrator / UAC privilege elevation.
4. **Vulnerability Mitigation**: Dependency floors are verified via automated CI and local unit tests (`tests/test_security_license_contract.py`).
