"""Settings window for adjusting reminder intervals and preferences."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from config import ConfigStore


class SettingsWindow:
    def __init__(self, root: tk.Tk, config: ConfigStore, on_saved: Callable[[], None]) -> None:
        self._root = root
        self._config = config
        self._on_saved = on_saved
        self._window: tk.Toplevel | None = None

    def open(self) -> None:
        if self._window is not None and self._window.winfo_exists():
            self._window.lift()
            self._window.focus_force()
            return

        settings = self._config.get()
        win = tk.Toplevel(self._root)
        self._window = win
        win.title("HydroBreak Settings")
        win.resizable(False, False)
        win.attributes("-topmost", True)

        pad = {"padx": 16, "pady": 8}
        frame = ttk.Frame(win)
        frame.pack(fill="both", expand=True)

        water_var = tk.IntVar(value=settings.water_interval_min)
        food_var = tk.IntVar(value=settings.food_interval_min)
        sound_var = tk.BooleanVar(value=settings.sound_enabled)
        timeout_var = tk.IntVar(value=settings.popup_timeout_sec)

        ttk.Label(frame, text="Water reminder every (minutes)").grid(row=0, column=0, sticky="w", **pad)
        ttk.Spinbox(frame, from_=5, to=480, textvariable=water_var, width=6).grid(row=0, column=1, **pad)

        ttk.Label(frame, text="Food reminder every (minutes)").grid(row=1, column=0, sticky="w", **pad)
        ttk.Spinbox(frame, from_=15, to=720, textvariable=food_var, width=6).grid(row=1, column=1, **pad)

        ttk.Label(frame, text="Reminder repeat every (seconds)").grid(row=2, column=0, sticky="w", **pad)
        ttk.Spinbox(frame, from_=5, to=120, textvariable=timeout_var, width=6).grid(row=2, column=1, **pad)

        ttk.Checkbutton(frame, text="Play sound", variable=sound_var).grid(
            row=3, column=0, columnspan=2, sticky="w", **pad)

        def save() -> None:
            self._config.update(
                water_interval_min=water_var.get(),
                food_interval_min=food_var.get(),
                popup_timeout_sec=timeout_var.get(),
                sound_enabled=sound_var.get(),
            )
            self._on_saved()
            win.destroy()

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(10, 14))
        ttk.Button(btn_frame, text="Save", command=save).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="left", padx=6)
