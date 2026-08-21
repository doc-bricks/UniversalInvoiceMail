# -*- coding: utf-8 -*-
"""
DATEV-Export Modul für UniversalInvoiceMail
============================================

Exportiert Rechnungen als DATEV-Buchungsstapel (CSV-Format).
Enthält fachliche Validierung von Beraternummer, Mandantennummer,
Konten-Mappings und Buchungsstapeln.

Erstellt: 2026-01-12
Aktualisiert: 2026-08-21 (Validierungshärtung & Taskplan #1156)
Version: 2.0.0
"""

import io
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Union

# ==================== KONFIGURATION ====================

# Standard SKR03-Konten-Mapping
DEFAULT_KONTEN_MAPPING: Dict[str, Tuple[int, int]] = {
    "Amazon": (70001, 4930),      # Bürobedarf
    "Vodafone": (70002, 4920),    # Telefon
    "Telekom": (70003, 4920),     # Telefon
    "O2": (70004, 4920),          # Telefon
    "Strom": (70005, 4240),       # Energie
    "Gas": (70006, 4240),         # Energie
    "Software": (70007, 4964),    # Software/Abos
    "Adobe": (70008, 4964),       # Software/Abos
    "Microsoft": (70009, 4964),   # Software/Abos
    "Google": (70010, 4964),      # Software/Abos
    "Apple": (70011, 4964),       # Software/Abos
    "Temu": (70012, 4930),        # Bürobedarf
    "Otto": (70013, 4930),        # Bürobedarf
    "eBay": (70014, 4930),        # Sonstige
    "PayPal": (70015, 4900),      # Sonstige
    "Sonstige": (70000, 4900),    # Standard-Fallback
}


def validate_account_number(account: Union[int, str], min_digits: int = 4, max_digits: int = 8) -> Tuple[bool, Optional[str]]:
    """
    Validiert eine DATEV-Kontonummer (Sachkonto, Kreditor oder Debitor).

    Regeln:
    - Muss numerisch sein (nur Ziffern, keine Buchstaben oder Sonderzeichen)
    - Wert > 0
    - Länge zwischen min_digits und max_digits (standardmäßig 4 bis 8 Ziffern)
    """
    if account is None:
        return False, "Kontonummer darf nicht leer sein"

    s_acc = str(account).strip()
    if not s_acc:
        return False, "Kontonummer darf nicht leer sein"

    if not s_acc.isdigit():
        return False, f"Kontonummer '{s_acc}' darf nur Ziffern enthalten"

    if len(s_acc) < min_digits or len(s_acc) > max_digits:
        return False, f"Kontonummer '{s_acc}' hat unzulässige Länge {len(s_acc)} (erlaubt: {min_digits} bis {max_digits} Ziffern)"

    int_val = int(s_acc)
    if int_val <= 0:
        return False, f"Kontonummer muss positiv sein (Wert: {int_val})"

    return True, None


@dataclass
class DATEVConfig:
    """Konfiguration für DATEV-Export."""
    berater_nr: str = "12345"
    mandant_nr: str = "67890"
    wj_beginn: str = ""  # YYYYMMDD, leer = aktuelles Jahr
    sachkontenlänge: int = 4
    währung: str = "EUR"
    konten_mapping: Dict[str, Tuple[int, int]] = None

    def __post_init__(self):
        if self.konten_mapping is None:
            self.konten_mapping = DEFAULT_KONTEN_MAPPING.copy()
        if not self.wj_beginn:
            self.wj_beginn = f"{datetime.now().year}0101"


