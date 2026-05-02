# UniversalInvoiceMail – User Guide

Version 2.2.3 | Stand: 2026-03-14

---

## Inhalt

1. [Einrichtung: IMAP](#einrichtung-imap)
2. [Einrichtung: Gmail API](#einrichtung-gmail-api)
3. [Profile konfigurieren](#profile-konfigurieren)
4. [Rechnungen abrufen](#rechnungen-abrufen)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

---

## 1. Einrichtung: IMAP {#einrichtung-imap}

IMAP funktioniert mit **jedem Mail-Anbieter** (Gmail, Outlook, GMX, web.de, etc.).

### Schritt-für-Schritt

1. Starte `UniversalInvoiceMail.py` (oder die .exe)
2. Klicke auf **"Mailkonto hinzufügen"**
3. Wähle **"IMAP"**
4. Fülle das Formular aus:

   | Feld           | Beispiel (Gmail)          | Beispiel (GMX)      |
   |----------------|--------------------------|---------------------|
   | IMAP-Server    | `imap.gmail.com`         | `imap.gmx.net`      |
   | Port           | `993`                    | `993`               |
   | SSL            | ✓ aktiviert              | ✓ aktiviert         |
   | Benutzername   | `deine@gmail.com`        | `deine@gmx.de`      |
   | Passwort       | App-Passwort (s. unten)  | Normales Passwort   |

5. Klicke **"Verbindung testen"** → Grüne Meldung = Erfolg
6. **"Speichern"**

### Gmail: App-Passwort erstellen

Gmail erfordert ein **App-Passwort** (kein normales Passwort):

1. Google-Konto → **Sicherheit** → **2-Faktor-Authentifizierung** aktivieren
2. Dann: **Sicherheit** → **App-Passwörter** → Neue App anlegen
3. Das generierte 16-stellige Passwort in UniversalInvoiceMail verwenden

### Outlook / Microsoft 365

Microsoft blockiert IMAP mit normalem Passwort. Alternativen:
- OAuth2 aktivieren (komplex, nur für Entwickler empfohlen)
- **Empfehlung:** Gmail API (Task 2) oder anderen Anbieter nutzen

---

## 2. Einrichtung: Gmail API {#einrichtung-gmail-api}

Die Gmail API ist schneller als IMAP und hat keine Rate-Limits.

### Voraussetzungen

```bash
pip install google-auth-oauthlib google-api-python-client
```

### OAuth2-Anmeldedaten erstellen

1. Öffne [Google Cloud Console](https://console.cloud.google.com/)
2. Neues Projekt anlegen (z. B. "InvoiceMail")
3. **APIs & Services → Bibliothek** → **"Gmail API"** aktivieren
4. **APIs & Services → Anmeldedaten** → **"OAuth 2.0-Client-IDs"** erstellen
   - Anwendungstyp: **Desktop-App**
5. `credentials.json` herunterladen
6. `credentials.json` in den Programmordner legen

### In UniversalInvoiceMail einrichten

1. **"Mailkonto hinzufügen"** → **"Gmail API"**
2. Klicke **"Autorisieren"** → Browser öffnet sich → Google-Konto auswählen
3. Berechtigungen bestätigen
4. Token wird als `token.json` im Programmordner gespeichert (einmalig)
5. **"Speichern"**

---

## 3. Profile konfigurieren {#profile-konfigurieren}

**Profile** definieren, von welchen Absendern und mit welchen Filtern
Rechnungen gesucht werden.

### Neues Profil erstellen

1. Tab **"Profile"** → **"Neu"**
2. Profilname vergeben (z. B. "Amazon-Bestellungen")
3. Felder ausfüllen:

   | Feld                    | Beschreibung                                         | Beispiel                      |
   |------------------------|------------------------------------------------------|-------------------------------|
   | Absender-Filter        | Kommagetrennte E-Mail-Adressen oder Domains          | `@amazon.de, @amazon.com`     |
   | Betreff-Filter         | Kommagetrennte Suchbegriffe (ODER-Verknüpfung)       | `Bestellung, Rechnung`        |
   | Blacklist              | Mails die diese Begriffe enthalten werden ignoriert  | `Newsletter, Werbung`         |
   | Body muss enthalten    | Body muss mindestens einen dieser Begriffe enthalten | `Rechnungsnummer`             |
   | Body darf nicht halten | Body darf keinen dieser Begriffe enthalten           | `abonnement`                  |
   | Zielordner             | Wohin die PDFs gespeichert werden                   | `C:\Dokumente\Rechnungen\Amazon` |
   | Zeitraum Von/Bis       | Mails außerhalb des Zeitraums werden ignoriert       | 01.01.2026 – 31.12.2026       |

4. **"Speichern"**

### Vorkonfigurierte Profile

Für gängige Shops sind Vorlagen vorhanden (z. B. Amazon, Zalando).
Diese können als Ausgangspunkt verwendet und angepasst werden.

---

## 4. Rechnungen abrufen {#rechnungen-abrufen}

1. Profil auswählen
2. Mailkonto auswählen
3. Klicke **"Suchen"**
4. Gefundene Mails werden in der Tabelle angezeigt
5. Klicke **"Herunterladen"** oder **"Alle herunterladen"**

### PDF-Modi

| Modus        | Beschreibung                                    |
|-------------|------------------------------------------------|
| Anhang      | Nur PDF-Anhänge speichern                       |
| Body→PDF    | Mail-Body als PDF konvertieren (kein Anhang)    |
| Vollständig | Anhang + Body zusammenführen (erfordert OCR)    |
| Browser     | Browser rendert die Mail als PDF (beste Qualität)|

### Duplikat-Erkennung

Bereits heruntergeladene Mails werden per SHA256-Hash erkannt und
nicht erneut heruntergeladen. Das Symbol 📎 in der Liste zeigt an,
dass ein PDF-Anhang vorhanden ist.

---

## 5. Troubleshooting {#troubleshooting}

### Auth-Fehler / "Authentication failed"

- **IMAP:** Falsches Passwort oder App-Passwort vergessen (→ neu erstellen)
- **Gmail:** Token abgelaufen → `token.json` löschen und neu autorisieren
- **GMX/Web.de:** IMAP muss in den Mailkonto-Einstellungen aktiviert sein
  (Web-Interface → Einstellungen → E-Mail → IMAP)

### "Keine Mails gefunden"

1. Zeitraum prüfen (Von/Bis-Datum korrekt?)
2. Absender-Filter zu streng? → Leerfeld = alle Absender
3. Betreff-Filter zu spezifisch? → Weniger Bedingungen testen
4. IMAP-Ordner korrekt? Standard ist `INBOX` – andere Ordner separat wählen

### SSL-Fehler

- Port prüfen: SSL = 993, ohne SSL = 143
- Wenn Firewall aktiv: Port 993 freigeben

### PDF-Konvertierung schlägt fehl

- `xhtml2pdf` installiert? → `pip install xhtml2pdf`
- Browser-Modus: Edge oder Chrome muss installiert sein

### Passwort wird nicht gespeichert

- `keyring` installiert? → `pip install keyring`
- Windows: Passwort wird in der Windows Credential Manager gespeichert

### OCR nicht verfügbar

- `pytesseract` und `pypdfium2` installieren: `pip install pytesseract pypdfium2`
- Oder: `tesseract_portable/` Ordner im Programmverzeichnis muss vorhanden sein

---

## 6. FAQ {#faq}

**F: Welche Mail-Anbieter werden unterstützt?**
A: Alle Anbieter mit IMAP-Unterstützung: Gmail, Outlook (eingeschränkt), GMX, web.de,
T-Online, Yahoo, iCloud (mit App-Passwort) und andere.

**F: Werden meine Passwörter sicher gespeichert?**
A: Ja – Passwörter werden via `keyring` im Windows Credential Manager gespeichert,
nicht in der Konfigurationsdatei.

**F: Kann die App mehrere Mailkonten gleichzeitig durchsuchen?**
A: Ja. Mehrere Konten können hinzugefügt und unabhängig verwendet werden.

**F: Was passiert mit dem Passwort wenn ich das Profil lösche?**
A: Der Eintrag im Windows Credential Manager bleibt erhalten.
Er kann manuell über "Systemsteuerung → Anmeldeinformationsverwaltung" gelöscht werden.

**F: Wie verhindere ich doppelte Downloads?**
A: Die Hash-basierte Duplikat-Erkennung ist automatisch aktiv.
Einmal heruntergeladene Anhänge werden nicht erneut gespeichert.

**F: Kann ich die Rechnungen direkt in einen Cloud-Ordner speichern?**
A: Ja – als Zielordner einfach den lokalen Sync-Ordner von OneDrive/Dropbox/etc. angeben.

**F: Welche Python-Version wird benötigt?**
A: Python 3.9 oder neuer.

**F: Kann ich die App ohne GUI (headless) nutzen?**
A: Nein, die aktuelle Version erfordert eine grafische Oberfläche (PyQt6).
