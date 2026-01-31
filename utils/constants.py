# Voice Dictation Widget - Constants
import ctypes

# DPI Awareness
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

try:
    dpi = ctypes.windll.user32.GetDpiForSystem()
    DPI_SCALE = dpi / 96.0
except:
    DPI_SCALE = 1.0

# Audio Settings
SAMPLE_RATE = 44100
CHANNELS = 1
BLOCK_SIZE = 1024

# UI Settings (with DPI scaling)
WIDGET_WIDTH = int(200 * DPI_SCALE)
WIDGET_HEIGHT = int(50 * DPI_SCALE)
CORNER_RADIUS = int(25 * DPI_SCALE)

# Glassmorphism Colors
GLASS_BG = "#1a1a2e"
GLASS_BORDER = "#4a4a6a"
ACCENT_COLOR = "#ff4757"
ERROR_COLOR = "#ffa502"
TRANSPARENT_KEY = "#000001"

# Framer-style Wave Animation Colors
WAVE_ACTIVE_COLOR = "#ffffff"    # Pure white for active bars
WAVE_IDLE_COLOR = "#555555"      # Muted gray for idle
