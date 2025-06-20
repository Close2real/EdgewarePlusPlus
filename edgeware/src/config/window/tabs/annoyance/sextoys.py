# Copyright (C) 2025 Araten & Marigold
#
# Sextoys implementation by Close2real
#
# This file is part of Edgeware++.
#
# Edgeware++ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Edgeware++ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Edgeware++.  If not, see <https://www.gnu.org/licenses/>.
from config.items import PERCENTAGE, FLOAT, BOOLEAN
from config.vars import Vars
from config.window.widgets.layout import ConfigRow, ConfigScale, ConfigSection, ConfigFloatScale, ConfigToggle, ConfigTitle
from config.window.widgets.scroll_frame import ScrollFrame
from config.window.utils import (
    config
)
from tkinter import Entry, Frame, StringVar, Listbox, Button, IntVar, messagebox, BooleanVar, DoubleVar, Checkbutton
from features.sextoy import Sextoy

SEXTOYS_TEXT = "Use this tab to configure your sex toys and ensure they work correctly with InitCentral. You can adjust the event-trigger chance using the controls below."
INITFACE_TEXT = "Configure your initface address in this input"

class SexToysTab(ScrollFrame):
    def __init__(self, vars: Vars) -> None:
        super().__init__()

        self.vars = vars

        self.sextoy = Sextoy(self.vars)
        self.known_devices = []
        self.device_indices = []

        self.setting_groups = {
            "General Vibration": ["sextoy_general_vibration_force"],
            "Sextoy Image Open Popup Settings": [
                "sextoy_image_open_chance",
                "sextoy_image_open_vibration_force",
                "sextoy_image_open_vibration_length"
            ],
            "Sextoy Image Close Popup Settings": [
                "sextoy_image_close_chance",
                "sextoy_image_close_vibration_force",
                "sextoy_image_close_vibration_length"
            ],
            "Sextoy Video Open Popup Settings": [
                "sextoy_video_open_chance",
                "sextoy_video_open_vibration_force",
                "sextoy_video_open_vibration_length"
            ],
            "Sextoy Video Close Popup Settings": [
                "sextoy_video_close_chance",
                "sextoy_video_close_vibration_force",
                "sextoy_video_close_vibration_length"
            ],
            "Sextoy Captions Settings": [
                "sextoy_caption_chance",
                "sextoy_caption_vibration_force",
                "sextoy_caption_vibration_length"
            ],
            "Sextoy Notifications Settings": [
                "sextoy_display_notification_chance",
                "sextoy_display_notification_vibration_force",
                "sextoy_display_notification_vibration_length"
            ],
            "Sextoy Prompts Settings": [
                "sextoy_prompt_enabled",
                "sextoy_prompt_vibration_force"
            ]
        }

        self.setting_types = {
            "sextoy_general_vibration_force": PERCENTAGE,
            "sextoy_image_open_chance": PERCENTAGE,
            "sextoy_image_open_vibration_force": PERCENTAGE,
            "sextoy_image_open_vibration_length": FLOAT,
            "sextoy_image_close_chance": PERCENTAGE,
            "sextoy_image_close_vibration_force": PERCENTAGE,
            "sextoy_image_close_vibration_length": FLOAT,
            "sextoy_video_open_chance": PERCENTAGE,
            "sextoy_video_open_vibration_force": PERCENTAGE,
            "sextoy_video_open_vibration_length": FLOAT,
            "sextoy_video_close_chance": PERCENTAGE,
            "sextoy_video_close_vibration_force": PERCENTAGE,
            "sextoy_video_close_vibration_length": FLOAT,
            "sextoy_caption_chance": PERCENTAGE,
            "sextoy_caption_vibration_force": PERCENTAGE,
            "sextoy_caption_vibration_length": FLOAT,
            "sextoy_display_notification_chance": PERCENTAGE,
            "sextoy_display_notification_vibration_force": PERCENTAGE,
            "sextoy_display_notification_vibration_length": FLOAT,
            "sextoy_prompt_enabled": BOOLEAN,
            "sextoy_prompt_vibration_force": PERCENTAGE,
        }

        self.default_values = {
            "sextoy_general_vibration_force": 50,
            "sextoy_image_open_chance": 0,
            "sextoy_image_open_vibration_force": 50,
            "sextoy_image_open_vibration_length": 0.5,
            "sextoy_image_close_chance": 0,
            "sextoy_image_close_vibration_force": 50,
            "sextoy_image_close_vibration_length": 0.5,
            "sextoy_video_open_chance": 0,
            "sextoy_video_open_vibration_force": 50,
            "sextoy_video_open_vibration_length": 0.5,
            "sextoy_video_close_chance": 0,
            "sextoy_video_close_vibration_force": 50,
            "sextoy_video_close_vibration_length": 0.5,
            "sextoy_caption_chance": 0,
            "sextoy_caption_vibration_force": 50,
            "sextoy_caption_vibration_length": 0.5,
            "sextoy_display_notification_chance": 0,
            "sextoy_display_notification_vibration_force": 50,
            "sextoy_display_notification_vibration_length": 0.5,
            "sextoy_prompt_enabled": False,
            "sextoy_prompt_vibration_force": 50,
        }

        self.addr_var = StringVar(value=config["initfaceAddress"])

        sextoys_section = ConfigSection(self.viewPort, "Sextoys settings", SEXTOYS_TEXT)
        sextoys_section.pack()

        self.current_device_index = None

        self.connect_button = Button(sextoys_section, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(pady=5)

        # Listbox for all known devices
        self.devices_listbox = Listbox(sextoys_section, height=6)
        self.devices_listbox.pack(fill="x", padx=5, pady=5)

        for key, sextoy_config in config['sextoys'].items():
            if key not in self.vars.sextoys:
                device_vars = {
                    'sextoy_name': StringVar(value=sextoy_config.get('sextoy_name', f"Device {key}"))
                }
                for setting, setting_type in self.setting_types.items():
                    value = sextoy_config.get(setting, self.default_values[setting])
                    
                    if setting_type == PERCENTAGE:
                        device_vars[setting] = IntVar(value=value)
                    elif setting_type == BOOLEAN:
                        device_vars[setting] = BooleanVar(value=value)
                    elif setting_type == FLOAT:
                        device_vars[setting] = DoubleVar(value=value)
                
                self.vars.sextoys[key] = device_vars
            
            name = self.vars.sextoys[key]['sextoy_name'].get()
            self.devices_listbox.insert('end', name)
            self.known_devices.append(name)
            self.device_indices.append({"sextoy_index": key})
            
        # Bind selection event to display that device's settings
        self.devices_listbox.bind("<<ListboxSelect>>", self.on_device_select)

        initface_settings = ConfigSection(self.viewPort, "Initface settings", INITFACE_TEXT)
        initface_settings.pack()

        initface_frame = Frame(initface_settings)
        initface_frame.pack(fill="x", pady=5)

        initface_address = Entry(initface_settings, textvariable=vars.initface_address)
        initface_address.pack(fill="x", padx=5)

        self.addr_var.trace_add("write", lambda *args: setattr(vars, "initface_address", self.addr_var.get()))

        self.settings_frame = ConfigSection(self.viewPort, "Device Settings")
        self.settings_frame.pack()

    def toggle_connection(self):
        if not self.sextoy.connected:
            # Disable the button while we're trying to connect
            self.connect_button.config(state="disabled")

            # Read the latest address from settings
            raw_addr = self.sextoy._settings.initface_address
            addr = raw_addr.get() if hasattr(raw_addr, "get") else raw_addr

            # Kick off the async connect and grab the Future
            future = self.sextoy.connect()

            def on_connect_done(fut):
                try:
                    # Will raise here if connect() failed
                    fut.result()
                except Exception as e:
                    # Capture `e` in default arg so it's available later
                    self.connect_button.after(0, lambda e=e: [
                        self.connect_button.config(text="Connect", state="normal"),
                        messagebox.showerror(
                            "Connection Error",
                            f"Unable to connect to {addr}:\n{e}"
                        )
                    ])
                else:
                    # On success, switch button to "Disconnect" and start updating devices
                    self.connect_button.after(0, lambda: [
                        self.connect_button.config(text="Disconnect", state="normal"),
                        self.update_devices()
                    ])

            if future:
                future.add_done_callback(on_connect_done)

        else:
            # If already connected, just disconnect and reset the button
            self.sextoy.disconnect()
            self.connect_button.config(text="Connect")

    def update_devices(self):
        for device in self.sextoy.devices.values():
            idx = str(device.index)  # Всегда используем строковые индексы
            
            if idx not in self.vars.sextoys:
                name = getattr(device, "name", f"Device {idx}")
                
                # Создаем все переменные с значениями по умолчанию
                device_vars = {
                    "sextoy_name": StringVar(value=name)
                }
                
                for setting, setting_type in self.setting_types.items():
                    if setting_type == PERCENTAGE:
                        device_vars[setting] = IntVar(value=self.default_values[setting])
                    elif setting_type == BOOLEAN:
                        device_vars[setting] = BooleanVar(value=self.default_values[setting])
                    elif setting_type == FLOAT:
                        device_vars[setting] = DoubleVar(value=self.default_values[setting])
                
                self.vars.sextoys[idx] = device_vars
                
                # Добавляем в список
                self.devices_listbox.insert('end', name)
                self.known_devices.append(name)
                self.device_indices.append({"sextoy_index": idx})

        if self.sextoy.connected:
            self.after(1000, self.update_devices)

    def on_device_select(self, event):
        for w in self.settings_frame.winfo_children():
            w.destroy()

        sel = event.widget.curselection()
        if not sel:
            return
        
        listbox_idx = sel[0]
        
        # Get the real device index
        try:
            device_index = self.device_indices[listbox_idx]["sextoy_index"]
        except (IndexError, KeyError):
            return
        
        # Directly access the device settings dictionary with Tkinter variables
        device_settings = self.vars.sextoys[device_index]

        ConfigTitle(self.settings_frame, "Device Settings").pack()

        # Create UI elements for each setting
        for group_name, settings in self.setting_groups.items():
            group_frame = ConfigSection(self.settings_frame, group_name)
            group_frame.pack()
            row = ConfigRow(group_frame)
            row.pack()
            
            for setting in settings:
                var = device_settings[setting]
                setting_type = self.setting_types[setting]
                label = setting.replace('_', ' ').title()
                
                # Для каждой настройки создаем отдельный ConfigRow
                if setting_type == PERCENTAGE:
                    scale = ConfigScale(row, label=f"{label}", variable=var, from_=0, to=100)
                    scale.pack()
                
                elif setting_type == BOOLEAN:
                    cb = ConfigToggle(row, text=label, variable=var)
                    cb.pack()
                
                elif setting_type == FLOAT:
                    scale = ConfigFloatScale(row, variable=var, from_=0.0, to=3.0, label=f"{label} (sec):",
                                 resolution=0.1)
                    scale.pack()
        
        self.after(100, self.update_scrollregion)
            
    def update_scrollregion(self):
        """Обновляет область прокрутки после изменения контента"""
        self.update_idletasks()  # Форсируем обновление геометрии
        self.onFrameConfigure(None)  # Пересчитываем область прокрутки
        self.onCanvasConfigure()  # Перепроверяем необходимость скроллбара

    def checkAndReturnValue(key, index):
        if "sextoys" in config \
          and index in config["sextoys"] \
          and key in config["sextoys"][index]:
            return config["sextoys"][index][key]
        else:
            return 50  # default
        