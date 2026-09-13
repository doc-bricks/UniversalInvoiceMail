# Portierungsplan — UniversalInvoiceMail

Stand: 2026-09-13

Status: Pfad A, Web/PWA-Companion lokal umgesetzt; lokaler Android-/iOS-naher Contract-Smoke ergänzt; Windows Store Release-Readiness & Packaging abgeschlossen.

## Entscheidung

UniversalInvoiceMail bleibt zuerst eine lokale Desktop-Vollversion. Windows ist die Hauptplattform, weil die beste ausgebaute Version lokale Mailkonten, Gmail OAuth, Keyring, PDF-/OCR-Konvertierung, optionale Office-/LibreOffice-Konvertierung, lokale Rechnungsarchive und DATEV-CSV-Export verbindet.

macOS und Linux sind sinnvolle Source-Smoke-Ziele, aber keine sofortigen Store-/Paketierungsziele. Android, iOS und Web/PWA werden nicht als vollständige Mobile-Klone geplant. Sinnvoll ist ein secrets-freier Companion für Status, Prüfung, Betragsnachtrag und Übergabe über `universalinvoicemail-invoicebundle-v1.json`. Der Desktop-Export, der kontrollierte Reimport für Beträge, Prüfflags und Notizen sowie die statische Web/PWA-Oberfläche sind umgesetzt; offen bleiben echte Android-/iOS-Geräte-Smokes mit realen Bundles.

Direkte Synchronisierung ist aktuell kein Ziel. Rechnungen, Mail-Metadaten, OAuth-Tokens, Passwörter und Buchhaltungsdaten sind sensibel; der robuste Standardpfad ist dateibasierter Austausch. Ein Server-Sync wäre erst nach expliziter Datenschutz-, Mandanten- und Supportentscheidung vertretbar.

## Features der besten Version

- IMAP-Abruf für Gmail, Outlook, GMX, Web.de, T-Online und weitere Anbieter.
- Optionale Gmail-API-Anbindung mit OAuth und Query Builder.
- Profilbasierte Suche nach Absender, Betreff, Body, Gmail Raw Query und Zeitraum.
- Download von PDF-Anhängen und Umwandlung von Mail-Body oder Nicht-PDF-Anhängen in PDF.
- Bild-, DOCX-, XLSX- und optionale Legacy-Office-Konvertierung über COM oder LibreOffice.
- Optionales OCR für bildbasierte PDFs mit Tesseract und `pypdfium2`.
- Lokales Rechnungsarchiv mit Hash-basierter Duplikaterkennung.
- Manuelle Betrags-Spalte, CSV-Export und DATEV-Buchungsstapel.
- Bundle Export und Bundle Import für redigierte Rechnungsmetadaten, Datei-Hashes, optionale Dateireferenzen sowie Companion-Rückfelder.
- Statischer Web/PWA-Companion für lokale Bundle-Prüfung, Profil-/Statusfilter, Betragsnachtrag, Prüfflag, Notiz und Änderungsbundle.
- Sichere lokale Zugangsdaten über `keyring`.

## Abgeleitete Usecases

### Usecase-Setting A: Lokale Rechnungszentrale

Nutzer: Selbstständige, kleine Büros und technisch affine Privatanwender, die Rechnungen aus Mailpostfächern lokal sichern und für Buchhaltung vorbereiten.

Usecases:
- Rechnungen aus mehreren Mailkonten periodisch abrufen.
- Shop- und Anbieterprofile mit Zeitraumfiltern pflegen.
- PDFs, Office-Anhänge und Mail-Bodies in ein einheitliches Archivformat bringen.
- Dubletten vermeiden und lokale Belegordner sauber halten.
- Beträge ergänzen und DATEV-nahe CSV-Dateien übergeben.

Plattformentscheidung: Windows Desktop und Windows Store sind Vollversion und Release-Fokus. macOS/Linux sind P2/P3-Smokes aus derselben PySide6-Codebasis, solange Gmail/IMAP, PDF-Konvertierung und LibreOffice-Fallback laufen. Windows-only COM-Konvertierung bleibt optionaler Komfortpfad.

