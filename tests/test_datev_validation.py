# -*- coding: utf-8 -*-
"""Unit and contract tests for DATEV validation, account checking and batch diagnostics."""

from datev_exporter import (
    DATEVConfig,
    DATEVBuchung,
    DATEVExporter,
    validate_account_number,
    validate_datev_config,
    validate_invoices_for_export,
    DATEVValidationReport,
)


# ==================== ACCOUNT VALIDATION TESTS ====================

def test_validate_account_number_valid():
    valid_cases = [
        (70000, 4, 8),
        ("70000", 4, 8),
        (4900, 4, 8),
        ("12345678", 4, 8),
        (1000, 4, 4),
        ("99999", 5, 5),
    ]
    for acc, min_d, max_d in valid_cases:
        ok, err = validate_account_number(acc, min_digits=min_d, max_digits=max_d)
        assert ok is True, f"Expected {acc} to be valid, got error: {err}"
        assert err is None


def test_validate_account_number_invalid():
    invalid_cases = [
        (None, 4, 8),
        ("", 4, 8),
        ("   ", 4, 8),
        ("abc", 4, 8),
        ("700a0", 4, 8),
        (-100, 4, 8),
        (0, 4, 8),
        ("123", 4, 8),         # Too short (<4 digits)
        ("123456789", 4, 8),    # Too long (>8 digits)
    ]
    for acc, min_d, max_d in invalid_cases:
        ok, err = validate_account_number(acc, min_digits=min_d, max_digits=max_d)
        assert ok is False, f"Expected {acc} to be invalid"
        assert err is not None


# ==================== CONFIG VALIDATION TESTS ====================

def test_validate_datev_config_default():
    cfg = DATEVConfig()
    ok, errors = validate_datev_config(cfg)
    assert ok is True, f"Default config must be valid, got errors: {errors}"
    assert len(errors) == 0


def test_validate_datev_config_custom_valid():
    cfg = DATEVConfig(
        berater_nr="987654",
        mandant_nr="4321",
        sachkontenlänge=6,
        konten_mapping={"TestProvider": (70001, 4900)}
    )
    ok, errors = validate_datev_config(cfg)
    assert ok is True, f"Custom valid config should pass, got: {errors}"
    assert len(errors) == 0


def test_validate_datev_config_invalid_fields():
    # Invalid berater_nr (> 7 digits)
    cfg1 = DATEVConfig(berater_nr="12345678")
    ok1, err1 = validate_datev_config(cfg1)
    assert ok1 is False
    assert any("Beraternummer" in e for e in err1)

    # Invalid mandant_nr (> 5 digits)
    cfg2 = DATEVConfig(mandant_nr="123456")
    ok2, err2 = validate_datev_config(cfg2)
    assert ok2 is False
    assert any("Mandantennummer" in e for e in err2)

    # Invalid sachkontenlänge (< 4 or > 8)
    cfg3 = DATEVConfig(sachkontenlänge=3)
    ok3, err3 = validate_datev_config(cfg3)
    assert ok3 is False
    assert any("Sachkontenlänge" in e for e in err3)

    # Invalid mapping key / values
    cfg4 = DATEVConfig(konten_mapping={"": (70000, 4900), "Valid": ("invalid_acc", 4900)})
    ok4, err4 = validate_datev_config(cfg4)
    assert ok4 is False
    assert len(err4) >= 2


# ==================== INVOICE BATCH VALIDATION TESTS ====================

def test_validate_invoices_for_export_valid_batch():
    invoices = [
        {"provider": "Amazon", "filename": "inv1.pdf", "date": "2026-01-10", "amount": 100.50},
        {"provider": "Vodafone", "filename": "inv2.pdf", "date": "15.01.2026", "amount": 49.99},
    ]
    report = validate_invoices_for_export(invoices)
    assert isinstance(report, DATEVValidationReport)
    assert report.is_valid is True
    assert report.total_invoices == 2
    assert report.valid_invoices == 2
    assert report.skipped_zero_amount == 0
    assert report.invalid_date_count == 0
    assert len(report.errors) == 0


def test_validate_invoices_for_export_with_zero_amounts_and_bad_dates():
    invoices = [
        {"provider": "Amazon", "filename": "inv1.pdf", "date": "2026-01-10", "amount": 100.50},
        {"provider": "Otto", "filename": "inv2.pdf", "date": "2026-02-12", "amount": 0.0},
        {"provider": "Temu", "filename": "inv3.pdf", "date": "unparseable_date", "amount": 25.00},
        {"provider": "Adobe", "filename": "inv4.pdf", "date": "2026-03-01", "amount": None},
    ]
    report = validate_invoices_for_export(invoices)
    assert report.is_valid is True
    assert report.total_invoices == 4
    assert report.valid_invoices == 2
    assert report.skipped_zero_amount == 2
    assert report.invalid_date_count == 1
    assert len(report.warnings) >= 3


def test_validate_invoices_for_export_empty_list():
    report = validate_invoices_for_export([])
    assert report.total_invoices == 0
    assert report.is_valid is True
    assert len(report.warnings) == 1


def test_datev_exporter_validate_method():
    exporter = DATEVExporter()
    invoices = [
        {"provider": "Amazon", "filename": "amz.pdf", "date": "2026-01-01", "amount": 55.0},
    ]
    report = exporter.validate(invoices)
    assert report.is_valid is True
    assert report.valid_invoices == 1


# ==================== DATEV ROW 93 COLS TEST ====================

def test_datev_buchung_row_length_and_fields():
    buchung = DATEVBuchung(
        umsatz=123.45,
        soll_haben="S",
        wkz="EUR",
        konto=70001,
        gegenkonto=4930,
        belegdatum="1201",
        belegfeld1="INV-9999",
        buchungstext="Test Rechnung",
    )
    row = buchung.to_row()
    assert len(row) == 93
    assert row[0] == "123,45"
    assert row[1] == "S"
    assert row[2] == "EUR"
    assert row[6] == "70001"
    assert row[7] == "4930"
    assert row[9] == "1201"
    assert row[10] == "INV-9999"
    assert row[13] == "Test Rechnung"
