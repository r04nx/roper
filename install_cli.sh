#!/bin/bash

# Roper CLI Installation Script

echo "🚀 Installing Roper CLI Tool..."

# Create local bin directory if it doesn't exist
mkdir -p ~/.local/bin

# Copy the CLI tool
cp roper_cli ~/.local/bin/roper
chmod +x ~/.local/bin/roper

echo "✅ Roper CLI installed to ~/.local/bin/roper"

# Check if ~/.local/bin is in PATH
if echo $PATH | grep -q "$HOME/.local/bin"; then
    echo "✅ ~/.local/bin is already in your PATH"
else
    echo "⚠️  Adding ~/.local/bin to your PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "✅ Added to ~/.bashrc - restart your terminal or run: source ~/.bashrc"
fi

# Optional: Install systemd service
read -p "📝 Do you want to install the systemd user service? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    mkdir -p ~/.config/systemd/user
    cp roper.service ~/.config/systemd/user/
    systemctl --user daemon-reload
    echo "✅ Systemd service installed. You can now use:"
    echo "   systemctl --user enable roper    # Enable auto-start"
    echo "   systemctl --user start roper     # Start service"
    echo "   systemctl --user stop roper      # Stop service"
    echo "   systemctl --user status roper    # Check status"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📖 Usage:"
echo "   roper start     # Start Roper"
echo "   roper stop      # Stop Roper"
echo "   roper status    # Check status"
echo "   roper help      # Show help"
echo ""
echo "🔧 Configuration file: $(pwd)/.env"
echo "📄 Logs: /tmp/roper.logs"
