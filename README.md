# Roper MCQ Solver

An AI-powered Multiple Choice Question (MCQ) solver that captures screenshots and uses Google Gemini AI to analyze and answer questions in real-time.

## Files

### Core Application
- `roper.py` - Main MCQ solver application with keyboard listener
- `overlay.py` - Notification overlay system
- `screenshot.py` - Screenshot capture functionality  
- `gemini_api.py` - Google Gemini AI integration
- `.env` - Environment variables (contains GEMINI_API_KEY)

### Scripts & Tools
- `start_roper.sh` - Launcher script with virtual environment
- `toggle_roper.py` - Toggle script to start/stop roper
- `setup_shortcut.py` - Script to set up keyboard shortcuts
- `overlay_env/` - Python virtual environment with dependencies

### Legacy Files
- `transparent_overlay_enhanced.py` - Original overlay application
- `toggle_overlay.py` - Original toggle script

## Features

- 🤖 **AI-Powered Analysis**: Uses Google Gemini 2.0 Flash to analyze MCQ questions
- 📸 **Screenshot Capture**: Automatically captures screen when triggered
- ⌨️ **Keyboard Shortcuts**: Ctrl+Alt+2 to analyze, Ctrl+Alt+` to toggle
- 🔄 **Smart Overlays**: Shows processing status and results in top-right corner
- 🎯 **Multi-Format Support**: Handles various MCQ formats and question types
- 🚀 **Background Processing**: Non-blocking analysis with visual feedback

## Installation

### Quick Install (Recommended)

**Option 1: One-liner with API key**
```bash
curl -fsSL https://raw.githubusercontent.com/r04nx/roper/master/install.sh | bash -s "YOUR_API_KEY_HERE"
```

**Option 2: Interactive installation**
```bash
curl -fsSL https://raw.githubusercontent.com/r04nx/roper/master/install.sh | bash
```

**Option 3: Manual installation**
```bash
git clone https://github.com/r04nx/roper.git
cd roper
chmod +x install.sh
./install.sh
```

### Get Your API Key
1. Visit: [Google AI Studio](https://ai.google.dev/aistudio)
2. Sign in with your Google account
3. Click 'Get API Key' → 'Create API Key'
4. Copy the generated API key

### What Gets Installed
- **System packages**: `python3-tk`, `python3-venv`, `wmctrl`, `git`
- **Python environment**: Virtual environment with all dependencies
- **CLI tool**: `roper` command available globally
- **Keyboard shortcuts**: System-wide shortcuts configured
- **Configuration**: `.env` file with your API key

### Uninstallation

**Option 1: Using the uninstall script**
```bash
# From the installation directory
cd ~/roper
./uninstall.sh
```

**Option 2: One-liner removal**
```bash
curl -fsSL https://raw.githubusercontent.com/r04nx/roper/master/uninstall.sh | bash
```

**Option 3: Manual uninstall**
```bash
roper stop
rm -rf ~/roper ~/.local/bin/roper
sed -i '/\.local\/bin.*PATH/d' ~/.bashrc
rm -f /tmp/roper*
```

### Keyboard Shortcuts
- **Ctrl+Alt+2**: Analyze current screen for MCQ questions
- **Ctrl+Alt+`**: Toggle roper on/off (setup required)
- **Escape**: Quit roper (when focused on terminal)

## Usage

### Starting Roper MCQ Solver
```bash
# Method 1: Using the launcher script
./start_roper.sh

# Method 2: Using the toggle script
python3 toggle_roper.py start

# Method 3: Direct execution (with virtual environment)
source overlay_env/bin/activate && python roper.py
```

### Controlling Roper
```bash
# Check if roper is running
python3 toggle_roper.py status

# Start roper
python3 toggle_roper.py start

# Stop roper
python3 toggle_roper.py stop

# Restart roper
python3 toggle_roper.py restart

# Toggle roper on/off
python3 toggle_roper.py
```

### Using MCQ Analysis
1. **Start Roper**: Run one of the start commands above
2. **Navigate to MCQ**: Open your MCQ test/question in any application
3. **Trigger Analysis**: Press **Ctrl+Alt+2**
4. **View Results**: Watch the overlay notifications:
   - 📸 "Taking screenshot..." (2 seconds)
   - 🤖 "Analyzing with AI..." (5 seconds)
   - 📝 "Answer: Q1B Q2A" (5 seconds)

## How It Works

### Transparency & Click-through
The overlay uses multiple X11 window properties to achieve click-through behavior:
1. Sets window type as `_NET_WM_WINDOW_TYPE_DESKTOP`
2. Uses `wmctrl` to set window below others
3. Attempts to disable input regions using `_NET_WM_WINDOW_INPUT_REGION`

