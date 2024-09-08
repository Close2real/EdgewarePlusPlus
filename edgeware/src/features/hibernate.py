import logging
import random
from collections.abc import Callable
from threading import Thread
from tkinter import Tk

from features.drive import fill_drive
from features.misc import handle_wallpaper
from pack import Pack
from roll import RollTarget, roll_targets
from settings import Settings
from state import State


def spaced(root: Tk, settings: Settings, targets: list[RollTarget], run: Callable[[], bool]) -> None:
    if not run():
        return

    roll_targets(settings, targets)
    root.after(settings.delay, lambda: spaced(root, settings, targets, run))


def glitch(root: Tk, settings: Settings, targets: list[RollTarget], run: Callable[[], bool]) -> None:
    def loop(n: int = 0) -> None:
        if not run() or n >= settings.hibernate_activity:
            return

        roll_targets(settings, targets)

        base = settings.hibernate_activity_length // settings.hibernate_activity
        modifier = random.randint(2, 4)

        delay = random.choice([0, base, base // modifier, base * modifier])
        root.after(delay, lambda: loop(n + 1))

    loop()


def ramp(root: Tk, settings: Settings, targets: list[RollTarget], run: Callable[[], bool]) -> None:
    halfway = False

    def reached_halfway() -> None:
        nonlocal halfway
        halfway = True

    root.after(settings.hibernate_activity_length // 2, reached_halfway)

    def loop(delay_modifier: float = settings.hibernate_activity_length // 4, accelerate: float = 1, n: int = 0) -> None:
        if not run() or n >= settings.hibernate_activity:
            return

        if delay_modifier < 100:
            roll_targets(settings, targets)
            n += 1
            delay = int(settings.delay * 0.9)
        else:
            roll_targets(settings, targets)
            accelerate *= 1.05 if halfway else 1.10
            delay_modifier = delay_modifier / accelerate
            delay = int(settings.delay + delay_modifier)

        root.after(delay, lambda: loop(delay_modifier, accelerate, n))

    loop()


def activity_loop(
    root: Tk, settings: Settings, targets: list[RollTarget], callback: Callable[[], None], activity: Callable[[Tk, Settings, list[RollTarget], bool], None]
) -> None:
    run = True

    def end() -> None:
        nonlocal run
        run = False
        callback()

    root.after(settings.hibernate_activity_length, end)
    activity(root, settings, targets, lambda: run)


def main_hibernate(root: Tk, settings: Settings, pack: Pack, state: State, targets: list[RollTarget]) -> None:
    def on_end() -> None:
        state.hibernate_active = False
        state.pump_scare = False
        delay = random.randint(settings.hibernate_delay_min, settings.hibernate_delay_max)
        state.hibernate_id = root.after(delay, lambda: main_hibernate(root, settings, pack, state, targets))

    state.hibernate_active = True
    type = settings.hibernate_type if settings.hibernate_type != "Chaos" else random.choice(["Original", "Spaced", "Glitch", "Ramp", "Pump-Scare"])

    Thread(target=lambda: fill_drive(root, settings, pack, state), daemon=True).start()  # Thread for performance reasons
    if settings.hibernate_fix_wallpaper:
        handle_wallpaper(root, settings, pack, state)

    match type:
        case "Original":
            for n in range(random.randint(settings.hibernate_activity // 2, settings.hibernate_activity)):
                roll_targets(settings, targets)
            on_end()
        case "Spaced":
            activity_loop(root, settings, targets, on_end, spaced)
        case "Glitch":
            activity_loop(root, settings, targets, on_end, glitch)
        case "Ramp":
            activity_loop(root, settings, targets, on_end, ramp)
        case "Pump-Scare":
            state.pump_scare = True
            targets[0].function()  # Image popup
            targets[4].function()  # Audio
            on_end()
        case _:
            logging.error(f"Unknown hibernate type {type}.")
