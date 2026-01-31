# Transcription Service
import logging
from groq import Groq

logger = logging.getLogger(__name__)


class Transcriber:
    """Handles audio transcription using Groq API"""
    
    def __init__(self, api_key, language="ar"):
        self.api_key = api_key
        self.language = language
        self.client = None
        if api_key:
            self.client = Groq(api_key=api_key)
    
    def set_language(self, language):
        """Update transcription language"""
        self.language = language
        logger.info(f"Transcription language set to: {language}")
    
    @staticmethod
    def capitalize_text(text):
        """
        Auto-capitalize sentences
        
        Args:
            text: Input text
            
        Returns:
            Capitalized text
        """
        import re
        
        if not text:
            return text
        
        # Capitalize first letter
        result = text[0].upper() + text[1:] if len(text) > 0 else text
        
        # Capitalize after sentence endings (. ! ?)
        result = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), result)
        
        return result
    
    def transcribe(self, audio_file_path, auto_capitalize=True):
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to WAV file
            auto_capitalize: Whether to apply auto-capitalization
            
        Returns:
            str: Transcribed text or None on error
        """
        if not self.api_key:
            logger.error("No API key configured")
            raise ValueError("API key required for transcription")
        
        if not self.client:
            self.client = Groq(api_key=self.api_key)
        
        try:
            logger.info(f"Transcribing audio (language={self.language})...")
            
            with open(audio_file_path, "rb") as f:
                result = self.client.audio.transcriptions.create(
                    file=(audio_file_path, f.read()),
                    model="whisper-large-v3",
                    language=self.language,
                    response_format="text"
                )
            
            if result:
                # Apply auto-capitalization if enabled
                if auto_capitalize:
                    result = self.capitalize_text(result)
                
                logger.info(f"Transcription complete: {result}")
                return result
            else:
                logger.warning("Empty transcription result")
                return None
                
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
