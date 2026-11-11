"""System tray icon and menu, running on its own thread via pystray."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Callable

import pystray

from config import ConfigStore
from icon import build_tray_image
from reminder import ReminderKind


class TrayController:
    def __init__(
        self,
        config: ConfigStore,
        on_open_settings: Callable[[], None],
        on_trigger: Callable[[ReminderKind], None],
        on_quit: Callable[[], None],
    ) -> None:
        self._config = config
        self._on_open_settings = on_open_settings
        self._on_trigger = on_trigger
        self._on_quit = on_quit
        self._icon: pystray.Icon | None = None

    def _toggle_pause(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        current = self._config.get()
        if current.paused or current.pause_until_epoch > time.time():
            self._config.resume()
        else:
            self._config.update(paused=True)
        icon.update_menu()

    def _is_paused(self, item: pystray.MenuItem) -> bool:
        return self._config.is_suppressed()

    def _get_pause_label(self, item: pystray.MenuItem) -> str:
        s = self._config.get()
        if s.paused:
            return "Resume Reminders"
        if s.pause_until_epoch > time.time():
            until = datetime.fromtimestamp(s.pause_until_epoch).strftime("%H:%M")
            return f"Paused until {until} (Resume now)"
        return "Pause Reminders"

    def _get_water_stats(self, item: pystray.MenuItem) -> str:
        s = self._config.get()
        return f"Hydration: {s.water_today_count}/{s.water_daily_goal} glasses"

    def _get_stretch_stats(self, item: pystray.MenuItem) -> str:
        s = self._config.get()
        return f"Daily breaks: {s.stretch_today_count} taken"

    def _log_water(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._config.log_water(1)
        icon.update_menu()

    def _log_stretch(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._config.log_stretch(1)
        icon.update_menu()

    def _pause_for(self, minutes: int) -> Callable:
        def callback(icon: pystray.Icon, item: pystray.MenuItem):
            self._config.pause_for(minutes)
            icon.update_menu()
        return callback

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(self._get_water_stats, lambda i, m: None, enabled=False),
            pystray.MenuItem(self._get_stretch_stats, lambda i, m: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("\U0001F4A7 Log a glass of water", self._log_water),
            pystray.MenuItem("\U0001F9D8 Log a break/stretch", self._log_stretch),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Settings", lambda icon, item: self._on_open_settings()),
            pystray.MenuItem("Trigger Reminders", pystray.Menu(
                pystray.MenuItem("Water Now", lambda i, m: self._on_trigger(ReminderKind.WATER)),
                pystray.MenuItem("Food Now", lambda i, m: self._on_trigger(ReminderKind.FOOD)),
                pystray.MenuItem("Stretch Now", lambda i, m: self._on_trigger(ReminderKind.STRETCH)),
            )),
            pystray.MenuItem(self._get_pause_label, self._toggle_pause),
            pystray.MenuItem("Pause for...", pystray.Menu(
                pystray.MenuItem("30 minutes", self._pause_for(30)),
                pystray.MenuItem("1 hour", self._pause_for(60)),
                pystray.MenuItem("2 hours", self._pause_for(120)),
                pystray.MenuItem("Until tomorrow", self._pause_for(1440)),
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda icon, item: self._quit(icon)),
        )

    def _quit(self, icon: pystray.Icon) -> None:
        icon.stop()
        self._on_quit()

    def _on_ready(self, icon: pystray.Icon) -> None:
        try:
            icon.visible = True
            icon.notify("HydroBreak is running", "Look for the droplet icon in the system tray.")
        except Exception:
            pass

    def start(self) -> None:
        image = build_tray_image(64)
        self._icon = pystray.Icon("HydroBreak", image, "HydroBreak", menu=self._build_menu())
        self._icon.run_detached(setup=self._on_ready)

    def stop(self) -> None:
        if self._icon is not None:
            try:
                self._icon.stop()
            except Exception:
                pass

    def update_menu(self) -> None:
        """Force-refreshes the tray menu to show updated stats."""
        if self._icon is not None:
            self._icon.update_menu()
