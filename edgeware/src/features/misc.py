import json
import logging
import random
import subprocess
import time
import webbrowser
from collections.abc import Callable
from threading import Thread
from tkinter import Tk

import pystray
from desktop_notifier.common import Attachment, Icon
from desktop_notifier.sync import DesktopNotifierSync
from pack import Pack
from panic import panic
from paths import Assets, Data, Process, Resource
from PIL import Image
from playsound import playsound
from pypresence import Presence
from roll import roll
from settings import Settings
from state import State
from utils import utils


def play_audio(settings: Settings, pack: Pack, state: State) -> None:
    # TODO: Race conditions?
    def play():
        state.audio_number += 1
        playsound(str(pack.random_audio()))
        state.audio_number -= 1

    if state.audio_number < settings.max_audio and pack.has_audio():
        Thread(target=play, daemon=True).start()


def open_web(pack: Pack) -> None:
    if pack.has_web():
        webbrowser.open(pack.random_web())


def display_notification(settings: Settings, pack: Pack) -> None:
    if not pack.has_notifications(settings):
        return

    notifier = DesktopNotifierSync(app_name="Edgeware++", app_icon=Icon(pack.icon))
    notifier.send(
        title=pack.info.name,
        message=pack.random_notification(settings),
        attachment=Attachment(pack.random_image()) if roll(settings.notification_image_chance) and pack.has_image() else None,
    )


def make_tray_icon(root: Tk, settings: Settings, pack: Pack, state: State, hibernate_activity: Callable[[], None]) -> None:
    menu = [pystray.MenuItem("Panic", lambda: panic(root, settings, state))]
    if settings.hibernate_mode:

        def skip_hibernate() -> None:
            if state.hibernate_active:
                return

            root.after_cancel(state.hibernate_id)
            hibernate_activity()

        menu.append(pystray.MenuItem("Skip to Hibernate", skip_hibernate))

    icon = pystray.Icon("Edgeware++", Image.open(pack.icon), "Edgeware++", menu)
    Thread(target=icon.run, daemon=True).start()


def make_desktop_icons(settings: Settings) -> None:
    if settings.desktop_icons:
        utils.make_shortcut("Edgeware++", Process.MAIN, Assets.DEFAULT_ICON)
        utils.make_shortcut("Edgeware++ Config", Process.CONFIG, Assets.CONFIG_ICON)
        utils.make_shortcut("Edgeware++ Panic", Process.PANIC, Assets.PANIC_ICON)


def handle_booru_download(settings: Settings, state: State) -> None:
    if not settings.booru_download:
        return

    root = f"https://{settings.booru_name}.booru.org"
    url = f"{root}/index.php?page=post&s=list&tags={settings.booru_tags}"

    with open(Data.GALLERY_DL_CONFIG, "w") as f:
        json.dump({"extractor": {"gelbooru_v01": {settings.booru_name: {"root": root}}}}, f)

    args = f'gallery-dl -D "{settings.download_path}" -c "{Data.GALLERY_DL_CONFIG}" "{url}"'
    state.gallery_dl_process = subprocess.Popen(args, shell=True)


def handle_wallpaper(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    def rotate(previous: str = None) -> None:
        if settings.hibernate_fix_wallpaper and not state.hibernate_active and state.popup_number == 0:
            return

        wallpapers = settings.wallpapers.copy()
        if previous:
            wallpapers.remove(previous)

        wallpaper = random.choice(wallpapers)
        utils.set_wallpaper(Resource.ROOT / wallpaper)

        t = settings.wallpaper_timer
        v = settings.wallpaper_variance
        root.after(t + random.randint(-v, v), lambda: rotate(wallpaper))

    if settings.corruption_mode and settings.corruption_wallpaper:
        return

    if settings.rotate_wallpaper and len(settings.wallpapers) > 1:
        rotate()
    else:
        utils.set_wallpaper(pack.wallpaper)


def handle_discord(root: Tk, settings: Settings, pack: Pack) -> None:
    if not settings.show_on_discord:
        return

    try:
        presence = Presence("820204081410736148")
        presence.connect()

        def update() -> None:
            presence.update(state=pack.discord.text, large_image=pack.discord.image, start=int(time.time()))
            root.after(15000, update)

        update()
    except Exception as e:
        logging.warning(f"Setting Discord presence failed. Reason: {e}")


def handle_timer_mode(root: Tk, settings: Settings, state: State) -> None:
    def timer_over() -> None:
        state.timer_active = False

    if settings.timer_mode:
        state.timer_active = True
        root.after(settings.timer_time, timer_over)


def handle_mitosis_mode(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    if settings.mitosis_mode:
        # Import done here to avoid circular imports
        from features.image_popup import ImagePopup

        ImagePopup(root, settings, pack, state)
