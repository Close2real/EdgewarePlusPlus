import ast
import json
import shutil
import subprocess
import sys

from paths import Assets, Data, Process, Resource

try:
    import vlc
except FileNotFoundError:
    pass

# TODO/TO CONSIDER FOR BLACKLIST:
# would rotate_wallpaper even work at all if the user didn't have any set? can packs set the rotating wallpapers somehow? (other than via corruption levels)
# you could maybe set wallpaperdat but not sure how many people would bother with this
config_blacklist = [
    "version",  # version, etc, things that make no sense to change
    "versionplusplus",
    "panicButton",  # while disabling panic could be used for danger-chasing fetishists, changing the hotkey serves little purpose
    "safeword",  # imo, the safeword is a safeword for a reason (timer mode)
    "drivePath",  # We can't know what paths exist and they look different on Linux and Windows
    "safeMode",  # optional warning in config to warn of dangerous settings. being able to disable remotely doesn't affect anything horny, just allows you to be a dick
    "toggleInternet",  # troubleshooting settings
    "toggleHibSkip",
    "toggleMoodSet",
    "corruptionMode",  # if you're turning off corruption mode with corruption just make it the final level lmao
    "vlcMode",  # we might get rid of this anyways if we force vlc, but also people shouldn't be able to disable/enable this forcibly
    "presetsDanger",  # see safeMode
    "corruptionDevMode",
    "corruptionFullPerm",
    "messageOff",
    "runOnSaveQuit",
    "themeNoConfig",
    # Changing these settings would most likely not do anything with their current implementation
    "desktopIcons",
    "showLoadingFlair",
    "rotateWallpaper",
    "replace",  # replace images
    "replaceThresh",
    "avoidList",  # avoid list for replace images. also works on fill drive but due to filepath the only thing you can do with this is make it blank
    "start_on_logon",
    "showDiscord",  # show discord status, technically not PC dangerous but socially dangerous
    "timerMode",  # locks out panic until certain time has passed
    "timerSetupTime",
    "hibernateMode",
    "start_on_logon",
    # TODO: Test changing these, they will probably work but may have strange interactions
    "lkToggle",
    "mitosisMode",
]

# TODO/TO CONSIDER FOR DANGEROUS:
# wakeupActivity for hibernate (as well as very low hibernate durations)?
# mitosismode/mitosis_strength can potentially cause a dangerous payload of popups if set incorrectly
# capPopTimer could potentially cause seizures if low enough... however, considering not bothering with this as so many settings have to be set right
config_dangerous = [
    "fill",  # fill drive
    "fill_delay",
    "maxFillThreads",
    "panicDisabled",  # disables panic in hotkey/system tray, can still be run via panic.pyw
    "webPopup",  # opens up web popup on popup close, this one could be cut from this list as it's not listed as dangerous in config but could lead to bad performance
]

# Settings I found that are maybe dead currently since I can't find use (feel free to delete this once it's taken care of):
# pumpScareOffset (used to be for offsetting the pumpscare audio, might be irrelevant once we force vlc)


def first_launch_configure() -> None:
    if not Data.CONFIG.is_file():
        subprocess.run([sys.executable, Process.CONFIG, "--first-launch-configure"])


def load_config() -> dict:
    if not Data.CONFIG.is_file():
        Data.ROOT.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Assets.DEFAULT_CONFIG, Data.CONFIG)

    default_config = load_default_config()
    with open(Data.CONFIG, "r+") as f:
        config = json.loads(f.read())

        new_keys = False
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
                new_keys = True

        if new_keys:
            f.seek(0)
            f.write(json.dumps(config))
            f.truncate()

    return config


def load_default_config() -> dict:
    with open(Assets.DEFAULT_CONFIG) as f:
        default_config = json.loads(f.read())

    return default_config