def validate_datev_config(config: DATEVConfig) -> Tuple[bool, List[str]]:
    """
    Validiert eine DATEVConfig auf formale und fachliche Korrektheit.

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_error_messages)
    """
    errors: List[str] = []

    # Beraternummer (1-7 Ziffern, standard 1001 bis 9999999)
    b_nr = str(config.berater_nr).strip()
    if not b_nr or not b_nr.isdigit() or len(b_nr) > 7:
        errors.append(f"Ungültige Beraternummer '{b_nr}': Erwartet werden 1 bis 7 Ziffern.")

    # Mandantennummer (1-5 Ziffern, standard 1 bis 99999)
    m_nr = str(config.mandant_nr).strip()
    if not m_nr or not m_nr.isdigit() or len(m_nr) > 5:
        errors.append(f"Ungültige Mandantennummer '{m_nr}': Erwartet werden 1 bis 5 Ziffern.")

    # Sachkontenlänge (4-8)
    if config.sachkontenlänge < 4 or config.sachkontenlänge > 8:
        errors.append(f"Sachkontenlänge {config.sachkontenlänge} ungültig (erlaubt: 4 bis 8).")

    # Konten-Mapping
    if not isinstance(config.konten_mapping, dict):
        errors.append("Konten-Mapping muss ein Wörterbuch sein.")
    else:
        for provider, accounts in config.konten_mapping.items():
            if not str(provider).strip():
                errors.append("Absender / Schlüsselwort im Konten-Mapping darf nicht leer sein.")
                continue

            if not isinstance(accounts, (tuple, list)) or len(accounts) != 2:
                errors.append(f"Mapping für '{provider}' muss aus (Konto, Gegenkonto) bestehen.")
                continue

            konto, gegenkonto = accounts
            ok_k, err_k = validate_account_number(konto, min_digits=4, max_digits=8)
            if not ok_k:
                errors.append(f"Mapping '{provider}' Kreditor-Konto: {err_k}")

            ok_gk, err_gk = validate_account_number(gegenkonto, min_digits=4, max_digits=8)
            if not ok_gk:
                errors.append(f"Mapping '{provider}' Aufwands-Gegenkonto: {err_gk}")

    return (len(errors) == 0), errors


@dataclass
class DATEVBuchung:
    """Eine einzelne DATEV-Buchung."""
    umsatz: float
    soll_haben: str = "S"  # S=Soll (Ausgabe), H=Haben (Einnahme)
    wkz: str = "EUR"
    konto: int = 70000
    gegenkonto: int = 4900
    belegdatum: str = ""  # TTMM
    belegfeld1: str = ""  # Rechnungsnummer
    buchungstext: str = ""

    def to_row(self) -> List[str]:
        """Konvertiert zu DATEV-CSV-Zeile (93 Felder, entspricht DATEVExporter.HEADER_COLS)."""
        row = [""] * 93

        # Pflichtfelder
        row[0] = f"{self.umsatz:.2f}".replace(".", ",")  # Umsatz (deutsches Format)
        row[1] = self.soll_haben
        row[2] = self.wkz
        # 3-5 leer (Kurs, Basisumsatz, WKZ Basis)
        row[6] = str(self.konto)
        row[7] = str(self.gegenkonto)
        # 8 BU-Schlüssel (leer)
        row[9] = self.belegdatum  # TTMM
        row[10] = self.belegfeld1[:36] if self.belegfeld1 else ""  # Max 36 Zeichen
        # 11 Belegfeld 2 (leer)
        # 12 Skonto (leer)
        row[13] = self.buchungstext[:60] if self.buchungstext else ""  # Max 60 Zeichen

        return row


@dataclass
class DATEVValidationReport:
    """Diagnose- und Validierungsbericht für einen DATEV-Exportlauf."""
    total_invoices: int = 0
    valid_invoices: int = 0
    skipped_zero_amount: int = 0
    invalid_date_count: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    is_valid: bool = True


