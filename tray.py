"""System tray icon and menu, running on its own thread via pystray."""

from __future__ import annotations

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
        self._config.update(paused=not current.paused)
        icon.update_menu()

    def _is_paused(self, item: pystray.MenuItem) -> bool:
        return self._config.get().paused

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("Open Settings", lambda icon, item: self._on_open_settings()),
            pystray.MenuItem("Water reminder now", lambda icon, item: self._on_trigger(ReminderKind.WATER)),
            pystray.MenuItem("Food reminder now", lambda icon, item: self._on_trigger(ReminderKind.FOOD)),
            pystray.MenuItem("Pause reminders", self._toggle_pause, checked=self._is_paused),
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
