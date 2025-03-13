from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                           QListWidget, QListWidgetItem, QPushButton,
                           QDialogButtonBox, QTabWidget, QMessageBox, QLabel)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from ..utils.constants import LANGUAGES, TARGET_LANGUAGES
from ..utils.language_manager import LanguageManager
from ..utils.theme_utils import get_dialog_theme_styles


class LanguageSelectionDialog(QDialog):
    def __init__(self, parent=None, current_lang=None, is_source=False):
        super().__init__(parent)
        self.current_lang = current_lang  # This is a language code
        self.is_source = is_source  # Whether this is source language selection
        self.selected_language = None  # Will hold the selected language code
        self.language_manager = LanguageManager()  # Get singleton instance
        self.setup_ui()
        self.apply_theme()
        self.populate_languages()

    def setup_ui(self):
        self.setWindowTitle("Select Language")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search languages...")
        self.search_input.textChanged.connect(self.filter_languages)
        layout.addWidget(self.search_input)

        # Language tabs
        self.tab_widget = QTabWidget()
        
        # Recent languages tab
        self.recent_list = QListWidget()
        self.tab_widget.addTab(self.recent_list, "Recent")

        # All languages tab
        self.system_list = QListWidget()
        self.tab_widget.addTab(self.system_list, "Available Languages")

        layout.addWidget(self.tab_widget)

        # Connect selection handlers
        for list_widget in [self.recent_list, self.system_list]:
            list_widget.itemClicked.connect(self.language_selected)
            list_widget.itemDoubleClicked.connect(self.accept)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def populate_languages(self):
        """Populate language lists using proper language names from Google constants"""
        print("Populating language selection dialog")
        
        # Get recent languages (codes)
        recent_langs = self.language_manager.recent_languages
        print(f"Recent languages (codes): {recent_langs}")
        
        # Populate recent languages with proper names
        for lang_code in recent_langs:
            name = self.language_manager.get_language_name(lang_code)
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, lang_code)
            print(f"Adding recent: {lang_code} -> {name}")
            self.recent_list.addItem(item)

        # Get languages from googletrans constants, filtered appropriately
        from googletrans.constants import LANGUAGES
        
        # Prepare language list (code -> name pairs)
        language_pairs = []
        for code, name in LANGUAGES.items():
            # Skip auto for target languages
            if not self.is_source and code == "auto":
                continue
            
            # Get proper name from language manager
            proper_name = self.language_manager.get_language_name(code)
            language_pairs.append((code, proper_name))
        
        # Sort by proper name, keeping Auto Detect first if applicable
        language_pairs.sort(key=lambda pair: (0 if pair[0] == "auto" else 1, pair[1]))
        
        # Add languages to list
        for code, name in language_pairs:
            # Skip if already in recent languages
            if code in recent_langs:
                continue
                
            # Create item with name display and code data
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, code)
            print(f"Adding language: {code} -> {name}")
            self.system_list.addItem(item)

    def filter_languages(self, text):
        """Filter language list based on search text"""
        text = text.lower()
        for list_widget in [self.recent_list, self.system_list]:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item.setHidden(text not in item.text().lower())

    def language_selected(self, item):
        """Store selected language code from item data"""
        self.selected_language = item.data(Qt.ItemDataRole.UserRole)
        print(f"Selected language: {item.text()} (code: {self.selected_language})")

    def apply_theme(self):
        dark_mode = getattr(self.parent(), 'dark_mode', False)
        self.setStyleSheet(get_dialog_theme_styles(dark_mode))