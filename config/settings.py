# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================

import json
import os
from pathlib import Path

# Default settings
DEFAULT_SETTINGS = {
    'language': 'fr',  # 'fr' or 'en'
    'theme': 'dark',   # 'dark' or 'light' (light not implemented yet)
    'import_mode': 'replace',  # 'add' or 'replace' (not implemented yet)
}

# Path to settings file
SETTINGS_PATH = Path(__file__).parent / 'settings.json'


class Config:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.lang = None
        self.load_settings()
        self.load_language()
    
    def load_settings(self):
        """Load settings from JSON file or create with defaults"""
        if SETTINGS_PATH.exists():
            try:
                with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except Exception as e:
                print(f"Error loading settings: {e}")
                print("Using default settings")
        else:
            self.save_settings()
    
    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_language(self):
        """Load language strings based on current language setting"""
        lang_code = self.settings.get('language', 'fr')
        try:
            if lang_code == 'en':
                from config.lang import en
                self.lang = en.LANG
            else:
                from config.lang import fr
                self.lang = fr.LANG
        except Exception as e:
            print(f"Error loading language {lang_code}: {e}")
            # Fallback to French
            from config.lang import fr
            self.lang = fr.LANG
    
    def set_language(self, lang_code):
        """Change language and reload strings"""
        self.settings['language'] = lang_code
        self.save_settings()
        self.load_language()
    
    def set_theme(self, theme):
        """Set theme (dark/light)"""
        self.settings['theme'] = theme
        self.save_settings()
    
    def set_import_mode(self, mode):
        """Set import mode (add/replace)"""
        self.settings['import_mode'] = mode
        self.save_settings()
    
    def get(self, key):
        """Get a setting value"""
        return self.settings.get(key)
    
    def get_text(self, key):
        """Get a language string"""
        return self.lang.get(key, key)
    
    def get_styles(self):
        """Get the appropriate styles module based on current theme"""
        theme = self.settings.get('theme', 'dark')
        if theme == 'light':
            from config import styles_light
            return styles_light
        else:
            from config import styles
            return styles


# Global config instance
config = Config()
