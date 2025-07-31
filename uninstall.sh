#!/bin/bash

# Roper AI Analysis Tool - Uninstallation Script
# Completely removes Roper from the system

# Disable exit on error for interactive prompts
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art
echo -e "${RED}"
cat << 'EOF'
______                           
| ___ \                          
| |_/ /  ___  _ __    ___  _ __   
|    /  / _ \| '_ \  / _ \| '__|  
| |\ \ | (_) | |_) ||  __/| |     
\_| \_| \___/| .__/  \___||_|     
             | |                  
             |_|                  

Uninstallation Tool
EOF
echo -e "${NC}"

echo -e "${RED}Roper Uninstallation${NC}"
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

# Confirmation prompt
echo -e "${YELLOW}This will completely remove Roper from your system.${NC}"
echo "The following will be removed:"
echo "  - Roper installation directory (~/.roper or ~/roper)"
echo "  - CLI tool (~/.local/bin/roper)"
echo "  - Configuration files (.env, logs)"
echo "  - Keyboard shortcuts"
echo "  - PATH modifications"
echo "  - Temporary files"
echo

read -p "Are you sure you want to uninstall Roper? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Uninstallation cancelled"
    exit 1
fi

echo
print_status "Starting Roper uninstallation..."

# Stop any running Roper processes
print_status "Stopping Roper processes..."
if command -v roper &> /dev/null; then
    roper stop 2>/dev/null || true
    print_success "Stopped Roper processes"
else
    print_warning "Roper CLI not found, attempting manual process termination"
fi

# Force kill any remaining Roper processes
print_status "Force killing any remaining Roper processes..."
pkill -9 -f "python.*roper" 2>/dev/null || true
pkill -9 -f "roper.py" 2>/dev/null || true
pkill -9 -f "roper" 2>/dev/null || true
print_success "Process cleanup completed"

# Remove installation directories
print_status "Removing installation directories..."
INSTALL_DIRS=("$HOME/roper" "$HOME/.roper")
for dir in "${INSTALL_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        rm -rf "$dir"
        print_success "Removed $dir"
    else
        print_warning "Directory $dir not found"
    fi
done

# Remove CLI tool
print_status "Removing CLI tool..."
CLI_LOCATIONS=("$HOME/.local/bin/roper" "/usr/local/bin/roper")
for cli in "${CLI_LOCATIONS[@]}"; do
    if [ -f "$cli" ] || [ -L "$cli" ]; then
        rm -f "$cli"
        print_success "Removed $cli"
    fi
done

# Remove PATH modifications from shell configuration files
print_status "Cleaning PATH modifications..."
SHELL_CONFIGS=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile")
for config in "${SHELL_CONFIGS[@]}"; do
    if [ -f "$config" ]; then
        # Remove lines that add ~/.local/bin to PATH (created by Roper installer)
        sed -i '/# Added by Roper installer/d' "$config" 2>/dev/null || true
        sed -i '/export PATH="$HOME\/\.local\/bin:$PATH"/d' "$config" 2>/dev/null || true
        sed -i '/\.local\/bin.*PATH/d' "$config" 2>/dev/null || true
        print_success "Cleaned $config"
    fi
done

# Remove keyboard shortcuts
print_status "Removing keyboard shortcuts..."
# Try to remove Cinnamon shortcuts
if pgrep -x "cinnamon" >/dev/null 2>&1; then
    # Remove from custom keybindings list
    dconf write /org/cinnamon/desktop/keybindings/custom-list "[]" 2>/dev/null || true
    # Remove the actual keybinding
    dconf reset -f /org/cinnamon/desktop/keybindings/custom-keybindings/ 2>/dev/null || true
    print_success "Removed Cinnamon keyboard shortcuts"
fi

# Try to remove GNOME shortcuts
if command -v gsettings &> /dev/null; then
    gsettings reset org.gnome.settings-daemon.plugins.media-keys custom-keybindings 2>/dev/null || true
    print_success "Removed GNOME keyboard shortcuts"
fi

# Clean up temporary files
print_status "Cleaning up temporary files..."
TEMP_FILES=("/tmp/roper*" "/tmp/*roper*" "$HOME/.cache/roper*")
for pattern in "${TEMP_FILES[@]}"; do
    rm -f $pattern 2>/dev/null || true
done
print_success "Temporary files cleaned"

# Clean up log files
print_status "Removing log files..."
LOG_FILES=("/tmp/roper.logs" "/tmp/roper.pid" "$HOME/.local/share/roper*" "$HOME/.config/roper*")
for pattern in "${LOG_FILES[@]}"; do
    rm -f $pattern 2>/dev/null || true
done
print_success "Log files removed"

# Optional: Ask about removing system packages
echo
print_warning "System packages were installed during Roper installation:"
echo "  - python3-tk (GUI toolkit)"
echo "  - python3-venv (Virtual environments)"  
echo "  - python3-pip (Package installer)"
echo "  - wmctrl (Window management)"
echo "  - git (Version control)"
echo

read -p "Do you want to remove these system packages? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Removing system packages..."
    sudo apt-get remove -y python3-tk python3-venv wmctrl 2>/dev/null || true
    sudo apt-get autoremove -y 2>/dev/null || true
    print_success "System packages removed"
else
    print_status "Keeping system packages (they may be used by other applications)"
fi

# Verify complete removal
print_status "Verifying removal..."
VERIFICATION_FAILED=false

# Check for remaining files
if [ -d "$HOME/roper" ] || [ -d "$HOME/.roper" ]; then
    print_error "Installation directories still exist"
    VERIFICATION_FAILED=true
fi

# Check for CLI tool
if command -v roper &> /dev/null; then
    print_error "CLI tool still accessible"
    VERIFICATION_FAILED=true
fi

# Check for running processes
if pgrep -f "roper" >/dev/null 2>&1; then
    print_error "Roper processes still running"
    VERIFICATION_FAILED=true
fi

if [ "$VERIFICATION_FAILED" = true ]; then
    echo
    print_error "Uninstallation may not be complete. Manual cleanup may be required."
    echo
    echo -e "${CYAN}Manual cleanup commands:${NC}"
    echo "  sudo pkill -9 -f roper"
    echo "  rm -rf ~/roper ~/.roper"
    echo "  rm -f ~/.local/bin/roper"
    echo "  rm -f /tmp/roper*"
    exit 1
fi

echo
echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}         UNINSTALLATION COMPLETE!${NC}"
echo -e "${GREEN}===============================================${NC}"
echo
print_success "Roper has been completely removed from your system"
echo
echo -e "${CYAN}What was removed:${NC}"
echo "  ✓ Installation directories"
echo "  ✓ CLI tool and PATH modifications"
echo "  ✓ Configuration files and logs"
echo "  ✓ Keyboard shortcuts"
echo "  ✓ Temporary files"
echo "  ✓ Running processes"
echo
echo -e "${YELLOW}Note:${NC} You may need to restart your terminal or run:"
echo "  source ~/.bashrc"
echo "to refresh your shell environment."
echo
print_success "Thank you for using Roper!"
