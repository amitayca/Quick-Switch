# src/utils/dictionary_utils.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QListWidget)
from PyQt6.QtCore import Qt

class ContextAnalyzer:
    """Analyzes text to suggest appropriate context"""
    
    def __init__(self):
        # Context keywords mapping
        self.context_keywords = {
            'Technical': {
                'code', 'programming', 'software', 'hardware', 'computer', 'database',
                'server', 'network', 'api', 'function', 'variable', 'class', 'method'
            },
            'Business': {
                'company', 'market', 'finance', 'budget', 'revenue', 'profit',
                'investment', 'stakeholder', 'client', 'management', 'strategy'
            },
            'Medical': {
                'patient', 'doctor', 'hospital', 'treatment', 'diagnosis', 'symptom',
                'medicine', 'clinic', 'health', 'disease', 'medical'
            },
            'Legal': {
                'law', 'court', 'legal', 'contract', 'agreement', 'regulation',
                'compliance', 'jurisdiction', 'rights', 'liability'
            },
            'Academic': {
                'research', 'study', 'theory', 'analysis', 'hypothesis', 'experiment',
                'literature', 'methodology', 'paper', 'thesis'
            }
        }

    def detect_context_and_translations(self, text: str, keyword_manager) -> dict:
        """
        Enhanced context detection with dictionary lookups
        Returns: {
            'context': str,
            'matches': List[dict],
            'keywords_found': List[str]
        }
        """
        text_lower = text.lower()
        context_matches = {}
        keywords_found = []
        
        # Check each context's keywords
        for context, data in keyword_manager.contexts.items():
            matches = []
            for keyword in data['keywords']:
                if keyword.lower() in text_lower:
                    keywords_found.append(keyword)
                    # Check for translations in this context
                    if context in keyword_manager.contexts:
                        context_translations = keyword_manager.contexts[context]['translations']
                        for orig, trans in context_translations.items():
                            if orig.lower() in text_lower:
                                matches.append({
                                    'original': orig,
                                    'translation': trans,
                                    'context': context
                                })
            
            if matches:
                context_matches[context] = matches

        # Determine primary context
        primary_context = "General"
        if context_matches:
            # Select context with most matches
            primary_context = max(
                context_matches.keys(),
                key=lambda k: len(context_matches[k])
            )

        return {
            'context': primary_context,
            'matches': [m for matches in context_matches.values() for m in matches],
            'keywords_found': keywords_found
        }

    def suggest_context(self, text):
        """Analyze text and suggest most likely context"""
        text = text.lower()
        scores = {context: 0 for context in self.context_keywords}
        
        # Count keyword matches for each context
        for context, keywords in self.context_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[context] += 1
        
        # Get context with highest score
        max_score = max(scores.values())
        if max_score > 0:
            suggested_contexts = [
                context for context, score in scores.items() 
                if score == max_score
            ]
            return suggested_contexts[0]
        
        return "General"  # Default context if no matches found


class SuggestionDialog(QDialog):
    def __init__(self, original_text, suggestions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Similar Translations Found")
        self.selected_translation = None
        self.setMinimumWidth(400)
        self.setup_ui(original_text, suggestions)
        
    def setup_ui(self, original_text, suggestions):
        layout = QVBoxLayout(self)
        
        # Original text display
        layout.addWidget(QLabel(f"Original text: {original_text}"))
        layout.addWidget(QLabel("Similar entries found:"))
        
        # Suggestions list
        self.suggestion_list = QListWidget()
        for suggestion in suggestions:
            similarity = suggestion.get("similarity", 0) * 100
            self.suggestion_list.addItem(
                f"{suggestion['translation']} (Context: {suggestion['context']}, "
                f"Match: {similarity:.1f}%)"
            )
        layout.addWidget(self.suggestion_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        use_btn = QPushButton("Use Selected")
        use_btn.clicked.connect(self.use_selected)
        
        ignore_btn = QPushButton("Ignore")
        ignore_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(use_btn)
        button_layout.addWidget(ignore_btn)
        layout.addLayout(button_layout)

    def use_selected(self):
        current_item = self.suggestion_list.currentItem()
        if current_item:
            # Extract translation from the item text (before the context)
            text = current_item.text()
            self.selected_translation = text.split(" (Context:")[0]
            self.accept()

    def apply_theme(self, dark_mode):
        """Apply theme to dialog"""
        base_style = """
            QDialog {
                padding: 8px;
            }
            QListWidget {
                border-radius: 4px;
                padding: 2px;
            }
            QPushButton {
                padding: 5px 10px;
                border-radius: 4px;
                min-height: 24px;
            }
        """
        
        if dark_mode:
            theme_style = """
                QDialog {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
                QListWidget {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #444;
                }
                QPushButton {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #444;
                }
                QPushButton:hover {
                    background-color: #404040;
                }
                QLabel {
                    color: #ffffff;
                }
            """
        else:
            theme_style = """
                QDialog {
                    background-color: #ffffff;
                    color: #212529;
                }
                QListWidget {
                    background-color: #ffffff;
                    color: #212529;
                    border: 1px solid #dee2e6;
                }
                QPushButton {
                    background-color: #f8f9fa;
                    color: #212529;
                    border: 1px solid #dee2e6;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                }
                QLabel {
                    color: #212529;
                }
            """
        
        self.setStyleSheet(base_style + theme_style)
