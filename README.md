# UniversalInvoiceMail v2.2.3

Desktop-Tool zum Abrufen, Konvertieren und Archivieren von Rechnungen und Belegen aus E-Mails.
Desktop tool for downloading, converting, and archiving invoices and receipts from email accounts.

![UniversalInvoiceMail Vorschau](README/screenshots/main.png)

## Überblick

UniversalInvoiceMail verbindet klassische IMAP-Postfächer und optional die Gmail API mit einem lokalen PDF-Archiv-Workflow. Das Tool lädt Anhänge, rendert Bestellbestätigungen als PDF, erkennt Duplikate per Hash und speichert die Ergebnisse strukturiert pro Profil oder Shop.

## Funktionen / Features

- Universal IMAP für Gmail, Outlook, GMX, Web.de, T-Online und weitere Provider
- Optionale Gmail-API-Anbindung für schnellere und robustere Gmail-Läufe
- Profilbasierte Filter für Absender, Betreff, Body und Zeiträume
- Download von PDF-Anhängen sowie Konvertierung weiterer Anhangstypen nach PDF
- Unterstützte Konvertierung: Bilder (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tif`, `.tiff`, `.webp`), `.docx`, `.xlsx`
- Optionale Legacy-Konvertierung für `.doc` und `.xls` via Word/Excel-COM oder LibreOffice
- Optionales OCR für bildbasierte PDFs mit Tesseract und `pypdfium2`
- Hash-basierte Duplikat-Erkennung über lokale Archivordner
- Sichere Passwortspeicherung via `keyring`

## Schnellstart / Quick Start

### Windows

1. `start.bat` ausführen
2. Mailkonto anlegen
3. Profil oder Shop-Vorlage konfigurieren
4. Zeitraum und Zielordner festlegen
5. `Rechnungen abrufen` starten

### Manuell / Manual

```bash
pip install -r requirements.txt
python UniversalInvoiceMail.py
```

## Typischer Workflow

1. Konto für IMAP oder Gmail API anlegen
2. Suchprofil mit Filtern und Zielordner konfigurieren
3. Optional OCR und PDF-Modus einstellen
4. Scan auslösen
5. Ergebnisse im lokalen Rechnungsarchiv prüfen

## Lokale Daten / Local Data

Konfigurations- und Laufzeitdaten werden unter `%USERPROFILE%\.universal_invoice_mail\` gespeichert:

```text
%USERPROFILE%\.universal_invoice_mail\
├── config.json
├── invoices.json
├── credentials.json
└── token.json
```

Standardmäßig landen archivierte Dateien unter `%USERPROFILE%\Documents\Rechnungen\`.

## Optionale Komponenten

- Gmail API: `google-api-python-client`, `google-auth`, `google-auth-oauthlib`
- OCR: `pytesseract`, `pypdfium2`, `pypdf`, Tesseract OCR
- Legacy Office: `pywin32` oder ein lokales LibreOffice mit `soffice.exe`

Wenn kein OCR- oder Office-Backend verfügbar ist, bleibt der Lauf robust; nicht unterstützte Schritte werden protokolliert und übersprungen.

## Tests

```bash
pytest tests -v
python -m pytest tests
```

Vorhanden sind Unit-Tests für Hilfsfunktionen sowie Integrations-Tests für IMAP- und Gmail-Workflows mit Mocks.

## Datenschutz / Privacy

- Zugangsdaten werden nicht im Projektordner gespeichert
- Lokale Beispielausgaben und Portable-Bundles sind bewusst per `.gitignore` aus zukünftigen Repositories ausgeschlossen
- Release-Artefakte bleiben unter `releases/` lokal

## Lizenz / License

[MIT](LICENSE)

## English

UniversalInvoiceMail is a desktop application for collecting invoices and receipts from IMAP mailboxes or the Gmail API, converting supported attachments to PDF, and storing them in a structured local archive.

### Highlights

- Universal IMAP plus optional Gmail API
- PDF conversion for images, `.docx`, and `.xlsx`
- Optional legacy Office conversion via COM or LibreOffice
- Optional OCR for image-based PDFs
- Hash-based duplicate detection
- Secure credential handling via `keyring`

### Local Storage

Runtime data is stored in `%USERPROFILE%\.universal_invoice_mail\`, while archived files are written to `%USERPROFILE%\Documents\Rechnungen\` by default.

### License

MIT License
