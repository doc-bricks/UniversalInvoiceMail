"""Tests für DATEV-Export."""
import csv
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import MagicMock

# Optionale Abhaengigkeiten mocken die moeglicherweise nicht installiert sind
for mod in ['xhtml2pdf', 'xhtml2pdf.pisa', 'pytesseract', 'pypdfium2',
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


def test_datev_exporter_import():
    from datev_exporter import DATEVConfig, DATEVExporter, export_invoices_datev
    cfg = DATEVConfig(berater_nr="12345", mandant_nr="67890")
    assert cfg.berater_nr == "12345"


def test_datev_export_empty():
    from datev_exporter import DATEVConfig, DATEVExporter
    cfg = DATEVConfig()
    exp = DATEVExporter(cfg)
    result = exp.export([], None)
    assert isinstance(result, str)


def test_datev_export_one_invoice(tmp_path):
    from datev_exporter import DATEVConfig, DATEVExporter
    cfg = DATEVConfig()
    exp = DATEVExporter(cfg)
    invoices = [{
        "provider": "Amazon",
        "filename": "rechnung.pdf",
        "date": "2026-01-15",
        "path": "/tmp/rechnung.pdf",
        "amount": 119.00,
        "category": "Amazon",
    }]
    out = tmp_path / "test.csv"
    result = exp.export(invoices, out)
    assert out.exists()
    content = out.read_text(encoding="cp1252")
    assert "119" in content or "119,00" in content


def test_datev_export_slash_dates_drive_header_range():
    from datev_exporter import DATEVConfig, DATEVExporter
    cfg = DATEVConfig()
    exp = DATEVExporter(cfg)
    invoices = [
        {
            "provider": "Amazon",
            "filename": "rechnung-1.pdf",
            "date": "15/01/2026",
            "path": "/tmp/rechnung-1.pdf",
            "amount": 19.99,
            "category": "Amazon",
        },
        {
            "provider": "Vodafone",
            "filename": "rechnung-2.pdf",
            "date": "20/02/2026",
            "path": "/tmp/rechnung-2.pdf",
            "amount": 29.99,
            "category": "Vodafone",
        },
    ]

    header = next(csv.reader([exp.export(invoices).splitlines()[0]], delimiter=";"))
    assert header[14] == "20260115"
    assert header[15] == "20260220"


def test_datev_row_column_count_matches_header():
    """to_row() muss exakt so viele Felder liefern wie HEADER_COLS Spalten hat."""
    from datev_exporter import DATEVBuchung, DATEVExporter
    buchung = DATEVBuchung(umsatz=10.0, belegdatum="1501", belegfeld1="RE-001")
    assert len(buchung.to_row()) == len(DATEVExporter.HEADER_COLS)


def test_invoice_amount_field():
    from UniversalInvoiceMail import Invoice
    inv = Invoice(id="1", profile_name="Test", filename="f.pdf", date="2026-01-01", path="/tmp/f.pdf")
    assert inv.amount is None
    inv2 = Invoice(id="2", profile_name="Test", filename="f.pdf", date="2026-01-01", path="/tmp/f.pdf", amount=99.99)
    assert inv2.amount == 99.99
    d = inv2.to_dict()
    inv3 = Invoice.from_dict(d)
    assert inv3.amount == 99.99


def test_datev_settings_dialog_table_operations():
    """DATEVSettingsDialog muss Konten-Mapping in Tabelle anzeigen, editieren und zurückgeben."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtWidgets import QApplication
    from datev_exporter import DATEVConfig, DEFAULT_KONTEN_MAPPING
    from UniversalInvoiceMail import DATEVSettingsDialog

    app = QApplication.instance() or QApplication([])

    cfg = DATEVConfig(berater_nr="99999", mandant_nr="11111", konten_mapping={"CustomShop": (70099, 4999)})
    dlg = DATEVSettingsDialog(cfg)

    # Initial populating
    assert dlg.table_mapping.rowCount() == 1
    assert dlg.table_mapping.item(0, 0).text() == "CustomShop"
    assert dlg.table_mapping.item(0, 1).text() == "70099"
    assert dlg.table_mapping.item(0, 2).text() == "4999"

    # Add row
    dlg._add_row()
    assert dlg.table_mapping.rowCount() == 2
    assert dlg.table_mapping.item(1, 0).text() == "Neuer Partner"

    # Reset mapping
    dlg._reset_mapping()
    assert dlg.table_mapping.rowCount() == len(DEFAULT_KONTEN_MAPPING)

    # get_config
    new_cfg = dlg.get_config()
    assert new_cfg.berater_nr == "99999"
    assert new_cfg.mandant_nr == "11111"
    assert "Amazon" in new_cfg.konten_mapping
    assert new_cfg.konten_mapping["Amazon"] == (70001, 4930)

    dlg.close()


def test_datev_settings_dialog_accessibility():
    """DATEVSettingsDialog Bedienelemente müssen Accessibility-Attribute besitzen."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtWidgets import QApplication, QDialogButtonBox
    from datev_exporter import DATEVConfig
    from UniversalInvoiceMail import DATEVSettingsDialog

    app = QApplication.instance() or QApplication([])

    cfg = DATEVConfig()
    dlg = DATEVSettingsDialog(cfg)

    assert dlg.inp_berater.accessibleName() == "Beraternummer"
    assert dlg.inp_berater.accessibleDescription() == "DATEV-Beraternummer für den Buchungsstapel."
    assert dlg.inp_berater.toolTip() == "DATEV-Beraternummer eingeben"
    assert dlg.inp_mandant.accessibleName() == "Mandantennummer"
    assert dlg.inp_mandant.accessibleDescription() == "DATEV-Mandantennummer für den Buchungsstapel."
    assert dlg.inp_mandant.toolTip() == "DATEV-Mandantennummer eingeben"
    assert dlg.table_mapping.accessibleName() == "DATEV-Konten-Mapping-Tabelle"
    assert dlg.table_mapping.accessibleDescription() == (
        "Ordnet Absendern oder Schlüsselwörtern ein Kreditor- und ein Aufwandskonto zu."
    )
    assert dlg.table_mapping.toolTip() == (
        "Absender oder Schlüsselwort sowie Kreditor- und Aufwandskonto bearbeiten"
    )
    assert dlg.btn_add_row.accessibleName() == "Zeile hinzufügen"
    assert dlg.btn_add_row.accessibleDescription() == (
        "Fügt eine neue, editierbare Konten-Mapping-Zeile hinzu."
    )
    assert dlg.btn_remove_row.accessibleName() == "Zeile entfernen"
    assert dlg.btn_remove_row.accessibleDescription() == (
        "Entfernt die aktuell ausgewählte Konten-Mapping-Zeile."
    )
    assert dlg.btn_reset_mapping.accessibleName() == "Standard wiederherstellen"
    assert dlg.btn_reset_mapping.accessibleDescription() == (
        "Ersetzt alle Einträge durch die standardmäßige Konten-Zuordnung."
    )

    ok_button = dlg.dialog_buttons.button(QDialogButtonBox.StandardButton.Ok)
    cancel_button = dlg.dialog_buttons.button(QDialogButtonBox.StandardButton.Cancel)
    assert ok_button.accessibleName() == "DATEV-Einstellungen speichern"
    assert ok_button.accessibleDescription() == (
        "Speichert Beraternummer, Mandantennummer und Konten-Mapping."
    )
    assert cancel_button.accessibleName() == "DATEV-Einstellungen verwerfen"
    assert cancel_button.accessibleDescription() == (
        "Schließt den Dialog ohne Änderungen zu speichern."
    )

    dlg.close()


def test_datev_export_none_provider():
    """export() muss robuster gegenüber None-Provider/Kategorie sein."""
    from datev_exporter import DATEVConfig, DATEVExporter
    cfg = DATEVConfig()
    exp = DATEVExporter(cfg)
    invoices = [{"provider": None, "category": None, "amount": 50.0}]
    csv_str = exp.export(invoices)
    assert "50,00" in csv_str


