import tkinter as tk
from tkinter import messagebox
import os

def save_api_key():
    api_key = entry_api_key.get()
    if not api_key:
        messagebox.showerror("Error", "API key cannot be empty.")
        return

    # Save the API key to the .env file
    with open(".env", "w") as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
    
    window.destroy()

def cancel():
    window.destroy()

# Create the main window
window = tk.Tk()
window.title("Roper - API Key Setup")
window.geometry("400x150")

# Create and pack the widgets
label_api_key = tk.Label(window, text="Please enter your Gemini API key:")
label_api_key.pack(pady=10)

entry_api_key = tk.Entry(window, width=50)
entry_api_key.pack(pady=5)

frame_buttons = tk.Frame(window)
frame_buttons.pack(pady=10)

button_save = tk.Button(frame_buttons, text="Save", command=save_api_key)
button_save.pack(side=tk.LEFT, padx=10)

button_cancel = tk.Button(frame_buttons, text="Cancel", command=cancel)
button_cancel.pack(side=tk.LEFT, padx=10)

window.mainloop()
