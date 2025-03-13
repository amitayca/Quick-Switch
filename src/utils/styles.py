# Location: Quick Switch/src/utils/styles.py

COMPACT_DARK_STYLES = """
    #compactPreview {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 13px;
        min-height: 40px;
    }
    
    #compactPreview:focus {
        border-color: #0d6efd;
        background-color: #333;
    }
    
    #compactSettingsButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 14px;
        color: #888;
        min-width: 24px;
        min-height: 20px;
    }
    
    #compactSettingsButton:hover {
        background: #444;
        color: #fff;
    }
    
    #compactWidget {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        min-width: 250px;
        max-width: 400px;
    }
    
    #compactTitleBar {
        background-color: #2d2d2d;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        min-height: 24px;
        padding: 2px;
    }
    
    #compactTitleLabel {
        color: #888;
        font-size: 12px;
        padding-left: 4px;
    }
    
    #expandButton, #compactCloseButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 14px;
        color: #888;
        min-width: 24px;
        min-height: 20px;
    }
    
    #expandButton:hover {
        background: #444;
        color: #fff;
    }
    
    #compactCloseButton:hover {
        background: #ff4d4d;
        color: #fff;
    }
    
    #compactContent {
        background-color: #1a1a1a;
        padding: 2px;
    }
    
    #compactInput {
        background-color: #2d2d2d;
        color: #fff;
        border: 1px solid #444;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 13px;
        selection-background-color: #0d6efd;
        selection-color: #fff;
    }
    
    #compactInput:focus {
        border-color: #0d6efd;
        background-color: #333;
    }
    
    #compactSizeGrip {
        width: 12px;
        height: 12px;
        margin: 2px;
    }
"""

COMPACT_LIGHT_STYLES = """
    
    #compactWidget {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        min-width: 250px;
        max-width: 400px;
    }
    
    #compactTitleBar {
        background-color: #f8f9fa;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        min-height: 24px;
        padding: 2px;
    }
    
    #compactContent {
        background-color: #ffffff;
        padding: 2px;
    }
    
    #compactInput {
        background-color: #ffffff;
        color: #212529;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 13px;
    }
    
    #compactPreview {
        background-color: #ffffff;
        color: #212529;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 13px;
    }
    
     #compactSettingsButton, #expandButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 14px;
        color: #495057;  /* Darker gray for better visibility */
        min-width: 24px;
        min-height: 20px;
    }
    
    #compactCloseButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 14px;
        color: #495057;
        min-width: 24px;
        min-height: 20px;
    }
    
    #compactSettingsButton:hover, #expandButton:hover {
        background: #e9ecef;
        color: #212529;
    }
    
    #compactCloseButton:hover {
        background: #ff4d4d;
        color: #ffffff;
    }
    }
    
    #compactInput:focus, #compactPreview:focus {
        border-color: #0d6efd;
        background-color: #f8f9fa;
    }
"""

DARK_THEME = """
    
     #compactModeButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 5px 10px;
        font-size: 14px;
        color: #ffffff;
    }
    
    #compactModeButton:hover {
        background: #444;
    }

    QMainWindow {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 10px;
    }
    
    #titleBar {
        background-color: #2d2d2d;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        border-bottom: 1px solid #333;
    }
    
    #titleLabel {
        color: #ffffff;
        font-size: 14px;
        font-weight: bold;
    }
    
    QComboBox {
        border: 1px solid #444;
        border-radius: 4px;
        padding: 4px;
        background: #2d2d2d;
        min-width: 80px;
        max-width: 150px;
        color: #ffffff;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid #ffffff;
        margin-right: 5px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        color: #ffffff;
        selection-background-color: #404040;
        selection-color: #ffffff;
        border: 1px solid #444;
    }
    
    #settingsButton, #themeButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 5px 10px;
        font-size: 14px;
        color: #ffffff;
    }
    
    #settingsButton:hover, #themeButton:hover {
        background: #444;
    }
    
    #minimizeButton, #closeButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 5px 10px;
        font-size: 14px;
        color: #ffffff;
    }
    
    #minimizeButton:hover {
        background: #444;
    }
    
    #closeButton:hover {
        background: #ff4d4d;
        color: white;
    }
    
    #content {
        background-color: #2d2d2d;
    }
    
    #inputBox, #previewBox {
        border: 1px solid #444;
        border-radius: 6px;
        padding: 10px;
        font-size: 14px;
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    #inputBox:focus, #previewBox:focus {
        border: 2px solid #0d6efd;
        background-color: #262626;
    }
    
    #shortcutsLabel {
        color: #888;
        font-size: 12px;
    }
    
    #sizeGrip {
        width: 16px;
        height: 16px;
        margin: 5px;
    }
    
    #sizeGripContainer {
        background-color: #2d2d2d;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
    }
    
    QMenu {
        background-color: #2d2d2d;
        border: 1px solid #444;
    }
    
    QMenu::item {
        padding: 5px 20px;
        color: #ffffff;
    }
    
    QMenu::item:selected {
        background-color: #444;
    }
"""

LIGHT_THEME = """
    
    #compactModeButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 5px 10px;
        font-size: 14px;
        color: #495057;
    }
    
    #compactModeButton:hover {
        background: #e9ecef;
    }
    
    QMainWindow {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
    }
    
    #titleBar {
        background-color: #ffffff;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        border-bottom: 1px solid #dee2e6;
    }
    
    #titleLabel {
        color: #495057;
        font-size: 14px;
        font-weight: bold;
    }
    
    QComboBox {
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 4px;
        background: #ffffff;
        min-width: 80px;
        max-width: 150px;
        color: #212529;
    }
    
    QComboBox:!editable, QComboBox::drop-down:editable {
        background: #ffffff;
    }
    
    QComboBox:!editable:on, QComboBox::drop-down:editable:on {
        background: #ffffff;
    }
    
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #212529;
        selection-background-color: #e9ecef;
        selection-color: #212529;
        border: 1px solid #ced4da;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid #495057;
        margin-right: 5px;
    }
    
    #settingsButton, #themeButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 5px 10px;
        font-size: 14px;
        color: #495057;
    }
    
    #settingsButton:hover, #themeButton:hover {
        background: #e9ecef;
    }
    
    #minimizeButton, #closeButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 5px 10px;
        font-size: 14px;
        color: #495057;
    }
    
    #minimizeButton:hover {
        background: #e9ecef;
    }
    
    #closeButton:hover {
        background: #ff4d4d;
        color: white;
    }
    
    #content {
        background-color: #ffffff;
    }
    
    #inputBox, #previewBox {
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 10px;
        font-size: 14px;
        background-color: #ffffff;
        color: #212529;
    }
    
    #inputBox:focus, #previewBox:focus {
        border: 2px solid #0d6efd;
        background-color: #f8f9fa;
    }
    
    #shortcutsLabel {
        color: #6c757d;
        font-size: 12px;
    }
    
    #sizeGrip {
        width: 16px;
        height: 16px;
        margin: 5px;
    }
    
    #sizeGripContainer {
        background-color: #ffffff;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
    }
    
    QMenu {
        background-color: white;
        border: 1px solid #dee2e6;
    }
    
    QMenu::item {
        padding: 5px 20px;
        color: #212529;
    }
    
    QMenu::item:selected {
        background-color: #e9ecef;
    }
"""