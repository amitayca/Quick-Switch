# Location: Quick Switch/src/utils/styles.py

def get_color_variants(base_color):
    """Generate color variants based on a main color hex value.
    Returns a dict with hover, pressed, disabled, and other variants."""
    # Simple implementation - for production, use proper color manipulation
    if base_color.startswith('#'):
        base_color = base_color[1:]
    
    # Convert hex to RGB
    r = int(base_color[0:2], 16)
    g = int(base_color[2:4], 16)
    b = int(base_color[4:6], 16)
    
    # Create lighter variant (for hover)
    lighter = f"#{min(r + 20, 255):02x}{min(g + 20, 255):02x}{min(b + 20, 255):02x}"
    
    # Create darker variant (for pressed)
    darker = f"#{max(r - 20, 0):02x}{max(g - 20, 0):02x}{max(b - 20, 0):02x}"
    
    # Create transparent variant (with 80% opacity)
    transparent = f"rgba({r}, {g}, {b}, 0.8)"
    
    # Create disabled variant (more desaturated)
    avg = (r + g + b) // 3
    disabled = f"#{(r + avg) // 2:02x}{(g + avg) // 2:02x}{(b + avg) // 2:02x}"
    
    return {
        'base': f"#{base_color}",
        'hover': lighter,
        'pressed': darker,
        'transparent': transparent,
        'disabled': disabled
    }

