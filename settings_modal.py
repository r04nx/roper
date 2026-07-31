import tkinter as tk
from tkinter import ttk
import threading
import os
import requests
import logging

logger = logging.getLogger('roper.settings_modal')

class SettingsModal:
    def __init__(self, parent, on_save_callback=None):
        self.parent = parent
        self.on_save_callback = on_save_callback
        self.fetch_timer_id = None
        self.current_mcq_model = "gemini-2.0-flash"
        
        # Default models list
        self.all_fetched_models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        
        # Load environment values
        self.env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        self.current_api_key = ""
        self.load_current_settings()

        # Create TopLevel window
        self.window = tk.Toplevel(parent)
        self.window.title("Roper Settings")
        self.window.configure(bg='#1e1e1e')
        
        # Glassmorphic semi-transparent effect
        self.window.attributes('-alpha', 0.90)
        
        # Size and Position (Centered)
        window_width = 460
        window_height = 340
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Ensure the window is always on top, lifted, and focused
        self.window.attributes('-topmost', True)
        self.window.lift()
        self.window.focus_force()
        
        # Custom TTK Style for Combobox
        self.setup_ttk_style()
        
        # Build UI
        self.create_widgets()
        
        # If API key already exists, auto-fetch models immediately on startup
        if self.current_api_key:
            self.trigger_model_fetch()

    def load_current_settings(self):
        if os.path.exists(self.env_path):
            with open(self.env_path, 'r') as f:
                for line in f:
                    clean = line.strip()
                    if clean.startswith("GEMINI_API_KEY="):
                        self.current_api_key = clean.split("=", 1)[1].strip()
                    elif clean.startswith("MCQ_MODEL="):
                        self.current_mcq_model = clean.split("=", 1)[1].strip()

    def setup_ttk_style(self):
        style = ttk.Style(self.window)
        style.theme_use('clam')
        style.configure(
            'TCombobox',
            fieldbackground='#2d2d2d',
            background='#2d2d2d',
            foreground='white',
            arrowcolor='white',
            bordercolor='#4a4a4a',
            lightcolor='#4a4a4a',
            darkcolor='#4a4a4a'
        )
        style.map('TCombobox',
            fieldbackground=[('readonly', '#2d2d2d'), ('!disabled', '#2d2d2d')],
            foreground=[('readonly', 'white'), ('!disabled', 'white')]
        )
        self.window.option_add('*TCombobox*Listbox.background', '#2d2d2d')
        self.window.option_add('*TCombobox*Listbox.foreground', 'white')
        self.window.option_add('*TCombobox*Listbox.selectBackground', '#00aa5f')
        self.window.option_add('*TCombobox*Listbox.selectForeground', 'white')
        self.window.option_add('*TCombobox*Entry.background', '#2d2d2d')
        self.window.option_add('*TCombobox*Entry.foreground', 'white')
        self.window.option_add('*TCombobox*Entry.selectBackground', '#00aa5f')
        self.window.option_add('*TCombobox*Entry.selectForeground', 'white')

    def create_widgets(self):
        # Outer container with padding
        container = tk.Frame(self.window, bg='#1e1e1e', padx=20, pady=20)
        container.pack(fill='both', expand=True)

        # Header Title
        title_label = tk.Label(
            container,
            text="Roper Configuration",
            font=("Arial", 14, "bold"),
            fg="white",
            bg='#1e1e1e'
        )
        title_label.pack(anchor='w', pady=(0, 15))

        # API Key Section
        api_label = tk.Label(
            container,
            text="Gemini API Key:",
            font=("Arial", 10, "bold"),
            fg="#e0e0e0",
            bg='#1e1e1e'
        )
        api_label.pack(anchor='w', pady=(0, 5))

        self.api_key_var = tk.StringVar(value=self.current_api_key)
        self.api_key_var.trace_add("write", self.on_api_key_changed)

        self.api_entry = tk.Entry(
            container,
            textvariable=self.api_key_var,
            font=("Arial", 10),
            bg='#2d2d2d',
            fg='white',
            insertbackground='white',
            relief='flat',
            highlightthickness=1,
            highlightbackground='#4a4a4a',
            highlightcolor='#00aa5f',
            width=50
        )
        self.api_entry.pack(fill='x', ipady=6, pady=(0, 15))

        # Model Select Section
        model_label = tk.Label(
            container,
            text="Select AI Model:",
            font=("Arial", 10, "bold"),
            fg="#e0e0e0",
            bg='#1e1e1e'
        )
        model_label.pack(anchor='w', pady=(0, 5))

        self.model_combobox = ttk.Combobox(
            container,
            values=self.all_fetched_models,
            font=("Arial", 10),
            state="normal"
        )
        if self.current_mcq_model in self.all_fetched_models:
            self.model_combobox.set(self.current_mcq_model)
        else:
            self.model_combobox.set("gemini-2.0-flash")
            
        self.model_combobox.pack(fill='x', ipady=4, pady=(0, 10))
        self.model_combobox.bind("<KeyRelease>", self.on_combobox_keyrelease)
        self.model_combobox.bind("<Button-1>", self.on_combobox_click)

        # Status indicator
        self.status_label = tk.Label(
            container,
            text="Waiting for API Key...",
            font=("Arial", 9),
            fg="#888888",
            bg='#1e1e1e'
        )
        self.status_label.pack(anchor='w', pady=(0, 15))

        # Action Buttons Frame
        btn_frame = tk.Frame(container, bg='#1e1e1e')
        btn_frame.pack(fill='x', side='bottom')

        save_btn = tk.Button(
            btn_frame,
            text="Save Settings",
            font=("Arial", 10, "bold"),
            bg='#00aa5f',
            fg='white',
            activebackground='#008f4f',
            activeforeground='white',
            relief='flat',
            bd=0,
            command=self.save_settings,
            cursor="hand2"
        )
        save_btn.pack(side='right', padx=(10, 0), ipadx=15, ipady=6)

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 10),
            bg='#3a3a3a',
            fg='white',
            activebackground='#4a4a4a',
            activeforeground='white',
            relief='flat',
            bd=0,
            command=self.close,
            cursor="hand2"
        )
        cancel_btn.pack(side='right', ipadx=15, ipady=6)

    def on_api_key_changed(self, *args):
        # Debounce model fetch by 500ms to avoid querying API during active typing
        if self.fetch_timer_id:
            self.window.after_cancel(self.fetch_timer_id)
            self.fetch_timer_id = None
        self.fetch_timer_id = self.window.after(500, self.trigger_model_fetch)

    def trigger_model_fetch(self):
        api_key = self.api_key_var.get().strip()
        if len(api_key) < 30:
            self.status_label.config(text="API key format invalid or too short", fg="#ffaa00")
            return
            
        self.status_label.config(text="Fetching available models from Gemini...", fg="#00aaff")
        threading.Thread(target=self.async_fetch_models, args=(api_key,), daemon=True).start()

    def async_fetch_models(self, api_key):
        from gemini_api import fetch_available_models
        models = fetch_available_models(api_key)
        self.window.after(0, self.update_models_list, models)

    def update_models_list(self, models):
        if models:
            self.model_combobox['values'] = models
            self.status_label.config(text=f"Fetched {len(models)} models successfully!", fg="#00ff00")
            
            # Reset selection if the current model doesn't exist in the fetched list
            selected = self.model_combobox.get()
            if selected not in models:
                if self.current_mcq_model in models:
                    self.model_combobox.set(self.current_mcq_model)
                else:
                    # Prefer gemini-2.0-flash if it's there
                    if "gemini-2.0-flash" in models:
                        self.model_combobox.set("gemini-2.0-flash")
                    else:
                        self.model_combobox.set(models[0])
        else:
            self.status_label.config(text="Failed to retrieve models. Check key/network.", fg="#ff5555")

    def save_settings(self):
        api_key = self.api_key_var.get().strip()
        selected_model = self.model_combobox.get()

        if not api_key:
            self.status_label.config(text="Error: API Key cannot be empty!", fg="#ff5555")
            return

        try:
            # Update .env lines safely
            lines = []
            if os.path.exists(self.env_path):
                with open(self.env_path, 'r') as f:
                    lines = f.readlines()

            updated_key = False
            updated_mcq = False
            updated_code = False

            for i, line in enumerate(lines):
                clean = line.strip()
                if clean.startswith("GEMINI_API_KEY="):
                    lines[i] = f"GEMINI_API_KEY={api_key}\n"
                    updated_key = True
                elif clean.startswith("MCQ_MODEL="):
                    lines[i] = f"MCQ_MODEL={selected_model}\n"
                    updated_mcq = True
                elif clean.startswith("CODE_MODEL="):
                    lines[i] = f"CODE_MODEL={selected_model}\n"
                    updated_code = True

            if not updated_key:
                lines.append(f"\nGEMINI_API_KEY={api_key}\n")
            if not updated_mcq:
                lines.append(f"MCQ_MODEL={selected_model}\n")
            if not updated_code:
                lines.append(f"CODE_MODEL={selected_model}\n")

            with open(self.env_path, 'w') as f:
                f.writelines(lines)

            # Reload parameters in memory
            from gemini_api import reload_configuration
            reload_configuration()

            if self.on_save_callback:
                self.on_save_callback(selected_model)

            self.close()

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            self.status_label.config(text=f"Save Error: {str(e)}", fg="#ff5555")

    def on_combobox_keyrelease(self, event):
        # Ignore navigation/control keys
        if event.keysym in ["Up", "Down", "Return", "Escape", "Left", "Right", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Tab"]:
            return
            
        typed = self.model_combobox.get().strip().lower()
        if typed == "":
            filtered = self.all_fetched_models
        else:
            filtered = [m for m in self.all_fetched_models if typed in m.lower()]
            
        self.model_combobox['values'] = filtered
        
        # Auto-open dropdown popup showing only filtered options
        try:
            self.model_combobox.event_generate('<Down>')
        except:
            pass

    def on_combobox_click(self, event):
        self.window.after(50, lambda: self.model_combobox.event_generate('<Down>'))

    def close(self):
        try:
            self.window.grab_release()
            self.window.destroy()
        except:
            pass
