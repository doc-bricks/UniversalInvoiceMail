"""Test: UniversalInvoiceMail importierbar ohne Gmail-Pakete (Regression Bug #17).

Bug #17: `-> Optional[Credentials]` in `_get_gmail_credentials()` war eine eager
ausgewertete Annotation. Ohne Gmail-Pakete ist `Credentials` undefiniert ->
NameError beim Klassenaufbau -> Modul-Import schlägt fehl -> App startet nicht.
Fix: Annotation als String `-> "Optional[Credentials]"` (lazy, nicht eager).
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


def _setup_non_google_mocks():
    """Mockt alle optionalen Abhängigkeiten außer Google-Paketen."""
    for mod in [
        'PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtCore', 'PyQt6.QtGui',
        'xhtml2pdf', 'xhtml2pdf.pisa', 'pytesseract', 'pypdfium2',
        'pypdf', 'PIL', 'PIL.Image', 'selenium', 'selenium.webdriver',
        'selenium.webdriver.edge.options', 'selenium.webdriver.edge.service',
        'selenium.webdriver.chrome.options', 'selenium.webdriver.chrome.service',
        'webdriver_manager', 'webdriver_manager.microsoft', 'webdriver_manager.chrome',
        'keyring',
        'reportlab', 'reportlab.pdfgen', 'reportlab.lib',
        'reportlab.lib.pagesizes', 'reportlab.lib.units', 'reportlab.lib.utils',
        'docx2pdf', 'win32com', 'win32com.client', 'pythoncom',
    ]:
        if mod not in sys.modules:
            sys.modules[mod] = MagicMock()
    sys.modules['PyQt6.QtCore'].Qt = MagicMock()
    sys.modules['PyQt6.QtCore'].QThread = MagicMock()
    sys.modules['PyQt6.QtCore'].Signal = MagicMock(return_value=MagicMock())
    sys.modules['PyQt6.QtCore'].QUrl = MagicMock()
    sys.modules['PyQt6.QtCore'].QSize = MagicMock()


def test_import_without_gmail_packages():
    """Modul importiert sauber wenn Gmail-Pakete fehlen.

    Ohne den Fix würde der Import mit NameError: name 'Credentials' is not defined
    in Zeile ~1554 (_get_gmail_credentials Klassendefinition) fehlschlagen.

    Technik: sys.modules[mod] = None blockiert den Import zuverlässig auch wenn
    die echten Pakete installiert sind (Pythons Standard-Mechanismus).
    """
    _setup_non_google_mocks()

    google_block = [
        'google', 'googleapiclient', 'google_auth_oauthlib',
        'google.auth', 'google.auth.transport', 'google.auth.transport.requests',
        'google.oauth2', 'google.oauth2.credentials', 'google.auth.exceptions',
        'googleapiclient.discovery',
        'google_auth_oauthlib.flow',
    ]

    # Vorherigen Zustand sichern (kann MagicMock, echtes Modul oder None sein)
    saved = {k: sys.modules.get(k, _MISSING) for k in google_block}
    saved_uim = sys.modules.get('UniversalInvoiceMail', _MISSING)

    # Auf None setzen → Python meldet ImportError wenn dieses Modul angefordert wird
    for k in google_block:
        sys.modules[k] = None  # type: ignore[assignment]

    # Gecachte UniversalInvoiceMail-Version ebenfalls entfernen (Fresh-Import)
    sys.modules.pop('UniversalInvoiceMail', None)

    try:
        import UniversalInvoiceMail as uim
        assert hasattr(uim, 'InvoiceWorker'), "InvoiceWorker fehlt nach Import"
        assert uim.GMAIL_API_AVAILABLE is False, "GMAIL_API_AVAILABLE sollte False sein"
    finally:
        if saved_uim is _MISSING:
            sys.modules.pop('UniversalInvoiceMail', None)
        else:
            sys.modules['UniversalInvoiceMail'] = saved_uim
        for k, v in saved.items():
            if v is _MISSING:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v  # type: ignore[assignment]


_MISSING = object()  # Sentinel für "war nicht in sys.modules"
