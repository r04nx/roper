from pynput import keyboard
from overlay import Overlay
from screenshot import take_screenshot
from gemini_api import ask_gemini, ask_gemini_code, initialize_api_keys
import threading
import sys
import os
import signal
import time
import logging
from datetime import datetime

# Keyboard shortcuts
MCQ_TRIGGER = {keyboard.Key.alt_l, keyboard.KeyCode.from_char('x')}
CODE_TRIGGER = {keyboard.Key.alt_l, keyboard.KeyCode.from_char('z')}
TYPE_TRIGGER = {keyboard.Key.alt_l, keyboard.KeyCode.from_char('c')}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/roper.logs'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('roper.main')

current_keys = set()
overlay = None
listener = None
running = True
last_code_solution = ""

def process_mcq():
    try:
        logger.info("MCQ processing started")
        overlay.show("Taking screenshot...", duration=2)
        time.sleep(0.5)  # Brief pause to show message
        
        img_path = take_screenshot()
        logger.info(f"Screenshot taken: {img_path}")
        overlay.show("Analyzing with AI...", duration=5)
        
        answer = ask_gemini(img_path)
        logger.info(f"MCQ answer received: {answer}")
        
        # Clean up temporary file
        if os.path.exists(img_path):
            os.remove(img_path)
            
        overlay.show(f"{answer}", duration=5)
        logger.info("MCQ processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in process_mcq: {e}")
        overlay.show(f"Error: {str(e)}", duration=3)
        print(f"Error in process_mcq: {e}")

def clean_code_response(code):
    """Clean AI response to extract pure code"""
    # Remove markdown formatting
    lines = code.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip markdown code blocks
        if line.strip().startswith('```'):
            continue
        # Fix common AI formatting issues - replace >> with ||
        line = line.replace('>>', '||')
        # Fix null comparisons
        line = line.replace('s == null || p == null', '(s == null || p == null)')
        # Fix boolean operations
        line = line.replace('dp[i][j] || dp[i - 1][j]', 'dp[i][j] || dp[i - 1][j]')
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()

def process_code():
    global last_code_solution
    try:
        logger.info("Code processing started")
        overlay.show("Taking screenshot...", duration=2)
        time.sleep(0.5)
        
        img_path = take_screenshot()
        logger.info(f"Screenshot taken for code: {img_path}")
        overlay.show("Generating code solution...", duration=7)
        
        solution = ask_gemini_code(img_path)
        last_code_solution = clean_code_response(solution)
        logger.info(f"Code solution generated, length: {len(last_code_solution)} characters")
        
        # Debug: print cleaned code
        print("=== CLEANED CODE ===")
        print(last_code_solution)
        print("=== END CLEANED CODE ===")
        
        # Clean up temporary file
        if os.path.exists(img_path):
            os.remove(img_path)
            
        overlay.show("Code ready! Use Alt+C to type", duration=4)
        logger.info("Code processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in process_code: {e}")
        overlay.show(f"Error: {str(e)}", duration=3)
        print(f"Error in process_code: {e}")

def auto_type_code():
    global last_code_solution
    try:
        logger.info("Auto-type code started")
        if not last_code_solution:
            logger.warning("No code solution available for typing")
            overlay.show("No code to type! Use Alt+Z first", duration=3)
            return
            
        overlay.show("Typing code...", duration=2)
        time.sleep(0.5)

        # Add comments at beginning of each line
        lines = last_code_solution.split('\n')
        commented_lines = []
        
        for line in lines:
            if line.strip():  # Only add comment to non-empty lines
                commented_lines.append(f"# {line}")
            else:
                commented_lines.append(line)
        
        commented_code = '\n'.join(commented_lines)
        logger.info(f"Starting to type {len(commented_code)} characters")
        
        # Type the code
        from pynput.keyboard import Controller
        kb = Controller()
        
        for char in commented_code:
            if char == '\n':
                kb.press(keyboard.Key.enter)
                kb.release(keyboard.Key.enter)
            else:
                kb.type(char)
            time.sleep(0.02)  # Small delay between characters
        
        overlay.show("Code typed successfully!", duration=3)
        logger.info("Auto-type code completed successfully")
        
    except Exception as e:
        logger.error(f"Error in auto_type_code: {e}")
        overlay.show(f"Error: {str(e)}", duration=3)
        print(f"Error in auto_type_code: {e}")

def on_press(key):
    global current_keys
    try:
        # Check for MCQ trigger
        if key in MCQ_TRIGGER:
            current_keys.add(key)
        if all(k in current_keys for k in MCQ_TRIGGER):
            print("MCQ trigger activated...")
            threading.Thread(target=process_mcq, daemon=True).start()
            current_keys.clear()
            return
            
        # Check for Code trigger
        if key in CODE_TRIGGER:
            current_keys.add(key)
        if all(k in current_keys for k in CODE_TRIGGER):
            print("Code analysis trigger activated...")
            threading.Thread(target=process_code, daemon=True).start()
            current_keys.clear()
            return
            
        # Check for Type trigger
        if key in TYPE_TRIGGER:
            current_keys.add(key)
        if all(k in current_keys for k in TYPE_TRIGGER):
            print("Auto-type trigger activated...")
            threading.Thread(target=auto_type_code, daemon=True).start()
            current_keys.clear()
            return
            
    except Exception as e:
        print(f"Error in on_press: {e}")

def on_release(key):
    global current_keys
    try:
        if key in current_keys:
            current_keys.remove(key)
        # Exit on Escape key
        if key == keyboard.Key.esc:
            print("Escape pressed - shutting down...")
            stop_application()
    except Exception as e:
        print(f"Error in on_release: {e}")

def stop_application():
    global running, listener, overlay
    running = False
    
    # Clean up PID file
    pid_file = "/tmp/roper.pid"
    if os.path.exists(pid_file):
        try:
            os.remove(pid_file)
            logger.info("PID file cleaned up")
        except Exception as e:
            logger.warning(f"Failed to remove PID file: {e}")
    
    if listener:
        listener.stop()
    if overlay:
        overlay.hide()
        overlay.root.quit()
    sys.exit(0)

def signal_handler(signum, frame):
    print(f"\nReceived signal {signum} - shutting down gracefully...")
    stop_application()

if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("Starting Roper Code Assistant")
        
        # Create PID file for CLI tracking
        pid_file = "/tmp/roper.pid"
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f"PID file created: {pid_file}")
        
        # Initialize API keys and find working one
        print("🔑 Initializing API keys...")
        initialize_api_keys()
        
        overlay = Overlay()
        logger.info("Overlay initialized")
        
        # Show startup acknowledgment overlay
        overlay.show("Roper", duration=1)
        logger.info("Startup overlay shown")
        
        print("🚀 Roper Code Assistant is running!")
        print("📝 Alt+X: Analyze MCQ questions")
        print("💻 Alt+Z: Generate code solution")
        print("⌨️ Alt+C: Auto-type code (with comments)")
        print("🛑 Escape: Quit")
        print("💡 API keys initialized and tested")
        print("📄 Logs are being written to /tmp/roper.logs")
        
        # Import here to get model info after initialization
        from gemini_api import MCQ_MODEL, CODE_MODEL
        print(f"🤖 Models - MCQ: {MCQ_MODEL}, Code: {CODE_MODEL}")
        
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        logger.info("Keyboard listener started, application ready")
        
        overlay.root.mainloop()
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        print("\nKeyboard interrupt received")
        stop_application()
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        print(f"Error starting application: {e}")
        stop_application()
