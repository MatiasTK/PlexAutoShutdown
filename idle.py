""" This module contains functions to prevent the OS from going to sleep and to get the last input event. """
from ctypes import Structure, windll, c_uint, sizeof, byref


class LASTINPUTINFO(Structure):
    """Struct for the last input event."""

    _fields_ = [
        ("cbSize", c_uint),
        ("dwTime", c_uint),
    ]


def get_idle_duration():
    """Returns the number of seconds since the last input event."""
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0


class WindowsInhibitor:
    """Prevent OS sleep/hibernate in windows; code from:
    https://github.com/h3llrais3r/Deluge-PreventSuspendPlus/blob/master/preventsuspendplus/core.py
    API documentation:
    https://msdn.microsoft.com/en-us/library/windows/desktop/aa373208(v=vs.85).aspx"""

    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    def __init__(self):
        pass

    def inhibit(self):
        """Disable Windows sleep/hibernate"""
        print("Preventing Windows from going to sleep")
        windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS | WindowsInhibitor.ES_SYSTEM_REQUIRED
        )

    def uninhibit(self):
        """Enable Windows sleep/hibernate"""
        print("Allowing Windows to go to sleep")
        windll.kernel32.SetThreadExecutionState(WindowsInhibitor.ES_CONTINUOUS)