def get_dark_theme(accent_color="#4da6ff"):
    """Generate dark theme styles with custom accent color"""
    colors = get_color_variants(accent_color)
    
    return f"""
    /* FLOW-inspired Main Window */
    QMainWindow {{
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 12px;
    }}
    
    /* Title Bar with cleaner styling */
    #titleBar {{
        background-color: #2d2d2d;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        padding: 6px 8px;
        border-bottom: 1px solid #333;
    }}
    
    #titleLabel {{
        color: #ffffff;
        font-size: 13px;
        font-weight: normal;
    }}
    
    /* App indicator dot */
    #appIndicator {{
        border-radius: 4px;
        min-width: 8px;
        min-height: 8px;
        max-width: 8px;
        max-height: 8px;
        background-color: {colors['base']};
    }}
    
    /* Content area */
    #content {{
        background-color: #2d2d2d;
        padding: 12px;
    }}
    
    /* FLOW-style search input */
    #inputBox {{
        background-color: #1f1f1f;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 8px 12px 8px 36px;
        font-size: 13px;
        selection-background-color: {colors['base']};
        selection-color: #ffffff;
    }}
    
    #inputBox:focus {{
        background-color: #262626;
        border: 1px solid {colors['base']};
    }}
    
    /* Search icon styling */
    #searchIcon {{
        color: #666;
        padding-left: 12px;
    }}
    
    /* Translation results area */
    #previewBox {{
        background-color: #1f1f1f;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-size: 13px;
        selection-background-color: {colors['base']};
        selection-color: #ffffff;
        margin-top: 8px;
    }}
    
    /* Modern ComboBox styling */
    QComboBox {{
        border: none;
        border-radius: 6px;
        padding: 6px 8px;
        background-color: transparent;
        color: {colors['base']};
        min-width: 60px;
        max-width: 120px;
        font-size: 12px;
    }}
    
    QComboBox:hover {{
        background-color: #3d3d3d;
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 16px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid {colors['base']};
        margin-right: 5px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: #2d2d2d;
        color: #ffffff;
        selection-background-color: #3d3d3d;
        selection-color: #ffffff;
        border: 1px solid #444;
        border-radius: 6px;
        padding: 4px;
    }}
    
    /* Buttons with FLOW-style */
    #langButton {{
        background-color: transparent;
        color: {colors['base']};
        border: none;
        border-radius: 6px;
        padding: 6px 8px;
        font-size: 12px;
        text-align: center;
    }}
    
    #langButton:hover {{
        background-color: #3d3d3d;
    }}
    
    QPushButton {{
        background-color: transparent;
        color: #cccccc;
        border: none;
        border-radius: 6px;
        padding: 6px 8px;
        font-size: 12px;
    }}
    
    QPushButton:hover {{
        background-color: #3d3d3d;
    }}
    
    /* Modern control buttons */
    #settingsButton, #themeButton, #compactModeButton {{
        background-color: transparent;
        color: #aaaaaa;
        border: none;
        border-radius: 6px;
        padding: 4px;
        font-size: 14px;
        min-width: 24px;
        max-width: 24px;
        min-height: 24px;
        max-height: 24px;
    }}
    
    #settingsButton:hover, #themeButton:hover, #compactModeButton:hover {{
        background-color: #3d3d3d;
        color: #ffffff;
    }}
    
    /* Close, minimize buttons */
    #minimizeButton, #closeButton {{
        background-color: transparent;
        color: #aaaaaa;
        border: none;
        border-radius: 6px;
        padding: 4px;
        font-size: 14px;
        min-width: 24px;
        max-width: 24px;
        min-height: 24px;
        max-height: 24px;
    }}
    
    #minimizeButton:hover {{
        background-color: #3d3d3d;
        color: #ffffff;
    }}
    
    #closeButton:hover {{
        background-color: #e41e3f;
        color: #ffffff;
    }}
    
    /* Insert button with accent color */
    #insertButton {{
        background-color: {colors['base']};
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 12px;
    }}
    
    #insertButton:hover {{
        background-color: {colors['hover']};
    }}
    
    /* Command history panel */
    #historyPanel {{
        background-color: #1f1f1f;
        color: #ffffff;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 2px;
        font-size: 12px;
        selection-background-color: #3d3d3d;
        selection-color: #ffffff;
        margin-top: 4px;
    }}
    
    #historyPanel::item {{
        padding: 6px 8px;
        border-radius: 4px;
    }}
    
    #historyPanel::item:selected {{
        background-color: #3d3d3d;
    }}
    
    #historyPanel::item:hover:!selected {{
        background-color: #353535;
    }}
    
    /* Shortcuts and hint labels */
    #shortcutsLabel {{
        color: #777;
        font-size: 11px;
        padding: 4px 0;
    }}
    
    /* Size grip for resizing */
    #sizeGrip {{
        width: 16px;
        height: 16px;
        margin: 4px;
    }}
    
    #sizeGripContainer {{
        background-color: #2d2d2d;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
    }}
    
    /* Context menu styling */
    QMenu {{
        background-color: #2d2d2d;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 4px;
    }}
    
    QMenu::item {{
        padding: 6px 28px 6px 12px;
        color: #ffffff;
        border-radius: 4px;
    }}
    
    QMenu::item:selected {{
        background-color: #3d3d3d;
    }}
    
    /* Command hint styling */
    #commandHint {{
        color: {colors['base']};
        background-color: transparent;
        padding: 2px 4px;
        border-radius: 4px;
        font-size: 11px;
        border: 1px solid {colors['base']};
        margin: 2px;
    }}
    """

