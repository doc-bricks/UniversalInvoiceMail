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
    """Compact buttons keep a screenreader-friendly name, description, and tooltip."""
    monkeypatch.setattr(uim, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(uim, "INVOICES_DB", tmp_path / "invoices.json")

    window = uim.MainWindow()
    try:
        expected = {
            "add_profile_button": (
                "Neues Suchprofil anlegen",
                "Öffnet den Dialog zum Anlegen eines neuen Suchprofils für Rechnungen.",
                "Neues Suchprofil anlegen",
            ),
            "delete_profile_button": (
                "Ausgewähltes Suchprofil löschen",
                "",
                "Ausgewähltes Suchprofil löschen",
            ),
            "add_account_button": (
                "Neues E-Mail-Konto anlegen",
                "Öffnet den Dialog zum Hinzufügen eines weiteren E-Mail-Kontos.",
                "Neues E-Mail-Konto anlegen",
            ),
            "delete_account_button": (
                "Ausgewähltes E-Mail-Konto löschen",
                "",
                "Ausgewähltes E-Mail-Konto löschen",
            ),
            "delete_selected_invoices_button": (
                "Ausgewählte Rechnungen und Dateien löschen",
                "",
                "Ausgewählte Einträge und Dateien löschen",
            ),
            "browse_download_path_button": (
                "Speicherordner auswählen",
                "Öffnet die Ordnerauswahl für den lokalen Rechnungs-Speicherort.",
                "Speicherordner auswählen",
            ),
        }

        for object_name, (accessible_name, accessible_description, tooltip) in expected.items():
            button = window.findChild(QPushButton, object_name)
            assert button is not None, object_name
            assert button.accessibleName() == accessible_name
            assert button.accessibleDescription() == accessible_description
            assert button.toolTip() == tooltip
    finally:
        window.close()


def test_invoice_action_buttons_expose_context(tmp_path, monkeypatch, qapp):
    """Short action labels in the invoice toolbar keep clear accessible context."""
    monkeypatch.setattr(uim, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(uim, "INVOICES_DB", tmp_path / "invoices.json")

    window = uim.MainWindow()
    try:
        expected = {
            "select_all_invoices_button": (
                "Alle sichtbaren Rechnungen auswählen",
                "Markiert alle sichtbaren Rechnungen für Export- oder Löschaktionen.",
                "Alle Einträge auswählen",
            ),
            "clear_invoice_selection_button": (
                "Rechnungsauswahl aufheben",
                "Entfernt alle Markierungen in der Rechnungstabelle.",
                "Auswahl aufheben",
            ),
            "open_invoice_folder_button": (
                "Speicherordner für Rechnungen öffnen",
                "Öffnet den aktuellen Rechnungsordner im Dateimanager.",
                "Speicherordner im Explorer öffnen",
            ),
            "refresh_invoice_table_button": (
                "Rechnungsliste aktualisieren",
                "Synchronisiert die Tabelle mit dem Dateisystem und importiert neue Dateien.",
                "Rechnungstabelle mit Ordnerinhalt synchronisieren",
            ),
            "export_invoices_csv_button": (
                "Rechnungsliste als CSV exportieren",
                "Exportiert die aktuelle Rechnungsliste als Tabellen-Datei.",
                "Rechnungsliste als CSV exportieren (filterbar in Excel)",
            ),
            "export_invoice_bundle_button": (
                "Redigiertes Rechnungs-Bundle exportieren",
                "Exportiert ausgewählte oder alle Rechnungen für Companion- oder Prüf-Workflows.",
                "Redigiertes Rechnungs-Bundle für Companion oder Prüfung exportieren",
            ),
            "import_invoice_bundle_button": (
                "Companion-Bundle importieren",
                "Übernimmt Betrag, Prüfflag und Notizen aus einem redigierten Rechnungs-Bundle.",
                "Companion-Änderungen für Betrag, Prüfflag und Notiz reimportieren",
            ),
            "export_datev_button": (
                "DATEV-Buchungsstapel exportieren",
                "Exportiert markierte Rechnungen als DATEV-Buchungsstapel für die Buchhaltung.",
                "Ausgewählte Rechnungen als DATEV-Buchungsstapel exportieren",
            ),
        }

        for object_name, (accessible_name, accessible_description, tooltip) in expected.items():
            button = window.findChild(QPushButton, object_name)
            assert button is not None, object_name
            assert button.accessibleName() == accessible_name
            assert button.accessibleDescription() == accessible_description
            assert button.toolTip() == tooltip
    finally:
        window.close()
