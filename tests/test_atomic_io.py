# -*- coding: utf-8 -*-
"""Comprehensive tests for atomic and crash-durable file I/O operations."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from atomic_io import (
    atomic_publish_file,
    atomic_write_bytes,
    atomic_write_json,
    atomic_write_text,
    get_default_protected_paths,
    is_protected_path,
    resolve_path,
)
from invoice_bundle import write_invoice_bundle
from datev_exporter import DATEVConfig, DATEVExporter



def test_resolve_path_returns_absolute(tmp_path: Path):
    rel_path = Path("some_file.txt")
    resolved = resolve_path(rel_path)
    assert resolved.is_absolute()


def test_atomic_write_text_success(tmp_path: Path):
    target = tmp_path / "subdir" / "output.txt"
    content = "Rechnungsdaten 2026 — Prüfung mit Umlauten: äöüÄÖÜß"

    written_path = atomic_write_text(target, content, encoding="utf-8")
    assert written_path.exists()
    assert written_path.read_text(encoding="utf-8") == content


def test_atomic_write_text_preserves_target_on_failure(tmp_path: Path, monkeypatch):
    target = tmp_path / "critical.txt"
    original_content = "Original, unberührter Zustand"
    atomic_write_text(target, original_content, encoding="utf-8")

    # Simulate an error during open/write
    def fake_open(*args, **kwargs):
        raise OSError("Disk I/O error simulated")

    monkeypatch.setattr("builtins.open", fake_open)

    with pytest.raises(OSError, match="Disk I/O error simulated"):
        atomic_write_text(target, "Neue Daten, die fehlschlagen", encoding="utf-8")

    # Target must remain completely intact
    assert target.exists()
    assert target.read_text(encoding="utf-8") == original_content


def test_atomic_write_json_success(tmp_path: Path):
    target = tmp_path / "config.json"
    data = {"app": "UniversalInvoiceMail", "version": "2.3.0", "active": True, "rates": [19, 7]}

    written = atomic_write_json(target, data, indent=2, ensure_ascii=False)
    assert written.exists()

    loaded = json.loads(written.read_text(encoding="utf-8"))
    assert loaded == data


def test_atomic_write_json_serialization_failure_leaves_target_untouched(tmp_path: Path):
    target = tmp_path / "intact.json"
    original_content = '{"intact": true}\n'
    atomic_write_text(target, original_content, encoding="utf-8")

    # Non-serializable object (set or object)
    unserializable_data = {"key": {1, 2, 3}}

    with pytest.raises(TypeError):
        atomic_write_json(target, unserializable_data)

    assert target.read_text(encoding="utf-8") == original_content


def test_atomic_write_bytes_success_and_min_bytes(tmp_path: Path):
    target = tmp_path / "binary.dat"
    payload = b"\x00\x01\x02\x03\xFF\xFE\xFD"

    written = atomic_write_bytes(target, payload, min_bytes=4)
    assert written.exists()
    assert written.read_bytes() == payload

    # Test failure when min_bytes is not reached
    small_payload = b"\x01"
    with pytest.raises(ValueError, match="Binärdaten sind unvollständig"):
        atomic_write_bytes(tmp_path / "failed.dat", small_payload, min_bytes=10)


def test_atomic_publish_file_success_and_cleanup(tmp_path: Path):
    src_tmp = tmp_path / "temp_source.tmp"
    src_tmp.write_text("Temporär generierter Bericht", encoding="utf-8")

    target = tmp_path / "published" / "final.txt"
    published = atomic_publish_file(src_tmp, target, min_bytes=5)

    assert published.exists()
    assert published.read_text(encoding="utf-8") == "Temporär generierter Bericht"
    assert not src_tmp.exists()  # Source tmp file must have been moved/cleaned up


def test_atomic_publish_file_rejects_empty_file(tmp_path: Path):
    src_tmp = tmp_path / "empty_source.tmp"
    src_tmp.write_text("", encoding="utf-8")

    target = tmp_path / "should_not_exist.txt"
    with pytest.raises(ValueError, match="unvollständig"):
        atomic_publish_file(src_tmp, target, min_bytes=1)

    assert not target.exists()


def test_is_protected_path_detection(tmp_path: Path):
    db_file = tmp_path / "invoices.json"
    cfg_file = tmp_path / "config.json"
    export_file = tmp_path / "export.csv"

    db_file.touch()
    cfg_file.touch()
    export_file.touch()

    protected = [db_file, cfg_file]

    assert is_protected_path(db_file, protected) is True
    assert is_protected_path(cfg_file, protected) is True
    assert is_protected_path(export_file, protected) is False
    assert is_protected_path(tmp_path / "other.txt", protected) is False


def test_get_default_protected_paths(tmp_path: Path):
    paths = get_default_protected_paths(tmp_path)
    assert tmp_path.resolve() / "config.json" in paths
    assert tmp_path.resolve() / "invoices.json" in paths
    assert tmp_path.resolve() / "token.json" in paths



def test_atomic_write_rejects_protected_paths(tmp_path: Path):
    protected_db = tmp_path / "invoices.json"
    protected_db.write_text('["wichtige_rechnungsdaten"]', encoding="utf-8")

    protected_set = {protected_db}

    with pytest.raises(PermissionError, match="geschützte Konfigurations- oder Datenbankdatei"):
        atomic_write_text(protected_db, "ungültiger Überschreibversuch", protected_paths=protected_set)

    with pytest.raises(PermissionError, match="geschützte Konfigurations- oder Datenbankdatei"):
        atomic_write_json(protected_db, {"hacked": True}, protected_paths=protected_set)

    # Database file remains strictly unchanged
    assert protected_db.read_text(encoding="utf-8") == '["wichtige_rechnungsdaten"]'


def test_bundle_write_uses_atomic_io(tmp_path: Path):
    bundle = {
        "schema": "universalinvoicemail-invoicebundle-v1",
        "created_at": "2026-10-02T00:00:00Z",
        "source": {"app": "UniversalInvoiceMail", "version": "2.3.0"},
        "invoices": [],
    }
    target = tmp_path / "bundle.json"
    result = write_invoice_bundle(bundle, target)

    assert result == target
    assert target.exists()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["schema"] == "universalinvoicemail-invoicebundle-v1"


def test_datev_export_uses_atomic_io(tmp_path: Path):
    cfg = DATEVConfig(berater_nr="99999", mandant_nr="88888")
    exporter = DATEVExporter(config=cfg)

    invoices = [
        {
            "date": "2026-09-15",
            "amount": 150.00,
            "sender": "Lieferant GmbH",
            "subject": "Rechnung RE-12345",
            "filename": "rechnung.pdf",
            "path": str(tmp_path / "rechnung.pdf"),
            "currency": "EUR",
        }
    ]
    target = tmp_path / "EXTF_Buchungsstapel.csv"
    res = exporter.export(invoices, output_path=target)



    assert res == str(target)
    assert target.exists()
    content = target.read_text(encoding="cp1252")
    assert "EXTF" in content
    assert "99999" in content
    assert "88888" in content
