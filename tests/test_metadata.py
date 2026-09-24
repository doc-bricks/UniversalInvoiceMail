# -*- coding: utf-8 -*-
"""Metadata, Manifest, and Documentation Parity Tests for UniversalInvoiceMail."""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_version_parity():
    """Verify that all version strings across package definitions match exactly."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml missing"
    pyproject_content = pyproject_path.read_text(encoding="utf-8")
    pyproject_ver_match = re.search(r'version\s*=\s*"([^"]+)"', pyproject_content)
    assert pyproject_ver_match, "version not found in pyproject.toml"
    version = pyproject_ver_match.group(1)

    # Check UniversalInvoiceMail.py header docstring
    app_path = REPO_ROOT / "UniversalInvoiceMail.py"
    assert app_path.exists(), "UniversalInvoiceMail.py missing"
    app_content = app_path.read_text(encoding="utf-8")
    assert f"UniversalInvoiceMail V{version}" in app_content or f"UniversalInvoiceMail v{version}" in app_content, (
        f"Version V{version} missing from UniversalInvoiceMail.py docstring"
    )

    # Check CHANGELOG.md
    changelog_path = REPO_ROOT / "CHANGELOG.md"
    assert changelog_path.exists(), "CHANGELOG.md missing"
    changelog_content = changelog_path.read_text(encoding="utf-8")
    assert f"[{version}]" in changelog_content, (
        f"Release [{version}] header missing from CHANGELOG.md"
    )


def test_core_documentation_files():
    """Verify presence and non-emptiness of core documentation and policy files."""
    required_files = [
        "README.md",
        "README-DE.md",
        "llms.txt",
        "LICENSE",
        "CHANGELOG.md",
        "ROADMAP.txt",
        "pyproject.toml",
        "EXPORTFORMAT.md",
        "USER_GUIDE.md",
        "translator.py",
        "locales/translations.json",
        "web_companion/package.json",
        "web_companion/index.html",
        "web_companion/manifest.webmanifest",
        "NOTICE",
        "THIRD_PARTY_LICENSES.md",
        "THIRD_PARTY_LICENSES.txt",
        "MARKETING-LOG.txt",
        ".github/workflows/stale.yml",
        ".github/workflows/welcome.yml",
        ".github/workflows/tests.yml",
        ".github/workflows/source-platform-smoke.yml",
    ]
    for rel_path in required_files:
        file_path = REPO_ROOT / rel_path
        assert file_path.exists(), f"Required file {rel_path} does not exist"
        assert file_path.stat().st_size > 0, f"Required file {rel_path} is empty"


def test_llms_txt_structure():
    """Verify that llms.txt provides complete RAG context and valid metadata."""
    llms_path = REPO_ROOT / "llms.txt"
    content = llms_path.read_text(encoding="utf-8")

    assert "# UniversalInvoiceMail" in content
    assert "Last-checked:" in content
    assert "Verification:" in content
    assert "Safety boundary:" in content
    assert "DATEV" in content
    assert "https://github.com/doc-bricks/UniversalInvoiceMail" in content


def test_web_companion_pwa_assets():
    """Verify that web companion files and icons are complete and valid JSON/HTML."""
    web_dir = REPO_ROOT / "web_companion"
    pkg_path = web_dir / "package.json"
    manifest_path = web_dir / "manifest.webmanifest"

    pkg_data = json.loads(pkg_path.read_text(encoding="utf-8"))
    assert "name" in pkg_data
    assert "scripts" in pkg_data and "test" in pkg_data["scripts"]

    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_data.get("name") == "UniversalInvoiceMail Companion"
    assert "icons" in manifest_data
    assert len(manifest_data["icons"]) >= 2

    # Check icons exist
    for icon_entry in manifest_data["icons"]:
        src = icon_entry["src"].lstrip("./")
        icon_file = web_dir / src
        assert icon_file.exists(), f"Companion icon missing: {src}"


def test_utf8_encoding_and_no_mojibake():
    """Verify that all markdown and python source files are clean UTF-8 without mojibake."""
    suspect_patterns = ["\u00c3\u00a4", "\u00c3\u00bc", "\u00c3\u00b6", "\u00c3\u009f", "\ufffd"]
    check_exts = {".py", ".md", ".txt", ".json", ".toml"}

    for p in REPO_ROOT.rglob("*"):
        if any(part.startswith(".") or part in ("node_modules", "__pycache__") for part in p.parts):
            continue
        if p.is_file() and p.suffix in check_exts:
            try:
                content = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                assert False, f"File {p} failed UTF-8 decoding"
            for pat in suspect_patterns:
                assert pat not in content, f"Mojibake pattern '{pat}' found in {p.relative_to(REPO_ROOT)}"


def test_datev_validation_guidance_matches_the_dialog_contract():
    """User-facing DATEV guidance must not describe the pre-save validation as deferred."""
    german_readme = (REPO_ROOT / "README-DE.md").read_text(encoding="utf-8")
    english_readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    user_guide = (REPO_ROOT / "USER_GUIDE.md").read_text(encoding="utf-8")
    roadmap = (REPO_ROOT / "ROADMAP.txt").read_text(encoding="utf-8")

    assert "Der Dialog prüft vor dem Speichern" in german_readme
    assert "The settings dialog validates" in english_readme
    assert "Der Dialog prüft beim Speichern" in user_guide
    assert "case-insensitive uniqueness" in english_readme
    assert "Groß-/Kleinschreibung" in german_readme
    assert "Rand-Leerzeichen" in user_guide
    assert "Formale Kontenbereichs- sowie Duplikat-/Konfliktregeln bleiben" not in german_readme
    assert "Formal account-range and duplicate/conflict validation is intentionally deferred" not in english_readme
    assert "Die formale Prüfung erlaubter Kontenbereiche" not in user_guide
    assert "154/154" in roadmap
    assert "10/10" in roadmap
    assert "Mapping-Tabelle bleibt als technische" in roadmap
    assert "Automatische oder fachlich verbindliche Kontierung" in roadmap
    assert "93-Spalten-Exportvertrag bleibt" in roadmap
    assert "TASKPLAN ist die kanonische" in roadmap


def test_notice_attribution_and_ecosystem():
    """Verify canonical NOTICE file attribution and ecosystem stewardship."""
    notice_path = REPO_ROOT / "NOTICE"
    assert notice_path.is_file(), "NOTICE file must exist"
    notice_text = notice_path.read_text(encoding="utf-8")

    assert "UniversalInvoiceMail" in notice_text
    assert "Lukas Geiger" in notice_text
    assert "doc-bricks" in notice_text
    assert "open-bricks" in notice_text
    assert "MIT License" in notice_text
    assert "THIRD_PARTY_LICENSES.md" in notice_text


def test_ci_workflow_hardening_contracts():
    """Verify all GitHub Actions workflows enforce concurrency and timeouts."""
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    assert workflows_dir.is_dir(), ".github/workflows directory must exist"

    # stale.yml
    stale_file = workflows_dir / "stale.yml"
    assert stale_file.is_file(), "stale.yml must exist"
    stale_text = stale_file.read_text(encoding="utf-8")
    assert "actions/stale@v9" in stale_text
    assert "timeout-minutes: 10" in stale_text
    assert "cancel-in-progress: true" in stale_text
    assert "issues: write" in stale_text
    assert "pull-requests: write" in stale_text

    # welcome.yml
    welcome_file = workflows_dir / "welcome.yml"
    assert welcome_file.is_file(), "welcome.yml must exist"
    welcome_text = welcome_file.read_text(encoding="utf-8")
    assert "actions/first-interaction@v3" in welcome_text
    assert "timeout-minutes: 5" in welcome_text
    assert "cancel-in-progress: true" in welcome_text

    # tests.yml
    tests_file = workflows_dir / "tests.yml"
    assert tests_file.is_file(), "tests.yml must exist"
    tests_text = tests_file.read_text(encoding="utf-8")
    assert "cancel-in-progress: true" in tests_text
    assert "timeout-minutes: 15" in tests_text
    assert "contents: read" in tests_text

    # source-platform-smoke.yml
    smoke_file = workflows_dir / "source-platform-smoke.yml"
    assert smoke_file.is_file(), "source-platform-smoke.yml must exist"
    smoke_text = smoke_file.read_text(encoding="utf-8")
    assert "cancel-in-progress: true" in smoke_text
    assert "timeout-minutes: 15" in smoke_text


def test_keywords_saturated_and_project_urls():
    """Verify that pyproject.toml has 20 saturated keywords matching GitHub topics and full project URLs."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml must exist"
    content = pyproject_path.read_text(encoding="utf-8")

    expected_topics = [
        "accounting", "datev", "document-archive", "email", "email-attachments",
        "gmail", "gmail-api", "imap", "invoice", "invoice-automation",
        "json-export", "local-first", "ocr", "offline-first", "pdf",
        "privacy-first", "pyside6", "python", "receipt", "windows"
    ]
    for topic in expected_topics:
        assert f'"{topic}"' in content, f"Topic '{topic}' missing from pyproject.toml keywords"

    # Verify project.urls
    for url_key in [
        "Homepage", "Repository", "Issues", "Bug Tracker", "Marketing Log",
        "LLM Ready", "Notice", "Third-Party Licenses", "Parent Organization", "Umbrella Ecosystem"
    ]:
        assert f'"{url_key}"' in content or f'{url_key} =' in content, f"URL '{url_key}' missing from project.urls"


