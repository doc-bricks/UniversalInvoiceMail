"""Tests for the redacted invoice bundle export/import workflow."""

import json
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
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))

import UniversalInvoiceMail as uim
from datev_exporter import DATEVConfig
from invoice_bundle import (
    ALLOWED_COMPANION_FIELDS,
    BUNDLE_SCHEMA,
    apply_invoice_bundle_changes,
    build_invoice_bundle,
)


@pytest.fixture(scope="module")
def qapp():
    qt_app = QApplication.instance()
    if qt_app is None:
        qt_app = QApplication([])
    return qt_app


def test_build_invoice_bundle_contains_redacted_data(tmp_path):
    download_root = tmp_path / "downloads"
    invoice_file = download_root / "Amazon" / "rechnung-1.pdf"
    invoice_file.parent.mkdir(parents=True)
    invoice_file.write_bytes(b"fake pdf bytes")

    account = uim.MailAccount(
        id="acc-1",
        name="Gmail Hauptkonto",
        provider="Gmail",
        username="billing@example.com",
        use_gmail_api=True,
    )
    profile = uim.InvoiceProfile(
        id="profile-amazon",
        name="Amazon",
        account_id="acc-1",
        sender_filter="@amazon.de",
        subject_filter="Rechnung, Bestellung",
        gmail_query="from:amazon has:attachment",
        target_subfolder="Rechnungen/Amazon",
    )
    invoice = uim.Invoice(
        id="inv-1",
        profile_id="profile-amazon",
        profile_name="Amazon",
        filename=invoice_file.name,
        date="2026-06-10",
        path=str(invoice_file),
        sender="billing@amazon.de",
        subject="Rechnung 12345",
        amount=19.99,
        review_status="checked",
        notes="Betrag stimmt",
    )
    datev_config = DATEVConfig(berater_nr="100000", mandant_nr="200000")

    bundle = build_invoice_bundle(
        app_name=uim.APP_NAME,
        app_version=uim.VERSION,
        accounts=[account],
        profiles=[profile],
        invoices=[invoice],
        download_path=str(download_root),
        datev_config=datev_config,
    )

    assert bundle["schema"] == BUNDLE_SCHEMA
    assert bundle["companion_changes"]["allowed_fields"] == list(ALLOWED_COMPANION_FIELDS)
    assert bundle["export_options"]["include_mail_bodies"] is False
    assert bundle["profiles"][0]["account_label"] == "Gmail Hauptkonto"
    assert bundle["profiles"][0]["target_folder_label"] == "Rechnungen/Amazon"
    assert bundle["datev"]["berater_nr"] == "100000"
    assert bundle["datev"]["mandant_nr"] == "200000"
    assert bundle["datev"]["export_encoding"] == "cp1252"

    invoice_row = bundle["invoices"][0]
    assert invoice_row["id"] == "inv-1"
    assert invoice_row["profile_id"] == "profile-amazon"
    assert invoice_row["amount"] == 19.99
    assert invoice_row["review_status"] == "checked"
    assert invoice_row["notes"] == "Betrag stimmt"
    assert Path(invoice_row["files"][0]["relative_path"]).parts[-2:] == ("Amazon", "rechnung-1.pdf")

    bundle_text = json.dumps(bundle, ensure_ascii=False)
    assert "password" not in bundle_text
    assert "token.json" not in bundle_text
    assert "credentials.json" not in bundle_text


