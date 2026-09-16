@echo off
:: ============================================================================
:: Agy Helper — 1-Click Setup and Application Launcher
:: 1. Installs the code signing certificate into Windows Trusted stores.
:: 2. Creates a Desktop and Start Menu shortcut for easy access.
:: 3. Launches Agy Helper smoothly without security warnings.
:: ============================================================================
setlocal enableextensions enabledelayedexpansion
title Agy Helper Setup & Launcher

:: Check for Administrative privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges to configure Agy Helper...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb runAs"
    exit /b
)

cls
echo ============================================================================
echo   Agy Helper -- 1-Click Setup & Launcher
echo ============================================================================
echo.
set "APP_DIR=%~dp0"
set "EXE_PATH=%APP_DIR%AgyHelper.exe"
set "CERT_FILE=%APP_DIR%AgyHelper-Certificate.cer"

if not exist "%EXE_PATH%" (
    echo [ERROR] AgyHelper.exe not found in "%APP_DIR%"
    pause
    exit /b 1
)

:: Step 1: Install Certificate
if exist "%CERT_FILE%" (
    echo [1/3] Ensuring Agy Helper security certificate is trusted...
    certutil.exe -addstore -f "Root" "%CERT_FILE%" >nul 2>&1
    certutil.exe -addstore -f "TrustedPublisher" "%CERT_FILE%" >nul 2>&1
    certutil.exe -addstore -f "TrustedPeople" "%CERT_FILE%" >nul 2>&1
    echo   -^> Security Certificate: OK
) else (
    echo [1/3] Note: Certificate file not found, skipping certificate installation.
)

:: Step 2: Create Desktop & Start Menu Shortcuts via PowerShell
echo [2/3] Creating convenient desktop and start menu shortcuts...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$desktop = [Environment]::GetFolderPath('Desktop'); " ^
  "$shortcut = $ws.CreateShortcut((Join-Path $desktop 'Agy Helper.lnk')); " ^
  "$shortcut.TargetPath = '%EXE_PATH%'; " ^
  "$shortcut.WorkingDirectory = '%APP_DIR%'; " ^
  "$shortcut.Description = 'Agy Helper - Friendly IT Companion'; " ^
  "$shortcut.Save(); " ^
  "$programs = [Environment]::GetFolderPath('Programs'); " ^
  "$shortcut2 = $ws.CreateShortcut((Join-Path $programs 'Agy Helper.lnk')); " ^
  "$shortcut2.TargetPath = '%EXE_PATH%'; " ^
  "$shortcut2.WorkingDirectory = '%APP_DIR%'; " ^
  "$shortcut2.Description = 'Agy Helper - Friendly IT Companion'; " ^
  "$shortcut2.Save();"

echo   -^> Desktop & Start Menu Shortcuts: Created

:: Step 3: Launch Agy Helper
echo [3/3] Starting Agy Helper...
start "" "%EXE_PATH%" --open-window
echo.
echo ============================================================================
echo   Setup Complete! Agy Helper is now running.
echo ============================================================================
timeout /t 3 >nul
exit /b 0