def test_dual_reciprocal_anchors_sec_01_to_sec_18():
    """Verify both README.md and README-DE.md implement 18-point bilateral navigation with dual anchors."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README-DE.md").read_text(encoding="utf-8")

    for i in range(1, 19):
        anchor = f'<a id="sec-{i:02d}"></a>'
        assert anchor in readme_en, f"Anchor {anchor} missing from README.md"
        assert anchor in readme_de, f"Anchor {anchor} missing from README-DE.md"


def test_level_1_sbom_cross_reference_matrix():
    """Verify THIRD_PARTY_LICENSES.md contains the Invariant Cross-Reference Matrix."""
    sbom_path = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
    assert sbom_path.exists(), "THIRD_PARTY_LICENSES.md must exist"
    sbom_text = sbom_path.read_text(encoding="utf-8")

    assert "Level 1 SBOM Invarianten-Kreuzreferenzmatrix" in sbom_text
    assert "2026-09-24" in sbom_text
    for i in range(1, 11):
        # Check codes INV-LOCAL-01 through INV-SLA-10
        pattern = re.compile(rf"INV-[A-Z]+-{i:02d}")
        assert pattern.search(sbom_text), f"Invariant index {i:02d} missing from matrix in THIRD_PARTY_LICENSES.md"


def test_statutory_disclaimer_and_sla_in_readmes():
    """Verify German statutory notice (§ 521 BGB Gefälligkeitsrecht) and 48h SLA in both READMEs."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README-DE.md").read_text(encoding="utf-8")

    for doc, name in [(readme_en, "README.md"), (readme_de, "README-DE.md")]:
        assert "521 BGB" in doc, f"§ 521 BGB disclaimer missing from {name}"
        assert "48h" in doc or "48-Stunden" in doc or "48-hour" in doc, f"48h SLA missing from {name}"
        assert "Gefälligkeitsrecht" in doc, f"Gefälligkeitsrecht missing from {name}"


def test_marketing_log_pfad_b_audit_20260924():
    """Verify MARKETING-LOG.txt documents the Pfad B milestone from 2026-09-24."""
    log_path = REPO_ROOT / "MARKETING-LOG.txt"
    assert log_path.exists(), "MARKETING-LOG.txt must exist"
    log_text = log_path.read_text(encoding="utf-8")

    assert "PFAD_B_MARKETING_DISCOVERABILITY_AND_VISUAL_ARCHITECTURE" in log_text
    assert "2026-09-24" in log_text
    assert "20-TOPIC & KEYWORD SATURATION" in log_text
    assert "18-POINT BILATERAL QUICK NAVIGATION" in log_text


def test_changelog_unreleased_pfad_b_entry():
    """Verify CHANGELOG.md contains Pfad B notes under [Unreleased]."""
    changelog_path = REPO_ROOT / "CHANGELOG.md"
    assert changelog_path.exists(), "CHANGELOG.md must exist"
    changelog_text = changelog_path.read_text(encoding="utf-8")

    assert "### Pfad B Marketing, Discoverability, Visual Architecture & Bilateral Navigation Parity (2026-09-24)" in changelog_text
    assert "T-20260920-167562623" in changelog_text

