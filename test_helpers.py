#!/usr/bin/env python3
"""Unit-Tests fuer UniversalInvoiceMail Helper-Funktionen."""

import sys
import os
import io
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

# PyQt6 und optionale Abhaengigkeiten mocken fuer headless Test
for mod in ['PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtCore', 'PyQt6.QtGui',
            'xhtml2pdf', 'xhtml2pdf.pisa', 'pytesseract', 'pypdfium2',
            'pypdf', 'PIL', 'PIL.Image', 'selenium', 'selenium.webdriver',
            'selenium.webdriver.edge.options', 'selenium.webdriver.edge.service',
            'selenium.webdriver.chrome.options', 'selenium.webdriver.chrome.service',
            'webdriver_manager', 'webdriver_manager.microsoft', 'webdriver_manager.chrome',
            'googleapiclient', 'googleapiclient.discovery',
            'google_auth_oauthlib', 'google_auth_oauthlib.flow',
            'google.auth', 'google.auth.transport', 'google.auth.transport.requests',
            'google.oauth2', 'google.oauth2.credentials',
            'google.auth.exceptions', 'keyring',
            'reportlab', 'reportlab.pdfgen', 'reportlab.lib',
            'reportlab.lib.pagesizes', 'reportlab.lib.units', 'reportlab.lib.utils',
            'docx2pdf', 'win32com', 'win32com.client', 'pythoncom']:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

# Spezielle Mocks fuer Konstanten die beim Import gebraucht werden
sys.modules['PyQt6.QtCore'].Qt = MagicMock()
sys.modules['PyQt6.QtCore'].QThread = MagicMock()
sys.modules['PyQt6.QtCore'].Signal = MagicMock(return_value=MagicMock())
sys.modules['PyQt6.QtCore'].QUrl = MagicMock()
sys.modules['PyQt6.QtCore'].QSize = MagicMock()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
from UniversalInvoiceMail import (
    sanitize_filename,
    format_imap_date,
    safe_b64decode,
    calculate_hash,
    calculate_file_hash,
    convert_attachment_to_pdf,
    decode_mail_header,
    get_attachment_conversion_type,
    MailAccount,
    InvoiceProfile,
    Invoice,
)


class TestSanitizeFilename(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(sanitize_filename("invoice.pdf"), "invoice.pdf")

    def test_special_chars(self):
        result = sanitize_filename('Rechnung<>:"/\\|?*.pdf')
        self.assertNotIn("<", result)
        self.assertNotIn(">", result)
        self.assertNotIn(":", result)
        self.assertTrue(result.endswith(".pdf"))

    def test_spaces(self):
        result = sanitize_filename("my   file   name.pdf")
        self.assertNotIn("  ", result)

    def test_empty(self):
        self.assertEqual(sanitize_filename(""), "unnamed")
        self.assertEqual(sanitize_filename(None), "unnamed")

    def test_max_length(self):
        long_name = "x" * 200 + ".pdf"
        result = sanitize_filename(long_name)
        self.assertLessEqual(len(result), 120)


class TestFormatImapDate(unittest.TestCase):

    def test_basic(self):
        dt = datetime(2026, 3, 8)
        self.assertEqual(format_imap_date(dt), "08-Mar-2026")

    def test_january(self):
        dt = datetime(2026, 1, 1)
        self.assertEqual(format_imap_date(dt), "01-Jan-2026")

    def test_december(self):
        dt = datetime(2025, 12, 31)
        self.assertEqual(format_imap_date(dt), "31-Dec-2025")

    def test_english_month_names(self):
        """Stellt sicher dass Monatsnamen IMMER englisch sind (nicht locale-abhaengig)."""
        for month in range(1, 13):
            result = format_imap_date(datetime(2026, month, 15))
            month_part = result.split("-")[1]
            self.assertIn(month_part, ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])


class TestSafeB64Decode(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(safe_b64decode(""), b"")
        self.assertEqual(safe_b64decode(None), b"")

    def test_valid(self):
        import base64
        original = b"Hello World"
        encoded = base64.urlsafe_b64encode(original).decode()
        self.assertEqual(safe_b64decode(encoded), original)

    def test_missing_padding(self):
        import base64
        original = b"Test Data"
        encoded = base64.urlsafe_b64encode(original).decode().rstrip("=")
        self.assertEqual(safe_b64decode(encoded), original)

    def test_whitespace_in_base64(self):
        import base64
        original = b"Test"
        encoded = base64.urlsafe_b64encode(original).decode()
        # Simuliere Newlines wie in E-Mails
        encoded_with_newlines = encoded[:2] + "\n" + encoded[2:]
        self.assertEqual(safe_b64decode(encoded_with_newlines), original)


class TestCalculateHash(unittest.TestCase):

    def test_basic(self):
        result = calculate_hash(b"test")
        self.assertEqual(len(result), 64)

    def test_deterministic(self):
        self.assertEqual(calculate_hash(b"abc"), calculate_hash(b"abc"))

    def test_different_input(self):
        self.assertNotEqual(calculate_hash(b"abc"), calculate_hash(b"def"))


class TestCalculateFileHash(unittest.TestCase):

    def test_existing_file(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"test content for hashing")
            path = f.name
        try:
            result = calculate_file_hash(path)
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 64)
        finally:
            os.unlink(path)

    def test_nonexistent(self):
        self.assertIsNone(calculate_file_hash("/nonexistent/path.txt"))

    def test_deterministic(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"deterministic content")
            path = f.name
        try:
            self.assertEqual(calculate_file_hash(path), calculate_file_hash(path))
        finally:
            os.unlink(path)


