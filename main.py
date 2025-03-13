import os
import sys
from PyQt6.QtWidgets import QApplication
from src.components.translation_window import TranslationWindow

def main():
    os.environ["QT_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = TranslationWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()