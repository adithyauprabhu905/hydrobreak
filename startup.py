"""Utilities for managing Windows startup registration."""

from __future__ import annotations

import os
import sys
import winreg
from pathlib import Path


def set_run_at_startup(enabled: bool) -> None:
    """Adds or removes the application from the Windows startup registry."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "HydroBreak"

    # When running as a PyInstaller bundle, sys.executable is the path to the .exe.
    # When running as a script, it's the path to the python interpreter.
    # For startup, we only really want to register the .exe.
    app_path = str(Path(sys.executable).resolve())

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
        )
        if enabled:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
        else:
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as exc:
        # In a real app we might log this or show an error, but for a simple utility
        # we'll just fail silently to avoid crashing the app.
        print(f"Failed to update startup registry: {exc}")


def is_registered_at_startup() -> bool:
    """Checks if the application is currently registered in the Windows startup registry."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "HydroBreak"

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        try:
            value, _ = winreg.QueryValueEx(key, app_name)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False
