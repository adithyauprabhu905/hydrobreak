"""Settings window for adjusting reminder intervals, goals, and preferences."""

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

        pad = {"padx": 12, "pady": 6}

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Reminders
        tab_reminders = ttk.Frame(notebook)
        notebook.add(tab_reminders, text="Reminders")

        water_en_var = tk.BooleanVar(value=settings.water_enabled)
        water_var = tk.IntVar(value=settings.water_interval_min)

        food_en_var = tk.BooleanVar(value=settings.food_enabled)
        food_var = tk.IntVar(value=settings.food_interval_min)

        stretch_en_var = tk.BooleanVar(value=settings.stretch_enabled)
        stretch_var = tk.IntVar(value=settings.stretch_interval_min)

        timeout_var = tk.IntVar(value=settings.popup_timeout_sec)

        # Water row
        ttk.Checkbutton(tab_reminders, text="Water reminder every", variable=water_en_var).grid(
            row=0, column=0, sticky="w", **pad
        )
        row0_f = ttk.Frame(tab_reminders)
        row0_f.grid(row=0, column=1, sticky="w", **pad)
        ttk.Spinbox(row0_f, from_=5, to=480, textvariable=water_var, width=5).pack(side="left")
        ttk.Label(row0_f, text=" min").pack(side="left")

        # Food row
        ttk.Checkbutton(tab_reminders, text="Food/meal reminder every", variable=food_en_var).grid(
            row=1, column=0, sticky="w", **pad
        )
        row1_f = ttk.Frame(tab_reminders)
        row1_f.grid(row=1, column=1, sticky="w", **pad)
        ttk.Spinbox(row1_f, from_=15, to=720, textvariable=food_var, width=5).pack(side="left")
        ttk.Label(row1_f, text=" min").pack(side="left")

        # Stretch row
        ttk.Checkbutton(tab_reminders, text="Stretch / Eye break every", variable=stretch_en_var).grid(
            row=2, column=0, sticky="w", **pad
        )
        row2_f = ttk.Frame(tab_reminders)
        row2_f.grid(row=2, column=1, sticky="w", **pad)
        ttk.Spinbox(row2_f, from_=5, to=240, textvariable=stretch_var, width=5).pack(side="left")
        ttk.Label(row2_f, text=" min").pack(side="left")

        # Repeat nudge row
        ttk.Label(tab_reminders, text="Nudge repeat frequency").grid(row=3, column=0, sticky="w", **pad)
        row3_f = ttk.Frame(tab_reminders)
        row3_f.grid(row=3, column=1, sticky="w", **pad)
        ttk.Spinbox(row3_f, from_=5, to=120, textvariable=timeout_var, width=5).pack(side="left")
        ttk.Label(row3_f, text=" sec").pack(side="left")

        # Tab 2: Goals & Schedule
        tab_goals = ttk.Frame(notebook)
        notebook.add(tab_goals, text="Goals & Quiet Hours")

        goal_var = tk.IntVar(value=settings.water_daily_goal)
        quiet_en_var = tk.BooleanVar(value=settings.quiet_hours_enabled)
        quiet_start_var = tk.IntVar(value=settings.quiet_hours_start)
        quiet_end_var = tk.IntVar(value=settings.quiet_hours_end)

        ttk.Label(tab_goals, text="Daily water goal").grid(row=0, column=0, sticky="w", **pad)
        row_goal = ttk.Frame(tab_goals)
        row_goal.grid(row=0, column=1, sticky="w", **pad)
        ttk.Spinbox(row_goal, from_=1, to=30, textvariable=goal_var, width=5).pack(side="left")
        ttk.Label(row_goal, text=" glasses").pack(side="left")

        ttk.Separator(tab_goals, orient="horizontal").grid(row=1, column=0, columnspan=2, sticky="ew", pady=6)

        ttk.Checkbutton(tab_goals, text="Enable Quiet Hours", variable=quiet_en_var).grid(
            row=2, column=0, columnspan=2, sticky="w", **pad
        )

        ttk.Label(tab_goals, text="Quiet from (hour 0-23):").grid(row=3, column=0, sticky="w", **pad)
        ttk.Spinbox(tab_goals, from_=0, to=23, textvariable=quiet_start_var, width=5).grid(
            row=3, column=1, sticky="w", **pad
        )

        ttk.Label(tab_goals, text="Quiet until (hour 0-23):").grid(row=4, column=0, sticky="w", **pad)
        ttk.Spinbox(tab_goals, from_=0, to=23, textvariable=quiet_end_var, width=5).grid(
            row=4, column=1, sticky="w", **pad
        )

        # Tab 3: System
        tab_sys = ttk.Frame(notebook)
        notebook.add(tab_sys, text="System")

        sound_var = tk.BooleanVar(value=settings.sound_enabled)
        startup_var = tk.BooleanVar(value=settings.run_at_startup)

        ttk.Checkbutton(tab_sys, text="Play alert sound on reminder", variable=sound_var).pack(
            anchor="w", **pad
        )
        ttk.Checkbutton(
            tab_sys, text="Start automatically on Windows startup", variable=startup_var
        ).pack(anchor="w", **pad)

        def save() -> None:
            self._config.update(
                water_enabled=water_en_var.get(),
                water_interval_min=water_var.get(),
                food_enabled=food_en_var.get(),
                food_interval_min=food_var.get(),
                stretch_enabled=stretch_en_var.get(),
                stretch_interval_min=stretch_var.get(),
                popup_timeout_sec=timeout_var.get(),
                water_daily_goal=goal_var.get(),
                quiet_hours_enabled=quiet_en_var.get(),
                quiet_hours_start=quiet_start_var.get(),
                quiet_hours_end=quiet_end_var.get(),
                sound_enabled=sound_var.get(),
                run_at_startup=startup_var.get(),
            )
            self._on_saved()
            win.destroy()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(side="bottom", fill="x", pady=(0, 10), padx=10)
        ttk.Button(btn_frame, text="Save Settings", command=save).pack(side="right", padx=6)
        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="right", padx=6)
