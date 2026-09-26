# Changelog - UniversalInvoiceMail

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

## [2.4.1] - 2026-07-27 - Technical Hygiene & Maintenance

### Changed
- `llms.txt`: Header auf `Last-checked: 2026-07-27` und 125 verifizierte Tests (115 Pytest + 10 Node Web Companion PWA) aktualisiert.
- Technischen Hygiene- & Maintenance-Check (Pfad A) in den internen Wartungsprotokollen registriert.
- Test-Verifikation: 115/115 Pytest-Tests 100% grün (0 Fehler, 24.08s execution time), `py_compile` fehlerfrei.

## [2.4.0] - 2026-07-26

### Added
- Standardisierte `pyproject.toml` (PEP 621) mit Metadaten, Keywords, Klassifikatoren und `[tool.pytest.ini_options]` (`pythonpath = ["."]`).
- Shields.io-Badges für Pytest (110 passed), Web Companion (10 passed), Lizenz (MIT), Local-First-Datenschutz und LLM-Ready-Kontext.
- Mermaid-Systemarchitekturdiagramm & Datenfluss-Visualisierung in `README.md` und `README-DE.md`.
- GFM-KI-Agenten-Hinweis (`> [!NOTE]`) für LLM-Verarbeitbarkeit und sicheres Auffinden von `llms.txt`.
- Sprachwechsler-Leiste (`[English](README.md) | [Deutsch](README-DE.md)`).

### Changed
- `llms.txt` Header-Datum auf `Last-checked: 2026-07-26` aktualisiert und Verifikationsteststand auf 120 grüne Tests (110 Pytest + 10 Node Web Companion) angeglichen.

## [Unreleased]

### UX & Accessibility Review (WCAG 2.1 AA / BITV 2.0) (2026-09-26)
- **Tastaturbedienung & Barrierefreiheit (WCAG 2.1 AA / BITV 2.0)**:
  - `AccessibleInvoiceTable`: Tastaturbedienung für die Rechnungstabelle implementiert (`Eingabe`/`Return` öffnet die ausgewählte Rechnung, `Leertaste` schaltet die Checkbox für den Export/Löschvorgang um).
  - `AccessibleListWidget`: Tastaturnavigation für Suchprofile (`profile_list`) und E-Mail-Konten (`account_list`) implementiert (`Eingabe`/`Return` öffnet den Bearbeitungsdialog, `Entf`/`Backspace` löscht den ausgewählten Eintrag).
  - `AccessibleMappingTable`: Tastatursteuerung für das DATEV-Konten-Mapping implementiert (`Entf`/`Backspace` entfernt die ausgewählte Zeile, `Einfg` fügt eine neue Zeile hinzu).
  - `ShortcutsDialog` & `F1`-Hilfe: Zentraler barrierefreier Hilfedialog mit tabellarischer Übersicht aller 16 Tastaturkürzel (Tastenkombination, Aktion, Bereich), WCAG 2.1 AA / BITV 2.0 Hinweistext, Schließen-Button mit Initialfokus und barrierefreiem Offscreen-Test-Bypass.
  - `MainWindow`: Neuer Toolbar-Button `show_shortcuts_button` ("❓ Hilfe & Kürzel") und globaler Shortcut `F1` (`shortcut_help_f1`) registriert.
- **DATEVSettingsDialog A11y & Mnemonics**:
  - Tastatur-Mnemonics und Label-Buddies ergänzt: `&Beraternummer:` (`Alt+B`) und `&Mandantennummer:` (`Alt+M`) mit `setBuddy()` an Eingabefelder angebunden.
  - Button-Mnemonics und Tastaturkürzel: `&Zeile hinzufügen` (`Alt+Z`), `Zeile &entfernen` (`Alt+E`), `&Standard wiederherstellen` (`Alt+S`).
  - Standardisierte `objectName`-Vergabe für alle Bedienelemente (`datev_berater_input`, `datev_mandant_input`, `datev_mapping_table`, `datev_add_row_button`, `datev_remove_row_button`, `datev_reset_mapping_button`, `datev_dialog_ok_button`, `datev_dialog_cancel_button`).
  - Kontextbezogene Tooltips für alle Mapping-Tabellenzellen (Absender, Kreditorenkonto, Aufwandskonto).
- **Internationalisierung (Tier-2 6-Sprachen-Parität)**:
  - 8 neue Lokalisierungsschlüssel in `locales/translations.json` für alle 6 Sprachen (`de`, `en`, `es`, `zh`, `ja`, `ru`) mit echten Umlauten eingepflegt.
