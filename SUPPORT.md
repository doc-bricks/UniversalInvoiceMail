# Support & Hilfe — UniversalInvoiceMail

**App:** UniversalInvoiceMail  
**Version:** 2.3.0  
**Autor:** Lukas Geiger  
**Kontakt / E-Mail:** lukasgeiger@googlemail.com  
**Projekt-Repository:** https://github.com/doc-bricks/UniversalInvoiceMail  

---

## Deutsch

### Kontakt & Fehlermeldungen

- **GitHub Issue Tracker:** [github.com/doc-bricks/UniversalInvoiceMail/issues](https://github.com/doc-bricks/UniversalInvoiceMail/issues)
- **E-Mail Support:** lukasgeiger@googlemail.com

Bitte fügen Sie bei Fehlermeldungen nach Möglichkeit folgende Angaben bei:
1. Betriebssystemversion (z. B. Windows 11 23H2 / 24H2)
2. Art des Mailkontos (IMAP mit SSL/TLS bzw. Gmail OAuth)
3. Ggf. relevante Log-Meldungen aus dem Status-Bereich der Anwendung (ohne Passwörter!)

### Häufig gestellte Fragen (FAQ)

**Wo speichert UniversalInvoiceMail Konfigurationen und Datenbanken?**  
Unter Windows liegen die Profildaten und die Rechnungsübersicht standardmäßig unter `%APPDATA%\UniversalInvoiceMail\` (bzw. im Anwendungsdaten-Verzeichnis des aktuellen Benutzers).

**Wie werden meine Passwörter geschützt?**  
UniversalInvoiceMail nutzt den Windows Anmeldeinformations-Manager (bzw. das `keyring`-Subsystem des Betriebssystems), sodass Passwörter verschlüsselt auf dem Betriebssystem abgelegt werden und niemals im Klartext in Konfigurationsdateien stehen.

**Welche Anhänge können automatisch in PDF konvertiert werden?**  
Neben nativen PDF-Rechnungen unterstützt die Anwendung Bildformate (PNG, JPG, JPEG, BMP, TIFF, WebP), Microsoft Excel (.xlsx), Word (.docx) sowie Maildateien (.eml, .msg).

**Wie funktioniert der DATEV-Export?**  
Über das Menü bzw. den DATEV-Tab können Sie Rechnungsbeträge, Belegnummern, Konten und Gegenkonten (SKR03 / SKR04) prüfen und als DATEV-konformen Buchungsstapel (CSV) für Ihre Buchhaltung oder Steuerberatung exportieren.

**Was ist der Invoice Bundle Export?**  
Der Bundle-Export (`universalinvoicemail-invoicebundle-v1.json`) erzeugt eine redigierte, datenschutzkonforme Zusammenfassung für den Web/PWA-Companion. Passwörter, Tokens und Roh-Mailbodies werden dabei nicht exportiert.

### Systemanforderungen

- **Betriebssystem:** Windows 10 (Version 1809 / Build 17763) oder neuer (64-Bit), macOS 12+ oder Linux
- **Architektur:** x64 / ARM64 (über Windows Emulation)
- **Arbeitsspeicher:** Mindestens 4 GB RAM empfohlen
- **Festplattenspeicher:** Ca. 150 MB freier Speicherplatz für die Anwendung zzgl. Speicher für heruntergeladene Belege

---

## English

### Contact & Bug Reports

- **GitHub Issue Tracker:** [github.com/doc-bricks/UniversalInvoiceMail/issues](https://github.com/doc-bricks/UniversalInvoiceMail/issues)
- **Email Support:** lukasgeiger@googlemail.com

When submitting issue reports, please provide:
1. Operating system version (e.g. Windows 11 23H2 / 24H2)
2. Mail account type (standard IMAP SSL/TLS or Gmail OAuth)
3. Relevant error messages from the status view (never include passwords or tokens)

### Frequently Asked Questions (FAQ)

**Where does UniversalInvoiceMail store its configuration and databases?**  
On Windows, settings and invoice records are stored in `%APPDATA%\UniversalInvoiceMail\` (within your user profile directory).

**How are my email passwords secured?**  
UniversalInvoiceMail uses the operating system's native Credential Manager (via Python `keyring`). Passwords are never saved as plain text in application configuration files.

**Which attachment file formats can be converted to PDF?**  
In addition to native PDF files, images (PNG, JPG, BMP, TIFF, WebP), spreadsheets (.xlsx), documents (.docx), and email containers (.eml, .msg) can be processed and converted locally.

**How does the DATEV export work?**  
From the DATEV panel, verify account mappings (SKR03 / SKR04), amounts, and invoice dates, then export standard DATEV-compliant booking batches (CSV) for your tax advisor or accounting software.

**What is the Invoice Bundle format?**  
The Bundle export (`universalinvoicemail-invoicebundle-v1.json`) produces a privacy-preserving summary for the companion app. Credentials, OAuth tokens, and raw message bodies are stripped automatically.

### System Requirements

- **Operating System:** Windows 10 (version 1809 / build 17763) or newer (64-bit), macOS 12+, or modern Linux
- **Architecture:** x64
- **RAM:** Minimum 4 GB RAM recommended
- **Disk Space:** Approx. 150 MB for the application plus storage for your invoice PDFs
