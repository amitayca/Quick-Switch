import os
from googletrans.constants import LANGUAGES as GOOGLE_LANGUAGES

# Create properly capitalized language names dictionary
# while preserving the original codes from Google's LANGUAGES
LANGUAGES = {name.capitalize() if name != 'auto' else 'Auto Detect': code 
             for name, code in GOOGLE_LANGUAGES.items()}

# Special cases for multi-word languages or specific capitalizations
LANGUAGE_OVERRIDES = {
    'Chinese (simplified)': 'zh-cn',
    'Chinese (traditional)': 'zh-tw',
    'Auto Detect': 'auto'
}

# Apply overrides
LANGUAGES.update(LANGUAGE_OVERRIDES)

# Remove 'auto' from target languages
TARGET_LANGUAGES = {k: v for k, v in LANGUAGES.items() if k != 'Auto Detect'}

WINDOW_DEFAULT_SIZE = (450, 400)
TRANSLATION_DEBOUNCE_MS = 500
GLOBAL_HOTKEY = 'ctrl+shift+h'
APP_NAME = 'Quick Translate'
ORGANIZATION_NAME = 'QuickTranslate'
SETTINGS_NAME = 'TranslationApp'

# Window modes
WINDOW_MODE_FULL = "Full Window"
WINDOW_MODE_COMPACT = "Compact Mode"

# Compact mode dimensions
COMPACT_WINDOW_SIZE = (300, 80)

# Window positioning constants
POSITION_CURSOR = "Near Text Cursor"
POSITION_CENTER = "Center of Screen"
POSITION_LAST = "Last Position"
CURSOR_OFFSET_X = 20
CURSOR_OFFSET_Y = 20

# Text insertion methods
INSERT_DIRECT = "Direct Input"
INSERT_CLIPBOARD = "Clipboard Only"

# Automation settings
TEXT_CONTROL_CLASSES = {
    'Edit',  # Standard text boxes
    'RichEdit20W',  # Rich text boxes
    'TextBox',  # .NET text boxes
    'Chrome_RenderWidgetHostHWND',  # Chrome text fields
    'MozillaWindowClass'  # Firefox text fields
}

# Window positioning
CURSOR_OFFSET_X = 20
CURSOR_OFFSET_Y = 20

DEFAULT_LANGUAGE_PAIRS = [
    ('auto', 'he'),  # Auto to Hebrew
    ('he', 'en'),    # Hebrew to English
    ('en', 'he'),    # English to Hebrew
]