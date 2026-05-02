# Beitragsrichtlinie / Contributing Guide

## Deutsch

Vielen Dank für Ihr Interesse, zu diesem Projekt beizutragen.

### Wie Sie beitragen können

1. **Bug melden:** Erstellen Sie ein Issue mit einer klaren Reproduktion
2. **Feature vorschlagen:** Beschreiben Sie den Ziel-Workflow und erwartete Ausgabe
3. **Code beitragen:** Öffnen Sie einen Pull Request mit einer nachvollziehbaren Änderung

### Pull Requests

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch: `git checkout -b feature/mein-feature`
3. Installieren Sie die Abhängigkeiten: `pip install -r requirements.txt`
4. Führen Sie vorhandene Tests aus
5. Committen Sie Ihre Änderungen mit präziser Nachricht
6. Öffnen Sie einen Pull Request

### Projektspezifische Hinweise

- Keine echten Rechnungen, Anhänge oder Zugangsdaten committen
- Lokale Beispielausgaben aus `Outputbeispiele/` bleiben außerhalb von Git
- OCR-, LibreOffice- und Windows-COM-Fallbacks möglichst separat testen
- Neue Features sollten sowohl IMAP- als auch Gmail-Pfade berücksichtigen

### Code-Richtlinien

- Python: PEP 8
- Encoding: UTF-8
- Keine hardcoded Secrets oder lokalen Benutzerpfade
- Dokumentation und README bei sichtbaren Workflow-Änderungen mitpflegen

---

## English

Thank you for your interest in contributing to this project.

### How to Contribute

1. **Report bugs:** Open an issue with a clear reproduction
2. **Suggest features:** Describe the target workflow and expected output
3. **Contribute code:** Open a pull request with a focused, explainable change

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the available tests
5. Commit your changes with a precise message
6. Open a pull request

### Project-Specific Notes

- Do not commit real invoices, attachments, or credentials
- Keep local example outputs in `Outputbeispiele/` out of Git
- Test OCR, LibreOffice, and Windows COM fallbacks independently when possible
- New features should cover both IMAP and Gmail execution paths where relevant

### Code Guidelines

- Python: PEP 8
- Encoding: UTF-8
- No hardcoded secrets or local user paths
- Keep README and documentation aligned with visible workflow changes
