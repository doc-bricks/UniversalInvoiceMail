"""Generate UniversalInvoiceMail Windows Store icons, assets and manifest."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOFTWARE_ROOT = PROJECT_ROOT.parents[1]
STORE_PACKAGER_PATH = SOFTWARE_ROOT / "_STORE" / "store_packager.py"
APP_NAME = "UniversalInvoiceMail"
ICON_SOURCE = PROJECT_ROOT / "UniversalInvoiceMail_icon.png"
STORE_PACKAGE_DIR = PROJECT_ROOT / "store_package" / APP_NAME
ICON_DIR = STORE_PACKAGE_DIR / "icons"
LEGACY_STORE_ASSETS_DIR = PROJECT_ROOT / "store_assets"

LEGACY_ICON_NAMES = {
    "icon_44x44.png": "Square44x44Logo.png",
    "icon_50x50.png": "StoreLogo.png",
    "icon_150x150.png": "Square150x150Logo.png",
    "icon_310x310.png": "Square310x310Logo.png",
    "icon_310x150.png": "Wide310x150Logo.png",
}


def load_store_config(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    config_path = project_root / "store_package.json"
    if not config_path.exists():
        raise FileNotFoundError(f"store_package.json fehlt: {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8"))


def _load_store_packager_class():
    if not STORE_PACKAGER_PATH.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location("store_packager", STORE_PACKAGER_PATH)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "StorePackager", None)
    except Exception:
        return None


def xml_attr(value: Any) -> str:
    return escape(str(value), {'"': "&quot;"})


def xml_text(value: Any) -> str:
    return escape(str(value))


def capability_lines(raw_capabilities: list[str] | str) -> str:
    if isinstance(raw_capabilities, list):
        items = raw_capabilities
    else:
        items = [c.strip() for c in str(raw_capabilities).split(",") if c.strip()]

    lines: list[str] = []
    for capability in items:
        if not capability:
            continue
        if capability == "runFullTrust":
            lines.append('    <rescap:Capability Name="runFullTrust" />')
        else:
            lines.append(f'    <Capability Name="{xml_attr(capability)}" />')
    return "\n".join(lines) or '    <rescap:Capability Name="runFullTrust" />'


def render_manifest(store_config: dict[str, Any], exe_name: str | None = None) -> str:
    app_name = str(store_config.get("app_name") or APP_NAME)
    executable = exe_name or str(store_config.get("executable") or f"{app_name}.exe")
    app_id = "".join(char for char in app_name if char.isalnum()) or APP_NAME
    display_name = str(store_config.get("display_name") or app_name)
    publisher_display = str(store_config.get("publisher_display") or store_config.get("publisher_name") or "Lukas Geiger")
    identity_name = str(store_config.get("identity_name") or store_config.get("package_id") or "Geiger.UniversalInvoiceMail")
    publisher_id = str(store_config.get("publisher") or store_config.get("publisher_id") or "CN=52596601-BAB4-4F3F-B182-E8F3F273B202")
    version = str(store_config.get("version") or "2.3.0.0")
    description = (
        "Lokale Rechnungszentrale: Automatischer Abruf, PDF-Konvertierung, "
        "DATEV-Export und Rechnungsmanagement aus E-Mail-Postfächern ohne Cloud-Zwang."
    )
    capabilities = capability_lines(store_config.get("capabilities", ["runFullTrust"]))

    return f"""<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
         xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
         IgnorableNamespaces="uap rescap">

  <Identity Name="{xml_attr(identity_name)}"
            Publisher="{xml_attr(publisher_id)}"
            Version="{xml_attr(version)}"
            ProcessorArchitecture="x64" />

  <Properties>
    <DisplayName>{xml_text(display_name)}</DisplayName>
    <PublisherDisplayName>{xml_text(publisher_display)}</PublisherDisplayName>
    <Logo>icons\\icon_150x150.png</Logo>
    <Description>{xml_text(description)}</Description>
  </Properties>

  <Dependencies>
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.26100.0" />
  </Dependencies>

  <Resources>
    <Resource Language="de-de" />
    <Resource Language="en-us" />
  </Resources>

  <Capabilities>
{capabilities}
  </Capabilities>

  <Applications>
    <Application Id="{xml_attr(app_id)}App"
                 Executable="{xml_attr(executable)}"
                 EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements DisplayName="{xml_attr(app_name)}"
                          Description="{xml_attr(description)}"
                          Square150x150Logo="icons\\icon_150x150.png"
                          Square44x44Logo="icons\\icon_44x44.png"
                          BackgroundColor="transparent">
        <uap:DefaultTile Wide310x150Logo="icons\\icon_310x150.png"
                         Square310x310Logo="icons\\icon_310x310.png" />
        <uap:SplashScreen Image="icons\\SplashScreen.png" />
      </uap:VisualElements>
    </Application>
  </Applications>
