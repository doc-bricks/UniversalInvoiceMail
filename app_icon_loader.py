"""App-Icon-Loader für UniversalInvoiceMail.

Lädt das Anwendungs-Icon mit robuster Multi-Pfad-Auflösung (PyInstaller-Bundle,
assets/UniversalInvoiceMail.ico, assets/app_icon.ico, Root-ICOs und PNG-Fallback)
sowohl als PIL-Image (für System-Tray / Bildbearbeitung) als auch optional als QIcon.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from PIL import Image


def get_project_root() -> Path:
    """Liefert das Basisverzeichnis für Ressourcen im Repo oder gefrorenen Bundle."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def get_app_icon_path() -> Path | None:
    """Findet den besten verfügbaren Pfad zur Icon-Datei."""
    root = get_project_root()
    candidates = [
        root / "UniversalInvoiceMail.ico",
        root / "UniversalInvoiceMail_icon.ico",
        root / "assets" / "UniversalInvoiceMail.ico",
        root / "assets" / "UniversalInvoiceMail_icon.ico",
        root / "assets" / "app_icon.ico",
        root / "assets" / "DesktopIcon.ico",
        root / "assets" / "icon.ico",
        root / "DesktopIcon.ico",
        root / "icon.ico",
        root / "ICO.ico",
        root / "UniversalInvoiceMail.png",
        root / "UniversalInvoiceMail_icon.png",
        root / "assets" / "UniversalInvoiceMail.png",
        root / "assets" / "UniversalInvoiceMail_icon.png",
        root / "assets" / "DesktopIcon.png",
        root / "assets" / "icon.png",
        root / "DesktopIcon.png",
        root / "icon.png",
    ]
    for cand in candidates:
        if cand.is_file():
            return cand
    return None


def load_app_icon_pil(size: int = 64) -> Image.Image:
    """Lädt das Anwendungs-Icon als PIL Image mit Fallback."""
    from PIL import Image, ImageDraw

    icon_path = get_app_icon_path()
    if icon_path is not None:
        try:
            with Image.open(icon_path) as img:
                return img.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
        except Exception:
            pass

    # Deterministischer Fallback falls Datei nicht lesbar (Theme #10203a / #14b8a6)
    image = Image.new("RGBA", (size, size), (16, 32, 58, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((2, 2, size - 3, size - 3), radius=max(2, size // 5), fill=(16, 32, 58, 255))
    draw.rounded_rectangle(
        (size * 0.2, size * 0.3, size * 0.8, size * 0.7),
        radius=max(1, size // 16),
        fill=(217, 238, 247, 255),
    )
    draw.rounded_rectangle(
        (size * 0.5, size * 0.2, size * 0.8, size * 0.5),
        radius=max(1, size // 16),
        fill=(255, 107, 87, 255),
    )
    draw.rounded_rectangle(
        (size * 0.2, size * 0.55, size * 0.45, size * 0.8),
        radius=max(1, size // 16),
        fill=(20, 184, 166, 255),
    )
    return image


def load_app_icon() -> Any:
    """Lädt ein valides QIcon falls eine Qt Application aktiv ist und PySide6/PyQt verfügbar ist, sonst None."""
    try:
        from PySide6.QtGui import QGuiApplication, QIcon
    except ImportError:
        try:
            from PyQt6.QtGui import QGuiApplication, QIcon
        except ImportError:
            return None

    app = QGuiApplication.instance()
    if app is None:
        return None

    icon_path = get_app_icon_path()
    if icon_path is not None:
        try:
            icon = QIcon(str(icon_path))
            if not icon.isNull():
                return icon
        except Exception:
            pass

    # Fallback über QPixmap aus PIL
    try:
        from PySide6.QtGui import QIcon, QImage, QPixmap

        pil_img = load_app_icon_pil(256)
        data = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_img.size[0], pil_img.size[1], QImage.Format.Format_RGBA8888)
        pix = QPixmap.fromImage(qimg)
        icon = QIcon(pix)
        if not icon.isNull():
            return icon
    except Exception:
        pass

    return None


def get_app_icon() -> Any:
    """Bequemer Alias für load_app_icon()."""
    return load_app_icon()