def get_light_theme(accent_color="#0d6efd"):
    """Generate light theme styles with custom accent color"""
    colors = get_color_variants(accent_color)
    
    return f"""
    /* FLOW-inspired Main Window */
    QMainWindow {{
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 12px;
    }}
    
    /* Title Bar with cleaner styling */
    #titleBar {{
        background-color: #ffffff;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        padding: 6px 8px;
        border-bottom: 1px solid #e9ecef;
    }}
    
    #titleLabel {{
        color: #212529;
        font-size: 13px;
        font-weight: normal;
    }}
    
    /* App indicator dot */
    #appIndicator {{
        border-radius: 4px;
        min-width: 8px;
        min-height: 8px;
        max-width: 8px;
        max-height: 8px;
        background-color: {colors['base']};
    }}
    
    /* Content area */
    #content {{
        background-color: #ffffff;
        padding: 12px;
    }}
    
    /* FLOW-style search input */
    #inputBox {{
        background-color: #f5f5f5;
        color: #212529;
        border: none;
        border-radius: 10px;
        padding: 8px 12px 8px 36px;
        font-size: 13px;
        selection-background-color: {colors['base']};
        selection-color: #ffffff;
    }}
    
    #inputBox:focus {{
        background-color: #f0f0f0;
        border: 1px solid {colors['base']};
    }}
    
    /* Search icon styling */
    #searchIcon {{
        color: #999;
        padding-left: 12px;
    }}
    
    /* Translation results area */
    #previewBox {{
        background-color: #f5f5f5;
        color: #212529;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-size: 13px;
        selection-background-color: {colors['base']};
        selection-color: #ffffff;
        margin-top: 8px;
    }}
    
    /* Modern ComboBox styling */
    QComboBox {{
        border: none;
        border-radius: 6px;
        padding: 6px 8px;
        background-color: transparent;
        color: {colors['base']};
        min-width: 60px;
        max-width: 120px;
        font-size: 12px;
    }}
    
    QComboBox:hover {{
        background-color: #e9ecef;
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 16px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid {colors['base']};
        margin-right: 5px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: #ffffff;
        color: #212529;
        selection-background-color: #e9ecef;
        selection-color: #212529;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 4px;
    }}
    
    /* Buttons with FLOW-style */
    #langButton {{
        background-color: transparent;
        color: {colors['base']};
        border: none;
        border-radius: 6px;
        padding: 6px 8px;
        font-size: 12px;
        text-align: center;
    }}
    
    #langButton:hover {{
        background-color: #e9ecef;
    }}
    
    QPushButton {{
        background-color: transparent;
        color: #495057;
        border: none;
        border-radius: 6px;
        padding: 6px 8px;
        font-size: 12px;
    }}
    
    QPushButton:hover {{
        background-color: #e9ecef;
    }}
    
    /* Modern control buttons */
    #settingsButton, #themeButton, #compactModeButton {{
        background-color: transparent;
        color: #6c757d;
        border: none;
        border-radius: 6px;
        padding: 4px;
        font-size: 14px;
        min-width: 24px;
        max-width: 24px;
        min-height: 24px;
        max-height: 24px;
    }}
    
    #settingsButton:hover, #themeButton:hover, #compactModeButton:hover {{
        background-color: #e9ecef;
        color: #212529;
    }}
    
    /* Close, minimize buttons */
    #minimizeButton, #closeButton {{
        background-color: transparent;
        color: #6c757d;
        border: none;
        border-radius: 6px;
        padding: 4px;
        font-size: 14px;
        min-width: 24px;
        max-width: 24px;
        min-height: 24px;
        max-height: 24px;
    }}
    
    #minimizeButton:hover {{
        background-color: #e9ecef;
        color: #212529;
    }}
    
    #closeButton:hover {{
        background-color: #e41e3f;
        color: #ffffff;
    }}
    
    /* Insert button with accent color */
    #insertButton {{
        background-color: {colors['base']};
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 12px;
    }}
    
    #insertButton:hover {{
        background-color: {colors['hover']};
    }}
    
    /* Command history panel */
    #historyPanel {{
        background-color: #f5f5f5;
        color: #212529;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 2px;
        font-size: 12px;
        selection-background-color: #e9ecef;
        selection-color: #212529;
        margin-top: 4px;
    }}
    
    #historyPanel::item {{
        padding: 6px 8px;
        border-radius: 4px;
    }}
    
    #historyPanel::item:selected {{
        background-color: #e9ecef;
    }}
    
    #historyPanel::item:hover:!selected {{
        background-color: #f0f0f0;
    }}
    
    /* Shortcuts and hint labels */
    #shortcutsLabel {{
        color: #6c757d;
        font-size: 11px;
        padding: 4px 0;
    }}
    
    /* Size grip for resizing */
    #sizeGrip {{
        width: 16px;
        height: 16px;
        margin: 4px;
    }}
    
    #sizeGripContainer {{
        background-color: #ffffff;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
    }}
    
    /* Context menu styling */
    QMenu {{
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 4px;
    }}
    
    QMenu::item {{
        padding: 6px 28px 6px 12px;
        color: #212529;
        border-radius: 4px;
    }}
    
    QMenu::item:selected {{
        background-color: #e9ecef;
    }}
    
    /* Command hint styling */
    #commandHint {{
        color: {colors['base']};
        background-color: transparent;
        padding: 2px 4px;
        border-radius: 4px;
        font-size: 11px;
        border: 1px solid {colors['base']};
        margin: 2px;
    }}
    """

