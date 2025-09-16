import ctypes
import os

def show_error_interface(error: str):
    ctypes.windll.user32.MessageBoxW(0, error, "Error", 0x10)
    os._exit(1)
