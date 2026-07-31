def optimize_code_for_typing(code):
    # Add # at the beginning of every line for safe typing
    lines = code.split('\n')
    commented_lines = []
    
    for line in lines:
        # Strip trailing whitespace but keep the content
        clean_line = line.rstrip()
        if clean_line:
            # Add # at the beginning of non-empty lines
            commented_lines.append(f"# {clean_line}")
        else:
            # For empty lines, just add #
            commented_lines.append("#")
    
    # Return commented code for safe typing
    return '\n'.join(commented_lines)

from pynput import keyboard, mouse
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
CODE_TRIGGER = {keyboard.Key.alt_l, keyboard.KeyCode.from_char('z')}
TYPE_TRIGGER = {keyboard.Key.alt_l, keyboard.KeyCode.from_char('c')}
SETTINGS_TRIGGER_COMMA = {keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.KeyCode.from_char(',')}
SETTINGS_TRIGGER_O = {keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.KeyCode.from_char('o')}

import tempfile
log_path = os.path.join(tempfile.gettempdir(), 'roper.logs')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('roper.main')

current_keys = set()
overlay = None
keyboard_listener = None
mouse_listener = None
running = True
last_code_solution = ""

# Request locking to prevent concurrent requests
request_lock = threading.Lock()
is_processing_mcq = False
is_processing_code = False

# Auto-typing state management
is_typing = False
typing_paused = False
typing_position = 0
typing_text = ""
typing_thread = None

def process_mcq():
    global is_processing_mcq, is_processing_code
    
    # Check if any processing is already in progress
    with request_lock:
        if is_processing_mcq:
            logger.info("MCQ processing already in progress, ignoring new request")
            overlay.show("MCQ analysis in progress...", duration=2)
            return
        if is_processing_code:
            logger.info("Code processing in progress, ignoring MCQ request")
            overlay.show("Code analysis in progress...", duration=2)
            return
        is_processing_mcq = True
    
    try:
        logger.info("MCQ processing started")
        overlay.show("Taking screenshot...", duration=2)
        time.sleep(0.5)  # Brief pause to show message
        
        img_path = take_screenshot()
        logger.info(f"Screenshot taken: {img_path}")
        overlay.show("Analyzing with AI...", duration=5)
        
        answer = ask_gemini(img_path)
        logger.info(f"MCQ answer received: {answer}")
        
        # Always log the MCQ solution to file
        logger.info(f"=== MCQ SOLUTION === {answer} === END MCQ SOLUTION ===")
        
        # Clean up temporary file
        if os.path.exists(img_path):
            os.remove(img_path)
            
        overlay.show(f"{answer}", duration=5)
        logger.info("MCQ processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in process_mcq: {e}")
        overlay.show(f"Error: {str(e)}", duration=3)
        print(f"Error in process_mcq: {e}")
    finally:
        # Always release the lock
        with request_lock:
            is_processing_mcq = False

def clean_code_response(code):
    """Clean AI response to extract pure code"""
    # Remove markdown formatting
    lines = code.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip markdown code blocks
        if line.strip().startswith('```'):
            continue
        # Keep the line as-is without modifying operators
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()

def process_code():
    global last_code_solution, is_processing_mcq, is_processing_code
    
    # Check if any processing is already in progress
    with request_lock:
        if is_processing_code:
            logger.info("Code processing already in progress, ignoring new request")
            overlay.show("Code analysis in progress...", duration=2)
            return
        if is_processing_mcq:
            logger.info("MCQ processing in progress, ignoring code request")
            overlay.show("MCQ analysis in progress...", duration=2)
            return
        is_processing_code = True
    
    try:
        logger.info("Code processing started")
        overlay.show("Taking screenshot...", duration=2)
        time.sleep(0.5)
        
        img_path = take_screenshot()
        logger.info(f"Screenshot taken for code: {img_path}")
        # Check if using pro model for better messaging
        from gemini_api import CODE_MODEL
        if CODE_MODEL == "gemini-2.5-pro":
            overlay.show("Generating optimal solution with Pro model...", duration=15)
        else:
            overlay.show("Generating code solution...", duration=10)
        
        solution = ask_gemini_code(img_path)
        if solution and "error" not in solution.lower() and "fail" not in solution.lower():
            last_code_solution = clean_code_response(solution)
            logger.info(f"Code solution generated successfully, length: {len(last_code_solution)} characters")
            
            # Always log the CODE solution to file
            logger.info(f"=== CODE SOLUTION START ===")
            logger.info(last_code_solution)
            logger.info(f"=== CODE SOLUTION END ===")
        else:
            logger.error(f"Code generation failed: {solution}")
            overlay.show(f"Code generation failed: {solution[:50]}...", duration=5)
            return
        
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
    finally:
        # Always release the lock
        with request_lock:
            is_processing_code = False

