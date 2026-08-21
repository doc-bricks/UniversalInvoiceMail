# -*- coding: utf-8 -*-
"""
TranslationSystem - Multi-Language Support für UniversalInvoiceMail
===================================================================
Version: 2.0.0 (6-Sprachen-Ausbau)
Referenz: Policy P-006 / Sprachstufen (de, en, es, zh, ja, ru)

Verwendung:
-----------
from translator import TranslationSystem, get_translator, t

translator = get_translator()
label = t('btn_save')
translator.set_language('en')
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

SUPPORTED_LANGUAGES: List[str] = ['de', 'en', 'es', 'zh', 'ja', 'ru']
DEFAULT_LANGUAGE: str = 'de'
FALLBACK_CHAIN: List[str] = ['en', 'de']

_GLOBAL_TRANSLATOR: Optional['TranslationSystem'] = None


class TranslationSystem:
    """Multi-Language Support System mit 6-Sprachen-Unterstützung und Fallback-Kette."""

    def __init__(self, default_lang: str = 'de', app_dir: Optional[Path] = None):
        self.current_lang = default_lang if default_lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

        if app_dir is None:
            app_dir = Path(__file__).resolve().parent
        self.app_dir = Path(app_dir)
        self.translations_file = self.app_dir / "locales" / "translations.json"

        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        if self.translations_file.exists():
            try:
                with open(self.translations_file, encoding='utf-8') as f:
                    data = json.load(f)
                    self.translations = {k: v for k, v in data.items() if not k.startswith("_")}
            except Exception:
                self.translations = {}
        else:
            self.translations = {}

    def _save_translations(self) -> None:
        self.translations_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.translations_file, 'w', encoding='utf-8') as f:
            json.dump(self.translations, f, indent=2, ensure_ascii=False)

    def t(self, key: str, **kwargs: Any) -> str:
        """
        Übersetzt einen Key in die aktuelle Sprache mit optionaler Parameter-Ersetzung.
        Fallback-Kette: aktuelle Sprache -> en -> de -> Key selbst.
        """
        template = key
        if key in self.translations:
            entry = self.translations[key]
            val = entry.get(self.current_lang)
            if val:
                template = val
            else:
                for fb in FALLBACK_CHAIN:
                    val = entry.get(fb)
                    if val:
                        template = val
                        break

        if kwargs:
            try:
                return template.format(**kwargs)
            except Exception:
                return template
        return template

    def set_language(self, lang: str) -> bool:
        """Setzt die aktive Sprache."""
        if lang in SUPPORTED_LANGUAGES:
            self.current_lang = lang
            return True
        return False

    def get_language(self) -> str:
        """Gibt die aktuell aktive Sprache zurück."""
        return self.current_lang

    def get_supported_languages(self) -> List[str]:
        """Gibt die Liste der unterstützten Sprachcodes zurück."""
        return list(SUPPORTED_LANGUAGES)

    def add_translation(self, key: str, **translations: str) -> None:
        """Fügt einen neuen Übersetzungsschlüssel hinzu."""
        if key not in self.translations:
            self.translations[key] = {lang: "" for lang in SUPPORTED_LANGUAGES}
        for lang, value in translations.items():
            if lang in SUPPORTED_LANGUAGES:
                self.translations[key][lang] = value
        self._save_translations()

    def get_missing_translations(self, lang: Optional[str] = None) -> Dict[str, List[str]]:
        """Gibt fehlende Übersetzungen zurück."""
        if lang and lang in SUPPORTED_LANGUAGES:
            return {lang: [k for k, v in self.translations.items() if not v.get(lang)]}
        missing: Dict[str, List[str]] = {}
        for lng in SUPPORTED_LANGUAGES:
            if lng == 'de':
                continue
            m = [k for k, v in self.translations.items() if not v.get(lng)]
            if m:
                missing[lng] = m
        return missing


def get_translator(default_lang: str = 'de') -> TranslationSystem:
    """Gibt die Singleton-Instanz des TranslationSystems zurück."""
    global _GLOBAL_TRANSLATOR
    if _GLOBAL_TRANSLATOR is None:
        _GLOBAL_TRANSLATOR = TranslationSystem(default_lang=default_lang)
    return _GLOBAL_TRANSLATOR


def t(key: str, **kwargs: Any) -> str:
    """Bequemlichkeitsfunktion zur Übersetzung über den globalen Translator."""
    return get_translator().t(key, **kwargs)
