# Settings Window
import customtkinter as ctk
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)


class SettingsWindow(ctk.CTkToplevel):
    """Settings configuration window"""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        
        self.config = config_manager
        self.title("Settings - Voice Dictation")
        self.geometry("400x550")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # UI
        self.create_ui()
        
    def create_ui(self):
        """Create the settings UI"""
        # Header
        header = ctk.CTkLabel(self, text="⚙️ Settings", font=("Arial", 20, "bold"))
        header.pack(pady=20)
        
        # API Key
        ctk.CTkLabel(self, text="Groq API Key:", anchor="w").pack(fill="x", padx=30, pady=(10, 5))
        self.api_key_entry = ctk.CTkEntry(self, placeholder_text="gsk_...", show="●")
        self.api_key_entry.pack(fill="x", padx=30)
        self.api_key_entry.insert(0, self.config.get("api_key"))
        
        # Language
        ctk.CTkLabel(self, text="Language:", anchor="w").pack(fill="x", padx=30, pady=(15, 5))
        self.language_var = ctk.StringVar(value=self.config.get("language"))
        language_menu = ctk.CTkOptionMenu(
            self,
            values=["ar", "en"],
            variable=self.language_var
        )
        language_menu.pack(fill="x", padx=30)
        
        # Hotkey info
        ctk.CTkLabel(self, text="💡 Shift+Win+0 to toggle language", 
                     font=("Arial", 10), text_color="gray").pack(pady=5)
        
        # Hotkey Customization
        ctk.CTkLabel(self, text="Recording Hotkey:", anchor="w").pack(fill="x", padx=30, pady=(15, 5))
        self.hotkey_entry = ctk.CTkEntry(self, placeholder_text="e.g., windows+grave")
        self.hotkey_entry.pack(fill="x", padx=30)
        self.hotkey_entry.insert(0, self.config.get("hotkey"))
        ctk.CTkLabel(self, text="ℹ️ Format: modifier+key (e.g., windows+grave for Win+`)", 
                     font=("Arial", 9), text_color="gray").pack(pady=2)
        
        # Silence Duration
        ctk.CTkLabel(self, text="Silence Duration (seconds):", anchor="w").pack(fill="x", padx=30, pady=(15, 5))
        self.silence_slider = ctk.CTkSlider(self, from_=0.5, to=3.0, number_of_steps=25)
        self.silence_slider.set(self.config.get("silence_duration"))
        self.silence_slider.pack(fill="x", padx=30)
        
        self.silence_label = ctk.CTkLabel(self, text=f"{self.config.get('silence_duration'):.1f}s")
        self.silence_label.pack()
        self.silence_slider.configure(command=lambda v: self.silence_label.configure(text=f"{v:.1f}s"))
        
        # Auto-Capitalization
        ctk.CTkLabel(self, text="Text Formatting:", anchor="w").pack(fill="x", padx=30, pady=(15, 5))
        self.auto_capitalize_var = ctk.BooleanVar(value=self.config.get("auto_capitalize", True))
        auto_cap_checkbox = ctk.CTkCheckBox(
            self,
            text="Auto-capitalize sentences",
            variable=self.auto_capitalize_var
        )
        auto_cap_checkbox.pack(fill="x", padx=30)
        
        # Save Button
        save_btn = ctk.CTkButton(self, text="Save Settings", command=self.save_settings, height=40)
        save_btn.pack(pady=30, padx=30, fill="x")
        
    def save_settings(self):
        """Validate and save settings"""
        # Validate inputs
        api_key = self.api_key_entry.get().strip()
        
        if api_key and (not api_key.startswith("gsk_") or len(api_key) < 20):
            messagebox.showerror("Invalid API Key", 
                "API key must start with 'gsk_' and be at least 20 characters long")
            return
        
        language = self.language_var.get()
        if language not in ["ar", "en"]:
            messagebox.showerror("Invalid Language", "Language must be 'ar' or 'en'")
            return
        
        hotkey = self.hotkey_entry.get().strip()
        if hotkey and not self._validate_hotkey(hotkey):
            messagebox.showerror("Invalid Hotkey", 
                "Hotkey format invalid. Use format: modifier+key (e.g., windows+grave, ctrl+shift+r)")
            return
        
        silence_duration = self.silence_slider.get()
        if not (0.5 <= silence_duration <= 3.0):
            messagebox.showerror("Invalid Duration", "Silence duration must be between 0.5 and 3.0 seconds")
            return
        
        # Save if valid
        old_hotkey = self.config.get("hotkey")
        
        self.config.set("api_key", api_key)
        self.config.set("language", language)
        self.config.set("hotkey", hotkey if hotkey else "windows+0")
        self.config.set("silence_duration", silence_duration)
        self.config.set("auto_capitalize", self.auto_capitalize_var.get())
        
        # Re-register hotkey if changed
        if hotkey and hotkey != old_hotkey:
            try:
                import keyboard
                keyboard.remove_hotkey(old_hotkey)
                keyboard.add_hotkey(hotkey, self.master._toggle_from_hotkey)
                logger.info(f"Hotkey changed from {old_hotkey} to {hotkey}")
            except Exception as e:
                logger.warning(f"Could not update hotkey: {e}")
        
        logger.info(f"Settings saved: lang={language}, silence={silence_duration}, auto_cap={self.auto_capitalize_var.get()}")
        self.destroy()
    
    def _validate_hotkey(self, hotkey):
        """Validate hotkey format"""
        # Basic validation: should contain at least one '+' and not be empty
        if not hotkey or '+' not in hotkey:
            return False
        
        parts = hotkey.split('+')
        if len(parts) < 2:
            return False
        
        # Check if modifiers are valid
        valid_modifiers = ['ctrl', 'alt', 'shift', 'windows', 'win', 'cmd']
        for part in parts[:-1]:  # All but last should be modifiers
            if part.lower() not in valid_modifiers:
                return False
        
        # Last part should be a key (non-empty)
        if not parts[-1].strip():
            return False
        
        return True
