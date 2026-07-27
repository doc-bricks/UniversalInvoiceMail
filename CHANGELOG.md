# Changelog - UniversalInvoiceMail

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

## [2.4.1] - 2026-07-27 - Technical Hygiene & Maintenance

### Changed
- `llms.txt`: Header auf `Last-checked: 2026-07-27` und 125 verifizierte Tests (115 Pytest + 10 Node Web Companion PWA) aktualisiert.
- `CHECKS-LOG.txt`: Technischen Hygiene- & Maintenance-Check (Pfad A) registriert.
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
- `EXPORTFORMAT.md` und `AUFGABEN.txt` auf den realen Bundle-Export/-Import-Stand gehoben; Companion-Rückfluss ist jetzt klar auf Betrag, Prüfflag und Notiz begrenzt.
- Die kompakte Rechnungs-Aktionsleiste exponiert jetzt klare Accessible Names, Descriptions und Tooltips für Auswahl-, Export-, Bundle- und DATEV-Aktionen, ohne die UI sichtbar aufzublähen.

### Added
- macOS/Linux platform smoke `tests/source_platform_smoke.py` (renamed from `tests/linux_platform_smoke.py` via `git mv`, history preserved) for offscreen PySide6 start, missing-keyring fallback, LibreOffice SOFFICE_PATH env-override detection and CSV export.
- GitHub Actions workflow `.github/workflows/source-platform-smoke.yml` on `ubuntu-latest` + `macos-latest`; installs PySide6 only (avoids pywin32/google-auth build failures on non-Windows).
- Neues Hilfsmodul `invoice_bundle.py` für redigierten Bundle-Export/-Import samt UI-Aktionen `Bundle Export` und `Bundle Import`.
- Neue Regressionstests `tests/test_invoice_bundle.py` für Exportvertrag, Hash-Konflikte und UI-Roundtrip.

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
