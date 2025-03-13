# src/utils/window_automation.py
import win32gui
import win32api
import win32con
import win32process
import ctypes
from ctypes import wintypes
import array

class WindowAutomation:
    """Utility class for window automation and text field detection"""
    
    def __init__(self):
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        
        # Define necessary Windows API structures
        class GUITHREADINFO(ctypes.Structure):
            _fields_ = [
                ('cbSize', wintypes.DWORD),
                ('flags', wintypes.DWORD),
                ('hwndActive', wintypes.HWND),
                ('hwndFocus', wintypes.HWND),
                ('hwndCapture', wintypes.HWND),
                ('hwndMenuOwner', wintypes.HWND),
                ('hwndMoveSize', wintypes.HWND),
                ('hwndCaret', wintypes.HWND),
                ('rcCaret', wintypes.RECT),
            ]
        self.GUITHREADINFO = GUITHREADINFO

    def get_focused_window(self):
        """Get handle and info about currently focused window"""
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return None, None
            
        # Get window class and title
        window_class = win32gui.GetClassName(hwnd)
        window_title = win32gui.GetWindowText(hwnd)
        
        return hwnd, {
            'class': window_class,
            'title': window_title,
            'handle': hwnd
        }

    def get_focused_control(self):
        """Get handle and info about currently focused control"""
        # Get the foreground window's thread
        hwnd = win32gui.GetForegroundWindow()
        thread_id = win32process.GetWindowThreadProcessId(hwnd)[0]
        
        # Initialize GUITHREADINFO structure
        gui_info = self.GUITHREADINFO()
        gui_info.cbSize = ctypes.sizeof(gui_info)
        
        # Get thread info
        if not self.user32.GetGUIThreadInfo(thread_id, ctypes.byref(gui_info)):
            return None, None
            
        focus_hwnd = gui_info.hwndFocus
        if not focus_hwnd:
            return None, None
            
        # Get control class name
        class_name = win32gui.GetClassName(focus_hwnd)
        
        # Determine if control is a text field
        is_text_field = self.is_text_control(focus_hwnd, class_name)
        
        return focus_hwnd, {
            'class': class_name,
            'handle': focus_hwnd,
            'is_text_field': is_text_field
        }

    def is_text_control(self, hwnd, class_name):
        """Determine if a control is a text input field"""
        text_control_classes = {
            'Edit',  # Standard text boxes
            'RichEdit20W',  # Rich text boxes
            'TextBox',  # .NET text boxes
            'Chrome_RenderWidgetHostHWND',  # Chrome text fields
            'MozillaWindowClass'  # Firefox text fields
        }
        
        # Check known text control classes
        if class_name in text_control_classes:
            return True
            
        # Get control styles
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        
        # Check if control has text input styles
        text_styles = (
            win32con.ES_MULTILINE |
            win32con.ES_LEFT |
            win32con.ES_RIGHT |
            win32con.ES_CENTER
        )
        
        return bool(style & text_styles)

    def get_caret_position(self, hwnd):
        """Get the current caret (text cursor) position"""
        gui_info = self.GUITHREADINFO()
        gui_info.cbSize = ctypes.sizeof(gui_info)
        
        thread_id = win32process.GetWindowThreadProcessId(hwnd)[0]
        if not self.user32.GetGUIThreadInfo(thread_id, ctypes.byref(gui_info)):
            return None
            
        return (gui_info.rcCaret.left, gui_info.rcCaret.top)

    def simulate_text_input(self, hwnd, text):
        """Simulate keyboard input to insert text"""
        for char in text:
            win32api.SendMessage(hwnd, win32con.WM_CHAR, ord(char), 0)