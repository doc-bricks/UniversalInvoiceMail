"""Store-Material-Tests für UniversalInvoiceMail.

Prüft, ob alle für den Windows Store benötigten Artefakte vorhanden und
inhaltlich korrekt sind.
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_store_package_json_exists_and_valid():
    path = PROJECT_ROOT / "store_package.json"
    assert path.exists(), "store_package.json fehlt"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["app_name"] == "UniversalInvoiceMail"
    assert "Geiger" in data["identity_name"]
    assert "languages" in data and len(data["languages"]) >= 2
    assert "runFullTrust" in data["capabilities"]
    assert data.get("license") == "MIT"


def test_store_listing_has_de_and_en():
    path = PROJECT_ROOT / "STORE_LISTING.md"
    assert path.exists(), "STORE_LISTING.md fehlt"
    content = path.read_text(encoding="utf-8")
    assert "Deutsch" in content or "## DE" in content or "German" in content
    assert "English" in content or "## EN" in content


def test_privacy_policy_mentions_local_and_keyring():
    path = PROJECT_ROOT / "PRIVACY_POLICY.md"
    assert path.exists(), "PRIVACY_POLICY.md fehlt"
    content = path.read_text(encoding="utf-8").lower()
    assert "lokal" in content or "local" in content
    assert "keyring" in content or "credential" in content or "schlüssel" in content


def test_support_md_exists():
    path = PROJECT_ROOT / "SUPPORT.md"
    assert path.exists(), "SUPPORT.md fehlt"
    content = path.read_text(encoding="utf-8")
    assert "http" in content or "github.com" in content


def test_windows_store_prep_exists():
    path = PROJECT_ROOT / "WINDOWS_STORE_PREP.md"
    assert path.exists(), "WINDOWS_STORE_PREP.md fehlt"


def test_screenshot_store_dir_exists():
    path = PROJECT_ROOT / "README" / "screenshots" / "store"
    assert path.exists(), "README/screenshots/store Verzeichnis fehlt"
    for name in [
        "01_rechnungsuebersicht.png",
        "02_postfach_konfiguration.png",
        "03_datev_export.png",
        "04_bundle_companion.png",
    ]:
        assert (path / name).is_file(), f"Screenshot {name} fehlt in {path}"


def test_portierungsplan_mentions_store_ready():
    path = PROJECT_ROOT / "PORTIERUNGSPLAN.md"
    assert path.exists(), "PORTIERUNGSPLAN.md fehlt"
    content = path.read_text(encoding="utf-8")
    assert "Windows Store" in content
    assert "universalinvoicemail-invoicebundle-v1" in content
