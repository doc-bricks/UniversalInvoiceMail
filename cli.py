#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI & Automation Interface for UniversalInvoiceMail
===================================================

Provides a headless command-line interface for UniversalInvoiceMail to enable
automation, background scheduling, batch export, and CLI management without
requiring a GUI display server.

Features:
- Version inquiry (--version / -v)
- List configured mail profiles (--list-profiles)
- List configured mail accounts (--list-accounts)
- List downloaded invoices with filtering (--list-invoices)
- Headless CSV export (--export-csv [PATH])
- Headless portable bundle export (--export-bundle [PATH])
- Headless portable bundle import with collision detection (--import-bundle PATH [--dry-run])
- Headless DATEV validation (--validate-datev)
- Structured JSON output (--json) for seamless tool/script/agent integration
- Custom config and database paths (--config, --invoices-db)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

# Version and identity constants
APP_NAME = "UniversalInvoiceMail"
VERSION = "2.3.0"

DEFAULT_BASE_DIR = Path.home() / ".universal_invoice_mail"
DEFAULT_CONFIG_FILE = DEFAULT_BASE_DIR / "config.json"
DEFAULT_INVOICES_DB = DEFAULT_BASE_DIR / "invoices.json"


def get_default_paths(config_path: Optional[str] = None, db_path: Optional[str] = None) -> Tuple[Path, Path]:
    """Returns resolved config and invoices database paths."""
    c_path = Path(config_path).resolve() if config_path else DEFAULT_CONFIG_FILE
    d_path = Path(db_path).resolve() if db_path else DEFAULT_INVOICES_DB
    return c_path, d_path


def load_data(
    config_path: Optional[str] = None,
    db_path: Optional[str] = None,
) -> Tuple[dict, List[dict], List[dict], List[dict], Optional[dict]]:
    """Loads settings, accounts, profiles, invoices, and datev_config without Qt dependencies."""
    c_path, d_path = get_default_paths(config_path, db_path)

    settings: dict = {}
    accounts: List[dict] = []
    profiles: List[dict] = []
    datev_config: Optional[dict] = None
    invoices: List[dict] = []

    if c_path.exists():
        try:
            data = json.loads(c_path.read_text(encoding="utf-8"))
            settings = data.get("settings", {})
            accounts = data.get("accounts", [])
            profiles = data.get("profiles", [])
            datev_config = data.get("datev_config", None)
        except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            print(f"[WARNUNG] Konfigurationsdatei konnte nicht vollständig geladen werden: {e}", file=sys.stderr)

    if d_path.exists():
        try:
            raw_inv = json.loads(d_path.read_text(encoding="utf-8"))
            if isinstance(raw_inv, list):
                invoices = raw_inv
        except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            print(f"[WARNUNG] Rechnungsdatenbank konnte nicht geladen werden: {e}", file=sys.stderr)

    return settings, accounts, profiles, invoices, datev_config


def save_invoices(invoices: List[dict], db_path: Optional[str] = None) -> None:
    """Saves updated invoices list to the database JSON file."""
    _, d_path = get_default_paths(db_path=db_path)
    d_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = d_path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(invoices, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp_path, d_path)


