"""Unit tests for scripts/store_assets.py."""

from __future__ import annotations

import sys
from pathlib import Path
from xml.etree import ElementTree as ET

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.store_assets import (
    APP_NAME,
    ICON_DIR,
    LEGACY_ICON_NAMES,
    LEGACY_STORE_ASSETS_DIR,
    STORE_PACKAGE_DIR,
    load_store_config,
    render_manifest,
)


def test_load_store_config():
    config = load_store_config(PROJECT_ROOT)
    assert config["app_name"] == APP_NAME
    assert "Geiger" in config["identity_name"]
    assert config["publisher"] == "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"


def test_render_manifest_xml_validity():
    config = load_store_config(PROJECT_ROOT)
    manifest_xml = render_manifest(config)

    # Validate XML parsing
    root = ET.fromstring(manifest_xml)
    assert root.tag.endswith("Package")

    # Check restricted capabilities
    assert "runFullTrust" in manifest_xml
    assert "Geiger.UniversalInvoiceMail" in manifest_xml
    assert "CN=52596601-BAB4-4F3F-B182-E8F3F273B202" in manifest_xml


def test_generated_assets_exist():
    # Icons must exist
    for icon_name in [
        "icon_44x44.png",
        "icon_50x50.png",
        "icon_150x150.png",
        "icon_310x150.png",
        "icon_310x310.png",
        "SplashScreen.png",
    ]:
        path = ICON_DIR / icon_name
        assert path.is_file(), f"{icon_name} fehlt in {ICON_DIR}"
        assert path.stat().st_size > 0

    # Legacy assets must exist
    for legacy_name in LEGACY_ICON_NAMES.values():
        path = LEGACY_STORE_ASSETS_DIR / legacy_name
        assert path.is_file(), f"{legacy_name} fehlt in {LEGACY_STORE_ASSETS_DIR}"

    # Manifests must exist
    assert (STORE_PACKAGE_DIR / "AppxManifest.xml").is_file()
    assert (LEGACY_STORE_ASSETS_DIR / "AppxManifest.xml").is_file()
