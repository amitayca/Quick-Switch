def get_dialog_theme_styles(dark_mode: bool) -> str:
    """Get consistent theme styles for all dialogs"""
    return """
        QDialog {
            background-color: """ + (dark_mode and "#1a1a1a" or "#ffffff") + """;
            color: """ + (dark_mode and "#ffffff" or "#212529") + """;
            padding: 8px;
        }
        QGroupBox {
            border: 1px solid """ + (dark_mode and "#444" or "#dee2e6") + """;
            color: """ + (dark_mode and "#ffffff" or "#212529") + """;
            margin-top: 16px;
            font-weight: bold;
            padding-top: 12px;
        }
        QLineEdit, QComboBox, QListWidget {
            background-color: """ + (dark_mode and "#2d2d2d" or "#ffffff") + """;
            color: """ + (dark_mode and "#ffffff" or "#212529") + """;
            border: 1px solid """ + (dark_mode and "#444" or "#dee2e6") + """;
            border-radius: 4px;
            padding: 4px;
        }
        QPushButton {
            background-color: """ + (dark_mode and "#2d2d2d" or "#f8f9fa") + """;
            color: """ + (dark_mode and "#ffffff" or "#212529") + """;
            border: 1px solid """ + (dark_mode and "#444" or "#dee2e6") + """;
            border-radius: 4px;
            padding: 6px 12px;
            min-width: 100px;
        }
        QPushButton:hover {
            background-color: """ + (dark_mode and "#404040" or "#e9ecef") + """;
        }
        QLabel {
            color: """ + (dark_mode and "#ffffff" or "#212529") + """;
        }
    """