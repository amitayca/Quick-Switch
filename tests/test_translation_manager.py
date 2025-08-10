import sys
import os
import types


# ---------------------------------------------------------------------------
# Test stubs for optional dependencies
# ---------------------------------------------------------------------------


class _DummySignal:
    """Minimal stand-in for PyQt6's pyqtSignal."""

    def __init__(self, *args, **kwargs):
        pass

    def emit(self, *args, **kwargs):  # pragma: no cover - behaviour not tested
        pass


qtcore = types.ModuleType("PyQt6.QtCore")
qtcore.QObject = object
qtcore.pyqtSignal = _DummySignal

pyqt6 = types.ModuleType("PyQt6")
pyqt6.QtCore = qtcore

sys.modules.setdefault("PyQt6", pyqt6)
sys.modules.setdefault("PyQt6.QtCore", qtcore)


googletrans = types.ModuleType("googletrans")


class _Translator:
    def translate(self, text, src=None, dest=None):  # pragma: no cover - simple stub
        class _Result:
            def __init__(self, text):
                self.text = text
                self.src = src

        return _Result(text)


googletrans.Translator = _Translator

sys.modules.setdefault("googletrans", googletrans)


# Ensure the src package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.translation_manager import EnhancedTranslationManager


class _DummyKeywordManager:
    def __init__(self):
        self.contexts = {
            "Automotive": {
                "translations": {"car": "auto"}
            }
        }


class _DummyPersonalDictionary:
    def __init__(self):
        self.keyword_manager = _DummyKeywordManager()


def test_context_suggestions_use_translations():
    manager = EnhancedTranslationManager(_DummyPersonalDictionary(), object())

    translated_text = "The auto is fast"
    suggestions = manager.get_context_matches(translated_text, "Automotive")

    assert any(s.suggested_word == "auto" for s in suggestions)

