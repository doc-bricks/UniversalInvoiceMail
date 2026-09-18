"""Tests for scripts/check_store_readiness.py."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.check_store_readiness import (
    REQUIRED_CANONICAL_PUBLISHER,
    REQUIRED_DOCUMENTS,
    REQUIRED_STORE_ICONS,
    REQUIRED_STORE_SCREENSHOTS,
    run_store_readiness_check,
)


def test_full_store_readiness_check_passes():
    findings = run_store_readiness_check(PROJECT_ROOT, require_executable=False)
    assert findings == [], f"Preflight-Store-Audit hat unerwartete Befunde: {findings}"


def test_required_documents_exist():
    for doc in REQUIRED_DOCUMENTS:
        doc_path = PROJECT_ROOT / doc
        assert doc_path.is_file(), f"Pflichtdokument fehlt: {doc}"


def test_store_icons_match_specification():
    icons_dir = PROJECT_ROOT / "store_package" / "UniversalInvoiceMail" / "icons"
    assert icons_dir.is_dir(), "Icons-Verzeichnis store_package/UniversalInvoiceMail/icons/ fehlt"

    from scripts.check_store_readiness import _png_size

    for name, (req_w, req_h) in REQUIRED_STORE_ICONS.items():
        icon_path = icons_dir / name
        assert icon_path.is_file(), f"Icon {name} fehlt"
        w, h = _png_size(icon_path)
        assert (w, h) == (req_w, req_h), f"{name}: Erwartet ({req_w}, {req_h}), erhalten ({w}, {h})"


def test_store_screenshots_match_aspect_ratio():
    screen_dir = PROJECT_ROOT / "store_package" / "UniversalInvoiceMail" / "screenshots"
    assert screen_dir.is_dir(), "Screenshots-Verzeichnis fehlt"

    from scripts.check_store_readiness import _png_size

    for name in REQUIRED_STORE_SCREENSHOTS:
        shot = screen_dir / name
        assert shot.is_file(), f"Screenshot {name} fehlt"
        w, h = _png_size(shot)
        assert w >= 1366, f"{name}: Breite {w} < 1366"
        assert h >= 768, f"{name}: Höhe {h} < 768"
        assert round(w / h, 2) == 1.78, f"{name}: Kein 16:9-Verhältnis ({w}x{h})"


def test_publisher_is_canonical():
    data = json.loads((PROJECT_ROOT / "store_package.json").read_text(encoding="utf-8"))
    assert data.get("publisher") == REQUIRED_CANONICAL_PUBLISHER
    assert data.get("publisher_id") == REQUIRED_CANONICAL_PUBLISHER


def test_partner_center_10_1_3_keywords_max_7():
    content = (PROJECT_ROOT / "STORE_LISTING.md").read_text(encoding="utf-8")

    de_match = re.search(r"### Schlüsselwörter[^\n]*\n+([^\n#]+)", content)
    assert de_match is not None, "Deutsche Schlüsselwörter nicht gefunden"
    de_kws = [k.strip() for k in de_match.group(1).split(",") if k.strip()]
    assert len(de_kws) <= 7, f"Zu viele deutsche Keywords: {len(de_kws)} > 7"
    for k in de_kws:
        assert len(k) <= 30, f"Keyword zu lang: '{k}'"

    en_match = re.search(r"### Keywords[^\n]*\n+([^\n#]+)", content)
    assert en_match is not None, "Englische Keywords nicht gefunden"
    en_kws = [k.strip() for k in en_match.group(1).split(",") if k.strip()]
    assert len(en_kws) <= 7, f"Zu viele englische Keywords: {len(en_kws)} > 7"
    for k in en_kws:
        assert len(k) <= 30, f"Keyword zu lang: '{k}'"


def test_store_package_json_license_is_mit():
    data = json.loads((PROJECT_ROOT / "store_package.json").read_text(encoding="utf-8"))
    assert data.get("license") == "MIT"


def test_appx_manifest_properties_logo_is_store_logo():
    manifest_path = PROJECT_ROOT / "store_package" / "UniversalInvoiceMail" / "AppxManifest.xml"
    content = manifest_path.read_text(encoding="utf-8")
    assert "<Logo>icons\\StoreLogo.png</Logo>" in content or "<Logo>icons/StoreLogo.png</Logo>" in content
    assert "icon_150x150.png" not in content.split("<Properties>")[1].split("</Properties>")[0]


def test_release_staging_directory_and_files():
    from scripts.check_store_readiness import REQUIRED_RELEASE_STAGING_FILES, REQUIRED_STORE_SCREENSHOTS
    staging_dir = PROJECT_ROOT / "releases" / "windowsstore"
    assert staging_dir.is_dir(), "Release-Staging-Verzeichnis fehlt"
    for f in REQUIRED_RELEASE_STAGING_FILES:
        p = staging_dir / f
        assert p.is_file(), f"Staging-Datei {f} fehlt"
        assert p.stat().st_size > 0, f"Staging-Datei {f} ist leer"
    st_screen_dir = staging_dir / "screenshots"
    assert st_screen_dir.is_dir()
    for s in REQUIRED_STORE_SCREENSHOTS:
        assert (st_screen_dir / s).is_file(), f"Screenshot {s} fehlt im Staging"
