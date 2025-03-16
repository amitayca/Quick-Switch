# Quick Translate Documentation

## Project Overview
Quick Translate is a desktop application providing real-time translation capabilities with dual interface modes, global hotkey activation, and seamless Windows integration. The application features a modern FLOW Launcher-inspired UI with improved usability and context-aware translation.

## Latest Implementations

### 1. FLOW Launcher-Inspired UI Design
- Modern UI with rounded corners and subtle shadows
- Redesigned input areas for better usability
- Improved layout organization with language selectors above input box
- Enhanced compact mode with better consistency
- Command system with visual feedback (text color changes when typing commands)

### 2. Fixed UI Issues
- Corrected title bar text colors
- Improved text box styling in both themes
- Fixed resize handle placement
- Implemented proper rounded corner design with translucent background

### 3. Command System Improvements
- Command execution with Alt+Enter shortcut
- Added short command aliases (e.g., `:s` for settings)
- Visual feedback when typing commands
- Help dialog with command reference and shortcuts
- Fixed command processing in both window modes

### 4. Context-Aware Translation
- Context detection functionality based on keywords
- Context notifications with auto-clearing
- Integration between translation and dictionary systems
- Support for multiple keywords in a single text

### 5. Settings Dialog Enhancement
- Tabbed interface with Languages, Appearance, and Advanced sections
- Theme selection with dark/light mode options
- Accent color selection with visual color swatches
- Language management with search functionality
- Window behavior configuration

## Known Issues and Bugs

### 1. Personal Dictionary
- **Bug**: Keywords in the personal dictionary are detected, but translations aren't applied correctly. Context identification works, but the actual text replacement in the translation doesn't function as expected.

### 2. Theme Management
- **Bug**: Accent color changes don't apply immediately after accepting the settings dialog. Changes only become visible after switching between dark/light modes.
- **Bug**: Dark mode in compact view doesn't display correctly. Only light mode works properly in compact view.

### 3. UI Refinements Needed
- Current UI requires additional refinements to achieve a cleaner and more modern appearance.
- Command text color should match the selected accent color for better visual consistency.
- Match the design of the window settings for the rest of the UI.

### 4. Other Issues
- Custom color selection utility needs improvement

## Pending Tasks

### 1. Bug Fixes
- Fix personal dictionary translation functionality
- Resolve theme application issues in compact mode
- Implement immediate accent color updates
- Correct styling issues in light/dark modes

### 2. UI Refinements
- Further optimize compact mode appearance
- Improve input/output field design
- Enhance visual feedback for language selection
- Consider additional animations for window appearance

### 3. Feature Enhancements
- Implement translation caching for improved performance
- Add automatic context detection refinements
- Delete any duplication in code or useless modules
- Implement AI translation options
- Add translation history functionality
- Enhance personal dictionary with import/export capabilities
- Add language usage statistics and recommendations
- Complete offline mode addition

## Project Structure
Quick Switch/
├── main.py                      # Application entry point
├── requirements.txt             # Project dependencies
├── setup.py                     # Setup configuration
├── README.md                    # Project overview
├── DOCUMENTATION.md             # Detailed documentation
├── __init__.py
└── src/
│   └── components/              # UI Components
│        ├── __init__.py
│        ├── language_dialogs.py  # Language selection dialogs
│        ├── settings_dialog.py   # Settings and dictionary interface
│        ├── color_selector_dialog.py  # Color selection components
│        └── translation_window.py # Main application window
│   └── utils/                   # Utility modules
│        ├── __init__.py
│        ├── constants.py         # Application constants and config
│        ├── context_manager.py   # Context management system
│        ├── dictionary_utils.py  # Dictionary functionality
│        ├── language_manager.py  # Language management utilities
│        ├── styles.py            # Theme definitions and styling
│        ├── suggestion_dialog.py # Translation suggestions
│        ├── theme_utils.py       # Theme management utilities
│        ├── translation_manager.py # Translation handling
│        └── window_automation.py # Windows integration utilities
│   └── offline_languages/
└── └── resources/

## Key Files Overview

### Main Components

1. `main.py` - Application entry point that initializes the main window and application loop

2. `translation_window.py` - Main application window with translation functionality, handling window management, UI creation, and translation operations

3. `settings_dialog.py` - Settings management with tabbed interface for language configuration, theme settings, and personal dictionary editor

4. `language_dialogs.py` - Language selection interface with filtering, search, and selection functionality

### Utility Modules

