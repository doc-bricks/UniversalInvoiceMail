"""Integration tests for UniversalInvoiceMail IMAP and Gmail API flows.

Uses unittest.mock to avoid real IMAP/Gmail API connections.
Run with: python -m pytest tests/test_integration.py
"""

import sys
import os
import base64
import email
import hashlib
import unittest
from email.message import EmailMessage
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
from dataclasses import dataclass

# Add project root to sys.path so we can import UniversalInvoiceMail
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock PyQt6 before importing to allow headless execution
_qt_mock = MagicMock()
sys.modules['PyQt6'] = _qt_mock
sys.modules['PyQt6.QtWidgets'] = _qt_mock
sys.modules['PyQt6.QtCore'] = _qt_mock
sys.modules['PyQt6.QtGui'] = _qt_mock

import importlib
import types

# Mock optional dependencies that might not be installed
for mod in ['xhtml2pdf', 'xhtml2pdf.pisa', 'pytesseract', 'pypdfium2',
            'pypdf', 'PIL', 'PIL.Image', 'selenium', 'webdriver_manager',
            'webdriver_manager.microsoft', 'webdriver_manager.chrome',
            'googleapiclient', 'googleapiclient.discovery',
            'google_auth_oauthlib', 'google_auth_oauthlib.flow',
            'google.auth', 'google.auth.transport', 'google.auth.transport.requests',
            'google.auth.exceptions', 'google.oauth2', 'google.oauth2.credentials',
            'keyring']:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

import UniversalInvoiceMail as uim


class TestImapConnect(unittest.TestCase):
    """Tests for IMAP connection and authentication flow."""

    def _make_account(self, use_gmail_api=False):
        return uim.MailAccount(
            id="acc1",
            name="Test Account",
            provider="IMAP",
            host="imap.example.com",
            port=993,
            username="user@example.com",
            use_gmail_api=use_gmail_api,
        )

    def _make_profile(self):
        return uim.InvoiceProfile(
            id="prof1",
            name="TestShop",
            account_id="acc1",
            sender_filter="shop@example.com",
            subject_filter="Rechnung",
            enabled=True,
        )

    def _make_settings(self, tmp_path=None):
        s = uim.AppSettings()
        if tmp_path:
            s.download_path = str(tmp_path)
        return s

    def test_imap_connect_success(self):
        """IMAP connection succeeds with valid credentials."""
        account = self._make_account()
        profile = self._make_profile()
        settings = self._make_settings()
        worker = uim.InvoiceWorker([account], [profile], settings, set())

        mock_mail = MagicMock()
        mock_mail.list.return_value = (None, [b'(\\HasNoChildren) "/" INBOX'])

        with patch('imaplib.IMAP4_SSL', return_value=mock_mail):
            with patch('UniversalInvoiceMail.KEYRING_AVAILABLE', True):
                with patch('keyring.get_password', return_value='secret'):
                    mock_mail.search.return_value = (None, [b''])
                    worker._process_imap(account, [profile])

        mock_mail.login.assert_called_once_with('user@example.com', 'secret')

    def test_imap_connect_no_password(self):
        """IMAP connection aborts when no password is stored."""
        account = self._make_account()
        profile = self._make_profile()
        settings = self._make_settings()
        worker = uim.InvoiceWorker([account], [profile], settings, set())
        log_messages = []
        worker.log = MagicMock()
        worker.log.emit = lambda msg: log_messages.append(msg)

        with patch('UniversalInvoiceMail.KEYRING_AVAILABLE', True):
            with patch('keyring.get_password', return_value=None):
                worker._process_imap(account, [profile])

        self.assertTrue(any("Kein Passwort" in m for m in log_messages))

    def test_imap_connect_auth_error(self):
        """IMAP connection handles authentication error gracefully."""
        import imaplib
        account = self._make_account()
        profile = self._make_profile()
        settings = self._make_settings()
        worker = uim.InvoiceWorker([account], [profile], settings, set())
        log_messages = []
        worker.log = MagicMock()
        worker.log.emit = lambda msg: log_messages.append(msg)

        mock_mail = MagicMock()
        mock_mail.login.side_effect = imaplib.IMAP4.error("LOGIN failed")

        with patch('imaplib.IMAP4_SSL', return_value=mock_mail):
            with patch('UniversalInvoiceMail.KEYRING_AVAILABLE', True):
                with patch('keyring.get_password', return_value='wrongpwd'):
                    worker._process_imap(account, [profile])

        self.assertTrue(any("IMAP Fehler" in m for m in log_messages))


