"""Tests for invoice CSV export (export_invoices_csv)."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Headless mock setup for PySide6 if running off-screen
sys.path.insert(0, str(Path(__file__).parent.parent))

for mod in (
    "winrt",
    "winrt.windows.media.ocr",
    "winrt.windows.graphics.imaging",
    "winrt.windows.storage",
    "winrt.windows.storage.streams",
):
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

import UniversalInvoiceMail as uim


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(["pytest", "-platform", "offscreen"])
    return app


def test_export_invoices_csv_headless_all(tmp_path: Path, monkeypatch, qapp):
    """Test exporting all invoices programmatically with comprehensive columns."""
    invoices_db = tmp_path / "invoices.json"
    invoices_db.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(uim, "INVOICES_DB", invoices_db)

    window = uim.MainWindow()
    try:
        window.invoices = [
            uim.Invoice(
                id="inv-1",
                profile_id="p-1",
                profile_name="Amazon DE",
                filename="rechnung_001.pdf",
                date="2026-09-01",
                path=str(tmp_path / "rechnung_001.pdf"),
                sender="rechnung@amazon.de",
                subject="Ihre Bestellung 123",
                amount=29.95,
                currency="EUR",
                review_status="verified",
                notes="Bürobedarf",
            ),
            uim.Invoice(
                id="inv-2",
                profile_id="p-2",
                profile_name="Telekom",
                filename="rechnung_002.pdf",
                date="2026-09-05",
                path=str(tmp_path / "rechnung_002.pdf"),
                sender="rechnung@telekom.de",
                subject="Monatsrechnung",
                amount=None,
                currency="EUR",
                review_status="unchecked",
                notes="",
            ),
        ]

        target_csv = tmp_path / "export_test.csv"
        result_path = window.export_invoices_csv(filepath=target_csv)

        assert result_path == str(target_csv)
        assert target_csv.exists()

        with open(target_csv, "r", encoding="utf-8-sig") as f:
            reader = list(csv.reader(f, delimiter=";"))

        # Header prüfen
        expected_header = [
            "Datum", "Profil/Shop", "Absender", "Betreff",
            "Dateiname", "Pfad", "Betrag", "Währung", "Status", "Notizen"
        ]
        assert reader[0] == expected_header
        assert len(reader) == 3

        # Zeile 1
        assert reader[1][0] == "2026-09-01"
        assert reader[1][1] == "Amazon DE"
        assert reader[1][2] == "rechnung@amazon.de"
        assert reader[1][4] == "rechnung_001.pdf"
        assert reader[1][6] == "29,95"
        assert reader[1][7] == "EUR"
        assert reader[1][8] == "verified"
        assert reader[1][9] == "Bürobedarf"

        # Zeile 2 (ohne Betrag)
        assert reader[2][0] == "2026-09-05"
        assert reader[2][1] == "Telekom"
        assert reader[2][6] == ""
        assert reader[2][8] == "unchecked"
    finally:
        window.close()


def test_export_invoices_csv_selection(tmp_path: Path, monkeypatch, qapp):
    """Test exporting only selected invoices when checkboxes are checked."""
    invoices_db = tmp_path / "invoices.json"
    invoices_db.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(uim, "INVOICES_DB", invoices_db)

    window = uim.MainWindow()
    try:
        pdf1 = tmp_path / "doc1.pdf"
        pdf2 = tmp_path / "doc2.pdf"
        pdf1.write_bytes(b"%PDF-1.4 test1")
        pdf2.write_bytes(b"%PDF-1.4 test2")

        window.invoices = [
            uim.Invoice(
                id="inv-1",
                profile_name="Shop A",
                filename="doc1.pdf",
                date="2026-09-10",
                path=str(pdf1),
                amount=10.0,
            ),
            uim.Invoice(
                id="inv-2",
                profile_name="Shop B",
                filename="doc2.pdf",
                date="2026-09-12",
                path=str(pdf2),
                amount=20.0,
            ),
        ]
        window.refresh_invoice_table()

        # Nur Zeile 1 selektieren
        item0 = window.invoice_table.item(0, 0)
        assert item0 is not None
        item0.setCheckState(Qt.CheckState.Checked)

        target_csv = tmp_path / "selected.csv"
        result = window.export_invoices_csv(filepath=target_csv)
        assert result == str(target_csv)

        with open(target_csv, "r", encoding="utf-8-sig") as f:
            reader = list(csv.reader(f, delimiter=";"))

        # Nur Header + 1 ausgewählte Rechnung
        assert len(reader) == 2
        selected_path = item0.data(Qt.ItemDataRole.UserRole)
        assert reader[1][5] == selected_path
    finally:
        window.close()


def test_export_invoices_csv_empty(tmp_path: Path, monkeypatch, qapp):
    """Test exporting when no invoices are available."""
    invoices_db = tmp_path / "invoices.json"
    invoices_db.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(uim, "INVOICES_DB", invoices_db)

    window = uim.MainWindow()
    try:
        window.invoices = []
        target_csv = tmp_path / "empty.csv"
        result = window.export_invoices_csv(filepath=target_csv)
        assert result is None
        assert not target_csv.exists()
    finally:
        window.close()


def test_export_invoices_csv_dialog_flow(tmp_path: Path, monkeypatch, qapp):
    """Test standard interactive export using QFileDialog."""
    invoices_db = tmp_path / "invoices.json"
    invoices_db.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(uim, "INVOICES_DB", invoices_db)

    window = uim.MainWindow()
    try:
        window.invoices = [
            uim.Invoice(
                id="inv-dialog",
                profile_name="Dialog Shop",
                filename="dialog.pdf",
                date="2026-09-15",
                path=str(tmp_path / "dialog.pdf"),
                amount=99.00,
            )
        ]

        target_csv = tmp_path / "dialog_saved.csv"
        info_shown = []
        monkeypatch.setattr(
            uim.QFileDialog,
            "getSaveFileName",
            lambda *args, **kwargs: (str(target_csv), "CSV Dateien (*.csv)"),
        )
        monkeypatch.setattr(
            uim.QMessageBox,
            "information",
            lambda *args, **kwargs: info_shown.append(args),
        )

        result = window.export_invoices_csv(filepath=None)
        assert result == str(target_csv)
        assert target_csv.exists()
        assert len(info_shown) >= 1
    finally:
        window.close()


def test_export_invoices_csv_headless_no_modals_and_nested_dirs(tmp_path: Path, monkeypatch, qapp):
    """Regression test: headless export creates parent dirs and never opens modal QMessageBoxes."""
    invoices_db = tmp_path / "invoices.json"
    invoices_db.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(uim, "INVOICES_DB", invoices_db)

    modal_calls = []
    monkeypatch.setattr(
        uim.QMessageBox,
        "information",
        lambda *args, **kwargs: modal_calls.append(("information", args)),
    )
    monkeypatch.setattr(
        uim.QMessageBox,
        "warning",
        lambda *args, **kwargs: modal_calls.append(("warning", args)),
    )

    window = uim.MainWindow()
    try:
        window.invoices = [
            uim.Invoice(
                id="inv-nested",
                profile_name="Nested Shop",
                filename="nested.pdf",
                date="2026-09-22",
                path=str(tmp_path / "nested.pdf"),
                amount=123.45,
            )
        ]

        # Nested directory that does not exist yet
        target_csv = tmp_path / "nested" / "subfolder" / "invoices.csv"
        assert not target_csv.parent.exists()

        result = window.export_invoices_csv(filepath=target_csv)
        assert result == str(target_csv)
        assert target_csv.exists()
        assert target_csv.parent.is_dir()
        # Headless mode must NOT trigger any modal dialogs
        assert len(modal_calls) == 0

        # Read back CSV to verify content
        with open(target_csv, "r", encoding="utf-8-sig") as f:
            lines = list(csv.reader(f, delimiter=";"))
        assert len(lines) == 2
        assert lines[1][1] == "Nested Shop"
        assert lines[1][6] == "123,45"
    finally:
        window.close()


def test_export_invoices_csv_headless_error_handling_no_modals(tmp_path: Path, monkeypatch, qapp):
    """Regression test: headless export errors do not trigger modal QMessageBox.warning."""
    invoices_db = tmp_path / "invoices.json"
    invoices_db.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(uim, "INVOICES_DB", invoices_db)

    modal_calls = []
    monkeypatch.setattr(
        uim.QMessageBox,
        "warning",
        lambda *args, **kwargs: modal_calls.append(("warning", args)),
    )

    window = uim.MainWindow()
    try:
        window.invoices = [
            uim.Invoice(
                id="inv-err",
                profile_name="Err Shop",
                filename="err.pdf",
                date="2026-09-22",
                path=str(tmp_path / "err.pdf"),
                amount=50.0,
            )
        ]

        # Pass a directory path as filepath to provoke an OSError/PermissionError on open()
        invalid_path = tmp_path / "is_a_directory"
        invalid_path.mkdir(parents=True, exist_ok=True)

        result = window.export_invoices_csv(filepath=invalid_path)
        assert result is None
        assert len(modal_calls) == 0
    finally:
        window.close()
