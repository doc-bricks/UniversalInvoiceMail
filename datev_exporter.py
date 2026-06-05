# -*- coding: utf-8 -*-
"""
DATEV-Export Modul für UniversalInvoiceMail
============================================

Exportiert Rechnungen als DATEV-Buchungsstapel (CSV-Format).

Erstellt: 2026-01-12
Version: 1.0.0
"""

import csv
import io
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

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


class DATEVExporter:
    """
    Exportiert Rechnungen im DATEV-Buchungsstapel Format.

    Format: CSV mit Semikolon-Trennung, Windows ANSI
    """

    # Spaltenüberschriften für Zeile 2
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

        # Auffüllen auf ca. 33 Felder
        while len(header) < 33:
            header.append('')

        return ";".join(header)

    def _get_konten(self, provider: str) -> Tuple[int, int]:
        """Ermittelt Konto und Gegenkonto für einen Provider."""
        # Exakte Übereinstimmung
        if provider in self.config.konten_mapping:
            return self.config.konten_mapping[provider]

        # Teilübereinstimmung (case-insensitive)
        provider_lower = provider.lower()
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


# ==================== TEST ====================

if __name__ == "__main__":
    # Beispiel-Rechnungen
    test_invoices = [
        {
            "provider": "Amazon",
            "filename": "AMZ-2026-001.pdf",
            "date": "2026-01-05",
            "path": "/tmp/AMZ-2026-001.pdf",
            "amount": 119.00,
            "category": "Amazon"
        },
        {
            "provider": "Vodafone",
            "filename": "VOD-2026-001.pdf",
            "date": "2026-01-15",
            "path": "/tmp/VOD-2026-001.pdf",
            "amount": 45.99,
            "category": "Vodafone"
        },
        {
            "provider": "Temu",
            "filename": "TEMU-2026-001.pdf",
            "date": "2026-01-10",
            "path": "/tmp/TEMU-2026-001.pdf",
            "amount": 23.50,
            "category": "Temu"
        }
    ]

    # Export testen
    exporter = DATEVExporter()
    result = exporter.export(test_invoices)
    print("=== DATEV Export Test ===")
    print(result)
