# Exportformat - UniversalInvoiceMail

Stand: 2026-06-12

Dieses Dokument beschreibt das implementierte dateibasierte Austauschformat für Portierung, Companion-Nutzung und Buchhaltungsübergabe. Die Desktop-App exportiert und reimportiert das Bundle jetzt direkt über `Bundle Export` und `Bundle Import` im Rechnungs-Tab.

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
      "account_id": "acc-1",
      "account_label": "Gmail Hauptkonto",
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
      "profile_name": "Amazon",
      "date": "2026-05-31",
      "sender": "billing@example.org",
      "subject": "Rechnung 12345",
      "filename": "2026-05-31_Rechnung_12345.pdf",
      "amount": "19.99",
      "currency": "EUR",
      "review_status": "unchecked",
      "notes": "",
      "datev_status": "ready",
      "files": [
        {
          "relative_path": "Amazon/2026-05-31_Rechnung_12345.pdf",
          "filename": "2026-05-31_Rechnung_12345.pdf",
          "mime_type": "application/pdf",
          "sha256": "...",
          "size_bytes": 123456
        }
      ],
      "local_hash": "...",
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
    "wj_beginn": "20260101",
    "waehrung": "EUR",
    "sachkontenlaenge": 4,
    "konten_mapping": {
      "Amazon": [70001, 4930]
    },
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
- `review_status`
- `notes`

Nicht überschrieben werden dürfen:

- Mailkonten
- Authentifizierungsdaten
- lokale Zielordner
- Dateipfade ohne Hash-Abgleich
- Original-Metadaten wie Sender, Betreff, Datum und Message-ID-Hash

Konflikte werden über `id` und Datei-Hash geprüft. Wenn eine Rechnung lokal gelöscht oder die Datei verändert wurde, übernimmt der Desktop keine Companion-Felder stillschweigend, sondern meldet den Konflikt im Importergebnis.

## Companion-Usecases

- Rechnungsliste mobil oder im Browser prüfen.
- Beträge ergänzen, wenn sie nach dem Abruf noch fehlen.
- Prüfflags setzen: `unchecked`, `checked`, `needs_question`, `ready`.
- Notizen für Rückfragen oder Korrekturen ergänzen.
- Übergabe an Steuerberatung mit reduziertem Bestand ermöglichen.

## Nicht-Ziele

- Vollständiges Backup der Desktop-App.
- Migration von Passwörtern oder OAuth-Tokens.
- Server-Synchronisierung.
- DATEV-Buchungsstapel als Ersatz für den bestehenden Desktop-Export.
