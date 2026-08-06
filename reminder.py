"""Background scheduling engine for reminders."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Optional

from config import ConfigStore


class ReminderKind(Enum):
    WATER = auto()
    FOOD = auto()


@dataclass
class ReminderEvent:
    kind: ReminderKind
    title: str
    message: str


_WATER_MESSAGES = [
    ("Water break!", "Take a sip of water, your brain will thank you."),
    ("Hydration check", "When did you last drink water? Now is a good time."),
    ("Splash o'clock", "A glass of water keeps the bugs away. Probably."),
]

_FOOD_MESSAGES = [
    ("Snack time", "Your code can wait a minute, your stomach can't."),
    ("Fuel check", "Have you eaten recently? Grab a bite."),
    ("Meal reminder", "Even compilers need fuel. So do you."),
]


class ReminderEngine:
    """Runs a background thread that ticks once per second and fires due reminders."""

    def __init__(self, config: ConfigStore, on_due: Callable[[ReminderEvent], None]) -> None:
        self._config = config
        self._on_due = on_due
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._water_msg_idx = 0
        self._food_msg_idx = 0
        self._reset_clocks()

    def _reset_clocks(self) -> None:
        now = time.monotonic()
        self._next_water = now + self._config.get().water_interval_min * 60
        self._next_food = now + self._config.get().food_interval_min * 60

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="ReminderEngine", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def snooze(self, kind: ReminderKind, minutes: int = 5) -> None:
        with self._lock:
            now = time.monotonic()
            if kind is ReminderKind.WATER:
                self._next_water = now + minutes * 60
            else:
                self._next_food = now + minutes * 60

    def trigger_now(self, kind: ReminderKind) -> None:
        event = self._build_event(kind)
        self._on_due(event)
        self.snooze(kind, self._config.get().water_interval_min if kind is ReminderKind.WATER
                    else self._config.get().food_interval_min)

    def _build_event(self, kind: ReminderKind) -> ReminderEvent:
        if kind is ReminderKind.WATER:
            title, message = _WATER_MESSAGES[self._water_msg_idx % len(_WATER_MESSAGES)]
            self._water_msg_idx += 1
        else:
            title, message = _FOOD_MESSAGES[self._food_msg_idx % len(_FOOD_MESSAGES)]
            self._food_msg_idx += 1
        return ReminderEvent(kind=kind, title=title, message=message)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            time.sleep(1)
            settings = self._config.get()
            if settings.paused:
                continue
            now = time.monotonic()
            with self._lock:
                if now >= self._next_water:
                    self._next_water = now + settings.water_interval_min * 60
                    fire_water = True
                else:
                    fire_water = False
                if now >= self._next_food:
                    self._next_food = now + settings.food_interval_min * 60
                    fire_food = True
                else:
                    fire_food = False
            if fire_water:
                self._on_due(self._build_event(ReminderKind.WATER))
            if fire_food:
                self._on_due(self._build_event(ReminderKind.FOOD))

    def apply_interval_change(self) -> None:
        """Call after settings intervals change so new values take effect immediately
        without instantly firing a reminder."""
        self._reset_clocks()
