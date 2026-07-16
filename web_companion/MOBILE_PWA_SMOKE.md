# Mobile PWA Smoke - UniversalInvoiceMail Companion

Stand: 2026-07-16

Dieser lokale Smoke ersetzt keinen echten Android-Chrome- oder iOS-Safari-Gerätetest. Er hält aber den aktuellen Companion-Vertrag reproduzierbar fest, bis ein Gerät oder Emulator verfügbar ist.

## Geprüfter Vertrag

- Import eines echten redigierten `universalinvoicemail-invoicebundle-v1.json`-Bundles.
- PWA-Start aus dem `web_companion/`-Root mit Manifest, Service Worker und In-Scope-Icons.
- Android-/iOS-nahe Install-Metadaten: `display=standalone`, `start_url`, `scope`, 192/512-Icons, Maskable-Icons und Apple-Touch-Icon.
- Lokaler Review-Flow mit Betrag, Prüfstatus und Notiz.
- Rückexport nur mit `amount`, `review_status`, `notes`, `files`, `local_hash` und `id`.
- Keine Mailpasswörter, OAuth-Tokens, `credentials.json`, Google-Client-Secrets, Mail-Bodies oder Anhänge im Fixture- oder Change-Bundle.

## Lokaler Lauf

```powershell
npm --prefix web_companion test
```

Der mobile Contract liegt in:

- `web_companion/tests/mobile_smoke_bundle.json`
- `web_companion/tests/mobile_pwa_smoke.test.mjs`

## Manueller Gerätesmoke

1. Desktop-App öffnen und ein frisches redigiertes Bundle exportieren.
2. Companion lokal oder im geschützten Intranet starten:

   ```powershell
   python -m http.server 8765 -d web_companion
   ```

3. Auf Android Chrome und iOS Safari öffnen: `http://<host>:8765/`.
4. Bundle importieren, Profil- und Statusfilter testen, einen fehlenden Betrag ergänzen, Status auf `Bereit` setzen und eine Notiz schreiben.
5. Änderungsbundle exportieren und in der Desktop-App reimportieren.
6. Prüfen, dass ID- und Datei-Hash-Konflikte sichtbar bleiben und keine Mail- oder Credential-Daten im Rückexport erscheinen.

Bis dieser Lauf auf echten Geräten ausgeführt wurde, bleibt der Geräte-/Emulator-Signoff offen.
