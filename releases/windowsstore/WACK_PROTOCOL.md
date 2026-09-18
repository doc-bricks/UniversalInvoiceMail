# UniversalInvoiceMail - WACK-Protokoll

## Ziel

Nach dem lokalen MSIX-Build soll der Windows App Certification Kit (WACK)-Lauf dokumentiert werden, damit Store-Submission und spätere Regressionen nachvollziehbar bleiben.

## Vorbereiteter Befehl

```powershell
$projectRoot = "C:\path\to\UniversalInvoiceMail"
$softwareRoot = "C:\path\to\.SOFTWARE"
$outputRoot = "C:\build\universalinvoicemail-store"
$reportRoot = Join-Path $projectRoot "releases\windowsstore\test_reports"
Start-Process powershell -Verb RunAs -ArgumentList @(
  "-ExecutionPolicy Bypass",
  "-File $(Join-Path $softwareRoot '_STORE\msstore_wack.ps1')",
  "-MsixPath $(Join-Path $outputRoot 'UniversalInvoiceMail.msix')",
  "-ReportDir $reportRoot"
)
```

## Aktueller Status

- Stand dieses Laufs: Preflight Store-Audit erfolgreich (21/21 Kriterien PASS, 0 Findings).
- Vollständige Test-Suite (191+ Tests) lokal grün.
- Kacheln (44x44, 50x50 `StoreLogo.png`, 150x150, 310x150, 310x310, 620x300 SplashScreen) und 4x 16:9 Screenshots maßhaltig vorhanden.
- Capabilities: `runFullTrust` deklariert (notwendig für IMAP-Netzwerkkommunikation, Dateisystemoperationen und Windows Credential Manager / Keyring-Zugriff).
- Verifizierter Blocker für WACK: WACK erfordert administrative Rechte (`RunAs`). In CI/Automationen ohne GUI-Elevation ist ein interaktiver Admin-Aufruf erforderlich.
- Erwartete Ablage:
  - XML-Report unter `releases\windowsstore\test_reports\`
  - Konsolenlog unter `releases\windowsstore\test_reports\`

## Eintrag für den nächsten WACK-Lauf

- Datum:
- MSIX-Pfad:
- WACK-Gesamtergebnis:
- Anzahl PASS:
- Anzahl FAIL:
- Anzahl WARNING:
- Relevante Findings:
- Nächste Korrektur:
