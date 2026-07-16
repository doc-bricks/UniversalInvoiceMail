# UniversalInvoiceMail Web Companion

Statischer Browser-/PWA-Companion für redigierte `universalinvoicemail-invoicebundle-v1.json`-Exporte aus der Desktop-App.

## Grenzen

- Keine IMAP-, Gmail-, OAuth-, Passwort- oder Maildownload-Funktionen.
- Keine Server-Synchronisierung und kein Upload.
- Rückexport ändert nur `amount`, `review_status` und `notes`.
- Der Desktop-Reimport prüft weiter lokale Rechnungs-ID und Datei-Hash.

## Lokal starten

```powershell
python -m http.server 8765 -d web_companion
```

Danach `http://127.0.0.1:8765/` öffnen.

## Mobile/PWA-Smoke

Der lokale Android-/iOS-nahe Contract-Smoke liegt in `MOBILE_PWA_SMOKE.md`.
Er prüft ein echtes redigiertes Bundle, Install-Metadaten, In-Scope-Icons,
Offline-Assets und den begrenzten Rückexport ohne Credentials oder Mail-Bodies.

```powershell
npm --prefix web_companion test
```
