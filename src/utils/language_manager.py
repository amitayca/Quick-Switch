from PyQt6.QtCore import QSettings
from typing import List, Dict
from googletrans.constants import LANGUAGES as GOOGLE_LANGUAGES

class LanguageManager:
    _instance = None
    _initialized = False

    def __new__(cls, settings: QSettings = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, settings: QSettings = None):
        if not self._initialized:
            self._initialized = True
            self.settings = settings if settings is not None else QSettings()
            self.recent_languages = self.load_recent_languages()
            
            # Create mappings for language names and codes
            self._initialize_language_mappings()

    def _initialize_language_mappings(self):
        """Initialize language mappings using Google Translate constants"""
        # Create mapping from code to proper name
        self._code_to_name_map = {}
        
        # Process Google's language dictionary
        # In GOOGLE_LANGUAGES: keys are codes ('en', 'fr') and values are names ('english', 'french')
        for code, name in GOOGLE_LANGUAGES.items():
            # Properly capitalize the language name
            if " " in name:
                # Handle multi-word names by capitalizing each word
                words = name.split()
                proper_name = " ".join(word.capitalize() for word in words)
            else:
                # Single word names
                proper_name = name.capitalize()
                
            # Store in our mapping
            self._code_to_name_map[code] = proper_name
        
        # Add special cases
        self._code_to_name_map["auto"] = "Auto Detect"
        
        # Create reverse mapping (name to code) for lookups
        self._name_to_code_map = {}
        for code, name in self._code_to_name_map.items():
            self._name_to_code_map[name.lower()] = code

    def load_recent_languages(self) -> List[str]:
        recent = self.settings.value("recent_languages", [])
        return recent if isinstance(recent, list) else []

    def add_recent_language(self, lang_code: str) -> None:
        if lang_code in self.recent_languages:
            self.recent_languages.remove(lang_code)
        self.recent_languages.insert(0, lang_code)
        self.recent_languages = self.recent_languages[:5]
        self.settings.setValue("recent_languages", self.recent_languages)

    def get_language_name(self, lang_code: str) -> str:
        """Get properly formatted language name from code"""
        if not lang_code:
            return "Unknown"
        
        # Direct lookup
        name = self._code_to_name_map.get(lang_code)
        if name:
            return name
        
        # Case-insensitive lookup
        for code, name in self._code_to_name_map.items():
            if code.lower() == lang_code.lower():
                return name
        
        # Fallback: return capitalized code
        return lang_code.capitalize()

    def get_language_code(self, lang_name: str) -> str:
        """Get language code from name (case-insensitive)"""
        if not lang_name:
            return "auto"
        
        # Case-insensitive lookup in name-to-code map
        code = self._name_to_code_map.get(lang_name.lower())
        if code:
            return code
        
        # Check if it's already a valid code
        for existing_code in self._code_to_name_map.keys():
            if lang_name.lower() == existing_code.lower():
                return existing_code
        
        # Fallback to auto
        return "auto"

    def save_language_pair(self, from_lang: str, to_lang: str) -> None:
        """Save the current language pair in settings"""
        self.settings.setValue("last_from_lang", from_lang)
        self.settings.setValue("last_to_lang", to_lang)
        self.add_recent_language(to_lang)

    def get_all_languages(self) -> Dict[str, str]:
        """Get all language name-to-code mappings"""
        return {self.get_language_name(code): code for code in GOOGLE_LANGUAGES.keys()}

    def get_target_languages(self) -> Dict[str, str]:
        """Get all target language name-to-code mappings (excluding auto)"""
        return {self.get_language_name(code): code for code in GOOGLE_LANGUAGES.keys() 
                if code != 'auto'}