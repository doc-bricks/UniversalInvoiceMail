# Security Policy / Sicherheitsrichtlinie

## Deutsch

### Sicherheitsphilosophie & Leitlinien

doc-bricks/UniversalInvoiceMail ist als lokale Desktop-Anwendung (Local-First) zur automatisierten Sammlung, Analyse und Archivierung von Rechnungs-E-Mails, PDF-Konvertierung von Anhängen und zum DATEV-kompatiblen CSV-Export konzipiert. Sicherheit, Vertraulichkeit von Finanzdaten und Geheimnisschutz basieren auf folgenden Kernprinzipien:

- **Local-First & Zero Egress:** UniversalInvoiceMail überträgt keinerlei Telemetriedaten, Nutzungsstatistiken oder Rechnungsdaten an Dritte. Die gesamte Verarbeitung von E-Mails, Rechnungsbeträgen, IBANs, Anhängen und DATEV-Buchungssätzen findet ausschließlich lokal auf dem System des Benutzers statt.
- **Sicherer Geheimnisschutz via OS-Keyring:** E-Mail- und Postfach-Zugangsdaten werden verschlüsselt im betriebssystemeigenen Keyring (keyring-Bibliothek: Windows Credential Manager) hinterlegt. Passwörter und OAuth-Tokens werden niemals im Klartext in Konfigurationsdateien oder im Quellcode-Repository gespeichert.
- **Unprivilegierter User-Mode (Non-Elevation):** UniversalInvoiceMail benötigt und verlangt keine Administratorrechte. Alle Dateisystemoperationen, Archivierungen und Konvertierungen laufen streng im unprivilegierten Benutzerkontext ab.
- **Sichere Dateinamen-Sanitisierung & Pfad-Isolation:** Beim Extrahieren von Anhängen aus EML-/MSG-Dateien werden Dateinamen strikt bereinigt, um Path-Traversal-Angriffe (../, unzulässige Windows-Gerätenamen wie CON, PRN, Steuerzeichen) abzuwehren.
- **Optionale Cloud-Schnittstellen (Opt-in):** Netzwerkverbindungen werden ausschließlich auf ausdrückliche Anforderung des Nutzers zu den vom Nutzer konfigurierten IMAP-Servern oder der Google Gmail API aufgebaut.

### Unterstützte Versionen

| Version | Unterstützt | Anmerkungen |
| ------- | ----------- | ----------- |
| 2.3.x   | Ja          | Aktuelle Version mit EML/MSG-Härtung, DATEV-Export und Offline-Archivierung |
| < 2.3.0 | Eingeschränkt | Bitte auf die aktuelle Version aktualisieren |

### Sicherheitslücken melden

Wenn Sie eine Sicherheitslücke oder ein Datenschutzrisiko in UniversalInvoiceMail entdecken:

1. **Bevorzugter Meldeweg:** Nutzen Sie die private Vulnerability-Reporting-Funktion auf GitHub:
   - Öffnen Sie den Tab **Security** in diesem Repository
   - Wählen Sie **Report a vulnerability** ([Direktlink](https://github.com/doc-bricks/UniversalInvoiceMail/security/advisories/new))
   - Beschreiben Sie das Problem, Schritte zur Reproduktion und mögliche Auswirkungen
2. **Direkter E-Mail-Kontakt:** Alternativ können Sie sich an unsere Sicherheitskoordinatoren wenden:
   - security@doc-bricks.org
   - security@open-bricks.org
   - support@lukasgeiger.com

### Reaktionszeiten & SLAs

- **Erste Eingangsbestätigung:** Verbindlich innerhalb von 48 Stunden nach Eingang der Meldung.
- **Erste Risikobewertung & Triage:** Innerhalb von 5 Werktagen.
- **Sicherheits-Patch:** Nach Priorität und Kritikalität im schnellstmöglichen Turnus.

Bitte öffnen Sie für Sicherheitslücken **keine öffentlichen Issues** und veröffentlichen Sie keine Rechnungs- oder Zugangsdaten.

---

## English

### Security Principles & Core Guarantees

doc-bricks/UniversalInvoiceMail is engineered as a local-first desktop application for collecting invoice emails, converting attachments to PDF, archiving receipts privately, and exporting DATEV-compliant accounting records. Privacy, financial confidentiality, and secret protection are grounded in the following guarantees:

- **Local-First & Zero Egress:** UniversalInvoiceMail does not transmit telemetry, tracking data, or financial records to external servers. All processing of emails, financial amounts, IBANs, attachments, and DATEV records occurs strictly on the user's local workstation.
- **OS Keyring Cryptographic Protection:** Email and mailbox credentials are stored exclusively in the operating system's secure credential store (keyring library: Windows Credential Manager). Passwords and OAuth tokens are never stored in plaintext on disk or in Git-tracked files.
- **Unprivileged User-Mode Operation (Non-Elevation):** UniversalInvoiceMail runs entirely within normal user permissions and does not require administrative elevation.
- **Safe Attachment Sanitization & Path Traversal Guard:** When extracting attachments from EML/MSG files, filenames are sanitized to prevent directory traversal (../, Windows reserved device names, illegal control characters).
- **Explicit Network Boundaries (Opt-in):** Outbound connections occur exclusively when explicitly initiated by the user to connect to user-configured IMAP servers or Google's Gmail API.

### Supported Versions

| Version | Supported | Notes |
| ------- | --------- | ----- |
| 2.3.x   | Yes       | Current production release with EML/MSG hardening, DATEV export, and private archive |
| < 2.3.0 | Deprecated | Upgrade to the latest version recommended |

### Reporting a Vulnerability

If you discover a security vulnerability or sensitive data exposure in UniversalInvoiceMail:

1. **Preferred Method:** Report privately via GitHub's Security Advisories:
   - Navigate to the **Security** tab of this repository
   - Click **Report a vulnerability** ([Direct Link](https://github.com/doc-bricks/UniversalInvoiceMail/security/advisories/new))
   - Provide reproduction steps, affected versions, and expected impact
2. **Direct Security Email:** Alternatively, email our security coordinators directly:
   - security@doc-bricks.org
   - security@open-bricks.org
   - support@lukasgeiger.com

### Response SLAs & Vulnerability Handling

- **Initial Acknowledgment:** Guaranteed within 48 hours of receipt.
- **Triage & Risk Assessment:** Within 5 business days.
- **Remediation & Patching:** Deployed with highest priority according to severity.

Please **do not disclose vulnerabilities in public issues**. Confirmed security patches are prioritized and released promptly.
