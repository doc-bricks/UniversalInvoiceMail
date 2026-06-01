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