def typing_worker():
    """Worker function that handles the actual typing with pause/resume capability"""
    global is_typing, typing_paused, typing_position, typing_text, last_code_solution
    
    from pynput.keyboard import Controller
    kb = Controller()
    
    while is_typing and typing_position < len(typing_text):
        if typing_paused:
            time.sleep(0.1)  # Check pause state frequently
            continue
            
        char = typing_text[typing_position]
        if char == '\n':
            kb.press(keyboard.Key.enter)
            kb.release(keyboard.Key.enter)
        else:
            kb.type(char)
        
        typing_position += 1
        time.sleep(0.015)  # Typing speed
    
    # Typing completed or stopped
    if typing_position >= len(typing_text):
        overlay.show("Elite code typed! Solution cleared.", duration=3)
        logger.info("Auto-type code completed successfully - solution cleared")
        # Clear the solution to prevent re-typing
        last_code_solution = ""
        typing_text = ""
        typing_position = 0
    
    is_typing = False
    typing_paused = False

def toggle_typing():
    """Toggle typing start/pause/resume/stop"""
    global is_typing, typing_paused, typing_position, typing_text, typing_thread, last_code_solution
    
    try:
        if not is_typing:
            # Start new typing session
            if not last_code_solution:
                logger.warning("No code solution available for typing")
                overlay.show("No code to type! Use Alt+Z first", duration=3)
                return
            
            # Prepare text for typing
            typing_text = optimize_code_for_typing(last_code_solution)
            typing_position = 0
            typing_paused = False
            is_typing = True
            
            logger.info(f"Starting to type {len(typing_text)} characters")
            overlay.show("Typing started! Alt+C: pause/resume/stop", duration=2)
            
            # Start typing in separate thread
            typing_thread = threading.Thread(target=typing_worker, daemon=True)
            typing_thread.start()
            
        elif typing_paused:
            # Check if user has been paused for a while - if so, offer to stop
            remaining = len(typing_text) - typing_position
            if remaining > 0:
                logger.info(f"Resuming typing from position {typing_position}, {remaining} characters remaining")
                overlay.show(f"Resumed! {remaining} chars left", duration=2)
                typing_paused = False
            else:
                # Edge case - shouldn't happen but handle it
                stop_typing_and_clear()
            
        else:
            # Currently typing - pause it
            typing_paused = True
            remaining = len(typing_text) - typing_position
            logger.info(f"Typing paused at position {typing_position}, {remaining} characters remaining")
            overlay.show(f"Paused! Alt+C again to resume ({remaining} left)", duration=3)
            
    except Exception as e:
        logger.error(f"Error in toggle_typing: {e}")
        overlay.show(f"Error: {str(e)}", duration=3)
        print(f"Error in toggle_typing: {e}")
        stop_typing_and_clear()

def stop_typing_and_clear():
    """Stop typing and clear the solution"""
    global is_typing, typing_paused, typing_position, typing_text, last_code_solution
    
    is_typing = False
    typing_paused = False
    typing_position = 0
    typing_text = ""
    last_code_solution = ""
    
    logger.info("Typing stopped and solution cleared")
    overlay.show("Typing stopped, solution cleared!", duration=2)

