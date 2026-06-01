# UniversalInvoiceMail

[![UniversalInvoiceMail tests](https://github.com/doc-bricks/UniversalInvoiceMail/actions/workflows/tests.yml/badge.svg)](https://github.com/doc-bricks/UniversalInvoiceMail/actions/workflows/tests.yml)

Desktop tool for downloading, converting, and archiving invoices and receipts from email accounts.

> **Deutsche Dokumentation:** [README-DE.md](README-DE.md)

![UniversalInvoiceMail Preview](README/screenshots/main.png)

## Features

- Universal IMAP for Gmail, Outlook, GMX, Web.de, T-Online, and other providers
- Optional Gmail API integration for faster and more robust Gmail runs
- Optional per-profile Gmail query builder for Gmail API and Gmail IMAP with `X-GM-RAW`
- Profile-based filters for sender, subject, body, and date ranges
- Downloads PDF attachments and converts other attachment types to PDF
- Supported conversions: images (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tif`, `.tiff`, `.webp`), `.docx`, `.xlsx`
- Optional legacy conversion for `.doc` and `.xls` via Word/Excel-COM or LibreOffice
- Optional OCR for image-based PDFs (Tesseract + `pypdfium2`)
- Manual invoice amount column plus DATEV export for selected invoices
- Hash-based duplicate detection across local archive folders
- Secure credential storage via `keyring`

## Quick Start

### Windows

1. Run `start.bat`
2. Add a mail account
3. Configure a profile or shop template
4. Set date range and target folder
5. Click "Fetch Invoices"

### Manual

```bash
pip install -r requirements.txt
python UniversalInvoiceMail.py
```

## Typical Workflow

1. Add an IMAP or Gmail API account
2. Configure a search profile with filters and target folder
3. Optionally enable OCR and PDF mode
4. Start a scan
5. Enter invoice amounts for entries that should flow into accounting
6. Review results in the local invoice archive or export them as DATEV CSV

## Local Data

Runtime data is stored in `%USERPROFILE%\.universal_invoice_mail\`:

```text
%USERPROFILE%\.universal_invoice_mail\
├── config.json
├── invoices.json
├── credentials.json
└── token.json
```

Archived files are written to `%USERPROFILE%\Documents\Rechnungen\` by default.

## Optional Components

- Gmail API: `google-api-python-client`, `google-auth`, `google-auth-oauthlib`
- OCR: `pytesseract`, `pypdfium2`, `pypdf`, Tesseract OCR
- Legacy Office: `pywin32` or a local LibreOffice with `soffice.exe`
- DATEV export uses the bundled `datev_exporter.py` and writes cp1252 CSV files

When no OCR or Office backend is available, unsupported steps are logged and skipped; the run remains robust.

## Accounting Export

- The invoice table exposes an editable amount column in EUR.
- `DATEV exportieren` creates DATEV booking batches from the selected invoices.
- `berater_nr` and `mandant_nr` are configurable in the export dialog.
- Invoices without an entered amount are skipped deliberately and called out after export.

## Tests

```bash
PYTHONIOENCODING=utf-8 python -m pytest -q
```

The repository currently has 53 mocked tests for helper functions, IMAP/Gmail workflows, DATEV-adjacent behavior and compact UI control accessibility.

## Privacy

- Credentials and Gmail OAuth tokens are stored under `%USERPROFILE%\.universal_invoice_mail\`, not in the repository.
- `.gitignore` excludes `credentials.json`, `client_secret*.json`, `token.json`, local databases, sample output folders, and portable OCR bundles.
- Real invoices, attachments, and generated release artifacts should remain local.

## Related Tools

Part of the [doc-bricks](https://github.com/doc-bricks) mail suite:

| Tool | Description |
|------|-------------|
| [MailProcessor](https://github.com/doc-bricks/MailProcessor) | System tray launcher for all Universal Mail Tools |
| [UniversalMailCleaner](https://github.com/doc-bricks/UniversalMailCleaner) | Rule-based IMAP mailbox cleaner with safe mode |
| [UniversalDocsGrabber](https://github.com/doc-bricks/UniversalDocsGrabber) | Download documents and attachments from IMAP mail |

## License

[MIT](LICENSE)