def get_compact_dark_theme(accent_color="#4da6ff"):
    """Generate compact dark theme styles with custom accent color"""
    colors = get_color_variants(accent_color)
    
    return f"""
    /* Compact mode container */
    #compactWidget {{
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 10px;
        min-width: 280px;
        max-width: 400px;
    }}
    
    /* Compact title bar */
    #compactTitleBar {{
        background-color: #2d2d2d;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        min-height: 28px;
        padding: 4px 8px;
        border-bottom: 1px solid #333;
    }}
    
    /* Compact title text */
    #compactTitleLabel {{
        color: #aaa;
        font-size: 11px;
        padding-left: 4px;
    }}
    
    /* App indicator dot */
    #compactIndicator {{
        border-radius: 3px;
        min-width: 6px;
        min-height: 6px;
        max-width: 6px;
        max-height: 6px;
        background-color: {colors['base']};
    }}
    
    /* Control buttons */
    #expandButton, #compactCloseButton, #compactThemeButton {{
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 2px;
        font-size: 12px;
        color: #aaa;
        min-width: 20px;
        max-width: 20px;
        min-height: 20px;
        max-height: 20px;
    }}
    
    #expandButton:hover, #compactThemeButton:hover {{
        background: #3d3d3d;
        color: #fff;
    }}
    
    #compactCloseButton:hover {{
        background: #e41e3f;
        color: #fff;
    }}
    
    /* Compact content area */
    #compactContent {{
        background-color: #1a1a1a;
        padding: 8px;
    }}
    
    /* Input with search icon */
    #compactInput {{
        background-color: #2d2d2d;
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 6px 8px 6px 28px;
        font-size: 12px;
        selection-background-color: {colors['base']};
        selection-color: #fff;
    }}
    
    #compactInput:focus {{
        background-color: #333;
        border: 1px solid {colors['base']};
    }}
    
    /* Compact search icon */
    #compactSearchIcon {{
        color: #666;
        padding-left: 10px;
    }}
    
    /* Language quick select buttons */
    #compactLangButton {{
        background-color: transparent;
        color: {colors['base']};
        border: none;
        border-radius: 4px;
        padding: 4px 6px;
        font-size: 11px;
        min-width: 28px;
        max-width: 28px;
    }}
    
    #compactLangButton:hover {{
        background-color: #3d3d3d;
    }}
    
    /* Compact translation preview */
    #compactPreview {{
        background-color: #2d2d2d;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 8px;
        font-size: 12px;
        min-height: 44px;
        max-height: 120px;
        margin-top: 6px;
    }}
    
    /* Compact hints */
    #compactHint {{
        color: #777;
        font-size: 10px;
        padding: 2px 0;
        margin-top: 4px;
    }}
    
    /* Compact size grip */
    #compactSizeGrip {{
        width: 12px;
        height: 12px;
        margin: 2px;
    }}
    """

