#!/usr/bin/env python3
import subprocess
import os
import sys

def setup_keyboard_shortcut():
    """Set up Ctrl+Alt+` keyboard shortcut for overlay toggle"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    toggle_script = os.path.join(script_dir, "toggle_overlay.py")
    
    # Command to execute - use the new toggle_roper.py
    new_toggle_script = os.path.join(script_dir, "toggle_roper.py")
    command = f"python3 {new_toggle_script}"
    
    print("Setting up keyboard shortcut: Ctrl+Alt+`")
    print(f"Command: {command}")
    
    try:
        # For Linux Mint with Cinnamon desktop
        # Check if we're running Cinnamon
        result = subprocess.run(
            ["pgrep", "-x", "cinnamon"],
            capture_output=True
        )
        
        if result.returncode == 0:
            print("Detected Cinnamon desktop environment")
            setup_cinnamon_shortcut(command)
        else:
            print("Cinnamon not detected, trying GNOME/generic method")
            setup_gnome_shortcut(command)
            
    except Exception as e:
        print(f"Error setting up shortcut: {e}")
        print("\nManual setup instructions:")
        print("1. Open System Settings")
        print("2. Go to Keyboard > Shortcuts")
        print("3. Add a custom shortcut:")
        print(f"   Name: Toggle Overlay")
        print(f"   Command: {command}")
        print(f"   Shortcut: Ctrl+Alt+`")

def setup_cinnamon_shortcut(command):
    """Set up shortcut for Cinnamon desktop"""
    try:
        # Get current custom keybindings
        result = subprocess.run([
            "dconf", "read", "/org/cinnamon/desktop/keybindings/custom-list"
        ], capture_output=True, text=True)
        
        # Parse existing keybindings
        if result.stdout.strip() == "" or result.stdout.strip() == "@as []":
            custom_list = []
        else:
            # Remove brackets and quotes, split by comma
            content = result.stdout.strip().strip("[]").replace("'", "")
            if content:
                custom_list = [item.strip() for item in content.split(",")]
            else:
                custom_list = []
        
        # Add our new keybinding
        new_binding = "custom0"
        if new_binding not in custom_list:
            custom_list.append(new_binding)
        
        # Update the custom list
        list_str = "[" + ", ".join(f"'{item}'" for item in custom_list) + "]"
        subprocess.run([
            "dconf", "write", "/org/cinnamon/desktop/keybindings/custom-list",
            list_str
        ])
        
        # Set the command
        subprocess.run([
            "dconf", "write", f"/org/cinnamon/desktop/keybindings/custom-keybindings/{new_binding}/command",
            f"'{command}'"
        ])
        
        # Set the binding key
        subprocess.run([
            "dconf", "write", f"/org/cinnamon/desktop/keybindings/custom-keybindings/{new_binding}/binding",
            "['<Primary><Alt>grave']"
        ])
        
        # Set the name
        subprocess.run([
            "dconf", "write", f"/org/cinnamon/desktop/keybindings/custom-keybindings/{new_binding}/name",
            "'Toggle Overlay'"
        ])
        
        print("✓ Keyboard shortcut set up successfully!")
        print("✓ Press Ctrl+Alt+` to toggle the overlay")
        
    except Exception as e:
        print(f"Failed to set up Cinnamon shortcut: {e}")
        fallback_instructions(command)

def setup_gnome_shortcut(command):
    """Set up shortcut for GNOME-based systems"""
    try:
        # Try to set up using gsettings
        subprocess.run([
            "gsettings", "set", "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/",
            "name", "'Toggle Overlay'"
        ])
        
        subprocess.run([
            "gsettings", "set", "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/",
            "command", f"'{command}'"
        ])
        
        subprocess.run([
            "gsettings", "set", "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/",
            "binding", "'<Primary><Alt>grave'"
        ])
        
        # Add to the list
        subprocess.run([
            "gsettings", "set", "org.gnome.settings-daemon.plugins.media-keys",
            "custom-keybindings", "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/']"
        ])
        
        print("✓ Keyboard shortcut set up successfully!")
        print("✓ Press Ctrl+Alt+` to toggle the overlay")
        
    except Exception as e:
        print(f"Failed to set up GNOME shortcut: {e}")
        fallback_instructions(command)

def fallback_instructions(command):
    """Show manual setup instructions"""
    print("\n" + "="*50)
    print("MANUAL SETUP REQUIRED")
    print("="*50)
    print("Please set up the keyboard shortcut manually:")
    print("\n1. Open System Settings")
    print("2. Navigate to Keyboard → Shortcuts (or Keyboard → Custom Shortcuts)")
    print("3. Click 'Add' or '+' to create a new custom shortcut")
    print("4. Fill in the details:")
    print(f"   Name: Toggle Overlay")
    print(f"   Command: {command}")
    print(f"   Key combination: Ctrl+Alt+` (grave/backtick)")
    print("\n5. Save and test the shortcut")

def main():
    print("Overlay Keyboard Shortcut Setup")
    print("=" * 40)
    
    # Check if required files exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    toggle_script = os.path.join(script_dir, "toggle_overlay.py")
    overlay_script = os.path.join(script_dir, "transparent_overlay_enhanced.py")
    
    if not os.path.exists(toggle_script):
        print(f"Error: {toggle_script} not found!")
        sys.exit(1)
    
    if not os.path.exists(overlay_script):
        print(f"Error: {overlay_script} not found!")
        sys.exit(1)
    
    setup_keyboard_shortcut()
    
    print("\n" + "="*50)
    print("SETUP COMPLETE!")
    print("="*50)
    print("You can now use:")
    print("• Ctrl+Alt+` to toggle the overlay on/off")
    print(f"• python3 {toggle_script} start/stop/status")
    print("\nThe overlay will show 'Hello World' in the top-left corner")
    print("and should be click-through and always on top.")

if __name__ == "__main__":
    main()
