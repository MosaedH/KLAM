# Voice Dictation Widget - Modular Architecture

## Directory Structure

```
KLAM/
├── main.py                    # Entry point (10 lines)
├── config.json                # User config
├── dictation.log              # Logs
├── beep.mp3                   # Sound effect
│
├── config/                    # Configuration
│   ├── __init__.py
│   └── manager.py             # ConfigManager class
│
├── ui/                        # User Interface
│   ├── __init__.py
│   ├── widget.py              # Main DictationWidget
│   ├── settings.py            # SettingsWindow
│   └── visualizer.py          # AudioVisualizer
│
├── core/                      # Business Logic
│   ├── __init__.py
│   ├── recorder.py            # AudioRecorder
│   └── transcriber.py         # Transcriber (Groq API)
│
└── utils/                     # Utilities
    ├── __init__.py
    ├── constants.py           # All constants
    └── logger.py              # Logging setup
```

## Usage

```bash
python main.py
```

## Module Responsibilities

- **main.py**: Application entry point
- **utils/**: Constants, logging, helpers
- **config/**: Configuration management
- **core/**: Audio recording and transcription logic
- **ui/**: All visual components
