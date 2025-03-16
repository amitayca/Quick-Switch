from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QTextEdit, QPushButton, QLabel, QSystemTrayIcon,
                            QMenu, QComboBox, QMessageBox, QSizeGrip, QSizePolicy,
                            QApplication, QLineEdit, QFormLayout, QDialog,
                            QGroupBox, QDialogButtonBox, QListWidget, QListWidgetItem,
                            QFrame)
from PyQt6.QtCore import Qt, QTimer, QSettings, QSize, QDateTime
from PyQt6.QtGui import QIcon, QActionGroup, QAction, QCursor, QRegion
import keyboard as kb
import win32gui
import win32clipboard
import win32con
from googletrans import Translator
import re

from ..utils.context_manager import ContextKeywordManager
from ..utils.window_automation import WindowAutomation
from ..utils.constants import (LANGUAGES, TARGET_LANGUAGES, WINDOW_DEFAULT_SIZE,
                             TRANSLATION_DEBOUNCE_MS, GLOBAL_HOTKEY,
                             APP_NAME, ORGANIZATION_NAME, SETTINGS_NAME,
                             POSITION_CURSOR, POSITION_CENTER, POSITION_LAST,
                             INSERT_DIRECT, INSERT_CLIPBOARD, WINDOW_MODE_FULL,
                             WINDOW_MODE_COMPACT, COMPACT_WINDOW_SIZE, DEFAULT_LANGUAGE_PAIRS,
                             CURSOR_OFFSET_X, CURSOR_OFFSET_Y)
from ..utils.styles import (DARK_THEME, LIGHT_THEME, 
                           COMPACT_DARK_STYLES, COMPACT_LIGHT_STYLES,
                           apply_accent_color, ACCENT_COLORS)
from .settings_dialog import EnhancedSettingsDialog, PersonalDictionaryEditor
from ..utils.dictionary_utils import ContextAnalyzer, SuggestionDialog
from ..utils.translation_manager import EnhancedTranslationManager
from ..utils.suggestion_dialog import TranslationSuggestionDialog
from .language_dialogs import LanguageSelectionDialog
from ..utils.language_manager import LanguageManager


class TranslationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Core settings
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(*WINDOW_DEFAULT_SIZE)
        self.settings = QSettings(ORGANIZATION_NAME, SETTINGS_NAME)
        self.dark_mode = self.settings.value("dark_mode", False, bool)
        
        # Initialize core components first
        self.window_automation = WindowAutomation()
        self.context_analyzer = ContextAnalyzer()
        self.language_manager = LanguageManager(self.settings)
        
        # Initialize context manager with settings
        self.context_manager = ContextKeywordManager(self.settings)
        
        # Initialize dictionary and translation components with shared context manager
        self.personal_dictionary = PersonalDictionaryEditor(parent=self)
        self.personal_dictionary.keyword_manager = self.context_manager  # Use shared context manager
        self.translation_manager = EnhancedTranslationManager(
            personal_dictionary=self.personal_dictionary,
            context_manager=self.context_manager  # Use shared context manager
        )
        
        # Connect signals
        self.translation_manager.translation_ready.connect(self.handle_translation_result)
        self.translation_manager.suggestions_ready.connect(self.handle_suggestions)
        
        # Initialize window state
        self.window_mode = self.settings.value("window_mode", WINDOW_MODE_FULL)
        self.old_pos = None
        self.title_bar_height = None
        self.last_focused_window = None
        self.last_focused_control = None
        self.compact_widgets = {}
        
        # Language setup
        self.source_languages = LANGUAGES
        self.target_languages = TARGET_LANGUAGES
        self.detected_language = None
        
        # Translation timer
        self.translation_timer = None
        
        # Setup UI components
        self.init_ui()
        self.setup_language_management()
        self.apply_theme()
        
        # Set rounded corners using Qt style
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.99)  # Slight opacity to enable rounded corners

    def init_ui(self):
        # Set window flags
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        
        # Initialize translation timer
        self.translation_timer = QTimer()
        self.translation_timer.setSingleShot(True)
        self.translation_timer.timeout.connect(self.update_translation)
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create UI modes
        self.create_full_ui()
        self.create_compact_ui()
        
        # Set initial mode
        self.set_window_mode(self.window_mode)
        
        # Setup hotkey and tray
        kb.add_hotkey(GLOBAL_HOTKEY, self.show_window, suppress=True)
        self.create_tray_icon()
        self.hide()

    def show_settings(self):
        """Show settings dialog with integrated color selection"""
        print("TranslationWindow: Opening settings dialog")
        dialog = EnhancedSettingsDialog(self)  # Pass self as parent
        
        # Connect signals
        if hasattr(dialog, 'languageUpdated'):
            dialog.languageUpdated.connect(self.update_language_selectors)
            print("TranslationWindow: Connected languageUpdated signal")
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            print("TranslationWindow: Settings dialog accepted, updating language selectors")
            # Update language selectors after dialog is accepted
            self.update_language_selectors()
        else:
            print("TranslationWindow: Settings dialog canceled")

    def show_language_selection(self, combo_box):
        """Display language selection dialog and handle selection"""
        is_source = (combo_box == self.from_lang)
        languages_dict = self.source_languages if is_source else self.target_languages
        
        # Get current language code with fallback
        try:
            current_text = combo_box.currentText()
            current_lang = languages_dict[current_text] if current_text else ("auto" if is_source else "en")
        except KeyError:
            current_lang = "auto" if is_source else "en"
        
        # Show language selection dialog
        dialog = LanguageSelectionDialog(parent=self, current_lang=current_lang, is_source=is_source)
        
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_language:
            # Get the language name from the code
            lang_name = self.language_manager.get_language_name(dialog.selected_language)
            
            # Update language selection if valid
            if lang_name:
                # Block signals temporarily to prevent recursive updates
                combo_box.blockSignals(True)
                combo_box.setCurrentText(lang_name)
                combo_box.blockSignals(False)
                
                # Save updated language pair
                try:
                    from_code = self.source_languages[self.from_lang.currentText()]
                    to_code = self.target_languages[self.to_lang.currentText()]
                    self.language_manager.save_language_pair(from_code, to_code)
                    
                    # Update settings
                    self.settings.setValue("last_from_lang", from_code)
                    self.settings.setValue("last_to_lang", to_code)
                    self.settings.sync()
                    
                except KeyError as e:
                    print(f"Error saving language pair: {str(e)}")
                
                # Add to recent languages
                if not is_source:  # Only add target languages to recent
                    self.language_manager.add_recent_language(dialog.selected_language)
                
                # Trigger translation update if we have text to translate
                if self.window_mode == WINDOW_MODE_COMPACT:
                    if self.compact_input.text().strip():
                        self.translation_timer.start(TRANSLATION_DEBOUNCE_MS)
                else:
                    if self.input_text.toPlainText().strip():
                        self.translation_timer.start(TRANSLATION_DEBOUNCE_MS)

    def setup_language_management(self):
        """Initial language management setup"""
        # Load last used languages with defaults
        last_from = self.settings.value("last_from_lang", "auto")
        last_to = self.settings.value("last_to_lang", "he")
        
        # Initialize combo boxes with correct values
        self.from_lang.setCurrentText(self.language_manager.get_language_name(last_from))
        self.to_lang.setCurrentText(self.language_manager.get_language_name(last_to))
        
        # Connect signal handlers for language changes
        self.from_lang.currentTextChanged.connect(lambda text: self.on_language_changed(text))
        self.to_lang.currentTextChanged.connect(lambda text: self.on_language_changed(text))
        
        # Initialize compact mode language buttons if they exist
        if hasattr(self, 'compact_from_lang') and hasattr(self, 'compact_to_lang'):
            self.update_compact_language_buttons()

    def update_translation(self):
        """Handle translation with proper personal dictionary integration"""
        # Get input text based on current mode
        if self.window_mode == WINDOW_MODE_COMPACT:
            text = self.compact_input.text().strip()
        else:
            text = self.input_text.toPlainText().strip()

        if not text:
            return

        # Check for commands (colon prefix)
        if text.startswith(':'):
            self.handle_command(text)
            return

        try:
            # Get language codes from current selections
            from_lang = self.source_languages[self.from_lang.currentText()]
            to_lang = self.target_languages[self.to_lang.currentText()]
            
            # Get context for the text
            context = self.context_manager.get_context_for_text(text)
            
            # Show context notification if not General
            if context != "General":
                self.show_context_notification(context)
            
            # First do the base translation
            translator = Translator()
            translation = translator.translate(text, src=from_lang, dest=to_lang)
            translated_text = translation.text
            
            # Now check for dictionary entries and apply them
            replacements = {}
            
            # Check the identified context's dictionary
            if context in self.context_manager.contexts:
                context_dict = self.context_manager.contexts[context]["translations"]
                for original, replacement in context_dict.items():
                    if original.lower() in text.lower():
                        replacements[original] = replacement
            
            # Also check the General context
            if "General" in self.context_manager.contexts and context != "General":
                general_dict = self.context_manager.contexts["General"]["translations"]
                for original, replacement in general_dict.items():
                    if original.lower() in text.lower() and original not in replacements:
                        replacements[original] = replacement
            
            # Apply all replacements to the translated text
            if replacements:
                import re
                for original, replacement in replacements.items():
                    # Use case-insensitive replacement
                    pattern = re.compile(re.escape(original), re.IGNORECASE)
                    translated_text = pattern.sub(replacement, translated_text)
            
            # Set the final translated text
            if self.window_mode == WINDOW_MODE_COMPACT:
                self.compact_preview.setPlainText(translated_text)
                self.compact_input.setProperty("currentTranslation", translated_text)
            else:
                self.translation_preview.setText(translated_text)
        
        except Exception as e:
            error_msg = f"Translation error: {str(e)}"
            if self.window_mode == WINDOW_MODE_COMPACT:
                self.compact_preview.setPlainText(error_msg)
            else:
                self.translation_preview.setText(error_msg)

    def handle_command(self, command_text):
        """Simple command handling"""
        # Ensure we're only processing the command part
        command_text = command_text.strip()
        if not command_text.startswith(':'):
            return
        
        command = command_text[1:].strip().lower()
        
        if command in ('settings', 'config', 'preferences', 's'):
            self.show_settings()
            
        elif command in ('theme', 'toggle-theme', 't'):
            self.toggle_theme()
            
        elif command in ('dictionary', 'dict', 'd'):
            self.personal_dictionary.exec()
            
        elif command in ('languages', 'langs', 'l'):
            self.show_language_selection(self.from_lang)
            
        elif command in ('help', '?', 'h'):
            self.show_help_dialog()
            
        elif command in ('quit', 'exit', 'q'):
            self.quit_application()
        
        # Clear the command input after processing
        if self.window_mode == WINDOW_MODE_COMPACT:
            self.compact_input.clear()
        else:
            self.input_text.clear()

    def show_help_dialog(self):
        help_text = """
    <h3>Quick Translate Commands</h3>
    <p>Type these commands after a colon (:) in the input field</p>

    <ul>
    <li><b>:settings</b> or <b>:s</b> - Open settings dialog</li>
    <li><b>:theme</b> or <b>:t</b> - Toggle between light and dark theme</li>
    <li><b>:dictionary</b> or <b>:d</b> - Open personal dictionary</li>
    <li><b>:languages</b> or <b>:l</b> - Manage languages</li>
    <li><b>:help</b> or <b>:h</b> - Show this help dialog</li>
    <li><b>:quit</b> or <b>:q</b> - Exit application</li>
    </ul>

    <h3>Keyboard Shortcuts</h3>
    <ul>
    <li><b>Alt+Enter</b> - Execute command</li>
    <li><b>Ctrl+Enter</b> - Insert translation</li>
    <li><b>Esc</b> - Hide window</li>
    <li><b>{}</b> - Show/hide translator</li>
    </ul>
        """.format(GLOBAL_HOTKEY)

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Quick Translate Help")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Apply theme to dialog
        if self.dark_mode:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                }
            """)
        
        msg_box.exec()

    def perform_offline_translation(self, text, from_lang, to_lang):
        """Perform offline translation using downloaded language data"""
        # This is a placeholder for actual offline translation logic
        return f"[Offline] {text}"
    
    def setup_language_selectors(self, layout):
        """Initial language selector setup"""
        selector_widget = QWidget()
        selector_layout = QHBoxLayout(selector_widget)
        selector_layout.setContentsMargins(0, 0, 0, 0)
        selector_layout.setSpacing(6)

        self.from_lang = QComboBox()
        self.to_lang = QComboBox()

        for combo in [self.from_lang, self.to_lang]:
            combo.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            combo.setMaximumWidth(150)

        arrow_label = QLabel("→")
        arrow_label.setStyleSheet("color: #666;")

        selector_layout.addWidget(self.from_lang)
        selector_layout.addWidget(arrow_label)
        selector_layout.addWidget(self.to_lang)
        selector_layout.addStretch()

        layout.addWidget(selector_widget)

        # Initialize languages and update selectors
        self.update_language_selectors()

        # Connect signals after initial setup
        self.from_lang.currentTextChanged.connect(self.on_language_changed)
        self.to_lang.currentTextChanged.connect(self.on_language_changed)
    
    def on_language_changed(self, new_text):
        """Protected method to handle language changes safely"""
        if not new_text:
            return
            
        try:
            # Get current selections
            from_text = self.from_lang.currentText()
            to_text = self.to_lang.currentText()
            
            # Verify both selections are valid
            if from_text in self.source_languages and to_text in self.target_languages:
                from_code = self.source_languages[from_text]
                to_code = self.target_languages[to_text]
                
                # Save the language pair
                self.language_manager.save_language_pair(from_code, to_code)
                self.settings.setValue("last_from_lang", from_code)
                self.settings.setValue("last_to_lang", to_code)
                self.settings.sync()
                
                # Update compact mode language buttons if they exist
                if hasattr(self, 'compact_from_lang') and hasattr(self, 'compact_to_lang'):
                    self.update_compact_language_buttons()
                
                # Trigger new translation if we have text and UI is ready
                if hasattr(self, 'window_mode'):  # Check if UI is initialized
                    if self.window_mode == WINDOW_MODE_COMPACT:
                        if hasattr(self, 'compact_input') and self.compact_input.text().strip():
                            self.translation_timer.start(TRANSLATION_DEBOUNCE_MS)
                    else:
                        if hasattr(self, 'input_text') and self.input_text.toPlainText().strip():
                            self.translation_timer.start(TRANSLATION_DEBOUNCE_MS)
                    
        except KeyError as e:
            print(f"Error saving language pair: Invalid language selection")

    def update_compact_language_buttons(self):
        """Update compact mode language button text"""
        if not hasattr(self, 'compact_from_lang') or not hasattr(self, 'compact_to_lang'):
            return
            
        try:
            # Get current language codes
            from_text = self.from_lang.currentText()
            to_text = self.to_lang.currentText()
            
            # Set abbreviated text for compact buttons
            from_code = self.source_languages.get(from_text, "auto")
            to_code = self.target_languages.get(to_text, "en")
            
            # Use first two letters of the language name, or 'Au' for Auto Detect
            self.compact_from_lang.setText(from_text[:2] if from_code != "auto" else "Au")
            self.compact_to_lang.setText(to_text[:2])
            
            # Store codes as properties
            self.compact_from_lang.setProperty("langCode", from_code)
            self.compact_to_lang.setProperty("langCode", to_code)
        except Exception as e:
            print(f"Error updating compact language buttons: {e}")

    def update_language_selectors(self):
        """Update language selectors with properly formatted language names and defaults"""
        try:
            # Store current selections before clearing
            current_from_name = self.from_lang.currentText() if self.from_lang.currentText() else "Auto Detect"
            current_to_name = self.to_lang.currentText() if self.to_lang.currentText() else "English"
            
            # Get enabled ISO codes - force refresh from disk
            self.settings.sync()
            enabled_iso_codes = self.settings.value("enabled_languages", ["en", "he"])
            
            if not isinstance(enabled_iso_codes, list):
                enabled_iso_codes = ["en", "he"]
            
            # Always include required languages
            for required in ["en", "he"]:
                if required not in enabled_iso_codes:
                    enabled_iso_codes.append(required)
            
            # Rebuild language dictionaries with proper names
            self.source_languages = {}
            self.target_languages = {}
            
            # Always include Auto Detect in source languages
            auto_name = self.language_manager.get_language_name("auto")
            self.source_languages[auto_name] = "auto"
            
            # Add enabled languages with proper names
            for code in enabled_iso_codes:
                # Get proper language name from code
                name = self.language_manager.get_language_name(code)
                
                # Add to source languages
                self.source_languages[name] = code
                
                # Add to target languages (excluding auto)
                if code != "auto":
                    self.target_languages[name] = code
            
            # Update dropdown menus - temporarily block signals
            self.from_lang.blockSignals(True)
            self.to_lang.blockSignals(True)
            
            self.from_lang.clear()
            self.to_lang.clear()
            
            # Add language names to dropdowns (sorted alphabetically, keeping "Auto Detect" first)
            source_language_names = sorted(self.source_languages.keys(), 
                                    key=lambda x: (0 if x == auto_name else 1, x))
            target_language_names = sorted(self.target_languages.keys())
            
            self.from_lang.addItems(source_language_names)
            self.to_lang.addItems(target_language_names)
            
            # Get default language names from settings
            default_from_code = self.settings.value("default_from", "auto")
            default_to_code = self.settings.value("default_to", "en")
            
            default_from_name = self.language_manager.get_language_name(default_from_code)
            default_to_name = self.language_manager.get_language_name(default_to_code)
            
            # Try to restore selections in this order: default, current, auto/first
            if default_from_name in source_language_names:
                self.from_lang.setCurrentText(default_from_name)
            elif current_from_name in source_language_names:
                self.from_lang.setCurrentText(current_from_name)
            elif auto_name in source_language_names:
                self.from_lang.setCurrentText(auto_name)
            elif self.from_lang.count() > 0:
                self.from_lang.setCurrentIndex(0)
            
            if default_to_name in target_language_names:
                self.to_lang.setCurrentText(default_to_name)
            elif current_to_name in target_language_names:
                self.to_lang.setCurrentText(current_to_name)
            elif "English" in target_language_names:
                self.to_lang.setCurrentText("English")
            elif self.to_lang.count() > 0:
                self.to_lang.setCurrentIndex(0)
            
            # Re-enable signals
            self.from_lang.blockSignals(False)
            self.to_lang.blockSignals(False)
            
            # Force UI update
            self.from_lang.update()
            self.to_lang.update()
            
            # Update compact mode language buttons if they exist
            if hasattr(self, 'compact_from_lang') and hasattr(self, 'compact_to_lang'):
                self.update_compact_language_buttons()
            
        except Exception as e:
            print(f"Error updating language selectors: {str(e)}")
            
            # Fallback to basic languages if something goes wrong
            self.source_languages = {"Auto Detect": "auto", "English": "en", "Hebrew": "he"}
            self.target_languages = {"English": "en", "Hebrew": "he"}
            
            self.from_lang.blockSignals(True)
            self.to_lang.blockSignals(True)
            
            self.from_lang.clear()
            self.to_lang.clear()
            self.from_lang.addItems(["Auto Detect", "English", "Hebrew"])
            self.to_lang.addItems(["English", "Hebrew"])
            
            self.from_lang.blockSignals(False)
            self.to_lang.blockSignals(False)

    def closeEvent(self, event):
        """Handle window close events"""
        # Unregister hotkey before hiding
        try:
            kb.unhook_all()
        except:
            pass
        event.ignore()
        self.hide()
        # Re-register hotkey after hiding
        try:
            kb.add_hotkey(GLOBAL_HOTKEY, self.show_window, suppress=True)
        except Exception as e:
            print(f"Error re-registering hotkey: {e}")

    def show_window(self):
        """Show the translation window"""
        # Get currently focused window and control before showing translator
        try:
            self.last_focused_window = self.window_automation.get_focused_window()[1]
            self.last_focused_control = self.window_automation.get_focused_control()[1]
            
            # Only show if we're not already focused
            if (not self.last_focused_window or 
                self.last_focused_window['title'] != APP_NAME):
                QTimer.singleShot(0, self._do_show_window)
        except Exception as e:
            print(f"Error showing window: {e}")
            self._do_show_window()

    def create_full_ui(self):
        """Create the full-size UI"""
        self.full_widget = QWidget()
        self.full_widget.setObjectName("mainWidget")
        full_layout = QVBoxLayout(self.full_widget)
        full_layout.setContentsMargins(0, 0, 0, 0)
        full_layout.setSpacing(0)
        
        # Create title bar with app info and controls
        self.create_title_bar()
        
        # Create main content area
        content = QWidget()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(15, 12, 15, 15)
        content_layout.setSpacing(10)
        
        # Language selectors first (moved above input box)
        lang_container = QWidget()
        lang_layout = QHBoxLayout(lang_container)
        lang_layout.setContentsMargins(0, 0, 0, 0)
        lang_layout.setSpacing(5)
        self.setup_language_selectors(lang_layout)
        content_layout.addWidget(lang_container)
        
        # Input field (now after language selectors)
        self.input_text = QTextEdit()
        self.input_text.setObjectName("inputBox")
        self.input_text.setPlaceholderText("Type to translate or type : followed by a command...")
        self.input_text.textChanged.connect(self.on_text_changed)
        self.input_text.setMaximumHeight(80)  # Limit height for cleaner appearance
        content_layout.addWidget(self.input_text)
        
        # Translation preview area
        self.translation_preview = QTextEdit()
        self.translation_preview.setObjectName("previewBox")
        self.translation_preview.setPlaceholderText("Translation will appear here")
        self.translation_preview.setReadOnly(True)
        content_layout.addWidget(self.translation_preview)
        
        # Insert button
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(5)
        
        actions_layout.addStretch()
        
        insert_btn = QPushButton("Insert (Ctrl+Enter)")
        insert_btn.setObjectName("insertButton")
        insert_btn.clicked.connect(self.insert_translation)
        actions_layout.addWidget(insert_btn)
        
        content_layout.addWidget(actions_container)
        
        # Keyboard shortcuts help
        shortcuts_label = QLabel(f"Press {GLOBAL_HOTKEY} to show/hide • Esc to close • Type : for commands")
        shortcuts_label.setObjectName("shortcutsLabel")
        content_layout.addWidget(shortcuts_label)
        
        full_layout.addWidget(content)
        
        # Add size grip for resizing (moved to bottom of window)
        size_grip_container = QWidget()
        size_grip_container.setObjectName("sizeGripContainer")
        size_grip_layout = QHBoxLayout(size_grip_container)
        size_grip_layout.setContentsMargins(0, 0, 4, 4)
        
        size_grip_layout.addStretch()
        size_grip = QSizeGrip(self)
        size_grip.setObjectName("sizeGrip")
        size_grip_layout.addWidget(size_grip)
        
        full_layout.addWidget(size_grip_container)
        
        # Store references to widgets
        self.full_widgets = {
            'main': self.full_widget,
            'title_bar': self.findChild(QWidget, "titleBar"),
            'content': content,
            'size_grip': size_grip_container
        }
        
        self.full_widget.hide()
        self.layout.addWidget(self.full_widget)

    def create_title_bar(self):
        """Create title bar with modern controls"""
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(8, 6, 8, 6)
        title_bar_layout.setSpacing(4)
        
        # App indicator and title
        title_container = QWidget()
        title_container_layout = QHBoxLayout(title_container)
        title_container_layout.setContentsMargins(0, 0, 0, 0)
        title_container_layout.setSpacing(6)
        
        # App color indicator
        app_indicator = QLabel()
        app_indicator.setObjectName("appIndicator")
        title_container_layout.addWidget(app_indicator)
        
        # App name
        title_label = QLabel(APP_NAME)
        title_label.setObjectName("titleLabel")
        title_container_layout.addWidget(title_label)
        
        title_bar_layout.addWidget(title_container)
        title_bar_layout.addStretch()
        
        # Control buttons
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(6)
        
        # Compact mode button
        compact_btn = QPushButton("⬓")
        compact_btn.setObjectName("compactModeButton")
        compact_btn.clicked.connect(lambda: self.set_window_mode(WINDOW_MODE_COMPACT))
        compact_btn.setToolTip("Switch to compact mode")
        
        # Settings button
        settings_button = QPushButton("⚙")
        settings_button.setObjectName("settingsButton")
        settings_button.clicked.connect(self.show_settings)
        settings_button.setToolTip("Settings")
        
        # Theme button
        self.theme_button = QPushButton("🌙")
        self.theme_button.setObjectName("themeButton")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setToolTip("Toggle theme")
        
        # Window controls
        minimize_btn = QPushButton("−")
        minimize_btn.setObjectName("minimizeButton")
        minimize_btn.clicked.connect(self.hide)
        minimize_btn.setToolTip("Minimize")
        
        close_btn = QPushButton("×")
        close_btn.setObjectName("closeButton")
        close_btn.clicked.connect(self.hide)
        close_btn.setToolTip("Close")
        
        # Add all buttons
        controls_layout.addWidget(compact_btn)
        controls_layout.addWidget(settings_button)
        controls_layout.addWidget(self.theme_button)
        controls_layout.addWidget(minimize_btn)
        controls_layout.addWidget(close_btn)
        
        title_bar_layout.addWidget(controls)
        self.layout.addWidget(title_bar)
    
    def create_compact_ui(self):
        """Create compact UI with improved layout"""
        self.compact_widget = QWidget()
        self.compact_widget.setObjectName("compactWidget")
        compact_layout = QVBoxLayout(self.compact_widget)
        compact_layout.setContentsMargins(0, 0, 0, 0)
        compact_layout.setSpacing(0)
        
        # Compact title bar
        compact_title = QWidget()
        compact_title.setObjectName("compactTitleBar")
        title_layout = QHBoxLayout(compact_title)
        title_layout.setContentsMargins(8, 4, 8, 4)
        title_layout.setSpacing(4)
        
        # App indicator and name
        indicator = QLabel()
        indicator.setObjectName("compactIndicator")
        title_layout.addWidget(indicator)
        
        title_label = QLabel(APP_NAME)
        title_label.setObjectName("compactTitleLabel")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Control buttons
        theme_btn = QPushButton("🌙" if not self.dark_mode else "☀️")
        theme_btn.setObjectName("compactThemeButton")
        theme_btn.clicked.connect(self.toggle_theme)
        theme_btn.setToolTip("Toggle theme")
        
        expand_btn = QPushButton("⬒")
        expand_btn.setObjectName("expandButton")
        expand_btn.clicked.connect(lambda: self.set_window_mode(WINDOW_MODE_FULL))
        expand_btn.setToolTip("Expand to full mode")
        
        close_btn = QPushButton("×")
        close_btn.setObjectName("compactCloseButton")
        close_btn.clicked.connect(self.hide)
        close_btn.setToolTip("Close")
        
        title_layout.addWidget(theme_btn)
        title_layout.addWidget(expand_btn)
        title_layout.addWidget(close_btn)
        
        compact_layout.addWidget(compact_title)
        
        # Compact content
        content = QWidget()
        content.setObjectName("compactContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(6)
        
        # Language selector row first
        lang_row = QWidget()
        lang_row_layout = QHBoxLayout(lang_row)
        lang_row_layout.setContentsMargins(0, 0, 0, 0)
        lang_row_layout.setSpacing(6)
        
        # Source language button on left
        self.compact_from_lang = QPushButton("Au")
        self.compact_from_lang.setObjectName("compactLangButton")
        self.compact_from_lang.clicked.connect(lambda: self.show_language_selection(self.from_lang))
        self.compact_from_lang.setToolTip("Source language")
        
        # Arrow between languages
        arrow_label = QLabel("→")
        arrow_label.setStyleSheet("color: #666;")
        
        # Target language button on right
        self.compact_to_lang = QPushButton("En")
        self.compact_to_lang.setObjectName("compactLangButton")
        self.compact_to_lang.clicked.connect(lambda: self.show_language_selection(self.to_lang))
        self.compact_to_lang.setToolTip("Target language")
        
        lang_row_layout.addWidget(self.compact_from_lang)
        lang_row_layout.addWidget(arrow_label)
        lang_row_layout.addWidget(self.compact_to_lang)
        lang_row_layout.addStretch()
        
        content_layout.addWidget(lang_row)
        
        # Input field (no search icon)
        self.compact_input = QLineEdit()
        self.compact_input.setObjectName("compactInput")
        self.compact_input.setPlaceholderText("Type to translate or : for commands...")
        self.compact_input.textChanged.connect(self.on_compact_text_changed)
        content_layout.addWidget(self.compact_input)
        
        # Translation preview
        self.compact_preview = QTextEdit()
        self.compact_preview.setObjectName("compactPreview")
        self.compact_preview.setReadOnly(True)
        self.compact_preview.setPlaceholderText("Translation will appear here")
        self.compact_preview.setMaximumHeight(80)
        content_layout.addWidget(self.compact_preview)
        
        # Shortcut hint
        compact_hint = QLabel("Ctrl+Enter to insert • Esc to hide")
        compact_hint.setObjectName("compactHint")
        compact_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(compact_hint)
        
        compact_layout.addWidget(content)
        
        # Add size grip
        compact_grip_container = QWidget()
        compact_grip_layout = QHBoxLayout(compact_grip_container)
        compact_grip_layout.setContentsMargins(0, 0, 4, 4)
        compact_grip_layout.addStretch()
        
        compact_grip = QSizeGrip(self)
        compact_grip.setObjectName("compactSizeGrip")
        compact_grip_layout.addWidget(compact_grip)
        
        compact_layout.addWidget(compact_grip_container)
        
        # Store widget references
        self.compact_widgets = {
            'main': self.compact_widget,
            'title': compact_title,
            'content': content,
            'input': self.compact_input,
            'preview': self.compact_preview,
            'theme_button': theme_btn,
            'from_lang': self.compact_from_lang,
            'to_lang': self.compact_to_lang,
            'size_grip': compact_grip_container
        }
        
        self.compact_widget.hide()
        self.layout.addWidget(self.compact_widget)
    
    def on_compact_text_changed(self):
        """Handle text changes in compact mode"""
        text = self.compact_input.text().strip()
        
        # Check for commands
        if text.startswith(':'):
            if text.endswith('\r') or text.endswith('\n'):  # Enter key pressed
                self.handle_command(text)
                return
            # Don't trigger translation for commands
            return
        
        if text:
            self.translation_timer.start(TRANSLATION_DEBOUNCE_MS)
        else:
            self.compact_preview.setPlainText("")
    
    def on_text_changed(self):
        """Handle text input changes with enhanced command experience"""
        if self.window_mode == WINDOW_MODE_COMPACT:
            text = self.compact_input.text().strip()
            
            # Apply special styling for command input
            if text.startswith(':'):
                self.compact_input.setStyleSheet("""
                    QLineEdit {
                        color: #4da6ff;
                        font-weight: bold;
                    }
                """)
                # Show command help hint
                self.compact_preview.setPlainText("Type a command: :s (settings), :t (theme), :d (dictionary), :h (help)...")
                return
            else:
                # Restore normal styling
                self.compact_input.setStyleSheet("")
        else:
            text = self.input_text.toPlainText().strip()
            
            # Apply special styling for command input
            if text.startswith(':'):
                self.input_text.setStyleSheet("""
                    QTextEdit {
                        color: #4da6ff;
                        font-weight: bold;
                    }
                """)
                # Show command help hint
                self.translation_preview.setText("Type a command: :s (settings), :t (theme), :d (dictionary), :h (help)...")
                return
            else:
                # Restore normal styling
                self.input_text.setStyleSheet("")
        
        # Normal translation behavior
        if text:
            # Check for context keywords before starting translation timer
            context = self.context_manager.get_context_for_text(text)
            if context != "General":
                # Notify user about context detection
                self.show_context_notification(context)
        
        self.translation_timer.start(TRANSLATION_DEBOUNCE_MS)

    def show_context_notification(self, context):
        """Show temporary notification about detected context"""
        notification = f"Using {context} context for translation..."
        
        if self.window_mode == WINDOW_MODE_COMPACT:
            self.compact_preview.setPlainText(notification)
        else:
            self.translation_preview.setText(notification)
            
        # Use a timer to clear the notification after a short delay
        QTimer.singleShot(1500, lambda: self.translation_timer.start(0))

    def handle_translation_result(self, result):
        """Handle completed translation result"""
        if not result or not result.full_text:
            return
            
        if self.window_mode == WINDOW_MODE_COMPACT:
            self.compact_preview.setPlainText(result.full_text)
            self.compact_input.setProperty("currentTranslation", result.full_text)
        else:
            self.translation_preview.setText(result.full_text)
            
    def handle_suggestions(self, suggestions):
        """Handle translation suggestions"""
        if not suggestions:
            return
            
        current_text = (
            self.compact_preview.toPlainText() 
            if self.window_mode == WINDOW_MODE_COMPACT 
            else self.translation_preview.toPlainText()
        )
        
        # Only show dialog if we have valid suggestions
        if current_text and suggestions:
            dialog = TranslationSuggestionDialog(current_text, suggestions, self)
            if dialog.exec() == QDialog.DialogCode.Accepted and dialog.accepted_suggestions:
                updated_text = current_text
                for suggestion in dialog.accepted_suggestions:
                    updated_text = updated_text.replace(
                        suggestion.original_word,
                        suggestion.suggested_word
                    )
                
                if self.window_mode == WINDOW_MODE_COMPACT:
                    self.compact_preview.setPlainText(updated_text)
                    self.compact_input.setProperty("currentTranslation", updated_text)
                else:
                    self.translation_preview.setText(updated_text)
    
    def save_window_state(self):
        """Save current window state and position"""
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("window_pos", self.pos())
        self.settings.setValue("window_size", self.size())
        if self.window_mode == WINDOW_MODE_COMPACT:
            self.settings.setValue("compact_window_size", self.size())
        self.settings.sync()
    
    def restore_window_state(self):
        """Enhanced window state restoration"""
        geometry = self.settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Restore compact mode size if available
        if self.window_mode == WINDOW_MODE_COMPACT:
            size = self.settings.value("compact_window_size")
            if size and isinstance(size, QSize):
                self.resize(size)
            else:
                self.resize(*COMPACT_WINDOW_SIZE)

    def set_window_mode(self, mode):
        """Switch between full and compact window modes"""
        self.window_mode = mode
        self.settings.setValue("window_mode", mode)
        
        # Hide all widgets first
        if hasattr(self, 'full_widget'):
            for widget in self.full_widgets.values():
                if widget:
                    widget.hide()
            
        if hasattr(self, 'compact_widgets'):
            for widget in self.compact_widgets.values():
                if widget:
                    widget.hide()
        
        if mode == WINDOW_MODE_COMPACT:
            # Show compact UI
            for widget in self.compact_widgets.values():
                if widget:
                    widget.show()
            self.setMinimumSize(*COMPACT_WINDOW_SIZE)
            
            # Update compact language buttons
            self.update_compact_language_buttons()
            
            # Preserve input text if switching modes
            if hasattr(self, 'input_text') and self.input_text.toPlainText():
                self.compact_input.setText(self.input_text.toPlainText())
                self.compact_preview.setPlainText(self.translation_preview.toPlainText())
        else:
            # Show full UI
            for widget in self.full_widgets.values():
                if widget:
                    widget.show()
            self.setMinimumSize(*WINDOW_DEFAULT_SIZE)
            
            # Preserve input text if switching modes
            if hasattr(self, 'compact_input') and self.compact_input.text():
                self.input_text.setPlainText(self.compact_input.text())
                self.translation_preview.setText(self.compact_preview.toPlainText())
        
        # Force layout update
        self.layout.activate()
        self.adjustSize()
        self.update()

    def create_tray_icon(self):
        """Create system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        try:
            self.tray_icon.setIcon(QIcon.fromTheme("edit-paste"))
        except:
            self.tray_icon.setIcon(QIcon.fromTheme("accessories-text-editor"))
        
        tray_menu = QMenu()
        show_action = QAction("Show Translator", self)
        settings_action = QAction("Settings", self)
        quit_action = QAction("Quit", self)
        
        show_action.triggered.connect(self.show_window)
        settings_action.triggered.connect(self.show_settings)
        quit_action.triggered.connect(self.quit_application)
        
        # Add mode toggle to tray menu
        mode_menu = QMenu("Window Mode", self)
        
        full_action = QAction(WINDOW_MODE_FULL, self)
        compact_action = QAction(WINDOW_MODE_COMPACT, self)
        
        full_action.setCheckable(True)
        compact_action.setCheckable(True)
        
        mode_group = QActionGroup(self)
        mode_group.addAction(full_action)
        mode_group.addAction(compact_action)
        
        if self.window_mode == WINDOW_MODE_FULL:
            full_action.setChecked(True)
        else:
            compact_action.setChecked(True)
            
        full_action.triggered.connect(lambda: self.set_window_mode(WINDOW_MODE_FULL))
        compact_action.triggered.connect(lambda: self.set_window_mode(WINDOW_MODE_COMPACT))
        
        mode_menu.addAction(full_action)
        mode_menu.addAction(compact_action)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(settings_action)
        tray_menu.addMenu(mode_menu)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.setToolTip(APP_NAME)
        self.tray_icon.show() 

    def toggle_theme(self):
        """Toggle between light and dark themes with accent color preservation"""
        self.dark_mode = not self.dark_mode
        self.settings.setValue("dark_mode", self.dark_mode)
        
        # Get current accent color
        accent_color = self.settings.value("accent_color", "Blue")
        
        # Get updated theme with accent color
        main_theme, compact_theme = apply_accent_color(accent_color, self.dark_mode)
        
        # Apply theme
        self.setStyleSheet(main_theme)
        
        # Update icon
        self.theme_button.setText("☀️" if self.dark_mode else "🌙")
        if hasattr(self, 'compact_widgets') and 'theme_button' in self.compact_widgets:
            self.compact_widgets['theme_button'].setText("☀️" if self.dark_mode else "🌙")
        
        # Update any child dialogs
        for child in self.findChildren(QDialog):
            if hasattr(child, 'apply_theme'):
                child.apply_theme()

    def update_detection_status(self):
        """Update language detection status"""
        if self.detected_language:
            # Get language name from code
            detected_name = self.language_manager.get_language_name(self.detected_language)
            self.from_lang.setToolTip(f"Detected: {detected_name}")

    def _do_show_window(self):
        """Show and position window according to settings"""
        window_position = self.settings.value("window_position", POSITION_CURSOR)
        
        if window_position == POSITION_CURSOR and self.last_focused_control:
            self._position_near_cursor()
        elif window_position == POSITION_LAST:
            geometry = self.settings.value("window_geometry")
            if geometry:
                self.restoreGeometry(geometry)
            else:
                self.center_on_screen()
        else:
            self.center_on_screen()
        
        self.show()
        self.activateWindow()
        self.raise_()
        QTimer.singleShot(100, self._set_input_focus)

    def _set_input_focus(self):
        """Set focus to the appropriate input field"""
        if self.window_mode == WINDOW_MODE_COMPACT:
            self.compact_input.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        else:
            self.input_text.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def _position_near_cursor(self):
        """Position window near text cursor or mouse cursor"""
        if not self.last_focused_control:
            self.center_on_screen()
            return
            
        screen = QApplication.primaryScreen()
        if not screen:
            return
            
        screen_geometry = screen.geometry()
        cursor_pos = QCursor.pos()
        
        # Calculate position with offset
        x = cursor_pos.x() + CURSOR_OFFSET_X
        y = cursor_pos.y() + CURSOR_OFFSET_Y
        
        # Ensure window stays within screen bounds
        x = min(max(x, screen_geometry.x()), 
                screen_geometry.width() - self.width())
        y = min(max(y, screen_geometry.y()), 
                screen_geometry.height() - self.height())
        
        self.move(x, y)

    def insert_translation(self):
        """Insert translation with context-aware improvements"""
        if self.window_mode == WINDOW_MODE_COMPACT:
            translation = self.compact_input.property("currentTranslation")
            if not translation:
                translation = self.compact_preview.toPlainText()
        else:
            translation = self.translation_preview.toPlainText()
            
        if not translation:
            return
            
        insertion_method = self.settings.value("insertion_method", INSERT_DIRECT)
        
        if insertion_method == INSERT_DIRECT:
            try:
                if (self.last_focused_control and 
                    self.last_focused_control['is_text_field']):
                    hwnd = self.last_focused_control['handle']
                    
                    # Set focus back to original window
                    if self.last_focused_window:
                        win32gui.SetForegroundWindow(self.last_focused_window['handle'])
                    
                    self.window_automation.simulate_text_input(hwnd, translation)
                    
                    # Clear and hide translator
                    if self.window_mode == WINDOW_MODE_COMPACT:
                        self.compact_input.clear()
                    else:
                        self.input_text.clear()
                        self.translation_preview.clear()
                    self.hide()
                    return
            except Exception as e:
                print(f"Error with direct input: {e}")
        
        # Fall back to clipboard method
        self._clipboard_insert(translation)

    def _clipboard_insert(self, text):
        """Fall back to clipboard-based insertion"""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            
            self.hide()
            QTimer.singleShot(100, self._do_paste)
        except Exception as e:
            print(f"Error copying to clipboard: {e}")

    def _do_paste(self):
        """Simulate Ctrl+V paste shortcut"""
        if self.last_focused_window:
            try:
                win32gui.SetForegroundWindow(self.last_focused_window['handle'])
                kb.press_and_release('ctrl+v')
            except Exception as e:
                print(f"Error pasting text: {e}")
        
        if self.window_mode == WINDOW_MODE_COMPACT:
            self.compact_input.clear()
        else:
            self.input_text.clear()
            self.translation_preview.clear()
    
    def quit_application(self):
        """Quit the application with cleanup"""
        try:
            kb.unhook_all()
            self.save_window_state()
            self.settings.sync()
        finally:
            QApplication.instance().quit()

    def mousePressEvent(self, event):
        """Handle mouse press events for window dragging"""
        if self.window_mode == WINDOW_MODE_COMPACT:
            if self.compact_widgets['title'].geometry().contains(event.pos()):
                self.old_pos = event.globalPosition().toPoint()
            else:
                self.old_pos = None
        else:
            if event.position().y() <= self.title_bar_height:
                self.old_pos = event.globalPosition().toPoint()
            else:
                self.old_pos = None

    def mouseMoveEvent(self, event):
        """Handle mouse move events for window dragging"""
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        self.old_pos = None

    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        title_bar = self.findChild(QWidget, "titleBar")
        if title_bar:
            self.title_bar_height = title_bar.height()

    def showEvent(self, event):
        """Handle window show events"""
        super().showEvent(event)
        if not hasattr(self, 'has_been_shown'):
            self.center_on_screen()
            self.has_been_shown = True
            
    def center_on_screen(self):
        """Center the window on the screen"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            self.move(
                (screen_geometry.width() - self.width()) // 2,
                (screen_geometry.height() - self.height()) // 2
            )

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for both modes"""
        # Process Alt+Enter for command execution
        if (event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter) and \
        event.modifiers() == Qt.KeyboardModifier.AltModifier:
            if self.window_mode == WINDOW_MODE_COMPACT:
                text = self.compact_input.text().strip()
                if text.startswith(':'):
                    self.handle_command(text)
                    self.compact_input.clear()
                    return
            else:  # Full mode
                text = self.input_text.toPlainText().strip()
                if text.startswith(':'):
                    # Handle first line only if there are multiple lines
                    lines = text.split('\n')
                    if lines:
                        command = lines[0].strip()
                        self.handle_command(command)
                        self.input_text.clear()
                    return
        
        # Regular Enter key handling remains the same
        if (event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter) and not event.modifiers():
            if self.window_mode == WINDOW_MODE_COMPACT:
                text = self.compact_input.text().strip()
                if text.startswith(':'):
                    self.handle_command(text)
                    self.compact_input.clear()
                    return
        
        # Handle Ctrl+Enter for insertion
        if (event.key() == Qt.Key.Key_Return and 
            event.modifiers() == Qt.KeyboardModifier.ControlModifier):
            self.insert_translation()
            return
        
        # Handle Escape
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            return
        
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close events"""
        event.ignore()
        self.hide()

    def apply_theme(self):
        """Apply theme with accent color support using theme utils"""
        # Get current accent color
        accent_color = self.settings.value("accent_color", "Blue")
        
        # Get updated theme with accent color
        main_theme, compact_theme = apply_accent_color(accent_color, self.dark_mode)
        
        # Apply main theme to the application window
        self.setStyleSheet(main_theme)
        
        # Apply compact theme directly to the compact widget
        if hasattr(self, 'compact_widget') and self.compact_widget:
            # Force style refresh by removing and reapplying properties
            self.compact_widget.setProperty("darkMode", self.dark_mode)
            self.compact_widget.setStyleSheet("")  # Clear first
            self.compact_widget.setStyleSheet(compact_theme)  # Then set
            
            # Apply styles to individual compact widgets to ensure proper propagation
            for name, widget in self.compact_widgets.items():
                if widget:
                    widget.setProperty("darkMode", self.dark_mode)
                    if hasattr(widget, 'style'):
                        widget.style().unpolish(widget)
                        widget.style().polish(widget)
        
        # Update theme button icons
        self.theme_button.setText("☀️" if self.dark_mode else "🌙")
        if hasattr(self, 'compact_widgets') and 'theme_button' in self.compact_widgets:
            self.compact_widgets['theme_button'].setText("☀️" if self.dark_mode else "🌙")

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()

    def save_window_state(self):
        """Save current window position and size"""
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.sync()

    def restore_window_state(self):
        """Restore saved window position and size"""
        geometry = self.settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def check_personal_dictionary(self, text):
        """Check personal dictionary with context awareness"""
        if not text.strip():
            return None

        # Get context based on keywords
        context = self.personal_dictionary.keyword_manager.get_context_for_text(text)
        
        # Try context-specific translation first
        translation = self.personal_dictionary.keyword_manager.get_translation(text, context)
        if translation:
            return translation

        # Fall back to regular dictionary lookup
        result = self.personal_dictionary.get_translation(text, context)
        if result and isinstance(result, dict):
            if result.get("type") == "exact":
                return result["translation"]
            elif result.get("type") == "similar" and result.get("entries"):
                dialog = SuggestionDialog(text, result["entries"], self)
                if hasattr(self, 'dark_mode'):
                    dialog.apply_theme(self.dark_mode)
                
                if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_translation:
                    return dialog.selected_translation

        return None

    def hideEvent(self, event):
        """Save window position when hiding if using last position setting"""
        if self.settings.value("window_position") == POSITION_LAST:
            self.save_window_state()
        super().hideEvent(event)

    def normalize_language_code(self, code):
        """Normalize a language code to its correct form"""
        # If code is a language name, convert to code
        for name, valid_code in LANGUAGES.items():
            if code.lower() == name.lower() or code.lower() == valid_code.lower():
                return valid_code
        return code.lower()