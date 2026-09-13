# Datenschutzerklärung / Privacy Policy — UniversalInvoiceMail

**Stand:** 2026-09-13  
**Anbieter / Kontakt:** Lukas Geiger (https://github.com/doc-bricks/UniversalInvoiceMail)  
**E-Mail:** lukasgeiger@googlemail.com

---

## Deutsch

### 1. Grundsatz
UniversalInvoiceMail ist als **datenschutzfreundliche ("Privacy-First") Desktop-Anwendung** konzipiert. Die Anwendung sammelt, speichert oder überträgt **keine** Personen-, Nutzungs- oder Telemetriedaten an den Entwickler oder an sonstige unbeteiligte Dritte.

### 2. Lokale Speicherung & Datensparsamkeit
Alle von der Anwendung verarbeiteten Daten verbleiben ausschließlich lokal auf Ihrem Computer:
- **Rechnungen & Belege:** Werden im von Ihnen definierten lokalen Verzeichnis strukturiert gespeichert (PDF, Originaldokumente).
- **Rechnungsdatenbank & Metadaten:** Lokale SQLite- bzw. JSON-Archive im Anwendungsdatenordner (`%APPDATA%\UniversalInvoiceMail\` bzw. `~/.config/universalinvoicemail/`).
- **Zugangsdaten:** Passwörter für IMAP-Postfächer werden nicht im Klartext gespeichert, sondern über den systemeigenen Schlüsselspeicher (Windows Credential Manager / macOS Keychain / Linux Secret Service) gesichert.
- **Gmail OAuth:** Autorisierungs-Token verbleiben lokal auf Ihrem Endgerät und dienen ausschließlich der Kommunikation zwischen Ihrem Rechner und den Google-Mail-APIs.

### 3. Netzwerkzugriff
UniversalInvoiceMail verbindet sich ausschließlich mit den von Ihnen explizit eingerichteten Mail-Servern (IMAP-Server Ihres Providers bzw. offizielle Google-OAuth-/Gmail-Endpunkte) zum Zweck des Abrufs von E-Mails und Rechnungsanhängen. Es findet keinerlei Kommunikation mit Werbenetzwerken, Analysediensten oder Tracking-Servern statt.

### 4. Lokale Konvertierung & OCR
Die Konvertierung von Office-Dokumenten (DOCX, XLSX), Bildern und Mail-Bodies sowie optionale OCR-Texterkennung erfolgen vollständig lokal auf Ihrem Rechner (unter Verwendung lokaler Bibliotheken wie `pypdfium2`, Tesseract oder installierter Office-/LibreOffice-Instanzen). Es werden keine Dokumente an Cloud-Dienste hochgeladen.

### 5. Bundle-Export & Companion-Datenaustausch
Für die mobile Einsicht via Web/PWA-Companion (`universalinvoicemail-invoicebundle-v1.json`) werden sensible Daten wie Passwörter, Gmail-Tokens, Google-Client-Secrets, absolute Systempfade und vollständige Mail-Bodies strikt herausgefiltert. Der Datenaustausch erfolgt dateibasiert und vollständig unter Ihrer manuellen Kontrolle.

### 6. Betroffenenrechte
Sie behalten zu jedem Zeitpunkt die uneingeschränkte Kontrolle über sämtliche Rechnungs- und Profildaten. Alle lokalen Datenbanken, exportierten DATEV-Dateien und Konfigurationsdateien können Sie jederzeit direkt einsehen, sichern oder löschen.

---

## English

### 1. Overview
UniversalInvoiceMail is designed as a **privacy-first desktop application**. It does not collect, track, or transmit any personal data, usage analytics, or telemetry to the developer or any third party.

### 2. Local Processing & Data Minimization
All invoice and account data is processed and stored 100% locally on your computer:
- **Invoices and Receipts:** Saved directly to your chosen local destination folders (PDF and original attachments).
- **Metadata & Cache:** Stored in local SQLite/JSON databases within your user profile directory (`%APPDATA%\UniversalInvoiceMail\` or `~/.config/universalinvoicemail/`).
- **Credentials:** IMAP account passwords are protected via the native operating system keyring (Windows Credential Manager / macOS Keychain / Linux Secret Service).
- **Gmail OAuth:** OAuth tokens remain on your local machine and are used strictly for direct communication between your computer and Google Mail APIs.

### 3. Network Communication
UniversalInvoiceMail establishes network connections exclusively to the email endpoints you explicitly configure (your email provider's IMAP server or Google's official Gmail APIs) to retrieve emails and invoice attachments. No telemetry, crash reporters, or third-party trackers are present.

### 4. Local Conversion and OCR
Conversion of email bodies, office documents (DOCX, XLSX), and images as well as optional OCR text recognition are carried out entirely on your local CPU (using local engines such as `pypdfium2`, Tesseract, or local Office/LibreOffice). No files are uploaded to external conversion clouds.

### 5. Invoice Bundle Export & Companion
When exporting redacted invoice bundles for mobile review (`universalinvoicemail-invoicebundle-v1.json`), credentials, tokens, secrets, full system paths, and raw email bodies are stripped automatically. The exchange is strictly file-based and under your full manual control.

### 6. User Rights & Data Control
You retain full ownership and control of all invoice data at all times. All local databases, DATEV files, and configurations can be inspected, backed up, or deleted at will.
