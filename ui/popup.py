"""Cute toast-style popup shown when a reminder fires."""

from __future__ import annotations

import sys
import tkinter as tk
from typing import Callable, Optional

from reminder import ReminderEvent, ReminderKind

_WATER_BG = "#eaf6ff"
_WATER_ACCENT = "#3aa0e8"
_FOOD_BG = "#fff4e6"
_FOOD_ACCENT = "#f2994a"

_WATER_EMOJI = "\U0001F4A7"   # droplet
_FOOD_EMOJI = "\U0001F34E"    # apple


def _beep() -> None:
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        else:
            print("\a", end="", flush=True)
    except Exception:
        pass


class ReminderPopup:
    """A small frameless, always-on-top, fading toast window.

    One popup instance is reused; calling show() while a previous popup is
    open simply replaces its content and resets the timers, avoiding a pile
    of stacked windows if reminders overlap.
    """

    _WIDTH = 360
    _HEIGHT = 190
    _MARGIN = 24

    def __init__(self, root: tk.Tk, timeout_sec: int, sound_enabled: bool,
                 on_snooze: Callable[[ReminderKind], None],
                 on_done: Callable[[ReminderKind], None]) -> None:
        self._root = root
        self._timeout_sec = timeout_sec
        self._sound_enabled = sound_enabled
        self._on_snooze = on_snooze
        self._on_done = on_done
        self._window: Optional[tk.Toplevel] = None
        self._after_ids: list[str] = []
        self._current_kind: Optional[ReminderKind] = None
        self._task_done_var: Optional[tk.BooleanVar] = None

    def set_defaults(self, timeout_sec: int, sound_enabled: bool) -> None:
        self._timeout_sec = timeout_sec
        self._sound_enabled = sound_enabled

    def show(self, event: ReminderEvent) -> None:
        self._root.after(0, self._show_on_main_thread, event)

    def _cancel_pending(self) -> None:
        for after_id in self._after_ids:
            try:
                self._root.after_cancel(after_id)
            except Exception:
                pass
        self._after_ids.clear()

    def _show_on_main_thread(self, event: ReminderEvent) -> None:
        self._cancel_pending()
        if self._window is not None:
            self._window.destroy()

        is_water = event.kind is ReminderKind.WATER
        bg = _WATER_BG if is_water else _FOOD_BG
        accent = _WATER_ACCENT if is_water else _FOOD_ACCENT
        emoji = _WATER_EMOJI if is_water else _FOOD_EMOJI
        self._current_kind = event.kind

        win = tk.Toplevel(self._root)
        self._window = win
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        try:
            win.attributes("-alpha", 0.0)
        except tk.TclError:
            pass
        win.configure(bg=accent)

        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = screen_w - self._WIDTH - self._MARGIN
        y = screen_h - self._HEIGHT - self._MARGIN - 50
        win.geometry(f"{self._WIDTH}x{self._HEIGHT}+{x}+{y}")

        card = tk.Frame(win, bg=bg, highlightbackground=accent, highlightthickness=2)
        card.place(x=2, y=2, width=self._WIDTH - 4, height=self._HEIGHT - 4)

        header = tk.Frame(card, bg=bg)
        header.pack(fill="x", padx=14, pady=(12, 0))
        tk.Label(header, text=emoji, font=("Segoe UI Emoji", 22), bg=bg).pack(side="left")
        tk.Label(header, text=event.title, font=("Segoe UI", 13, "bold"), bg=bg, fg=accent).pack(
            side="left", padx=(8, 0))

        tk.Label(card, text=event.message, font=("Segoe UI", 10), bg=bg, fg="#333333",
                 wraplength=self._WIDTH - 40, justify="left").pack(
            fill="x", padx=14, pady=(8, 10))

        action_text = "I drank water" if is_water else "I ate food"
        self._task_done_var = tk.BooleanVar(value=False)

        btn_row = tk.Frame(card, bg=bg)
        btn_row.pack(fill="x", padx=14, pady=(0, 10))

        def snooze_clicked() -> None:
            self._close()
            if self._current_kind is not None:
                self._on_snooze(self._current_kind)

        def done_clicked() -> None:
            if self._task_done_var is None or not self._task_done_var.get():
                return
            self._close()
            if self._current_kind is not None:
                self._on_done(self._current_kind)

        def sync_done_state() -> None:
            if self._task_done_var is None:
                return
            state = "normal" if self._task_done_var.get() else "disabled"
            done_btn.configure(state=state)

        tk.Checkbutton(
            card,
            text=f"{action_text} (required to close)",
            variable=self._task_done_var,
            command=sync_done_state,
            bg=bg,
            fg="#222222",
            activebackground=bg,
            highlightthickness=0,
            selectcolor=bg,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=14, pady=(0, 8))

        tk.Button(btn_row, text="Snooze 5 min", command=snooze_clicked, bg=bg, fg=accent,
                  activebackground=bg, relief="flat", font=("Segoe UI", 9), cursor="hand2").pack(
            side="right", padx=(6, 0))
        done_btn = tk.Button(btn_row, text="Done", command=done_clicked, bg=accent, fg="white",
                             activebackground=accent, relief="flat", font=("Segoe UI", 9, "bold"),
                             cursor="hand2", state="disabled")
        done_btn.pack(side="right")

        if self._sound_enabled:
            _beep()

        win.deiconify()
        win.lift()
        win.focus_force()
        self._fade_in(win, 0.0)
        nudge_id = self._root.after(self._timeout_sec * 1000, self._nudge)
        self._after_ids.append(nudge_id)

    def _fade_in(self, win: tk.Toplevel, alpha: float) -> None:
        if not win.winfo_exists():
            return
        alpha = min(alpha + 0.12, 0.97)
        try:
            win.attributes("-alpha", alpha)
        except tk.TclError:
            return
        if alpha < 0.97:
            after_id = self._root.after(15, lambda: self._fade_in(win, alpha))
            self._after_ids.append(after_id)

    def _close(self) -> None:
        self._cancel_pending()
        if self._window is not None and self._window.winfo_exists():
            self._window.destroy()
        self._window = None
        self._current_kind = None
        self._task_done_var = None

    def _nudge(self) -> None:
        if self._window is None or not self._window.winfo_exists():
            return
        if self._sound_enabled:
            _beep()
        self._window.lift()
        self._window.focus_force()
        next_nudge_id = self._root.after(self._timeout_sec * 1000, self._nudge)
        self._after_ids.append(next_nudge_id)
