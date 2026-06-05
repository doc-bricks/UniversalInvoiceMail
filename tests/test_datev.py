"""Tests für DATEV-Export."""
import csv
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


def test_invoice_amount_field():
    from UniversalInvoiceMail import Invoice
    inv = Invoice(id="1", profile_name="Test", filename="f.pdf", date="2026-01-01", path="/tmp/f.pdf")
    assert inv.amount is None
    inv2 = Invoice(id="2", profile_name="Test", filename="f.pdf", date="2026-01-01", path="/tmp/f.pdf", amount=99.99)
    assert inv2.amount == 99.99
    d = inv2.to_dict()
    inv3 = Invoice.from_dict(d)
    assert inv3.amount == 99.99