- **Automatisierte Testsuite**:
  - 6 neue Hermetische Tests in `tests/test_ui_accessibility.py` implementiert (ShortcutsDialog-Inhalt, MainWindow-F1 & Button, DATEVSettingsDialog-Buddies, AccessibleMappingTable-Tastaturnavigation, AccessibleInvoiceTable-Tastaturnavigation, AccessibleListWidget-Tastaturnavigation).
  - Gesamt-Testsuite: 218 passed in 14.3s (100% grün).

### Pfad B Marketing, Discoverability, Visual Architecture & Bilateral Navigation Parity (2026-09-24)
- **18-Point Bilateral Quick Navigation & Dual Reciprocal Anchors**:
  - Implemented 18-point bilateral quick navigation across both `README.md` and `README-DE.md` with reciprocal dual HTML anchors (`<a id="sec-01"></a>` through `<a id="sec-18"></a>`) and language-specific anchors for deep-linking.
  - Saturated Shields.io badges for attribution (NOTICE), verification date, test pass rates (100% green), Web Companion status, Local-First privacy, RunAsInvoker unprivileged execution, and 48h Security SLA.
- **20-Topic & Keywords Saturation (PEP 621 Parity)**:
  - Synchronized `pyproject.toml` keywords 20/20 with GitHub repository topics: `accounting`, `datev`, `document-archive`, `email`, `email-attachments`, `gmail`, `gmail-api`, `imap`, `invoice`, `invoice-automation`, `json-export`, `local-first`, `ocr`, `offline-first`, `pdf`, `privacy-first`, `pyside6`, `python`, `receipt`, `windows`.
- **Target Personas & 5-Way Comparative Matrix**:
  - Documented 4 core user personas (Freelancers/SMBs, Tax Advisors/Bookkeepers, Privacy Officers, Open-Source Developers) with dedicated high-intent search queries.
  - Published 5-way comparative matrix benchmarking UniversalInvoiceMail against Cloud Aggregators, Manual Saving, Thunderbird Add-ins, and Generic CLI Scripts across 10 invariant dimensions.
- **Governance, Level 1 SBOM & German Statutory Legal Notice**:
  - Re-audited Level 1 SBOM in `THIRD_PARTY_LICENSES.md` (Stand 2026-09-24) with complete Invariant Cross-Reference Matrix (`INV-LOCAL-01` through `INV-SLA-10`).
  - Added statutory liability limitation under German Civil Code (§ 521 BGB Gefälligkeitsrecht) and 48h Security Response SLA in Section 18 of both `README.md` and `README-DE.md`.
- **Automated Metadata Contract Test Suite**:
  - Extended `tests/test_metadata.py` with contract tests verifying 20-topic saturation, 18-point dual reciprocal anchors (`sec-01` to `sec-18`), Level 1 SBOM matrix, and § 521 BGB / SLA presence.
- **Strict Version Freeze**:
  - Version 2.3.0 preserved strictly intact per `T-20260920-167562623`.

### Technical Hygiene, CI Lifecycle Hardening & Level 1 SBOM Audit (2026-09-23)
- **CI Workflows Hardening**:
  - Added `.github/workflows/stale.yml` (actions/stale@v9, daily schedule 01:30 UTC, concurrency group with cancel-in-progress, least-privilege permissions `issues: write`, `pull-requests: write`, 10-minute timeout).
  - Added `.github/workflows/welcome.yml` (actions/first-interaction@v3, concurrency group with cancel-in-progress, least-privilege permissions `issues: write`, `pull-requests: write`, 5-minute timeout).
  - Hardened `.github/workflows/tests.yml` and `source-platform-smoke.yml` with concurrency groups (`cancel-in-progress: true`), explicit 15-minute job timeouts, and strict `contents: read` permissions.
- **Canonical Root NOTICE & Level 1 SBOM Audit**:
  - Created canonical root `NOTICE` file documenting copyright attribution, doc-bricks/open-bricks ecosystem affiliation, and permissive MIT licensing.
  - Authored comprehensive Level 1 SBOM in `THIRD_PARTY_LICENSES.md` documenting 10 system and governance invariants (`INV-LOCAL-01` through `INV-SLA-10`), direct runtime packages, transitive dependencies, build/test chains, and license compatibility analysis.
- **Repository Hygiene & Multi-Host Lock Defense**:
  - Hardened `.gitignore` with cloud-sync conflict tokens (`*conflicted copy*`, `* (Kopie)*`, `* (Copy)*`, `*-WORKSTATION*`, `*-ASUS*`, `*-LAPTOP*`, `*-Mac Studio*`, `*-MacBook*`), canonical lock patterns (`LOCK`, `LOCK.user.*`, `LOCK.until.*`, `LOCK.condition.*`, `LOCK.permissions.json`, `uv.lock`, `.automation-lock`), and cache/build directories (`.hypothesis/`, `.turbo/`, `.nyc_output/`).
