# HydroBreak

A tiny, cute desktop buddy that reminds programmers (and everyone else glued
to a screen) to drink water and eat food. Lives in the system tray, pops up
a friendly toast when it's time, and gets out of your way otherwise.

## Features

- Configurable water and food reminder intervals
- Cute animated popup (fade-in, droplet/apple mascot, snooze or task-confirm)
- System tray icon with pause/resume, "remind me now", and settings
- Settings persisted to disk between runs
- Zero external image assets - the icon is generated in code with Pillow
- Packages into a single-file Windows `.exe` with PyInstaller

## Running from source

```bash
pip install -r requirements.txt
python app.py
```

The app has no main window - look for the droplet icon in your system tray.
Right-click it for options.

If `python app.py` opens the wrong interpreter, run it from the virtual
environment directly:

```bat
venv\Scripts\python.exe app.py
```

You can also double-click `run_app.bat` on Windows.

If you use PowerShell, run:

```powershell
& .\venv\Scripts\python.exe .\app.py
```

or double-click `run_app.ps1` from PowerShell.

## Building the .exe (Windows)

PyInstaller cannot cross-compile, so the `.exe` must be built on Windows,
either locally or via CI.

**Locally, on Windows:**

```bat
build_exe.bat
```

This installs dependencies, generates `assets/icon.ico`, and produces
`dist/HydroBreak.exe`.

**Via GitHub Actions:**

Push a tag like `v1.0.0`, or trigger the "Build Windows executable" workflow
manually from the Actions tab. It builds on a `windows-latest` runner and
attaches `HydroBreak.exe` to the run's artifacts (and to the GitHub Release
if triggered by a tag).

## Project layout

```
app.py            entry point, wires everything together
config.py          persisted settings (JSON, in %APPDATA%/HydroBreak)
reminder.py         background scheduler that fires water/food events
icon.py             procedural icon generation (Pillow)
tray.py             system tray icon and menu (pystray)
ui/popup.py         the reminder toast window (tkinter)
ui/settings.py       settings dialog (tkinter)
build_exe.bat        Windows build script (PyInstaller)
.github/workflows/build.yml   CI build for the .exe
```

## Configuration

All settings are editable from the tray menu's "Open Settings":

| Setting | Default |
|---|---|
| Water reminder interval | 45 minutes |
| Food reminder interval | 3 hours |
| Reminder repeat interval | 20 seconds |
| Sound on reminder | on |

Settings are stored at `%APPDATA%\HydroBreak\config.json` on Windows.

## License

MIT - do whatever you like with it.
