"""Exports retain old data and never replace source/state files."""

import ast
import csv
from datetime import datetime
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

import cli
import csv_export


@pytest.fixture
def gui_export(tmp_path):
    # Execute the exact GUI method without constructing a window or touching settings.
    source = Path(__file__).parents[1] / "UniversalInvoiceMail.py"
    tree = ast.parse(source.read_text(encoding="utf-8-sig"))
    main = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "MainWindow")
    method = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == "export_invoices_csv")
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), method], type_ignores=[])
    namespace = {"Path": Path, "datetime": datetime, "CONFIG_FILE": tmp_path / "config.json", "INVOICES_DB": tmp_path / "invoices.json"}
    exec(compile(ast.fix_missing_locations(module), str(source), "exec"), namespace)
    return namespace["export_invoices_csv"]


def invoice(tmp_path, **changes):
    values = dict(date="2026-10-01", profile_name="Äpfel", sender="test@example.invalid", subject="Test", filename="original.pdf", path=str(tmp_path / "original.pdf"), amount=12.5, currency="EUR", review_status="unchecked", notes="Größe; geprüft")
    values.update(changes)
    return values


@pytest.mark.parametrize("failure", ["encoding", "body", "fsync", "replace"])
def test_old_export_survives_failure(tmp_path, monkeypatch, failure):
    target = tmp_path / "old.csv"
    target.write_bytes(b"previous export")
    foreign = tmp_path / ".uim-csv-foreign.tmp"
    foreign.write_bytes(b"foreign")
    if failure in ("fsync", "replace"):
        def fail(*args):
            raise OSError("injected failure")
        monkeypatch.setattr(csv_export.os, failure, fail)
    with pytest.raises((OSError, ValueError, UnicodeError)):
        with csv_export.atomic_csv_output(target) as stream:
            stream.write("\ud800" if failure == "encoding" else "complete output")
            if failure == "body":
                raise ValueError("invalid row")
    assert target.read_bytes() == b"previous export"
    assert foreign.read_bytes() == b"foreign"
    assert list(tmp_path.glob(".uim-csv-*.tmp")) == [foreign]


def test_complete_csv_preserves_format(tmp_path):
    target = tmp_path / "nested" / "output.csv"
    count = cli.export_invoices_to_csv([invoice(tmp_path)], target)
    raw = target.read_bytes()
    assert count == 1 and raw.startswith(b"\xef\xbb\xbf")
    assert raw.count(b"\r\n") == 2
    rows = list(csv.reader(raw.decode("utf-8-sig").splitlines(), delimiter=";"))
    assert rows[1][1] == "Äpfel" and rows[1][6] == "12,50" and rows[1][9] == "Größe; geprüft"
    assert not list(target.parent.glob(".uim-csv-*.tmp"))


@pytest.mark.parametrize("alias", ["direct", "hardlink"])
def test_filtered_originals_are_protected(tmp_path, alias):
    original = tmp_path / "excluded.pdf"
    original.write_bytes(b"source")
    target = original
    if alias == "hardlink":
        target = tmp_path / "alias.csv"
        os.link(original, target)
    invoices = [invoice(tmp_path), invoice(tmp_path, path=str(original), profile_name="excluded")]
    with pytest.raises(ValueError, match="geschützte"):
        cli.export_invoices_to_csv(invoices, target, profile_filter="Äpfel")
    assert original.read_bytes() == target.read_bytes() == b"source"
    assert not list(tmp_path.glob(".uim-csv-*.tmp"))


def test_new_alias_before_publication_is_protected(tmp_path):
    source = tmp_path / "source.pdf"
    source.write_bytes(b"source")
    target = tmp_path / "out.csv"
    with pytest.raises(ValueError, match="geschützte"):
        with csv_export.atomic_csv_output(target, [source]) as stream:
            stream.write("new output")
            os.link(source, target)
    assert source.read_bytes() == target.read_bytes() == b"source"
    assert not list(tmp_path.glob(".uim-csv-*.tmp"))


@pytest.mark.parametrize("kind", ["config", "database"])
@pytest.mark.parametrize("alias", [False, True])
def test_cli_actual_state_paths_protected(tmp_path, capsys, kind, alias):
    config = tmp_path / "custom-config.json"
    database = tmp_path / "custom-db.json"
    config.write_text("{}", encoding="utf-8")
    database.write_text(json.dumps([invoice(tmp_path)]), encoding="utf-8")
    source = config if kind == "config" else database
    before = source.read_bytes()
    target = source
    if alias:
        target = tmp_path / "alias.csv"
        os.link(source, target)
    rc = cli.run_cli(["--config", str(config), "--invoices-db", str(database), "--export-csv", str(target), "--json"])
    assert rc == 1 and json.loads(capsys.readouterr().out)["status"] == "error"
    assert source.read_bytes() == target.read_bytes() == before


def test_cli_encoding_error_is_structured_and_preserves_export(tmp_path, capsys):
    database = tmp_path / "db.json"
    database.write_text(json.dumps([invoice(tmp_path, notes="\ud800")]), encoding="utf-8")
    target = tmp_path / "old.csv"
    target.write_bytes(b"old")
    assert cli.run_cli(["--config", str(tmp_path / "absent.json"), "--invoices-db", str(database), "--export-csv", str(target), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "error"
    assert target.read_bytes() == b"old"


def test_gui_late_amount_error_preserves_old_export(tmp_path, gui_export):
    target = tmp_path / "old.csv"
    target.write_bytes(b"old")
    logs = []
    fake = SimpleNamespace(invoices=[SimpleNamespace(**invoice(tmp_path, amount="invalid"))], _get_selected_invoice_paths=lambda: set(), _log=logs.append)
    assert gui_export(fake, target) is None
    assert target.read_bytes() == b"old" and "[ERROR]" in logs[-1]


@pytest.mark.parametrize("kind", ["excluded", "config", "database"])
def test_gui_protects_unselected_and_state_files(tmp_path, gui_export, kind):
    first = SimpleNamespace(**invoice(tmp_path))
    excluded = SimpleNamespace(**invoice(tmp_path, path=str(tmp_path / "excluded.pdf")))
    target = Path(excluded.path) if kind == "excluded" else tmp_path / ("config.json" if kind == "config" else "invoices.json")
    target.write_bytes(b"protected")
    fake = SimpleNamespace(invoices=[first, excluded], _get_selected_invoice_paths=lambda: {first.path}, _log=lambda text: None)
    assert gui_export(fake, target) is None
    assert target.read_bytes() == b"protected"
