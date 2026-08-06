@echo off
setlocal

if exist "venv\Scripts\python.exe" (
  "venv\Scripts\python.exe" app.py
) else (
  echo Virtual environment not found. Run: python -m venv venv
  exit /b 1
)