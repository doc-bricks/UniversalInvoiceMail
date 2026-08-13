# Mail-Provider-Evaluierung (TASKPLAN #1154)

Stand: 2026-08-13
Scope: lokale Architektur- und Quelltextprüfung für UniversalInvoiceMail v2.3.0

## Ergebnis

Die Anwendung hat heute zwei Abrufpfade: den generischen IMAP-Pfad und einen
optionalen Gmail-API-Pfad. Eine direkte Microsoft-Graph-, ProtonMail- oder
Tutanota-Implementierung ist im Klon nicht vorhanden. In diesem Slice wurden
keine Provider-Endpunkte angesprochen und keine Zugangsdaten angefordert.

| Provider | Lokal belegter Stand | Entscheidung für diesen Slice |
| --- | --- | --- |
| Gmail | Optionaler Gmail-API-Pfad mit lokalem OAuth-Token; alternativ IMAP. | Bestehenden Pfad weiterverwenden. |
| Outlook/Hotmail | Generischer IMAP-Preset (`outlook.office365.com`). | Keine zusätzliche Graph-Abhängigkeit ohne konkreten Bedarf. |
| Microsoft Graph API | Kein Adapter, kein OAuth-App-/Scope-Vertrag und kein Live-Credential im Projekt. | Nicht implementieren; erst Tenant-/Scope-Bedarf, Datenschutz- und Security-Review festlegen. |
| ProtonMail | Kein direkter Adapter; kein Provider-SDK oder API-Credential im Projekt. | Keine Behauptung direkter Unterstützung. Eine explizite Bridge-/API-Entscheidung ist Voraussetzung; bis dahin bleibt nur der vorhandene generische Abrufpfad, sofern die Nutzerkonfiguration ihn bereitstellt. |
| Tutanota | Kein direkter Adapter, kein Provider-SDK oder API-Credential im Projekt. | Nicht implementieren; Provider-spezifische Anschluss- und Datenschutzentscheidung zuerst klären. |

## Local-First-Grenzen

- Zugangsdaten und OAuth-Tokens bleiben außerhalb des Repositories im lokalen
  Benutzerprofil bzw. Credential-Store.
- Eine direkte Provider-Anbindung darf den bestehenden IMAP-/Gmail-Pfad nicht
  brechen und darf keine pauschale Server- oder Upload-Annahme einführen.
- Live-Provider-Tests benötigen eine ausdrückliche Testfreigabe, konkrete
  Konten/Scopes und einen dokumentierten Secret-Lifecycle. Mock-Tests belegen
  nur die lokale Adapterlogik, nicht die externe Provider-Verfügbarkeit.

## Nächster Entscheidungs-Gate

Die Evaluierung ist abgeschlossen. Eine Implementierung eines neuen Adapters
bleibt eine separate Aufgabe und darf erst beginnen, wenn der Nutzer einen
konkreten Providerbedarf und den zulässigen OAuth-/Credential-Umfang bestätigt.
Dann ist ein Adapter-Interface mit isolierter Fehlerbehandlung, Secret-Redaction,
Mock-Tests und einer gesonderten Live-Abnahme zu spezifizieren.

## Lokale Belege

- `UniversalInvoiceMail.py`: `IMAP_PRESETS`, `MailAccount`,
  `_process_imap` und `_process_gmail_api`.
- `tests/test_integration.py`: ausschließlich gemockte IMAP-/Gmail-Abläufe;
  keine Live-Provider-Anmeldung.
- `tests/test_no_google_import.py`: Gmail-Abhängigkeit bleibt optional.
