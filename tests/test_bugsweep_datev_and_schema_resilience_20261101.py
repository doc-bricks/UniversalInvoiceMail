# -*- coding: utf-8 -*-
"""
Regressionstests für Bugsweep 2026-11-01:
DATEV-Export-Pipeline, Betragsnormalisierung, Schema-Resilienz, Beleg-Formatierung und Dataclass-Kompatibilität.
"""

from datev_exporter import (
    DATEVConfig,
    DATEVExporter,
    parse_datev_amount,
    validate_datev_config,
    validate_invoices_for_export,
)
from invoice_bundle import _normalize_amount
from UniversalInvoiceMail import Invoice, extract_order_id, sanitize_filename


def test_extract_order_id_resilience():
    """extract_order_id darf bei None, leeren Strings und Nicht-Strings nicht mit TypeError abstürzen."""
    assert extract_order_id(None) == ""
    assert extract_order_id("") == ""
    assert extract_order_id(12345) == ""
    assert extract_order_id(["Bestellnummer: 12345"]) == ""
    assert extract_order_id("Bestellnummer: ABC-12345") == "ABC-12345"
    assert extract_order_id("Auftrags-Nr. XYZ-98765") == "XYZ-98765"


def test_sanitize_filename_clock_device_name():
    """sanitize_filename muss Windows-reservierten Gerätenamen CLOCK$ abfangen."""
    assert sanitize_filename("CLOCK$.pdf").startswith("_")
    assert sanitize_filename("clock$").startswith("_")
    assert sanitize_filename("clock$.txt").startswith("_")
    assert sanitize_filename("NUL.txt").startswith("_")
    assert sanitize_filename("CON").startswith("_")


def test_datev_config_integer_coercion_and_header_generation():
    """DATEVConfig muss Integer für berater_nr, mandant_nr und sachkontenlänge fehlerfrei unterstützen."""
    # Integer für berater_nr und mandant_nr übergeben
    cfg = DATEVConfig(berater_nr=12345, mandant_nr=67890, sachkontenlänge="4")
    # validate_datev_config darf nicht an '4' < 4 mit TypeError scheitern
    is_valid, errors = validate_datev_config(cfg)
    assert is_valid is True, f"Validierungsfehler: {errors}"

    # Header-Erzeugung darf nicht mit TypeError: sequence item 10: expected str instance, int found abstürzen
    exp = DATEVExporter(cfg)
    header = exp._build_header("20260101", "20261231")
    assert "12345;67890;" in header


def test_datev_export_with_none_filename_does_not_crash():
    """DATEVExporter.export darf bei invoices mit filename=None nicht bei slicing (None[:36]) abstürzen."""
    cfg = DATEVConfig()
    exp = DATEVExporter(cfg)
    invoices = [
        {
            "provider": "Amazon",
            "filename": None,
            "date": "2026-05-10",
            "amount": 42.50,
        }
    ]
    csv_str = exp.export(invoices)
    assert "42,50" in csv_str
    assert "Amazon Rechnung" in csv_str


def test_datev_export_and_validation_with_invoice_dataclasses():
    """DATEVExporter.export und validate_invoices_for_export müssen Invoice-Dataclass-Instanzen unterstützen."""
    inv = Invoice(
        id="inv-123",
        profile_name="Telekom",
        filename="Rechnung_Telekom_Mai.pdf",
        date="2026-05-15",
        path="C:/docs/Rechnung_Telekom_Mai.pdf",
        amount=79.90,
    )
    # Validierung
    report = validate_invoices_for_export([inv])
    assert report.total_invoices == 1
    assert report.valid_invoices == 1

    # Export
    exp = DATEVExporter()
    csv_str = exp.export([inv])
    assert "79,90" in csv_str
    assert "Rechnung_Telekom_Mai" in csv_str


def test_datev_export_with_heterogeneous_invoices_mixed():
    """DATEVExporter.export muss gemischte Listen aus Dicts und Invoice-Dataclasses nahtlos verarbeiten."""
    inv_dc = Invoice(
        id="inv-dc-1",
        profile_name="Adobe",
        filename="Adobe_CreativeCloud.pdf",
        date="2026-06-01",
        path="C:/docs/Adobe_CreativeCloud.pdf",
        amount=59.49,
    )
    inv_dict = {
        "provider": "Google",
        "filename": "Google_Workspace_Mai.pdf",
        "date": "2026-06-02",
        "amount": 12.00,
    }
    exp = DATEVExporter()
    csv_str = exp.export([inv_dc, inv_dict])
    assert "59,49" in csv_str
    assert "Adobe_CreativeCloud" in csv_str
    assert "12,00" in csv_str
    assert "Google_Workspace_Mai" in csv_str


def test_parse_datev_amount_currency_and_thousands_resilience():
    """parse_datev_amount muss internationale Währungen, Tausendertrennpunkte ohne Cents und Unendlichkeitswerte handhaben."""
    # Mehrfache Tausenderpunkte ohne Cents (Deutsch)
    assert parse_datev_amount("1.234.567") == 1234567.0
    assert parse_datev_amount("1,234,567") == 1234567.0

    # Internationale Währungen mit Symbolen und Codes
    assert parse_datev_amount("120,50 CHF") == 120.50
    assert parse_datev_amount("1'234.56 CHF") == 1234.56
    assert parse_datev_amount("$ 99.95") == 99.95
    assert parse_datev_amount("99.95 USD") == 99.95
    assert parse_datev_amount("£ 49,99") == 49.99

    # Unendlichkeit und NaN dürfen nicht als gültig zurückgegeben werden
    assert parse_datev_amount(float("inf")) is None
    assert parse_datev_amount(float("-inf")) is None
    assert parse_datev_amount(float("nan")) is None
    assert parse_datev_amount("nan") is None
    assert parse_datev_amount("infinity") is None
    assert parse_datev_amount(0) is None
    assert parse_datev_amount(-15.50) is None


def test_normalize_amount_inf_nan_defense():
    """_normalize_amount in invoice_bundle.py muss float('nan') und float('inf') abfangen und None liefern."""
    assert _normalize_amount(float("nan")) is None
    assert _normalize_amount(float("inf")) is None
    assert _normalize_amount(float("-inf")) is None
    assert _normalize_amount("nan") is None
    assert _normalize_amount("infinity") is None
    assert _normalize_amount("19.99") == 19.99


def test_datev_get_konten_malformed_mapping_resilience():
    """_get_konten muss bei korrupten oder unvollständigen Konten-Mappings stets ein sicheres 2-Tupel liefern."""
    cfg = DATEVConfig()
    # Malformed konten_mapping with singletons, None, strings
    cfg.konten_mapping = {
        "Amazon": (70001,),           # Singleton, nicht entpackbar
        "Corrupt": None,               # None
        "Broken": "70005,4920",        # String statt Tupel
        "Sonstige": (70000, 4900),
    }
    exp = DATEVExporter(cfg)
    # Darf nicht mit ValueError: not enough values to unpack abstürzen
    k, gk = exp._get_konten("Amazon")
    assert isinstance(k, int) and isinstance(gk, int)
    k2, gk2 = exp._get_konten("Corrupt")
    assert isinstance(k2, int) and isinstance(gk2, int)
    k3, gk3 = exp._get_konten("Broken")
    assert isinstance(k3, int) and isinstance(gk3, int)
    k4, gk4 = exp._get_konten(None)
    assert isinstance(k4, int) and isinstance(gk4, int)
