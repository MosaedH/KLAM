# Main Dictation Widget
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
import math
import os
import logging
import pyperclip
import pyautogui
import keyboard
import pygame
from ctypes import windll, byref, Structure, c_long
import win32gui
import pystray
from PIL import Image, ImageDraw

from utils.constants import *
from config import ConfigManager
from core import AudioRecorder, Transcriber
from ui.visualizer import AudioVisualizer
from ui.settings import SettingsWindow

logger = logging.getLogger(__name__)

# Apply theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class DictationWidget(ctk.CTk):
    """Main voice dictation widget"""
    
    def __init__(self):
        super().__init__()
        
        logger.info("Starting Voice Dictation Widget")
        
        # Config
        self.config = ConfigManager()
        
        # Window setup
        self._setup_window()
        
        # State
        self.is_visible = False
        self.error_flash_count = 0
        self.prev_window = None
        self.is_shutting_down = False
        
        # Drag and drop state
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        
        # Audio quality warning
        self.show_low_volume_warning = False
        
        # Components
        self.recorder = AudioRecorder(SAMPLE_RATE, CHANNELS, BLOCK_SIZE)
        self.transcriber = Transcriber(
            self.config.get("api_key"),
            self.config.get("language")
        )
        
        # UI
        self._create_ui()
        
        # Bind drag events
        self._bind_drag_events()
        
        # Sound
        self._init_sound()
        
        # Hotkeys
        self._register_hotkeys()
        
        # Start hidden
        self.withdraw()
        
        # Animations
        self._pulse_indicator()
        
        # System Tray
        self.setup_tray()
        
        # Exit handler
        self.protocol("WM_DELETE_WINDOW", self._exit_app)
    
    def _setup_window(self):
        """Configure window properties"""
        self.title("")
        self.geometry(f"{WIDGET_WIDTH}x{WIDGET_HEIGHT}")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-toolwindow", True)
        self.configure(fg_color=TRANSPARENT_KEY)
        self.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        self.wm_attributes("-alpha", 0.95)
        self._position_widget()
    
    def _create_ui(self):
        """Create main UI elements"""
        # Main container
        self.container = ctk.CTkFrame(
            self,
            width=WIDGET_WIDTH,
            height=WIDGET_HEIGHT,
            corner_radius=CORNER_RADIUS,
            fg_color=GLASS_BG,
            border_width=1,
            border_color=GLASS_BORDER,
            bg_color=TRANSPARENT_KEY
        )
        self.container.pack(fill="both", expand=True)
        self.container.pack_propagate(False)
        
        # Inner layout
        self.inner = ctk.CTkFrame(self.container, fg_color="transparent")
        self.inner.pack(fill="both", expand=True, padx=int(12*DPI_SCALE), pady=int(8*DPI_SCALE))
        
        # Left side: Indicator + Language
        left_frame = ctk.CTkFrame(self.inner, fg_color="transparent")
        left_frame.pack(side="left", padx=(0, int(8*DPI_SCALE)))
        
        # Recording indicator
        self.indicator = ctk.CTkLabel(
            left_frame,
            text="●",
            font=("Arial", int(24*DPI_SCALE)),
            text_color=ACCENT_COLOR,
            fg_color="transparent"
        )
        self.indicator.pack(side="left")
        
        # Language indicator
        self.lang_indicator = ctk.CTkLabel(
            left_frame,
            text=self.config.get("language").upper(),
            font=("Arial", int(11*DPI_SCALE), "bold"),
            text_color="#a0a0c0",
            fg_color="transparent"
        )
        self.lang_indicator.pack(side="left", padx=(int(2*DPI_SCALE), 0))
        
        # Low volume warning indicator (initially hidden)
        self.warning_indicator = ctk.CTkLabel(
            left_frame,
            text="⚠️",
            font=("Arial", int(16*DPI_SCALE)),
            text_color=ERROR_COLOR,
            fg_color="transparent"
        )
        # Don't pack initially - will show/hide dynamically
        
        # Audio visualizer
        self.visualizer = AudioVisualizer(
            self.inner,
            width=int(120*DPI_SCALE),
            height=int(36*DPI_SCALE),
            bg_color=GLASS_BG
        )
        self.visualizer.pack(side="left", fill="y", expand=True)
    
    def _init_sound(self):
        """Initialize sound effects"""
        try:
            pygame.mixer.init()
            # Get parent directory (project root) not ui/ directory
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sound_path = os.path.join(project_root, "beep.mp3")
            if os.path.exists(sound_path):
                self.beep_sound = pygame.mixer.Sound(sound_path)
                logger.info(f"Sound loaded from: {sound_path}")
            else:
                self.beep_sound = None
                logger.warning(f"beep.mp3 not found at: {sound_path}")
        except Exception as e:
            logger.error(f"Sound init error: {e}")
            self.beep_sound = None
    
    def _bind_drag_events(self):
        """Bind drag-and-drop events to container"""
        # Bind to main window
        self.bind("<Button-1>", self._start_drag)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._end_drag)
        
        # Also bind to container and inner frame for better coverage
        self.container.bind("<Button-1>", self._start_drag)
        self.container.bind("<B1-Motion>", self._on_drag)
        self.container.bind("<ButtonRelease-1>", self._end_drag)
        
        self.inner.bind("<Button-1>", self._start_drag)
        self.inner.bind("<B1-Motion>", self._on_drag)
        self.inner.bind("<ButtonRelease-1>", self._end_drag)
    
    def _register_hotkeys(self):
        """Register keyboard hotkeys"""
        try:
            keyboard.add_hotkey(self.config.get("hotkey"), self._toggle_from_hotkey)
            keyboard.add_hotkey('shift+windows+0', self._toggle_language)
            logger.info("Hotkeys registered")
        except Exception as e:
            logger.error(f"Hotkey error: {e}")
    
    def _position_widget(self):
        """Position widget on current monitor"""
        # Check for saved position first
        saved_x = self.config.get("widget_x")
        saved_y = self.config.get("widget_y")
        
        if saved_x is not None and saved_y is not None:
            # Use saved position
            self.geometry(f"{WIDGET_WIDTH}x{WIDGET_HEIGHT}+{saved_x}+{saved_y}")
            logger.info(f"Using saved position: ({saved_x}, {saved_y})")
            return
        
        # Otherwise, center on current monitor
        try:
            work_area = self._get_monitor_from_mouse()
            mon_x = work_area.left
            mon_y = work_area.top
            mon_width = work_area.right - work_area.left
            mon_height = work_area.bottom - work_area.top
            
            x = mon_x + (mon_width - WIDGET_WIDTH) // 2
            y = mon_y + mon_height - WIDGET_HEIGHT - int(70*DPI_SCALE)
            
            self.geometry(f"{WIDGET_WIDTH}x{WIDGET_HEIGHT}+{x}+{y}")
        except Exception as e:
            logger.error(f"Positioning error: {e}")
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x = (sw - WIDGET_WIDTH) // 2
            y = sh - WIDGET_HEIGHT - int(70*DPI_SCALE)
            self.geometry(f"{WIDGET_WIDTH}x{WIDGET_HEIGHT}+{x}+{y}")
    
    def _get_monitor_from_mouse(self):
        """Get monitor info where mouse is located"""
        import ctypes
        
        class POINT(Structure):
            _fields_ = [("x", c_long), ("y", c_long)]
        
        class RECT(Structure):
            _fields_ = [("left", c_long), ("top", c_long), ("right", c_long), ("bottom", c_long)]
            
        class MONITORINFO(Structure):
            _fields_ = [("cbSize", c_long), ("rcMonitor", RECT), ("rcWork", RECT), ("dwFlags", c_long)]

        pt = POINT()
        windll.user32.GetCursorPos(byref(pt))
        hMonitor = windll.user32.MonitorFromPoint(pt, 2)
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)  # Fixed: use ctypes.sizeof not len(byref())
        windll.user32.GetMonitorInfoA(hMonitor, byref(mi))
        return mi.rcWork
    
    def setup_tray(self):
        """Setup system tray icon"""
        def create_icon():
            img = Image.new('RGB', (64, 64), color='black')
            draw = ImageDraw.Draw(img)
            draw.ellipse([16, 16, 48, 48], fill='red')
            return img
        
        icon_image = create_icon()
        
        menu = pystray.Menu(
            pystray.MenuItem("Settings", self._open_settings),
            pystray.MenuItem(f"Toggle Recording ({self.config.get('hotkey')})", self._toggle_from_tray),
            pystray.MenuItem("Reset Position", self._reset_position),
            pystray.MenuItem("Exit", self._exit_app)
        )
        
        self.tray_icon = pystray.Icon("voice_dictation", icon_image, "Voice Dictation", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        logger.info("System tray initialized")
    
    def _open_settings(self, icon=None, item=None):
        """Open settings window"""
        self.after(0, lambda: SettingsWindow(self, self.config))
    
    def _toggle_from_tray(self, icon=None, item=None):
        """Toggle recording from tray"""
        self.after(0, self._toggle)
    
    def _start_drag(self, event):
        """Start dragging the widget"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.is_dragging = True
    
    def _on_drag(self, event):
        """Handle widget dragging"""
        if not self.is_dragging:
            return
        
        # Calculate new position
        x = self.winfo_x() + (event.x - self.drag_start_x)
        y = self.winfo_y() + (event.y - self.drag_start_y)
        
        # Move window
        self.geometry(f"{WIDGET_WIDTH}x{WIDGET_HEIGHT}+{x}+{y}")
    
    def _end_drag(self, event):
        """End dragging and save position"""
        if not self.is_dragging:
            return
        
        self.is_dragging = False
        
        # Save final position to config
        x = self.winfo_x()
        y = self.winfo_y()
        self.config.set("widget_x", x)
        self.config.set("widget_y", y)
        logger.info(f"Widget position saved: ({x}, {y})")
    
    def _reset_position(self, icon=None, item=None):
        """Reset widget position to default centered location"""
        self.config.set("widget_x", None)
        self.config.set("widget_y", None)
        logger.info("Widget position reset to default")
        
        # Re-position if currently visible
        if self.is_visible:
            self._position_widget()
    
    def _toggle_from_hotkey(self):
        """Toggle recording from hotkey"""
        self.after(0, self._toggle)
    
    def _toggle_language(self):
        """Toggle between ar/en"""
        current = self.config.get("language")
        new_lang = "en" if current == "ar" else "ar"
        self.config.set("language", new_lang)
        self.transcriber.set_language(new_lang)
        self.lang_indicator.configure(text=new_lang.upper())
        logger.info(f"Language switched to: {new_lang}")
    
    def _toggle(self):
        """Toggle recording on/off"""
        if self.is_visible:
            self._stop_and_hide()
        else:
            # Save current foreground window
            try:
                self.prev_window = win32gui.GetForegroundWindow()
                logger.debug(f"Saved window handle: {self.prev_window}")
            except Exception as e:
                logger.warning(f"Could not save window: {e}")
                self.prev_window = None
            
            self._position_widget()
            self.deiconify()
            self.is_visible = True
            self._start_recording()
    
    def _start_recording(self):
        """Start audio recording"""
        logger.info("Recording started")
        if self.beep_sound:
            self.beep_sound.play()
        
        # Setup recorder callbacks
        self.recorder.on_volume_change = lambda vol: self.visualizer.set_volume(vol)
        self.recorder.on_recording_complete = self._on_recording_complete
        self.recorder.on_low_volume_warning = self._on_low_volume_warning
        
        # Start recording
        self.recorder.start(
            self.config.get("silence_threshold"),
            self.config.get("silence_duration")
        )
    
    def _stop_and_hide(self):
        """Stop recording and hide widget"""
        if not self.is_visible:
            return
        
        logger.info("Recording stopped")
        if self.beep_sound:
            self.beep_sound.play()
        
        self.is_visible = False
        self.recorder.stop()
        self.withdraw()
        self.visualizer.set_volume(0)
    
    def _on_recording_complete(self, audio_file, error=None):
        """Callback when recording completes"""
        self.after(0, self.withdraw)
        self.is_visible = False
        
        if error or not audio_file:
            logger.error(f"Recording failed: {error}")
            self.error_flash_count = 6
            return
        
        # Transcribe
        self._transcribe(audio_file)
    
    def _transcribe(self, filename):
        """Transcribe audio file"""
        try:
            # Check API key
            if not self.config.get("api_key"):
                logger.error("No API key configured")
                self.error_flash_count = 6
                messagebox.showerror("API Key Required",
                    "Please configure your Groq API key in Settings")
                return
            
            # Update transcriber with latest config
            self.transcriber.api_key = self.config.get("api_key")
            self.transcriber.language = self.config.get("language")
            
            # Transcribe with auto-capitalization setting
            auto_cap = self.config.get("auto_capitalize")
            if auto_cap is None:
                auto_cap = True  # Default to True if not set
            
            result = self.transcriber.transcribe(filename, auto_capitalize=auto_cap)
            
            if result:
                pyperclip.copy(result)
                
                # Robust paste with retry logic
                if self.prev_window:
                    self._paste_to_window(self.prev_window)
                else:
                    logger.info("No previous window saved - text in clipboard only")
        
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            self.error_flash_count = 6
            messagebox.showerror("Transcription Error",
                f"API Error: {str(e)}\nText may be in clipboard if partial success.")
        
        finally:
            # Cleanup temp file
            if filename and os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass
    
    def _paste_to_window(self, window_handle):
        """
        Paste text to the specified window with retry logic and multiple fallback strategies.
        
        Windows has security restrictions on SetForegroundWindow that can cause failures.
        This method implements multiple strategies to maximize success rate.
        """
        import ctypes
        
        # Check if window still exists
        if not win32gui.IsWindow(window_handle):
            logger.warning("Previous window no longer exists")
            messagebox.showinfo("Text Copied",
                "Window was closed. Text is in clipboard - paste manually (Ctrl+V)")
            return
        
        # Strategy 1: Simple SetForegroundWindow with retry
        for attempt in range(3):
            try:
                win32gui.SetForegroundWindow(window_handle)
                time.sleep(0.05)  # Short delay to let window come to foreground
                pyautogui.hotkey('ctrl', 'v')
                logger.info(f"Text pasted successfully (attempt {attempt + 1})")
                return  # Success!
            except Exception as e:
                logger.debug(f"Paste attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
        
        # Strategy 2: AttachThreadInput method
        logger.info("Trying AttachThreadInput method...")
        try:
            # Get current thread and target window thread
            current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
            target_thread = ctypes.windll.user32.GetWindowThreadProcessId(window_handle, 0)
            
            if target_thread and current_thread != target_thread:
                # Attach to the target thread
                ctypes.windll.user32.AttachThreadInput(current_thread, target_thread, True)
                
                try:
                    # Now try to set foreground
                    win32gui.SetForegroundWindow(window_handle)
                    time.sleep(0.05)
                    pyautogui.hotkey('ctrl', 'v')
                    logger.info("Text pasted successfully (AttachThreadInput method)")
                    return  # Success!
                finally:
                    # Always detach
                    ctypes.windll.user32.AttachThreadInput(current_thread, target_thread, False)
        except Exception as e:
            logger.debug(f"AttachThreadInput method failed: {e}")
        
        # Strategy 3: BringWindowToTop + ShowWindow method
        logger.info("Trying BringWindowToTop method...")
        try:
            # Restore window if minimized
            ctypes.windll.user32.ShowWindow(window_handle, 9)  # SW_RESTORE
            time.sleep(0.05)
            
            # Bring to top
            win32gui.BringWindowToTop(window_handle)
            time.sleep(0.05)
            
            # Try setting foreground again
            win32gui.SetForegroundWindow(window_handle)
            time.sleep(0.05)
            
            pyautogui.hotkey('ctrl', 'v')
            logger.info("Text pasted successfully (BringWindowToTop method)")
            return  # Success!
        except Exception as e:
            logger.debug(f"BringWindowToTop method failed: {e}")
        
        # All strategies failed - silent fallback (text already in clipboard)
        logger.warning("All paste strategies failed. Text is in clipboard for manual paste.")
        # Don't show a dialog - this is less intrusive
        # User can paste with Ctrl+V when they're ready

    
    def _on_low_volume_warning(self, is_low):
        """Callback for low volume warning"""
        if is_low and not self.show_low_volume_warning:
            # Show warning icon
            self.warning_indicator.pack(side="left", padx=(int(4*DPI_SCALE), 0))
            self.show_low_volume_warning = True
        elif not is_low and self.show_low_volume_warning:
            # Hide warning icon
            self.warning_indicator.pack_forget()
            self.show_low_volume_warning = False
    
    def _pulse_indicator(self):
        """Animate the recording indicator"""
        if self.error_flash_count > 0:
            self.indicator.configure(text_color=ERROR_COLOR if self.error_flash_count % 2 == 0 else GLASS_BG)
            self.error_flash_count -= 1
        elif self.recorder.is_recording:
            t = time.time()
            alpha = 0.5 + 0.5 * math.sin(t * 4)
            r = int(255 * (0.6 + 0.4 * alpha))
            color = f"#{r:02x}4757"
            self.indicator.configure(text_color=color)
        else:
            self.indicator.configure(text_color=WAVE_IDLE_COLOR)
        
        self.after(50, self._pulse_indicator)
    
    def _exit_app(self, icon=None, item=None):
        """Clean shutdown"""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        logger.info("Shutting down...")
        
        # Stop recording
        self.recorder.stop()
        
        # Unregister hotkeys
        try:
            keyboard.unhook_all()
            logger.info("Keyboard hooks removed")
        except:
            pass
        
        # Close pygame
        try:
            pygame.mixer.quit()
        except:
            pass
        
        # Stop tray
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        
        # Destroy window
        try:
            self.quit()
            self.destroy()
        except:
            pass
        
        logger.info("Shutdown complete")