class TestGmailAuth(unittest.TestCase):
    """Tests for Gmail API authentication flow."""

    def test_gmail_auth_missing_credentials_file(self):
        """Gmail auth aborts when credentials.json is absent and cannot be found."""
        account = uim.MailAccount(
            id="acc2", name="Gmail", provider="Gmail API",
            use_gmail_api=True
        )
        profile = uim.InvoiceProfile(
            id="p2", name="Amazon", account_id="acc2", enabled=True
        )
        settings = uim.AppSettings()
        worker = uim.InvoiceWorker([account], [profile], settings, set())
        log_messages = []
        worker.log = MagicMock()
        worker.log.emit = lambda msg: log_messages.append(msg)

        with patch('UniversalInvoiceMail.GMAIL_API_AVAILABLE', True):
            with patch.object(Path, 'exists', return_value=False):
                creds = worker._get_gmail_credentials()

        self.assertIsNone(creds)

    def test_gmail_api_unavailable(self):
        """_process_gmail_api logs an error when Gmail API is not installed."""
        account = uim.MailAccount(
            id="acc3", name="Gmail2", provider="Gmail API", use_gmail_api=True
        )
        profile = uim.InvoiceProfile(
            id="p3", name="Google", account_id="acc3", enabled=True
        )
        settings = uim.AppSettings()
        worker = uim.InvoiceWorker([account], [profile], settings, set())
        log_messages = []
        worker.log = MagicMock()
        worker.log.emit = lambda msg: log_messages.append(msg)

        with patch('UniversalInvoiceMail.GMAIL_API_AVAILABLE', False):
            worker._process_gmail_api(account, [profile])

        self.assertTrue(any("nicht verfügbar" in m or "nicht verf" in m
                            for m in log_messages))


