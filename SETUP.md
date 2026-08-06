# Setup Guide (From Scratch)

This walks through setting up HydroBreak on a fresh machine, including the
virtual environment, from zero.

## 1. Prerequisites

- Python 3.10 or newer installed. Check with:
  ```bash
  python --version
  ```
  On Windows, download it from https://python.org/downloads if missing, and
  during install, tick "Add python.exe to PATH".

- Tkinter must also work in that Python install. If `python -m tkinter` fails
  with an `init.tcl` error, reinstall Python from python.org and make sure the
  Tcl/Tk support is included.

- Git (optional, only needed if cloning instead of downloading the zip).

## 2. Get the project

Either unzip the `hydrobreak.zip` you were given, or clone your GitHub repo:

```bash
git clone https://github.com/<your-username>/hydrobreak.git
cd hydrobreak
```

## 3. Create a virtual environment

A virtual environment keeps this project's dependencies separate from every
other Python project on your machine.

**Windows (Command Prompt):**
```bat
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```
If that command does not change your prompt to start with `(venv)`, run the
app with the virtual environment's interpreter instead of `python`:
```bat
venv\Scripts\python.exe app.py
```
In PowerShell, the equivalent is:
```powershell
& .\venv\Scripts\python.exe .\app.py
```
If PowerShell blocks the script, run this once first:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Once activated, your terminal prompt will show `(venv)` at the start of the
line. Every `pip install` and `python` command from here on runs inside this
isolated environment.

## 4. Install dependencies

With the virtual environment active:

```bash
pip install -r requirements.txt
```

This installs `pystray`, `Pillow`, and `pyinstaller`.

## 5. Run the app

```bash
python app.py
```

If your shell still points at the system Python, use:

```bat
venv\Scripts\python.exe app.py
```

For PowerShell specifically:

```powershell
& .\venv\Scripts\python.exe .\app.py
```

On Windows you can also double-click `run_app.bat`.

Nothing opens as a window — look for the droplet icon in your system tray
(bottom-right on Windows, top-right menu bar on macOS). Right-click it:

- **Open Settings** — change water/food intervals, popup duration, sound
- **Water reminder now / Food reminder now** — trigger a popup immediately, useful for testing
- **Pause reminders** — stop popups temporarily without closing the app
- **Quit** — closes it completely

## 6. Build the standalone .exe (Windows only)

Still inside the activated virtual environment:

```bat
build_exe.bat
```

This regenerates the icon and runs PyInstaller, producing
`dist\HydroBreak.exe` — a single file with no Python installation required
to run it. Copy that file anywhere, or double-click it to add to Startup
(see below).

## 7. Optional: run it automatically at login (Windows)

1. Press `Win + R`, type `shell:startup`, press Enter.
2. Copy `HydroBreak.exe` (or a shortcut to it) into the folder that opens.
3. It will now launch quietly in the tray every time you log in.

## 8. Deactivating the virtual environment

When you're done working on the project:

```bash
deactivate
```

## 9. Publishing to GitHub

```bash
git init
git add .
git commit -m "Initial commit: HydroBreak"
git branch -M main
git remote add origin https://github.com/<your-username>/hydrobreak.git
git push -u origin main
```

The `.gitignore` already excludes `venv/`, `__pycache__/`, `build/`, `dist/`,
and the generated `icon.ico`, so your repo stays clean — only source files
get committed. Tag a release (`git tag v1.0.0 && git push --tags`) to have
GitHub Actions build and attach the `.exe` automatically.
