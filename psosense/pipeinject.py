# pipeinject.py
import os
import threading
import pywintypes
import win32file
import win32pipe
import psutil
import pyinjector


PIPE_NAME = r'\\.\pipe\psosense'
DLL_PATH = os.path.join(os.path.dirname(__file__), "PSOSENSE.dll")
PROCESS_NAME = "ProSoccerOnline-Win64-Shipping.exe"

def _send_command(command, callback=None):
    def thread_func():
        try:
            handle = win32file.CreateFile(
                PIPE_NAME,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None,
                win32file.OPEN_EXISTING,
                0, None
            )
            win32file.WriteFile(handle, command.encode())
            _, response = win32file.ReadFile(handle, 1024)
            response_text = response.decode()

            if callback:
                callback(response_text, True)
            handle.close()

        except pywintypes.error as e:
            if callback:
                callback(f"Erro: {e}", False)

    threading.Thread(target=thread_func, daemon=True).start()

# === Funções pré-definidas para comandos fixos ===
def force_swap(callback=None):
    _send_command("force_swap", callback)

def spawn_ball(callback=None):
    _send_command("spawn_ball", callback)

def reset_match(callback=None):
    _send_command("reset_match", callback)

def toggle_keeper(callback=None):
    _send_command("toggle_keeper", callback)

def enable_antikick(callback=None):
    _send_command("enable_antikick", callback)

def disable_antikick(callback=None):
    _send_command("disable_antikick", callback)

def enable_touchslow(callback=None):
    _send_command("enable_touchslow", callback)

def disable_touchslow(callback=None):
    _send_command("disable_touchslow", callback)

def enable_watermark(callback=None):
    _send_command("enable_watermark", callback)

def disable_watermark(callback=None):
    _send_command("disable_watermark", callback)

    
def custom_command(comando, callback=None):
    _send_command(comando, callback)




# === Injeção da DLL ===

try:
    from pyinjector import inject as pyinjector_inject
except ImportError:
    pyinjector_inject = None

def _get_pid_by_name(name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == name:
            return proc.info['pid']
    return None

def inject_psosense_dll(callback=None):
    def thread_func():
        if pyinjector_inject is None:
            if callback:
                callback("Erro: pyinjector não está instalado.", False)
            return

        # Verifica se o pipe já está disponível
        try:
            handle = win32file.CreateFile(
                PIPE_NAME,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None,
                win32file.OPEN_EXISTING,
                0, None
            )
            win32file.CloseHandle(handle)
            if callback:
                callback("DLL já injetada (pipe ativo).", True)
            return
        except pywintypes.error:
            pass  # Pipe ainda não existe, continuar com injeção

        pid = _get_pid_by_name(PROCESS_NAME)
        if pid is None:
            if callback:
                callback("Erro: processo não encontrado.", False)
            return

        try:
            pyinjector_inject(pid, DLL_PATH)
            if callback:
                callback("DLL injetada com sucesso!", True)
        except Exception as e:
            if callback:
                callback(f"Erro na injeção: {e}", False)

    threading.Thread(target=thread_func, daemon=True).start()

