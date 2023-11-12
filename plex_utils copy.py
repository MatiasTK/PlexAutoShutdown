""" This file contains all the functions related to the plex monitor and shutdown """
from __future__ import annotations

import os
from time import sleep
from typing import TYPE_CHECKING

from win32api import GetLastInputInfo, GetTickCount
from win32com.client import GetObject

if TYPE_CHECKING:
    from app import App

# TODO: Ver si puedo hacer que esta variable sea local, dificil ya que la uso en app.py
shutdown_enabled = False


def check_if_are_active_sessions(app: App):
    """Returns true if there is any plex active session"""
    if app.get_plex_instance() is None:
        app.show_error(
            app, "Cannot check if there are active sessions, Plex connection error"
        )
        return False
    return len(app.get_plex_instance().sessions()) > 0


def check_if_transcoder_running(app: App):
    """Returns true if plex is running and transcoder not"""
    if app.get_plex_instance() is None:
        app.show_error(
            app, "Cannot check if there are active sessions, Plex connection error"
        )
        return False
    plex_running = False
    transcoder_running = False

    wmi = GetObject("winmgmts:")
    processes = wmi.InstancesOf("Win32_Process")

    for process in processes:
        if process.Properties_("Name").Value == "Plex Media Server.exe":
            plex_running = True
        if process.Properties_("Name").Value == "Plex Transcoder.exe":
            transcoder_running = True

    return plex_running and not transcoder_running


def minutes_to_seconds(minutes):
    """Converts minutes to seconds"""
    return minutes * 60


def minutes_to_milliseconds(minutes):
    """Converts minutes to milliseconds"""
    return minutes * 60000


def cancel_shutdown():
    """Cancels the shutdown"""
    global shutdown_enabled
    print("Auto-shutdown aborted")
    os.system("shutdown -a")
    shutdown_enabled = False


def activate_shutdown(time_in_minutes):
    """Activates the shutdown"""
    global shutdown_enabled
    print(
        "Auto-shutdown initiated, computer will shutdown in "
        + str(time_in_minutes)
        + " seconds"
    )
    os.system("shutdown -s -t " + str(minutes_to_seconds(time_in_minutes)))
    shutdown_enabled = True


def get_idle_time():
    """Returns computer idle time in seconds"""
    idle_time = (GetTickCount() - GetLastInputInfo()) / 1000.0
    return idle_time


def monitor_plex_and_shutdown(app: App):
    """Checks if there is any active plex session and if the computer is in idle mode, if both are true it will shutdown the computer after the given delay"""
    print(f"SHUTDOWN STATUS {app.get_shutdown_status()}")
    if not app.get_shutdown_status():
        return

    print("Monitoring...")  # TODO: Quitar
    max_idle_seconds = minutes_to_seconds(app.get_computer_idle())

    if shutdown_enabled:
        if get_idle_time() < max_idle_seconds or check_if_are_active_sessions(app):
            cancel_shutdown()

    if max_idle_seconds != 0:
        if get_idle_time() < max_idle_seconds:
            print("Computer is not in idle mode")
            return
        print("Computer is in idle mode")

    if not check_if_transcoder_running(app):
        print("Plex transcoder is running")
        return
    print("Plex transcoder is not running")

    if check_if_are_active_sessions(app):
        print("There are an active plex session")
        return
    print("No plex session is active")

    if not shutdown_enabled:
        activate_shutdown(app.get_shutdown_delay())


def monitor_mainloop(app: App):
    """Main loop for the monitor thread"""
    print("MONITOR LOOP STARTED")  # TODO: Quitar
    monitor_plex_and_shutdown(app)
    # sleep(minutes_to_seconds(app.getIntervalDelay()))
    sleep(5)  # TODO: Poner valor real
    monitor_mainloop(app)
