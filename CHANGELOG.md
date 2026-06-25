# Changelog - UniversalInvoiceMail

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

## [Unreleased]

### Fixed
- PDF-HTML-Sanitizer entfernen `script`-/`style`-Blöcke jetzt parserbasiert,
  sodass auch Varianten wie `</script >` zuverlässig gefiltert werden.
- IMAP multi-subject OR: Wenn 2+ Betreff-Filter konfiguriert waren, wurden Betreff-Einträge nach dem ersten stillschweigend verworfen; es wurde kein OR-Ausdruck aufgebaut, sodass nur Nachrichten mit dem ersten Betreff gefunden wurden.
- AccountDialog: `use_gmail_api` wurde beim Bearbeiten eines Gmail-Kontos (use_gmail_api=False) durch `on_provider_changed()` auf True zurückgesetzt; der gespeicherte Wert wird jetzt nach dem Provider-Lookup wiederhergestellt.
- MailAccount.from_dict: Unbekannte Schlüssel wurden stillschweigend verworfen; jetzt werden neue Felder toleriert (Vorwärtskompatibilität).
- IMAP multi-sender OR: Für 2+ Absender-Filter wurde die korrekte verschachtelte OR-FROM-Kette aufgebaut; zuvor wurden Absender mit AND verknüpft, sodass keine Nachricht passte.
- on_invoice_found nutzt jetzt save_invoices_db statt save_config (kein vollständiges Rewrite der Config bei jeder gefundenen Rechnung).
- start_grabbing: redundanter log_output.clear()-Aufruf entfernt, der Sync-Status-Meldungen löschte, bevor der Worker-Thread startete.

### Changed
- README, README-DE und `llms.txt` mit Startpunkten, local-first Invoice-Archive-/Gmail-/IMAP-/DATEV-Suchkontext und klarer Privacy-Abgrenzung geschärft.

### Added
- macOS/Linux platform smoke `tests/source_platform_smoke.py` (renamed from `tests/linux_platform_smoke.py` via `git mv`, history preserved) for offscreen PySide6 start, missing-keyring fallback, LibreOffice SOFFICE_PATH env-override detection and CSV export.
- GitHub Actions workflow `.github/workflows/source-platform-smoke.yml` on `ubuntu-latest` + `macos-latest`; installs PySide6 only (avoids pywin32/google-auth build failures on non-Windows).

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
- Lokaler Teststand auf 101 grüne Tests aktualisiert

## [2.3.0] - 2026-05-02
### Added
- DATEV-Export: Rechnungen als DATEV-Buchungsstapel (CSV, cp1252) exportieren
- Invoice.amount Feld: Rechnungsbetrag direkt in der Tabelle editierbar
- DATEVSettingsDialog: Berater-Nr. und Mandant-Nr. konfigurierbar

### Changed
- NEU: Nicht-PDF-Anhänge werden jetzt zentral in PDF-Archive umgewandelt
  - Unterstützt Bilddateien (`.png/.jpg/.jpeg/.bmp/.tif/.tiff/.webp`)
  - Unterstützt `.xlsx` direkt und `.docx` wenn `python-docx` installiert ist
  - Gleiche Konvertierungslogik für Gmail API und IMAP
  - Unterstützt `.doc/.xls` optional via Word/Excel-COM oder LibreOffice
- TESTS: Neue Abdeckung für Dateityp-Erkennung, XLSX-Konvertierung, Legacy-Fallbacks und Nicht-PDF-Anhänge in Gmail/IMAP
- HINWEIS: Wenn weder pywin32/Office noch LibreOffice lokal verfügbar sind, werden `.doc/.xls` weiterhin sauber mit Hinweis übersprungen

## [2.2.3] - 2026-01-16 - Portable Tesseract
* NEU: Automatische Erkennung von portablem Tesseract
  - Sucht nach tesseract_portable/tesseract.exe im Anwendungsordner
  - Setzt automatisch pytesseract.tesseract_cmd
  - Setzt automatisch TESSDATA_PREFIX Umgebungsvariable
* Vorhandene Sprachdaten: deu.traineddata, eng.traineddata
  - Deutsch + Englisch OCR funktioniert out-of-the-box
