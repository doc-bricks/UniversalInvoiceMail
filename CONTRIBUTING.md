# Beitragsrichtlinie / Contributing Guide

## Deutsch

Vielen Dank für Ihr Interesse, zu **UniversalInvoiceMail** beizutragen.

### Wie Sie beitragen können

1. **Bugs melden:** Erstellen Sie ein GitHub Issue mit detaillierten Reproduktionsschritten, erwartetem vs. tatsächlichem Verhalten und Betriebssystemversion.
2. **Features vorschlagen:** Diskutieren Sie Erweiterungen über GitHub Issues, insbesondere unter Berücksichtigung des 100% Local-First Prinzips.
3. **Code & Doku beitragen:** Reichen Sie zielgerichtete, getestete Pull Requests ein.

Bitte veröffentlichen Sie niemals echte Rechnungsdaten, Zugangsdaten (IMAP-Passwörter, Gmail-Tokens) oder private Dokumente in öffentlichen Issues oder PRs. Für Sicherheitsmeldungen gilt strikt `SECURITY.md`.

### Pull Requests & Entwicklungsworkflow

1. Forken Sie das Repository auf GitHub.
2. Erstellen Sie einen fokussierten Feature-Branch: `git checkout -b feature/mein-feature`.
3. Entwickeln und testen Sie Ihre Änderung lokal gemäß den Qualitäts-Gates.
4. Committen Sie Ihre Änderungen mit präziser, semantischer Commit-Nachricht.
5. Pushen Sie den Branch zu Ihrem Fork und öffnen Sie einen Pull Request.

### Qualitäts-Gates & Automatisierte Tests

Vor jedem Pull Request oder Commit müssen alle lokalen Qualitätsprüfungen fehlerfrei bestehen:

```bash
# 1. Vollständige Python-Testsuite ausführen (inklusive Metadaten- und Vertragstests)
pytest -ra -v

# 2. Linter & statische Codeanalyse
ruff check .

# 3. Vollständige Bytecode-Kompilierung
python -m compileall -q .

# 4. Mobile Web-Companion-Testsuite
node --test web_companion/tests/library.test.mjs web_companion/tests/mobile_pwa_smoke.test.mjs
```

### Architektonische Invarianten & Governance

Beiträge müssen alle 10 Kern-Invarianten des Projekts einhalten:
- `INV-LOCAL-01` (100% Local-First Execution): Gesamte Postfachverarbeitung, PDF-Konvertierung, OCR-Indexierung und Archivierung verbleiben strikt auf dem lokalen System; null externe Telemetrie oder Cloud-Tracking.
- `INV-CRED-02` (Encrypted Credential Isolation): Passwörter und OAuth-Tokens werden über `keyring` in der Windows-Anmeldeinformationsverwaltung (DPAPI) isoliert; niemals im Klartext gespeichert.
- `INV-PRIVACY-03` (Redacted Bundle Export Boundary): Exportierte Prüfbundles (`universalinvoicemail-invoicebundle-v1.json`) schwärzen Mail-Inhalte und Rohanhänge standardmäßig zum Schutz der Privatsphäre.
- `INV-DATEV-04` (Strict DATEV Validation Pre-Save): DATEV-Einstellungen erzwingen syntaktische Sachkontenvalidierung (4–8 Ziffern), Case-Insensitive Eindeutigkeit und getrimmte Leerzeichen vor der Speicherung.
- `INV-FLOOR-05` (Hardened Vulnerability Floors): Abhängigkeiten erzwingen gehärtete Sicherheitsuntergrenzen (`Pillow>=12.3.0`, `keyring>=25.0.0`, `pytest>=9.1.1`).
- `INV-TLS-06` (Enforced TLS Transport Security): E-Mail-Abruf verlangt zwingend TLS-Verschlüsselung (`IMAP4_SSL` auf Port 993, HTTPS für OAuth2); unverschlüsselte Klartextübertragung ist unzulässig.
- `INV-LEASTPRIV-07` (Least-Privilege API Scopes): Google OAuth2 fordert nur minimale Lese-/Metadatenberechtigungen für die Rechnungssuche an; weitreichende Kontoberechtigungen sind ausgeschlossen.
- `INV-LAZYLOAD-08` (Lazy Optional Dependency Boundary): Google-Client-Bibliotheken werden ausschließlich bei Bedarf geladen; reine IMAP-Nutzer benötigen keine Google-Pakete.
- `INV-OFFLINE-09` (Zero-Network Conversion Fallbacks): Anhangverarbeitung (PDF-Rendering, Bildzusammenführung, DOCX/XLSX-Konvertierung, OCR) funktioniert vollständig offline ohne Cloud-APIs.
- `INV-SLA-10` (48h Security SLA & 5-Day Triage): Verbindliche Sicherheitsreaktionszeit von 48 Stunden und 5 Werktagen Triage gemäß `SECURITY.md`.

### Unprivilegierter Modus (`RunAsInvoker`)

Die Anwendung erfordert und beansprucht ausschließlich Standard-Benutzerrechte (`asInvoker` / Non-Elevation). Es werden zu keinem Zeitpunkt administrative Windows-UAC-Rechte verlangt.

### Plan D Lokales Setup & Versions-Disziplin