### Always On Top
- Uses tkinter's `-topmost` attribute
- Window stays visible across all workspaces

### Position
- Currently positioned at coordinates (100, 100)
- Size: 150x30 pixels
- Can be modified in `transparent_overlay_enhanced.py`

## Troubleshooting

### Roper Not Starting
- **Missing API Key**: Check if `GEMINI_API_KEY` is set in `.env` file
- **Virtual Environment**: Ensure dependencies are installed: `source overlay_env/bin/activate && pip list`
- **Permissions**: Make scripts executable: `chmod +x start_roper.sh toggle_roper.py`

### MCQ Analysis Issues
- **No Response**: Check your internet connection and Gemini API key validity
- **Wrong Answers**: Ensure the question is clearly visible on screen
- **API Errors**: Check the terminal output for detailed error messages
- **Screenshot Issues**: Verify PIL/Pillow is working: `python3 -c "from PIL import ImageGrab; print('OK')"`

### Keyboard Shortcuts Not Working
- **Ctrl+Alt+2 not working**: Check if roper is running with `python3 toggle_roper.py status`
- **Ctrl+Alt+` not working**: Run `python3 setup_shortcut.py` to set up the shortcut
- **Permissions**: Some systems may require additional permissions for global key monitoring

### Process Management Issues
- **Roper won't stop**: Use `pkill -f "python.*roper.py"` to force stop
- **Multiple instances**: Check with `ps aux | grep roper` and kill extra processes
- **Zombie processes**: Restart your terminal or system if processes become unresponsive

## Customization

### Change Text
Edit the `text="Hello World"` line in `transparent_overlay_enhanced.py`

### Change Position
Modify the `geometry('150x30+100+100')` line:
- Format: `'width x height + x_position + y_position'`

### Change Font
Modify the `font.Font()` parameters in `create_widgets()` method

### Change Transparency
Adjust the `attributes('-alpha', 0.8)` value (0.0 = fully transparent, 1.0 = opaque)

### MCQ Solver Customization

#### Change Keyboard Shortcut
Edit `TRIGGER` in `roper.py`:
```python
TRIGGER = {keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.KeyCode.from_char('3')}
# Changes shortcut to Ctrl+Alt+3
```

#### Modify AI Prompt
Edit `SYSTEM_PROMPT` in `gemini_api.py` to change how questions are analyzed:
```python
SYSTEM_PROMPT = (
    "You are an expert at solving coding questions. "
    "Given an image of a programming question..."
)
```

#### Adjust Overlay Appearance
Modify `overlay.py`:
- **Position**: Change `x_pos` and `y_pos` calculations
- **Colors**: Modify `bg='#2c2c2c'` and `fg='white'`
- **Font**: Change `font=("Arial", 10, "bold")`
- **Duration**: Adjust `duration` parameter in `show()` calls

## Technical Details

### Architecture
- **Main Process**: `roper.py` runs the keyboard listener and coordinates components
- **Screenshot Module**: `screenshot.py` uses PIL.ImageGrab for screen capture
- **AI Integration**: `gemini_api.py` handles API communication with Google Gemini
- **Overlay System**: `overlay.py` manages floating notifications with tkinter
- **Process Management**: `toggle_roper.py` provides process control and monitoring

### Technologies Used
- **Input Monitoring**: `pynput` library for global keyboard event capture
- **Image Processing**: `Pillow (PIL)` for screenshot capture and processing
- **AI API**: Google Gemini 2.0 Flash via REST API
- **GUI Framework**: tkinter for overlay notifications
- **Environment Management**: `python-dotenv` for configuration
- **Process Control**: Linux system commands (`pgrep`, `pkill`, `ps`)

### Security & Privacy
- **Local Processing**: Screenshots are temporarily stored and automatically deleted
- **API Communication**: Only image data is sent to Gemini API
- **No Data Persistence**: No question/answer data is permanently stored
- **Secure Configuration**: API keys stored in local `.env` file

### Performance
- **Non-blocking**: Analysis runs in separate threads to maintain responsiveness
- **Memory Efficient**: Temporary files are cleaned up after each analysis
- **Low CPU Usage**: Keyboard listener uses minimal system resources
- **Quick Response**: Average analysis time: 2-5 seconds depending on internet speed

### Compatibility
- **Operating System**: Optimized for Linux Mint with Cinnamon desktop
- **Python Version**: Requires Python 3.12+
- **Display**: Works with single and multi-monitor setups
- **Network**: Requires internet connection for AI analysis
