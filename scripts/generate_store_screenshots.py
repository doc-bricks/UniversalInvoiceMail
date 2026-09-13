"""
Generate high-resolution Microsoft Store screenshots (1920x1080, 16:9) for UniversalInvoiceMail.

Creates 4 compliant presentation frames:
1. 01_rechnungsuebersicht.png: Rechnungszentrale & Automatischer Mailabruf (Inbox, PDF, Status)
2. 02_postfach_konfiguration.png: Sichere Postfach-Verwaltung & Keyring-Schutz (IMAP, Gmail API, Keyring)
3. 03_datev_export.png: DATEV Buchungsstapel & Konten-Mapping (GoBD, SKR03/SKR04 CSV cp1252)
4. 04_bundle_companion.png: Datensparsamer Bundle-Austausch & PWA Mobile Companion
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "README" / "screenshots" / "store"
STORE_PACKAGE_SCREENSHOTS_DIR = PROJECT_ROOT / "store_package" / "UniversalInvoiceMail" / "screenshots"
MAIN_SCREENSHOT = PROJECT_ROOT / "README" / "screenshots" / "main.png"
ICON_PATH = PROJECT_ROOT / "UniversalInvoiceMail_icon.png"

CANVAS_SIZE = (1920, 1080)

# Colors
BG_GRADIENT_TOP = (246, 248, 252)
BG_GRADIENT_BOTTOM = (232, 238, 246)
CARD_BG = (255, 255, 255)
HEADER_COLOR = (24, 38, 59)
SUBTITLE_COLOR = (71, 85, 105)
PRIMARY_ACCENT = (14, 116, 144)      # Cyan/Teal (#0e7490)
SECONDARY_ACCENT = (2, 132, 199)    # Sky blue (#0284c7)
SUCCESS_COLOR = (22, 163, 74)        # Green
BADGE_BG = (236, 254, 255)           # Light cyan
BORDER_COLOR = (226, 232, 240)
TEXT_DARK = (30, 41, 59)
TEXT_MUTED = (100, 116, 139)


def _get_font(size: int, bold: bool = False) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    font_names = (
        ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]
        if bold
        else ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"]
    )
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def _create_canvas() -> Image.Image:
    base = Image.new("RGB", CANVAS_SIZE, BG_GRADIENT_TOP)
    draw = ImageDraw.Draw(base)
    top_r, top_g, top_b = BG_GRADIENT_TOP
    bot_r, bot_g, bot_b = BG_GRADIENT_BOTTOM
    height = CANVAS_SIZE[1]
    for y in range(height):
        factor = y / height
        r = int(top_r + (bot_r - top_r) * factor)
        g = int(top_g + (bot_g - top_g) * factor)
        b = int(top_b + (bot_b - top_b) * factor)
        draw.line([(0, y), (CANVAS_SIZE[0], y)], fill=(r, g, b))
    return base


def _draw_header(
    canvas: Image.Image,
    draw: ImageDraw.Draw,
    title: str,
    subtitle: str,
    badge: str = "UniversalInvoiceMail | Windows Store Edition",
) -> None:
    badge_font = _get_font(18, bold=True)
    draw.rounded_rectangle((80, 48, 540, 84), radius=8, fill=BADGE_BG, outline=PRIMARY_ACCENT, width=1)
    draw.text((96, 54), badge, fill=PRIMARY_ACCENT, font=badge_font)

    title_font = _get_font(42, bold=True)
    draw.text((80, 96), title, fill=HEADER_COLOR, font=title_font)

    sub_font = _get_font(22, bold=False)
    draw.text((80, 150), subtitle, fill=SUBTITLE_COLOR, font=sub_font)

    if ICON_PATH.exists():
        try:
            with Image.open(ICON_PATH) as icon:
                icon_resized = icon.convert("RGBA").resize((96, 96), Image.Resampling.LANCZOS)
                canvas.paste(icon_resized, (1744, 48), icon_resized)
        except Exception:
            pass


def _draw_feature_list(
    draw: ImageDraw.Draw,
    items: list[tuple[str, str]],
    box: tuple[int, int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle((x0, y0, x1, y1), radius=16, fill=CARD_BG, outline=BORDER_COLOR, width=2)

    title_font = _get_font(22, bold=True)
    head_font = _get_font(18, bold=True)
    desc_font = _get_font(15, bold=False)

    draw.text((x0 + 32, y0 + 28), "Wichtigste Funktionen & Highlights", fill=HEADER_COLOR, font=title_font)
    draw.line((x0 + 32, y0 + 64, x1 - 32, y0 + 64), fill=BORDER_COLOR, width=1)

    curr_y = y0 + 84
    for title, desc in items:
        draw.rounded_rectangle((x0 + 32, curr_y, x0 + 62, curr_y + 30), radius=6, fill=(236, 253, 245), outline=SUCCESS_COLOR, width=1)
        draw.text((x0 + 40, curr_y + 4), "✓", fill=SUCCESS_COLOR, font=head_font)

        draw.text((x0 + 76, curr_y + 2), title, fill=TEXT_DARK, font=head_font)
        draw.text((x0 + 76, curr_y + 28), desc, fill=TEXT_MUTED, font=desc_font)
        curr_y += 74


def _embed_ui_image(
    canvas: Image.Image,
    img: Image.Image,
    box: tuple[int, int, int, int],
    crop_box: tuple[int, int, int, int] | None = None,
    caption: str = "UniversalInvoiceMail — Lokale Rechnungszentrale",
) -> None:
    x0, y0, x1, y1 = box
    target_w = x1 - x0
    target_h = y1 - y0

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((x0, y0, x1, y1), radius=14, fill=CARD_BG, outline=BORDER_COLOR, width=2)

    tb_h = 36
    draw.rounded_rectangle((x0, y0, x1, y0 + tb_h), radius=12, fill=(241, 245, 249))
    draw.rectangle((x0, y0 + 20, x1, y0 + tb_h), fill=(241, 245, 249))
    draw.line((x0, y0 + tb_h, x1, y0 + tb_h), fill=BORDER_COLOR, width=1)

    draw.ellipse((x0 + 16, y0 + 12, x0 + 26, y0 + 22), fill=(239, 68, 68))
    draw.ellipse((x0 + 34, y0 + 12, x0 + 44, y0 + 22), fill=(245, 158, 11))
    draw.ellipse((x0 + 52, y0 + 12, x0 + 62, y0 + 22), fill=(34, 197, 94))

    title_font = _get_font(13, bold=False)
    draw.text((x0 + 76, y0 + 10), caption, fill=TEXT_MUTED, font=title_font)

    inner_w = target_w - 4
    inner_h = target_h - tb_h - 4
    to_fit = img
    if crop_box:
        to_fit = to_fit.crop(crop_box)

    scaled = ImageOps.fit(to_fit, (inner_w, inner_h), Image.Resampling.LANCZOS)
    canvas.paste(scaled, (x0 + 2, y0 + tb_h + 2))


def generate_screenshot_01(ui_image: Image.Image) -> Image.Image:
    canvas = _create_canvas()
    draw = ImageDraw.Draw(canvas)
    _draw_header(
        canvas,
        draw,
        "Rechnungszentrale & Automatischer Mailabruf",
        "E-Mail-Postfächer, Belege, PDF-Konvertierung & Rechnungsstatus im direkten Überblick",
    )

    _embed_ui_image(canvas, ui_image, (80, 205, 1260, 990))

    features = [
        ("Lokaler Mailabruf", "Rechnungen per IMAP oder Gmail ohne Drittanbieter-Cloud abrufen"),
        ("Multi-Format Konverter", "Bilder, EML, MSG, DOCX und XLSX lokal in PDF umwandeln"),
        ("Integrierte OCR-Prüfung", "Texterkennung und Metadaten-Prüfung für gescannte Belege"),
        ("Status & Betragskontrolle", "Geprüft, bezahlt und DATEV-Exportstatus direkt im Blick"),
    ]
    _draw_feature_list(draw, features, (1290, 205, 1840, 600))

    draw.rounded_rectangle((1290, 620, 1840, 990), radius=16, fill=CARD_BG, outline=BORDER_COLOR, width=2)
    card_title_font = _get_font(20, bold=True)
    draw.text((1320, 646), "Sicherheit & Rechnungsstandards", fill=HEADER_COLOR, font=card_title_font)
    draw.line((1320, 680, 1810, 680), fill=BORDER_COLOR, width=1)

    badges = [
        ("100% Offline-Fähig", "Alle Belege und Metadaten bleiben auf Ihrem Computer"),
        ("DATEV EXTF Format", "Standardisierter CSV-Buchungsstapel nach GoBD"),
        ("Windows Store", "Signiertes MSIX-Paket mit nativer Windows-Integration"),
        ("Zero-Cloud-Zwang", "Keine versteckten Gebühren, keine Abo-Bindung"),
    ]
    y_badge = 700
    badge_title_font = _get_font(16, bold=True)
    badge_sub_font = _get_font(14, bold=False)
    for b_title, b_desc in badges:
        draw.rounded_rectangle((1320, y_badge, 1490, y_badge + 32), radius=6, fill=BADGE_BG, outline=PRIMARY_ACCENT, width=1)
        draw.text((1330, y_badge + 6), b_title, fill=PRIMARY_ACCENT, font=badge_title_font)
        draw.text((1505, y_badge + 6), b_desc, fill=TEXT_DARK, font=badge_sub_font)
        y_badge += 64

    return canvas


def generate_screenshot_02(ui_image: Image.Image) -> Image.Image:
    canvas = _create_canvas()
    draw = ImageDraw.Draw(canvas)
    _draw_header(
        canvas,
        draw,
        "Sichere Postfach-Verwaltung & Keyring-Schutz",
        "IMAP, Gmail API & Windows Credential Manager für maximale Sicherheit ohne Klartext-Passwörter",
        badge="Postfach-Verwaltung & Sicherheit",
    )

    w, h = ui_image.size
    crop_area = (int(w * 0.05), int(h * 0.10), int(w * 0.95), int(h * 0.85))
    _embed_ui_image(
        canvas, ui_image, (640, 205, 1840, 990),
        crop_box=crop_area,
        caption="Kontenverwaltung — IMAP, Gmail OAuth und Windows Credential Manager",
    )

    features = [
        ("Keyring-Verschlüsselung", "Passwörter liegen im Windows Anmeldeinformations-Manager"),
        ("Mehrere Konten", "Beliebig viele IMAP- und Gmail-Postfächer konfigurieren"),
        ("Gmail OAuth2", "Sichere Autorisierung über Google-Tokens ohne Passwortspeicherung"),
        ("Gezielte Filterung", "Nur E-Mails mit Rechnungsbezug und PDF-Anhängen laden"),
    ]
    _draw_feature_list(draw, features, (80, 205, 610, 600))

    draw.rounded_rectangle((80, 620, 610, 990), radius=16, fill=CARD_BG, outline=BORDER_COLOR, width=2)
    card_title_font = _get_font(20, bold=True)
    draw.text((110, 646), "Schutz Ihrer Anmeldedaten", fill=HEADER_COLOR, font=card_title_font)
    draw.line((110, 680, 580, 680), fill=BORDER_COLOR, width=1)

    bullets = [
        "Keine Klartext-Passwörter in Konfigurationsdateien",
        "OAuth-Tokens verbleiben strikt auf Ihrem Endgerät",
        "SSL/TLS-Verschlüsselung für alle Mailabrufe",
        "Ausschließlich direkte Verbindungen zu Ihren Mailservern",
    ]
    b_y = 705
    bullet_font = _get_font(15, bold=False)
    for b in bullets:
        draw.text((110, b_y), "•", fill=PRIMARY_ACCENT, font=card_title_font)
        draw.text((130, b_y + 2), b, fill=TEXT_DARK, font=bullet_font)
        b_y += 62

    return canvas


def generate_screenshot_03(ui_image: Image.Image) -> Image.Image:
    canvas = _create_canvas()
    draw = ImageDraw.Draw(canvas)
    _draw_header(
        canvas,
        draw,
        "DATEV-Export & Finanzbuchhaltung",
        "GoBD-konforme Buchungsstapel (CSV cp1252) für Steuerberater und Buchhaltungssoftware",
        badge="DATEV & Buchhaltungsschnittstelle",
    )

    w, h = ui_image.size
    crop_area = (int(w * 0.10), int(h * 0.15), int(w * 0.90), int(h * 0.90))
    _embed_ui_image(
        canvas, ui_image, (80, 205, 1260, 990),
        crop_box=crop_area,
        caption="DATEV Buchungsstapel — Kontenrahmen SKR03 / SKR04 & Beleg-Mapping",
    )

    features = [
        ("DATEV EXTF-Export", "Standardisierter CSV-Buchungsstapel im Windows-Format (cp1252)"),
        ("SKR03 / SKR04 Support", "Einfaches Mapping von Sachkonten und Gegenkonten"),
        ("Plausibilitätsprüfung", "Validiert Steuersätze, Belegnummern und Datumsangaben"),
        ("Belegarchiv-Verknüpfung", "Eindeutige Dateinamen für revisionssichere Ablage"),
    ]
    _draw_feature_list(draw, features, (1290, 205, 1840, 600))

    draw.rounded_rectangle((1290, 620, 1840, 990), radius=16, fill=CARD_BG, outline=BORDER_COLOR, width=2)
    card_title_font = _get_font(20, bold=True)
    draw.text((1320, 646), "Buchhaltung ohne Medienbrüche", fill=HEADER_COLOR, font=card_title_font)
    draw.line((1320, 680, 1810, 680), fill=BORDER_COLOR, width=1)

    stats = [
        ("1-Klick Export", "DATEV-Stapel direkt für den Steuerberater ausgeben"),
        ("Steuersatz-Erkennung", "Automatische Zuordnung von 19%, 7% oder steuerfrei"),
        ("Historie & Logging", "Jeder Export wird mit Zeitstempel und Hash protokolliert"),
        ("Revisionssicherheit", "Dokumente und Buchungszeilen bleiben konsistent"),
    ]
    s_y = 700
    stat_title_font = _get_font(16, bold=True)
    stat_sub_font = _get_font(14, bold=False)
    for s_title, s_desc in stats:
        draw.rounded_rectangle((1320, s_y, 1490, s_y + 32), radius=6, fill=BADGE_BG, outline=PRIMARY_ACCENT, width=1)
        draw.text((1330, s_y + 6), s_title, fill=PRIMARY_ACCENT, font=stat_title_font)
        draw.text((1505, s_y + 6), s_desc, fill=TEXT_DARK, font=stat_sub_font)
        s_y += 64

    return canvas


def generate_screenshot_04(ui_image: Image.Image) -> Image.Image:
    canvas = _create_canvas()
    draw = ImageDraw.Draw(canvas)
    _draw_header(
        canvas,
        draw,
        "PWA Mobile Companion & Bundle-Austausch",
        "Datensparsamer, offline-fähiger Austausch mit Mobilgeräten ohne Cloud-Server",
        badge="Mobile Companion & Datensparsamkeit",
    )

    w, h = ui_image.size
    crop_area = (int(w * 0.15), int(h * 0.05), int(w * 0.95), int(h * 0.95))
    _embed_ui_image(
        canvas, ui_image, (640, 205, 1840, 990),
        crop_box=crop_area,
        caption="Invoice Bundle — Redigierter JSON-Austausch mit PWA Web Companion",
    )

    features = [
        ("Redigierter Bundle-Export", "Keine Passwörter, Tokens oder Mail-Bodies in der Exportdatei"),
        ("Plattformunabhängig", "Öffnen und Prüfen auf Smartphone, Tablet oder Laptop im Browser"),
        ("Reimport von Prüfdaten", "Mobil gesetzte Beträge und Freigaben fließen sicher zurück"),
        ("100% Lokaler Transfer", "Dateibasierter Austausch ohne Registrierung oder Clouddienst"),
    ]
    _draw_feature_list(draw, features, (80, 205, 610, 600))

    draw.rounded_rectangle((80, 620, 610, 990), radius=16, fill=CARD_BG, outline=BORDER_COLOR, width=2)
    card_title_font = _get_font(20, bold=True)
    draw.text((110, 646), "Datenschutz-Garantie", fill=HEADER_COLOR, font=card_title_font)
    draw.line((110, 680, 580, 680), fill=BORDER_COLOR, width=1)

    bullets = [
        "Streng geprüfter universeller Schema-Standard (v1)",
        "Secrets-freie JSON-Dateien für mobile Begleiter",
        "Hash-basierte Konflikterkennung beim Desktop-Reimport",
        "Optimale Ergänzung für papierlose Arbeitsabläufe",
    ]
    b_y = 705
    bullet_font = _get_font(15, bold=False)
    for b in bullets:
        draw.text((110, b_y), "•", fill=PRIMARY_ACCENT, font=card_title_font)
        draw.text((130, b_y + 2), b, fill=TEXT_DARK, font=bullet_font)
        b_y += 62

    return canvas


def generate_all_screenshots(
    out_dir: Path = OUTPUT_DIR,
    package_dir: Path = STORE_PACKAGE_SCREENSHOTS_DIR,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    package_dir.mkdir(parents=True, exist_ok=True)

    if not MAIN_SCREENSHOT.exists():
        raise FileNotFoundError(f"Haupt-Screenshot fehlt: {MAIN_SCREENSHOT}")

    with Image.open(MAIN_SCREENSHOT) as img:
        ui_img = img.convert("RGB")

    generators = [
        ("01_rechnungsuebersicht.png", generate_screenshot_01),
        ("02_postfach_konfiguration.png", generate_screenshot_02),
        ("03_datev_export.png", generate_screenshot_03),
        ("04_bundle_companion.png", generate_screenshot_04),
    ]

    generated: list[Path] = []
    for filename, gen_fn in generators:
        canvas = gen_fn(ui_img)
        target_path = out_dir / filename
        canvas.save(target_path, format="PNG", quality=95)
        pkg_target = package_dir / filename
        canvas.save(pkg_target, format="PNG", quality=95)
        generated.append(target_path)
        print(f"Generated: {target_path.relative_to(PROJECT_ROOT)}")

    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUTPUT_DIR, help="Ausgabeverzeichnis")
    parser.add_argument("--package-out", type=Path, default=STORE_PACKAGE_SCREENSHOTS_DIR, help="Store Package Verzeichnis")
    args = parser.parse_args()

    try:
        generate_all_screenshots(out_dir=args.out, package_dir=args.package_out)
        return 0
    except Exception as exc:
        print(f"Fehler bei Screenshot-Generierung: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
