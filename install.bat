@echo off
setlocal

REM Roper AI Analysis Tool - Installation Script for Windows

REM Colors for output (using escape codes, requires modern Windows terminal)
for /f "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem" ') do set "DEL=%%a"

set "RED=^<ESC^>[0;31m"
set "GREEN=^<ESC^>[0;32m"
set "YELLOW=^<ESC^>[1;33m"
set "BLUE=^<ESC^>[0;34m"
set "PURPLE=^<ESC^>[0;35m"
set "CYAN=^<ESC^>[0;36m"
set "NC=^<ESC^>[0m"

REM ASCII Art
echo %CYAN%
echo ______                           
echo ^| ___ \                          
echo ^| |_/ /  ___  _ __    ___  _ __   
echo ^|    /  / _ \^| '_ \  / _ \^| '__^|  
echo ^| |\ \ ^| (_) ^| |_) ^|^|  __/^| ^|     
echo \_| \_\ \___/^| .__/  \___^|^|_^|     
echo              ^| ^|                  
echo              ^_^ 

echo.
echo Advanced AI Analysis Tool
echo %NC%

echo %GREEN%Welcome to Roper Installation%NC%
echo ===============================================
echo.

REM Get installation directory
set "INSTALL_DIR=%USERPROFILE%\roper"
echo %CYAN%Installation Directory:%NC% %INSTALL_DIR%
echo.

REM Check if directory already exists
if exist "%INSTALL_DIR%" (
    echo %YELLOW%Directory %INSTALL_DIR% already exists%NC%
    set /p "REPLY=Do you want to remove it and reinstall? (y/N): "
    if /i "%REPLY%" NEQ "Y" (
        echo %RED%Installation cancelled%NC%
        exit /b 1
    )
    echo Deleting existing directory...
    rmdir /s /q "%INSTALL_DIR%"
    echo Removed existing directory.
)

REM Clone the repository
echo %BLUE%[INFO]%NC% Cloning Roper repository...
set "REPO_URL=https://github.com/r04nx/roper.git"
git clone "%REPO_URL%" "%INSTALL_DIR%"
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Failed to clone repository.
    exit /b 1
)
cd /d "%INSTALL_DIR%"
echo %GREEN%[SUCCESS]%NC% Repository cloned successfully

REM Check Python version
echo %BLUE%[INFO]%NC% Checking Python version...
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
if not defined PYTHON_VERSION (
    echo %RED%[ERROR]%NC% Python is not installed or not in PATH.
    exit /b 1
)
echo %GREEN%[SUCCESS]%NC% Python version: %PYTHON_VERSION%

REM Setup Python virtual environment
echo %BLUE%[INFO]%NC% Creating Python virtual environment...
python -m venv overlay_env
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Failed to create virtual environment.
    exit /b 1
)
echo %GREEN%[SUCCESS]%NC% Virtual environment created

REM Activate virtual environment
call .\overlay_env\Scripts\activate.bat

REM Upgrade pip
echo %BLUE%[INFO]%NC% Upgrading pip...
pip install --upgrade pip

REM Install Python dependencies
echo %BLUE%[INFO]%NC% Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Failed to install Python dependencies.
    exit /b 1
)
echo %GREEN%[SUCCESS]%NC% Python dependencies installed

REM Setup environment file
echo %BLUE%[INFO]%NC% Setting up environment configuration...
(
    echo # Gemini API Configuration
    echo # Add your API key here: GEMINI_API_KEY=your_api_key_here
    echo # Get your API key from: https://ai.google.dev/aistudio
    echo GEMINI_API_KEY=
    echo.
    echo # Model Configuration (you can change these)
    echo MCQ_MODEL=gemini-1.0-pro
    echo CODE_MODEL=gemini-1.0-pro
) > .env
echo %GREEN%[SUCCESS]%NC% Default environment configuration created

REM Setup CLI tool
echo %BLUE%[INFO]%NC% Setting up CLI tool...
set "CLI_PATH=%INSTALL_DIR%\roper_cli.bat"
(
    echo @echo off
    echo ""%INSTALL_DIR%\overlay_env\Scripts\python.exe"" "%INSTALL_DIR%\roper_cli" %* 
) > "%CLI_PATH%"

REM Add to PATH
echo %BLUE%[INFO]%NC% Adding installation directory to PATH...
setx PATH "%PATH%;%INSTALL_DIR%"
if errorlevel 1 (
    echo %YELLOW%[WARNING]%NC% Failed to add to PATH automatically. Please add %INSTALL_DIR% to your PATH manually.
) else (
    echo %GREEN%[SUCCESS]%NC% Added to PATH. Please restart your terminal for changes to take effect.
)

REM Setup keyboard shortcuts
echo %BLUE%[INFO]%NC% Setting up keyboard shortcuts...
echo This will configure system shortcuts for Roper...
python setup_shortcut.py

REM Test the installation
echo %BLUE%[INFO]%NC% Testing installation...
python -c "import pynput, requests, PIL; print('All dependencies imported successfully')"
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Dependency test failed
) else (
    echo %GREEN%[SUCCESS]%NC% Dependency test passed
)

REM Deactivate virtual environment
call .\overlay_env\Scripts\deactivate.bat

echo.
echo %GREEN%===============================================%NC%
echo %GREEN%         INSTALLATION COMPLETE!%NC%
echo %GREEN%===============================================%NC%
echo.
echo %CYAN%Usage:%NC%
echo   roper start      - Start Roper
echo   roper stop       - Stop Roper
echo   roper status     - Check status
echo   roper help       - Show help
echo.
echo %CYAN%API Key Setup:%NC%
echo   1. Get your API key from: https://ai.google.dev/aistudio
    echo   2. Edit the configuration: notepad "%INSTALL_DIR%\.env"

echo.
echo %YELLOW%Note:%NC% You may need to restart your terminal to use the 'roper' command from anywhere.

echo.

echo %GREEN%Roper is installed! Configure your API key to start using it.%NC%

endlocal