### Usecase-Setting B: Mobile Prüfung und Nachtrag

Nutzer: Dieselben Nutzer wie Setting A, aber unterwegs oder auf Tablet/Telefon. Sie brauchen nicht den kompletten Mailabruf, sondern Übersicht, Prüfung und Nachtrag.

Usecases:
- Letzten Rechnungsbestand einsehen.
- Fehlende Beträge oder Prüfflags ergänzen.
- Belegstatus für die Buchhaltung kontrollieren.
- Notizen für Rückfragen ergänzen und später kontrolliert in die Desktop-App zurückführen.

Plattformentscheidung: Web/PWA-Companion ist sinnvoller als native Voll-App. Android/iOS können über PWA-Smokes abgedeckt werden. Native Android-/iOS-Apps lohnen erst, wenn Kamera-/Belegcapture oder Offline-Nachtrag belegt regelmäßig genutzt wird.

### Usecase-Setting C: Steuerberatung / Übergabe

Nutzer: Externe Buchhaltung oder Steuerberatung, die keine Mailzugänge und keine komplette App braucht.

Usecases:
- Reduzierten Export prüfen.
- Rechnungsmetadaten, Beträge, Hashes und DATEV-Status nachvollziehen.
- Rückfragen anhand stabiler Beleg-IDs stellen.

Plattformentscheidung: Kein App-Klon. Das Austauschformat und optional ein read-only Web/PWA-Viewer reichen. Anhänge werden nur optional und bewusst gebündelt; Standard ist Metadaten plus lokale Dateireferenz.

## Plattformmatrix

| Plattform | Entscheidung | Begründung |
|---|---|---|
| Windows Desktop / Store | Voll-App & Store-Ready | Bester Fit für lokale Dateiablage, Credential Manager, Office-COM, Tesseract-Bundle, DATEV-Workflow und Windows Store Paketierung (MSIX / WACK). |
| macOS | Source-Smoke, später Direktpaket möglich | IMAP/Gmail, PySide6 und LibreOffice-Fallback sind plausibel; Keyring, Browser-PDF und Tesseract müssen separat geprüft werden. |
| Linux | Source-Smoke, später AppImage/Tarball möglich | Für technisch affine Nutzer machbar; Desktop-Keyring, LibreOffice und Tesseract sind prüfpflichtig. |
| Web/PWA | Companion, nicht Voll-App | Browser darf keine lokalen Mailkonten, OAuth-Tokens und Rechnungsarchive wie die Desktop-App verwalten; gut geeignet für redigierte Bundles. |
| Android | PWA-Smoke, native App zurückstellen | Nutzen liegt in Prüfung/Nachtrag, nicht im kompletten Mail-/DATEV-Workflow. |
| iOS | PWA-Smoke, native App zurückstellen | Gleiche Logik wie Android; nativer Store-Pfad erst bei belegtem Kamera-/Review-Usecase. |

## Synchronisation und Austausch

Standard: dateibasierter Austausch über `universalinvoicemail-invoicebundle-v1.json`.

Nicht exportiert werden:
- IMAP-Passwörter
- Gmail OAuth Tokens
- `credentials.json`
- vollständige Mail-Bodies mit sensiblen Inhalten, außer der Nutzer aktiviert dies ausdrücklich
- Belegdateien als Base64 im Standardpfad

Das implementierte Bundle enthält redigierte Rechnungsmetadaten, Profilfilter, DATEV-Basisdaten sowie optionale relative Dateireferenzen mit SHA256-Hashes. Companion-Rückfluss ist bewusst eng begrenzt: Beträge, Prüfflags und Notizen dürfen zurückgeschrieben werden; Konflikte werden über Rechnungs-ID und Datei-Hash sichtbar gemacht. Damit ist der dateibasierte Austausch als Grundlage für Web/PWA, Android und iOS belastbar.

## Roadmap

### P0: Plan und Exportkontrakt - erledigt

