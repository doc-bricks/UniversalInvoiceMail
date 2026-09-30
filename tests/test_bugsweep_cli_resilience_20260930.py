"""Regression tests for UniversalInvoiceMail CLI resilience and bugfixes."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Mock GUI modules for headless test safety
for mod in [
    "xhtml2pdf", "xhtml2pdf.pisa", "pytesseract", "pypdfium2", "pypdf",
    "PIL", "PIL.Image", "selenium", "webdriver_manager", "googleapiclient",
    "google_auth_oauthlib", "google.auth", "google.oauth2", "keyring",
    "win32com", "win32com.client", "pythoncom",
]:
    if mod not in sys.modules:
        from unittest.mock import MagicMock
        sys.modules[mod] = MagicMock()

import cli


class TestCliResilienceBugsweep(unittest.TestCase):
    """Test suite proving and guarding against CLI bugs identified in bugsweep."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = Path(self.temp_dir.name)
        self.config_path = self.dir_path / "config.json"
        self.db_path = self.dir_path / "invoices.json"

        # Baseline minimal valid setup
        self.config_path.write_text(json.dumps({
            "settings": {"download_path": str(self.dir_path / "downloads")},
            "accounts": [],
            "profiles": [],
        }), encoding="utf-8")
        self.db_path.write_text("[]", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_list_invoices_with_string_amounts_does_not_crash(self):
        """BUG 1: String amounts like '42.50' or '19,99' crashed with ValueError: Unknown format code 'f'."""
        invoices_data = [
            {
                "id": "inv-str-1",
                "profile_name": "ShopA",
                "filename": "inv1.pdf",
                "date": "2026-09-01",
                "amount": "42.50",
                "currency": "EUR",
                "review_status": "ready",
            },
            {
                "id": "inv-str-2",
                "profile_name": "ShopB",
                "filename": "inv2.pdf",
                "date": "2026-09-02",
                "amount": "19,99 €",
                "currency": "EUR",
                "review_status": "checked",
            },
            {
                "id": "inv-str-3",
                "profile_name": "ShopC",
                "filename": "inv3.pdf",
                "date": "2026-09-03",
                "amount": None,
                "currency": "EUR",
                "review_status": "unchecked",
            },
        ]
        self.db_path.write_text(json.dumps(invoices_data), encoding="utf-8")

        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-invoices",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        output = out.getvalue()
        self.assertIn("42.50 EUR", output)
        self.assertIn("19.99 EUR", output)
        self.assertIn("Kein Betrag", output)

    def test_filter_status_unchecked_matches_none_and_missing_review_status(self):
        """BUG 2: Invoices with review_status=None or missing were excluded by --status unchecked."""
        invoices_data = [
            {
                "id": "inv-1",
                "profile_name": "ShopA",
                "filename": "inv1.pdf",
                "review_status": None,  # null in JSON -> default is unchecked
            },
            {
                "id": "inv-2",
                "profile_name": "ShopB",
                "filename": "inv2.pdf",
                # review_status omitted entirely -> default is unchecked
            },
            {
                "id": "inv-3",
                "profile_name": "ShopC",
                "filename": "inv3.pdf",
                "review_status": "checked",
            },
        ]
        self.db_path.write_text(json.dumps(invoices_data), encoding="utf-8")

        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-invoices",
                "--status", "unchecked",
                "--json",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        # Both inv-1 and inv-2 must match the unchecked filter
        self.assertEqual(data["total_count"], 2)
        matched_ids = [inv["id"] for inv in data["invoices"]]
        self.assertIn("inv-1", matched_ids)
        self.assertIn("inv-2", matched_ids)

    def test_load_data_with_null_or_non_dict_config_does_not_crash(self):
        """BUG 3: config.json containing 'null' or a list caused AttributeError: 'NoneType' object has no attribute 'get'."""
        self.config_path.write_text("null", encoding="utf-8")
        settings, accounts, profiles, invoices, datev_config = cli.load_data(
            config_path=str(self.config_path),
            db_path=str(self.db_path),
        )
        self.assertEqual(settings, {})
        self.assertEqual(accounts, [])
        self.assertEqual(profiles, [])
        self.assertIsNone(datev_config)

    def test_datev_config_with_scalar_mapping_or_extra_attributes(self):
        """BUG 4: DATEVConfig with scalar or malformed mapping caused unhandled TypeError: 'int' object is not iterable."""
        bad_datev_config = {
            "datev_config": {
                "berater_nr": 12345,  # int instead of str
                "mandant_nr": 67890,
                "sachkontenlaenge": 6,
                "waehrung": "EUR",
                "konten_mapping": {
                    "Amazon": [70001, 4930],
                    "FaultyProvider": 70002,  # scalar instead of list/tuple
                },
            }
        }
        self.config_path.write_text(json.dumps(bad_datev_config), encoding="utf-8")

        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--validate-datev",
                "--json",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 1)
        data = json.loads(out.getvalue())
        self.assertFalse(data["is_valid"])
        self.assertTrue(any("FaultyProvider" in err for err in data["errors"]))

    def test_export_bundle_creates_target_directory_automatically(self):
        """BUG 5: export-bundle to a non-existent directory failed with FileNotFoundError."""
        invoices_data = [
            {
                "id": "inv-001",
                "profile_name": "Shop",
                "filename": "doc.pdf",
                "date": "2026-09-01",
                "amount": 50.0,
            }
        ]
        self.db_path.write_text(json.dumps(invoices_data), encoding="utf-8")

        nested_bundle = self.dir_path / "subfolder" / "nested" / "bundle.json"
        self.assertFalse(nested_bundle.parent.exists())

        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--export-bundle", str(nested_bundle),
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        self.assertTrue(nested_bundle.exists())

    def test_has_cli_action_includes_gui_trigger(self):
        """BUG 7: --gui is recognized by has_cli_action."""
        self.assertTrue(cli.has_cli_action(["--gui"]))

    def test_filter_profile_none_does_not_falsely_match_word_none(self):
        """None profile_name must not falsely match '--profile none' query."""
        invoices_data = [
            {"id": "inv-none", "profile_name": None, "filename": "none.pdf"},
            {"id": "inv-real", "profile_name": "NoneShop", "filename": "real.pdf"},
        ]
        self.db_path.write_text(json.dumps(invoices_data), encoding="utf-8")

        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-invoices",
                "--profile", "noneshop",
                "--json",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(data["total_count"], 1)
        self.assertEqual(data["invoices"][0]["id"], "inv-real")

    def test_export_csv_oserror_returns_exit_code_1(self):
        """CSV export returns 1 cleanly when file write raises OSError."""
        csv_file = self.dir_path / "blocked.csv"
        out = io.StringIO()
        err = io.StringIO()
        with patch("cli.export_invoices_to_csv", side_effect=PermissionError("Permission denied")):
            with patch("sys.stdout", out), patch("sys.stderr", err):
                code = cli.run_cli([
                    "--export-csv", str(csv_file),
                    "--json",
                    "--config", str(self.config_path),
                    "--invoices-db", str(self.db_path),
                ])
        self.assertEqual(code, 1)
        res = json.loads(out.getvalue())
        self.assertEqual(res["status"], "error")

    def test_export_bundle_oserror_returns_exit_code_1(self):
        """Bundle export returns 1 cleanly when file write raises OSError."""
        bundle_file = self.dir_path / "blocked.json"
        out = io.StringIO()
        err = io.StringIO()
        with patch("invoice_bundle.write_invoice_bundle", side_effect=PermissionError("Permission denied")):
            with patch("sys.stdout", out), patch("sys.stderr", err):
                code = cli.run_cli([
                    "--export-bundle", str(bundle_file),
                    "--json",
                    "--config", str(self.config_path),
                    "--invoices-db", str(self.db_path),
                ])
        self.assertEqual(code, 1)
        res = json.loads(out.getvalue())
        self.assertEqual(res["status"], "error")

    def test_import_bundle_save_invoices_oserror_returns_exit_code_1(self):
        """Bundle import returns 1 cleanly when save_invoices raises OSError."""
        bundle_file = self.dir_path / "sample_bundle.json"
        bundle_file.write_text(json.dumps({
            "schema": "universalinvoicemail-invoicebundle-v1",
            "invoices": [],
        }), encoding="utf-8")

        out = io.StringIO()
        err = io.StringIO()
        with patch("cli.save_invoices", side_effect=PermissionError("Permission denied")):
            with patch("sys.stdout", out), patch("sys.stderr", err):
                code = cli.run_cli([
                    "--import-bundle", str(bundle_file),
                    "--json",
                    "--config", str(self.config_path),
                    "--invoices-db", str(self.db_path),
                ])
        self.assertEqual(code, 1)
        res = json.loads(out.getvalue())
        self.assertEqual(res["status"], "error")


if __name__ == "__main__":
    unittest.main()