* Keine systemweite Tesseract-Installation nötig!
  - Einfach tesseract_portable Ordner mitliefern

## [2.2.2] - 2026-01-16 - Poppler entfernt
* ENTFERNT: pdf2image und Poppler-Abhängigkeit
  - Poppler musste separat installiert werden (umständlich auf Windows)
* NEU: pypdfium2 für PDF-zu-Bild Konvertierung
  - Alle Binaries sind im pip-Paket enthalten
  - Keine separate Installation nötig!
  - Schneller als pdf2image/Poppler
* OCR-Installation jetzt einfacher:
  - pip install pytesseract pypdfium2 pypdf Pillow
  - Nur noch Tesseract OCR separat installieren

## [2.2.1] - 2026-01-16 - OCR Enhancement
* FIX: OCR läuft jetzt IMMER über Bilder (nicht nur wenn kein Text vorhanden)
  - Wichtig für Temu/Amazon: Text UND Bilder mit Artikelinfos
* NEU: enhance_with_ocr() Methode im OCRProcessor
  - Original-PDF Layout bleibt erhalten (Browser-Rendering!)
  - OCR-Text wird als zusätzliche Seite am Ende angefügt
  - Überschrift "OCR-Erkannter Text aus Bildern"
  - Alle Seiten werden gescannt, Text wird zusammengefasst
* OCR-Logik geändert:
  - Vorher: Nur wenn PDF <50 Zeichen Text hatte (has_text Check)
  - Jetzt: Immer wenn OCR aktiviert ist (scannt alle Bilder)

## [2.2.0] - 2026-01-16 - Browser-Rendering
* NEU: Dritter PDF-Modus "Browser (Edge/Chrome)" - Empfohlen!
  - Nutzt Headless Edge/Chrome für natives HTML-Rendering
  - Chrome DevTools Protocol (CDP) für PDF-Export
  - Beste Qualität: Bilder, Fonts, modernes CSS werden korrekt gerendert
  - Keine PermissionError bei externen Ressourcen
* NEU: BrowserPDFRenderer Klasse
  - Automatischer Browser-Start (headless)
  - Versucht Edge zuerst, dann Chrome
  - Fallback zu xhtml2pdf wenn Browser fehlschlägt
* NEU: webdriver-manager Integration
  - Automatischer Download des passenden WebDrivers
  - Keine manuelle Driver-Installation nötig
* GUI: Browser-Modus nur sichtbar wenn Selenium installiert
* Optionale Abhängigkeiten: selenium, webdriver-manager
  - pip install selenium webdriver-manager

## [2.1.0] - 2026-01-16 - Zwei PDF-Modi mit OCR
* NEU: PDF-Modus Auswahl in Einstellungen
  - "Schnell (nur Text)" = Standard, entfernt Bilder (stabil, schnell)
  - "Vollständig (mit Bildern)" = behält Bilder, schöner Output
* NEU: OCR-Option für bildbasierte Mails (Temu, Amazon)
  - Checkbox "OCR für bildbasierte PDFs" in Einstellungen
  - Nutzt Tesseract + Poppler für Texterkennung
  - Nur wenn PDF keine Textebene hat (automatische Erkennung)
* NEU: sanitize_html_for_pdf_full() für "Vollständig"-Modus
  - Behält <img> Tags und inline Bilder (CID, Base64)
  - Entfernt nur Scripts und externe URLs
* NEU: OCRProcessor Klasse (portiert von GmailDocsGrabberV5)
  - has_text() prüft ob PDF durchsuchbaren Text hat
  - add_text_layer() fügt OCR-Textebene hinzu
* Optionale Abhängigkeiten: pytesseract, pdf2image, pypdf, Pillow
  - Poppler-Installation für Windows notwendig (pdf2image)

## [2.0.2] - 2026-01-16 - PDF & Order-ID Fixes
* FIX: 0KB PDF-Dateien werden jetzt gelöscht statt behalten
  - html_to_pdf() löscht leere Dateien bei Fehler
  - Verhindert "Datei existiert bereits" bei erneutem Durchlauf