- `PORTIERUNGSPLAN.md` und `EXPORTFORMAT.md` pflegen.
- Bundle-Schema `universalinvoicemail-invoicebundle-v1.json` definiert.
- Erlaubte Felder aus Rechnungen, Profilen und DATEV-Konfiguration ohne Secrets festgelegt.

### P1: Desktop-Portabilität absichern - erledigt

- Windows-Smoke gegen Start, IMAP/Gmail-Mock, PDF-Konvertierung, OCR-Option und DATEV-Export dokumentieren.
- Linux- und macOS-Source-Smokes für Start, Keyring-Fallback, LibreOffice-Fallback und CSV-Export automatisiert absichern.
- Windows-only COM-Konvertierung als optionalen Pfad markieren, nicht als Kernabhängigkeit.

### P2: Companion vorbereiten - erledigt

- Exportfunktion für das Bundle in der Desktop-App ergänzt.
- Reimport für Beträge, Prüfflags und Notizen mit ID-/Hash-Konfliktprüfung umgesetzt.
- Statischer Web/PWA-Viewer für redigierte Bundles ergänzt; keine IMAP-, Gmail-, OAuth- oder Passwortfunktionen im Browser.

### P3: Store- und Release-Fähigkeit — erledigt (2026-09-13)

- Windows Store Release-Readiness vollständig umgesetzt: `store_package.json` (v2.3.0.0, Identity `Geiger.UniversalInvoiceMail`), `AppxManifest.xml`, alle 5 Store-Kacheln (`icon_44x44.png`, `icon_50x50.png`, `icon_150x150.png`, `icon_310x150.png`, `icon_310x310.png`) sowie `SplashScreen.png` (620x300).
- Partner Center Richtlinie 10.1.3 Compliance für `STORE_LISTING.md` mit exakt 7 DE- und 7 EN-Suchbegriffen (jeweils <= 30 Zeichen, keine Markennamen).
- 4 hochauflösende Store-Präsentationsscreenshots (1920x1080, 16:9 PNG) in `README/screenshots/store/` und `store_package/UniversalInvoiceMail/screenshots/`.
- Privacy- und Support-Dokumentation (`PRIVACY_POLICY.md`, `SUPPORT.md`, `WINDOWS_STORE_PREP.md`) erstellt und verlinkt.
- Standalone PyInstaller onedir-Buildvertrag (`UniversalInvoiceMail.spec`) und `scripts/build_windows_exe.ps1` angelegt.
- Preflight-Store-Auditor `scripts/check_store_readiness.py` und automatisierte Test-Suite integriert (21/21 Kriterien bestanden).
- Linux- und macOS-Paketierung bleiben P3-Folgeziele nach Source-Smokes.
- Native Mobile-Apps nur nach belegtem eigenem Mobile-Usecase (PWA Companion bleibt primäre Mobile-Lösung).

### P4: Web/PWA-Companion - lokaler Stand erledigt

- Read-only Rechnungsliste, Profilfilter, DATEV-Status und Belegdetails aus `universalinvoicemail-invoicebundle-v1.json` sind in `web_companion/` umgesetzt.
- Lokaler Browser-State für zuletzt geöffnete Bundles ist vorhanden; Server-Synchronisierung bleibt Nicht-Ziel.
- Eingabe ist auf `amount`, `review_status` und `notes` begrenzt; Export erzeugt ein Companion-Änderungsbundle zurück zur Desktop-App.
- Lokaler Android-/iOS-naher Contract-Smoke ist ergänzt: echtes redigiertes Fixture, Manifest-/Service-Worker-/Icon-Vertrag, Filter und begrenzter Rückexport.
- Android-/iOS-PWA-Smoke mit echtem Bundle und Konfliktfall bleibt offen.

## Nicht-Ziele

- Öffentliche Upload-Webapp für echte Rechnungen.
- Direkte Cloud-Synchronisierung ohne neue Datenschutzentscheidung.
- Native Android-/iOS-Voll-App als Desktop-Klon.
- Speicherung oder Export von Mailpasswörtern, Gmail-Tokens oder Google-Client-Secrets.
- DATEV-Export im Browser als primärer Workflow.