- **Packaging & PEP 621 Metadata**:
  - Enhanced `pyproject.toml` with PEP 621 / PEP 639 standard metadata (`license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md", "THIRD_PARTY_LICENSES.txt"]`), extended URLs (`Marketing Log`, `LLM Ready`, `Notice`, `Third-Party Licenses`, `Parent Organization`, `Umbrella Ecosystem`), and hardened test configurations.
- **Documentation & LLM Context Parity**:
  - Refreshed `llms.txt` and `README.md` / `README-DE.md` badges to reflect 206 passing Pytest tests (+ 10 Node Web Companion tests).
  - Created root `MARKETING-LOG.txt` documenting Pfad A hygiene baseline, target personas, invariants, and ecosystem links.
- **Automated Contract Tests**:
  - Expanded `tests/test_metadata.py` and `tests/test_security_license_contract.py` with regression checks for `NOTICE`, `THIRD_PARTY_LICENSES.md`, `.github/workflows/stale.yml`, `.github/workflows/welcome.yml`, and hardened lock defense patterns (206 Pytest tests passing).

### Headless CSV Export & Dialog Decoupling (2026-09-22)
- **Modal Dialog Decoupling in `export_invoices_csv()`**: Decoupled GUI `QMessageBox` popups (both success and failure) from programmatic/headless invocations (`filepath is not None`) in `UniversalInvoiceMail.py`. Headless callers and test suites no longer block on modal message boxes.
- **Directory Auto-Creation**: Ensured `target_path.parent.mkdir(parents=True, exist_ok=True)` is called before writing CSV files, preventing `FileNotFoundError` when exporting to non-existent subdirectories.
- **Headless Contract & Regression Tests**: Added `test_export_invoices_csv_headless_no_modals_and_nested_dirs` and `test_export_invoices_csv_headless_error_handling_no_modals` in `tests/test_csv_export.py` ensuring zero modal popups occur during headless exports, and set `QT_QPA_PLATFORM=offscreen` at the module level.

### Accessibility: CSV export scope guidance (2026-09-20)
- The CSV export action now tells screen-reader and keyboard users that marked invoices are exported, while an empty selection exports the complete list; its tooltip also exposes the `Strg+E` shortcut.
- `tests/test_ui_accessibility.py` keeps this selection/fallback guidance under contract.

### CSV Export Enhancement & DATEV Amount Robustness [TW-UIM-07] (2026-09-20)
- **Selection-Aware & Enriched CSV Export (`UniversalInvoiceMail.py`)**:
  - Enhanced `export_invoices_csv()` to respect table selections (`_get_selected_invoice_paths()`) with graceful fallback to all invoices.
  - Added essential invoice metadata columns to CSV export: `Betrag`, `Währung`, `Status`, and `Notizen`.
  - Added headless/programmatic parameter `filepath` support for scripted and automated runs.
- **DATEV Amount & Date Robustness (`datev_exporter.py`)**:
  - Implemented `parse_datev_amount()` supporting floats, ints, Decimals, and strings with currency symbols/commas to prevent `TypeError` exceptions during validation and export.
  - Expanded date parsing formats (`%Y/%m/%d`, `%d.%m.%y`, `%d/%m/%y`, `%d-%m-%y`) in `parse_datev_datetime()`.
- **Code Hygiene & Accessibility Imports Cleanup (`tests/test_ui_accessibility.py`)**:
  - Removed 8 unused PySide6 widget imports (`QCheckBox`, `QComboBox`, `QDateEdit`, `QDialogButtonBox`, `QLineEdit`, `QListWidget`, `QRadioButton`, `QSpinBox`) to bring `ruff check .` to 100% clean (0 warnings).
- **Test Coverage Expansion**:
  - Added `tests/test_csv_export.py` covering programmatic export, table selection filtering, empty states, and dialog interactions.
  - Added `tests/test_datev_robustness.py` covering edge case amounts, extended date formats, and string amount DATEV export.
  - Test suite expanded to 201 Pytest tests (+ 10 Node Web Companion tests), all green.

### Security, Dependency Floor & Third-Party License Audit (2026-09-11)
- **Dependency Floors & CVE Mitigation**:
  - Hardened `Pillow>=12.3.0` in `requirements.txt` and `pyproject.toml` to protect against known CVEs/GHSAs (including `GHSA-4x4j-2g7c-83w6` and `GHSA-45hq-cxwh-f6vc`).
  - Enforced `keyring>=25.0.0` for OS-level secure credential handling.
  - Added dev dependencies with `pytest>=9.1.1` (mitigating CVE-2025-7117 / GHSA-6w46-j5rx-g56g) and `ruff>=0.9.0`.
  - Added complete PEP 621 dependencies section with minimum version floors in `pyproject.toml`.