def test_apply_invoice_bundle_changes_detects_updates_and_hash_conflicts(tmp_path):
    download_root = tmp_path / "downloads"
    download_root.mkdir()

    update_file = download_root / "update.pdf"
    update_file.write_bytes(b"update me")
    conflict_file = download_root / "conflict.pdf"
    conflict_file.write_bytes(b"old version")

    update_invoice = uim.Invoice(
        id="inv-update",
        profile_name="Amazon",
        filename=update_file.name,
        date="2026-06-10",
        path=str(update_file),
        amount=None,
    )
    conflict_invoice = uim.Invoice(
        id="inv-conflict",
        profile_name="Amazon",
        filename=conflict_file.name,
        date="2026-06-10",
        path=str(conflict_file),
        notes="Alt",
    )
    profile = uim.InvoiceProfile(id="profile-amazon", name="Amazon", account_id="acc-1")

    update_bundle = build_invoice_bundle(
        app_name=uim.APP_NAME,
        app_version=uim.VERSION,
        accounts=[],
        profiles=[profile],
        invoices=[update_invoice],
        download_path=str(download_root),
    )
    update_bundle["invoices"][0]["amount"] = "12,50"
    update_bundle["invoices"][0]["review_status"] = "ready"
    update_bundle["invoices"][0]["notes"] = "Vom Companion"
    update_bundle["invoices"][0]["subject"] = "Darf lokal nicht überschreiben"

    update_result = apply_invoice_bundle_changes([update_invoice], update_bundle)
    assert update_result["updated"] == 1
    assert update_result["conflicts"] == []
    assert update_invoice.amount == 12.5
    assert update_invoice.review_status == "ready"
    assert update_invoice.notes == "Vom Companion"
    assert update_invoice.subject == ""

    conflict_bundle = build_invoice_bundle(
        app_name=uim.APP_NAME,
        app_version=uim.VERSION,
        accounts=[],
        profiles=[profile],
        invoices=[conflict_invoice],
        download_path=str(download_root),
    )
    conflict_file.write_bytes(b"changed after export")
    conflict_bundle["invoices"][0]["notes"] = "Neu vom Companion"

    conflict_result = apply_invoice_bundle_changes([conflict_invoice], conflict_bundle)
    assert conflict_result["updated"] == 0
    assert conflict_result["conflicts"] == [{"id": "inv-conflict", "reason": "file_hash_mismatch"}]
    assert conflict_invoice.notes == "Alt"


def test_main_window_bundle_export_import_roundtrip(tmp_path, monkeypatch, qapp):
    config_path = tmp_path / "config.json"
    invoices_db = tmp_path / "invoices.json"
    monkeypatch.setattr(uim, "CONFIG_FILE", config_path)
    monkeypatch.setattr(uim, "INVOICES_DB", invoices_db)

    download_root = tmp_path / "downloads"
    invoice_file = download_root / "Amazon" / "rechnung-2.pdf"
    invoice_file.parent.mkdir(parents=True)
    invoice_file.write_bytes(b"roundtrip pdf")

    window = uim.MainWindow()
    try:
        window.settings.download_path = str(download_root)
        window.accounts = [
            uim.MailAccount(id="acc-1", name="Gmail Hauptkonto", provider="Gmail", username="billing@example.com")
        ]
        window.profiles = [
            uim.InvoiceProfile(id="profile-amazon", name="Amazon", account_id="acc-1", sender_filter="@amazon.de")
        ]
        window.invoices = [
            uim.Invoice(
                id="inv-roundtrip",
                profile_id="profile-amazon",
                profile_name="Amazon",
                filename=invoice_file.name,
                date="2026-06-10",
                path=str(invoice_file),
                sender="billing@amazon.de",
                subject="Rechnung 54321",
                amount=9.99,
            )
        ]
        window.refresh_invoice_table()

        export_path = tmp_path / "bundle.json"
        info_calls = []
        monkeypatch.setattr(uim.QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(export_path), "JSON Dateien (*.json)"))
        monkeypatch.setattr(uim.QFileDialog, "getOpenFileName", lambda *args, **kwargs: (str(export_path), "JSON Dateien (*.json)"))
        monkeypatch.setattr(uim.QMessageBox, "information", lambda *args, **kwargs: info_calls.append((args, kwargs)) or 0)
        monkeypatch.setattr(uim.QMessageBox, "warning", lambda *args, **kwargs: pytest.fail(f"warning dialog: {args[2]}"))

        window.export_invoice_bundle()
        bundle = json.loads(export_path.read_text(encoding="utf-8"))
        assert bundle["schema"] == BUNDLE_SCHEMA

        bundle["invoices"][0]["amount"] = 11.49
        bundle["invoices"][0]["review_status"] = "checked"
        bundle["invoices"][0]["notes"] = "Companion bestätigt"
        export_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")

        window.import_invoice_bundle()

        assert window.invoices[0].amount == 11.49
        assert window.invoices[0].review_status == "checked"
        assert window.invoices[0].notes == "Companion bestätigt"
        assert info_calls, "expected information dialogs for export/import"
    finally:
        window.close()