* FIX: Aggressivere HTML-Bereinigung für xhtml2pdf
  - <style> Tags komplett entfernt (modernes CSS crasht xhtml2pdf)
  - Inline style-Attribute entfernt
  - HTML-Kommentare entfernt
  - Control Characters (0x00-0x1F) entfernt
* FIX: Order-ID Fallback nutzt jetzt MD5-Hash statt msg['id']
  - Verhindert "-collapse" und "-bottom" in Dateinamen
  - Diese kamen aus HTML-Fragmenten der Gmail Message ID

## [2.0.1] - 2026-01-16 - Gemini Audit Fixes
* FIX: IMAP Datumsformat Locale-Problem (RFC 3501)
  - Neue Funktion format_imap_date() mit englischen Monatsnamen
  - strftime("%d-%b-%Y") erzeugte auf DE-Systemen "Mai" statt "May"
  - IMAP-Server akzeptieren nur englische Monatsnamen
* FIX: Base64 Padding-Berechnung mit Whitespaces
  - safe_b64decode() entfernt jetzt Newlines/Spaces vor len()
  - E-Mails enthalten oft Zeilenumbrüche in Base64-Strings
* FIX: Gmail API Rate Limiting
  - time.sleep(0.1) nach messages().get() Aufrufen
  - time.sleep(0.05) nach attachments().get() Aufrufen
  - Verhindert HttpError 429 bei vielen Mails

## [2.0.0] - 2026-01-16 - Audit-Fix Release
* FIX #3: Inline-PDFs werden erkannt (data ohne attachmentId)
  - Temu/eBay PDFs die direkt base64-codiert sind werden jetzt gespeichert
* FIX #7: IMAP BEFORE ist exklusiv -> +1 Tag addiert
  - date_to wird jetzt korrekt als "bis einschließlich" interpretiert
* FIX #14: Order-ID Regex verschärft
  - UUIDs werden nicht mehr fälschlich als Bestellnummer erkannt
  - Längenbegrenzung auf 5-20 Zeichen
  - Erfordert Kontext-Keyword (Bestellnummer, Order, Invoice etc.)
* FIX #12: Division by Zero in Progress bereits abgesichert
  - Guard "if t > 0 else 0" vorhanden

## [1.9.2] - 2026-01-16
* FIX: Vollständige HTML-Bereinigung VOR PDF-Konvertierung
  - Neue Funktion sanitize_html_for_pdf() entfernt:
    * <img> Tags (Hauptursache für Windows PermissionError)
    * <link> Tags (externe Stylesheets)
    * <script> Tags
    * @font-face und @import CSS-Regeln
    * url() Referenzen in CSS
    * Zero-Width-Spaces (\u200b, \u200c, \u200d, \ufeff)
  - link_callback bleibt als Fallback-Schutz
* FIX: break_long_urls() deaktiviert (verursachte UnicodeEncodeError)
  - CSS word-break: break-all übernimmt URL-Umbruch

## [1.9.1] - 2026-01-16
* FIX: Korrupte PDFs behoben - link_callback blockiert externe Ressourcen
  - html_to_pdf nutzt jetzt pisa.CreatePDF mit link_callback=lambda: None
  - Keine TTFError/PermissionError mehr durch externe Fonts
  - Ersetzt problematische clean_html_for_pdf() Funktion (gelöscht)
* FIX: 0-Byte Dateien werden in scan_folders_for_new_files() übersprungen
  - Korrupte/unvollständige Dateien werden nicht mehr importiert

## [1.9.0] - 2026-01-16
* FIX: Temu-Mails zeigen nun vollständigen HTML-Inhalt statt nur Fallback-Text
  - HTML wird bei multipart/alternative bevorzugt (Gmail API + IMAP)
* FIX: Lange URLs brechen nun korrekt um (Zero-Width-Space Workaround für xhtml2pdf)
  - URLs in src/href bleiben unverändert (Bilder laden korrekt)
* FIX: Typ-Spalte zeigt Emoji korrekt (Spaltenbreite 40px, zentriert)
* FIX: Hash-Sync vor Download - alle PDFs im Ordner werden jetzt korrekt erkannt
  - Auch defekte/manuell hinzugefügte Dateien werden nicht erneut heruntergeladen
  - Neue Funktion _collect_folder_hashes() sammelt alle Hashes aus Zielordnern
