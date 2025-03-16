from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QFormLayout,
                             QComboBox, QListWidget, QPushButton, QDialogButtonBox,
                             QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem,
                             QLabel, QLineEdit, QCheckBox, QSpinBox, QInputDialog, QListWidgetItem,
                             QTabWidget, QRadioButton, QButtonGroup, QWidget, QColorDialog)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
import re
from ..utils.context_manager import ContextKeywordManager
from ..utils.language_manager import LanguageManager
from ..utils.dictionary_utils import ContextAnalyzer, SuggestionDialog
from ..utils.context_manager import ContextKeywordManager
from .language_dialogs import LanguageSelectionDialog
from ..utils.constants import (POSITION_CURSOR, POSITION_CENTER, POSITION_LAST,
                             INSERT_DIRECT, INSERT_CLIPBOARD, TARGET_LANGUAGES)
from ..utils.theme_utils import get_dialog_theme_styles
from ..utils.styles import ACCENT_COLORS
from googletrans.constants import LANGUAGES

class PersonalDictionaryEditor(QDialog):
    dictionaryUpdated = pyqtSignal()  # Signal when dictionary is modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = parent.settings if parent else QSettings()
        self.keyword_manager = ContextKeywordManager(self.settings)
        #self.keyword_manager.verify_translations()
        self.setWindowTitle("Personal Dictionary")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setup_ui()
        self.load_dictionary()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Split into left and right sections
        main_layout = QHBoxLayout()
        
        # Left section: Dictionary table and entry controls
        left_section = QVBoxLayout()
        
        # Dictionary table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Original Text", "Translation", "Context"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 200)
        left_section.addWidget(self.table)

        # Entry controls
        entry_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        
        # Original text input
        original_layout = QVBoxLayout()
        original_layout.addWidget(QLabel("Original Text:"))
        self.original_text = QLineEdit()
        self.original_text.setPlaceholderText("Enter original text")
        original_layout.addWidget(self.original_text)
        input_layout.addLayout(original_layout)

        # Translation input
        translation_layout = QVBoxLayout()
        translation_layout.addWidget(QLabel("Translation:"))
        self.translation_text = QLineEdit()
        self.translation_text.setPlaceholderText("Enter translation")
        translation_layout.addWidget(self.translation_text)
        input_layout.addLayout(translation_layout)

        # Context input
        context_layout = QVBoxLayout()
        context_layout.addWidget(QLabel("Context:"))
        self.context = QComboBox()
        self.context.addItems(sorted(self.keyword_manager.contexts.keys()))
        context_layout.addWidget(self.context)
        input_layout.addLayout(context_layout)

        entry_layout.addLayout(input_layout)

        # Entry buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Entry")
        add_btn.clicked.connect(self.add_entry)
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_selected)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        
        entry_layout.addLayout(button_layout)
        left_section.addLayout(entry_layout)
        
        # Right section: Context management
        right_section = QVBoxLayout()
        right_section.addWidget(self.setup_context_management())

        # Combine sections
        main_layout.addLayout(left_section, stretch=2)
        main_layout.addLayout(right_section, stretch=1)
        layout.addLayout(main_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_dictionary)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def add_context(self):
        """Add new context via dialog input"""
        context_name, ok = QInputDialog.getText(
            self, 
            "Add Context",
            "Enter new context name:",
            QLineEdit.EchoMode.Normal
        )
        
        if ok and context_name:
            context_name = context_name.strip()
            if context_name:
                current_contexts = list(self.keyword_manager.contexts.keys())
                if context_name not in current_contexts:
                    self.keyword_manager.contexts[context_name] = {
                        "keywords": set(),
                        "translations": {}
                    }
                    self.keyword_manager.save_contexts()
                    self.context_select.addItem(context_name)
                    self.context.addItem(context_name)
                    self.context_select.setCurrentText(context_name)

    def delete_context(self):
        """Delete selected context after confirmation"""
        current_context = self.context_select.currentText()
        if current_context == "General":
            QMessageBox.warning(self, "Warning", "Cannot delete General context")
            return

        reply = QMessageBox.question(
            self,
            "Delete Context",
            f"Delete context '{current_context}' and its keywords?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.keyword_manager.contexts.pop(current_context, None)
            self.keyword_manager.save_contexts()
            
            # Update UI
            self.context_select.removeItem(self.context_select.currentIndex())
            index = self.context.findText(current_context)
            if index >= 0:
                self.context.removeItem(index)
                
            self.context_select.setCurrentText("General")

    def load_dictionary(self):
        """Load personal dictionary from settings"""
        dictionary = self.settings.value("personal_dictionary", [])
        self.table.setRowCount(len(dictionary))
        
        # Load entries into table and context manager
        for i, entry in enumerate(dictionary):
            self.table.setItem(i, 0, QTableWidgetItem(entry.get("original", "")))
            self.table.setItem(i, 1, QTableWidgetItem(entry.get("translation", "")))
            self.table.setItem(i, 2, QTableWidgetItem(entry.get("context", "General")))
            
            # Add to context manager translations
            context = entry.get("context", "General")
            if context not in self.keyword_manager.contexts:
                self.keyword_manager.contexts[context] = {"keywords": set(), "translations": {}}
            
            original = entry.get("original", "").lower()
            translation = entry.get("translation", "")
            self.keyword_manager.contexts[context]["translations"][original] = translation
        
        # Save updated contexts
        self.keyword_manager.save_contexts()

    def add_entry(self):
        """Add new entry to dictionary"""
        original = self.original_text.text().strip()
        translation = self.translation_text.text().strip()
        context = self.context.currentText().strip()

        if not original or not translation:
            QMessageBox.warning(self, "Input Error", "Both original text and translation are required.")
            return

        # Check for duplicates
        for row in range(self.table.rowCount()):
            if (self.table.item(row, 0).text() == original and 
                self.table.item(row, 2).text() == context):
                reply = QMessageBox.question(
                    self, 
                    "Duplicate Entry",
                    f"An entry for '{original}' already exists in this context. Update it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.table.setItem(row, 1, QTableWidgetItem(translation))
                return

        # Add new row
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(original))
        self.table.setItem(row, 1, QTableWidgetItem(translation))
        self.table.setItem(row, 2, QTableWidgetItem(context))

        # Clear input fields
        self.original_text.clear()
        self.translation_text.clear()
        self.context.setCurrentText("General")

    def delete_selected(self):
        """Delete selected entries"""
        rows = set(item.row() for item in self.table.selectedItems())
        if not rows:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete {len(rows)} selected entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for row in sorted(rows, reverse=True):
                self.table.removeRow(row)

    def save_dictionary(self):
        """Save dictionary entries and update context translations"""
        dictionary = []
        
        for row in range(self.table.rowCount()):
            entry = {
                "original": self.table.item(row, 0).text(),
                "translation": self.table.item(row, 1).text(),
                "context": self.table.item(row, 2).text()
            }
            dictionary.append(entry)
            
            context = entry["context"]
            if context not in self.keyword_manager.contexts:
                self.keyword_manager.contexts[context] = {
                    "keywords": set(),
                    "translations": {}
                }
            self.keyword_manager.contexts[context]["translations"][entry["original"].lower()] = entry["translation"]
        
        self.settings.setValue("personal_dictionary", dictionary)
        self.keyword_manager.save_contexts()
        self.dictionaryUpdated.emit()
        self.accept()

    def apply_theme(self):
        dark_mode = getattr(self.parent(), 'dark_mode', False)
        self.setStyleSheet(get_dialog_theme_styles(dark_mode))
        
    def get_similar_entries(self, text, threshold=0.8):
        """Find similar entries using fuzzy matching"""
        from difflib import SequenceMatcher
        
        dictionary = self.settings.value("personal_dictionary", [])
        similar_entries = []
        
        for entry in dictionary:
            similarity = SequenceMatcher(
                None,
                text.lower(),
                entry["original"].lower()
            ).ratio()
            
            if similarity >= threshold:
                similar_entries.append({
                    "original": entry["original"],
                    "translation": entry["translation"],
                    "context": entry["context"],
                    "similarity": similarity
                })
        
        return sorted(similar_entries, key=lambda x: x["similarity"], reverse=True)

    def get_translation(self, text, context="General"):
        """Get context-aware translation for text"""
        dictionary = self.settings.value("personal_dictionary", [])
        
        # First try exact match with context
        for entry in dictionary:
            if (entry["original"].lower() == text.lower() and 
                entry["context"] == context):
                return {"translation": entry["translation"], "type": "exact"}
        
        # Then try exact match with any context
        for entry in dictionary:
            if entry["original"].lower() == text.lower():
                return {"translation": entry["translation"], "type": "exact"}
        
        # Check for similar entries
        similar_entries = self.get_similar_entries(text)
        if similar_entries:
            return {"translation": None, "type": "similar", "entries": similar_entries}
        
        return {"translation": None, "type": "none"}
    
    def setup_context_management(self):
        """Add context and keyword management UI"""
        context_group = QGroupBox("Context Management")
        layout = QVBoxLayout()

        # Context selection
        context_layout = QHBoxLayout()
        self.context_select = QComboBox()
        self.context_select.addItems(self.keyword_manager.contexts.keys())
        self.context_select.currentTextChanged.connect(self.load_context_keywords)
        
        add_context_btn = QPushButton("New Context")
        add_context_btn.clicked.connect(self.add_context)
        
        context_layout.addWidget(QLabel("Context:"))
        context_layout.addWidget(self.context_select)
        context_layout.addWidget(add_context_btn)
        layout.addLayout(context_layout)

        # Keyword management
        keyword_layout = QHBoxLayout()
        
        # Keyword list
        self.keyword_list = QListWidget()
        
        # Keyword controls
        control_layout = QVBoxLayout()
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter keyword")
        
        add_keyword_btn = QPushButton("Add Keyword")
        add_keyword_btn.clicked.connect(self.add_keyword)
        
        remove_keyword_btn = QPushButton("Remove Keyword")
        remove_keyword_btn.clicked.connect(self.remove_keyword)
        
        control_layout.addWidget(self.keyword_input)
        control_layout.addWidget(add_keyword_btn)
        control_layout.addWidget(remove_keyword_btn)
        control_layout.addStretch()
        
        keyword_layout.addWidget(self.keyword_list)
        keyword_layout.addLayout(control_layout)
        layout.addLayout(keyword_layout)

        context_group.setLayout(layout)
        return context_group

    def load_context_keywords(self):
        """Load keywords for selected context"""
        context = self.context_select.currentText()
        self.keyword_list.clear()
        if context in self.keyword_manager.contexts:
            keywords = sorted(self.keyword_manager.contexts[context]["keywords"])
            self.keyword_list.addItems(keywords)

    def add_keyword(self):
        """Add keyword to current context"""
        keyword = self.keyword_input.text().strip()
        if not keyword:
            return
            
        context = self.context_select.currentText()
        self.keyword_manager.add_keyword(context, keyword)
        self.load_context_keywords()
        self.keyword_input.clear()

    def remove_keyword(self):
        """Remove selected keyword from context"""
        current_item = self.keyword_list.currentItem()
        if not current_item:
            return
            
        context = self.context_select.currentText()
        self.keyword_manager.remove_keyword(context, current_item.text())
        self.load_context_keywords()

class AISettingsDialog(QDialog):
    """Dialog for configuring AI translation settings"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = parent.settings if parent else QSettings()
        self.setWindowTitle("AI Translation Settings")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # API Configuration
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout()

        self.api_key = QLineEdit()
        self.api_key.setText(self.settings.value("ai_api_key", ""))
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)

        self.enable_ai = QCheckBox("Enable AI Translation")
        self.enable_ai.setChecked(self.settings.value("ai_enabled", False, bool))

        api_layout.addRow("API Key:", self.api_key)
        api_layout.addRow(self.enable_ai)
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # AI Features
        features_group = QGroupBox("AI Features")
        features_layout = QVBoxLayout()

        self.context_aware = QCheckBox("Context-Aware Translation")
        self.style_matching = QCheckBox("Style Matching")
        self.alternative_suggestions = QCheckBox("Show Alternative Suggestions")
        
        self.context_aware.setChecked(self.settings.value("ai_context_aware", True, bool))
        self.style_matching.setChecked(self.settings.value("ai_style_matching", True, bool))
        self.alternative_suggestions.setChecked(self.settings.value("ai_alternatives", False, bool))

        features_layout.addWidget(self.context_aware)
        features_layout.addWidget(self.style_matching)
        features_layout.addWidget(self.alternative_suggestions)
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)

        # Usage limits
        limits_group = QGroupBox("Usage Limits")
        limits_layout = QFormLayout()

        self.daily_limit = QSpinBox()
        self.daily_limit.setRange(0, 1000)
        self.daily_limit.setValue(self.settings.value("ai_daily_limit", 100, int))

        limits_layout.addRow("Daily Request Limit:", self.daily_limit)
        limits_group.setLayout(limits_layout)
        layout.addWidget(limits_group)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def save_settings(self):
        """Save AI settings"""
        self.settings.setValue("ai_api_key", self.api_key.text())
        self.settings.setValue("ai_enabled", self.enable_ai.isChecked())
        self.settings.setValue("ai_context_aware", self.context_aware.isChecked())
        self.settings.setValue("ai_style_matching", self.style_matching.isChecked())
        self.settings.setValue("ai_alternatives", self.alternative_suggestions.isChecked())
        self.settings.setValue("ai_daily_limit", self.daily_limit.value())
        self.accept()

class EnhancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = parent.settings if parent else QSettings()
        
        # Initialize base language dictionaries (unfiltered)
        self.source_languages = LANGUAGES.copy()  # Include Auto Detect
        self.target_languages = {name: code for name, code in LANGUAGES.items() 
                            if name != "Auto Detect"}  # Exclude Auto Detect
        
        # Initialize language manager for consistent name/code conversion
        self.language_manager = LanguageManager()
        
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Setup settings dialog UI with tabs for better organization"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Create a tab widget for better organization
        tab_widget = QTabWidget()
        
        # Tab 1: Languages
        language_tab = QWidget()
        language_layout = QVBoxLayout(language_tab)
        language_layout.setSpacing(10)
        
        # Default languages group with proper code handling
        default_group = QGroupBox("Default Languages")
        default_layout = QFormLayout()
        default_layout.setContentsMargins(10, 15, 10, 10)

        # Setup source language combo
        self.default_from = QComboBox()
        
        # Get language names and ensure Auto Detect is first
        auto_name = self.language_manager.get_language_name("auto")
        source_langs = []
        
        # Add languages (excluding Auto Detect)
        for code in sorted(self.language_manager.get_all_languages().values()):
            if code != "auto":
                name = self.language_manager.get_language_name(code)
                source_langs.append(name)
        
        # Insert Auto Detect at the beginning
        all_source_langs = [auto_name] + source_langs
        self.default_from.addItems(all_source_langs)
        
        # Get current default or fallback to "auto"
        current_from = self.settings.value("default_from", "auto")
        current_from_name = self.language_manager.get_language_name(current_from)
        self.default_from.setCurrentText(current_from_name)

        # Setup target language combo (excluding Auto Detect)
        self.default_to = QComboBox()
        target_langs = []
        for code, name in self.language_manager.get_target_languages().items():
            target_langs.append(self.language_manager.get_language_name(name))
        target_langs = sorted(target_langs)
        self.default_to.addItems(target_langs)
        
        # Get current default or fallback to "he"
        current_to = self.settings.value("default_to", "he")
        current_to_name = self.language_manager.get_language_name(current_to)
        self.default_to.setCurrentText(current_to_name)

        default_layout.addRow("Default From:", self.default_from)
        default_layout.addRow("Default To:", self.default_to)
        default_group.setLayout(default_layout)
        language_layout.addWidget(default_group)

        # Language Management group
        lang_group = QGroupBox("Language Management")
        lang_layout = QVBoxLayout()
        lang_layout.setContentsMargins(10, 15, 10, 10)

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search languages...")
        self.search_input.textChanged.connect(self.filter_languages)
        lang_layout.addWidget(self.search_input)

        # Create language list widget
        self.lang_list = QListWidget()
        
        # Get and normalize enabled languages
        enabled_codes = self.settings.value("enabled_languages", ["en", "he"])
        if not isinstance(enabled_codes, list):
            enabled_codes = ["en", "he"]
        
        # Process all languages (excluding Auto Detect)
        for code in sorted(self.language_manager.get_target_languages().values()):
            # Get proper language name for display
            language_name = self.language_manager.get_language_name(code)
            
            # Create item with language name
            item = QListWidgetItem(language_name)
            # Store code as item data
            item.setData(Qt.ItemDataRole.UserRole, code)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if code in enabled_codes
                else Qt.CheckState.Unchecked
            )
            self.lang_list.addItem(item)

        lang_layout.addWidget(self.lang_list)
        lang_group.setLayout(lang_layout)
        language_layout.addWidget(lang_group)
        
        language_tab.setLayout(language_layout)
        tab_widget.addTab(language_tab, "Languages")
        
        # Tab 2: Appearance
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        
        # Theme selection
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        
        # Theme radio buttons
        theme_buttons_layout = QHBoxLayout()
        self.dark_mode_radio = QRadioButton("Dark Theme")
        self.light_mode_radio = QRadioButton("Light Theme")
        
        # Set initial selection based on current theme
        dark_mode = self.settings.value("dark_mode", False, bool)
        self.dark_mode_radio.setChecked(dark_mode)
        self.light_mode_radio.setChecked(not dark_mode)
        
        theme_buttons_layout.addWidget(self.dark_mode_radio)
        theme_buttons_layout.addWidget(self.light_mode_radio)
        theme_layout.addLayout(theme_buttons_layout)

        # Accent color selection
        color_label = QLabel("Accent Color:")

        # Create color selector grid
        color_layout = QHBoxLayout()
        color_layout.setSpacing(8)
        color_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.color_group = QButtonGroup(self)
        self.color_group.setExclusive(True)

        # Get current accent color from settings - ADD THIS LINE
        current_color = self.settings.value("accent_color", "Blue")

        # Add color swatches
        for i, (name, colors) in enumerate(ACCENT_COLORS.items()):
            # Create a color sample button
            color_btn = QPushButton()
            color_btn.setFixedSize(24, 24)
            color_hex = colors["dark" if dark_mode else "light"]
            
            # Set button style to show the color
            color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_hex};
                    border: 2px solid {"#555" if dark_mode else "#ddd"};
                    border-radius: 12px;
                }}
                QPushButton:checked {{
                    border: 2px solid {"#fff" if dark_mode else "#000"};
                }}
            """)
            
            color_btn.setCheckable(True)
            color_btn.setChecked(name == current_color)
            color_btn.setToolTip(name)
            
            # Store the color name as property
            color_btn.setProperty("colorName", name)
            
            self.color_group.addButton(color_btn, i)
            color_layout.addWidget(color_btn)
        
        theme_layout.addWidget(color_label)
        theme_layout.addLayout(color_layout)
        
        # Custom color button (as a placeholder for now)
        custom_color_btn = QPushButton("Custom Color...")
        custom_color_btn.setEnabled(False)  # Disabled for now
        theme_layout.addWidget(custom_color_btn)
        
        theme_group.setLayout(theme_layout)
        appearance_layout.addWidget(theme_group)
        
        # Window behavior settings
        window_group = QGroupBox("Window Behavior")
        window_layout = QFormLayout()
        window_layout.setContentsMargins(10, 15, 10, 10)

        self.position_combo = QComboBox()
        positions = [POSITION_CURSOR, POSITION_CENTER, POSITION_LAST]
        self.position_combo.addItems(positions)
        self.position_combo.setCurrentText(
            self.settings.value("window_position", POSITION_CURSOR)
        )

        self.insert_combo = QComboBox()
        insert_methods = [INSERT_DIRECT, INSERT_CLIPBOARD]
        self.insert_combo.addItems(insert_methods)
        self.insert_combo.setCurrentText(
            self.settings.value("insertion_method", INSERT_DIRECT)
        )

        window_layout.addRow("Window Position:", self.position_combo)
        window_layout.addRow("Text Insertion:", self.insert_combo)
        window_group.setLayout(window_layout)
        appearance_layout.addWidget(window_group)
        
        appearance_tab.setLayout(appearance_layout)
        tab_widget.addTab(appearance_tab, "Appearance")
        
        # Tab 3: Advanced
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # AI Translation section
        ai_group = QGroupBox("AI Translation")
        ai_layout = QVBoxLayout()
        ai_layout.setContentsMargins(10, 15, 10, 10)
        
        self.ai_settings_btn = QPushButton("Configure AI Translation")
        self.ai_settings_btn.clicked.connect(self.show_ai_settings)
        ai_layout.addWidget(self.ai_settings_btn)
        
        ai_group.setLayout(ai_layout)
        advanced_layout.addWidget(ai_group)

        # Dictionary button
        self.dict_btn = QPushButton("Personal Dictionary")
        self.dict_btn.setMinimumHeight(32)
        self.dict_btn.clicked.connect(self.show_dictionary)
        advanced_layout.addWidget(self.dict_btn)
        
        advanced_tab.setLayout(advanced_layout)
        tab_widget.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tab_widget)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def preview_accent_color(self, is_checked):
        """Preview the selected accent color immediately"""
        if is_checked and self.parent:
            button = self.color_group.checkedButton()
            if button:
                color_name = button.property("colorName")
                if color_name:
                    # Update parent's theme immediately
                    self.settings.setValue("accent_color", color_name)
                    self.parent.apply_theme()

    def select_custom_color(self):
        """Open color picker for custom color selection"""
        dark_mode = self.parent.dark_mode if hasattr(self.parent, 'dark_mode') else False
        
        color_dialog = QColorDialog(self)
        color_dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, False)
        
        # Get current accent color for initial selection
        current_color_name = self.settings.value("accent_color", "Blue")
        current_color = QColor(ACCENT_COLORS[current_color_name]["dark" if dark_mode else "light"])
        color_dialog.setCurrentColor(current_color)
        
        # Apply dialog theme
        from ..utils.theme_utils import get_dialog_theme_styles
        color_dialog.setStyleSheet(get_dialog_theme_styles(dark_mode))
        
        if color_dialog.exec() == QDialog.DialogCode.Accepted:
            selected_color = color_dialog.selectedColor()
            if selected_color.isValid():
                # Convert to hex
                hex_color = selected_color.name()
                
                # Store custom color in settings
                self.settings.setValue("custom_color_dark", hex_color)
                self.settings.setValue("custom_color_light", hex_color)
                
                # Update ACCENT_COLORS dictionary temporarily
                ACCENT_COLORS["Custom"] = {
                    "dark": hex_color,
                    "light": hex_color
                }
                
                # Create and select a new button for the custom color
                for btn in self.color_group.buttons():
                    if btn.property("colorName") == "Custom":
                        self.color_group.removeButton(btn)
                        btn.deleteLater()
                
                # Create new custom button
                custom_btn = QPushButton()
                custom_btn.setFixedSize(24, 24)
                custom_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {hex_color};
                        border: 2px solid {"#555" if dark_mode else "#ddd"};
                        border-radius: 12px;
                    }}
                    QPushButton:checked {{
                        border: 2px solid {"#fff" if dark_mode else "#000"};
                    }}
                """)
                custom_btn.setCheckable(True)
                custom_btn.setChecked(True)
                custom_btn.setToolTip("Custom")
                custom_btn.setProperty("colorName", "Custom")
                custom_btn.toggled.connect(self.preview_accent_color)
                
                # Add to button group and layout
                self.color_group.addButton(custom_btn)
                self.custom_color_layout.addWidget(custom_btn)
                
                # Apply the color immediately
                self.settings.setValue("accent_color", "Custom")
                if self.parent:
                    self.parent.apply_theme()

    def get_language_name(self, code):
        """Helper to get language name from code using LanguageManager"""
        return self.language_manager.get_language_name(code)
    
    def show_dictionary(self):
        dialog = PersonalDictionaryEditor(self)
        dialog.exec()

    def normalize_code(self, language):
        """Normalize a language name or code to its standard code form"""
        # If it's already a valid code, return it
        if language in LANGUAGES.values():
            return language
        
        # Convert language name to code (case-insensitive)
        language_lower = language.lower()
        for name, code in LANGUAGES.items():
            if name.lower() == language_lower or code.lower() == language_lower:
                return code
                
        return None  # Return None if not found
    
    def save_settings(self):
        """Save settings with proper language code handling and theme preferences"""
        try:
            # Save language settings
            enabled_codes = set()  # Use set to prevent duplicates
            
            for i in range(self.lang_list.count()):
                item = self.lang_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    # Get the ISO code from item data
                    iso_code = item.data(Qt.ItemDataRole.UserRole)
                    enabled_codes.add(iso_code)
            
            # Add required languages
            enabled_codes.add("en")
            enabled_codes.add("he")
            
            # Convert to sorted list for consistent storage
            enabled_codes_list = sorted(list(enabled_codes))
            
            # Save language codes
            self.settings.setValue("enabled_languages", enabled_codes_list)
            
            # Save default languages using language selectors
            from_name = self.default_from.currentText()
            to_name = self.default_to.currentText()
            
            # Convert names to codes
            from_code = self.language_manager.get_language_code(from_name)
            to_code = self.language_manager.get_language_code(to_name)
            
            self.settings.setValue("default_from", from_code)
            self.settings.setValue("default_to", to_code)
            
            # Save window position and insertion method
            self.settings.setValue("window_position", self.position_combo.currentText())
            self.settings.setValue("insertion_method", self.insert_combo.currentText())
            
            # Save theme preferences
            self.settings.setValue("dark_mode", self.dark_mode_radio.isChecked())
            
            # Save accent color if selected
            selected_color_btn = self.color_group.checkedButton()
            if selected_color_btn:
                color_name = selected_color_btn.property("colorName")
                if color_name:
                    self.settings.setValue("accent_color", color_name)
            
            # Ensure settings are written to disk
            self.settings.sync()
            
            # Apply theme if parent window exists
            if self.parent:
                dark_mode = self.dark_mode_radio.isChecked()
                if dark_mode != self.parent.dark_mode:
                    self.parent.dark_mode = dark_mode
                    self.parent.apply_theme()
                
                # Force translation window to update its selectors
                if hasattr(self.parent, 'update_language_selectors'):
                    self.parent.update_language_selectors()
            
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Error saving settings: {str(e)}")
            self.settings.setValue("enabled_languages", ["en", "he"])
            self.accept()

    def filter_languages(self, text):
        """Filter language list based on search text"""
        text = text.lower()
        for i in range(self.lang_list.count()):
            item = self.lang_list.item(i)
            # Only search in the display name (not the code)
            item.setHidden(text not in item.text().lower())

    def show_ai_settings(self):
        dialog = AISettingsDialog(self)
        dialog.exec()

    def apply_theme(self):
        """Apply consistent theme styling to settings dialog with proper text colors"""
        dark_mode = self.parent.dark_mode if hasattr(self.parent, 'dark_mode') else False
        
        base_style = """
            QDialog {
                padding: 8px;
            }
            QGroupBox {
                margin-top: 16px;
                font-weight: bold;
                padding-top: 12px;
            }
            QComboBox {
                padding: 4px;
                border-radius: 4px;
                min-width: 150px;
                min-height: 24px;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 100px;
            }
            QLabel {
                min-height: 20px;
            }
            QTabWidget::pane {
                border: 1px solid """ + ("#444" if dark_mode else "#dee2e6") + """;
                border-radius: 4px;
            }
            QTabBar::tab {
                padding: 6px 12px;
                margin-right: 2px;
                border: 1px solid """ + ("#444" if dark_mode else "#dee2e6") + """;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: """ + ("#ffffff" if dark_mode else "#212529") + """;
            }
            QTabBar::tab:selected {
                background-color: """ + ("#2d2d2d" if dark_mode else "#ffffff") + """;
                color: """ + ("#ffffff" if dark_mode else "#212529") + """;
            }
            QTabBar::tab:!selected {
                background-color: """ + ("#1a1a1a" if dark_mode else "#f5f5f5") + """;
                color: """ + ("#cccccc" if dark_mode else "#495057") + """;
            }
        """
        
        theme_style = """
            QDialog {
                background-color: """ + ("#1a1a1a" if dark_mode else "#ffffff") + """;
                color: """ + ("#ffffff" if dark_mode else "#212529") + """;
            }
            QGroupBox {
                border: 1px solid """ + ("#444" if dark_mode else "#dee2e6") + """;
                color: """ + ("#ffffff" if dark_mode else "#212529") + """;
            }
            QComboBox, QLineEdit, QListWidget {
                background-color: """ + ("#2d2d2d" if dark_mode else "#ffffff") + """;
                border: 1px solid """ + ("#444" if dark_mode else "#dee2e6") + """;
                color: """ + ("#ffffff" if dark_mode else "#212529") + """;
            }
            QPushButton {
                background-color: """ + ("#2d2d2d" if dark_mode else "#f8f9fa") + """;
                border: 1px solid """ + ("#444" if dark_mode else "#dee2e6") + """;
                color: """ + ("#ffffff" if dark_mode else "#212529") + """;
            }
            QPushButton:hover {
                background-color: """ + ("#404040" if dark_mode else "#e9ecef") + """;
            }
            QLabel {
                color: """ + ("#ffffff" if dark_mode else "#212529") + """;
            }
            QRadioButton {
                color: """ + ("#ffffff" if dark_mode else "#212529") + """;
            }
        """
        
        self.setStyleSheet(base_style + theme_style)