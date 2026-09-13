# -*- mode: python ; coding: utf-8 -*-
"""Windows onedir build contract for UniversalInvoiceMail."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


project_root = Path(SPECPATH).resolve()

datas = [
    (str(project_root / "UniversalInvoiceMail_icon.ico"), "."),
    (str(project_root / "UniversalInvoiceMail_icon.png"), "."),
]

locales_dir = project_root / "locales"
if locales_dir.exists():
    datas.append((str(locales_dir), "locales"))

a = Analysis(
    [str(project_root / "UniversalInvoiceMail.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=collect_submodules("keyring.backends"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "tkinter"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="UniversalInvoiceMail",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(project_root / "UniversalInvoiceMail_icon.ico")],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="UniversalInvoiceMail",
)
