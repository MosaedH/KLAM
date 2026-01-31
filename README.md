# KLAM - Voice Dictation Widget

> **K**eyboard-**L**ess **A**rabic & **M**ultilingual Dictation Widget  
> A professional, always-on-top voice dictation tool with Groq AI-powered transcription

<div align="center">

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.8+-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## 📋 Overview

**KLAM** is a modern, lightweight desktop widget for Windows that enables seamless voice-to-text dictation in multiple languages. Built with a modular architecture, it features a beautiful glassmorphic UI with Siri-like wave animations and integrates with the Groq API for fast, accurate transcription.

### ✨ Key Features

- 🎤 **Voice Dictation**: Record and transcribe speech in Arabic, English, and more
- 🌊 **Beautiful Animations**: Siri-inspired wave visualizer with smooth color gradients
- ⌨️ **Global Hotkeys**: Quick recording toggle with customizable keyboard shortcuts (default: `Windows+0`)
- 🪟 **Always on Top**: Floating widget stays accessible across all applications
- 🎯 **Smart Auto-Paste**: Automatically pastes transcribed text into your active window
- 🌍 **Multi-Language Support**: Quick language switching (Arabic ↔ English)
- 🎨 **Modern UI**: Dark glassmorphism design with smooth animations
- 💾 **Persistent Settings**: Saves position, language preference, and configuration
- 🔊 **Audio Feedback**: Visual and sound notifications for recording states
- 🔄 **System Tray Integration**: Minimize to tray for background operation
- 📊 **Volume Monitoring**: Real-time audio level detection with visual feedback

---

## 🎬 Video Demonstrations

### Quick Start Guide

````carousel
![Running the KLAM project - demonstrates launching the application and basic usage](C:\Users\Mos\.gemini\antigravity\brain\d2506318-256e-46a9-a79c-70b45eb35e28\demo_run_project.mp4)
<!-- slide -->
![Adding files to KLAM - shows how to add and configure files in the project](C:\Users\Mos\.gemini\antigravity\brain\d2506318-256e-46a9-a79c-70b45eb35e28\demo_add_files.mp4)
````

> 💡 **Tip**: Watch these videos to quickly understand how to set up and use KLAM!

---

## 🚀 Installation

### Prerequisites