def open_settings_modal():
    from settings_modal import SettingsModal
    def on_settings_saved(new_model):
        if overlay:
            overlay.show(f"Settings saved! Model: {new_model}", duration=3)
    logger.info("Opening settings modal")
    SettingsModal(overlay.root, on_save_callback=on_settings_saved)

def on_press(key):
    global current_keys
    try:
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
            print("Typing toggle activated...")
            threading.Thread(target=toggle_typing, daemon=True).start()
            current_keys.clear()
            return
            
        # Check for Settings triggers
        if key in SETTINGS_TRIGGER_COMMA:
            current_keys.add(key)
        if all(k in current_keys for k in SETTINGS_TRIGGER_COMMA):
            print("Settings trigger (Ctrl+Alt+,) activated...")
            if overlay and overlay.root:
                overlay.root.after(0, open_settings_modal)
            current_keys.clear()
            return
            
        if key in SETTINGS_TRIGGER_O:
            current_keys.add(key)
        if all(k in current_keys for k in SETTINGS_TRIGGER_O):
            print("Settings trigger (Ctrl+Alt+O) activated...")
            if overlay and overlay.root:
                overlay.root.after(0, open_settings_modal)
            current_keys.clear()
            return
            
    except Exception as e:
        print(f"Error in on_press: {e}")

def on_click(x, y, button, pressed):
    """Handle mouse click events"""
    try:
        # Only respond to middle mouse button press (not release)
        if button == mouse.Button.middle and pressed:
            print("Middle mouse button clicked - MCQ trigger activated...")
            threading.Thread(target=process_mcq, daemon=True).start()
    except Exception as e:
        print(f"Error in on_click: {e}")

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
    global running, keyboard_listener, mouse_listener, overlay
    running = False
    
    # Clean up PID file
    pid_file = os.path.join(tempfile.gettempdir(), "roper.pid")
    if os.path.exists(pid_file):
        try:
            os.remove(pid_file)
            logger.info("PID file cleaned up")
        except Exception as e:
            logger.warning(f"Failed to remove PID file: {e}")
    
    # Stop both listeners
    if keyboard_listener:
        keyboard_listener.stop()
    if mouse_listener:
        mouse_listener.stop()
    if overlay:
        overlay.hide()
        overlay.root.quit()
    sys.exit(0)

def signal_handler(signum, frame):
    print(f"\nReceived signal {signum} - shutting down gracefully...")
    stop_application()

if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown (cross-platform)
    try:
        signal.signal(signal.SIGINT, signal_handler)
        if os.name != 'nt':
            signal.signal(signal.SIGTERM, signal_handler)
    except Exception as e:
        logger.debug(f"Failed to set signal handlers: {e}")
        
    try:
        logger.info("Starting Roper Code Assistant")
        
        # Create PID file for CLI tracking
        pid_file = os.path.join(tempfile.gettempdir(), "roper.pid")
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
        print("🖱️  Middle Mouse Button: Analyze MCQ questions")
        print("💻 Alt+Z: Generate code solution (10min timeout)")
        print("⌨️  Alt+C: Auto-type (start/pause/resume)")
        print("⚙️  Ctrl+Alt+, / Ctrl+Alt+O: Open Settings Modal")
        print("🛑 Escape: Quit")
        print("💡 API keys initialized and tested")
        print(f"📄 Logs are being written to {log_path}")
        
        # Import here to get model info after initialization
        from gemini_api import MCQ_MODEL, CODE_MODEL
        print(f"🤖 Models - MCQ: {MCQ_MODEL}, Code: {CODE_MODEL}")
        
        # Start both keyboard and mouse listeners
        keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        mouse_listener = mouse.Listener(on_click=on_click)
        
        keyboard_listener.start()
        mouse_listener.start()
        
        logger.info("Keyboard and mouse listeners started, application ready")
        
        overlay.root.mainloop()
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        print("\nKeyboard interrupt received")
        stop_application()
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        print(f"Error starting application: {e}")
        stop_application()