def export_invoices_to_csv(
    invoices: List[dict],
    output_path: Path,
    profile_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> int:
    """Exports invoices to a semicolon-separated CSV file with UTF-8 BOM."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    filtered = invoices
    if profile_filter:
        p_low = profile_filter.lower()
        filtered = [i for i in filtered if p_low in str(i.get("profile_name", "")).lower()]
    if status_filter:
        s_low = status_filter.lower()
        filtered = [i for i in filtered if s_low == str(i.get("review_status", "")).lower()]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "Datum", "Profil/Shop", "Absender", "Betreff",
            "Dateiname", "Pfad", "Betrag", "Währung", "Status", "Notizen"
        ])
        for inv in filtered:
            raw_amt = inv.get("amount")
            amt_str = ""
            if raw_amt is not None:
                try:
                    amt_str = f"{float(raw_amt):.2f}".replace(".", ",")
                except (ValueError, TypeError):
                    amt_str = str(raw_amt)
            curr = inv.get("currency", "EUR") or "EUR"
            status = inv.get("review_status", "unchecked") or "unchecked"
            notes = inv.get("notes", "") or ""
            writer.writerow([
                inv.get("date", ""),
                inv.get("profile_name", ""),
                inv.get("sender", ""),
                inv.get("subject", ""),
                inv.get("filename", ""),
                inv.get("path", ""),
                amt_str,
                curr,
                status,
                notes,
            ])

    return len(filtered)


def build_parser() -> argparse.ArgumentParser:
    """Constructs the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="UniversalInvoiceMail",
        description="Headless CLI und Automations-Schnittstelle für UniversalInvoiceMail.",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"{APP_NAME} {VERSION}",
    )
    parser.add_argument(
        "--config",
        dest="config_path",
        metavar="PFAD",
        help="Pfad zur alternativen config.json Datei.",
    )
    parser.add_argument(
        "--invoices-db",
        dest="invoices_db_path",
        metavar="PFAD",
        help="Pfad zur alternativen invoices.json Datei.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Gibt Ausgaben als strukturiertes JSON auf stdout aus.",
    )

    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--list-profiles",
        action="store_true",
        help="Listet alle konfigurierten Shop- und E-Mail-Profile auf.",
    )
    action_group.add_argument(
        "--list-accounts",
        action="store_true",
        help="Listet alle konfigurierten Mail-Accounts auf.",
    )
    action_group.add_argument(
        "--list-invoices",
        action="store_true",
        help="Listet erfasste Rechnungen auf.",
    )
    action_group.add_argument(
        "--export-csv",
        nargs="?",
        const="DEFAULT",
        metavar="ZIELPFAD",
        help="Exportiert Rechnungen in eine CSV-Datei (Default: ~/.universal_invoice_mail/rechnungen_export.csv).",
    )
    action_group.add_argument(
        "--export-bundle",
        nargs="?",
        const="DEFAULT",
        metavar="ZIELPFAD",
        help="Exportiert das portable Austausch-Bundle universalinvoicemail-invoicebundle-v1.json.",
    )
    action_group.add_argument(
        "--import-bundle",
        metavar="QUELLPFAD",
        help="Importiert ein portables Austausch-Bundle und aktualisiert Rechnungsmetadaten.",
    )
    action_group.add_argument(
        "--validate-datev",
        action="store_true",
        help="Führt die DATEV-Validierung für Konfiguration und Buchungsstapel aus.",
    )
    action_group.add_argument(
        "--gui",
        action="store_true",
        help="Startet die grafische Benutzeroberfläche (Standard bei Aufruf ohne Flags).",
    )

    # Filter-Optionen für List- und Export-Befehle
    parser.add_argument(
        "--profile",
        dest="filter_profile",
        metavar="NAME",
        help="Filtert Rechnungen nach Profil-/Shop-Name.",
    )
    parser.add_argument(
        "--status",
        dest="filter_status",
        metavar="STATUS",
        help="Filtert Rechnungen nach Review-Status (unchecked, checked, needs_question, ready).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="ANZAHL",
        help="Maximale Anzahl Rechnungen bei --list-invoices (Standard: 50, 0 = unbegrenzt).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simuliert Importe oder Änderungen ohne Schreibzugriff auf die Datenbank.",
    )

    return parser


def has_cli_action(argv: Optional[Sequence[str]] = None) -> bool:
    """Checks whether the argument list contains a command-line action."""
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        return False

    cli_triggers = {
        "-h", "--help",
        "-v", "--version",
        "--list-profiles",
        "--list-accounts",
        "--list-invoices",
        "--export-csv",
        "--export-bundle",
        "--import-bundle",
        "--validate-datev",
    }
    for arg in argv:
        clean_arg = arg.split("=")[0]
        if clean_arg in cli_triggers:
            return True
    return False


