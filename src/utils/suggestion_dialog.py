# src/utils/suggestion_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                             QListWidget, QListWidgetItem, QHBoxLayout)
from PyQt6.QtCore import Qt
from dataclasses import dataclass

class TranslationSuggestionDialog(QDialog):
    """Dialog for displaying and managing translation suggestions"""
    
    def __init__(self, original_text: str, suggestions: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Translation Suggestions")
        self.suggestions = suggestions
        self.accepted_suggestions = []
        self.setup_ui(original_text)
        self.apply_theme()
        
    def setup_ui(self, original_text):
        layout = QVBoxLayout(self)
        
        # Original text display
        layout.addWidget(QLabel(f"Original translation:\n{original_text}"))
        
        # Suggestions list
        layout.addWidget(QLabel("Context-specific translations available:"))
        self.suggestion_list = QListWidget()
        
        for suggestion in self.suggestions:
            item = QListWidgetItem(
                f"Replace '{suggestion['original']}' with '{suggestion['translation']}' "
                f"(Context: {suggestion['context']})"
            )
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.suggestion_list.addItem(item)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Apply Selected")
        apply_btn.clicked.connect(self.apply_selected)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
    def apply_selected(self):
        """Collect selected suggestions"""
        for i in range(self.suggestion_list.count()):
            item = self.suggestion_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                self.accepted_suggestions.append(self.suggestions[i])
        self.accept()
        
    def apply_theme(self):
        """Apply current theme to dialog"""
        if hasattr(self.parent(), 'dark_mode') and self.parent().dark_mode:
            self.setStyleSheet("""
                QDialog {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
                QLabel {
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
                    padding: 5px 10px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #404040;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #ffffff;
                    color: #212529;
                }
                QLabel {
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
                    padding: 5px 10px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                }
            """)