#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
manage_translations.py — Translation Management & CI Check Gate
==============================================================
Validates, checks, and manages translation catalogs for UniversalInvoiceMail
according to Policy P-006 (Tier-2 Multi-Language Standard: de, en, es, zh, ja, ru).

Usage:
------
    python manage_translations.py --check
    python manage_translations.py --stats
    python manage_translations.py --scan
    python manage_translations.py --export
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Reconfigure stdout/stderr to UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent
TRANSLATIONS_FILE = REPO_ROOT / "locales" / "translations.json"
SUPPORTED_LANGUAGES: List[str] = ["de", "en", "es", "zh", "ja", "ru"]
PLACEHOLDER_REGEX = re.compile(r"\{(\w+)\}")
T_CALL_REGEX = re.compile(r"""\bt\(\s*['"]([a-zA-Z0-9_\-\.]+)['"]""")


def load_translations() -> Tuple[Dict[str, Dict[str, str]], Dict[str, any]]:
    """Load translations and metadata from locales/translations.json."""
    if not TRANSLATIONS_FILE.exists():
        raise FileNotFoundError(f"Translations file missing: {TRANSLATIONS_FILE}")
    with open(TRANSLATIONS_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    meta = raw.get("_meta", {})
    translations = {k: v for k, v in raw.items() if not k.startswith("_")}
    return translations, meta


def check_translations() -> int:
    """Run strict verification gate for all translations.

    Returns:
        0 on success, 1 on any violation.
    """
    print("=" * 60)
    print("UniversalInvoiceMail — Translation Parity Check Gate")
    print("=" * 60)

    try:
        translations, meta = load_translations()
    except Exception as e:
        print(f"[FAIL] Error loading translations: {e}")
        return 1

    errors = 0
    warnings = 0

    # 1. Check meta header
    meta_langs = meta.get("languages", [])
    if set(meta_langs) != set(SUPPORTED_LANGUAGES):
        print(f"[FAIL] Meta languages mismatch: expected {SUPPORTED_LANGUAGES}, got {meta_langs}")
        errors += 1
    else:
        print(f"[OK] Meta languages match Tier-2 standard ({len(meta_langs)} languages)")

    # 2. Check key completeness across all languages
    missing_keys = []
    empty_translations = []
    placeholder_mismatches = []

    for key, lang_map in sorted(translations.items()):
        if not isinstance(lang_map, dict):
            print(f"[FAIL] Key '{key}' does not map to a dictionary")
            errors += 1
            continue

        for lang in SUPPORTED_LANGUAGES:
            if lang not in lang_map:
                missing_keys.append((key, lang))
            else:
                val = lang_map[lang]
                if val is None or not str(val).strip():
                    empty_translations.append((key, lang))

        # Check placeholder tokens
        ref_tokens: Set[str] = set()
        for lang in ("de", "en"):
            if lang in lang_map and lang_map[lang]:
                ref_tokens = set(PLACEHOLDER_REGEX.findall(str(lang_map[lang])))
                break

        if ref_tokens:
            for lang in SUPPORTED_LANGUAGES:
                if lang in lang_map and lang_map[lang]:
                    target_tokens = set(PLACEHOLDER_REGEX.findall(str(lang_map[lang])))
                    if target_tokens != ref_tokens:
                        placeholder_mismatches.append(
                            f"Key '{key}' [{lang}]: {target_tokens} != ref {ref_tokens}"
                        )

    total_keys = len(translations)
    print(f"Total keys audited: {total_keys}")

    if missing_keys:
        print(f"\n[FAIL] {len(missing_keys)} missing translation entries found:")
        for key, lang in missing_keys[:20]:
            print(f"  - Key: '{key}' missing language: '{lang}'")
        if len(missing_keys) > 20:
            print(f"  ... and {len(missing_keys) - 20} more.")
        errors += len(missing_keys)
    else:
        print(f"[OK] 100% key parity across all {len(SUPPORTED_LANGUAGES)} languages")

    if empty_translations:
        print(f"\n[FAIL] {len(empty_translations)} empty translation entries found:")
        for key, lang in empty_translations[:20]:
            print(f"  - Key: '{key}' empty for: '{lang}'")
        if len(empty_translations) > 20:
            print(f"  ... and {len(empty_translations) - 20} more.")
        errors += len(empty_translations)
    else:
        print("[OK] No empty translation values found")

    if placeholder_mismatches:
        print(f"\n[FAIL] {len(placeholder_mismatches)} placeholder token inconsistencies found:")
        for mismatch in placeholder_mismatches:
            print(f"  - {mismatch}")
        errors += len(placeholder_mismatches)
    else:
        print("[OK] All format placeholder tokens are consistent")

    print("=" * 60)
    if errors == 0:
        print(f"[SUCCESS] Translation check gate PASSED (0 errors, {warnings} warnings).")
        return 0
    else:
        print(f"[FAILURE] Translation check gate FAILED with {errors} error(s).")
        return 1


def scan_source_code() -> int:
    """Scan Python files for t(...) calls and compare against catalog."""
    print("=" * 60)
    print("Scanning codebase for t('...') calls...")
    print("=" * 60)

    try:
        translations, _ = load_translations()
    except Exception as e:
        print(f"Error loading translations: {e}")
        return 1

    catalog_keys = set(translations.keys())
    used_keys: Set[str] = set()

    for py_file in REPO_ROOT.glob("**/*.py"):
        if ".pytest_cache" in py_file.parts or ".pytest_temp" in py_file.parts or "venv" in py_file.parts:
            continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            for match in T_CALL_REGEX.finditer(content):
                used_keys.add(match.group(1))
        except Exception:
            pass

    print(f"Keys used in codebase: {len(used_keys)}")
    print(f"Keys in catalog:       {len(catalog_keys)}")

    missing_in_catalog = used_keys - catalog_keys
    if missing_in_catalog:
        print(f"\n[WARN] {len(missing_in_catalog)} keys referenced in code but missing from catalog:")
        for k in sorted(missing_in_catalog):
            print(f"  - {k}")
    else:
        print("[OK] All keys referenced in code exist in translations catalog.")

    return 0


def print_stats() -> int:
    """Print translation catalog statistics."""
    try:
        translations, meta = load_translations()
    except Exception as e:
        print(f"Error: {e}")
        return 1

    total_keys = len(translations)
    print(f"\nTranslation Catalog Statistics ({TRANSLATIONS_FILE.name}):")
    print(f"Total Translation Keys: {total_keys}")
    print(f"Supported Languages:    {', '.join(SUPPORTED_LANGUAGES)}")
    print("-" * 50)
    print(f"{'Language':<12} | {'Filled Keys':<12} | {'Coverage':<10}")
    print("-" * 50)

    for lang in SUPPORTED_LANGUAGES:
        filled = sum(1 for m in translations.values() if m.get(lang) and str(m.get(lang)).strip())
        pct = (filled / total_keys * 100.0) if total_keys > 0 else 0.0
        print(f"{lang:<12} | {filled:<12} | {pct:6.1f}%")
    print("-" * 50)
    return 0


def export_translations() -> int:
    """Sort and format translations file atomically."""
    from atomic_io import atomic_write_json
    try:
        translations, meta = load_translations()
        data = {"_meta": meta}
        for k in sorted(translations.keys()):
            data[k] = translations[k]
        atomic_write_json(TRANSLATIONS_FILE, data, indent=2, ensure_ascii=False)
        print(f"[OK] Successfully formatted and atomically saved {TRANSLATIONS_FILE}")
        return 0
    except Exception as e:
        print(f"[FAIL] Error exporting translations: {e}")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="UniversalInvoiceMail Translation Manager")
    parser.add_argument("--check", action="store_true", help="Run CI verification gate")
    parser.add_argument("--scan", action="store_true", help="Scan codebase for t(...) calls")
    parser.add_argument("--stats", action="store_true", help="Display translation coverage stats")
    parser.add_argument("--export", action="store_true", help="Sort and atomically format catalog")

    args = parser.parse_args()

    if args.check:
        return check_translations()
    elif args.scan:
        return scan_source_code()
    elif args.stats:
        return print_stats()
    elif args.export:
        return export_translations()
    else:
        # Default behavior: run check
        return check_translations()


if __name__ == "__main__":
    sys.exit(main())
