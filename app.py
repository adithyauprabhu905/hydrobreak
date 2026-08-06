"""HydroBreak - a cute desktop reminder to drink water and eat food.

Entry point: run `python app.py` during development, or build a standalone
.exe with `build_exe.bat` (Windows) using PyInstaller.
"""

from __future__ import annotations

import sys
import tkinter as tk

from config import ConfigStore
from reminder import ReminderEngine, ReminderEvent, ReminderKind
from tray import TrayController
from ui.popup import ReminderPopup
from ui.settings import SettingsWindow


class HydroBreakApp:
    def __init__(self) -> None:
        self._root = self._create_root()
        self._root.withdraw()  # No main window; this is a tray-resident app.

        self._config = ConfigStore()

        self._popup = ReminderPopup(
            root=self._root,
            timeout_sec=self._config.get().popup_timeout_sec,
            sound_enabled=self._config.get().sound_enabled,
            on_snooze=self._handle_snooze,
            on_done=self._handle_done,
        )

        self._engine = ReminderEngine(config=self._config, on_due=self._handle_due)

        self._settings_window = SettingsWindow(
            root=self._root, config=self._config, on_saved=self._handle_settings_saved
        )

        self._tray = TrayController(
            config=self._config,
            on_open_settings=self._open_settings,
            on_trigger=self._trigger_now,
            on_quit=self._quit,
        )

    @staticmethod
    def _create_root() -> tk.Tk:
        try:
            return tk.Tk()
        except tk.TclError as exc:
            raise RuntimeError(
                "HydroBreak could not start because Tk/Tcl is missing or broken in this Python installation. "
                "Reinstall Python from python.org and ensure the Tcl/Tk option is included, then try again."
            ) from exc

    def _handle_due(self, event: ReminderEvent) -> None:
        self._popup.show(event)

    def _handle_snooze(self, kind: ReminderKind) -> None:
        self._engine.snooze(kind, minutes=5)

    def _handle_done(self, kind: ReminderKind) -> None:
        pass  # Interval already advanced by the engine when the event fired.

    def _open_settings(self) -> None:
        self._root.after(0, self._settings_window.open)

    def _handle_settings_saved(self) -> None:
        settings = self._config.get()
        self._popup.set_defaults(settings.popup_timeout_sec, settings.sound_enabled)
        self._engine.apply_interval_change()

    def _trigger_now(self, kind: ReminderKind) -> None:
        self._root.after(0, lambda: self._engine.trigger_now(kind))

    def _quit(self) -> None:
        self._engine.stop()
        self._root.after(0, self._root.quit)

    def run(self) -> None:
        self._engine.start()
        self._tray.start()
        print(
            "HydroBreak started. Look for the droplet icon in the system tray or hidden icons.",
            flush=True,
        )
        try:
            self._root.mainloop()
        finally:
            self._engine.stop()
            self._tray.stop()


def main() -> int:
    try:
        app = HydroBreakApp()
        app.run()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
