#!/usr/bin/env python3
"""Preflight Windows Store readiness audit for UniversalInvoiceMail."""

from __future__ import annotations

import argparse
import json
import re
import struct
from pathlib import Path
from xml.etree import ElementTree as ET

REQUIRED_CANONICAL_PUBLISHER = "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"

REQUIRED_DOCUMENTS = [
    "UniversalInvoiceMail.spec",
    "scripts/build_windows_exe.ps1",
    "store_package.json",
    "STORE_LISTING.md",
    "PRIVACY_POLICY.md",
    "SUPPORT.md",
    "THIRD_PARTY_LICENSES.txt",
    "WINDOWS_STORE_PREP.md",
    "PORTIERUNGSPLAN.md",
    "scripts/store_assets.py",
    "scripts/generate_store_screenshots.py",
]

REQUIRED_STORE_ICONS = {
    "icon_44x44.png": (44, 44),
    "icon_50x50.png": (50, 50),
    "icon_150x150.png": (150, 150),
    "icon_310x150.png": (310, 150),
    "icon_310x310.png": (310, 310),
    "SplashScreen.png": (620, 300),
}

REQUIRED_LEGACY_STORE_ASSETS = [
    "Square44x44Logo.png",
    "StoreLogo.png",
    "Square150x150Logo.png",
    "Square310x310Logo.png",
    "Wide310x150Logo.png",
    "SplashScreen.png",
    "AppxManifest.xml",
]

REQUIRED_STORE_SCREENSHOTS = [
    "01_rechnungsuebersicht.png",
    "02_postfach_konfiguration.png",
    "03_datev_export.png",
    "04_bundle_companion.png",
]