* FIX: Duplikat-Dateien werden jetzt in GUI importiert (Gemini-Fix)
  - Dateien mit bekanntem Hash werden nicht mehr übersprungen
  - Defekte Dateien sind sichtbar und löschbar in der GUI
  - Sender zeigt "Duplikat (Import)" zur Unterscheidung
* Neue Funktion break_long_urls() für PDF-Lesbarkeit
* Neue Funktion _get_all_body_parts() für rekursive Part-Sammlung

## [1.8.1] - 2026-01-13
* FIX: Header-Design nutzt jetzt Tabellen statt CSS-Gradient (xhtml2pdf kompatibel)
* NEU: Body-Filter im Profil: "Body muss enthalten" und "Body darf nicht enthalten"
* Beide Body-Filter sind optional (leer = kein Filter)
* Kommasepariert = ODER-Verknüpfung

## [1.8] - 2026-01-13
* NEU: "Dem PDF den Mail-Body anhängen" Option in Einstellungen
* NEU: Hybrid-Design für Body-PDFs mit Header (Datum, Betreff, Absender)
* Bei aktivierter Option werden PDF-Anhänge + Mail-Body zu einer Datei gemerged
* Body-PDFs erhalten jetzt einen designten Header-Bereich
* Benötigt PyPDF2 für Merge-Funktion (Fallback: nur Original)

## [1.7.5] - 2026-01-13
* NEU: Typ-Symbol in Rechnungsliste (📎 = Anhang, 📄 = Body-PDF)
* NEU: Blacklist-Feld im Profil "Darf NICHT enthalten"
* Mails mit Blacklist-Begriffen in Betreff/Body werden übersprungen
* Tooltip zeigt Typ-Bedeutung bei Hover

## [1.6] - 2026-01-13
* BUG-Fix: Dateiliste synchronisiert jetzt mit Dateisystem
* Gelöschte Dateien werden automatisch aus Liste entfernt
* Neue Methode save_invoices_db() für persistente Speicherung
* Log-Ausgabe zeigt Anzahl entfernter Einträge

## [1.5] - 2026-01-13
* NEU: CSV Export Button - Rechnungsliste als CSV exportieren
* CSV Format: Semikolon-getrennt, UTF-8 mit BOM (Excel-kompatibel)
* Spalten: Datum, Profil/Shop, Absender, Betreff, Dateiname, Pfad
* ROADMAP.txt erstellt für zukünftige Features

## [1.4] - 2026-01-13
* GUI: Von/Bis Datum-Auswahl mit Kalender-Popup
* GUI: Schnellauswahl-Dropdown ("Letzte 12 Monate", "Dieses Jahr", etc.)
* Datum-Auswahl: Gespeicherte Werte werden beim Start geladen
* Bestellnummer: Wird jetzt auch aus Mail-Body extrahiert
* Gmail/IMAP: Nutzt date_from/date_to statt date_filter_months

## [1.3] - 2026-01-13
* BUG-Fix: Mailkonto kann per Doppelklick bearbeitet werden
* Neue Option: "Papierkorb durchsuchen" Checkbox in Einstellungen
* Filter-Transparenz: Tooltips erklären ODER-Verknüpfung
* AccountDialog: Zeigt "Leer lassen = unverändert" bei Passwort

## [1.2] - 2026-01-13
* PDF-Fix: Besseres A4-Layout mit word-wrap
* IMAP: Durchsucht alle Ordner (Gmail nutzt "All Mail")
* Order-ID: Verbesserte Bestellnummern-Erkennung

## [1.1] - 2026-01-13
* Bug-Fix: Start-Button löst korrekt den Abruf aus
* Neue Funktion: Automatische Suche nach credentials.json

## [1.0] - 2026-01-09
* Erste Veröffentlichung
* Universal IMAP + Gmail API Support
* Vorkonfigurierte Shop-Profile
* PDF-Anhänge + Mail-zu-PDF Konvertierung
* Hash-basierte Duplikat-Erkennung
* Sichere Passwort-Speicherung via Keyring