class TestDecodeMailHeader(unittest.TestCase):

    def test_plain_text(self):
        self.assertEqual(decode_mail_header("Hello"), "Hello")

    def test_empty(self):
        self.assertEqual(decode_mail_header(""), "")
        self.assertEqual(decode_mail_header(None), "")


class TestMailAccount(unittest.TestCase):

    def test_roundtrip(self):
        acc = MailAccount(id="test1", name="Test", provider="IMAP",
                          host="imap.test.com", port=993, username="user@test.com")
        d = acc.to_dict()
        acc2 = MailAccount.from_dict(d)
        self.assertEqual(acc.id, acc2.id)
        self.assertEqual(acc.host, acc2.host)

    def test_defaults(self):
        acc = MailAccount(id="x", name="X", provider="IMAP")
        self.assertEqual(acc.port, 993)
        self.assertFalse(acc.use_gmail_api)


class TestInvoiceProfile(unittest.TestCase):

    def test_roundtrip(self):
        p = InvoiceProfile(id="p1", name="Amazon", account_id="a1",
                           sender_filter="amazon", subject_filter="Rechnung")
        d = p.to_dict()
        p2 = InvoiceProfile.from_dict(d)
        self.assertEqual(p.name, p2.name)
        self.assertEqual(p.sender_filter, p2.sender_filter)


class TestAttachmentConversion(unittest.TestCase):

    def test_attachment_type_detection(self):
        self.assertEqual(get_attachment_conversion_type("invoice.pdf"), "pdf")
        self.assertEqual(get_attachment_conversion_type("scan.PNG"), "image")
        self.assertEqual(get_attachment_conversion_type("report.docx"), "docx")
        self.assertEqual(get_attachment_conversion_type("table.xlsx"), "xlsx")
        self.assertEqual(get_attachment_conversion_type("legacy.xls"), "legacy_office")
        self.assertIsNone(get_attachment_conversion_type("archive.zip"))

    def test_convert_xlsx_attachment_uses_html_pipeline(self):
        try:
            from openpyxl import Workbook
        except ImportError:
            self.skipTest("openpyxl nicht installiert")

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Rechnungen"
        sheet.append(["Bestellung", "Betrag"])
        sheet.append(["A-100", 19.99])

        buffer = io.BytesIO()
        workbook.save(buffer)
        workbook.close()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "attachment.pdf"

            def fake_html_to_pdf(html_content, output_pdf, mail_meta, mode="fast"):
                self.assertIn("Bestellung", html_content)
                self.assertIn("A-100", html_content)
                output_pdf.write_bytes(b"%PDF-1.4 xlsx")
                return True

            with patch("UniversalInvoiceMail.html_to_pdf", side_effect=fake_html_to_pdf) as mocked_pdf:
                success, message = convert_attachment_to_pdf(
                    buffer.getvalue(), "rechnung.xlsx", output_path
                )

            self.assertTrue(success)
            self.assertIn("XLSX", message)
            self.assertTrue(output_path.exists())
            mocked_pdf.assert_called_once()

    def test_legacy_attachment_uses_com_converter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "attachment.pdf"

            def fake_convert(source_path, temp_output):
                self.assertEqual(source_path.suffix, ".xls")
                temp_output.write_bytes(b"%PDF-1.4 legacy-com")
                return "Excel COM"

            with patch("UniversalInvoiceMail.convert_legacy_office_via_com", side_effect=fake_convert) as mocked_com:
                with patch("UniversalInvoiceMail.convert_legacy_office_via_libreoffice") as mocked_libreoffice:
                    success, message = convert_attachment_to_pdf(
                        b"legacy-data", "altbestand.xls", output_path
                    )

            self.assertTrue(success)
            self.assertIn("Excel COM", message)
            self.assertTrue(output_path.exists())
            mocked_com.assert_called_once()
            mocked_libreoffice.assert_not_called()

    def test_legacy_attachment_falls_back_to_libreoffice(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "attachment.pdf"

            def fake_libreoffice(source_path, temp_output):
                self.assertEqual(source_path.suffix, ".doc")
                temp_output.write_bytes(b"%PDF-1.4 legacy-libreoffice")
                return "LibreOffice"

            with patch(
                "UniversalInvoiceMail.convert_legacy_office_via_com",
                side_effect=RuntimeError("Word/Excel nicht installiert"),
            ) as mocked_com:
                with patch(
                    "UniversalInvoiceMail.convert_legacy_office_via_libreoffice",
                    side_effect=fake_libreoffice,
                ) as mocked_libreoffice:
                    success, message = convert_attachment_to_pdf(
                        b"legacy-data", "altbestand.doc", output_path
                    )

            self.assertTrue(success)
            self.assertIn("LibreOffice", message)
            self.assertTrue(output_path.exists())
            mocked_com.assert_called_once()
            mocked_libreoffice.assert_called_once()

    def test_legacy_attachment_reports_missing_converters(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "attachment.pdf"

            with patch(
                "UniversalInvoiceMail.convert_legacy_office_via_com",
                side_effect=RuntimeError("COM nicht verfügbar"),
            ):
                with patch(
                    "UniversalInvoiceMail.convert_legacy_office_via_libreoffice",
                    side_effect=RuntimeError("LibreOffice nicht gefunden"),
                ):
                    success, message = convert_attachment_to_pdf(
                        b"legacy-data",
                        "altbestand.xls",
                        output_path,
                    )

        self.assertFalse(success)
        self.assertIn("Legacy-Format", message)
        self.assertIn("konnte nicht konvertiert werden", message)


if __name__ == "__main__":
    unittest.main()
