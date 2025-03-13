from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from googletrans import Translator
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal

@dataclass
class TranslationSuggestion:
    original_word: str
    suggested_word: str
    context: str
    confidence: float
    start_pos: int
    end_pos: int

@dataclass
class TranslationResult:
    full_text: str
    detected_language: str
    suggestions: List[TranslationSuggestion]
    context: str

class EnhancedTranslationManager(QObject):
    """
    Manages the translation pipeline combining Google Translate, 
    personal dictionary, and context awareness
    """
    translation_ready = pyqtSignal(TranslationResult)
    suggestions_ready = pyqtSignal(list)  # List[TranslationSuggestion]
    
    def __init__(self, personal_dictionary, context_manager):
        super().__init__()
        self.translator = Translator()
        self.personal_dictionary = personal_dictionary
        self.context_manager = context_manager
        self.suggestion_threshold = 0.85  # Confidence threshold for suggestions
        
    def find_word_positions(self, text: str, word: str) -> List[Tuple[int, int]]:
        """Find all positions of a word in text, handling partial matches"""
        positions = []
        text_lower = text.lower()
        word_lower = word.lower()
        
        start = 0
        while True:
            index = text_lower.find(word_lower, start)
            if index == -1:
                break
            positions.append((index, index + len(word)))
            start = index + 1
            
        return positions
    
    def get_context_matches(self, translated_text: str, context: str) -> List[TranslationSuggestion]:
        """Find matches from personal dictionary for given context"""
        suggestions = []
        
        # Get context-specific translations
        context_translations = self.personal_dictionary.keyword_manager.contexts.get(
            context, {}).get('translations', {})
            
        # Look for matches in translated text
        for original_word, translation in context_translations.items():
            # Find potential matches using fuzzy matching
            positions = self.find_word_positions(translated_text, original_word)
            
            for start_pos, end_pos in positions:
                match_text = translated_text[start_pos:end_pos]
                confidence = SequenceMatcher(
                    None, 
                    match_text.lower(), 
                    original_word.lower()
                ).ratio()
                
                if confidence >= self.suggestion_threshold:
                    suggestions.append(TranslationSuggestion(
                        original_word=match_text,
                        suggested_word=translation,
                        context=context,
                        confidence=confidence,
                        start_pos=start_pos,
                        end_pos=end_pos
                    ))
        
        return suggestions
    
    async def translate_text(self, text: str, from_lang: str, to_lang: str) -> TranslationResult:
        """Execute full translation pipeline"""
        if not text.strip():
            return TranslationResult("", "", [], "General")
            
        try:
            # 1. Detect context from input text
            context = self.context_manager.get_context_for_text(text)
            
            # 2. Get initial Google translation
            translation = self.translator.translate(
                text, 
                src=from_lang, 
                dest=to_lang
            )
            translated_text = translation.text
            
            # 3. Find dictionary matches based on context
            suggestions = self.get_context_matches(translated_text, context)
            
            # 4. Create translation result
            result = TranslationResult(
                full_text=translated_text,
                detected_language=translation.src,
                suggestions=suggestions,
                context=context
            )
            
            # Emit signals
            self.translation_ready.emit(result)
            if suggestions:
                self.suggestions_ready.emit(suggestions)
                
            return result
            
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return TranslationResult("", "", [], "General")
    
    def apply_suggestion(self, text: str, suggestion: TranslationSuggestion) -> str:
        """Apply a single translation suggestion to the text"""
        return (
            text[:suggestion.start_pos] +
            suggestion.suggested_word +
            text[suggestion.end_pos:]
        )
    
    def apply_suggestions(self, text: str, suggestions: List[TranslationSuggestion]) -> str:
        """Apply multiple suggestions to text, handling overlaps"""
        # Sort suggestions by position to handle them in order
        suggestions.sort(key=lambda x: x.start_pos)
        
        # Apply suggestions from end to start to maintain positions
        result = text
        for suggestion in reversed(suggestions):
            result = self.apply_suggestion(result, suggestion)
            
        return result