- **Kanonischer Arbeitsort:** Lokaler Git-Klon unter `C:\_Local_DEV\repos\UniversalInvoiceMail`.
- **OneDrive-Spiegel:** `C:\Users\lukas\OneDrive\.TOPICS\.SOFTWARE\MAIL\REL-PUB_UniversalInvoiceMail` dient als gitloser Multi-Device-Spiegel.
- **Versions-Freeze (T-20260920-167562623):** Die Version `2.3.0` bleibt für laufende Hygiene- und Wartungsläufe strikt eingefroren. Alle Änderungen werden unter `## [Unreleased]` im `CHANGELOG.md` dokumentiert.

### Haftungsausschluss & Rechtlicher Rahmen

Gemäß § 521 BGB (Gefälligkeitsrecht) erfolgt die Bereitstellung dieser Open-Source-Software unentgeltlich und ohne Gewährleistung für Sach- und Rechtsmängel, soweit gesetzlich zulässig.

---

## English

Thank you for your interest in contributing to **UniversalInvoiceMail**.

### How to Contribute

1. **Report bugs:** Open a GitHub issue with clear reproduction steps, expected vs. actual behavior, and Windows OS version.
2. **Suggest features:** Discuss enhancements via GitHub issues, keeping the 100% Local-First architecture in focus.
3. **Contribute code & docs:** Submit focused, well-tested pull requests.

Never post real invoice documents, credentials (IMAP passwords, Gmail tokens), or private client data in public issues or PRs. For security vulnerabilities, follow `SECURITY.md`.

### Pull Requests & Development Workflow

1. Fork the repository on GitHub.
2. Create a focused feature branch: `git checkout -b feature/my-feature`.
3. Develop and verify changes locally against all quality gates.
4. Commit your changes with a precise, semantic commit message.
5. Push the branch to your fork and submit a pull request.

### Quality Gates & Automated Tests

All local quality gates must pass cleanly prior to submitting a pull request:

```bash
# 1. Run complete Python test suite (including metadata and contract tests)
pytest -ra -v

# 2. Linter & static code analysis
ruff check .

# 3. Full bytecode compilation check
python -m compileall -q .

# 4. Mobile Web Companion test suite
node --test web_companion/tests/library.test.mjs web_companion/tests/mobile_pwa_smoke.test.mjs
```

### Architectural Invariants & Governance

All contributions must respect the 10 core system invariants:
- `INV-LOCAL-01` (100% Local-First Execution): Mailbox fetching, PDF conversion, OCR indexing, and private archive remain entirely local; zero external telemetry or cloud tracking.
- `INV-CRED-02` (Encrypted Credential Isolation): Passwords and OAuth tokens are secured via `keyring` in Windows Credential Manager (DPAPI); never saved in plaintext.
- `INV-PRIVACY-03` (Redacted Bundle Export Boundary): Exported invoice review bundles (`universalinvoicemail-invoicebundle-v1.json`) redact mail bodies and attachments by default.
- `INV-DATEV-04` (Strict DATEV Validation Pre-Save): DATEV dialog validates account numbers (4–8 digits), case-insensitive uniqueness, and trimmed whitespace before saving.
- `INV-FLOOR-05` (Hardened Vulnerability Floors): Dependencies enforce patched security baselines (`Pillow>=12.3.0`, `keyring>=25.0.0`, `pytest>=9.1.1`).
- `INV-TLS-06` (Enforced TLS Transport Security): Mail retrieval strictly requires TLS encryption (`IMAP4_SSL` on port 993, HTTPS for OAuth2); plaintext transmissions are disallowed.
- `INV-LEASTPRIV-07` (Least-Privilege API Scopes): Google OAuth2 requests only minimal read/search scopes; whole-account mutation is barred.
- `INV-LAZYLOAD-08` (Lazy Optional Dependency Boundary): Google client libraries are loaded lazily; standard IMAP users have zero Google dependency overhead.
- `INV-OFFLINE-09` (Zero-Network Conversion Fallbacks): Document conversion (PDF rendering, image stitching, DOCX/XLSX, OCR) operates fully offline without cloud APIs.
- `INV-SLA-10` (48h Security SLA & 5-Day Triage): Binding 48-hour response and 5-day triage SLA per `SECURITY.md`.

### Unprivileged Mode (`RunAsInvoker`)

The application requires and operates under standard user permissions (`asInvoker` / Non-Elevation). Administrative Windows UAC elevation is never required.

### Plan D Local Setup & Version Freeze

- **Canonical Repository:** Local Git clone at `C:\_Local_DEV\repos\UniversalInvoiceMail`.
- **OneDrive Mirror:** `C:\Users\lukas\OneDrive\.TOPICS\.SOFTWARE\MAIL\REL-PUB_UniversalInvoiceMail` acts as a gitless multi-device mirror.
- **Version Freeze (T-20260920-167562623):** Version `2.3.0` remains strictly frozen during routine hygiene maintenance. All updates are logged under `## [Unreleased]` in `CHANGELOG.md`.

### Legal Disclaimer & Statutory Notice

Per § 521 BGB (German Civil Code gratuitous service rules), this open-source software is provided free of charge without warranties for defects or non-conformity, to the maximum extent permitted by law.
