"""Unit and contract tests for UniversalInvoiceMail CLI interface."""

from __future__ import annotations

import csv
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
import UniversalInvoiceMail as uim


class TestCliInterface(unittest.TestCase):
    """Tests for cli.py functionality, actions and JSON output."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = Path(self.temp_dir.name)
        self.config_path = self.dir_path / "config.json"
        self.db_path = self.dir_path / "invoices.json"

        # Populate sample config
        config_data = {
            "settings": {
                "download_path": str(self.dir_path / "downloads"),
                "download_attachments": True,
            },
            "accounts": [
                {
                    "id": "acc-1",
                    "name": "Arbeits-Mail",
                    "provider": "IMAP",
                    "host": "imap.example.com",
                    "port": 993,
                    "username": "lukas@example.com",
                }
            ],
            "profiles": [
                {
                    "id": "prof-1",
                    "name": "Amazon",
                    "account_id": "acc-1",
                    "sender_filter": "amazon.de",
                    "subject_filter": "Bestellung,Rechnung",
                    "enabled": True,
                },
                {
                    "id": "prof-2",
                    "name": "Telekom",
                    "account_id": "acc-1",
                    "sender_filter": "rechnung@telekom.de",
                    "subject_filter": "Rechnung",
                    "enabled": False,
                },
            ],
            "datev_config": {
                "berater_nr": "12345",
                "mandant_nr": "67890",
                "konten_mapping": {
                    "Amazon": [70001, 4930],
                    "Telekom": [70003, 4920],
                },
            },
        }
        self.config_path.write_text(json.dumps(config_data, indent=2), encoding="utf-8")

        # Populate sample invoices
        self.sample_pdf = self.dir_path / "downloads" / "rechnung_01.pdf"
        self.sample_pdf.parent.mkdir(parents=True, exist_ok=True)
        self.sample_pdf.write_bytes(b"%PDF-1.4 sample invoice")

        invoices_data = [
            {
                "id": "inv-001",
                "profile_name": "Amazon",
                "filename": "rechnung_01.pdf",
                "date": "2026-08-15",
                "path": str(self.sample_pdf),
                "amount": 42.50,
                "currency": "EUR",
                "review_status": "ready",
                "notes": "Büromaterial",
                "sender": "rechnung@amazon.de",
                "subject": "Ihre Amazon.de Bestellung",
            },
            {
                "id": "inv-002",
                "profile_name": "Telekom",
                "filename": "rechnung_02.pdf",
                "date": "2026-08-20",
                "path": str(self.dir_path / "downloads" / "rechnung_02.pdf"),
                "amount": 19.99,
                "currency": "EUR",
                "review_status": "unchecked",
                "notes": "Mobilfunk",
                "sender": "rechnung@telekom.de",
                "subject": "Ihre Telekom Rechnung",
            },
        ]
        self.db_path.write_text(json.dumps(invoices_data, indent=2), encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_has_cli_action(self):
        self.assertFalse(cli.has_cli_action([]))
        self.assertFalse(cli.has_cli_action(["--unknown", "val"]))
        self.assertTrue(cli.has_cli_action(["--version"]))
        self.assertTrue(cli.has_cli_action(["-v"]))
        self.assertTrue(cli.has_cli_action(["--help"]))
        self.assertTrue(cli.has_cli_action(["-h"]))
        self.assertTrue(cli.has_cli_action(["--list-profiles"]))
        self.assertTrue(cli.has_cli_action(["--list-accounts"]))
        self.assertTrue(cli.has_cli_action(["--list-invoices"]))
        self.assertTrue(cli.has_cli_action(["--export-csv"]))
        self.assertTrue(cli.has_cli_action(["--export-bundle"]))
        self.assertTrue(cli.has_cli_action(["--import-bundle", "b.json"]))
        self.assertTrue(cli.has_cli_action(["--validate-datev"]))

    def test_version_action(self):
        with self.assertRaises(SystemExit) as cm:
            cli.run_cli(["--version"])
        self.assertEqual(cm.exception.code, 0)

    def test_list_profiles_text(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-profiles",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        output = out.getvalue()
        self.assertIn("Konfigurierte Profile (2)", output)
        self.assertIn("Amazon", output)
        self.assertIn("Telekom", output)
        self.assertIn("Aktiv", output)
        self.assertIn("Deaktiviert", output)

    def test_list_profiles_json(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-profiles",
                "--json",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Amazon")
        self.assertEqual(data[1]["name"], "Telekom")

    def test_list_accounts(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-accounts",
                "--json",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Arbeits-Mail")
        self.assertEqual(data[0]["username"], "lukas@example.com")

    def test_list_invoices_with_filter(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-invoices",
                "--profile", "Amazon",
                "--json",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(data["total_count"], 1)
        self.assertEqual(data["invoices"][0]["id"], "inv-001")
        self.assertEqual(data["invoices"][0]["amount"], 42.50)

    def test_export_csv(self):
        csv_file = self.dir_path / "export.csv"
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--export-csv", str(csv_file),
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        self.assertTrue(csv_file.exists())

        # Verify CSV content
        with open(csv_file, "r", encoding="utf-8-sig") as f:
            reader = list(csv.reader(f, delimiter=";"))
            self.assertEqual(len(reader), 3)  # Header + 2 rows
            self.assertEqual(reader[0][0], "Datum")
            self.assertEqual(reader[1][1], "Amazon")
            self.assertEqual(reader[1][6], "42,50")
            self.assertEqual(reader[2][1], "Telekom")
            self.assertEqual(reader[2][6], "19,99")

    def test_export_csv_json_output(self):
        csv_file = self.dir_path / "export_json.csv"
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--export-csv", str(csv_file),
                "--json",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        res = json.loads(out.getvalue())
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["exported_count"], 2)

    def test_export_and_import_bundle(self):
        bundle_file = self.dir_path / "test_bundle.json"
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--export-bundle", str(bundle_file),
                "--json",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        self.assertTrue(bundle_file.exists())

        bundle_content = json.loads(bundle_file.read_text(encoding="utf-8"))
        self.assertEqual(bundle_content["schema"], "universalinvoicemail-invoicebundle-v1")
        self.assertEqual(len(bundle_content["invoices"]), 2)

        # Modify an invoice in bundle and import with --dry-run
        bundle_content["invoices"][0]["notes"] = "Neuer Kommentar aus Companion"
        bundle_file.write_text(json.dumps(bundle_content, indent=2), encoding="utf-8")

        out_dry = io.StringIO()
        with patch("sys.stdout", out_dry):
            code_dry = cli.run_cli([
                "--import-bundle", str(bundle_file),
                "--dry-run",
                "--json",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code_dry, 0)
        dry_res = json.loads(out_dry.getvalue())
        self.assertTrue(dry_res["dry_run"])
        self.assertEqual(dry_res["applied_changes"], 1)

        # Verify DB was NOT updated yet
        db_content_after_dry = json.loads(self.db_path.read_text(encoding="utf-8"))
        self.assertEqual(db_content_after_dry[0]["notes"], "Büromaterial")

        # Now import for real
        out_live = io.StringIO()
        with patch("sys.stdout", out_live):
            code_live = cli.run_cli([
                "--import-bundle", str(bundle_file),
                "--json",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code_live, 0)
        live_res = json.loads(out_live.getvalue())
        self.assertFalse(live_res["dry_run"])
        self.assertEqual(live_res["applied_changes"], 1)

        # Verify DB WAS updated
        db_content_after_live = json.loads(self.db_path.read_text(encoding="utf-8"))
        self.assertEqual(db_content_after_live[0]["notes"], "Neuer Kommentar aus Companion")

    def test_validate_datev_success(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--validate-datev",
                "--json",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        report = json.loads(out.getvalue())
        self.assertTrue(report["is_valid"])
        self.assertEqual(report["total_invoices"], 2)
        self.assertEqual(report["valid_invoices"], 2)
        self.assertEqual(len(report["errors"]), 0)

    def test_validate_datev_invalid_config(self):
        bad_config = {
            "datev_config": {
                "berater_nr": "NICHT_NUMERISCH",
                "mandant_nr": "67890",
            }
        }
        bad_cfg_file = self.dir_path / "bad_config.json"
        bad_cfg_file.write_text(json.dumps(bad_config), encoding="utf-8")

        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--validate-datev",
                "--json",
                "--config", str(bad_cfg_file),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 1)
        report = json.loads(out.getvalue())
        self.assertFalse(report["is_valid"])
        self.assertTrue(len(report["errors"]) > 0)

    def test_uim_main_delegates_to_cli(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = uim.main([
                "--list-profiles",
                "--json",
                "--config", str(self.config_path),
                "--invoices-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(len(data), 2)


if __name__ == "__main__":
    unittest.main()
