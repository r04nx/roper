# Roper - Windows One-Line Installer
# Usage: irm https://raw.githubusercontent.com/r04nx/roper/master/install.ps1 | iex

$ErrorActionPreference = "Stop"
$REPO_URL = "https://github.com/r04nx/roper/archive/refs/heads/master.zip"
$INSTALL_DIR = "$env:USERPROFILE\roper"
$ZIP_PATH = "$env:TEMP\roper.zip"

function Write-Step($msg) { Write-Host "  $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "  [ERROR] $msg" -ForegroundColor Red; exit 1 }
function Write-Warn($msg) { Write-Host "  [!] $msg" -ForegroundColor Yellow }

Clear-Host
Write-Host ""
Write-Host "  ____                           " -ForegroundColor Green
Write-Host " |  _ \ ___  _ __   ___ _ __    " -ForegroundColor Green
Write-Host " | |_) / _ \| '_ \ / _ \ '__|   " -ForegroundColor Green
Write-Host " |  _ < (_) | |_) |  __/ |      " -ForegroundColor Green
Write-Host " |_| \_\___/| .__/ \___|_|      " -ForegroundColor Green
Write-Host "            |_|                  " -ForegroundColor Green
Write-Host ""
Write-Host "  Roper - AI Code & MCQ Assistant" -ForegroundColor White
Write-Host "  Windows Installer v1.0" -ForegroundColor DarkGray
Write-Host "  ================================" -ForegroundColor DarkGray
Write-Host ""

# --- Step 1: Check Python ---
Write-Step "Checking Python..."
try {
    $pyver = & python --version 2>&1
    Write-Ok "Found: $pyver"
} catch {
    Write-Fail "Python not found. Install from https://python.org and check 'Add to PATH'"
}

# --- Step 2: Download Repository ---
Write-Step "Downloading Roper from GitHub..."
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $wc = New-Object System.Net.WebClient
    $wc.DownloadFile($REPO_URL, $ZIP_PATH)
    Write-Ok "Download complete."
} catch {
    Write-Fail "Download failed: $_"
}

# --- Step 3: Extract ZIP ---
Write-Step "Extracting files to $INSTALL_DIR ..."
if (Test-Path $INSTALL_DIR) {
    Remove-Item -Recurse -Force $INSTALL_DIR
}
Add-Type -AssemblyName System.IO.Compression.FileSystem
$extracted = "$env:TEMP\roper_extracted"
if (Test-Path $extracted) { Remove-Item -Recurse -Force $extracted }
[System.IO.Compression.ZipFile]::ExtractToDirectory($ZIP_PATH, $extracted)
$inner = Get-ChildItem $extracted | Select-Object -First 1
Move-Item $inner.FullName $INSTALL_DIR
Remove-Item $ZIP_PATH -Force
Remove-Item $extracted -Recurse -Force
Write-Ok "Extracted to $INSTALL_DIR"

# --- Step 4: Run Python Installer ---
Write-Step "Running installation script..."
Write-Host ""
Set-Location $INSTALL_DIR
& python install.py