</Package>
"""


def write_manifest(store_config: dict[str, Any], output_dir: Path = STORE_PACKAGE_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "AppxManifest.xml"
    manifest_path.write_text(
        render_manifest(store_config, exe_name=str(store_config.get("executable") or f"{APP_NAME}.exe")),
        encoding="utf-8",
    )
    legacy_manifest = LEGACY_STORE_ASSETS_DIR / "AppxManifest.xml"
    LEGACY_STORE_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    legacy_manifest.write_text(manifest_path.read_text(encoding="utf-8"), encoding="utf-8")
    return manifest_path


def _generate_icons_pil(icon_source: Path, icon_dir: Path) -> list[Path]:
    from PIL import Image

    icon_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(icon_source) as img:
        img_rgba = img.convert("RGBA")
        square_sizes = [(44, 44), (50, 50), (150, 150), (310, 310)]
        for w, h in square_sizes:
            target = icon_dir / f"icon_{w}x{h}.png"
            resized = img_rgba.resize((w, h), Image.Resampling.LANCZOS)
            resized.save(target, format="PNG")

        # Wide icon 310x150
        wide_img = Image.new("RGBA", (310, 150), (0, 0, 0, 0))
        h_scaled = 120
        w_scaled = int(120 * (img_rgba.width / img_rgba.height))
        scaled_icon = img_rgba.resize((w_scaled, h_scaled), Image.Resampling.LANCZOS)
        x = (310 - w_scaled) // 2
        y = (150 - h_scaled) // 2
        wide_img.paste(scaled_icon, (x, y), scaled_icon)
        wide_target = icon_dir / "icon_310x150.png"
        wide_img.save(wide_target, format="PNG")

        # Splash screen 620x300
        splash_img = Image.new("RGBA", (620, 300), (0, 0, 0, 0))
        h_splash = 200
        w_splash = int(200 * (img_rgba.width / img_rgba.height))
        splash_scaled = img_rgba.resize((w_splash, h_splash), Image.Resampling.LANCZOS)
        x_splash = (620 - w_splash) // 2
        y_splash = (300 - h_splash) // 2
        splash_img.paste(splash_scaled, (x_splash, y_splash), splash_scaled)
        splash_target = icon_dir / "SplashScreen.png"
        splash_img.save(splash_target, format="PNG")

    return sorted(icon_dir.glob("*.png"))


def generate_icons(icon_source: Path = ICON_SOURCE, icon_dir: Path = ICON_DIR) -> list[Path]:
    if not icon_source.exists():
        raise FileNotFoundError(f"Icon-Quelle fehlt: {icon_source}")

    store_packager_class = _load_store_packager_class()
    if store_packager_class:
        try:
            packager = store_packager_class(PROJECT_ROOT)
            if packager.generate_icons(str(icon_source), output_dir=icon_dir):
                from PIL import Image
                splash_target = icon_dir / "SplashScreen.png"
                if not splash_target.exists():
                    with Image.open(icon_source) as img:
                        img_rgba = img.convert("RGBA")
                        splash_img = Image.new("RGBA", (620, 300), (0, 0, 0, 0))
                        h_splash = 200
                        w_splash = int(200 * (img_rgba.width / img_rgba.height))
                        splash_scaled = img_rgba.resize((w_splash, h_splash), Image.Resampling.LANCZOS)
                        splash_img.paste(splash_scaled, ((620 - w_splash) // 2, (300 - h_splash) // 2), splash_scaled)
                        splash_img.save(splash_target, format="PNG")
                return sorted(icon_dir.glob("*.png"))
        except Exception:
            pass

    return _generate_icons_pil(icon_source, icon_dir)


def sync_legacy_store_assets(icon_dir: Path = ICON_DIR, assets_dir: Path = LEGACY_STORE_ASSETS_DIR) -> list[Path]:
    assets_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for source_name, target_name in LEGACY_ICON_NAMES.items():
        source = icon_dir / source_name
        if not source.exists():
            raise FileNotFoundError(f"Generiertes Icon fehlt: {source}")
        target = assets_dir / target_name
        shutil.copyfile(source, target)
        written.append(target)
    splash_src = icon_dir / "SplashScreen.png"
    if splash_src.exists():
        splash_dst = assets_dir / "SplashScreen.png"
        shutil.copyfile(splash_src, splash_dst)
        written.append(splash_dst)
    return written


def write_store_assets_readme(
    icon_paths: list[Path],
    legacy_paths: list[Path],
    manifest_path: Path,
    icon_dir: Path = ICON_DIR,
) -> Path:
    lines = [
        f"# Windows-Store-Assets ({APP_NAME})",
        "",
        f"Erzeugt aus {ICON_SOURCE.name} über scripts/store_assets.py.",
        "Kompatibel mit Windows Store / MSIX Packaging und WACK-Kriterien.",
        "",
        f"## Store-Package-Icons (store_package/{APP_NAME}/icons/)",
        "",
    ]
    lines.extend(f"- {path.name}" for path in icon_paths)
    lines.extend(["", "## Legacy-/MSIX-Asset-Namen (store_assets/)", ""])
    lines.extend(f"- {path.relative_to(PROJECT_ROOT).as_posix()}" for path in legacy_paths)
    lines.extend(["", f"Manifest: {manifest_path.relative_to(PROJECT_ROOT).as_posix()}", ""])
    target = icon_dir / "README.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def generate_store_assets() -> dict[str, Any]:
    store_config = load_store_config()
    icon_paths = generate_icons()
    legacy_paths = sync_legacy_store_assets()
    manifest_path = write_manifest(store_config)
    readme_path = write_store_assets_readme(icon_paths, legacy_paths, manifest_path)
    return {
        "icons": [str(path.relative_to(PROJECT_ROOT)) for path in icon_paths],
        "legacy_assets": [str(path.relative_to(PROJECT_ROOT)) for path in legacy_paths],
        "manifest": str(manifest_path.relative_to(PROJECT_ROOT)),
        "readme": str(readme_path.relative_to(PROJECT_ROOT)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Ergebnis als JSON ausgeben.")
    args = parser.parse_args(argv)

    result = generate_store_assets()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Manifest: {result['manifest']}")
        print(f"Icons: {len(result['icons'])}")
        print(f"Legacy Assets: {len(result['legacy_assets'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
