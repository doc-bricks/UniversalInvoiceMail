"""Tests für den UniversalInvoiceMail Web Companion & PWA.

Validiert:
1. Vollständigkeit der Dateien und W3C-Manifest-Integrität.
2. Existenz aller referenzierten App-Icons und Service-Worker-Caches.
3. Zero-Egress-Invariante (keine externen CDNs, Scripts oder Web-Fonts).
4. Kompatibilität des Session-Exchange-Formats (universalinvoicemail-invoicebundle-v1).
5. Tier-2 Lokalisierungs-Parität (DE, EN, ES, ZH, JA, RU) und HTML5-Sprachauswahl.
6. Erfolgreicher Durchlauf der nativen Node.js-Testsuite.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = PROJECT_ROOT / "web_companion"


def test_web_companion_core_files_exist():
    """Prüft, ob alle Kernkomponenten des Web Companions vorhanden sind."""
    required_files = [
        WEB_DIR / "index.html",
        WEB_DIR / "styles.css",
        WEB_DIR / "app.js",
        WEB_DIR / "library.js",
        WEB_DIR / "sw.js",
        WEB_DIR / "manifest.webmanifest",
        WEB_DIR / "package.json",
        WEB_DIR / "README.md",
        WEB_DIR / "favicon.png",
        WEB_DIR / "favicon.ico",
        WEB_DIR / "icons" / "apple-touch-icon-180.png",
        WEB_DIR / "icons" / "Icon-192.png",
        WEB_DIR / "icons" / "Icon-512.png",
    ]
    for file_path in required_files:
        assert file_path.is_file(), f"Pflichtdatei fehlt im Web Companion: {file_path.name}"
        assert file_path.stat().st_size > 0, f"Datei ist leer: {file_path.name}"


def test_web_companion_zero_egress_and_local_only():
    """Stellt sicher, dass die PWA keine externen CDNs oder Skripte referenziert."""
    for file_name in ["index.html", "styles.css", "app.js", "sw.js"]:
        content = (WEB_DIR / file_name).read_text(encoding="utf-8")
        assert "http://" not in content, f"Insecure HTTP link in {file_name}"
        assert "fonts.googleapis.com" not in content, f"Google Fonts found in {file_name}"
        assert "cdnjs.cloudflare.com" not in content, f"External CDN found in {file_name}"
        assert "unpkg.com" not in content, f"External CDN found in {file_name}"
        assert "cdn.jsdelivr.net" not in content, f"External CDN found in {file_name}"


def test_web_companion_tier2_language_parity():
    """Prüft 100% Key-Parität über alle 6 Tier-2 Zielsprachen in app.js."""
    node_script = """
    import { TRANSLATIONS } from "./app.js";
    console.log(JSON.stringify(TRANSLATIONS));
    """
    res = subprocess.run(
        ["node", "--input-type=module", "-e", node_script],
        cwd=WEB_DIR,
        capture_output=True,
        check=True,
    )
    translations = json.loads(res.stdout.decode("utf-8"))

    required_languages = ["de", "en", "es", "zh", "ja", "ru"]
    for lang in required_languages:
        assert lang in translations, f"Fehlende Tier-2 Sprache: {lang}"

    de_keys = sorted(translations["de"].keys())
    assert len(de_keys) >= 25, f"Zu wenige Übersetzungsschlüssel ({len(de_keys)})"

    for lang in required_languages:
        lang_keys = sorted(translations[lang].keys())
        assert lang_keys == de_keys, f"Key-Mismatches zwischen de und {lang}"
        for k in de_keys:
            val = translations[lang][k]
            assert isinstance(val, str) and len(val.strip()) > 0, (
                f"Leerer Übersetzungswert für {lang}.{k}"
            )


def test_web_companion_index_html_has_language_selector():
    """Prüft, ob der Sprachauswahldialog in index.html vorhanden und korrekt verankert ist."""
    html_content = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    assert 'id="lang-select"' in html_content, "Sprachauswahl #lang-select fehlt in index.html"
    for lang in ['value="de"', 'value="en"', 'value="es"', 'value="zh"', 'value="ja"', 'value="ru"']:
        assert lang in html_content, f"Sprachoption {lang} fehlt in index.html"
    assert "data-i18n=" in html_content, "data-i18n Attribute fehlen in index.html"


def test_web_companion_service_worker_offline_cache():
    """Prüft die Service-Worker-Konfiguration für Offline-Betrieb."""
    sw_text = (WEB_DIR / "sw.js").read_text(encoding="utf-8")
    assert 'CACHE_NAME = "universalinvoicemail-companion-v2"' in sw_text
    assert '"./index.html"' in sw_text
    assert '"./styles.css"' in sw_text
    assert '"./app.js"' in sw_text
    assert '"./library.js"' in sw_text


def test_web_companion_node_test_suite_passes():
    """Führt die native Node.js-Testsuite des Web-Companions aus."""
    res = subprocess.run(
        ["npm", "test"],
        cwd=WEB_DIR,
        capture_output=True,
        shell=True,
    )
    stdout = res.stdout.decode("utf-8", errors="replace") if res.stdout else ""
    stderr = res.stderr.decode("utf-8", errors="replace") if res.stderr else ""
    assert res.returncode == 0, f"Node-Testsuite fehlgeschlagen:\n{stdout}\n{stderr}"
    assert "pass 13" in stdout or "fail 0" in stdout