def get_compact_light_theme(accent_color="#0d6efd"):
    """Generate compact light theme styles with custom accent color"""
    colors = get_color_variants(accent_color)
    
    return f"""
    /* Compact mode container */
    #compactWidget {{
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        min-width: 280px;
        max-width: 400px;
    }}
    
    /* Compact title bar */
    #compactTitleBar {{
        background-color: #f8f9fa;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        min-height: 28px;
        padding: 4px 8px;
        border-bottom: 1px solid #e9ecef;
    }}
    
    /* Compact title text */
    #compactTitleLabel {{
        color: #6c757d;
        font-size: 11px;
        padding-left: 4px;
    }}
    
    /* App indicator dot */
    #compactIndicator {{
        border-radius: 3px;
        min-width: 6px;
        min-height: 6px;
        max-width: 6px;
        max-height: 6px;
        background-color: {colors['base']};
    }}
    
    /* Control buttons */
    #expandButton, #compactCloseButton, #compactThemeButton {{
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 2px;
        font-size: 12px;
        color: #6c757d;
        min-width: 20px;
        max-width: 20px;
        min-height: 20px;
        max-height: 20px;
    }}
    
    #expandButton:hover, #compactThemeButton:hover {{
        background: #e9ecef;
        color: #212529;
    }}
    
    #compactCloseButton:hover {{
        background: #e41e3f;
        color: #fff;
    }}
    
    /* Compact content area */
    #compactContent {{
        background-color: #ffffff;
        padding: 8px;
    }}
    
    /* Input with search icon */
    #compactInput {{
        background-color: #f5f5f5;
        color: #212529;
        border: none;
        border-radius: 8px;
        padding: 6px 8px 6px 28px;
        font-size: 12px;
        selection-background-color: {colors['base']};
        selection-color: #fff;
    }}
    
    #compactInput:focus {{
        background-color: #f0f0f0;
        border: 1px solid {colors['base']};
    }}
    
    /* Compact search icon */
    #compactSearchIcon {{
        color: #999;
        padding-left: 10px;
    }}
    
    /* Language quick select buttons */
    #compactLangButton {{
        background-color: transparent;
        color: {colors['base']};
        border: none;
        border-radius: 4px;
        padding: 4px 6px;
        font-size: 11px;
        min-width: 28px;
        max-width: 28px;
    }}
    
    #compactLangButton:hover {{
        background-color: #e9ecef;
    }}
    
    /* Compact translation preview */
    #compactPreview {{
        background-color: #f5f5f5;
        color: #212529;
        border: none;
        border-radius: 8px;
        padding: 8px;
        font-size: 12px;
        min-height: 44px;
        max-height: 120px;
        margin-top: 6px;
    }}
    
    /* Compact hints */
    #compactHint {{
        color: #6c757d;
        font-size: 10px;
        padding: 2px 0;
        margin-top: 4px;
    }}
    
    /* Compact size grip */
    #compactSizeGrip {{
        width: 12px;
        height: 12px;
        margin: 2px;
    }}
    """

# Default accent colors 
DEFAULT_ACCENT_DARK = "#4da6ff"  # Blue for dark mode
DEFAULT_ACCENT_LIGHT = "#0d6efd"  # Blue for light mode

# Generate default themes
DARK_THEME = get_dark_theme(DEFAULT_ACCENT_DARK)
LIGHT_THEME = get_light_theme(DEFAULT_ACCENT_LIGHT)
COMPACT_DARK_STYLES = get_compact_dark_theme(DEFAULT_ACCENT_DARK)
COMPACT_LIGHT_STYLES = get_compact_light_theme(DEFAULT_ACCENT_LIGHT)

# Available accent colors with friendly names
ACCENT_COLORS = {
    "Blue": {"dark": "#4da6ff", "light": "#0d6efd"},
    "Green": {"dark": "#4caf50", "light": "#28a745"},
    "Purple": {"dark": "#9c27b0", "light": "#6f42c1"},
    "Orange": {"dark": "#ff9800", "light": "#fd7e14"},
    "Red": {"dark": "#f44336", "light": "#dc3545"},
    "Teal": {"dark": "#009688", "light": "#20c997"},
    "Pink": {"dark": "#e91e63", "light": "#e83e8c"},
    "Indigo": {"dark": "#3f51b5", "light": "#6610f2"}
}

def apply_accent_color(color_name, dark_mode=True):
    """Apply a specific accent color to the theme"""
    if color_name not in ACCENT_COLORS:
        color_name = "Blue"  # Default fallback
        
    color_hex = ACCENT_COLORS[color_name]["dark" if dark_mode else "light"]
    
    if dark_mode:
        return get_dark_theme(color_hex), get_compact_dark_theme(color_hex)
    else:
        return get_light_theme(color_hex), get_compact_light_theme(color_hex)