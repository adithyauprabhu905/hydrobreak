"""Persisted configuration and daily stats for HydroBreak."""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from threading import Lock


def _config_dir() -> Path:
    base = os.environ.get("APPDATA") or os.environ.get("XDG_CONFIG_HOME") or str(Path.home())
    path = Path(base) / "HydroBreak"
    path.mkdir(parents=True, exist_ok=True)
    return path


CONFIG_PATH = _config_dir() / "config.json"


@dataclass
class Settings:
    # Intervals in minutes
    water_interval_min: int = 45
    food_interval_min: int = 180
    stretch_interval_min: int = 30

    # Feature toggles
    water_enabled: bool = True
    food_enabled: bool = True
    stretch_enabled: bool = True
    sound_enabled: bool = True
    paused: bool = False
    pause_until_epoch: float = 0.0
    run_at_startup: bool = False

    # Quiet hours (e.g. 22 = 10 PM to 8 = 8 AM)
    quiet_hours_enabled: bool = False
    quiet_hours_start: int = 22
    quiet_hours_end: int = 8

    # Daily goals and tracking
    water_daily_goal: int = 8
    water_today_count: int = 0
    stretch_today_count: int = 0
    last_logged_date: str = ""

    popup_timeout_sec: int = 20

    def clamp(self) -> None:
        self.water_interval_min = max(5, min(self.water_interval_min, 480))
        self.food_interval_min = max(15, min(self.food_interval_min, 720))
        self.stretch_interval_min = max(5, min(self.stretch_interval_min, 240))
        self.popup_timeout_sec = max(5, min(self.popup_timeout_sec, 120))
        self.water_daily_goal = max(1, min(self.water_daily_goal, 50))
        self.quiet_hours_start = max(0, min(self.quiet_hours_start, 23))
        self.quiet_hours_end = max(0, min(self.quiet_hours_end, 23))


class ConfigStore:
    """Thread-safe load/save wrapper around Settings, backed by a JSON file."""

    def __init__(self, path: Path = CONFIG_PATH) -> None:
        self._path = path
        self._lock = Lock()
        self._settings = self._load()
        self._check_date_rollover()

    def _load(self) -> Settings:
        if not self._path.exists():
            return Settings()
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            settings = Settings(**{k: v for k, v in data.items() if k in Settings.__annotations__})
            settings.clamp()
            return settings
        except (json.JSONDecodeError, OSError, TypeError):
            return Settings()

    def _check_date_rollover(self) -> None:
        today = date.today().isoformat()
        if self._settings.last_logged_date != today:
            self._settings.last_logged_date = today
            self._settings.water_today_count = 0
            self._settings.stretch_today_count = 0
            self._save()

    def get(self) -> Settings:
        with self._lock:
            self._check_date_rollover()
            return Settings(**asdict(self._settings))

    def update(self, **changes) -> Settings:
        with self._lock:
            self._check_date_rollover()
            for key, value in changes.items():
                if hasattr(self._settings, key):
                    setattr(self._settings, key, value)
            self._settings.clamp()
            self._save()
            return Settings(**asdict(self._settings))

    def log_water(self, amount: int = 1) -> tuple[int, int]:
        """Increments today's water count and returns (today_count, daily_goal)."""
        with self._lock:
            self._check_date_rollover()
            self._settings.water_today_count = max(0, self._settings.water_today_count + amount)
            self._save()
            return self._settings.water_today_count, self._settings.water_daily_goal

    def log_stretch(self, amount: int = 1) -> int:
        """Increments today's stretch count and returns today's total."""
        with self._lock:
            self._check_date_rollover()
            self._settings.stretch_today_count = max(0, self._settings.stretch_today_count + amount)
            self._save()
            return self._settings.stretch_today_count

    def pause_for(self, minutes: int) -> None:
        """Pauses reminders until a given number of minutes from now."""
        with self._lock:
            self._settings.pause_until_epoch = time.time() + minutes * 60
            self._settings.paused = False
            self._save()

    def resume(self) -> None:
        """Resumes active reminders immediately."""
        with self._lock:
            self._settings.paused = False
            self._settings.pause_until_epoch = 0.0
            self._save()

    def is_suppressed(self) -> bool:
        """Returns True if reminders should not fire (paused, temporary mute, or quiet hours)."""
        with self._lock:
            if self._settings.paused:
                return True
            if self._settings.pause_until_epoch > time.time():
                return True
            if self._settings.quiet_hours_enabled:
                curr_hour = datetime.now().hour
                start = self._settings.quiet_hours_start
                end = self._settings.quiet_hours_end
                if start <= end:
                    if start <= curr_hour < end:
                        return True
                else:  # Overnight range, e.g. 22:00 to 08:00
                    if curr_hour >= start or curr_hour < end:
                        return True
            return False

    def _save(self) -> None:
        tmp_path = self._path.with_suffix(".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                json.dump(asdict(self._settings), fh, indent=2)
            os.replace(tmp_path, self._path)
        except OSError:
            pass
