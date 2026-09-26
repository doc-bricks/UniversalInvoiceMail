"""GUI accessibility checks for compact symbol-only controls."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

for mod in [
    "xhtml2pdf",
    "xhtml2pdf.pisa",
    "pytesseract",
    "pypdfium2",
    "pypdf",
    "PIL",
    "PIL.Image",
    "selenium",
    "selenium.webdriver",
    "selenium.webdriver.edge.options",
    "selenium.webdriver.edge.service",
    "selenium.webdriver.chrome.options",
    "selenium.webdriver.chrome.service",
    "webdriver_manager",
    "webdriver_manager.microsoft",
    "webdriver_manager.chrome",
    "googleapiclient",
    "googleapiclient.discovery",
    "google_auth_oauthlib",
    "google_auth_oauthlib.flow",
    "google.auth",
    "google.auth.transport",
    "google.auth.transport.requests",
    "google.oauth2",
    "google.oauth2.credentials",
    "google.auth.exceptions",
    "keyring",
    "reportlab",
    "reportlab.pdfgen",
    "reportlab.lib",
    "reportlab.lib.pagesizes",
    "reportlab.lib.units",
    "reportlab.lib.utils",
    "docx2pdf",
    "win32com",
    "win32com.client",
    "pythoncom",
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

import pytest
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTabWidget,
)
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt, QEvent

sys.path.insert(0, str(Path(__file__).parent.parent))

import UniversalInvoiceMail as uim


@pytest.fixture(scope="module")
def qapp():
    qt_app = QApplication.instance()
    if qt_app is None:
        qt_app = QApplication([])
    return qt_app


def test_start_grabbing_does_not_wipe_sync_log(tmp_path, monkeypatch, qapp):
    """Sync messages before the worker must not be cleared by a second log_output.clear()."""
    monkeypatch.setattr(uim, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(uim, "INVOICES_DB", tmp_path / "invoices.json")

    window = uim.MainWindow()
    try:
        acc = uim.MailAccount(
            id="a1", name="Test", provider="IMAP",
            host="imap.example.com", port=993,
            username="test@example.com",
        )
        window.accounts.append(acc)
        prof = uim.InvoiceProfile(id="p1", name="TestShop", account_id="a1",
                                  sender_filter="shop@example.com", enabled=True)
        window.profiles.append(prof)

        clear_calls = []
        original_clear = window.log_output.clear
        def tracking_clear():
            clear_calls.append(1)
            original_clear()
        window.log_output.clear = tracking_clear

        class _FakeWorker:
            log = MagicMock()
            progress = MagicMock()
            invoice_found = MagicMock()
            finished_signal = MagicMock()
            def start(self): pass
            def isRunning(self): return False
            def stop(self): pass

        monkeypatch.setattr(uim, "InvoiceWorker", lambda *a, **kw: _FakeWorker())

        window.start_grabbing()

        assert len(clear_calls) == 1, (
            f"log_output.clear() called {len(clear_calls)} times — expected exactly 1 "
            "(sync messages must not be wiped before worker output)"
        )
    finally:
        window.close()


def test_account_dialog_restores_use_gmail_api_false_on_edit(qapp):
    """AccountDialog must not force use_gmail_api=True when editing a Gmail account with it off.

    Regression: on_provider_changed("Gmail") sets ck_gmail_api=True, overriding the loaded
    account value. Fix: ck_gmail_api is re-applied after provider detection.
    """
    account = uim.MailAccount(
        id="a1", name="MyGmail", provider="Gmail",
        host="imap.gmail.com", port=993,
        username="test@gmail.com",
        use_gmail_api=False,
    )
    dialog = uim.AccountDialog(account=account)
    try:
        assert not dialog.ck_gmail_api.isChecked(), (
            "AccountDialog must respect use_gmail_api=False when editing a Gmail account; "
            "on_provider_changed must not override it"
        )
    finally:
        dialog.close()


def test_symbol_buttons_expose_accessible_context(tmp_path, monkeypatch, qapp):
    """Compact buttons keep a screenreader-friendly name, description, and tooltip."""
    monkeypatch.setattr(uim, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(uim, "INVOICES_DB", tmp_path / "invoices.json")

    window = uim.MainWindow()
    try:
        expected = {
            "add_profile_button": (
                "Neues Suchprofil anlegen",
                "Öffnet den Dialog zum Anlegen eines neuen Suchprofils für Rechnungen.",
                "Neues Suchprofil anlegen",
            ),
            "delete_profile_button": (
                "Ausgewähltes Suchprofil löschen",
                "",
                "Ausgewähltes Suchprofil löschen",
            ),
            "add_account_button": (
                "Neues E-Mail-Konto anlegen",
                "Öffnet den Dialog zum Hinzufügen eines weiteren E-Mail-Kontos.",
                "Neues E-Mail-Konto anlegen",
            ),
            "delete_account_button": (
                "Ausgewähltes E-Mail-Konto löschen",
                "",
                "Ausgewähltes E-Mail-Konto löschen",
            ),
            "delete_selected_invoices_button": (
                "Ausgewählte Rechnungen und Dateien löschen",
                "",
                "Ausgewählte Einträge und Dateien löschen",
            ),
            "browse_download_path_button": (
                "Speicherordner auswählen",
                "Öffnet die Ordnerauswahl für den lokalen Rechnungs-Speicherort.",
                "Speicherordner auswählen",
            ),
        }

        for object_name, (accessible_name, accessible_description, tooltip) in expected.items():
            button = window.findChild(QPushButton, object_name)
            assert button is not None, object_name
            assert button.accessibleName() == accessible_name
            assert button.accessibleDescription() == accessible_description
            assert button.toolTip() == tooltip
    finally:
        window.close()


def test_invoice_action_buttons_expose_context(tmp_path, monkeypatch, qapp):
    """Short action labels in the invoice toolbar keep clear accessible context."""
    monkeypatch.setattr(uim, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(uim, "INVOICES_DB", tmp_path / "invoices.json")

    window = uim.MainWindow()
    try:
        expected = {
            "select_all_invoices_button": (
                "Alle sichtbaren Rechnungen auswählen",
                "Markiert alle sichtbaren Rechnungen für Export- oder Löschaktionen.",
                "Alle Einträge auswählen",
            ),
            "clear_invoice_selection_button": (
                "Rechnungsauswahl aufheben",
                "Entfernt alle Markierungen in der Rechnungstabelle.",
                "Auswahl aufheben",
            ),
            "open_invoice_folder_button": (
                "Speicherordner für Rechnungen öffnen",
                "Öffnet den aktuellen Rechnungsordner im Dateimanager.",
                "Speicherordner im Explorer öffnen",
            ),
            "refresh_invoice_table_button": (
                "Rechnungsliste aktualisieren",
                "Synchronisiert die Tabelle mit dem Dateisystem und importiert neue Dateien.",
                "Rechnungstabelle mit Ordnerinhalt synchronisieren",
            ),
            "export_invoices_csv_button": (
                "Rechnungsliste als CSV exportieren",
                "Exportiert markierte Rechnungen als Tabellen-Datei. Sind keine Rechnungen markiert, wird die gesamte Liste exportiert.",
                "Markierte Rechnungen exportieren; ohne Markierung die gesamte Liste (Strg+E)",
            ),
            "export_invoice_bundle_button": (
                "Redigiertes Rechnungs-Bundle exportieren",
                "Exportiert ausgewählte oder alle Rechnungen für Companion- oder Prüf-Workflows.",
                "Redigiertes Rechnungs-Bundle für Companion oder Prüfung exportieren",
            ),
            "import_invoice_bundle_button": (
                "Companion-Bundle importieren",
                "Übernimmt Betrag, Prüfflag und Notizen aus einem redigierten Rechnungs-Bundle.",
                "Companion-Änderungen für Betrag, Prüfflag und Notiz reimportieren",
            ),
            "export_datev_button": (
                "DATEV-Buchungsstapel exportieren",
                "Exportiert markierte Rechnungen als DATEV-Buchungsstapel für die Buchhaltung.",
                "Ausgewählte Rechnungen als DATEV-Buchungsstapel exportieren",
            ),
        }

        for object_name, (accessible_name, accessible_description, tooltip) in expected.items():
            button = window.findChild(QPushButton, object_name)
            assert button is not None, object_name
            assert button.accessibleName() == accessible_name
            assert button.accessibleDescription() == accessible_description
            assert button.toolTip() == tooltip
    finally:
        window.close()


def test_primary_work_areas_expose_accessible_context(tmp_path, monkeypatch, qapp):
    """The main work areas keep their purpose clear for screenreader users."""
    monkeypatch.setattr(uim, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(uim, "INVOICES_DB", tmp_path / "invoices.json")

    window = uim.MainWindow()
    try:
        tabs = window.findChild(QTabWidget, "main_workspace_tabs")
        assert tabs is not None
        assert tabs.accessibleName() == "Arbeitsbereiche"
        assert tabs.accessibleDescription() == (
            "Wechselt zwischen Rechnungen, Einstellungen, Protokoll und Informationen."
        )

        invoice_table = window.findChild(QTableWidget, "invoice_table")
        assert invoice_table is not None
        assert invoice_table.accessibleName() == "Rechnungsliste"
        assert invoice_table.accessibleDescription() == (
            "Zeigt gefundene Rechnungen. Zeilen können für Export- oder Löschaktionen ausgewählt werden."
        )
        assert invoice_table.toolTip() == "Rechnungen auswählen oder mit Doppelklick öffnen"

        activity_log = window.findChild(QPlainTextEdit, "activity_log")
        assert activity_log is not None
        assert activity_log.accessibleName() == "Aktivitätsprotokoll"
        assert activity_log.accessibleDescription() == (
            "Zeigt Fortschritt, gefundene Rechnungen und Fehlermeldungen des aktuellen Abrufs."
        )
        assert activity_log.toolTip() == "Fortschritt und Meldungen des Rechnungsabrufs"
    finally:
        window.close()


def test_invalid_manual_invoice_amount_is_restored_and_announced(tmp_path, monkeypatch, qapp):
    """Invalid amount edits must keep the prior value and give clear user feedback."""
    monkeypatch.setattr(uim, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(uim, "INVOICES_DB", tmp_path / "invoices.json")

    window = uim.MainWindow()
    try:
        invoice_path = tmp_path / "rechnung.pdf"
        invoice_path.write_bytes(b"test invoice")
        invoice = uim.Invoice(
            id="inv-1",
            profile_name="Test-Shop",
            filename="rechnung.pdf",
            date="2026-08-23",
            path=str(invoice_path),
            amount=19.99,
        )
        window.invoices = [invoice]
        window.refresh_invoice_table()

        warnings = []
        save_calls = []
        monkeypatch.setattr(
            uim.QMessageBox,
            "warning",
            lambda *args, **kwargs: warnings.append((args, kwargs)) or 0,
        )
        monkeypatch.setattr(window, "save_invoices_db", lambda: save_calls.append(True))

        amount_item = window.invoice_table.item(0, 5)
        amount_item.setText("nicht lesbar")

        assert invoice.amount == 19.99
        assert amount_item.text() == "19.99"
        assert "ungültig" in amount_item.toolTip()
        assert "ungültig" in window.log_output.toPlainText()
        assert warnings and warnings[0][0][1] == "Ungültiger Betrag"
        assert not save_calls
    finally:
        window.close()


def test_mainwindow_keyboard_shortcuts_and_control_accessibility(tmp_path, monkeypatch, qapp):
    """MainWindow registers keyboard shortcuts and exposes rich accessibility attributes."""
    monkeypatch.setattr(uim, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(uim, "INVOICES_DB", tmp_path / "invoices.json")

    window = uim.MainWindow()
    try:
        # Check shortcuts
        assert window.shortcut_refresh_f5.key() == QKeySequence("F5")
        assert window.shortcut_refresh_ctrl_r.key() == QKeySequence("Ctrl+R")
        assert window.shortcut_start_ctrl_ret.key() == QKeySequence("Ctrl+Return")
        assert window.shortcut_start_ctrl_ent.key() == QKeySequence("Ctrl+Enter")
        assert window.shortcut_open_folder.key() == QKeySequence("Ctrl+O")
        assert window.shortcut_select_all.key() == QKeySequence("Ctrl+A")
        assert window.shortcut_select_none_esc.key() == QKeySequence("Escape")
        assert window.shortcut_select_none_ctrl.key() == QKeySequence("Ctrl+Shift+A")
        assert window.shortcut_delete_invoices.key() == QKeySequence("Delete")
        assert window.shortcut_export_csv.key() == QKeySequence("Ctrl+E")
        assert window.shortcut_save_settings.key() == QKeySequence("Ctrl+S")

        # Check main controls accessibility
        assert window.btn_start.accessibleName() == "Rechnungen abrufen"
        assert "Strg+Eingabetaste" in window.btn_start.toolTip()

        assert window.cb_timeframe.accessibleName() == "Zeitraum-Schnellauswahl"
        assert window.date_from.accessibleName() == "Zeitraum Von"
        assert window.date_to.accessibleName() == "Zeitraum Bis"

        assert window.profile_list.accessibleName() == "Suchprofile"
        assert window.account_list.accessibleName() == "E-Mail-Konten"

        # Settings tab controls
        assert window.inp_path.accessibleName() == "Speicherordner-Pfad"
        assert window.ck_attachments.accessibleName() == "PDF-Anhänge herunterladen"
        assert window.ck_body_pdf.accessibleName() == "Mail-Body als PDF speichern"
        assert window.ck_merge_body.accessibleName() == "Mail-Body an PDF anhängen"
        assert window.ck_hash.accessibleName() == "Duplikat-Erkennung"
        assert window.ck_trash.accessibleName() == "Papierkorb durchsuchen"
        assert window.cmb_pdf_mode.accessibleName() == "PDF-Erstellungsmodus"
        assert window.ck_ocr.accessibleName() == "OCR-Texterkennung"
        assert window.inp_max_mails.accessibleName() == "Maximale Mails pro Durchlauf"
        assert window.findChild(QPushButton, "save_settings_button").accessibleName() == "Einstellungen speichern"
    finally:
        window.close()


def test_account_dialog_accessibility_and_buddies(qapp):
    """AccountDialog provides screenreader context and mnemonic keyboard buddies."""
    dialog = uim.AccountDialog()
    try:
        assert dialog.windowTitle() == "E-Mail-Konto"

        # Accessible names & descriptions
        assert dialog.inp_name.accessibleName() == "Anzeigename"
        assert "Identifizierung" in dialog.inp_name.accessibleDescription()

        assert dialog.cb_provider.accessibleName() == "E-Mail-Anbieter"
        assert dialog.ck_gmail_api.accessibleName() == "Gmail API nutzen"

        assert dialog.inp_host.accessibleName() == "IMAP-Server"
        assert dialog.inp_port.accessibleName() == "IMAP-Port"
        assert dialog.inp_user.accessibleName() == "Benutzername"
        assert dialog.inp_pass.accessibleName() == "Passwort"

        # Check label buddies
        labels = dialog.findChildren(QLabel)
        buddies = {lbl.text(): lbl.buddy() for lbl in labels if lbl.buddy() is not None}

        assert "&Anzeigename:" in buddies and buddies["&Anzeigename:"] == dialog.inp_name
        assert "&Anbieter:" in buddies and buddies["&Anbieter:"] == dialog.cb_provider
        assert "&Server:" in buddies and buddies["&Server:"] == dialog.inp_host
        assert "&Port:" in buddies and buddies["&Port:"] == dialog.inp_port
        assert "&Benutzername:" in buddies and buddies["&Benutzername:"] == dialog.inp_user
        assert "&Passwort:" in buddies and buddies["&Passwort:"] == dialog.inp_pass

        # Buttons
        assert dialog.findChild(QPushButton, "account_dialog_ok_button").accessibleName() == "Konto speichern"
        assert dialog.findChild(QPushButton, "account_dialog_cancel_button").accessibleName() == "Abbrechen"
    finally:
        dialog.close()


def test_profile_dialog_accessibility_and_buddies(qapp):
    """ProfileDialog provides screenreader context and mnemonic keyboard buddies."""
    acc = uim.MailAccount(
        id="acc_test",
        name="Test Mail",
        provider="IMAP",
        host="imap.test.de",
        port=993,
        username="user@test.de",
    )
    dialog = uim.ProfileDialog([acc])
    try:
        assert dialog.windowTitle() == "Suchprofil"

        # Accessible names & descriptions
        assert dialog.inp_name.accessibleName() == "Profilname"
        assert dialog.cb_account.accessibleName() == "Zugeordnetes E-Mail-Konto"
        assert dialog.cb_shop.accessibleName() == "Shop-Vorlage"
        assert dialog.inp_sender.accessibleName() == "Absender-Filter"
        assert dialog.inp_subject.accessibleName() == "Betreff-Filter"
        assert dialog.inp_gmail_query.accessibleName() == "Gmail-Query-Filter"
        assert dialog.findChild(QPushButton, "open_query_builder_button").accessibleName() == "Gmail-Query-Builder öffnen"
        assert dialog.inp_blacklist.accessibleName() == "Ausschlussfilter"
        assert dialog.inp_body_must.accessibleName() == "Erforderlicher Nachrichtentext"
        assert dialog.inp_body_must_not.accessibleName() == "Ausgeschlossener Nachrichtentext"
        assert dialog.inp_folder.accessibleName() == "Ziel-Unterordner"
        assert dialog.ck_enabled.accessibleName() == "Suchprofil aktiviert"

        # Label buddies
        labels = dialog.findChildren(QLabel)
        buddies = {lbl.text(): lbl.buddy() for lbl in labels if lbl.buddy() is not None}

        assert "&Name:" in buddies and buddies["&Name:"] == dialog.inp_name
        assert "&E-Mail-Konto:" in buddies and buddies["&E-Mail-Konto:"] == dialog.cb_account
        assert "&Shop-Vorlage:" in buddies and buddies["&Shop-Vorlage:"] == dialog.cb_shop
        assert "A&bsender enthält:" in buddies and buddies["A&bsender enthält:"] == dialog.inp_sender
        assert "B&etreff enthält:" in buddies and buddies["B&etreff enthält:"] == dialog.inp_subject
        assert "&Gmail-Query:" in buddies and buddies["&Gmail-Query:"] == dialog.inp_gmail_query
        assert "&Darf NICHT enthalten:" in buddies and buddies["&Darf NICHT enthalten:"] == dialog.inp_blacklist
        assert "Body &muss enthalten:" in buddies and buddies["Body &muss enthalten:"] == dialog.inp_body_must
        assert "Body darf &nicht enthalten:" in buddies and buddies["Body darf &nicht enthalten:"] == dialog.inp_body_must_not
        assert "&Unterordner:" in buddies and buddies["&Unterordner:"] == dialog.inp_folder

        # Buttons
        assert dialog.findChild(QPushButton, "profile_dialog_ok_button").accessibleName() == "Profil speichern"
        assert dialog.findChild(QPushButton, "profile_dialog_cancel_button").accessibleName() == "Abbrechen"
    finally:
        dialog.close()


def test_query_builder_dialog_accessibility(qapp):
    """QueryBuilderDialog provides screenreader context and accessible radio buttons."""
    dialog = uim.QueryBuilderDialog()
    try:
        assert dialog.windowTitle() == "Gmail-Suchabfrage erstellen"

        # Radio buttons
        assert dialog.rb_all.accessibleName() == "Suchbereich Überall außer Papierkorb"
        assert dialog.rb_inbox.accessibleName() == "Suchbereich Nur Posteingang"
        assert dialog.rb_sent.accessibleName() == "Suchbereich Gesendet"
        assert dialog.rb_trash.accessibleName() == "Suchbereich Auch Papierkorb"

        # Form controls
        assert dialog.cb_time.accessibleName() == "Zeitraum-Vorlage"
        assert dialog.de_from.accessibleName() == "Query-Datum Von"
        assert dialog.de_to.accessibleName() == "Query-Datum Bis"
        assert dialog.inp_from.accessibleName() == "Absender-Filter"
        assert dialog.inp_subject.accessibleName() == "Betreff-Filter"
        assert dialog.chk_attachment.accessibleName() == "Muss Anhänge haben"
        assert dialog.result_query.accessibleName() == "Erzeugte Gmail-Query"

        # Buttons
        assert dialog.findChild(QPushButton, "query_generate_button").accessibleName() == "Query generieren"
        assert dialog.findChild(QPushButton, "query_dialog_ok_button").accessibleName() == "Query übernehmen"
        assert dialog.findChild(QPushButton, "query_dialog_cancel_button").accessibleName() == "Abbrechen"
    finally:
        dialog.close()
def test_shortcuts_dialog_content_and_accessibility(qapp):
    """ShortcutsDialog lists key combinations, provides WCAG 2.1 AA context, and supports offscreen testing."""
    shortcuts = [
        ("F1", "Tastaturkürzel & Barrierefreiheits-Hilfe anzeigen", "Global"),
        ("Strg+Eingabe / Strg+Enter", "Rechnungen abrufen (Start)", "Global"),
        ("F5 / Strg+R", "Rechnungstabelle mit Ordnerinhalt aktualisieren", "Global / Rechnungen"),
        ("Strg+O", "Speicherordner für Rechnungen im Dateimanager öffnen", "Global / Rechnungen"),
        ("Strg+A", "Alle sichtbaren Rechnungen in der Tabelle markieren", "Rechnungen"),
        ("Esc / Strg+Umschalt+A", "Markierungen in der Rechnungstabelle aufheben", "Rechnungen"),
        ("Eingabe / Return", "Ausgewählte Rechnung öffnen / Profil bzw. Konto bearbeiten", "Tabelle / Listen"),
        ("Leertaste", "Rechnungs-Auswahlfeld umschalten (Check/Uncheck)", "Rechnungstabelle"),
        ("Entf / Backspace", "Ausgewählte Rechnungen, Profile oder Konten löschen", "Tabelle / Listen"),
        ("Strg+E", "Rechnungsliste als CSV exportieren", "Rechnungen"),
        ("Strg+S", "Einstellungen speichern", "Einstellungen"),
        ("Alt+B", "Fokus auf Beraternummer setzen", "DATEV-Dialog"),
        ("Alt+M", "Fokus auf Mandantennummer setzen", "DATEV-Dialog"),
        ("Alt+Z / Einfg", "Neue Zeile im Konten-Mapping hinzufügen", "DATEV-Dialog"),
        ("Alt+E / Entf", "Ausgewählte Zeile im Konten-Mapping entfernen", "DATEV-Dialog"),
        ("Alt+S", "Standardmäßige Konten-Zuordnung wiederherstellen", "DATEV-Dialog"),
    ]
    dialog = uim.ShortcutsDialog(shortcuts)
    try:
        assert dialog.windowTitle() == "Tastaturkürzel & Hilfe"
        assert dialog.objectName() == "shortcuts_help_dialog"
        assert dialog.accessibleName() == "Tastaturkürzel und Hilfe"
        assert "Übersicht" in dialog.accessibleDescription()

        assert dialog.table.rowCount() == len(shortcuts)
        assert dialog.table.columnCount() == 3
        assert dialog.table.objectName() == "shortcuts_table"
        assert dialog.table.accessibleName() == "Tabelle aller Tastaturkürzel"
        assert "barrierefreien Bedienung" in dialog.table.accessibleDescription()

        # Check first and last shortcut entries
        assert dialog.table.item(0, 0).text() == "F1"
        assert dialog.table.item(0, 1).text() == "Tastaturkürzel & Barrierefreiheits-Hilfe anzeigen"
        assert dialog.table.item(0, 2).text() == "Global"

        assert dialog.table.item(len(shortcuts) - 1, 0).text() == "Alt+S"

        # Close button
        assert dialog.close_btn is not None
        assert dialog.close_btn.objectName() == "shortcuts_dialog_close_button"
        assert dialog.close_btn.accessibleName() == "Dialog schließen"
    finally:
        dialog.close()


def test_mainwindow_shortcuts_f1_and_help_button(tmp_path, monkeypatch, qapp):
    """MainWindow registers F1 shortcut, provides a visible help button, and returns shortcuts in offscreen mode."""
    monkeypatch.setattr(uim, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(uim, "INVOICES_DB", tmp_path / "invoices.json")

    window = uim.MainWindow()
    try:
        # F1 Shortcut registered
        assert hasattr(window, "shortcut_help_f1")
        assert window.shortcut_help_f1.key() == QKeySequence("F1")

        # Visible button in toolbar
        btn_help = window.findChild(QPushButton, "show_shortcuts_button")
        assert btn_help is not None
        assert btn_help.text() == "❓ Hilfe & Kürzel"
        assert btn_help.accessibleName() == "Tastaturkürzel und Hilfe anzeigen"
        assert "F1" in btn_help.toolTip()

        # show_shortcuts_dialog() offscreen bypass returns title and list of shortcuts
        title, sc_list = window.show_shortcuts_dialog()
        assert title == "Tastaturkürzel & Hilfe"
        assert len(sc_list) == 16
        keys = [sc[0] for sc in sc_list]
        assert "F1" in keys
        assert "Strg+Eingabe / Strg+Enter" in keys
        assert "F5 / Strg+R" in keys
        assert "Ctrl+O" in [k.replace("Strg", "Ctrl") for k in keys]
    finally:
        window.close()


def test_datev_settings_dialog_accessibility_and_buddies(qapp):
    """DATEVSettingsDialog provides mnemonic buddies, object names, and accessible descriptions."""
    config = uim.DATEVConfig(
        berater_nr="98765",
        mandant_nr="43210",
        konten_mapping={"TestProvider": (70001, 4901)},
    )
    dialog = uim.DATEVSettingsDialog(config)
    try:
        assert dialog.objectName() == "datev_settings_dialog"
        assert dialog.accessibleName() == "DATEV-Export Einstellungen und Konten-Mapping"

        # Object names
        assert dialog.inp_berater.objectName() == "datev_berater_input"
        assert dialog.inp_mandant.objectName() == "datev_mandant_input"
        assert dialog.table_mapping.objectName() == "datev_mapping_table"
        assert dialog.btn_add_row.objectName() == "datev_add_row_button"
        assert dialog.btn_remove_row.objectName() == "datev_remove_row_button"
        assert dialog.btn_reset_mapping.objectName() == "datev_reset_mapping_button"

        # Label buddies
        labels = dialog.findChildren(QLabel)
        buddies = {lbl.text(): lbl.buddy() for lbl in labels if lbl.buddy() is not None}
        assert "&Beraternummer:" in buddies and buddies["&Beraternummer:"] == dialog.inp_berater
        assert "&Mandantennummer:" in buddies and buddies["&Mandantennummer:"] == dialog.inp_mandant

        # Button texts & mnemonics
        assert "&Zeile hinzufügen" in dialog.btn_add_row.text()
        assert "Zeile &entfernen" in dialog.btn_remove_row.text()
        assert "&Standard wiederherstellen" in dialog.btn_reset_mapping.text()

        # Table items have tooltips
        assert dialog.table_mapping.rowCount() == 1
        item_k = dialog.table_mapping.item(0, 0)
        assert item_k is not None and "Absender" in item_k.toolTip()
        item_c = dialog.table_mapping.item(0, 1)
        assert item_c is not None and "Kreditorenkonto" in item_c.toolTip()

        # Dialog buttons have object names
        ok_btn = dialog.dialog_buttons.button(uim.QDialogButtonBox.StandardButton.Ok)
        assert ok_btn.objectName() == "datev_dialog_ok_button"
        assert ok_btn.accessibleName() == "DATEV-Einstellungen speichern"

        cancel_btn = dialog.dialog_buttons.button(uim.QDialogButtonBox.StandardButton.Cancel)
        assert cancel_btn.objectName() == "datev_dialog_cancel_button"
        assert cancel_btn.accessibleName() == "DATEV-Einstellungen verwerfen"
    finally:
        dialog.close()


def test_accessible_mapping_table_keyboard_navigation(qapp):
    """AccessibleMappingTable handles Delete/Backspace (remove row) and Insert (add row)."""
    from PySide6.QtGui import QKeyEvent

    config = uim.DATEVConfig(
        berater_nr="12345",
        mandant_nr="67890",
        konten_mapping={"A": (70000, 4900), "B": (70001, 4901)},
    )
    dialog = uim.DATEVSettingsDialog(config)
    try:
        assert dialog.table_mapping.rowCount() == 2

        # Select row 1 and press Delete
        dialog.table_mapping.setCurrentCell(1, 0)
        del_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Delete, Qt.KeyboardModifier.NoModifier)
        dialog.table_mapping.keyPressEvent(del_event)
        assert dialog.table_mapping.rowCount() == 1

        # Press Insert to add row
        ins_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Insert, Qt.KeyboardModifier.NoModifier)
        dialog.table_mapping.keyPressEvent(ins_event)
        assert dialog.table_mapping.rowCount() == 2
        assert dialog.table_mapping.item(1, 0).text() == "Neuer Partner"
    finally:
        dialog.close()


def test_accessible_invoice_table_keyboard_navigation(tmp_path, monkeypatch, qapp):
    """AccessibleInvoiceTable handles Enter (open invoice) and Space (toggle checkbox)."""
    from PySide6.QtGui import QKeyEvent

    monkeypatch.setattr(uim, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(uim, "INVOICES_DB", tmp_path / "invoices.json")

    window = uim.MainWindow()
    try:
        invoice_path = tmp_path / "test_rechnung.pdf"
        invoice_path.write_bytes(b"dummy")
        inv = uim.Invoice(
            id="inv_kb_1",
            profile_name="Shop",
            filename="test_rechnung.pdf",
            date="2026-09-26",
            path=str(invoice_path),
            amount=42.50,
        )
        window.invoices = [inv]
        window.refresh_invoice_table()

        assert window.invoice_table.rowCount() == 1

        # Test Space key toggles checkmark
        window.invoice_table.setCurrentCell(0, 0)
        item0 = window.invoice_table.item(0, 0)
        assert item0.checkState() == Qt.CheckState.Unchecked

        space_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier)
        window.invoice_table.keyPressEvent(space_event)
        assert item0.checkState() == Qt.CheckState.Checked

        window.invoice_table.keyPressEvent(space_event)
        assert item0.checkState() == Qt.CheckState.Unchecked

        # Test Enter key triggers cellDoubleClicked
        opened = []
        window.invoice_table.cellDoubleClicked.connect(lambda row, col: opened.append((row, col)))
        enter_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
        window.invoice_table.keyPressEvent(enter_event)
        assert opened == [(0, 0)]
    finally:
        window.close()


def test_accessible_list_widget_keyboard_navigation(qapp):
    """AccessibleListWidget handles Return (edit callback) and Delete (delete callback)."""
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QListWidgetItem

    edited = []
    deleted = []

    list_widget = uim.AccessibleListWidget(
        on_edit_callback=lambda item: edited.append(item.text()),
        on_delete_callback=lambda: deleted.append(True),
    )
    try:
        item1 = QListWidgetItem("Item 1")
        item2 = QListWidgetItem("Item 2")
        list_widget.addItem(item1)
        list_widget.addItem(item2)

        list_widget.setCurrentItem(item1)

        # Press Enter -> on_edit_callback
        ret_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
        list_widget.keyPressEvent(ret_event)
        assert edited == ["Item 1"]

        # Press Delete -> on_delete_callback
        del_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Delete, Qt.KeyboardModifier.NoModifier)
        list_widget.keyPressEvent(del_event)
        assert deleted == [True]
    finally:
        list_widget.close()