def validate_invoices_for_export(invoices: List[dict], config: Optional[DATEVConfig] = None) -> DATEVValidationReport:
    """
    Validiert eine Liste von Rechnungs-Dicts vor dem DATEV-Export.

    Prüft:
    - Konfiguration (Berater, Mandant, Konten)
    - Rechnungsbeträge (Erkennung von Null-/Fehlbeträgen)
    - Datumsformate
    """
    report = DATEVValidationReport(total_invoices=len(invoices))

    cfg = config or DATEVConfig()
    cfg_valid, cfg_errors = validate_datev_config(cfg)
    if not cfg_valid:
        report.errors.extend(cfg_errors)
        report.is_valid = False

    if not invoices:
        report.warnings.append("Keine Rechnungen zur Validierung übergeben.")
        return report

    for idx, inv in enumerate(invoices, start=1):
        amount = inv.get("amount", None)
        filename = inv.get("filename", f"Rechnung #{idx}")

        # Betragsprüfung
        if amount is None or amount <= 0:
            report.skipped_zero_amount += 1
            report.warnings.append(f"'{filename}': Kein oder negativer/null Betrag ({amount}) - wird beim Export übersprungen.")
        else:
            report.valid_invoices += 1

        # Datumsprüfung
        date_str = inv.get("date", "")
        parsed = None
        for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"]:
            try:
                parsed = datetime.strptime(date_str, fmt)
                break
            except (ValueError, TypeError):
                continue
        if parsed is None and date_str:
            report.invalid_date_count += 1
            report.warnings.append(f"'{filename}': Unbekanntes Datumsformat '{date_str}', Fallback auf aktuelles Datum.")

    if report.valid_invoices == 0 and report.total_invoices > 0:
        report.warnings.append("Keine der übergebenen Rechnungen hat einen gültigen Betrag > 0. DATEV-Exportdatei wird keine Buchungszeilen enthalten.")

    return report


