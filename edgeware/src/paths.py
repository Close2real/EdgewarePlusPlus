from dataclasses import dataclass
from pathlib import Path

PATH = Path(__file__).parent.parent


@dataclass
class Process:
    ROOT = PATH / "src"

    CONFIG = ROOT / "config.py"
    MAIN = ROOT / "main.py"
    PANIC = ROOT / "panic.py"


@dataclass
class Assets:
    ROOT = PATH / "assets"

    CORRUPTION_ABRUPT = ROOT / "corruption_abruptfade.png"
    CORRUPTION_DEFAULT = ROOT / "corruption_defaultfade.png"
    CORRUPTION_NOISE = ROOT / "corruption_noisefade.png"

    # Unchangeable defaults
    DEFAULT_CONFIG = ROOT / "default_config.json"
    DEFAULT_IMAGE = ROOT / "default_image.png"
    DEFAULT_WALLPAPER = ROOT / "default_wallpaper.png"

    # Changeable defaults
    DEFAULT_CONFIG_ICON = ROOT / "default_config_icon.ico"
    DEFAULT_ICON = ROOT / "default_icon.ico"
    DEFAULT_PANIC_ICON = ROOT / "default_panic_icon.ico"
    DEFAULT_PANIC_WALLPAPER = ROOT / "default_panic_wallpaper.jpg"
    DEFAULT_STARTUP_SPLASH = ROOT / "default_loading_splash.png"
    DEFAULT_SUBLIMINAL_OVERLAY = ROOT / "default_subliminal_overlay.gif"
    DEFAULT_THEME_DEMO = ROOT / "default_theme_demo.png"


@dataclass
class Data:
    ROOT = PATH / "data"

    # Directories
    BACKUPS = ROOT / "backups"
    DOWNLOAD = ROOT / "download"
    LOGS = ROOT / "logs"
    MOODS = ROOT / "moods"
    PRESETS = ROOT / "presets"

    # Files
    CONFIG = ROOT / "config.json"
    CORRUPTION_LAUNCHES = ROOT / "corruption_launches.dat"
    GALLERY_DL_CONFIG = ROOT / "gallery-dl.json"

    # Changed defaults
    CONFIG_ICON = ROOT / "config_icon.ico"
    ICON = ROOT / "icon.ico"
    PANIC_ICON = ROOT / "panic_icon.ico"
    PANIC_WALLPAPER = ROOT / "panic_wallpaper.png"
    STARTUP_SPLASH = ROOT / "loading_splash.png"
    SUBLIMINAL_OVERLAY = ROOT / "subliminal_overlay.png"
    THEME_DEMO = ROOT / "theme_demo.png"


@dataclass
class CustomAssets:
    def config_icon() -> Path:
        return Data.CONFIG_ICON if Data.CONFIG_ICON.is_file() else Assets.DEFAULT_CONFIG_ICON

    def icon() -> Path:
        return Data.ICON if Data.ICON.is_file() else Assets.DEFAULT_ICON

    def panic_icon() -> Path:
        return Data.PANIC_ICON if Data.PANIC_ICON.is_file() else Assets.DEFAULT_PANIC_ICON

    def panic_wallpaper() -> Path:
        return Data.PANIC_WALLPAPER if Data.PANIC_WALLPAPER.is_file() else Assets.DEFAULT_PANIC_WALLPAPER

    def startup_splash() -> Path:
        return Data.STARTUP_SPLASH if Data.STARTUP_SPLASH.is_file() else Assets.DEFAULT_STARTUP_SPLASH

    def subliminal_overlay() -> Path:
        return Data.SUBLIMINAL_OVERLAY if Data.SUBLIMINAL_OVERLAY.is_file() else Assets.DEFAULT_SUBLIMINAL_OVERLAY

    def theme_demo() -> Path:
        return Data.THEME_DEMO if Data.THEME_DEMO.is_file() else Assets.DEFAULT_THEME_DEMO


@dataclass
class Resource:
    ROOT = PATH / "resource"

    # Directories
    AUDIO = ROOT / "aud"
    IMAGE = ROOT / "img"
    SUBLIMINALS = ROOT / "subliminals"
    VIDEO = ROOT / "vid"

    # Files
    CAPTIONS = ROOT / "captions.json"
    CONFIG = ROOT / "config.json"
    CORRUPTION = ROOT / "corruption.json"
    DISCORD = ROOT / "discord.dat"
    ICON = ROOT / "icon.ico"
    INFO = ROOT / "info.json"
    SPLASH = [PATH / "resource" / f"loading_splash.{extension}" for extension in [".png", ".gif", ".jpg", ".jpeg", ".bmp"]]
    MEDIA = ROOT / "media.json"
    PROMPT = ROOT / "prompt.json"
    WALLPAPER = ROOT / "wallpaper.png"
    WEB = ROOT / "web.json"
