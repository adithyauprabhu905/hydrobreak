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
    STRETCH = auto()


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

_STRETCH_MESSAGES = [
    ("Posture check!", "Sit up tall, roll your shoulders back and relax your neck."),
    ("20-20-20 Eye Break", "Look at an object 20 feet away for 20 seconds to rest your eyes."),
    ("Stand up & stretch", "Get up from your chair! A quick stretch boosts circulation and energy."),
    ("Wrist & hand shake", "Shake out your wrists and stretch your fingers to prevent strain."),
    ("Deep breath break", "Take three deep breaths. Inhale calm, exhale tension."),
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
        self._stretch_msg_idx = 0
        self._reset_clocks()

    def _reset_clocks(self) -> None:
        now = time.monotonic()
        settings = self._config.get()
        self._next_water = now + settings.water_interval_min * 60
        self._next_food = now + settings.food_interval_min * 60
        self._next_stretch = now + settings.stretch_interval_min * 60

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
            elif kind is ReminderKind.FOOD:
                self._next_food = now + minutes * 60
            elif kind is ReminderKind.STRETCH:
                self._next_stretch = now + minutes * 60

    def trigger_now(self, kind: ReminderKind) -> None:
        event = self._build_event(kind)
        self._on_due(event)
        settings = self._config.get()
        interval = 5
        if kind is ReminderKind.WATER:
            interval = settings.water_interval_min
        elif kind is ReminderKind.FOOD:
            interval = settings.food_interval_min
        elif kind is ReminderKind.STRETCH:
            interval = settings.stretch_interval_min
        self.snooze(kind, interval)

    def _build_event(self, kind: ReminderKind) -> ReminderEvent:
        if kind is ReminderKind.WATER:
            title, message = _WATER_MESSAGES[self._water_msg_idx % len(_WATER_MESSAGES)]
            self._water_msg_idx += 1
        elif kind is ReminderKind.FOOD:
            title, message = _FOOD_MESSAGES[self._food_msg_idx % len(_FOOD_MESSAGES)]
            self._food_msg_idx += 1
        else:
            title, message = _STRETCH_MESSAGES[self._stretch_msg_idx % len(_STRETCH_MESSAGES)]
            self._stretch_msg_idx += 1
        return ReminderEvent(kind=kind, title=title, message=message)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            time.sleep(1)
            if self._config.is_suppressed():
                continue

            settings = self._config.get()
            now = time.monotonic()
            fire_kinds = []

            with self._lock:
                if settings.water_enabled and now >= self._next_water:
                    self._next_water = now + settings.water_interval_min * 60
                    fire_kinds.append(ReminderKind.WATER)

                if settings.food_enabled and now >= self._next_food:
                    self._next_food = now + settings.food_interval_min * 60
                    fire_kinds.append(ReminderKind.FOOD)

                if settings.stretch_enabled and now >= self._next_stretch:
                    self._next_stretch = now + settings.stretch_interval_min * 60
                    fire_kinds.append(ReminderKind.STRETCH)

            for kind in fire_kinds:
                self._on_due(self._build_event(kind))

    def apply_interval_change(self) -> None:
        """Call after settings intervals change so new values take effect immediately
        without instantly firing a reminder."""
        self._reset_clocks()
