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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Get installation directory
INSTALL_DIR="$HOME/roper"
echo -e "${CYAN}Installation Directory:${NC} $INSTALL_DIR"
echo

# Check if directory already exists
if [ -d "$INSTALL_DIR" ]; then
    print_warning "Directory $INSTALL_DIR already exists"
    read -p "Do you want to remove it and reinstall? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        print_status "Removed existing directory"
    else
        print_error "Installation cancelled"
        exit 1
    fi
fi

# Clone the repository
print_status "Cloning Roper repository..."
REPO_URL="https://github.com/r04nx/roper.git"
git clone "$REPO_URL" "$INSTALL_DIR"
cd "$INSTALL_DIR" || exit 1
print_success "Repository cloned successfully"

# Check Python version
print_status "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python 3.8+ required. Found: $PYTHON_VERSION"
    exit 1
fi
print_success "Python version: $PYTHON_VERSION"

# Install system dependencies
print_status "Installing system dependencies..."
echo "You may be prompted for your sudo password..."

# Update package list
sudo apt-get update -qq

# Install required packages
PACKAGES=("python3-tk" "python3-venv" "python3-pip" "wmctrl" "git")
for package in "${PACKAGES[@]}"; do
    if ! dpkg -l | grep -qw "$package"; then
        print_status "Installing $package..."
        sudo apt-get install -y "$package"
    else
        print_success "$package already installed"
    fi
done

# Setup Python virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv overlay_env
source overlay_env/bin/activate
print_success "Virtual environment created"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt
print_success "Python dependencies installed"

# Setup environment file
print_status "Setting up environment configuration..."
echo
echo -e "${YELLOW}API Key Configuration${NC}"
echo "=============================================="
echo -e "${CYAN}To get your Gemini API key:${NC}"
echo "1. Visit: https://ai.google.dev/aistudio"
echo "2. Sign in with your Google account"
echo "3. Click 'Get API Key' -> 'Create API Key'"
echo "4. Copy the generated API key"
echo

# Check if API key was provided as an argument
if [ -z "$1" ]; then
  echo
  echo -n "Enter your Google Gemini API Key: "
  read -s gemini_api_key
  echo
else
  gemini_api_key="$1"
fi

# Basic validation (Gemini API keys typically start with 'AIza')
if [[ ! $gemini_api_key =~ ^AIza[A-Za-z0-9_-]{35}$ ]]; then
    print_error "Invalid API key format. Should start with 'AIza' and be 39 characters long."
    exit 1
fi

# Create .env file
cat > .env << EOF
# Gemini API Configuration
GEMINI_API_KEY=$gemini_api_key

# Model Configuration (you can change these)
MCQ_MODEL=gemini-2.0-flash
CODE_MODEL=gemini-2.0-flash

# Optional: Additional API keys for rotation
# GEMINI_API_KEY_2=
# GEMINI_API_KEY_3=
EOF

print_success "Environment configuration saved"
# Make scripts executable
print_status "Making scripts executable..."
chmod +x start_roper.sh
chmod +x roper_cli
print_success "Scripts made executable"

# Setup CLI tool in PATH
print_status "Setting up CLI tool..."
CLI_LINK="$HOME/.local/bin/roper"
mkdir -p "$HOME/.local/bin"

# Update the roper_cli script with correct path
sed -i "s|ROPER_DIR=\"/home/rohan/Downloads/roper\"|ROPER_DIR=\"$INSTALL_DIR\"|g" roper_cli

# Create symlink
ln -sf "$INSTALL_DIR/roper_cli" "$CLI_LINK"
print_success "CLI tool linked to $CLI_LINK"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    print_status "Added ~/.local/bin to PATH in ~/.bashrc"
    export PATH="$HOME/.local/bin:$PATH"
fi

# Setup keyboard shortcuts
print_status "Setting up keyboard shortcuts..."
echo "This will configure system shortcuts for Roper..."
python3 setup_shortcut.py

# Test the installation
print_status "Testing installation..."
if python3 -c "import pynput, requests, PIL; print('All dependencies imported successfully')" 2>/dev/null; then
    print_success "Dependency test passed"
else
    print_error "Dependency test failed"
fi

# Deactivate virtual environment
deactivate

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
echo -e "${CYAN}Keyboard Shortcuts:${NC}"
echo "  Alt+X - Analyze MCQ questions"
echo "  Alt+Z - Generate code solutions"
echo "  Alt+C - Auto-type code"
echo "  Escape - Quit (when Roper window is focused)"
echo
echo -e "${CYAN}Quick Start:${NC}"
echo "  1. Run: roper start"
echo "  2. Open any MCQ or coding problem"
echo "  3. Press Alt+X for MCQ analysis or Alt+Z for code"
echo
echo -e "${YELLOW}Note:${NC} You may need to restart your terminal or run:"
echo "  source ~/.bashrc"
echo "to use the 'roper' command from anywhere."
echo
print_success "Roper is ready to use!"

