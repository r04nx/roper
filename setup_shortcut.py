#!/usr/bin/env python3
import subprocess
import os
import sys

def setup_keyboard_shortcut():
    """Set up Ctrl+Alt+` keyboard shortcut for overlay toggle"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    toggle_script = os.path.join(script_dir, "toggle_overlay.py")
    
    # Command to execute - use roper CLI toggle
    roper_cli = os.path.join(script_dir, "roper_cli")
    command = f"{roper_cli} toggle"
    
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
    print("Roper Keyboard Shortcut Setup")
    print("=" * 40)
    
    # Use roper CLI for shortcuts instead of old overlay files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    roper_cli = os.path.join(script_dir, "roper_cli")
    
    if not os.path.exists(roper_cli):
        print(f"Error: {roper_cli} not found!")
        sys.exit(1)
    
    setup_keyboard_shortcut()
    
    print("\n" + "="*50)
    print("SETUP COMPLETE!")
    print("="*50)
    print("You can now use:")
    print("• Ctrl+Alt+` to toggle Roper on/off")
    print("• Alt+X to analyze MCQ questions")
    print("• Alt+Z to generate code solutions")
    print("• Alt+C to auto-type code")
    print("• roper start/stop/status from CLI")

if __name__ == "__main__":
    main()
