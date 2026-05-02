# IMPLEMENTATION_GUIDE_IMPORT_FEATURE.md
# UniversalInvoiceMail - Import & Sync Feature

## Übersicht

Implementierungsanleitung für das automatische Import-Feature von externen PDFs und E-Mails (.eml/.msg) in UniversalInvoiceMail.

**Ziel:** User legt Dateien in Profilordner → App erkennt sie automatisch → Kategorisiert und fügt zur Liste hinzu

---

## Ausbaustufen

### Stufe 1: Basis-Import (v1.7)
- Ordner-Scan Button (manuell ausgelöst)
- Neue PDFs in Profilordnern erkennen
- Automatische Zuordnung zum Profil (aus Ordnername)
- Sync bei Aktualisieren (gelöschte = raus, neue = rein)

### Stufe 2: Erweiterte Erkennung (v1.8+)
- E-Mail-Dateien (.eml) unterstützen → zu PDF konvertieren
- Body + Anhänge in eine PDF zusammenführen
- Watchdog-basierte Live-Erkennung (optional)

### Stufe 3: Intelligente Kategorisierung (v2.0+)
- PDF-Inhalt analysieren → Shop/Absender erkennen
- Automatische Profilzuordnung basierend auf Inhalt
- OCR für gescannte Rechnungen

---

## Stufe 1: Implementierung

### 1.1 Ordner-Scan Methode

```python
def scan_folders_for_new_files(self) -> int:
    """
    Scannt alle Profilordner nach neuen PDFs.
    Inspiriert von DokuZentrum FileIndex.index_folder()
    
    Returns:
        Anzahl neu hinzugefügter Dateien
    """
    new_count = 0
    base_path = Path(self.settings.download_path)
    
    # Alle bekannten Pfade sammeln für schnellen Lookup
    known_paths = {inv.path for inv in self.invoices}
    known_hashes = {inv.hash for inv in self.invoices if inv.hash}
    
    # Jeden Profilordner durchsuchen
    for profile in self.profiles:
        # Profilordner bestimmen
        if profile.target_subfolder:
            folder = base_path / sanitize_filename(profile.target_subfolder)
        else:
            folder = base_path / sanitize_filename(profile.name)
        
        if not folder.exists():
            continue
        
        # PDFs im Ordner finden
        for pdf_path in folder.glob("*.pdf"):
            str_path = str(pdf_path)
            
            # Bereits bekannt?
            if str_path in known_paths:
                continue
            
            # Hash berechnen für Duplikat-Check
            file_hash = calculate_file_hash(pdf_path)
            if file_hash and file_hash in known_hashes:
                self.log_output.appendPlainText(f"[SCAN] Duplikat übersprungen: {pdf_path.name}")
                continue
            
            # Metadaten extrahieren
            stat = pdf_path.stat()
            file_date = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
            
            # Invoice erstellen
            inv = Invoice(
                id=str(uuid.uuid4()),
                profile_name=profile.name,
                filename=pdf_path.name,
                date=file_date,
                path=str_path,
                sender="Manuell importiert",
                subject=pdf_path.stem,  # Dateiname als Subject
                hash=file_hash or ""
            )
            
            self.invoices.append(inv)
            known_paths.add(str_path)
            if file_hash:
                known_hashes.add(file_hash)
            new_count += 1
            
            self.log_output.appendPlainText(f"[SCAN] Neu: {pdf_path.name} → {profile.name}")
    
    if new_count > 0:
        self.save_invoices_db()
    
    return new_count
```

### 1.2 Integration in refresh_invoice_table()

