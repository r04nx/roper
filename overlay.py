import tkinter as tk
import subprocess
import os
from tkinter import Canvas

class Overlay:
    def __init__(self, message="Processing..."):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.0)  # Initially fully transparent
        self.root.configure(bg='black')
        
        # Create canvas for custom rounded rectangle
        self.canvas = Canvas(
            self.root, 
            highlightthickness=0, 
            bd=0,
            bg='black'
        )
        self.canvas.pack(expand=True, fill='both')
        
        # Store message for later updates
        self.current_message = message
        
        # Initialize canvas elements (will be created in show method)
        self.bg_rect = None
        self.text_item = None
        
        self.root.withdraw()
        
        # Set up click-through properties after window is created
        self.root.after(100, self.setup_click_through)

    def setup_click_through(self):
        """Make the overlay click-through when not showing messages"""
        try:
            window_id = self.root.winfo_id()
            # Set window properties for better behavior
            subprocess.run([
                'wmctrl', '-i', '-r', str(window_id),
                '-b', 'add,skip_taskbar,skip_pager'
            ], check=False, capture_output=True)
        except Exception as e:
            pass  # Silently fail if wmctrl is not available

    def show(self, message=None, duration=3):
        if message:
            self.current_message = message
        
        # Use a temporary label to measure text size (smaller font)
        temp_label = tk.Label(self.root, text=self.current_message, font=("Arial", 7, "normal"))
        temp_label.update_idletasks()
        text_width = temp_label.winfo_reqwidth()
        text_height = temp_label.winfo_reqheight()
        temp_label.destroy()
        
        # Calculate total window dimensions with padding (further reduced)
        padding = 2
        width = text_width + padding * 2
        height = text_height + padding * 2
        
        # Position in top-right corner
        screen_width = self.root.winfo_screenwidth()
        x_pos = screen_width - width - 20
        y_pos = 20
        
        # Set window geometry first
        self.root.geometry(f'{width}x{height}+{x_pos}+{y_pos}')
        
        # Update canvas size
        self.canvas.config(width=width, height=height)
        
        # Clear previous drawings
        self.canvas.delete("all")
        
        # Create soft rounded rectangle background
        self.bg_rect = self.rounded_rectangle(
            2, 2, width-2, height-2, 
            radius=12, 
            fill="#3a3a3a",  # Softer dark color
            outline="#4a4a4a",  # Subtle border
            outline_width=1
        )
        
        # Add text centered in the rounded rectangle
        center_x = width // 2
        center_y = height // 2
        self.text_item = self.canvas.create_text(
            center_x, center_y, 
            text=self.current_message, 
            font=("Arial", 7, "normal"), 
            anchor="center", 
            fill='white'
        )
        
        # Show window with soft transparency
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-alpha', 0.3)  # 70% transparency (0.3 opacity)
        
        # Hide after duration
        self.root.after(int(duration * 1000), self.hide)

    def rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        # Handle outline_width parameter
        outline_width = kwargs.pop('outline_width', 1)
        
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.canvas.create_polygon(points, width=outline_width, **kwargs, smooth=True)


    def hide(self):
        self.root.withdraw()
        self.root.attributes('-alpha', 0.0)  # Hide with full transparency

    def destroy(self):
        """Properly destroy the overlay"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
