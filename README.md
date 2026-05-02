# UniversalInvoiceMail

Desktop tool for downloading, converting, and archiving invoices and receipts from email accounts.

> **Deutsche Dokumentation:** [README-DE.md](README-DE.md)

![UniversalInvoiceMail Preview](README/screenshots/main.png)

## Features

- Universal IMAP for Gmail, Outlook, GMX, Web.de, T-Online, and other providers
- Optional Gmail API integration for faster and more robust Gmail runs
- Profile-based filters for sender, subject, body, and date ranges
- Downloads PDF attachments and converts other attachment types to PDF
- Supported conversions: images (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tif`, `.tiff`, `.webp`), `.docx`, `.xlsx`
- Optional legacy conversion for `.doc` and `.xls` via Word/Excel-COM or LibreOffice
- Optional OCR for image-based PDFs (Tesseract + `pypdfium2`)
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
5. Review results in the local invoice archive

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

When no OCR or Office backend is available, unsupported steps are logged and skipped; the run remains robust.

## Tests

```bash
pytest tests -v
```

Unit tests for helper functions and integration tests for IMAP and Gmail workflows with mocks.

## Privacy

- Credentials are not stored in the project folder
- Local sample outputs and portable bundles are excluded via `.gitignore`
- Release artifacts remain in `releases/` locally

## Related Tools

Part of the [doc-bricks](https://github.com/doc-bricks) mail suite:

| Tool | Description |
|------|-------------|
| [MailProcessor](https://github.com/doc-bricks/MailProcessor) | System tray launcher for all Universal Mail Tools |
| [UniversalMailCleaner](https://github.com/doc-bricks/UniversalMailCleaner) | Rule-based IMAP mailbox cleaner with safe mode |
| [UniversalDocsGrabber](https://github.com/doc-bricks/UniversalDocsGrabber) | Download documents and attachments from IMAP mail |

## License

[MIT](LICENSE)
