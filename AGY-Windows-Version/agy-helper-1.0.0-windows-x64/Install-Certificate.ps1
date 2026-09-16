# ============================================================================
# Agy Helper — PowerShell Code Signing Certificate Installer
# Imports AgyHelper-Certificate.cer into Windows Trusted Root and Trusted Publisher stores.
# ============================================================================

# Ensure script is running with elevated privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Requesting administrative privileges..." -ForegroundColor Cyan
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CertFile = Join-Path $ScriptDir "AgyHelper-Certificate.cer"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  Agy Helper -- Code Signing Certificate Installer (PowerShell)             " -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $CertFile)) {
    Write-Error "Certificate file not found at: $CertFile"
    Read-Host "Press Enter to exit..."
    exit 1
}

try {
    Write-Host "[1/3] Adding certificate to Trusted Root Certification Authorities..." -ForegroundColor Yellow
    Import-Certificate -FilePath $CertFile -CertStoreLocation Cert:\LocalMachine\Root | Out-Null
    Write-Host "  -> Root Store: OK" -ForegroundColor Green

    Write-Host "[2/3] Adding certificate to Trusted Publishers..." -ForegroundColor Yellow
    Import-Certificate -FilePath $CertFile -CertStoreLocation Cert:\LocalMachine\TrustedPublisher | Out-Null
    Write-Host "  -> Trusted Publishers: OK" -ForegroundColor Green

    Write-Host "[3/3] Adding certificate to Trusted People..." -ForegroundColor Yellow
    Import-Certificate -FilePath $CertFile -CertStoreLocation Cert:\LocalMachine\TrustedPeople | Out-Null
    Write-Host "  -> Trusted People: OK" -ForegroundColor Green

    Write-Host ""
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "  SUCCESS! Agy Helper is now trusted on this system.                         " -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "You can now run AgyHelper.exe without security warnings." -ForegroundColor White
} catch {
    Write-Error "Error installing certificate: $_"
}

Write-Host ""
Read-Host "Press Enter to exit..."
