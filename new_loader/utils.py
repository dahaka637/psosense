# utils.py
import platform
import hashlib

def get_hwid():
    info = platform.uname()
    raw = f"{info.system}-{info.node}-{info.machine}"
    return hashlib.sha256(raw.encode()).hexdigest()
