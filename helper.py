# This file provides a long_running decorator to indicate that a function needs a long amount of time to complete and
# the computer should not enter standby. This file currently only works on Windows and is a no-op on other platforms.

import ctypes
import platform
import winreg

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


def _set_thread_execution(state):
    ctypes.windll.kernel32.SetThreadExecutionState(state)


def prevent_standby():
    """Prevents the computer from entering standby"""
    if platform.system() == "Windows":
        _set_thread_execution(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)


def allow_standby():
    """Allows the computer to enter standby"""
    if platform.system() == "Windows":
        _set_thread_execution(ES_CONTINUOUS)


def long_running(func):
    """Decorator to indicate that a function needs a long amount of time to complete and the computer should not enter"""

    def inner(*args, **kwargs):
        prevent_standby()
        result = func(*args, **kwargs)
        allow_standby()
        return result

    return inner


def check_aumid(aumid):
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            f"SOFTWARE\\Classes\\AppUserModelId\\{aumid}",
        ) as key:
            print("AUMID found")
            return True
    except FileNotFoundError:
        print("AUMID not found")
        return False
