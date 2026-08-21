# -*- coding: utf-8 -*-
"""Tests für das Multi-Language- und i18n-System von UniversalInvoiceMail."""

import json
import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_PATH = REPO_ROOT / "locales" / "translations.json"
REQUIRED_LANGUAGES = ["de", "en", "es", "zh", "ja", "ru"]
PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")


@pytest.fixture(scope="module")
def raw_translations_data():
    assert TRANSLATIONS_PATH.exists(), "locales/translations.json existiert nicht"
    with open(TRANSLATIONS_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def translations(raw_translations_data):
    return {k: v for k, v in raw_translations_data.items() if not k.startswith("_")}


def test_translations_file_exists():
    assert TRANSLATIONS_PATH.exists(), "locales/translations.json existiert nicht"


def test_translations_meta_header(raw_translations_data):
    assert "_meta" in raw_translations_data
    meta = raw_translations_data["_meta"]
    assert "languages" in meta
    assert set(meta["languages"]) == set(REQUIRED_LANGUAGES)


def test_all_keys_have_all_languages(translations):
    missing = []
    for key, entry in translations.items():
        for lang in REQUIRED_LANGUAGES:
            if lang not in entry:
                missing.append(f"{key}.{lang}")
    assert not missing, f"Fehlende Sprachschlüssel: {missing}"


def test_all_languages_translations_not_empty(translations):
    empty = []
    for key, entry in translations.items():
        for lang in REQUIRED_LANGUAGES:
            val = entry.get(lang)
            if val is None or val == "":
                empty.append(f"{key}.{lang}")
    assert not empty, f"Leere Übersetzungen gefunden: {empty}"


def test_placeholder_tokens_consistent_all_languages(translations):
    inconsistent = []
    for key, entry in translations.items():
        de_tokens = set(PLACEHOLDER_RE.findall(entry.get("de", "")))
        for lang in REQUIRED_LANGUAGES:
            if lang == "de":
                continue
            lang_tokens = set(PLACEHOLDER_RE.findall(entry.get(lang, "")))
            if de_tokens != lang_tokens:
                inconsistent.append(
                    f"{key}: DE={de_tokens} {lang.upper()}={lang_tokens}"
                )
    assert not inconsistent, f"Inkonsistente Platzhalter across languages: {inconsistent}"


def test_translation_system_basic():
    from translator import TranslationSystem
    ts = TranslationSystem(default_lang="de", app_dir=REPO_ROOT)
    assert ts.get_language() == "de"
    assert ts.t("app_title") == "UniversalInvoiceMail"
    assert ts.t("btn_datev_export") == "DATEV-Export"


@pytest.mark.parametrize("lang", REQUIRED_LANGUAGES)
def test_translation_system_all_languages_return_string(lang):
    from translator import TranslationSystem
    ts = TranslationSystem(default_lang=lang, app_dir=REPO_ROOT)
    result = ts.t("btn_fetch_invoices")
    assert isinstance(result, str) and len(result) > 0, f"Translation for {lang} empty"


def test_translation_system_formatting_and_placeholders():
    from translator import TranslationSystem
    ts = TranslationSystem(default_lang="en", app_dir=REPO_ROOT)
    formatted = ts.t("datev_warn_zero_amount", count=3)
    assert "3 invoices skipped" in formatted
    assert "{count}" not in formatted


def test_translation_system_fallback_chain():
    from translator import TranslationSystem
    ts = TranslationSystem(default_lang="invalid_code", app_dir=REPO_ROOT)
    # Default fallback to 'de'
    assert ts.get_language() == "de"
    # Fallback to key itself for nonexistent keys
    assert ts.t("non_existent_key_xyz_123") == "non_existent_key_xyz_123"


def test_translation_system_set_language():
    from translator import TranslationSystem
    ts = TranslationSystem(default_lang="de", app_dir=REPO_ROOT)
    assert ts.set_language("es") is True
    assert ts.get_language() == "es"
    assert ts.t("btn_save") == "Guardar"

    assert ts.set_language("zh") is True
    assert ts.get_language() == "zh"
    assert ts.t("btn_save") == "保存"

    assert ts.set_language("invalid") is False
    assert ts.get_language() == "zh"


def test_utf8_multi_language_smoke():
    from translator import TranslationSystem
    expected_samples = {
        "de": "Rechnungen abrufen",
        "en": "Fetch Invoices",
        "es": "Obtener facturas",
        "zh": "获取发票",
        "ja": "請求書を取得",
        "ru": "Получить счета",
    }
    for lang, sample in expected_samples.items():
        ts = TranslationSystem(default_lang=lang, app_dir=REPO_ROOT)
        text = ts.t("btn_fetch_invoices")
        assert text == sample, f"Mismatch for language {lang}: got '{text}', expected '{sample}'"
