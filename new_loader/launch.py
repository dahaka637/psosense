import os
import time
import threading
import psutil
import win32file
import pywintypes
from pyinjector import inject as pyinjector_inject
from error_notify import show_error_interface  # Certifique-se de importar corretamente


PIPE_NAME = r'\\.\\pipe\\crasher'
TARGET_PROCESS = "ProSoccerOnline-Win64-Shipping.exe"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DLL_PATH = os.path.join(SCRIPT_DIR, "crasher.dll")


# Globals
global_token = None

def start_launcher(token):
    global global_token
    global_token = token

    print(f"[INFO] Received token: {global_token}")
    print("[INFO] Starting process monitor...")

    threading.Thread(target=monitor_process, daemon=True).start()


def monitor_process():
    print(f"[THREAD] Monitoring '{TARGET_PROCESS}'...")
    while True:
        if is_process_running(TARGET_PROCESS):
            print("[INFO] Game process found. Waiting 1 second...")
            time.sleep(1)

            if inject_dll():
                print("[INFO] DLL injected. Waiting 2 seconds for pipe...")
                time.sleep(2)

                # Inicia thread de verificação do pipe
                threading.Thread(target=pipe_verification_thread, daemon=True).start()
            else:
                print("[ERROR] Failed to inject DLL.")
            break
        time.sleep(1)


def pipe_verification_thread():
    start_time = time.time()

    for attempt in range(3):
        print(f"[PIPE] Attempt {attempt + 1}/3: trying to send token...")

        try:
            handle = win32file.CreateFile(
                PIPE_NAME,
                win32file.GENERIC_WRITE | win32file.GENERIC_READ,
                0, None,
                win32file.OPEN_EXISTING,
                0, None
            )

            win32file.WriteFile(handle, global_token.encode("utf-16-le"))
            print(f"[PIPE] Token sent: {global_token}")

            _, response = win32file.ReadFile(handle, 1024)
            reply = ''.join(c for c in response.decode("utf-16-le") if c.isprintable()).strip().lower()
            win32file.CloseHandle(handle)

            print(f"[PIPE] DLL response: {reply}")
            if reply == "ok":
                print("[INFO] DLL confirmed token. Exiting immediately.")
                os._exit(0)
            else:
                print("[PIPE] DLL responded, but not 'ok'.")

        except pywintypes.error as e:
            print(f"[PIPE] Communication error: {e}")
        except Exception as e:
            print(f"[PIPE] Unexpected error: {e}")

        if time.time() - start_time > 10:
            break

        time.sleep(1)

    # Após 10 segundos ou 3 tentativas sem sucesso
    show_error_interface("The DLL did not respond within the expected time.\n\n"
                         "Please make sure the DLL is loaded correctly and try again.")


def is_process_running(process_name):
    for proc in psutil.process_iter(attrs=["name"]):
        if proc.info["name"].lower() == process_name.lower():
            return True
    return False


def get_pid(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == process_name.lower():
            return proc.info['pid']
    return None



def inject_dll():
    pid = get_pid(TARGET_PROCESS)
    if not pid:
        show_error_interface("Target process not found.")
        return False  # Em caso de fallback, caso não feche

    if not os.path.exists(DLL_PATH):
        show_error_interface(f"DLL file not found:\n{DLL_PATH}")
        return False

    try:
        pyinjector_inject(pid, DLL_PATH)
        print("[INFO] DLL injected successfully.")
        return True
    except Exception as e:
        show_error_interface(f"DLL injection failed:\n{str(e)}")
        return False


def try_send_token(token):
    print("[PIPE] Connecting to pipe...")
    try:
        handle = win32file.CreateFile(
            PIPE_NAME,
            win32file.GENERIC_WRITE | win32file.GENERIC_READ,
            0, None,
            win32file.OPEN_EXISTING,
            0, None
        )

        win32file.WriteFile(handle, token.encode("utf-16-le"))
        print(f"[PIPE] Token sent: {token}")

        _, response = win32file.ReadFile(handle, 1024)
        reply = response.decode("utf-16-le").strip().lower()
        win32file.CloseHandle(handle)

        print(f"[PIPE] DLL response: {reply}")
        return reply == "ok"

    except pywintypes.error as e:
        print(f"[PIPE] Communication error: {e}")
        return False
    except Exception as e:
        print(f"[PIPE] Unexpected error: {e}")
        return False
