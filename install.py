import sys
import os
import subprocess
import shutil

def print_status(msg):
    print(f"\033[94m[INFO]\033[0m {msg}")

def print_success(msg):
    print(f"\033[92m[SUCCESS]\033[0m {msg}")

def print_error(msg):
    print(f"\033[91m[ERROR]\033[0m {msg}")

def print_warning(msg):
    print(f"\033[93m[WARNING]\033[0m {msg}")

def install_windows():
    print_status("Starting Roper Windows Installation...")
    install_dir = os.path.abspath(os.path.dirname(__file__))
    
    # 1. Create virtual environment
    venv_dir = os.path.join(install_dir, "overlay_env")
    if os.path.exists(venv_dir):
        print_warning("Re-creating existing virtual environment...")
        shutil.rmtree(venv_dir)
        
    print_status("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "--copies", venv_dir], check=True)
    print_success("Virtual environment created.")
    
    # Paths to pip and python inside venv
    venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    venv_pip = os.path.join(venv_dir, "Scripts", "pip.exe")
    
    # 2. Upgrade pip
    print_status("Upgrading pip...")
    subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # 3. Install requirements
    print_status("Installing dependencies...")
    req_file = os.path.join(install_dir, "requirements.txt")
    subprocess.run([venv_pip, "install", "-r", req_file], check=True)
    print_success("Dependencies installed.")
    
    # 4. Setup environment file
    env_file = os.path.join(install_dir, ".env")
    if not os.path.exists(env_file):
        print_status("Creating default .env file...")
        with open(env_file, 'w') as f:
            f.write("GEMINI_API_KEY=\nMCQ_MODEL=gemini-2.0-flash\nCODE_MODEL=gemini-2.0-flash\n")
        print_success(".env file created.")
        
    # 5. Create roper.bat wrapper
    print_status("Creating roper.bat CLI wrapper...")
    bat_content = f"""@echo off
rem Roper CLI Tool for Windows
set ROPER_DIR={install_dir}
set ROPER_PID_FILE=%temp%\\roper.pid
set ROPER_LOG_FILE=%temp%\\roper.logs

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
    start /B "" "%ROPER_DIR%\\overlay_env\\Scripts\\pythonw.exe" roper.py
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
"""
    bat_file = os.path.join(install_dir, "roper.bat")
    with open(bat_file, 'w') as f:
        f.write(bat_content)
    print_success("roper.bat CLI wrapper created.")
    
    # 6. Configure User PATH via Registry
    print_status("Registering CLI wrapper in user PATH...")
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
        try:
            path_val, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            path_val = ""
            
        if install_dir not in path_val:
            new_path = path_val + ";" + install_dir if path_val else install_dir
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            # Notify system of environment change
            import ctypes
            ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, None)
            print_success("User PATH environment variable updated.")
        else:
            print_status("PATH environment variable already configured.")
    except Exception as e:
        print_warning(f"Could not automatically update registry PATH: {e}")
        print_warning(f"Please add this folder to your PATH manually: {install_dir}")

    print_success("Windows installation complete!")
    
    # Launch Onboarding Setup Wizard
    print_status("Launching Onboarding Wizard...")
    subprocess.run([venv_python, "onboarding.py"])

def main():
    if os.name == 'nt':
        install_windows()
    else:
        print_status("Detected Linux system. Running install.sh...")
        subprocess.run(["bash", "./install.sh"])

if __name__ == "__main__":
    main()
