#!/bin/bash

# Roper AI Analysis Tool - Installation Script
# Advanced AI analysis tool for screen content

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art
echo -e "${CYAN}"
cat << 'EOF'
______                           
| ___ \                          
| |_/ /  ___  _ __    ___  _ __   
|    /  / _ \| '_ \  / _ \| '__|  
| |\ \ | (_) | |_) ||  __/| |     
\_| \_| \___/| .__/  \___||_|     
             | |                  
             |_|                  

Advanced AI Analysis Tool
EOF
echo -e "${NC}"

echo -e "${GREEN}Welcome to Roper Installation${NC}"
echo "==============================================="
echo

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Progress Bar & Execution Helper
show_progress() {
    local percent=$1
    local msg=$2
    local width=35
    local filled=$(( percent * width / 100 ))
    local empty=$(( width - filled ))
    
    local bar=""
    for ((i=0; i<filled; i++)); do bar="${bar}█"; done
    for ((i=0; i<empty; i++)); do bar="${bar}░"; done
    
    # Carriage return to overwrite the same line
    echo -ne "\r${CYAN}[PROGRESS]${NC} [${bar}] ${percent}% | ${msg}"
    
    if [ $percent -eq 100 ]; then
        echo -e "\n"
    fi
}

run_with_progress() {
    local cmd="$1"
    local start_pct=$2
    local target_pct=$3
    local msg="$4"
    
    # Run task in background logging to a temporary file
    eval "$cmd" > /tmp/roper_install_step.log 2>&1 &
    local pid=$!
    
    local current_pct=$start_pct
    while kill -0 $pid 2>/dev/null; do
        show_progress $current_pct "$msg"
        sleep 0.1
        if [ $current_pct -lt $(( target_pct - 2 )) ]; then
            current_pct=$(( current_pct + 1 ))
        fi
    done
    
    wait $pid
    local status=$?
    
    if [ $status -ne 0 ]; then
        echo -e "\n"
        print_error "Installation failed at step: $msg"
        print_error "Error Log (/tmp/roper_install_step.log):"
        cat /tmp/roper_install_step.log
        exit 1
    fi
    
    show_progress $target_pct "$msg (Completed)"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if roper files are in the current directory
if [ ! -f "roper.py" ] || [ ! -f "requirements.txt" ]; then
    print_warning "Roper files not found in current directory. Setting up ~/roper..."
    
    cloned=false
    
    # Try Git clone first
    if command -v git &> /dev/null; then
        print_status "Trying to clone repository from GitHub..."
        if [ -d "$HOME/roper" ]; then
            print_warning "~/roper directory already exists. Updating..."
            cd "$HOME/roper"
            if git pull; then
                cloned=true
            fi
        else
            if git clone https://github.com/r04nx/roper.git "$HOME/roper"; then
                cd "$HOME/roper"
                cloned=true
            fi
        fi
    fi
    
    # Fallback to tarball approach if git clone failed or wasn't available
    if [ "$cloned" = false ]; then
        print_warning "Git clone failed or unavailable. Falling back to tarball download..."
        mkdir -p "$HOME/roper"
        
        # Download from Filebin CDN
        TARBALL_URL="https://filebin.net/roperbin/roper.tar.gz"
        print_status "Downloading tarball from $TARBALL_URL..."
        
        if command -v curl &> /dev/null; then
            curl -fsSL "$TARBALL_URL" -o "$HOME/roper.tar.gz"
        elif command -v wget &> /dev/null; then
            wget -qO "$HOME/roper.tar.gz" "$TARBALL_URL"
        else
            print_error "Neither curl nor wget found. Cannot download tarball."
            exit 1
        fi
        
        print_status "Extracting files to ~/roper..."
        tar -xzf "$HOME/roper.tar.gz" -C "$HOME/roper"
        rm "$HOME/roper.tar.gz"
        cd "$HOME/roper"
    fi
    
    # Re-run installation from the prepared directory
    exec ./install.sh "$@"
fi

INSTALL_DIR="$(pwd)"
echo -e "${CYAN}Installation Directory:${NC} $INSTALL_DIR"
echo
print_success "Found Roper files in directory: $INSTALL_DIR"

# Check Python version
print_status "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python 3.8+ required. Found: $PYTHON_VERSION"
    exit 1
fi
print_success "Python version: $PYTHON_VERSION"

# Check for missing dependencies
PACKAGES=("python3-tk" "python3-venv" "python3-pip" "wmctrl" "git")
missing_package=false
for package in "${PACKAGES[@]}"; do
    if ! dpkg -l | grep -qw "$package" 2>/dev/null; then
        missing_package=true
        break
    fi
done

if [ "$missing_package" = true ]; then
    print_status "Installing missing system dependencies..."
    echo "You may be prompted for your sudo password..."
    
    # Update package list
    sudo apt-get update -qq
    
    # Install required packages
    for package in "${PACKAGES[@]}"; do
        if ! dpkg -l | grep -qw "$package" 2>/dev/null; then
            print_status "Installing $package..."
            sudo apt-get install -y "$package"
        else
            print_success "$package already installed"
        fi
    done
else
    print_success "All system dependencies are already installed!"
fi

# Setup Python virtual environment
run_with_progress "python3 -m venv --copies overlay_env" 10 35 "Creating Python virtual environment"

# Upgrade pip
run_with_progress "./overlay_env/bin/pip install --upgrade pip" 35 45 "Upgrading package manager (pip)"

# Install Python dependencies
run_with_progress "./overlay_env/bin/pip install -r requirements.txt" 45 75 "Installing Python dependencies"

# Setup environment file
show_progress 75 "Setting up environment configuration"
if [ ! -f .env ]; then
    cat > .env << EOF
# Gemini API Configuration
GEMINI_API_KEY=
MCQ_MODEL=gemini-2.0-flash
CODE_MODEL=gemini-2.0-flash
EOF
fi
show_progress 80 "Default environment configuration created"

# Make scripts executable and link CLI
CLI_LINK="$HOME/.local/bin/roper"
run_with_progress "chmod +x start_roper.sh roper_cli && mkdir -p \"\$HOME/.local/bin\" && sed -i \"s#^ROPER_DIR=.*#ROPER_DIR=\\\"\$INSTALL_DIR\\\"#g\" roper_cli && ln -sf \"\$INSTALL_DIR/roper_cli\" \"\$CLI_LINK\"" 80 90 "Configuring system CLI tools"

# Setup keyboard shortcuts
run_with_progress "python3 setup_shortcut.py" 90 95 "Setting up system hotkey shortcuts"

# Test the installation
run_with_progress "./overlay_env/bin/python -c 'import pynput, requests, PIL'" 95 100 "Running final validation checks"

# Launch Onboarding Wizard if DISPLAY is set
if [ -n "$DISPLAY" ]; then
    print_status "Launching Onboarding Setup Wizard..."
    ./overlay_env/bin/python onboarding.py
else
    print_warning "No graphical display detected. Skipping setup wizard."
    print_warning "You can configure Roper later by running: nano ~/roper/.env"
fi

echo
echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}         INSTALLATION COMPLETE!${NC}"
echo -e "${GREEN}===============================================${NC}"
echo
echo -e "${CYAN}Usage:${NC}"
echo "  roper start      - Start Roper"
echo "  roper stop       - Stop Roper"
echo "  roper status     - Check status"
echo "  roper help       - Show help"
echo
echo -e "${CYAN}Keyboard & Mouse Shortcuts:${NC}"
echo "  Middle Mouse Click - Solve MCQ from screen screenshot"
echo "  Alt+Z              - Generate code solution from screenshot"
echo "  Alt+C              - Auto-type generated code safely (commented)"
echo "  Ctrl+Alt+, / O     - Open settings configuration modal"
echo "  Escape             - Quit (when focused on terminal running Roper)"
echo
echo -e "${CYAN}API Key Setup:${NC}"
echo "  If you skipped the onboarding wizard, you can configure your key by:"
echo "  1. Editing the config file: nano $INSTALL_DIR/.env"
echo "  2. Adding your API key: GEMINI_API_KEY=your_api_key"
echo
echo -e "${CYAN}Quick Start:${NC}"
echo "  1. Run: roper start"
echo "  2. Press Ctrl+Alt+, to verify/update your credentials"
echo
echo -e "${YELLOW}Note:${NC} You may need to restart your terminal or run:"
echo "  source ~/.bashrc"
echo "to use the 'roper' command from anywhere."
echo
print_success "Roper is installed! Configure your API key to start using it."

