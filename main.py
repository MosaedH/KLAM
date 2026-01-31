"""
Voice Dictation Widget - Professional Edition
Modern, modular dictation application with Groq API integration
"""
from utils.logger import setup_logging
from ui.widget import DictationWidget

if __name__ == "__main__":
    setup_logging()
    app = DictationWidget()
    app.mainloop()