- **Python 3.8+**
- **Windows 10/11**
- **Microphone** (working audio input device)
- **Groq API Key** ([Get one free here](https://console.groq.com))

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/KLAM.git
   cd KLAM
   ```

2. **Install dependencies**
   ```bash
   pip install customtkinter
   pip install groq
   pip install sounddevice numpy scipy
   pip install pyaudio
   pip install pyperclip pyautogui keyboard
   pip install pygame
   pip install pystray Pillow
   pip install pywin32
   ```

3. **Configure your API key**
   
   Edit `config.json` and add your Groq API key:
   ```json
   {
     "api_key": "YOUR_GROQ_API_KEY_HERE",
     "language": "en",
     "hotkey": "windows+0"
   }
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

---

## 📖 Usage

### Basic Workflow

1. **Start Recording**: Press `Windows+0` (or click the microphone button)
2. **Speak Clearly**: The widget shows animated waves while recording
3. **Auto-Stop**: Recording stops automatically after 1.2s of silence
4. **Auto-Paste**: Transcribed text is automatically pasted to your active window

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Windows+0` | Toggle recording on/off |
| `Windows+Shift+L` | Switch language (Arabic ↔ English) |
| `Ctrl+Q` | Quick show/hide widget |
| `Ctrl+Alt+R` | Reset widget position |

### System Tray Menu

Right-click the system tray icon for:
- ⚙️ **Settings**: Configure API key, language, hotkeys, and audio settings
- 🎤 **Toggle Recording**: Start/stop dictation
- 🔄 **Reset Position**: Center widget on current monitor
- ❌ **Exit**: Close the application

---

## ⚙️ Configuration

### Settings Panel

Access via right-click tray icon → **Settings**:

- **API Key**: Your Groq API key for transcription
- **Language**: Default language (Arabic/English)
- **Hotkey**: Custom keyboard shortcut for recording
- **Silence Threshold**: Audio level to detect silence (0.015 default)
- **Silence Duration**: Seconds of silence before auto-stop (1.2 default)
- **Auto-Capitalize**: Automatically capitalize sentences
- **Microphone**: Select input device

### Configuration File

`config.json` structure:
```json
{
  "api_key": "gsk_...",
  "language": "en",                    // "en" or "ar"
  "silence_threshold": 0.015,          // 0.01 - 0.03
  "silence_duration": 1.2,             // seconds
  "hotkey": "windows+0",               // any valid combo
  "widget_x": 164,                     // saved position
  "widget_y": 697,
  "auto_capitalize": true,
  "min_volume_threshold": 0.01,
  "mic_index": 33                      // microphone device index
}
```

---

## 🏗️ Architecture

### Project Structure

```
KLAM/
├── main.py                    # Entry point (application launcher)
├── config.json                # User configuration & settings
├── dictation.log              # Application logs
├── beep.mp3                   # Recording complete sound effect
│
├── config/                    # Configuration Management
│   ├── __init__.py
│   └── manager.py             # ConfigManager class
│
├── ui/                        # User Interface Components
│   ├── __init__.py
│   ├── widget.py              # Main DictationWidget (UI logic)
│   ├── settings.py            # SettingsWindow (configuration UI)
│   └── visualizer.py          # AudioVisualizer (wave animation)
│
├── core/                      # Business Logic
│   ├── __init__.py
│   ├── recorder.py            # AudioRecorder (voice capture)
│   └── transcriber.py         # Transcriber (Groq API integration)
│
└── utils/                     # Utilities & Helpers
    ├── __init__.py
    ├── constants.py           # UI/Audio constants, DPI scaling
    └── logger.py              # Logging configuration
```

### Module Responsibilities

- **`main.py`**: Application entry point, initializes logging and launches the widget
- **`config/`**: Manages reading/writing configuration from `config.json`
- **`ui/`**: All visual components including the main widget, settings panel, and wave visualizer
- **`core/`**: Audio recording logic and Groq API transcription service
- **`utils/`**: Shared constants, logging setup, and helper utilities

### Technology Stack

- **UI Framework**: CustomTkinter (modern themed Tkinter widgets)
- **Audio Processing**: SoundDevice, NumPy, SciPy
- **API Integration**: Groq Python SDK (Whisper large-v3 model)
- **System Integration**: PyAutoGUI, Keyboard, Pyperclip, PyWin32
- **Graphics**: Pygame (sound effects), PIL (system tray icons)

---

## 🐛 Troubleshooting

### Common Issues

**"No API key configured"**
- Ensure `config.json` has a valid `api_key` value
- Get a free API key from [Groq Console](https://console.groq.com)

**Widget not recording**
- Check microphone permissions in Windows Settings
- Verify correct microphone is selected in Settings panel
- Check volume levels and ensure mic is not muted

**Hotkey not working**
- Ensure no other application is using the same hotkey
- Try a different key combination in Settings
- Run as Administrator (some hotkeys require elevated privileges)

**Paste not working**
- The target application must allow keyboard input
- Some applications block automated paste for security
- Try manually pasting with `Ctrl+V` as fallback

**Transcription errors**
- Check internet connection (Groq API requires internet)
- Verify API key is valid and has remaining credits
- Ensure audio is clear and not too quiet

**High DPI issues**
- The widget automatically adjusts for DPI scaling
- If text appears blurry, check Windows display scaling settings

### Logging

Check `dictation.log` for detailed error information:
```bash
tail -f dictation.log  # Linux/Mac
Get-Content dictation.log -Wait  # Windows PowerShell
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Groq** for the lightning-fast Whisper API
- **CustomTkinter** for the modern UI framework
- Inspired by Siri's beautiful wave animations

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues before creating new ones
- Provide logs and system information when reporting bugs

---

<div align="center">

**Made with ❤️ for seamless multilingual dictation**

</div>