RESTRICTED_TRADEMARKS = [
    "windows",
    "microsoft",
    "office",
    "word",
    "apple",
    "ios",
    "android",
    "google",
]


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path.name} ist keine gültige PNG-Datei")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def run_store_readiness_check(
    project_root: Path | None = None,
    *,
    require_executable: bool = False,
) -> list[str]:
    if project_root is None:
        project_root = Path(__file__).resolve().parents[1]

    findings: list[str] = []

    # 1. Document Existence Check
    for doc in REQUIRED_DOCUMENTS:
        doc_path = project_root / doc
        if not doc_path.exists():
            findings.append(f"Fehlendes Store-Pflichtdokument: {doc}")

    # 2. Package JSON Validation
    package_json_path = project_root / "store_package.json"
    package_data: dict = {}
    if package_json_path.exists():
        try:
            with open(package_json_path, "r", encoding="utf-8") as f:
                package_data = json.load(f)

            app_name = package_data.get("app_name")
            if app_name != "UniversalInvoiceMail":
                findings.append(f"Ungültiger app_name in store_package.json: {app_name}")

            identity_name = package_data.get("identity_name") or package_data.get("package_id")
            if identity_name != "Geiger.UniversalInvoiceMail":
                findings.append(f"Ungültiger identity_name / package_id: {identity_name}")

            publisher = package_data.get("publisher") or package_data.get("publisher_id")
            if publisher != REQUIRED_CANONICAL_PUBLISHER:
                findings.append(f"Publisher stimmt nicht mit kanonischem CN überein: {publisher}")

            version = package_data.get("version", "")
            if not re.match(r"^\d+\.\d+\.\d+\.\d+$", version):
                findings.append(f"Ungültiges Versionsformat in store_package.json: {version}")

            capabilities = package_data.get("capabilities", "")
            cap_str = capabilities if isinstance(capabilities, str) else " ".join(capabilities)
            if "runFullTrust" not in cap_str:
                findings.append("Fehlende Berechtigung runFullTrust in store_package.json")

            languages = package_data.get("languages", [])
            if len(languages) < 2:
                findings.append("Mindestens 2 Sprachen (de-DE, en-US) in store_package.json gefordert")

        except Exception as e:
            findings.append(f"store_package.json ist kein gültiges JSON: {e}")

    # 3. Executable Validation (if required)
    if require_executable:
        exe_name = package_data.get("executable", "UniversalInvoiceMail.exe")
        exe_path = project_root / "dist" / "UniversalInvoiceMail" / exe_name
        if not exe_path.exists():
            findings.append(f"Store-Executable nicht gefunden: {exe_path}")

    # 4. Store Listing (DE/EN) & Partner Center Policy 10.1.3 Compliance
    store_listing_path = project_root / "STORE_LISTING.md"
    if store_listing_path.exists():
        content = store_listing_path.read_text(encoding="utf-8")

        if "## Deutsch" not in content and "## German" not in content and "# Deutsch" not in content:
            findings.append("STORE_LISTING.md: Deutscher Abschnitt fehlt")
        if "## English" not in content and "# English" not in content:
            findings.append("STORE_LISTING.md: Englischer Abschnitt fehlt")

        # Policy 10.1.3 Keywords Audit
        de_match = re.search(r"### Schlüsselwörter[^\n]*\n+([^\n#]+)", content)
        if de_match:
            de_raw = de_match.group(1).strip()
            de_keywords = [k.strip() for k in de_raw.split(",") if k.strip()]
            if len(de_keywords) > 7:
                findings.append(
                    f"Partner Center Richtlinie 10.1.3 Verstoß: {len(de_keywords)} deutsche Keywords (> 7)"
                )
            for kw in de_keywords:
                if len(kw) > 30:
                    findings.append(f"Keyword zu lang (>30 Zeichen): '{kw}'")
                for tm in RESTRICTED_TRADEMARKS:
                    if tm in kw.lower():
                        findings.append(f"Markenname '{tm}' in deutschem Keyword gefunden: '{kw}'")
        else:
            findings.append("STORE_LISTING.md: Abschnitt '### Schlüsselwörter' nicht gefunden")

        en_match = re.search(r"### Keywords[^\n]*\n+([^\n#]+)", content)
        if en_match:
            en_raw = en_match.group(1).strip()
            en_keywords = [k.strip() for k in en_raw.split(",") if k.strip()]
            if len(en_keywords) > 7:
                findings.append(
                    f"Partner Center Richtlinie 10.1.3 Verstoß: {len(en_keywords)} englische Keywords (> 7)"
                )
            for kw in en_keywords:
                if len(kw) > 30:
                    findings.append(f"Keyword zu lang (>30 Zeichen): '{kw}'")
                for tm in RESTRICTED_TRADEMARKS:
                    if tm in kw.lower():
                        findings.append(f"Markenname '{tm}' in englischem Keyword gefunden: '{kw}'")
        else:
            findings.append("STORE_LISTING.md: Abschnitt '### Keywords' nicht gefunden")

        if "Screenshots" not in content:
            findings.append("STORE_LISTING.md: Screenshots-Tabelle fehlt")

    # 5. Privacy Policy Compliance
    privacy_path = project_root / "PRIVACY_POLICY.md"
    if privacy_path.exists():
        p_text = privacy_path.read_text(encoding="utf-8").lower()
        if "lokal" not in p_text and "local" not in p_text:
            findings.append("PRIVACY_POLICY.md erwähnt keine lokale Datenhaltung")
        if "keyring" not in p_text and "credential" not in p_text and "schlüssel" not in p_text:
            findings.append("PRIVACY_POLICY.md erwähnt keine sichere Schlüsselverwaltung")

    # 6. Support Documentation
    support_path = project_root / "SUPPORT.md"
    if support_path.exists():
        s_text = support_path.read_text(encoding="utf-8")
        if "http" not in s_text and "github.com" not in s_text:
            findings.append("SUPPORT.md enthält keine URL oder Kontaktmöglichkeit")

    # 7. Store Package Icons
    icons_dir = project_root / "store_package" / "UniversalInvoiceMail" / "icons"
    if not icons_dir.exists():
        findings.append(f"Icons-Verzeichnis fehlt: {icons_dir}")
    else:
        for icon_name, (req_w, req_h) in REQUIRED_STORE_ICONS.items():
            icon_file = icons_dir / icon_name
            if not icon_file.exists():
                findings.append(f"Store-Icon fehlt: {icon_name}")
            else:
                try:
                    w, h = _png_size(icon_file)
                    if (w, h) != (req_w, req_h):
                        findings.append(
                            f"Falsche Bildgröße für {icon_name}: ({w}, {h}) statt ({req_w}, {req_h})"
                        )
                except Exception as err:
                    findings.append(f"Fehler beim Lesen von {icon_name}: {err}")

    # 8. Legacy Store Assets
    store_assets_dir = project_root / "store_assets"
    if not store_assets_dir.exists():
        findings.append(f"store_assets Verzeichnis fehlt: {store_assets_dir}")
    else:
        for asset_name in REQUIRED_LEGACY_STORE_ASSETS:
            asset_file = store_assets_dir / asset_name
            if not asset_file.exists():
                findings.append(f"Legacy Store-Asset fehlt in store_assets: {asset_name}")

    # 9. Store Screenshots Validation (16:9, >=1366x768)
    screenshots_dirs = [
        project_root / "store_package" / "UniversalInvoiceMail" / "screenshots",
        project_root / "README" / "screenshots" / "store",
    ]
    for s_dir in screenshots_dirs:
        if not s_dir.exists():
            findings.append(f"Screenshots-Verzeichnis fehlt: {s_dir}")
        else:
            for s_name in REQUIRED_STORE_SCREENSHOTS:
                s_file = s_dir / s_name
                if not s_file.exists():
                    findings.append(f"Store-Screenshot fehlt in {s_dir.name}: {s_name}")
                else:
                    try:
                        w, h = _png_size(s_file)
                        if w < 1366 or h < 768:
                            findings.append(f"Screenshot {s_name} zu klein (<1366x768): ({w}, {h})")
                        aspect = round(w / h, 2)
                        if aspect != 1.78:
                            findings.append(
                                f"Screenshot {s_name} hat kein 16:9-Format: ({w}, {h}, ratio {aspect})"
                            )
                    except Exception as err:
                        findings.append(f"Fehler beim Prüfen von Screenshot {s_name}: {err}")

    # 10. AppxManifest.xml Validation
    manifest_path = project_root / "store_package" / "UniversalInvoiceMail" / "AppxManifest.xml"
    if not manifest_path.exists():
        findings.append(f"AppxManifest.xml fehlt: {manifest_path}")
    else:
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()

            ns = {
                "m": "http://schemas.microsoft.com/appx/manifest/foundation/windows10",
                "uap": "http://schemas.microsoft.com/appx/manifest/uap/windows10",
                "rescap": "http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities",
            }

            identity = root.find("m:Identity", ns)
            if identity is None:
                findings.append("AppxManifest.xml: Identity-Element fehlt")
            else:
                if identity.attrib.get("Name") != "Geiger.UniversalInvoiceMail":
                    findings.append(f"AppxManifest.xml: Falscher Name: {identity.attrib.get('Name')}")
                if identity.attrib.get("Publisher") != REQUIRED_CANONICAL_PUBLISHER:
                    findings.append(
                        f"AppxManifest.xml: Falscher Publisher: {identity.attrib.get('Publisher')}"
                    )

            run_full_trust = False
            for cap in root.findall(".//rescap:Capability", ns):
                if cap.attrib.get("Name") == "runFullTrust":
                    run_full_trust = True
                    break
            if not run_full_trust:
                findings.append("AppxManifest.xml: restrictedcapability runFullTrust fehlt")

            app_node = root.find(".//m:Application", ns)
            if app_node is not None:
                exe = app_node.attrib.get("Executable")
                if exe != "UniversalInvoiceMail.exe":
                    findings.append(f"AppxManifest.xml: Falsches Executable: {exe}")

        except Exception as e:
            findings.append(f"AppxManifest.xml ist kein valides XML: {e}")

    # 11. Portierungsplan Integrity
    port_plan_path = project_root / "PORTIERUNGSPLAN.md"
    if port_plan_path.exists():
        p_text = port_plan_path.read_text(encoding="utf-8")
        if "Windows Desktop" not in p_text:
            findings.append("PORTIERUNGSPLAN.md erwähnt Windows Desktop nicht")
        if "Windows Store" not in p_text:
            findings.append("PORTIERUNGSPLAN.md erwähnt Windows Store nicht")
        if "universalinvoicemail-invoicebundle-v1" not in p_text:
            findings.append("PORTIERUNGSPLAN.md erwähnt Bundle-Format v1 nicht")

    # 12. PyInstaller Spec Validation
    spec_path = project_root / "UniversalInvoiceMail.spec"
    if spec_path.exists():
        spec_text = spec_path.read_text(encoding="utf-8")
        if "console=False" not in spec_text:
            findings.append("UniversalInvoiceMail.spec: console=False fehlt")
        if "name='UniversalInvoiceMail'" not in spec_text and 'name="UniversalInvoiceMail"' not in spec_text:
            findings.append("UniversalInvoiceMail.spec: name='UniversalInvoiceMail' fehlt")

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight Store Readiness Audit")
    parser.add_argument(
        "--require-exe",
        action="store_true",
        help="Prüft zwingend das Vorhandensein des kompilierten Executables",
    )
    args = parser.parse_args()

    findings = run_store_readiness_check(require_executable=args.require_exe)
    if findings:
        print(f"[FEHLER] Preflight-Store-Audit fehlgeschlagen ({len(findings)} Findings):")
        for f in findings:
            print(f"  - {f}")
        return 1

    print("[OK] Preflight-Store-Audit erfolgreich: Alle 21 Kriterien erfuellt (0 Findings)!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
