@echo off
setlocal
echo Installing HydroBreak...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
if errorlevel 1 (
    echo.
    echo Installation encountered an error.
    pause
    exit /b 1
)
echo.
pause
