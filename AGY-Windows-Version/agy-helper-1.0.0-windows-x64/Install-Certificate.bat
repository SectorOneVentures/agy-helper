@echo off
:: ============================================================================
:: Agy Helper — Code Signing Certificate Installer
:: Automatically elevates to Administrator and installs AgyHelper-Certificate.cer
:: into Windows Trusted Root Certification Authorities and Trusted Publishers.
:: ============================================================================
setlocal enableextensions enabledelayedexpansion
title Agy Helper - Code Signing Certificate Installer

:: Check for Administrative privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges to install security certificate...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb runAs"
    exit /b
)

cls
echo ============================================================================
echo   Agy Helper -- Code Signing Certificate Installer
echo ============================================================================
echo.
echo Installing code signing certificate for Agy Helper...
echo.

set "CERT_FILE=%~dp0AgyHelper-Certificate.cer"

if not exist "%CERT_FILE%" (
    echo [ERROR] Certificate file not found:
    echo "%CERT_FILE%"
    echo.
    echo Please make sure AgyHelper-Certificate.cer is in the same folder as this script.
    echo.
    pause
    exit /b 1
)

:: 1. Add to Trusted Root Certification Authorities (LocalMachine Root)
echo [1/3] Adding certificate to Trusted Root Certification Authorities...
certutil.exe -addstore -f "Root" "%CERT_FILE%" >nul 2>&1
if %errorlevel% equ 0 (
    echo   -^> Root Store: OK
) else (
    echo   -^> Root Store: Warning (code %errorlevel%)
)

:: 2. Add to Trusted Publishers (LocalMachine TrustedPublisher)
echo [2/3] Adding certificate to Trusted Publishers...
certutil.exe -addstore -f "TrustedPublisher" "%CERT_FILE%" >nul 2>&1
if %errorlevel% equ 0 (
    echo   -^> Trusted Publishers: OK
) else (
    echo   -^> Trusted Publishers: Warning (code %errorlevel%)
)

:: 3. Add to Trusted People (LocalMachine TrustedPeople)
echo [3/3] Adding certificate to Trusted People...
certutil.exe -addstore -f "TrustedPeople" "%CERT_FILE%" >nul 2>&1
if %errorlevel% equ 0 (
    echo   -^> Trusted People: OK
) else (
    echo   -^> Trusted People: Warning (code %errorlevel%)
)

echo.
echo ============================================================================
echo   SUCCESS! Agy Helper is now recognized as a trusted app on this computer.
echo ============================================================================
echo.
echo You can now launch AgyHelper.exe directly without SmartScreen or
echo "Unknown Publisher" security warnings.
echo.
echo Press any key to finish...
pause >nul