1. `constants.py` - Defines application-wide constants including window dimensions, key bindings, translation settings, and language data. Centralizes configuration values to ensure consistency throughout the application.

2. `language_manager.py` - Singleton class that manages language data including proper name-to-code and code-to-name mapping, recent language tracking, and persistence of language settings. Provides a unified API for language operations.

3. `styles.py` - Contains complete stylesheet definitions for both dark and light themes, including specific styling for compact mode. Centralizes UI styling to maintain consistent appearance.

4. `theme_utils.py` - Provides functions to generate theme-appropriate styles for dialogs and UI components. Ensures consistent theming across the application based on the user's selected theme.

5. `window_automation.py` - Handles interaction with Windows systems, providing text field detection, focus management, and text insertion capabilities for seamless integration.

6. `context_manager.py` - Manages translation contexts and domain-specific terminology, determining appropriate contexts based on text content and maintaining keyword sets.

7. `dictionary_utils.py` - Provides utilities for personal dictionary functionality, including context analysis, similarity detection, and suggestion handling.

8. `suggestion_dialog.py` - Implements the UI for displaying translation suggestions based on the user's personal dictionary and translation context.

9. `translation_manager.py` - Manages the translation pipeline, combining Google Translate with personal dictionary and context-awareness to provide enhanced translations.

## Core Features

### 1. Translation Interface
- Full window mode for complete control
- Compact mode for quick translations
- Context-aware real-time translation
- Intelligent word replacement system (when working correctly)
- Direct text insertion capability

### 2. Window Management
- Global hotkey activation (Ctrl+Shift+H)
- Multiple window positioning options
- Size persistence across sessions
- Window mode switching

### 3. Theming and UI
- Light/Dark theme switching
- Accent color customization
- Consistent styling across components (with some exceptions in compact mode)
- Responsive layouts
- System tray integration

### 4. Language Management
- Configurable language selection
- Search functionality for languages
- Language pair persistence
- Recent languages tracking
- Proper language name display
- Settings-UI synchronization

### 5. Command System
- Command prefix with colon (:)
- Visual feedback when typing commands
- Alt+Enter to execute commands
- Command aliases for common actions
- Help dialog with command reference

## Implementation Details

### FLOW Launcher-Inspired UI

The UI follows FLOW Launcher principles:
- Clean, minimalist design with ample whitespace
- Focus on keyboard-driven interaction
- Rounded corners and subtle shadow effects
- Streamlined controls with clear visual hierarchy
- Command-driven interface with colon prefix

### Command System

The command system supports:
- Simple text commands starting with a colon (`:`)
- Command execution on Alt+Enter key press
- Visual feedback when typing commands
- Short aliases for common commands
- Help dialog with command reference

### Context-Aware Translation

The context detection system:
- Identifies context based on text keywords
- Retrieves context-specific translations from the dictionary (detection works, but application has issues)
- Shows context notification with auto-clearing
- Falls back to regular translation when needed
- Maintains performance during translation

## Best Practices

### UI Design
- Maintain consistent spacing and alignment
- Use subtle animations for transitions
- Ensure proper contrast in both themes
- Follow FLOW Launcher design principles for minimal, clean UI

### Code Organization
- Keep theme logic separate from application logic
- Use proper error handling throughout
- Maintain clear data flow between components
- Document new functionality clearly

### Settings Management
- Store user preferences consistently
- Apply settings changes immediately
- Provide clear visual feedback for settings changes
- Implement proper default values

### Language Management
- Store language codes in settings, not names
- Use bidirectional mappings for efficient lookups
- Always handle language conversions through the LanguageManager
- Include fallback options for error resilience
- Maintain consistent capitalization of language names
- Use explicit settings synchronization when updating language preferences
- Separate UI display (names) from data storage (codes)
- Implement proper validation for user-selected languages

### Theme Management
- Use centralized theme definitions
- Implement proper theme inheritance for child dialogs
- Maintain consistent styling across components
- Ensure color schemes are consistent within each theme
- Use theme-aware icons and visual elements
- Apply themes reactively when user preferences change

### Window Management
- Respect user settings for positioning and behavior
- Implement proper positioning with screen boundary checks
- Handle DPI scaling appropriately
- Manage window state persistence
- Implement proper focus handling
- Ensure keyboard navigation works consistently

## Installation and Requirements

### Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

### Dependencies
```bash
pip install -r requirements.txt
```

### Requirements
- Python 3.8+
- PyQt6
- googletrans==3.1.0a0
- keyboard
- pywin32