class TestDownloadAttachment(unittest.TestCase):
    """Tests for attachment detection and download."""

    def test_filter_messages_blacklist(self):
        """Messages matching the blacklist are rejected by _check_message_filters."""
        account = uim.MailAccount(id="a", name="A", provider="IMAP")
        profile = uim.InvoiceProfile(
            id="p", name="Shop", account_id="a",
            blacklist="newsletter,werbung",
            enabled=True,
        )
        settings = uim.AppSettings()
        worker = uim.InvoiceWorker([account], [profile], settings, set())
        worker.log = MagicMock()
        worker.log.emit = MagicMock()

        # Message with blacklisted word in subject
        result = worker._check_message_filters(profile, "Dein Newsletter", "")
        self.assertFalse(result)

        # Message with blacklisted word in body
        result = worker._check_message_filters(profile, "Rechnung", "tolle werbung hier")
        self.assertFalse(result)

    def test_filter_messages_passes(self):
        """Messages with no blacklist match pass _check_message_filters."""
        account = uim.MailAccount(id="a", name="A", provider="IMAP")
        profile = uim.InvoiceProfile(
            id="p", name="Shop", account_id="a",
            blacklist="newsletter",
            body_must_contain="rechnung",
            enabled=True,
        )
        settings = uim.AppSettings()
        worker = uim.InvoiceWorker([account], [profile], settings, set())
        worker.log = MagicMock()
        worker.log.emit = MagicMock()

        result = worker._check_message_filters(
            profile, "Ihre Rechnung bei Shop", "ihre rechnung ist beigefuegt"
        )
        self.assertTrue(result)

    def test_filter_messages_body_must_contain_fails(self):
        """Messages missing required body terms are rejected."""
        account = uim.MailAccount(id="a", name="A", provider="IMAP")
        profile = uim.InvoiceProfile(
            id="p", name="Shop", account_id="a",
            body_must_contain="rechnung,invoice",
            enabled=True,
        )
        settings = uim.AppSettings()
        worker = uim.InvoiceWorker([account], [profile], settings, set())
        worker.log = MagicMock()
        worker.log.emit = MagicMock()

        result = worker._check_message_filters(
            profile, "Hallo, toller Inhalt", "keine relevanten inhalte hier"
        )
        self.assertFalse(result)

    def test_compute_target_dir(self, tmp_path=None):
        """_compute_target_dir creates the expected subdirectory."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            account = uim.MailAccount(id="a", name="A", provider="IMAP")
            profile = uim.InvoiceProfile(
                id="p", name="TestShop", account_id="a", enabled=True
            )
            settings = uim.AppSettings()
            settings.download_path = tmp
            worker = uim.InvoiceWorker([account], [profile], settings, set())

            target = worker._compute_target_dir(profile)
            self.assertTrue(target.exists())
            self.assertTrue(target.name.startswith("TestShop"))

    def test_compute_target_dir_with_subfolder(self):
        """_compute_target_dir uses target_subfolder when specified."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            account = uim.MailAccount(id="a", name="A", provider="IMAP")
            profile = uim.InvoiceProfile(
                id="p", name="Shop", account_id="a",
                target_subfolder="Rechnungen2024",
                enabled=True,
            )
            settings = uim.AppSettings()
            settings.download_path = tmp
            worker = uim.InvoiceWorker([account], [profile], settings, set())

            target = worker._compute_target_dir(profile)
            self.assertTrue(target.exists())
            self.assertIn("Rechnungen2024", str(target))

    def test_imap_png_attachment_is_converted_and_emitted(self):
        """IMAP processing accepts supported non-PDF attachments via the shared converter."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            account = uim.MailAccount(id="a", name="A", provider="IMAP")
            profile = uim.InvoiceProfile(
                id="p", name="TestShop", account_id="a",
                subject_filter="Rechnung",
                enabled=True,
            )
            settings = uim.AppSettings()
            settings.download_path = tmp
            worker = uim.InvoiceWorker([account], [profile], settings, set())
            worker.log = MagicMock()
            worker.log.emit = MagicMock()
            worker.invoice_found = MagicMock()
            worker.invoice_found.emit = MagicMock()

            message = EmailMessage()
            message["From"] = "shop@example.com"
            message["Subject"] = "Ihre Rechnung"
            message["Date"] = "Mon, 01 Apr 2026 10:00:00 +0000"
            message.set_content("Im Anhang befindet sich die Rechnung.")
            message.add_attachment(
                b"fake-png",
                maintype="image",
                subtype="png",
                filename="rechnung.png",
            )

            def fake_convert(file_data, source_name, output_path):
                self.assertEqual(file_data, b"fake-png")
                self.assertEqual(source_name, "rechnung.png")
                output_path.write_bytes(b"%PDF-1.4 fake")
                return True, "Bild-Anhang konvertiert"

            with patch("UniversalInvoiceMail.convert_attachment_to_pdf", side_effect=fake_convert) as mocked_convert:
                worker._process_imap_message(message, profile)

            mocked_convert.assert_called_once()
            worker.invoice_found.emit.assert_called_once()
            invoice = worker.invoice_found.emit.call_args.args[0]
            self.assertTrue(invoice.filename.endswith(".pdf"))
            self.assertTrue(Path(invoice.path).exists())

    def test_gmail_png_attachment_is_converted_and_emitted(self):
        """Gmail payload processing accepts supported non-PDF attachments."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            account = uim.MailAccount(id="a", name="A", provider="Gmail API", use_gmail_api=True)
            profile = uim.InvoiceProfile(
                id="p", name="TestShop", account_id="a",
                enabled=True,
            )
            settings = uim.AppSettings()
            settings.download_path = tmp
            worker = uim.InvoiceWorker([account], [profile], settings, set())
            worker.log = MagicMock()
            worker.log.emit = MagicMock()
            worker.invoice_found = MagicMock()
            worker.invoice_found.emit = MagicMock()

            attachment_bytes = b"gmail-image"
            encoded_attachment = base64.urlsafe_b64encode(attachment_bytes).decode().rstrip("=")
            gmail_message = {
                "id": "msg-123",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "shop@example.com"},
                        {"name": "Subject", "value": "Ihre Rechnung"},
                        {"name": "Date", "value": "Mon, 01 Apr 2026 10:00:00 +0000"},
                    ],
                    "parts": [
                        {
                            "filename": "rechnung.png",
                            "mimeType": "image/png",
                            "body": {"data": encoded_attachment},
                        }
                    ],
                },
            }

            def fake_convert(file_data, source_name, output_path):
                self.assertEqual(file_data, attachment_bytes)
                self.assertEqual(source_name, "rechnung.png")
                output_path.write_bytes(b"%PDF-1.4 fake")
                return True, "Bild-Anhang konvertiert"

            with patch("UniversalInvoiceMail.convert_attachment_to_pdf", side_effect=fake_convert) as mocked_convert:
                worker._process_gmail_message(MagicMock(), gmail_message, profile)

            mocked_convert.assert_called_once()
            worker.invoice_found.emit.assert_called_once()
            invoice = worker.invoice_found.emit.call_args.args[0]
            self.assertTrue(invoice.filename.endswith(".pdf"))
            self.assertTrue(Path(invoice.path).exists())


if __name__ == "__main__":
    unittest.main()