class DATEVExporter:
    """
    Exportiert Rechnungen im DATEV-Buchungsstapel Format.

    Format: CSV mit Semikolon-Trennung, Windows ANSI (cp1252)
    """

    # Spaltenüberschriften für Zeile 2 (93 Spalten)
    HEADER_COLS = [
        "Umsatz (ohne Soll/Haben-Kz)", "Soll/Haben-Kennzeichen", "WKZ Umsatz",
        "Kurs", "Basisumsatz", "WKZ Basisumsatz", "Konto",
        "Gegenkonto (ohne BU-Schlüssel)", "BU-Schlüssel", "Belegdatum",
        "Belegfeld 1", "Belegfeld 2", "Skonto", "Buchungstext",
        "Postensperre", "Diverse Adressnummer", "Geschäftspartnerbank",
        "Sachverhalt", "Zinssperre", "Beleglink", "Beleginfo - Art 1",
        "Beleginfo - Inhalt 1", "Beleginfo - Art 2", "Beleginfo - Inhalt 2",
        "Beleginfo - Art 3", "Beleginfo - Inhalt 3", "Beleginfo - Art 4",
        "Beleginfo - Inhalt 4", "Beleginfo - Art 5", "Beleginfo - Inhalt 5",
        "Beleginfo - Art 6", "Beleginfo - Inhalt 6", "Beleginfo - Art 7",
        "Beleginfo - Inhalt 7", "Beleginfo - Art 8", "Beleginfo - Inhalt 8",
        "KOST1 - Kostenstelle", "KOST2 - Kostenstelle", "KOST-Menge",
        "EU-Mitgliedstaat u. UStIdNr", "EU-Steuersatz", "Abw. Versteuerungsart",
        "Sachverhalt L+L", "Funktionsergänzung L+L", "BU 49 Hauptfunktionstyp",
        "BU 49 Hauptfunktionsnummer", "BU 49 Funktionsergänzung", "Zusatzinformation - Art 1",
        "Zusatzinformation - Inhalt 1", "Zusatzinformation - Art 2", "Zusatzinformation - Inhalt 2",
        "Zusatzinformation - Art 3", "Zusatzinformation - Inhalt 3", "Zusatzinformation - Art 4",
        "Zusatzinformation - Inhalt 4", "Zusatzinformation - Art 5", "Zusatzinformation - Inhalt 5",
        "Zusatzinformation - Art 6", "Zusatzinformation - Inhalt 6", "Zusatzinformation - Art 7",
        "Zusatzinformation - Inhalt 7", "Zusatzinformation - Art 8", "Zusatzinformation - Inhalt 8",
        "Zusatzinformation - Art 9", "Zusatzinformation - Inhalt 9", "Zusatzinformation - Art 10",
        "Zusatzinformation - Inhalt 10", "Zusatzinformation - Art 11", "Zusatzinformation - Inhalt 11",
        "Zusatzinformation - Art 12", "Zusatzinformation - Inhalt 12", "Zusatzinformation - Art 13",
        "Zusatzinformation - Inhalt 13", "Zusatzinformation - Art 14", "Zusatzinformation - Inhalt 14",
        "Zusatzinformation - Art 15", "Zusatzinformation - Inhalt 15", "Zusatzinformation - Art 16",
        "Zusatzinformation - Inhalt 16", "Zusatzinformation - Art 17", "Zusatzinformation - Inhalt 17",
        "Zusatzinformation - Art 18", "Zusatzinformation - Inhalt 18", "Zusatzinformation - Art 19",
        "Zusatzinformation - Inhalt 19", "Zusatzinformation - Art 20", "Zusatzinformation - Inhalt 20",
        "Stück", "Gewicht", "Zahlweise", "Forderungsart", "Veranlagungsjahr", "Zugeordnete Fälligkeit"
    ]

    def __init__(self, config: Optional[DATEVConfig] = None):
        self.config = config or DATEVConfig()

    def validate(self, invoices: List[dict]) -> DATEVValidationReport:
        """Führt eine Vorab-Validierung der Rechnungsliste durch."""
        return validate_invoices_for_export(invoices, self.config)

    def _build_header(self, datum_von: str, datum_bis: str) -> str:
        """Erstellt die DATEV-Header-Zeile (Zeile 1)."""
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S") + "000"

        # Header-Felder (33 Felder)
        header = [
            '"EXTF"',           # 1 Format-Kennung
            '700',              # 2 Versionsnummer
            '21',               # 3 Formatkategorie (21 = Buchungsstapel)
            '"Buchungsstapel"', # 4 Formatname
            '13',               # 5 Formatversion
            timestamp,          # 6 Erzeugt am
            '',                 # 7 (reserviert)
            '"UIM"',            # 8 Kürzel
            '"UniversalInvoiceMail"', # 9 Bezeichnung Herkunft
            '',                 # 10 (reserviert)
            self.config.berater_nr,   # 11 Beraternummer
            self.config.mandant_nr,   # 12 Mandantennummer
            self.config.wj_beginn,    # 13 WJ-Beginn
            str(self.config.sachkontenlänge), # 14 Sachkontenlänge
            datum_von,          # 15 Datum von
            datum_bis,          # 16 Datum bis
            '"UniversalInvoiceMail Export"', # 17 Bezeichnung
            '',                 # 18 (Diktatkürzel)
            '',                 # 19 (Buchungstyp)
            '1',                # 20 Rechnungslegungszweck (1=Handelsrecht)
            '',                 # 21 (reserviert)
            '0',                # 22 Festschreibung (0=nein)
            f'"{self.config.währung}"', # 23 Währung
            '',                 # 24-33 (reserviert)
        ]

        while len(header) < 33:
            header.append('')

        return ";".join(header)

    def _get_konten(self, provider: str) -> Tuple[int, int]:
        """Ermittelt Konto und Gegenkonto für einen Provider."""
        if not provider:
            return self.config.konten_mapping.get("Sonstige", (70000, 4900))

        # Exakte Übereinstimmung
        if provider in self.config.konten_mapping:
            return self.config.konten_mapping[provider]

        # Teilübereinstimmung (case-insensitive)
        provider_lower = str(provider).lower()
        for key, konten in self.config.konten_mapping.items():
            if key.lower() in provider_lower or provider_lower in key.lower():
                return konten

        # Fallback
        return self.config.konten_mapping.get("Sonstige", (70000, 4900))

    def _parse_invoice_date(self, date_str: str) -> str:
        """Konvertiert Datum zu TTMM Format."""
        parsed = self._parse_invoice_datetime(date_str)
        if parsed is None:
            return datetime.now().strftime("%d%m")
        return parsed.strftime("%d%m")

    def _parse_invoice_datetime(self, date_str: str) -> Optional[datetime]:
        """Parst unterstützte Rechnungsdatumsformate konsistent für Header und Buchung."""
        if not date_str:
            return None

        for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def export(self, invoices: List[dict], output_path: Optional[Path] = None) -> str:
        """
        Exportiert Rechnungen als DATEV-Buchungsstapel.

        Args:
            invoices: Liste von Invoice-Dicts mit keys:
                - provider: str
                - filename: str
                - date: str (YYYY-MM-DD)
                - path: str
                - amount: Optional[float]
                - category: Optional[str]
            output_path: Optionaler Ausgabepfad

        Returns:
            str: CSV-Inhalt oder Pfad zur gespeicherten Datei
        """
        if not invoices:
            return ""

        # Datum-Range ermitteln
        dates = []
        for inv in invoices:
            date_str = inv.get("date", "")
            parsed = self._parse_invoice_datetime(date_str)
            if parsed is not None:
                dates.append(parsed)

        if dates:
            datum_von = min(dates).strftime("%Y%m%d")
            datum_bis = max(dates).strftime("%Y%m%d")
        else:
            now = datetime.now()
            datum_von = now.strftime("%Y0101")
            datum_bis = now.strftime("%Y%m%d")

        # CSV erstellen
        output = io.StringIO()

        # Zeile 1: Header
        output.write(self._build_header(datum_von, datum_bis) + "\n")

        # Zeile 2: Spaltenüberschriften
        output.write(";".join(self.HEADER_COLS) + "\n")

        # Ab Zeile 3: Buchungen
        for inv in invoices:
            amount = inv.get("amount", 0.0)
            if not amount or amount <= 0:
                continue  # Überspringe Rechnungen ohne Betrag

            provider = inv.get("provider", "Sonstige")
            category = inv.get("category", provider)

            konto, gegenkonto = self._get_konten(category or provider)

            buchung = DATEVBuchung(
                umsatz=amount,
                soll_haben="S",  # Ausgabe
                wkz=self.config.währung,
                konto=konto,
                gegenkonto=gegenkonto,
                belegdatum=self._parse_invoice_date(inv.get("date", "")),
                belegfeld1=inv.get("filename", "")[:36],
                buchungstext=f"{provider} Rechnung"[:60]
            )

            row = buchung.to_row()
            output.write(";".join(row) + "\n")

        csv_content = output.getvalue()

        # Speichern falls Pfad angegeben
        if output_path:
            output_path = Path(output_path)
            # DATEV erwartet Windows ANSI (cp1252)
            with open(output_path, "w", encoding="cp1252", errors="replace") as f:
                f.write(csv_content)
            return str(output_path)

        return csv_content


def export_invoices_datev(
    invoices: List[dict],
    output_path: str,
    berater_nr: str = "12345",
    mandant_nr: str = "67890"
) -> str:
    """
    Convenience-Funktion für DATEV-Export.

    Args:
        invoices: Liste von Invoice-Dicts
        output_path: Ausgabepfad
        berater_nr: DATEV Beraternummer
        mandant_nr: DATEV Mandantennummer

    Returns:
        str: Pfad zur exportierten Datei
    """
    config = DATEVConfig(
        berater_nr=berater_nr,
        mandant_nr=mandant_nr
    )
    exporter = DATEVExporter(config)
    return exporter.export(invoices, Path(output_path))
