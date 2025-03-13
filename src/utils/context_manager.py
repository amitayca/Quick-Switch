# src/utils/context_manager.py
from PyQt6.QtCore import QSettings

class ContextKeywordManager:
    def __init__(self, settings):
        self.settings = settings
        self.contexts = self.load_contexts()

    def get_context_for_text(self, text):
        """Determine context based on text content"""
        text_lower = text.lower()
        context_matches = {}
        
        # First check for keyword matches
        for context, data in self.contexts.items():
            keyword_matches = sum(1 for keyword in data["keywords"] 
                                if keyword in text_lower)
            if keyword_matches > 0:
                context_matches[context] = keyword_matches

        # Only if we found a context with keywords, check translations
        if context_matches:
            primary_context = max(context_matches.items(), key=lambda x: x[1])[0]
            return primary_context
            
        return "General"

    def load_contexts(self):
        """Load contexts with explicit type checking"""
        contexts = self.settings.value("context_keywords", {})
        
        # Initialize default structure if empty
        if not contexts:
            contexts = {
                "General": {"keywords": set(), "translations": {}},
                "Name": {"keywords": set(), "translations": {}},
                "Technical": {"keywords": set(), "translations": {}},
                "Business": {"keywords": set(), "translations": {}}
            }
        
        # Convert types explicitly
        for context in contexts:
            if isinstance(contexts[context]["keywords"], list):
                contexts[context]["keywords"] = set(contexts[context]["keywords"])
            elif not isinstance(contexts[context]["keywords"], set):
                contexts[context]["keywords"] = set()
                
            if not isinstance(contexts[context]["translations"], dict):
                contexts[context]["translations"] = {}
        
        return contexts

    def save_contexts(self):
        """Save contexts with explicit type conversion"""
        serializable = {}
        for context, data in self.contexts.items():
            serializable[context] = {
                "keywords": list(data["keywords"]),
                "translations": dict(data["translations"])
            }
        self.settings.setValue("context_keywords", serializable)
        self.settings.sync()

    def add_keyword(self, context, keyword):
        """Add keyword to context with automatic context creation"""
        if context not in self.contexts:
            self.contexts[context] = {"keywords": set(), "translations": {}}
        self.contexts[context]["keywords"].add(keyword.lower())
        self.save_contexts()

    def add_translation(self, context, original, translation):
        """Add translation to context with automatic context creation"""
        if context not in self.contexts:
            self.contexts[context] = {"keywords": set(), "translations": {}}
        self.contexts[context]["translations"][original.lower()] = translation
        self.save_contexts()

    def get_translation(self, text, context):
        """Get translation with fallback to General context"""
        text_lower = text.lower()
        if context in self.contexts and text_lower in self.contexts[context]["translations"]:
            return self.contexts[context]["translations"][text_lower]
        # Try General context as fallback
        if "General" in self.contexts and text_lower in self.contexts["General"]["translations"]:
            return self.contexts["General"]["translations"][text_lower]
        return None
    
    def remove_keyword(self, context, keyword):
        """Remove keyword from specified context"""
        if context in self.contexts:
            try:
                # Convert keyword to lower case for consistent handling
                keyword_lower = keyword.lower()
                # Remove from keywords set if exists
                self.contexts[context]["keywords"].discard(keyword_lower)
                self.save_contexts()
            except Exception as e:
                raise ValueError(f"Error removing keyword: {str(e)}")

    #def verify_translations(self):
        """Verify loaded translations"""
        print("Current contexts and translations:")
        for context, data in self.contexts.items():
            print(f"\nContext: {context}")
            print("Keywords:", data["keywords"])
            print("Translations:", data["translations"])