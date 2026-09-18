# Windows Store Vorbereitung & Release-Readiness — UniversalInvoiceMail

**Stand:** 2026-09-18
**Version:** 2.3.0.0
**Package-ID:** `Geiger.UniversalInvoiceMail`
**Publisher:** `CN=52596601-BAB4-4F3F-B182-E8F3F273B202` (Lukas Geiger)
**Status:** Release-Ready & Staged für Welle-2-Freigabe (Preflight 25/25 Kriterien erfüllt, 0 Findings)

---

## 1. Artefakt- & Dokumentenstatus

| Artefakt | Status | Anmerkung |
|---|---|---|
| `store_package.json` | OK | v2.3.0.0, Identity `Geiger.UniversalInvoiceMail`, Publisher CN, Lizenz MIT, Kategorie Productivity, DE+EN |
| `STORE_LISTING.md` | OK | DE+EN Listing-Texte vollständig, Richtlinie 10.1.3 konform (exakt 7 Keywords <= 30 Zeichen, keine Markennamen) |
| `PRIVACY_POLICY.md` | OK | DE+EN, Offline-Invariante garantiert, lokaler Schlüsselspeicher & Anwendungsdatenordner `%APPDATA%\UniversalInvoiceMail\` |
| `SUPPORT.md` | OK | DE+EN, Support-URL, FAQ, Systemanforderungen |
| `THIRD_PARTY_LICENSES.txt` | OK | PySide6 (LGPL), pypdfium2 (Apache/BSD), Pillow, keyring |
| `PORTIERUNGSPLAN.md` | OK | Mehrziel-Architektur (Desktop P0, Store P0, Web/PWA Companion P1, macOS/Linux P2) & Invoice-Bundle-Format v1 |
| Store-Kacheln (`store_package/UniversalInvoiceMail/icons/`) | OK | 5 quadratische/rechteckige Kacheln (`icon_44x44.png`, `icon_50x50.png`, `StoreLogo.png`, `icon_150x150.png`, `icon_310x150.png`, `icon_310x310.png`) + `SplashScreen.png` (620x300) |
| Packaging-Staging (`releases/windowsstore/`) | OK | Vollständiges Staging analog zu ProSync/HausLagerist (`BUILD.md`, `store_settings.json`, `store_listing_de.md`, `store_listing_en.md`, `WACK_PROTOCOL.md`, `StoreLogo.png`, `screenshots/`) |
| Legacy-Assets (`store_assets/`) | OK | Gespiegelt für ältere Build-Pipelines inkl. `AppxManifest.xml` |
| Store-Screenshots (4x 16:9) | OK | 1920x1080 in `releases/windowsstore/screenshots/`, `store_package/UniversalInvoiceMail/screenshots/` und `README/screenshots/store/` |
| Preflight-Store-Auditor | OK | `scripts/check_store_readiness.py` (25/25 Kriterien bestanden, 0 Findings) |
| Asset-Generator | OK | `scripts/store_assets.py` (erzeugt Icons, Kacheln und AppxManifest mit 50x50 StoreLogo) |
| Screenshot-Generator | OK | `scripts/generate_store_screenshots.py` (hochauflösende 16:9 PNG-Präsentationsframes) |
| Test-Abdeckung | OK | Vollständige Test-Suite für Store-Readiness, Asset-Validierung, Release-Staging und Listing-Compliance |

---

## 2. Partner Center Richtlinie 10.1.3 Compliance (Suchbegriffe)

- **Regel:** Maximal 7 Suchbegriffe pro Sprache, jeweils maximal 30 Zeichen, keine fremden Markennamen.
- **Deutsch (7):** `Rechnungsverwaltung`, `Mailabruf`, `DATEV Export`, `Rechnungsarchiv`, `PDF Konverter`, `Belegerfassung`, `Buchhaltung`
- **Englisch (7):** `Invoice Manager`, `Email Fetcher`, `DATEV Export`, `Invoice Archive`, `PDF Converter`, `Receipt Capture`, `Accounting Tool`

---

## 3. AppxManifest.xml Konfiguration

- **Identity Name:** `Geiger.UniversalInvoiceMail`
- **Publisher:** `CN=52596601-BAB4-4F3F-B182-E8F3F273B202`
- **Version:** `2.3.0.0`
- **Capabilities:** `<rescap:Capability Name="runFullTrust" />` (erforderlich für Dateisystemzugriff, Netzwerkzugriff auf IMAP-Server und Windows Credential Manager Interaktion)
- **Visual Elements:** Kachel-Icons in allen Standardauflösungen und Splash-Screen integriert.

---

## 4. Audit & Verifikation

```powershell
# Preflight Store Readiness Audit (21 Prüfungen)
python scripts/check_store_readiness.py

# Kachel- & Manifest-Generierung
python scripts/store_assets.py

# 16:9 Screenshots erzeugen
python scripts/generate_store_screenshots.py

# Test-Suite ausführen
pytest tests/test_store_readiness.py tests/test_store_assets.py tests/test_store_materials.py
```
