<#
.SYNOPSIS
    Installs HydroBreak to the current user's system without needing admin privileges.
#>

$ErrorActionPreference = "Stop"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "       HydroBreak Installer          " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceExe = Join-Path $scriptDir "dist\HydroBreak.exe"
$sourceIcon = Join-Path $scriptDir "assets\icon.ico"

# If the exe isn't built yet, build it first
if (-not (Test-Path $sourceExe)) {
    Write-Host "Executable not found. Building HydroBreak.exe first..." -ForegroundColor Yellow
    $buildBat = Join-Path $scriptDir "build_exe.bat"
    if (Test-Path $buildBat) {
        & cmd.exe /c $buildBat
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path $sourceExe)) {
            Write-Error "Build failed. Please check errors above."
            exit 1
        }
    } else {
        Write-Error "dist\HydroBreak.exe not found and build script missing."
        exit 1
    }
}

$installDir = Join-Path $env:LOCALAPPDATA "HydroBreak"
$destExe = Join-Path $installDir "HydroBreak.exe"
$destIcon = Join-Path $installDir "icon.ico"

# Create install folder
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

# Stop any running instances
Write-Host "Closing running instances (if any)..."
Get-Process -Name "HydroBreak" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500

# Copy executable and icon
Write-Host "Copying application files to $installDir..." -ForegroundColor Green
Copy-Item -Path $sourceExe -Destination $destExe -Force
if (Test-Path $sourceIcon) {
    Copy-Item -Path $sourceIcon -Destination $destIcon -Force
}

# Create Windows Shell COM Object for shortcuts
$wscript = New-Object -ComObject WScript.Shell

# 1. Desktop shortcut
$desktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$desktopShortcutPath = Join-Path $desktopPath "HydroBreak.lnk"
Write-Host "Creating Desktop shortcut: $desktopShortcutPath" -ForegroundColor Green
$shortcut = $wscript.CreateShortcut($desktopShortcutPath)
$shortcut.TargetPath = $destExe
$shortcut.WorkingDirectory = $installDir
$shortcut.Description = "HydroBreak - Water, Break & Health Reminder"
if (Test-Path $destIcon) {
    $shortcut.IconLocation = "$destIcon,0"
}
$shortcut.Save()

# 2. Start Menu shortcut
$programsPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Programs)
$startMenuShortcutPath = Join-Path $programsPath "HydroBreak.lnk"
Write-Host "Creating Start Menu shortcut: $startMenuShortcutPath" -ForegroundColor Green
$startShortcut = $wscript.CreateShortcut($startMenuShortcutPath)
$startShortcut.TargetPath = $destExe
$startShortcut.WorkingDirectory = $installDir
$startShortcut.Description = "HydroBreak - Water, Break & Health Reminder"
if (Test-Path $destIcon) {
    $startShortcut.IconLocation = "$destIcon,0"
}
$startShortcut.Save()

# 3. Add to Windows Startup (Registry)
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Set-ItemProperty -Path $regPath -Name "HydroBreak" -Value $destExe -Force
Write-Host "Registered in Windows Startup." -ForegroundColor Green

# 4. Launch app
Write-Host "`nInstallation successful! Launching HydroBreak..." -ForegroundColor Cyan
Start-Process -FilePath $destExe

Write-Host "HydroBreak is now running in your system tray (look for the water droplet icon)." -ForegroundColor Green
