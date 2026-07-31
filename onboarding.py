#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import threading
import os
import requests
import logging
import subprocess

import tempfile
log_path = os.path.join(tempfile.gettempdir(), 'roper.logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('roper.onboarding')

class OnboardingWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Roper Onboarding Setup")
        self.root.configure(bg='#1e1e1e')
        
        # Glassmorphic transparency
        self.root.attributes('-alpha', 0.95)
        self.root.attributes('-topmost', True)
        
        # Center the window
        window_width = 540
        window_height = 420
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Initialize variables
        self.env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        self.current_api_key = ""
        self.current_mcq_model = "gemini-2.0-flash"
        self.all_fetched_models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        self.fetch_timer_id = None
        
        self.load_current_settings()
        self.setup_ttk_style()
        
        # Slide containers
        self.slide_frame = tk.Frame(self.root, bg='#1e1e1e')
        self.slide_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Start on Slide 1
        self.show_slide_1()

    def load_current_settings(self):
        if os.path.exists(self.env_path):
            try:
                with open(self.env_path, 'r') as f:
                    for line in f:
                        clean = line.strip()
                        if clean.startswith("GEMINI_API_KEY="):
                            self.current_api_key = clean.split("=", 1)[1].strip()
                        elif clean.startswith("MCQ_MODEL="):
                            self.current_mcq_model = clean.split("=", 1)[1].strip()
            except Exception as e:
                logger.error(f"Failed to read existing .env: {e}")

    def setup_ttk_style(self):
        style = ttk.Style(self.root)
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
        self.root.option_add('*TCombobox*Listbox.background', '#2d2d2d')
        self.root.option_add('*TCombobox*Listbox.foreground', 'white')
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#00aa5f')
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')
        self.root.option_add('*TCombobox*Entry.background', '#2d2d2d')
        self.root.option_add('*TCombobox*Entry.foreground', 'white')
        self.root.option_add('*TCombobox*Entry.selectBackground', '#00aa5f')
        self.root.option_add('*TCombobox*Entry.selectForeground', 'white')

    def clear_slide(self):
        for widget in self.slide_frame.winfo_children():
            widget.destroy()

    def show_slide_1(self):
        self.clear_slide()
        
        # Welcome Title
        title_label = tk.Label(
            self.slide_frame,
            text="🚀 Welcome to Roper MCQ & Code Solver",
            font=("Arial", 16, "bold"),
            fg="white",
            bg='#1e1e1e'
        )
        title_label.pack(anchor='w', pady=(0, 20))
        
        # Description
        desc_label = tk.Label(
            self.slide_frame,
            text="Roper is installed successfully! Here is a guide to your configured shortcuts:",
            font=("Arial", 10),
            fg="#cccccc",
            bg='#1e1e1e',
            wraplength=480,
            justify='left'
        )
        desc_label.pack(anchor='w', pady=(0, 20))
        
        # Shortcuts Frame
        shortcut_container = tk.Frame(self.slide_frame, bg='#282828', bd=1, relief='flat', padx=15, pady=15)
        shortcut_container.pack(fill='x', pady=(0, 25))
        
        shortcuts = [
            ("🖱️  Middle Mouse Click", "Capture screen & solve MCQ question in real-time"),
            ("💻  Alt + Z", "Capture screen & generate optimized code solution"),
            ("⌨️  Alt + C", "Auto-type the generated code (prefixed with # for safety)"),
            ("⚙️  Ctrl+Alt+,  or  Ctrl+Alt+O", "Open settings modal to change key or model")
        ]
        
        for key, desc in shortcuts:
            row = tk.Frame(shortcut_container, bg='#282828', pady=4)
            row.pack(fill='x')
            
            lbl_key = tk.Label(row, text=key, font=("Arial", 9, "bold"), fg="#00aa5f", bg='#282828', width=24, anchor='w')
            lbl_key.pack(side='left')
            
            lbl_desc = tk.Label(row, text=desc, font=("Arial", 9), fg="white", bg='#282828', anchor='w')
            lbl_desc.pack(side='left', fill='x', expand=True)
            
        # Navigation
        btn_frame = tk.Frame(self.slide_frame, bg='#1e1e1e')
        btn_frame.pack(fill='x', side='bottom')
        
        next_btn = tk.Button(
            btn_frame,
            text="Next: Setup API Key ➔",
            font=("Arial", 10, "bold"),
            bg='#00aa5f',
            fg='white',
            activebackground='#008f4f',
            activeforeground='white',
            relief='flat',
            bd=0,
            command=self.show_slide_2,
            cursor="hand2"
        )
        next_btn.pack(side='right', ipadx=20, ipady=8)

    def show_slide_2(self):
        self.clear_slide()
        
        # Title
        title_label = tk.Label(
            self.slide_frame,
            text="🔑 Gemini API Configuration",
            font=("Arial", 16, "bold"),
            fg="white",
            bg='#1e1e1e'
        )
        title_label.pack(anchor='w', pady=(0, 20))
        
        # API Key Label & Input
        api_label = tk.Label(
            self.slide_frame,
            text="Gemini API Key:",
            font=("Arial", 10, "bold"),
            fg="#e0e0e0",
            bg='#1e1e1e'
        )
        api_label.pack(anchor='w', pady=(0, 5))
        
        self.api_key_var = tk.StringVar(value=self.current_api_key)
        self.api_key_var.trace_add("write", self.on_api_key_changed)
        
        self.api_entry = tk.Entry(
            self.slide_frame,
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
        self.api_entry.pack(fill='x', ipady=6, pady=(0, 20))
        
        # Model selection
        model_label = tk.Label(
            self.slide_frame,
            text="Select AI Model:",
            font=("Arial", 10, "bold"),
            fg="#e0e0e0",
            bg='#1e1e1e'
        )
        model_label.pack(anchor='w', pady=(0, 5))
        
        self.model_combobox = ttk.Combobox(
            self.slide_frame,
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
        
        # Status Label
        self.status_label = tk.Label(
            self.slide_frame,
            text="Waiting for API Key..." if not self.current_api_key else "Fetching available models...",
            font=("Arial", 9),
            fg="#888888",
            bg='#1e1e1e'
        )
        self.status_label.pack(anchor='w', pady=(0, 20))
        
        # Navigation
        btn_frame = tk.Frame(self.slide_frame, bg='#1e1e1e')
        btn_frame.pack(fill='x', side='bottom')
        
        finish_btn = tk.Button(
            btn_frame,
            text="Finish & Start Roper ✔",
            font=("Arial", 10, "bold"),
            bg='#00aa5f',
            fg='white',
            activebackground='#008f4f',
            activeforeground='white',
            relief='flat',
            bd=0,
            command=self.finish_setup,
            cursor="hand2"
        )
        finish_btn.pack(side='right', ipadx=20, ipady=8)
        
        back_btn = tk.Button(
            btn_frame,
            text="◀ Back",
            font=("Arial", 10),
            bg='#3a3a3a',
            fg='white',
            activebackground='#4a4a4a',
            activeforeground='white',
            relief='flat',
            bd=0,
            command=self.show_slide_1,
            cursor="hand2"
        )
        back_btn.pack(side='left', ipadx=20, ipady=8)
        
        # Trigger fetch immediately if key exists
        if self.current_api_key:
            self.trigger_model_fetch()

    def on_api_key_changed(self, *args):
        if self.fetch_timer_id:
            self.root.after_cancel(self.fetch_timer_id)
            self.fetch_timer_id = None
        self.fetch_timer_id = self.root.after(500, self.trigger_model_fetch)

    def trigger_model_fetch(self):
        api_key = self.api_key_var.get().strip()
        if len(api_key) < 30:
            self.status_label.config(text="API key format invalid or too short", fg="#ffaa00")
            return
            
        self.status_label.config(text="Fetching available models from Gemini...", fg="#00aaff")
        threading.Thread(target=self.async_fetch_models, args=(api_key,), daemon=True).start()

    def async_fetch_models(self, api_key):
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key.strip()}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                models_list = []
                for m in data.get("models", []):
                    if "generateContent" in m.get("supportedGenerationMethods", []):
                        name = m.get("name", "")
                        if name.startswith("models/"):
                            name = name[len("models/"):]
                        models_list.append(name)
                models_list = sorted(models_list)
                self.root.after(0, self.update_models_list, models_list, True)
            else:
                self.root.after(0, self.update_models_list, [], False)
        except Exception as e:
            logger.error(f"Error fetching models in onboarding: {e}")
            self.root.after(0, self.update_models_list, [], False)

    def update_models_list(self, models, success):
        if success and models:
            self.all_fetched_models = models
            self.model_combobox['values'] = models
            self.status_label.config(text=f"Fetched {len(models)} models successfully!", fg="#00ff00")
            
            selected = self.model_combobox.get()
            if selected not in models:
                if self.current_mcq_model in models:
                    self.model_combobox.set(self.current_mcq_model)
                else:
                    if "gemini-2.0-flash" in models:
                        self.model_combobox.set("gemini-2.0-flash")
                    else:
                        self.model_combobox.set(models[0])
        else:
            self.status_label.config(text="Failed to retrieve models. Check key/network.", fg="#ff5555")

    def on_combobox_keyrelease(self, event):
        if event.keysym in ["Up", "Down", "Return", "Escape", "Left", "Right", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Tab"]:
            return
            
        typed = self.model_combobox.get().strip().lower()
        if typed == "":
            filtered = self.all_fetched_models
        else:
            filtered = [m for m in self.all_fetched_models if typed in m.lower()]
            
        self.model_combobox['values'] = filtered
        try:
            self.model_combobox.event_generate('<Down>')
        except:
            pass

    def on_combobox_click(self, event):
        self.root.after(50, lambda: self.model_combobox.event_generate('<Down>'))

    def finish_setup(self):
        api_key = self.api_key_var.get().strip()
        selected_model = self.model_combobox.get().strip()
        
        if not api_key:
            self.status_label.config(text="Error: API Key cannot be empty!", fg="#ff5555")
            return
            
        try:
            # Save to .env
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
                
            # Start Roper service
            if os.name == 'nt':
                bat_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'roper.bat')
                if os.path.exists(bat_path):
                    subprocess.run([bat_path, "start"], capture_output=True, shell=True)
                    logger.info("Roper started on Windows from onboarding setup")
            else:
                cli_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'roper_cli')
                if os.path.exists(cli_path):
                    subprocess.run([cli_path, "start"], capture_output=True)
                    logger.info("Roper started from onboarding setup")
                
            # Show completed screen
            self.show_completed_slide()
            
        except Exception as e:
            logger.error(f"Failed in finish_setup: {e}")
            self.status_label.config(text=f"Setup Error: {str(e)}", fg="#ff5555")

    def show_completed_slide(self):
        self.clear_slide()
        
        title_label = tk.Label(
            self.slide_frame,
            text="✨ Setup Complete!",
            font=("Arial", 18, "bold"),
            fg="#00aa5f",
            bg='#1e1e1e'
        )
        title_label.pack(anchor='center', pady=(30, 20))
        
        success_label = tk.Label(
            self.slide_frame,
            text="Roper has been configured and started successfully in the background!\n\n"
                 "To manage the assistant service, use these terminal commands:\n"
                 "• roper start   - Start the service\n"
                 "• roper stop    - Stop the service\n"
                 "• roper status  - Check running status\n\n"
                 "Usage: Alt+Z (Solve Code), Alt+C (Type Code), Middle-Click (Solve MCQ)",
            font=("Arial", 10),
            fg="white",
            bg='#1e1e1e',
            wraplength=440,
            justify='center'
        )
        success_label.pack(anchor='center', pady=(0, 30))
        
        close_btn = tk.Button(
            self.slide_frame,
            text="Close Wizard",
            font=("Arial", 11, "bold"),
            bg='#00aa5f',
            fg='white',
            activebackground='#008f4f',
            activeforeground='white',
            relief='flat',
            bd=0,
            command=self.root.destroy,
            cursor="hand2"
        )
        close_btn.pack(anchor='center', ipadx=30, ipady=10)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    wizard = OnboardingWizard()
    wizard.run()
