
# Quick Translate Documentation

## Project Overview
Quick Translate is a desktop application providing real-time translation capabilities with dual interface modes, global hotkey activation, and seamless Windows integration.

## Recent Implementations

### 1. Window Positioning
- Implemented proper window positioning based on settings
- Added support for cursor, center, and last position options
- Implemented screen boundary checks
- Added position offset constants

### 2. Theme System Enhancements
- Implemented consistent theming across main window and dialogs
- Added theme inheritance for child windows
- Standardized color schemes for light and dark modes
- Fixed theme-related styling issues in dialogs

### 3. Language Management Improvements
- Added language management interface in settings
- Implemented language filtering functionality
- Added search capability for languages
- Removed duplicate language entries
- Added persistence for language selections
- Fixed language display to show proper names instead of codes
- Implemented robust synchronization between settings and UI
- Added bidirectional mapping between language codes and names
- Enhanced error handling in language selection processes

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
│        ├──translation_manager.py # Translation handling
│        └── window_automation.py # Windows integration utilities
│   └── offline_languages/
└── └── resources/

## Key Files Overview

### Main Components

1. `main.py` - Application entry point that initializes the main window and application loop

2. `translation_window.py` - Main application window with translation functionality, handling window management, UI creation, and translation operations

3. `settings_dialog.py` - Settings management with language configuration and personal dictionary editor for custom translations

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
- Intelligent word replacement system
- Direct text insertion capability

### 2. Window Management
- Global hotkey activation (Ctrl+Shift+H)
- Multiple window positioning options
- Size persistence across sessions
- Window mode switching

### 3. Theming and UI
- Light/Dark theme switching
- Consistent styling across components
- Responsive layouts
- System tray integration

### 4. Language Management
- Configurable language selection
- Search functionality for languages
- Language pair persistence
- Recent languages tracking
- Proper language name display
- Settings-UI synchronization

## Language Management System

The language management system provides consistent handling of language codes and names throughout the application:

### LanguageManager Class
- Implements singleton pattern for consistent state across the application
- Maintains bidirectional mappings between language codes and properly formatted names
- Handles language code normalization and name formatting
- Tracks recent language selections
- Provides consistent API for language operations

### UI/Data Layer Separation
- UI layer displays properly formatted language names ("English", "Spanish")
- Data layer stores standardized language codes ("en", "es")
- Qt's role-based data storage associates codes with UI elements

### Settings Synchronization
- Settings dialog saves language codes to persistent storage
- Translation window reads language codes and converts to names for display
- Explicit settings synchronization ensures changes propagate correctly

## Pending Tasks

### 1. Language Management Integration
- Add language selection validation and error handling
- Improve language pair management across multiple sessions
- Implement language usage statistics for UI optimization
- Add support for language auto-detection toggle
- Add a better handling of default languages.

### 2. UI Refinements
- Fix remaining theme inconsistencies in specialized dialogs
- Enhance dialog styling for better visual hierarchy
- Improve language selector UI with additional metadata
- Add visual feedback for language changes and selections
- Design the theme to be more modern and stylish

### 3. Core Functionality
- Enhance error handling in translation engine integration
- Implement translation caching for improved performance
- Add automatic context detection refinements
- Delete any dupliction in code or useless moudles

### 4. Feature Enhancements
- Implement AI translation options
- Add translation history functionality
- Enhance personal dictionary with import/export capabilities
- Add language usage statistics and recommendations
- Remove minimaize button
- Complete offline mode addtion

## Best Practices

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

### Code Organization
- Maintain clear separation of concerns
- Use consistent naming conventions
- Follow Qt design patterns
- Implement singleton pattern for shared services
- Use composition over inheritance where appropriate
- Document public APIs and key implementation details

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
Dependencies
bashCopypip install -r requirements.txt
Requirements

Python 3.8+
PyQt6
googletrans==3.1.0a0
keyboard
pywin32