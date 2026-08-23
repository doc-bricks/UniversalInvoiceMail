"""Helpers for the redacted UniversalInvoiceMail exchange bundle."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Optional

BUNDLE_SCHEMA = "universalinvoicemail-invoicebundle-v1"
ALLOWED_COMPANION_FIELDS = ("amount", "review_status", "notes")
KNOWN_REVIEW_STATUSES = {"unchecked", "checked", "needs_question", "ready"}


def _get_value(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _normalize_text(value: Any, *, limit: int = 1000) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return text[:limit]


def _normalize_amount(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    if not isinstance(value, str):
        value = str(value)

    text = value.strip()
    if not text:
        return None

    # Remove currency symbols and common currency codes (€, $, £, ¥, ₹, EUR, USD, CHF, GBP)
    text = re.sub(r"[€$£¥₹\s]|(?i:\b(eur|usd|chf|gbp)\b)", "", text).strip()
    if not text:
        return None

    # Handle European vs US number formats:
    # "1.234,56" -> "1234.56"
    # "1,234.56" -> "1234.56"
    # "12,50" -> "12.50"
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")

    try:
        return round(float(text), 2)
    except ValueError:
        raise ValueError(f"could not convert string to float: {value!r}")


def _normalize_review_status(value: Any) -> str:
    normalized = _normalize_text(value, limit=40).lower() or "unchecked"
    if normalized not in KNOWN_REVIEW_STATUSES:
        raise ValueError(f"unknown review_status: {normalized}")
    return normalized


def _bundle_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _safe_relative_path(path: Path, base_dir: Path) -> Optional[str]:
    try:
        return str(path.resolve().relative_to(base_dir.resolve()))
    except ValueError:
        return None


def _safe_int(value: Any, default: int = 4) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def _build_file_reference(invoice: Any, download_root: Path) -> list[dict[str, Any]]:
    invoice_path_raw = _get_value(invoice, "path", "")
    if not invoice_path_raw:
        return []

    invoice_path = Path(invoice_path_raw)
    if not invoice_path.exists() or not invoice_path.is_file():
        return []

    try:
        sha256 = invoice_path.read_bytes()
    except OSError:
        return []

    import hashlib

    file_hash = hashlib.sha256(sha256).hexdigest()
    relative_path = _safe_relative_path(invoice_path, download_root)
    return [{
        "relative_path": relative_path,
        "filename": invoice_path.name,
        "mime_type": "application/pdf",
        "sha256": file_hash,
        "size_bytes": invoice_path.stat().st_size,
    }]


def _resolve_profile_id(invoice: Any, profiles_by_id: dict[str, Any], profiles_by_name: dict[str, Any]) -> str:
    profile_id = _normalize_text(_get_value(invoice, "profile_id", ""), limit=120)
    if profile_id and profile_id in profiles_by_id:
        return profile_id

    profile_name = _normalize_text(_get_value(invoice, "profile_name", ""), limit=120)
    profile = profiles_by_name.get(profile_name)
    if profile is not None:
        return _normalize_text(_get_value(profile, "id", ""), limit=120)
    return profile_id


def build_invoice_bundle(
    *,
    app_name: str,
    app_version: str,
    accounts: Iterable[Any],
    profiles: Iterable[Any],
    invoices: Iterable[Any],
    download_path: str,
    datev_config: Any = None,
    selected_paths: Optional[set[str]] = None,
) -> dict[str, Any]:
    """Create a redacted bundle for a selected or full invoice set."""
    selected_paths = selected_paths or set()
    accounts_by_id = {
        _normalize_text(_get_value(account, "id", ""), limit=120): account
        for account in accounts
    }
    profiles_list = list(profiles)
    profiles_by_id = {
        _normalize_text(_get_value(profile, "id", ""), limit=120): profile
        for profile in profiles_list
    }
    profiles_by_name = {
        _normalize_text(_get_value(profile, "name", ""), limit=120): profile
        for profile in profiles_list
    }
    download_root = Path(download_path)

    invoice_rows = []
    for invoice in invoices:
        invoice_path = _normalize_text(_get_value(invoice, "path", ""), limit=1000)
        if selected_paths and invoice_path not in selected_paths:
            continue

        file_refs = _build_file_reference(invoice, download_root)
        file_hash = ""
        if file_refs:
            file_hash = file_refs[0]["sha256"]
        else:
            file_hash = _normalize_text(_get_value(invoice, "hash", ""), limit=128)

        amount = _normalize_amount(_get_value(invoice, "amount", None))

        invoice_rows.append({
            "id": _normalize_text(_get_value(invoice, "id", ""), limit=120),
            "profile_id": _resolve_profile_id(invoice, profiles_by_id, profiles_by_name),
            "profile_name": _normalize_text(_get_value(invoice, "profile_name", ""), limit=120),
            "date": _normalize_text(_get_value(invoice, "date", ""), limit=40),
            "sender": _normalize_text(_get_value(invoice, "sender", ""), limit=200),
            "subject": _normalize_text(_get_value(invoice, "subject", ""), limit=300),
            "filename": _normalize_text(_get_value(invoice, "filename", ""), limit=260),
            "amount": amount,
            "currency": _normalize_text(_get_value(invoice, "currency", "EUR"), limit=16) or "EUR",
            "review_status": _normalize_review_status(_get_value(invoice, "review_status", "unchecked")),
            "notes": _normalize_text(_get_value(invoice, "notes", ""), limit=4000),
            "datev_status": "ready" if amount is not None and amount > 0 else "missing_amount",
            "files": file_refs,
            "mail_reference": {
                "account_label": _normalize_text(_get_value(invoice, "account_name", ""), limit=200),
                "message_id_hash": _normalize_text(_get_value(invoice, "message_id_hash", ""), limit=128),
                "folder": _normalize_text(_get_value(invoice, "mail_folder", ""), limit=200),
            },
            "local_hash": file_hash,
        })

    profile_rows = []
    for profile in profiles_list:
        account = accounts_by_id.get(_normalize_text(_get_value(profile, "account_id", ""), limit=120))
        profile_rows.append({
            "id": _normalize_text(_get_value(profile, "id", ""), limit=120),
            "name": _normalize_text(_get_value(profile, "name", ""), limit=120),
            "account_id": _normalize_text(_get_value(profile, "account_id", ""), limit=120),
            "account_label": _normalize_text(_get_value(account, "name", ""), limit=200),
            "sender_filter": _normalize_text(_get_value(profile, "sender_filter", ""), limit=500),
            "subject_filter": _normalize_text(_get_value(profile, "subject_filter", ""), limit=500),
            "gmail_query": _normalize_text(_get_value(profile, "gmail_query", ""), limit=500),
            "target_folder_label": _normalize_text(
                _get_value(profile, "target_subfolder", "") or _get_value(profile, "name", ""),
                limit=240,
            ),
        })

    datev_payload = None
    if datev_config is not None:
        konten_mapping = _get_value(datev_config, "konten_mapping", {}) or {}
        datev_payload = {
            "berater_nr": _normalize_text(_get_value(datev_config, "berater_nr", ""), limit=50),
            "mandant_nr": _normalize_text(_get_value(datev_config, "mandant_nr", ""), limit=50),
            "wj_beginn": _normalize_text(_get_value(datev_config, "wj_beginn", ""), limit=20),
            "waehrung": _normalize_text(_get_value(datev_config, "währung", "EUR"), limit=16)
            or _normalize_text(_get_value(datev_config, "waehrung", "EUR"), limit=16)
            or "EUR",
            "sachkontenlaenge": _safe_int(_get_value(datev_config, "sachkontenlänge", 4) or _get_value(datev_config, "sachkontenlaenge", 4), default=4),
            "konten_mapping": {
                str(key): list(value) if isinstance(value, tuple) else value
                for key, value in konten_mapping.items()
            },
            "export_encoding": "cp1252",
            "last_export_at": None,
        }

    return {
        "schema": BUNDLE_SCHEMA,
        "created_at": _bundle_timestamp(),
        "source": {
            "app": app_name,
            "version": app_version,
            "platform": "windows",
        },
        "export_options": {
            "include_profiles": True,
            "include_file_references": True,
            "include_mail_bodies": False,
            "include_attachments": False,
        },
        "profiles": profile_rows,
        "invoices": invoice_rows,
        "datev": datev_payload,
        "companion_changes": {
            "mode": "none",
            "allowed_fields": list(ALLOWED_COMPANION_FIELDS),
        },
    }


def write_invoice_bundle(bundle: Mapping[str, Any], output_path: Path) -> Path:
    output_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def load_invoice_bundle(bundle_path: Path) -> dict[str, Any]:
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    if bundle.get("schema") != BUNDLE_SCHEMA:
        raise ValueError(f"unsupported bundle schema: {bundle.get('schema')!r}")
    return bundle


def _bundle_invoice_hash(bundle_invoice: Mapping[str, Any]) -> str:
    files = bundle_invoice.get("files") or []
    if files and isinstance(files[0], Mapping):
        return _normalize_text(files[0].get("sha256", ""), limit=128)
    return _normalize_text(bundle_invoice.get("local_hash", ""), limit=128)


def _current_local_hash(invoice: Any) -> tuple[Optional[str], Optional[str]]:
    invoice_path_raw = _normalize_text(_get_value(invoice, "path", ""), limit=1000)
    if not invoice_path_raw:
        return None, "missing_local_path"

    invoice_path = Path(invoice_path_raw)
    if not invoice_path.exists() or not invoice_path.is_file():
        return None, "missing_local_file"

    try:
        import hashlib

        current_hash = hashlib.sha256(invoice_path.read_bytes()).hexdigest()
    except OSError:
        return None, "local_file_unreadable"
    return current_hash, None


def apply_invoice_bundle_changes(invoices: Iterable[Any], bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Apply allowed bundle fields back onto local invoices."""
    if bundle.get("schema") != BUNDLE_SCHEMA:
        raise ValueError(f"unsupported bundle schema: {bundle.get('schema')!r}")

    invoice_map = {
        _normalize_text(_get_value(invoice, "id", ""), limit=120): invoice
        for invoice in invoices
        if _normalize_text(_get_value(invoice, "id", ""), limit=120)
    }
    allowed_fields = set(bundle.get("companion_changes", {}).get("allowed_fields", ALLOWED_COMPANION_FIELDS))
    allowed_fields &= set(ALLOWED_COMPANION_FIELDS)

    result = {
        "updated": 0,
        "unchanged": 0,
        "missing_local": [],
        "conflicts": [],
        "invalid_rows": [],
    }

    for bundle_invoice in bundle.get("invoices", []):
        invoice_id = _normalize_text(bundle_invoice.get("id", ""), limit=120)
        if not invoice_id:
            result["invalid_rows"].append({"id": "", "reason": "missing_id"})
            continue

        local_invoice = invoice_map.get(invoice_id)
        if local_invoice is None:
            result["missing_local"].append({"id": invoice_id, "reason": "missing_local_invoice"})
            continue

        current_hash, hash_error = _current_local_hash(local_invoice)
        if hash_error:
            result["conflicts"].append({"id": invoice_id, "reason": hash_error})
            continue

        bundle_hash = _bundle_invoice_hash(bundle_invoice)
        if bundle_hash and current_hash and bundle_hash != current_hash:
            result["conflicts"].append({"id": invoice_id, "reason": "file_hash_mismatch"})
            continue

        changed = False
        for field_name in ALLOWED_COMPANION_FIELDS:
            if field_name not in allowed_fields or field_name not in bundle_invoice:
                continue

            try:
                if field_name == "amount":
                    new_value = _normalize_amount(bundle_invoice.get(field_name))
                elif field_name == "review_status":
                    new_value = _normalize_review_status(bundle_invoice.get(field_name))
                else:
                    new_value = _normalize_text(bundle_invoice.get(field_name), limit=4000)
            except (TypeError, ValueError):
                result["invalid_rows"].append({"id": invoice_id, "reason": f"invalid_{field_name}"})
                continue

            current_val = local_invoice[field_name] if isinstance(local_invoice, Mapping) else getattr(local_invoice, field_name, None)
            if current_val != new_value:
                if isinstance(local_invoice, (dict, MutableMapping)):
                    local_invoice[field_name] = new_value
                else:
                    setattr(local_invoice, field_name, new_value)
                changed = True

        if changed:
            result["updated"] += 1
        else:
            result["unchanged"] += 1

    return result
