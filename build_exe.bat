@echo off
setlocal

echo === HydroBreak build ===

python -m pip install --upgrade pip
if errorlevel 1 goto :error

pip install -r requirements.txt
if errorlevel 1 goto :error

python icon.py
if errorlevel 1 goto :error

pyinstaller --noconfirm --onefile --windowed --name HydroBreak ^
  --icon assets\icon.ico ^
  --add-data "assets;assets" ^
  app.py
if errorlevel 1 goto :error

echo.
echo Build complete: dist\HydroBreak.exe
goto :eof

:error
echo.
echo Build failed. See errors above.
exit /b 1
