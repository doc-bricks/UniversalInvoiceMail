"""Automated security, dependency floor, and third-party license contract tests for UniversalInvoiceMail."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dependency_vulnerability_floors() -> None:
    """Verify requirements.txt and pyproject.toml enforce patched dependency floors against CVEs."""
    req_file = ROOT / "requirements.txt"
    assert req_file.is_file(), "requirements.txt must exist"
    req_text = req_file.read_text(encoding="utf-8")

    # Pillow >= 12.3.0 floor resolves 26+ CVEs/GHSAs (GHSA-4x4j-2g7c-83w6, GHSA-45hq-cxwh-f6vc)
    assert re.search(r"^Pillow\s*>=\s*12\.3\.0", req_text, re.MULTILINE), (
        "requirements.txt must enforce Pillow>=12.3.0 floor"
    )
    assert re.search(r"^keyring\s*>=\s*25\.0\.0", req_text, re.MULTILINE), (
        "requirements.txt must enforce keyring>=25.0.0 floor"
    )
    assert re.search(r"^pytest\s*>=\s*9\.1\.1", req_text, re.MULTILINE), (
        "requirements.txt must enforce pytest>=9.1.1 floor against CVE-2025-7117"
    )

    pyproject_file = ROOT / "pyproject.toml"
    assert pyproject_file.is_file(), "pyproject.toml must exist"
    pyproject_text = pyproject_file.read_text(encoding="utf-8")

    # PEP 621 dependencies section
    assert "dependencies = [" in pyproject_text, "pyproject.toml must define project.dependencies"
    assert "Pillow>=12.3.0" in pyproject_text, "pyproject.toml must specify Pillow>=12.3.0"
    assert "keyring>=25.0.0" in pyproject_text, "pyproject.toml must specify keyring>=25.0.0"

    # Dev optional dependencies floor (pytest >= 9.1.1 protects against CVE-2025-7117 / GHSA-6w46-j5rx-g56g)
    assert "[project.optional-dependencies]" in pyproject_text, "pyproject.toml must define optional-dependencies"
    assert "pytest>=9.1.1" in pyproject_text, "pyproject.toml dev dependencies must require pytest>=9.1.1"
    assert "ruff>=0.9.0" in pyproject_text, "pyproject.toml dev dependencies must require ruff>=0.9.0"


def test_third_party_licenses_complete_and_accurate() -> None:
    """Verify THIRD_PARTY_LICENSES.txt comprehensively covers runtime, transitive, and test packages."""
    license_file = ROOT / "THIRD_PARTY_LICENSES.txt"
    assert license_file.is_file(), "THIRD_PARTY_LICENSES.txt must exist"
    content = license_file.read_text(encoding="utf-8")

    required_packages = [
        ("PySide6", "LGPL-3.0-only"),
        ("shiboken6", "LGPL-3.0-only"),
        ("keyring", "MIT"),
        ("jaraco.classes", "MIT"),
        ("jaraco.context", "MIT"),
        ("jaraco.functools", "MIT"),
        ("pywin32-ctypes", "BSD-3-Clause"),
        ("Pillow", "HPND-sell-variant"),
        ("openpyxl", "MIT"),
        ("python-docx", "MIT"),
        ("xhtml2pdf", "Apache-2.0"),
        ("reportlab", "BSD-3-Clause"),
        ("pypdfium2", "Apache-2.0 AND BSD-3-Clause"),
        ("pypdf", "BSD-3-Clause"),
        ("docx2pdf", "MIT"),
        ("pytesseract", "Apache-2.0"),
        ("pytest", "MIT"),
        ("pluggy", "MIT"),
        ("iniconfig", "MIT"),
        ("ruff", "MIT OR Apache-2.0"),
        ("packaging", "Apache-2.0 OR BSD-2-Clause"),
    ]

    for pkg, spdx in required_packages:
        assert pkg in content, f"Package {pkg} missing from THIRD_PARTY_LICENSES.txt"
        assert spdx in content, f"SPDX identifier {spdx} for {pkg} missing from THIRD_PARTY_LICENSES.txt"

    # Ensure structured schema fields exist
    assert "License:" in content, "License: field missing in THIRD_PARTY_LICENSES.txt"
    assert "URL:" in content, "URL: field missing in THIRD_PARTY_LICENSES.txt"
    assert "SPDX:" in content, "SPDX: field missing in THIRD_PARTY_LICENSES.txt"


def test_gitignore_security_and_multi_host_hardening() -> None:
    """Verify .gitignore blocks private secrets, certificates, and multi-host conflict files."""
    gitignore_file = ROOT / ".gitignore"
    assert gitignore_file.is_file(), ".gitignore must exist"
    content = gitignore_file.read_text(encoding="utf-8")

    # Secrets and certificate protection
    for pat in ["credentials.json", "*.pfx", "*.pem", "*.key", "keyring/", "secrets.*"]:
        assert pat in content, f"Secret pattern {pat} missing in .gitignore"

    # Multi-host sync hardening
    for host_pat in ["*-WORKSTATION-LG*", "*-ASUS-GEI*", "*-WORKSTATION*", "*-ASUS*", "*-LAPTOP*", "*conflicted copy*", "*.sync-conflict-*", "*.conflict"]:
        assert host_pat in content, f"Sync conflict pattern {host_pat} missing in .gitignore"

    # Multi-agent lock system fail-closed patterns
    for lock_pat in ["LOCK.*", "*.lock", "LOCK*.txt", "LOCK", "LOCK.user.*", "LOCK.until.*", "LOCK.condition.*", "LOCK.permissions.json", "uv.lock", ".automation-lock"]:
        assert lock_pat in content, f"Lock pattern {lock_pat} missing in .gitignore"


def test_level1_sbom_and_governance_invariants() -> None:
    """Verify THIRD_PARTY_LICENSES.md contains complete Level 1 SBOM and all 10 invariants."""
    sbom_file = ROOT / "THIRD_PARTY_LICENSES.md"
    assert sbom_file.is_file(), "THIRD_PARTY_LICENSES.md must exist"
    sbom_text = sbom_file.read_text(encoding="utf-8")

    # 10 System Invariants
    for code in [
        "INV-LOCAL-01", "INV-CRED-02", "INV-PRIVACY-03", "INV-DATEV-04", "INV-FLOOR-05",
        "INV-TLS-06", "INV-LEASTPRIV-07", "INV-LAZYLOAD-08", "INV-OFFLINE-09", "INV-SLA-10",
    ]:
        assert code in sbom_text, f"Invariant code {code} missing from THIRD_PARTY_LICENSES.md"

    # Core package coverage in SBOM
    for pkg in ["PySide6", "keyring", "Pillow", "openpyxl", "python-docx", "xhtml2pdf", "reportlab", "pypdfium2", "pypdf", "docx2pdf", "pytesseract"]:
        assert pkg in sbom_text, f"Package {pkg} missing from Level 1 SBOM"

    assert "Weak Copyleft / Permissive" in sbom_text
    assert "asInvoker" in sbom_text



def test_no_hardcoded_user_paths_in_python_code() -> None:
    """Verify no hardcoded personal user profile paths exist in active Python source."""
    disallowed_regex = re.compile(r"""(?i)C:[/\\]Users[/\\](?:lukas|admin|administrator)[/\\]""", re.VERBOSE)

    python_files = list(ROOT.glob("*.py")) + list((ROOT / "tests").glob("*.py"))
    assert len(python_files) > 5, "Expected at least 5 Python files to scan"

    violating_lines = []
    for py_file in python_files:
        if not py_file.is_file():
            continue
        try:
            text = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        for idx, line in enumerate(text.splitlines(), 1):
            if disallowed_regex.search(line):
                violating_lines.append(f"{py_file.name}:{idx}: {line.strip()}")

    assert not violating_lines, "Found hardcoded user paths in Python code:\n" + "\n".join(violating_lines)


def test_security_policy_bilingual_and_sla() -> None:
    """Verify SECURITY.md provides bilingual policy, security contact addresses, and 48h SLA."""
    sec_file = ROOT / "SECURITY.md"
    assert sec_file.is_file(), "SECURITY.md must exist"
    sec_text = sec_file.read_text(encoding="utf-8")

    assert "## Deutsch" in sec_text, "SECURITY.md must contain German section"
    assert "## English" in sec_text, "SECURITY.md must contain English section"

    # Contact addresses
    assert "security@doc-bricks.org" in sec_text, "SECURITY.md must list security@doc-bricks.org"
    assert "support@lukasgeiger.com" in sec_text, "SECURITY.md must list support@lukasgeiger.com"

    # SLA commitment
    assert "48" in sec_text, "SECURITY.md must define 48-hour response SLA"
    assert "Local-First" in sec_text, "SECURITY.md must document Local-First commitment"


def test_local_first_and_offline_invariants() -> None:
    """Verify absence of unapproved telemetry, analytics, and remote trackers."""
    disallowed_patterns = [
        re.compile(r"google-analytics\.com", re.IGNORECASE),
        re.compile(r"mixpanel\.com", re.IGNORECASE),
        re.compile(r"segment\.io", re.IGNORECASE),
        re.compile(r"sentry\.io", re.IGNORECASE),
    ]

    core_files = [
        ROOT / "UniversalInvoiceMail.py",
        ROOT / "datev_exporter.py",
        ROOT / "invoice_bundle.py",
    ]

    for py_file in core_files:
        if not py_file.is_file():
            continue
        text = py_file.read_text(encoding="utf-8")
        for pat in disallowed_patterns:
            assert not pat.search(text), f"Found disallowed telemetry/analytics pattern {pat.pattern} in {py_file.name}"
