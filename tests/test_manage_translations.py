# -*- coding: utf-8 -*-
"""Contract tests for manage_translations.py CLI utility."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_manage_translations_check_gate():
    """Verify that python manage_translations.py --check exits 0 with complete parity."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "manage_translations.py"), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Check gate failed:\nStdout: {result.stdout}\nStderr: {result.stderr}"
    assert "Translation check gate PASSED" in result.stdout
    assert "100% key parity across all 6 languages" in result.stdout


def test_manage_translations_stats_output():
    """Verify that python manage_translations.py --stats outputs all 6 supported languages."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "manage_translations.py"), "--stats"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "de" in result.stdout
    assert "en" in result.stdout
    assert "es" in result.stdout
    assert "zh" in result.stdout
    assert "ja" in result.stdout
    assert "ru" in result.stdout
    assert "100.0%" in result.stdout


def test_manage_translations_scan():
    """Verify that python manage_translations.py --scan executes without crashing."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "manage_translations.py"), "--scan"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Keys used in codebase" in result.stdout