- **Repository Hygiene & Multi-Host Hardening**:
  - Hardened `.gitignore` with multi-host sync conflict patterns (`*-WORKSTATION-LG*`, `*-ASUS-GEI*`, `*.sync-conflict-*`, `*.conflict`), `.ruff_cache/`, `*.pfx`, `secrets.*`, and lock patterns (`LOCK.*`, `*.lock`).
- **Security Policy (`SECURITY.md`)**:
  - Upgraded bilingual security policy with explicit contacts (`security@doc-bricks.org`, `security@open-bricks.org`, `support@lukasgeiger.com`), a binding 48-hour response SLA, and local-first zero-egress guarantees.
- **Third-Party Licenses Inventory (`THIRD_PARTY_LICENSES.txt`)**:
  - Structured all direct, transitive, test, and build dependencies with licenses, SPDX identifiers, upstream URLs, and notice blocks.
- **Security Contract Test Suite**:
  - Added automated contract tests (`tests/test_security_license_contract.py`) covering vulnerability floors, third-party licenses, `.gitignore` multi-host patterns, zero hardcoded user paths, bilingual security policy SLA, and offline local-first invariants.

### DATEV mapping contract and roadmap readback (2026-08-26)
- Prevented empty mapping keys, non-numeric account values, empty adviser/client
  numbers, and case-insensitive duplicate sender/keyword keys from being silently
  discarded or replaced before `DATEVSettingsDialog` validation.
- Kept the mapping table as a user-configured technical aid; professional account
  assignment remains with accounting or tax advisers, and the 93-column export
  contract is unchanged.
- Synchronized `ROADMAP.txt` with the verified v2.3.0/Companion baseline of
  154 Pytest and 10 Node tests and identified TASKPLAN as the canonical task status.

### UX: Accurate DATEV validation guidance (2026-08-25)
- Corrected the German and English user-facing DATEV documentation: the settings dialog
  validates its technical inputs before saving and reports errors; it does not silently fall
  back to default account values. The guide now distinguishes this check from an accountant's
  professional review of the account assignment.

### Bugfix & Hardening: DATEV CSV Quoting, Multi-Format Date Parsing & Dynamic Fiscal Year (2026-08-25)
- **DATEV EXTF CSV Escaping & Delimiter Injection Protection (`datev_exporter.py` / `DATEVBuchung`)**:
  - Replaced naive string concatenation with standard `csv.writer(..., delimiter=";", quoting=csv.QUOTE_MINIMAL)` in `DATEVExporter.export()`, preventing CSV column shifts and parser failures when invoice filenames (`belegfeld1`), provider names, or descriptions (`buchungstext`) contain semicolons `;` or quotation marks `"`.
  - Added whitespace and control character sanitation (stripping `\r`, `\n`, `\t` and boundary whitespace) in `DATEVBuchung.to_row()`.
  - Guaranteed invariant: Exported booking rows always parse to exactly 93 EXTF columns under RFC 4180 / DATEV CSV specifications.
- **Robust Multi-Format Date Parsing (`datev_exporter.py` / `parse_datev_datetime`)**:
  - Implemented unified `parse_datev_datetime()` supporting ISO dates, timestamps (`YYYY-MM-DDTHH:MM:SS`, `YYYY-MM-DD HH:MM:SS`), German dates (`DD.MM.YYYY`, `DD-MM-YYYY`), dotted dates (`YYYY.MM.DD`), and compact formats (`YYYYMMDD`).
  - Unified date parsing across `validate_invoices_for_export()` and `DATEVExporter` to prevent false invalid date fallback warnings.
  - Enabled dynamic `wj_beginn` fiscal year alignment in `DATEVExporter._build_header()` when exporting historical invoices across multiple tax years.
- **Provider Resolution Fallback (`UniversalInvoiceMail.py`)**:
  - Added fallback from `inv.profile_name` to `inv.sender` in `_export_datev()` to preserve provider-based SKR03/SKR04 account mapping when profile names are generic.
- **Test Coverage Expansion**:
  - Added comprehensive unit and regression tests in `tests/test_datev.py` and `tests/test_datev_validation.py` (3 new tests, 153/153 Pytest passed, 10/10 Node Web Companion passed, 100% green).

