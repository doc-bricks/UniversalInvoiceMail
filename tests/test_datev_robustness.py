"""Unit tests for DATEV exporter robustness (amounts, extended formats, and export)."""

from datetime import datetime
from decimal import Decimal
import io
import csv
from datev_exporter import (
    DATEVConfig,
    DATEVExporter,
    parse_datev_amount,
    parse_datev_datetime,
    validate_invoices_for_export,
)


def test_parse_datev_amount_valid_and_edge_cases():
    """Verify robust parsing of numbers, strings, and decimals."""
    assert parse_datev_amount(19.99) == 19.99
    assert parse_datev_amount(25) == 25.0
    assert parse_datev_amount("19.99") == 19.99
    assert parse_datev_amount("19,99") == 19.99
    assert parse_datev_amount(" 19,99 € ") == 19.99
    assert parse_datev_amount("1.234,56 EUR") == 1234.56
    assert parse_datev_amount("1,234.56") == 1234.56
    assert parse_datev_amount("1'234.56") == 1234.56
    assert parse_datev_amount(Decimal("45.67")) == 45.67

    # Ungültige, leere oder negative Beträge
    assert parse_datev_amount(None) is None
    assert parse_datev_amount("") is None
    assert parse_datev_amount("   ") is None
    assert parse_datev_amount("0") is None
    assert parse_datev_amount(0.0) is None
    assert parse_datev_amount(-15.0) is None
    assert parse_datev_amount("-15.00") is None
    assert parse_datev_amount("(15.00)") is None
    assert parse_datev_amount("ungültig") is None


def test_parse_datev_datetime_extended_formats():
    """Verify extended format parsing including slash and 2-digit years."""
    dt_iso = parse_datev_datetime("2026-08-12")
    assert dt_iso == datetime(2026, 8, 12)

    dt_slash = parse_datev_datetime("2026/08/12")
    assert dt_slash == datetime(2026, 8, 12)

    dt_short_year_de = parse_datev_datetime("12.08.26")
    assert dt_short_year_de == datetime(2026, 8, 12)

    dt_short_year_slash = parse_datev_datetime("12/08/26")
    assert dt_short_year_slash == datetime(2026, 8, 12)


def test_validate_and_export_with_string_and_decimal_amounts():
    """Verify that validate_invoices_for_export and export do not crash on string/decimal amounts."""
    invoices = [
        {
            "provider": "Amazon",
            "filename": "rechnung_str.pdf",
            "date": "2026-08-15",
            "amount": "29,99 €",
        },
        {
            "provider": "Otto",
            "filename": "rechnung_dec.pdf",
            "date": "2026/08/16",
            "amount": Decimal("49.50"),
        },
        {
            "provider": "Invalid",
            "filename": "rechnung_zero.pdf",
            "date": "2026-08-17",
            "amount": "0,00",
        },
    ]

    report = validate_invoices_for_export(invoices)
    assert report.is_valid is True
    assert report.total_invoices == 3
    assert report.valid_invoices == 2
    assert report.skipped_zero_amount == 1

    exporter = DATEVExporter(DATEVConfig())
    csv_output = exporter.export(invoices)
    assert csv_output

    lines = csv_output.strip().split("\n")
    # Zeile 1: Header, Zeile 2: Spalten, Zeile 3 & 4: Buchungen
    assert len(lines) >= 4

    reader = list(csv.reader(io.StringIO(csv_output), delimiter=";"))
    # Erste Buchungszeile prüfen (Zeile 2 im 0-basierten Index nach Header und Spalten)
    booking1 = reader[2]
    assert booking1[0] == "29,99"
    assert booking1[1] == "S"

    booking2 = reader[3]
    assert booking2[0] == "49,50"
    assert booking2[1] == "S"