def run_cli(argv: Optional[Sequence[str]] = None) -> int:
    """Main CLI execution router."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.gui:
        return -1  # Signal to caller to launch GUI

    settings, accounts, profiles, invoices, datev_config_dict = load_data(
        config_path=args.config_path,
        db_path=args.invoices_db_path,
    )

    # 1. Profile auflisten
    if args.list_profiles:
        if args.json_output:
            print(json.dumps(profiles, indent=2, ensure_ascii=False))
            return 0
        print(f"Konfigurierte Profile ({len(profiles)}):")
        print("-" * 75)
        for p in profiles:
            p_id = p.get("id", "")
            p_name = p.get("name", "Unbenannt")
            p_sender = p.get("sender_filter", "*")
            p_subj = p.get("subject_filter", "*")
            p_en = "Aktiv" if p.get("enabled", True) else "Deaktiviert"
            print(f"• [{p_en}] {p_name:<20} (ID: {p_id}) | Absender: {p_sender:<20} | Betreff: {p_subj}")
        return 0

    # 2. Accounts auflisten
    if args.list_accounts:
        if args.json_output:
            print(json.dumps(accounts, indent=2, ensure_ascii=False))
            return 0
        print(f"Konfigurierte E-Mail-Konten ({len(accounts)}):")
        print("-" * 75)
        for a in accounts:
            a_name = a.get("name", "Unbenannt")
            a_prov = a.get("provider", "IMAP")
            a_host = a.get("host", "localhost")
            a_user = a.get("username", "")
            print(f"• {a_name:<20} | Typ: {a_prov:<12} | Host: {a_host:<25} | Benutzer: {a_user}")
        return 0

    # 3. Rechnungen auflisten
    if args.list_invoices:
        filtered = invoices
        if args.filter_profile:
            p_low = args.filter_profile.lower()
            filtered = [i for i in filtered if p_low in str(i.get("profile_name", "")).lower()]
        if args.filter_status:
            s_low = args.filter_status.lower()
            filtered = [i for i in filtered if s_low == str(i.get("review_status", "")).lower()]

        total_matching = len(filtered)
        if args.limit > 0:
            filtered = filtered[:args.limit]

        if args.json_output:
            print(json.dumps({
                "total_count": total_matching,
                "displayed_count": len(filtered),
                "invoices": filtered,
            }, indent=2, ensure_ascii=False))
            return 0

        print(f"Rechnungen (Zeige {len(filtered)} von {total_matching}):")
        print("-" * 80)
        for inv in filtered:
            date_str = inv.get("date", "Unbekannt")
            p_name = inv.get("profile_name", "")
            fname = inv.get("filename", "")
            amt = inv.get("amount")
            curr = inv.get("currency", "EUR") or "EUR"
            status = inv.get("review_status", "unchecked")
            amt_disp = f"{amt:.2f} {curr}" if amt is not None else "Kein Betrag"
            print(f"[{date_str}] {p_name:<15} | {fname:<30} | {amt_disp:<14} | Status: {status}")
        return 0

    # 4. CSV-Export
    if args.export_csv:
        target = args.export_csv
        if target == "DEFAULT":
            target = str(DEFAULT_BASE_DIR / f"rechnungen_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        out_path = Path(target).resolve()
        count = export_invoices_to_csv(
            invoices=invoices,
            output_path=out_path,
            profile_filter=args.filter_profile,
            status_filter=args.filter_status,
        )
        if args.json_output:
            print(json.dumps({
                "status": "success",
                "exported_count": count,
                "output_path": str(out_path),
            }, indent=2, ensure_ascii=False))
        else:
            print(f"[OK] {count} Rechnungen erfolgreich als CSV exportiert:\n  {out_path}")
        return 0

    # 5. Bundle-Export
    if args.export_bundle:
        try:
            from invoice_bundle import build_invoice_bundle, write_invoice_bundle
            from datev_exporter import DATEVConfig
        except ImportError as e:
            print(f"[FEHLER] Modul für Bundle-Export nicht verfügbar: {e}", file=sys.stderr)
            return 1

        target = args.export_bundle
        if target == "DEFAULT":
            target = str(DEFAULT_BASE_DIR / f"invoice_bundle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        out_path = Path(target).resolve()

        cfg_obj = None
        if datev_config_dict:
            km = datev_config_dict.get("konten_mapping")
            cfg_obj = DATEVConfig(
                berater_nr=datev_config_dict.get("berater_nr", "12345"),
                mandant_nr=datev_config_dict.get("mandant_nr", "67890"),
                konten_mapping={k: tuple(v) for k, v in km.items()} if km else None,
            )

        dl_path = settings.get("download_path", str(Path.home() / "Documents" / "Rechnungen"))
        bundle = build_invoice_bundle(
            app_name=APP_NAME,
            app_version=VERSION,
            accounts=accounts,
            profiles=profiles,
            invoices=invoices,
            download_path=dl_path,
            datev_config=cfg_obj,
        )
        write_invoice_bundle(bundle, out_path)

        if args.json_output:
            print(json.dumps({
                "status": "success",
                "bundle_schema": bundle.get("schema"),
                "invoice_count": len(bundle.get("invoices", [])),
                "output_path": str(out_path),
            }, indent=2, ensure_ascii=False))
        else:
            print(f"[OK] Austausch-Bundle ({len(bundle.get('invoices', []))} Rechnungen) exportiert:\n  {out_path}")
        return 0

    # 6. Bundle-Import
    if args.import_bundle:
        try:
            from invoice_bundle import load_invoice_bundle, apply_invoice_bundle_changes
        except ImportError as e:
            print(f"[FEHLER] Modul für Bundle-Import nicht verfügbar: {e}", file=sys.stderr)
            return 1

        bundle_path = Path(args.import_bundle).resolve()
        if not bundle_path.exists():
            print(f"[FEHLER] Bundle-Datei nicht gefunden: {bundle_path}", file=sys.stderr)
            return 1

        try:
            bundle_data = load_invoice_bundle(bundle_path)
            report = apply_invoice_bundle_changes(invoices, bundle_data)
        except Exception as e:
            print(f"[FEHLER] Bundle-Import fehlgeschlagen: {e}", file=sys.stderr)
            return 1

        updated_count = report.get("updated", 0)
        unchanged_count = report.get("unchanged", 0)
        missing_count = len(report.get("missing_local", []))
        conflict_count = len(report.get("conflicts", []))
        invalid_count = len(report.get("invalid_rows", []))

        if not args.dry_run:
            save_invoices(invoices, db_path=args.invoices_db_path)

        if args.json_output:
            print(json.dumps({
                "status": "success",
                "dry_run": args.dry_run,
                "applied_changes": updated_count,
                "unchanged": unchanged_count,
                "missing": missing_count,
                "conflicts": conflict_count,
                "invalid": invalid_count,
            }, indent=2, ensure_ascii=False))
        else:
            mode_str = " (Dry-Run / Simulation)" if args.dry_run else ""
            print(f"[OK] Bundle-Import abgeschlossen{mode_str}:")
            print(f"  • Übernommene Änderungen: {updated_count}")
            print(f"  • Unverändert:            {unchanged_count}")
            print(f"  • Nicht zugeordnet:       {missing_count}")
            print(f"  • Konflikte/Kollisionen:  {conflict_count}")
            if invalid_count:
                print(f"  • Ungültige Einträge:     {invalid_count}")
        return 0

    # 7. DATEV-Validierung
    if args.validate_datev:
        try:
            from datev_exporter import (
                DATEVConfig, validate_invoices_for_export
            )
        except ImportError as e:
            print(f"[FEHLER] DATEV-Modul nicht verfügbar: {e}", file=sys.stderr)
            return 1

        cfg_obj = DATEVConfig()
        if datev_config_dict:
            km = datev_config_dict.get("konten_mapping")
            cfg_obj = DATEVConfig(
                berater_nr=datev_config_dict.get("berater_nr", "12345"),
                mandant_nr=datev_config_dict.get("mandant_nr", "67890"),
                konten_mapping={k: tuple(v) for k, v in km.items()} if km else None,
            )

        report = validate_invoices_for_export(invoices, cfg_obj)

        if args.json_output:
            print(json.dumps({
                "is_valid": report.is_valid,
                "total_invoices": report.total_invoices,
                "valid_invoices": report.valid_invoices,
                "skipped_zero_amount": report.skipped_zero_amount,
                "invalid_date_count": report.invalid_date_count,
                "errors": report.errors,
                "warnings": report.warnings,
            }, indent=2, ensure_ascii=False))
        else:
            status_text = "GÜLTIG" if report.is_valid else "FEHLERHAFT"
            print(f"DATEV-Validierungsbericht: {status_text}")
            print("=" * 50)
            print(f"Gesamtanzahl Rechnungen: {report.total_invoices}")
            print(f"Gültig mit Betrag > 0:   {report.valid_invoices}")
            print(f"Übersprungen (Betrag 0): {report.skipped_zero_amount}")
            print(f"Ungültige Datumsformate: {report.invalid_date_count}")
            if report.errors:
                print("\nFehler:")
                for err in report.errors:
                    print(f"  ❌ {err}")
            if report.warnings:
                print(f"\nHinweise/Warnungen ({len(report.warnings)}):")
                for w in report.warnings[:15]:
                    print(f"  ⚠️  {w}")
                if len(report.warnings) > 15:
                    print(f"  ... und {len(report.warnings) - 15} weitere Hinweise.")

        return 0 if report.is_valid else 1

    # Falls kein Action-Flag angegeben wurde
    parser.print_help()
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Standalone CLI entry point."""
    return run_cli(argv)


if __name__ == "__main__":
    sys.exit(main())
