# Roper Windows Installation Script
# Run this script in PowerShell to install Roper on Windows

Write-Host "______" -ForegroundColor Green
Write-Host "| ___ \" -ForegroundColor Green
Write-Host "| |_/ /  ___  _ __    ___  _ __" -ForegroundColor Green
Write-Host "|    /  / _ \| '_ \  / _ \| '__|" -ForegroundColor Green
Write-Host "| |\ \ | (_) | |_) ||  __/| |" -ForegroundColor Green
Write-Host "\_| \_| \___/| .__/  \___||_|" -ForegroundColor Green
Write-Host "             | |" -ForegroundColor Green
Write-Host "             |_|" -ForegroundColor Green
Write-Host ""
Write-Host "Roper Code & MCQ Assistant - Windows Installer" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$INSTALL_DIR = Get-Location
Write-Host "[INFO] Installation Directory: $INSTALL_DIR"

# 1. Check Python installation
Write-Host "[INFO] Checking Python installation..." -ForegroundColor Blue
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "[SUCCESS] Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in your system PATH." -ForegroundColor Red
    Write-Host "Please download and install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check the option 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Exit
}

# 2. Create Python virtual environment
Write-Host "[INFO] Creating Python virtual environment..." -ForegroundColor Blue
if (Test-Path "overlay_env") {
    Write-Host "[WARNING] Re-creating existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "overlay_env"
}
& python -m venv --copies overlay_env
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to create virtual environment." -ForegroundColor Red
    Exit
}
Write-Host "[SUCCESS] Virtual environment created." -ForegroundColor Green

# 3. Upgrade pip & Install requirements
Write-Host "[INFO] Upgrading pip..." -ForegroundColor Blue
& .\overlay_env\Scripts\python.exe -m pip install --upgrade pip
Write-Host "[INFO] Installing Python dependencies..." -ForegroundColor Blue
& .\overlay_env\Scripts\pip.exe install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies." -ForegroundColor Red
    Exit
}
Write-Host "[SUCCESS] Python dependencies installed." -ForegroundColor Green

# 4. Setup environment file
Write-Host "[INFO] Configuring default environment settings..." -ForegroundColor Blue
if (-not (Test-Path ".env")) {
    $defaultEnv = @"
# Gemini API Configuration
GEMINI_API_KEY=
MCQ_MODEL=gemini-2.0-flash
CODE_MODEL=gemini-2.0-flash
"@
    Set-Content -Path ".env" -Value $defaultEnv
    Write-Host "[SUCCESS] Created default .env configuration." -ForegroundColor Green
} else {
    Write-Host "[INFO] Retaining existing .env configuration."
}

# 5. Create Windows CLI wrapper (roper.bat)
Write-Host "[INFO] Setting up CLI tool wrapper..." -ForegroundColor Blue
$batContent = @"
@echo off
rem Roper CLI Tool for Windows
set ROPER_DIR=$INSTALL_DIR
set ROPER_PID_FILE=%temp%\roper.pid
set ROPER_LOG_FILE=%temp%\roper.logs

if "%1"=="start" (
    echo [INFO] Starting Roper Code Assistant...
    if exist "%ROPER_PID_FILE%" (
        set /p oldpid=<"%ROPER_PID_FILE%"
        tasklist /FI "PID eq %oldpid%" 2>NUL | find /I "%oldpid%" >NUL
        if not errorlevel 1 (
            echo [WARNING] Roper is already running under PID %oldpid%
            exit /b 0
        )
    )
    cd /d "%ROPER_DIR%"
    start /B "" "%ROPER_DIR%\overlay_env\Scripts\pythonw.exe" roper.py
    timeout /t 2 /nobreak >nul
    echo [SUCCESS] Roper started successfully.
    exit /b 0
)

if "%1"=="stop" (
    echo [INFO] Stopping Roper...
    if exist "%ROPER_PID_FILE%" (
        set /p oldpid=<"%ROPER_PID_FILE%"
        taskkill /PID %oldpid% /F >nul 2>nul
        del "%ROPER_PID_FILE%" >nul 2>nul
        echo [SUCCESS] Roper stopped successfully.
    ) else (
        echo [WARNING] Roper is not running.
    )
    exit /b 0
)

if "%1"=="status" (
    if exist "%ROPER_PID_FILE%" (
        set /p oldpid=<"%ROPER_PID_FILE%"
        tasklist /FI "PID eq %oldpid%" 2>NUL | find /I "%oldpid%" >NUL
        if not errorlevel 1 (
            echo [SUCCESS] Roper is running (PID: %oldpid%)
        ) else (
            echo [WARN] Roper is not running (stale PID file found)
        )
    ) else (
        echo [WARN] Roper is not running
    )
    exit /b 0
)

if "%1"=="logs" (
    if exist "%ROPER_LOG_FILE%" (
        type "%ROPER_LOG_FILE%"
    ) else (
        echo [WARNING] No log file found.
    )
    exit /b 0
)

if "%1"=="restart" (
    call %0 stop
    call %0 start
    exit /b 0
)

echo Roper Code Assistant CLI
echo =========================
echo Usage:
echo   roper start   - Start background service
echo   roper stop    - Stop background service
echo   roper status  - Check active service status
echo   roper logs    - Show recent execution logs
echo   roper restart - Restart active service
"@
Set-Content -Path "roper.bat" -Value $batContent

# 6. Add roper.bat directory to PATH
$binDir = "$INSTALL_DIR"
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -notlike "*$binDir*") {
    Write-Host "[INFO] Adding $binDir to User PATH..." -ForegroundColor Blue
    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$binDir", "User")
    Write-Host "[SUCCESS] User PATH updated. Please restart terminal to use 'roper' from anywhere." -ForegroundColor Green
} else {
    Write-Host "[INFO] Directory is already in your PATH."
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "         INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:"
Write-Host "  roper start      - Start Roper"
Write-Host "  roper stop       - Stop Roper"
Write-Host "  roper status     - Check status"
Write-Host ""

# Launch Onboarding Wizard
Write-Host "[INFO] Launching Onboarding Setup Wizard..." -ForegroundColor Blue
& .\overlay_env\Scripts\python.exe onboarding.py
