from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QRadioButton, QButtonGroup, QColorDialog)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap, QPainter, QIcon

from ..utils.styles import ACCENT_COLORS

class ColorSwatchButton(QPushButton):
    """Button showing a color swatch with a border when selected"""
    
    def __init__(self, color, color_name, parent=None):
        super().__init__(parent)
        self.color_hex = color
        self.color_name = color_name
        self.setFixedSize(32, 32)
        self.setCheckable(True)
        self.setToolTip(color_name)
        self.update_swatch()
        
    def update_swatch(self):
        """Update the button appearance with the current color"""
        pixmap = QPixmap(30, 30)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw color circle
        painter.setBrush(QColor(self.color_hex))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(1, 1, 28, 28)
        
        # Draw border if checked
        if self.isChecked():
            painter.setPen(QColor("#ffffff" if self.parent().dark_mode else "#000000"))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(1, 1, 28, 28)
        
        painter.end()
        
        # Fixed: Convert QPixmap to QIcon
        icon = QIcon(pixmap)
        self.setIcon(icon)
        self.setIconSize(pixmap.size())
        self.setText("")  # No text, just the icon


class AccentColorDialog(QDialog):
    """Dialog for selecting the app's accent color"""
    
    colorChanged = pyqtSignal(str)  # Emits the selected color name
    
    def __init__(self, parent=None, current_color="Blue"):
        super().__init__(parent)
        self.settings = parent.settings if parent else QSettings()
        self.dark_mode = getattr(parent, 'dark_mode', False)
        self.current_color = current_color
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Accent Color")
        self.setFixedWidth(360)
        
        layout = QVBoxLayout(self)
        
        # Header
        layout.addWidget(QLabel("Select accent color:"))
        
        # Color grid
        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(8)
        colors_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.color_group = QButtonGroup(self)
        self.color_group.setExclusive(True)
        
        # Add color swatches for each predefined color
        for i, (name, colors) in enumerate(ACCENT_COLORS.items()):
            color_hex = colors["dark" if self.dark_mode else "light"]
            swatch = ColorSwatchButton(color_hex, name, self)
            if name == self.current_color:
                swatch.setChecked(True)
            
            self.color_group.addButton(swatch, i)
            colors_layout.addWidget(swatch)
        
        layout.addLayout(colors_layout)
        
        # Custom color button
        custom_layout = QHBoxLayout()
        custom_layout.addStretch()
        
        custom_btn = QPushButton("Custom Color...")
        custom_btn.clicked.connect(self.select_custom_color)
        custom_layout.addWidget(custom_btn)
        
        layout.addLayout(custom_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_color)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addSpacing(10)
        layout.addLayout(button_layout)
        
    def select_custom_color(self):
        """Open color picker for custom color selection"""
        # This is a placeholder - custom colors would need more implementation
        # to properly integrate with the theme system
        color_dialog = QColorDialog(self)
        color_dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, False)
        
        if color_dialog.exec() == QDialog.DialogCode.Accepted:
            # Custom color handling would go here
            # For simplicity, this demo just uses predefined colors
            pass
    
    def apply_color(self):
        """Apply selected color and close dialog"""
        selected_button = self.color_group.checkedButton()
        if selected_button:
            self.colorChanged.emit(selected_button.color_name)
            self.accept()