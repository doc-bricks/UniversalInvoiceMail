"""GUI accessibility checks for compact symbol-only controls."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

for mod in [
    "xhtml2pdf",
    "xhtml2pdf.pisa",
    "pytesseract",
    "pypdfium2",
    "pypdf",
    "PIL",
    "PIL.Image",
    "selenium",
    "selenium.webdriver",
    "selenium.webdriver.edge.options",
    "selenium.webdriver.edge.service",
    "selenium.webdriver.chrome.options",
    "selenium.webdriver.chrome.service",
    "webdriver_manager",
    "webdriver_manager.microsoft",
    "webdriver_manager.chrome",
    "googleapiclient",
    "googleapiclient.discovery",
    "google_auth_oauthlib",
    "google_auth_oauthlib.flow",
    "google.auth",
    "google.auth.transport",
    "google.auth.transport.requests",
    "google.oauth2",
    "google.oauth2.credentials",
    "google.auth.exceptions",
    "keyring",
    "reportlab",
    "reportlab.pdfgen",
    "reportlab.lib",
    "reportlab.lib.pagesizes",
    "reportlab.lib.units",
    "reportlab.lib.utils",
    "docx2pdf",
    "win32com",
    "win32com.client",
    "pythoncom",
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

import pytest
from PySide6.QtWidgets import QApplication, QPushButton

sys.path.insert(0, str(Path(__file__).parent.parent))

import UniversalInvoiceMail as uim


@pytest.fixture(scope="module")
def qapp():
    qt_app = QApplication.instance()
    if qt_app is None:
        qt_app = QApplication([])
    return qt_app


def test_start_grabbing_does_not_wipe_sync_log(tmp_path, monkeypatch, qapp):
    """Sync messages before the worker must not be cleared by a second log_output.clear()."""
    monkeypatch.setattr(uim, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(uim, "INVOICES_DB", tmp_path / "invoices.json")

    window = uim.MainWindow()
    try:
        acc = uim.MailAccount(
            id="a1", name="Test", provider="IMAP",
            host="imap.example.com", port=993,
            username="test@example.com",
        )
        window.accounts.append(acc)
        prof = uim.InvoiceProfile(id="p1", name="TestShop", account_id="a1",
                                  sender_filter="shop@example.com", enabled=True)
        window.profiles.append(prof)

        clear_calls = []
        original_clear = window.log_output.clear
        def tracking_clear():
            clear_calls.append(1)
            original_clear()
        window.log_output.clear = tracking_clear

        class _FakeWorker:
            log = MagicMock()
            progress = MagicMock()
            invoice_found = MagicMock()
            finished_signal = MagicMock()
            def start(self): pass
            def isRunning(self): return False
            def stop(self): pass

        monkeypatch.setattr(uim, "InvoiceWorker", lambda *a, **kw: _FakeWorker())

        window.start_grabbing()

        assert len(clear_calls) == 1, (
            f"log_output.clear() called {len(clear_calls)} times — expected exactly 1 "
            "(sync messages must not be wiped before worker output)"
        )
    finally:
        window.close()


def test_account_dialog_restores_use_gmail_api_false_on_edit(qapp):
    """AccountDialog must not force use_gmail_api=True when editing a Gmail account with it off.

    Regression: on_provider_changed("Gmail") sets ck_gmail_api=True, overriding the loaded
    account value. Fix: ck_gmail_api is re-applied after provider detection.
    """
    account = uim.MailAccount(
        id="a1", name="MyGmail", provider="Gmail",
        host="imap.gmail.com", port=993,
        username="test@gmail.com",
        use_gmail_api=False,
    )
    dialog = uim.AccountDialog(account=account)
    try:
        assert not dialog.ck_gmail_api.isChecked(), (
            "AccountDialog must respect use_gmail_api=False when editing a Gmail account; "
            "on_provider_changed must not override it"
        )
    finally:
        dialog.close()


def test_symbol_buttons_expose_accessible_context(tmp_path, monkeypatch, qapp):
    """Compact icon buttons keep a screenreader-friendly name and tooltip."""
    monkeypatch.setattr(uim, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(uim, "INVOICES_DB", tmp_path / "invoices.json")

    window = uim.MainWindow()
    try:
        expected = {
            "delete_profile_button": (
                "Ausgewähltes Suchprofil löschen",
                "Ausgewähltes Suchprofil löschen",
            ),
            "delete_account_button": (
                "Ausgewähltes E-Mail-Konto löschen",
                "Ausgewähltes E-Mail-Konto löschen",
            ),
            "delete_selected_invoices_button": (
                "Ausgewählte Rechnungen und Dateien löschen",
                "Ausgewählte Einträge und Dateien löschen",
            ),
            "browse_download_path_button": (
                "Speicherordner auswählen",
                "Speicherordner auswählen",
            ),
        }

        for object_name, (accessible_name, tooltip) in expected.items():
            button = window.findChild(QPushButton, object_name)
            assert button is not None, object_name
            assert button.accessibleName() == accessible_name
            assert button.toolTip() == tooltip
    finally:
        window.close()
