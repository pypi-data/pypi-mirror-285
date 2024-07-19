import ctypes
import ctypes.wintypes
from ctypes import *
import os

dll_path = os.path.join(os.path.dirname(__file__), 'PyGUIBuilder.dll')

g = ctypes.CDLL(dll_path)

HWND = c_int

class Window_t(Structure):
    _fields_ = [("hwnd", c_void_p),
                ("hInstance", c_void_p),
                ("width", c_int),
                ("height", c_int)]

g.createWindow_dll.argtypes = [c_char_p, c_char_p, c_int, c_int]
g.createWindow_dll.restype = Window_t

g.createLabel_dll.argtypes = [Window_t, c_char_p, c_int, c_int]
g.createLabel_dll.restype = c_void_p

g.createButton_dll.argtypes = [Window_t, c_char_p, CFUNCTYPE(None), c_int, c_int]
g.createButton_dll.restype = c_void_p

g.createEntry_dll.argtypes = [Window_t, c_char_p, c_int, c_int]
g.createEntry_dll.restype = c_void_p

g.clearText_dll.argtypes = [HWND]
g.clearText_dll.restype = None

g.getText_dll.argtypes = [HWND]
g.getText_dll.restype = c_char_p

g.setText_dll.argtypes = [HWND, c_char_p]
g.setText_dll.restype = None

g.showMessageBox_dll.argtypes = [c_char_p, c_char_p, c_char_p]
g.showMessageBox_dll.restype = c_int

g.createComboBox_dll.argtypes = [Window_t, POINTER(c_char_p), c_int, c_int, c_int]
g.createComboBox_dll.restype = c_void_p

g.getComboBoxSelection_dll.argtypes = [c_void_p]
g.getComboBoxSelection_dll.restype = c_char_p

g.createCheckbox_dll.argtypes = [Window_t, c_char_p, c_int, c_int]
g.createCheckbox_dll.restype = c_void_p

g.getCheckbox_dll.argtypes = [HWND]
g.getCheckbox_dll.restype = c_void_p

ButtonCallback = CFUNCTYPE(None)

_global_callbacks = []

IDOK = 1
IDCANCEL = 2
IDABORT = 3
IDRETRY = 4
IDIGNORE = 5
IDYES = 6
IDNO = 7

def createWindow(title, icon, width, height):
    return g.createWindow_dll(title.encode('utf-8'), icon.encode('utf-8'), width, height)

def createLabel(window, text, row, column):
    return g.createLabel_dll(window, text.encode('utf-8'), row, column)

def createButton(window, text, callback, row, column):
    callback_c = ButtonCallback(callback)
    _global_callbacks.append(callback_c)
    return g.createButton_dll(window, text.encode('utf-8'), callback_c, row, column)

def createEntry(window, text, row, column):
    return g.createEntry_dll(window, text.encode('utf-8'), row, column)

def clearText(hwnd):
    return g.clearText_dll(hwnd)

def getText(hwnd):
    text = g.getText_dll(hwnd)
    return text.decode('utf-8')

def setText(hwnd, text):
    g.setText_dll(hwnd, text.encode('utf-8'))

def destroyElement(hwnd):
    ctypes.windll.user32.DestroyWindow(hwnd)

def showMessageBox(type, title, message):
    result = g.showMessageBox_dll(type.encode('utf-8'), title.encode('utf-8'), message.encode('utf-8'))
    
    if result == IDOK:
        return "OK"
    elif result == IDCANCEL:
        return "Cancel"
    elif result == IDYES:
        return "Yes"
    elif result == IDNO:
        return "No"
    elif result == IDRETRY:
        return "Retry"
    elif result == IDABORT:
        return "Abort"
    elif result == IDIGNORE:
        return "Ignore"
    else:
        return "Unknown"

def createComboBox(window, options, row, column):
    options_c = (c_char_p * len(options))(*[opt.encode('utf-8') for opt in options])
    return g.createComboBox_dll(window, options_c, len(options), row, column)

def getComboBoxSelection(comboBox):
    return g.getComboBoxSelection_dll(comboBox).decode('utf-8')

def createCheckbox(window, text, row, column):
    return g.createCheckbox_dll(window, text.encode('utf-8'), row, column)

def getCheckbox(hwnd):
    return g.getCheckbox_dll(hwnd)

def run():
    msg = ctypes.wintypes.MSG()
    while True:
        ret = ctypes.windll.user32.GetMessageW(ctypes.pointer(msg), None, 0, 0)
        if ret == 0:
            break
        ctypes.windll.user32.TranslateMessage(ctypes.pointer(msg))
        ctypes.windll.user32.DispatchMessageW(ctypes.pointer(msg))
