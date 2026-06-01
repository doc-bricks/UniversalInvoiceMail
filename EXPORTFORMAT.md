# Exportformat - UniversalInvoiceMail

Stand: 2026-06-01

Dieses Dokument beschreibt das geplante dateibasierte Austauschformat für Portierung, Companion-Nutzung und Buchhaltungsübergabe. Das Format ist ein Planungs- und Kompatibilitätsvertrag; die Desktop-App muss den Export/Reimport noch umsetzen.

## Formatname

`universalinvoicemail-invoicebundle-v1.json`

## Zweck

Das Bundle transportiert einen redigierten Rechnungsbestand aus der Desktop-App in einen Web/PWA-Companion oder zu einer externen Prüfung. Es ist nicht für Mailkonto-Migration, Credential-Backup oder direkte Cloud-Synchronisierung gedacht.

## Sicherheitsregeln

Das Bundle darf standardmäßig nicht enthalten:

- IMAP-Passwörter
- Gmail OAuth Tokens
- `credentials.json` oder Google-Client-Secrets
- Keyring-Einträge
- vollständige Mail-Bodies
- vollständige Rechnungsdateien als Base64

Belegdateien werden im Standard nur über relative Pfade, Dateinamen, MIME-Typen und SHA256-Hashes referenziert. Ein späteres ZIP-Bundle mit echten Dateien muss opt-in sein und klar als sensibler Export markiert werden.

## JSON-Struktur

```json
{
  "schema": "universalinvoicemail-invoicebundle-v1",
  "created_at": "2026-06-01T12:00:00+02:00",
  "source": {
    "app": "UniversalInvoiceMail",
    "version": "2.3.0",
    "platform": "windows"
  },
  "export_options": {
    "include_profiles": true,
    "include_file_references": true,
    "include_mail_bodies": false,
    "include_attachments": false
  },
  "profiles": [
    {
      "id": "profile-amazon",
      "name": "Amazon",
      "sender_filter": "@amazon.de",
      "subject_filter": "Rechnung, Bestellung",
      "gmail_query": "from:amazon has:attachment",
      "target_folder_label": "Rechnungen/Amazon"
    }
  ],
  "invoices": [
    {
      "id": "sha256:...",
      "profile_id": "profile-amazon",
      "date": "2026-05-31",
      "sender": "billing@example.org",
      "subject": "Rechnung 12345",
      "provider": "Amazon",
      "amount": "19.99",
      "currency": "EUR",
      "datev_status": "ready",
      "review_status": "unchecked",
      "notes": "",
      "files": [
        {
          "relative_path": "Amazon/2026-05-31_Rechnung_12345.pdf",
          "filename": "2026-05-31_Rechnung_12345.pdf",
          "mime_type": "application/pdf",
          "sha256": "...",
          "size_bytes": 123456
        }
      ],
      "mail_reference": {
        "account_label": "Gmail Hauptkonto",
        "message_id_hash": "sha256:...",
        "folder": "INBOX"
      }
    }
  ],
  "datev": {
    "berater_nr": "100000",
    "mandant_nr": "10000",
    "export_encoding": "cp1252",
    "last_export_at": null
  },
  "companion_changes": {
    "mode": "none",
    "allowed_fields": ["amount", "review_status", "notes"]
  }
}
```

## Reimport-Regeln

Ein Companion-Reimport darf nur fachliche Ergänzungen ändern:

- `amount`
- `currency`
- `review_status`
- `notes`
- optional `datev_status`, wenn der Desktop dies ausdrücklich erlaubt

Nicht überschrieben werden dürfen:

- Mailkonten
- Authentifizierungsdaten
- lokale Zielordner
- Dateipfade ohne Hash-Abgleich
- Original-Metadaten wie Sender, Betreff, Datum und Message-ID-Hash

Konflikte müssen über `id` und Datei-Hash sichtbar gemacht werden. Wenn eine Rechnung lokal gelöscht oder die Datei verändert wurde, darf ein Reimport nicht still ein altes Companion-Feld übernehmen.

## Companion-Usecases

- Rechnungsliste mobil oder im Browser prüfen.
- Beträge ergänzen, wenn sie nach dem Abruf noch fehlen.
- Prüfflags setzen: `unchecked`, `checked`, `needs_question`, `ready`.
- Übergabe an Steuerberatung mit reduziertem Bestand ermöglichen.

## Nicht-Ziele

- Vollständiges Backup der Desktop-App.
- Migration von Passwörtern oder OAuth-Tokens.
- Server-Synchronisierung.
- DATEV-Buchungsstapel als Ersatz für den bestehenden Desktop-Export.
