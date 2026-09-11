"""Regression tests for local EML/MSG conversion, charset resilience, attachment extraction,
and folder scanning in UniversalInvoiceMail.
"""

from __future__ import annotations

from email.message import EmailMessage
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import UniversalInvoiceMail as uim


class MockMainWindowForEML:
    """Minimal harness representing MainWindow for testing conversion methods."""

    def __init__(self, download_path: Path):
        self.settings = uim.AppSettings()
        self.settings.download_path = str(download_path)
        self.settings.download_attachments = True
        self.settings.merge_body_with_attachments = False
        self.log_output = None  # Crucial test: None should NOT cause AttributeError
        self.invoices = []
        self.profiles = [
            uim.InvoiceProfile(
                id="prof-1",
                name="Invoices",
                account_id="acc-1",
                target_subfolder="",
                enabled=True,
            )
        ]

    _log = uim.MainWindow._log
    _convert_eml_to_pdf = uim.MainWindow._convert_eml_to_pdf
    _convert_msg_to_pdf = uim.MainWindow._convert_msg_to_pdf
    scan_folders_for_new_files = uim.MainWindow.scan_folders_for_new_files
    save_invoices_db = MagicMock()


class TestEmlMsgConversionRegressions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.download_dir = Path(self.temp_dir.name)
        self.window = MockMainWindowForEML(self.download_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_convert_eml_handles_unknown_charset_resiliently(self):
        """EML with unknown charset (e.g. unknown-8bit) must not crash with LookupError."""
        raw_eml = (
            b"From: billing@example.com\r\n"
            b"To: client@example.com\r\n"
            b"Subject: Rechnung 9999\r\n"
            b"Date: Wed, 10 Sep 2026 12:00:00 +0200\r\n"
            b"Content-Type: text/html; charset=unknown-custom-charset\r\n"
            b"\r\n"
            b"<html><body><p>Rechnungssumme: 149,00 EUR</p></body></html>\r\n"
        )
        eml_file = self.download_dir / "invoice_unknown_charset.eml"
        eml_file.write_bytes(raw_eml)

        # Mock html_to_pdf to verify it receives the recovered HTML without crashing
        with patch.object(uim, "html_to_pdf", return_value=True) as mock_pdf:
            res = self.window._convert_eml_to_pdf(eml_file)
            self.assertIsNotNone(res, "Conversion should return a PDF path, not None")
            self.assertEqual(res, eml_file.with_suffix(".pdf"))
            self.assertTrue(mock_pdf.called)
            # Verify body was safely decoded with fallback
            html_arg = mock_pdf.call_args[0][0]
            self.assertIn("149,00 EUR", html_arg)

    def test_convert_eml_handles_none_or_empty_part_payload(self):
        """EML with empty/malformed parts returning None payload must not raise AttributeError."""
        raw_eml = (
            b'Content-Type: multipart/alternative; boundary="boundary42"\r\n'
            b"\r\n"
            b"--boundary42\r\n"
            b"Content-Type: text/html; charset=utf-8\r\n"
            b"Content-Transfer-Encoding: base64\r\n"
            b"\r\n"
            b"\r\n"
            b"--boundary42\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"\r\n"
            b"Fallback plain text invoice content\r\n"
            b"--boundary42--\r\n"
        )
        eml_file = self.download_dir / "invoice_empty_part.eml"
        eml_file.write_bytes(raw_eml)

        with patch.object(uim, "html_to_pdf", return_value=True) as mock_pdf:
            res = self.window._convert_eml_to_pdf(eml_file)
            self.assertIsNotNone(res)
            self.assertTrue(mock_pdf.called)
            html_arg = mock_pdf.call_args[0][0]
            self.assertIn("Fallback plain text invoice content", html_arg)

    def test_convert_eml_extracts_pdf_attachment_without_requiring_xhtml2pdf(self):
        """EML with PDF invoice attachment must extract attachment even if body converter is absent."""
        msg = EmailMessage()
        msg["From"] = "invoicing@supplier.com"
        msg["To"] = "buyer@example.com"
        msg["Subject"] = "Ihre Rechnung RE-2026-001"
        msg["Date"] = "Wed, 10 Sep 2026 10:00:00 +0200"
        msg.set_content("Hallo, anbei die Rechnung.")

        pdf_payload = b"%PDF-1.4\n%real-attachment-data\n%%EOF"
        msg.add_attachment(
            pdf_payload,
            maintype="application",
            subtype="pdf",
            filename="Invoice_RE2026.pdf",
        )

        eml_file = self.download_dir / "supplier_mail.eml"
        eml_file.write_bytes(msg.as_bytes())

        # Ensure attachment is extracted and saved
        res = self.window._convert_eml_to_pdf(eml_file)
        self.assertIsNotNone(res)
        expected_attachment = self.download_dir / "Invoice_RE2026.pdf"
        self.assertTrue(expected_attachment.exists(), "PDF attachment should be extracted to disk")
        self.assertEqual(expected_attachment.read_bytes(), pdf_payload)

    def test_convert_eml_extracts_full_multilingual_subject_metadata(self):
        """RFC-2047 encoded-word chunks in Subject must all be preserved in mail_meta."""
        raw_eml = (
            b"From: =?utf-8?B?QWNtZSBDb3Jw?= <acme@example.com>\r\n"
            b"To: client@example.com\r\n"
            b"Subject: =?utf-8?B?UmVjaG51bmc=?= =?utf-8?B?IDEyMzQ1?= =?utf-8?B?IGbDvHIgTcO8bGxlcg==?=\r\n"
            b"Date: Wed, 10 Sep 2026 12:00:00 +0200\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"\r\n"
            b"Vielen Dank fuer Ihre Zahlung.\r\n"
        )
        eml_file = self.download_dir / "invoice_multi_chunk.eml"
        eml_file.write_bytes(raw_eml)

        with patch.object(uim, "html_to_pdf", return_value=True) as mock_pdf:
            res = self.window._convert_eml_to_pdf(eml_file)
            self.assertIsNotNone(res)
            self.assertTrue(mock_pdf.called)
            mail_meta = mock_pdf.call_args[0][2]
            self.assertIn("Rechnung 12345 für Müller", mail_meta["subject"])
            self.assertIn("Acme Corp", mail_meta["sender"])

    def test_scan_folders_processes_case_insensitive_extensions(self):
        """scan_folders_for_new_files must recognize .EML and .MSG uppercase extensions."""
        folder = self.download_dir / "Invoices"
        folder.mkdir(parents=True, exist_ok=True)

        eml_file = folder / "INVOICE_UPPER.EML"
        eml_file.write_bytes(
            b"From: a@b.com\r\nSubject: Test\r\nContent-Type: text/plain\r\n\r\nHello"
        )

        with patch.object(self.window, "_convert_eml_to_pdf") as mock_convert:
            self.window.scan_folders_for_new_files()
            self.assertTrue(
                any(call_arg[0][0].name.upper() == "INVOICE_UPPER.EML" for call_arg in mock_convert.call_args_list),
                f"_convert_eml_to_pdf was not called for uppercase EML: {mock_convert.call_args_list}",
            )


if __name__ == "__main__":
    unittest.main()