### UX & Accessibility: Manual Amount Validation (2026-08-23)
- Ungültige manuelle Betragseingaben werden nicht mehr stillschweigend verworfen: Die Tabelle stellt den zuletzt gespeicherten Betrag wieder her und erläutert den Fehler in einem zugänglichen Warnhinweis sowie im Aktivitätsprotokoll.
- Neuer Offscreen-Regressionstest stellt sicher, dass ungültige Eingaben keinen gespeicherten Betrag überschreiben.

### Bugfix & Hardening: Amount Normalization & Companion Exchange Bundle (2026-08-23)
- **Amount Normalization & Parsing Hardening (`invoice_bundle.py` / `UniversalInvoiceMail.py`)**:
  - Hardened `_normalize_amount()` against formatted European numbers with thousand-separators (`1.234,56`), US format (`1,234.56`), currency symbols (`€`, `$`, `£`, `¥`, `₹`), ISO currency codes (`EUR`, `USD`, `CHF`, `GBP`), whitespace-only strings, and negative credit amounts (`-15,50`).
  - Switched `build_invoice_bundle()` to use `_normalize_amount()` instead of raw `float(amount)` to prevent unhandled `ValueError` crashes during bundle export.
  - Added safe integer fallback parsing `_safe_int()` for Sachkontenlänge in DATEV bundle configurations.
  - Preserved fallback `profile_id` on invoices when profile collections do not contain matching profile name/id entries.
  - Added support for `collections.abc.MutableMapping` (e.g. `UserDict`) in `apply_invoice_bundle_changes()`.
  - Hardened GUI amount input handler `_on_invoice_amount_changed()` in `UniversalInvoiceMail.py` using `_normalize_amount()`.
  - Added comprehensive regression test suite in `tests/test_invoice_bundle.py` (3 new tests, 149/149 passed).

