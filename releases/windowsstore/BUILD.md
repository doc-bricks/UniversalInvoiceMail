# UniversalInvoiceMail - Windows Store Build- & Packaging-Anleitung

## Voraussetzungen

1. Python 3.10+ mit PySide6, pypdfium2, Pillow, keyring
2. PyInstaller für den Desktop-Build (`UniversalInvoiceMail.spec`)
3. Windows 10/11 SDK mit `makeappx.exe`, `signtool.exe` und `appcert.exe`
4. Lokaler Schreibpfad außerhalb synchronisierter Cloud-Ordner für MSIX-Artefakte, z. B. `C:\_Local_DEV\codex_build\universalinvoicemail-store`

Die Befehle verwenden bewusst Platzhalter bzw. relative Pfade.
Setze `$projectRoot` auf den lokalen Checkout `C:\_Local_DEV\repos\UniversalInvoiceMail` und `$softwareRoot` auf den lokalen Pipeline-Ordner `C:\Users\lukas\OneDrive\.TOPICS\.SOFTWARE`.

---

## Schritt 0: Store-Material & Icons aktualisieren

```powershell
$projectRoot = "C:\_Local_DEV\repos\UniversalInvoiceMail"
Set-Location $projectRoot
$env:PYTHONIOENCODING="utf-8"

# Kacheln & Manifest prüfen/erzeugen
python scripts/store_assets.py

# 16:9 Store-Screenshots erzeugen (falls aktualisiert)
python scripts/generate_store_screenshots.py

# Preflight-Store-Audit ausführen
python scripts/check_store_readiness.py
```

Erwartete Artefakte:
- `store_package\UniversalInvoiceMail\icons\icon_44x44.png`
- `store_package\UniversalInvoiceMail\icons\StoreLogo.png` (50x50)
- `store_package\UniversalInvoiceMail\icons\icon_50x50.png`
- `store_package\UniversalInvoiceMail\icons\icon_150x150.png`
- `store_package\UniversalInvoiceMail\icons\icon_310x150.png`
- `store_package\UniversalInvoiceMail\icons\icon_310x310.png`
- `store_package\UniversalInvoiceMail\icons\SplashScreen.png` (620x300)
- `releases\windowsstore\screenshots\*.png` (4 hochauflösende 16:9 PNG-Screenshots)

---

## Schritt 1: Desktop-EXE bauen

```powershell
Set-Location $projectRoot
python -m PyInstaller --clean --noconfirm UniversalInvoiceMail.spec
```

Erwarteter Hauptpfad:
- `dist\UniversalInvoiceMail\UniversalInvoiceMail.exe`

---

## Schritt 2: Store-Pretest

```powershell
$softwareRoot = "C:\Users\lukas\OneDrive\.TOPICS\.SOFTWARE"
& (Join-Path $softwareRoot "_STORE\msstore_pretest.ps1") `
  -ExePath (Join-Path $projectRoot "dist\UniversalInvoiceMail\UniversalInvoiceMail.exe") `
  -ProjectRoot $projectRoot `
  -StartWait 8
```

---

## Schritt 3: MSIX lokal außerhalb von OneDrive bauen

```powershell
$outputRoot = "C:\_Local_DEV\codex_build\universalinvoicemail-store"
New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null

python (Join-Path $softwareRoot "_STORE\store_packager.py") `
  $projectRoot `
  --dist (Join-Path $projectRoot "dist\UniversalInvoiceMail") `
  --output-dir $outputRoot `
  --app-name "UniversalInvoiceMail" `
  --version "2.3.0.0" `
  --publisher "CN=52596601-BAB4-4F3F-B182-E8F3F273B202" `
  --identity-name "Geiger.UniversalInvoiceMail" `
  --capabilities "runFullTrust"
```

Erwartetes MSIX-Paket:
- `C:\_Local_DEV\codex_build\universalinvoicemail-store\UniversalInvoiceMail.msix`

---

## Schritt 4: Windows App Certification Kit (WACK) Lauf

In einer PowerShell-Konsole mit Administratorrechten:

```powershell
$softwareRoot = "C:\Users\lukas\OneDrive\.TOPICS\.SOFTWARE"
$msixPath = "C:\_Local_DEV\codex_build\universalinvoicemail-store\UniversalInvoiceMail.msix"
$reportDir = Join-Path $projectRoot "releases\windowsstore\test_reports"

& (Join-Path $softwareRoot "_STORE\msstore_wack.ps1") `
  -MsixPath $msixPath `
  -ReportDir $reportDir
```

Ergebnis im `WACK_PROTOCOL.md` eintragen.

---

## Schritt 5: Partner Center Upload & Listing Checkliste

1. Paket `UniversalInvoiceMail.msix` im Microsoft Partner Center unter Packages hochladen.
2. Store-Listing aus `releases\windowsstore\store_listing_de.md` und `store_listing_en.md` übernehmen.
3. Suchbegriffe (exakt 7 Keywords nach Richtlinie 10.1.3) einpflegen.
4. Screenshots aus `releases\windowsstore\screenshots\` für Desktop hochladen.
5. Privacy Policy URL hinterlegen: `https://github.com/doc-bricks/UniversalInvoiceMail/blob/master/PRIVACY_POLICY.md`.
6. Support URL hinterlegen: `https://github.com/doc-bricks/UniversalInvoiceMail/issues`.
7. Preis & Verfügbarkeit: Kostenlos (Free).
