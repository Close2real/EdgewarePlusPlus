import logging
from multiprocessing.connection import Client, Listener
from threading import Thread
from tkinter import Tk, simpledialog

from paths import CustomAssets
from settings import Settings
from state import State
from utils import utils

ADDRESS = ("localhost", 6000)
AUTHKEY = b"Edgeware++"
PANIC_MESSAGE = "panic"


def panic(root: Tk, settings: Settings, state: State, key: str | None = None) -> None:
    if settings.panic_disabled or (key and key != settings.panic_key):
        return

    if settings.timer_mode and state.timer_active:
        password = simpledialog.askstring("Panic", "Enter Panic Password")
        if password != settings.timer_password:
            return

    utils.set_wallpaper(CustomAssets.panic_wallpaper())
    root.destroy()
    if state.gallery_dl_process:
        state.gallery_dl_process.kill()


def start_panic_listener(root: Tk, settings: Settings, state: State) -> None:
    def listen() -> None:
        try:
            with Listener(address=ADDRESS, authkey=AUTHKEY) as listener:
                with listener.accept() as connection:
                    message = connection.recv()
                    if message == PANIC_MESSAGE:
                        panic(root, settings, state)
        except OSError as e:
            logging.warning(f"Failed to start panic listener, some panic sources may not be functional. Reason: {e}")

    Thread(target=listen, daemon=True).start()


def send_panic() -> None:
    with Client(address=ADDRESS, authkey=AUTHKEY) as connection:
        connection.send(PANIC_MESSAGE)


if __name__ == "__main__":
    send_panic()
