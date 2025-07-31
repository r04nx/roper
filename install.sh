#!/bin/bash

# Simple ASCII Art
ascii_art=""
read -r -d '' ascii_art << EOM
.______       _______  _______ .______          ___   .___________. _______  
|   _  \     |   ____||   ____||   _  \        /   \  |           ||   ____| 
|  |_)  |    |  |__   |  |__   |  |_)  |      /  ^  \ `---|  |----`|  |__    
|      /     |   __|  |   __|  |      /      /  /_\  \    |  |     |   __|   
|  |\  \----.|  |____ |  |____ |  |\  \----./  _____  \   |  |     |  |____  
| _| `._____||_______||_______|| _| `._____/__/     \__\  |__|     |_______| 
EOM

# Display the ASCII art
echo "$ascii_art"

# Clone the repository
repo_url="https://github.com/user/roper.git"
git clone $repo_url
cd roper || exit

# Setup Python virtual environment
python3 -m venv overlay_env
source overlay_env/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Prompt user for Gemini API keys
read -p "Enter your Google Gemini API Key: " gemini_api_key
cat <<EOF >.env
GEMINI_API_KEY=$gemini_api_key
EOF

# Display link to Google AI Studio for API Key
echo "To obtain your API Key, visit: https://ai.google/studio"

# Ensure necessary packages are installed
if ! dpkg -l | grep -qw python3-tk; then
    echo "python3-tk not found. Installing..."
    sudo apt-get install python3-tk
fi

if ! dpkg -l | grep -qw wmctrl; then
    echo "wmctrl not found. Installing..."
    sudo apt-get install wmctrl
fi

# Setup Keyboard Shortcuts
python3 setup_shortcut.py

# Deactivate virtual environment
 deactivate 

echo "Installation complete. You can start Roper by running ./start_roper.sh"

