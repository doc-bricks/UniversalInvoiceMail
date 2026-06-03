"""Headless Linux platform smoke for UniversalInvoiceMail.

This smoke covers the planned Linux desktop path:
- PySide6 main window starts offscreen.
- IMAP login path handles missing keyring data without crashing.
- LibreOffice executable discovery honors Linux env-path overrides.
- CSV export works with a minimal local invoice set.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

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
    "docx2pdf",
    "win32com",
    "win32com.client",
    "pythoncom",
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication

import UniversalInvoiceMail as uim


def _write_test_config(config_path: Path, download_path: Path) -> None:
    payload = {
        "settings": {
            "download_path": str(download_path),
            "download_attachments": True,
            "convert_body_to_pdf": True,
            "merge_body_with_attachments": False,
            "enable_hash_check": True,
            "max_emails_per_run": 100,
            "date_filter_months": 12,
            "date_from": "",
            "date_to": "",
            "include_trash": False,
            "pdf_mode": "fast",
            "ocr_enabled": False,
        },
        "accounts": [],
        "profiles": [],
    }
    config_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _exercise_keyring_fallback() -> None:
    account = uim.MailAccount(
        id="linux-imap",
        name="Linux IMAP",
        provider="IMAP",
        host="imap.example.com",
        port=993,
        username="linux@example.com",
    )
    profile = uim.InvoiceProfile(
        id="linux-profile",
        name="Linux Shop",
        account_id=account.id,
        sender_filter="shop@example.com",
        enabled=True,
    )
    worker = uim.InvoiceWorker([account], [profile], uim.AppSettings(), set())
    messages: list[str] = []
    worker.log = MagicMock()
    worker.log.emit = lambda message: messages.append(message)

    with patch.object(uim, "KEYRING_AVAILABLE", True):
        with patch("UniversalInvoiceMail.keyring.get_password", side_effect=RuntimeError("backend missing")):
            worker._process_imap(account, [profile])

    assert any("Kein Passwort" in message for message in messages), messages


def _exercise_libreoffice_linux_path(temp_dir: Path) -> None:
    fake_soffice = temp_dir / "soffice"
    fake_soffice.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fake_soffice.chmod(0o755)

    old_soffice_path = os.environ.get("SOFFICE_PATH")
    os.environ["SOFFICE_PATH"] = str(fake_soffice)
    try:
        resolved = uim.find_libreoffice_executable()
        assert resolved == fake_soffice, resolved

        output_path = temp_dir / "legacy.pdf"

        def _fake_libreoffice(_source_path: Path, target_path: Path) -> str:
            target_path.write_bytes(b"%PDF-1.4\nlinux smoke\n")
            return "LibreOffice"

        with patch.object(uim, "convert_legacy_office_via_libreoffice", side_effect=_fake_libreoffice):
            success, message = uim.convert_legacy_office_attachment(
                b"legacy",
                "rechnung.doc",
                output_path,
            )

        assert success, message
        assert output_path.exists(), output_path
        assert "LibreOffice" in message, message
    finally:
        if old_soffice_path is None:
            os.environ.pop("SOFFICE_PATH", None)
        else:
            os.environ["SOFFICE_PATH"] = old_soffice_path


def _exercise_offscreen_window_and_csv_export(temp_dir: Path) -> None:
    config_path = temp_dir / "config.json"
    invoices_db = temp_dir / "invoices.json"
    download_dir = temp_dir / "downloads"
    download_dir.mkdir(parents=True, exist_ok=True)
    _write_test_config(config_path, download_dir)
    invoices_db.write_text("[]", encoding="utf-8")

    sample_pdf = download_dir / "beleg.pdf"
    sample_pdf.write_bytes(b"%PDF-1.4\nsmoke\n")

    app = QApplication.instance() or QApplication([])
    with patch.object(uim, "CONFIG_FILE", config_path):
        with patch.object(uim, "INVOICES_DB", invoices_db):
            with patch.object(uim.QMessageBox, "information", return_value=None):
                with patch.object(uim.QMessageBox, "warning", return_value=None):
                    with patch.object(uim.QMessageBox, "critical", return_value=None):
                        window = uim.MainWindow()
                        try:
                            window.show()
                            app.processEvents()

                            assert window.windowTitle().startswith("UniversalInvoiceMail"), window.windowTitle()

                            window.invoices = [
                                uim.Invoice(
                                    id="linux-1",
                                    profile_name="Linux Shop",
                                    filename=sample_pdf.name,
                                    date="2026-06-03",
                                    path=str(sample_pdf),
                                    sender="shop@example.com",
                                    subject="Rechnung",
                                )
                            ]
                            window.refresh_invoice_table()
                            app.processEvents()

                            assert window.invoice_table.rowCount() == 1, window.invoice_table.rowCount()

                            csv_path = temp_dir / "linux-smoke.csv"
                            with patch.object(
                                uim.QFileDialog,
                                "getSaveFileName",
                                return_value=(str(csv_path), "CSV Dateien (*.csv)"),
                            ):
                                window.export_invoices_csv()

                            assert csv_path.exists(), csv_path
                            content = csv_path.read_text(encoding="utf-8-sig")
                            assert "Linux Shop" in content, content
                            assert sample_pdf.name in content, content
                        finally:
                            window.close()
                            app.processEvents()


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="uim-linux-smoke-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        _exercise_keyring_fallback()
        _exercise_libreoffice_linux_path(temp_dir)
        _exercise_offscreen_window_and_csv_export(temp_dir)
    print("linux platform smoke passed")


if __name__ == "__main__":
    main()
