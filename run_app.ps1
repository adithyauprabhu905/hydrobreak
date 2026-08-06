$ErrorActionPreference = 'Stop'

$pythonExe = Join-Path $PSScriptRoot 'venv\Scripts\python.exe'
$appPath = Join-Path $PSScriptRoot 'app.py'

if (-not (Test-Path $pythonExe)) {
    Write-Error 'Virtual environment not found. Run: python -m venv venv'
    exit 1
}

& $pythonExe $appPath