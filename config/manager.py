# Configuration Manager
import os
import json
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration with validation"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load()
    
    def load(self):
        """Load configuration from file with defaults"""
        defaults = {
            "api_key": "",
            "language": "ar",
            "silence_threshold": 0.015,
            "silence_duration": 1.2,
            "hotkey": "windows+0",
            "widget_x": None,
            "widget_y": None,
            "auto_capitalize": True,
            "min_volume_threshold": 0.01
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, encoding='utf-8') as f:
                    loaded = json.load(f)
                    if not self._validate_config(loaded):
                        logger.warning("Invalid config file, using defaults")
                        return defaults
                    return {**defaults, **loaded}
            except Exception as e:
                logger.error(f"Config load error: {e}")
                return defaults
        return defaults
    
    def _validate_config(self, cfg):
        """Validate config values"""
        try:
            if "silence_duration" in cfg:
                if not (0.5 <= cfg["silence_duration"] <= 5.0):
                    return False
            if "language" in cfg:
                if cfg["language"] not in ["ar", "en"]:
                    return False
            return True
        except:
            return False
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("Config saved")
        except Exception as e:
            logger.error(f"Config save error: {e}")
    
    def get(self, key):
        """Get configuration value"""
        return self.config.get(key)
    
    def set(self, key, value):
        """Set configuration value and save"""
        self.config[key] = value
        self.save()
