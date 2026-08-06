"""Persisted configuration for HydroBreak."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
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
    water_interval_min: int = 45
    food_interval_min: int = 180
    sound_enabled: bool = True
    paused: bool = False
    popup_timeout_sec: int = 20

    def clamp(self) -> None:
        self.water_interval_min = max(5, min(self.water_interval_min, 480))
        self.food_interval_min = max(15, min(self.food_interval_min, 720))
        self.popup_timeout_sec = max(5, min(self.popup_timeout_sec, 120))


class ConfigStore:
    """Thread-safe load/save wrapper around Settings, backed by a JSON file."""

    def __init__(self, path: Path = CONFIG_PATH) -> None:
        self._path = path
        self._lock = Lock()
        self._settings = self._load()

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

    def get(self) -> Settings:
        with self._lock:
            return Settings(**asdict(self._settings))

    def update(self, **changes) -> Settings:
        with self._lock:
            for key, value in changes.items():
                if hasattr(self._settings, key):
                    setattr(self._settings, key, value)
            self._settings.clamp()
            self._save()
            return Settings(**asdict(self._settings))

    def _save(self) -> None:
        tmp_path = self._path.with_suffix(".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as fh:
                json.dump(asdict(self._settings), fh, indent=2)
            os.replace(tmp_path, self._path)
        except OSError:
            pass