```python
def refresh_invoice_table(self):
    """Aktualisiert die Rechnungstabelle und synchronisiert mit Dateisystem"""
    
    # === PHASE 1: Gelöschte entfernen ===
    valid_invoices = []
    removed_count = 0
    
    for inv in self.invoices:
        if Path(inv.path).exists():
            valid_invoices.append(inv)
        else:
            removed_count += 1
    
    if removed_count > 0:
        self.invoices = valid_invoices
        if hasattr(self, 'log_output'):
            self.log_output.appendPlainText(f"[SYNC] {removed_count} gelöschte Einträge entfernt")
    
    # === PHASE 2: Neue PDFs finden ===
    new_count = self.scan_folders_for_new_files()
    if new_count > 0 and hasattr(self, 'log_output'):
        self.log_output.appendPlainText(f"[SYNC] {new_count} neue Dateien importiert")
    
    # === PHASE 3: Speichern wenn Änderungen ===
    if removed_count > 0 or new_count > 0:
        self.save_invoices_db()
    
    # === PHASE 4: Tabelle neu aufbauen ===
    self.invoice_table.setRowCount(0)
    # ... Rest wie gehabt
```

### 1.3 GUI: Scan-Button (optional, da automatisch bei Aktualisieren)

```python
# In setup_ui() bei den Rechnungs-Buttons:
btn_scan = QPushButton("Ordner scannen")
btn_scan.clicked.connect(self.manual_scan)
btn_scan.setToolTip("Sucht nach manuell hinzugefügten PDFs in allen Profilordnern")
inv_btn_row.addWidget(btn_scan)

def manual_scan(self):
    """Manueller Ordner-Scan mit Feedback"""
    new_count = self.scan_folders_for_new_files()
    if new_count > 0:
        self.refresh_invoice_table()
        QMessageBox.information(self, "Scan", f"{new_count} neue Dateien gefunden und importiert.")
    else:
        QMessageBox.information(self, "Scan", "Keine neuen Dateien gefunden.")
```

---

## Stufe 2: E-Mail-Import (.eml/.msg)

### 2.1 E-Mail zu PDF Konvertierung

**Referenz:** DokuZentrum `core/pdf/merger.py` für PDF-Zusammenführung

```python
def convert_eml_to_pdf(self, eml_path: Path, output_path: Path) -> bool:
    """
    Konvertiert .eml zu PDF (Body + Anhänge in einer Datei).
    
    Workflow:
    1. E-Mail parsen
    2. Body zu HTML → PDF (erste Seiten)
    3. PDF-Anhänge extrahieren
    4. Alle PDFs zusammenführen
    5. Original .eml löschen
    """
    import email
    from email import policy
    
    try:
        # E-Mail parsen
        with open(eml_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
        
        # Metadaten extrahieren
        subject = msg.get('Subject', 'Unbekannt')
        sender = msg.get('From', 'Unbekannt')
        date_str = msg.get('Date', '')
        
        # Body extrahieren
        body_html = ""
        body_text = ""
        pdf_attachments = []
        
        for part in msg.walk():
            content_type = part.get_content_type()
            
            if content_type == 'text/html':
                body_html = part.get_content()
            elif content_type == 'text/plain' and not body_html:
                body_text = part.get_content()
            elif content_type == 'application/pdf':
                # PDF-Anhang
                filename = part.get_filename()
                data = part.get_content()
                pdf_attachments.append((filename, data))
        
        # Body zu PDF konvertieren
        if body_html:
            body_content = body_html
        else:
            body_content = f"<pre>{body_text}</pre>"
        
        # Header hinzufügen
        header_html = f"""
        <div style="border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px;">
            <p><strong>Von:</strong> {sender}</p>
            <p><strong>Betreff:</strong> {subject}</p>
            <p><strong>Datum:</strong> {date_str}</p>
        </div>
        """
        full_html = f"<html><body>{header_html}{body_content}</body></html>"
        
        # Temporäre PDFs erstellen
        temp_dir = Path(tempfile.mkdtemp())
        body_pdf = temp_dir / "body.pdf"
        html_to_pdf(full_html, body_pdf)
        
        # Anhänge speichern
        attachment_pdfs = []
        for i, (filename, data) in enumerate(pdf_attachments):
            att_path = temp_dir / f"attachment_{i}.pdf"
            with open(att_path, 'wb') as f:
                f.write(data)
            attachment_pdfs.append(att_path)
        
        # PDFs zusammenführen (Body + Anhänge)
        all_pdfs = [body_pdf] + attachment_pdfs
        if len(all_pdfs) == 1:
            # Nur Body, direkt kopieren
            shutil.copy(body_pdf, output_path)
        else:
            # Merge mit PyMuPDF
            self._merge_pdfs(all_pdfs, output_path)
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        self.log_output.appendPlainText(f"[EML] Fehler: {e}")
        return False

def _merge_pdfs(self, pdf_paths: List[Path], output_path: Path):
    """
    Führt mehrere PDFs zusammen.
    Basiert auf DokuZentrum PDFMerger.merge()
    """
    import fitz  # PyMuPDF
    
    output_doc = fitz.open()
    
    for pdf_path in pdf_paths:
        if pdf_path.exists():
            src_doc = fitz.open(str(pdf_path))
            output_doc.insert_pdf(src_doc)
            src_doc.close()
    
    output_doc.save(str(output_path))
    output_doc.close()
```