class Settings:
    def __init__(self):
        self.config = load_config()
        self.load_settings()

        # if self.config["corruptionMode"] and self.config["corruptionFullPerm"]:
        # self.dangers = self.danger_check()
        # print(self.dangers)

    def set_config(key: str, value: str | int) -> None:
        if key not in config_blacklist:
            self.config[key] = value

    def danger_check(self) -> list:
        danger_list = []
        with open(Resource.CORRUPTION) as f:
            corruption_data = json.loads(f.read())
            for level in corruption_data["config"]:
                for key in corruption_data["config"][level]:
                    if key in config_dangerous and not danger_list:
                        danger_list.append(key)
                    if key == "delay":
                        if corruption_data["config"][level]["delay"] < 2000:
                            danger_list.append(f"Low delay ({corruption_data['config'][level]['delay']}ms)")
                    if key == "wakeupActivity":
                        if corruption_data["config"][level]["wakeupActivity"] > 35:
                            danger_list.append(f"High hibernate wakeup ({corruption_data['config'][level]['wakeupActivity']})")
                    if key == "hibernateMax":
                        if corruption_data["config"][level]["hibernateMax"] < 10:
                            danger_list.append(f"Low max hibernate delay ({corruption_data['config'][level]['hibernateMax']})")
        return danger_list

    def load_settings(self) -> None:
        # Impacts other settings
        lowkey_mode = bool(self.config["lkToggle"])
        mitosis_mode = bool(self.config["mitosisMode"]) or lowkey_mode

        # General
        self.theme = self.config["themeType"]
        self.startup_splash = bool(self.config["showLoadingFlair"])
        self.desktop_icons = bool(self.config["desktopIcons"])
        self.panic_key = self.config["panicButton"]

        # Booru downloader
        self.booru_download = bool(self.config["downloadEnabled"])
        self.booru_name = self.config["booruName"]
        # self.min_score = int(self.config["booruMinScore"])  # TODO: Can this be used with gallery-dl?
        self.booru_tags = self.config["tagList"].replace(">", "+")  # TODO: Store in a better way
        self.download_path = Data.DOWNLOAD / f"{self.booru_name}-{self.booru_tags}"

        # Popups
        self.delay = int(self.config["delay"])  # Milliseconds
        self.image_chance = int(self.config["popupMod"]) if not mitosis_mode else 0  # 0 to 100
        self.opacity = int(self.config["lkScaling"]) / 100  # Float between 0 and 1
        self.timeout_enabled = bool(self.config["timeoutPopups"]) or lowkey_mode
        self.timeout = int(self.config["popupTimeout"]) * 1000 if not lowkey_mode else self.delay  # Milliseconds
        self.buttonless = bool(self.config["buttonless"])
        self.single_mode = bool(self.config["singleMode"])

        # Overlays
        self.denial_chance = int(self.config["denialChance"]) if bool(self.config["denialMode"]) else 0  # 0 to 100
        self.subliminal_chance = int(self.config["subliminalsChance"]) if bool(self.config["popupSubliminals"]) else 0  # 0 to 100
        self.max_subliminals = int(self.config["maxSubliminals"])
        self.subliminal_opacity = int(self.config["subliminalsAlpha"]) / 100  # Float between 0 and 1

        # Web
        self.web_chance = int(self.config["webMod"])  # 0 to 100
        self.web_on_popup_close = bool(self.config["webPopup"]) and not lowkey_mode

        # Prompt
        self.prompt_chance = int(self.config["promptMod"])  # 0 to 1000
        self.prompt_max_mistakes = int(self.config["promptMistakes"])

        # Audio
        self.audio_chance = int(self.config["audioMod"])  # 0 to 100
        self.max_audio = int(self.config["maxAudio"])

        # Video
        self.video_chance = int(self.config["vidMod"]) if not mitosis_mode else 0  # 0 to 100
        self.video_volume = int(self.config["videoVolume"])  # 0 to 100
        self.max_video = int(self.config["maxVideos"]) if bool(self.config["maxVideoBool"]) else float("inf")
        self.vlc_mode = bool(self.config["vlcMode"])
        try:
            vlc.libvlc_hex_version()  # Check if VLC is installed
        except NameError:
            self.vlc_mode = False

        # Captions
        self.captions_in_popups = bool(self.config["showCaptions"])
        self.filename_caption_moods = bool(self.config["captionFilename"])
        self.multi_click_popups = bool(self.config["multiClick"])
        self.subliminal_caption_mood = bool(self.config["capPopMood"])
        self.subliminal_message_popup_chance = int(self.config["capPopChance"])  # 0 to 100
        self.subliminal_message_popup_opacity = int(self.config["capPopOpacity"]) / 100  # Float between 0 and 1
        self.subliminal_message_popup_timeout = int(self.config["capPopTimer"])  # Milliseconds
        self.notification_mood = bool(self.config["notificationMood"])
        self.notification_chance = int(self.config["notificationChance"])  # 0 to 100
        self.notification_image_chance = int(self.config["notificationImageChance"])  # 0 to 100

        # Wallpaper
        self.rotate_wallpaper = bool(self.config["rotateWallpaper"])
        self.wallpaper_timer = int(self.config["wallpaperTimer"]) * 1000  # Milliseconds
        self.wallpaper_variance = int(self.config["wallpaperVariance"]) * 1000  # Milliseconds
        self.wallpapers = list(ast.literal_eval(self.config["wallpaperDat"]).values())  # TODO: Can fail, store in a better way

        # Dangerous
        self.drive_avoid_list = self.config["avoidList"].split(">")  # TODO: Store in a better way
        self.fill_drive = bool(self.config["fill"])
        self.drive_path = self.config["drivePath"]
        self.fill_delay = int(self.config["fill_delay"]) * 10  # Milliseconds
        self.replace_images = bool(self.config["replace"])
        self.replace_threshold = int(self.config["replaceThresh"])
        self.panic_disabled = bool(self.config["panicDisabled"])
        self.show_on_discord = bool(self.config["showDiscord"])

        # Basic modes
        self.lowkey_mode = lowkey_mode
        self.lowkey_corner = int(self.config["lkCorner"])
        self.moving_chance = int(self.config["movingChance"])  # 0 to 100
        self.moving_speed = int(self.config["movingSpeed"])
        self.moving_random = bool(self.config["movingRandom"])

        # Dangerous modes
        self.timer_mode = bool(self.config["timerMode"])
        self.timer_time = int(self.config["timerSetupTime"]) * 60 * 1000  # Milliseconds
        self.timer_password = self.config["safeword"]
        self.mitosis_mode = mitosis_mode
        self.mitosis_strength = int(self.config["mitosisStrength"]) if not self.lowkey_mode else 1

        # Hibernate mode
        self.hibernate_mode = bool(self.config["hibernateMode"])
        self.hibernate_fix_wallpaper = bool(self.config["fixWallpaper"]) and self.hibernate_mode
        self.hibernate_type = self.config["hibernateType"]
        self.hibernate_delay_min = int(self.config["hibernateMin"]) * 1000  # Milliseconds
        self.hibernate_delay_max = int(self.config["hibernateMax"]) * 1000  # Milliseconds
        self.hibernate_activity = int(self.config["wakeupActivity"])
        self.hibernate_activity_length = int(self.config["hibernateLength"]) * 1000  # Milliseconds
        # TODO: Pump-scare audio
        # self.pump_scare_offset = int(self.config["pumpScareOffset"])  # Seconds

        # Corruption mode
        self.corruption_mode = bool(self.config["corruptionMode"])
        self.corruption_full = bool(self.config["corruptionFullPerm"])
        # self.corruption_fade = self.config["corruptionFadeType"]
        self.corruption_trigger = self.config["corruptionTrigger"]
        self.corruption_time = int(self.config["corruptionTime"]) * 1000  # Milliseconds
        self.corruption_popups = int(self.config["corruptionPopups"])
        self.corruption_launches = int(self.config["corruptionLaunches"])
        self.corruption_wallpaper = not bool(self.config["corruptionWallpaperCycle"])
        # self.corruption_themes = not bool(self.config["corruptionThemeCycle"])
        self.corruption_purity = bool(self.config["corruptionPurityMode"])
        self.corruption_dev_mode = bool(self.config["corruptionDevMode"])