### DATEV Validation Hardening & Multi-Language I18N System (2026-08-21)
- **DATEV Account Validation & Mapping Hardening (TW-UIM-04 / TASKPLAN #1156)**:
  - Added `validate_account_number()` verifying numerical validity, positive values, and standard 4-to-8 digit ranges for SKR03/SKR04 accounts.
  - Added `validate_datev_config()` validating Beraternummer (1-7 digits), Mandantennummer (1-5 digits), Sachkontenlänge (4-8), and non-empty mappings.
  - Added `validate_invoices_for_export()` and `DATEVExporter.validate()` producing structured `DATEVValidationReport` batch diagnostics (valid counts, skipped zero-amount items, unparseable dates).
  - Enhanced `DATEVSettingsDialog` in `UniversalInvoiceMail.py` with pre-save input validation in `accept()`, providing clear user-facing guidance on configuration errors.
  - Added test suite `tests/test_datev_validation.py` with 10 contract and unit tests (100% green).
- **I18N / Multi-Language System (Policy P-006 / 6-Languages Support)**:
  - Implemented `translator.py` (`TranslationSystem`) supporting 6 standard languages (`de`, `en`, `es`, `zh`, `ja`, `ru`) with fallback chain (current -> en -> de -> key).
  - Created `locales/translations.json` with complete translations for core actions, statuses, table headers, DATEV dialogs, validation messages, and mail filters.
  - Added test suite `tests/test_i18n.py` with 16 tests verifying completeness, token consistency, formatting, and language switching across all 6 languages.
- **Metadata, Linting & Parity**:
  - Updated `tests/test_metadata.py` with `translator.py` and `locales/translations.json`.
  - Pytest test suite expanded to 146 tests (146 passed in 2.74s, 100% green).
  - Node Web Companion test suite maintained at 10 passed (156 total passed tests).
  - Clean `ruff check .` (0 errors) and `python -m compileall .` (0 errors).

### Maintainer verification, Hygiene & Discoverability (2026-08-16)
- **Ruff Linting**: Resolved all 34 pre-existing Ruff linting errors (`F401` unused imports, `E402` module-level imports, `F841` unused variables) across `test_helpers.py`, `tests/test_datev.py`, and `tests/test_integration.py`. Added `[tool.ruff]` and `[tool.ruff.lint]` configuration in `pyproject.toml`.
- **Automated Metadata Parity Tests**: Added `tests/test_metadata.py` verifying version parity, documentation file presence, `llms.txt` integrity, web companion PWA assets and UTF-8 encoding.
- **Discoverability & Badges**: Synchronized test badges to 120 Pytest passed (100% green) and 10 Node Web Companion passed across `README.md` and `README-DE.md`. Added doc-bricks and open-bricks ecosystem sibling tool grid.
- **Testsuite Status**: 120/120 Pytest tests passing, 10/10 Node Web Companion tests passing, source-platform smoke passing, `ruff check .` 100% clean.

### Repo hygiene (2026-08-15)
- Internal `TASKPLAN_STATUS_*.md` readbacks are now ignored and no longer intended for public Git tracking because they can contain local Plan-D evidence paths.

### TASKPLAN Steuerdokumente und DATEV-Readback (2026-08-12)
- ROADMAP, AUFGABEN, README/README-DE, User Guide und `llms.txt` gegen den v2.3.0-/Companion-Stand sowie den frischen Plan-D-Readback abgeglichen.
- `115/115` Pytest-Tests, Source-Platform-Smoke und `compileall` liefen grün. Die getrackte Node-Baseline bleibt `10/10`; eine fremde, uncommittete Manifest-Variante liefert `9/10` und wurde nicht übernommen.
- Die DATEV-Mapping-UI (Tabelle, Hinzufügen/Entfernen, Standard-Wiederherstellung, Laden/Speichern und Accessibility-Metadaten) ist dokumentiert. Kontenbereichs- und Duplikat-/Konfliktregeln bleiben bis zur Accounting-Entscheidung offen; der 93-Spalten-Exportvertrag wurde nicht verändert.
- Keine kanonische OneDrive-Projektion: aktiver Cloud-Lock und fremde Arbeitsbaumänderungen wurden nicht überschrieben.

### Maintainer verification (2026-08-10)
- Fresh local readback: 114/114 Pytest, source-platform smoke, `py_compile` and
  JavaScript syntax checks passed. Ruff reports 34 existing test/import findings.
- The Node Web Companion suite is 9/10 only because the pre-existing uncommitted
  `web_companion/manifest.webmanifest` change points to lowercase/root-relative
  icons while the tracked assets use `./icons/Icon-*.png`. The foreign manifest
  change was preserved and not staged or committed; the public 10/10 baseline was
  not rewritten from this dirty working tree.

### Maintainer verification & Discoverability (2026-08-04)
- Discoverability, README-Design & SEO Check (Pfad B) für `doc-bricks/UniversalInvoiceMail` durchgeführt.
- Shields.io-Badges für doc-bricks Organisation, open-bricks Ökosystem, Pytest (114 passed), Web Companion (10 passed), Python 3.10+ und MIT-Lizenz in `README.md` & `README-DE.md` integriert.
- Interaktive Mermaid-Systemarchitekturdiagramme für Datenfluss (IMAP/Gmail API -> Conversion/OCR -> Archive/DATEV/Web Companion) in deutscher und englischer Dokumentation hinterlegt.
- GFM-KI-Agenten-Callout-Box (`> [!NOTE]`) für `llms.txt` Discovery Index eingebunden; `llms.txt` Timestamp auf `2026-08-04` und 124 passed Tests (114 Pytest + 10 Node Web Companion) aktualisiert.
- PWA-Manifest `manifest.webmanifest` Icon-Pfade für case-sensitive und offline PWA Installationen gehärtet (`./icons/Icon-192.png`, etc.); Node test suite (10/10 passed) und Pytest test suite (114/114 passed) 100% grün.

### Maintainer verification (2026-08-01)
- 114/114 Pytest-Tests, 10/10 Node-Web-Companion-PWA-Tests, `py_compile` und der
  Source-Platform-Smoke erfolgreich verifiziert. Der Plattform-Smoke meldete nur
  einen nicht-fatalen Qt-Font-Hinweis; der echte Android-/iOS-Geräte-Signoff bleibt offen.

### Fixed
- PWA-Manifest und Companion-HTML referenzieren wieder ausschließlich die versionierten Icons unter `web_companion/icons/`; dadurch bleibt die Offline-Installation auf case-sensitiven Hosts funktionsfähig und der mobile PWA-Smoke-Test grün.
- IMAP MSN→UID (kritisch): `_search_imap` verwendet jetzt `uid('search')` und `uid('fetch')` statt `search()`/`fetch()`. MSN-Nummern sind instabil wenn andere Clients gleichzeitig Mails verschieben/löschen; UIDs sind stabile Kennungen gemäß RFC 3501 §2.3.1.1.
- IMAP NIL-Guard: `uid('fetch')` kann bei nicht mehr existierenden UIDs eine leere/fehlerhafte Antwortstruktur zurückgeben; Guard verhindert AttributeError auf `msg_data[0][1]`.
- MIME-Charset: `_get_imap_message_body` liest den Charset aus dem Content-Type-Header (`get_content_charset`) statt blind UTF-8 anzunehmen; verhindert Mojibake bei ISO-8859-1/windows-1252-Mails.
- PDF-HTML-Sanitizer entfernen `script`-/`style`-Blöcke jetzt parserbasiert,
  sodass auch Varianten wie `</script >` zuverlässig gefiltert werden.
- IMAP multi-subject OR: Wenn 2+ Betreff-Filter konfiguriert waren, wurden Betreff-Einträge nach dem ersten stillschweigend verworfen; es wurde kein OR-Ausdruck aufgebaut, sodass nur Nachrichten mit dem ersten Betreff gefunden wurden.
- AccountDialog: `use_gmail_api` wurde beim Bearbeiten eines Gmail-Kontos (use_gmail_api=False) durch `on_provider_changed()` auf True zurückgesetzt; der gespeicherte Wert wird jetzt nach dem Provider-Lookup wiederhergestellt.
- MailAccount.from_dict: Unbekannte Schlüssel wurden stillschweigend verworfen; jetzt werden neue Felder toleriert (Vorwärtskompatibilität).
- IMAP multi-sender OR: Für 2+ Absender-Filter wurde die korrekte verschachtelte OR-FROM-Kette aufgebaut; zuvor wurden Absender mit AND verknüpft, sodass keine Nachricht passte.
- on_invoice_found nutzt jetzt save_invoices_db statt save_config (kein vollständiges Rewrite der Config bei jeder gefundenen Rechnung).
- start_grabbing: redundanter log_output.clear()-Aufruf entfernt, der Sync-Status-Meldungen löschte, bevor der Worker-Thread startete.

### Changed
- Der DATEV-Einstellungsdialog erläutert seine Konten-Mapping-Felder, Tabellenaktionen und Speichern-/Abbrechen-Aktionen jetzt zusätzlich per Accessible Description und Tooltip; das kompakte Layout bleibt unverändert.
- README, README-DE und `llms.txt` mit Startpunkten, local-first Invoice-Archive-/Gmail-/IMAP-/DATEV-Suchkontext und klarer Privacy-Abgrenzung geschärft.
- Interne Wartungsdateien (`CHECKS-LOG*.txt`, `LOCK*.txt`) sind jetzt gitignored; das Repo führt stattdessen nur veröffentlichbare Projektdateien.
- `EXPORTFORMAT.md` und `AUFGABEN.txt` auf den realen Bundle-Export/-Import-Stand gehoben; Companion-Rückfluss ist jetzt klar auf Betrag, Prüfflag und Notiz begrenzt.
- Die kompakte Rechnungs-Aktionsleiste exponiert jetzt klare Accessible Names, Descriptions und Tooltips für Auswahl-, Export-, Bundle- und DATEV-Aktionen, ohne die UI sichtbar aufzublähen.

### Added
- macOS/Linux platform smoke `tests/source_platform_smoke.py` (renamed from `tests/linux_platform_smoke.py` via `git mv`, history preserved) for offscreen PySide6 start, missing-keyring fallback, LibreOffice SOFFICE_PATH env-override detection and CSV export.
- GitHub Actions workflow `.github/workflows/source-platform-smoke.yml` on `ubuntu-latest` + `macos-latest`; installs PySide6 only (avoids pywin32/google-auth build failures on non-Windows).
- Neues Hilfsmodul `invoice_bundle.py` für redigierten Bundle-Export/-Import samt UI-Aktionen `Bundle Export` und `Bundle Import`.
- Neue Regressionstests `tests/test_invoice_bundle.py` für Exportvertrag, Hash-Konflikte und UI-Roundtrip.
- Committebare Web-Companion-PWA-Ressourcen (`favicon.ico`, `favicon.png`, `apple-touch-icon-180.png`) für lokale Installierbarkeit ohne tote Repo-Referenzen.

### CI
- Source-platform smoke workflow now uses verified `actions/checkout@v6` and `actions/setup-python@v6`, matching the main test workflow, and forces UTF-8 Python output.

### Fixed
- HTML-Injection in PDF-Covern: Mail-Metadaten (Datum, Betreff, Absender) werden nun mit `html.escape()` gesichert, bevor sie in xhtml2pdf/Selenium-HTML eingebettet werden.
- HTML-Injection bei OCR-Ergebnissen: OCR-Text in `<pre>`-Tags wird mit `html.escape()` gesichert.
- HTML-Injection in EML/MSG-Fallback: Plain-Text-Körper aus EML- und MSG-Dateien werden vor dem Einbetten in `<pre>`-Tags escaped.
- HTML-Injection in Gmail-Body: `_get_message_body()` escaped Plain-Text-Fallback jetzt mit `html.escape()`.
- HTML-Injection in IMAP-Merge-Pfad: `_process_imap_message()` escaped den Body beim Zusammenführen mit PDF-Anhängen.
- Ressourcen-Leak in `_pdf_to_images()`: `pdfium.PdfDocument.close()` wird jetzt per `try/finally` auch bei Rendering-Exceptions aufgerufen.
- Ressourcen-Leak in `_convert_msg_to_pdf()`: `extract_msg.Message.close()` wird jetzt per `try/finally` auch bei pisa-Exceptions aufgerufen.
- Temp-Datei in `add_text_layer()` wird bei Fehlern bereinigt: `temp_path` wird jetzt vor dem `try`-Block deklariert, damit der `except`-Handler sie per `unlink(missing_ok=True)` löschen kann.
- Variablen-Shadowing in `_process_gmail_message()` und `_process_imap_message()`: `success, msg = ocr.enhance_with_ocr(...)` überschrieb den `msg`-Parameter (E-Mail-Objekt); umbenannt zu `ocr_msg`.
- Regex-Backreference-Bug in `BrowserPDFRenderer.render_html_to_pdf()`: Ein Absendername mit `\1` (z. B. `CORP\1user`) wurde von `re.sub()` als Backreferenz interpretiert und duplizierte den `<body>`-Tag; Ersatz durch Lambda-Funktion behoben.
- Import-Crash ohne Gmail-Pakete: Die Rückgabe-Annotation `-> Optional[Credentials]` in `_get_gmail_credentials()` wurde eager ausgewertet; wenn Gmail-Pakete fehlen, ist `Credentials` undefiniert und das gesamte Modul schlägt beim Import fehl. Annotation auf `-> "Optional[Credentials]"` (String, lazy) umgestellt.
- Gmail-Datumsfilter-Inkonsistenz in `_build_gmail_search_query()`: Der `date_filter_months`-Fallback wurde ausgelöst wenn nur `date_to` gesetzt war (ohne `date_from`), sodass fälschlicherweise eine `after:`-Schranke eingefügt wurde; IMAP-Pendant prüft korrekt `if not search_args`. Bedingung auf `not date_from and not date_to` korrigiert.
- Windows-File-Lock in `enhance_with_ocr()`: `PdfReader(ocr_pdf_path)` hielt die `ocr_page.pdf`-Datei nach der Pages-Schleife offen; `unlink()` schlug auf Windows mit `PermissionError` fehl, OCR gab `False` zurück und hinterließ Temp-Dateien. `del ocr_reader` (und `del original_reader`) nach den jeweiligen Pages-Schleifen hinzugefügt, damit CPythons Refcounting die File-Handles sofort freigibt.
- Startup-Crash bei korrupter Konfiguration: `load_config()` fing `TypeError` nicht ab; fehlende Pflichtfelder in `Invoice` oder `InvoiceProfile` (z. B. nach Sync-Fehler oder manueller Bearbeitung der JSON-Dateien) ließen `cls(**filtered)` mit `TypeError` fehlschlagen, der aus dem Konstruktor propagierte. `TypeError` zu beiden `except`-Klauseln in `load_config()` hinzugefügt.

### Changed
- Porting status: macOS and Linux source smoke unified under `source_platform_smoke.py`; both platforms covered by CI.
- DATEV-Header nutzt jetzt dieselbe Datumslogik wie die Buchungszeilen, damit auch `TT/MM/JJJJ` das korrekte Exportintervall setzt.
### Added
- Gmail Query Builder im Profil-Dialog ergänzt; optionale Raw Queries können jetzt ohne manuelle Syntaxpflege vorbereitet werden
- GitHub-Actions-Testworkflow für Python 3.10, 3.11 und 3.12 ergänzt
- `llms.txt` als maschinenlesbarer Projektkontext ergänzt

### Changed
- Gmail-Suchen kombinieren gespeicherte Raw Queries jetzt mit Sender-, Betreff- und Datumsfiltern
- IMAP nutzt bei Gmail-kompatiblen Servern `X-GM-RAW` und fällt sonst sauber auf normale IMAP-Kriterien zurück

### Verified
- DATEV-Export als bereits vorhandene Migration gegen Code, Dialog, Doku und Regressionstests nachgezogen; `AUFGABEN.txt` entsprechend korrigiert
- Lokaler Teststand auf 104 grüne Tests aktualisiert

## [2.3.0] - 2026-05-02
### Added
- DATEV-Export: Rechnungen als DATEV-Buchungsstapel (CSV, cp1252) exportieren
- Invoice.amount Feld: Rechnungsbetrag direkt in der Tabelle editierbar
- DATEVSettingsDialog: Berater-Nr. und Mandant-Nr. konfigurierbar