### 2.2 Erweiterter Ordner-Scan für E-Mails

```python
def scan_folders_for_new_files(self) -> int:
    """Erweitert um .eml/.msg Support"""
    new_count = 0
    # ... wie oben ...
    
    for profile in self.profiles:
        folder = self._get_profile_folder(profile)
        if not folder.exists():
            continue
        
        # PDFs
        for pdf_path in folder.glob("*.pdf"):
            # ... wie oben ...
        
        # E-Mails konvertieren
        for eml_path in folder.glob("*.eml"):
            output_name = f"{profile.name}_{eml_path.stem}.pdf"
            output_path = folder / output_name
            
            if output_path.exists():
                continue
            
            if self.convert_eml_to_pdf(eml_path, output_path):
                # Original löschen nach erfolgreicher Konvertierung
                eml_path.unlink()
                self.log_output.appendPlainText(f"[EML] Konvertiert: {eml_path.name}")
                
                # Invoice hinzufügen
                # ... wie bei PDFs ...
                new_count += 1
    
    return new_count
```

---

## Diskussion: Body+PDF Zusammenführung für Mail-Abruf

### Use Case
User möchte:
- Mail-Body und PDF-Anhänge in EINER Datei
- Kein einzelnes Zusammensuchen
- Nach Konvertierung: Nur PDF bleibt, Mail-Daten werden nicht separat gespeichert

### Vorteile
1. **Übersichtlichkeit:** Eine Datei = eine Rechnung (komplett)
2. **Archivierung:** Body enthält oft wichtige Infos (Bestellnummer, Kundendaten)
3. **Suchbarkeit:** PDF-Text durchsuchbar (Body + Anhang)

### Nachteile
1. **Dateigröße:** Größere PDFs
2. **Performance:** Merge-Operation kostet Zeit
3. **Komplexität:** Mehr Fehlerquellen

### Empfehlung
**JA, implementieren** als **Option** in Einstellungen:

```python
@dataclass
class AppSettings:
    # ... existing ...
    merge_body_with_attachments: bool = True  # Neue Option
```

**Workflow:**
1. Mail hat PDF-Anhang → Body + Anhang mergen
2. Mail hat nur Body → Body zu PDF
3. Mail hat nur Anhang → Anhang direkt speichern
4. Option aus → Altes Verhalten (separate Dateien)

### Implementation in _process_gmail_message / _process_imap_message

```python
def _process_mail_with_merge(self, headers, body_html, attachments, profile, target_dir):
    """
    Verarbeitet Mail mit optionalem Body+Attachment Merge.
    """
    if not self.settings.merge_body_with_attachments:
        # Altes Verhalten: Separate Dateien
        return self._process_mail_legacy(...)
    
    # Neues Verhalten: Alles zusammenführen
    temp_dir = Path(tempfile.mkdtemp())
    pdfs_to_merge = []
    
    # 1. Body zu PDF (mit Header-Infos)
    if body_html and len(body_html) > 100:
        header_html = self._create_mail_header_html(headers)
        full_html = f"{header_html}{body_html}"
        body_pdf = temp_dir / "body.pdf"
        if html_to_pdf(full_html, body_pdf):
            pdfs_to_merge.append(body_pdf)
    
    # 2. PDF-Anhänge
    for i, (filename, data) in enumerate(attachments):
        att_pdf = temp_dir / f"att_{i}.pdf"
        with open(att_pdf, 'wb') as f:
            f.write(data)
        pdfs_to_merge.append(att_pdf)
    
    # 3. Zusammenführen
    if pdfs_to_merge:
        output_name = self._generate_filename(profile, headers)
        output_path = target_dir / output_name
        
        if len(pdfs_to_merge) == 1:
            shutil.copy(pdfs_to_merge[0], output_path)
        else:
            self._merge_pdfs(pdfs_to_merge, output_path)
        
        # Invoice erstellen
        # ...
    
    # 4. Cleanup
    shutil.rmtree(temp_dir)
```

---

## Code-Referenzen aus DokuZentrum

### Relevante Module

| Modul | Verwendung |
|-------|------------|
| `core/knowledge/watcher.py` | FileWatcher mit Debouncing für Live-Erkennung |
| `core/knowledge/file_index.py` | Hash-Berechnung, Duplikat-Erkennung, Kategorisierung |
| `core/pdf/merger.py` | PDF-Zusammenführung mit PyMuPDF |
| `core/converter/formats.py` | Format-Konvertierung (HTML→PDF, etc.) |

### Best Practices übernommen

1. **DebouncedQueue** (watcher.py:44-78)
   - Verhindert Event-Spam bei schnellen Änderungen
   - DELETE sofort verarbeiten, CREATE/MODIFY debounced

2. **calculate_hash()** (file_index.py:174-184)
   - SHA256 mit Chunk-Reading für große Dateien
   - Für Duplikat-Erkennung

3. **PDFMerger.merge()** (merger.py:47-98)
   - PyMuPDF-basierte PDF-Zusammenführung
   - Robuste Fehlerbehandlung

4. **FileWatchHandler._should_ignore()** (watcher.py:103-125)
   - Ignore-Patterns für temp-Dateien
   - Extension-Filter

---

## Implementierungsreihenfolge

### v1.7 (Nächster Release)
- [ ] `scan_folders_for_new_files()` implementieren
- [ ] In `refresh_invoice_table()` integrieren
- [ ] Optional: "Ordner scannen" Button

### v1.8
- [ ] .eml Support mit `convert_eml_to_pdf()`
- [ ] `_merge_pdfs()` Hilfsmethode
- [ ] Optional: .msg Support (benötigt extract-msg)

### v1.9
- [ ] Settings-Option `merge_body_with_attachments`
- [ ] Mail-Abruf anpassen für Merge-Verhalten
- [ ] Tests mit verschiedenen Mail-Typen

### v2.0+
- [ ] Watchdog-Integration (optional, ressourcenintensiv)
- [ ] Intelligente Kategorisierung basierend auf PDF-Inhalt

---

## Abhängigkeiten

### Bereits vorhanden
- PyQt6
- keyring
- weasyprint (für html_to_pdf)

### Neu benötigt (Stufe 2+)
- PyMuPDF (`pip install pymupdf`) - für PDF-Merge
- extract-msg (`pip install extract-msg`) - optional für .msg

### Optional (Stufe 3+)
- watchdog (`pip install watchdog`) - für Live-Erkennung
- pytesseract - für OCR

---

## Testfälle

1. **Neue PDF in Ordner legen** → Wird beim Aktualisieren gefunden
2. **PDF löschen** → Verschwindet aus Liste
3. **Duplikat (gleicher Hash)** → Wird übersprungen
4. **E-Mail mit Anhang** → Body + Anhang in einer PDF
5. **E-Mail nur Body** → Body wird zu PDF
6. **Mehrere Anhänge** → Alle in einer PDF zusammengeführt
